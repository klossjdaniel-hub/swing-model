"""
Main entry point for swing-model data pipeline.

Run entire Phase 1 pipeline in sequence.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

import config
from data import db
from data import fetch_vix
from data import fetch_company_info
from data import fetch_earnings
from data import fetch_prices

def run_phase1():
    """Run complete Phase 1 data pipeline."""
    print("\n" + "=" * 70)
    print(" SWING MODEL - PHASE 1: DATA PIPELINE")
    print("=" * 70 + "\n")

    try:
        # Validate configuration
        print("Step 0: Validating configuration...")
        config.validate_config(phase="phase1")
        print()

        # Step 1: Create database schema
        print("Step 1: Creating database schema...")
        db.create_tables()
        print()

        # Step 2: Fetch VIX data (smoke test)
        print("Step 2: Fetching VIX data...")
        fetch_vix.main()
        print()

        # Step 3: Fetch company metadata
        print("Step 3: Fetching company metadata from Finnhub...")
        fetch_company_info.main()
        print()

        # Step 4: Fetch earnings data
        print("Step 4: Fetching earnings data from Finnhub...")
        fetch_earnings.main()
        print()

        # Step 5: Fetch historical prices
        print("Step 5: Fetching historical prices (this will take a while)...")
        print("Estimated time: ~5-10 minutes for 50 stocks\n")
        fetch_prices.main()
        print()

        # Success summary
        print("\n" + "=" * 70)
        print(" ✓ PHASE 1 COMPLETE!")
        print("=" * 70)
        print(f"\nDatabase created at: {config.DB_PATH}")
        print("\nNext steps:")
        print("  1. Review data quality: Check logs above for any warnings")
        print("  2. Build events dataset: Run data/build_events.py")
        print("  3. Validate dataset: Run data/validate_dataset.py")
        print("\nThen proceed to Phase 2: Model training")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_phase1()
