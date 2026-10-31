"""Build replacement-submission sources from reproducible model outputs."""

# Long lines below are literal Markdown paragraphs for report generation.
# ruff: noqa: E501
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd

from src import config
from src.advanced_validation import joint_bootstrap_risk, stress_vectors
from src.data import load_returns, load_risk_free
from src.evt import evt_var_es
from src.kpis import kpi_table
from src.portfolio import (
    annual_risk_free,
    candidate_kpis,
    candidate_portfolios,
    construct_final_portfolio,
    final_weights,
    min_es,
    portfolio_returns,
)
from src.risk_budget import risk_budget
from src.var_es import var_es

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/report"
OUT = ROOT / "submission/advanced"
r = load_returns()
rf = annual_risk_free(load_risk_free(), r.index)
w = final_weights()
p = portfolio_returns(r, w)
solved = construct_final_portfolio(r, rf)
assert np.allclose(solved, w, atol=0.0001)
assert (stress_vectors(r) @ w >= -config.SCENARIO_LOSS_LIMIT).all()
v, e = var_es(p, 0.99, "historical")
assert v <= config.DAILY_VAR_LIMIT and e <= config.DAILY_ES_LIMIT
pd.DataFrame({"Constrained solve": solved, "Frozen target": w}).to_csv(
    OUT / "final_construction.csv"
)


def table(frame, formats=None, index=False):
    result = frame.copy()
    if formats:
        for key, fmt in formats.items():
            result[key] = result[key].map(fmt.format)
    return result.to_markdown(index=index)


def write(name, text):
    (REPORT / name).write_text(text.strip() + "\n")


