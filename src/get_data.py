"""Download prices and the risk-free rate, clean them and save to data/clean.

Run from the repo root:

    python -m src.get_data             download, clean and save
    python -m src.get_data --from-raw  clean the files already in data/raw

Owner: Sameera Ekanayaka
"""

import argparse
import sys

import numpy as np
import pandas as pd

from src import config

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"

# Longest run of missing days we fill with the last price. Anything longer is
# a real data problem and should stop the run.
MAX_FILL_DAYS = 3

# Daily moves bigger than this get listed in the summary so someone looks at them
LARGE_MOVE = 0.15


def download_prices(
    tickers: list[str] = config.TICKERS,
    start: str = config.START_DATE,
    end: str = config.END_DATE,
) -> pd.DataFrame:
    """Adjusted close prices from Yahoo Finance, one column per ticker."""
    import yfinance as yf

    raw = yf.download(tickers, start=start, end=end, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise RuntimeError("Yahoo Finance returned no data. Check your connection.")
    prices = raw["Adj Close"]
    missing = [t for t in tickers if t not in prices.columns or prices[t].isna().all()]
    if missing:
        raise RuntimeError(f"No prices downloaded for {', '.join(missing)}")
    return prices[tickers]


def download_risk_free(series: str = config.RISK_FREE_SERIES) -> pd.DataFrame:
    """The full FRED series as published, annualised percent."""
    raw = pd.read_csv(
        FRED_CSV_URL.format(series=series),
        index_col=0,
        parse_dates=True,
        na_values=".",
    )
    raw.index.name = "Date"
    return raw.rename(columns={raw.columns[0]: series})


def clean_prices(
    raw: pd.DataFrame,
    tickers: list[str] = config.TICKERS,
    start: str = config.START_DATE,
    end: str = config.END_DATE,
    max_fill: int = MAX_FILL_DAYS,
) -> tuple[pd.DataFrame, pd.Series]:
    """Clean raw adjusted closes.

    Returns the cleaned prices and the number of filled days per ticker.
    """
    missing = [t for t in tickers if t not in raw.columns]
    if missing:
        raise ValueError(f"Raw prices are missing {', '.join(missing)}")

    prices = raw[tickers].apply(pd.to_numeric, errors="coerce")
    prices.index = pd.to_datetime(prices.index).tz_localize(None).normalize()
    prices.index.name = "Date"
    prices = prices[~prices.index.duplicated(keep="last")].sort_index()
    prices = prices.loc[start : pd.Timestamp(end) - pd.Timedelta(days=1)]

    # Zero or negative prices are bad ticks, treat them as missing
    prices = prices.where(prices > 0)
    # Rows where nothing traded are exchange holidays
    prices = prices.dropna(how="all")

    complete = prices.dropna()
    if complete.empty:
        raise ValueError("No date has a price for every ticker")
    prices = prices.loc[complete.index[0] :]

    was_missing = prices.isna()
    prices = prices.ffill(limit=max_fill)
    still_missing = prices.isna()
    if still_missing.any().any():
        bad = still_missing.stack()
        bad = bad[bad].index[:5]
        listed = ", ".join(f"{t} on {d.date()}" for d, t in bad)
        raise ValueError(
            f"Gaps longer than {max_fill} days, for example {listed}. "
            "Check the raw data before going further."
        )

    filled = (was_missing & ~prices.isna()).sum().rename("filled_days")
    return prices, filled


def clean_risk_free(
    raw: pd.DataFrame | pd.Series,
    dates: pd.DatetimeIndex,
    series: str = config.RISK_FREE_SERIES,
) -> pd.DataFrame:
    """Line the risk-free rate up with the price dates.

    FRED skips bond market holidays that are normal trading days for stocks,
    so those days take the last published rate.
    """
    rf = raw.iloc[:, 0] if isinstance(raw, pd.DataFrame) else raw
    rf = pd.to_numeric(rf, errors="coerce")
    rf.index = pd.to_datetime(rf.index).tz_localize(None).normalize()
    rf = rf[~rf.index.duplicated(keep="last")].sort_index().dropna()

    aligned = rf.reindex(rf.index.union(dates)).ffill().reindex(dates)
    if aligned.isna().any():
        first = aligned[aligned.isna()].index[0].date()
        raise ValueError(f"No risk-free rate on or before {first}")
    aligned.index.name = "Date"
    return aligned.rename(series).to_frame()


def large_moves(prices: pd.DataFrame, threshold: float = LARGE_MOVE) -> pd.Series:
    """Daily log returns bigger than the threshold in either direction."""
    returns = np.log(prices).diff().stack()
    return returns[returns.abs() > threshold]


def summary(
    prices: pd.DataFrame, filled: pd.Series, risk_free: pd.DataFrame
) -> list[str]:
    """Lines to print after a run, so the data can be checked by eye."""
    first, last = prices.index[0].date(), prices.index[-1].date()
    lines = [
        f"Prices: {len(prices)} days from {first} to {last}, "
        f"{prices.shape[1]} tickers",
        f"Risk-free: {risk_free.iloc[:, 0].min():.2f}% to "
        f"{risk_free.iloc[:, 0].max():.2f}% a year",
        "Filled days per ticker: " + ", ".join(f"{t} {n}" for t, n in filled.items()),
    ]

    for name, (start, end) in config.STRESS_PERIODS.items():
        status = "covered" if _covers(prices, start, end) else "NOT COVERED"
        lines.append(f"{name}: {status}")

    moves = large_moves(prices)
    if moves.empty:
        lines.append(f"No daily moves above {LARGE_MOVE:.0%}")
    else:
        lines.append(f"Daily moves above {LARGE_MOVE:.0%}, check these look real:")
        lines += [f"  {t} {d.date()} {r:+.1%}" for (d, t), r in moves.items()]
    return lines


def _covers(prices: pd.DataFrame, start: str, end: str) -> bool:
    return prices.index[0] <= pd.Timestamp(start) and prices.index[-1] >= pd.Timestamp(
        end
    )


def stress_periods_covered(prices: pd.DataFrame) -> bool:
    return all(_covers(prices, s, e) for s, e in config.STRESS_PERIODS.values())


def run(from_raw: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Download (unless from_raw), clean and save. Returns prices and risk-free."""
    if from_raw:
        raw_prices = pd.read_csv(config.RAW_PRICES_FILE, index_col=0, parse_dates=True)
        raw_rf = pd.read_csv(config.RAW_RISK_FREE_FILE, index_col=0, parse_dates=True)
    else:
        print("Downloading prices from Yahoo Finance...")
        raw_prices = download_prices()
        print("Downloading the risk-free rate from FRED...")
        raw_rf = download_risk_free()
        config.RAW_DIR.mkdir(parents=True, exist_ok=True)
        raw_prices.to_csv(config.RAW_PRICES_FILE)
        raw_rf.to_csv(config.RAW_RISK_FREE_FILE)

    prices, filled = clean_prices(raw_prices)
    risk_free = clean_risk_free(raw_rf, prices.index)

    if not stress_periods_covered(prices):
        raise ValueError("The data does not cover every stress period in config")

    config.CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    prices.to_csv(config.PRICES_FILE, float_format="%.6f")
    risk_free.to_csv(config.RISK_FREE_FILE, float_format="%.4f")

    print("\n".join(summary(prices, filled, risk_free)))
    print(f"Saved {config.PRICES_FILE.name} and {config.RISK_FREE_FILE.name}")
    return prices, risk_free


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--from-raw",
        action="store_true",
        help="skip the download and clean the files already in data/raw",
    )
    args = parser.parse_args(argv)
    try:
        run(from_raw=args.from_raw)
    except (RuntimeError, ValueError, FileNotFoundError, OSError) as err:
        print(f"Data step failed: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
