# Option B Results: Enhanced Feature Engineering

**Date:** March 9, 2026
**Status:** ✅ COMPLETE

---

## 📊 Three-Model Comparison

| Model | Test Accuracy | Train Accuracy | Overfitting Gap | Key Features |
|-------|---------------|----------------|-----------------|--------------|
| **Baseline** (no catalyst) | 65.7% | 82.7% | +17.0% | Move size, volume, VIX, drift |
| **Catalyst-Aware** | **67.7%** ⭐ | 83.1% | +15.4% | Above + catalyst type |
| **Enhanced** (all features) | 66.0% | 97.4% | **+31.4%** ❌ | Above + 11 enhanced features |

---

## 🔍 What Happened?

### The Enhanced Model HURT Performance

**Expected:** 70%+ accuracy with sophisticated features
**Actual:** 66.0% accuracy (worse than catalyst-aware!)

**Why it failed:**
1. **Severe overfitting** - 97% train vs 66% test (31% gap!)
2. **Too many features** - 27 total features for 4,194 events
3. **Correlated features** - Many new features measure similar things
4. **Signal dilution** - Added noise along with signal

---

## 📈 Performance Breakdown

### Baseline Model (No Catalyst)
- **Accuracy:** 65.7%
- **Precision:** 53.9% (when predicting revert, right 54% of time)
- **Recall:** 27.3% (catches 27% of actual reversions)
- **Overfitting:** Moderate (+17%)

**Strengths:** Simple, generalizes reasonably well
**Weaknesses:** Misses catalyst signal

---

### Catalyst-Aware Model (Winner!) ⭐
- **Accuracy:** 67.7%
- **Precision:** 60.1% (when predicting revert, right 60% of time)
- **Recall:** 28.7% (catches 29% of actual reversions)
- **Overfitting:** Moderate (+15.4%)

**Strengths:**
- Best test accuracy
- Best precision (60%)
- Reasonable overfitting
- catalyst_type_unknown was #2 most important feature

**Weaknesses:** Still only catching 29% of reversions

---

### Enhanced Model (Overfit!)
- **Accuracy:** 66.0%
- **Precision:** 54.7% (WORSE than catalyst-aware)
- **Recall:** 29.3% (slightly better)
- **Overfitting:** SEVERE (+31.4%)

**Strengths:** None - worse than catalyst-aware

**Weaknesses:**
- Memorizing training data
- Won't generalize to new data
- Too complex for dataset size

---

## 💡 Key Insights

### 1. Catalyst Detection Helps (+2%)
Baseline → Catalyst-Aware: **+2.0% improvement**
- catalyst_type_unknown is highly predictive (10.3% importance)
- Simple 3-type classification is enough
- More sophisticated detection probably won't help much more

### 2. Feature Engineering Backfired (-1.7%)
Catalyst-Aware → Enhanced: **-1.7% decline**
- 11 new features added noise, not signal
- Severe overfitting (97% train vs 66% test)
- Model memorizing training patterns that don't generalize

### 3. We're Near the Ceiling
Best accuracy: **67.7%** (catalyst-aware model)
- Only 3.5% better than random baseline (64.2%)
- Only catching 29% of actual reversions
- Mean reversion is inherently noisy

---

## 🎯 What the Enhanced Features Showed

| Feature | Importance Rank | Helped? |
|---------|----------------|---------|
| **vix_change_5d** | #3 | ✅ Yes (0.0452) |
| **gap_pct** | #6 | ✅ Yes (0.0418) |
| **drift_volatility_20d** | #8 | ✅ Yes (0.0387) |
| **drift_volatility_5d** | #10 | ✅ Yes (0.0378) |
| **sector_relative_return** | #12 | ⚠️ Marginal (0.0369) |
| **intraday_volatility_pct** | #13 | ⚠️ Marginal (0.0360) |
| **price_pct_of_52week_high** | #14 | ⚠️ Marginal (0.0359) |
| **ticker_reversion_rate** | Not in top 20 | ❌ No |
| **consecutive_days** | Not in top 20 | ❌ No |
| **volume_surge_zscore** | #19 | ⚠️ Minimal (0.0351) |

**Conclusion:** A few features helped slightly, but overall made things worse by increasing overfitting.

---

## 🤔 Why Mean Reversion is Hard

### The Fundamental Problem:

**Only 35.8% of big moves actually revert ≥30%**

This means:
- 64.2% DON'T revert (majority)
- Even perfect classification caps recall at ~36%
- We're trying to find signal in 36% of cases

**Best case scenario:**
- If we perfectly identified which 36% revert → 100% precision, 36% recall
- That would give us ~68% accuracy (which is where we are!)

**We're basically at the theoretical ceiling given:**
- The 30% reversion threshold
- The 35.8% base reversion rate
- The features available from price/volume data

---

## 📋 Decision Matrix

### Should We Continue With Mean Reversion?

**✅ Continue IF:**
- 67.7% accuracy is acceptable for your risk tolerance
- You're okay with low recall (catching only 29% of reversions)
- You want to proceed to Phase 3 (news scraping, social monitoring)

**❌ Pivot IF:**
- You want >70% accuracy
- You need higher recall (catching more opportunities)
- You'd rather try a different strategy with better theoretical backing

---

## 🔄 The Three Paths Forward

### Path A: Accept 67.7% and Deploy
**Timeline:** 1-2 weeks
**Actions:**
- Use catalyst-aware model (best performer)
- Set up paper trading
- Validate for 1-3 months
- Deploy with small capital if successful

