"""
Detect big moves and generate predictions using trained model.

This is the core daily pipeline:
1. Check latest prices for big moves (>2%, >1.5x volume)
2. Classify catalyst type
3. Calculate features
4. Load trained model
5. Generate predictions
6. Store in forward_predictions table
"""

import sys
import os
from datetime import datetime, timedelta
import pickle
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from data.db import get_connection
from universe import UNIVERSE

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def get_latest_trading_day(conn):
    """Get the most recent trading day with data."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(date) FROM prices
        WHERE ticker IN ({})
    """.format(','.join('?' * len(UNIVERSE))), UNIVERSE)
    return cursor.fetchone()[0]


def get_price_data(ticker, date, conn):
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


def get_previous_close(ticker, date, conn):
    """Get previous day's close."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT close FROM prices
        WHERE ticker = ? AND date < ?
        ORDER BY date DESC
        LIMIT 1
    """, (ticker, date))
    row = cursor.fetchone()
    return row[0] if row else None


def get_avg_volume(ticker, date, days, conn):
    """Get average volume for N days before date."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(volume) FROM prices
        WHERE ticker = ? AND date < ? AND volume > 0
        ORDER BY date DESC
        LIMIT ?
    """, (ticker, date, days))
    row = cursor.fetchone()
    return row[0] if row and row[0] else None


def classify_catalyst(ticker, date, prices, prev_close, conn):
    """Classify catalyst type: earnings, gap, or unknown."""
    cursor = conn.cursor()

    # Check if earnings day
    cursor.execute("""
        SELECT COUNT(*) FROM earnings_raw
        WHERE ticker = ? AND report_date = ?
    """, (ticker, date))
    if cursor.fetchone()[0] > 0:
        return 'earnings'

    # Check for gap (>1%)
    if prev_close and prices:
        gap_size = abs(prices['open'] - prev_close) / prev_close
        if gap_size > 0.01:
            return 'gap'

    return 'unknown'


def calculate_features(ticker, date, prices, prev_close, catalyst_type, conn):
    """Calculate all features needed for prediction."""
    cursor = conn.cursor()

    features = {}

    # Move characteristics
    day0_return = (prices['close'] - prev_close) / prev_close
    features['day0_return_abs'] = abs(day0_return)
    features['direction'] = 1 if day0_return > 0 else -1

    # Volume ratio
    avg_volume = get_avg_volume(ticker, date, 20, conn)
    if avg_volume and avg_volume > 0:
        features['volume_ratio'] = prices['volume'] / avg_volume
    else:
        features['volume_ratio'] = 1.0

    # Pre-drift (5 and 20 day)
    cursor.execute("""
        SELECT close FROM prices
        WHERE ticker = ? AND date < ?
        ORDER BY date DESC
        LIMIT 21
    """, (ticker, date))
    closes = [row[0] for row in cursor.fetchall()]

    if len(closes) >= 6:
        drift_5d = (closes[0] - closes[5]) / closes[5]
        features['pre_earnings_drift_5d'] = drift_5d
    else:
        features['pre_earnings_drift_5d'] = 0.0

    if len(closes) >= 21:
        drift_20d = (closes[0] - closes[20]) / closes[20]
        features['pre_earnings_drift_20d'] = drift_20d
    else:
        features['pre_earnings_drift_20d'] = 0.0

    # VIX
    cursor.execute("SELECT close FROM vix WHERE date = ?", (date,))
    vix_row = cursor.fetchone()
    features['vix_day0'] = vix_row[0] if vix_row else 20.0  # Default VIX

    # Day of week
    features['day_of_week'] = datetime.strptime(date, '%Y-%m-%d').weekday()

    # Catalyst type (one-hot encoded)
    features['catalyst_type_gap'] = 1.0 if catalyst_type == 'gap' else 0.0
    features['catalyst_type_unknown'] = 1.0 if catalyst_type == 'unknown' else 0.0

    # Sector (one-hot encoded)
    cursor.execute("SELECT sector FROM company_info WHERE ticker = ?", (ticker,))
    sector_row = cursor.fetchone()
    sector = sector_row[0] if sector_row else 'Other'

    features['sector_Financials'] = 1.0 if sector == 'Financials' else 0.0
    features['sector_Other'] = 1.0 if sector == 'Other' else 0.0
    features['sector_Technology'] = 1.0 if sector == 'Technology' else 0.0

    # Market cap bucket
    cursor.execute("SELECT market_cap_bucket FROM company_info WHERE ticker = ?", (ticker,))
    cap_row = cursor.fetchone()
    cap_bucket = cap_row[0] if cap_row else 'mid'

    features['market_cap_bucket_mid'] = 1.0 if cap_bucket == 'mid' else 0.0
    features['market_cap_bucket_small'] = 1.0 if cap_bucket == 'small' else 0.0

    return features


