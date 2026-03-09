"""
Add catalyst_type column to events table.

This is a one-time migration for the Ultra-Minimal catalyst detection approach.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import get_connection

def migrate():
    """Add catalyst_type column to events table."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("DATABASE MIGRATION: Adding catalyst_type column")
    print("=" * 60 + "\n")

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(events)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'catalyst_type' in columns:
            print("[OK] Column 'catalyst_type' already exists")
        else:
            # Add column
            cursor.execute("""
                ALTER TABLE events ADD COLUMN catalyst_type TEXT
            """)
            conn.commit()
            print("[OK] Added column 'catalyst_type' to events table")

        # Create index for faster filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_catalyst_type
            ON events(catalyst_type)
        """)
        conn.commit()
        print("[OK] Created index on catalyst_type")

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

    print("\n" + "=" * 60)
    print("[OK] Migration complete")
    print("=" * 60 + "\n")
    return True


if __name__ == "__main__":
    migrate()
