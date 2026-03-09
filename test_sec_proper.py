"""Test proper way to access 8-K earnings data."""

from edgar import *

set_identity("User user@example.com")

print("Testing AAPL Q4 2024 earnings 8-K...\n")

company = Company("AAPL")
filings = company.get_filings(form="8-K").filter(date="2024-10-31:2024-10-31")

if filings:
    filing = filings[0]
    filing_obj = filing.obj()

    print(f"Filing date: {filing.filing_date}")
    print(f"Has press release: {filing_obj.has_press_release}")
    print(f"Has earnings: {filing_obj.has_earnings}\n")

    # Try press_releases
    if filing_obj.has_press_release:
        print("Accessing press_releases...")
        press_releases = filing_obj.press_releases
        print(f"Press releases type: {type(press_releases)}")
        print(f"Press releases: {press_releases}\n")

        if press_releases:
            for i, pr in enumerate(press_releases, 1):
                print(f"Press Release {i}:")
                print(f"  Type: {type(pr)}")

                # Try to get text
                if hasattr(pr, 'text'):
                    text = pr.text
                    print(f"  Text length: {len(text)} chars")

                    # Search for EPS
                    import re
                    eps_matches = re.findall(r'earnings per share.*?\$?(\d+\.\d+)', text[:3000], re.IGNORECASE)
                    if eps_matches:
                        print(f"  [OK] Found EPS values: {eps_matches}")

                    # Show sample
                    lines = [l for l in text.split('\n')[:50] if 'EPS' in l.upper() or 'earnings per share' in l.lower()]
                    if lines:
                        print(f"  Sample EPS lines:")
                        for line in lines[:3]:
                            print(f"    {line.strip()[:100]}")
                elif hasattr(pr, 'content'):
                    print(f"  Has content attribute")
                elif hasattr(pr, 'html'):
                    print(f"  Has html attribute")
                else:
                    print(f"  Available methods: {[x for x in dir(pr) if not x.startswith('_')]}")

    # Try earnings attribute
    if filing_obj.has_earnings:
        print("\n\nAccessing earnings attribute...")
        earnings = filing_obj.earnings
        print(f"Earnings type: {type(earnings)}")
        print(f"Earnings: {earnings}\n")

        if earnings:
            # Check what's in earnings
            if isinstance(earnings, dict):
                print("Earnings is a dict:")
                for key, value in earnings.items():
                    print(f"  {key}: {value}")
            elif isinstance(earnings, list):
                print(f"Earnings is a list with {len(earnings)} items")
                for i, item in enumerate(earnings[:3]):
                    print(f"  Item {i}: {item}")
            else:
                print(f"Earnings attributes: {[x for x in dir(earnings) if not x.startswith('_')]}")

    # Try accessing the raw document text
    print("\n\nAccessing full document text...")
    text = filing_obj.text
    print(f"Full document text length: {len(text)} chars")

    # Search entire document for EPS
    import re
    eps_matches = re.findall(r'earnings per share.*?\$?(\d+\.\d+)', text[:5000], re.IGNORECASE)
    if eps_matches:
        print(f"[OK] Found EPS in document: {eps_matches}")
    else:
        print("[WARNING] No EPS found in first 5000 chars")

    # Show lines with EPS mentions
    lines = [l for l in text.split('\n') if 'EPS' in l.upper() or 'earnings per share' in l.lower()]
    if lines:
        print(f"\nFound {len(lines)} lines mentioning EPS")
        print("Sample lines:")
        for line in lines[:5]:
            print(f"  {line.strip()[:120]}")

else:
    print("No filing found")
