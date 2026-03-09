"""Debug why we can't access 8-K exhibit data."""

from edgar import *

set_identity("User user@example.com")

print("Testing detailed 8-K access for AAPL Q4 2024 earnings...\n")

company = Company("AAPL")
filings = company.get_filings(form="8-K").filter(date="2024-10-31:2024-10-31")

if filings:
    filing = filings[0]
    print(f"Filing date: {filing.filing_date}")
    print(f"Filing URL: {filing.filing_url}\n")

    # Get the filing object
    filing_obj = filing.obj()

    print(f"Filing object type: {type(filing_obj)}")
    print(f"Has items: {hasattr(filing_obj, 'items')}")
    print(f"Items: {filing_obj.items if hasattr(filing_obj, 'items') else 'N/A'}")
    print(f"Has exhibits: {hasattr(filing_obj, 'exhibits')}")

    if hasattr(filing_obj, 'exhibits'):
        exhibits = filing_obj.exhibits
        print(f"\nNumber of exhibits: {len(exhibits)}")

        for i, exhibit in enumerate(exhibits, 1):
            print(f"\n  Exhibit {i}:")
            print(f"    Type: {type(exhibit)}")
            print(f"    String repr: {str(exhibit)[:100]}")

            # Try to get document
            try:
                doc = exhibit.document()
                print(f"    Document type: {type(doc)}")
                print(f"    Has text: {hasattr(doc, 'text')}")

                if hasattr(doc, 'text'):
                    text = doc.text
                    print(f"    Text length: {len(text)} chars")
                    print(f"    First 200 chars: {text[:200]}")

                    # Search for EPS
                    if 'EPS' in text or 'earnings per share' in text.lower():
                        print(f"    [OK] Contains EPS data!")
                    else:
                        print(f"    [WARNING] No obvious EPS mentions")

            except Exception as e:
                print(f"    [ERROR] Can't read document: {e}")
    else:
        print("\n[ERROR] No exhibits attribute found")

        # Try alternative access methods
        print("\nTrying alternative methods...")
        print(f"Dir of filing_obj: {[x for x in dir(filing_obj) if not x.startswith('_')]}")

else:
    print("No filings found for that date")
