"""Post-submission model extensions; original results are preserved."""

import numpy as np
import pandas as pd
from arch import arch_model
from scipy import stats
from scipy.optimize import linprog, minimize

from src import config
from src.backtest import summarise
from src.data import log_to_simple
from src.evt import evt_var_es, fit_gpd
from src.portfolio import TICKERS, asset_stats, get_bounds
from src.stress import INFLATION_SHOCK, asset_period_returns
from src.var_es import var_es

DOLLAR_CRASH = dict(
    zip(TICKERS, [-0.35, -0.40, -0.45, 0.05, -0.10, -0.40, -0.40], strict=True)
)


def stress_vectors(returns):
    """Historical buy-and-hold period returns and two assumed instant shocks."""
    vectors = {
        name: asset_period_returns(returns, *period).reindex(TICKERS)
        for name, period in config.STRESS_PERIODS.items()
    }
    vectors["Inflation shock"] = pd.Series(INFLATION_SHOCK).reindex(TICKERS)
    vectors["Equity crash and dollar spike (assumption)"] = pd.Series(
        DOLLAR_CRASH
    ).reindex(TICKERS)
    return pd.DataFrame(vectors).T


def constrained_sharpe(
    returns, rf_annual, stress_limit=0.15, es_limit=0.02, var_limit=0.015, alpha=0.99
):
    """New in-sample alternative: hard scenario and empirical daily risk limits.

    Uses exact empirical tail ES, not Gaussian ES. Enforces original bounds,
    full investment, all historical window shocks and both assumed shocks.
    Does not constrain path drawdown. Never replaces the submitted weights.
    """
    simple = log_to_simple(returns[TICKERS]).to_numpy()
    mu, cov = asset_stats(returns[TICKERS])
    shocks = stress_vectors(returns).to_numpy()
    feasible = linprog(
        np.zeros(7),
        A_ub=-shocks,
        b_ub=np.full(len(shocks), stress_limit),
        A_eq=np.ones((1, 7)),
        b_eq=[1],
        bounds=get_bounds(),
        method="highs",
    )
    if not feasible.success:
        raise ValueError("Scenario limits infeasible under the original asset bounds")

    def risk(w):
        return var_es(pd.Series(simple @ w), alpha, "historical")

    def objective(w):
        return -(mu.to_numpy() @ w - rf_annual) / np.sqrt(w @ cov.to_numpy() @ w)

    result = minimize(
        objective,
        feasible.x,
        method="SLSQP",
        bounds=get_bounds(),
        constraints=[
            {"type": "eq", "fun": lambda w: w.sum() - 1},
            {"type": "ineq", "fun": lambda w: shocks @ w + stress_limit},
            {"type": "ineq", "fun": lambda w: es_limit - risk(w)[1]},
            {"type": "ineq", "fun": lambda w: var_limit - risk(w)[0]},
        ],
        options={"maxiter": 1000, "ftol": 1e-11},
    )
    if not result.success:
        raise RuntimeError(f"Constrained solve failed: {result.message}")
    w = pd.Series(result.x, index=TICKERS)
    v, e = risk(result.x)
    if (
        min(shocks @ result.x + stress_limit) < -1e-7
        or e > es_limit + 1e-7
        or v > var_limit + 1e-7
    ):
        raise RuntimeError(
            "Returned allocation failed independent risk-limit validation"
        )
    return w


def joint_bootstrap_risk(returns, weights, alpha=0.99, draws=100000, seed=config.SEED):
    """Joint ETF row bootstrap preserves contemporaneous empirical dependence.

    Each Monte Carlo draw resamples one complete seven-ETF observation, then
    combines simple returns with weights. No time dependence or unseen crashes.
    """
    simple = log_to_simple(returns[TICKERS]).dropna().to_numpy()
    indices = np.random.default_rng(seed).integers(0, len(simple), draws)
    simulated = simple[indices] @ weights.reindex(TICKERS).to_numpy()
    return var_es(pd.Series(simulated), alpha, "historical")


def alternative_threshold(losses, min_exceedances=100):
    """Exploratory minimum KS discrepancy among prespecified quantiles.

    Fit each candidate GPD then minimise its in-sample CDF discrepancy.
    This is a diagnostic rule, not a valid goodness-of-fit hypothesis test.
    """
    rows = []
    for q in (0.80, 0.85, 0.90, 0.925, 0.95, 0.975):
        u = float(losses.quantile(q))
        y = losses[losses > u] - u
        if len(y) < min_exceedances:
            continue
        xi, sigma = fit_gpd(y)
        distance = float(stats.kstest(y, "genpareto", args=(xi, 0, sigma)).statistic)
        rows.append(
            {
                "Quantile": q,
                "Threshold": u,
                "Exceedances": len(y),
                "KS distance": distance,
            }
        )
    if not rows:
        raise ValueError("Too few exceedances for any candidate threshold")
    table = pd.DataFrame(rows)
    return float(table.loc[table["KS distance"].idxmin(), "Threshold"]), table


