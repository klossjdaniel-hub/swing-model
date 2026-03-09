"""Test if yfinance has earnings estimates + actuals."""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import yfinance as yf

print("Testing yfinance for earnings data...\n")

# Get AAPL ticker
ticker = yf.Ticker("AAPL")

print("1. Checking calendar attribute...")
try:
    calendar = ticker.calendar
    print(f"   Type: {type(calendar)}")
    print(f"   Data: {calendar}\n")
except Exception as e:
    print(f"   [ERROR] {e}\n")

print("2. Checking earnings attribute...")
try:
    earnings = ticker.earnings
    print(f"   Type: {type(earnings)}")
    if earnings is not None and not earnings.empty:
        print(f"   Shape: {earnings.shape}")
        print(f"   Columns: {list(earnings.columns)}")
        print(f"\n   Sample:")
        print(earnings.head())
    else:
        print(f"   [WARNING] No data\n")
except Exception as e:
    print(f"   [ERROR] {e}\n")

print("\n3. Checking quarterly_earnings attribute...")
try:
    quarterly = ticker.quarterly_earnings
    print(f"   Type: {type(quarterly)}")
    if quarterly is not None and not quarterly.empty:
        print(f"   Shape: {quarterly.shape}")
        print(f"   Columns: {list(quarterly.columns)}")
        print(f"\n   Sample:")
        print(quarterly.head())

        # Check if has estimates
        if 'Estimate' in quarterly.columns or 'estimate' in str(quarterly.columns).lower():
            print(f"\n   [OK] Has estimate column!")
        else:
            print(f"\n   [WARNING] No obvious estimate column")
    else:
        print(f"   [WARNING] No data\n")
except Exception as e:
    print(f"   [ERROR] {e}\n")

print("\n4. Checking earnings_dates attribute...")
try:
    earnings_dates = ticker.earnings_dates
    print(f"   Type: {type(earnings_dates)}")
    if earnings_dates is not None and not earnings_dates.empty:
        print(f"   Shape: {earnings_dates.shape}")
        print(f"   Columns: {list(earnings_dates.columns)}")
        print(f"\n   Sample:")
        print(earnings_dates.head(10))

        # Check columns for estimates
        cols_str = str(earnings_dates.columns).lower()
        has_estimate = 'estimate' in cols_str or 'consensus' in cols_str
        has_actual = 'reported' in cols_str or 'actual' in cols_str

        print(f"\n   Has estimates: {has_estimate}")
        print(f"   Has actuals: {has_actual}")

        if has_estimate and has_actual:
            print(f"\n   [OK] FEASIBLE - yfinance has estimates + actuals!")
    else:
        print(f"   [WARNING] No data\n")
except Exception as e:
    print(f"   [ERROR] {e}\n")

print("\n5. Check all available data attributes...")
try:
    attrs = [x for x in dir(ticker) if not x.startswith('_') and 'earn' in x.lower()]
    print(f"   Earnings-related attributes: {attrs}")
except Exception as e:
    print(f"   [ERROR] {e}")

print("\n" + "="*60)
print("CONCLUSION:")
print("="*60)
print("\nChecking if yfinance is a viable solution...")
