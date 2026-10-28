"""VaR backtesting: rolling forecasts, Kupiec, Christoffersen, Basel traffic light.

Owner: Tharindu Dhanushka
"""

from collections.abc import Callable

import pandas as pd


def rolling_backtest(
    returns: pd.Series, model: Callable, alpha: float, window: int
) -> pd.DataFrame:
    """Out-of-sample VaR forecasts and a breach flag for each day."""
    raise NotImplementedError
