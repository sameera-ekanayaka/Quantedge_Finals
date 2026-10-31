# Section 8: Committee memo

**Decision requested:** Conditional acceptance of Maximum Sharpe for the USD 10m endowment, with a 15% crisis-window monitoring limit. Committee approval of the disclosed inflation-stress exception is required; this portfolio does not satisfy a hard 15% ceiling across all scenarios.

| SPY | EFA | EEM | AGG | GLD | XLE | XLK |
|---|---|---|---|---|---|---|
| 9.55% | 0% | 0% | 58.85% | 15% | 1.60% | 15% |

## Rationale and trade-off

The portfolio historically returned 7.4% annually with 7.2% volatility, Sharpe 0.79 and maximum drawdown -18.3%. Minimum variance returned 6.5% with -17.8% maximum drawdown. The extra return supports our assumed 7.0% objective (4.5% spending plus 2.5% inflation). It approximately meets the 7.4% spending sensitivity and misses the 7.8% inflation sensitivity. These are team assumptions, not forecasts. Income payments and trading costs are not separately modeled.

## Measured downside and proposed limits

| Measure | Portfolio | Proposed limit |
|---|---|---|
| One-day 99% Student t VaR | 1.16%, USD 116k | 1.5%, USD 150k |
| One-day 99% Student t ES | 1.73%, USD 173k | 2.0%, USD 200k |
| Worst historical crisis-window loss | 12.6%, 2022 | 15%, USD 1.5m |
| Hypothetical inflation loss | 17.2%, USD 1.72m | Exceeds 15% |

Historical crisis losses were 5.2% in 2008 and 9.9% in March 2020. The 2022 peak-to-trough loss was 17.2%; the 15% limit measures the full crisis window, not drawdown. Almost 59% in bonds creates rate exposure, while technology contributes about 37% of historical ES despite a 15% capital weight.

We prefer Maximum Sharpe for its return advantage with similar historical crisis losses to Minimum variance. Neither meets the hypothetical 15% limit. If that ceiling is mandatory, do not approve these weights: require a revised allocation and rerun every risk test. Disclosure alone does not cure a breach.

## Monitoring and conditions

Monitor Student t and EVT daily risk, stock-bond correlation, technology concentration and inflation stress. A shift of about 6.5 percentage points from XLK to XLE reduces the specified inflation shock below 15%, but depends on the assumed XLE shock and requires fresh return/risk validation before adoption. Use Minimum variance if lower historical drawdown takes priority over the return objective.

Weights were selected in sample. Risk forecasts use prior observations conditional on those fixed weights. Student t and EVT pass 99% coverage, but all models fail breach independence: losses cluster. Daily rebalancing underlies headline numbers; quarterly rebalancing gives 7.3% return and -18.7% drawdown. Limits are review triggers, not guarantees. Review the allocation on a limit breach, persistent positive stock-bond correlation or a 99%/250-day Basel red signal.
