"""Portfolio construction: efficient frontier and candidate portfolios.

Owner: Imasha Karunathilaka
"""

import numpy as np
import pandas as pd

from src.data import log_to_simple


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
