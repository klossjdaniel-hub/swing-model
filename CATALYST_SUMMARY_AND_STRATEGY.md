# Executive Summary: All Stock Price Catalysts & Our Strategy

**Source:** 1,095-line comprehensive research document (COMPREHENSIVE_CATALYST_TAXONOMY.md)
**Research Scope:** 60+ catalyst types with academic citations, real examples, and detection methods

---

## 🎯 The Big Picture: What Makes Stocks Move >2%

### 6 Major Categories of Catalysts:

1. **Company-Specific** (25 types) - Earnings, products, corporate actions, legal
2. **Industry/Sector** (8 types) - Regulatory, competition, supply chain
3. **Macro/Market** (8 types) - Fed, economic data, geopolitics
4. **Technical/Positioning** (11 types) - Squeezes, flows, rebalancing
5. **Sentiment/Social** (7 types) - Analysts, Reddit, viral trends
6. **Rare High-Impact** (3 types) - Weather, crypto correlation, conferences

**Total:** 60+ distinct catalyst types identified

---

## 📊 Magnitude Hierarchy: How Big Do Stocks Move?

### **EXTREME (>50% single day)**
- Short squeezes (GameStop: +2,700%)
- Fraud scandals (Enron: -99%)
- Bankruptcy filings (-70% to -100%)
- Major clinical trial failures (-90%)

### **LARGE (10-50%)**
- FDA rejections (pharma: -90%)
- Phase 3 trial results (±30%)
- M&A targets (+32% median)
- Short seller reports (-20% to -50%)

### **MODERATE (2-10%)**
- Earnings surprises (5-8% average)
- Guidance revisions (3-10%)
- Product launches (2-8%)
- Analyst upgrades/downgrades (2-5%)
- Government contracts (5-100% for small caps)

### **SMALL (<2%)**
- Insider buying patterns (0.5-2%)
- Sector rotation (1-3%)
- Minor news (0.5-2%)

---

## 🔄 Critical Finding: Reversion vs Continuation Patterns

### **Catalysts That Typically REVERT:**
1. **Technical events** - Gaps (75% fill), short squeezes, triple witching
2. **Geopolitical shocks** - Initial panic, then normalization
3. **Index rebalancing** - Temporary flows, mean revert after
4. **Social media pumps** - Meme stocks, viral trends (fade fast)
5. **Overreaction to minor news** - Sentiment-driven, no fundamental change

**Trading Strategy:** Fade these moves (bet on reversion)

---

### **Catalysts That Typically CONTINUE:**
1. **Earnings with PEAD** - Post-Earnings Announcement Drift (6+ months)
2. **Business developments** - Contracts, partnerships, FDA approvals
3. **Fundamental changes** - New management, business model shifts
4. **Institutional accumulation** - 13F filings showing big buys
5. **Analyst upgrades** - Price targets raised = momentum

**Trading Strategy:** Follow these moves (bet on continuation)

---

### **Catalysts That Are MIXED (Context-Dependent):**
1. **Guidance changes** - Positive continues, negative can bounce
2. **Leadership changes** - Depends on circumstances
3. **Product events** - Success continues, failure can bounce
4. **M&A acquirer** - Market skeptical (-3-5%), but depends on synergies
5. **Recalls** - Severity matters (minor bounce, major continues down)

**Trading Strategy:** Need more features to predict direction

---

## 💡 The Key Insight: It's About CATALYST TYPE, Not Just Move Size

**Old Model Thinking:**
"Big move + high volume → will it revert?"

**New Model Reality:**
"Big move + high volume + **WHAT CAUSED IT** → will it revert or continue?"

**Example:**
- Stock up 8% on earnings beat → **Continues** (PEAD)
- Stock up 8% on Reddit pump → **Reverts** (no fundamentals)
- Stock up 8% on gap at open → **Reverts** (75% fill rate)
- Stock up 8% on M&A target → **Continues** to offer price

**The catalyst type IS the signal!**

---

## 🔍 Detection Feasibility: What Can We Actually Identify?

### **EASY TO DETECT (Scheduled + Free Data):**
| Catalyst | Frequency | Data Source | Detection Method |
|----------|-----------|-------------|------------------|
| **Earnings** | Quarterly | Finnhub, SEC | Earnings calendar API |
| **Fed meetings** | 8x/year | Fed calendar | Known schedule |
| **Economic data** | Monthly | BLS, BEA | Release calendar |
| **FDA PDUFA** | Varies | FDA.gov | PDUFA calendar |
| **Options expiration** | Quarterly | Exchange calendar | Fixed dates |
| **Index rebalancing** | Annual | S&P, Russell | Announcement dates |

