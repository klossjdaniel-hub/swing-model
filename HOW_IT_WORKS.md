# How the Prediction System Works

**Simple explanation of the automated stock prediction system**

---

## What It Does

Monitors 350 stocks daily for big moves (>2% + high volume), then predicts if they'll reverse direction over the next 2-3 days.

**Current status:** 67.7% accuracy in backtesting, now running live to build real track record.

---

## The Timeline (How Predictions Work)

### Day 0 (e.g., March 6)
- Big move detected: "NVDA up 5.2% on 3x normal volume"
- System makes prediction: "68% chance this reverses in next 2-3 days"
- Prediction stored in database with timestamp

### Days 1-3 (March 7, 8, 9)
- System collects closing prices each day
- Waiting to see what actually happens
- No scoring yet - not enough data

### Night of Day 3 (March 9 at 9:15 PM UK)
- Market closes at 9:00 PM UK (4:00 PM ET)
- Pipeline runs at 9:15 PM UK (4:15 PM ET)
- Fetches final closing price for Day 3
- **NOW we can score:** Did the stock reverse as predicted?
- Updates win rate in database

### Day 4 Morning (March 10)
- Dashboard shows results: "I predicted X would reverse, and it did/didn't"
- Win rate updated with the results

**In short:** Predictions made on Day 0, scored on Night of Day 3, results visible Day 4 morning.

---

## Automated Daily Schedule

**Every weekday at 9:15 PM UK time (4:15 PM ET):**

1. Fetch latest closing prices (Yahoo Finance - free, no API key)
2. Scan all 350 stocks for big moves today
3. Make predictions for any new big moves detected
4. Score old predictions that now have 3 days of data
5. Update dashboard with latest win rate
6. Save results to GitHub

**You do:** Nothing - it's fully automated

**You check:** Dashboard next morning to see results

---

## What's Documented

### 1. Complete Prediction Records

Every prediction stores 17 data points:
- **What we predicted:** Direction, probability, confidence tier
- **The original move:** Size, direction, volume ratio, catalyst type
- **What happened:** Day 1, 2, 3 returns, did it actually revert
- **Metadata:** Timestamp, model version, when it was scored

### 2. Export to CSV

Run `python production/export_predictions.py` to get detailed spreadsheet with:
- Every prediction ever made
- Complete documentation of what was predicted vs what happened
- Win/loss for each prediction
- Suitable for Excel/Google Sheets analysis

### 3. Live Dashboard

**Web:** https://swing-model-crh4-oovicekw7-klossjdaniel-hubs-projects.vercel.app

Shows:
- Overall win rate
- High-confidence win rate
- Total predictions made
- Pending predictions (awaiting results)
- Recent activity

Updates automatically by pulling from GitHub.

### 4. Daily Terminal Output

Run `python production/dashboard.py` locally to see:
- Current win rate
- Performance by confidence tier
- Performance by catalyst type
- Recent predictions
- Pending predictions
- Trading activity timeline

---

## The Stock Universe

**350 stocks monitored:**

- All major S&P 500 stocks (280)
- Crypto-exposed stocks: COIN, MSTR, MARA, RIOT, CLSK, HUT, HOOD, SQ, SOFI, AFRM
- High-volatility biotech: MRNA, BNTX, SGEN, EXAS, etc.
- Meme stocks: GME, AMC, BBBY
- Recent IPOs and AI momentum plays

**Why 350?**
- Comprehensive market coverage
- Catches all significant moves
- Scan time: ~3-5 minutes (acceptable)

---

## How Predictions Are Made

### Detection Criteria
Stock must have:
1. >2% move from previous close
2. >1.5x average volume (vs 20-day average)

### Model Features (14 total)
- Move size and direction
- Volume ratio
- Pre-move drift (5-day and 20-day)
- VIX level
- Day of week
- Catalyst type (earnings, gap, unknown)
- Sector (Technology, Financials, Other)
- Market cap bucket (large, mid, small)

### Confidence Tiers
- **High:** ≥65% probability (best trades)
- **Medium:** 55-65% probability
- **Low:** <55% probability

### Scoring
Prediction is "correct" if stock reverses ≥30% of the original move within 3 days.

Example:
- Stock up 10% on Day 0
- Predict it will reverse
- If stock down ≥3% by Day 3 → **Correct**
- If stock still up or down <3% → **Wrong**

