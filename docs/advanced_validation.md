# Post-report audit response: additional models and constrained alternative

**Historical research record.** The replacement submission now integrates these analyses and explicitly proposes an 18% scenario-loss limit. Read `docs/report/` and the current PDFs in `submission/` for the final decision. References below to the submitted/unchanged PDFs describe the earlier submission, now archived in `submission/previous_submission/`.

Prepared 31 October 2026 after the submitted PDF. This supplements the report; it does not replace or retroactively change the submitted recommendation, portfolio weights, documents or model results. The app's **Supplementary research** page presents the additions separately. Original models remain available for reproduction.

Reproduce all archived outputs with `python scripts/build_advanced_validation.py`. Clean market data and original ETF bounds are unchanged. The submitted PDF checksums remain in `submission/SHA256SUMS`.

## Decision: ADJUST

If a hard 15% scenario ceiling is required, adjust the allocation rather than approve the submitted allocation. The original allocation still loses 17.215% in the assumed inflation shock. The new numerical alternative is AGG 60%, GLD 15%, XLE 10%, XLK 15%, with effectively zero in other assets.

The SLSQP optimisation maximises estimated in-sample Sharpe with full investment, original asset bounds, 99% historical one-day VaR ≤ 1.5%, historical ES ≤ 2.0%, and loss ≤ 15% in each of three historical full-window buy-and-hold replays and both hypothetical scenarios. A linear programme supplies a scenario-feasible starting point; the returned allocation is checked independently against the risk limits. This is a numerical local solve, not proof of a global optimum. Infeasibility or a failed solve raises an error, without relaxing limits silently.

The alternative inflation loss is 15.0%, but March 2020 worsens from 9.89% to 11.38%. Annual return is 7.40%, Sharpe 0.764 and full-sample maximum drawdown 19.58%. The latter is worse than the submitted 18.27%; **the optimisation does not impose a 15% path-drawdown ceiling**. Constraints on finite scenarios are not guarantees about future losses. The portfolio depends on XLE's assumed 0% inflation shock; uncertainty in that assumption remains. This is a feasible in-sample alternative, not an independently validated replacement recommendation.

All four original daily methods, EVT and joint ETF bootstrap are recomputed at 95% and 99% for the alternative, together with historical 99% risk attribution, five original 99% backtests, stress results and KPIs. Historical risk constraints do not guarantee that every other fitted model stays below the same limits. Full-precision files are under `submission/advanced/`.

## Conditional risk models

GARCH(1,1) uses a constant mean and Gaussian quasi-maximum-likelihood variance fit on 500 preceding daily returns, expressed in percentage units. Refit every 21 observations. Update conditional variance daily with the latest observed return; fit parameters and standardised residual distributions stay fixed between refits. Convergence failures raise errors. Models are fitted before the forecast observation and do not use the return they predict.

Filtered historical simulation takes empirical residual-tail VaR/ES. GARCH-EVT fits a GPD to losses above the residual 90th percentile. Both forecasts transform residual-tail estimates using the conditional mean and next-day volatility. Prefix-invariance tests verify that changing future observations leaves prior forecasts unchanged.

At 99%, evaluated on identical dates from January 2008 through October 2026 (4,735 forecasts):

| Model | Breaches | Kupiec p | Independence p | Joint coverage p |
|---|---:|---:|---:|---:|
| Historical | 61 | 0.0563 | 0.00000994 | 0.00000932 |
| Unfiltered EVT | 51 | 0.5985 | 0.0000000374 | 0.000000231 |
| Joint ETF bootstrap | 61 | 0.0563 | 0.0000000474 | 0.0000000541 |
| GARCH filtered HS | 63 | 0.0296 | 0.000166 | 0.0000781 |
| GARCH EVT | 61 | 0.0563 | 0.000113 | 0.0000941 |

