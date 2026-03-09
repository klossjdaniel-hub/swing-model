"""Check what actual data is in the earnings object."""

from edgar import *
import sys

set_identity("User user@example.com")

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("Checking AAPL earnings data structures...\n")

company = Company("AAPL")
filings = company.get_filings(form="8-K").filter(date="2024-10-31:2024-10-31")

filing_obj = filings[0].obj()
earnings = filing_obj.earnings

print("1. Summary:")
try:
    summary = earnings.summary
    print(f"   Type: {type(summary)}")
    print(f"   Content: {summary}\n")
except Exception as e:
    print(f"   ERROR: {e}\n")

print("2. Income Statement:")
try:
    income = earnings.income_statement
    print(f"   Type: {type(income)}")
    if income is not None:
        print(f"   {income}\n")
    else:
        print("   None\n")
except Exception as e:
    print(f"   ERROR: {e}\n")

print("3. EPS Reconciliation:")
try:
    eps_recon = earnings.eps_reconciliation
    print(f"   Type: {type(eps_recon)}")
    if eps_recon is not None:
        print(f"   {eps_recon}\n")
    else:
        print("   None\n")
except Exception as e:
    print(f"   ERROR: {e}\n")

print("4. Financial Tables:")
try:
    tables = earnings.financial_tables
    print(f"   Type: {type(tables)}")
    print(f"   Number of tables: {len(tables) if tables else 0}")
    if tables and len(tables) > 0:
        for i, table in enumerate(tables[:3]):
            print(f"\n   Table {i+1}:")
            print(f"   {table}")
except Exception as e:
    print(f"   ERROR: {e}\n")

print("\n" + "="*60)
print("CRITICAL QUESTION:")
print("="*60)
print("Does SEC provide analyst estimates in 8-K filings?")
print("\nAnswer: NO - 8-K filings only contain company-reported actuals.")
print("Analyst estimates come from research firms, not SEC filings.")
print("\nThis means we CANNOT get estimates from SEC/edgartools alone.")