def load_model():
    """Load the trained catalyst-aware model."""
    # For now, we'll need to save the model first
    # This is a placeholder - we'll train and save it
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'catalyst_aware_model.pkl')

    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            # Extract the actual model from the dict
            return model_data['model'] if isinstance(model_data, dict) else model_data
    else:
        print(f"[ERROR] Model not found at {model_path}")
        print("       Run models/save_model.py first to train and save the model")
        return None


def generate_predictions():
    """Main pipeline: detect moves and generate predictions."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("DETECTING BIG MOVES & GENERATING PREDICTIONS")
    print("=" * 60 + "\n")

    # Load model first
    print("Loading trained model...")
    model = load_model()
    if not model:
        print("[ERROR] Cannot proceed without model")
        return
    print("[OK] Model loaded\n")

    # Feature names (must match training order!)
    feature_names = [
        'day0_return_abs', 'direction', 'volume_ratio',
        'pre_earnings_drift_5d', 'pre_earnings_drift_20d',
        'vix_day0', 'day_of_week',
        'sector_Financials', 'sector_Other', 'sector_Technology',
        'market_cap_bucket_mid', 'market_cap_bucket_small',
        'catalyst_type_gap', 'catalyst_type_unknown'
    ]

    predictions_made = 0
    moves_detected = 0

    print("Scanning for big moves...\n")
    print("Checking each stock's latest available date...\n")

    for ticker in UNIVERSE:
        # Get this stock's latest available date
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(date) FROM prices WHERE ticker = ?
        """, (ticker,))
        latest_date = cursor.fetchone()[0]

        if not latest_date:
            continue

        # Get today's data for this stock
        prices = get_price_data(ticker, latest_date, conn)
        if not prices:
            continue

        prev_close = get_previous_close(ticker, latest_date, conn)
        if not prev_close:
            continue

        # Calculate return
        day0_return = (prices['close'] - prev_close) / prev_close
        day0_return_abs = abs(day0_return)

        # Filter: >2% move
        if day0_return_abs < 0.02:
            continue

        # Filter: >1.5x volume
        avg_volume = get_avg_volume(ticker, latest_date, 20, conn)
        if not avg_volume or avg_volume <= 0:
            continue

        volume_ratio = prices['volume'] / avg_volume
        if volume_ratio < 1.5:
            continue

        moves_detected += 1

        # Classify catalyst
        catalyst_type = classify_catalyst(ticker, latest_date, prices, prev_close, conn)

        # Calculate features
        features = calculate_features(ticker, latest_date, prices, prev_close, catalyst_type, conn)

        # Create feature vector (must match training order!)
        X = np.array([[features.get(f, 0.0) for f in feature_names]])

        # Generate prediction
        reversion_prob = model.predict_proba(X)[0][1]  # Probability of reversion
        predicted_direction = 1 if reversion_prob >= 0.5 else 0

        # Confidence tier
        if reversion_prob >= 0.65:
            confidence = 'high'
        elif reversion_prob >= 0.55:
            confidence = 'medium'
        else:
            confidence = 'low'

        # Store prediction
        cursor.execute("""
            INSERT INTO forward_predictions (
                prediction_timestamp,
                ticker,
                day0_date,
                predicted_direction,
                reversion_prob_day2,
                confidence_tier,
                model_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ticker,
            latest_date,
            predicted_direction,
            reversion_prob,
            confidence,
            'catalyst_aware_v1'
        ))

        predictions_made += 1

        # Print high-confidence predictions
        if confidence == 'high':
            direction_str = "UP" if features['direction'] == 1 else "DOWN"
            action = "FADE (short)" if predicted_direction == 1 and features['direction'] == 1 else "FADE (long)"
            if predicted_direction == 1 and features['direction'] == -1:
                action = "FADE (long)"

            print(f"[HIGH CONFIDENCE] {ticker}")
            print(f"  Move: {direction_str} {day0_return_abs*100:.1f}% (volume {volume_ratio:.1f}x)")
            print(f"  Catalyst: {catalyst_type}")
            print(f"  Prediction: {reversion_prob*100:.1f}% chance of reversion")
            print(f"  Action: {action}\n")

    conn.commit()
    conn.close()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60 + "\n")
    print(f"Big moves detected: {moves_detected}")
    print(f"Predictions generated: {predictions_made}\n")

    print("[OK] Predictions stored in forward_predictions table")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    generate_predictions()