The independence p-values improve for conditional models relative to these baselines, but **all still reject independence and joint coverage at 5%**. GARCH filtered HS also rejects unconditional coverage. No clustering failure is declared solved. Allocation selection remains in sample; dynamic risk forecasts do not remove that selection bias. Forecast CSVs include every prediction and realised outcome. The app filters the archived 99% results by date and explicitly labels their confidence instead of pretending they follow the confidence slider.

## Joint ETF Monte Carlo

Sample complete seven-ETF daily simple-return vectors with replacement and combine each vector with the selected weights. This preserves contemporaneous empirical dependence and differs from fitting one parametric t distribution to aggregate returns. Seed 42, 100,000 draws for static risk, 20,000 per monthly rolling refit. It retains the empirical support and cannot invent new crash regimes. It ignores serial dependence and may closely match historical simulation by construction. It is supplementary; the original Student-t Monte Carlo remains labeled as an original model.

## Alternative threshold rule and bootstrap intervals

For quantiles 80%, 85%, 90%, 92.5%, 95% and 97.5%, fit each GPD with at least 100 exceedances. Choose the smallest in-sample KS CDF discrepancy. On the submitted portfolio it selects the 80th percentile (threshold 0.240%): 99% VaR 1.239%, ES 1.710%. This is an exploratory diagnostic selection criterion. Its fitted KS score is not a valid unadjusted hypothesis-test p-value or evidence of optimality. The headline rule remains 90%.

For the original 90% threshold rule, run 200 seeded IID bootstrap replicates, reselecting the threshold and refitting the GPD in each replicate. The 95% percentile intervals at 99% confidence are approximately VaR [1.123%, 1.299%] and ES [1.488%, 1.966%], with all 200 replicates valid. Nonfinite estimates and fitting failures are counted; too many failures stop interval reporting. IID resampling omits serial dependence, may understate uncertainty, and is not a guarantee of future coverage. At 90% confidence the app uses an 89th-percentile bootstrap threshold to avoid extrapolating below the fitted tail when resampled observations tie.

## Benchmark and additional stress scenario

A daily-rebalanced 40% SPY / 60% AGG policy benchmark supplements SPY. The submitted portfolio's information ratio is approximately 0.197 versus policy, compared with -0.332 versus SPY. Benchmark choice affects interpretation; neither benchmark is claimed to be uniquely correct. The original SPY metrics are preserved.

The second hypothetical scenario assumes equity crash plus dollar spike: SPY -35%, EFA -40%, EEM -45%, AGG +5%, GLD -10%, XLE -40%, XLK -40%. It differs from inflation because bonds rally while energy crashes. These are disclosed team assumptions, not data or forecasts. Loss is 8.54% for the submitted allocation and 8.50% for the constrained alternative. The previously suggested 6.5-point XLK-to-XLE shift improves the inflation shock to 14.94% but leaves the new scenario loss at 8.54%: it is not a universal hedge. No probability is assigned to either scenario.

## Document corrections and packaging

The original PDFs remain exact archived copies. The earlier supplementary note corrects the report's unsupported reserve and binding-constraint claims, the in-sample selection interpretation and the retrospective limit justification. The submitted memo still requests conditional acceptance; this supplement's explicit **ADJUST** decision applies if a hard scenario ceiling is required. It does not alter the submitted document.

New tables retain full precision in CSVs, and presentation rounds risk percentages to three decimal places, weights/stress percentages to two. Original rounded PDF dollar figures are approximations, not distinct calculations; they are not rewritten here. The live deployment still requires an allowed-browser check following merge, because the environment cannot access the Streamlit host.

## Verification

156 tests passed after these additions. Ruff and Black formatting checks passed. Regression tests cover hard risk-limit feasibility and infeasibility, preservation of a perfectly hedged joint-ETF observation, conditional forecast prefix invariance, reproducible threshold selection/bootstrap, and rendering the new page at all three confidence levels. Local Chromium loaded the new page without displayed exceptions. Original PDF hashes were verified unchanged. Live Streamlit access remains blocked by the environment; production checks are still required after merge.
