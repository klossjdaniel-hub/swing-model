"""
Calculate enhanced features for all events.

Uses existing price/volume data to create sophisticated features that capture:
- Emotion (intraday volatility, volume surges, gaps)
- History (reversion tendency, consecutive moves)
- Context (sector-relative, VIX changes, price level)
"""

import sys
import os
import sqlite3
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import get_connection

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def get_price_data(ticker, start_date, end_date, conn):
    """Get price data for a ticker between dates."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, open, high, low, close, volume
        FROM prices
        WHERE ticker = ? AND date >= ? AND date <= ?
        ORDER BY date
    """, (ticker, start_date, end_date))
    return cursor.fetchall()


def calculate_intraday_volatility(high, low, open_price):
    """Calculate intraday volatility as % of open."""
    if open_price and open_price > 0:
        return (high - low) / open_price
    return None


def calculate_gap(open_price, prev_close):
    """Calculate gap percentage."""
    if prev_close and prev_close > 0:
        return (open_price - prev_close) / prev_close
    return None


def calculate_volume_zscore(volume, mean_vol, std_vol):
    """Calculate z-score of volume."""
    if std_vol and std_vol > 0:
        return (volume - mean_vol) / std_vol
    return None


def calculate_drift_volatility(returns):
    """Calculate standard deviation of returns."""
    if len(returns) > 1:
        return np.std(returns)
    return None


def calculate_vix_change(vix_today, vix_5d_ago):
    """Calculate VIX change over 5 days."""
    if vix_today is not None and vix_5d_ago is not None:
        return vix_today - vix_5d_ago
    return None


def calculate_52week_position(price, prices_52weeks):
    """Calculate current price as % of 52-week high."""
    if len(prices_52weeks) > 0:
        high_52w = max(prices_52weeks)
        if high_52w > 0:
            return price / high_52w
    return None


def calculate_consecutive_days(returns):
    """Calculate consecutive days in same direction."""
    if len(returns) == 0:
        return 0

    consecutive = 1
    last_direction = 1 if returns[-1] > 0 else -1

    for i in range(len(returns) - 2, -1, -1):
        current_direction = 1 if returns[i] > 0 else -1
        if current_direction == last_direction:
            consecutive += 1
        else:
            break

    return consecutive


def get_move_magnitude_bucket(return_abs):
    """Categorize move size into buckets."""
    if return_abs < 0.03:
        return "small_2-3pct"
    elif return_abs < 0.05:
        return "medium_3-5pct"
    elif return_abs < 0.10:
        return "large_5-10pct"
    else:
        return "extreme_10pct+"


