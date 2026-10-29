"""Performance KPIs: Sharpe, Sortino, Treynor, Jensen's alpha, IR, drawdown, Calmar.

Owner: Imasha Karunathilaka
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def annual_return(returns: pd.Series) -> float:
    """Return the compound annual growth rate of daily simple returns."""
    growth = float((1 + returns).prod())
    return float(growth ** (TRADING_DAYS / len(returns)) - 1)


def annual_volatility(returns: pd.Series) -> float:
    """Return the yearly volatility of daily simple returns."""
    return float(returns.std() * np.sqrt(TRADING_DAYS))


def drawdown_series(returns: pd.Series) -> pd.Series:
    """Return the fall from the previous peak on every day, as a negative number."""
    wealth = (1 + returns).cumprod()
    return wealth / wealth.cummax() - 1


def max_drawdown(returns: pd.Series) -> float:
    """Return the largest fall from a peak to a later bottom."""
    return float(drawdown_series(returns).min())


def sharpe_ratio(returns: pd.Series, rf_annual: float) -> float:
    """Return yearly excess return divided by yearly volatility."""
    vol = returns.std()
    if np.isclose(vol, 0):
        return float("nan")
    excess = returns - rf_annual / TRADING_DAYS
    return float(excess.mean() / vol * np.sqrt(TRADING_DAYS))


def sortino_ratio(returns: pd.Series, rf_annual: float) -> float:
    """Return yearly excess return divided by downside volatility only."""
    excess = returns - rf_annual / TRADING_DAYS
    downside = np.sqrt((np.minimum(excess, 0) ** 2).mean())
    if np.isclose(downside, 0):
        return float("nan")
    return float(excess.mean() / downside * np.sqrt(TRADING_DAYS))


def capm_beta_alpha(
    returns: pd.Series, market: pd.Series, rf_annual: float
) -> tuple[float, float]:
    """Return CAPM beta and Jensen's alpha (yearly) against the market."""
    beta = float(returns.cov(market) / market.var())
    port_excess = float(returns.mean()) * TRADING_DAYS - rf_annual
    market_excess = float(market.mean()) * TRADING_DAYS - rf_annual
    alpha = float(port_excess - beta * market_excess)
    return float(beta), float(alpha)


def treynor_ratio(returns: pd.Series, market: pd.Series, rf_annual: float) -> float:
    """Return yearly excess return divided by CAPM beta."""
    beta, _ = capm_beta_alpha(returns, market, rf_annual)
    if np.isclose(beta, 0):
        return float("nan")
    return float((float(returns.mean()) * TRADING_DAYS - rf_annual) / beta)


def information_ratio(returns: pd.Series, benchmark: pd.Series) -> float:
    """Return yearly active return divided by tracking error."""
    active = returns - benchmark
    tracking_error = float(active.std())
    if np.isclose(tracking_error, 0):
        return float("nan")
    return float(float(active.mean()) / tracking_error * np.sqrt(TRADING_DAYS))


def calmar_ratio(returns: pd.Series) -> float:
    """Return the annual return divided by the size of the max drawdown."""
    mdd = max_drawdown(returns)
    if np.isclose(mdd, 0):
        return float("nan")
    return float(annual_return(returns) / abs(mdd))


def kpi_table(returns: pd.Series, benchmark: pd.Series, rf_annual: float) -> pd.Series:
    """Return every KPI for one portfolio as a single labelled series."""
    beta, alpha = capm_beta_alpha(returns, benchmark, rf_annual)
    return pd.Series(
        {
            "Annual return": annual_return(returns),
            "Annual volatility": annual_volatility(returns),
            "Sharpe": sharpe_ratio(returns, rf_annual),
            "Sortino": sortino_ratio(returns, rf_annual),
            "Treynor": treynor_ratio(returns, benchmark, rf_annual),
            "Beta": beta,
            "Jensen alpha": alpha,
            "Information ratio": information_ratio(returns, benchmark),
            "Max drawdown": max_drawdown(returns),
            "Calmar": calmar_ratio(returns),
        }
    )
