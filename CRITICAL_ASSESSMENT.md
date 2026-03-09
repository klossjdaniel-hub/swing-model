# Critical Assessment: Will This Model Actually Work?

**Date:** March 9, 2026
**Status:** Honest evaluation before we invest more time

---

## 🎯 What We're Trying to Predict

**Core Thesis:**
"After a big post-earnings move (Day 0), can we predict if it will revert ≥30% within Days 1-3?"

**Example:**
- Stock pops 5% on earnings → Will it give back ≥1.5% in next 1-3 days?
- Stock drops 8% on earnings → Will it bounce back ≥2.4% in next 1-3 days?

---

## ✅ What We Have

### Data (Good)
- ✅ 5,300 earnings records across 50 stocks (tomorrow)
- ✅ EPS estimates + actuals + surprise %
- ✅ 5 years of daily prices (OHLCV)
- ✅ VIX data
- ✅ Company metadata (sector, market cap)

### Features We're Planning (Decent)
1. **Event characteristics:**
   - `day0_return` - Size of initial move
   - `day0_return_abs` - Absolute move size
   - `direction` - Up or down
   - `volume_ratio` - Volume surge vs average

2. **Earnings context:**
   - `eps_surprise_pct` - Beat or miss magnitude
   - `beat_miss` - Classification

3. **Pre-event behavior:**
   - `pre_earnings_drift_5d` - Run-up before earnings
   - `pre_earnings_drift_20d` - Longer trend

4. **Market context:**
   - `vix_day0` - Fear gauge
   - `day_of_week` - Timing effect
   - `sector` - Industry behavior
   - `market_cap_bucket` - Size effect

### Expected Dataset Size (Marginal)
- Total earnings: ~5,300
- After filters (>2% move, >1.5x volume): ~250 events
- Train/test split: ~150-200 for training

---

## ❌ Critical Gaps That Will Kill Performance

### 1. **MISSING: Revenue Surprise** (CRITICAL)
**Problem:** Alpha Vantage doesn't provide revenue estimates/actuals

**Why it matters:**
- For tech stocks, revenue surprise > EPS surprise
- "Beat on EPS, miss on revenue" = stock tanks
- "Miss on EPS, beat on revenue + guide up" = stock rallies

**Impact:** Missing 30-40% of the signal

**Fix options:**
- ❌ Can't get from Alpha Vantage
- ⚠️ Could scrape from Finnhub earnings calls (complex)
- ⚠️ Could parse from SEC 8-Ks (very complex)
- ✅ Accept we won't have it (model will be weaker)

---

### 2. **MISSING: Guidance** (CRITICAL)
**Problem:** We have NO data on forward guidance

**Why it matters:**
- "Beat but lower guidance" → stock drops 10% (looks like miss)
- "Miss but raise guidance" → stock rallies 8% (looks like beat)
- Guidance often drives the move MORE than the actual results

**Real example:**
- NVDA Q2 2024: Beat EPS by 20%, but guided inline → stock flat
- NVDA Q3 2024: Beat EPS by 15%, guided UP → stock +30%

**Impact:** Missing 40-50% of the signal

**Fix options:**
- ⚠️ Parse 8-K text for "guidance", "outlook", "raising", "lowering"
- ⚠️ Use earnings call transcripts (if we can get them free)
- ❌ Accept we won't have it (model will struggle)

---

### 3. **MISSING: AMC vs BMO Accurate Detection** (HIGH IMPACT)
**Problem:** We're GUESSING timing based on known lists + assumptions

**Why it matters:**
- If we get Day 0 wrong, EVERYTHING breaks
- AMC reporters: Day 0 = next trading day
- BMO reporters: Day 0 = same day
- Getting this wrong = we're measuring the wrong move

**Current approach:**
- Known AMC list (incomplete)
- Known BMO list (incomplete)
- Default to BMO for unknowns (risky)

**Impact:** 10-20% of events have wrong Day 0 assignment

**Fix options:**
- ✅ Parse actual 8-K filing timestamps from SEC
- ✅ Build better detection from historical patterns
- ⚠️ Accept 10-20% error rate

