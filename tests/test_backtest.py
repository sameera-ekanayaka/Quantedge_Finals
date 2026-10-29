import math

import numpy as np
import pandas as pd
import pytest

from src import backtest
from src.data import stub_returns
from src.portfolio import portfolio_returns


@pytest.fixture
def port_returns():
    returns = stub_returns(n_days=800)
    weights = np.full(returns.shape[1], 1 / returns.shape[1])
    return portfolio_returns(returns, weights)


def constant_model(var: float, es: float):
    return lambda window, alpha: (var, es)


def test_rolling_backtest_shape_and_columns(port_returns):
    results = backtest.rolling_backtest(
        port_returns, backtest.make_model("historical"), 0.95, window=250
    )
    assert len(results) == len(port_returns) - 250
    assert list(results.columns) == ["return", "var", "es", "breach"]
    assert results.index[0] == port_returns.index[250]
    assert (results["es"] >= results["var"]).all()


def test_rolling_backtest_is_out_of_sample():
    # A crash on the first forecast day must not be in its own window
    returns = pd.Series(np.full(100, 0.001))
    returns.iloc[50] = -0.5
    seen = []

    def spy_model(window, alpha):
        seen.append(window.min())
        return 0.01, 0.02

    results = backtest.rolling_backtest(returns, spy_model, 0.99, window=50)
    assert seen[0] == pytest.approx(0.001)
    assert bool(results["breach"].iloc[0])


def test_breach_flag_uses_loss_above_var():
    returns = pd.Series([0.0] * 30 + [-0.02, -0.005, 0.01])
    results = backtest.rolling_backtest(
        returns, constant_model(0.01, 0.015), 0.99, window=30
    )
    assert results["breach"].tolist() == [True, False, False]


def test_refit_every_holds_the_forecast(port_returns):
    calls = []

    def counting_model(window, alpha):
        calls.append(1)
        return float(-window.min()), float(-window.min())

    results = backtest.rolling_backtest(
        port_returns, counting_model, 0.99, window=500, refit_every=5
    )
    assert len(calls) == math.ceil(len(results) / 5)
    assert results["var"].iloc[0] == results["var"].iloc[4]


def test_rolling_backtest_rejects_short_series(port_returns):
    with pytest.raises(ValueError):
        backtest.rolling_backtest(
            port_returns.iloc[:100], constant_model(0.01, 0.02), 0.99, window=250
        )


def test_kupiec_zero_when_breaches_match_expectation():
    result = backtest.kupiec_test(breaches=10, days=1000, alpha=0.99)
    assert result["lr"] == pytest.approx(0.0, abs=1e-10)
    assert result["p_value"] == pytest.approx(1.0)


def test_kupiec_known_value():
    n, x, p = 250, 10, 0.01
    expected = -2 * (
        (n - x) * math.log(1 - p)
        + x * math.log(p)
        - (n - x) * math.log(1 - x / n)
        - x * math.log(x / n)
    )
    result = backtest.kupiec_test(x, n, 0.99)
    assert result["lr"] == pytest.approx(expected)
    assert result["p_value"] < 0.01


def test_kupiec_handles_zero_breaches():
    result = backtest.kupiec_test(0, 250, 0.99)
    # Only the null term remains: -2 * 250 * ln(0.99)
    assert result["lr"] == pytest.approx(-2 * 250 * math.log(0.99))
    assert np.isfinite(result["p_value"])


def test_christoffersen_flags_clustered_breaches():
    spread = np.zeros(1000, dtype=bool)
    spread[::100] = True
    clustered = np.zeros(1000, dtype=bool)
    clustered[500:510] = True
    assert backtest.christoffersen_test(spread, 0.99)["p_value_ind"] > 0.5
    assert backtest.christoffersen_test(clustered, 0.99)["p_value_ind"] < 0.001


def test_christoffersen_transition_counts():
    result = backtest.christoffersen_test(np.array([0, 1, 1, 0, 0, 1]), 0.9)
    assert (result["n00"], result["n01"], result["n10"], result["n11"]) == (
        1,
        2,
        1,
        1,
    )
    assert result["lr_cc"] == pytest.approx(
        result["lr_ind"] + backtest.kupiec_test(3, 6, 0.9)["lr"]
    )


@pytest.mark.parametrize(
    "breaches, zone", [(0, "green"), (4, "green"), (5, "yellow"), (9, "yellow")]
)
def test_basel_zones_for_250_days(breaches, zone):
    assert backtest.traffic_light(breaches, 250, 0.99) == zone


def test_basel_red_zone():
    assert backtest.traffic_light(10, 250, 0.99) == "red"


def test_binomial_rule_matches_official_zones_at_250_days():
    # The rule used for other sample lengths should reproduce the Basel table
    for breaches in range(15):
        official = backtest.traffic_light(breaches, 250, 0.99)
        rule = backtest.traffic_light(breaches, 251, 0.99)
        assert official == rule, breaches


def test_traffic_light_only_at_99():
    assert backtest.traffic_light(3, 250, 0.95) == "n/a"


def test_basel_multiplier():
    assert backtest.basel_multiplier(2) == 3.0
    assert backtest.basel_multiplier(7) == pytest.approx(3.65)
    assert backtest.basel_multiplier(12) == 4.0


def test_es_backtest_near_zero_when_es_is_right():
    # Breaches exactly 1% of the time, each loss equal to the forecast ES
    n = 1000
    returns = np.zeros(n)
    returns[::100] = -0.03
    results = pd.DataFrame(
        {"return": returns, "var": 0.02, "es": 0.03, "breach": returns < -0.02}
    )
    out = backtest.es_backtest(results, 0.99)
    assert out["z2"] == pytest.approx(0.0, abs=1e-12)
    assert out["loss_to_es"] == pytest.approx(1.0)
    assert out["zone"] == "green"


def test_backtest_by_period_splits_calm_and_stressed():
    index = pd.bdate_range("2019-12-02", "2020-06-30")
    results = pd.DataFrame(
        {"return": 0.0, "var": 0.01, "es": 0.02, "breach": False}, index=index
    )
    table = backtest.backtest_by_period(
        results, 0.99, {"Covid": ("2020-02-19", "2020-03-23")}
    )
    assert table.loc["Full sample", "days"] == len(index)
    assert table.loc["Covid", "days"] + table.loc[
        "Calm days (outside stress periods)", "days"
    ] == len(index)


def test_summarise_keys(port_returns):
    results = backtest.rolling_backtest(
        port_returns, backtest.make_model("normal"), 0.99, window=250
    )
    summary = backtest.summarise(results, 0.99)
    assert summary["days"] == len(results)
    assert summary["zone_last_250"] in {"green", "yellow", "red"}
    assert 0 <= summary["kupiec_p"] <= 1


@pytest.mark.parametrize("method", ["historical", "normal", "student_t", "monte_carlo"])
def test_every_var_method_runs_in_the_backtest(port_returns, method):
    results = backtest.rolling_backtest(
        port_returns.iloc[:320],
        backtest.make_model(method),
        0.99,
        window=300,
        refit_every=10,
    )
    assert results["var"].gt(0).all()


def test_make_model_rejects_unknown_method():
    with pytest.raises(ValueError):
        backtest.make_model("garch")
