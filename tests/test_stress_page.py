from pathlib import Path

from streamlit.testing.v1 import AppTest

PAGE = Path(__file__).resolve().parent.parent / "app" / "pages" / "6_stress_tests.py"


def test_stress_page_renders_every_scenario():
    at = AppTest.from_file(str(PAGE), default_timeout=60).run()
    assert not at.exception
    assert "Stress tests" in at.title[0].value
    assert any("Worst scenario" in m.label for m in at.metric)


def test_editing_a_shock_updates_the_page():
    at = AppTest.from_file(str(PAGE), default_timeout=60).run()
    at.number_input(key="shock_AGG").set_value(10.0).run()
    assert not at.exception
