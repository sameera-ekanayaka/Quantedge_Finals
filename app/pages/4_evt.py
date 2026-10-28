import streamlit as st

from src.ui import get_settings

st.title("Extreme value theory")
st.caption("Owner: Praveen Madawalage")

settings = get_settings()
st.info(
    "Coming soon: threshold choice, mean excess and stability plots, and the GPD fit."
)
