import numpy as np
import pandas as pd
import pytest
from scipy import stats

from src import config
from src.data import stub_returns
from src.evt import (
    evt_var_es,
    fit_gpd,
    gpd_qq_data,
    mean_excess_plot_data,
    parameter_stability_plot_data,
    select_threshold,
)
from src.portfolio import portfolio_returns


@pytest.fixture
def sample_losses():
    returns_df = stub_returns(n_days=1000, seed=config.SEED)
    weights = np.full(returns_df.shape[1], 1.0 / returns_df.shape[1])
    port_ret = portfolio_returns(returns_df, weights)
    return -port_ret


def test_fit_gpd_known_distribution():
    """Verify GPD fit recovers known synthetic shape and scale."""
    true_xi = 0.20
    true_sigma = 0.015
    rng = np.random.default_rng(config.SEED)
    synthetic = stats.genpareto.rvs(
        c=true_xi, scale=true_sigma, size=3000, random_state=rng
    )

    fitted_xi, fitted_sigma = fit_gpd(synthetic)
    assert fitted_xi == pytest.approx(true_xi, abs=0.04)
    assert fitted_sigma == pytest.approx(true_sigma, abs=0.003)


def test_fit_gpd_insufficient_exceedances():
    with pytest.raises(ValueError, match="Need at least 10 exceedances"):
        fit_gpd(np.array([0.01, 0.02, 0.03]))


def test_mean_excess_plot_data(sample_losses):
    df = mean_excess_plot_data(sample_losses, n_points=20)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = [
        "threshold",
        "mean_excess",
        "std_error",
        "ci_lower",
        "ci_upper",
        "n_exceedances",
    ]
    for col in expected_cols:
        assert col in df.columns
    # Thresholds must be strictly increasing
    assert (df["threshold"].diff().dropna() > 0).all()
    # Number of exceedances must decrease as threshold increases
    assert (df["n_exceedances"].diff().dropna() <= 0).all()


def test_parameter_stability_plot_data(sample_losses):
    df = parameter_stability_plot_data(sample_losses, n_points=15)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = [
        "threshold",
        "shape_xi",
        "scale_sigma",
        "modified_scale",
        "shape_se",
        "n_exceedances",
    ]
    for col in expected_cols:
        assert col in df.columns
    assert (df["scale_sigma"] > 0).all()


def test_gpd_qq_data(sample_losses):
    u = float(np.quantile(sample_losses, 0.90))
    exceed = sample_losses[sample_losses > u] - u
    xi, sigma = fit_gpd(exceed)

    theo, emp = gpd_qq_data(sample_losses, threshold=u, xi=xi, sigma=sigma)
    assert len(theo) == len(emp) == len(exceed)
    assert (np.diff(theo) >= 0).all()
    assert (np.diff(emp) >= 0).all()


def test_select_threshold(sample_losses):
    chosen, reason, comp = select_threshold(sample_losses, target_quantile=0.90)
    assert isinstance(chosen, float)
    assert isinstance(reason, str)
    assert comp["chosen_threshold"] == pytest.approx(
        float(np.quantile(sample_losses, 0.90))
    )
    assert comp["n_exceedances"] > 0
    assert "standard errors" in reason
    assert "exceedances" in reason


def test_evt_var_es_returns_positive_floats(sample_losses):
    for alpha in [0.90, 0.95, 0.99]:
        var, es, params = evt_var_es(sample_losses, alpha=alpha)
        assert isinstance(var, float)
        assert isinstance(es, float)
        assert isinstance(params, dict)
        assert var > 0.0
        assert es > 0.0
        assert es >= var
        assert "xi" in params
        assert "sigma" in params


def test_evt_var_es_monotonicity_in_alpha(sample_losses):
    """Higher confidence level alpha must produce larger VaR and ES."""
    var_90, es_90, _ = evt_var_es(sample_losses, alpha=0.90)
    var_95, es_95, _ = evt_var_es(sample_losses, alpha=0.95)
    var_99, es_99, _ = evt_var_es(sample_losses, alpha=0.99)

    assert var_90 < var_95 < var_99
    assert es_90 < es_95 < es_99


def test_evt_var_es_with_explicit_threshold(sample_losses):
    u = float(np.quantile(sample_losses, 0.92))
    var, es, params = evt_var_es(sample_losses, alpha=0.99, threshold=u)
    assert params["threshold"] == pytest.approx(u)
    assert var > u  # 99% VaR should exceed the 92% threshold


def test_evt_var_es_invalid_inputs(sample_losses):
    with pytest.raises(ValueError, match="Confidence alpha"):
        evt_var_es(sample_losses, alpha=1.05)

    with pytest.raises(ValueError, match="Too few exceedances"):
        evt_var_es(sample_losses, alpha=0.95, threshold=sample_losses.max() + 0.1)
