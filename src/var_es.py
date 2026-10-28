"""Value at Risk (VaR) and Expected Shortfall (ES): historical, parametric and Monte Carlo.

Owner: Aadhila Anees
Layer 2 & 3: Quantitative Risk Measurement
"""

import numpy as np
import pandas as pd
from scipy import stats

from src import config


def _validate_inputs(returns: pd.Series, alpha: float, method: str) -> pd.Series:
    """Validate returns series, confidence alpha, and chosen methodology."""
    if not isinstance(returns, (pd.Series, np.ndarray)):
        raise TypeError("returns must be a pandas Series or numpy 1D array")
    clean_returns = pd.Series(returns).dropna()
    if len(clean_returns) < 30:
        raise ValueError(f"Insufficient data points ({len(clean_returns)}) to compute reliable VaR/ES.")

    if not (0.0 < alpha < 1.0):
        raise ValueError(f"Confidence level alpha must be strictly between 0 and 1, got {alpha}")

    if method not in config.VAR_METHODS:
        valid_methods = list(config.VAR_METHODS.keys())
        raise ValueError(f"Unknown method '{method}'. Must be one of {valid_methods}")

    return clean_returns


def _historical_var_es(returns: pd.Series, alpha: float) -> tuple[float, float]:
    """Historical Simulation VaR and ES.

    VaR is the empirical quantile of historical returns at (1 - alpha).
    ES is the conditional expectation of returns below -VaR.
    Both returned as positive loss decimals.
    """
    # At alpha = 0.95, we look at the lowest 5% quantile of returns (which are negative)
    cutoff = float(np.quantile(returns, 1.0 - alpha))
    var = -cutoff

    # Tail returns are those worse than or equal to the cutoff
    tail_losses = -returns[returns <= cutoff]
    es = float(tail_losses.mean()) if len(tail_losses) > 0 else var

    return float(var), float(es)


def _parametric_normal_var_es(
    returns: pd.Series, alpha: float, include_drift: bool = True
) -> tuple[float, float]:
    """Parametric Gaussian (Normal) VaR and ES using exact closed-form equations.

    If include_drift is True, the sample mean mu is included.
    If False, mu is assumed to be 0 (conservative zero-drift assumption).
    """
    mu = float(returns.mean()) if include_drift else 0.0
    sigma = float(returns.std(ddof=1))

    # Standard normal quantile: z_alpha = Phi^{-1}(alpha)
    z = float(stats.norm.ppf(alpha))

    # VaR = - (mu - z * sigma) = -mu + z * sigma
    var = -mu + z * sigma

    # Closed-form Normal ES: -mu + sigma * phi(z) / (1 - alpha)
    phi_z = float(stats.norm.pdf(z))
    es = -mu + sigma * (phi_z / (1.0 - alpha))

    return float(var), float(es)


def _parametric_student_t_var_es(
    returns: pd.Series, alpha: float, include_drift: bool = True
) -> tuple[float, float]:
    """Parametric Student's t VaR and ES to capture leptokurtosis (fat tails).

    Fits degrees of freedom (df), location (loc), and scale using maximum likelihood.
    """
    df, loc, scale = stats.t.fit(returns)
    if not include_drift:
        loc = 0.0

    # Lower tail quantile of returns at (1 - alpha)
    cutoff = float(stats.t.ppf(1.0 - alpha, df, loc=loc, scale=scale))
    var = -cutoff

    # Closed-form ES for standardized Student's t
    # Let T = (R - loc) / scale ~ t(df)
    t_cutoff = (cutoff - loc) / scale
    if df > 1.0:
        pdf_val = float(stats.t.pdf(t_cutoff, df))
        tail_factor = (df + t_cutoff**2) / (df - 1.0)
        expected_standardized_loss = (pdf_val / (1.0 - alpha)) * tail_factor
        es = -loc + scale * expected_standardized_loss
    else:
        # Fallback to numerical integration if df <= 1 (undefined theoretical mean)
        tail_integral, _ = stats.quad(
            lambda x: x * stats.t.pdf(x, df, loc=loc, scale=scale),
            -np.inf,
            cutoff,
        )
        es = -(tail_integral / (1.0 - alpha))

    return float(var), float(es)


def _monte_carlo_var_es(
    returns: pd.Series,
    alpha: float,
    n_simulations: int = 100_000,
    seed: int = config.SEED,
    distribution: str = "student_t",
) -> tuple[float, float]:
    """Monte Carlo simulated VaR and ES with fixed random seed for full reproducibility.

    Simulates return paths from the empirical or fitted distribution.
    """
    rng = np.random.default_rng(seed)

    if distribution == "student_t":
        df, loc, scale = stats.t.fit(returns)
        # standard_t generates standardized t; multiply by scale and shift by loc
        simulated = loc + scale * rng.standard_t(df=df, size=n_simulations)
    else:
        mu = float(returns.mean())
        sigma = float(returns.std(ddof=1))
        simulated = rng.normal(loc=mu, scale=sigma, size=n_simulations)

    cutoff = float(np.quantile(simulated, 1.0 - alpha))
    var = -cutoff
    tail_losses = -simulated[simulated <= cutoff]
    es = float(tail_losses.mean()) if len(tail_losses) > 0 else var

    return float(var), float(es)


def var_es(
    returns: pd.Series,
    alpha: float,
    method: str,
    include_drift: bool = True,
    n_simulations: int = 100_000,
    seed: int = config.SEED,
) -> tuple[float, float]:
    """Calculate 1-day Value at Risk (VaR) and Expected Shortfall (ES).

    Both metrics are returned as positive loss numbers (decimals, e.g., 0.02 = 2% loss).

    Parameters
    ----------
    returns : pd.Series
        Daily portfolio return series.
    alpha : float
        Confidence level, strictly between 0 and 1 (typically 0.90, 0.95, or 0.99).
    method : str
        One of 'historical', 'normal', 'student_t', 'monte_carlo'.
    include_drift : bool, default=True
        Whether to include the expected return (mu) in parametric models.
        Setting to False enforces a conservative zero-drift assumption.
    n_simulations : int, default=100,000
        Number of simulated paths for Monte Carlo.
    seed : int, default=42
        Reproducibility seed for Monte Carlo.

    Returns
    -------
    tuple[float, float]
        (VaR, ES) as positive loss fractions.
    """
    clean_returns = _validate_inputs(returns, alpha, method)

    if method == "historical":
        return _historical_var_es(clean_returns, alpha)
    elif method == "normal":
        return _parametric_normal_var_es(clean_returns, alpha, include_drift=include_drift)
    elif method == "student_t":
        return _parametric_student_t_var_es(clean_returns, alpha, include_drift=include_drift)
    elif method == "monte_carlo":
        return _monte_carlo_var_es(
            clean_returns,
            alpha,
            n_simulations=n_simulations,
            seed=seed,
            distribution="student_t",
        )
    else:
        raise ValueError(f"Unhandled method: {method}")
