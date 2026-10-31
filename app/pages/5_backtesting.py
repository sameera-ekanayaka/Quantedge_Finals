import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import backtest
from src.data import load_returns, load_risk_free
from src.portfolio import annual_risk_free, candidate_portfolios, portfolio_returns
from src.ui import get_settings

ZONE_COLOURS = {"green": "#2e7d32", "yellow": "#f9a825", "red": "#c62828"}
SIGNIFICANCE = 0.05


@st.cache_data
def load_candidates() -> tuple[pd.DataFrame, pd.DataFrame]:
    returns = load_returns()
    rf = annual_risk_free(load_risk_free(), returns.index)
    return returns, candidate_portfolios(returns, rf)


@st.cache_data(show_spinner="Running the rolling backtest...")
def cached_backtest(
    portfolio: str, method: str, alpha: float, window: int
) -> pd.DataFrame:
    returns, candidates = load_candidates()
    series = portfolio_returns(returns, candidates[portfolio])
    return backtest.run_backtest(series, method, alpha, window)


def verdict(p_value: float) -> str:
    return "Reject" if p_value < SIGNIFICANCE else "Pass"


def zone_badge(zone: str, label: str) -> None:
    colour = ZONE_COLOURS.get(zone, "#757575")
    text = zone.upper() if zone != "n/a" else "N/A"
    st.markdown(
        f"<div style='padding:0.8rem;border-radius:0.5rem;background:{colour};"
        f"color:white;text-align:center'><b>{label}</b><br>"
        f"<span style='font-size:1.6rem'>{text}</span></div>",
        unsafe_allow_html=True,
    )


def breach_chart(results: pd.DataFrame, alpha: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=results.index,
            y=results["return"],
            name="Daily return",
            mode="lines",
            line={"width": 1, "color": "#90a4ae"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=results.index,
            y=-results["var"],
            name=f"{alpha:.0%} VaR forecast",
            mode="lines",
            line={"color": "#1565c0"},
        )
    )
    hits = results[results["breach"]]
    fig.add_trace(
        go.Scatter(
            x=hits.index,
            y=hits["return"],
            name="Breach",
            mode="markers",
            marker={"color": "#c62828", "size": 6},
        )
    )
    fig.update_layout(
        yaxis_tickformat=".1%",
        height=420,
        margin={"t": 10},
        legend={"orientation": "h", "y": 1.08},
    )
    return fig


def rolling_breach_chart(results: pd.DataFrame) -> go.Figure:
    counts = results["breach"].rolling(backtest.BASEL_DAYS).sum().dropna()
    fig = go.Figure()
    top = max(counts.max(), backtest.BASEL_YELLOW_MAX + 3)
    bands = [
        (0, backtest.BASEL_GREEN_MAX + 0.5, "green"),
        (backtest.BASEL_GREEN_MAX + 0.5, backtest.BASEL_YELLOW_MAX + 0.5, "yellow"),
        (backtest.BASEL_YELLOW_MAX + 0.5, top, "red"),
    ]
    for low, high, zone in bands:
        fig.add_hrect(
            y0=low, y1=high, fillcolor=ZONE_COLOURS[zone], opacity=0.15, line_width=0
        )
    fig.add_trace(go.Scatter(x=counts.index, y=counts, mode="lines", name="Breaches"))
    fig.update_layout(
        yaxis_title="Breaches in last 250 days", height=320, margin={"t": 10}
    )
    return fig


st.title("Backtesting")

settings = get_settings()
alpha = settings.confidence
method = settings.var_method

st.markdown(
    "Each day we forecast VaR using only the returns before that day, then check "
    "whether the actual loss was bigger. A good model is breached about "
    f"{1 - alpha:.0%} of the time, and the breaches do not bunch together."
)

returns, candidates = load_candidates()
col_portfolio, col_method, col_window = st.columns(3)
portfolio = col_portfolio.selectbox(
    "Portfolio",
    list(candidates.columns),
    index=list(candidates.columns).index("Maximum Sharpe"),
)
methods = list(backtest.MODEL_LABELS)
if not backtest.evt_available():
    methods.remove("evt")
method = col_method.selectbox(
    "VaR model",
    methods,
    index=methods.index(method),
    format_func=backtest.MODEL_LABELS.get,
    help="Defaults to the sidebar choice. EVT appears once its module is ready.",
)
window = col_window.selectbox(
    "Estimation window (days)",
    backtest.WINDOW_CHOICES,
    index=backtest.WINDOW_CHOICES.index(backtest.DEFAULT_WINDOW),
)

full = cached_backtest(portfolio, method, alpha, window)
start = pd.Timestamp(settings.backtest_start)
end = pd.Timestamp(settings.backtest_end)
results = full.loc[start:end]
if len(results) < backtest.BASEL_DAYS:
    st.warning(
        f"Only {len(results)} forecast days in the chosen range. Pick a range of at "
        f"least {backtest.BASEL_DAYS} days in the sidebar. Forecasts start on "
        f"{full.index[0].date()}."
    )
    st.stop()

summary = backtest.summarise(results, alpha)
st.caption(
    f"{summary['days']:,} rolling forecast days, {results.index[0].date()} to "
    f"{results.index[-1].date()}. Model refit every "
    f"{backtest.REFIT_EVERY[method]} day(s) on the previous {window} days."
)

