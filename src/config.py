"""Project-wide settings: tickers, dates, paths and seeds."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"

PRICES_FILE = CLEAN_DIR / "prices.csv"
RISK_FREE_FILE = CLEAN_DIR / "risk_free.csv"

TICKERS = ["SPY", "EFA", "EEM", "AGG", "GLD", "XLE", "XLK"]
BENCHMARK = "SPY"
RISK_FREE_SERIES = "DTB3"  # FRED 3-month T-bill, annualised percent

# GLD is the last of the seven to list (Nov 2004), so this is the common start
START_DATE = "2004-11-18"

PORTFOLIO_VALUE_USD = 10_000_000
TRADING_DAYS = 252
CONFIDENCE_LEVELS = [0.90, 0.95, 0.99]
SEED = 42

# Keys are what src/ functions take, values are what the sidebar shows
VAR_METHODS = {
    "historical": "Historical simulation",
    "normal": "Parametric (normal)",
    "student_t": "Parametric (Student t)",
    "monte_carlo": "Monte Carlo",
}

DEFAULT_BACKTEST_START = "2008-01-01"
