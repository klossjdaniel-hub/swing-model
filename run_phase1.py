"""
Phase 1 data pipeline runner - Windows compatible (no Unicode issues).
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data.db import create_tables, get_connection
import yfinance as yf
import finnhub
import time
from datetime import datetime
from universe import UNIVERSE, get_sector_group

def fetch_vix():
    """Fetch VIX data."""
    print("\n" + "=" * 60)
    print("STEP 1: FETCHING VIX DATA")
    print("=" * 60)

    try:
        vix = yf.download("^VIX", start=config.START_DATE, progress=False)
        vix_close = vix[['Close']].reset_index()
        vix_close.columns = ['date', 'close']
        vix_close['date'] = vix_close['date'].dt.strftime('%Y-%m-%d')

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vix")

        for _, row in vix_close.iterrows():
            cursor.execute("INSERT INTO vix (date, close) VALUES (?, ?)",
                         (row['date'], row['close']))

        conn.commit()
        conn.close()

        print(f"[OK] Fetched {len(vix_close)} days of VIX data")
        print(f"[OK] Latest VIX: {vix_close['close'].iloc[-1]:.2f}")
        return True
    except Exception as e:
        print(f"[ERROR] VIX fetch failed: {e}")
        return False

def fetch_company_info():
    """Fetch company metadata from Finnhub."""
    print("\n" + "=" * 60)
    print("STEP 2: FETCHING COMPANY METADATA")
    print("=" * 60)

    try:
        client = finnhub.Client(api_key=config.FINNHUB_API_KEY)
        conn = get_connection()
        cursor = conn.cursor()

        successful = 0

        for i, ticker in enumerate(UNIVERSE, 1):
            print(f"[{i}/{len(UNIVERSE)}] {ticker}...", end=" ")

            try:
                profile = client.company_profile2(symbol=ticker)

                if profile:
                    cursor.execute("""
                        INSERT OR REPLACE INTO company_info
                        (ticker, name, sector, industry, market_cap, market_cap_bucket, country, type, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ticker,
                        profile.get('name', ''),
                        get_sector_group(profile.get('finnhubIndustry', 'Other')),
                        profile.get('finnhubIndustry', ''),
                        profile.get('marketCapitalization', 0) * 1_000_000,
                        'large' if profile.get('marketCapitalization', 0) * 1_000_000 >= 10e9 else 'mid',
                        profile.get('country', ''),
                        'STOCK',
                        datetime.now().isoformat()
                    ))
                    print("[OK]")
                    successful += 1
                else:
                    print("[SKIP]")

                time.sleep(1.1)  # Rate limiting

            except Exception as e:
                print(f"[ERROR: {e}]")

        conn.commit()
        conn.close()

        print(f"\n[OK] Stored {successful}/{len(UNIVERSE)} companies")
        return True

    except Exception as e:
        print(f"[ERROR] Company info fetch failed: {e}")
        return False