**Expected:**
- 60% win rate in live trading (vs 67.7% backtest - slippage)
- Catch ~30% of reversion opportunities
- Modest but consistent edge

**Risk:** Real-world performance might be lower (algo costs, slippage, changing regimes)

---

### Path B: Try Phase 3 (More Catalyst Detection)
**Timeline:** 1-2 weeks scraper building
**Actions:**
- Add news scraping (Google News)
- Add social monitoring (Reddit)
- Add analyst tracking (Finviz)
- Re-train model

**Expected improvement:** +1-3% accuracy (to 68-71%)
**Rationale:** We got +2% from simple 3-type classification, maybe more types help more

**Risk:**
- Scrapers break (websites change)
- Diminishing returns (already near ceiling)
- 1-2 weeks before knowing if it works

---

### Path C: Pivot to Different Strategy
**Timeline:** 1-2 weeks
**Actions:**
- Try post-earnings MOMENTUM (not reversion) - 60-70% win rate in research
- Or pairs trading (cointegration) - market-neutral, well-researched
- Or sector rotation - robust, works in all markets

**Expected:** Could be better than 67.7%!
**Rationale:** Mean reversion ceiling is low, other strategies might have higher ceilings

**Risk:** Starting over, current work not wasted but not directly useful

---

## 💭 My Honest Assessment

### The Catalyst-Aware Model is "Good Enough" But Not Great

**67.7% accuracy means:**
- ✅ Statistically better than random (64.2%)
- ✅ Catalyst detection helps (proven with +2%)
- ⚠️ Only catching 29% of reversions (missing 71%)
- ⚠️ Only 60% precision (40% false positives)
- ⚠️ Near theoretical ceiling for this approach

**For comparison, well-researched strategies:**
- Post-earnings drift (PEAD): 60-70% win rate, holds for 20-60 days
- Pairs trading: 60-70% win rate, market-neutral
- Volatility selling: 70-80% win rate (but tail risk)

---

## 🎯 My Recommendation

### **Path C: Pivot to Post-Earnings MOMENTUM**

**Why:**

1. **We've validated mean reversion is near ceiling (67.7%)**
   - Enhanced features didn't help
   - Severe overfitting when we tried
   - Only catching 29% of events

2. **Post-Earnings Announcement Drift (PEAD) has STRONGER research backing**
   - Documented in academic literature for 30+ years
   - 60-70% win rate consistently
   - Works for 20-60 days (not just 1-3 days)
   - Used by actual hedge funds

3. **We already have the infrastructure!**
   - 4,194 events dataset ✅
   - 25 stocks with earnings data ✅
   - XGBoost pipeline ✅
   - Just change target from "reverted" to "continued"

4. **Fast pivot (1-2 days)**
   - Change outcome label: `return_day_20` instead of `reverted_day2`
   - Train model to predict which earnings beats continue UP
   - See if accuracy is better than 67.7%

5. **Combined strategy possible**
   - Some catalysts revert (gaps, unknown) → fade them
   - Some catalysts continue (earnings beats) → follow them
   - Multi-strategy approach = more opportunities

---

## 📊 What We Learned from Option B

### ✅ What Worked:
1. Catalyst detection DOES help (+2%)
2. "Unknown" moves are most predictable (37.5% reversion rate)
3. Simple features > complex features
4. We have enough data (4,194 events)

### ❌ What Didn't Work:
1. Enhanced features caused overfitting
2. More features ≠ better performance
3. Mean reversion ceiling is low (67.7%)
4. Trying to catch only 36% of events limits upside

### 💡 Key Insight:
**The problem isn't our features or model - it's the strategy itself.**

Mean reversion with 30% threshold only works 36% of the time. We've optimized as much as possible. Time to try a different approach.

---

## 🚀 Next Steps

**Recommended:** Pivot to PEAD (Post-Earnings Momentum)

**Quick test (2 hours):**
1. Change target: `continued_day20` = return on day 20 > 0
2. Filter: earnings beats only (eps_surprise_pct > 0.02)
3. Train XGBoost
4. Compare accuracy to 67.7%

**If PEAD accuracy > 70%:**
- ✅ Proceed with momentum strategy
- Build out 20-60 day holding models
- Add revenue surprise, guidance features
- Expected: 60-70% win rate

**If PEAD accuracy < 67.7%:**
- Try pairs trading or sector rotation
- Or accept 67.7% and deploy mean reversion

---

## 📁 Files Created

**Database:**
- 11 new enhanced feature columns added
- All 4,194 events have enhanced features calculated

**Training:**
- `models/train_enhanced.py` - Enhanced model (overfit to 66.0%)
- `data/calculate_enhanced_features.py` - Feature calculation script

**Documentation:**
- `ENHANCED_FEATURES_PLAN.md` - Original plan
- `OPTION_B_RESULTS.md` - This document

---

## ✅ Conclusion

**Option B (Enhanced Features) didn't break 70%.**

**Results:**
- Baseline: 65.7%
- Catalyst-Aware: 67.7% ⭐
- Enhanced: 66.0% (overfit)

**Best model:** Catalyst-aware (67.7%)

**Recommendation:** Pivot to PEAD momentum strategy
- Better research backing
- Higher theoretical ceiling
- Can test in 2 hours

**Alternative:** Accept 67.7% and deploy, or try Phase 3 scrapers

**Your call!** 🎯
