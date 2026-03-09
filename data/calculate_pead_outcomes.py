"""
Calculate PEAD (momentum) outcomes for all events.

For each event, calculate:
- Forward returns at 5, 10, 20, 60 days
- Whether move CONTINUED (momentum) vs reverted
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


def get_trading_days(ticker, start_date, end_date, conn):
    """Get list of trading days for a ticker between dates."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date FROM prices
        WHERE ticker = ? AND date >= ? AND date <= ?
        ORDER BY date
    """, (ticker, start_date, end_date))
    return [row[0] for row in cursor.fetchall()]


def get_price_on_date(ticker, date, conn):
    """Get close price for a ticker on a specific date."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT close FROM prices
        WHERE ticker = ? AND date = ?
    """, (ticker, date))
    row = cursor.fetchone()
    return row[0] if row else None


def calculate_forward_return(ticker, day0_date, days_forward, conn):
    """Calculate return from day0 close to N days forward close."""
    # Get trading days starting from day0
    day0_dt = datetime.strptime(day0_date, '%Y-%m-%d')
    end_date = (day0_dt + timedelta(days=days_forward*2)).strftime('%Y-%m-%d')

    trading_days = get_trading_days(ticker, day0_date, end_date, conn)

    if day0_date not in trading_days:
        return None

    day0_idx = trading_days.index(day0_date)

    if day0_idx + days_forward >= len(trading_days):
        return None

    target_date = trading_days[day0_idx + days_forward]

    day0_close = get_price_on_date(ticker, day0_date, conn)
    target_close = get_price_on_date(ticker, target_date, conn)

    if day0_close and target_close:
        return (target_close - day0_close) / day0_close

    return None


def calculate_pead_outcomes():
    """Calculate PEAD outcomes for all events."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("CALCULATING PEAD (MOMENTUM) OUTCOMES")
    print("=" * 60 + "\n")

    # Get all events
    cursor.execute("""
        SELECT id, ticker, day0_date, direction
        FROM events
        ORDER BY day0_date
    """)
    events = cursor.fetchall()

    print(f"Processing {len(events)} events...\n")

    updated = 0
    failed = 0

    for i, (event_id, ticker, day0_date, direction) in enumerate(events, 1):
        if i % 100 == 0:
            print(f"[{i}/{len(events)}] Processing {ticker} on {day0_date}...")
            conn.commit()

        try:
            # Calculate forward returns
            return_day5 = calculate_forward_return(ticker, day0_date, 5, conn)
            return_day10 = calculate_forward_return(ticker, day0_date, 10, conn)
            return_day20 = calculate_forward_return(ticker, day0_date, 20, conn)
            return_day60 = calculate_forward_return(ticker, day0_date, 60, conn)

            # Calculate continuation flags
            # Continuation = move in SAME direction as Day 0
            continued_day5 = None
            if return_day5 is not None and direction is not None:
                if direction == 1:  # Up move
                    continued_day5 = 1 if return_day5 > 0 else 0
                else:  # Down move
                    continued_day5 = 1 if return_day5 < 0 else 0

            continued_day10 = None
            if return_day10 is not None and direction is not None:
                if direction == 1:
                    continued_day10 = 1 if return_day10 > 0 else 0
                else:
                    continued_day10 = 1 if return_day10 < 0 else 0

            continued_day20 = None
            if return_day20 is not None and direction is not None:
                if direction == 1:
                    continued_day20 = 1 if return_day20 > 0 else 0
                else:
                    continued_day20 = 1 if return_day20 < 0 else 0

            continued_day60 = None
            if return_day60 is not None and direction is not None:
                if direction == 1:
                    continued_day60 = 1 if return_day60 > 0 else 0
                else:
                    continued_day60 = 1 if return_day60 < 0 else 0

            # Update event
            cursor.execute("""
                UPDATE events
                SET return_day5 = ?,
                    return_day10 = ?,
                    return_day20 = ?,
                    return_day60 = ?,
                    continued_day5 = ?,
                    continued_day10 = ?,
                    continued_day20 = ?,
                    continued_day60 = ?
                WHERE id = ?
            """, (return_day5, return_day10, return_day20, return_day60,
                  continued_day5, continued_day10, continued_day20, continued_day60,
                  event_id))

            updated += 1

        except Exception as e:
            print(f"[ERROR] Failed to process event {event_id}: {e}")
            failed += 1

    conn.commit()

    # Print summary statistics
    print("\n" + "=" * 60)
    print("PEAD OUTCOMES SUMMARY")
    print("=" * 60 + "\n")

    print(f"Events processed: {len(events)}")
    print(f"Successfully updated: {updated}")
    print(f"Failed: {failed}\n")

    # Continuation rates
    print("Continuation Rates (% of moves that continued in same direction):\n")
    for days in [5, 10, 20, 60]:
        cursor.execute(f"""
            SELECT COUNT(*), SUM(continued_day{days})
            FROM events
            WHERE continued_day{days} IS NOT NULL
        """)
        row = cursor.fetchone()
        if row and row[0]:
            total = row[0]
            continued = row[1] or 0
            rate = continued / total * 100
            print(f"  Day {days:2d}: {continued:4d}/{total:4d} ({rate:5.1f}%)")

    # By catalyst type
    print("\nContinuation Rates by Catalyst Type (Day 20):\n")
    for catalyst in ['earnings', 'gap', 'unknown']:
        cursor.execute("""
            SELECT COUNT(*), SUM(continued_day20)
            FROM events
            WHERE catalyst_type = ? AND continued_day20 IS NOT NULL
        """, (catalyst,))
        row = cursor.fetchone()
        if row and row[0]:
            total = row[0]
            continued = row[1] or 0
            rate = continued / total * 100
            print(f"  {catalyst:10s}: {continued:4d}/{total:4d} ({rate:5.1f}%)")

    # By direction
    print("\nContinuation Rates by Direction (Day 20):\n")
    cursor.execute("""
        SELECT COUNT(*), SUM(continued_day20)
        FROM events
        WHERE direction = 1 AND continued_day20 IS NOT NULL
    """)
    row = cursor.fetchone()
    if row and row[0]:
        total_up = row[0]
        continued_up = row[1] or 0
        rate_up = continued_up / total_up * 100
        print(f"  Up moves:   {continued_up:4d}/{total_up:4d} ({rate_up:5.1f}%)")

    cursor.execute("""
        SELECT COUNT(*), SUM(continued_day20)
        FROM events
        WHERE direction = -1 AND continued_day20 IS NOT NULL
    """)
    row = cursor.fetchone()
    if row and row[0]:
        total_down = row[0]
        continued_down = row[1] or 0
        rate_down = continued_down / total_down * 100
        print(f"  Down moves: {continued_down:4d}/{total_down:4d} ({rate_down:5.1f}%)")

    conn.close()

    print("\n" + "=" * 60)
    print("[OK] PEAD outcomes calculated successfully")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    calculate_pead_outcomes()
