"""Page 7: Assumptions & Limitations.

Owner: Praveen Madawalage
Non-negotiable, explicitly graded section covering all analytical layers.
"""

import streamlit as st

from src.ui import get_settings

st.title("Assumptions & Limitations")
st.warning(
    "Weights were selected in sample. Weight bounds are enforced "
    "during optimisation; VaR, ES and stress limits are checked "
    "afterward. The inflation scenario loses 17.2%, exceeding the"
    " proposed 15% monitoring limit. Acceptance requires an "
    "explicit exception."
)

settings = get_settings()

st.markdown(
    "Every quantitative financial model is an abstraction of "
    "reality. For the "
    "**Serendib University Endowment Fund**, where avoiding large"
    " losses "
    "takes precedence over maximizing gains, institutional "
    "credibility demands "
    "complete transparency regarding our underlying assumptions, "
    "mathematical "
    "approximations, and known failure modes."
)

tab_overview, tab_port, tab_data, tab_var, tab_evt, tab_backtest, tab_stress = st.tabs(
    [
        "Executive Summary",
        "1. Portfolio & Mandate",
        "2. Data & Hygiene",
        "3. VaR & Expected Shortfall",
        "4. Extreme Value Theory",
        "5. Backtesting & Validation",
        "6. Stress Scenarios",
    ]
)

# ---------------- TAB 0: EXECUTIVE SUMMARY ----------------
with tab_overview:
    st.subheader("Model Risk Governance Matrix")
    st.markdown(
        "A structured overview of core assumptions, their "
        "vulnerabilities, "
        "and institutional mitigations:"
    )

    summary_data = [
        {
            "Area": "Portfolio Mandate",
            "Core Assumption": "Long-only, no leverage, daily costless rebalancing",
            "Primary Vulnerability": ("Transaction costs, illiquidity during crashes"),
            "Committee Defense": (
                "Daily rebalancing assumed; quarterly sensitivity reported separately"
            ),
        },
        {
            "Area": "Data Hygiene",
            "Core Assumption": (
                "Split/dividend-adjusted close reflects true investable return"
            ),
            "Primary Vulnerability": (
                "Stale prices, holiday calendar desynchronization"
            ),
            "Committee Defense": (
                "Forward-fill capped at 3 days; cleaning audit verifies 0 fill days"
            ),
        },
        {
            "Area": "VaR & ES",
            "Core Assumption": (
                "Returns are identically distributed with constant parameters"
            ),
            "Primary Vulnerability": (
                "Volatility clustering; Normal VaR understates tail risk"
            ),
            "Committee Defense": (
                "Student-t & Historical simulation; ES captures tail severity"
            ),
        },
        {
            "Area": "EVT (Tail Model)",
            "Core Assumption": (
                "Exceedances follow GPD; asymptotic tail behaviour is stationary"
            ),
            "Primary Vulnerability": (
                "Threshold selection sensitivity; finite-sample bias"
            ),
            "Committee Defense": (
                "Dual diagnostics (MEP + parameter stability); 90/95th cross-check"
            ),
        },
        {
            "Area": "Backtesting",
            "Core Assumption": (
                "Kupiec/Christoffersen tests have sufficient power over sample"
            ),
            "Primary Vulnerability": (
                "At 99%, 250-day rolling window generates sparse breach counts"
            ),
            "Committee Defense": (
                "Combined coverage and independence tests; multi-regime audits"
            ),
        },
        {
            "Area": "Stress Testing",
            "Core Assumption": (
                "Historical replay represents plausible worst-case joint shocks"
            ),
            "Primary Vulnerability": (
                "Correlations break down; stock-bond hedge failure under stagflation"
            ),
            "Committee Defense": (
                "Dedicated inflation/rate shock scenario (stocks & bonds fall)"
            ),
        },
    ]
    st.dataframe(summary_data, hide_index=True, use_container_width=True)

