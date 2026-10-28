"""Sidebar controls shared by every page of the app.

Owner: Sameera Ekanayaka
"""

from dataclasses import dataclass
from datetime import date

import pandas as pd
import streamlit as st

from src import config


@dataclass(frozen=True)
class Settings:
    confidence: float
    var_method: str
    backtest_start: date
    backtest_end: date


def render_sidebar() -> None:
    """Draw the sidebar. Values live in st.session_state so all pages share them."""
    st.sidebar.header("Settings")
    st.sidebar.select_slider(
        "Confidence level",
        options=config.CONFIDENCE_LEVELS,
        value=0.99,
        format_func=lambda c: f"{c:.0%}",
        key="confidence",
    )
    st.sidebar.selectbox(
        "VaR method",
        options=list(config.VAR_METHODS),
        format_func=config.VAR_METHODS.get,
        key="var_method",
    )
    st.sidebar.date_input(
        "Backtest date range",
        value=(pd.Timestamp(config.DEFAULT_BACKTEST_START).date(), date.today()),
        min_value=pd.Timestamp(config.START_DATE).date(),
        max_value=date.today(),
        key="backtest_range",
    )


def get_settings() -> Settings:
    """Current sidebar choices."""
    dates = st.session_state["backtest_range"]
    # The date picker returns one date while the user is still choosing the end
    start, end = (dates[0], dates[-1]) if len(dates) else (None, None)
    return Settings(
        confidence=st.session_state["confidence"],
        var_method=st.session_state["var_method"],
        backtest_start=start,
        backtest_end=end,
    )