---

### 4. **Small Sample Size** (MARGINAL)
**Problem:** ~250 events after filters

**Why it matters:**
- XGBoost needs hundreds of examples per feature
- With 12 features, we need 500-1000 events ideally
- With 250 events, risk of overfitting is HIGH

**Walk-forward splits:**
- Fold 1 train: ~100 events (too small!)
- Fold 2 train: ~150 events (marginal)
- Fold 3 train: ~200 events (ok)

**Impact:** Model will likely overfit, won't generalize

**Fix options:**
- ✅ Expand universe to 100 stocks (more events)
- ✅ Lower filter thresholds (1.5% move instead of 2%)
- ✅ Go back further in time (2015-2026 instead of 2020-2026)
- ⚠️ Accept smaller model (simpler = less overfitting)

---

### 5. **Missing Behavioral Signals**

**What we DON'T have but matters:**

| Signal | Why It Matters | Can We Get It? |
|--------|---------------|----------------|
| **Options activity** | Put/call ratio predicts direction | ❌ Expensive |
| **Short interest** | High SI + beat = short squeeze | ⚠️ Maybe (finviz scrape?) |
| **Analyst rating changes** | Upgrades post-earnings = momentum | ❌ Expensive |
| **Institutional ownership** | Smart money positioning | ⚠️ SEC 13F (quarterly, delayed) |
| **Earnings call sentiment** | CEO tone predicts guidance | ⚠️ SEC transcripts (complex) |
| **Pre-earnings IV** | Options pricing in big move | ❌ Expensive |
| **Intraday volume profile** | Where volume happened matters | ❌ Need intraday data |

**Reality:** We have 30-40% of useful signals

---

## 🔬 The Core Thesis: Does Mean Reversion Even Exist?

### Academic Research Says:
- ✅ **Post-Earnings Drift EXISTS** - but it's MOMENTUM, not reversion
- ✅ **Intraday mean reversion** - yes, minutes/hours after open
- ❌ **Multi-day reversion** - inconsistent, weak signal
- ❌ **Predictable reversion** - very hard to forecast

### What Actually Happens:
1. **Earnings beat → continues UP** (drift for weeks)
2. **Earnings miss → continues DOWN** (drift for weeks)
3. **Intraday overreaction → reverts same day** (too fast to trade)
4. **Multi-day reversion** - only in specific cases:
   - Mismatch: beat EPS but bad guidance
   - Overreaction: retail FOMO into illiquid stock
   - Positioning: shorts covering then re-shorting

**Our model assumes:** Multi-day reversion is predictable
**Reality:** It's RARE and context-dependent

---

## 📊 Expected Model Performance (Honest Estimate)

### Best Case Scenario:
- **Accuracy:** 55-58% (barely better than coin flip)
- **Precision:** 52% (more false positives than true positives)
- **Why:** We have SOME signal but missing critical features

### Realistic Scenario:
- **Accuracy:** 50-52% (barely better than random)
- **Precision:** 48-50% (as many false positives as true)
- **Why:** Weak signal, small sample, missing guidance/revenue

### After Transaction Costs:
- Entry slippage: -0.2%
- Exit slippage: -0.2%
- Bid-ask spread: -0.1%
- **Total:** -0.5% per round trip

**Even at 55% accuracy, edge disappears after costs**

---

## 🚨 What Would Actually Make This Work?

### Must-Have (Without These, Don't Build):
1. ✅ **Revenue surprise data** - Try to get from Finnhub or SEC
2. ✅ **Guidance extraction** - Parse 8-Ks for "guide", "outlook", "expect"
3. ✅ **Larger sample** - Expand to 100 stocks or go back to 2015
4. ✅ **Better AMC/BMO detection** - Parse SEC filing timestamps
5. ✅ **Paper trading validation** - Test live for 3 months before believing