def evt_bootstrap(losses, alpha=0.99, quantile=0.90, repeats=200, seed=config.SEED):
    """IID percentile bootstrap, refitting threshold and GPD each replicate.

    Does not capture volatility clustering; intervals may understate uncertainty.
    Nonfinite ES is reported as a failed replicate, never silently discarded.
    """
    rng = np.random.default_rng(seed)
    records = []
    failures = 0
    for _ in range(repeats):
        sample = pd.Series(rng.choice(losses.to_numpy(), len(losses), replace=True))
        try:
            v, e, _ = evt_var_es(
                sample, alpha, threshold=float(sample.quantile(quantile))
            )
            if not np.isfinite([v, e]).all():
                failures += 1
            else:
                records.append((v, e))
        except (ValueError, RuntimeError, FloatingPointError):
            failures += 1
    if len(records) < max(10, int(0.8 * repeats)):
        raise RuntimeError(f"Only {len(records)}/{repeats} bootstrap replicates valid")
    values = np.array(records)
    return pd.DataFrame(
        {
            "Measure": ["VaR", "ES"],
            "2.5%": np.quantile(values, 0.025, axis=0),
            "97.5%": np.quantile(values, 0.975, axis=0),
            "Valid replicates": len(records),
            "Failed replicates": failures,
        }
    )


def conditional_backtests(returns, alpha=0.99, window=500, refit_every=21):
    """GARCH(1,1) Gaussian QMLE with daily variance recursion and monthly refits.

    At each refit, all fits and residual-tail estimates use only the preceding
    window. Parameters and residual distributions stay fixed between refits;
    conditional variance updates daily with the last observed return.
    """
    if len(returns) <= window or window < 100 or refit_every < 1:
        raise ValueError("Insufficient history or invalid refit schedule")
    values = returns.to_numpy() * 100
    records = {"GARCH filtered HS": [], "GARCH EVT": []}
    for i in range(window, len(values)):
        if (i - window) % refit_every == 0:
            history = values[i - window : i]
            fitted = arch_model(
                history,
                mean="Constant",
                vol="GARCH",
                p=1,
                q=1,
                dist="normal",
                rescale=False,
            ).fit(disp="off", show_warning=False)
            if fitted.convergence_flag != 0:
                raise RuntimeError(f"GARCH fit did not converge at {returns.index[i]}")
            params = fitted.params
            mu = float(params["mu"])
            omega = float(params["omega"])
            a = float(params["alpha[1]"])
            b = float(params["beta[1]"])
            previous_variance = float(
                np.asarray(fitted.conditional_volatility)[-1] ** 2
            )
            residuals = pd.Series(np.asarray(fitted.std_resid)).dropna()
            hs = var_es(residuals, alpha, "historical")
            ev, ee, _ = evt_var_es(
                -residuals, alpha, threshold=float((-residuals).quantile(0.90))
            )
            tail = {"GARCH filtered HS": hs, "GARCH EVT": (ev, ee)}
        variance = omega + a * (values[i - 1] - mu) ** 2 + b * previous_variance
        sigma = np.sqrt(variance)
        for name, (v, e) in tail.items():
            forecast_v = (-mu + sigma * v) / 100
            forecast_e = (-mu + sigma * e) / 100
            records[name].append(
                {
                    "return": values[i] / 100,
                    "var": forecast_v,
                    "es": forecast_e,
                    "breach": -values[i] / 100 > forecast_v,
                }
            )
        previous_variance = variance
    frames = {
        name: pd.DataFrame(rows, index=returns.index[window:])
        for name, rows in records.items()
    }
    summary = pd.DataFrame(
        [{"Model": name, **summarise(frame, alpha)} for name, frame in frames.items()]
    )
    return frames, summary


def joint_bootstrap_backtest(returns, weights, alpha=0.99, window=500, refit_every=21):
    """Monthly joint-ETF bootstrap fits, evaluated on next observations."""
    if len(returns) <= window:
        raise ValueError("Insufficient history")
    portfolio = log_to_simple(returns[TICKERS]) @ weights.reindex(TICKERS)
    rows = []
    for i in range(window, len(returns)):
        if (i - window) % refit_every == 0:
            v, e = joint_bootstrap_risk(
                returns.iloc[i - window : i], weights, alpha, draws=20000
            )
        r = float(portfolio.iloc[i])
        rows.append({"return": r, "var": v, "es": e, "breach": -r > v})
    return pd.DataFrame(rows, index=returns.index[window:])