---

### **MODERATE DIFFICULTY (Real-Time News + Free Scraping):**
| Catalyst | Data Source | Detection Method |
|----------|-------------|------------------|
| **Guidance changes** | 8-K filings | SEC RSS feed + NLP |
| **Product launches** | Press releases | PR Newswire scraping |
| **Analyst actions** | Finviz, Yahoo | Scrape ratings tables |
| **Partnerships** | Business Wire | NLP for "partnership" keywords |
| **Clinical trials** | Clinicaltrials.gov | Track readout dates |
| **Insider trades** | SEC Form 4 | Parse transaction tables |

---

### **HARD TO PREDICT (Real-Time Only, Unscheduled):**
| Catalyst | Challenge | Best Approach |
|----------|-----------|---------------|
| **M&A announcements** | Surprise events | React immediately, don't predict |
| **Fraud/scandals** | Unexpected | Monitor news, classify post-facto |
| **Recalls** | Rare, random | FDA/NHTSA RSS feeds |
| **Geopolitical shocks** | Unpredictable | Monitor news APIs |
| **Breaches/hacks** | Random | Security news feeds |

---

## 🎨 Our Model Architecture: Three-Tier Detection System

### **Tier 1: Real-Time Catalyst Detection (24/7 Monitoring)**

**What we monitor:**
- SEC 8-K filings (guidance, M&A, material events)
- Press releases (partnerships, products, contracts)
- FDA announcements (approvals, rejections)
- News feeds (Google News, Reuters)
- Social media (Reddit WSB, Twitter/X finance)
- Economic calendars (Fed, CPI, jobs)

**When a big move happens:**
1. Detect the move (>2%, >1.5x volume)
2. Classify the catalyst (earnings, FDA, M&A, gap, unknown, etc.)
3. Extract features (sentiment, magnitude, timing)

---

### **Tier 2: Catalyst Classification Engine**

**For each detected move, classify into:**

#### **Primary Categories:**
1. **Earnings** (beat, miss, guidance up/down)
2. **Product/Regulatory** (FDA, trials, recalls)
3. **Corporate Action** (M&A, buyback, dividend)
4. **Technical** (gap, squeeze, rebalancing)
5. **Analyst** (upgrade, downgrade, target change)
6. **Social/Sentiment** (Reddit, viral, meme)
7. **Macro** (Fed, CPI, geopolitical)
8. **Unknown** (mysterious move, no clear catalyst)

#### **Sub-Classification:**
- Earnings → {beat_eps, miss_eps, beat_revenue, guide_up, guide_down}
- FDA → {approval, rejection, phase_success, phase_fail}
- Technical → {gap_up, gap_down, short_squeeze, index_add}
- Etc.

---

### **Tier 3: Response Prediction Model**

**Input Features:**
1. **Move characteristics**
   - day0_return, day0_return_abs, volume_ratio, intraday_volatility
2. **Catalyst classification**
   - catalyst_primary, catalyst_sub, catalyst_confidence
3. **Catalyst-specific features**
   - If earnings: eps_surprise_pct, revenue_surprise_pct, guidance_change
   - If FDA: phase_type, company_market_cap, pipeline_dependency
   - If technical: gap_size, pre_market_volume, has_news
   - If social: reddit_mentions, sentiment_score, viral_velocity
4. **Context**
   - pre_move_drift_5d, pre_move_drift_20d, vix_day0, sector, market_cap
5. **Historical patterns**
   - stock_reversion_tendency, sector_reversion_rate, catalyst_reversion_rate

**Outputs:**
- `reversion_prob` (0-1) - Probability move will reverse ≥30%
- `continuation_prob` (0-1) - Probability move will continue
- `neutral_prob` (0-1) - Neither (1 - reversion - continuation)
- `confidence` - Model confidence in prediction

**Trade Decision:**
- If `reversion_prob > 0.65` → Fade the move
- If `continuation_prob > 0.65` → Follow the move
- If `neutral_prob > 0.65` → No trade
- If confidence < 0.5 → No trade

---

## 📈 Expected Performance by Catalyst Type

Based on research findings:

| Catalyst Type | Base Rate Revert | With ML Model | Trade Viability |
|---------------|------------------|---------------|-----------------|
| **Earnings (beat)** | 15% | 25-35% | LOW (PEAD dominates) |
| **Earnings (miss)** | 20% | 30-40% | MEDIUM |
| **Gaps (no news)** | 75% | 80-85% | ✅ HIGH |
| **FDA approval** | 30% | 40-50% | MEDIUM |
| **FDA rejection** | 10% | 15-25% | LOW (continues down) |
| **Short squeeze** | 80% | 85-90% | ✅ HIGH |
| **Index rebalancing** | 70% | 75-85% | ✅ HIGH |
| **Reddit pump** | 85% | 90-95% | ✅ HIGH |
| **M&A target** | 5% | 10-15% | LOW (continues to offer) |
| **Analyst upgrade** | 25% | 35-45% | MEDIUM |
| **Guidance raise** | 15% | 20-30% | LOW (continues) |
| **Unknown catalyst** | 50% | 55-60% | MEDIUM |

**Best opportunities for reversion trading:**
1. ✅ Gaps (no fundamental news)
2. ✅ Short squeezes (unsustainable)
3. ✅ Social media pumps (no fundamentals)
4. ✅ Index flows (temporary)
5. ⚠️ Geopolitical shocks (initial panic fades)

**Avoid trying to fade:**
1. ❌ Earnings beats (PEAD)
2. ❌ M&A targets (rational pricing)
3. ❌ FDA approvals (fundamental change)
4. ❌ Guidance raises (future growth)

---

## 🚀 Implementation Plan: Build the Broadest Possible Model

### **Phase 1: Base Model (Week 1)**

**Scope:** Detect ALL big moves, classify basic catalyst types

**Steps:**
1. Flag all moves >2%, >1.5x volume (expect ~3,000 events from 50 stocks × 5 years)
2. Basic catalyst detection:
   - Check if earnings day (from Finnhub calendar) → label "earnings"
   - Check if gap (open vs prev close) → label "gap"
   - Check if options expiration → label "expiration"
   - Else → label "unknown"
3. Calculate universal features (move size, volume, pre-drift, VIX, sector)
4. Train model to predict: `will_revert_day2`

**Expected accuracy:** 55-60% (baseline)

**Insight:** Which catalyst types revert most? Which features matter?

---

### **Phase 2: Enhanced Catalyst Detection (Week 2)**

**Add detection for:**
1. **Guidance changes** - Parse 8-K filings for keywords
2. **News events** - Scrape Google News for catalyst context
3. **Analyst actions** - Scrape Finviz for upgrades/downgrades
4. **Social sentiment** - Monitor Reddit WSB for mentions
5. **FDA events** - Track FDA calendar for PDUFA dates

**New features:**
- catalyst_type (earnings, FDA, gap, news, social, analyst, unknown)
- catalyst_sentiment (positive, negative, neutral)
- has_fundamental_change (yes/no)
- news_headline_keywords (extracted)

**Expected accuracy:** 60-65%

**Insight:** Catalyst-aware model significantly outperforms blind model

---

### **Phase 3: Catalyst-Specific Models (Week 3)**

**Train specialized sub-models:**
1. **Earnings model** - Uses EPS surprise, revenue surprise, guidance
2. **Gap model** - Uses gap size, pre-market volume, catalyst detection
3. **Technical model** - Uses short interest, volume patterns, index flows
4. **Social model** - Uses Reddit mentions, sentiment velocity, stock characteristics
5. **News model** - Uses headline sentiment, news source credibility, timing

**Ensemble approach:**
- Route each event to appropriate sub-model based on catalyst
- Fallback to universal model if catalyst unclear
- Weight predictions by catalyst confidence

**Expected accuracy:** 65-70%

**Trade filter:** Only trade when confidence > 65% AND prediction > 65%

---

### **Phase 4: Live Testing (Week 4+)**

**Paper trade for 3 months:**
1. Real-time catalyst detection
2. Real-time predictions
3. Simulated trades
4. Track performance by catalyst type

**Success metrics:**
- Overall win rate > 60%
- Sharpe ratio > 1.5
- Max drawdown < 15%
- Works across catalyst types

**Then:** Deploy with real capital (start small!)

---

## 🎓 Key Strategic Insights

### **1. Catalyst Classification is 80% of the Signal**

**Why:** Different catalysts have different reversion rates
- Gaps: 75% revert
- Earnings beats: 15% revert (85% continue!)
- Knowing this BEFORE predicting is huge

