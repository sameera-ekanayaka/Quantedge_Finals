"""Tests for candidate portfolios and the efficient frontier."""

import numpy as np
import pandas as pd

from src.portfolio import (
    TICKERS,
    asset_stats,
    candidate_kpis,
    candidate_portfolios,
    check_weights,
    efficient_frontier,
    max_sharpe,
    min_variance,
)


def make_returns() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    means = np.array([0.0004, 0.0003, 0.0004, 0.0001, 0.0002, 0.0003, 0.0005])
    vols = np.array([0.010, 0.011, 0.014, 0.003, 0.009, 0.015, 0.013])
    data = rng.normal(means, vols, size=(1000, 7))
    index = pd.bdate_range("2020-01-01", periods=1000)
    return pd.DataFrame(data, index=index, columns=TICKERS)


def test_every_candidate_follows_the_mandate():
    weights = candidate_portfolios(make_returns(), 0.02)
    for name in weights.columns:
        assert check_weights(weights[name]), name


def test_min_variance_has_the_lowest_risk():
    returns = make_returns()
    _, cov = asset_stats(returns)
    weights = candidate_portfolios(returns, 0.02)
    risk = {}
    for name in weights.columns:
        w = weights[name].to_numpy()
        risk[name] = float(w @ cov.to_numpy() @ w)
    assert risk["Minimum variance"] <= min(risk.values()) + 1e-9


def test_max_sharpe_beats_min_variance_on_sharpe():
    mu, cov = asset_stats(make_returns())
    rf = 0.02

    def sharpe(w: pd.Series) -> float:
        v = w.to_numpy()
        return float((mu.to_numpy() @ v - rf) / np.sqrt(v @ cov.to_numpy() @ v))

    assert sharpe(max_sharpe(mu, cov, rf)) >= sharpe(min_variance(cov)) - 1e-9


def test_frontier_is_valid_and_rising():
    mu, cov = asset_stats(make_returns())
    frontier = efficient_frontier(mu, cov, n_points=10)
    assert len(frontier) == 10
    assert frontier["Return"].is_monotonic_increasing
    for _, row in frontier.iterrows():
        assert check_weights(row[TICKERS].astype(float))


def test_candidate_kpis_shape():
    returns = make_returns()
    weights = candidate_portfolios(returns, 0.02)
    table = candidate_kpis(returns, weights, 0.02)
    assert table.shape == (10, 4)
