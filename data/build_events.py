"""
Build labeled events dataset from raw data.

Joins earnings_raw + prices to create events table with:
- Event characteristics (Day 0 move, volume, earnings surprise, etc.)
- Outcome labels (Day 1-3 returns, reversion flags)
- Filters: require Day 0 move >= 2%, volume surge >= 1.5x

Uses relative reversion threshold: 30% of initial move.
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from data.db import get_connection
from universe import KNOWN_AMC_REPORTERS, KNOWN_BMO_REPORTERS

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

def determine_earnings_timing(ticker, report_date):
    """
    Determine if earnings were AMC or BMO.

    Logic:
    1. If ticker is in known AMC/BMO list, use that
    2. Otherwise, assume BMO (since most earnings are BMO)

    Returns: ('AMC' or 'BMO', 'known' or 'assumed')
    """
    if ticker in KNOWN_AMC_REPORTERS:
        return 'AMC', 'known'
    elif ticker in KNOWN_BMO_REPORTERS:
        return 'BMO', 'known'
    else:
        return 'BMO', 'assumed'

def find_day0_date(ticker, report_date, timing, conn):
    """
    Find Day 0 date based on earnings timing.

    AMC: Day 0 = next trading day after report_date
    BMO: Day 0 = report_date itself (market reacts during that day)
    """
    trading_days = get_trading_days(
        ticker,
        report_date,
        (datetime.strptime(report_date, '%Y-%m-%d') + timedelta(days=5)).strftime('%Y-%m-%d'),
        conn
    )

    if not trading_days:
        return None

    if timing == 'AMC':
        # Day 0 is next trading day after report
        if report_date in trading_days:
            idx = trading_days.index(report_date)
            if idx + 1 < len(trading_days):
                return trading_days[idx + 1]
        # If report_date not a trading day, use first trading day after
        for day in trading_days:
            if day > report_date:
                return day
    else:  # BMO
        # Day 0 is report_date itself
        if report_date in trading_days:
            return report_date
        # If report_date not a trading day, use next trading day
        for day in trading_days:
            if day > report_date:
                return day

    return None

def calculate_pre_earnings_drift(ticker, day0_date, days, conn):
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

def build_events():
    """Build events table from raw data."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("BUILDING EVENTS DATASET")
    print("=" * 60)

    # Clear existing events
    cursor.execute("DELETE FROM events")

    # Get all earnings with required data
    cursor.execute("""
        SELECT
            e.ticker,
            e.report_date,
            e.eps_estimate,
            e.eps_actual,
            e.revenue_estimate,
            e.revenue_actual,
            e.surprise_pct,
            c.sector,
            c.market_cap_bucket
        FROM earnings_raw e
        JOIN company_info c ON e.ticker = c.ticker
        WHERE e.eps_estimate IS NOT NULL
          AND e.eps_actual IS NOT NULL
        ORDER BY e.report_date
    """)

    earnings = cursor.fetchall()
    print(f"\n[OK] Found {len(earnings)} earnings reports with EPS data\n")

    events_created = 0
    events_filtered = 0

    for i, earning in enumerate(earnings, 1):
        ticker = earning[0]
        report_date = earning[1]
        eps_estimate = earning[2]
        eps_actual = earning[3]
        revenue_estimate = earning[4]
        revenue_actual = earning[5]
        eps_surprise_pct = earning[6]
        sector = earning[7]
        market_cap_bucket = earning[8]

        if i % 10 == 0:
            print(f"[{i}/{len(earnings)}] Processing {ticker} on {report_date}...")

        # Determine earnings timing
        timing, timing_method = determine_earnings_timing(ticker, report_date)

        # Find Day 0
        day0_date = find_day0_date(ticker, report_date, timing, conn)
        if not day0_date:
            events_filtered += 1
            continue

        # Get Day 0 prices
        day0_prices = get_price_on_date(ticker, day0_date, conn)
        if not day0_prices:
            events_filtered += 1
            continue

        # Get previous day's close
        trading_days = get_trading_days(
            ticker,
            (datetime.strptime(day0_date, '%Y-%m-%d') - timedelta(days=5)).strftime('%Y-%m-%d'),
            day0_date,
            conn
        )

        if day0_date not in trading_days or trading_days.index(day0_date) == 0:
            events_filtered += 1
            continue

        day_minus1 = trading_days[trading_days.index(day0_date) - 1]
        prev_close_data = get_price_on_date(ticker, day_minus1, conn)
        if not prev_close_data:
            events_filtered += 1
            continue

        prev_close = prev_close_data['close']

        # Calculate Day 0 return (close-to-close)
        day0_return = (day0_prices['close'] - prev_close) / prev_close
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

        # Direction: 1 = up, -1 = down
        direction = 1 if day0_return > 0 else -1

        # Beat/miss classification
        if eps_surprise_pct and eps_surprise_pct > 0.02:
            beat_miss = 'beat'
        elif eps_surprise_pct and eps_surprise_pct < -0.02:
            beat_miss = 'miss'
        else:
            beat_miss = 'inline'

        # Revenue surprise
        revenue_surprise_pct = None
        if revenue_estimate and revenue_actual and revenue_estimate != 0:
            revenue_surprise_pct = (revenue_actual - revenue_estimate) / abs(revenue_estimate)

        # Pre-earnings drift
        drift_5d = calculate_pre_earnings_drift(ticker, day0_date, 5, conn)
        drift_20d = calculate_pre_earnings_drift(ticker, day0_date, 20, conn)

        # Price trends (same as drift for now)
        trend_5d = drift_5d
        trend_20d = drift_20d

        # VIX on Day 0
        cursor.execute("SELECT close FROM vix WHERE date = ?", (day0_date,))
        vix_row = cursor.fetchone()
        vix_day0 = vix_row[0] if vix_row else None

        # Day of week (0 = Monday, 4 = Friday)
        day_of_week = datetime.strptime(day0_date, '%Y-%m-%d').weekday()

        # Days since previous earnings
        cursor.execute("""
            SELECT MAX(report_date) FROM earnings_raw
            WHERE ticker = ? AND report_date < ?
        """, (ticker, report_date))
        prev_earnings_row = cursor.fetchone()
        days_since_prev = None
        if prev_earnings_row and prev_earnings_row[0]:
            prev_date = datetime.strptime(prev_earnings_row[0], '%Y-%m-%d')
            curr_date = datetime.strptime(report_date, '%Y-%m-%d')
            days_since_prev = (curr_date - prev_date).days

        # Calculate outcome labels (Day 1-3 returns)
        day0_idx = trading_days.index(day0_date)

        return_day1 = None
        return_day2 = None
        return_day3 = None

        if day0_idx + 1 < len(trading_days):
            return_day1 = calculate_return(ticker, day0_date, trading_days[day0_idx + 1], conn)

        if day0_idx + 2 < len(trading_days):
            return_day2 = calculate_return(ticker, day0_date, trading_days[day0_idx + 2], conn)

        if day0_idx + 3 < len(trading_days):
            return_day3 = calculate_return(ticker, day0_date, trading_days[day0_idx + 3], conn)

        # Reversion flags (30% threshold)
        threshold = config.REVERSION_THRESHOLD  # 0.30

        reverted_day1 = 0
        if return_day1 is not None:
            # Reversion = move in opposite direction >= 30% of initial move
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

        # Insert event
        cursor.execute("""
            INSERT INTO events (
                ticker, event_type, earnings_timing, timing_method, report_date,
                day0_date, sector, market_cap_bucket,
                day0_return, day0_return_abs, direction, volume_ratio,
                eps_surprise_pct, revenue_surprise_pct, beat_miss,
                pre_earnings_drift_5d, pre_earnings_drift_20d,
                price_trend_5d, price_trend_20d,
                vix_day0, day_of_week, days_since_prev_earnings,
                return_day1, return_day2, return_day3,
                reverted_day1, reverted_day2, reverted_day3,
                reversion_magnitude_day2
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker, 'earnings', timing, timing_method, report_date,
            day0_date, sector, market_cap_bucket,
            day0_return, day0_return_abs, direction, volume_ratio,
            eps_surprise_pct, revenue_surprise_pct, beat_miss,
            drift_5d, drift_20d, trend_5d, trend_20d,
            vix_day0, day_of_week, days_since_prev,
            return_day1, return_day2, return_day3,
            reverted_day1, reverted_day2, reverted_day3,
            reversion_magnitude_day2
        ))

        events_created += 1

    conn.commit()

    # Print summary statistics
    print("\n" + "=" * 60)
    print("EVENT DATASET SUMMARY")
    print("=" * 60)

    print(f"\nTotal earnings processed: {len(earnings)}")
    print(f"Events created: {events_created}")
    print(f"Events filtered out: {events_filtered}")
    print(f"  (< 2% move or < 1.5x volume or missing data)")

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

    # Direction split
    cursor.execute("SELECT COUNT(*) FROM events WHERE direction = 1")
    ups = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM events WHERE direction = -1")
    downs = cursor.fetchone()[0]

    if events_created > 0:
        print(f"\nDirection split:")
        print(f"  Up moves: {ups} ({ups/events_created*100:.1f}%)")
        print(f"  Down moves: {downs} ({downs/events_created*100:.1f}%)")

    # Beat/miss split
    cursor.execute("SELECT beat_miss, COUNT(*) FROM events GROUP BY beat_miss")
    beat_miss_counts = cursor.fetchall()
    print(f"\nEarnings results:")
    for bm, count in beat_miss_counts:
        print(f"  {bm}: {count} ({count/events_created*100:.1f}%)")

    # Sector distribution
    cursor.execute("SELECT sector, COUNT(*) FROM events GROUP BY sector ORDER BY COUNT(*) DESC")
    sector_counts = cursor.fetchall()
    print(f"\nEvents by sector:")
    for sector_name, count in sector_counts:
        print(f"  {sector_name}: {count}")

    conn.close()

    print("\n" + "=" * 60)
    print("[OK] Events dataset built successfully")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    build_events()
