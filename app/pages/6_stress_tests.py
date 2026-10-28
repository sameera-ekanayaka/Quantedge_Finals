import streamlit as st

from src.ui import get_settings

st.title("Stress tests")
st.caption("Owner: Tharindu Dhanushka")

settings = get_settings()
st.info(
    "Coming soon: portfolio impact under 2008, March 2020, 2022 and our own scenario."
)
