# Quant Edge Finals: Serendib University Endowment Fund

A Streamlit app that builds and defends a conservative USD 10m portfolio from
seven ETFs (SPY, EFA, EEM, AGG, GLD, XLE, XLK). It goes from real prices to a
recommendation: portfolio construction and KPIs, VaR and ES, extreme value
theory, backtesting, risk budgeting and stress tests.

Team Nexora. Live app: https://nexora-serendib.streamlit.app/

## Running the app

Python 3.12 is required.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
streamlit run app.py
```

`requirements.txt` has only what the app needs. `requirements-dev.txt` adds
yfinance for the data download plus the test and lint tools, so use that one
for local work.

Run the checks before opening a pull request:

```bash
pytest
ruff check .
black --check .
```

## Live app

The app is deployed on Streamlit Community Cloud: https://nexora-serendib.streamlit.app/

It redeploys by itself whenever `main` changes. The settings it uses:

- Repository `sameera-ekanayaka/Quantedge_Finals`, branch `main`
- Main file `app.py`
- Python 3.12 (set under Advanced settings when the app is created)
- Packages from `requirements.txt`, config from `.streamlit/config.toml`

The app reads the committed CSVs in `data/clean/`, so the cloud copy needs no
download step and no secrets. To try the same setup locally, install only
`requirements.txt` in a fresh environment and run `streamlit run app.py`.

## Project layout

```
app.py                 Streamlit entry point and page list
app/pages/             One file per app page, UI only
src/                   All calculations, one module per area
  config.py            Tickers, dates, paths, seeds
  data.py              load_prices, load_returns, load_risk_free
  get_data.py          Download and clean the data
notebooks/             Walkthroughs, e.g. the data cleaning steps
  ui.py                Shared sidebar and settings
tests/                 pytest tests, one file per module
data/clean/            Cleaned CSVs (committed)
data/raw/              Raw downloads (not committed)
docs/report/           Report sections, one markdown file each
docs/AI_DISCLOSURE.md  AI use disclosure table
```

Pages only call functions from `src/` and draw charts. No maths inside pages.

## Who owns what

| Person | Area | Code | App page |
|---|---|---|---|
| Sameera Ekanayaka | Repo, data, app shell, deploy | `src/data.py`, `src/ui.py`, `app.py` | Home, sidebar |
| Imasha Karunathilaka | Portfolio and recommendation | `src/portfolio.py`, `src/kpis.py` | Portfolio |
| Aadhila Anees | VaR, ES, risk budgeting | `src/var_es.py`, `src/risk_budget.py` | Risk dashboard |
| Praveen Madawalage | EVT, limitations | `src/evt.py` | EVT, Assumptions & Limitations |
| Tharindu Dhanushka | Backtesting, stress tests | `src/backtest.py`, `src/stress.py` | Backtesting, Stress tests |

## Shared functions

Agree on these before changing them, since other modules depend on them.

- `load_prices()`, `load_returns()`, `load_risk_free()` in `src/data.py`. Date
  index, one column per ticker. Returns are log returns.
- `portfolio_returns(returns, weights)` in `src/portfolio.py`. Daily simple
  returns.
- `var_es(returns, alpha, method)` in `src/var_es.py`. VaR and ES as positive
  loss numbers.
- `evt_var_es(losses, alpha, threshold)` in `src/evt.py`. VaR, ES and the
  fitted parameters.
- `rolling_backtest(returns, model, alpha, window)` in `src/backtest.py`.
  Forecasts and breaches.

Until the cleaned data is in `data/clean/`, use `stub_returns()` from
`src/data.py`. It has the same shape as `load_returns()`. Never use its
numbers in the report.

## Git rules

- Nobody works on `main`. It is protected, so direct pushes are refused.
- One branch per piece of work, always cut from the latest `main`:
  ```bash
  git switch main
  git pull
  git switch -c feat/var-es-engine
  ```
- Branch names are a prefix and a short topic: `feat/` new work, `fix/` bug
  fixes, `docs/` report and README, `test/` tests, `chore/` setup. For
  example `feat/evt-gpd-threshold`, `feat/backtest-kupiec`,
  `docs/report-stress-tests`.
- Small commits with a short plain message in the imperative, like
  "Add historical simulation VaR". No emojis, no em dashes.
- Before merging, pull the latest `main` into your branch, run `pytest` and
  `ruff check .`, and make sure the app still starts.
- Push your branch and open a pull request into `main`. One teammate reviews
  it (Imasha with Aadhila, Praveen with Tharindu, Sameera checks shared
  files). Merge once CI is green, then delete the branch.
- Only edit your own files. Shared files (`app.py`, `requirements.txt`,
  `src/config.py`, `src/ui.py`) go through Sameera with a small PR.
- Never commit credentials, or downloaded data other than the cleaned CSVs.
- Merge often. A branch that lives longer than a day is where conflicts
  come from.

## Coding standards

- PEP 8, formatted with black and checked with ruff.
- Type hints on public functions and a one or two line docstring.
- Comments only where the reason is not obvious. No commented out code, no
  debug prints.
- Tests for each module: shapes, a known value, an edge case.
- No hard coded paths (use `src/config.py`), fixed seed for Monte Carlo.
- Use `st.cache_data` for anything slow.

## Data sources

Prices from yfinance (adjusted close), the risk-free rate from FRED (3-month
T-bill, DTB3), macro context from the World Bank or IMF. No other sources.

## Getting the data

One command downloads, cleans and saves everything:

```bash
python -m src.get_data
```

It pulls adjusted closes for the seven ETFs from Yahoo Finance and DTB3 from
FRED, then:

- keeps trading days only, from 18 Nov 2004 (GLD's first day) to 27 Oct 2026
- fills gaps of up to 3 days with the last price and stops on anything longer
- lines the risk-free rate up with the price dates
- checks the 2008, March 2020 and 2022 stress periods are covered
- lists any daily move above 15% so it can be checked by eye

Raw downloads go to `data/raw/` (not committed). The cleaned `prices.csv`
and `risk_free.csv` go to `data/clean/`, along with `cleaning_report.json`,
which records what each step did. The app's Data page reads that report, and
`notebooks/data_cleaning.ipynb` walks through the same steps one at a time. To redo the cleaning
without downloading again, run `python -m src.get_data --from-raw`.

## AI disclosure

See [docs/AI_DISCLOSURE.md](docs/AI_DISCLOSURE.md).
