"""Risk budgeting: Marginal VaR, Component VaR, and risk attribution per asset.

Owner: Aadhila Anees
Layer 2 & 3 / Practical Decision Layer: Euler Risk Decomposition
"""

import numpy as np
import pandas as pd
from scipy import stats

from src.data import log_to_simple


def _clean_inputs(
    returns: pd.DataFrame, weights: np.ndarray | pd.Series
) -> tuple[pd.DataFrame, pd.Series]:
    """Validate asset returns DataFrame and weight vector."""
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a pandas DataFrame")

    if isinstance(weights, pd.Series):
        w = weights.reindex(returns.columns).astype(float)
    else:
        w = pd.Series(weights, index=returns.columns, dtype=float)

    if not np.isclose(w.sum(), 1.0, atol=1e-4):
        raise ValueError(f"Weights must sum to 1.0, got {w.sum():.4f}")

    # Convert log returns to simple returns for linear portfolio aggregation
    simple_returns = log_to_simple(returns).dropna()
    return simple_returns, w


def parametric_risk_budget(
    returns: pd.DataFrame,
    weights: np.ndarray | pd.Series,
    alpha: float = 0.95,
    include_drift: bool = True,
) -> pd.DataFrame:
    """Euler risk decomposition for parametric Gaussian VaR and ES.

    By Euler's theorem for homogeneous degree-1 risk measures:
    Total Risk = sum(Weight_i * Marginal_Risk_i) = sum(Component_Risk_i).

    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns (log returns).
    weights : array-like or pd.Series
        Portfolio asset allocations summing to 1.
    alpha : float, default=0.95
        Confidence level.
    include_drift : bool, default=True
        Whether to incorporate mean asset returns in the drift term.

    Returns
    -------
    pd.DataFrame
        Risk budget table with columns:
        ['weight', 'marginal_var', 'component_var', 'pct_var_contrib',
         'marginal_es', 'component_es', 'pct_es_contrib']
    """
    simple_returns, w = _clean_inputs(returns, weights)
    tickers = list(simple_returns.columns)

    cov_matrix = simple_returns.cov()
    mu = simple_returns.mean() if include_drift else pd.Series(0.0, index=tickers)

    w_arr = w.values
    cov_arr = cov_matrix.values
    mu_arr = mu.values

    # Portfolio variance and volatility
    port_var = float(w_arr @ cov_arr @ w_arr)
    port_vol = np.sqrt(port_var) if port_var > 0 else 1e-8

    # Standard normal critical value and density
    z = float(stats.norm.ppf(alpha))
    phi_z = float(stats.norm.pdf(z))
    lambda_es = phi_z / (1.0 - alpha)

    # Marginal volatility: d(sigma_p)/dw = (Sigma @ w) / sigma_p
    cov_w = cov_arr @ w_arr
    marginal_vol = cov_w / port_vol

    # Marginal VaR and ES
    marginal_var = -mu_arr + z * marginal_vol
    marginal_es = -mu_arr + lambda_es * marginal_vol

    # Component VaR and ES
    component_var = w_arr * marginal_var
    component_es = w_arr * marginal_es

    total_var = float(component_var.sum())
    total_es = float(component_es.sum())

    # Percentage risk contributions (%RC)
    pct_var = (
        component_var / total_var if total_var > 0 else np.zeros_like(component_var)
    )
    pct_es = component_es / total_es if total_es > 0 else np.zeros_like(component_es)

    df = pd.DataFrame(
        {
            "weight": w.values,
            "marginal_var": marginal_var,
            "component_var": component_var,
            "pct_var_contrib": pct_var,
            "marginal_es": marginal_es,
            "component_es": component_es,
            "pct_es_contrib": pct_es,
        },
        index=tickers,
    )
    return df


def historical_risk_budget(
    returns: pd.DataFrame,
    weights: np.ndarray | pd.Series,
    alpha: float = 0.95,
) -> pd.DataFrame:
    """Historical Euler risk decomposition for Expected Shortfall.

    For historical ES:
    Marginal ES_i = -E[R_i | R_portfolio <= -VaR_portfolio].
    Component ES_i = Weight_i * Marginal ES_i.
    Euler guarantee: sum(Component ES_i) == Total Portfolio ES.

    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns (log returns).
    weights : array-like or pd.Series
        Portfolio asset allocations summing to 1.
    alpha : float, default=0.95
        Confidence level.

    Returns
    -------
    pd.DataFrame
        Historical risk attribution table.
    """
    simple_returns, w = _clean_inputs(returns, weights)
    tickers = list(simple_returns.columns)

    # Calculate portfolio return series
    port_series = simple_returns @ w

    # Portfolio VaR and cutoff
    cutoff = float(np.quantile(port_series, 1.0 - alpha))
    tail_mask = port_series <= cutoff

    # Tail returns of each individual asset on portfolio tail days
    asset_tail_returns = simple_returns.loc[tail_mask]

    # Marginal ES of each asset (positive loss)
    marginal_es = -asset_tail_returns.mean().values
    component_es = w.values * marginal_es
    total_es = float(component_es.sum())

    pct_es = component_es / total_es if total_es > 0 else np.zeros_like(component_es)

    # For historical VaR, estimate marginal VaR using narrow quantile bandwidth (+- 1%)
    low_q = max(0.0, 1.0 - alpha - 0.01)
    high_q = min(1.0, 1.0 - alpha + 0.01)
    var_mask = (port_series >= np.quantile(port_series, low_q)) & (
        port_series <= np.quantile(port_series, high_q)
    )
    if var_mask.sum() > 0:
        marginal_var = -simple_returns.loc[var_mask].mean().values
    else:
        # Fallback to asset quantile
        marginal_var = -np.quantile(simple_returns, 1.0 - alpha, axis=0)

    component_var = w.values * marginal_var
    total_var = float(component_var.sum())
    pct_var = (
        component_var / total_var if total_var > 0 else np.zeros_like(component_var)
    )

    df = pd.DataFrame(
        {
            "weight": w.values,
            "marginal_var": marginal_var,
            "component_var": component_var,
            "pct_var_contrib": pct_var,
            "marginal_es": marginal_es,
            "component_es": component_es,
            "pct_es_contrib": pct_es,
        },
        index=tickers,
    )
    return df


def risk_budget(
    returns: pd.DataFrame,
    weights: np.ndarray | pd.Series,
    alpha: float = 0.95,
    method: str = "parametric",
) -> pd.DataFrame:
    """Unified risk budgeting dispatcher.

    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns (log returns).
    weights : array-like or pd.Series
        Portfolio asset allocations summing to 1.
    alpha : float, default=0.95
        Confidence level.
    method : str, default='parametric'
        Methodology: 'parametric' (Gaussian Euler) or 'historical' (Tail expectation).

    Returns
    -------
    pd.DataFrame
        Table containing marginal, component, and percentage risk contributions.
    """
    if method == "parametric":
        return parametric_risk_budget(returns, weights, alpha=alpha)
    elif method == "historical":
        return historical_risk_budget(returns, weights, alpha=alpha)
    else:
        raise ValueError(
            f"Unknown method '{method}'. Choose 'parametric' or 'historical'."
        )
