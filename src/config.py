"""Project-wide settings: tickers, dates, paths and seeds."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"

PRICES_FILE = CLEAN_DIR / "prices.csv"
RISK_FREE_FILE = CLEAN_DIR / "risk_free.csv"
REPORT_FILE = CLEAN_DIR / "cleaning_report.json"
RAW_PRICES_FILE = RAW_DIR / "prices_raw.csv"
RAW_RISK_FREE_FILE = RAW_DIR / "risk_free_raw.csv"

TICKERS = ["SPY", "EFA", "EEM", "AGG", "GLD", "XLE", "XLK"]
BENCHMARK = "SPY"
RISK_FREE_SERIES = "DTB3"  # FRED 3-month T-bill, annualised percent

# GLD is the last of the seven to list (Nov 2004), so this is the common start
START_DATE = "2004-11-18"
# Fixed so a rerun gives the same data. Exclusive, so prices run to 27 Oct 2026
END_DATE = "2026-10-28"

# Periods the data must cover for the stress tests
STRESS_PERIODS = {
    "2008 financial crisis": ("2008-09-01", "2009-03-31"),
    "March 2020 Covid crash": ("2020-02-19", "2020-03-23"),
    "2022 rate hikes": ("2022-01-03", "2022-12-30"),
}

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
