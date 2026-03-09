"""
Stock universe definition for swing-model.

Phase 1: 50 stocks (testing)
Phase 2: 200 stocks (full backtest)

Mix of large caps (S&P 500) and mid caps ($1B-$10B) across diverse sectors:
- Technology
- Financials
- Healthcare
- Consumer (Discretionary + Staples)
- Energy
- Industrials
"""

# Phase 1 universe: 50 stocks for initial testing
PHASE1_UNIVERSE = [
    # Technology (10)
    "AAPL", "MSFT", "NVDA", "GOOGL", "META",
    "TSLA", "AVGO", "ORCL", "ADBE", "CRM",

    # Financials (8)
    "JPM", "BAC", "WFC", "GS", "MS",
    "C", "BLK", "AXP",

    # Healthcare (8)
    "UNH", "JNJ", "LLY", "ABBV", "MRK",
    "PFE", "TMO", "AMGN",

    # Consumer Discretionary (6)
    "AMZN", "HD", "MCD", "NKE", "SBUX",
    "TGT",

    # Consumer Staples (4)
    "WMT", "PG", "KO", "PEP",

    # Energy (5)
    "XOM", "CVX", "COP", "SLB", "EOG",

    # Industrials (5)
    "BA", "CAT", "UNP", "HON", "LMT",

    # Mid caps (4) - $1B-$10B
    "BROS", "PLTR", "RBLX", "SNOW"
]

# Phase 2 universe: 200 stocks (to be expanded later)
# Will add more stocks after Phase 1 validation
PHASE2_UNIVERSE = PHASE1_UNIVERSE  # Placeholder - expand later

# Current active universe
UNIVERSE = PHASE1_UNIVERSE

# Sector mappings (for Finnhub sector -> GICS sector grouping)
SECTOR_MAPPING = {
    # Finnhub sectors → Our 6 broad groups
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
}

# Known AMC reporters (earnings after market close)
KNOWN_AMC_REPORTERS = [
    "NVDA", "META", "GOOGL", "GOOG", "AMZN", "NFLX",
    "TSLA", "AMD", "AAPL", "MSFT"  # Note: AAPL/MSFT sometimes vary
]

# Known BMO reporters (earnings before market open)
KNOWN_BMO_REPORTERS = [
    "JPM", "BAC", "WFC", "C", "GS", "MS",
    "JNJ", "PG", "WMT", "HD", "UNH"
]

def get_universe(phase=1):
    """Return the appropriate stock universe for the given phase."""
    if phase == 1:
        return PHASE1_UNIVERSE
    elif phase == 2:
        return PHASE2_UNIVERSE
    else:
        raise ValueError(f"Unknown phase: {phase}")

def get_sector_group(finnhub_sector):
    """Map Finnhub sector to our 6 broad sector groups."""
    return SECTOR_MAPPING.get(finnhub_sector, "Other")
