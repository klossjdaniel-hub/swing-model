"""
Fetch historical earnings data from Alpha Vantage (free tier: 25 calls/day).

This script is designed to run over 2-3 days due to rate limits.
It saves progress after each ticker, so you can stop and resume.

Alpha Vantage EARNINGS endpoint provides:
- Quarterly earnings with estimates + actuals
- Annual earnings with estimates + actuals
- Full historical data back to IPO
"""

import requests
import time
import sys
import os
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from universe import UNIVERSE
from data.db import get_connection

# Progress tracking file
PROGRESS_FILE = "data/.alpha_vantage_progress.json"

def load_progress():
    """Load progress from previous runs."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'completed': [], 'failed': [], 'calls_today': 0, 'last_run_date': None}

def save_progress(progress):
    """Save progress for resuming later."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def reset_daily_counter(progress):
    """Reset call counter if it's a new day."""
    today = datetime.now().strftime('%Y-%m-%d')
    if progress['last_run_date'] != today:
        progress['calls_today'] = 0
        progress['last_run_date'] = today
    return progress

def fetch_earnings_alpha_vantage(ticker, api_key):
    """
    Fetch earnings data from Alpha Vantage EARNINGS endpoint.

    Returns: List of earnings dicts with estimates + actuals
    """
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'EARNINGS',
        'symbol': ticker,
        'apikey': api_key
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Check for error messages
        if 'Error Message' in data:
            raise Exception(f"API Error: {data['Error Message']}")

        if 'Note' in data:
            # Rate limit message
            raise Exception(f"Rate limited: {data['Note']}")

        # Alpha Vantage returns quarterly and annual earnings
        quarterly_earnings = data.get('quarterlyEarnings', [])

        if not quarterly_earnings:
            return []

        earnings_list = []

        for earning in quarterly_earnings:
            # Extract fields
            report_date = earning.get('reportedDate', '')
            fiscal_date = earning.get('fiscalDateEnding', '')
            eps_estimate = earning.get('estimatedEPS')
            eps_actual = earning.get('reportedEPS')
            surprise = earning.get('surprise')
            surprise_pct = earning.get('surprisePercentage')

            # Convert to float if possible
            try:
                eps_estimate = float(eps_estimate) if eps_estimate and eps_estimate != 'None' else None
            except:
                eps_estimate = None

            try:
                eps_actual = float(eps_actual) if eps_actual and eps_actual != 'None' else None
            except:
                eps_actual = None

            try:
                surprise_pct = float(surprise_pct) if surprise_pct and surprise_pct != 'None' else None
            except:
                surprise_pct = None

            # Skip if missing critical data
            if not report_date or (eps_estimate is None and eps_actual is None):
                continue

            # Calculate surprise if not provided
            if surprise_pct is None and eps_estimate and eps_actual and eps_estimate != 0:
                surprise_pct = (eps_actual - eps_estimate) / abs(eps_estimate)

            # Parse quarter and year from fiscal date
            try:
                fiscal_dt = datetime.strptime(fiscal_date, '%Y-%m-%d')
                quarter = (fiscal_dt.month - 1) // 3 + 1
                year = fiscal_dt.year
            except:
                quarter = 0
                year = 0

            earnings_data = {
                'ticker': ticker,
                'report_date': report_date,
                'quarter': quarter,
                'year': year,
                'eps_estimate': eps_estimate,
                'eps_actual': eps_actual,
                'revenue_estimate': None,  # Alpha Vantage doesn't provide revenue
                'revenue_actual': None,
                'surprise_pct': surprise_pct
            }

            earnings_list.append(earnings_data)

        return earnings_list

    except Exception as e:
        raise Exception(f"{e}")

def store_earnings_alpha_vantage(ticker, earnings_list, conn):
    """Store Alpha Vantage earnings data in database."""
    cursor = conn.cursor()

    stored_count = 0

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

        stored_count += 1

    conn.commit()
    return stored_count

