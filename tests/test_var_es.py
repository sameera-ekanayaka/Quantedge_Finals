import numpy as np
import pandas as pd
import pytest

from src import config
from src.data import stub_returns
from src.portfolio import portfolio_returns
from src.var_es import var_es


@pytest.fixture
def sample_returns():
    returns_df = stub_returns(n_days=1000, seed=config.SEED)
    weights = np.full(returns_df.shape[1], 1.0 / returns_df.shape[1])
    return portfolio_returns(returns_df, weights)


def test_var_es_returns_positive_floats(sample_returns):
    for method in config.VAR_METHODS.keys():
        for alpha in [0.90, 0.95, 0.99]:
            var, es = var_es(sample_returns, alpha=alpha, method=method)
            assert isinstance(var, float)
            assert isinstance(es, float)
            # Both should be positive losses for realistic equity/bond portfolios
            assert var > 0.0
            assert es > 0.0
            # By definition, Expected Shortfall is strictly >= Value at Risk
            assert es >= var


def test_var_es_monotonicity_in_alpha(sample_returns):
    """Higher confidence level alpha must produce larger VaR and ES."""
    for method in config.VAR_METHODS.keys():
        var_90, es_90 = var_es(sample_returns, alpha=0.90, method=method)
        var_95, es_95 = var_es(sample_returns, alpha=0.95, method=method)
        var_99, es_99 = var_es(sample_returns, alpha=0.99, method=method)

        assert var_90 < var_95 < var_99
        assert es_90 < es_95 < es_99


def test_historical_known_distribution():
    """Test historical calculation against known exact empirical values."""
    # 100 values from -0.05 to +0.05 evenly spaced
    # Lowest 5 values are -0.050, -0.049, -0.048, -0.047, -0.046
    arr = np.linspace(-0.05, 0.05, 101)
    series = pd.Series(arr)
    var, es = var_es(series, alpha=0.95, method="historical")

    # 5% quantile is around -0.045
    assert var == pytest.approx(0.045, abs=1e-3)
    assert es >= var


def test_parametric_normal_known_analytical():
    """Verify parametric normal matches theoretical formula for standard normal."""
    # Standard normal mean=0, std=1
    rng = np.random.default_rng(123)
    series = pd.Series(rng.normal(loc=0.0, scale=0.02, size=100_000))

    var, es = var_es(series, alpha=0.95, method="normal", include_drift=False)
    # Theoretical normal VaR at 95% = 1.64485 * 0.02 = 0.032897
    expected_var = 1.6448536 * 0.02
    assert var == pytest.approx(expected_var, rel=1e-2)

    # Theoretical normal ES at 95% = sigma * phi(1.64485) / 0.05
    # = 0.02 * 0.103135 / 0.05 = 0.04125
    expected_es = 0.02 * (0.10313564 / 0.05)
    assert es == pytest.approx(expected_es, rel=1e-2)


def test_monte_carlo_reproducibility(sample_returns):
    """Monte Carlo with fixed seed must yield deterministic results."""
    var1, es1 = var_es(sample_returns, alpha=0.95, method="monte_carlo", seed=42)
    var2, es2 = var_es(sample_returns, alpha=0.95, method="monte_carlo", seed=42)
    assert var1 == var2
    assert es1 == es2


def test_invalid_inputs(sample_returns):
    with pytest.raises(ValueError, match="Confidence level"):
        var_es(sample_returns, alpha=1.05, method="historical")

    with pytest.raises(ValueError, match="Unknown method"):
        var_es(sample_returns, alpha=0.95, method="unsupported_method")

    with pytest.raises(ValueError, match="Insufficient data"):
        var_es(sample_returns.iloc[:10], alpha=0.95, method="historical")
