from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

PAGE = Path(__file__).resolve().parent.parent / "app" / "pages" / "5_backtesting.py"


def run_page(confidence: float) -> AppTest:
    at = AppTest.from_file(str(PAGE), default_timeout=120)
    at.session_state["confidence"] = confidence
    at.session_state["var_method"] = "historical"
    at.session_state["backtest_range"] = (date(2008, 1, 1), date(2026, 10, 27))
    return at.run()


def test_backtesting_page_at_99_shows_traffic_light():
    at = run_page(0.99)
    assert not at.exception
    assert "Backtesting" in at.title[0].value
    assert any("Basel capital multiplier" in m.label for m in at.metric)


def test_backtesting_page_at_95_says_light_is_for_99_only():
    at = run_page(0.95)
    assert not at.exception
    assert any("99% VaR only" in i.value for i in at.info)