**Implication:** Invest heavily in catalyst detection infrastructure

---

### **2. "Unknown" Catalysts Are the Best Targets**

**Why:** When there's no obvious fundamental reason for a move:
- Likely technical/positioning/sentiment-driven
- These reverse at much higher rates (50-60%)
- Example: Stock up 5%, no news, high volume = prime reversal candidate

**Implication:** When catalyst detection returns "unknown", that's actually a strong signal

---

### **3. Don't Fight Fundamentals**

**Earnings beats, FDA approvals, M&A targets = let them run**
- These have fundamental reasons to continue
- Trying to fade them = fighting the tape
- Better to sit out or even follow

**Implication:** Model should OUTPUT "no trade" for these, not try to predict

---

### **4. Social/Sentiment Moves Are Gold Mines**

**Reddit pumps, meme stocks, viral trends:**
- Driven by emotion, not fundamentals
- Revert 85-95% of the time
- Easy to detect (social media monitoring)
- High reward-to-risk

**Implication:** Build robust social media monitoring (Reddit API is free)

---

### **5. Combine Reversion + Momentum Strategies**

**Don't pick just one!**
- Some moves should be faded (gaps, squeezes, social)
- Some should be followed (earnings beats, guidance raises)
- Model should predict BOTH outcomes

**Implication:** Multi-strategy approach = more opportunities, lower correlation

---

## 📋 Data Requirements Summary

### **Already Have (Free):**
- ✅ Daily prices (yfinance)
- ✅ Volume data
- ✅ VIX
- ✅ Company metadata (sector, market cap)

### **Easy to Add (Free):**
- ✅ Earnings calendar (Finnhub)
- ✅ 8-K filings (SEC RSS)
- ✅ News scraping (Google News RSS)
- ✅ Analyst ratings (Finviz scraping)
- ✅ FDA calendar (FDA.gov)
- ✅ Economic calendar (BLS, Fed)
- ✅ Reddit mentions (Reddit API)

### **Nice to Have (Free but more work):**
- ⚠️ Earnings call transcripts (Seeking Alpha scraping)
- ⚠️ Short interest (Finviz scraping)
- ⚠️ Insider trades (SEC Form 4)
- ⚠️ Options data (Tradier free tier)
- ⚠️ Social sentiment (Twitter/X API)

### **Don't Need (Can skip):**
- ❌ Real-time tick data
- ❌ Order flow data
- ❌ Expensive data providers

**Bottom line:** Everything we need is free, just requires scraping/parsing

---

## ✅ Final Recommendation: The Comprehensive Catalyst Model

**Build This:**

**"Universal Catalyst Response Prediction System"**

**What it does:**
1. **Monitors** all stocks 24/7 for big moves
2. **Detects** what caused the move (earnings, gap, FDA, social, etc.)
3. **Classifies** catalyst type and sentiment
4. **Predicts** whether move will revert, continue, or stay neutral
5. **Trades** only when confidence is high and edge is clear

**Why it's better than narrow approaches:**
- 12X more data (3,000+ events vs 250 earnings)
- Catalyst-aware (know when to fade vs follow)
- Multi-strategy (reversion + momentum)
- Robust (not dependent on one pattern)
- Scalable (add new catalyst types easily)

**Timeline:**
- Week 1: Base model (all moves, basic classification)
- Week 2: Enhanced detection (news, social, analyst)
- Week 3: Specialized sub-models
- Week 4+: Live testing

**Expected Performance:**
- Win rate: 60-70% (varies by catalyst)
- Sharpe ratio: 1.5-2.0
- Drawdown: <15%
- Trade frequency: 2-5 trades/day across 50 stocks

---

## 📚 Next Steps

**Tomorrow:**
1. ~~Don't fetch more Alpha Vantage data~~ (we're going broader!)
2. ✅ Use price/volume data we already have
3. ✅ Build events from ALL big moves (not just earnings)
4. ✅ Start with basic catalyst classification (earnings vs gap vs unknown)
5. ✅ Train first model iteration

**This Week:**
1. Implement catalyst detection infrastructure
2. Build news scraping
3. Add Reddit monitoring
4. Create classification engine

**Next 2 Weeks:**
1. Specialized sub-models by catalyst type
2. Backtesting framework
3. Paper trading system

**See full 1,095-line research document:** `COMPREHENSIVE_CATALYST_TAXONOMY.md`

---

**The research is done. Now let's build the broadest, most robust catalyst response prediction system possible!** 🚀