candidates = candidate_portfolios(r, rf)
candidates["Minimum ES"] = min_es(r)
kpis = (
    candidate_kpis(r, candidates, rf)
    .loc[["Annual return", "Annual volatility", "Sharpe", "Max drawdown"]]
    .T
)
wf = pd.read_csv(ROOT / "submission/supplementary/walk_forward.csv")
policy = pd.read_csv(OUT / "benchmark_kpis.csv")
write(
    "02_mandate_portfolio.md",
    f"""
# Section 2: Mandate, construction and decision

**Decision: ADJUST the scenario-loss limit to 18%, retaining the Maximum Sharpe allocation.** This is a proposed mandate change requiring committee agreement, not acceptance of the original 15% ceiling. Weights were selected and evaluated on the same 2004–2026 sample; historical performance is not a forecast.

## 2.1 Explicit construction constraints

The USD 10m long-only fund has no leverage. Bounds are SPY 0–40%, EFA 0–30%, EEM 0–10%, AGG 30–60%, GLD 0–15%, XLE 0–10%, XLK 0–15%. Full investment is required. The final solve additionally enforces 99% historical one-day VaR ≤ 1.5% and ES ≤ 2.0%, and loss ≤ 18% in all three historical crisis windows and both hypothetical scenarios. `construct_final_portfolio` runs this SLSQP solve from a scenario-feasible linear-programming start; infeasibility or a failed post-solve check raises an error. It is a numerical local solve, not a proof of global optimality. Benchmarks are constructed separately and need not satisfy every final risk constraint.

The constrained solve produces SPY 9.5494%, AGG 58.8471%, GLD 15%, XLE 1.6034%, XLK 15%. We freeze rounded targets of 9.55%, 58.85%, 15%, 1.60%, 15% respectively, with EFA/EEM zero, and verify that rounding still satisfies the risk limits. The full-precision solve and targets are archived in `submission/advanced/final_construction.csv`.

**Why 18%:** an initial 10% idea and then a 15% proposed scenario limit were reviewed after observing candidate results. Neither was independently calibrated. We now openly propose 18% because the retained allocation loses 17.215% in our inflation scenario, leaving only 0.785 percentage points of modeled headroom. This is a retrospective policy choice, not statistical evidence that 18% is safe. If the committee requires 15%, do not approve this allocation under that mandate. A feasible 15%-constrained alternative exists, but raises March 2020 loss to 11.38% and full-sample drawdown to 19.58%; see Section 6. We prefer the original allocation's historical drawdown and request the limit adjustment explicitly.

The scenario limit measures full-window or instantaneous scenario loss, **not peak-to-trough drawdown**. The retained allocation's maximum drawdown is 18.27%, greater than 18%; no 18% drawdown ceiling is imposed or claimed. Historical 99% VaR is {v:.3%}, ES {e:.3%}. These constraints are sample-dependent and cannot guarantee future compliance.

## 2.2 Candidates and KPIs

Mean/covariance Markowitz construction uses daily simple returns. Maximum Sharpe maximises excess arithmetic mean divided by volatility; Minimum variance minimises variance; risk parity equalises variance contributions subject to bounds. Minimum ES uses a historical CVaR linear programme. The bounded equal-weight candidate is closest to 1/7 subject to bounds; it is not an unconstrained benchmark.

{table(kpis.reset_index(names="Candidate"), {"Annual return": "{:.2%}", "Annual volatility": "{:.2%}", "Sharpe": "{:.3f}", "Max drawdown": "{:.2%}"})}

Return is CAGR; volatility uses 252 trading days. Sharpe, Sortino, Treynor, CAPM beta/Jensen alpha, information ratio, drawdown and Calmar are implemented in `src/kpis.py`. SPY is retained for market comparison; a 40% SPY/60% AGG daily-rebalanced policy benchmark better reflects the bond-heavy mandate. The final allocation's information ratio is 0.197 against policy versus −0.332 against SPY. Benchmark choice changes interpretation, not the underlying return.

Our 7.0% nominal objective (4.5% spending plus 2.5% inflation), 7.4% and 7.8% sensitivities are team assumptions. Historical 7.42% CAGR clears 7.0%, approximately meets 7.4% and misses 7.8%. Income distributions, taxes and costs are not separately modeled. Daily rebalancing underlies headline returns; quarterly sensitivity is 7.3% return and −18.7% drawdown.

## 2.3 Full KPI set for retained allocation

{table(kpi_table(p, np.expm1(r["SPY"]), rf).rename("Value").rename_axis("KPI").reset_index(), {"Value": "{:.5f}"})}

Values above are decimals (returns, volatility, alpha and drawdown), or unitless ratios. CAPM beta is covariance with SPY divided by SPY variance; Jensen alpha is annual portfolio excess mean minus beta times annual SPY excess mean. Sharpe uses total volatility, Sortino uses downside deviation, Treynor scales excess return by beta, information ratio uses benchmark-relative tracking error, and Calmar divides CAGR by absolute maximum drawdown. All metrics use consistent daily simple-return inputs and annualisation conventions in the code.

## 2.4 Walk-forward allocation validation

Each January from 2010, re-estimate Maximum Sharpe and Minimum variance from preceding observations only (minimum 756 days). Apply each year's allocation with daily target rebalancing. Asset bounds are enforced; this validates the baseline selection rules, not a walk-forward strategy with the retrospectively revised scenario limit. Costs are excluded. Evaluation dates are identical, 4 January 2010 to 27 October 2026.

{table(wf[["Strategy", "Annual return", "Volatility", "Sharpe", "Max drawdown"]], {"Annual return": "{:.2%}", "Volatility": "{:.2%}", "Sharpe": "{:.3f}", "Max drawdown": "{:.2%}"})}

The frozen comparator retains full-sample selection bias. Maximum Sharpe preserves a return advantage but loses to Minimum variance on walk-forward Sharpe. We therefore justify the selection as a return/risk preference, not demonstrated out-of-sample superiority. The allocation and revised policy still require committee judgment. Annual training cutoffs and weights are archived for reproduction.
""",
)

risk = []
for a in (0.95, 0.99):
    for key, label in config.VAR_METHODS.items():
        vv, ee = var_es(p, a, key)
        risk.append({"Confidence": a, "Model": label, "VaR": vv, "ES": ee})
    vv, ee = joint_bootstrap_risk(r, w, a)
    risk.append({"Confidence": a, "Model": "Joint ETF bootstrap", "VaR": vv, "ES": ee})
    vv, ee, _ = evt_var_es(-p, a, threshold=None)
    risk.append({"Confidence": a, "Model": "EVT / GPD", "VaR": vv, "ES": ee})
