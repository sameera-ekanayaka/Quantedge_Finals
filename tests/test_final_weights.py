"""Tests for the frozen final portfolio weights."""

import numpy as np

from src.data import load_returns, load_risk_free
from src.portfolio import (
    TICKERS,
    annual_risk_free,
    candidate_portfolios,
    check_weights,
    final_weights,
)


def test_final_weights_follow_the_mandate():
    weights = final_weights()
    assert list(weights.index) == TICKERS
    assert check_weights(weights)


def test_final_weights_match_max_sharpe_on_real_data():
    returns = load_returns()
    rf = annual_risk_free(load_risk_free(), returns.index)
    best = candidate_portfolios(returns, rf)["Maximum Sharpe"]
    assert np.allclose(final_weights(), best, atol=1e-3)
