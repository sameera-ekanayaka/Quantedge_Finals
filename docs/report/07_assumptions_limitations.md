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
