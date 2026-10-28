from pathlib import Path

from streamlit.testing.v1 import AppTest

from src import data, get_data
from tests.test_get_data import synthetic_prices, synthetic_rf

PAGE = Path(__file__).resolve().parent.parent / "app" / "pages" / "8_data.py"


def test_data_page_without_report(tmp_data_dirs):
    at = AppTest.from_file(str(PAGE), default_timeout=30).run()
    assert not at.exception
    assert "No cleaning report" in at.warning[0].value


def test_data_page_shows_report(tmp_data_dirs, monkeypatch):
    raw = synthetic_prices()
    raw.loc[raw.index[300] :, "XLE"] *= 0.7
    monkeypatch.setattr(get_data, "download_prices", lambda: raw)
    monkeypatch.setattr(get_data, "download_risk_free", lambda: synthetic_rf(raw.index))
    get_data.run()

    at = AppTest.from_file(str(PAGE), default_timeout=30).run()
    assert not at.exception
    report_days = data.load_cleaning_report()["days"]
    assert at.metric[0].value == f"{report_days:,}"
    assert len(at.dataframe) == 3
