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
| 99% historical daily VaR | 1.163%, USD 116,306 | 1.5%, USD 150,000 |
| 99% historical daily ES | 1.734%, USD 173,429 | 2.0%, USD 200,000 |
| Worst historical full-window loss | 12.64%, 2022 | 18%, USD 1,800,000 |
| Inflation scenario | 17.215%, USD 1,721,500 | 18%, USD 1,800,000 |
| Equity-crash/dollar-spike scenario | 8.54%, USD 854,000 | 18%, USD 1,800,000 |

The 18.27% maximum drawdown exceeds 18%; no 18% drawdown cap is claimed. Technology contributes about 36.5% of historical ES with 15% of capital. Bonds comprise 58.85%, leaving material rate and correlation risk.

## Validation and governance

Weights were selected in sample. Walk-forward Maximum Sharpe earns 7.10% with Sharpe 0.807, versus Minimum variance 6.82% and 0.839: the risk-adjusted advantage does not hold out of sample. GARCH improves some clustering diagnostics, but all compared models still fail independence. EVT sensitivity and bootstrap intervals expose tail uncertainty. No model is a guarantee.

Headline returns assume daily rebalancing; quarterly sensitivity is 7.3% return and −18.7% drawdown. Monitor Student-t/EVT daily risk, conditional-model diagnostics, concentration and both scenarios. Review on a limit breach, persistent adverse correlation or a 99%/250-day Basel red signal. Reject the retained policy if the committee declines the 18% adjustment.
