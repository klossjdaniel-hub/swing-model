"""
Build a comprehensive stock universe of all US stocks with market cap >$1B.

This script screens for liquid, large-cap stocks to monitor for predictions.
Run this monthly to update the universe.
"""

import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# List of all major US exchange tickers
# We'll use major indices as our starting point for efficiency
def get_index_tickers():
    """Get tickers from major US indices."""

    # S&P 500
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    sp500_tickers = sp500['Symbol'].str.replace('.', '-').tolist()

    # S&P MidCap 400
    sp400 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_400_companies')[0]
    sp400_tickers = sp400['Symbol'].str.replace('.', '-').tolist()

    # S&P SmallCap 600
    sp600 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_600_companies')[0]
    sp600_tickers = sp600['Symbol'].str.replace('.', '-').tolist()

    # Combine all
    all_tickers = list(set(sp500_tickers + sp400_tickers + sp600_tickers))

    print(f"Found {len(sp500_tickers)} S&P 500 stocks")
    print(f"Found {len(sp400_tickers)} S&P 400 stocks")
    print(f"Found {len(sp600_tickers)} S&P 600 stocks")
    print(f"Total unique tickers: {len(all_tickers)}")

    return all_tickers


def screen_by_market_cap(tickers, min_market_cap_billions=1.0):
    """Screen tickers by market cap threshold."""

    print(f"\nScreening {len(tickers)} tickers for market cap >${min_market_cap_billions}B...")

    qualified = []
    failed = []

    for i, ticker in enumerate(tickers, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(tickers)} ({i/len(tickers)*100:.1f}%)")

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            market_cap = info.get('marketCap', 0)

            if market_cap >= min_market_cap_billions * 1e9:
                qualified.append({
                    'ticker': ticker,
                    'market_cap': market_cap,
                    'name': info.get('longName', ticker),
                    'sector': info.get('sector', 'Unknown')
                })

            # Rate limit
            time.sleep(0.05)

        except Exception as e:
            failed.append(ticker)
            continue

    print(f"\nQualified: {len(qualified)}")
    print(f"Failed/Missing data: {len(failed)}")

    return qualified, failed


def save_universe(qualified_stocks):
    """Save the qualified universe to universe.py."""

    # Sort by market cap descending
    qualified_stocks.sort(key=lambda x: x['market_cap'], reverse=True)

    tickers = [s['ticker'] for s in qualified_stocks]

    # Generate Python code
    code = f'''"""
Stock universe definition for swing-model.

Auto-generated on {datetime.now().strftime('%Y-%m-%d')}

Universe: All US stocks with market cap >$1B (~{len(tickers)} stocks)
"""

# Full universe: {len(tickers)} stocks with market cap >$1B
UNIVERSE = {tickers}

# Quick access to universe size
UNIVERSE_SIZE = {len(tickers)}

# For sector analysis
def get_sector_group(finnhub_sector):
    """Map sector to broad groups."""
    sector_mapping = {{
        "Technology": "Technology",
        "Communication Services": "Technology",
        "Consumer Cyclical": "Cyclicals",
        "Consumer Defensive": "Defensive",
        "Financial Services": "Financials",
        "Financial": "Financials",
        "Healthcare": "Healthcare",
        "Industrials": "Cyclicals",
        "Basic Materials": "Cyclicals",
        "Energy": "Energy",
        "Utilities": "Defensive",
        "Real Estate": "Defensive",
    }}
    return sector_mapping.get(finnhub_sector, "Other")
'''

    with open('universe.py', 'w') as f:
        f.write(code)

    print(f"\n✅ Universe saved to universe.py")
    print(f"   Total stocks: {len(tickers)}")

    # Show top 20 by market cap
    print("\nTop 20 stocks by market cap:")
    for i, stock in enumerate(qualified_stocks[:20], 1):
        mc_b = stock['market_cap'] / 1e9
        print(f"  {i:2d}. {stock['ticker']:6} - ${mc_b:7.1f}B - {stock['name'][:40]}")

    # Show sector breakdown
    sector_counts = {}
    for stock in qualified_stocks:
        sector = stock['sector']
        sector_counts[sector] = sector_counts.get(sector, 0) + 1

    print("\nSector breakdown:")
    for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {sector:30} - {count:4d} stocks")


def main():
    """Build the full universe."""

    print("=" * 70)
    print("BUILDING COMPREHENSIVE STOCK UNIVERSE")
    print("=" * 70)
    print()

    # Step 1: Get all major index tickers
    print("STEP 1: Fetching index constituents...")
    all_tickers = get_index_tickers()

    # Step 2: Screen by market cap
    print("\nSTEP 2: Screening by market cap...")
    qualified, failed = screen_by_market_cap(all_tickers, min_market_cap_billions=1.0)

    # Step 3: Save to universe.py
    print("\nSTEP 3: Saving universe...")
    save_universe(qualified)

    print("\n" + "=" * 70)
    print("✅ UNIVERSE BUILD COMPLETE")
    print("=" * 70)
    print()
    print(f"Final universe size: {len(qualified)} stocks")
    print(f"Estimated scan time: {len(qualified) * 0.1 / 60:.1f} minutes")
    print()


if __name__ == "__main__":
    main()
