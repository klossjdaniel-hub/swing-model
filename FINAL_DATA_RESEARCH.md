# Final Comprehensive Data Source Research
## Historical Earnings Estimates + Actuals for Free

**Date:** March 9, 2026
**Objective:** Find ANY free source for 5 years of historical earnings estimates + actuals for 50 US stocks

---

## 🔍 Research Summary

I conducted an exhaustive search across:
- ✅ Open source GitHub projects
- ✅ Chinese/Asian data providers (Tushare, AKShare)
- ✅ Academic datasets (WRDS, Kaggle)
- ✅ Scraping libraries (Yahoo Finance, Seeking Alpha)
- ✅ Free API providers globally
- ✅ Alternative APIs from different countries

---

## 📊 All Options Found

### 1. **Alpha Vantage** ⭐ BEST FREE OPTION
**Status:** ✅ Working, Free, Has Estimates + Actuals

- **Free Tier:** 25 calls/day
- **Data:** `EARNINGS` function with EPS estimates + actuals
- **History:** Full historical back to IPO
- **Cost:** $0 forever
- **Time to fetch 50 stocks:** 2-3 days (25 calls/day limit)
- **Reliability:** Medium (free tier could be paywalled eventually)
- **Setup:** Sign up at [alphavantage.co](https://www.alphavantage.co/)

**Sources:**
- [Alpha Vantage API](https://www.alphavantage.co/)
- [Alpha Vantage 2026 Guide](https://alphalog.ai/blog/alphavantage-api-complete-guide)
- [Getting API Key](https://www.macroption.com/alpha-vantage-api-key/)

**Verdict:** FEASIBLE but slow

---

### 2. **yfinance / yahoo_fin**
**Status:** ⚠️ Broken/Unreliable

- **yfinance:** Has `earnings_dates` attribute with estimates + actuals
- **yahoo_fin:** Abandoned since 2021, no longer works
- **Issue:** Yahoo Finance keeps changing page structure, breaks scrapers
- **Dependency hell:** websockets version conflicts

**Sources:**
- [yfinance PyPI](https://pypi.org/project/yfinance/)
- [yahoo_fin Documentation](https://theautomatic.net/yahoo_fin-documentation/)
- [How to Scrape Yahoo Finance 2026](https://brightdata.com/blog/how-tos/scrape-yahoo-finance-guide)

**Verdict:** NOT RELIABLE - breaks frequently

---

### 3. **Financial Modeling Prep (FMP)**
**Status:** ❌ Paywalled

- **Free tier deprecated:** August 31, 2025
- **Historical earnings:** Premium only (403 Forbidden)
- **Tested with your API key:** Failed

**Sources:**
- [FMP Pricing](https://site.financialmodelingprep.com/developer/docs/pricing)

**Verdict:** NOT FREE ANYMORE

---

###4. **API Ninjas - Earnings Calendar**
**Status:** ⚠️ Limited Free Tier

- **Free tier:** Unknown call limits
- **Historical data:** Pre-2025 data requires premium subscription
- **Data:** Estimates + actuals for 2025+

**Sources:**
- [API Ninjas Earnings Calendar](https://api-ninjas.com/api/earningscalendar)
- [API Ninjas Pricing](https://api-ninjas.com/pricing)

**Verdict:** NOT SUFFICIENT (only recent data on free tier)

---

### 5. **Tushare / AKShare (China)**
**Status:** ⚠️ Limited US Coverage

- **Tushare:** Points-based system, limited free points
- **AKShare:** Can access US stocks with `stock_us_daily("AAPL")`
- **Issue:** Primarily focused on Chinese/HK markets
- **US earnings data:** Unclear if includes estimates

**Sources:**
- [TuShare GitHub](https://github.com/waditu/tushare)
- [AKShare GitHub](https://github.com/akfamily/akshare)
- [OpenBB with AKShare](https://openbb.co/blog/extending-openbb-for-a-share-and-hong-kong-stock-analysis-with-akshare-and-tushare)

**Verdict:** UNCERTAIN - need to test US earnings support

---

### 6. **SEC EDGAR (edgartools)**
**Status:** ✅ Working but ❌ No Estimates

- **Free:** Unlimited, forever
- **Data:** EPS actuals from 8-K filings
- **Missing:** Analyst estimates (not in SEC filings)
- **Tested:** Successfully extracted actuals for AAPL

**Sources:**
- [edgartools PyPI](https://pypi.org/project/edgartools/)
- [edgartools GitHub](https://github.com/dgunning/edgartools)
- [EdgarTools Documentation](https://edgartools.readthedocs.io/)

**Verdict:** NOT FEASIBLE - no estimates

---

### 7. **WRDS (Wharton Research)**
**Status:** ✅ Has Data but ❌ Requires University Access

- **Data:** IBES analyst estimates, Compustat
- **Access:** Free only if your university subscribes
- **Individual access:** Not available

**Sources:**
- [WRDS Homepage](https://wrds-www.wharton.upenn.edu/)
- [WRDS UC Berkeley Guide](https://guides.lib.berkeley.edu/wrdsdata)

**Verdict:** NOT ACCESSIBLE (need institutional subscription)

---

### 8. **Kaggle Dataset: US Historical Stock Prices with Earnings Data**
**Status:** 🔍 Needs Investigation

- **Dataset:** [US historical stock prices with earnings data](https://www.kaggle.com/datasets/tsaustin/us-historical-stock-prices-with-earnings-data)
- **Format:** CSV download
- **Access:** Free Kaggle account
- **Unknown:** Whether it has estimates or just actuals

**Sources:**
- [Kaggle Dataset](https://www.kaggle.com/datasets/tsaustin/us-historical-stock-prices-with-earnings-data)

**Verdict:** MAYBE - need to download and check

---

### 9. **NASDAQ Finance Calendars (Python)**
**Status:** ❌ Broken Package

- **GitHub:** [finance_calendars](https://github.com/s-kerin/finance_calendars)
- **Issue:** Package installed but broken (empty exports)
- **Tested:** Import failed

**Verdict:** NOT WORKING

---

### 10. **Open Source GitHub Projects**
**Status:** ⚠️ Mostly Transcripts, Not Estimates

- **pystock-data:** Unmaintained since 2009
- **EarningsCall_Dataset:** Transcripts only
- **bearbull-finance:** Has estimates vs actuals but unclear if free API

**Sources:**
- [pystock-data GitHub](https://github.com/eliangcs/pystock-data)
- [bearbull-finance GitHub](https://github.com/bearbull-io/bearbull-finance)

**Verdict:** NOT VIABLE

---

### 11. **FinCall-Surprise Academic Dataset**
**Status:** ✅ Has Data but ❌ Limited Scope

- **Timeframe:** 2019-2021 only (3 years)
- **Data:** Earnings surprises with transcripts
- **Access:** Free research dataset (arXiv)

**Sources:**
- [FinCall-Surprise Paper](https://arxiv.org/pdf/2510.03965)

**Verdict:** TOO LIMITED (only 3 years, old data)

---

## 🎯 FINAL VERDICT

After exhaustive research across **11 different options**, here are the ONLY truly free, working solutions:

### ✅ **Option A: Alpha Vantage** (RECOMMENDED)
- 25 calls/day = 2-3 days to fetch 50 stocks
- Has estimates + actuals
- Completely free
- Actively maintained
- **Downside:** Slow, could be paywalled in future

### 🔍 **Option B: Kaggle Dataset** (NEEDS TESTING)
- Download CSV from [here](https://www.kaggle.com/datasets/tsaustin/us-historical-stock-prices-with-earnings-data)
- Free Kaggle account
- Unknown if has estimates
- **Downside:** Static snapshot, not API

### ⚠️ **Option C: Accept 9 Events from Finnhub**
- Use current Finnhub data (2025-2026)
- Build minimal proof-of-concept
- See if ANY signal exists
- **Downside:** Too few events for real training

---

## 💡 HONEST RECOMMENDATION

### If you can wait 2-3 days:
**Use Alpha Vantage** - It's the ONLY reliable free option with estimates + actuals.

### If you need data NOW:
1. **Download Kaggle dataset** to check if it has what we need
2. If Kaggle works: Use it immediately
3. If Kaggle doesn't have estimates: We're blocked unless you pay

### Reality Check:
**Earnings estimates are proprietary data.** Bloomberg, FactSet, Refinitiv charge thousands per year for this data. The fact that Alpha Vantage gives it away for free (25/day) is remarkable and could end anytime.

**The project IS viable** with Alpha Vantage, but it requires:
- Patience (2-3 days to fetch)
- Accepting risk that free tier could disappear
- Being ready to pivot if Alpha Vantage changes

---

## 🚀 NEXT STEPS

**Option 1: Go with Alpha Vantage**
1. Sign up at https://www.alphavantage.co/
2. Get free API key (no credit card)
3. I'll build fetcher that runs over 2-3 days
4. Fetch 5 years of data for 50 stocks
5. Build model

**Option 2: Test Kaggle Dataset**
1. You download CSV from [Kaggle](https://www.kaggle.com/datasets/tsaustin/us-historical-stock-prices-with-earnings-data)
2. I inspect if it has estimates
3. If yes: import into database
4. If no: back to Option 1

**Option 3: Pay for Data**
- Databento: ~$50 one-time for 5 years
- FMP Starter: $14/month
- Polygon: $30/month

---

## 📚 ALL SOURCES CITED

1. [Alpha Vantage API](https://www.alphavantage.co/)
2. [Alpha Vantage 2026 Guide](https://alphalog.ai/blog/alphavantage-api-complete-guide)
3. [Financial Modeling Prep](https://site.financialmodelingprep.com/developer/docs)
4. [edgartools GitHub](https://github.com/dgunning/edgartools)
5. [TuShare GitHub](https://github.com/waditu/tushare)
6. [AKShare GitHub](https://github.com/akfamily/akshare)
7. [WRDS Homepage](https://wrds-www.wharton.upenn.edu/)
8. [Kaggle US Stock Dataset](https://www.kaggle.com/datasets/tsaustin/us-historical-stock-prices-with-earnings-data)
9. [API Ninjas Earnings Calendar](https://api-ninjas.com/api/earningscalendar)
10. [yfinance PyPI](https://pypi.org/project/yfinance/)
11. [yahoo_fin Documentation](https://theautomatic.net/yahoo_fin-documentation/)
12. [FinCall-Surprise Dataset](https://arxiv.org/pdf/2510.03965)
13. [NASDAQ finance_calendars](https://github.com/s-kerin/finance_calendars)
14. [bearbull-finance GitHub](https://github.com/bearbull-io/bearbull-finance)
15. [OpenBB Platform](https://openbb.co/)

---

**Research completed:** March 9, 2026
**Bottom line:** Alpha Vantage or Kaggle dataset are your only free options. Everything else is either broken, paywalled, or doesn't have estimates.
