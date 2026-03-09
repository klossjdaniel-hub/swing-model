"""
Fetch company metadata from Finnhub.

Retrieves sector, market cap, and company type.
Rejects mutual funds and classifies by market cap bucket.
"""

import finnhub
import time
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import config
from universe import UNIVERSE, get_sector_group
from data.db import get_connection

def init_finnhub_client():
    """Initialize Finnhub client with API key."""
    if not config.FINNHUB_API_KEY:
        raise ValueError("FINNHUB_API_KEY not set in environment")

    return finnhub.Client(api_key=config.FINNHUB_API_KEY)

def fetch_company_profile(client, ticker):
    """
    Fetch company profile from Finnhub.

    Args:
        client: Finnhub client
        ticker: Stock ticker symbol

    Returns:
        Dict with company info or None if failed
    """
    try:
        profile = client.company_profile2(symbol=ticker)

        if not profile:
            print(f"  ✗ {ticker}: No profile data returned")
            return None

        # Extract relevant fields
        company_info = {
            'ticker': ticker,
            'name': profile.get('name', ''),
            'sector': get_sector_group(profile.get('finnhubIndustry', 'Other')),
            'industry': profile.get('finnhubIndustry', ''),
            'market_cap': profile.get('marketCapitalization', 0) * 1_000_000,  # Convert to dollars
            'country': profile.get('country', ''),
            'type': profile.get('exchange', '').upper() if profile.get('exchange') else 'STOCK',
        }

        # Determine market cap bucket
        if company_info['market_cap'] >= 10_000_000_000:
            company_info['market_cap_bucket'] = 'large'
        elif company_info['market_cap'] >= 1_000_000_000:
            company_info['market_cap_bucket'] = 'mid'
        else:
            company_info['market_cap_bucket'] = 'small'

        print(f"  ✓ {ticker}: {company_info['name']} | {company_info['sector']} | {company_info['market_cap_bucket']}")
        return company_info

    except Exception as e:
        print(f"  ✗ {ticker}: Error fetching profile: {e}")
        return None

def store_company_info(company_data):
    """Store company info in database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO company_info
        (ticker, name, sector, industry, market_cap, market_cap_bucket, country, type, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company_data['ticker'],
        company_data['name'],
        company_data['sector'],
        company_data['industry'],
        company_data['market_cap'],
        company_data['market_cap_bucket'],
        company_data['country'],
        company_data['type'],
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

def main():
    """Main execution function."""
    print("=" * 60)
    print("FETCH COMPANY METADATA FROM FINNHUB")
    print("=" * 60)

    try:
        # Validate API key
        config.validate_config(phase="phase1")

        # Initialize Finnhub client
        client = init_finnhub_client()

        print(f"\nFetching profiles for {len(UNIVERSE)} tickers...")
        print(f"Rate limit: 60 calls/min (Finnhub free tier)\n")

        successful = 0
        rejected = 0

        for i, ticker in enumerate(UNIVERSE, 1):
            print(f"[{i}/{len(UNIVERSE)}] Fetching {ticker}...")

            company_info = fetch_company_profile(client, ticker)

            if company_info:
                # Check if it's a mutual fund (reject)
                if 'MUTUAL' in company_info.get('type', '').upper():
                    print(f"  ⚠ {ticker}: Rejected (MUTUAL_FUND)")
                    rejected += 1
                    continue

                # Store in database
                store_company_info(company_info)
                successful += 1

            # Rate limiting: 60 calls/min = 1 call per second
            if i < len(UNIVERSE):
                time.sleep(1.1)  # Slightly over 1 second to be safe

        print(f"\n" + "=" * 60)
        print(f"✓ SUCCESS: {successful} companies stored")
        print(f"⚠ Rejected: {rejected} (mutual funds or failed)")
        print(f"✓ Database: {config.DB_PATH}")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
