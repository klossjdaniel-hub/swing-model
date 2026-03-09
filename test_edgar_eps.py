"""Test extracting EPS from SEC 8-K earnings filings using edgartools."""

from edgar import *

set_identity("User user@example.com")

print("Testing EPS extraction from AAPL 8-K filing...\n")

try:
    # Get AAPL
    company = Company("AAPL")

    # Get most recent earnings 8-K
    filings = company.get_filings(form="8-K").filter(date="2024-10-01:")
    earnings_filing = None

    for filing in filings:
        filing_obj = filing.obj()
        if hasattr(filing_obj, 'items'):
            if '2.02' in str(filing_obj.items):
                earnings_filing = filing_obj
                print(f"Found earnings 8-K from: {filing.filing_date}\n")
                break

    if earnings_filing:
        # Try to get the press release exhibit
        if hasattr(earnings_filing, 'exhibits'):
            exhibits = earnings_filing.exhibits
            print(f"Exhibits: {len(exhibits)} found\n")

            # Usually the press release is Exhibit 99.1
            for exhibit in exhibits:
                if '99.1' in str(exhibit):
                    print(f"Found press release exhibit: {exhibit}\n")

                    # Get the text content
                    content = exhibit.document().text[:5000]  # First 5000 chars

                    # Look for EPS mentions
                    lines = content.split('\n')
                    print("Searching for EPS data in press release...\n")

                    for i, line in enumerate(lines):
                        if 'EPS' in line.upper() or 'EARNINGS PER SHARE' in line.upper():
                            # Print context (3 lines before and after)
                            start = max(0, i-2)
                            end = min(len(lines), i+3)
                            print("Found EPS mention:")
                            for j in range(start, end):
                                print(f"  {lines[j]}")
                            print()

                    break

        print("\n[OK] Can access 8-K filing content")
        print("[NOTE] Need to build parser to extract structured EPS data from text")
        print("[NOTE] But the data IS there and completely FREE")

    else:
        print("[WARNING] Could not find earnings 8-K")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
