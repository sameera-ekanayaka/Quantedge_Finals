from datetime import date
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PAGE = Path(__file__).resolve().parents[1] / "app/pages/9_supplementary.py"


@pytest.mark.parametrize("alpha", [0.90, 0.95, 0.99])
def test_supplementary_page_discloses_fixed_comparison_confidence(alpha):
    at = AppTest.from_file(str(PAGE), default_timeout=60)
    at.session_state["confidence"] = alpha
    at.session_state["var_method"] = "historical"
    at.session_state["backtest_range"] = (date(2008, 1, 1), date(2026, 10, 27))
    at.run()
    assert not at.exception
    assert len(at.dataframe) >= 8
    assert any("99% confidence" in element.value for element in at.info)
    assert any("ADJUST" in element.value for element in at.markdown)