---

## Current Status

**Deployed:** ✅ Fully automated on GitHub Actions
**Dashboard:** ✅ Live at Vercel
**Data Source:** ✅ Yahoo Finance (free, reliable)
**Universe:** ✅ 350 stocks monitored
**Documentation:** ✅ Complete prediction tracking

**Waiting for:** Tonight's pipeline run (9:15 PM UK) to score first 20 predictions from March 6

**Next milestone:** Tomorrow morning - first real win rate appears on dashboard

---

## How to Check Results

### Daily (1 minute)
**Visit dashboard:** https://swing-model-crh4-oovicekw7-klossjdaniel-hubs-projects.vercel.app

Look for:
- Overall win rate (target: >60%)
- High-confidence win rate (target: >70%)
- New pending predictions

### Weekly (5 minutes)
**Export detailed results:**
```bash
cd "C:\Users\djklo\OneDrive\Documents\GitHub\swing-model"
python production/export_predictions.py
```

Then answer Y to export CSV and analyze in Excel.

### Manual Dashboard View
```bash
python production/dashboard.py
```

Shows full terminal-based dashboard with all stats.

---

## Repository Structure

```
swing-model/
├── data/
│   └── swing_model.db          # SQLite database with all predictions
├── production/
│   ├── detect_and_predict.py   # Core prediction engine
│   ├── score_predictions.py    # Scores old predictions
│   ├── dashboard.py            # Terminal dashboard
│   ├── export_predictions.py   # CSV export tool
│   └── run_daily_pipeline.py   # Main automation script
├── web/
│   └── index.html              # Live dashboard (deployed to Vercel)
├── .github/workflows/
│   └── daily-pipeline.yml      # GitHub Actions automation
├── universe.py                 # 350-stock list
└── HOW_IT_WORKS.md            # This file
```

---

## Tech Stack

- **Language:** Python 3.9+
- **Data Source:** Yahoo Finance (yfinance library)
- **Database:** SQLite (local file: swing_model.db)
- **Model:** XGBoost binary classifier (saved as pickle)
- **Automation:** GitHub Actions (2,000 free minutes/month)
- **Dashboard:** Static HTML + JavaScript (no backend needed)
- **Hosting:** Vercel (free tier)
- **Cost:** £0 (all free services)

---

## Example Prediction Flow

**March 6, 2:00 PM:**
- Market closes, COIN up 8.2% on 4.1x volume
- Pipeline detects move at 4:15 PM ET (9:15 PM UK)
- Model predicts: 71% chance of reversion (HIGH confidence)
- Stores prediction with all details

**March 7-9:**
- Collects closing prices each day
- Prediction shows as "Pending" on dashboard

**March 9, 9:15 PM UK:**
- Pipeline runs, fetches March 9 closing price
- Calculates: COIN actually down 5.8% from March 6 peak
- 5.8% > 30% of 8.2% → **REVERSAL CONFIRMED**
- Marks prediction as CORRECT
- Updates win rate

**March 10, 8:00 AM:**
- You check dashboard
- See: "21 total predictions, 14 correct, 66.7% win rate"
- COIN prediction shows as ✓ CORRECT

---

## What Makes a Good Result?

### Target Performance
- **Overall win rate:** 60-65%
- **High-confidence win rate:** 70-75%
- **Sample size:** 40+ predictions per month

### Validation Period
Need **8-12 weeks** of live results to validate the model.

With ~10 predictions/week = 80-120 total predictions over 8-12 weeks.

### Credibility
Every prediction is:
- Timestamped before market open
- Stored in public GitHub repo (immutable)
- Fully documented (what we predicted, what happened)
- Exportable to CSV for external verification

---

## Questions?

**"When do results appear?"**
→ Next morning after scoring happens at 9:15 PM UK

**"How do I see detailed results?"**
→ Run `python production/export_predictions.py`

**"What if I miss a day?"**
→ No problem - system runs automatically, just check dashboard anytime

**"Can I see individual predictions?"**
→ Yes - dashboard shows recent predictions and CSV export has all details

**"How do I know it's working?"**
→ Check dashboard URL - should update daily with new predictions/results

---

**Last updated:** March 9, 2026
**System status:** ✅ Fully operational
**Next run:** Tonight at 9:15 PM UK
