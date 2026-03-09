# Enhanced Feature Engineering Plan

**Goal:** Reach 70%+ accuracy using only existing price/volume data (no scrapers!)

**Timeline:** 2-3 days

---

## 🎯 New Features to Add

### 1. Intraday Volatility (Emotion Gauge)
**Feature:** `intraday_volatility_pct`
**Calculation:** `(high - low) / open` on Day 0
**Why it helps:** Large intraday swings = emotional trading = more likely to revert
**Expected impact:** HIGH

### 2. Gap Size (Universal)
**Feature:** `gap_pct`
**Calculation:** `(open - prev_close) / prev_close`
**Why it helps:** Even non-gap events have some gap, measures overnight emotion
**Expected impact:** MEDIUM

### 3. Volume Surge Magnitude
**Feature:** `volume_surge_zscore`
**Calculation:** Z-score of volume vs 20-day mean/std
**Why it helps:** Extreme volume (3+ sigma) = unsustainable = revert
**Expected impact:** HIGH

### 4. Drift Volatility
**Feature:** `drift_volatility_5d`, `drift_volatility_20d`
**Calculation:** Std deviation of daily returns over 5d, 20d before Day 0
**Why it helps:** High volatility = unstable = more reversions
**Expected impact:** MEDIUM

### 5. Recent Reversion Tendency
**Feature:** `ticker_reversion_rate_historical`
**Calculation:** % of this stock's previous big moves that reverted
**Why it helps:** Some stocks are "reverters", some aren't (behavior persists)
**Expected impact:** HIGH

### 6. VIX Change (Not Just Level)
**Feature:** `vix_change_5d`
**Calculation:** VIX today vs 5 days ago
**Why it helps:** VIX spike = fear spike = reversions more common
**Expected impact:** MEDIUM

### 7. Sector-Relative Performance
**Feature:** `sector_relative_return_day0`
**Calculation:** Stock's Day 0 return vs sector average return
**Why it helps:** Outperformance vs peers = more likely to revert to sector mean
**Expected impact:** MEDIUM

### 8. Price Level (52-week position)
**Feature:** `price_pct_of_52week_high`
**Calculation:** Current price / 52-week high
**Why it helps:** Stocks near highs have less room to run = more reversions
**Expected impact:** LOW-MEDIUM

### 9. Consecutive Move Direction
**Feature:** `consecutive_days_same_direction`
**Calculation:** How many days in a row moved in same direction before Day 0
**Why it helps:** Momentum exhaustion = reversion
**Expected impact:** MEDIUM

### 10. Move Magnitude Bucket
**Feature:** `move_magnitude_bucket`
**Calculation:** Categorize into: 2-3%, 3-5%, 5-10%, >10%
**Why it helps:** Extreme moves (>10%) revert more than mild moves (2-3%)
**Expected impact:** MEDIUM

---

## 📊 Implementation Plan

### Day 1: Calculate & Store Features (4-5 hours)

**Step 1:** Add columns to events table
- Add all 10+ new feature columns
- Run migration script

**Step 2:** Calculate features for all 4,194 events
- Iterate through events
- Calculate each feature from price/volume data
- Update database

**Step 3:** Validate
- Check for NULL values
- Verify calculations on sample events
- Ensure distributions make sense

---

### Day 2: Train Enhanced Model (2-3 hours)

**Step 1:** Prepare features
- Load events with new features
- Handle missing values
- Normalize/scale features if needed

**Step 2:** Train XGBoost
- Same 80/20 split
- Maybe tune hyperparameters (learning rate, depth, etc.)

**Step 3:** Evaluate
- Test accuracy
- Feature importance (which new features matter most?)
- Confusion matrix

---

### Day 2-3: Decision Point

**If accuracy ≥ 70%:**
- ✅ **SUCCESS!** Model is good enough to proceed
- Next: Paper trading or Phase 3 catalyst detection
- We proved feature engineering > scrapers

**If accuracy 68-69%:**
- ⚠️ **Marginal gain** - close but not quite
- Decision: Proceed to Phase 3 (scrapers) or pivot?