def calculate_features_for_event(event_id, ticker, day0_date, day0_return_abs, conn):
    """Calculate all enhanced features for a single event."""
    cursor = conn.cursor()

    features = {}

    # Get Day 0 prices
    cursor.execute("""
        SELECT open, high, low, close, volume
        FROM prices
        WHERE ticker = ? AND date = ?
    """, (ticker, day0_date))
    row = cursor.fetchone()
    if not row:
        return features

    open_price, high, low, close, volume = row

    # Get previous close for gap calculation
    cursor.execute("""
        SELECT close FROM prices
        WHERE ticker = ? AND date < ?
        ORDER BY date DESC
        LIMIT 1
    """, (ticker, day0_date))
    prev_row = cursor.fetchone()
    prev_close = prev_row[0] if prev_row else None

    # 1. Intraday volatility
    features['intraday_volatility_pct'] = calculate_intraday_volatility(high, low, open_price)

    # 2. Gap percentage
    features['gap_pct'] = calculate_gap(open_price, prev_close)

    # 3. Volume surge z-score
    cursor.execute("""
        SELECT volume
        FROM prices
        WHERE ticker = ? AND date < ? AND volume > 0
        ORDER BY date DESC
        LIMIT 20
    """, (ticker, day0_date))
    volumes = [row[0] for row in cursor.fetchall()]
    if len(volumes) > 1:
        mean_vol = np.mean(volumes)
        std_vol = np.std(volumes)
        features['volume_surge_zscore'] = calculate_volume_zscore(volume, mean_vol, std_vol)

    # 4 & 5. Drift volatility (5d and 20d)
    for days in [5, 20]:
        cursor.execute("""
            SELECT close FROM prices
            WHERE ticker = ? AND date < ?
            ORDER BY date DESC
            LIMIT ?
        """, (ticker, day0_date, days + 1))
        closes = [row[0] for row in cursor.fetchall()]
        if len(closes) > 1:
            returns = [(closes[i] - closes[i+1]) / closes[i+1] for i in range(len(closes)-1)]
            features[f'drift_volatility_{days}d'] = calculate_drift_volatility(returns)

    # 6. Ticker reversion rate (historical)
    # Get all previous events for this ticker where reverted_day2 is not null
    cursor.execute("""
        SELECT COUNT(*), SUM(reverted_day2)
        FROM events
        WHERE ticker = ? AND day0_date < ? AND reverted_day2 IS NOT NULL
    """, (ticker, day0_date))
    rev_stats = cursor.fetchone()
    if rev_stats and rev_stats[0] and rev_stats[0] > 0:
        total, reverted = rev_stats
        features['ticker_reversion_rate_historical'] = (reverted or 0) / total

    # 7. VIX change (5 day)
    cursor.execute("SELECT close FROM vix WHERE date = ?", (day0_date,))
    vix_row = cursor.fetchone()
    vix_today = vix_row[0] if vix_row else None

    day0_dt = datetime.strptime(day0_date, '%Y-%m-%d')
    vix_5d_ago_date = (day0_dt - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute("SELECT close FROM vix WHERE date <= ? ORDER BY date DESC LIMIT 1", (vix_5d_ago_date,))
    vix_5d_row = cursor.fetchone()
    vix_5d_ago = vix_5d_row[0] if vix_5d_row else None

    features['vix_change_5d'] = calculate_vix_change(vix_today, vix_5d_ago)

    # 8. Sector-relative return
    # Get sector and day0_return
    cursor.execute("""
        SELECT sector, day0_return FROM events WHERE id = ?
    """, (event_id,))
    event_row = cursor.fetchone()
    if event_row:
        sector, day0_return = event_row

        # Get average return for all stocks in same sector on same day
        cursor.execute("""
            SELECT AVG(e.day0_return)
            FROM events e
            WHERE e.sector = ? AND e.day0_date = ? AND e.ticker != ?
        """, (sector, day0_date, ticker))
        sector_avg_row = cursor.fetchone()
        if sector_avg_row and sector_avg_row[0] is not None:
            sector_avg = sector_avg_row[0]
            features['sector_relative_return_day0'] = day0_return - sector_avg

    # 9. Price as % of 52-week high
    day0_dt = datetime.strptime(day0_date, '%Y-%m-%d')
    year_ago = (day0_dt - timedelta(days=365)).strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT close FROM prices
        WHERE ticker = ? AND date >= ? AND date < ?
    """, (ticker, year_ago, day0_date))
    prices_52w = [row[0] for row in cursor.fetchall()]
    features['price_pct_of_52week_high'] = calculate_52week_position(close, prices_52w)

    # 10. Consecutive days same direction
    cursor.execute("""
        SELECT close FROM prices
        WHERE ticker = ? AND date < ?
        ORDER BY date DESC
        LIMIT 10
    """, (ticker, day0_date))
    recent_closes = [row[0] for row in cursor.fetchall()]
    if len(recent_closes) > 1:
        recent_returns = [(recent_closes[i] - recent_closes[i+1]) / recent_closes[i+1]
                          for i in range(len(recent_closes)-1)]
        features['consecutive_days_same_direction'] = calculate_consecutive_days(recent_returns)

    # 11. Move magnitude bucket
    features['move_magnitude_bucket'] = get_move_magnitude_bucket(day0_return_abs)

    return features


def calculate_all_features():
    """Calculate enhanced features for all events."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("CALCULATING ENHANCED FEATURES")
    print("=" * 60 + "\n")

    # Get all events
    cursor.execute("""
        SELECT id, ticker, day0_date, day0_return_abs
        FROM events
        ORDER BY day0_date
    """)
    events = cursor.fetchall()

    print(f"Processing {len(events)} events...\n")

    updated = 0
    failed = 0

    for i, (event_id, ticker, day0_date, day0_return_abs) in enumerate(events, 1):
        if i % 100 == 0:
            print(f"[{i}/{len(events)}] Processing {ticker} on {day0_date}...")
            conn.commit()  # Commit every 100 events

        try:
            features = calculate_features_for_event(event_id, ticker, day0_date, day0_return_abs, conn)

            # Update event with features
            update_parts = []
            update_values = []

            for feature_name, feature_value in features.items():
                update_parts.append(f"{feature_name} = ?")
                update_values.append(feature_value)

            if update_parts:
                update_values.append(event_id)
                cursor.execute(f"""
                    UPDATE events
                    SET {', '.join(update_parts)}
                    WHERE id = ?
                """, update_values)
                updated += 1

        except Exception as e:
            print(f"[ERROR] Failed to process event {event_id} ({ticker} on {day0_date}): {e}")
            failed += 1

    conn.commit()

    # Print summary statistics
    print("\n" + "=" * 60)
    print("FEATURE CALCULATION SUMMARY")
    print("=" * 60 + "\n")

    print(f"Events processed: {len(events)}")
    print(f"Successfully updated: {updated}")
    print(f"Failed: {failed}\n")

    # Show sample statistics for each feature
    features_to_check = [
        'intraday_volatility_pct',
        'gap_pct',
        'volume_surge_zscore',
        'drift_volatility_5d',
        'ticker_reversion_rate_historical',
        'vix_change_5d',
        'price_pct_of_52week_high',
        'consecutive_days_same_direction'
    ]

    print("Feature Statistics (non-null values):\n")
    for feature in features_to_check:
        cursor.execute(f"""
            SELECT
                COUNT(*) as count,
                AVG({feature}) as mean,
                MIN({feature}) as min,
                MAX({feature}) as max
            FROM events
            WHERE {feature} IS NOT NULL
        """)
        row = cursor.fetchone()
        if row:
            count, mean, min_val, max_val = row
            coverage = count / len(events) * 100 if len(events) > 0 else 0
            print(f"  {feature:35s} {count:4d} ({coverage:5.1f}%)  "
                  f"mean={mean:7.4f}  min={min_val:7.4f}  max={max_val:7.4f}")

    # Check move magnitude buckets
    print("\nMove Magnitude Distribution:")
    cursor.execute("""
        SELECT move_magnitude_bucket, COUNT(*)
        FROM events
        WHERE move_magnitude_bucket IS NOT NULL
        GROUP BY move_magnitude_bucket
        ORDER BY COUNT(*) DESC
    """)
    for bucket, count in cursor.fetchall():
        print(f"  {bucket:20s} {count:4d} ({count/len(events)*100:5.1f}%)")

    conn.close()

    print("\n" + "=" * 60)
    print("[OK] Enhanced features calculated successfully")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    calculate_all_features()
