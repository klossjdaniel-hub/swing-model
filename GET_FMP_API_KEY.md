# How to Get Your Free FMP API Key

Financial Modeling Prep offers a completely free tier with 250 API calls per day - more than enough for our needs.

## Steps to Get API Key (2 minutes)

1. **Visit FMP Website**
   - Go to: https://site.financialmodelingprep.com/developer/docs

2. **Click "Get your Free API Key"**
   - Usually a big button on the top of the page

3. **Sign Up**
   - Enter your email
   - Create a password
   - **No credit card required!**

4. **Verify Email**
   - Check your inbox for verification email
   - Click the verification link

5. **Get Your API Key**
   - Log in to your FMP dashboard
   - Copy your API key (long string like: `abc123def456...`)

6. **Add to .env File**
   - Open `.env` file in this project
   - Find the line: `FMP_API_KEY=`
   - Paste your key after the `=`
   - Example: `FMP_API_KEY=abc123def456ghi789`
   - Save the file

## What You Get (Free Tier)

- ✅ 250 API calls per day
- ✅ 5 years of historical earnings data
- ✅ EPS estimates + actuals
- ✅ Revenue estimates + actuals
- ✅ No credit card required
- ✅ No expiration

## Next Steps

Once you've added your API key to `.env`:

```bash
python data/fetch_earnings_fmp.py
```

This will fetch 5 years of earnings data for all 50 stocks (~10 minutes).

---

**Need Help?**
- FMP Documentation: https://site.financialmodelingprep.com/developer/docs
- FMP Support: Usually responds within 24 hours
