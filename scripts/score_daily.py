"""
Daily scoring script - Phase 3 only.

Runs weekdays at 4pm ET via GitHub Actions.
Fetches closing prices, scores predictions, updates Supabase.

TODO: Implement this in Phase 3 after model is trained.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def main():
    """Main scoring workflow."""
    print("=" * 60)
    print("SWING MODEL - DAILY SCORING")
    print("=" * 60)
    print("\n⚠ This script is not yet implemented (Phase 3)")
    print("\nThis script will:")
    print("  1. Fetch closing prices from Eulerpool/Finnhub")
    print("  2. Find predictions where day+1/day+2/day+3 are now known")
    print("  3. Calculate actual returns")
    print("  4. Apply reversion labels")
    print("  5. Update Supabase with actuals + scored_at timestamp")
    print("\nCurrent phase: Phase 1 (Data Pipeline)")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