# ---------------- TAB 1: PORTFOLIO & MANDATE ----------------
with tab_port:
    st.subheader("Layer 0 & 1: Mandate & Portfolio Construction")

    st.markdown("#### 1. Daily Costless Rebalancing")
    st.markdown(
        "- **Assumption:** The portfolio is rebalanced daily to exact"
        " target "
        "weights without incurring brokerage commissions, bid-ask "
        "spread "
        "slippage, or market impact.\n"
        "- **Limitation:** In a real USD 10m endowment, daily "
        "rebalancing is "
        "impractical and cost-prohibitive. During liquidity freezes, "
        "rebalancing trades can incur severe market impact.\n"
        "- **Mitigation:** In practical implementation, the endowment"
        " should "
        "report quarterly sensitivity; headline results assume daily "
        "rebalancing."
    )

    st.markdown("#### 2. Stationary Asset Return Expectations")
    st.markdown(
        "- **Assumption:** Historic means and covariances over 2004 "
        "to 2026 "
        "provide an unbiased estimate of future risk and return "
        "distributions.\n"
        "- **Limitation:** Macroeconomic regimes shift. The post-GFC "
        "zero-interest-rate environment (2009 to 2021) does not "
        "reflect future "
        "higher-for-longer rate regimes.\n"
        "- **Mitigation:** We enforce structural mandate limits "
        "(minimum 30% "
        "AGG bond floor, single sector caps at 10 to 15%) rather than"
        " relying "
        "solely on unconstrained mathematical optimization."
    )

# ---------------- TAB 2: DATA & HYGIENE ----------------
with tab_data:
    st.subheader("Data Sourcing & Cleaning Assumptions")

    st.markdown("#### 1. Sample Horizon Selection (Nov 2004 to Present)")
    st.markdown(
        "- **Assumption:** Commencing the dataset on November 18, "
        "2004 ensures "
        "all 7 ETFs are traded simultaneously and captures 22 years "
        "of market "
        "history, including three major market crises.\n"
        "- **Limitation:** The 2000 to 2002 dot-com crash is omitted "
        "because GLD "
        "and several sector ETFs did not exist.\n"
        "- **Mitigation:** The 2008 GFC, 2020 COVID crash, and 2022 "
        "stagflationary rate hikes provide ample multi-regime stress."
    )

    st.markdown("#### 2. Price Imputation and Gap Handling")
    st.markdown(
        "- **Assumption:** Forward-filling missing ETF prices up to 3"
        " business "
        "days resolves holiday mismatches without distorting return "
        "dynamics.\n"
        "- **Limitation:** Forward-filling induces artificial zero "
        "returns on "
        "closed exchanges, temporarily dampening realized volatility.\n"
        "- **Mitigation:** In our universe, all seven ETFs trade on "
        "major US "
        "exchanges with synchronized calendars; the cleaning audit "
        "verifies "
        "that 0 days required fill across the equity and commodity "
        "tickers."
    )

# ---------------- TAB 3: VAR & ES ----------------
with tab_var:
    st.subheader("Layers 2 & 3: VaR and Expected Shortfall")

    st.markdown("#### 1. Distributional Assumptions (Normal vs. Student-t)")
    st.markdown(
        "- **Assumption:** Parametric models assume returns follow a "
        "defined "
        "parametric density function.\n"
        "- **Limitation:** Gaussian Normal VaR assumes thin "
        "exponential tails, "
        "dangerously underestimating 99% 1-day losses. Parametric "
        "Student-t "
        "captures kurtosis but assumes tail symmetry, failing to "
        "model negative "
        "skewness.\n"
        "- **Mitigation:** We report Historical Simulation, "
        "Student-t, and EVT "
        "side by side, and establish Expected Shortfall (which is "
        "subadditive "
        "and coherent) as the primary risk limit."
    )

    st.markdown("#### 2. 1-Day Horizon and Square-Root-of-Time Scaling")
    st.markdown(
        "- **Assumption:** Tail risk is evaluated over a 1-day horizon. "
        "Scaling to 10-day regulatory horizons assumes returns are "
        "i.i.d.\n"
        "- **Limitation:** Volatility clustering and autoregressive "
        "dependency "
        "cause multi-day losses to compound non-linearly.\n"
        "- **Mitigation:** For endowment capital adequacy, multi-week"
        " liquidity "
        "buffers are not calibrated here. Future analysis should use "
        "stress scenarios, not "
        "purely square-root scaled 1-day figures."
    )

