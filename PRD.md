# Swing Model PRD v4 - UPDATED

**Last Updated:** March 9, 2026
**Status:** Phase 1 Complete - Pivoting Data Strategy

---

## Executive Summary

Building a machine learning model to predict **post-earnings mean reversion** for swing trading. The model identifies when a stock's initial earnings reaction is likely to reverse within 1-3 days.

**Key Insight:** Markets often overreact to earnings. The model learns behavioral patterns (emotional overreaction signatures) rather than earnings math.

---

## What We've Accomplished

### ✅ Phase 1 Pipeline (COMPLETE)
- SQLite database created with 7 tables
- VIX data: 1,553 days fetched from yfinance
- Company metadata: 50/50 stocks fetched from Finnhub
- Price data: 76,557 records (~5 years per stock) from yfinance
- Earnings data: 188 records from Finnhub (2025-2026 only)

### ⚠️ Critical Discovery
Finnhub free tier only provides **last 4-6 quarters** of earnings, not 5 years as initially assumed. After filtering for significant moves (>2%, >1.5x volume), only **9 events** remain - far too few to train a model.

**Minimum needed:** 100-150 events (2-3 years)
**Ideal:** 200-300 events (3-5 years)

---

## Updated Data Strategy

### Previous Approaches (Tested & Rejected)
- ❌ Finnhub free tier: Only has last 4-6 quarters (insufficient history)
- ❌ FMP free tier: Deprecated Aug 31, 2025 (paywalled)
- ❌ yahoo_fin/yfinance: Broken/unreliable scrapers
- ❌ SEC/edgartools: Only has actuals, no estimates
- ❌ NASDAQ finance_calendars: Broken package

### Final Approach (After Exhaustive Research)
- ✅ **Alpha Vantage free tier** for historical earnings backfill (Phase 1-2)
  - 25 API calls/day
  - Full historical data (back to IPO)
  - EPS estimates + actuals
  - Surprise percentages
  - Takes 2-3 days to fetch 50 stocks
  - Completely free, no credit card

- ✅ **Finnhub free tier** for ongoing daily updates (Phase 3)
  - 60 calls/min
  - Recent earnings with estimates + actuals
  - Perfect for 2-5 stocks/day production use

### Why This Hybrid Approach?
1. **Alpha Vantage:** Deep historical archive (one-time backfill)
2. **Finnhub:** Ongoing recent data (daily updates)
3. **Different tools for different jobs** - Optimize for each phase
4. **Total cost:** $0 forever

### Long-term Sustainability
- Alpha Vantage backfill is one-time (risk only during 2-3 day fetch window)
- Finnhub for Phase 3 is proven (already tested in Phase 1)
- If Alpha Vantage ever paywalls: Kaggle dataset fallback or accept paying ~$50 for Databento one-time backfill

---

## Architecture

### Data Sources

| Source | Data | Timeframe | Cost | Status |
|--------|------|-----------|------|--------|
| **yfinance** | Historical prices (OHLCV) | 2020-present | Free | ✅ Working |
| **yfinance** | VIX daily close | 2020-present | Free | ✅ Working |
| **Finnhub** | Company metadata | Current | Free (60/min) | ✅ Working |
| **Alpha Vantage** | Historical earnings (full history) | 2020-2025 | Free (25/day) | 🔄 Next step |
| **Finnhub** | Daily earnings updates | Phase 3 | Free (60/min) | ⏳ Future |

### Database (SQLite → Supabase)
- **Phase 1-2:** Local SQLite (`data/swing_model.db`)
- **Phase 3:** Migrate to Supabase Postgres (free tier: 500MB, 2GB bandwidth/month)

### Automation (Phase 3)
- **GitHub Actions** (free: 2,000 min/month)
  - Daily evening predictions (23:00 UTC)
  - Daily scoring/validation (21:00 UTC)
  - No servers, no hosting costs

---

## Data Pipeline

### Phase 1: Historical Backfill (IN PROGRESS)

**Step 1: Foundation ✅**
- ✅ SQLite schema created
- ✅ VIX data fetched
- ✅ Company metadata fetched
- ✅ 5 years price data fetched

**Step 2: Earnings Backfill 🔄**
- 🔄 Fetch 5 years earnings from FMP
- 🔄 Build events dataset with labels
- 🔄 Validate data quality

**Expected Output:**
- 200-300 labeled events
- 2020-2025 timeframe
- Each event has:
  - Day 0 characteristics (move size, volume, EPS surprise)
  - Outcome labels (Day 1-3 returns, reversion flags)

### Phase 2: Model Training (NEXT)
- Train/test split with walk-forward validation
- 3 time-based folds (avoid lookahead bias)
- Models: XGBoost + Logistic Regression
- Metrics: Accuracy, AUC, directional accuracy
- Feature importance analysis

### Phase 3: Production Deployment (FUTURE)
- Migrate to Supabase
- GitHub Actions automation
- Daily predictions and scoring
- Web interface for viewing signals

---

## Event Definition & Filters

### What Qualifies as an Event?
1. **Earnings announcement** with EPS estimate + actual
2. **Day 0 move ≥ 2%** (absolute)
3. **Volume ≥ 1.5x** 20-day average
4. **Has Day 1-3 follow-through data** (not at end of dataset)

### Why These Filters?
- **2% move threshold:** Too small = noise, not tradeable
- **1.5x volume:** Ensures real reaction, not thin trading
- **EPS data required:** Need surprise % as feature

