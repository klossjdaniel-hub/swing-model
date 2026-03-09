"""Test proper 8-K earnings data extraction - FIXED."""

from edgar import *
import re

set_identity("User user@example.com")

print("Testing AAPL Q4 2024 earnings extraction...\n")

company = Company("AAPL")
filings = company.get_filings(form="8-K").filter(date="2024-10-31:2024-10-31")

if filings:
    filing = filings[0]
    filing_obj = filing.obj()

    print(f"Filing date: {filing.filing_date}")
    print(f"Has press release: {filing_obj.has_press_release}")
    print(f"Has earnings: {filing_obj.has_earnings}\n")

    # Access press releases
    if filing_obj.has_press_release:
        press_releases = filing_obj.press_releases

        if press_releases and len(press_releases) > 0:
            pr = press_releases[0]  # Get first press release
            print(f"Press Release type: {type(pr)}\n")

            # Try different ways to get text
            text = None
            try:
                # Try as method
                if callable(getattr(pr, 'text', None)):
                    text = pr.text()
                    print(f"[OK] Got text via text() method: {len(text)} chars\n")
            except:
                pass

            if not text:
                try:
                    # Try as property
                    text = pr.text
                    print(f"[OK] Got text via text property: {len(text)} chars\n")
                except:
                    pass

            if not text:
                try:
                    # Try getting document
                    doc = pr.document if hasattr(pr, 'document') else pr
                    if callable(getattr(doc, 'text', None)):
                        text = doc.text()
                    else:
                        text = doc.text
                    print(f"[OK] Got text via document: {len(text)} chars\n")
                except Exception as e:
                    print(f"[ERROR] Can't get text: {e}\n")

            if text:
                # Search for EPS data
                print("Searching for EPS data...\n")

                # Pattern 1: Look for "diluted earnings per share"
                eps_pattern1 = re.findall(r'diluted earnings per share.*?\$?(\d+\.\d+)', text[:5000], re.IGNORECASE)
                if eps_pattern1:
                    print(f"  Found diluted EPS: ${eps_pattern1}")

                # Pattern 2: Look for table-style data
                eps_pattern2 = re.findall(r'EPS.*?[\$]?(\d+\.\d+)', text[:5000], re.IGNORECASE)
                if eps_pattern2:
                    print(f"  Found EPS values: ${eps_pattern2}")

                # Pattern 3: Look for estimates
                estimate_pattern = re.findall(r'(estimate|expected|consensus).*?\$?(\d+\.\d+)', text[:5000], re.IGNORECASE)
                if estimate_pattern:
                    print(f"  Found estimates: {estimate_pattern[:3]}")

                # Show lines containing EPS
                lines = [l for l in text.split('\n') if 'EPS' in l.upper() or 'earnings per share' in l.lower()]
                if lines:
                    print(f"\n  Lines with EPS mentions ({len(lines)} total):")
                    for line in lines[:5]:
                        clean_line = ' '.join(line.split())  # Clean whitespace
                        print(f"    {clean_line[:120]}")
                else:
                    print("\n  [WARNING] No lines with EPS found")

                # Check if we found usable data
                if eps_pattern1 or eps_pattern2:
                    print("\n[OK] FEASIBLE - Can extract EPS actual values")
                else:
                    print("\n[WARNING] MARGINAL - EPS present but hard to extract")

            else:
                print("[ERROR] Could not access press release text")

    # Also test direct earnings access
    if filing_obj.has_earnings:
        print("\n" + "="*60)
        print("Testing earnings attribute...")
        earnings = filing_obj.earnings

        print(f"Type: {type(earnings)}")

        # Check if it's structured data
        if hasattr(earnings, 'eps'):
            print(f"[OK] Has eps attribute: {earnings.eps}")
        elif hasattr(earnings, '__dict__'):
            print(f"Earnings dict: {earnings.__dict__}")
        else:
            print(f"Available: {[x for x in dir(earnings) if not x.startswith('_')][:10]}")

else:
    print("No filing found")
