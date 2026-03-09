# Paper Trading Setup Guide

**Your 67.7% catalyst-aware reversion model is ready for live validation!**

---

## 🚀 Quick Start (First Time Setup)

### Step 1: Train and Save the Model

```bash
cd "C:\Users\djklo\OneDrive\Documents\GitHub\swing-model"
python models/save_model.py
```

**What this does:**
- Trains the catalyst-aware model on all 4,194 historical events
- Saves to `models/catalyst_aware_model.pkl`
- This file will be loaded daily for predictions

**Expected output:**
```
[OK] Model saved and ready for production
Test Accuracy: 67.7%
```

---

### Step 2: Run the Daily Pipeline (Test It)

```bash
python production/run_daily_pipeline.py
```

**What this does:**
1. Fetches latest prices from Finnhub (last 5 days)
2. Scans for big moves (>2%, >1.5x volume)
3. Generates predictions using the model
4. Scores previous predictions (if any)

**Expected output:**
```
STEP 1/3: Fetching latest prices from Finnhub...
  [OK] 50 stocks fetched

STEP 2/3: Detecting big moves and generating predictions...
  Big moves detected: X
  Predictions generated: X
  [HIGH CONFIDENCE] predictions shown

STEP 3/3: Scoring previous predictions...
  WIN RATE: X%
```

---

### Step 3: View the Dashboard

```bash
python production/dashboard.py
```

**What you'll see:**
- Overall win rate
- Performance by confidence tier (high/medium/low)
- Performance by catalyst type (earnings/gap/unknown)
- Recent predictions
- Pending predictions

---

## 📅 Daily Workflow (Ongoing)

### Manual Mode (While Testing)

**Every day after market close (4:30 PM ET or later):**

```bash
cd "C:\Users\djklo\OneDrive\Documents\GitHub\swing-model"
python production/run_daily_pipeline.py
```

**Then check dashboard:**

```bash
python production/dashboard.py
```

**Review:**
- Did we get any high-confidence predictions today?
- What was yesterday's win rate?
- Are we maintaining 60%+ accuracy?

---

### Automated Mode (After Validation)

**Set up Windows Task Scheduler:**

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Swing Model Daily Pipeline"
4. Trigger: Daily at 6:00 PM
5. Action: Start a program
   - Program: `python`
   - Arguments: `production\run_daily_pipeline.py`
   - Start in: `C:\Users\djklo\OneDrive\Documents\GitHub\swing-model`

**This will run automatically every day!**

---

## 📊 What the Model Does

### Detection Criteria:

**A "big move" is detected when:**
- Stock moves >2% in one day
- Volume is >1.5x the 20-day average
- Happens to any stock in our 50-stock universe

### Catalyst Classification:

Each big move is classified as:
- **earnings** - If it's an earnings report day
- **gap** - If stock gapped >1% from previous close
- **unknown** - No clear catalyst (best reversion candidates!)

### Prediction:

**Model outputs:**
- Probability of reversion (0-100%)
- Confidence tier:
  - **HIGH** - ≥65% probability (trade these!)
  - **MEDIUM** - 55-65% probability (watch)
  - **LOW** - <55% probability (skip)

### Expected Performance:

**Backtest:** 67.7% accuracy
**Live target:** 60%+ accuracy (allowing for slippage)

**High-confidence predictions** should have ~70% win rate

---

## 🎯 Trading Rules (Paper Trading)

### When to Take a Trade:

**ONLY trade high-confidence predictions (≥65% probability)**

**For high-confidence predictions:**

1. **If stock moved UP and model says revert:**
   - Action: SHORT (or buy puts)
   - Entry: Next day at open
   - Exit: When reverts ≥30% OR day 3 (whichever first)

2. **If stock moved DOWN and model says revert:**
   - Action: LONG (or buy calls)
   - Entry: Next day at open
   - Exit: When reverts ≥30% OR day 3 (whichever first)

### Example:

```
[HIGH CONFIDENCE] AAPL
  Move: UP 5.2% (volume 2.3x)
  Catalyst: unknown
  Prediction: 72% chance of reversion
  Action: SHORT (fade the move)

Trade plan:
  Entry: Next day at open (short AAPL)
  Target: -1.6% move (30% of initial 5.2%)
  Stop: Day 3 close
  Expected: 70% chance this works
```

