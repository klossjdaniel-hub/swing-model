"""
Performance dashboard for paper trading.

Shows:
- Overall win rate
- Performance by confidence tier
- Performance by catalyst type
- Recent predictions
- Trade history
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import get_connection

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def show_dashboard():
    """Display performance dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print(" " * 25 + "PAPER TRADING DASHBOARD")
    print("=" * 80)
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Overall stats
    print("=" * 80)
    print("OVERALL PERFORMANCE")
    print("=" * 80 + "\n")

    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN predicted_direction = actual_reverted_day2 THEN 1 ELSE 0 END) as correct,
            AVG(reversion_prob_day2) as avg_confidence
        FROM forward_predictions
        WHERE scored_at IS NOT NULL
          AND actual_reverted_day2 IS NOT NULL
    """)

    row = cursor.fetchone()
    if row and row[0]:
        total, correct, avg_conf = row
        accuracy = correct / total * 100 if total > 0 else 0

        print(f"Total Predictions: {total}")
        print(f"Correct: {correct}")
        print(f"Wrong: {total - correct}")
        print(f"**WIN RATE: {accuracy:.1f}%**")
        print(f"Average Confidence: {avg_conf*100:.1f}%\n")

        # Target comparison
        target = 60.0
        diff = accuracy - target
        if accuracy >= target:
            print(f"✓ ABOVE TARGET ({diff:+.1f}% vs {target}% goal)\n")
        else:
            print(f"✗ BELOW TARGET ({diff:.1f}% vs {target}% goal)\n")
    else:
        print("No scored predictions yet.\n")

    # By confidence tier
    print("=" * 80)
    print("PERFORMANCE BY CONFIDENCE TIER")
    print("=" * 80 + "\n")

    print(f"{'Confidence':<15} {'Total':<10} {'Correct':<10} {'Win Rate':<15}")
    print("-" * 80)

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
            print(f"{conf.upper():<15} {conf_total:<10} {conf_correct:<10} {conf_accuracy:>5.1f}%")
        else:
            print(f"{conf.upper():<15} {0:<10} {0:<10} {'N/A':>15}")

    print()

    # Get catalyst types from predictions
    print("=" * 80)
    print("PERFORMANCE BY CATALYST TYPE")
    print("=" * 80 + "\n")

    # Join with events to get catalyst type
    cursor.execute("""
        SELECT
            e.catalyst_type,
            COUNT(*) as total,
            SUM(CASE WHEN p.predicted_direction = p.actual_reverted_day2 THEN 1 ELSE 0 END) as correct
        FROM forward_predictions p
        LEFT JOIN events e ON p.ticker = e.ticker AND p.day0_date = e.day0_date
        WHERE p.scored_at IS NOT NULL
          AND p.actual_reverted_day2 IS NOT NULL
          AND e.catalyst_type IS NOT NULL
        GROUP BY e.catalyst_type
        ORDER BY total DESC
    """)

    catalyst_rows = cursor.fetchall()

    if catalyst_rows:
        print(f"{'Catalyst':<15} {'Total':<10} {'Correct':<10} {'Win Rate':<15}")
        print("-" * 80)

        for catalyst, total, correct in catalyst_rows:
            accuracy = correct / total * 100 if total > 0 else 0
            print(f"{catalyst:<15} {total:<10} {correct:<10} {accuracy:>5.1f}%")
        print()
    else:
        print("No catalyst data available yet.\n")

    # Recent predictions
    print("=" * 80)
    print("RECENT PREDICTIONS (Last 10)")
    print("=" * 80 + "\n")

    cursor.execute("""
        SELECT
            p.ticker,
            p.day0_date,
            p.reversion_prob_day2,
            p.confidence_tier,
            p.actual_reverted_day2,
            p.predicted_direction,
            e.catalyst_type,
            e.day0_return
        FROM forward_predictions p
        LEFT JOIN events e ON p.ticker = e.ticker AND p.day0_date = e.day0_date
        WHERE p.scored_at IS NOT NULL
        ORDER BY p.day0_date DESC
        LIMIT 10
    """)

    recent = cursor.fetchall()

    if recent:
        for ticker, date, prob, conf, actual, predicted, catalyst, day0_return in recent:
            correct = (predicted == actual) if actual is not None else None

            if correct is True:
                result = "✓ CORRECT"
            elif correct is False:
                result = "✗ WRONG"
            else:
                result = "? PENDING"

            direction = "UP" if day0_return and day0_return > 0 else "DOWN"
            mag = abs(day0_return * 100) if day0_return else 0

            print(f"{date} {ticker:6s} | {direction:4s} {mag:4.1f}% | {catalyst or 'unknown':10s} | "
                  f"Prob:{prob*100:5.1f}% {conf:6s} | {result}")

        print()
    else:
        print("No recent predictions.\n")

    # Pending predictions (not yet scored)
    print("=" * 80)
    print("PENDING PREDICTIONS (Awaiting Outcome)")
    print("=" * 80 + "\n")

    cursor.execute("""
        SELECT
            p.ticker,
            p.day0_date,
            p.reversion_prob_day2,
            p.confidence_tier,
            e.catalyst_type,
            e.day0_return
        FROM forward_predictions p
        LEFT JOIN events e ON p.ticker = e.ticker AND p.day0_date = e.day0_date
        WHERE p.scored_at IS NULL
        ORDER BY p.day0_date DESC
        LIMIT 20
    """)

    pending = cursor.fetchall()

    if pending:
        print(f"Total pending: {len(pending)}\n")

        for ticker, date, prob, conf, catalyst, day0_return in pending[:10]:
            direction = "UP" if day0_return and day0_return > 0 else "DOWN"
            mag = abs(day0_return * 100) if day0_return else 0

            action = "SHORT" if prob >= 0.5 and day0_return > 0 else "LONG" if prob >= 0.5 else "WATCH"

            print(f"{date} {ticker:6s} | {direction:4s} {mag:4.1f}% | {catalyst or 'unknown':10s} | "
                  f"Prob:{prob*100:5.1f}% {conf:6s} | Action: {action}")

        if len(pending) > 10:
            print(f"\n... and {len(pending) - 10} more")

        print()
    else:
        print("No pending predictions.\n")

    # Trade log summary
    print("=" * 80)
    print("TRADING ACTIVITY TIMELINE")
    print("=" * 80 + "\n")

    cursor.execute("""
        SELECT
            DATE(day0_date) as date,
            COUNT(*) as predictions
        FROM forward_predictions
        GROUP BY DATE(day0_date)
        ORDER BY date DESC
        LIMIT 7
    """)

    timeline = cursor.fetchall()

    if timeline:
        print("Last 7 days:\n")
        for date, count in timeline:
            print(f"  {date}: {count} predictions")
        print()
    else:
        print("No trading activity yet.\n")

    conn.close()

    print("=" * 80)
    print("END OF DASHBOARD")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    show_dashboard()
