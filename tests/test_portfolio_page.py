from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src import config

PAGE = Path(__file__).resolve().parent.parent / "app" / "pages" / "2_portfolio.py"
FINAL = "Final recommendation (Maximum Sharpe)"


def run_page(confidence: float = 0.99) -> AppTest:
    at = AppTest.from_file(str(PAGE), default_timeout=180)
    at.session_state["confidence"] = confidence
    at.session_state["var_method"] = next(iter(config.VAR_METHODS))
    at.session_state["backtest_range"] = (date(2010, 1, 1), date(2020, 1, 1))
    return at.run()


def test_page_runs_and_starts_on_the_final_portfolio():
    at = run_page()
    assert not at.exception
    assert at.selectbox[0].value == FINAL
    assert len(at.metric) == 5


def test_final_portfolio_headline_numbers():
    at = run_page()
    assert at.metric[0].label == "Annual return"
    assert at.metric[0].value == "7.4%"
    assert at.metric[2].label == "Sharpe ratio"
    assert at.metric[2].value == "0.79"


def test_confidence_level_changes_the_es_number():
    low = run_page(0.95)
    high = run_page(0.99)
    assert low.metric[4].label == "1-day ES at 95%"
    assert high.metric[4].label == "1-day ES at 99%"
    assert low.metric[4].value != high.metric[4].value


def test_choosing_another_portfolio_changes_the_numbers():
    at = run_page()
    at.selectbox[0].select("Equal weight").run()
    assert not at.exception
    assert at.metric[0].value == "9.0%"
