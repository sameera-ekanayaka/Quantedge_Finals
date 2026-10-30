from pathlib import Path

from streamlit.testing.v1 import AppTest

PAGE = Path(__file__).resolve().parent.parent / "app" / "pages" / "4_evt.py"


def test_evt_page_renders_cleanly():
    at = AppTest.from_file(str(PAGE), default_timeout=30)
    # Pre-populate sidebar session state values that ui.py expects
    at.session_state["confidence"] = 0.99
    at.session_state["var_method"] = "historical"
    at.session_state["backtest_range"] = (Path().resolve(),)
    at.run()

    assert not at.exception
    assert len(at.metric) >= 6
    assert "Extreme Value Theory" in at.title[0].value
