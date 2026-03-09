# Deploy Your Paper Trading System NOW

**3 simple steps to get automated daily predictions + live dashboard**

---

## ⚡ Step 1: Push to GitHub (2 minutes)

```bash
cd "C:\Users\djklo\OneDrive\Documents\GitHub\swing-model"

# Add all files
git add .

# Commit
git commit -m "Add automated paper trading system with GitHub Actions"

# Push to GitHub
git push origin main
```

**What this does:** Uploads all code to GitHub so it can run automatically

---

## 🔐 Step 2: Add Finnhub API Key to GitHub (1 minute)

1. Go to your GitHub repo: `https://github.com/YOUR_USERNAME/swing-model`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `FINNHUB_API_KEY`
5. Value: `d5uh709r01qr4f897r9gd5uh709r01qr4f897ra0`
6. Click **Add secret**

**What this does:** Gives GitHub Actions access to fetch prices from Finnhub

---

## 🚀 Step 3: Run First Pipeline (1 minute)

1. Go to **Actions** tab in your GitHub repo
2. Click **Daily Paper Trading Pipeline** (left sidebar)
3. Click **Run workflow** → **Run workflow** (green button)

**What happens:**
- Fetches latest prices from Finnhub
- Detects any big moves today
- Generates predictions
- Creates a GitHub Issue with daily summary
- Saves results to `daily_results/` folder

**You'll get:**
- ✅ Daily GitHub Issue with summary (check Issues tab)
- ✅ Results saved to `daily_results/dashboard_YYYY-MM-DD.txt`
- ✅ Database updated with predictions

---

## 📊 Step 4: Deploy Live Dashboard (Optional - 2 minutes)

### Option A: View on GitHub (Simplest)

After pipeline runs, check:
- **Issues tab** → Latest daily update
- **daily_results** folder → Raw dashboard output

### Option B: Deploy to Vercel (Prettier)

1. Update `web/dashboard.html` line 216:
   ```javascript
   // Change this line:
   const response = await fetch('https://api.github.com/repos/YOUR_USERNAME/swing-model/contents/daily_results');

   // To (replace YOUR_USERNAME with your GitHub username):
   const response = await fetch('https://api.github.com/repos/djklo/swing-model/contents/daily_results');
   ```

2. Commit and push:
   ```bash
   git add web/dashboard.html
   git commit -m "Update dashboard with correct GitHub username"
   git push origin main
   ```

3. Deploy to Vercel:
   - Go to https://vercel.com
   - Click **Add New** → **Project**
   - Import `swing-model` repo
   - Framework Preset: **Other**
   - Root Directory: `web`
   - Click **Deploy**

4. You'll get a URL like `https://swing-model.vercel.app`

**What you'll see:**
- Live dashboard with win rate
- Recent predictions
- Performance stats
- Updates automatically!

---

## ✅ Done! Here's What Happens Now:

### Automatically Every Weekday at 6 PM ET:

1. **GitHub Actions runs** (free, 2000 minutes/month)
2. **Fetches latest prices** from Finnhub
3. **Detects big moves** (>2%, >1.5x volume)
4. **Generates predictions** using your trained model
5. **Scores old predictions** (checks if they were right)
6. **Creates GitHub Issue** with daily summary
7. **Saves results** to repository

### You Get Notified:

- **GitHub Issue** created daily (you'll get email if notifications on)
- **Dashboard updates** (if you deployed to Vercel)
- **Check Issues tab** anytime for history

---

## 📱 How to Check Daily:

### Method 1: GitHub Issues (Easiest)

1. Go to your repo → **Issues** tab
2. See latest daily update
3. Shows:
   - Win rate
   - High-confidence predictions
   - Recent performance

### Method 2: Live Dashboard (Prettiest)

1. Go to your Vercel URL (if deployed)
2. See real-time stats
3. Auto-refreshes every 5 minutes

### Method 3: GitHub Files (Most Detail)

1. Go to `daily_results/` folder in repo
2. Open latest `dashboard_YYYY-MM-DD.txt`
3. See full performance breakdown

---

## 🎯 What to Look For:

### Every Day:

**Check GitHub Issue for:**
- Any high-confidence predictions? (≥65% probability)
- What's the current win rate?
- Any trends?

**If you see high-confidence prediction:**
```
[HIGH CONFIDENCE] NVDA
  Move: UP 6.2% (volume 2.8x)
  Catalyst: unknown
  Prediction: 68% chance of reversion
  Action: SHORT (fade the move)
```

**What to do (paper trading):**
- Write it down (ticker, direction, probability)
- Track outcome after 3 days
- Compare to model prediction

### Every Week:

**Review dashboard:**
- Is win rate trending toward 60%?
- Are high-confidence predictions performing well?
- Any patterns?

### Every Month:

**Assess performance:**
- Total predictions: aim for 40-60/month
- Win rate: should be 55-65%
- High-confidence win rate: should be 65-75%

---

## 🔧 Manual Controls:

### Run Pipeline Manually:

1. Go to **Actions** → **Daily Paper Trading Pipeline**
2. Click **Run workflow**
3. Wait 2-3 minutes for results

### View Dashboard Locally:

```bash
cd "C:\Users\djklo\OneDrive\Documents\GitHub\swing-model"
python production/dashboard.py
```

### Check Latest Results:

```bash
# View most recent issue
git pull
cat daily_results/dashboard_$(date +%Y-%m-%d).txt
```

---

## 📊 Example Daily Issue:

```markdown
## Paper Trading Daily Summary

**Date:** 2026-03-10

### Performance
- **Current Win Rate:** 65.2%
- **High-Confidence Predictions Today:** 2

### High-Confidence Predictions

[HIGH CONFIDENCE] META
  Move: UP 4.8% (volume 2.1x)
  Catalyst: unknown
  Prediction: 71% chance of reversion
  Action: SHORT (fade the move)

[HIGH CONFIDENCE] NVDA
  Move: DOWN 5.2% (volume 3.4x)
  Catalyst: gap
  Prediction: 66% chance of reversion
  Action: LONG (fade the move)

### Dashboard
Total Predictions: 23
Correct: 15
WIN RATE: 65.2%

Performance by Confidence Tier:
  HIGH: 10/14 (71.4%)
  MEDIUM: 3/6 (50.0%)
  LOW: 2/3 (66.7%)
```

---

## ⚠️ Troubleshooting:

### "Workflow failed" in GitHub Actions:

**Check:**
1. Did you add Finnhub API key secret?
2. Is it named exactly `FINNHUB_API_KEY`?
3. Check Actions logs for error message

### "No data available" on dashboard:

**Fix:**
1. Run pipeline manually first (Actions → Run workflow)
2. Wait for it to complete
3. Refresh dashboard

### Not getting daily issues:

**Check:**
1. Go to repo Settings → Notifications
2. Make sure you're watching the repo
3. Check email preferences

---

## 🎉 You're Live!

After completing these steps:

✅ Pipeline runs automatically every weekday at 6 PM ET
✅ Predictions generated and tracked automatically
✅ Win rate calculated daily
✅ GitHub Issues keep you updated
✅ Dashboard shows live performance (if deployed)

**No manual work required!**

Just check GitHub Issues daily to see:
- Latest predictions
- Win rate progress
- High-confidence opportunities

---

## 🚀 Next Actions:

**Right now:**
1. Push to GitHub (Step 1)
2. Add API key secret (Step 2)
3. Run workflow manually (Step 3)
4. Check Issues tab for first results!

**Tomorrow:**
- Wait for 6 PM ET
- Check for automatic GitHub Issue
- Review any high-confidence predictions

**This week:**
- Track first 5-10 predictions
- Get comfortable with system
- Watch win rate develop

**This month:**
- Collect 20-40 predictions
- Validate performance
- Decide on deployment strategy

---

**Total setup time: 5 minutes**
**Ongoing effort: 0 minutes (fully automated!)**

🎯 **Let's deploy it!** Push to GitHub now and you'll have your first results in minutes!
