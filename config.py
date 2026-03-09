"""
Configuration and environment setup for swing-model.

Loads API keys from environment variables and defines project paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Database paths
DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "swing_model.db"))

# API Keys
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
EULERPOOL_API_KEY = os.getenv("EULERPOOL_API_KEY")
DATABENTO_API_KEY = os.getenv("DATABENTO_API_KEY")

# Supabase (Phase 3+)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Optional: Alpaca for after-hours data (Phase 3+)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# Validation
def validate_config(phase="phase1"):
    """Validate that required API keys are set for the given phase."""
    missing_keys = []

    if phase in ["phase1", "phase2"]:
        if not FINNHUB_API_KEY:
            missing_keys.append("FINNHUB_API_KEY")

    if phase in ["phase3", "phase4"]:
        if not FINNHUB_API_KEY:
            missing_keys.append("FINNHUB_API_KEY")
        if not SUPABASE_URL:
            missing_keys.append("SUPABASE_URL")
        if not SUPABASE_KEY:
            missing_keys.append("SUPABASE_KEY")

    if missing_keys:
        raise ValueError(
            f"Missing required environment variables for {phase}: {', '.join(missing_keys)}\n"
            "Please set them in your .env file (see .env.example)"
        )

    print(f"✓ Configuration validated for {phase}")

# Constants
START_DATE = "2020-01-01"  # 5 years of historical data
REVERSION_THRESHOLD = 0.30  # 30% reversion threshold (configurable)
MIN_EVENT_MOVE = 0.02  # Minimum 2% move to qualify as event
