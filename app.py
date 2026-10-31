"""Entry point for the Streamlit app. Run with: streamlit run app.py"""

import streamlit as st

from src.ui import render_sidebar

st.set_page_config(page_title="Serendib Endowment Risk", layout="wide")

PAGES = [
    st.Page("app/pages/1_home.py", title="Home", default=True),
    st.Page("app/pages/8_data.py", title="Data"),
    st.Page("app/pages/2_portfolio.py", title="Portfolio"),
    st.Page("app/pages/3_risk_dashboard.py", title="Risk dashboard"),
    st.Page("app/pages/4_evt.py", title="Extreme value theory"),
    st.Page("app/pages/5_backtesting.py", title="Backtesting"),
    st.Page("app/pages/6_stress_tests.py", title="Stress tests"),
    st.Page(
        "app/pages/7_assumptions_limitations.py", title="Assumptions & Limitations"
    ),
]

PAGES.append(st.Page("app/pages/9_supplementary.py", title="Extended validation"))

page = st.navigation(PAGES)
render_sidebar()
page.run()
