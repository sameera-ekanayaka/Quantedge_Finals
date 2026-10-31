import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import config, stress
from src.data import load_returns, load_risk_free
from src.kpis import (
    annual_return,
    annual_volatility,
    drawdown_series,
    kpi_table,
    max_drawdown,
)
from src.portfolio import (
    BOUNDS,
    annual_risk_free,
    asset_stats,
    candidate_kpis,
    candidate_portfolios,
    efficient_frontier,
    final_weights,
    min_es,
    portfolio_es,
    portfolio_returns,
    risk_shares,
)
from src.ui import get_settings

FINAL = "Final recommendation (Maximum Sharpe)"
PALETTE = px.colors.qualitative.Set2


@st.cache_data(show_spinner="Building the candidate portfolios...")
def load_everything():
    returns = load_returns()
    rf = annual_risk_free(load_risk_free(), returns.index)
    candidates = candidate_portfolios(returns, rf)
    candidates["Minimum ES"] = min_es(returns)
    return returns, rf, candidates


@st.cache_data(show_spinner="Drawing the efficient frontier...")
def load_frontier(returns):
    mu, cov = asset_stats(returns)
    return mu, cov, efficient_frontier(mu, cov)


@st.cache_data(show_spinner="Running the risk and stress tests...")
def load_comparison(returns, candidates, alpha):
    rows = {}
    for name in candidates.columns:
        w = candidates[name]
        p = portfolio_returns(returns, w)
        row = {
            "Annual return": annual_return(p),
            "Annual volatility": annual_volatility(p),
            "Max drawdown": max_drawdown(p),
            f"1-day ES at {alpha:.0%}": portfolio_es(returns, w, alpha),
        }
        row.update(stress.stress_table(returns, w)["return"].to_dict())
        rows[name] = row
    return pd.DataFrame(rows).T


def risk_return(w, mu, cov):
    v = w.reindex(mu.index).to_numpy()
    vol = float(np.sqrt(v @ cov.to_numpy() @ v))
    return vol, float(mu.to_numpy() @ v)


st.title("Portfolio")
st.caption("Owner: Imasha Karunathilaka")

settings = get_settings()
alpha = settings.confidence
fund = config.PORTFOLIO_VALUE_USD
returns, rf, candidates = load_everything()

portfolios = {FINAL: final_weights()}
portfolios.update({name: candidates[name] for name in candidates.columns})
choice = st.selectbox("Choose a portfolio to inspect", list(portfolios))
weights = portfolios[choice]
port = portfolio_returns(returns, weights)
spy = np.exp(returns["SPY"]) - 1
kpi = kpi_table(port, spy, rf)
es = portfolio_es(returns, weights, alpha)

cols = st.columns(5)
cols[0].metric(
    "Annual return", f"{kpi['Annual return']:.1%}", help="Historical, in-sample"
)
cols[1].metric("Annual volatility", f"{kpi['Annual volatility']:.1%}")
cols[2].metric("Sharpe ratio", f"{kpi['Sharpe']:.2f}")
cols[3].metric("Max drawdown", f"{kpi['Max drawdown']:.1%}")
cols[4].metric(
    f"1-day ES at {alpha:.0%}",
    f"USD {es * fund:,.0f}",
    help=(
        f"{es:.2%} of the fund. This is the average loss on the worst "
        f"{1 - alpha:.0%} of days."
    ),
)

tab_w, tab_g, tab_f, tab_c = st.tabs(
    ["Weights and risk", "Growth and drawdown", "Efficient frontier", "Compare"]
)

with tab_w:
    _, cov_all = asset_stats(returns)
    shares = risk_shares(weights, cov_all)
    left, right = st.columns(2)

    wdf = pd.DataFrame({"ETF": weights.index, "Weight": weights.to_numpy()})
    fig = px.bar(
        wdf,
        x="Weight",
        y="ETF",
        orientation="h",
        color="ETF",
        color_discrete_sequence=PALETTE,
        text=wdf["Weight"].map("{:.1%}".format),
        title="Weights",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False, xaxis_tickformat=".0%", xaxis_range=[0, 0.75])
    left.plotly_chart(fig, width="stretch")

    sdf = pd.DataFrame({"ETF": shares.index, "Share": shares.to_numpy()})
    fig = px.bar(
        sdf,
        x="Share",
        y="ETF",
        orientation="h",
        color="ETF",
        color_discrete_sequence=PALETTE,
        text=sdf["Share"].map("{:.1%}".format),
        title="Share of portfolio variance",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False, xaxis_tickformat=".0%", xaxis_range=[0, 0.75])
    right.plotly_chart(fig, width="stretch")

    st.caption(
        "If an ETF's risk share is bigger than its weight, it is riskier "
        "than its size suggests."
    )
    with st.expander("Mandate limits"):
        limits = pd.DataFrame(BOUNDS, index=["Minimum", "Maximum"]).T
        limits["Chosen"] = weights
        st.dataframe(limits.style.format("{:.1%}"), width="stretch")

with tab_g:
    wealth = (1 + port).cumprod() * fund
    spy_wealth = (1 + spy).cumprod() * fund
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=wealth.index, y=wealth, name=choice, line=dict(width=3)))
    fig.add_trace(
        go.Scatter(
            x=spy_wealth.index, y=spy_wealth, name="SPY only", line=dict(dash="dot")
        )
    )
    fig.update_layout(
        title="Growth of USD 10m",
        yaxis_tickprefix="USD ",
        yaxis_tickformat=",.0f",
    )
    st.plotly_chart(fig, width="stretch")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=port.index,
            y=drawdown_series(port),
            name=choice,
            fill="tozeroy",
            line=dict(width=1),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=spy.index,
            y=drawdown_series(spy),
            name="SPY only",
            line=dict(dash="dot"),
        )
    )
    fig.update_layout(title="Drawdown from the previous peak", yaxis_tickformat=".0%")
    st.plotly_chart(fig, width="stretch")

with tab_f:
    mu, cov, frontier = load_frontier(returns)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frontier["Volatility"],
            y=frontier["Return"],
            mode="lines",
            name="Efficient frontier",
            line=dict(width=3),
        )
    )
    for i, name in enumerate(candidates.columns):
        vol, ret = risk_return(candidates[name], mu, cov)
        fig.add_trace(
            go.Scatter(
                x=[vol],
                y=[ret],
                mode="markers",
                name=name,
                marker=dict(size=12, color=PALETTE[i % len(PALETTE)]),
            )
        )
    vol, ret = risk_return(weights, mu, cov)
    fig.add_trace(
        go.Scatter(
            x=[vol],
            y=[ret],
            mode="markers",
            name="Selected",
            marker=dict(size=20, symbol="star", color="black"),
        )
    )
    fig.update_layout(
        title="Best return for each level of risk",
        xaxis_title="Yearly volatility",
        yaxis_title="Yearly return (average)",
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "The frontier uses the average yearly return, so it is a little higher "
        "than the compound return shown in the numbers above."
    )

with tab_c:
    st.subheader("Return against risk")
    table = load_comparison(returns, candidates, alpha)
    st.dataframe(table.style.format("{:.1%}"), width="stretch")
    st.subheader("Full KPI table")
    kpis = candidate_kpis(returns, candidates, rf)
    st.dataframe(kpis.style.format("{:.3f}"), width="stretch")

st.caption(
    "All results use the full 2004 to 2026 history. The weights were chosen on "
    "the same data, so the returns are historical and likely too optimistic."
)
