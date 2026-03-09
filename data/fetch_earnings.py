"""
Fetch historical earnings data from Finnhub.

Retrieves quarterly earnings with EPS and revenue estimates/actuals.
Stores raw data in earnings_raw staging table.
"""

import finnhub
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import config
from universe import UNIVERSE
from data.db import get_connection

def init_finnhub_client():
    """Initialize Finnhub client with API key."""
    if not config.FINNHUB_API_KEY:
        raise ValueError("FINNHUB_API_KEY not set in environment")

    return finnhub.Client(api_key=config.FINNHUB_API_KEY)

def fetch_earnings_for_ticker(client, ticker):
    """
    Fetch historical earnings for a single ticker.

    Args:
        client: Finnhub client
        ticker: Stock ticker symbol

    Returns:
        List of earnings dicts
    """
    try:
        # Finnhub earnings endpoint returns all historical earnings
        earnings = client.company_earnings(ticker, limit=250)

        if not earnings:
            print(f"  ⚠ {ticker}: No earnings data")
            return []

        earnings_list = []

        for earning in earnings:
            # Calculate surprise percentage
            eps_estimate = earning.get('epsEstimate', 0)
            eps_actual = earning.get('epsActual', 0)
            surprise_pct = None

            if eps_estimate and eps_estimate != 0:
                surprise_pct = (eps_actual - eps_estimate) / abs(eps_estimate)

            earnings_data = {
                'ticker': ticker,
                'report_date': earning.get('date', earning.get('period', '')),
                'quarter': earning.get('quarter', 0),
                'year': earning.get('year', 0),
                'eps_estimate': eps_estimate,
                'eps_actual': eps_actual,
                'revenue_estimate': earning.get('revenueEstimate'),
                'revenue_actual': earning.get('revenueActual'),
                'surprise_pct': surprise_pct
            }

            earnings_list.append(earnings_data)

        print(f"  ✓ {ticker}: {len(earnings_list)} earnings records")
        return earnings_list

    except Exception as e:
        print(f"  ✗ {ticker}: Error fetching earnings: {e}")
        return []

def store_earnings_data(earnings_list):
    """Store earnings data in database."""
    conn = get_connection()
    cursor = conn.cursor()

    for earning in earnings_list:
        cursor.execute("""
            INSERT OR REPLACE INTO earnings_raw
            (ticker, report_date, quarter, year, eps_estimate, eps_actual,
             revenue_estimate, revenue_actual, surprise_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            earning['ticker'],
            earning['report_date'],
            earning['quarter'],
            earning['year'],
            earning['eps_estimate'],
            earning['eps_actual'],
            earning['revenue_estimate'],
            earning['revenue_actual'],
            earning['surprise_pct']
        ))

    conn.commit()
    conn.close()

def main():
    """Main execution function."""
    print("=" * 60)
    print("FETCH EARNINGS DATA FROM FINNHUB")
    print("=" * 60)

    try:
        # Validate API key
        config.validate_config(phase="phase1")

        # Initialize Finnhub client
        client = init_finnhub_client()

        print(f"\nFetching earnings for {len(UNIVERSE)} tickers...")
        print(f"Rate limit: 60 calls/min (Finnhub free tier)\n")

        total_earnings = 0
        successful_tickers = 0

        for i, ticker in enumerate(UNIVERSE, 1):
            print(f"[{i}/{len(UNIVERSE)}] Fetching {ticker}...")

            earnings_list = fetch_earnings_for_ticker(client, ticker)

            if earnings_list:
                store_earnings_data(earnings_list)
                total_earnings += len(earnings_list)
                successful_tickers += 1

            # Rate limiting: 60 calls/min = 1 call per second
            if i < len(UNIVERSE):
                time.sleep(1.1)

        print(f"\n" + "=" * 60)
        print(f"✓ SUCCESS: {total_earnings} earnings records from {successful_tickers} tickers")
        print(f"✓ Average: {total_earnings / successful_tickers:.1f} earnings per ticker")
        print(f"✓ Database: {config.DB_PATH}")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
