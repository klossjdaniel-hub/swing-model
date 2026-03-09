"""
Train ENHANCED model with all new features.

Includes catalyst detection + sophisticated features:
- Emotion indicators (intraday volatility, volume surges, gaps)
- Historical patterns (ticker reversion tendency, consecutive moves)
- Market context (VIX changes, sector-relative, price levels)

Goal: Reach 70%+ accuracy
"""

import sys
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import get_connection

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def load_events():
    """Load events from database with ALL features."""
    conn = get_connection()

    query = """
        SELECT
            ticker,
            day0_date,
            sector,
            market_cap_bucket,
            catalyst_type,
            move_magnitude_bucket,

            -- Original features
            day0_return,
            day0_return_abs,
            direction,
            volume_ratio,
            pre_earnings_drift_5d,
            pre_earnings_drift_20d,
            vix_day0,
            day_of_week,

            -- Enhanced features
            intraday_volatility_pct,
            gap_pct,
            volume_surge_zscore,
            drift_volatility_5d,
            drift_volatility_20d,
            ticker_reversion_rate_historical,
            vix_change_5d,
            sector_relative_return_day0,
            price_pct_of_52week_high,
            consecutive_days_same_direction,

            -- Target
            reverted_day2
        FROM events
        WHERE reverted_day2 IS NOT NULL
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def prepare_features_enhanced(df):
    """
    Prepare ALL features for enhanced model.

    Returns: X (features), y (target), feature_names
    """
    # Create copy
    data = df.copy()

    # Fill missing values
    numeric_cols = [
        'pre_earnings_drift_5d', 'pre_earnings_drift_20d',
        'drift_volatility_5d', 'drift_volatility_20d',
        'ticker_reversion_rate_historical',
        'sector_relative_return_day0',
        'gap_pct'
    ]
    for col in numeric_cols:
        if col in data.columns:
            data[col] = data[col].fillna(0)

    # Fill VIX with median
    data['vix_day0'] = data['vix_day0'].fillna(data['vix_day0'].median())
    data['vix_change_5d'] = data['vix_change_5d'].fillna(0)

    # Fill price level with 0.8 (typical value)
    data['price_pct_of_52week_high'] = data['price_pct_of_52week_high'].fillna(0.8)

    # Fill consecutive days with 1 (default)
    data['consecutive_days_same_direction'] = data['consecutive_days_same_direction'].fillna(1)

    # One-hot encode categorical features
    data = pd.get_dummies(data, columns=[
        'sector',
        'market_cap_bucket',
        'catalyst_type',
        'move_magnitude_bucket'
    ], drop_first=True)

    # Select all features
    feature_cols = [
        # Original features
        'day0_return_abs',
        'direction',
        'volume_ratio',
        'pre_earnings_drift_5d',
        'pre_earnings_drift_20d',
        'vix_day0',
        'day_of_week',

        # Enhanced features
        'intraday_volatility_pct',
        'gap_pct',
        'volume_surge_zscore',
        'drift_volatility_5d',
        'drift_volatility_20d',
        'ticker_reversion_rate_historical',
        'vix_change_5d',
        'sector_relative_return_day0',
        'price_pct_of_52week_high',
        'consecutive_days_same_direction',
    ]

    # Add one-hot encoded columns
    sector_cols = [col for col in data.columns if col.startswith('sector_')]
    market_cap_cols = [col for col in data.columns if col.startswith('market_cap_bucket_')]
    catalyst_cols = [col for col in data.columns if col.startswith('catalyst_type_')]
    magnitude_cols = [col for col in data.columns if col.startswith('move_magnitude_bucket_')]

    feature_cols.extend(sector_cols)
    feature_cols.extend(market_cap_cols)
    feature_cols.extend(catalyst_cols)
    feature_cols.extend(magnitude_cols)

    # Convert to numpy arrays to avoid pandas/xgboost compatibility issues
    X = data[feature_cols].values.astype('float64')
    y = data['reverted_day2'].values.astype('int32')

    return X, y, feature_cols


def train_enhanced_model():
    """Train enhanced XGBoost model with all features."""

    print("\n" + "=" * 60)
    print("ENHANCED MODEL (ALL FEATURES)")
    print("=" * 60 + "\n")

    # Load data
    print("[1/5] Loading events with enhanced features...")
    df = load_events()
    print(f"      Loaded {len(df)} events\n")

    # Prepare features
    print("[2/5] Preparing enhanced features...")
    X, y, feature_names = prepare_features_enhanced(df)
    print(f"      Total features: {len(feature_names)}")

    # Show feature categories
    original = len([f for f in feature_names if f in [
        'day0_return_abs', 'direction', 'volume_ratio',
        'pre_earnings_drift_5d', 'pre_earnings_drift_20d',
        'vix_day0', 'day_of_week'
    ]])
    enhanced = len([f for f in feature_names if f in [
        'intraday_volatility_pct', 'gap_pct', 'volume_surge_zscore',
        'drift_volatility_5d', 'drift_volatility_20d',
        'ticker_reversion_rate_historical', 'vix_change_5d',
        'sector_relative_return_day0', 'price_pct_of_52week_high',
        'consecutive_days_same_direction'
    ]])
    categorical = len(feature_names) - original - enhanced

    print(f"        Original features: {original}")
    print(f"        Enhanced features: {enhanced}")
    print(f"        Categorical (one-hot): {categorical}")
    print(f"      Target balance: {y.mean():.1%} revert, {1-y.mean():.1%} don't revert\n")

    # Train/test split (80/20)
    print("[3/5] Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"      Train: {len(X_train)} events")
    print(f"      Test: {len(X_test)} events\n")

    # Train XGBoost
    print("[4/5] Training XGBoost model...")
    model = xgb.XGBClassifier(
        n_estimators=150,  # More trees
        max_depth=6,       # Slightly deeper
        learning_rate=0.08,  # Slightly slower learning
        random_state=42,
        eval_metric='logloss',
        subsample=0.8,     # Sample 80% of data for each tree
        colsample_bytree=0.8  # Sample 80% of features for each tree
    )

    model.fit(X_train, y_train, verbose=False)
    print("      Model trained\n")

    # Evaluate
    print("[5/5] Evaluating model...\n")

    # Training accuracy
    y_train_pred = model.predict(X_train)
    train_acc = accuracy_score(y_train, y_train_pred)

    # Test accuracy
    y_test_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, y_test_pred)

    print("=" * 60)
    print("RESULTS")
    print("=" * 60 + "\n")

    print(f"Training Accuracy: {train_acc:.1%}")
    print(f"Test Accuracy: {test_acc:.1%}")
    print(f"Baseline (always predict majority): {1-y_test.mean():.1%}\n")

    # Classification report
    print("Classification Report (Test Set):")
    print(classification_report(y_test, y_test_pred,
                                target_names=['No Revert', 'Revert'],
                                digits=3))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_test_pred)
    print("\nConfusion Matrix (Test Set):")
    print(f"                Predicted No | Predicted Yes")
    print(f"Actual No       {cm[0,0]:>12} | {cm[0,1]:>13}")
    print(f"Actual Yes      {cm[1,0]:>12} | {cm[1,1]:>13}\n")

    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("Top 20 Most Important Features:")
    for i, row in feature_importance.head(20).iterrows():
        # Highlight feature types
        feature_type = ""
        if 'catalyst_type' in row['feature']:
            feature_type = " <-- CATALYST"
        elif row['feature'] in ['intraday_volatility_pct', 'gap_pct', 'volume_surge_zscore',
                                 'drift_volatility_5d', 'drift_volatility_20d',
                                 'ticker_reversion_rate_historical', 'vix_change_5d',
                                 'sector_relative_return_day0', 'price_pct_of_52week_high',
                                 'consecutive_days_same_direction']:
            feature_type = " <-- ENHANCED"

        print(f"  {row['feature']:40s} {row['importance']:.4f}{feature_type}")

    print("\n" + "=" * 60)
    print(f"ENHANCED MODEL ACCURACY: {test_acc:.1%}")
    print("=" * 60 + "\n")

    return {
        'model': model,
        'test_accuracy': test_acc,
        'train_accuracy': train_acc,
        'feature_importance': feature_importance,
        'y_test': y_test,
        'y_test_pred': y_test_pred
    }


if __name__ == "__main__":
    results = train_enhanced_model()
