import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data

st.title("Data")

report = data.load_cleaning_report()
if report is None:
    st.warning(
        "No cleaning report yet. Run `python -m src.get_data` to download and "
        "clean the data."
    )
    st.stop()

st.markdown(
    f"**Prices:** {report['sources']['prices']}  \n"
    f"**Risk-free rate:** {report['sources']['risk_free']}"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Trading days", f"{report['days']:,}")
col2.metric("First day", report["first_date"])
col3.metric("Last day", report["last_date"])
col4.metric("Days filled", sum(report["filled_days"].values()))

st.subheader("Cleaning steps")
steps = pd.DataFrame(report["steps"]).rename(
    columns={
        "step": "Step",
        "rows": "Rows",
        "removed": "Rows removed",
        "detail": "Details",
    }
)
st.dataframe(steps, hide_index=True)

left, right = st.columns(2)
with left:
    st.subheader("Gaps filled")
    st.caption(
        f"Gaps of up to {report['max_fill_days']} days take the last price. "
        "A longer gap stops the run."
    )
    filled = pd.Series(report["filled_days"], name="Days filled")
    st.dataframe(filled.rename_axis("Ticker"))

with right:
    st.subheader("Stress periods covered")
    for period in report["stress_periods"]:
        mark = "Covered" if period["covered"] else "Not covered"
        st.write(f"{mark}: {period['name']} ({period['start']} to {period['end']})")

threshold = report["large_move_threshold"]
st.subheader(f"Daily moves above {threshold:.0%}")
moves = pd.DataFrame(report["large_moves"])
if moves.empty:
    st.write("None.")
else:
    st.caption("Flagged for a manual check and kept, since they are real market days.")
    st.dataframe(
        moves.rename(
            columns={"date": "Date", "ticker": "Ticker", "log_return": "Log return"}
        ).style.format({"Log return": "{:+.1%}"}),
        hide_index=True,
    )

st.subheader("Stale-price check")
stale = pd.DataFrame(report.get("stale_price_runs", []))
st.caption(
    f"Runs of at least {report.get('stale_run_days', 3)} consecutive trading days "
    "with an unchanged adjusted close are flagged, not removed."
)
if stale.empty:
    st.write("No stale-price runs found.")
else:
    st.dataframe(
        stale.rename(
            columns={
                "ticker": "Ticker",
                "start": "Start",
                "end": "End",
                "unchanged_days": "Unchanged days",
            }
        ),
        hide_index=True,
    )

st.subheader("Return stationarity")
stationarity = report.get("stationarity")
if stationarity is None:
    st.warning("Stationarity results are missing. Rerun the data pipeline.")
else:
    adf = pd.DataFrame.from_dict(stationarity["results"], orient="index")
    adf.index.name = "Ticker"
    adf = adf.reset_index().rename(
        columns={
            "statistic": "ADF statistic",
            "p_value": "p-value",
            "lags": "Lags",
            "observations": "Observations",
            "critical_value_5pct": "5% critical value",
            "stationary_at_5pct": "Stationary at 5%",
        }
    )
    st.caption(
        "Augmented Dickey-Fuller tests use daily log returns. The null hypothesis "
        f"is a unit root; p < 0.05 rejects it. Lags: {stationarity['lag_selection']}."
    )
    st.dataframe(
        adf.style.format(
            {
                "ADF statistic": "{:.3f}",
                "p-value": "{:.4f}",
                "5% critical value": "{:.3f}",
            }
        ),
        hide_index=True,
    )

st.subheader("Prices, rebased to 100")
prices = data.rebase(data.load_prices())
fig = go.Figure()
for ticker in prices.columns:
    fig.add_trace(go.Scatter(x=prices.index, y=prices[ticker], name=ticker))
if not moves.empty:
    dates = pd.to_datetime(moves["date"])
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[prices.at[d, t] for d, t in zip(dates, moves["ticker"], strict=True)],
            mode="markers",
            marker={"size": 10, "symbol": "x", "color": "black"},
            name="Flagged move",
            text=moves["ticker"],
        )
    )
for period in report["stress_periods"]:
    fig.add_vrect(
        x0=period["start"],
        x1=period["end"],
        fillcolor="grey",
        opacity=0.15,
        line_width=0,
    )
fig.update_layout(yaxis_type="log", height=450, margin={"t": 10})
st.plotly_chart(fig)
st.caption("Log scale. Shaded areas are the stress periods.")

st.subheader("Risk-free rate")
rf = report["risk_free"]
st.caption(
    f"Published on {rf['published_days']:,} of our trading days. The other "
    f"{rf['carried_forward_days']} are bond market holidays and take the last rate."
)
st.line_chart(data.load_risk_free_annual().rename("Annual rate (%)"))
