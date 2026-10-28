import numpy as np
import pandas as pd
import pytest

from src import config, data


def test_stub_returns_shape_and_columns():
    returns = data.stub_returns(n_days=500)
    assert returns.shape == (500, len(config.TICKERS))
    assert list(returns.columns) == config.TICKERS
    assert isinstance(returns.index, pd.DatetimeIndex)


def test_stub_returns_is_reproducible():
    pd.testing.assert_frame_equal(data.stub_returns(), data.stub_returns())


def test_load_returns_from_prices_gives_log_returns():
    prices = pd.DataFrame(
        {"SPY": [100.0, 110.0, 99.0]}, index=pd.bdate_range("2020-01-01", periods=3)
    )
    returns = data.load_returns(prices)
    assert len(returns) == 2
    assert returns["SPY"].iloc[0] == pytest.approx(np.log(1.1))


def test_log_to_simple_round_trip():
    assert data.log_to_simple(np.log(1.05)) == pytest.approx(0.05)


def test_missing_clean_file_has_clear_error(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PRICES_FILE", tmp_path / "prices.csv")
    with pytest.raises(FileNotFoundError, match="data/clean"):
        data.load_prices()
