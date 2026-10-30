"""Tests for the minimum ES candidate."""

import numpy as np
import pandas as pd

from src.portfolio import (
    TICKERS,
    candidate_portfolios,
    check_weights,
    min_es,
    portfolio_es,
)


def make_returns() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    means = np.array([0.0004, 0.0003, 0.0004, 0.0001, 0.0002, 0.0003, 0.0005])
    vols = np.array([0.010, 0.011, 0.014, 0.003, 0.009, 0.015, 0.013])
    data = rng.normal(means, vols, size=(1000, 7))
    index = pd.bdate_range("2020-01-01", periods=1000)
    return pd.DataFrame(data, index=index, columns=TICKERS)


def test_min_es_follows_the_mandate():
    assert check_weights(min_es(make_returns()))


def test_min_es_has_the_lowest_es():
    returns = make_returns()
    best = portfolio_es(returns, min_es(returns))
    others = candidate_portfolios(returns, 0.02)
    for name in others.columns:
        assert best <= portfolio_es(returns, others[name]) + 5e-4
