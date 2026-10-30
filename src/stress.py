"""Stress tests: historical crisis replays and our own scenario.

Owner: Tharindu Dhanushka
"""

import numpy as np
import pandas as pd

from src import config

# Our own scenario. These are assumptions, not data: an inflation surprise that
# pushes rates up 250bp, so stocks and bonds fall together and nothing hedges.
INFLATION_SHOCK = {
    "SPY": -0.25,
    "EFA": -0.25,
    "EEM": -0.30,
    "AGG": -0.15,
    "GLD": -0.05,
    "XLE": 0.00,
    "XLK": -0.35,
}

INFLATION_SHOCK_REASONS = {
    "SPY": "Higher real rates cut equity valuations, about 1.4 times the 2022 fall",
    "EFA": "Developed markets move with the US, as in 2022",
    "EEM": "A strong dollar and capital outflows hit emerging markets hardest",
    "AGG": "250bp rise in yields times a duration of about 6 years",
    "GLD": "Rising real yields weigh on gold, so it does not hedge",
    "XLE": "Energy rose in 2022; we assume no gain so the hedge cannot save us",
    "XLK": "Long-duration tech falls most when rates rise, as in 2022",
}

HYPOTHETICAL_SCENARIOS = {"Inflation shock, stocks and bonds fall": INFLATION_SHOCK}

# Crisis loss limit agreed in the committee memo (Section 8)
DEFAULT_LOSS_LIMIT = 0.15


def _weights(weights, tickers) -> pd.Series:
    if isinstance(weights, pd.Series):
        w = weights.reindex(tickers).astype(float)
    else:
        w = pd.Series(weights, index=tickers, dtype=float)
    if not np.isclose(w.sum(), 1.0, atol=1e-4):
        raise ValueError(f"Weights must sum to 1, got {w.sum():.4f}")
    return w


def _window(returns: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    part = returns.loc[start:end]
    if part.empty:
        raise ValueError(f"No returns between {start} and {end}")
    return part


def asset_period_returns(returns: pd.DataFrame, start: str, end: str) -> pd.Series:
    """Total simple return of each asset from the close before start to end."""
    return np.expm1(_window(returns, start, end).sum())


def portfolio_path(returns: pd.DataFrame, weights, start: str, end: str) -> pd.Series:
    """Value of 1 dollar invested at the start and held through the period.

    Buy and hold, not rebalanced: in a crisis we would not rebalance daily, so
    the weights drift with prices. The series starts at 1 on the day before.
    """
    part = _window(returns, start, end)
    w = _weights(weights, returns.columns)
    growth = np.exp(part.cumsum())
    path = growth @ w
    before = returns.index[returns.index.get_loc(part.index[0]) - 1]
    return pd.concat([pd.Series([1.0], index=[before]), path]).rename("value")


def contributions(returns: pd.DataFrame, weights, start: str, end: str) -> pd.Series:
    """Each asset's share of the portfolio return. They add up to the total."""
    w = _weights(weights, returns.columns)
    return w * asset_period_returns(returns, start, end)


def replay(returns: pd.DataFrame, weights, start: str, end: str) -> dict:
    """Portfolio impact of replaying one historical period."""
    path = portfolio_path(returns, weights, start, end)
    daily = path.pct_change().dropna()
    total = float(path.iloc[-1] - 1)
    return {
        "start": start,
        "end": end,
        "days": len(daily),
        "return": total,
        "pnl_usd": total * config.PORTFOLIO_VALUE_USD,
        "max_drawdown": float((path / path.cummax() - 1).min()),
        "worst_day": float(daily.min()),
        "worst_day_date": daily.idxmin().date().isoformat(),
        "spy_return": float(
            asset_period_returns(returns, start, end).get(
                config.BENCHMARK, float("nan")
            )
        ),
    }


def hypothetical(weights, shocks: dict[str, float]) -> dict:
    """Portfolio impact of an instant shock to each asset."""
    tickers = list(shocks)
    w = _weights(weights, tickers)
    total = float(w @ pd.Series(shocks))
    return {
        "return": total,
        "pnl_usd": total * config.PORTFOLIO_VALUE_USD,
        "spy_return": shocks.get(config.BENCHMARK, float("nan")),
    }


def stress_table(
    returns: pd.DataFrame,
    weights,
    periods: dict[str, tuple[str, str]] = config.STRESS_PERIODS,
    scenarios: dict[str, dict[str, float]] = HYPOTHETICAL_SCENARIOS,
) -> pd.DataFrame:
    """Every scenario for one portfolio, historical replays first."""
    rows = {}
    for name, (start, end) in periods.items():
        rows[name] = {
            "type": "Historical replay",
            **replay(returns, weights, start, end),
        }
    for name, shocks in scenarios.items():
        rows[name] = {
            "type": "Hypothetical (assumption)",
            **hypothetical(weights, shocks),
        }
    return pd.DataFrame(rows).T


def stress_across_candidates(
    returns: pd.DataFrame,
    candidates: pd.DataFrame,
    periods: dict[str, tuple[str, str]] = config.STRESS_PERIODS,
    scenarios: dict[str, dict[str, float]] = HYPOTHETICAL_SCENARIOS,
) -> pd.DataFrame:
    """Scenario return for every candidate, one column per candidate."""
    return pd.DataFrame(
        {
            name: stress_table(returns, candidates[name], periods, scenarios)[
                "return"
            ].astype(float)
            for name in candidates.columns
        }
    )


def reverse_stress(weights, shocks: dict[str, float], loss_limit: float) -> float:
    """How many times the scenario must be scaled up to lose loss_limit.

    Assumes the shocks scale linearly. Below 1 means the scenario as written
    already breaks the limit. Infinite when the scenario makes money.
    """
    if loss_limit <= 0:
        raise ValueError("loss_limit must be a positive fraction")
    loss = -hypothetical(weights, shocks)["return"]
    return float(loss_limit / loss) if loss > 0 else float("inf")


def main() -> None:
    """Print the stress tables used in the report."""
    from src.data import load_returns, load_risk_free
    from src.portfolio import annual_risk_free, candidate_portfolios, final_weights

    returns = load_returns()
    rf = annual_risk_free(load_risk_free(), returns.index)
    candidates = candidate_portfolios(returns, rf)
    weights = final_weights()
    print("Final portfolio\n", stress_table(returns, weights).to_string())
    print("\nAll candidates\n", stress_across_candidates(returns, candidates).round(4))
    for name, (start, end) in config.STRESS_PERIODS.items():
        print(f"\nContributions, {name}")
        print(contributions(returns, weights, start, end).round(4).to_string())
    print("\nInflation shock in USD, by ETF")
    shock_usd = weights * pd.Series(INFLATION_SHOCK) * config.PORTFOLIO_VALUE_USD
    print(shock_usd.round(0).to_string())
    for name in candidates.columns:
        multiple = reverse_stress(candidates[name], INFLATION_SHOCK, DEFAULT_LOSS_LIMIT)
        print(f"Reverse stress multiple, {name}: {multiple:.2f}")
    multiple = reverse_stress(weights, INFLATION_SHOCK, DEFAULT_LOSS_LIMIT)
    print(f"Reverse stress multiple, final portfolio: {multiple:.2f}")


if __name__ == "__main__":
    main()
