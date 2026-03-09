"""
Fetch historical daily OHLCV prices.

Option A: yfinance (free, may hit rate limits but workable for 50-200 stocks)
Option B: Databento (use $125 credit for professional-grade backfill)

This script implements Option A by default.
"""

import yfinance as yf
import pandas as pd
import time
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import config
from universe import UNIVERSE
from data.db import get_connection

def fetch_ticker_prices(ticker, start_date=config.START_DATE):
    """
    Fetch daily OHLCV for a single ticker using yfinance.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date for historical data

    Returns:
        DataFrame with OHLCV data or None if failed
    """
    try:
        # Download data from yfinance
        stock_data = yf.download(ticker, start=start_date, progress=False)

        if stock_data.empty:
            print(f"  ⚠ {ticker}: No data returned")
            return None

        # Reset index and prepare data
        stock_data = stock_data.reset_index()

        # Handle multi-level columns (yfinance sometimes returns these)
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = stock_data.columns.get_level_values(0)

        # Rename columns to match our schema
        stock_data = stock_data.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })

        # Convert date to string
        stock_data['date'] = pd.to_datetime(stock_data['date']).dt.strftime('%Y-%m-%d')

        # Add ticker column
        stock_data['ticker'] = ticker

        # Select only needed columns
        stock_data = stock_data[['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']]

        # Validate: check for large gaps (>5 trading days)
        stock_data['date_dt'] = pd.to_datetime(stock_data['date'])
        stock_data = stock_data.sort_values('date_dt')
        date_diffs = stock_data['date_dt'].diff().dt.days

        large_gaps = date_diffs[date_diffs > 7]  # More than 5 business days
        if not large_gaps.empty:
            print(f"  ⚠ {ticker}: Found {len(large_gaps)} gaps >5 trading days")

        stock_data = stock_data.drop('date_dt', axis=1)

        print(f"  ✓ {ticker}: {len(stock_data)} days from {stock_data['date'].min()} to {stock_data['date'].max()}")
        return stock_data

    except Exception as e:
        print(f"  ✗ {ticker}: Error fetching prices: {e}")
        return None

def store_price_data(price_df):
    """Store price data in database."""
    conn = get_connection()
    cursor = conn.cursor()

    for _, row in price_df.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO prices
            (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row['ticker'],
            row['date'],
            row['open'],
            row['high'],
            row['low'],
            row['close'],
            int(row['volume']) if pd.notna(row['volume']) else 0
        ))

    conn.commit()
    conn.close()

def main():
    """Main execution function."""
    print("=" * 60)
    print("FETCH HISTORICAL PRICES (YFINANCE)")
    print("=" * 60)

    try:
        print(f"\nFetching prices for {len(UNIVERSE)} tickers...")
        print(f"Start date: {config.START_DATE}")
        print(f"Note: yfinance may show rate limit warnings. Retrying with delays...\n")

        total_days = 0
        successful_tickers = 0
        failed_tickers = []

        for i, ticker in enumerate(UNIVERSE, 1):
            print(f"[{i}/{len(UNIVERSE)}] Fetching {ticker}...")

            # Retry logic with exponential backoff
            price_df = None
            for attempt in range(3):
                price_df = fetch_ticker_prices(ticker)

                if price_df is not None and not price_df.empty:
                    break

                if attempt < 2:
                    wait_time = (attempt + 1) * 10
                    print(f"  ⟳ Retry {attempt + 1}/3 after {wait_time}s...")
                    time.sleep(wait_time)

            if price_df is not None and not price_df.empty:
                store_price_data(price_df)
                total_days += len(price_df)
                successful_tickers += 1
            else:
                print(f"  ✗ {ticker}: Failed after 3 attempts")
                failed_tickers.append(ticker)

            # Rate limiting: small delay between tickers
            if i < len(UNIVERSE):
                time.sleep(2)

            # Progress checkpoint every 10 tickers
            if i % 10 == 0:
                print(f"\n--- Checkpoint: {i}/{len(UNIVERSE)} tickers processed ---\n")

        print(f"\n" + "=" * 60)
        print(f"✓ SUCCESS: {total_days} price records from {successful_tickers} tickers")
        print(f"✓ Average: {total_days / successful_tickers:.0f} days per ticker")

        if failed_tickers:
            print(f"\n⚠ Failed tickers ({len(failed_tickers)}): {', '.join(failed_tickers)}")
            print("  Consider retrying these manually or removing from universe")

        print(f"\n✓ Database: {config.DB_PATH}")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
