import streamlit as st

from src.ui import get_settings

st.title("Backtesting")
st.caption("Owner: Tharindu Dhanushka")

settings = get_settings()
st.info("Coming soon: Kupiec and Christoffersen results with the Basel traffic light.")
