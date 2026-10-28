from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app.py"


def test_app_starts_without_errors():
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not at.exception
    assert at.sidebar.select_slider[0].value == 0.99
