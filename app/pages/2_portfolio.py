import streamlit as st

from src.ui import get_settings

st.title("Portfolio")
st.caption("Owner: Imasha Karunathilaka")

settings = get_settings()
st.info(
    "Coming soon: weights, cumulative return and drawdown for the chosen portfolio."
)
