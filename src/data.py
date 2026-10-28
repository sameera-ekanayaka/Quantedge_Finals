"""Load cleaned prices, returns and the risk-free rate.

Owner: Sameera Ekanayaka
"""

import numpy as np
import pandas as pd

from src import config


def _read_clean_csv(path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"{path.name} not found in data/clean. Run the data download first, "
            "or use stub_returns() while the cleaned data is not committed yet."
        )
    return pd.read_csv(path, index_col=0, parse_dates=True).sort_index()


def load_prices() -> pd.DataFrame:
    """Adjusted close prices, indexed by date, one column per ticker."""
    prices = _read_clean_csv(config.PRICES_FILE)
    return prices[config.TICKERS]


def load_returns(prices: pd.DataFrame | None = None) -> pd.DataFrame:
    """Daily log returns, indexed by date, one column per ticker."""
    if prices is None:
        prices = load_prices()
    return np.log(prices).diff().dropna(how="all")


def load_risk_free() -> pd.Series:
    """Daily risk-free rate as a decimal, from the FRED 3-month T-bill."""
    rf = _read_clean_csv(config.RISK_FREE_FILE).iloc[:, 0]
    # DTB3 is an annualised percent
    return (rf / 100 / config.TRADING_DAYS).rename("risk_free")


def log_to_simple(log_returns: pd.DataFrame | pd.Series):
    """Convert log returns to simple returns."""
    return np.expm1(log_returns)


def stub_returns(n_days: int = 2500, seed: int = config.SEED) -> pd.DataFrame:
    """Random fat-tailed log returns with the same shape as load_returns().

    For building and testing modules before the real data is in. Never use
    these numbers in the report.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(config.START_DATE, periods=n_days)
    daily_vol = 0.01
    # Student t with 4 dof, scaled so the standard deviation is daily_vol
    draws = rng.standard_t(df=4, size=(n_days, len(config.TICKERS)))
    values = draws * daily_vol / np.sqrt(4 / (4 - 2))
    return pd.DataFrame(values, index=dates, columns=config.TICKERS)
