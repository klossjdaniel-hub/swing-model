"""Test yahoo_fin library for historical earnings data."""

from yahoo_fin import stock_info as si

# Test with AAPL
print("Testing yahoo_fin for AAPL earnings history...\n")

try:
    # Get earnings history
    earnings_history = si.get_earnings_history('AAPL')

    print(f"Found {len(earnings_history)} earnings reports for AAPL\n")

    # Show first 3 earnings
    print("Sample earnings data:")
    for i, earning in enumerate(earnings_history[:3], 1):
        print(f"\n{i}. {earning.get('startdatetime', 'N/A')}")
        print(f"   EPS Estimate: {earning.get('epsestimate', 'N/A')}")
        print(f"   EPS Actual: {earning.get('epsactual', 'N/A')}")
        print(f"   Surprise: {earning.get('epssurprisepct', 'N/A')}")

    print(f"\n✓ SUCCESS: yahoo_fin works and has historical earnings data!")
    print(f"✓ Available fields: {list(earnings_history[0].keys())}")

except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