risk = pd.DataFrame(risk)
risk.to_csv(OUT / "final_daily_risk.csv", index=False)
budget = risk_budget(r, w, 0.99, "historical")
write(
    "03_var_es_risk_budget.md",
    f"""
# Section 3: VaR, Expected Shortfall and risk budget

All estimates are one-day positive losses on USD 10m. VaR is a loss quantile; ES measures average loss beyond that quantile. ES is coherent under its population definition; finite-sample estimates remain uncertain. Historical daily VaR/ES are hard constraints in the final construction, while other models are independent monitoring estimates.

## 3.1 Methods and results

Historical simulation uses the empirical quantile and tail mean. Gaussian VaR/ES use the sample mean and variance; Student t fits degrees of freedom, location and scale. The original Monte Carlo samples that fitted portfolio-level t and is retained as a parametric reference. Its agreement with Student t is expected, not independent corroboration. The new joint ETF bootstrap instead samples entire seven-ETF return vectors before applying weights, preserving empirical contemporaneous dependence. Static estimates use 100,000 draws, seed 42. It is close to historical simulation by design, ignores serial dependence and cannot generate unseen crash regimes. GARCH-filtered alternatives are evaluated in Section 5.

{table(risk, {"Confidence": "{:.0%}", "VaR": "{:.3%}", "ES": "{:.3%}"})}

To convert a decimal risk estimate into dollars, multiply by USD 10m. Across all new documents percentages use consistent rounding and dollar amounts are derived from full-precision estimates. Normal 99% ES is about USD 117,310 versus EVT USD 172,578: an approximate USD 55,268 gap. This is a model comparison, not an error bound. The dashboard shows grouped VaR/ES bars and a numeric table at the selected confidence.

## 3.2 Concentration and attribution

{table(budget[["weight", "component_var", "component_es", "pct_es_contrib"]].reset_index(names="ETF"), {"weight": "{:.2%}", "component_var": "{:.3%}", "component_es": "{:.3%}", "pct_es_contrib": "{:.2%}"})}

Technology is only 15% of capital but about 36.5% of historical ES. Historical ES contributions sum to portfolio ES through tail conditional expectations. Historical component VaR is a local approximation around the empirical quantile and need not reconcile exactly; it must not be presented as exact Euler allocation. Parametric Gaussian contributions use Euler derivatives. A large bond weight reduces ordinary volatility but creates rate and correlation risk, as 2022 demonstrates. The mean tail contains only about 55 days at 99%, so concentration figures are imprecise.
""",
)

