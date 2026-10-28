"""Value at Risk and Expected Shortfall: historical, parametric and Monte Carlo.

Owner: Aadhila Anees
"""

import pandas as pd


def var_es(returns: pd.Series, alpha: float, method: str) -> tuple[float, float]:
    """One-day VaR and ES at confidence alpha, both as positive loss numbers.

    method is one of the keys in config.VAR_METHODS.
    """
    raise NotImplementedError
