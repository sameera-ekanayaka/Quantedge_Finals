import pytest

from src import config


@pytest.fixture
def tmp_data_dirs(tmp_path, monkeypatch):
    for name, value in {
        "RAW_DIR": tmp_path / "raw",
        "CLEAN_DIR": tmp_path / "clean",
        "RAW_PRICES_FILE": tmp_path / "raw" / "prices_raw.csv",
        "RAW_RISK_FREE_FILE": tmp_path / "raw" / "risk_free_raw.csv",
        "PRICES_FILE": tmp_path / "clean" / "prices.csv",
        "RISK_FREE_FILE": tmp_path / "clean" / "risk_free.csv",
        "REPORT_FILE": tmp_path / "clean" / "cleaning_report.json",
    }.items():
        monkeypatch.setattr(config, name, value)
    return tmp_path
