"""Reproduce post-report model extensions; never modifies submitted PDFs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd

from src import backtest, config
from src.advanced_validation import (
    alternative_threshold,
    conditional_backtests,
    constrained_sharpe,
    evt_bootstrap,
    joint_bootstrap_backtest,
    joint_bootstrap_risk,
    stress_vectors,
)
from src.data import load_returns, load_risk_free
from src.evt import evt_var_es
from src.kpis import kpi_table
from src.portfolio import annual_risk_free, final_weights, portfolio_returns
from src.risk_budget import risk_budget
from src.var_es import var_es

out = Path(__file__).resolve().parents[1] / "submission" / "advanced"
out.mkdir(parents=True, exist_ok=True)
r = load_returns()
rf = annual_risk_free(load_risk_free(), r.index)
w = final_weights()
p = portfolio_returns(r, w)
new = constrained_sharpe(r, rf)
pd.DataFrame({"Submitted": w, "Risk-constrained alternative": new}).to_csv(
    out / "allocations.csv"
)
policy_weights = pd.Series(
    {"SPY": 0.4, "EFA": 0.0, "EEM": 0.0, "AGG": 0.6, "GLD": 0.0, "XLE": 0.0, "XLK": 0.0}
)
policy = portfolio_returns(r, policy_weights)
rows = []
for label, series in [
    ("Submitted allocation", p),
    ("Risk-constrained alternative", portfolio_returns(r, new)),
    ("40% SPY / 60% AGG policy", policy),
]:
    rows.append(
        {
            "Portfolio": label,
            "Benchmark": "SPY",
            **kpi_table(series, np.expm1(r["SPY"]), rf).to_dict(),
        }
    )
    rows.append(
        {
            "Portfolio": label,
            "Benchmark": "40% SPY / 60% AGG",
            **kpi_table(series, policy, rf).to_dict(),
        }
    )
pd.DataFrame(rows).to_csv(out / "benchmark_kpis.csv", index=False)
shocks = stress_vectors(r)
remedy = w.copy()
remedy["XLK"] -= 0.065
remedy["XLE"] += 0.065
pd.DataFrame(
    {
        "Submitted": shocks @ w,
        "Risk-constrained alternative": shocks @ new,
        "XLK to XLE remedy": shocks @ remedy,
    }
).to_csv(out / "stress_comparison.csv")
losses = -p
u, rules = alternative_threshold(losses)
rules.to_csv(out / "threshold_rule.csv", index=False)
ci = evt_bootstrap(losses)
ci.to_csv(out / "evt_bootstrap.csv", index=False)
v, e, params = evt_var_es(losses, 0.99, threshold=u)
vj, ej = joint_bootstrap_risk(r, w)
pd.DataFrame(
    [
        {"Model": "Joint ETF bootstrap", "VaR": vj, "ES": ej},
        {
            "Model": "Alternative threshold EVT",
            "VaR": v,
            "ES": e,
            "Threshold": u,
            "Shape": params["xi"],
        },
    ]
).to_csv(out / "additional_risk.csv", index=False)
frames, summary = conditional_backtests(p)
print("Conditional fits completed", flush=True)
frames["Historical"] = backtest.run_backtest(p, "historical", 0.99)
frames["Unfiltered EVT"] = backtest.run_backtest(p, "evt", 0.99)
frames["Joint ETF bootstrap"] = joint_bootstrap_backtest(r, w)
rows = []
for name, frame in frames.items():
    frame.to_csv(out / (name.lower().replace(" ", "_") + "_forecasts.csv"))
    evaluated = frame.loc["2008-01-01":]
    rows.append({"Model": name, **backtest.summarise(evaluated, 0.99)})
summary = pd.DataFrame(rows)
summary.to_csv(out / "backtest_summary.csv", index=False)
print("ALLOCATION", new.to_dict(), flush=True)
print(
    summary[["Model", "days", "breaches", "kupiec_p", "ind_p", "cc_p"]].to_string(
        index=False
    ),
    flush=True,
)

# Recompute all daily models and risk attribution for the supplementary mix.

new_returns = portfolio_returns(r, new)
risk_rows = []
for alpha in (0.95, 0.99):
    for key, label in config.VAR_METHODS.items():
        v, e = var_es(new_returns, alpha, key)
        risk_rows.append({"Confidence": alpha, "Model": label, "VaR": v, "ES": e})
    v, e, _ = evt_var_es(-new_returns, alpha, threshold=None)
    risk_rows.append({"Confidence": alpha, "Model": "EVT", "VaR": v, "ES": e})
    v, e = joint_bootstrap_risk(r, new, alpha)
    risk_rows.append(
        {"Confidence": alpha, "Model": "Joint ETF bootstrap", "VaR": v, "ES": e}
    )
pd.DataFrame(risk_rows).to_csv(out / "alternative_daily_risk.csv", index=False)
risk_budget(r, new, alpha=0.99, method="historical").to_csv(
    out / "alternative_risk_budget.csv"
)
# Original forecast schedule and dates; selection remains in sample.
new_rows = []
for method in ["historical", "normal", "student_t", "monte_carlo", "evt"]:
    result = backtest.run_backtest(new_returns, method, 0.99).loc["2008-01-01":]
    new_rows.append({"Model": method, **backtest.summarise(result, 0.99)})
pd.DataFrame(new_rows).to_csv(out / "alternative_backtests.csv", index=False)