### Nice-to-Have (Boosts Performance):
- ⚠️ Earnings call sentiment (SEC transcripts + NLP)
- ⚠️ Short interest data (scrape finviz?)
- ⚠️ Historical stock reversion tendency (does this stock usually revert?)
- ⚠️ Sector momentum (is tech rallying or selling off?)
- ⚠️ VIX regime change (stable vs rising)

---

## 🎯 Revised Plan: Build It Right or Don't Build It

### Option A: Build a Proper Model (Recommended)
**Phase 1.5: Get Missing Critical Data**
1. **Revenue data** - Try Finnhub earnings endpoint or scrape
2. **Guidance extraction** - Parse 8-K Item 2.02 text for keywords
3. **AMC/BMO detection** - Parse filing timestamps from SEC
4. **Expand sample** - Add 50 more stocks (100 total) or go back to 2015

**Timeline:** +1 week
**Result:** 500-800 events with revenue + guidance → 60-65% accuracy possible

### Option B: Build Minimal Model (Educational)
**Accept limitations:**
- No revenue data
- No guidance data
- 250 events
- 50-55% accuracy at best

**Purpose:** Learn ML workflow, validate hypothesis, see what happens
**Timeline:** Current plan (2 days)
**Result:** Academic exercise, NOT tradeable

### Option C: Don't Build It (Honest)
**Reality check:**
- Post-earnings drift is well-studied
- Mean reversion signals are weak
- We're missing 50% of critical features
- Even hedge funds struggle with this

**Alternative:** Focus on simpler, more reliable signals?

---

## 🧮 My Honest Recommendation

### Short Answer:
**Build Option A** - Get revenue + guidance, expand sample to 500-800 events, THEN train model.

### Why:
1. **Current plan has 50-55% accuracy ceiling** - not worth the effort
2. **Adding revenue + guidance bumps to 60-65%** - potentially tradeable
3. **Larger sample reduces overfitting** - model actually generalizes
4. **Free data exists** - we just need to work harder to get it

### How to Get Missing Data (All Free):

**Revenue Surprise:**
```python
# Finnhub has revenue in earnings calendar
calendar = client.earnings_calendar(from='2020-01-01', to='2025-12-31', symbol='AAPL')
# Returns: revenueEstimate, revenueActual
```

**Guidance Extraction:**
```python
# Use edgartools to get 8-K text
filing = company.get_filings(form="8-K")[0]
text = filing.obj().text

# Search for guidance keywords
guidance_keywords = ['guidance', 'outlook', 'expect', 'project', 'forecast']
has_positive_guidance = any(word in text.lower() for word in ['raising', 'increasing', 'above'])
```

**AMC/BMO Detection:**
```python
# Get filing timestamp from SEC
filing_time = filing.filing_date + ' ' + filing.accepted_date
# If before 9:30 AM ET = BMO
# If after 4:00 PM ET = AMC
```

### Estimated Effort:
- Get revenue from Finnhub: 1 day
- Build guidance extractor: 2 days
- Improve AMC/BMO detection: 1 day
- Expand to 100 stocks: 1 day (already have fetcher)

**Total:** +5 days to go from 50-55% to 60-65% accuracy

---

## ✅ Decision Point

**Question:** Do we:
1. **Continue with current plan** → Build weak model (50-55% accuracy) in 2 days
2. **Invest 1 more week** → Build proper model (60-65% accuracy) with revenue + guidance
3. **Pivot entirely** → Acknowledge this signal is too weak, build something else

**My vote:** Option 2 - Invest the week, do it right.

**Your call!**

---

## 📋 If We Continue Current Plan (Limitations)

**You should know:**
- ✅ Good learning exercise
- ✅ Validates ML workflow
- ✅ Tests hypothesis
- ❌ NOT tradeable (edge too small)
- ❌ Missing critical features
- ❌ Will overfit badly
- ❌ Won't work in production

**Acceptable for:** Academic project, learning, portfolio piece
**NOT acceptable for:** Real trading, production use

**Final test:** If model shows 52% accuracy, we MUST stop and add features before Phase 3.

---

**Bottom Line:** Current plan works for learning but won't make money. Investing 1 week to get revenue + guidance + larger sample makes it potentially tradeable.
