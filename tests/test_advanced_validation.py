import numpy as np
import pandas as pd
import pytest

from src.advanced_validation import (
    alternative_threshold,
    conditional_backtests,
    constrained_sharpe,
    evt_bootstrap,
    joint_bootstrap_risk,
    stress_vectors,
)
from src.data import load_returns, load_risk_free
from src.portfolio import (
    TICKERS,
    annual_risk_free,
    check_weights,
    final_weights,
    portfolio_returns,
)
from src.var_es import var_es


def test_risk_constrained_solution_enforces_all_limits():
    r = load_returns()
    w = constrained_sharpe(r, annual_risk_free(load_risk_free(), r.index))
    assert check_weights(w)
    assert (stress_vectors(r) @ w >= -0.15 - 1e-7).all()
    v, e = var_es(portfolio_returns(r, w), 0.99, "historical")
    assert v <= 0.015 + 1e-7
    assert e <= 0.02 + 1e-7
    assert not np.allclose(w, final_weights())
    with pytest.raises(ValueError, match="infeasible"):
        constrained_sharpe(r, 0.02, stress_limit=0.01)


def test_joint_bootstrap_preserves_cross_asset_hedge():
    rng = np.random.default_rng(7)
    simple = rng.uniform(-0.03, 0.03, 1000)
    r = pd.DataFrame(0.0, index=range(1000), columns=TICKERS)
    r["SPY"] = np.log1p(simple)
    r["AGG"] = np.log1p(-simple)
    w = pd.Series(0.0, index=TICKERS)
    w["SPY"] = w["AGG"] = 0.5
    v, e = joint_bootstrap_risk(r, w)
    assert abs(v) < 1e-12
    assert abs(e) < 1e-12


def test_conditional_forecasts_are_prefix_invariant():
    rng = np.random.default_rng(42)
    r = pd.Series(
        rng.normal(0.0002, 0.01, 670), index=pd.bdate_range("2010-01-01", periods=670)
    )
    first, _ = conditional_backtests(r.iloc[:650], window=500)
    changed = r.copy()
    changed.iloc[650:] = -0.15
    second, _ = conditional_backtests(changed, window=500)
    for name in first:
        pd.testing.assert_frame_equal(first[name], second[name].iloc[:150])
        assert (first[name]["es"] >= first[name]["var"]).all()
        assert first[name]["var"].nunique() > 100


def test_threshold_rule_and_bootstrap_are_reproducible():
    r = -portfolio_returns(load_returns(), final_weights())
    u, table = alternative_threshold(r)
    best = table.loc[table["KS distance"].idxmin()]
    assert u == best["Threshold"]
    ci = evt_bootstrap(r, repeats=20)
    assert (ci["97.5%"] >= ci["2.5%"]).all()
    assert ci["Valid replicates"].iloc[0] + ci["Failed replicates"].iloc[0] == 20
    pd.testing.assert_frame_equal(ci, evt_bootstrap(r, repeats=20))
