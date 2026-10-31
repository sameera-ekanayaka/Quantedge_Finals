"""Page 4: Extreme Value Theory (EVT).

Owner: Praveen Madawalage
Layer 4: Extreme Value Theory (Peaks-Over-Threshold GPD)
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import config
from src.data import load_returns, load_risk_free
from src.evt import (
    evt_var_es,
    fit_gpd,
    gpd_qq_data,
    mean_excess_plot_data,
    parameter_stability_plot_data,
    select_threshold,
)
from src.portfolio import annual_risk_free, candidate_portfolios, portfolio_returns
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


def render_mep_chart(mep_df: pd.DataFrame, chosen_u: float) -> go.Figure:
    """Plot Mean Excess Plot with 95% confidence intervals and chosen threshold."""
    fig = go.Figure()

    # Confidence interval band
    fig.add_trace(
        go.Scatter(
            x=list(mep_df["threshold"] * 100) + list(mep_df["threshold"][::-1] * 100),
            y=list(mep_df["ci_upper"] * 100) + list(mep_df["ci_lower"][::-1] * 100),
            fill="toself",
            fillcolor="rgba(99, 110, 250, 0.15)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="95% Confidence Band",
        )
    )

    # Mean excess line
    fig.add_trace(
        go.Scatter(
            x=mep_df["threshold"] * 100,
            y=mep_df["mean_excess"] * 100,
            mode="lines+markers",
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=4),
            name="Mean Excess e(u)",
        )
    )

    # Vertical threshold line
    fig.add_vline(
        x=chosen_u * 100,
        line_width=2,
        line_dash="dash",
        line_color="#d62728",
        annotation_text=f"Chosen u = {chosen_u:.2%}",
        annotation_position="top right",
    )

    fig.update_layout(
        title="Mean Excess Function (Linearity indicates GPD domain of attraction)",
        xaxis_title="Threshold u (%)",
        yaxis_title="Mean Excess e(u) (%)",
        template="plotly_white",
        height=380,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def render_stability_chart(stab_df: pd.DataFrame, chosen_u: float) -> go.Figure:
    """Plot GPD shape parameter stability across thresholds with ±2 SE band."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=list(stab_df["threshold"] * 100) + list(stab_df["threshold"][::-1] * 100),
            y=list(stab_df["shape_xi"] + 2.0 * stab_df["shape_se"])
            + list((stab_df["shape_xi"] - 2.0 * stab_df["shape_se"])[::-1]),
            fill="toself",
            fillcolor="rgba(0, 204, 150, 0.15)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="±2 SE Band",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=stab_df["threshold"] * 100,
            y=stab_df["shape_xi"],
            mode="lines+markers",
            line=dict(color="#00cc96", width=2),
            marker=dict(size=4),
            name="Shape (ξ)",
        )
    )

    fig.add_vline(
        x=chosen_u * 100,
        line_width=2,
        line_dash="dash",
        line_color="#d62728",
        annotation_text=f"u = {chosen_u:.2%}",
        annotation_position="bottom right",
    )

    fig.update_layout(
        title="Parameter Stability Plot: Shape (ξ) vs. Threshold (±2 SE)",
        xaxis_title="Threshold u (%)",
        yaxis_title="Fitted Shape (ξ)",
        template="plotly_white",
        height=380,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def render_qq_chart(theoretical: np.ndarray, empirical: np.ndarray) -> go.Figure:
    """Plot QQ diagnostic comparing theoretical GPD quantiles with exceedances."""
    fig = go.Figure()

    # Convert to percent
    theo_pct = theoretical * 100.0
    emp_pct = empirical * 100.0

    max_val = max(float(theo_pct.max()), float(emp_pct.max())) * 1.05

    # 45 degree reference line
    fig.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode="lines",
            line=dict(color="#d62728", dash="dash", width=2),
            name="Theoretical Fit (y = x)",
        )
    )

    # Exceedance points
    fig.add_trace(
        go.Scatter(
            x=theo_pct,
            y=emp_pct,
            mode="markers",
            marker=dict(color="#636EFA", size=5, opacity=0.8),
            name="Exceedances",
        )
    )

    fig.update_layout(
        title="GPD Quantile-Quantile (Q-Q) Goodness-of-Fit",
        xaxis_title="Theoretical GPD Quantiles (%)",
        yaxis_title="Empirical Exceedances (%)",
        template="plotly_white",
        height=380,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


# ---------------- PAGE EXECUTION ----------------
st.title("Extreme Value Theory (EVT)")
st.caption(
    "Owner: Praveen Madawalage | Layer 4: Deep Tail Risk & Peaks-Over-Threshold (POT)"
)

settings = get_settings()
alpha = settings.confidence
fund_size = config.PORTFOLIO_VALUE_USD

returns_df, candidates = get_cached_data()

col_sel, col_fund = st.columns([2, 1])
with col_sel:
    portfolio_name = st.selectbox(
        "Candidate Portfolio",
        options=list(candidates.columns),
        index=(
            list(candidates.columns).index("Maximum Sharpe")
            if "Maximum Sharpe" in candidates.columns
            else 0
        ),
        help="Select a candidate portfolio to inspect its tail model.",
    )
with col_fund:
    st.metric(
        "Serendib Fund Size",
        format_currency(fund_size),
        help="University Endowment Capital Pool",
    )

weights = candidates[portfolio_name]
port_returns = portfolio_returns(returns_df, weights)
losses = -port_returns

# ---------------- SECTION 1: THRESHOLD SELECTION ----------------
st.subheader("1. Threshold Selection & Diagnostics")
st.markdown(
    "Under the Pickands-Balkema-de Haan Theorem, exceedances over a sufficiently high "
    "threshold $u$ converge in distribution to the **Generalized Pareto Distribution "
    "(GPD)**. We select the **90th percentile of losses** as the threshold, with the "
    "**Mean Excess Plot (MEP)** and **Parameter Stability Plot** serving as visual "
    "diagnostics to check consistency. The threshold is not automatically optimized "
    "by the algorithm; it is a percentile-based choice whose adequacy is assessed "
    "visually."
)

chosen_u, reason_text, comparison = select_threshold(losses, target_quantile=0.90)

mep_df = mean_excess_plot_data(losses, n_points=40)
stab_df = parameter_stability_plot_data(losses, n_points=35)

col_mep, col_stab = st.columns(2)
with col_mep:
    st.plotly_chart(render_mep_chart(mep_df, chosen_u), use_container_width=True)
with col_stab:
    st.plotly_chart(render_stability_chart(stab_df, chosen_u), use_container_width=True)

st.info(f"**Threshold Selection Justification:** {reason_text}")

# Rule comparison summary
col_r1, col_r2, col_r3, col_r4 = st.columns(4)
col_r1.metric("90th Percentile Rule", format_pct(comparison["rule_90_pct"]))
col_r2.metric("95th Percentile Rule", format_pct(comparison["rule_95_pct"]))
col_r3.metric("Selected Threshold (u)", format_pct(chosen_u))
col_r4.metric("Tail Exceedances (N_u)", f"{comparison['n_exceedances']} days")

st.markdown("---")

# ---------------- SECTION 2: GPD FIT & QQ DIAGNOSTICS ----------------
st.subheader("2. Generalized Pareto Distribution (GPD) Fit & Validation")

exceed = losses[losses > chosen_u] - chosen_u
xi, sigma = fit_gpd(exceed)
theo_q, emp_q = gpd_qq_data(losses, threshold=chosen_u, xi=xi, sigma=sigma)

col_fit_metrics, col_qq = st.columns([1, 2])

with col_fit_metrics:
    st.markdown("**Maximum Likelihood Fit Parameters:**")
    st.metric(
        "Tail Shape (ξ)",
        f"{xi:.4f}",
        help="ξ > 0 indicates a heavy-tailed Fréchet domain (fat tails).",
    )
    st.metric(
        "Scale Parameter (σ)",
        f"{sigma:.4f}",
        help="Scale of exceedance dispersion.",
    )
    st.metric(
        "Exceedance Probability (p_u)",
        format_pct(comparison["n_exceedances"] / len(losses)),
    )
    tail_desc = (
        "**Heavy-tailed (Fréchet Domain)**: Tail decays as a power law, "
        "confirming significant tail risk beyond Gaussian assumptions."
        if xi > 0
        else "**Thin-tailed (Weibull/Gumbel Domain)**"
    )
    st.markdown(f"**Tail Classification:**\n{tail_desc}")

with col_qq:
    st.plotly_chart(render_qq_chart(theo_q, emp_q), use_container_width=True)

st.markdown("---")

# ---------------- SECTION 3: EVT RISK ESTIMATES & COMPARISON ----------------
st.subheader(f"3. Tail Risk Estimates at {alpha:.0%} Confidence (1-Day Horizon)")

evt_var, evt_es, params = evt_var_es(losses, alpha=alpha, threshold=chosen_u)
hist_var, hist_es = var_es(port_returns, alpha=alpha, method="historical")
norm_var, norm_es = var_es(port_returns, alpha=alpha, method="normal")
stud_var, stud_es = var_es(port_returns, alpha=alpha, method="student_t")

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    f"EVT VaR ({alpha:.0%})",
    format_pct(evt_var),
    delta=f"{format_currency(evt_var * fund_size)} at risk",
    delta_color="inverse",
)
c2.metric(
    f"EVT Expected Shortfall ({alpha:.0%})",
    format_pct(evt_es),
    delta=f"{format_currency(evt_es * fund_size)} tail loss",
    delta_color="inverse",
)
c3.metric(
    "Tail Gap (ES - VaR)",
    format_pct(evt_es - evt_var),
    delta=f"{format_currency((evt_es - evt_var) * fund_size)} tail buffer",
    delta_color="inverse",
)
c4.metric(
    "EVT vs. Normal VaR Delta",
    format_pct(evt_var - norm_var),
    help="Additional capital at risk recognized by EVT relative to Gaussian model.",
)

