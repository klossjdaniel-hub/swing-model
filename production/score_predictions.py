"""
Score previous predictions against actual outcomes.

This runs after market close to check if our predictions were correct.
Updates forward_predictions table with actual results.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from data.db import get_connection

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def get_price_on_date(ticker, date, conn):
    """Get close price for a ticker on a specific date."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT close FROM prices
        WHERE ticker = ? AND date = ?
    """, (ticker, date))
    row = cursor.fetchone()
    return row[0] if row else None


def get_trading_days_after(ticker, start_date, days_forward, conn):
    """Get trading days starting from start_date."""
    cursor = conn.cursor()

    # Get up to 10 trading days after start_date
    end_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=days_forward*2)).strftime('%Y-%m-%d')

    cursor.execute("""
        SELECT date FROM prices
        WHERE ticker = ? AND date >= ? AND date <= ?
        ORDER BY date
        LIMIT ?
    """, (ticker, start_date, end_date, days_forward + 1))

    return [row[0] for row in cursor.fetchall()]


def calculate_reversion(day0_close, day_n_close, direction):
    """
    Calculate if move reverted.

    Reversion = moved in opposite direction ≥30% of initial move.
    """
    if not day0_close or not day_n_close:
        return None

    return_n = (day_n_close - day0_close) / day0_close

    # Check if reversed direction
    if direction == 1 and return_n < 0:  # Up move reversed down
        return 1  # Reverted
    elif direction == -1 and return_n > 0:  # Down move reversed up
        return 1  # Reverted
    else:
        return 0  # Did not revert


def score_predictions():
    """Score all unscored predictions."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("SCORING PREDICTIONS")
    print("=" * 60 + "\n")

    # Get predictions that haven't been scored yet
    cursor.execute("""
        SELECT
            id,
            ticker,
            day0_date,
            predicted_direction,
            reversion_prob_day2,
            confidence_tier
        FROM forward_predictions
        WHERE scored_at IS NULL
        ORDER BY day0_date
    """)

    predictions = cursor.fetchall()

    if not predictions:
        print("No unscored predictions found.\n")
        return

    print(f"Found {len(predictions)} unscored predictions\n")

    scored = 0
    skipped = 0

    for pred_id, ticker, day0_date, predicted_direction, reversion_prob, confidence in predictions:
        # Get trading days after day0
        trading_days = get_trading_days_after(ticker, day0_date, 3, conn)

        if day0_date not in trading_days:
            print(f"[SKIP] {ticker} {day0_date} - day0 not found")
            skipped += 1
            continue

        day0_idx = trading_days.index(day0_date)

        # Need at least 3 days of data
        if len(trading_days) < day0_idx + 3:
            print(f"[WAIT] {ticker} {day0_date} - not enough days yet")
            skipped += 1
            continue

        # Get prices
        day0_close = get_price_on_date(ticker, trading_days[day0_idx], conn)

        # Get direction from the event
        cursor.execute("""
            SELECT direction FROM events
            WHERE ticker = ? AND day0_date = ?
            LIMIT 1
        """, (ticker, day0_date))
        direction_row = cursor.fetchone()
        direction = direction_row[0] if direction_row else None

        if not day0_close or direction is None:
            print(f"[ERROR] {ticker} {day0_date} - missing data")
            skipped += 1
            continue

        # Calculate actual outcomes
        actual_return_day1 = None
        actual_return_day2 = None
        actual_return_day3 = None
        actual_reverted_day2 = None
        actual_reverted_day3 = None

        if len(trading_days) > day0_idx + 1:
            day1_close = get_price_on_date(ticker, trading_days[day0_idx + 1], conn)
            if day1_close:
                actual_return_day1 = (day1_close - day0_close) / day0_close

        if len(trading_days) > day0_idx + 2:
            day2_close = get_price_on_date(ticker, trading_days[day0_idx + 2], conn)
            if day2_close:
                actual_return_day2 = (day2_close - day0_close) / day0_close
                actual_reverted_day2 = calculate_reversion(day0_close, day2_close, direction)

        if len(trading_days) > day0_idx + 3:
            day3_close = get_price_on_date(ticker, trading_days[day0_idx + 3], conn)
            if day3_close:
                actual_return_day3 = (day3_close - day0_close) / day0_close
                actual_reverted_day3 = calculate_reversion(day0_close, day3_close, direction)

        # Update prediction with actual results
        cursor.execute("""
            UPDATE forward_predictions
            SET actual_return_day1 = ?,
                actual_return_day2 = ?,
                actual_return_day3 = ?,
                actual_reverted_day2 = ?,
                actual_reverted_day3 = ?,
                scored_at = ?
            WHERE id = ?
        """, (
            actual_return_day1,
            actual_return_day2,
            actual_return_day3,
            actual_reverted_day2,
            actual_reverted_day3,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            pred_id
        ))

        # Check if prediction was correct
        if actual_reverted_day2 is not None:
            was_correct = (predicted_direction == actual_reverted_day2)
            result_str = "✓ CORRECT" if was_correct else "✗ WRONG"

            print(f"[{result_str}] {ticker} {day0_date}")
            print(f"  Predicted: {reversion_prob*100:.1f}% revert ({confidence} confidence)")
            print(f"  Actual: {'Reverted' if actual_reverted_day2 else 'Did not revert'}")
            print(f"  Return Day 2: {actual_return_day2*100:+.1f}%\n")

            scored += 1
        else:
            skipped += 1

    conn.commit()

    # Calculate overall performance
    cursor.execute("""
        SELECT COUNT(*),
               SUM(CASE WHEN predicted_direction = actual_reverted_day2 THEN 1 ELSE 0 END)
        FROM forward_predictions
        WHERE scored_at IS NOT NULL
          AND actual_reverted_day2 IS NOT NULL
    """)
    total, correct = cursor.fetchone()

    print("=" * 60)
    print("OVERALL PERFORMANCE")
    print("=" * 60 + "\n")

    if total and total > 0:
        accuracy = correct / total * 100
        print(f"Total predictions scored: {total}")
        print(f"Correct predictions: {correct}")
        print(f"**WIN RATE: {accuracy:.1f}%**\n")

        # By confidence tier
        print("Performance by Confidence Tier:\n")
        for conf in ['high', 'medium', 'low']:
            cursor.execute("""
                SELECT COUNT(*),
                       SUM(CASE WHEN predicted_direction = actual_reverted_day2 THEN 1 ELSE 0 END)
                FROM forward_predictions
                WHERE scored_at IS NOT NULL
                  AND actual_reverted_day2 IS NOT NULL
                  AND confidence_tier = ?
            """, (conf,))
            conf_total, conf_correct = cursor.fetchone()
            if conf_total and conf_total > 0:
                conf_accuracy = conf_correct / conf_total * 100
                print(f"  {conf.upper():6s}: {conf_correct:3d}/{conf_total:3d} ({conf_accuracy:5.1f}%)")

    else:
        print("No scored predictions yet.\n")

    conn.close()

    print("\n" + "=" * 60)
    print(f"[OK] Scored {scored} predictions, skipped {skipped}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    score_predictions()
