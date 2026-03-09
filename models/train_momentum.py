"""
Train MOMENTUM model (PEAD - Post-Earnings Announcement Drift).

Instead of predicting REVERSION, predict CONTINUATION.
Target: continued_day20 (will the move continue in same direction for 20 days?)
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
    """Load events from database."""
    conn = get_connection()

    query = """
        SELECT
            ticker,
            day0_date,
            sector,
            market_cap_bucket,
            catalyst_type,

            -- Features
            day0_return,
            day0_return_abs,
            direction,
            volume_ratio,
            pre_earnings_drift_5d,
            pre_earnings_drift_20d,
            vix_day0,
            day_of_week,
            intraday_volatility_pct,
            gap_pct,
            vix_change_5d,

            -- Target (MOMENTUM - not reversion!)
            continued_day20
        FROM events
        WHERE continued_day20 IS NOT NULL
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def prepare_features_momentum(df):
    """
    Prepare features for MOMENTUM model.

    Returns: X (features), y (target), feature_names
    """
    # Create copy
    data = df.copy()

    # Fill missing values
    data['pre_earnings_drift_5d'] = data['pre_earnings_drift_5d'].fillna(0)
    data['pre_earnings_drift_20d'] = data['pre_earnings_drift_20d'].fillna(0)
    data['vix_day0'] = data['vix_day0'].fillna(data['vix_day0'].median())
    data['vix_change_5d'] = data['vix_change_5d'].fillna(0)
    data['gap_pct'] = data['gap_pct'].fillna(0)
    data['intraday_volatility_pct'] = data['intraday_volatility_pct'].fillna(data['intraday_volatility_pct'].median())

    # One-hot encode categorical features
    data = pd.get_dummies(data, columns=['sector', 'market_cap_bucket', 'catalyst_type'], drop_first=True)

    # Select features
    feature_cols = [
        'day0_return_abs',
        'direction',
        'volume_ratio',
        'pre_earnings_drift_5d',
        'pre_earnings_drift_20d',
        'vix_day0',
        'day_of_week',
        'intraday_volatility_pct',
        'gap_pct',
        'vix_change_5d',
    ]

    # Add one-hot encoded columns
    sector_cols = [col for col in data.columns if col.startswith('sector_')]
    market_cap_cols = [col for col in data.columns if col.startswith('market_cap_bucket_')]
    catalyst_cols = [col for col in data.columns if col.startswith('catalyst_type_')]

    feature_cols.extend(sector_cols)
    feature_cols.extend(market_cap_cols)
    feature_cols.extend(catalyst_cols)

    # Convert to numpy
    X = data[feature_cols].values.astype('float64')
    y = data['continued_day20'].values.astype('int32')

    return X, y, feature_cols


def train_momentum_model():
    """Train XGBoost model to predict MOMENTUM (continuation)."""

    print("\n" + "=" * 60)
    print("MOMENTUM MODEL (PEAD - Post-Earnings Drift)")
    print("=" * 60 + "\n")
    print("Target: Will the move CONTINUE in same direction for 20 days?")
    print("(Opposite of reversion strategy)\n")

    # Load data
    print("[1/5] Loading events...")
    df = load_events()
    print(f"      Loaded {len(df)} events\n")

    # Show continuation rates
    print("      Overall continuation rate (Day 20):")
    cont_rate = df['continued_day20'].mean()
    print(f"        {cont_rate:.1%} continue, {1-cont_rate:.1%} don't continue\n")

    # By direction
    up_moves = df[df['direction'] == 1]
    down_moves = df[df['direction'] == -1]
    print(f"      Up moves:   {up_moves['continued_day20'].mean():.1%} continue")
    print(f"      Down moves: {down_moves['continued_day20'].mean():.1%} continue\n")

    # Prepare features
    print("[2/5] Preparing features...")
    X, y, feature_names = prepare_features_momentum(df)
    print(f"      Features: {len(feature_names)}\n")

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
                                target_names=['No Continue', 'Continue'],
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

    print("Top 15 Most Important Features:")
    for i, row in feature_importance.head(15).iterrows():
        feature_type = ""
        if 'catalyst_type' in row['feature']:
            feature_type = " <-- CATALYST"
        print(f"  {row['feature']:40s} {row['importance']:.4f}{feature_type}")

    print("\n" + "=" * 60)
    print(f"MOMENTUM MODEL ACCURACY: {test_acc:.1%}")
    print("=" * 60 + "\n")

    # CRITICAL COMPARISON
    print("=" * 60)
    print("COMPARISON TO REVERSION MODEL")
    print("=" * 60 + "\n")

    reversion_acc = 0.677  # Our best reversion model
    improvement = test_acc - reversion_acc

    print(f"Reversion Model (best):  {reversion_acc:.1%}")
    print(f"Momentum Model (new):    {test_acc:.1%}")
    print(f"Difference:              {improvement:+.1%}\n")

    if test_acc >= 0.70:
        print("✅ BREAKTHROUGH! Momentum beats 70% threshold!")
        print("   Recommendation: Proceed with PEAD momentum strategy")
        print("   Expected: 60-70% win rate in live trading")
    elif test_acc > reversion_acc + 0.02:
        print("✅ MOMENTUM WINS! Significantly better than reversion")
        print("   Recommendation: Pivot to momentum strategy")
    elif test_acc > reversion_acc:
        print("⚠️  MOMENTUM SLIGHTLY BETTER")
        print("   Marginal improvement - consider hybrid approach")
    else:
        print("❌ REVERSION STILL BETTER")
        print("   Stick with 67.7% reversion model")

    print("\n" + "=" * 60 + "\n")

    return {
        'model': model,
        'test_accuracy': test_acc,
        'train_accuracy': train_acc,
        'feature_importance': feature_importance,
        'y_test': y_test,
        'y_test_pred': y_test_pred
    }


if __name__ == "__main__":
    results = train_momentum_model()
