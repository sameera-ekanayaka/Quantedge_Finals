import numpy as np
import pandas as pd

from src.portfolio import (
    TICKERS,
    final_weights,
    portfolio_returns,
    rebalanced_returns,
    rebalancing_comparison,
)


def make_returns() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    means = np.array([0.0004, 0.0003, 0.0004, 0.0001, 0.0002, 0.0003, 0.0005])
    vols = np.array([0.010, 0.011, 0.014, 0.003, 0.009, 0.015, 0.013])
    data = rng.normal(means, vols, size=(600, 7))
    index = pd.bdate_range("2020-01-01", periods=600)
    return pd.DataFrame(data, index=index, columns=TICKERS)


def test_single_asset_is_the_same_either_way():
    returns = make_returns()
    weights = pd.Series(0.0, index=TICKERS)
    weights["SPY"] = 1.0
    daily = portfolio_returns(returns, weights)
    quarterly = rebalanced_returns(returns, weights)
    assert np.allclose(daily, quarterly)


def test_first_day_of_each_quarter_matches_daily():
    returns = make_returns()
    weights = final_weights()
    daily = portfolio_returns(returns, weights)
    quarterly = rebalanced_returns(returns, weights)
    first_days = returns.groupby(returns.index.to_period("Q")).head(1).index
    assert np.allclose(daily.loc[first_days], quarterly.loc[first_days])


def test_same_dates_and_small_difference():
    returns = make_returns()
    weights = final_weights()
    daily = portfolio_returns(returns, weights)
    quarterly = rebalanced_returns(returns, weights)
    assert quarterly.index.equals(daily.index)
    assert abs(daily.sum() - quarterly.sum()) < 0.05


def test_comparison_table_shape():
    table = rebalancing_comparison(make_returns(), final_weights(), 0.02)
    assert table.shape == (2, 5)
    assert not table.isna().any().any()
