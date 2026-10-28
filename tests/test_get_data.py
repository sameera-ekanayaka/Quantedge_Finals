import numpy as np
import pandas as pd
import pytest

from src import config, data, get_data


def synthetic_prices(start="2004-11-01", end="2023-06-30", seed=1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, end)
    steps = rng.normal(0, 0.01, size=(len(dates), len(config.TICKERS)))
    prices = 100 * np.exp(np.cumsum(steps, axis=0))
    # Shuffled column order, like yfinance gives back
    return pd.DataFrame(prices, index=dates, columns=config.TICKERS)[
        sorted(config.TICKERS)
    ]


def synthetic_rf(dates: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame({"DTB3": np.linspace(1.0, 5.0, len(dates))}, index=dates)


def test_clean_prices_orders_columns_and_trims_dates():
    prices, filled = get_data.clean_prices(synthetic_prices(), end="2023-01-01")
    assert list(prices.columns) == config.TICKERS
    assert prices.index[0] >= pd.Timestamp(config.START_DATE)
    assert prices.index[-1] < pd.Timestamp("2023-01-01")
    assert prices.index.is_monotonic_increasing
    assert not prices.isna().any().any()
    assert filled.sum() == 0


def test_clean_prices_starts_when_every_ticker_trades():
    raw = synthetic_prices()
    raw.loc[:"2004-11-30", "GLD"] = np.nan
    prices, _ = get_data.clean_prices(raw)
    assert prices.index[0] == pd.Timestamp("2004-12-01")


def test_clean_prices_fills_short_gaps_and_counts_them():
    raw = synthetic_prices()
    gap = raw.index[100:102]
    raw.loc[gap, "EEM"] = np.nan
    raw.loc[raw.index[200], "AGG"] = 0.0
    prices, filled = get_data.clean_prices(raw)
    assert (prices.loc[gap, "EEM"] == raw["EEM"].iloc[99]).all()
    assert filled["EEM"] == 2
    assert filled["AGG"] == 1
    assert filled["SPY"] == 0


def test_clean_prices_stops_on_long_gap():
    raw = synthetic_prices()
    raw.loc[raw.index[300:310], "XLE"] = np.nan
    with pytest.raises(ValueError, match="XLE"):
        get_data.clean_prices(raw)


def test_clean_prices_drops_holidays_and_duplicates():
    raw = synthetic_prices()
    holiday = raw.index[50]
    raw.loc[holiday] = np.nan
    raw = pd.concat([raw, raw.iloc[[60]]])
    prices, filled = get_data.clean_prices(raw)
    assert holiday not in prices.index
    assert prices.index.is_unique
    assert filled.sum() == 0


def test_clean_prices_handles_timezone_aware_index():
    raw = synthetic_prices()
    raw.index = raw.index.tz_localize("America/New_York")
    prices, _ = get_data.clean_prices(raw)
    assert prices.index.tz is None


def test_clean_prices_missing_ticker():
    with pytest.raises(ValueError, match="XLK"):
        get_data.clean_prices(synthetic_prices().drop(columns="XLK"))


def test_clean_risk_free_fills_bond_holidays():
    dates = pd.bdate_range("2020-01-01", periods=10)
    raw = synthetic_rf(dates).drop(dates[3])
    raw.loc[dates[5], "DTB3"] = np.nan
    rf = get_data.clean_risk_free(raw, dates)
    assert rf.index.equals(dates)
    assert rf.loc[dates[3], "DTB3"] == raw.loc[dates[2], "DTB3"]
    assert rf.loc[dates[5], "DTB3"] == raw.loc[dates[4], "DTB3"]


def test_clean_risk_free_needs_a_rate_before_the_first_price():
    dates = pd.bdate_range("2020-01-01", periods=10)
    with pytest.raises(ValueError, match="2020-01-01"):
        get_data.clean_risk_free(synthetic_rf(dates[2:]), dates)


def test_large_moves_flags_jumps():
    prices = synthetic_prices(end="2005-06-30")
    prices.loc[prices.index[40] :, "XLE"] *= 0.7
    moves = get_data.large_moves(prices)
    assert list(moves.index) == [(prices.index[40], "XLE")]


def test_stress_periods_covered():
    assert get_data.stress_periods_covered(synthetic_prices())
    assert not get_data.stress_periods_covered(synthetic_prices(start="2010-01-01"))


@pytest.fixture
def tmp_data_dirs(tmp_path, monkeypatch):
    for name, value in {
        "RAW_DIR": tmp_path / "raw",
        "CLEAN_DIR": tmp_path / "clean",
        "RAW_PRICES_FILE": tmp_path / "raw" / "prices_raw.csv",
        "RAW_RISK_FREE_FILE": tmp_path / "raw" / "risk_free_raw.csv",
        "PRICES_FILE": tmp_path / "clean" / "prices.csv",
        "RISK_FREE_FILE": tmp_path / "clean" / "risk_free.csv",
    }.items():
        monkeypatch.setattr(config, name, value)
    return tmp_path


def test_run_saves_files_the_loaders_can_read(tmp_data_dirs, monkeypatch):
    raw = synthetic_prices()
    monkeypatch.setattr(get_data, "download_prices", lambda: raw)
    monkeypatch.setattr(get_data, "download_risk_free", lambda: synthetic_rf(raw.index))

    prices, risk_free = get_data.run()

    loaded = data.load_prices()
    pd.testing.assert_frame_equal(loaded, prices, check_freq=False, atol=1e-6)
    returns = data.load_returns()
    assert returns.shape == (len(prices) - 1, len(config.TICKERS))
    assert list(returns.columns) == list(data.stub_returns(n_days=5).columns)
    rf = data.load_risk_free()
    assert rf.index.equals(loaded.index)
    expected = risk_free["DTB3"].iloc[0] / 100 / config.TRADING_DAYS
    assert rf.iloc[0] == pytest.approx(expected, rel=1e-3)


def test_run_from_raw_matches_download_run(tmp_data_dirs, monkeypatch):
    raw = synthetic_prices()
    monkeypatch.setattr(get_data, "download_prices", lambda: raw)
    monkeypatch.setattr(get_data, "download_risk_free", lambda: synthetic_rf(raw.index))
    first, _ = get_data.run()

    def no_download():
        raise AssertionError("should not download")

    monkeypatch.setattr(get_data, "download_prices", no_download)
    second, _ = get_data.run(from_raw=True)
    pd.testing.assert_frame_equal(first, second, check_freq=False)


def test_main_returns_error_code_on_bad_data(tmp_data_dirs, monkeypatch, capsys):
    raw = synthetic_prices(start="2015-01-01")
    monkeypatch.setattr(get_data, "download_prices", lambda: raw)
    monkeypatch.setattr(get_data, "download_risk_free", lambda: synthetic_rf(raw.index))
    assert get_data.main([]) == 1
    assert "stress period" in capsys.readouterr().err


def test_download_prices_takes_adjusted_close(monkeypatch):
    import yfinance as yf

    dates = pd.bdate_range("2020-01-01", periods=3)
    columns = pd.MultiIndex.from_product(
        [["Adj Close", "Close"], sorted(config.TICKERS)], names=["Price", "Ticker"]
    )
    fake = pd.DataFrame(1.0, index=dates, columns=columns)
    fake["Close"] = 2.0
    calls = {}

    def fake_download(tickers, **kwargs):
        calls.update(kwargs)
        return fake

    monkeypatch.setattr(yf, "download", fake_download)
    prices = get_data.download_prices()
    assert list(prices.columns) == config.TICKERS
    assert (prices == 1.0).all().all()
    assert calls["auto_adjust"] is False


def test_download_risk_free_reads_fred_csv(tmp_path, monkeypatch):
    csv = tmp_path / "DTB3.csv"
    csv.write_text("observation_date,DTB3\n2020-01-01,\n2020-01-02,1.52\n")
    monkeypatch.setattr(get_data, "FRED_CSV_URL", str(tmp_path / "{series}.csv"))
    rf = get_data.download_risk_free()
    assert list(rf.columns) == ["DTB3"]
    assert np.isnan(rf["DTB3"].iloc[0])
    assert rf["DTB3"].iloc[1] == 1.52
