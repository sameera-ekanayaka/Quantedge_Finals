"""VaR backtesting: rolling forecasts, Kupiec, Christoffersen, Basel traffic light.

Owner: Tharindu Dhanushka
"""

from collections.abc import Callable

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import xlogy

from src import config
from src.var_es import var_es

# 500 days is two years: above the Basel one-year minimum, five tail points at
# 99%, and the first forecast lands in late 2006 so all of 2008 is out of sample.
DEFAULT_WINDOW = 500
WINDOW_CHOICES = [250, 500, 1000]

# Monte Carlo inside a rolling loop runs thousands of times, so fewer draws
BACKTEST_SIMULATIONS = 20_000

# Fitted models take 0.1 to 0.3 s per fit, so they are re-estimated monthly
# (21 trading days). Fits on 500 days barely move in a month.
REFIT_EVERY = {
    "historical": 1,
    "normal": 1,
    "student_t": 21,
    "monte_carlo": 21,
    "evt": 21,
}

# Basel zones for 99% VaR over 250 days: green 0-4, yellow 5-9, red 10+
BASEL_DAYS = 250
BASEL_ALPHA = 0.99
BASEL_GREEN_MAX = 4
BASEL_YELLOW_MAX = 9
# Plus factor added to the capital multiplier of 3, by number of breaches
BASEL_PLUS_FACTOR = {5: 0.40, 6: 0.50, 7: 0.65, 8: 0.75, 9: 0.85}

# Acerbi and Szekely (2014) Z2 cut-offs for 250 days at 97.5%. Indicative only
ES_Z2_YELLOW = 0.70
ES_Z2_RED = 1.80

VaRModel = Callable[[pd.Series, float], tuple[float, float]]

MODEL_LABELS = {**config.VAR_METHODS, "evt": "EVT (GPD)"}


def make_model(method: str) -> VaRModel:
    """A model for rolling_backtest: takes a return window, gives (VaR, ES)."""
    if method == "evt":
        from src.evt import evt_var_es

        def evt_model(window: pd.Series, alpha: float) -> tuple[float, float]:
            var, es, _ = evt_var_es(-window, alpha, threshold=None)
            return var, es

        return evt_model
    if method not in config.VAR_METHODS:
        raise ValueError(f"Unknown method '{method}'")

    def model(window: pd.Series, alpha: float) -> tuple[float, float]:
        return var_es(window, alpha, method, n_simulations=BACKTEST_SIMULATIONS)

    return model


def evt_available() -> bool:
    """True once src.evt.evt_var_es is implemented."""
    try:
        make_model("evt")(pd.Series(np.linspace(-0.05, 0.05, 200)), 0.99)
    except NotImplementedError:
        return False
    return True


def rolling_backtest(
    returns: pd.Series,
    model: VaRModel,
    alpha: float,
    window: int = DEFAULT_WINDOW,
    refit_every: int = 1,
) -> pd.DataFrame:
    """Out-of-sample VaR forecasts and a breach flag for each day.

    The forecast for day t uses only the `window` returns before t. With
    refit_every > 1 the model is re-estimated every that many days and the
    forecast is held in between, which keeps slow models practical.
    """
    returns = returns.dropna()
    if window < 30:
        raise ValueError("window must be at least 30 days")
    if len(returns) <= window:
        raise ValueError(f"Need more than {window} returns, got {len(returns)}")
    if refit_every < 1:
        raise ValueError("refit_every must be at least 1")

    values = returns.to_numpy()
    n_forecasts = len(values) - window
    var = np.empty(n_forecasts)
    es = np.empty(n_forecasts)
    for i in range(n_forecasts):
        if i % refit_every == 0:
            history = returns.iloc[i : i + window]
            current = model(history, alpha)
        var[i], es[i] = current

    realised = values[window:]
    loss = -realised
    return pd.DataFrame(
        {"return": realised, "var": var, "es": es, "breach": loss > var},
        index=returns.index[window:],
    )


