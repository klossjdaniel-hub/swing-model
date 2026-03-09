"""
Database setup and connection management for swing-model.

Phase 1-2: SQLite (local)
Phase 3+: Can migrate to Supabase Postgres

Creates all tables with proper schema and indexes.
"""

import sqlite3
from pathlib import Path
import config

def get_connection():
    """Get a connection to the SQLite database."""
    db_path = Path(config.DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def create_tables():
    """Create all tables with proper schema and indexes."""
    conn = get_connection()
    cursor = conn.cursor()

    # Raw daily prices
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_ticker ON prices(ticker)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_date ON prices(date)")

    # VIX daily close
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vix (
            date TEXT PRIMARY KEY,
            close REAL NOT NULL
        )
    """)

    # Company metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_info (
            ticker TEXT PRIMARY KEY,
            name TEXT,
            sector TEXT,
            industry TEXT,
            market_cap REAL,
            market_cap_bucket TEXT,
            country TEXT,
            type TEXT,
            fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Raw earnings staging table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS earnings_raw (
            ticker TEXT NOT NULL,
            report_date TEXT NOT NULL,
            quarter INTEGER,
            year INTEGER,
            eps_estimate REAL,
            eps_actual REAL,
            revenue_estimate REAL,
            revenue_actual REAL,
            surprise_pct REAL,
            PRIMARY KEY (ticker, report_date)
        )
    """)

    # Labelled events
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            event_type TEXT NOT NULL,
            earnings_timing TEXT,
            timing_method TEXT,
            report_date TEXT,
            day0_date TEXT NOT NULL,
            sector TEXT,
            market_cap_bucket TEXT,

            -- Event characteristics (features)
            day0_return REAL,
            day0_return_abs REAL,
            direction INTEGER,
            volume_ratio REAL,
            eps_surprise_pct REAL,
            revenue_surprise_pct REAL,
            beat_miss TEXT,
            pre_earnings_drift_5d REAL,
            pre_earnings_drift_20d REAL,
            price_trend_5d REAL,
            price_trend_20d REAL,
            vix_day0 REAL,
            day_of_week INTEGER,
            days_since_prev_earnings INTEGER,

            -- Outcome labels
            return_day1 REAL,
            return_day2 REAL,
            return_day3 REAL,
            reverted_day1 INTEGER,
            reverted_day2 INTEGER,
            reverted_day3 INTEGER,
            reversion_magnitude_day2 REAL,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_sector ON events(sector)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_day0_date ON events(day0_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_ticker ON events(ticker)")

    # Forward test predictions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forward_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_timestamp TEXT NOT NULL,
            ticker TEXT NOT NULL,
            day0_date TEXT NOT NULL,
            predicted_direction INTEGER,
            reversion_prob_day2 REAL,
            reversion_prob_day3 REAL,
            confidence_tier TEXT,
            n_similar_events INTEGER,
            model_version TEXT,
            timing_option TEXT,

            -- Filled in after the fact
            actual_return_day1 REAL,
            actual_return_day2 REAL,
            actual_return_day3 REAL,
            actual_reverted_day2 INTEGER,
            actual_reverted_day3 INTEGER,
            scored_at TEXT
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_forward_ticker_date ON forward_predictions(ticker, day0_date)")

    # Experiment log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiment_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT DEFAULT CURRENT_TIMESTAMP,
            model_version TEXT,
            train_period TEXT,
            test_period TEXT,
            universe_size INTEGER,
            n_train_events INTEGER,
            n_test_events INTEGER,
            target TEXT,
            features_used TEXT,
            reversion_threshold REAL,
            baseline_accuracy REAL,
            model_accuracy REAL,
            model_auc REAL,
            model_f1 REAL,
            directional_accuracy REAL,
            notes TEXT,
            survivorship_bias_acknowledged INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()

    print("✓ All database tables created successfully")
    print(f"✓ Database location: {config.DB_PATH}")

if __name__ == "__main__":
    print("Creating database schema...")
    create_tables()
