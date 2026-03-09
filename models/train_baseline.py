"""
Train baseline model WITHOUT catalyst detection.

This establishes our accuracy floor. Any catalyst-aware model should beat this.

Features: move size, volume, drift, VIX, sector, etc.
Target: reverted_day2 (binary classification)
"""

import sys
import os
import sqlite3
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
    """Load events from database."""
    conn = get_connection()

    query = """
        SELECT
            ticker,
            day0_date,
            sector,
            market_cap_bucket,
            catalyst_type,
            day0_return,
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


def prepare_features_baseline(df):
    """
    Prepare features for BASELINE model (no catalyst info).

    Returns: X (features), y (target), feature_names
    """
    # Create copy
    data = df.copy()

    # Fill missing values
    data['pre_earnings_drift_5d'] = data['pre_earnings_drift_5d'].fillna(0)
    data['pre_earnings_drift_20d'] = data['pre_earnings_drift_20d'].fillna(0)
    data['vix_day0'] = data['vix_day0'].fillna(data['vix_day0'].median())

    # One-hot encode categorical features
    data = pd.get_dummies(data, columns=['sector', 'market_cap_bucket'], drop_first=True)

    # Select features (NO catalyst_type!)
    feature_cols = [
        'day0_return_abs',
        'direction',
        'volume_ratio',
        'pre_earnings_drift_5d',
        'pre_earnings_drift_20d',
        'vix_day0',
        'day_of_week',
    ]

    # Add one-hot encoded columns
    sector_cols = [col for col in data.columns if col.startswith('sector_')]
    market_cap_cols = [col for col in data.columns if col.startswith('market_cap_bucket_')]

    feature_cols.extend(sector_cols)
    feature_cols.extend(market_cap_cols)

    X = data[feature_cols]
    y = data['reverted_day2']

    return X, y, feature_cols


def train_baseline_model():
    """Train baseline XGBoost model without catalyst detection."""

    print("\n" + "=" * 60)
    print("BASELINE MODEL (NO CATALYST DETECTION)")
    print("=" * 60 + "\n")

    # Load data
    print("[1/5] Loading events from database...")
    df = load_events()
    print(f"      Loaded {len(df)} events\n")

    # Prepare features
    print("[2/5] Preparing features (NO catalyst_type)...")
    X, y, feature_names = prepare_features_baseline(df)
    print(f"      Features: {len(feature_names)}")
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
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
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

    print("Top 10 Most Important Features:")
    for i, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']:30s} {row['importance']:.4f}")

    print("\n" + "=" * 60)
    print(f"BASELINE ACCURACY: {test_acc:.1%}")
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
    results = train_baseline_model()
