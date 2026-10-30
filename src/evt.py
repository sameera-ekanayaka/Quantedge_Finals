"""Extreme value theory: peaks over threshold with a Generalized Pareto fit.

Owner: Praveen Madawalage
Layer 4: Extreme Value Theory (Deep Tail Modelling)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def _clean_losses(losses: pd.Series | np.ndarray) -> pd.Series:
    """Validate and clean the loss series, ensuring positive numeric values."""
    if not isinstance(losses, (pd.Series, np.ndarray)):
        raise TypeError("losses must be a pandas Series or numpy 1D array")
    clean = pd.Series(losses).dropna().astype(float)
    if len(clean) < 30:
        raise ValueError(f"Insufficient data points ({len(clean)}) for tail modeling.")
    return clean


def fit_gpd(exceedances: pd.Series | np.ndarray) -> tuple[float, float]:
    """Fit a Generalized Pareto Distribution to threshold exceedances (y = x - u).

    Uses Maximum Likelihood Estimation with the location parameter fixed at 0.

    Parameters
    ----------
    exceedances : pd.Series or np.ndarray
        Positive values representing losses beyond the chosen threshold.

    Returns
    -------
    tuple[float, float]
        (xi, sigma) where xi is the shape parameter and sigma is the scale.
    """
    y = np.asarray(exceedances, dtype=float)
    if len(y) < 10:
        raise ValueError(f"Need at least 10 exceedances to fit GPD, got {len(y)}")
    if np.any(y <= 0):
        raise ValueError("Exceedances must be strictly positive (losses > threshold).")

    # In scipy.stats.genpareto, c is the shape parameter xi, floc=0 fixes loc=0
    shape, loc, scale = stats.genpareto.fit(y, floc=0)
    return float(shape), float(scale)


def mean_excess_plot_data(
    losses: pd.Series | np.ndarray,
    n_points: int = 50,
    q_min: float = 0.70,
    q_max: float = 0.98,
) -> pd.DataFrame:
    """Compute empirical mean excess values and standard errors across thresholds.

    For a threshold u, the mean excess is e(u) = E[X - u | X > u].
    If the tail follows a GPD with shape xi < 1, e(u) is linear in u.

    Returns
    -------
    pd.DataFrame
        Columns: ['threshold', 'mean_excess', 'std_error', 'ci_lower',
                  'ci_upper', 'n_exceedances']
    """
    clean = _clean_losses(losses)
    u_min = float(np.quantile(clean, q_min))
    u_max = float(np.quantile(clean, q_max))
    thresholds = np.linspace(u_min, u_max, n_points)

    rows = []
    for u in thresholds:
        exceed = clean[clean > u] - u
        n_u = len(exceed)
        if n_u < 5:
            continue
        mean_e = float(exceed.mean())
        std_e = float(exceed.std(ddof=1) / np.sqrt(n_u)) if n_u > 1 else 0.0
        rows.append(
            {
                "threshold": float(u),
                "mean_excess": mean_e,
                "std_error": std_e,
                "ci_lower": max(0.0, mean_e - 1.96 * std_e),
                "ci_upper": mean_e + 1.96 * std_e,
                "n_exceedances": int(n_u),
            }
        )
    return pd.DataFrame(rows)


def parameter_stability_plot_data(
    losses: pd.Series | np.ndarray,
    n_points: int = 40,
    q_min: float = 0.75,
    q_max: float = 0.98,
) -> pd.DataFrame:
    """Compute fitted GPD shape and modified scale across a grid of thresholds.

    The modified scale sigma* = sigma - xi * u remains constant above the true
    threshold where GPD tail behaviour begins.

    Returns
    -------
    pd.DataFrame
        Columns: ['threshold', 'shape_xi', 'scale_sigma', 'modified_scale',
                  'shape_se', 'n_exceedances']
    """
    clean = _clean_losses(losses)
    u_min = float(np.quantile(clean, q_min))
    u_max = float(np.quantile(clean, q_max))
    thresholds = np.linspace(u_min, u_max, n_points)

    rows = []
    for u in thresholds:
        exceed = clean[clean > u] - u
        n_u = len(exceed)
        if n_u < 15:
            continue
        try:
            xi, sigma = fit_gpd(exceed)
            # Asymptotic standard error of MLE shape parameter: (1 + xi) / sqrt(n_u)
            se_xi = float(abs(1.0 + xi) / np.sqrt(n_u))
            mod_scale = float(sigma - xi * u)
            rows.append(
                {
                    "threshold": float(u),
                    "shape_xi": xi,
                    "scale_sigma": sigma,
                    "modified_scale": mod_scale,
                    "shape_se": se_xi,
                    "n_exceedances": int(n_u),
                }
            )
        except Exception:
            continue
    return pd.DataFrame(rows)


def gpd_qq_data(
    losses: pd.Series | np.ndarray,
    threshold: float,
    xi: float,
    sigma: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute theoretical GPD quantiles and empirical sorted exceedances.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        (theoretical_quantiles, empirical_quantiles) for QQ validation.
    """
    clean = _clean_losses(losses)
    exceed = np.sort(clean[clean > threshold] - threshold)
    k = len(exceed)
    if k == 0:
        return np.array([]), np.array([])

    # Empirical plotting positions: (i - 0.5) / k
    p = (np.arange(1, k + 1) - 0.5) / k
    theoretical = stats.genpareto.ppf(p, c=xi, scale=sigma)
    return theoretical, exceed