st.subheader("Basel traffic light")
if summary["zone_last_250"] == "n/a":
    st.info(
        f"The Basel traffic light is defined for 99% VaR only. At {alpha:.0%} we "
        "report Kupiec and Christoffersen below. Pick 99% in the sidebar to see it."
    )
else:
    left, middle, right = st.columns(3)
    with left:
        zone_badge(summary["zone_last_250"], "Last 250 days")
    with middle:
        zone_badge(summary["zone_full"], "Whole range (binomial rule)")
    right.metric("Breaches in last 250 days", summary["last_250_breaches"])
    right.metric(
        "Basel capital multiplier",
        f"{backtest.basel_multiplier(summary['last_250_breaches']):.2f}",
    )
    st.caption(
        "Official zones: 0 to 4 breaches green, 5 to 9 yellow, 10 or more red, "
        "over 250 days. For the whole range we use the binomial rule the zones come "
        "from: green below 95% cumulative probability, red from 99.99%."
    )

st.subheader("Coverage and independence tests")
m1, m2, m3 = st.columns(3)
m1.metric("Breaches", summary["breaches"], f"{summary['expected']:.1f} expected")
m2.metric("Breach rate", f"{summary['breach_rate']:.2%}", f"target {1 - alpha:.0%}")
m3.metric("ES test (Z2)", f"{summary['es_z2']:+.2f}", summary["es_zone"])
tests = pd.DataFrame(
    [
        {
            "Test": "Kupiec (right number of breaches)",
            "LR statistic": summary["kupiec_lr"],
            "p-value": summary["kupiec_p"],
            "Result at 5%": verdict(summary["kupiec_p"]),
        },
        {
            "Test": "Christoffersen independence (no clustering)",
            "LR statistic": summary["ind_lr"],
            "p-value": summary["ind_p"],
            "Result at 5%": verdict(summary["ind_p"]),
        },
        {
            "Test": "Christoffersen conditional coverage (both)",
            "LR statistic": summary["cc_lr"],
            "p-value": summary["cc_p"],
            "Result at 5%": verdict(summary["cc_p"]),
        },
    ]
)
st.dataframe(
    tests.style.format({"LR statistic": "{:.2f}", "p-value": "{:.3f}"}),
    hide_index=True,
)
st.caption(
    "Reject means the data are unlikely under a correct model. Pass does not prove "
    "the model right: with few expected breaches these tests have little power. "
    "Z2 (Acerbi and Szekely) checks the ES forecasts: near 0 is good, above 0.7 "
    f"suggests ES is too low. Average breach loss was "
    f"{summary['es_loss_to_es']:.2f} times the forecast ES."
)

st.subheader("Forecasts and breaches")
st.plotly_chart(breach_chart(results, alpha))

if backtest.traffic_light(0, backtest.BASEL_DAYS, alpha) != "n/a":
    st.subheader("Rolling 250-day breach count")
    st.plotly_chart(rolling_breach_chart(results))

st.subheader("Calm and stressed periods")
periods = backtest.backtest_by_period(results, alpha)
st.dataframe(
    periods.rename(
        columns={
            "days": "Days",
            "breaches": "Breaches",
            "expected": "Expected",
            "breach_rate": "Breach rate",
            "kupiec_p": "Kupiec p-value",
        }
    ).style.format(
        {"Expected": "{:.1f}", "Breach rate": "{:.2%}", "Kupiec p-value": "{:.3f}"}
    )
)
st.caption(
    "Most models breach far more often in crises than in calm years. That is the "
    "cost of a window that adapts slowly."
)

st.subheader("All models side by side")
if st.toggle("Compare every model (takes about a minute the first time)"):
    rows = []
    for key in methods:
        part = cached_backtest(portfolio, key, alpha, window).loc[start:end]
        s = backtest.summarise(part, alpha)
        rows.append(
            {
                "Model": backtest.MODEL_LABELS[key],
                "Breaches": s["breaches"],
                "Expected": s["expected"],
                "Kupiec p": s["kupiec_p"],
                "Independence p": s["ind_p"],
                "Cond. coverage p": s["cc_p"],
                "Traffic light (last 250)": s["zone_last_250"],
                "ES Z2": s["es_z2"],
            }
        )
    st.dataframe(
        pd.DataFrame(rows).style.format(
            {
                "Expected": "{:.1f}",
                "Kupiec p": "{:.3f}",
                "Independence p": "{:.3f}",
                "Cond. coverage p": "{:.3f}",
                "ES Z2": "{:+.2f}",
            }
        ),
        hide_index=True,
    )

with st.expander("How the backtest is set up"):
    st.markdown(f"""
- **Out of sample, conditional on fixed weights.** The forecast for each day
  only uses the {window} days before it, so a crash never sits in its own
  forecast window. The weights were selected using the full history, so this
  does not test the portfolio-selection rule out of sample.
- **Window.** 500 days (about two years) is the default. It is above the Basel
  minimum of one year, gives five tail observations at 99%, and puts the first
  forecast in late 2006 so the whole 2008 crisis is tested out of sample.
  250 and 1000 days are there to check the conclusion does not hinge on it.
- **Refitting.** Historical and normal VaR are refit every day. Student t,
  Monte Carlo and EVT are refit every 21 trading days and held in between,
  because each fit is slow and a month of new data barely moves a 500-day fit.
- **Portfolio returns** are daily simple returns with fixed weights selected
  from the full 2004 to 2026 sample.
- **Traffic light.** Only defined for 99% VaR. At 90% and 95% we show the
  tests without it.
""")