---

## 📈 Performance Tracking

### Key Metrics to Watch:

1. **Overall Win Rate**
   - Target: ≥60%
   - If <55% after 30 trades → revisit model

2. **High-Confidence Win Rate**
   - Target: ≥70%
   - These are your best trades

3. **Frequency**
   - Expected: 2-3 predictions per day
   - 1-2 high-confidence per week

4. **Catalyst Performance**
   - **Unknown** should perform best (highest reversion rate)
   - **Earnings** should be worst (PEAD effect)

### Dashboard Command:

```bash
python production/dashboard.py
```

Shows all these metrics updated daily!

---

## 🗂️ File Structure

```
swing-model/
├── production/
│   ├── run_daily_pipeline.py       ← RUN THIS DAILY
│   ├── fetch_daily_prices.py       (Step 1: Get prices)
│   ├── detect_and_predict.py       (Step 2: Predict)
│   ├── score_predictions.py        (Step 3: Score)
│   └── dashboard.py                ← VIEW PERFORMANCE
│
├── models/
│   ├── save_model.py               ← RUN ONCE (setup)
│   └── catalyst_aware_model.pkl    (Trained model)
│
├── data/
│   └── swing_model.db              (Database with predictions)
│
└── PAPER_TRADING_SETUP.md          (This file)
```

---

## ❓ FAQ

### Q: How often should I run the pipeline?

**A:** Once per day, after market close (6 PM ET is safe)

### Q: What if I miss a day?

**A:** No problem! The pipeline fetches the last 5 days of prices, so it will catch up.

### Q: How long until I have enough data to validate?

**A:**
- After 30 predictions: Can see if >50% win rate
- After 100 predictions: Statistically significant
- After 3 months: Confident to deploy real capital

### Q: What if win rate is below 60%?

**A:**
- Check if high-confidence predictions are >65% (they should be)
- If overall <55% after 50+ predictions → model not working in live
- Consider Phase 3 (enhanced catalyst detection) or pivot

### Q: Can I run this intraday?

**A:**
- Technically yes, but designed for daily after-close
- Intraday would need real-time price feeds (not Finnhub daily API)

### Q: How do I actually place trades?

**A:**
- Currently: Paper trading only (track mentally or in spreadsheet)
- Future: Could integrate with broker API (Alpaca, Interactive Brokers)
- For now: Write down each high-confidence prediction and track manually

---

## 🎓 Success Criteria (3-Month Validation)

### After 3 months of paper trading, proceed to live trading IF:

✅ Overall win rate ≥ 60%
✅ High-confidence win rate ≥ 65%
✅ At least 50 predictions total
✅ Performance stable across catalyst types
✅ No major regime changes (market crash, etc.)

### If criteria met:

**Deploy with small capital:**
- Start with 5-10% of trading capital
- 1-2% risk per trade
- Scale up if maintaining 60%+ for 6 months

---

## 📞 Troubleshooting

### "Model not found" error

**Solution:** Run `python models/save_model.py` first

### "No price data found"

**Solution:**
1. Check Finnhub API key in .env
2. Run `python production/fetch_daily_prices.py` manually
3. Check Finnhub API limits (60 calls/min)

### "No big moves detected"

**Normal!** Some days have no qualifying moves. The model is selective.

### Win rate tracking seems off

**Check:**
1. Are you waiting 3 days before scoring? (predictions need time)
2. Run `python production/score_predictions.py` manually
3. Check forward_predictions table in database

---

## 🎉 You're Ready!

**Your paper trading system is complete:**
- ✅ Trained model (67.7% backtest accuracy)
- ✅ Daily data fetching (Finnhub)
- ✅ Automated prediction generation
- ✅ Performance tracking & scoring
- ✅ Dashboard for monitoring

**Next steps:**
1. Run `python models/save_model.py` (one time)
2. Run `python production/run_daily_pipeline.py` (daily)
3. Review `python production/dashboard.py` (daily)
4. Track performance for 3 months
5. Deploy with real capital if win rate ≥ 60%

**Good luck!** 🚀
