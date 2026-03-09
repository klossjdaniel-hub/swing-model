"""
Train the catalyst-aware model and save it for production use.

This creates the model file that production scripts will load.
"""

import sys
import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import xgboost as xgb

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import get_connection

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def load_events():
    """Load events from database."""
    conn = get_connection()

    query = """
        SELECT
            sector,
            market_cap_bucket,
            catalyst_type,
            day0_return_abs,
            direction,
            volume_ratio,
            pre_earnings_drift_5d,
            pre_earnings_drift_20d,
            vix_day0,
            day_of_week,
            reverted_day2
        FROM events
        WHERE reverted_day2 IS NOT NULL
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def prepare_features(df):
    """Prepare features matching production pipeline."""
    data = df.copy()

    # Fill missing values
    data['pre_earnings_drift_5d'] = data['pre_earnings_drift_5d'].fillna(0)
    data['pre_earnings_drift_20d'] = data['pre_earnings_drift_20d'].fillna(0)
    data['vix_day0'] = data['vix_day0'].fillna(data['vix_day0'].median())

    # One-hot encode
    data = pd.get_dummies(data, columns=['sector', 'market_cap_bucket', 'catalyst_type'], drop_first=True)

    # Feature columns (MUST MATCH PRODUCTION ORDER!)
    base_cols = [
        'day0_return_abs',
        'direction',
        'volume_ratio',
        'pre_earnings_drift_5d',
        'pre_earnings_drift_20d',
        'vix_day0',
        'day_of_week'
    ]

    # Add one-hot columns that exist
    optional_cols = [
        'sector_Financials',
        'sector_Other',
        'sector_Technology',
        'market_cap_bucket_mid',
        'market_cap_bucket_small',
        'catalyst_type_gap',
        'catalyst_type_unknown'
    ]

    feature_cols = base_cols.copy()

    # Add only columns that exist
    for col in optional_cols:
        if col in data.columns:
            feature_cols.append(col)
        else:
            # Create missing column with zeros
            data[col] = 0.0
            feature_cols.append(col)

    X = data[feature_cols].values.astype('float64')
    y = data['reverted_day2'].values.astype('int32')

    return X, y, feature_cols


def train_and_save_model():
    """Train model and save to disk."""

    print("\n" + "=" * 60)
    print("TRAINING & SAVING CATALYST-AWARE MODEL")
    print("=" * 60 + "\n")

    # Load data
    print("[1/4] Loading training data...")
    df = load_events()
    print(f"      Loaded {len(df)} events\n")

    # Prepare features
    print("[2/4] Preparing features...")
    X, y, feature_names = prepare_features(df)
    print(f"      Features: {len(feature_names)}\n")

    # Train on ALL data (not train/test split - we want full model for production)
    print("[3/4] Training XGBoost on full dataset...")
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )

    model.fit(X, y, verbose=False)
    print("      Model trained\n")

    # Save model
    print("[4/4] Saving model to disk...")
    model_path = os.path.join(os.path.dirname(__file__), 'catalyst_aware_model.pkl')

    model_data = {
        'model': model,
        'feature_names': feature_names,
        'version': 'catalyst_aware_v1',
        'trained_on': len(df),
        'train_date': pd.Timestamp.now().strftime('%Y-%m-%d')
    }

    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)

    print(f"      Saved to: {model_path}\n")

    # Show model info
    print("=" * 60)
    print("MODEL INFO")
    print("=" * 60 + "\n")
    print(f"Version: {model_data['version']}")
    print(f"Trained on: {model_data['trained_on']} events")
    print(f"Train date: {model_data['train_date']}")
    print(f"Features: {len(feature_names)}")
    print(f"\nFeature list:")
    for i, feat in enumerate(feature_names, 1):
        print(f"  {i:2d}. {feat}")

    # Test prediction
    print("\n" + "=" * 60)
    print("TEST PREDICTION")
    print("=" * 60 + "\n")

    test_features = np.array([[
        0.05,  # day0_return_abs (5% move)
        1,     # direction (up)
        2.5,   # volume_ratio (2.5x volume)
        0.01,  # pre_earnings_drift_5d (1% drift)
        0.02,  # pre_earnings_drift_20d (2% drift)
        25.0,  # vix_day0
        2,     # day_of_week (Wednesday)
        0,     # sector_Financials
        1,     # sector_Other
        0,     # sector_Technology
        1,     # market_cap_bucket_mid
        0,     # market_cap_bucket_small
        0,     # catalyst_type_gap
        1      # catalyst_type_unknown
    ]])

    prob = model.predict_proba(test_features)[0][1]
    print("Test case: 5% up move, unknown catalyst, 2.5x volume")
    print(f"Prediction: {prob*100:.1f}% chance of reversion\n")

    print("=" * 60)
    print("[OK] Model saved and ready for production")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    train_and_save_model()
