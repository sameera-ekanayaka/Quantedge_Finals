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


def test_final_construction_and_rounded_targets_meet_revised_policy():
    from src import config
    from src.advanced_validation import stress_vectors
    from src.portfolio import construct_final_portfolio, portfolio_returns
    from src.var_es import var_es

    returns = load_returns()
    solved = construct_final_portfolio(
        returns, annual_risk_free(load_risk_free(), returns.index)
    )
    assert np.allclose(solved, final_weights(), atol=0.0001)
    for weights in (solved, final_weights()):
        assert check_weights(weights)
        assert (
            stress_vectors(returns) @ weights >= -config.SCENARIO_LOSS_LIMIT - 1e-7
        ).all()
        v, e = var_es(portfolio_returns(returns, weights), 0.99, "historical")
        assert v <= config.DAILY_VAR_LIMIT + 1e-7
        assert e <= config.DAILY_ES_LIMIT + 1e-7
