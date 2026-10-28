"""Extreme value theory: peaks over threshold with a GPD fit.

Owner: Praveen Madawalage
"""

import pandas as pd


def evt_var_es(
    losses: pd.Series, alpha: float, threshold: float
) -> tuple[float, float, dict]:
    """VaR, ES and the fitted GPD parameters for losses above threshold."""
    raise NotImplementedError
