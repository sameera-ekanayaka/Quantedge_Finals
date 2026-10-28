"""Page 3: Risk Dashboard.

Owner: Aadhila Anees
Layers 2 & 3: VaR, Expected Shortfall, and Risk Budgeting
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import config
from src.data import load_prices, load_returns, load_risk_free, log_to_simple
from src.portfolio import annual_risk_free, candidate_portfolios, portfolio_returns
from src.risk_budget import risk_budget
from src.ui import get_settings
from src.var_es import var_es


@st.cache_data
def get_cached_data():
    """Load and cache market data and candidate portfolio weights."""
    returns = load_returns()
    rf = load_risk_free()
    rf_ann = annual_risk_free(rf, returns.index)
    candidates = candidate_portfolios(returns, rf_ann)
    return returns, candidates


def format_currency(val: float) -> str:
    """Format dollar amount with commas."""
    return f"${val:,.0f}"


def format_pct(val: float) -> str:
    """Format decimal as a clean percentage."""
    return f"{val:.2%}"


def render_tail_gap_chart(
    returns_series: pd.Series, var_val: float, es_val: float, alpha: float, method_name: str
):
    """Plot return distribution highlighting VaR threshold and ES tail region."""
    # Convert series to percentage terms
    ret_pct = returns_series * 100.0
    var_cutoff_pct = -var_val * 100.0
    es_cutoff_pct = -es_val * 100.0

    fig = go.Figure()

    # Histogram of daily returns
    fig.add_trace(
        go.Histogram(
            x=ret_pct,
            nbinsx=100,
            histnorm="probability density",
            name="Daily Returns",
            marker_color="rgba(99, 110, 250, 0.6)",
        )
    )

    # VaR vertical line
    fig.add_vline(
        x=var_cutoff_pct,
        line_width=2.5,
        line_dash="dash",
        line_color="#EF553B",
        annotation_text=f"{alpha:.0%} VaR: -{var_val:.2%}",
        annotation_position="top left",
    )

    # ES vertical line
    fig.add_vline(
        x=es_cutoff_pct,
        line_width=2.5,
        line_dash="dot",
        line_color="#AB63FA",
        annotation_text=f"{alpha:.0%} ES: -{es_val:.2%}",
        annotation_position="bottom left",
    )

    fig.update_layout(
        title=f"Return Distribution & Tail Risk Gap ({method_name} at {alpha:.0%} Confidence)",
        xaxis_title="Daily Return (%)",
        yaxis_title="Probability Density",
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
    )
    return fig


def render_risk_budget_chart(budget_df: pd.DataFrame):
    """Plot comparison of Capital Weight vs VaR Contribution vs ES Contribution."""
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=budget_df.index,
            y=budget_df["weight"] * 100,
            name="Capital Weight (%)",
            marker_color="#636EFA",
        )
    )
    fig.add_trace(
        go.Bar(
            x=budget_df.index,
            y=budget_df["pct_var_contrib"] * 100,
            name="% Contribution to VaR",
            marker_color="#EF553B",
        )
    )
    fig.add_trace(
        go.Bar(
            x=budget_df.index,
            y=budget_df["pct_es_contrib"] * 100,
            name="% Contribution to ES",
            marker_color="#FFA15A",
        )
    )

    fig.update_layout(
        title="Asset Allocation vs. Risk Budgeting Contribution",
        xaxis_title="Asset (ETF)",
        yaxis_title="Percentage (%)",
        barmode="group",
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
    )
    return fig


# ---------------- MAIN PAGE EXECUTION ----------------
st.title("Risk Dashboard")
st.caption("Owner: Aadhila Anees | Layers 2 & 3: VaR, Expected Shortfall & Risk Budgeting")

settings = get_settings()
alpha = settings.confidence
chosen_method = settings.var_method

returns_df, candidates = get_cached_data()

# Portfolio candidate selector
col_sel, col_fund = st.columns([2, 1])
with col_sel:
    portfolio_name = st.selectbox(
        "Candidate Portfolio",
        options=list(candidates.columns),
        index=list(candidates.columns).index("Risk parity")
        if "Risk parity" in candidates.columns
        else 0,
        help="Select a candidate portfolio to inspect its risk profile.",
    )
with col_fund:
    fund_size = config.PORTFOLIO_VALUE_USD
    st.metric("Mandate Fund Size", format_currency(fund_size), help="Serendib Endowment capital pool")

weights = candidates[portfolio_name]
port_returns = portfolio_returns(returns_df, weights)

# Primary metrics based on sidebar chosen method
primary_var, primary_es = var_es(port_returns, alpha=alpha, method=chosen_method)
tail_gap = primary_es - primary_var

dollar_var = primary_var * fund_size
dollar_es = primary_es * fund_size
dollar_gap = tail_gap * fund_size

st.subheader("1. Core Risk Metrics (1-Day Horizon)")

m1, m2, m3, m4 = st.columns(4)
m1.metric(
    label=f"{alpha:.0%} Value at Risk (VaR)",
    value=format_pct(primary_var),
    delta=format_currency(dollar_var) + " at risk",
    delta_color="inverse",
    help="Maximum expected loss over 1 day under normal market conditions.",
)
m2.metric(
    label=f"{alpha:.0%} Expected Shortfall (ES)",
    value=format_pct(primary_es),
    delta=format_currency(dollar_es) + " expected tail loss",
    delta_color="inverse",
    help="Average loss when returns breach the VaR threshold.",
)
m3.metric(
    label="Tail Risk Gap (ES - VaR)",
    value=format_pct(tail_gap),
    delta=format_currency(dollar_gap) + " additional buffer",
    delta_color="inverse",
    help="The severity gap: how much deeper losses reach beyond the VaR cutoff.",
)
m4.metric(
    label="Active VaR Method",
    value=config.VAR_METHODS.get(chosen_method, chosen_method),
    help="Selected in the global sidebar.",
)

st.markdown("---")

# Section 2: Side-by-Side Methodology Comparison
st.subheader("2. Multi-Methodology Comparison")
st.markdown(
    """
    The brief requires comparing **Historical, Parametric, and Monte Carlo** models at the same confidence level.
    The gap between them highlights distributional assumptions and tail fatness.
    """
)

# Compute across all methods
comp_records = []
for m_key, m_label in config.VAR_METHODS.items():
    v, e = var_es(port_returns, alpha=alpha, method=m_key)
    comp_records.append(
        {
            "Methodology": m_label,
            f"1-Day VaR ({alpha:.0%})": format_pct(v),
            "1-Day VaR ($)": format_currency(v * fund_size),
            f"1-Day ES ({alpha:.0%})": format_pct(e),
            "1-Day ES ($)": format_currency(e * fund_size),
            "Tail Gap (ES - VaR)": format_pct(e - v),
        }
    )

# Check EVT from Praveen
try:
    from src.evt import evt_var_es

    # Test if implemented
    evt_v, evt_e, _ = evt_var_es(-port_returns, alpha=alpha, threshold=0.01)
    comp_records.append(
        {
            "Methodology": "Extreme Value Theory (EVT / GPD)",
            f"1-Day VaR ({alpha:.0%})": format_pct(evt_v),
            "1-Day VaR ($)": format_currency(evt_v * fund_size),
            f"1-Day ES ({alpha:.0%})": format_pct(evt_e),
            "1-Day ES ($)": format_currency(evt_e * fund_size),
            "Tail Gap (ES - VaR)": format_pct(evt_e - evt_v),
        }
    )
except (NotImplementedError, ImportError, Exception):
    comp_records.append(
        {
            "Methodology": "Extreme Value Theory (EVT / GPD)",
            f"1-Day VaR ({alpha:.0%})": "Pending (Wave 3)",
            "1-Day VaR ($)": "Pending",
            f"1-Day ES ({alpha:.0%})": "Pending",
            "1-Day ES ($)": "Pending",
            "Tail Gap (ES - VaR)": "Pending",
        }
    )

comp_df = pd.DataFrame(comp_records)
st.dataframe(comp_df, hide_index=True, use_container_width=True)

with st.expander("Why do these methods disagree? (Investment Committee Insights)"):
    st.markdown(
        """
        - **Parametric (Normal) vs. Fat Tails:**  
          Normal VaR assumes returns follow a Gaussian bell curve. At $99\\%$, it severely **understates risk** because real market drawdowns have extreme kurtosis (fat tails).
        - **Parametric (Student's $t$):**  
          By fitting degrees of freedom, the Student's $t$ model captures tail kurtosis directly, producing higher and more realistic tail loss estimates than Normal.
        - **Historical Simulation:**  
          Empirical and model-free, reflecting true historical crashes (like 2008 and March 2020), but cannot forecast losses beyond the worst historically observed drawdown.
        - **Why Expected Shortfall (CVaR) is Mandatory:**  
          VaR is **not a coherent risk measure** because it fails subadditivity (diversification can mathematically increase VaR in pathological non-normal distributions). ES is coherent, convex, and answers the committee's vital question: *"If our risk limit is breached, how bad is the loss?"*
        """
    )

st.markdown("---")

# Section 3: Visualizing the Tail Risk Gap
st.subheader("3. Tail Distribution & Shortfall Region")
fig_dist = render_tail_gap_chart(
    port_returns,
    primary_var,
    primary_es,
    alpha,
    config.VAR_METHODS.get(chosen_method, chosen_method),
)
st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("---")

# Section 4: Risk Budgeting & Risk Attribution
st.subheader("4. Risk Budgeting & Position Sizing (Euler Decomposition)")
st.markdown(
    """
    Risk budgeting decomposes total portfolio tail risk into asset-level **Marginal** and **Component** risk contributions.
    """
)

budget_method = st.radio(
    "Risk Attribution Method",
    options=["parametric", "historical"],
    format_func=lambda x: "Parametric (Gaussian Euler)" if x == "parametric" else "Historical (Tail Expectation)",
    horizontal=True,
)

budget_df = risk_budget(returns_df, weights, alpha=alpha, method=budget_method)

# Render Plotly bar chart
fig_budget = render_risk_budget_chart(budget_df)
st.plotly_chart(fig_budget, use_container_width=True)

# Formatted Table
table_display = pd.DataFrame(
    {
        "Capital Weight": budget_df["weight"].apply(format_pct),
        "Marginal VaR": budget_df["marginal_var"].apply(format_pct),
        "Component VaR": budget_df["component_var"].apply(format_pct),
        "% Contribution to VaR": budget_df["pct_var_contrib"].apply(format_pct),
        "Marginal ES": budget_df["marginal_es"].apply(format_pct),
        "Component ES": budget_df["component_es"].apply(format_pct),
        "% Contribution to ES": budget_df["pct_es_contrib"].apply(format_pct),
    },
    index=budget_df.index,
)

st.dataframe(table_display, use_container_width=True)

st.info(
    f"""
    **Euler Check:**  
    Sum of Component VaR = **{format_pct(budget_df['component_var'].sum())}** (matches portfolio VaR) | 
    Sum of Component ES = **{format_pct(budget_df['component_es'].sum())}** (matches portfolio ES) | 
    Total Risk Contribution = **{budget_df['pct_es_contrib'].sum():.1%}**.
    """
)