sens = pd.read_csv(ROOT / "submission/supplementary/evt_sensitivity.csv")
ci = pd.read_csv(OUT / "evt_bootstrap.csv")
write(
    "04_evt.md",
    f"""
# Section 4: Extreme Value Theory and tail uncertainty

POT models loss exceedances Y = X − u. Under appropriate asymptotic conditions their conditional distribution approaches GPD: G(y) = 1 − (1 + ξy/σ)<sup>−1/ξ</sup>, σ > 0, y ≥ 0, 1 + ξy/σ > 0. Positive ξ means a power-law heavy tail; ξ = 0 is an unbounded exponential/Gumbel tail; negative ξ has a finite endpoint. This is an asymptotic approximation, not proof that financial losses follow a stable GPD.

## 4.1 Justified threshold and a second rule

The headline threshold is the 90th percentile of portfolio losses, 0.447%, with 552 exceedances in 5,518 observations. Mean-excess, shape/modified-scale stability and Q–Q plots support visual review. They do not automatically select the threshold. Fitted ξ = 0.1843 and σ = 0.002696 imply heavy tails. App and dashboard use the same threshold-selection function.

{table(sens[["Threshold quantile", "Threshold", "Exceedances", "Shape", "VaR", "ES"]], {"Threshold quantile": "{:.1%}", "Threshold": "{:.3%}", "Shape": "{:.3f}", "VaR": "{:.3%}", "ES": "{:.3%}"})}

All risk columns above are at 99%. VaR/ES vary modestly over this grid while shape changes materially. A second exploratory rule minimises the fitted GPD's in-sample KS CDF discrepancy over this same prespecified grid, requiring at least 100 exceedances. It selects the 80th percentile, giving 99% VaR 1.239% and ES 1.710%. The fitted KS score is not a valid unadjusted hypothesis test, and this rule is not claimed statistically optimal. The 90th-percentile model remains the headline estimate.

## 4.2 Formulas and intervals

Let p = N<sub>u</sub>/N. For α inside the fitted tail and ξ ≠ 0, VaR<sub>α</sub> = u + (σ/ξ)[(p/(1 − α))<sup>ξ</sup> − 1]. ES<sub>α</sub> = (VaR<sub>α</sub> + σ − ξu)/(1 − ξ), requiring ξ < 1. At ξ = 0, VaR = u + σ log(p/(1 − α)) and ES = VaR + σ. For ξ ≥ 1 theoretical ES is infinite. Requests below the fitted tail are rejected, not extrapolated into the body.

{table(ci[["Measure", "2.5%", "97.5%", "Valid replicates", "Failed replicates"]], {"2.5%": "{:.3%}", "97.5%": "{:.3%}"})}

These are 95% percentile intervals at 99% confidence from 200 IID bootstrap samples, seed 42, reselecting the 90th percentile and refitting the GPD each time. Failed/nonfinite replicates are counted; too many failures stop reporting. IID resampling ignores clustering and may understate uncertainty. Sensitivity tables and intervals measure different uncertainties and neither guarantees future coverage. At 90% confidence the bootstrap page uses an 89th-percentile threshold to avoid boundary/body extrapolation with resampled ties.
""",
)

bt = pd.concat(
    [
        pd.read_csv(OUT / "backtest_summary.csv"),
        pd.read_csv(OUT / "final_original_backtests.csv"),
    ],
    ignore_index=True,
)
write(
    "05_backtesting.md",
    f"""
# Section 5: Backtesting and conditional risk

## 5.1 Honest validation design

Risk forecasts use prior returns conditional on fixed weights. The weights themselves were chosen in sample; this is not an out-of-sample allocation test. A 500-day estimation window yields 5,018 forecasts from November 2006. The comparison below uses identical dates from January 2008 through October 2026: 4,735 forecasts. Allocation walk-forward validation is reported separately in Section 2.

Historical and Gaussian models refit daily. Original Student t, parametric Monte Carlo and EVT refit every 21 trading days and hold forecasts between fits. The joint ETF bootstrap also refits monthly, with 20,000 draws. Forecast CSVs record every return, VaR/ES and breach for the models below. The app's original Backtesting page also offers 250/500/1000-day windows and date controls.

## 5.2 GARCH extensions

GARCH(1,1) with constant mean uses Gaussian quasi-maximum-likelihood on the preceding 500 returns in percentage units, refitting every 21 days. Conditional variance updates daily using only the last observed residual. Filtered historical simulation estimates standardised residual-tail VaR/ES; GARCH-EVT fits the residual 90th-percentile loss tail. Transform these by next-day conditional volatility and mean. Convergence failures raise errors. Prefix-invariance tests ensure changing future returns cannot alter prior forecasts. Volatility filtering addresses time variation, but cannot guarantee independence or stable regimes.

## 5.3 Tests and outcomes at 99%

{table(bt[["Model", "days", "breaches", "kupiec_p", "ind_p", "cc_p"]], {"kupiec_p": "{:.4g}", "ind_p": "{:.4g}", "cc_p": "{:.4g}"})}

Kupiec compares the observed breach frequency with 1 − α using a likelihood ratio with a chi-squared(1) reference. Christoffersen independence tests transition probabilities (chi-squared(1)); joint conditional coverage adds the two likelihood ratios (chi-squared(2)). At 99% over 250 days the Basel zones are green 0–4 breaches, yellow 5–9, red ≥10; these standard zones do not apply unchanged to other confidence levels. The extra ES Z2 check is indicative, with cutoffs derived for a different confidence level; it is not a formal calibrated approval test here.

**All models above reject independence and joint coverage at 5%.** GARCH improves independence p-values relative to the listed unfiltered baselines, but does not cure clustering. Filtered HS also rejects unconditional coverage; GARCH-EVT narrowly passes it. High coverage p-values do not validate allocation selection or prove model correctness. Monitor both historical/Student-t and EVT risk, plus conditional-model diagnostics; do not select a model solely because it passes one test. Limited expected tail counts weaken short-window tests.
""",
)

