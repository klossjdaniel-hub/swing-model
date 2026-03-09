"""
Add PEAD (Post-Earnings Announcement Drift) outcome columns.

Calculate 5, 10, 20, and 60-day forward returns for momentum testing.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import get_connection

def migrate():
    """Add PEAD outcome columns to events table."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("DATABASE MIGRATION: Adding PEAD Outcome Columns")
    print("=" * 60 + "\n")

    columns_to_add = [
        ("return_day5", "REAL"),
        ("return_day10", "REAL"),
        ("return_day20", "REAL"),
        ("return_day60", "REAL"),
        ("continued_day5", "INTEGER"),
        ("continued_day10", "INTEGER"),
        ("continued_day20", "INTEGER"),
        ("continued_day60", "INTEGER"),
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
