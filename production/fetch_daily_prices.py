"""
Fetch today's prices from Yahoo Finance for all stocks in universe.

Run this daily to get latest OHLCV data.
"""

import sys
import os
from datetime import datetime, timedelta
import time
import yfinance as yf

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import get_connection
from universe import UNIVERSE

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def fetch_stock_candles(ticker, from_date, to_date):
    """Fetch daily candles from Yahoo Finance."""
    try:
        # Download data from yfinance
        stock = yf.Ticker(ticker)
        df = stock.history(start=from_date, end=to_date)

        if df.empty:
            return []

        # Convert to list of dicts
        candles = []
        for date, row in df.iterrows():
            candles.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })

        return candles

    except Exception as e:
        print(f"[ERROR] Failed to fetch candles for {ticker}: {e}")
        return []


def store_prices(ticker, candles, conn):
    """Store price data in database."""
    cursor = conn.cursor()

    stored = 0
    for candle in candles:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO prices (ticker, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ticker,
                candle['date'],
                candle['open'],
                candle['high'],
                candle['low'],
                candle['close'],
                candle['volume']
            ))
            stored += 1
        except Exception as e:
            print(f"[ERROR] Failed to store {ticker} {candle['date']}: {e}")

    return stored


def fetch_daily_prices():
    """Fetch latest prices for all stocks."""
    conn = get_connection()

    print("\n" + "=" * 60)
    print("FETCHING DAILY PRICES FROM YAHOO FINANCE")
    print("=" * 60 + "\n")

    # Get last 7 days to ensure we have recent data
    today = datetime.now()
    from_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    print(f"Fetching prices from {from_date} to {to_date}\n")
    print(f"Stocks: {len(UNIVERSE)}\n")

    total_stored = 0
    failed = 0

    for i, ticker in enumerate(UNIVERSE, 1):
        print(f"[{i}/{len(UNIVERSE)}] {ticker}...", end=' ')

        candles = fetch_stock_candles(ticker, from_date, to_date)

        if candles:
            stored = store_prices(ticker, candles, conn)
            total_stored += stored
            print(f"{stored} days")
        else:
            print("FAILED")
            failed += 1

        # Small delay to be nice to Yahoo
        time.sleep(0.1)

        # Commit every 10 stocks
        if i % 10 == 0:
            conn.commit()

    conn.commit()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60 + "\n")
    print(f"Total prices stored: {total_stored}")
    print(f"Failed tickers: {failed}")

    # Show latest prices
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ticker, MAX(date) as latest_date
        FROM prices
        WHERE ticker IN ({})
        GROUP BY ticker
        ORDER BY ticker
    """.format(','.join('?' * len(UNIVERSE))), UNIVERSE)

    latest_dates = cursor.fetchall()

    print(f"\nLatest data dates:")
    unique_dates = set(row[1] for row in latest_dates)
    for date in sorted(unique_dates, reverse=True):
        tickers_on_date = [row[0] for row in latest_dates if row[1] == date]
        print(f"  {date}: {len(tickers_on_date)} stocks")

    conn.close()

    print("\n" + "=" * 60)
    print("[OK] Daily prices fetched")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    fetch_daily_prices()