**If accuracy < 68%:**
- ❌ **No improvement** - feature engineering didn't help
- Likely: Mean reversion is near ceiling
- Recommendation: Pivot to different strategy

---

## 🔧 Technical Details

### New Database Columns

```sql
ALTER TABLE events ADD COLUMN intraday_volatility_pct REAL;
ALTER TABLE events ADD COLUMN gap_pct REAL;
ALTER TABLE events ADD COLUMN volume_surge_zscore REAL;
ALTER TABLE events ADD COLUMN drift_volatility_5d REAL;
ALTER TABLE events ADD COLUMN drift_volatility_20d REAL;
ALTER TABLE events ADD COLUMN ticker_reversion_rate_historical REAL;
ALTER TABLE events ADD COLUMN vix_change_5d REAL;
ALTER TABLE events ADD COLUMN sector_relative_return_day0 REAL;
ALTER TABLE events ADD COLUMN price_pct_of_52week_high REAL;
ALTER TABLE events ADD COLUMN consecutive_days_same_direction INTEGER;
ALTER TABLE events ADD COLUMN move_magnitude_bucket TEXT;
```

### Feature Calculation Examples

**Intraday Volatility:**
```python
intraday_volatility_pct = (high - low) / open
```

**Volume Surge Z-Score:**
```python
mean_vol = avg_volume_20d
std_vol = std_volume_20d
volume_surge_zscore = (day0_volume - mean_vol) / std_vol
```

**Ticker Reversion Rate:**
```python
# Get all previous big moves for this ticker
previous_moves = get_previous_events(ticker, before_date)
# Calculate % that reverted
reversion_rate = sum(previous_moves.reverted_day2) / len(previous_moves)
```

**Sector-Relative Return:**
```python
sector_stocks_returns = get_same_sector_returns(sector, day0_date)
sector_avg = mean(sector_stocks_returns)
sector_relative = day0_return - sector_avg
```

---

## 📈 Expected Results

### Conservative Estimate:
- New features add 1-2% accuracy
- Total: **68-69%** (from current 67.7%)
- Precision: **62-65%**
- Recall: **30-35%**

### Optimistic Estimate:
- New features add 3-5% accuracy
- Total: **70-73%** (breakthrough!)
- Precision: **65-70%**
- Recall: **35-40%**

### Most Likely:
- Total accuracy: **69-71%**
- Enough to justify continuing with this approach
- Some features help a lot, others don't matter

---

## 🎯 Success Criteria

**Proceed with mean reversion strategy if:**
- Accuracy ≥ 70%
- Precision ≥ 65% (when we say revert, right 65% of time)
- Recall ≥ 33% (catching 1/3 of reversions)
- Feature importance makes intuitive sense

**Pivot to different strategy if:**
- Accuracy < 68%
- No clear improvement from new features
- Overfitting (train accuracy >> test accuracy)

---

## 💡 Key Insights We're Testing

1. **Emotion = Reversion**: Intraday volatility, volume surges, gaps measure emotion
2. **History Repeats**: Stocks that reverted before will revert again
3. **Mean Reversion to Sector**: Outperformers revert to sector average
4. **Exhaustion**: Consecutive moves in one direction exhaust
5. **Extremes Revert**: Very large moves (>10%) revert more than small (2-3%)

If these hypotheses are TRUE → features will help
If they're FALSE → we're near the ceiling, need different approach

---

## 📋 Files to Create

**Day 1:**
- `data/add_enhanced_features.py` - Migration script
- `data/calculate_enhanced_features.py` - Feature calculation
- `data/validate_features.py` - Sanity checks

**Day 2:**
- `models/train_enhanced.py` - New model with all features
- `models/compare_all_models.py` - 3-way comparison
- `ENHANCED_RESULTS.md` - Final analysis

---

## 🚀 Let's Do This!

We're squeezing every drop of signal from existing data before building scrapers.

**Smart approach because:**
- Fast (2-3 days not 1-2 weeks)
- Low risk (no scrapers to maintain)
- Validates if approach has legs
- Learn what features actually matter

**Starting now!** 🎯