# Comparison Table across all 4 methodologies
st.markdown("#### Model Comparison: Why Competing Methodologies Disagree")
comp_df = pd.DataFrame(
    [
        {
            "Methodology": "Parametric Normal (Gaussian)",
            f"1-Day VaR ({alpha:.0%})": format_pct(norm_var),
            "1-Day VaR ($)": format_currency(norm_var * fund_size),
            f"1-Day ES ({alpha:.0%})": format_pct(norm_es),
            "1-Day ES ($)": format_currency(norm_es * fund_size),
            "Tail Gap (ES - VaR)": format_pct(norm_es - norm_var),
            "Key Limitation": (
                "Underestimates deep tail losses due to thin exponential tails."
            ),
        },
        {
            "Methodology": "Parametric Student-t",
            f"1-Day VaR ({alpha:.0%})": format_pct(stud_var),
            "1-Day VaR ($)": format_currency(stud_var * fund_size),
            f"1-Day ES ({alpha:.0%})": format_pct(stud_es),
            "1-Day ES ($)": format_currency(stud_es * fund_size),
            "Tail Gap (ES - VaR)": format_pct(stud_es - stud_var),
            "Key Limitation": (
                "Assumes symmetric fat tails across entire distribution."
            ),
        },
        {
            "Methodology": "Historical Simulation",
            f"1-Day VaR ({alpha:.0%})": format_pct(hist_var),
            "1-Day VaR ($)": format_currency(hist_var * fund_size),
            f"1-Day ES ({alpha:.0%})": format_pct(hist_es),
            "1-Day ES ($)": format_currency(hist_es * fund_size),
            "Tail Gap (ES - VaR)": format_pct(hist_es - hist_var),
            "Key Limitation": (
                "Bounded by history; cannot extrapolate beyond worst observed day."
            ),
        },
        {
            "Methodology": "Extreme Value Theory (POT / GPD)",
            f"1-Day VaR ({alpha:.0%})": format_pct(evt_var),
            "1-Day VaR ($)": format_currency(evt_var * fund_size),
            f"1-Day ES ({alpha:.0%})": format_pct(evt_es),
            "1-Day ES ($)": format_currency(evt_es * fund_size),
            "Tail Gap (ES - VaR)": format_pct(evt_es - evt_var),
            "Key Limitation": (
                "Requires high threshold and sufficient exceedances for MLE stability."
            ),
        },
    ]
)
st.dataframe(comp_df, hide_index=True, use_container_width=True)

with st.expander("Investment Committee Briefing: Why EVT Matters for Serendib"):
    st.markdown(
        "- **The Blindspot of Normal VaR:**\n"
        "  Gaussian models assume extreme losses are virtually impossible. At 99% "
        "confidence, Normal VaR understates loss by hundreds of thousands of dollars.\n"
        "- **The Blindspot of Historical Simulation:**\n"
        "  Historical simulation is constrained to the past sample. If the worst "
        "day in history was -5.8%, it cannot imagine a -7.5% crash.\n"
        "- **Why Peaks-Over-Threshold GPD Wins:**\n"
        "  EVT models the mathematical tail directly. It indicates that the Serendib "
        "endowment's portfolio exhibits fat-tailed Fréchet behavior (ξ > 0), "
        "allowing the committee to provision realistic capital buffers."
    )
