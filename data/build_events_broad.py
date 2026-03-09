"""
Build labeled events dataset from ALL big moves (not just earnings).

Ultra-Minimal Catalyst Detection:
- earnings: Check if date is in earnings calendar
- gap: Check if open differs significantly from prev close
- unknown: Everything else

This broader approach gives us 12X more data (~3,000 events vs ~250 earnings-only).
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from data.db import get_connection

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def get_earnings_dates(ticker, conn):
    """Get set of all earnings dates for a ticker."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT report_date FROM earnings_raw
        WHERE ticker = ?
    """, (ticker,))
    return set(row[0] for row in cursor.fetchall())


def classify_catalyst(ticker, date, prices, prev_prices, earnings_dates):
    """
    Classify catalyst type for a big move.

    Returns: 'earnings', 'gap', or 'unknown'
    """
    # Check if it's an earnings day
    if date in earnings_dates:
        return 'earnings'

    # Check for gap (open significantly different from prev close)
    if prev_prices and prices:
        gap_size = abs(prices['open'] - prev_prices['close']) / prev_prices['close']
        if gap_size > 0.01:  # >1% gap
            return 'gap'

    # Unknown catalyst
    return 'unknown'


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
    """Get OHLCV for a ticker on a specific date."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT open, high, low, close, volume
        FROM prices
        WHERE ticker = ? AND date = ?
    """, (ticker, date))
    row = cursor.fetchone()
    if row:
        return {
            'open': row[0],
            'high': row[1],
            'low': row[2],
            'close': row[3],
            'volume': row[4]
        }
    return None


def calculate_return(ticker, from_date, to_date, conn):
    """Calculate return from close-to-close."""
    from_price = get_price_on_date(ticker, from_date, conn)
    to_price = get_price_on_date(ticker, to_date, conn)

    if not from_price or not to_price:
        return None

    return (to_price['close'] - from_price['close']) / from_price['close']


def get_avg_volume(ticker, end_date, days, conn):
    """Get average volume for N days before end_date."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(volume) FROM prices
        WHERE ticker = ? AND date < ? AND volume > 0
        ORDER BY date DESC
        LIMIT ?
    """, (ticker, end_date, days))
    row = cursor.fetchone()
    return row[0] if row and row[0] else None


def calculate_pre_drift(ticker, day0_date, days, conn):
    """Calculate return from N days before Day 0 to day before Day 0."""
    trading_days = get_trading_days(
        ticker,
        (datetime.strptime(day0_date, '%Y-%m-%d') - timedelta(days=days*2)).strftime('%Y-%m-%d'),
        day0_date,
        conn
    )

    if len(trading_days) < days + 1:
        return None

    # Get day before Day 0
    day0_idx = trading_days.index(day0_date)
    if day0_idx == 0:
        return None

    day_before = trading_days[day0_idx - 1]

    # Get day N days before
    if day0_idx - days < 0:
        return None

    start_day = trading_days[day0_idx - days]

    return calculate_return(ticker, start_day, day_before, conn)


def build_events_broad():
    """Build events table from ALL big moves (not just earnings)."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("BUILDING EVENTS DATASET - BROAD CATALYST APPROACH")
    print("=" * 60)
    print("\nDetecting ALL big moves (>2%, >1.5x volume)")
    print("Classifying catalyst: earnings | gap | unknown\n")

    # Clear existing events
    cursor.execute("DELETE FROM events")

    # Get all tickers with company info
    cursor.execute("""
        SELECT ticker, sector, market_cap_bucket
        FROM company_info
        ORDER BY ticker
    """)
    tickers_info = cursor.fetchall()

    print(f"[OK] Processing {len(tickers_info)} stocks\n")

    events_created = 0
    events_filtered = 0
    total_days_checked = 0

    catalyst_counts = {'earnings': 0, 'gap': 0, 'unknown': 0}

    for ticker_idx, (ticker, sector, market_cap_bucket) in enumerate(tickers_info, 1):
        print(f"[{ticker_idx}/{len(tickers_info)}] {ticker}...", end=' ')

        # Get earnings dates for this ticker
        earnings_dates = get_earnings_dates(ticker, conn)

        # Get all trading days for this ticker
        trading_days = get_trading_days(ticker, config.START_DATE, '2026-12-31', conn)

        if len(trading_days) < 2:
            print("(no data)")
            continue

        ticker_events = 0

        # Iterate through all trading days (starting from day 1, need prev day)
        for day_idx in range(1, len(trading_days)):
            total_days_checked += 1

            day0_date = trading_days[day_idx]
            day_minus1 = trading_days[day_idx - 1]

            # Get prices
            day0_prices = get_price_on_date(ticker, day0_date, conn)
            prev_prices = get_price_on_date(ticker, day_minus1, conn)

            if not day0_prices or not prev_prices:
                continue

            # Calculate Day 0 return (close-to-close)
            day0_return = (day0_prices['close'] - prev_prices['close']) / prev_prices['close']
            day0_return_abs = abs(day0_return)

            # Filter: require >= 2% move
            if day0_return_abs < 0.02:
                events_filtered += 1
                continue

            # Calculate volume ratio
            avg_volume = get_avg_volume(ticker, day0_date, 20, conn)
            volume_ratio = None
            if avg_volume and avg_volume > 0:
                volume_ratio = day0_prices['volume'] / avg_volume

            # Filter: require >= 1.5x volume
            if not volume_ratio or volume_ratio < 1.5:
                events_filtered += 1
                continue

            # Classify catalyst
            catalyst_type = classify_catalyst(ticker, day0_date, day0_prices, prev_prices, earnings_dates)
            catalyst_counts[catalyst_type] += 1

            # Direction: 1 = up, -1 = down
            direction = 1 if day0_return > 0 else -1

            # Pre-move drift
            drift_5d = calculate_pre_drift(ticker, day0_date, 5, conn)
            drift_20d = calculate_pre_drift(ticker, day0_date, 20, conn)

            # VIX on Day 0
            cursor.execute("SELECT close FROM vix WHERE date = ?", (day0_date,))
            vix_row = cursor.fetchone()
            vix_day0 = vix_row[0] if vix_row else None

            # Day of week (0 = Monday, 4 = Friday)
            day_of_week = datetime.strptime(day0_date, '%Y-%m-%d').weekday()

            # Calculate outcome labels (Day 1-3 returns)
            return_day1 = None
            return_day2 = None
            return_day3 = None

            if day_idx + 1 < len(trading_days):
                return_day1 = calculate_return(ticker, day0_date, trading_days[day_idx + 1], conn)

            if day_idx + 2 < len(trading_days):
                return_day2 = calculate_return(ticker, day0_date, trading_days[day_idx + 2], conn)

            if day_idx + 3 < len(trading_days):
                return_day3 = calculate_return(ticker, day0_date, trading_days[day_idx + 3], conn)

            # Reversion flags (30% threshold)
            threshold = config.REVERSION_THRESHOLD  # 0.30

            reverted_day1 = 0
            if return_day1 is not None:
                if direction == 1 and return_day1 < 0:
                    reverted_day1 = 1 if abs(return_day1) >= threshold * day0_return_abs else 0
                elif direction == -1 and return_day1 > 0:
                    reverted_day1 = 1 if abs(return_day1) >= threshold * day0_return_abs else 0

            reverted_day2 = 0
            if return_day2 is not None:
                if direction == 1 and return_day2 < 0:
                    reverted_day2 = 1 if abs(return_day2) >= threshold * day0_return_abs else 0
                elif direction == -1 and return_day2 > 0:
                    reverted_day2 = 1 if abs(return_day2) >= threshold * day0_return_abs else 0

            reverted_day3 = 0
            if return_day3 is not None:
                if direction == 1 and return_day3 < 0:
                    reverted_day3 = 1 if abs(return_day3) >= threshold * day0_return_abs else 0
                elif direction == -1 and return_day3 > 0:
                    reverted_day3 = 1 if abs(return_day3) >= threshold * day0_return_abs else 0

            # Reversion magnitude for Day 2
            reversion_magnitude_day2 = None
            if return_day2 is not None and day0_return_abs > 0:
                reversion_magnitude_day2 = abs(return_day2) / day0_return_abs

            # Insert event with catalyst_type
            cursor.execute("""
                INSERT INTO events (
                    ticker, event_type, day0_date, sector, market_cap_bucket,
                    catalyst_type,
                    day0_return, day0_return_abs, direction, volume_ratio,
                    pre_earnings_drift_5d, pre_earnings_drift_20d,
                    vix_day0, day_of_week,
                    return_day1, return_day2, return_day3,
                    reverted_day1, reverted_day2, reverted_day3,
                    reversion_magnitude_day2
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticker, 'broad_catalyst', day0_date, sector, market_cap_bucket,
                catalyst_type,
                day0_return, day0_return_abs, direction, volume_ratio,
                drift_5d, drift_20d,
                vix_day0, day_of_week,
                return_day1, return_day2, return_day3,
                reverted_day1, reverted_day2, reverted_day3,
                reversion_magnitude_day2
            ))

            events_created += 1
            ticker_events += 1

        print(f"{ticker_events} events")

        # Commit every 10 tickers
        if ticker_idx % 10 == 0:
            conn.commit()

    conn.commit()

    # Print summary statistics
    print("\n" + "=" * 60)
    print("EVENT DATASET SUMMARY")
    print("=" * 60)

    print(f"\nTotal stock-days checked: {total_days_checked:,}")
    print(f"Events created: {events_created}")
    print(f"Events filtered out: {events_filtered}")
    print(f"  (< 2% move or < 1.5x volume or missing data)")

    # Catalyst breakdown
    print(f"\nEvents by catalyst type:")
    for catalyst, count in sorted(catalyst_counts.items(), key=lambda x: x[1], reverse=True):
        pct = count / events_created * 100 if events_created > 0 else 0
        print(f"  {catalyst}: {count} ({pct:.1f}%)")

    # Reversion rates
    cursor.execute("SELECT COUNT(*) FROM events WHERE reverted_day1 = 1")
    rev_day1 = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM events WHERE reverted_day2 = 1")
    rev_day2 = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM events WHERE reverted_day3 = 1")
    rev_day3 = cursor.fetchone()[0]

    if events_created > 0:
        print(f"\nReversion rates (30% threshold):")
        print(f"  Day 1: {rev_day1}/{events_created} ({rev_day1/events_created*100:.1f}%)")
        print(f"  Day 2: {rev_day2}/{events_created} ({rev_day2/events_created*100:.1f}%)")
        print(f"  Day 3: {rev_day3}/{events_created} ({rev_day3/events_created*100:.1f}%)")

    # Reversion by catalyst type
    print(f"\nReversion rates by catalyst (Day 2):")
    for catalyst_type in ['earnings', 'gap', 'unknown']:
        cursor.execute("""
            SELECT COUNT(*), SUM(reverted_day2)
            FROM events
            WHERE catalyst_type = ?
        """, (catalyst_type,))
        row = cursor.fetchone()
        total = row[0]
        reverted = row[1] or 0
        if total > 0:
            print(f"  {catalyst_type}: {reverted}/{total} ({reverted/total*100:.1f}%)")

    # Direction split
    cursor.execute("SELECT COUNT(*) FROM events WHERE direction = 1")
    ups = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM events WHERE direction = -1")
    downs = cursor.fetchone()[0]

    if events_created > 0:
        print(f"\nDirection split:")
        print(f"  Up moves: {ups} ({ups/events_created*100:.1f}%)")
        print(f"  Down moves: {downs} ({downs/events_created*100:.1f}%)")

    # Sector distribution
    cursor.execute("SELECT sector, COUNT(*) FROM events GROUP BY sector ORDER BY COUNT(*) DESC")
    sector_counts = cursor.fetchall()
    print(f"\nEvents by sector:")
    for sector_name, count in sector_counts:
        print(f"  {sector_name}: {count}")

    conn.close()

    print("\n" + "=" * 60)
    print("[OK] Broad events dataset built successfully")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    build_events_broad()
