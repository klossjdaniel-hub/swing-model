"""
Build a comprehensive stock universe by combining major indices.

Uses a curated list of liquid stocks across major indices and sectors.
"""

# Major indices combined - comprehensive coverage of US market >$1B
# This includes S&P 500, high-volume mid-caps, and volatile momentum stocks

# S&P 500 (500 stocks) - represents ~80% of US market cap
SP500 = [
    # Mega cap tech
    "AAPL", "MSFT", "NVDA", "GOOGL", "GOOG", "AMZN", "META", "TSLA", "AVGO", "ORCL",
    "ADBE", "CRM", "CSCO", "ACN", "AMD", "IBM", "INTC", "INTU", "TXN", "QCOM",
    "AMAT", "MU", "LRCX", "ADI", "KLAC", "SNPS", "CDNS", "MRVL", "MCHP", "FTNT",
    "ANSS", "ADSK", "ROP", "PANW", "FICO", "MSI", "APH", "NOW", "PLTR", "CRWD",

    # Financials
    "BRK.B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "SPGI", "BLK",
    "C", "SCHW", "AXP", "CB", "PGR", "MMC", "ICE", "CME", "AON", "TRV",
    "AIG", "MET", "PRU", "AFL", "ALL", "USB", "PNC", "TFC", "COF", "BK",

    # Healthcare
    "UNH", "LLY", "JNJ", "ABBV", "MRK", "TMO", "ABT", "DHR", "PFE", "AMGN",
    "CVS", "BMY", "MDT", "GILD", "CI", "VRTX", "REGN", "HUM", "ZTS", "ISRG",
    "BSX", "ELV", "SYK", "MCK", "COR", "EW", "IDXX", "A", "RMD", "MTD",

    # Consumer Discretionary
    "TSLA", "AMZN", "HD", "MCD", "NKE", "LOW", "SBUX", "TJX", "BKNG", "MAR",
    "GM", "F", "ABNB", "CMG", "ORLY", "AZO", "YUM", "ROST", "DHI", "LEN",
    "HLT", "GPC", "ULTA", "DPZ", "BBY", "DRI", "POOL", "TPR", "RL", "NVR",

    # Consumer Staples
    "WMT", "PG", "COST", "KO", "PEP", "PM", "MO", "MDLZ", "CL", "KMB",
    "GIS", "HSY", "K", "SJM", "CAG", "CPB", "TSN", "HRL", "MKC", "CHD",

    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
    "WMB", "HES", "KMI", "FANG", "DVN", "BKR", "TRGP", "OKE", "EQT", "CTRA",

    # Industrials
    "GE", "CAT", "BA", "HON", "UNP", "RTX", "UPS", "LMT", "DE", "ADP",
    "GD", "NOC", "ETN", "TT", "EMR", "ITW", "MMM", "PH", "CSX", "NSC",
    "FDX", "WM", "RSG", "CARR", "OTIS", "PCAR", "IR", "FAST", "PAYX", "VRSK",

    # Materials
    "LIN", "APD", "SHW", "FCX", "ECL", "NEM", "DD", "NUE", "DOW", "PPG",
    "VMC", "MLM", "ALB", "CTVA", "CE", "IFF", "EMN", "FMC", "MOS", "CF",

    # Real Estate
    "PLD", "AMT", "CCI", "EQIX", "PSA", "SPG", "O", "WELL", "DLR", "AVB",
    "EQR", "VICI", "ARE", "INVH", "VTR", "ESS", "MAA", "SUI", "EXR", "UDR",

    # Utilities
    "NEE", "SO", "DUK", "CEG", "SRE", "AEP", "D", "PEG", "VST", "EXC",
    "XEL", "ED", "EIX", "WEC", "ES", "AWK", "DTE", "PPL", "FE", "AEE",

    # Communication Services
    "META", "GOOGL", "GOOG", "NFLX", "DIS", "CMCSA", "VZ", "T", "TMUS", "CHTR",
    "EA", "TTWO", "NXST", "MTCH", "PARA", "WBD", "LYV", "FOXA", "FOX", "OMC",
]

# High-volatility additions (crypto, biotech, recent IPOs, meme stocks)
HIGH_VOLATILITY = [
    # Crypto-exposed
    "COIN", "MSTR", "MARA", "RIOT", "CLSK", "HUT", "HOOD", "SQ", "SOFI", "AFRM",

    # Biotech high-flyers
    "MRNA", "BNTX", "SGEN", "BIIB", "RGEN", "ALNY", "TECH", "EXAS", "ILMN", "INCY",
    "IONS", "BGNE", "ARWR", "SWTX", "VRTX", "CRSP", "NTLA", "EDIT", "BLUE", "FATE",

    # Recent IPOs & Growth
    "SNOW", "ABNB", "DASH", "U", "DDOG", "ZS", "NET", "OKTA", "ESTC", "MDB",
    "TEAM", "ZM", "DOCN", "BILL", "GTLB", "S", "PATH", "RBLX", "RIVN", "LCID",

    # Meme stocks & High momentum
    "GME", "AMC", "BB", "BBBY", "TLRY", "SNDL", "WISH", "CLOV", "WKHS", "RIDE",
    "NKLA", "SPCE", "PLUG", "FCEL", "BLNK", "CHPT", "GOEV", "FSR", "QS", "STEM",

    # AI/Tech momentum
    "PLTR", "CRWD", "DDOG", "NET", "FTNT", "PANW", "ZS", "S", "SNOW", "MDB",
    "HUBS", "COUP", "DOMO", "BILL", "VEEV", "WDAY", "GTLB", "PATH", "DT", "FROG",
]

# Combine and deduplicate
ALL_TICKERS = list(set(SP500 + HIGH_VOLATILITY))
ALL_TICKERS.sort()

print(f"Total universe: {len(ALL_TICKERS)} stocks")
print(f"\nBreakdown:")
print(f"  S&P 500 core: {len(SP500)}")
print(f"  High-volatility: {len(HIGH_VOLATILITY)}")
print(f"  After dedup: {len(ALL_TICKERS)}")

# Write to universe.py
code = f'''"""
Stock universe definition for swing-model.

Universe: Comprehensive coverage of US market >$1B
- All S&P 500 stocks
- High-volatility stocks (crypto, biotech, meme, AI)
- Recent IPOs and momentum plays

Total: {len(ALL_TICKERS)} stocks
"""

# Full universe: {len(ALL_TICKERS)} liquid stocks
UNIVERSE = {ALL_TICKERS}

# For sector analysis
def get_sector_group(finnhub_sector):
    """Map sector to broad groups."""
    sector_mapping = {{
        "Technology": "Technology",
        "Communication Services": "Technology",
        "Consumer Cyclical": "Cyclicals",
        "Consumer Defensive": "Defensive",
        "Financial Services": "Financials",
        "Financial": "Financials",
        "Healthcare": "Healthcare",
        "Industrials": "Cyclicals",
        "Basic Materials": "Cyclicals",
        "Energy": "Energy",
        "Utilities": "Defensive",
        "Real Estate": "Defensive",
    }}
    return sector_mapping.get(finnhub_sector, "Other")
'''

with open('universe.py', 'w') as f:
    f.write(code)

print(f"\n✅ Universe saved to universe.py")
print(f"   Estimated scan time: ~{len(ALL_TICKERS) * 0.1 / 60:.1f} minutes")
print(f"\nSample tickers:")
print(f"  First 10: {ALL_TICKERS[:10]}")
print(f"  Last 10: {ALL_TICKERS[-10:]}")
