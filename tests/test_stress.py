import numpy as np
import pandas as pd
import pytest

from src import config, stress
from src.data import stub_returns


def two_asset_returns() -> pd.DataFrame:
    # A falls 10% then rises 10%; B is flat
    index = pd.bdate_range("2020-01-01", periods=4)
    return pd.DataFrame(
        {
            "A": [0.0, np.log(0.9), np.log(1.1), 0.0],
            "B": [0.0, 0.0, 0.0, 0.0],
        },
        index=index,
    )


def test_asset_period_returns_compound_log_returns():
    out = stress.asset_period_returns(two_asset_returns(), "2020-01-02", "2020-01-03")
    assert out["A"] == pytest.approx(0.9 * 1.1 - 1)
    assert out["B"] == pytest.approx(0.0)


def test_portfolio_path_is_buy_and_hold():
    path = stress.portfolio_path(
        two_asset_returns(), [0.5, 0.5], "2020-01-02", "2020-01-03"
    )
    assert path.iloc[0] == 1.0
    assert path.index[0] == pd.Timestamp("2020-01-01")
    assert path.iloc[1] == pytest.approx(0.95)
    # Buy and hold: A's 10% rise is on its drifted weight, 0.5 * 0.99 + 0.5
    assert path.iloc[-1] == pytest.approx(0.995)


def test_contributions_add_up_to_the_replay_return():
    returns = stub_returns(n_days=300)
    weights = np.full(7, 1 / 7)
    start, end = "2005-03-01", "2005-06-30"
    total = stress.replay(returns, weights, start, end)["return"]
    assert stress.contributions(returns, weights, start, end).sum() == pytest.approx(
        total
    )


def test_replay_reports_drawdown_and_worst_day():
    result = stress.replay(two_asset_returns(), [0.5, 0.5], "2020-01-02", "2020-01-03")
    assert result["max_drawdown"] == pytest.approx(-0.05)
    assert result["worst_day"] == pytest.approx(-0.05)
    assert result["worst_day_date"] == "2020-01-02"
    assert result["pnl_usd"] == pytest.approx(
        result["return"] * config.PORTFOLIO_VALUE_USD
    )


def test_replay_rejects_empty_period():
    with pytest.raises(ValueError, match="No returns"):
        stress.replay(two_asset_returns(), [0.5, 0.5], "2030-01-01", "2030-02-01")


def test_hypothetical_is_weighted_sum_of_shocks():
    weights = pd.Series(1 / 7, index=config.TICKERS)
    result = stress.hypothetical(weights, stress.INFLATION_SHOCK)
    assert result["return"] == pytest.approx(
        np.mean(list(stress.INFLATION_SHOCK.values()))
    )


def test_inflation_shock_has_bonds_and_stocks_falling_together():
    shock = stress.INFLATION_SHOCK
    assert set(shock) == set(config.TICKERS)
    assert shock["AGG"] < 0 and shock["SPY"] < 0
    assert set(stress.INFLATION_SHOCK_REASONS) == set(shock)


def test_stress_table_on_stub_data_has_every_scenario():
    returns = stub_returns(n_days=1300)
    periods = {
        "early": ("2005-02-01", "2005-03-31"),
        "later": ("2008-01-02", "2008-06-30"),
    }
    table = stress.stress_table(returns, np.full(7, 1 / 7), periods)
    assert list(table.index) == ["early", "later", *stress.HYPOTHETICAL_SCENARIOS]
    assert table["type"].iloc[-1] == "Hypothetical (assumption)"


def test_stress_across_candidates_shape():
    returns = stub_returns(n_days=1300)
    candidates = pd.DataFrame(
        {"Equal": np.full(7, 1 / 7), "All SPY": np.eye(7)[0]}, index=config.TICKERS
    )
    periods = {"early": ("2005-02-01", "2005-03-31")}
    table = stress.stress_across_candidates(returns, candidates, periods)
    assert table.shape == (1 + len(stress.HYPOTHETICAL_SCENARIOS), 2)
    assert table.loc["early", "All SPY"] == pytest.approx(
        stress.asset_period_returns(returns, "2005-02-01", "2005-03-31")["SPY"]
    )


def test_reverse_stress_multiple():
    weights = pd.Series(1 / 7, index=config.TICKERS)
    loss = -stress.hypothetical(weights, stress.INFLATION_SHOCK)["return"]
    assert stress.reverse_stress(
        weights, stress.INFLATION_SHOCK, loss
    ) == pytest.approx(1.0)
    assert stress.reverse_stress(
        weights, stress.INFLATION_SHOCK, loss / 2
    ) == pytest.approx(0.5)


def test_reverse_stress_when_scenario_gains():
    shocks = dict.fromkeys(config.TICKERS, 0.05)
    assert stress.reverse_stress(np.full(7, 1 / 7), shocks, 0.1) == float("inf")


def test_weights_must_sum_to_one():
    with pytest.raises(ValueError):
        stress.hypothetical([0.5] * 7, stress.INFLATION_SHOCK)
