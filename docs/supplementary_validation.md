# Supplementary validation — 31 October 2026

These additions were prepared after the submitted PDF. They supplement that fixed document; they do not replace its portfolio, change its limits or revise its headline results. Exact copies of the PDFs supplied for submission are archived in `submission/`.

## Clarifications to the submitted report

- Portfolio optimisation enforces weight bounds and full investment. Daily VaR/ES and stress limits are checked afterward, not enforced as optimisation constraints. Section 7's description of ES as a binding constraint overstates the implementation.
- The 15% crisis-window limit is a team-proposed monitoring trigger, revised after examining candidate results. The claim that it was not chosen to fit results is not supported by independent calibration and should not be relied on.
- The submitted portfolio loses 17.2% under the assumed inflation scenario. It therefore fails a hard 15% scenario ceiling. Conditional acceptance requires an explicit committee exception; neither disclosure nor this supplement cures the breach. Full-sample maximum drawdown is a separate measure at 18.3%.
- No multi-week liquidity reserve is calibrated or implemented. Those Section 7 statements describe future work rather than completed calculations. Headline results assume daily rebalancing; quarterly rebalancing is only a sensitivity.
- Risk-model forecasts use prior observations conditional on fixed weights. This does not make the full-sample portfolio selection out of sample. All model breach-independence failures remain unresolved.

## Annual walk-forward allocation validation

Run `python scripts/build_supplementary.py` from the repository root. Outputs include the training cutoff and asset weights for every annual decision in `submission/supplementary/annual_weights.csv`.

Each January from 2010, estimate means, covariance and the risk-free rate using only preceding observations (minimum 756 days). Re-optimise Maximum Sharpe and Minimum variance with the original asset bounds, then apply each allocation with daily target rebalancing for the evaluation year. Evaluate both on identical dates, 4 January 2010 through 27 October 2026. Costs, slippage and taxes are excluded. Risk constraints are not introduced in this supplementary solve.

| Strategy | Annual return | Volatility | Sharpe | Maximum drawdown |
|---|---:|---:|---:|---:|
| Walk-forward Maximum Sharpe | 7.10% | 6.94% | 0.807 | -18.18% |
| Walk-forward Minimum variance | 6.82% | 6.31% | 0.839 | -16.94% |
| Frozen submitted weights, same dates | 7.50% | 6.84% | 0.873 | -17.31% |

The frozen comparator retains full-sample selection bias and is not a genuine out-of-sample allocation strategy. Maximum Sharpe retains a return advantage but does not beat Minimum variance on walk-forward Sharpe. The submitted recommendation should be understood as a return/risk preference, not demonstrated out-of-sample superiority. This is one historical evaluation, not independent replication or proof of future performance.

## EVT threshold sensitivity

For the submitted weights, refit the GPD at loss percentiles 80, 85, 90, 92.5, 95 and 97.5. At 99% confidence, VaR ranges from approximately 1.18% to 1.24%, ES from 1.70% to 1.75%, and fitted shape from 0.13 to 0.34. Full-precision results are in `submission/supplementary/evt_sensitivity.csv`.

These are sensitivity results, not bootstrap confidence intervals. The headline rule remains the 90th percentile. The live table follows the selected confidence level and marks thresholds outside its fitted tail as unavailable rather than extrapolating into the body. No second automatic threshold rule is claimed.

## Scope and remaining limitations

The app now includes the risk comparison chart, removes owner captions, and reports expected EVT estimation failures rather than swallowing every exception. A clean-run command and archived PDFs improve packaging. No GARCH model, multivariate replacement Monte Carlo, new policy benchmark, second hypothetical scenario or re-optimised recommendation is claimed. The submitted PDFs remain unchanged, including their rounding conventions.

Production verification must be performed from an allowed browser: this environment's network policy blocks the deployed Streamlit host. Visit every page and exercise confidence, method and date controls after deployment. A local test pass cannot establish the production revision.