def run_backtest(
    returns: pd.Series, method: str, alpha: float, window: int = DEFAULT_WINDOW
) -> pd.DataFrame:
    """rolling_backtest for a named method, with that method's refit schedule."""
    return rolling_backtest(
        returns, make_model(method), alpha, window, REFIT_EVERY[method]
    )


def kupiec_test(breaches: int, days: int, alpha: float) -> dict:
    """Kupiec proportion of failures test: is the breach rate 1 - alpha?"""
    if days <= 0:
        raise ValueError("days must be positive")
    p = 1 - alpha
    rate = breaches / days
    log_null = xlogy(days - breaches, 1 - p) + xlogy(breaches, p)
    log_alt = xlogy(days - breaches, 1 - rate) + xlogy(breaches, rate)
    lr = float(-2 * (log_null - log_alt))
    return {
        "breaches": int(breaches),
        "expected": days * p,
        "rate": rate,
        "lr": lr,
        "p_value": float(stats.chi2.sf(lr, df=1)),
    }


def _transitions(breach: np.ndarray) -> tuple[int, int, int, int]:
    """Counts of day-to-day moves: (no to no, no to yes, yes to no, yes to yes)."""
    prev, curr = breach[:-1], breach[1:]
    n00 = int(np.sum(~prev & ~curr))
    n01 = int(np.sum(~prev & curr))
    n10 = int(np.sum(prev & ~curr))
    n11 = int(np.sum(prev & curr))
    return n00, n01, n10, n11


def christoffersen_test(breach: pd.Series | np.ndarray, alpha: float) -> dict:
    """Christoffersen independence and conditional coverage tests.

    Independence asks whether a breach today makes one tomorrow more likely.
    Conditional coverage combines that with Kupiec, so it has 2 degrees of
    freedom.
    """
    hits = np.asarray(breach, dtype=bool)
    if len(hits) < 2:
        raise ValueError("Need at least two days")
    n00, n01, n10, n11 = _transitions(hits)
    pi01 = n01 / (n00 + n01) if n00 + n01 else 0.0
    pi11 = n11 / (n10 + n11) if n10 + n11 else 0.0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)

    log_null = xlogy(n00 + n10, 1 - pi) + xlogy(n01 + n11, pi)
    log_alt = (
        xlogy(n00, 1 - pi01)
        + xlogy(n01, pi01)
        + xlogy(n10, 1 - pi11)
        + xlogy(n11, pi11)
    )
    lr_ind = float(max(-2 * (log_null - log_alt), 0.0))
    lr_pof = kupiec_test(int(hits.sum()), len(hits), alpha)["lr"]
    lr_cc = lr_pof + lr_ind
    return {
        "n00": n00,
        "n01": n01,
        "n10": n10,
        "n11": n11,
        "pi01": pi01,
        "pi11": pi11,
        "lr_ind": lr_ind,
        "p_value_ind": float(stats.chi2.sf(lr_ind, df=1)),
        "lr_cc": lr_cc,
        "p_value_cc": float(stats.chi2.sf(lr_cc, df=2)),
    }


def traffic_light(breaches: int, days: int = BASEL_DAYS, alpha: float = 0.99) -> str:
    """Basel zone: 'green', 'yellow', 'red', or 'n/a' when it does not apply.

    The official zones are for 99% VaR over 250 days. For other lengths at
    99% we use the rule Basel built them from: green while the binomial
    probability of that many breaches or fewer is below 95%, red from 99.99%.
    """
    if not np.isclose(alpha, BASEL_ALPHA):
        return "n/a"
    if days == BASEL_DAYS:
        if breaches <= BASEL_GREEN_MAX:
            return "green"
        return "yellow" if breaches <= BASEL_YELLOW_MAX else "red"
    cumulative = stats.binom.cdf(breaches, days, 1 - alpha)
    if cumulative < 0.95:
        return "green"
    return "yellow" if cumulative < 0.9999 else "red"


def basel_multiplier(breaches: int) -> float:
    """Capital multiplier for 99% VaR over 250 days: 3 plus the plus factor."""
    if breaches <= BASEL_GREEN_MAX:
        return 3.0
    return 3.0 + BASEL_PLUS_FACTOR.get(breaches, 1.0)


