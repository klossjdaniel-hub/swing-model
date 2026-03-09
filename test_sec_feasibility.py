"""
Deep feasibility test for SEC EDGAR earnings parsing.

Testing:
1. Can we find earnings 8-Ks reliably?
2. What format is the EPS data in?
3. Can we extract estimates + actuals?
4. How consistent is it across companies?
5. Historical coverage back to 2020?
"""

from edgar import *
import re

set_identity("User user@example.com")

def test_company_earnings(ticker, test_year="2024"):
    """Test earnings data extraction for a single company."""
    print(f"\n{'='*60}")
    print(f"Testing {ticker} - {test_year}")
    print('='*60)

    try:
        company = Company(ticker)
        print(f"Company: {company.name}")

        # Get 8-K filings (earnings are in Item 2.02)
        filings = company.get_filings(form="8-K").filter(date=f"{test_year}-01-01:{test_year}-12-31")

        print(f"Total 8-Ks in {test_year}: {len(filings)}")

        earnings_found = 0
        earnings_with_data = 0

        for filing in filings:
            filing_obj = filing.obj()

            # Check if it's an earnings announcement (Item 2.02)
            if hasattr(filing_obj, 'items') and '2.02' in str(filing_obj.items):
                earnings_found += 1
                print(f"\n  Earnings 8-K #{earnings_found}: {filing.filing_date}")

                # Try to get press release exhibit (usually 99.1)
                if hasattr(filing_obj, 'exhibits'):
                    for exhibit in filing_obj.exhibits:
                        if '99.1' in str(exhibit) or 'Press Release' in str(exhibit):
                            try:
                                # Get the text content
                                doc = exhibit.document()
                                text = doc.text

                                # Search for EPS data in text
                                eps_patterns = [
                                    r'earnings per share.*?\$?(\d+\.\d+)',
                                    r'EPS.*?\$?(\d+\.\d+)',
                                    r'diluted.*?(\$\d+\.\d+)',
                                    r'per share.*?\$?(\d+\.\d+)'
                                ]

                                found_eps = False
                                for pattern in eps_patterns:
                                    matches = re.findall(pattern, text[:3000], re.IGNORECASE)
                                    if matches:
                                        print(f"    Found EPS mentions: {matches[:3]}")
                                        found_eps = True
                                        break

                                # Look for "expected" or "estimate" or "consensus"
                                estimate_patterns = [
                                    r'expected.*?\$?(\d+\.\d+)',
                                    r'estimate.*?\$?(\d+\.\d+)',
                                    r'consensus.*?\$?(\d+\.\d+)',
                                    r'analyst.*?\$?(\d+\.\d+)'
                                ]

                                for pattern in estimate_patterns:
                                    matches = re.findall(pattern, text[:3000], re.IGNORECASE)
                                    if matches:
                                        print(f"    Found estimate mentions: {matches[:2]}")
                                        break

                                if found_eps:
                                    earnings_with_data += 1
                                    print(f"    ✓ Extractable EPS data found")
                                else:
                                    print(f"    ✗ No clear EPS data")

                                # Show sample text
                                lines = text.split('\n')[:30]
                                relevant_lines = [l for l in lines if 'EPS' in l.upper() or 'earnings per share' in l.lower()]
                                if relevant_lines:
                                    print(f"    Sample lines:")
                                    for line in relevant_lines[:3]:
                                        print(f"      {line.strip()[:80]}")

                            except Exception as e:
                                print(f"    Error reading exhibit: {e}")

                            break

        print(f"\n  Summary:")
        print(f"    Earnings 8-Ks found: {earnings_found}")
        print(f"    With extractable data: {earnings_with_data}")

        return {
            'ticker': ticker,
            'year': test_year,
            'earnings_found': earnings_found,
            'with_data': earnings_with_data,
            'success_rate': earnings_with_data / earnings_found if earnings_found > 0 else 0
        }

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

# Test multiple companies with different characteristics
test_companies = [
    ('AAPL', '2024'),  # Tech giant
    ('JPM', '2024'),   # Bank
    ('XOM', '2024'),   # Energy
    ('AAPL', '2023'),  # Historical
    ('AAPL', '2022'),  # Further back
]

print("="*60)
print("SEC EDGAR EARNINGS EXTRACTION FEASIBILITY TEST")
print("="*60)

results = []
for ticker, year in test_companies:
    result = test_company_earnings(ticker, year)
    if result:
        results.append(result)
    print("\n" + "."*60 + "\n")

# Final summary
print("\n" + "="*60)
print("OVERALL FEASIBILITY ASSESSMENT")
print("="*60)

if results:
    total_earnings = sum(r['earnings_found'] for r in results)
    total_with_data = sum(r['with_data'] for r in results)
    avg_success = sum(r['success_rate'] for r in results) / len(results)

    print(f"\nTotal earnings 8-Ks tested: {total_earnings}")
    print(f"With extractable EPS data: {total_with_data}")
    print(f"Average success rate: {avg_success*100:.1f}%")

    print("\n" + "="*60)
    if avg_success >= 0.7:
        print("✓ FEASIBLE - 70%+ success rate")
        print("Recommendation: Build the parser")
    elif avg_success >= 0.5:
        print("⚠ MARGINAL - 50-70% success rate")
        print("Recommendation: Could work but will miss some data")
    else:
        print("✗ NOT FEASIBLE - <50% success rate")
        print("Recommendation: Find alternative approach")
    print("="*60)
else:
    print("✗ FAILED - Could not extract any data")
