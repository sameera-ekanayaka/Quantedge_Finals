# Section 2: Mandate, construction and decision

**Decision: ADJUST the scenario-loss limit to 18%, retaining the Maximum Sharpe allocation.** This is a proposed mandate change requiring committee agreement, not acceptance of the original 15% ceiling. Weights were selected and evaluated on the same 2004–2026 sample; historical performance is not a forecast.

## 2.1 Explicit construction constraints

The USD 10m long-only fund has no leverage. Bounds are SPY 0–40%, EFA 0–30%, EEM 0–10%, AGG 30–60%, GLD 0–15%, XLE 0–10%, XLK 0–15%. Full investment is required. The final solve additionally enforces 99% historical one-day VaR ≤ 1.5% and ES ≤ 2.0%, and loss ≤ 18% in all three historical crisis windows and both hypothetical scenarios. `construct_final_portfolio` runs this SLSQP solve from a scenario-feasible linear-programming start; infeasibility or a failed post-solve check raises an error. It is a numerical local solve, not a proof of global optimality. Benchmarks are constructed separately and need not satisfy every final risk constraint.

The constrained solve produces SPY 9.5494%, AGG 58.8471%, GLD 15%, XLE 1.6034%, XLK 15%. We freeze rounded targets of 9.55%, 58.85%, 15%, 1.60%, 15% respectively, with EFA/EEM zero, and verify that rounding still satisfies the risk limits. The full-precision solve and targets are archived in `submission/advanced/final_construction.csv`.

**Why 18%:** an initial 10% idea and then a 15% proposed scenario limit were reviewed after observing candidate results. Neither was independently calibrated. We now openly propose 18% because the retained allocation loses 17.215% in our inflation scenario, leaving only 0.785 percentage points of modeled headroom. This is a retrospective policy choice, not statistical evidence that 18% is safe. If the committee requires 15%, do not approve this allocation under that mandate. A feasible 15%-constrained alternative exists, but raises March 2020 loss to 11.38% and full-sample drawdown to 19.58%; see Section 6. We prefer the original allocation's historical drawdown and request the limit adjustment explicitly.

The scenario limit measures full-window or instantaneous scenario loss, **not peak-to-trough drawdown**. The retained allocation's maximum drawdown is 18.27%, greater than 18%; no 18% drawdown ceiling is imposed or claimed. Historical 99% VaR is 1.163%, ES 1.734%. These constraints are sample-dependent and cannot guarantee future compliance.

## 2.2 Candidates and KPIs

Mean/covariance Markowitz construction uses daily simple returns. Maximum Sharpe maximises excess arithmetic mean divided by volatility; Minimum variance minimises variance; risk parity equalises variance contributions subject to bounds. Minimum ES uses a historical CVaR linear programme. The bounded equal-weight candidate is closest to 1/7 subject to bounds; it is not an unconstrained benchmark.

| Candidate        | Annual return   | Annual volatility   |   Sharpe | Max drawdown   |
|:-----------------|:----------------|:--------------------|---------:|:---------------|
| Equal weight     | 8.98%           | 12.75%              |    0.598 | -35.36%        |
| Minimum variance | 6.55%           | 6.69%               |    0.715 | -17.82%        |
| Maximum Sharpe   | 7.42%           | 7.16%               |    0.786 | -18.27%        |
| Risk parity      | 7.02%           | 8.13%               |    0.656 | -23.01%        |
| Minimum ES       | 6.55%           | 6.69%               |    0.715 | -17.82%        |

Return is CAGR; volatility uses 252 trading days. Sharpe, Sortino, Treynor, CAPM beta/Jensen alpha, information ratio, drawdown and Calmar are implemented in `src/kpis.py`. SPY is retained for market comparison; a 40% SPY/60% AGG daily-rebalanced policy benchmark better reflects the bond-heavy mandate. The final allocation's information ratio is 0.197 against policy versus −0.332 against SPY. Benchmark choice changes interpretation, not the underlying return.

Our 7.0% nominal objective (4.5% spending plus 2.5% inflation), 7.4% and 7.8% sensitivities are team assumptions. Historical 7.42% CAGR clears 7.0%, approximately meets 7.4% and misses 7.8%. Income distributions, taxes and costs are not separately modeled. Daily rebalancing underlies headline returns; quarterly sensitivity is 7.3% return and −18.7% drawdown.

## 2.3 Full KPI set for retained allocation

| KPI               |    Value |
|:------------------|---------:|
| Annual return     |  0.07424 |
| Annual volatility |  0.07162 |
| Sharpe            |  0.78647 |
| Sortino           |  1.12872 |
| Treynor           |  0.19634 |
| Beta              |  0.28689 |
| Jensen alpha      |  0.02663 |
| Information ratio | -0.33187 |
| Max drawdown      | -0.1827  |
| Calmar            |  0.40636 |

Values above are decimals (returns, volatility, alpha and drawdown), or unitless ratios. CAPM beta is covariance with SPY divided by SPY variance; Jensen alpha is annual portfolio excess mean minus beta times annual SPY excess mean. Sharpe uses total volatility, Sortino uses downside deviation, Treynor scales excess return by beta, information ratio uses benchmark-relative tracking error, and Calmar divides CAGR by absolute maximum drawdown. All metrics use consistent daily simple-return inputs and annualisation conventions in the code.

## 2.4 Walk-forward allocation validation

Each January from 2010, re-estimate Maximum Sharpe and Minimum variance from preceding observations only (minimum 756 days). Apply each year's allocation with daily target rebalancing. Asset bounds are enforced; this validates the baseline selection rules, not a walk-forward strategy with the retrospectively revised scenario limit. Costs are excluded. Evaluation dates are identical, 4 January 2010 to 27 October 2026.

| Strategy                                       | Annual return   | Volatility   |   Sharpe | Max drawdown   |
|:-----------------------------------------------|:----------------|:-------------|---------:|:---------------|
| Walk-forward Maximum Sharpe                    | 7.10%           | 6.94%        |    0.807 | -18.18%        |
| Walk-forward Minimum variance                  | 6.82%           | 6.31%        |    0.839 | -16.94%        |
| Frozen submitted weights (in-sample selection) | 7.50%           | 6.84%        |    0.873 | -17.31%        |

The frozen comparator retains full-sample selection bias. Maximum Sharpe preserves a return advantage but loses to Minimum variance on walk-forward Sharpe. We therefore justify the selection as a return/risk preference, not demonstrated out-of-sample superiority. The allocation and revised policy still require committee judgment. Annual training cutoffs and weights are archived for reproduction.