def es_backtest(results: pd.DataFrame, alpha: float) -> dict:
    """Acerbi and Szekely Z2 test of the ES forecasts, plus a severity ratio.

    Z2 near 0 means breach losses match the forecast ES on average. Positive
    values mean ES was too low. The cut-offs are indicative, not exact.
    """
    loss = -results["return"]
    hit = results["breach"].astype(float)
    z2 = float((loss * hit / ((1 - alpha) * results["es"])).mean() - 1)
    breached = results[results["breach"]]
    ratio = (
        float((-breached["return"] / breached["es"]).mean())
        if len(breached)
        else float("nan")
    )
    if z2 >= ES_Z2_RED:
        zone = "red"
    elif z2 >= ES_Z2_YELLOW:
        zone = "yellow"
    else:
        zone = "green"
    return {"z2": z2, "loss_to_es": ratio, "zone": zone}


def summarise(results: pd.DataFrame, alpha: float) -> dict:
    """All the tests for one backtest run, as one flat record."""
    days = len(results)
    breaches = int(results["breach"].sum())
    kupiec = kupiec_test(breaches, days, alpha)
    christoffersen = christoffersen_test(results["breach"], alpha)
    last = results.tail(BASEL_DAYS)
    last_breaches = int(last["breach"].sum())
    return {
        "days": days,
        "breaches": breaches,
        "expected": kupiec["expected"],
        "breach_rate": kupiec["rate"],
        "kupiec_lr": kupiec["lr"],
        "kupiec_p": kupiec["p_value"],
        "ind_lr": christoffersen["lr_ind"],
        "ind_p": christoffersen["p_value_ind"],
        "cc_lr": christoffersen["lr_cc"],
        "cc_p": christoffersen["p_value_cc"],
        "zone_full": traffic_light(breaches, days, alpha),
        "last_250_breaches": last_breaches,
        "zone_last_250": traffic_light(last_breaches, len(last), alpha),
        **{f"es_{k}": v for k, v in es_backtest(results, alpha).items()},
    }


def backtest_by_period(
    results: pd.DataFrame,
    alpha: float,
    periods: dict[str, tuple[str, str]] = config.STRESS_PERIODS,
) -> pd.DataFrame:
    """Breach counts and Kupiec p-values for the full sample, each stress period
    and the calm days outside them."""
    stressed = pd.Series(False, index=results.index)
    slices = {"Full sample": results}
    for name, (start, end) in periods.items():
        mask = (results.index >= start) & (results.index <= end)
        stressed |= mask
        slices[name] = results[mask]
    slices["Calm days (outside stress periods)"] = results[~stressed]

    rows = []
    for name, part in slices.items():
        if part.empty:
            continue
        breaches = int(part["breach"].sum())
        kupiec = kupiec_test(breaches, len(part), alpha)
        rows.append(
            {
                "period": name,
                "days": len(part),
                "breaches": breaches,
                "expected": kupiec["expected"],
                "breach_rate": kupiec["rate"],
                "kupiec_p": kupiec["p_value"],
            }
        )
    return pd.DataFrame(rows).set_index("period")


def main() -> None:
    """Print the backtest tables used in the report, for the risk parity mix."""
    from src.data import load_returns, load_risk_free
    from src.portfolio import annual_risk_free, candidate_portfolios, portfolio_returns

    returns = load_returns()
    rf = annual_risk_free(load_risk_free(), returns.index)
    weights = candidate_portfolios(returns, rf)["Risk parity"]
    series = portfolio_returns(returns, weights)
    methods = [m for m in MODEL_LABELS if m != "evt" or evt_available()]
    for alpha in (0.95, 0.99):
        rows = {}
        for method in methods:
            results = run_backtest(series, method, alpha)
            rows[MODEL_LABELS[method]] = summarise(results, alpha)
            if alpha == 0.99:
                print(f"\nBy period, 99%, {MODEL_LABELS[method]}")
                print(backtest_by_period(results, alpha).round(4).to_string())
        print(f"\nSummary at {alpha:.0%}")
        print(pd.DataFrame(rows).T.to_string())


if __name__ == "__main__":
    main()