# ---------------- TAB 4: EVT ----------------
with tab_evt:
    st.subheader("Layer 4: Extreme Value Theory (EVT)")

    st.markdown("#### 1. Peak-Over-Threshold Asymptotic Validity")
    st.markdown(
        "- **Assumption:** Losses exceeding threshold u adhere "
        "asymptotically "
        "to a Generalized Pareto Distribution (GPD).\n"
        "- **Limitation:** The GPD theorem is an asymptotic result (n"
        " → ∞). "
        "In finite samples, a threshold set too high yields high "
        "parameter "
        "variance, while a threshold set too low introduces central "
        "bias.\n"
        "- **Mitigation:** We employ systematic dual diagnostics "
        "(Mean Excess "
        "Plot linearity and Parameter Stability) and anchor u to the "
        "90th "
        "percentile to balance bias against variance."
    )

    st.markdown("#### 2. Tail Stationarity")
    st.markdown(
        "- **Assumption:** Extreme tail dynamics are stationary "
        "across time.\n"
        "- **Limitation:** Tail thickness (ξ) can expand abruptly "
        "during "
        "liquidity contagions.\n"
        "- **Mitigation:** EVT is evaluated with rolling out-of-"
        "sample coverage "
        "and independence tests, then considered alongside crisis "
        "replays. "
        "These checks reveal breach clustering rather than proving "
        "reliability."
    )

# ---------------- TAB 5: BACKTESTING ----------------
with tab_backtest:
    st.subheader("Layer 5: Backtesting & Model Validation")

    st.markdown("#### 1. Test Power and Horizon Limits")
    st.markdown(
        "- **Assumption:** Kupiec POF and Christoffersen independence"
        " tests "
        "provide rigorous statistical validation of model accuracy.\n"
        "- **Limitation:** At 99% confidence over a standard 250-day "
        "window, "
        "expected breaches are only 2.5 days. With so few breach "
        "events, "
        "the Kupiec test has low statistical power to detect model "
        "underestimation.\n"
        "- **Mitigation:** We evaluate backtests across the full "
        "multi-year "
        "sample (over 5,000 trading days) and supplement frequency "
        "tests with "
        "independence tests and Basel traffic-light classification."
    )

    st.markdown("#### 2. Realized vs. Investable Portfolios")
    st.markdown(
        "- **Assumption:** Out-of-sample backtests accurately represent "
        "real-time risk forecasts.\n"
        "- **Limitation:** Backtests assume frozen weights and "
        "instantaneous "
        "execution at closing prices without cash drag.\n"
        "- **Mitigation:** Cash reserves are not modeled. Future "
        "implementation must plan for "
        "liquidity disbursements."
    )

# ---------------- TAB 6: STRESS SCENARIOS ----------------
with tab_stress:
    st.subheader("Decision Layer: Stress Testing & Macro Scenarios")

    st.markdown("#### 1. Historical Crisis Replay Assumptions")
    st.markdown(
        "- **Assumption:** Replaying 2008 GFC, March 2020 COVID, and "
        "2022 "
        "rate hikes captures the portfolio's drawdown behavior.\n"
        "- **Limitation:** Future market shocks will not repeat past "
        "history "
        "identically. Correlation structures frequently alter during "
        "novel "
        "crises.\n"
        "- **Mitigation:** We introduce a dedicated inflation shock "
        "scenario "
        "where stocks and bonds fall concurrently, directly "
        "addressing the "
        "vulnerability of the classic 60/40 allocation."
    )

    st.markdown("#### 2. Hypothetical vs. Empirical Stress")
    st.markdown(
        "- **Assumption:** Synthetic stress shocks provide meaningful"
        " downside "
        "bounds.\n"
        "- **Limitation:** Hypothetical factor shifts require "
        "subjective "
        "assumptions regarding cross-asset betas.\n"
        "- **Mitigation:** All hypothetical stress scenarios are "
        "clearly "
        "demarcated from historical replays in our presentation to "
        "the committee."
    )
