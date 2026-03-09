"""
Fetch VIX historical data using yfinance.

This is the smoke test script - run this first to verify setup.
Fast, free, no API key needed.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
import config
from data.db import get_connection

def fetch_vix_data(start_date=config.START_DATE):
    """
    Fetch VIX daily closes from Yahoo Finance.

    Args:
        start_date: Start date for historical data (default: 2020-01-01)

    Returns:
        DataFrame with dates and VIX closes
    """
    print(f"Fetching VIX data from {start_date}...")

    try:
        # Download VIX data
        vix = yf.download("^VIX", start=start_date, progress=False)

        if vix.empty:
            raise ValueError("No VIX data returned from yfinance")

        # Extract close prices and reset index
        vix_close = vix[['Close']].reset_index()
        vix_close.columns = ['date', 'close']

        # Convert date to string format
        vix_close['date'] = vix_close['date'].dt.strftime('%Y-%m-%d')

        print(f"✓ Fetched {len(vix_close)} days of VIX data")
        return vix_close

    except Exception as e:
        print(f"✗ Error fetching VIX data: {e}")
        raise

def store_vix_data(vix_df):
    """Store VIX data in SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Delete existing VIX data (we'll refresh it)
    cursor.execute("DELETE FROM vix")

    # Insert new data
    for _, row in vix_df.iterrows():
        cursor.execute(
            "INSERT INTO vix (date, close) VALUES (?, ?)",
            (row['date'], row['close'])
        )

    conn.commit()
    conn.close()

    print(f"✓ Stored {len(vix_df)} VIX records in database")

def main():
    """Main execution function."""
    print("=" * 60)
    print("FETCH VIX DATA - Smoke Test")
    print("=" * 60)

    try:
        # Fetch VIX data
        vix_df = fetch_vix_data()

        # Store in database
        store_vix_data(vix_df)

        # Verify storage
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM vix")
        count = cursor.fetchone()['count']
        conn.close()

        print(f"\n✓ SUCCESS: {count} VIX records in database")
        print(f"✓ Date range: {vix_df['date'].min()} to {vix_df['date'].max()}")
        print(f"✓ Latest VIX: {vix_df['close'].iloc[-1]:.2f}")

    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