stress = stress_vectors(r)
new = pd.read_csv(OUT / "allocations.csv", index_col=0)["Risk-constrained alternative"]
remedy = w.copy()
remedy["XLK"] -= 0.065
remedy["XLE"] += 0.065
st = pd.DataFrame(
    {
        "Scenario": stress.index,
        "Retained allocation": stress @ w,
        "15% constrained alternative": stress @ new,
        "6.5-point XLK to XLE shift": stress @ remedy,
    }
)
write(
    "06_stress_tests.md",
    f"""
# Section 6: Historical and hypothetical stress tests

Historical replays use buy-and-hold asset returns over each complete crisis window: September 2008–March 2009, 19 February–23 March 2020, and calendar 2022. Daily performance KPIs instead assume daily rebalancing. Full-window loss is distinct from intrawindow drawdown, and all results are conditional on today's fixed weights being held in those past windows.

{table(st, {"Retained allocation": "{:.3%}", "15% constrained alternative": "{:.3%}", "6.5-point XLK to XLE shift": "{:.3%}"})}

## 6.1 Two distinct assumed scenarios

Inflation shock assumes SPY/EFA −25%, EEM −30%, AGG −15%, GLD −5%, XLE 0%, XLK −35%. The bond shock approximates duration 6 times a 250bp yield increase; it ignores convexity, credit spread shifts and nonlinear responses. XLE's zero is a team assumption, not a reliable hedge. Loss on the retained allocation is 17.215%, below the **proposed revised 18%** limit but above the former 15% proposal.

Equity crash with dollar spike assumes SPY −35%, EFA −40%, EEM −45%, AGG +5%, GLD −10%, XLE −40%, XLK −40%. Unlike inflation, bonds rally while energy crashes. Loss is 8.54%. No probabilities are assigned; these are scenarios, not approved-source observations or forecasts.

## 6.2 Why not adopt the 15%-constrained mix automatically?

The 60% AGG/15% GLD/10% XLE/15% XLK alternative meets the tested 15% scenario ceiling. However, its March 2020 loss is 11.38% versus 9.89%, and maximum drawdown is 19.58% versus 18.27%. It still depends on the assumed XLE inflation shock. Its annual return is 7.40% and Sharpe 0.764. We therefore request an explicit scenario-limit adjustment rather than hide a risk trade-off by changing the portfolio. If the committee declines the adjustment, reject the retained allocation under the 15% mandate.

Moving 6.5 percentage points from XLK to XLE reduces the assumed inflation loss to 14.94%, but worsens March 2020 and leaves the dollar-crash loss unchanged at 8.54%. This is not an adopted trade or universal hedge. Additional scenarios could overturn its apparent benefit.

The 2022 retained-allocation full-window loss is 12.64%, while its intrawindow drawdown reached about 17.2%. Full-sample drawdown is 18.27%. The revised 18% limit applies to tested scenario loss, not to either drawdown measure. Stress tests are finite examples and cannot bound future loss.
""",
)

