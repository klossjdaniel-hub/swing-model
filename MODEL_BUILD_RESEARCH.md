# Model Build & Validation Research

**Date:** March 10, 2026
**Purpose:** Research findings before building production-grade prediction models

---

## Key Research Findings

### 1. Overfitting is THE Critical Risk

**Source:** [Backtest overfitting in ML era](https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110)

**Problem:**
- ML models easily learn **spurious patterns** in historical data
- High backtest accuracy ≠ real-world performance
- Financial data is **extremely noisy** with low signal-to-noise ratio

**Our current risk:**
- We tested on 2024-2025 data (recent)
- Haven't tested across different market regimes
- 100% accuracy on 7 earnings predictions = **suspiciously good** (likely overfitting)

**Solution needed:**
- Walk-forward validation across multiple years
- Test on completely unseen data
- Reduce model complexity if needed

---

### 2. Walk-Forward Validation is Industry Standard

**Source:** [Walk-Forward Analysis 2026](https://medium.com/@NFS303/walk-forward-analysis-a-production-ready-comparison-of-three-validation-approaches-69cd25fc9fc7)

**What it is:**
1. Train on Year 1-2
2. Test on Year 3
3. **Roll forward:** Train on Year 2-3, test on Year 4
4. Repeat for entire dataset
5. Aggregate all out-of-sample results

**Why it works:**
- Simulates real deployment (you retrain periodically)
- Each test period is truly unseen
- Prevents "peeking into the future"

**Our current approach:**
- ❌ Simple train/test split (2024-2025 = test)
- ❌ No rolling validation
- ❌ No multiple market regimes tested

**What we need:**
- ✅ Walk-forward with 1-year windows
- ✅ Test across 2020-2026 (includes COVID crash, bull market, rate hikes)
- ✅ Aggregate results to get true accuracy

---

### 3. Generalization Ratio is Key Metric

**Source:** [GT-Score for reducing overfitting](https://www.mdpi.com/1911-8074/19/1/60)

**Formula:**
```
Generalization Ratio = Out-of-Sample Performance / In-Sample Performance
```

**Interpretation:**
- **>0.9:** Excellent generalization
- **0.7-0.9:** Good (some degradation expected)
- **<0.7:** Poor (overfitting)

**Example:**
- Train accuracy: 80%
- Test accuracy: 72%
- Generalization ratio: 72/80 = 0.90 ✓ Good

**Our current situation:**
- Train: Unknown (haven't checked)
- Test: 75-100%
- **Need to calculate this!**

---

### 4. Financial Model Audit Checklist

**Source:** [Best practices for model review](https://www.flatworldsolutions.com/financial-services/articles/best-practices-assessing-reviewing-financial-models.php)

**Essential checks:**

1. **Data Quality**
   - No data leakage (using future data to predict past)
   - No survivorship bias (missing delisted stocks)
   - Proper handling of corporate actions (splits, dividends)

2. **Feature Engineering**
   - No look-ahead bias (features calculated with only past data)
   - Handle missing values properly
   - Standardize/normalize features

3. **Model Architecture**
   - Appropriate complexity for data size
   - Regularization to prevent overfitting
   - Cross-validation strategy

4. **Performance Metrics**
   - Accuracy (overall correctness)
   - Precision (when you predict yes, how often right?)
   - Recall (of all yes cases, how many did you catch?)
   - F1 score (balance of precision/recall)
   - Confusion matrix

5. **Robustness Tests**
   - Performance across different time periods
   - Performance across different sectors
   - Performance in bull vs bear markets
   - Sensitivity to parameter changes

---

## Current Model Status

### What We Have

**Model 1: Earnings Fade**
- Test accuracy: 100% (7/7 predictions)
- Test period: 2024-2025
- Sample size: 73 earnings events total
- **Status:** ⚠️ Suspiciously perfect, needs more validation

**Model 2: Unknown Catalyst Fade**
- Test accuracy: 91.3% at 50% threshold
- Test period: 2024-2025
- Sample size: 693 events
- **Status:** ⚠️ Good but needs cross-validation

### What We Don't Know

❌ Train set accuracy (can't calculate generalization ratio)
❌ Performance in 2020-2023 (different market conditions)
❌ Feature importance (which features actually matter?)
❌ Confusion matrix (what types of errors do we make?)
❌ Performance degradation over time
❌ Robustness to parameter changes

---

## Critical Risks Identified

### Risk 1: Look-Ahead Bias

**What it is:** Using future information to predict the past

**Examples:**
- Using Day 3 price to calculate Day 0 features
- Including post-event data in pre-event calculations

**Our check needed:**
- Verify all features use ONLY data available at prediction time
- Check `pre_earnings_drift` calculations
- Verify `volume_ratio` uses historical average

### Risk 2: Data Leakage

**What it is:** Train and test sets share information

**Examples:**
- Same stock appears in both train and test
- Features calculated across entire dataset (including test period)

**Our check needed:**
- Verify strict time-based split
- No cross-contamination of statistics

### Risk 3: Small Sample Overfitting

**Earnings model:**
- Only 7 test predictions with 100% accuracy
- Could be pure luck (7 coin flips = 0.78% chance of all heads)
- **Need:** 50+ predictions minimum for statistical significance

**Solution:**
- Expand test set using walk-forward validation
- Don't trust 100% on tiny samples

### Risk 4: Market Regime Dependency

**What it is:** Model works in bull markets, fails in bear

**Our risk:**
- 2024-2025 was mostly bullish
- Haven't tested in:
  - 2020 COVID crash
  - 2022 bear market
  - 2023 recovery

**Solution:**
- Test across all market conditions
- Report separate accuracies by regime

---

## Required Validation Pipeline

### Phase 1: Data Quality Audit

1. **Check for look-ahead bias**
   - Review feature calculation code
   - Verify date filters
   - Ensure no future data used

2. **Check for data leakage**
   - Verify train/test split
   - Check feature normalization
   - Ensure independence

3. **Check for survivorship bias**
   - Confirm dataset includes delisted stocks
   - Check if selection criteria introduces bias

### Phase 2: Walk-Forward Validation

**Setup:**
```
Training Windows:
- 2020-2021 → Test 2022
- 2021-2022 → Test 2023
- 2022-2023 → Test 2024
- 2023-2024 → Test 2025
- 2024-2025 → Test 2026 (current)
```

**For each window:**
- Train model
- Generate predictions on test period
- Calculate metrics
- Store results

**Aggregate:**
- Overall accuracy across all test periods
- Accuracy by year
- Generalization ratio
- Stability of performance

### Phase 3: Robustness Testing

1. **Cross-sectional tests**
   - Accuracy by sector
   - Accuracy by market cap
   - Accuracy by move size

2. **Temporal tests**
   - Accuracy by year
   - Accuracy by market regime
   - Performance degradation over time

3. **Sensitivity analysis**
   - Vary confidence thresholds
   - Test different reversion definitions (20%, 30%, 40%)
   - Feature ablation (remove features one by one)

### Phase 4: Error Analysis

1. **Confusion matrix**
   ```
                Predicted No    Predicted Yes
   Actual No         TN              FP
   Actual Yes        FN              TP
   ```

2. **Analyze false positives**
   - What do wrong "fade" predictions have in common?
   - Are we missing a key feature?

3. **Analyze false negatives**
   - What reversions did we miss?
   - Why didn't model flag them?

---

## Model Improvement Checklist

### Before Declaring Victory

- [ ] Walk-forward validation complete
- [ ] Generalization ratio >0.8
- [ ] Tested across 5+ years of data
- [ ] Tested in bull AND bear markets
- [ ] Sample size >50 predictions per model
- [ ] Feature importance analysis done
- [ ] Error analysis complete
- [ ] No look-ahead bias confirmed
- [ ] No data leakage confirmed
- [ ] Performance stable across time
- [ ] Documented limitations clearly

### Red Flags That Mean Overfitting

🚩 Perfect accuracy (100%) on small samples
🚩 Train accuracy >> Test accuracy
🚩 Generalization ratio <0.7
🚩 Performance degrades rapidly over time
🚩 Model only works in one market regime
🚩 Adding more features keeps improving accuracy
🚩 Can't explain why model works

---

## Recommended Approach

### Week 1: Audit Current Model

**Goals:**
- Calculate train set accuracy
- Check for look-ahead bias
- Verify data quality
- Calculate generalization ratio

**Deliverable:** "Current Model Audit Report"

### Week 2: Walk-Forward Validation

**Goals:**
- Implement walk-forward validation
- Test 2020-2026 with rolling windows
- Aggregate results across all periods

**Deliverable:** "Walk-Forward Validation Results"

### Week 3: Robustness Testing

**Goals:**
- Test across market regimes
- Test across sectors
- Sensitivity analysis

**Deliverable:** "Robustness Test Results"

### Week 4: Error Analysis & Refinement

**Goals:**
- Analyze false positives/negatives
- Feature importance analysis
- Model refinement if needed

**Deliverable:** "Final Model with Documented Performance"

---

## Expected Outcomes

### Realistic Accuracy Estimates

**Current claims:**
- Earnings: 100% (7/7)
- Unknown: 91% (115 predictions)

**After proper validation, expect:**
- Earnings: 60-75% (more realistic)
- Unknown: 65-75% (some degradation expected)
- Overall: Still strong edge, but not perfect

### Why Lower is Actually Better

**60% with proper validation > 100% with cherry-picking**

Reasons:
- Provable and reproducible
- Works across market conditions
- Survives regime changes
- Builds real credibility

---

## Production Deployment Checklist

Once models are validated:

- [ ] Prediction pipeline automated
- [ ] Results logged to GitHub (immutable)
- [ ] Performance monitoring dashboard
- [ ] Alerts when model degrades
- [ ] Monthly retraining schedule
- [ ] Documented assumptions and limitations
- [ ] Clear confidence thresholds
- [ ] Transparent track record

---

## Key References

- [Backtest Overfitting Study](https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110) - CPCV vs Walk-Forward
- [GT-Score for Generalization](https://www.mdpi.com/1911-8074/19/1/60) - Anti-overfitting objective function
- [Walk-Forward Validation Guide](https://medium.com/@NFS303/walk-forward-analysis-a-production-ready-comparison-of-three-validation-approaches-69cd25fc9fc7) - 2026 implementation
- [Financial Model Audit Best Practices](https://www.flatworldsolutions.com/financial-services/articles/best-practices-assessing-reviewing-financial-models.php)
- [Time Series Cross-Validation](https://medium.com/@pacosun/respect-the-order-cross-validation-in-time-series-7d12beab79a1)

---

## Bottom Line

**We have promising results, but they're not validated yet.**

Current status:
- ✅ Models show strong initial performance
- ✅ Good sample sizes (except earnings)
- ❌ Only tested on recent data (2024-2025)
- ❌ No walk-forward validation
- ❌ Unknown train set performance
- ❌ Not tested across market regimes

**Next step:** Rigorous validation before claiming any accuracy numbers publicly.

**Timeline:** 2-3 weeks of proper validation work before launch.

**Outcome:** Lower claimed accuracy, but 100% credible and defensible.
