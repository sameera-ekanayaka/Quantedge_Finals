"""Post-report validation and research, separate from submitted results."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src import backtest
from src.advanced_validation import (
    alternative_threshold,
    evt_bootstrap,
    joint_bootstrap_risk,
)
from src.data import load_returns
from src.evt import evt_var_es
from src.portfolio import final_weights, portfolio_returns
from src.ui import get_settings

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "submission" / "advanced"
settings = get_settings()
st.title("Supplementary research and audit response")
st.warning(
    "Prepared after the submitted PDF. Original weights, reported "
    "results and archived PDFs remain unchanged. The new allocation "
    "and models below are supplementary alternatives, not results "
    "contained in that PDF."
)
st.markdown(
    "**Supplementary decision: ADJUST the allocation if the 15% "
    "scenario ceiling is mandatory.** The submitted allocation fails "
    "that ceiling. The alternative enforces the tested scenario and "
    "daily risk limits; it does not guarantee a 15% maximum drawdown "
    "or future losses below the limit."
)

st.header("1. Risk-constrained allocation alternative")
st.dataframe(pd.read_csv(OUT / "allocations.csv", index_col=0).style.format("{:.2%}"))
st.markdown(
    "Maximise in-sample Sharpe subject to full investment, original "
    "ETF bounds, 99% historical daily VaR ≤ 1.5%, ES ≤ 2.0%, and "
    "losses ≤ 15% in every historical replay and both assumed "
    "scenarios. Daily risk uses daily rebalancing; historical stress "
    "uses buy-and-hold window returns. These are distinct metrics. The"
    " alternative remains in sample and is not a validated replacement"
    " recommendation."
)
st.dataframe(
    pd.read_csv(OUT / "benchmark_kpis.csv").style.format(precision=3), hide_index=True
)
st.caption(
    "SPY is retained as the market comparator. The additional policy "
    "benchmark is 40% SPY / 60% AGG, rebalanced daily. Neither "
    "benchmark is a risk-free hurdle."
)

st.subheader("Alternative daily risk and attribution")
st.dataframe(
    pd.read_csv(OUT / "alternative_daily_risk.csv").style.format(
        {"Confidence": "{:.0%}", "VaR": "{:.3%}", "ES": "{:.3%}"}
    ),
    hide_index=True,
)
st.dataframe(
    pd.read_csv(OUT / "alternative_risk_budget.csv", index_col=0).style.format("{:.3%}")
)
st.dataframe(pd.read_csv(OUT / "alternative_backtests.csv"), hide_index=True)
st.caption(
    "Alternative allocation risk and backtests remain conditional on "
    "weights selected in sample. Feasibility under historical VaR/ES "
    "constraints does not guarantee every parametric risk estimate "
    "is below the same limit."
)
st.header("2. Distinct stress scenario and remedy check")
st.markdown(
    "The additional equity-crash/dollar-spike scenario assumes SPY "
    "−35%, EFA −40%, EEM −45%, AGG +5%, GLD −10%, XLE −40%, XLK −40%. "
    "It is an assumption, not a forecast or observed replay. Bonds "
    "rally while energy falls, unlike the inflation scenario. A "
    "6.5-point XLK-to-XLE shift is tested in both; no universal hedge "
    "is claimed."
)
st.dataframe(
    pd.read_csv(OUT / "stress_comparison.csv", index_col=0).style.format("{:.2%}")
)


@st.cache_data
def current_risk(alpha):
    r = load_returns()
    losses = -portfolio_returns(r, final_weights())
    v, e = joint_bootstrap_risk(r, final_weights(), alpha)
    threshold, rules = alternative_threshold(losses)
    if (1 - alpha) <= float((losses > threshold).mean()) + 1e-12:
        av, ae, _ = evt_var_es(losses, alpha, threshold=threshold)
    else:
        av, ae = float("nan"), float("nan")
    ci = evt_bootstrap(losses, alpha=alpha, quantile=min(0.90, alpha - 0.01))
    return (
        pd.DataFrame(
            [
                {"Model": "Joint ETF bootstrap", "VaR": v, "ES": e},
                {"Model": "Minimum KS threshold EVT", "VaR": av, "ES": ae},
            ]
        ),
        rules,
        ci,
    )


st.header("3. Joint Monte Carlo and EVT uncertainty")
risk, rules, ci = current_risk(settings.confidence)
st.caption(
    f"Current confidence: {settings.confidence:.0%}. Original submitted weights."
)
st.dataframe(risk.style.format({"VaR": "{:.3%}", "ES": "{:.3%}"}), hide_index=True)
st.markdown(
    "The joint ETF bootstrap resamples whole seven-ETF daily "
    "observations before combining weights. It preserves empirical "
    "cross-asset dependence, but not serial dependence or unseen "
    "crashes. It is distinct from the original parametric Student-t "
    "simulation, which remains available for reproducibility."
)
st.dataframe(
    rules.style.format(
        {"Quantile": "{:.1%}", "Threshold": "{:.3%}", "KS distance": "{:.4f}"}
    ),
    hide_index=True,
)
st.markdown(
    "Alternative rule: choose the smallest in-sample "
    "Kolmogorov–Smirnov CDF discrepancy over the listed quantiles, "
    "with at least 100 exceedances. This exploratory rule is not an "
    "independently validated optimal threshold or a valid KS "
    "hypothesis test after parameter fitting. Missing tail metrics "
    "mean the selected confidence lies below the fitted tail. The "
    "headline rule remains the 90th percentile."
)
st.dataframe(ci.style.format({"2.5%": "{:.3%}", "97.5%": "{:.3%}"}), hide_index=True)
st.caption(
    "95% percentile intervals from 200 IID bootstrap replicates, "
    "reselecting the threshold and refitting the GPD "
    "(89th percentile at 90% confidence, 90th otherwise to avoid body extrapolation) "
    "each time. Seed 42. Counts of invalid/nonfinite replicates are "
    "shown. IID sampling ignores volatility clustering and may "
    "understate uncertainty; these are not guarantees."
)

st.header("4. Conditional volatility models and independence")
st.markdown(
    "GARCH(1,1) Gaussian quasi-maximum-likelihood fit on the preceding"
    " 500 days, re-estimated every 21 trading days. Variance updates "
    "each day using only the last observed return. Filtered historical"
    " simulation uses empirical standardised residuals; GARCH-EVT fits"
    " their 90th-percentile loss tail. No forecast uses the return it "
    "predicts. Allocation selection remains in sample."
)
st.info(
    "The archived model comparison is at 99% confidence. Confidence "
    "controls above affect Section 3; the date control filters this "
    "99% backtest comparison. Original backtesting remains on its own "
    "page."
)
rows = []
paths = {
    "Historical": "historical_forecasts.csv",
    "Unfiltered EVT": "unfiltered_evt_forecasts.csv",
    "Joint ETF bootstrap": "joint_etf_bootstrap_forecasts.csv",
    "GARCH filtered HS": "garch_filtered_hs_forecasts.csv",
    "GARCH EVT": "garch_evt_forecasts.csv",
}
for name, file in paths.items():
    frame = pd.read_csv(OUT / file, index_col=0, parse_dates=True)
    frame = frame.loc[str(settings.backtest_start) : str(settings.backtest_end)]
    if not frame.empty:
        rows.append({"Model": name, **backtest.summarise(frame, 0.99)})
if rows:
    comparison = pd.DataFrame(rows)
    st.dataframe(
        comparison[
            [
                "Model",
                "days",
                "breaches",
                "expected",
                "kupiec_p",
                "ind_p",
                "cc_p",
                "zone_last_250",
            ]
        ],
        hide_index=True,
    )
    st.plotly_chart(
        px.bar(
            comparison,
            x="Model",
            y="ind_p",
            title="Breach-independence p-value (99% forecasts)",
        ),
        use_container_width=True,
    )
    st.caption(
        "Larger p-values do not prove independence; compare at a 5% test "
        "threshold. Passing coverage does not imply passing independence "
        "or joint conditional coverage. Small date windows produce weak "
        "tests. Forecasts use the same evaluation dates; conditional "
        "models are not claimed to eliminate clustering."
    )
else:
    st.info("No archived forecasts fall in the selected dates.")
st.markdown(
    "Reproduce with `python scripts/build_advanced_validation.py`. "
    "Methods, assumptions and limitations are documented in "
    "`docs/advanced_validation.md`. Submitted PDFs remain archived "
    "unchanged in `submission/`."
)
