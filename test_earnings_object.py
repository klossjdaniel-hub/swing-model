"""Test if edgartools EarningsRelease object has estimate data."""

from edgar import *
import sys

set_identity("User user@example.com")

# Redirect to UTF-8 to avoid encoding errors
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("Testing edgartools earnings object...\n")

company = Company("AAPL")
filings = company.get_filings(form="8-K").filter(date="2024-10-31:2024-10-31")

if filings:
    filing = filings[0]
    filing_obj = filing.obj()

    if filing_obj.has_earnings:
        earnings = filing_obj.earnings
        print(f"Earnings object type: {type(earnings)}\n")

        # Check all available attributes
        attrs = [x for x in dir(earnings) if not x.startswith('_')]
        print(f"Available attributes/methods:")
        for attr in attrs:
            print(f"  - {attr}")

        print("\n" + "="*60)

        # Try to access common fields
        fields_to_check = [
            'eps', 'eps_estimate', 'eps_actual', 'eps_expected',
            'revenue', 'revenue_estimate', 'revenue_actual',
            'date', 'period', 'quarter', 'fiscal_year',
            'data', 'values', 'metrics'
        ]

        print("\nChecking for data fields:")
        for field in fields_to_check:
            if hasattr(earnings, field):
                try:
                    value = getattr(earnings, field)
                    print(f"  {field}: {value}")
                except Exception as e:
                    print(f"  {field}: ERROR - {e}")

        # Try to see if there's raw data
        if hasattr(earnings, '__dict__'):
            print(f"\nEarnings __dict__:")
            try:
                for key, value in earnings.__dict__.items():
                    print(f"  {key}: {str(value)[:100]}")
            except Exception as e:
                print(f"  ERROR: {e}")

        # Try to get the DataFrame if it exists
        if hasattr(earnings, 'df') or hasattr(earnings, 'dataframe'):
            print("\nHas DataFrame!")
            try:
                df = earnings.df if hasattr(earnings, 'df') else earnings.dataframe
                print(df)
            except Exception as e:
                print(f"  ERROR: {e}")

print("\n" + "="*60)
print("CONCLUSION:")
print("="*60)
print("\nQ: Does edgartools provide EPS estimates?")
print("A: Checking above output...")
