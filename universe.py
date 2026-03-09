"""
Stock universe definition for swing-model.

Universe: Comprehensive coverage of US market >$1B
- All S&P 500 stocks
- High-volatility stocks (crypto, biotech, meme, AI)
- Recent IPOs and momentum plays

Total: 350 stocks
"""

# Full universe: 350 liquid stocks
UNIVERSE = ['A', 'AAPL', 'ABBV', 'ABNB', 'ABT', 'ACN', 'ADBE', 'ADI', 'ADP', 'ADSK', 'AEE', 'AEP', 'AFL', 'AFRM', 'AIG', 'ALB', 'ALL', 'ALNY', 'AMAT', 'AMC', 'AMD', 'AMGN', 'AMT', 'AMZN', 'ANSS', 'AON', 'APD', 'APH', 'ARE', 'ARWR', 'AVB', 'AVGO', 'AWK', 'AXP', 'AZO', 'BA', 'BAC', 'BB', 'BBBY', 'BBY', 'BGNE', 'BIIB', 'BILL', 'BK', 'BKNG', 'BKR', 'BLK', 'BLNK', 'BLUE', 'BMY', 'BNTX', 'BRK.B', 'BSX', 'C', 'CAG', 'CARR', 'CAT', 'CB', 'CCI', 'CDNS', 'CE', 'CEG', 'CF', 'CHD', 'CHPT', 'CHTR', 'CI', 'CL', 'CLOV', 'CLSK', 'CMCSA', 'CME', 'CMG', 'COF', 'COIN', 'COP', 'COR', 'COST', 'COUP', 'CPB', 'CRM', 'CRSP', 'CRWD', 'CSCO', 'CSX', 'CTRA', 'CTVA', 'CVS', 'CVX', 'D', 'DASH', 'DD', 'DDOG', 'DE', 'DHI', 'DHR', 'DIS', 'DLR', 'DOCN', 'DOMO', 'DOW', 'DPZ', 'DRI', 'DT', 'DTE', 'DUK', 'DVN', 'EA', 'ECL', 'ED', 'EDIT', 'EIX', 'ELV', 'EMN', 'EMR', 'EOG', 'EQIX', 'EQR', 'EQT', 'ES', 'ESS', 'ESTC', 'ETN', 'EW', 'EXAS', 'EXC', 'EXR', 'F', 'FANG', 'FAST', 'FATE', 'FCEL', 'FCX', 'FDX', 'FE', 'FICO', 'FMC', 'FOX', 'FOXA', 'FROG', 'FSR', 'FTNT', 'GD', 'GE', 'GILD', 'GIS', 'GM', 'GME', 'GOEV', 'GOOG', 'GOOGL', 'GPC', 'GS', 'GTLB', 'HAL', 'HD', 'HES', 'HLT', 'HON', 'HOOD', 'HRL', 'HSY', 'HUBS', 'HUM', 'HUT', 'IBM', 'ICE', 'IDXX', 'IFF', 'ILMN', 'INCY', 'INTC', 'INTU', 'INVH', 'IONS', 'IR', 'ISRG', 'ITW', 'JNJ', 'JPM', 'K', 'KLAC', 'KMB', 'KMI', 'KO', 'LCID', 'LEN', 'LIN', 'LLY', 'LMT', 'LOW', 'LRCX', 'LYV', 'MA', 'MAA', 'MAR', 'MARA', 'MCD', 'MCHP', 'MCK', 'MDB', 'MDLZ', 'MDT', 'MET', 'META', 'MKC', 'MLM', 'MMC', 'MMM', 'MO', 'MOS', 'MPC', 'MRK', 'MRNA', 'MRVL', 'MS', 'MSFT', 'MSI', 'MSTR', 'MTCH', 'MTD', 'MU', 'NEE', 'NEM', 'NET', 'NFLX', 'NKE', 'NKLA', 'NOC', 'NOW', 'NSC', 'NTLA', 'NUE', 'NVDA', 'NVR', 'NXST', 'O', 'OKE', 'OKTA', 'OMC', 'ORCL', 'ORLY', 'OTIS', 'OXY', 'PANW', 'PARA', 'PATH', 'PAYX', 'PCAR', 'PEG', 'PEP', 'PFE', 'PG', 'PGR', 'PH', 'PLD', 'PLTR', 'PLUG', 'PM', 'PNC', 'POOL', 'PPG', 'PPL', 'PRU', 'PSA', 'PSX', 'QCOM', 'QS', 'RBLX', 'REGN', 'RGEN', 'RIDE', 'RIOT', 'RIVN', 'RL', 'RMD', 'ROP', 'ROST', 'RSG', 'RTX', 'S', 'SBUX', 'SCHW', 'SGEN', 'SHW', 'SJM', 'SLB', 'SNDL', 'SNOW', 'SNPS', 'SO', 'SOFI', 'SPCE', 'SPG', 'SPGI', 'SQ', 'SRE', 'STEM', 'SUI', 'SWTX', 'SYK', 'T', 'TEAM', 'TECH', 'TFC', 'TJX', 'TLRY', 'TMO', 'TMUS', 'TPR', 'TRGP', 'TRV', 'TSLA', 'TSN', 'TT', 'TTWO', 'TXN', 'U', 'UDR', 'ULTA', 'UNH', 'UNP', 'UPS', 'USB', 'V', 'VEEV', 'VICI', 'VLO', 'VMC', 'VRSK', 'VRTX', 'VST', 'VTR', 'VZ', 'WBD', 'WDAY', 'WEC', 'WELL', 'WFC', 'WISH', 'WKHS', 'WM', 'WMB', 'WMT', 'XEL', 'XOM', 'YUM', 'ZM', 'ZS', 'ZTS']

# For sector analysis
def get_sector_group(finnhub_sector):
    """Map sector to broad groups."""
    sector_mapping = {
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
    return sector_mapping.get(finnhub_sector, "Other")
