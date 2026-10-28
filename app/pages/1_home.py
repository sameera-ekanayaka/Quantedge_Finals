import streamlit as st

from src import config
from src.ui import get_settings

st.title("Serendib University Endowment Fund")
st.subheader("USD 10m conservative portfolio: construction and risk review")

st.markdown(
    "We build a long-only portfolio from seven ETFs, measure its downside with "
    "several methods, test those methods against history and recommend the "
    "portfolio whose worst case the fund can live with."
)

st.write("Universe:", ", ".join(config.TICKERS))

settings = get_settings()
st.markdown(
    f"**Current settings:** {settings.confidence:.0%} confidence, "
    f"{config.VAR_METHODS[settings.var_method]}, backtest from "
    f"{settings.backtest_start} to {settings.backtest_end}."
)
