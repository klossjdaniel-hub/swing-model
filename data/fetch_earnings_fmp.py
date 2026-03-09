"""
Fetch historical earnings data from Financial Modeling Prep (FMP) free tier.

FMP Free Tier:
- 250 API calls/day
- 5 years of historical earnings data
- EPS estimates + actuals
- Revenue estimates + actuals
- No credit card required

Sign up: https://site.financialmodelingprep.com/developer/docs
"""

import requests
import time
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from universe import UNIVERSE
from data.db import get_connection

def fetch_earnings_history(ticker, api_key):
    """
    Fetch historical earnings for a ticker from FMP.

    Endpoint: /historical/earning_calendar/{ticker}
    Returns: List of earnings with estimates + actuals
    """
    url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{ticker}"
    params = {'apikey': api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            return data
        else:
            return []

    except Exception as e:
        raise Exception(f"API error: {e}")

def store_earnings_fmp(ticker, earnings_list, conn):
    """Store FMP earnings data in database."""
    cursor = conn.cursor()

    stored_count = 0

    for earning in earnings_list:
        # Extract fields from FMP response
        date = earning.get('date', '')
        eps_estimate = earning.get('epsEstimated')
        eps_actual = earning.get('eps')
        revenue_estimate = earning.get('revenueEstimated')
        revenue_actual = earning.get('revenue')

        # Skip if no EPS data
        if eps_estimate is None or eps_actual is None:
            continue

        # Calculate surprise percentage
        surprise_pct = None
        if eps_estimate and eps_estimate != 0:
            surprise_pct = (eps_actual - eps_estimate) / abs(eps_estimate)

        # Calculate revenue surprise
        revenue_surprise_pct = None
        if revenue_estimate and revenue_actual and revenue_estimate != 0:
            revenue_surprise_pct = (revenue_actual - revenue_estimate) / abs(revenue_estimate)

        # Extract quarter and year from date
        try:
            dt = datetime.strptime(date, '%Y-%m-%d')
            quarter = (dt.month - 1) // 3 + 1
            year = dt.year
        except:
            quarter = 0
            year = 0

        # Insert or update
        cursor.execute("""
            INSERT OR REPLACE INTO earnings_raw
            (ticker, report_date, quarter, year, eps_estimate, eps_actual,
             revenue_estimate, revenue_actual, surprise_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker, date, quarter, year,
            eps_estimate, eps_actual,
            revenue_estimate, revenue_actual,
            surprise_pct
        ))

        stored_count += 1

    conn.commit()
    return stored_count

def main():
    """Main execution function."""
    print("\n" + "=" * 60)
    print("FETCH EARNINGS DATA FROM FINANCIAL MODELING PREP")
    print("=" * 60)

    # Check for API key
    fmp_api_key = os.getenv('FMP_API_KEY')

    if not fmp_api_key:
        print("\n[ERROR] FMP_API_KEY not found in .env file")
        print("\nTo get a FREE API key:")
        print("1. Visit: https://site.financialmodelingprep.com/developer/docs")
        print("2. Click 'Get your Free API Key'")
        print("3. Sign up (no credit card required)")
        print("4. Copy your API key")
        print("5. Add to .env file: FMP_API_KEY=your_key_here")
        print("\nFree tier: 250 calls/day, 5 years history")
        sys.exit(1)

    print(f"\n[OK] FMP API key found")
    print(f"[OK] Fetching earnings for {len(UNIVERSE)} tickers...")
    print(f"[OK] Free tier: 250 calls/day (enough for all 50 stocks)\n")

    conn = get_connection()

    # Clear existing earnings (fresh start with FMP data)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM earnings_raw")
    conn.commit()
    print("[OK] Cleared existing earnings data\n")

    total_earnings = 0
    successful_tickers = 0
    failed_tickers = []

    for i, ticker in enumerate(UNIVERSE, 1):
        print(f"[{i}/{len(UNIVERSE)}] {ticker}...", end=" ", flush=True)

        try:
            earnings_list = fetch_earnings_history(ticker, fmp_api_key)

            if earnings_list:
                stored = store_earnings_fmp(ticker, earnings_list, conn)
                total_earnings += stored
                successful_tickers += 1
                print(f"[OK] {stored} earnings")
            else:
                print("[NO DATA]")
                failed_tickers.append(ticker)

            # Rate limiting: ~4 calls/second = 240/minute << 250/day limit
            # Be conservative to avoid hitting limits
            time.sleep(0.3)

        except Exception as e:
            print(f"[ERROR] {e}")
            failed_tickers.append(ticker)

    conn.close()

    # Summary
    print("\n" + "=" * 60)
    print("EARNINGS FETCH COMPLETE")
    print("=" * 60)
    print(f"\n[OK] Successful tickers: {successful_tickers}/{len(UNIVERSE)}")
    print(f"[OK] Total earnings records: {total_earnings}")

    if successful_tickers > 0:
        print(f"[OK] Average per ticker: {total_earnings / successful_tickers:.1f}")

    if failed_tickers:
        print(f"\n[WARNING] Failed tickers ({len(failed_tickers)}):")
        for ticker in failed_tickers:
            print(f"  - {ticker}")

    # Check date range
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(report_date), MAX(report_date) FROM earnings_raw")
    date_range = cursor.fetchone()
    conn.close()

    if date_range[0]:
        print(f"\n[OK] Date range: {date_range[0]} to {date_range[1]}")

    print("\n" + "=" * 60)
    print("Next step: python data/build_events.py")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
