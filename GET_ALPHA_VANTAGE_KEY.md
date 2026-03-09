# How to Get Your Free Alpha Vantage API Key

Alpha Vantage offers a completely free tier with 25 API calls per day - enough to fetch all 50 stocks over 2-3 days.

## Steps (2 minutes)

1. **Visit Alpha Vantage**
   - Go to: https://www.alphavantage.co/support/#api-key

2. **Enter Your Email**
   - Fill in your email address
   - No password needed!

3. **Click "GET FREE API KEY"**
   - Submit the form

4. **Check Your Email**
   - Alpha Vantage will send your API key immediately
   - Key looks like: `ABC123XYZ456...` (long string)

5. **Add to .env File**
   - Open `.env` file in this project
   - Find the line: `ALPHA_VANTAGE_API_KEY=`
   - Paste your key after the `=`
   - Example: `ALPHA_VANTAGE_API_KEY=ABC123XYZ456`
   - Save the file

## What You Get (Free Tier)

- ✅ 25 API calls per day
- ✅ Full historical earnings data (back to IPO)
- ✅ EPS estimates + actuals
- ✅ Surprise percentages
- ✅ No credit card required
- ✅ No expiration
- ✅ Unlimited history depth

## Timeline

- **Day 1:** Fetch 25 stocks (today)
- **Day 2:** Fetch 25 more stocks (tomorrow)
- **Done:** All 50 stocks fetched in 2 days

## Next Steps

Once you've added your API key to `.env`:

```bash
python data/fetch_earnings_alphavantage.py
```

The script will:
- Fetch up to 25 stocks per day
- Save progress automatically
- Resume where it left off tomorrow
- Take 15-second breaks between calls (rate limiting)

**Estimated time per run:** ~10 minutes (25 stocks × 15 sec + API time)

---

**Need Help?**
- Alpha Vantage Support: https://www.alphavantage.co/support/
- API Documentation: https://www.alphavantage.co/documentation/
