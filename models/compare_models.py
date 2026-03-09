"""
Compare baseline vs catalyst-aware models.

Runs both models and shows side-by-side comparison.
Determines if catalyst detection is worth pursuing further.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from train_baseline import train_baseline_model
from train_catalyst_aware import train_catalyst_aware_model


def compare_models():
    """Run both models and compare results."""

    print("\n" + "=" * 80)
    print(" " * 20 + "MODEL COMPARISON: BASELINE VS CATALYST-AWARE")
    print("=" * 80 + "\n")

    # Train baseline
    print("STEP 1: Training baseline model (no catalyst detection)...\n")
    baseline_results = train_baseline_model()

    print("\n" + "-" * 80 + "\n")

    # Train catalyst-aware
    print("STEP 2: Training catalyst-aware model (with catalyst detection)...\n")
    catalyst_results = train_catalyst_aware_model()

    print("\n" + "=" * 80)
    print(" " * 30 + "FINAL COMPARISON")
    print("=" * 80 + "\n")

    # Side-by-side comparison
    baseline_acc = baseline_results['test_accuracy']
    catalyst_acc = catalyst_results['test_accuracy']
    improvement = catalyst_acc - baseline_acc
    improvement_pct = (improvement / baseline_acc) * 100

    print(f"{'Model':<30} {'Test Accuracy':>15} {'Improvement':>15}")
    print("-" * 80)
    print(f"{'Baseline (no catalyst):':<30} {baseline_acc:>14.1%}")
    print(f"{'Catalyst-Aware:':<30} {catalyst_acc:>14.1%} {improvement:>14.1%} ({improvement_pct:+.1f}%)")
    print()

    # Decision logic
    print("=" * 80)
    print(" " * 35 + "DECISION")
    print("=" * 80 + "\n")

    if improvement >= 0.03:  # 3% improvement
        print("✅ CATALYST DETECTION HELPS!")
        print(f"   Improvement: {improvement:.1%} ({improvement_pct:+.1f}%)")
        print()
        print("RECOMMENDATION: Proceed to Phase 3")
        print("  - Add news scraping (detect if there was news)")
        print("  - Add Reddit monitoring (social sentiment)")
        print("  - Add analyst upgrades/downgrades")
        print("  - Add 8-K guidance parsing")
        print()
        print("Expected timeline: 1-2 weeks")
        print("Expected accuracy with enhanced detection: 60-65%")
        print()

    elif improvement >= 0.01:  # 1-3% improvement
        print("⚠️  CATALYST DETECTION HELPS SLIGHTLY")
        print(f"   Improvement: {improvement:.1%} ({improvement_pct:+.1f}%)")
        print()
        print("RECOMMENDATION: Marginal benefit")
        print("  - Catalyst detection helps a little")
        print("  - Could proceed to Phase 3, but gains may be modest")
        print("  - Alternative: Try other feature engineering first")
        print()
        print("Consider:")
        print("  - Adding intraday volatility features")
        print("  - Short interest data")
        print("  - Options flow (if available)")
        print()

    else:  # <1% improvement or negative
        print("❌ CATALYST DETECTION DOESN'T HELP")
        print(f"   Change: {improvement:+.1%} ({improvement_pct:+.1f}%)")
        print()
        print("RECOMMENDATION: Pivot to different approach")
        print("  - Catalyst type isn't predictive of reversion")
        print("  - Don't invest 1-2 weeks building more catalyst detection")
        print()
        print("Alternative strategies to try:")
        print("  1. Post-earnings MOMENTUM (not reversion)")
        print("  2. Pairs trading (cointegration)")
        print("  3. Sector rotation")
        print("  4. Gap fills (intraday)")
        print("  5. Volatility selling (options)")
        print()
        print("See OPTION_C_ALTERNATIVES.md for details")
        print()

    # Feature importance insight
    print("-" * 80)
    print("\nTop 5 Features in Catalyst-Aware Model:")
    for i, row in catalyst_results['feature_importance'].head(5).iterrows():
        is_catalyst = 'catalyst_type' in row['feature']
        marker = " <-- CATALYST FEATURE" if is_catalyst else ""
        print(f"  {i+1}. {row['feature']:30s} (importance: {row['importance']:.4f}){marker}")

    print("\n" + "=" * 80)
    print(" " * 25 + "END OF COMPARISON")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    compare_models()
