# Section 1: Data

**Owner:** Sameera Ekanayaka
**Code:** `src/get_data.py` and `src/data.py`, tested in `tests/test_get_data.py` and `tests/test_data.py`
**App page:** Data
**Reproduce:** `python -m src.get_data` (download and clean), or `python -m src.get_data --from-raw`

## 1.1 Sources and period

| Data | Source | Series |
|---|---|---|
| ETF prices | Yahoo Finance through `yfinance` | Adjusted close for SPY, EFA, EEM, AGG, GLD, XLE, XLK |
| Risk-free rate | FRED | DTB3, 3-month Treasury bill, annualised percent |

We use adjusted close so dividends are in the returns. Without them AGG, which
earns most of its return as income, would look far worse than it is.

Prices run from **18 Nov 2004 to 27 Oct 2026** (5,519 trading days). The start
is the first day GLD traded, the last of the seven to list, so every day has a
price for every ETF. The end date is fixed in `src/config.py` so a rerun gives
the same data, and the cleaned files are committed in `data/clean/`. The
period covers 2008, March 2020 and 2022, and the script stops if any of them
is missing.

## 1.2 Cleaning

Each step is a small function in `src/get_data.py`. Its row count is saved to
`cleaning_report.json`, which the Data page shows.

| Step | What it does | Rows removed |
|---|---|---|
| Tidy and trim | Sorts dates, drops duplicates, keeps the study period | 0 |
| Bad ticks and holidays | Zero or negative prices become missing, days with no trades are dropped | 0 |
| Common start | Starts on the first day all seven trade | 0 |
| Fill short gaps | Carries the last price over gaps of up to 3 days, stops on longer ones | 0 (0 filled) |

Yahoo's adjusted data was already clean, so no step changed anything. We kept
the steps so a future rerun is safe: a short gap is filled, a long one stops
the run instead of being guessed.

FRED does not publish on bond market holidays that are normal stock trading
days, so on those **41 days** we carry the last rate forward. The daily rate is
annual / 100 / 252.

The script lists any daily move above 15% for a manual check. There are eight,
all in October 2008 (EEM, XLE) and March 2020 (XLE). They are real market
events, so we keep them. Removing them would hide the tail risk this project
is about.

We model with daily **log returns** (`load_returns()`), which add up over time.
Whenever ETFs are combined into a portfolio or a return becomes USD, we
convert to **simple returns**, which add up across assets.

## 1.3 What the data looks like

Daily simple returns, Nov 2004 to Oct 2026. Excess kurtosis is 0 for a normal
distribution.

| ETF | Annual return | Annual volatility | Max drawdown | Worst day | Excess kurtosis |
|---|---|---|---|---|---|
| SPY | 10.9% | 18.8% | -55.2% | -10.9% (16 Mar 2020) | 15.5 |
| EFA | 6.3% | 20.9% | -61.0% | -11.2% (29 Sep 2008) | 14.3 |
| EEM | 7.1% | 27.5% | -66.4% | -16.2% (15 Oct 2008) | 17.8 |
| AGG | 2.9% | 5.2% | -18.4% | -6.8% (10 Oct 2008) | 50.5 |
| GLD | 10.2% | 18.3% | -45.6% | -10.3% (30 Jan 2026) | 6.4 |
| XLE | 9.3% | 29.6% | -71.3% | -20.1% (9 Mar 2020) | 11.6 |
| XLK | 15.6% | 22.6% | -53.0% | -13.8% (16 Mar 2020) | 9.8 |

Three things here shape the rest of the report:

1. **Every ETF has fat tails** (excess kurtosis 6 to 50), so a normal model
   understates the worst days. That is why Section 3 compares four VaR methods
   and Section 4 fits EVT to the tail.
2. **AGG is calm but not safe.** It has by far the lowest volatility but the
   highest kurtosis: long quiet spells broken by sharp falls, as in October
   2008 and 2022.
3. **Diversification comes from asset classes, not regions.** The five equity
   ETFs, XLE and XLK included, move closely together (correlations 0.54 to 0.91). AGG has a
   correlation of about 0 with every equity ETF, and GLD 0.06 to 0.20.
