"""Test NASDAQ finance_calendars library for historical earnings estimates."""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from finance_calendars import EarningsCalendar
    import datetime

    print("Testing NASDAQ finance_calendars library...\n")

    # Initialize calendar
    ec = EarningsCalendar()

    # Test 1: Get earnings for a specific date in the past
    print("Test 1: Get historical earnings for 2024-01-01")
    try:
        date = datetime.date(2024, 1, 1)
        earnings = ec.get_earnings_on_date(date)

        if earnings:
            print(f"  [OK] Found {len(earnings)} earnings on 2024-01-01")

            # Show first earnings
            if len(earnings) > 0:
                first = earnings[0]
                print(f"\n  Sample earnings:")
                print(f"    Ticker: {first.get('symbol', 'N/A')}")
                print(f"    Company: {first.get('companyName', 'N/A')}")
                print(f"    EPS Estimate: ${first.get('epsForecast', 'N/A')}")
                print(f"    Date: {first.get('date', 'N/A')}")

                # Check what fields are available
                print(f"\n  Available fields: {list(first.keys())}")

                # Check if we have historical actuals
                if 'epsActual' in first:
                    print(f"    [OK] Has epsActual field!")
                else:
                    print(f"    [WARNING] No epsActual field")

        else:
            print("  [WARNING] No earnings found")

    except Exception as e:
        print(f"  [ERROR] {e}")

    # Test 2: Get earnings for a specific ticker
    print("\n\nTest 2: Get AAPL earnings history")
    try:
        # Try to get historical earnings for AAPL
        # Check if method exists
        if hasattr(ec, 'get_earnings_by_ticker'):
            aapl_earnings = ec.get_earnings_by_ticker('AAPL')
            print(f"  [OK] Found {len(aapl_earnings)} AAPL earnings")
        elif hasattr(ec, 'get_ticker_earnings'):
            aapl_earnings = ec.get_ticker_earnings('AAPL')
            print(f"  [OK] Found {len(aapl_earnings)} AAPL earnings")
        else:
            print(f"  [INFO] Methods available: {[x for x in dir(ec) if not x.startswith('_')]}")

    except Exception as e:
        print(f"  [ERROR] {e}")

    # Test 3: Check date range capabilities
    print("\n\nTest 3: Get earnings for date range (2023-2024)")
    try:
        start_date = datetime.date(2023, 1, 1)
        end_date = datetime.date(2024, 12, 31)

        if hasattr(ec, 'get_earnings_in_date_range'):
            range_earnings = ec.get_earnings_in_date_range(start_date, end_date)
            print(f"  [OK] Found {len(range_earnings)} earnings in 2023-2024")
        else:
            print(f"  [INFO] No date range method found")
            print(f"  Available methods: {[x for x in dir(ec) if 'earn' in x.lower() and not x.startswith('_')]}")

    except Exception as e:
        print(f"  [ERROR] {e}")

    print("\n" + "="*60)
    print("CONCLUSION:")
    print("="*60)
    if earnings and len(earnings) > 0:
        has_estimate = 'epsForecast' in earnings[0] or 'epsEstimate' in earnings[0]
        has_actual = 'epsActual' in earnings[0]

        print(f"\n  Can access NASDAQ earnings data: YES")
        print(f"  Has EPS estimates: {has_estimate}")
        print(f"  Has EPS actuals: {has_actual}")

        if has_estimate and has_actual:
            print(f"\n  [OK] FEASIBLE - Has both estimates and actuals!")
        elif has_estimate:
            print(f"\n  [PARTIAL] Has estimates, need to check for actuals")
        else:
            print(f"\n  [WARNING] May not have estimates")
    else:
        print(f"\n  [ERROR] Could not retrieve data")

except ImportError as e:
    print(f"[ERROR] finance_calendars not installed properly: {e}")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
