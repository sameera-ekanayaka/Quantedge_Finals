"""Portfolio construction: efficient frontier and candidate portfolios.

Owner: Imasha Karunathilaka
"""

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.optimize import linprog, minimize

from src.data import log_to_simple
from src.kpis import annual_return, annual_volatility, kpi_table, max_drawdown
from src.var_es import var_es

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


def risk_shares(weights: pd.Series, cov: pd.DataFrame) -> pd.Series:
    """Return each ETF's share of total portfolio risk, adding up to 1."""
    w = weights.reindex(cov.columns).to_numpy()
    c = cov.to_numpy()
    share = w * (c @ w) / (w @ c @ w)
    return pd.Series(share, index=cov.columns)


def candidate_risk_shares(returns: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    """Return the risk share of every ETF, one column per candidate."""
    _, cov = asset_stats(returns)
    return pd.DataFrame(
        {name: risk_shares(weights[name], cov) for name in weights.columns}
    )


def candidate_tradeoffs(returns: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    """Return the return versus risk trade-off, one row per candidate."""
    rows = {}
    for name in weights.columns:
        port = portfolio_returns(returns, weights[name])
        rows[name] = {
            "Annual return": annual_return(port),
            "Annual volatility": annual_volatility(port),
            "Max drawdown": max_drawdown(port),
            "Worst day": float(port.min()),
        }
    return pd.DataFrame(rows).T


def portfolio_es(returns: pd.DataFrame, weights, alpha: float = 0.95) -> float:
    """Return the one-day historical ES of a portfolio, using var_es."""
    port = portfolio_returns(returns, weights)
    _, es = var_es(port, alpha, "historical")
    return es


def min_es(returns: pd.DataFrame, alpha: float = 0.95) -> pd.Series:
    """Return the allowed mix with the lowest historical ES at level alpha.

    ES is not smooth, so the optimiser from earlier would struggle.
    It is solved as a linear programme instead (Rockafellar and Uryasev).
    """
    simple = log_to_simple(returns)[TICKERS].to_numpy()
    n_days, n_assets = simple.shape
    tail_weight = 1 / ((1 - alpha) * n_days)
    cost = np.concatenate([np.zeros(n_assets), [1.0], np.full(n_days, tail_weight)])
    a_ub = sparse.hstack(
        [
            sparse.csr_matrix(-simple),
            sparse.csr_matrix(-np.ones((n_days, 1))),
            -sparse.identity(n_days, format="csr"),
        ],
        format="csr",
    )
    a_eq = sparse.csr_matrix(
        np.concatenate([np.ones(n_assets), np.zeros(1 + n_days)]).reshape(1, -1)
    )
    bounds = get_bounds() + [(None, None)] + [(0, None)] * n_days
    result = linprog(
        cost,
        A_ub=a_ub,
        b_ub=np.zeros(n_days),
        A_eq=a_eq,
        b_eq=[1.0],
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        raise RuntimeError(f"Optimiser failed: {result.message}")
    return pd.Series(result.x[:n_assets], index=TICKERS)


# Final recommended portfolio (Maximum Sharpe), frozen by the team
FINAL_WEIGHTS = {
    "SPY": 0.0955,
    "EFA": 0.0,
    "EEM": 0.0,
    "AGG": 0.5885,
    "GLD": 0.15,
    "XLE": 0.016,
    "XLK": 0.15,
}


def final_weights() -> pd.Series:
    """Return the frozen final portfolio weights in ticker order."""
    weights = pd.Series(FINAL_WEIGHTS, dtype=float)[TICKERS]
    if not check_weights(weights):
        raise ValueError("Final weights break the mandate")
    return weights
