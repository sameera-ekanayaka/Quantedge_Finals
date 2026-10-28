"""Portfolio construction: efficient frontier and candidate portfolios.

Owner: Imasha Karunathilaka
"""

import numpy as np
import pandas as pd

from src.data import log_to_simple

TICKERS = ["SPY", "EFA", "EEM", "AGG", "GLD", "XLE", "XLK"]

# Proposed mandate: (minimum weight, maximum weight) for each ETF
BOUNDS = {
    "SPY": (0.00, 0.40),
    "EFA": (0.00, 0.30),
    "EEM": (0.00, 0.10),
    "AGG": (0.30, 0.60),
    "GLD": (0.00, 0.15),
    "XLE": (0.00, 0.10),
    "XLK": (0.00, 0.15),
}


def portfolio_returns(returns: pd.DataFrame, weights) -> pd.Series:
    """Daily simple portfolio returns from asset log returns and weights.

    Simple returns are used here because they add up across assets and log
    returns do not. Weights are held fixed, i.e. rebalanced daily.
    """
    w = pd.Series(weights, index=returns.columns, dtype=float)
    if not np.isclose(w.sum(), 1.0):
        raise ValueError(f"Weights must sum to 1, got {w.sum():.4f}")
    simple = log_to_simple(returns)
    return (simple @ w).rename("portfolio")


def get_bounds() -> list[tuple[float, float]]:
    """Return the weight limits in ticker order, ready for scipy.optimize."""
    return [BOUNDS[t] for t in TICKERS]


def check_weights(weights: pd.Series, tol: float = 1e-6) -> bool:
    """Return True if weights sum to 1 and respect every mandate limit."""
    if abs(weights.sum() - 1.0) > tol:
        return False
    for ticker, (low, high) in BOUNDS.items():
        if weights[ticker] < low - tol or weights[ticker] > high + tol:
            return False
    return True