def main():
    """Main execution function."""
    print("\n" + "=" * 60)
    print("FETCH EARNINGS FROM ALPHA VANTAGE")
    print("Free Tier: 25 calls/day - Runs over 2-3 days")
    print("=" * 60)

    # Check for API key
    alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')

    if not alpha_vantage_key:
        print("\n[ERROR] ALPHA_VANTAGE_API_KEY not found in .env file")
        print("\nTo get a FREE API key:")
        print("1. Visit: https://www.alphavantage.co/support/#api-key")
        print("2. Enter your email")
        print("3. Click 'GET FREE API KEY'")
        print("4. Check your email for the key")
        print("5. Add to .env file: ALPHA_VANTAGE_API_KEY=your_key_here")
        print("\nFree tier: 25 calls/day, unlimited history")
        sys.exit(1)

    # Load progress
    progress = load_progress()
    progress = reset_daily_counter(progress)

    print(f"\n[OK] API key found")
    print(f"[OK] Progress: {len(progress['completed'])}/{len(UNIVERSE)} tickers completed")
    print(f"[OK] Today's calls: {progress['calls_today']}/25")

    if progress['calls_today'] >= 25:
        print("\n[STOP] Daily limit reached (25 calls)")
        print("Run again tomorrow to continue fetching")
        sys.exit(0)

    # Determine which tickers need fetching
    remaining_tickers = [t for t in UNIVERSE if t not in progress['completed'] and t not in progress['failed']]

    if not remaining_tickers:
        print("\n[OK] All tickers already fetched!")
        sys.exit(0)

    print(f"[OK] Remaining tickers: {len(remaining_tickers)}")
    print(f"[OK] Can fetch up to {25 - progress['calls_today']} more today\n")

    conn = get_connection()

    total_earnings = 0
    tickers_fetched_today = 0

    for ticker in remaining_tickers:
        # Check daily limit
        if progress['calls_today'] >= 25:
            print("\n[STOP] Daily limit reached (25 calls)")
            print("Progress saved. Run again tomorrow to continue.")
            break

        print(f"[{len(progress['completed']) + 1}/{len(UNIVERSE)}] {ticker}...", end=" ", flush=True)

        try:
            earnings_list = fetch_earnings_alpha_vantage(ticker, alpha_vantage_key)
            progress['calls_today'] += 1

            if earnings_list:
                stored = store_earnings_alpha_vantage(ticker, earnings_list, conn)
                total_earnings += stored
                print(f"[OK] {stored} earnings")
                progress['completed'].append(ticker)
            else:
                print("[NO DATA]")
                progress['completed'].append(ticker)  # Mark as done even if no data

            tickers_fetched_today += 1

            # Save progress after each ticker
            save_progress(progress)

            # Rate limiting: Alpha Vantage recommends 5 calls/min = 12 sec delay
            # But we're being conservative with 15 sec
            if progress['calls_today'] < 25:
                time.sleep(15)

        except Exception as e:
            print(f"[ERROR] {e}")
            progress['failed'].append(ticker)
            save_progress(progress)

            # Check if rate limited
            if 'rate limit' in str(e).lower() or 'premium' in str(e).lower():
                print("\n[STOP] Hit rate limit")
                print("Progress saved. Run again tomorrow.")
                break

    conn.close()

    # Final summary
    print("\n" + "=" * 60)
    print("SESSION COMPLETE")
    print("=" * 60)
    print(f"\nTickers fetched this session: {tickers_fetched_today}")
    print(f"Total earnings stored: {total_earnings}")
    print(f"Overall progress: {len(progress['completed'])}/{len(UNIVERSE)} tickers")
    print(f"API calls today: {progress['calls_today']}/25")

    if len(progress['completed']) < len(UNIVERSE):
        print(f"\n[INFO] Still {len(UNIVERSE) - len(progress['completed'])} tickers remaining")
        print("[INFO] Run this script again tomorrow to continue")
    else:
        print("\n[OK] ALL TICKERS COMPLETE!")

        # Show final stats
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(report_date), MAX(report_date), COUNT(*) FROM earnings_raw")
        date_range = cursor.fetchone()
        conn.close()

        if date_range[0]:
            print(f"\n[OK] Date range: {date_range[0]} to {date_range[1]}")
            print(f"[OK] Total earnings: {date_range[2]}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
