"""Test edgartools for historical earnings data from SEC filings."""

from edgar import *
from datetime import datetime

# Set user identity for SEC (required)
set_identity("Your Name your.email@example.com")

print("Testing edgartools for AAPL earnings from SEC filings...\n")

try:
    # Get company
    company = Company("AAPL")
    print(f"Company: {company.name}\n")

    # Get 8-K filings (earnings announcements) from 2023-2024
    filings = company.get_filings(form="8-K").filter(date="2023-01-01:2024-12-31")

    print(f"Found {len(filings)} 8-K filings in 2023-2024\n")

    # Show first 5 earnings-related 8-Ks
    print("Looking for earnings announcements...\n")
    earnings_count = 0

    for filing in filings[:20]:  # Check first 20
        # Get the filing object
        filing_obj = filing.obj()

        # Check if it's an earnings announcement (Item 2.02)
        if hasattr(filing_obj, 'items'):
            items = filing_obj.items
            if '2.02' in str(items) or 'Results of Operations' in str(items):
                earnings_count += 1
                print(f"{earnings_count}. {filing.filing_date} - {filing.form}")
                print(f"   Items: {items}")
                print()

                if earnings_count >= 5:
                    break

    if earnings_count > 0:
        print(f"\n[OK] SUCCESS: edgartools can access earnings 8-K filings!")
        print(f"[OK] This is completely FREE with no limits")
        print(f"\nNext step: Parse these 8-Ks to extract EPS data")
    else:
        print("\n[WARNING] No earnings 8-Ks found in sample")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