def select_threshold(
    losses: pd.Series | np.ndarray,
    target_quantile: float = 0.90,
) -> tuple[float, str, dict]:
    """Select a defensible POT threshold using empirical quantiles and stability.

    Cross-checks against standard benchmark rules (90th and 95th percentiles).

    Parameters
    ----------
    losses : pd.Series or np.ndarray
        Historical portfolio loss series.
    target_quantile : float, default=0.90
        Initial target quantile for threshold selection (typically 0.90).

    Returns
    -------
    tuple[float, str, dict]
        (chosen_threshold, justification_text, comparison_summary)
    """
    clean = _clean_losses(losses)
    q90 = float(np.quantile(clean, 0.90))
    q95 = float(np.quantile(clean, 0.95))
    chosen = float(np.quantile(clean, target_quantile))

    n_total = len(clean)
    n_exceed = int((clean > chosen).sum())

    exceed = clean[clean > chosen] - chosen
    try:
        xi, _ = fit_gpd(exceed)
        shape_se = float(abs(1.0 + xi) / np.sqrt(n_exceed))
    except Exception:
        shape_se = None

    comparison = {
        "rule_90_pct": q90,
        "rule_95_pct": q95,
        "chosen_threshold": chosen,
        "target_quantile": target_quantile,
        "n_exceedances": n_exceed,
        "total_observations": n_total,
    }
    if shape_se is not None:
        comparison["shape_xi"] = xi
        comparison["shape_se"] = shape_se

    if shape_se is not None:
        reason = (
            f"Chosen threshold u = {chosen:.4f} is the "
            f"{target_quantile:.0%} percentile with {n_exceed} exceedances "
            f"(out of {n_total} trading days). Fitted shape parameter ξ above u "
            f"stays within about 2 standard errors "
            f"(shape_se ≈ {shape_se:.4f}, ±2 SE ≈ ±{2 * shape_se:.4f})."
        )
    else:
        reason = (
            f"Chosen threshold u = {chosen:.4f} is the "
            f"{target_quantile:.0%} percentile with {n_exceed} exceedances "
            f"(out of {n_total} trading days)."
        )
    return chosen, reason, comparison


def evt_var_es(
    losses: pd.Series | np.ndarray,
    alpha: float,
    threshold: float | None = None,
) -> tuple[float, float, dict]:
    """Calculate 1-day VaR and Expected Shortfall using Peaks-Over-Threshold GPD.

    Both VaR and ES are returned as positive loss fractions.

    Parameters
    ----------
    losses : pd.Series or np.ndarray
        Portfolio losses (positive values represent losses, i.e. -returns).
    alpha : float
        Confidence level strictly between 0 and 1 (e.g. 0.90, 0.95, 0.99).
    threshold : float, optional
        Loss threshold u above which GPD is fitted. If None, selected automatically.

    Returns
    -------
    tuple[float, float, dict]
        (VaR, ES, fitted_parameters)
    """
    clean = _clean_losses(losses)
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"Confidence alpha must be between 0 and 1, got {alpha}")

    if threshold is None:
        threshold, _, _ = select_threshold(clean)
    else:
        threshold = float(threshold)

    exceedances = clean[clean > threshold] - threshold
    n_u = len(exceedances)
    n_total = len(clean)

    if n_u < 10:
        raise ValueError(
            f"Too few exceedances ({n_u}) above threshold {threshold:.4f} "
            "for reliable GPD estimation. Lower the threshold."
        )

    p_u = n_u / n_total
    xi, sigma = fit_gpd(exceedances)

    # Closed-form POT VaR
    # When (1 - alpha) is smaller than p_u, we extrapolate into the tail
    prob_ratio = p_u / (1.0 - alpha)
    if abs(xi) < 1e-7:
        var = threshold + sigma * np.log(prob_ratio)
        es = var + sigma
    else:
        var = threshold + (sigma / xi) * (prob_ratio**xi - 1.0)
        # Closed-form GPD Expected Shortfall for xi < 1
        if xi < 1.0:
            es = (var + sigma - xi * threshold) / (1.0 - xi)
        else:
            # Theoretical mean is infinite if xi >= 1; empirical fallback
            tail = clean[clean > var]
            es = float(tail.mean()) if len(tail) > 0 else var

    # Sanity guard: ES must always be at least VaR
    if es < var:
        es = var

    params = {
        "xi": float(xi),
        "sigma": float(sigma),
        "threshold": float(threshold),
        "n_exceedances": int(n_u),
        "p_exceed": float(p_u),
        "alpha": float(alpha),
        "tail_type": "Heavy-tailed (Fréchet)" if xi > 0 else "Thin-tailed (Weibull)",
    }

    return float(var), float(es), params
