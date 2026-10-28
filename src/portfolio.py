"""Portfolio construction: efficient frontier and candidate portfolios.

Owner: Imasha Karunathilaka
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from src.data import log_to_simple
from src.kpis import kpi_table

TICKERS = ["SPY", "EFA", "EEM", "AGG", "GLD", "XLE", "XLK"]
TRADING_DAYS = 252

# Proposed mandate: (minimum weight, maximum weight) for each ETF
BOUNDS = {
    "SPY": (0.00, 0.40),
    "EFA": (0.00, 0.30),
    "EEM": (0.00, 0.10),
    "AGG": (0.30, 0.60),
    "GLD": (0.00, 0.15),
    "XLE": (0.00, 0.10),
    "XLK": (0.00, 0.15),
}


def portfolio_returns(returns: pd.DataFrame, weights) -> pd.Series:
    """Daily simple portfolio returns from asset log returns and weights.

    Simple returns are used here because they add up across assets and log
    returns do not. Weights are held fixed, i.e. rebalanced daily.
    """
    w = pd.Series(weights, index=returns.columns, dtype=float)
    if not np.isclose(w.sum(), 1.0):
        raise ValueError(f"Weights must sum to 1, got {w.sum():.4f}")
    simple = log_to_simple(returns)
    return (simple @ w).rename("portfolio")


def get_bounds() -> list[tuple[float, float]]:
    """Return the weight limits in ticker order, ready for scipy.optimize."""
    return [BOUNDS[t] for t in TICKERS]


def check_weights(weights: pd.Series, tol: float = 1e-6) -> bool:
    """Return True if weights sum to 1 and respect every mandate limit."""
    if abs(weights.sum() - 1.0) > tol:
        return False
    for ticker, (low, high) in BOUNDS.items():
        if weights[ticker] < low - tol or weights[ticker] > high + tol:
            return False
    return True


def asset_stats(returns: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """Return the yearly mean return and yearly covariance of simple returns."""
    simple = log_to_simple(returns)
    return simple.mean() * TRADING_DAYS, simple.cov() * TRADING_DAYS


def annual_risk_free(rf: pd.Series, index: pd.Index) -> float:
    """Return the average yearly risk free rate over the given dates."""
    daily = rf.reindex(index).ffill()
    return float(daily.mean() * TRADING_DAYS)


def _start_weights() -> np.ndarray:
    """Return a starting mix that already follows every mandate limit."""
    low = np.array([BOUNDS[t][0] for t in TICKERS])
    high = np.array([BOUNDS[t][1] for t in TICKERS])
    share = (1 - low.sum()) / (high - low).sum()
    return low + (high - low) * share


def _solve(objective, extra_constraints=()) -> np.ndarray:
    """Minimise an objective over weights that follow the mandate."""
    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1.0}]
    constraints.extend(extra_constraints)
    result = minimize(
        objective,
        _start_weights(),
        method="SLSQP",
        bounds=get_bounds(),
        constraints=constraints,
        options={"maxiter": 500, "ftol": 1e-12},
    )
    if not result.success:
        raise RuntimeError(f"Optimiser failed: {result.message}")
    return result.x


def equal_weight() -> pd.Series:
    """Return the allowed mix that is closest to 1/7 in every ETF."""
    target = 1 / len(TICKERS)
    w = _solve(lambda w: np.sum((w - target) ** 2))
    return pd.Series(w, index=TICKERS)


def min_variance(cov: pd.DataFrame) -> pd.Series:
    """Return the allowed mix with the lowest portfolio variance."""
    c = cov.to_numpy()
    w = _solve(lambda w: w @ c @ w)
    return pd.Series(w, index=TICKERS)


def max_sharpe(mu: pd.Series, cov: pd.DataFrame, rf_annual: float) -> pd.Series:
    """Return the allowed mix with the highest Sharpe ratio."""
    m, c = mu.to_numpy(), cov.to_numpy()
    w = _solve(lambda w: -(m @ w - rf_annual) / np.sqrt(w @ c @ w))
    return pd.Series(w, index=TICKERS)


def risk_parity(cov: pd.DataFrame) -> pd.Series:
    """Return the allowed mix where each ETF adds the most equal share of risk."""
    c = cov.to_numpy()

    def objective(w: np.ndarray) -> float:
        share = w * (c @ w) / (w @ c @ w)
        return float(np.sum((share - 1 / len(w)) ** 2))

    return pd.Series(_solve(objective), index=TICKERS)


def efficient_frontier(
    mu: pd.Series, cov: pd.DataFrame, n_points: int = 25
) -> pd.DataFrame:
    """Return return, volatility and weights for portfolios on the frontier."""
    m, c = mu.to_numpy(), cov.to_numpy()
    calmest = _solve(lambda w: w @ c @ w)
    richest = _solve(lambda w: -(m @ w))
    targets = np.linspace(m @ calmest, m @ richest - 1e-6, n_points)
    rows = []
    for target in targets:
        hit_target = [{"type": "eq", "fun": lambda w, t=target: m @ w - t}]
        w = _solve(lambda w: w @ c @ w, hit_target)
        row = {"Return": float(m @ w), "Volatility": float(np.sqrt(w @ c @ w))}
        row.update(dict(zip(TICKERS, w, strict=True)))
        rows.append(row)
    return pd.DataFrame(rows)


def candidate_portfolios(returns: pd.DataFrame, rf_annual: float) -> pd.DataFrame:
    """Return the weights of every candidate, one column per candidate."""
    mu, cov = asset_stats(returns)
    return pd.DataFrame(
        {
            "Equal weight": equal_weight(),
            "Minimum variance": min_variance(cov),
            "Maximum Sharpe": max_sharpe(mu, cov, rf_annual),
            "Risk parity": risk_parity(cov),
        }
    )


def candidate_kpis(
    returns: pd.DataFrame, weights: pd.DataFrame, rf_annual: float
) -> pd.DataFrame:
    """Return the full KPI table, one column per candidate, against SPY."""
    spy = log_to_simple(returns)["SPY"]
    table = {
        name: kpi_table(portfolio_returns(returns, weights[name]), spy, rf_annual)
        for name in weights.columns
    }
    return pd.DataFrame(table)
