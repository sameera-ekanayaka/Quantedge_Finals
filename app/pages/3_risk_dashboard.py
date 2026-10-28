import streamlit as st

from src.ui import get_settings

st.title("Risk dashboard")
st.caption("Owner: Aadhila Anees")

settings = get_settings()
st.info(
    "Coming soon: VaR, ES and the EVT estimate side by side at one confidence level."
)
