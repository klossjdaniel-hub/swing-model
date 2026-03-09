"""
Add enhanced feature columns to events table.

These features use only existing price/volume data - no new APIs needed.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import get_connection

def migrate():
    """Add enhanced feature columns to events table."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("DATABASE MIGRATION: Adding Enhanced Feature Columns")
    print("=" * 60 + "\n")

    columns_to_add = [
        ("intraday_volatility_pct", "REAL"),
        ("gap_pct", "REAL"),
        ("volume_surge_zscore", "REAL"),
        ("drift_volatility_5d", "REAL"),
        ("drift_volatility_20d", "REAL"),
        ("ticker_reversion_rate_historical", "REAL"),
        ("vix_change_5d", "REAL"),
        ("sector_relative_return_day0", "REAL"),
        ("price_pct_of_52week_high", "REAL"),
        ("consecutive_days_same_direction", "INTEGER"),
        ("move_magnitude_bucket", "TEXT"),
    ]

    # Check existing columns
    cursor.execute("PRAGMA table_info(events)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    added = 0
    skipped = 0

    for col_name, col_type in columns_to_add:
        if col_name in existing_columns:
            print(f"[SKIP] {col_name} already exists")
            skipped += 1
        else:
            try:
                cursor.execute(f"ALTER TABLE events ADD COLUMN {col_name} {col_type}")
                print(f"[OK]   Added {col_name} ({col_type})")
                added += 1
            except Exception as e:
                print(f"[ERROR] Failed to add {col_name}: {e}")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print(f"Migration complete: {added} added, {skipped} skipped")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    migrate()
