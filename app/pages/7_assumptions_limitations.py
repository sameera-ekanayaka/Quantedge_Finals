import streamlit as st

from src.ui import get_settings

st.title("Assumptions & Limitations")
st.caption("Owner: Praveen Madawalage")

settings = get_settings()
st.info("Coming soon: every assumption we make and where the models can fail.")
