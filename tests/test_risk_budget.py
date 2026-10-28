import numpy as np
import pandas as pd
import pytest

from src import config
from src.data import stub_returns
from src.portfolio import portfolio_returns
from src.risk_budget import risk_budget
from src.var_es import var_es


@pytest.fixture
def returns_df():
    return stub_returns(n_days=1000, seed=config.SEED)


@pytest.fixture
def equal_weights(returns_df):
    n = returns_df.shape[1]
    return pd.Series(np.full(n, 1.0 / n), index=returns_df.columns)


def test_parametric_euler_decomposition(returns_df, equal_weights):
    """Component VaR and ES must sum exactly to portfolio VaR and ES."""
    alpha = 0.95
    df = risk_budget(returns_df, equal_weights, alpha=alpha, method="parametric")

    # Verify columns exist
    expected_cols = [
        "weight",
        "marginal_var",
        "component_var",
        "pct_var_contrib",
        "marginal_es",
        "component_es",
        "pct_es_contrib",
    ]
    for col in expected_cols:
        assert col in df.columns

    # Percentage contributions must sum to 1.0 (100%)
    assert df["pct_var_contrib"].sum() == pytest.approx(1.0, abs=1e-5)
    assert df["pct_es_contrib"].sum() == pytest.approx(1.0, abs=1e-5)

    # Compare component sum with portfolio var_es
    port_ret = portfolio_returns(returns_df, equal_weights)
    port_var, port_es = var_es(port_ret, alpha=alpha, method="normal")

    assert df["component_var"].sum() == pytest.approx(port_var, rel=1e-3)
    assert df["component_es"].sum() == pytest.approx(port_es, rel=1e-3)


def test_historical_euler_decomposition(returns_df, equal_weights):
    """Historical Component ES must sum exactly to portfolio ES."""
    alpha = 0.95
    df = risk_budget(returns_df, equal_weights, alpha=alpha, method="historical")

    # Percentage contributions must sum to 1.0 (100%)
    assert df["pct_es_contrib"].sum() == pytest.approx(1.0, abs=1e-5)

    port_ret = portfolio_returns(returns_df, equal_weights)
    _, port_es = var_es(port_ret, alpha=alpha, method="historical")

    assert df["component_es"].sum() == pytest.approx(port_es, rel=1e-3)


def test_invalid_weights_sum(returns_df):
    bad_weights = [0.5, 0.6] + [0.0] * (returns_df.shape[1] - 2)
    with pytest.raises(ValueError, match="Weights must sum to 1"):
        risk_budget(returns_df, bad_weights, method="parametric")


def test_invalid_method(returns_df, equal_weights):
    with pytest.raises(ValueError, match="Unknown method"):
        risk_budget(returns_df, equal_weights, method="invalid_method")