---

## Reversion Definition

**Relative threshold:** Move reverses by ≥30% of initial Day 0 move

**Examples:**
- Stock up 5% on earnings → Down 1.5%+ = reversion ✅
- Stock down 8% on earnings → Up 2.4%+ = reversion ✅
- Stock up 10% → Down 0.5% = no reversion ❌

**Why relative vs absolute?**
- Scales with volatility
- 30% reversal on 3% move (0.9%) is meaningful
- Avoids false positives from small noise

---

## Features for Model

### Event Characteristics
- `day0_return` - Size of initial move
- `day0_return_abs` - Absolute move size
- `direction` - Up (1) or down (-1)
- `volume_ratio` - Volume vs 20-day average
- `eps_surprise_pct` - (Actual - Est) / |Est|
- `revenue_surprise_pct` - Revenue surprise %
- `beat_miss` - Beat / miss / inline label

### Context Features
- `pre_earnings_drift_5d` - Run-up before earnings
- `pre_earnings_drift_20d` - Longer-term trend
- `vix_day0` - Market fear gauge
- `day_of_week` - Timing effect
- `sector` - Sector behavior differences
- `market_cap_bucket` - Large vs mid cap

### Target Variables
- `reverted_day1` - Binary (0/1)
- `reverted_day2` - Binary (0/1)
- `reverted_day3` - Binary (0/1)
- `return_day1` - Actual return %
- `return_day2` - Actual return %
- `return_day3` - Actual return %

---

## Universe (Phase 1)

50 stocks across 6 sectors:

**Technology (10):** AAPL, MSFT, NVDA, GOOGL, META, TSLA, AVGO, ORCL, ADBE, CRM
**Financials (8):** JPM, BAC, WFC, GS, MS, C, BLK, AXP
**Healthcare (7):** UNH, JNJ, LLY, ABBV, MRK, PFE, TMO, AMGN
**Consumer (8):** AMZN, HD, MCD, NKE, SBUX, TGT, WMT, PG, KO, PEP
**Energy (5):** XOM, CVX, COP, SLB, EOG
**Industrials (5):** BA, CAT, UNP, HON, LMT
**Other (3):** BROS, PLTR, RBLX, SNOW

---

## Walk-Forward Validation

**Strict time-based splits** (no future data leakage):

**Fold 1:**
- Train: 2020-2022
- Test: 2023

**Fold 2:**
- Train: 2020-2023
- Test: 2024

**Fold 3:**
- Train: 2020-2024
- Test: 2025

Final model trained on all data (2020-2025) for production use.

---

## Success Metrics

### Minimum Viable (Phase 1-2)
- ✅ Build dataset with 100+ events
- ✅ Train model with >55% directional accuracy
- ✅ Demonstrate edge over baseline (50%)

### Production Ready (Phase 3)
- 60%+ accuracy on Day 2 reversions
- AUC > 0.65
- Profitable on paper trading (3-month test)
- Automated daily predictions working

---

## Cost Breakdown

| Component | Phase 1-2 | Phase 3 | Notes |
|-----------|-----------|---------|-------|
| **Historical data** | Free | Free | FMP free tier (250/day) |
| **Daily data** | N/A | Free | Finnhub or Eulerpool |
| **Database** | Free | Free | SQLite → Supabase free tier |
| **Hosting** | N/A | Free | GitHub Actions (2,000 min/month) |
| **TOTAL** | **£0** | **£0** | Completely free forever |

---

## Risks & Mitigation

### Risk 1: FMP Free Tier Changes
- **Likelihood:** Low (stable for years)
- **Mitigation:** Fallback to Alpha Vantage (25/day) or edgartools (SEC direct)

### Risk 2: Model Doesn't Work
- **Likelihood:** Medium (this is research)
- **Mitigation:** Fast iteration, pivot features if needed, accept failure quickly

### Risk 3: Insufficient Events After Filtering
- **Likelihood:** Low (5 years × 50 stocks should yield 200+)
- **Mitigation:** Lower thresholds (1.5% move, 1.3x volume) or expand universe

### Risk 4: Overfitting to Historical Data
- **Likelihood:** High (common in trading models)
- **Mitigation:** Walk-forward validation, simple models, regularization, paper trading Phase 3

---

## Next Immediate Steps

1. ✅ ~~Sign up for FMP free API key~~
2. 🔄 Fetch 5 years of earnings data for 50 stocks
3. 🔄 Run `build_events.py` to create labeled dataset
4. 🔄 Run `validate_dataset.py` to check data quality
5. ⏳ Begin Phase 2: Model training

---

## Timeline

- **Phase 1:** 1 day (fetch historical data)
- **Phase 2:** 2-3 days (train, validate, iterate)
- **Phase 3:** 1 week (deploy, automate, test)

**Total to working prototype:** ~2 weeks

---

## Open Questions

- None currently - pivoting to FMP resolves data shortage issue

---

## Appendix: Data Schema

See `data/db.py` for complete schema. Key tables:

- `prices` - Daily OHLCV for 50 stocks
- `vix` - Daily VIX close
- `company_info` - Sector, market cap metadata
- `earnings_raw` - EPS/revenue estimates + actuals (staging)
- `events` - Labeled events with features + outcomes
- `forward_predictions` - Phase 3 live predictions
- `experiment_log` - Model training history

---

**Document Version:** 4.0
**Date:** March 9, 2026
**Status:** Phase 1 pivot to FMP for earnings data
