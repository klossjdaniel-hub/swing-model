# The Broader Model: ALL Catalysts, Not Just Earnings

## 🎯 Your Insight: Earnings is Just ONE Catalyst

**Current narrow thinking:**
"Post-EARNINGS mean reversion"

**Your better framing:**
"Post-CATALYST mean reversion"

Stocks pop/drop for MANY reasons:
- ✅ Earnings (what we're doing)
- ✅ FDA approvals/rejections
- ✅ Product launches
- ✅ M&A announcements
- ✅ Analyst upgrades/downgrades
- ✅ Guidance updates (outside earnings)
- ✅ Patent wins/losses
- ✅ Executive changes
- ✅ Short seller reports
- ✅ Regulatory decisions
- ✅ Macro news (Fed, CPI, etc.)
- ✅ Social media hype
- ✅ Meme stock pumps
- ✅ Mysterious moves (no obvious catalyst)

**The underlying psychology is the SAME:**
Big move → Emotional reaction → Potential overreaction → Reversion

---

## 📊 The Math: Way More Data!

### Current Approach (Earnings Only):
- 50 stocks × 5 years × 4 earnings/year = 1,000 earnings
- After filters (>2%, >1.5x volume): **~250 events**

### Broader Approach (All Big Moves):
- 50 stocks × 5 years × 252 trading days = 63,000 stock-days
- Big moves (>2%, >1.5x volume): ~5% of days = **~3,000 events**

**12X MORE DATA!**

Even better:
- No dependency on earnings timing
- No need for EPS estimates/actuals
- No need for revenue data
- No need for guidance parsing
- Just need: prices + volume + news (optional)

---

## 🔬 The New Model Definition

### What We're Predicting:
"When ANY stock has a big move (>2%, >1.5x volume), will it revert ≥30% within 1-3 days?"

### Core Features (Simple & Powerful):

**Move Characteristics:**
- `day0_return` - Size of move
- `day0_return_abs` - Absolute magnitude
- `direction` - Up or down
- `volume_ratio` - How emotional was it?
- `intraday_volatility` - High-low range

**Context:**
- `pre_move_drift_5d` - Was it already trending?
- `pre_move_drift_20d` - Longer trend
- `vix_day0` - Market fear level
- `sector` - Industry behavior
- `market_cap_bucket` - Size matters
- `day_of_week` - Monday vs Friday behavior

**Catalyst Detection (Optional but Powerful):**
- `has_earnings` - Is this an earnings day?
- `has_news` - Was there news? (scrape)
- `catalyst_type` - earnings | FDA | M&A | upgrade | unknown
- `news_sentiment` - Positive or negative catalyst?

### Outcome Labels:
- `return_day1`, `return_day2`, `return_day3`
- `reverted_day1`, `reverted_day2`, `reverted_day3`
- `reversion_magnitude_day2`

---

## 💡 Why This is MUCH Better

### Advantages:
1. **12X more training data** (3,000 events vs 250)
2. **No dependency on earnings APIs** (just need prices)
3. **More generalizable pattern** (works for any catalyst)
4. **Simpler feature engineering** (no EPS/revenue complexity)
5. **Easier to maintain** (prices + volume = free forever)
6. **Can add catalyst detection later** (enhancement, not requirement)

### The Beauty:
**The model learns:**
"This size move + this volume spike + this market regime + this sector → usually reverts 60% of the time"

It doesn't NEED to know WHY the stock moved. It just needs to know the CHARACTERISTICS of moves that revert.

---

## 🎨 Enhanced Version: Add Catalyst Detection

Once the base model works, we can ADD:

### Free News Detection:
```python
# 1. Check if it's earnings day (we have this)
is_earnings_day = ticker in earnings_calendar

# 2. Scrape Google News for the stock
news_articles = scrape_google_news(ticker, date)

# 3. Simple sentiment: count positive vs negative words
positive_words = ['approval', 'beat', 'surge', 'upgrade', 'launch']
negative_words = ['rejection', 'miss', 'downgrade', 'scandal', 'lawsuit']

sentiment_score = count_positive - count_negative

# 4. Classify catalyst type
if 'FDA' in news_text: catalyst = 'FDA'
elif 'earnings' in news_text: catalyst = 'earnings'
elif 'upgrade' in news_text: catalyst = 'analyst'
elif 'acquire' in news_text: catalyst = 'M&A'
else: catalyst = 'unknown'
```

### Feature Enhancement:
- `catalyst_type` - earnings | FDA | M&A | analyst | news | unknown
- `news_sentiment` - -1 to +1 scale
- `news_volume` - Number of articles
- `mismatch` - Positive news but stock down? (contrarian signal)

**This becomes a SUPER feature:**
- "Stock up 5% on positive FDA news with low volume in healthcare sector during high VIX"
- vs
- "Stock up 5% on no news with massive volume in meme stock during low VIX"

Different reversion probabilities!

---

## 📋 Implementation Plan: Broader Model

### Phase 1: Base Model (Simple, Fast)
**Use what we already have:**
1. Daily prices (✅ we have this)
2. Volume data (✅ we have this)
3. VIX (✅ we have this)
4. Sector/market cap (✅ we have this)

**Build events table:**
```python
# For EVERY trading day, EVERY stock:
if day0_return_abs > 0.02 and volume_ratio > 1.5:
    # This is an event!
    # Calculate outcomes (Day 1-3 returns)
    # Label if it reverted
    # Store in events table
```

**Expected:** ~3,000 events from 50 stocks over 5 years

**Features:** Just the basics (move size, volume, context)

**Accuracy estimate:** 55-60% (already better than earnings-only!)

**Timeline:** 2 days (what we already planned)

---

### Phase 2: Add Catalyst Detection (Enhancement)
**Enhance with:**
1. Earnings calendar (✅ already have from Finnhub)
2. News scraping (Google News RSS - free)
3. Basic sentiment (keyword matching)
4. Catalyst classification

**Features:** Add catalyst_type, news_sentiment, mismatch

**Accuracy estimate:** 60-65% (catalyst context helps)

**Timeline:** +3 days

---

### Phase 3: Advanced Features (Optional)
**Add if needed:**
- Short interest (scrape finviz)
- Options activity (if we can get free)
- Social media sentiment (Reddit/Twitter scraping)
- Institutional ownership changes (SEC 13F)

**Accuracy estimate:** 65-70% (best case)

**Timeline:** +1 week

---

## 🔄 Comparison: Narrow vs Broad

| Aspect | Earnings-Only (Old) | Any Catalyst (New) |
|--------|--------------------|--------------------|
| **Data size** | ~250 events | ~3,000 events |
| **Data dependencies** | EPS, revenue, guidance | Just prices + volume |
| **API complexity** | High (Alpha Vantage + Finnhub) | Low (just yfinance) |
| **Feature engineering** | Complex (earnings-specific) | Simple (universal) |
| **Maintenance** | Fragile (APIs can break) | Robust (price data is stable) |
| **Generalizability** | Only works for earnings | Works for ANY catalyst |
| **Accuracy ceiling** | 60-65% | 60-70% |
| **Time to build** | 1 week | 2 days base, +3 days enhanced |
| **Cost** | Free but complex | Free and simple |

**Winner:** Broader approach on almost every dimension!

---

## 🎯 The New Hypothesis

**Original (too narrow):**
"Post-earnings moves often revert because markets overreact to quarterly results"

**Revised (much better):**
"Markets overreact to ALL catalysts. Big moves with high volume often revert because:
1. Initial reaction is emotional
2. Algorithms amplify moves
3. Retail FOMO/panic at extremes
4. Profit-taking after quick gains
5. Contrarian positioning"

**This works for:**
- ✅ Earnings beats/misses
- ✅ FDA approvals/rejections
- ✅ Analyst upgrades/downgrades
- ✅ Product launches
- ✅ M&A rumors
- ✅ Meme stock pumps
- ✅ Short squeezes
- ✅ Mysterious moves

**The pattern is universal, not earnings-specific!**

---

## 🚀 Recommended Path Forward

### Option A1: Broader Model (RECOMMENDED)
**Build the general "post-catalyst reversion" model:**

**Week 1 (Now - Simple Base):**
1. Use existing price + volume data
2. Flag ALL big moves (>2%, >1.5x volume)
3. Build events dataset (~3,000 events)
4. Train XGBoost on basic features
5. **Expected: 55-60% accuracy**

**Week 2 (Enhancement):**
1. Add earnings calendar flag
2. Scrape Google News for context
3. Basic sentiment analysis
4. Catalyst classification
5. **Expected: 60-65% accuracy**

**Week 3 (Production):**
1. Paper trade for validation
2. Refine based on live results
3. Deploy to Phase 3

---

### Option A2: Earnings-Focused (Original Plan)
**Build the narrow "post-earnings reversion" model:**

**Week 1:**
1. Get revenue data from Finnhub
2. Parse guidance from 8-Ks
3. Expand to 100 stocks
4. **Expected: 60-65% accuracy**

**Harder to build, similar accuracy ceiling**

---

## 💡 My Strong Recommendation

**Go with Option A1 (Broader Model):**

**Why:**
1. **12X more data** = less overfitting
2. **Simpler to build** = no earnings API complexity
3. **More robust** = price data never breaks
4. **More generalizable** = works for any catalyst
5. **Easier to maintain** = free forever
6. **Same accuracy ceiling** = 60-65%
7. **Can always narrow later** = add earnings features as enhancement

**Start broad, then specialize if needed**

Not: Start narrow (earnings), struggle with small data, complex features

---

## 📊 Quick Feasibility Check

**Can we build this in 2 days?**

**Day 1:**
```python
# 1. Get all big move days (1 hour)
for ticker in UNIVERSE:
    for date in price_data:
        if abs(return) > 0.02 and volume_ratio > 1.5:
            events.append(...)

# 2. Calculate outcomes (1 hour)
for event in events:
    event['return_day1'] = ...
    event['reverted_day2'] = ...

# 3. Already have context features (done!)
# - VIX ✅
# - Sector ✅
# - Market cap ✅
# - Pre-move drift (calculate, 1 hour)
```

**Day 2:**
```python
# 1. Train/test split
# 2. Train XGBoost
# 3. Evaluate
# 4. Done!
```

**YES! We can build the base model in 2 days using ONLY the data we already have!**

---

## ✅ Decision Matrix

| Model | Data Size | Complexity | Time | Accuracy | Robust? |
|-------|-----------|------------|------|----------|---------|
| **Earnings-only** | 250 | High | 1 week | 60-65% | Fragile |
| **Broad base** | 3,000 | Low | 2 days | 55-60% | ✅ Robust |
| **Broad + catalysts** | 3,000 | Medium | 5 days | 60-65% | ✅ Robust |

**Best path:** Broad base → validate → add catalysts if needed

---

## 🎓 The Bigger Picture

**You've identified the key insight:**
We're not building an "earnings model" - we're building a "market overreaction detection model"

Earnings is just one type of catalyst. The REAL pattern is:

**"Big move + high emotion + specific context = reversion opportunity"**

This works whether the catalyst is:
- Quarterly results
- FDA decision
- Elon tweet
- Analyst report
- Mysterious pump

**The psychology is universal.**

---

## 🚀 Final Recommendation

**Tomorrow, instead of:**
- Fetching remaining 25 stocks from Alpha Vantage
- Building earnings-only model with 250 events

**Do this:**
- Use the price data we ALREADY HAVE
- Build events from ALL big moves (3,000 events)
- Train on universal features
- Get 55-60% accuracy in 2 days
- Enhance with catalyst detection if needed (another 60-65%)

**This is:**
- ✅ Faster
- ✅ Simpler
- ✅ More data
- ✅ More robust
- ✅ More generalizable
- ✅ Easier to maintain

**Your call - but I think the broader approach is way better!**