write(
    "07_assumptions_limitations.md",
    """
# Section 7: Assumptions and limitations

**Weights were selected in sample.** The 22-year data both selects the allocation and measures its headline performance. Walk-forward validation of the baseline allocation rules does not support a Maximum Sharpe advantage on risk-adjusted performance. The revised 18% scenario policy was chosen after reviewing results and has no independent calibration or claimed loss probability.

| Area | Limitation | Implemented response / remaining work |
|---|---|---|
| Allocation | Means/covariances and scenario choices may not persist | Bounds and explicit historical VaR/ES/scenario constraints in the final solve; alternative-policy trade-offs disclosed |
| Rebalancing | Headline daily costless targets omit execution drag | Quarterly sensitivity only; no claim that quarterly execution is implemented |
| Data | Common sample omits earlier regimes; adjustments can be revised | Adjusted yfinance ETF prices, FRED DTB3; cleaning audit, ADF and outlier/stale-price checks; no unapproved model data |
| Tail models | Gaussian thin tails, t symmetry, small empirical tails | Historical, t, joint bootstrap, POT and GARCH comparisons; no universal best model claimed |
| EVT | Threshold choice, asymptotic fit and unstable tail shape | Sensitivity, second exploratory rule and IID bootstrap intervals; these do not remove serial dependence |
| Backtesting | All listed models still fail independence | Daily GARCH recursion improves some diagnostics, not acceptance; monitor coverage, clustering and Basel signals |
| Stress | Finite assumed scenarios, XLE zero-shock dependence | Second distinct scenario and remedy countercheck; no probability or future bound |
| Liquidity | Income, cash needs, trading costs and multi-week reserves not modeled | No calibrated reserve or multi-day risk claim; require further implementation before real deployment |

The final construction enforces historical daily VaR/ES limits and full-window/instant scenario loss constraints; other risk methods are monitoring estimates. ES may be enforced without being numerically active at the optimum. Scenario feasibility does not imply drawdown feasibility, robust optimisation or future compliance. Solver success plus independent checks is not proof of global optimality.

Risk forecasts use prior observations but a fixed in-sample-selected allocation. Dependence tests and small tail samples limit confidence. IID bootstrap intervals may be too narrow under clustering. Joint ETF resampling preserves empirical cross-asset dependence but not time dependence or unseen shocks. GARCH Gaussian QMLE is a variance model, not an assumption that residual tails are Gaussian; residual tails are empirical/GPD.

Committee action: ADJUST to 18% only if the explicit trade-off is acceptable. Review on a daily VaR/ES limit breach, scenario deterioration, persistent stock–bond correlation increase, or a 99%/250-day Basel red signal. Continue Student-t and EVT monitoring with conditional diagnostics. A mandatory 15% ceiling requires rejecting the retained allocation or selecting and validating a different policy. The application is research support, not a promise of investable performance.
""",
)

memo = f"""
# Section 8: Committee memo

**Decision: ADJUST the scenario-loss limit to 18%, retaining Maximum Sharpe.** This is a proposed mandate change; if the committee requires 15%, reject this allocation under that ceiling. The 18% limit measures complete historical windows or instantaneous hypothetical losses, not peak-to-trough drawdown.

| SPY | EFA | EEM | AGG | GLD | XLE | XLK |
|---|---|---|---|---|---|---|
| 9.55% | 0% | 0% | 58.85% | 15% | 1.60% | 15% |

## Rationale and construction

Historical CAGR is 7.42%, volatility 7.16%, Sharpe 0.786 and maximum drawdown 18.27%. Our 7.0%, 7.4% and 7.8% return hurdles are team assumptions; income, costs and taxes are not separately modeled. The final solve enforces asset bounds, full investment, 99% historical daily VaR ≤ 1.5%, ES ≤ 2.0%, and loss ≤ 18% in all five tested scenarios. Frozen rounded weights pass the same checks.

We revised the limit after reviewing results, not through independent calibration. The inflation scenario loses 17.215%, leaving only 0.785 percentage points below the proposed limit. A feasible 15%-constrained mix exists but increases maximum drawdown to 19.58% and March 2020 loss to 11.38%. We prefer the retained allocation's historical drawdown and request the policy adjustment openly.

## Measured downside

| Measure | Retained allocation | Proposed constraint |
|---|---|---|
| 99% historical daily VaR | {v:.3%}, USD {v * 1e7:,.0f} | 1.5%, USD 150,000 |
| 99% historical daily ES | {e:.3%}, USD {e * 1e7:,.0f} | 2.0%, USD 200,000 |
| Worst historical full-window loss | 12.64%, 2022 | 18%, USD 1,800,000 |
| Inflation scenario | 17.215%, USD 1,721,500 | 18%, USD 1,800,000 |
| Equity-crash/dollar-spike scenario | 8.54%, USD 854,000 | 18%, USD 1,800,000 |

The 18.27% maximum drawdown exceeds 18%; no 18% drawdown cap is claimed. Technology contributes about 36.5% of historical ES with 15% of capital. Bonds comprise 58.85%, leaving material rate and correlation risk.

## Validation and governance

Weights were selected in sample. Walk-forward Maximum Sharpe earns 7.10% with Sharpe 0.807, versus Minimum variance 6.82% and 0.839: the risk-adjusted advantage does not hold out of sample. GARCH improves some clustering diagnostics, but all compared models still fail independence. EVT sensitivity and bootstrap intervals expose tail uncertainty. No model is a guarantee.

Headline returns assume daily rebalancing; quarterly sensitivity is 7.3% return and −18.7% drawdown. Monitor Student-t/EVT daily risk, conditional-model diagnostics, concentration and both scenarios. Review on a limit breach, persistent adverse correlation or a 99%/250-day Basel red signal. Reject the retained policy if the committee declines the 18% adjustment.
"""
write("08_committee_memo.md", memo)

