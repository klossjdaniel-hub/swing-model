# Swing Trade Prediction Model

A data-driven model that predicts stock price behavior in the 2-3 trading days following significant earnings events.

**Purpose**: Build a credible, data-driven track record for Invstify content. Trading profits are secondary — the primary value is differentiated tweet content and brand positioning.

## Project Status

**Current Phase**: Phase 1 - Data Pipeline Setup

## Tech Stack

- **Data Sources**: Finnhub (earnings), Eulerpool/yfinance (prices), yfinance (VIX)
- **Database**: SQLite (Phase 1-2), Supabase Postgres (Phase 3+)
- **Automation**: GitHub Actions (2,000 min/month free)
- **Machine Learning**: scikit-learn, XGBoost
- **Cost**: £0 (all free tiers)

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-username/swing-model.git
cd swing-model
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required keys:
- `FINNHUB_API_KEY` - Get free key at https://finnhub.io
- `SUPABASE_URL` - Your Invstify Supabase URL (Phase 3+)
- `SUPABASE_KEY` - Your Invstify Supabase key (Phase 3+)

Optional keys:
- `EULERPOOL_API_KEY` - Get free key at https://eulerpool.com (Phase 3+)
- `DATABENTO_API_KEY` - $125 free credit at https://databento.com (Phase 1 optional)

### 4. Run Phase 1 - Data Pipeline

```bash
# Pull VIX data (smoke test)
python data/fetch_vix.py

# Pull company metadata from Finnhub
python data/fetch_company_info.py

# Pull earnings data from Finnhub
python data/fetch_earnings.py

# Pull 5 years of historical prices (yfinance)
python data/fetch_prices.py

# Build events dataset
python data/build_events.py

# Validate dataset
python data/validate_dataset.py
```

## Project Structure

```
swing-model/
├── .github/workflows/       # GitHub Actions (Phase 3)
├── data/                    # Data fetching scripts
├── model/                   # ML model code
├── scripts/                 # Production scripts (Phase 3)
├── tests/                   # Unit tests
├── logs/                    # Weekly review logs
├── config.py                # Configuration
├── universe.py              # Stock universe definition
└── main.py                  # Entry point
```

## Phases

### Phase 1: Data Pipeline (Current)
Build a clean, labeled dataset of earnings events and price movements.

**Deliverable**: SQLite database with `prices`, `vix`, `company_info`, `earnings_raw`, and `events` tables.

### Phase 2: Backtesting and Modeling
Train models (Logistic Regression, XGBoost) using walk-forward validation. Evaluate against naive baselines.

**Deliverable**: Trained model with documented performance metrics.

### Phase 3: Forward Validation (Paper Trading)
Run daily predictions via GitHub Actions, log to Supabase, track accuracy over 8+ weeks.

**Deliverable**: Credible track record of predictions timestamped before market open.

### Phase 4: Output Layer
Add `/swing-signals` page to invstify.com showing top predictions and track record.

**Deliverable**: Public-facing signals page integrated with Invstify.

## Documentation

Full PRD: See `PRD-v3-FINAL.md`

## License

Private project for Invstify.com
