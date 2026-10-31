"""Supplementary validation; does not change submitted portfolio results."""

import pandas as pd

from src.data import log_to_simple
from src.evt import evt_var_es
from src.kpis import annual_return, annual_volatility, max_drawdown, sharpe_ratio
from src.portfolio import (
    annual_risk_free,
    asset_stats,
    final_weights,
    max_sharpe,
    min_variance,
)


def walk_forward(returns, rf, start_year=2010):
    """Expanding history, annual January decisions, daily target rebalancing.

    Train strictly before each evaluation year. Use identical held-out dates
    for the frozen comparator; that comparator is not out-of-sample selection.
    No transaction costs. At least three calendar years of training required.
    """
    series = {
        name: []
        for name in [
            "Walk-forward Maximum Sharpe",
            "Walk-forward Minimum variance",
            "Frozen submitted weights (in-sample selection)",
        ]
    }
    decisions = []
    simple = log_to_simple(returns)
    for year in range(start_year, returns.index.max().year + 1):
        train = returns[returns.index.year < year]
        test = simple[simple.index.year == year]
        if len(train) < 3 * 252 or test.empty:
            continue
        mu, cov = asset_stats(train)
        weights = {
            "Walk-forward Maximum Sharpe": max_sharpe(
                mu, cov, annual_risk_free(rf, train.index)
            ),
            "Walk-forward Minimum variance": min_variance(cov),
            "Frozen submitted weights (in-sample selection)": final_weights(),
        }
        for name, w in weights.items():
            series[name].append(test @ w)
            decisions.append(
                {
                    "Year": year,
                    "Strategy": name,
                    "Training end": train.index.max().date().isoformat(),
                    **w.to_dict(),
                }
            )
    rows = []
    for name, chunks in series.items():
        if not chunks:
            raise ValueError("Not enough data for walk-forward evaluation")
        r = pd.concat(chunks)
        rows.append(
            {
                "Strategy": name,
                "Start": str(r.index.min().date()),
                "End": str(r.index.max().date()),
                "Annual return": annual_return(r),
                "Volatility": annual_volatility(r),
                "Sharpe": sharpe_ratio(r, annual_risk_free(rf, r.index)),
                "Max drawdown": max_drawdown(r),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(decisions)


def threshold_sensitivity(losses, alpha=0.99):
    """Refit POT at each percentile; sensitivity is not a confidence interval."""
    rows = []
    for q in (0.80, 0.85, 0.90, 0.925, 0.95, 0.975):
        u = float(losses.quantile(q))
        if (1 - alpha) > float((losses > u).mean()) + 1e-12:
            rows.append(
                {
                    "Threshold quantile": q,
                    "Threshold": u,
                    "Exceedances": int((losses > u).sum()),
                    "Shape": float("nan"),
                    "VaR": float("nan"),
                    "ES": float("nan"),
                    "Status": "Outside fitted tail",
                }
            )
            continue
        v, e, params = evt_var_es(losses, alpha=alpha, threshold=u)
        rows.append(
            {
                "Threshold quantile": q,
                "Threshold": u,
                "Exceedances": int((losses > u).sum()),
                "Status": "Fitted tail",
                "Shape": params["xi"],
                "VaR": v,
                "ES": e,
            }
        )
    return pd.DataFrame(rows)