tear = f"""
# Serendib University Endowment Fund — Portfolio Tear Sheet

**USD 10m | Decision: ADJUST scenario limit to 18% | Sample: 19 Nov 2004–27 Oct 2026**

## Allocation and construction

{table(pd.DataFrame({"ETF": w.index, "Weight": w.values, "Capital USD": w.values * 1e7}), {"Weight": "{:.2%}", "Capital USD": "{:,.0f}"})}

Full investment, original ETF bounds, 99% historical daily VaR ≤ 1.5%, ES ≤ 2.0%, and all five scenario losses ≤ 18% are enforced in construction. The 18% proposal was selected after reviewing results; it is not independently calibrated. If 15% is mandatory, reject this retained allocation under that mandate.

## Performance and validation

Historical CAGR **7.42%**, volatility **7.16%**, Sharpe **0.786**, maximum drawdown **18.27%**. Return hurdles 7.0%/7.4%/7.8% are team assumptions, not forecasts. Weights were selected in sample. Walk-forward Maximum Sharpe: 7.10% return, Sharpe 0.807; Minimum variance: 6.82%, 0.839. Maximum Sharpe has no demonstrated walk-forward Sharpe advantage. Policy benchmark: 40% SPY/60% AGG; information ratio 0.197.

## One-day risk on USD 10m

{table(risk[risk.Confidence == 0.99][["Model", "VaR", "ES"]], {"VaR": "{:.3%}", "ES": "{:.3%}"})}

Historical 99% VaR USD {v * 1e7:,.0f}; ES USD {e * 1e7:,.0f}. Technology is 15% of money but about 36.5% of historical ES. EVT 99% bootstrap 95% intervals: VaR 1.123–1.299%, ES 1.488–1.966% (200 IID replicates; clustering may widen uncertainty).

## Stress and decision

{table(pd.DataFrame({"Scenario": stress.index, "Loss": -(stress @ w).values, "Loss USD": -(stress @ w).values * 1e7}), {"Loss": "{:.3%}", "Loss USD": "{:,.0f}"})}

Inflation loss is 17.215%, below revised 18% but above former 15%. The limit is scenario loss, **not drawdown**. A 15%-constrained alternative exists but worsens drawdown to 19.58%. Both hypothetical scenarios are assumptions, including XLE 0% in inflation. Energy rotation is not a universal hedge.

## Monitoring and limitations

All compared models, including GARCH, still fail independence. GARCH filtered HS also fails coverage. Daily rebalancing/costless execution underlies headline results; quarterly sensitivity: 7.3% return, −18.7% drawdown. Liquidity reserves and multi-day risk are not implemented. Monitor Student-t, EVT, conditional diagnostics and scenarios; review on limit breaches, adverse correlations or a 99%/250-day Basel red signal. Scenario feasibility does not guarantee future compliance.
"""
(ROOT / "docs/tearsheet.md").write_text(tear.strip() + "\n")
print("Replacement sources generated; final hard constraints verified")
