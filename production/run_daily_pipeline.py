"""
Daily pipeline orchestrator.

Run this once per day (after market close) to:
1. Fetch latest prices
2. Detect big moves and generate predictions
3. Score previous predictions

Recommended: Schedule with Windows Task Scheduler for 6 PM ET daily
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Import pipeline steps
from fetch_daily_prices import fetch_daily_prices
from detect_and_predict import generate_predictions
from score_predictions import score_predictions


def run_daily_pipeline():
    """Run the complete daily pipeline."""

    print("\n" + "=" * 80)
    print(" " * 25 + "DAILY PAPER TRADING PIPELINE")
    print("=" * 80)
    print(f"\nRun time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("=" * 80 + "\n")

    # Step 1: Fetch prices
    print("STEP 1/3: Fetching latest prices from Finnhub...\n")
    try:
        fetch_daily_prices()
    except Exception as e:
        print(f"[ERROR] Failed to fetch prices: {e}\n")
        print("Continuing with next steps...\n")

    # Step 2: Detect and predict
    print("STEP 2/3: Detecting big moves and generating predictions...\n")
    try:
        generate_predictions()
    except Exception as e:
        print(f"[ERROR] Failed to generate predictions: {e}\n")
        print("Continuing with next steps...\n")

    # Step 3: Score old predictions
    print("STEP 3/3: Scoring previous predictions...\n")
    try:
        score_predictions()
    except Exception as e:
        print(f"[ERROR] Failed to score predictions: {e}\n")

    # Final summary
    print("\n" + "=" * 80)
    print(" " * 30 + "PIPELINE COMPLETE")
    print("=" * 80 + "\n")
    print("Next steps:")
    print("  1. Check forward_predictions table for today's predictions")
    print("  2. Review performance dashboard: python production/dashboard.py")
    print("  3. Check high-confidence predictions above\n")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_daily_pipeline()