def fetch_earnings():
    """Fetch earnings data from Finnhub."""
    print("\n" + "=" * 60)
    print("STEP 3: FETCHING EARNINGS DATA")
    print("=" * 60)

    try:
        client = finnhub.Client(api_key=config.FINNHUB_API_KEY)
        conn = get_connection()
        cursor = conn.cursor()

        total_earnings = 0

        for i, ticker in enumerate(UNIVERSE, 1):
            print(f"[{i}/{len(UNIVERSE)}] {ticker}...", end=" ")

            try:
                earnings = client.company_earnings(ticker, limit=250)

                if earnings:
                    for earning in earnings:
                        eps_estimate = earning.get('epsEstimate', 0)
                        eps_actual = earning.get('epsActual', 0)
                        surprise_pct = None
                        if eps_estimate and eps_estimate != 0:
                            surprise_pct = (eps_actual - eps_estimate) / abs(eps_estimate)

                        cursor.execute("""
                            INSERT OR REPLACE INTO earnings_raw
                            (ticker, report_date, quarter, year, eps_estimate, eps_actual,
                             revenue_estimate, revenue_actual, surprise_pct)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            ticker,
                            earning.get('date', earning.get('period', '')),
                            earning.get('quarter', 0),
                            earning.get('year', 0),
                            eps_estimate,
                            eps_actual,
                            earning.get('revenueEstimate'),
                            earning.get('revenueActual'),
                            surprise_pct
                        ))

                    print(f"[OK] {len(earnings)} earnings")
                    total_earnings += len(earnings)
                else:
                    print("[NO DATA]")

                time.sleep(1.1)

            except Exception as e:
                print(f"[ERROR: {e}]")

        conn.commit()
        conn.close()

        print(f"\n[OK] Stored {total_earnings} total earnings records")
        return True

    except Exception as e:
        print(f"[ERROR] Earnings fetch failed: {e}")
        return False

def fetch_prices():
    """Fetch historical prices from yfinance."""
    print("\n" + "=" * 60)
    print("STEP 4: FETCHING HISTORICAL PRICES")
    print("=" * 60)
    print("This will take ~5-10 minutes for 50 stocks...\n")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        total_days = 0
        successful = 0

        for i, ticker in enumerate(UNIVERSE, 1):
            print(f"[{i}/{len(UNIVERSE)}] {ticker}...", end=" ")

            try:
                stock_data = yf.download(ticker, start=config.START_DATE, progress=False)

                if not stock_data.empty:
                    stock_data = stock_data.reset_index()

                    if isinstance(stock_data.columns, __import__('pandas').MultiIndex):
                        stock_data.columns = stock_data.columns.get_level_values(0)

                    stock_data = stock_data.rename(columns={
                        'Date': 'date', 'Open': 'open', 'High': 'high',
                        'Low': 'low', 'Close': 'close', 'Volume': 'volume'
                    })

                    stock_data['date'] = __import__('pandas').to_datetime(stock_data['date']).dt.strftime('%Y-%m-%d')

                    for _, row in stock_data.iterrows():
                        cursor.execute("""
                            INSERT OR REPLACE INTO prices
                            (ticker, date, open, high, low, close, volume)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            ticker, row['date'], row['open'], row['high'],
                            row['low'], row['close'], int(row['volume']) if __import__('pandas').notna(row['volume']) else 0
                        ))

                    print(f"[OK] {len(stock_data)} days")
                    total_days += len(stock_data)
                    successful += 1
                else:
                    print("[NO DATA]")

                time.sleep(2)  # Rate limiting for yfinance

            except Exception as e:
                print(f"[ERROR: {e}]")

        conn.commit()
        conn.close()

        print(f"\n[OK] Stored {total_days} price records from {successful} tickers")
        return True

    except Exception as e:
        print(f"[ERROR] Price fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run complete Phase 1 pipeline."""
    print("\n" + "=" * 70)
    print(" SWING MODEL - PHASE 1: DATA PIPELINE")
    print("=" * 70)

    try:
        # Validate config
        print("\n[STEP 0] Validating configuration...")
        config.validate_config(phase="phase1")

        # Create database
        print("\n[STEP 1] Creating database schema...")
        create_tables()

        # Fetch VIX
        if not fetch_vix():
            print("\n[WARNING] VIX fetch failed, continuing anyway...")

        # Fetch company info
        if not fetch_company_info():
            print("\n[ERROR] Company info fetch failed!")
            return

        # Fetch earnings
        if not fetch_earnings():
            print("\n[ERROR] Earnings fetch failed!")
            return

        # Fetch prices
        if not fetch_prices():
            print("\n[ERROR] Price fetch failed!")
            return

        # Success
        print("\n" + "=" * 70)
        print(" PHASE 1 COMPLETE!")
        print("=" * 70)
        print(f"\nDatabase: {config.DB_PATH}")
        print("\nNext steps:")
        print("  1. Review data above for any warnings")
        print("  2. Build events dataset (create data/build_events.py)")
        print("  3. Validate dataset (create data/validate_dataset.py)")
        print("\nThen proceed to Phase 2: Model training")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Pipeline stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FAILED] Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
