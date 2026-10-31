import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import config, stress
from src.data import load_returns, load_risk_free
from src.portfolio import annual_risk_free, candidate_portfolios, final_weights


@st.cache_data
def load_candidates() -> tuple[pd.DataFrame, pd.DataFrame]:
    returns = load_returns()
    rf = annual_risk_free(load_risk_free(), returns.index)
    candidates = candidate_portfolios(returns, rf)
    candidates["Maximum Sharpe"] = final_weights()
    return returns, candidates


def impact_chart(table: pd.DataFrame, loss_limit: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=table.index,
            y=table["return"].astype(float),
            name="Portfolio",
            marker_color="#1565c0",
        )
    )
    fig.add_trace(
        go.Bar(
            x=table.index,
            y=table["spy_return"].astype(float),
            name="SPY only",
            marker_color="#b0bec5",
        )
    )
    fig.add_hline(
        y=-loss_limit,
        line_dash="dash",
        line_color="#c62828",
        annotation_text=f"Loss limit {loss_limit:.0%}",
    )
    fig.update_layout(
        barmode="group", yaxis_tickformat=".0%", height=380, margin={"t": 10}
    )
    return fig


st.title("Stress tests")
st.markdown(
    "What would the portfolio have lost in the worst markets of the last twenty "
    "years, and in a crisis we design ourselves where stocks and bonds fall "
    "together? Historical replays use real returns. Our own scenario is an "
    "assumption and is labelled as one."
)

returns, candidates = load_candidates()
col_portfolio, col_limit = st.columns(2)
portfolio = col_portfolio.selectbox(
    "Portfolio",
    list(candidates.columns),
    index=list(candidates.columns).index("Maximum Sharpe"),
)
loss_limit = col_limit.slider(
    "Crisis loss limit",
    min_value=0.05,
    max_value=0.30,
    value=stress.DEFAULT_LOSS_LIMIT,
    step=0.01,
    format="%.2f",
    help=(
        "Revised scenario-loss proposal: 18%. "
        "This is not a drawdown cap or a future guarantee."
    ),
)
weights = candidates[portfolio]

with st.expander("Our scenario: inflation shock (edit the assumptions)"):
    st.caption(
        "An inflation surprise pushes rates up about 250bp. Stocks and bonds fall "
        "together, which is the case where a 60/40 style hedge fails."
    )
    shocks = {}
    for ticker in config.TICKERS:
        default = stress.INFLATION_SHOCK[ticker]
        left, right = st.columns([1, 3])
        shocks[ticker] = (
            left.number_input(
                ticker,
                min_value=-80.0,
                max_value=80.0,
                value=default * 100,
                step=1.0,
                format="%.0f",
                key=f"shock_{ticker}",
            )
            / 100
        )
        right.caption(stress.INFLATION_SHOCK_REASONS[ticker])
    st.caption(
        "AGG's -15% shock is the first-order duration approximation -DΔy: "
        "duration 6 × a parallel 250bp yield rise. It ignores convexity, spread "
        "changes, changing duration and the path of rates, so it is a scenario "
        "assumption rather than a bond-price forecast."
    )

scenarios = {
    "Inflation shock (our scenario)": shocks,
    "Equity crash and dollar spike (assumption)": stress.DOLLAR_CRASH_SHOCK,
}
table = stress.stress_table(returns, weights, scenarios=scenarios)

st.subheader("Impact on the USD 10m portfolio")
worst = table["return"].astype(float).idxmin()
m1, m2, m3 = st.columns(3)
m1.metric("Worst scenario", worst)
m2.metric(
    "Loss in worst scenario",
    f"{table.at[worst, 'return']:.1%}",
    f"USD {table.at[worst, 'pnl_usd']:,.0f}",
    delta_color="off",
)
breaks = table["return"].astype(float) < -loss_limit
m3.metric("Scenarios over the loss limit", f"{int(breaks.sum())} of {len(table)}")

shown = table.rename(
    columns={
        "type": "Type",
        "start": "From",
        "end": "To",
        "days": "Days",
        "return": "Portfolio return",
        "pnl_usd": "P&L (USD)",
        "max_drawdown": "Max drawdown",
        "worst_day": "Worst day",
        "worst_day_date": "Worst day date",
        "spy_return": "SPY return",
    }
)
st.dataframe(
    shown.style.format(
        {
            "Portfolio return": "{:.1%}",
            "P&L (USD)": "{:,.0f}",
            "Max drawdown": "{:.1%}",
            "Worst day": "{:.2%}",
            "SPY return": "{:.1%}",
        },
        na_rep="",
    )
)
st.plotly_chart(impact_chart(table, loss_limit))
st.caption(
    "Replays are buy and hold from the close before the first day: the weights "
    "drift with prices and nothing is rebalanced mid-crisis. Max drawdown is the "
    "deepest fall inside the period, which can be worse than the end result."
)

st.subheader("Inside each crisis")
period = st.selectbox("Crisis", list(config.STRESS_PERIODS))
start, end = config.STRESS_PERIODS[period]
path = stress.portfolio_path(returns, weights, start, end)
spy_only = pd.Series({config.BENCHMARK: 1.0}).reindex(config.TICKERS, fill_value=0.0)
spy_path = stress.portfolio_path(returns, spy_only, start, end)
left, right = st.columns(2)
with left:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=path.index, y=path - 1, name=portfolio))
    fig.add_trace(go.Scatter(x=spy_path.index, y=spy_path - 1, name="SPY only"))
    fig.update_layout(
        yaxis_tickformat=".0%",
        height=340,
        margin={"t": 30},
        title="Cumulative return",
    )
    st.plotly_chart(fig)
with right:
    contrib = stress.contributions(returns, weights, start, end)
    fig = go.Figure(
        go.Bar(
            x=contrib.index,
            y=contrib,
            marker_color=["#c62828" if v < 0 else "#2e7d32" for v in contrib],
        )
    )
    fig.update_layout(
        yaxis_tickformat=".1%",
        height=340,
        margin={"t": 30},
        title="Contribution by ETF (adds up to the total)",
    )
    st.plotly_chart(fig)

st.subheader("Reverse stress test")
multiple = stress.reverse_stress(weights, shocks, loss_limit)
if multiple == float("inf"):
    st.write("The scenario as set makes money, so it can never hit the limit.")
elif multiple < 1:
    st.error(
        f"Our scenario already breaks the {loss_limit:.0%} limit. It would only "
        f"need to be {multiple:.2f} times as severe."
    )
else:
    st.success(
        f"Our scenario would have to be {multiple:.2f} times as severe before the "
        f"portfolio lost {loss_limit:.0%}."
    )
st.caption("Assumes every shock scales up in proportion.")

st.subheader("Every candidate under every scenario")
across = stress.stress_across_candidates(returns, candidates, scenarios=scenarios)
st.dataframe(across.style.format("{:.1%}"))
st.caption(
    "One input to the return against risk trade-off: a more defensive mix should "
    "lose less in every row."
)
