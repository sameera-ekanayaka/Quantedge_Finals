"""Tests for risk shares and the trade-off table."""

import numpy as np
import pandas as pd

from src.portfolio import (
    TICKERS,
    candidate_portfolios,
    candidate_risk_shares,
    candidate_tradeoffs,
    risk_shares,
)


def make_returns() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    means = np.array([0.0004, 0.0003, 0.0004, 0.0001, 0.0002, 0.0003, 0.0005])
    vols = np.array([0.010, 0.011, 0.014, 0.003, 0.009, 0.015, 0.013])
    data = rng.normal(means, vols, size=(1000, 7))
    index = pd.bdate_range("2020-01-01", periods=1000)
    return pd.DataFrame(data, index=index, columns=TICKERS)


def test_equal_risk_for_identical_assets():
    cov = pd.DataFrame(np.diag([0.04, 0.04]), index=["A", "B"], columns=["A", "B"])
    shares = risk_shares(pd.Series([0.5, 0.5], index=["A", "B"]), cov)
    assert np.allclose(shares, [0.5, 0.5])


def test_risk_shares_add_up_to_one():
    returns = make_returns()
    weights = candidate_portfolios(returns, 0.02)
    shares = candidate_risk_shares(returns, weights)
    assert np.allclose(shares.sum(), 1.0)


def test_tradeoff_table_shape_and_signs():
    returns = make_returns()
    weights = candidate_portfolios(returns, 0.02)
    table = candidate_tradeoffs(returns, weights)
    assert table.shape == (4, 4)
    assert (table["Max drawdown"] <= 0).all()
    assert (table["Worst day"] < 0).all()
