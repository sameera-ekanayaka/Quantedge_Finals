# Serendib University Endowment Fund — Portfolio Tear Sheet

**USD 10m | Decision: ADJUST scenario limit to 18% | Sample: 19 Nov 2004–27 Oct 2026**

## Allocation and construction

| ETF   | Weight   |   Capital USD |
|:------|:---------|--------------:|
| SPY   | 9.55%    |       955,000 |
| EFA   | 0.00%    |             0 |
| EEM   | 0.00%    |             0 |
| AGG   | 58.85%   |     5,885,000 |
| GLD   | 15.00%   |     1,500,000 |
| XLE   | 1.60%    |       160,000 |
| XLK   | 15.00%   |     1,500,000 |

Full investment, original ETF bounds, 99% historical daily VaR ≤ 1.5%, ES ≤ 2.0%, and all five scenario losses ≤ 18% are enforced in construction. The 18% proposal was selected after reviewing results; it is not independently calibrated. If 15% is mandatory, reject this retained allocation under that mandate.

## Performance and validation

Historical CAGR **7.42%**, volatility **7.16%**, Sharpe **0.786**, maximum drawdown **18.27%**. Return hurdles 7.0%/7.4%/7.8% are team assumptions, not forecasts. Weights were selected in sample. Walk-forward Maximum Sharpe: 7.10% return, Sharpe 0.807; Minimum variance: 6.82%, 0.839. Maximum Sharpe has no demonstrated walk-forward Sharpe advantage. Policy benchmark: 40% SPY/60% AGG; information ratio 0.197.

## One-day risk on USD 10m

| Model                  | VaR    | ES     |
|:-----------------------|:-------|:-------|
| Historical simulation  | 1.163% | 1.734% |
| Parametric (normal)    | 1.020% | 1.173% |
| Parametric (Student t) | 1.157% | 1.726% |
| Monte Carlo            | 1.152% | 1.674% |
| Joint ETF bootstrap    | 1.169% | 1.735% |
| EVT / GPD              | 1.220% | 1.726% |

Historical 99% VaR USD 116,306; ES USD 173,429. Technology is 15% of money but about 36.5% of historical ES. EVT 99% bootstrap 95% intervals: VaR 1.123–1.299%, ES 1.488–1.966% (200 IID replicates; clustering may widen uncertainty).

## Stress and decision

| Scenario                                   | Loss    |   Loss USD |
|:-------------------------------------------|:--------|-----------:|
| 2008 financial crisis                      | 5.170%  |    517,024 |
| March 2020 Covid crash                     | 9.892%  |    989,191 |
| 2022 rate hikes                            | 12.645% |  1,264,453 |
| Inflation shock                            | 17.215% |  1,721,500 |
| Equity crash and dollar spike (assumption) | 8.540%  |    854,000 |

Inflation loss is 17.215%, below revised 18% but above former 15%. The limit is scenario loss, **not drawdown**. A 15%-constrained alternative exists but worsens drawdown to 19.58%. Both hypothetical scenarios are assumptions, including XLE 0% in inflation. Energy rotation is not a universal hedge.

## Monitoring and limitations

All compared models, including GARCH, still fail independence. GARCH filtered HS also fails coverage. Daily rebalancing/costless execution underlies headline results; quarterly sensitivity: 7.3% return, −18.7% drawdown. Liquidity reserves and multi-day risk are not implemented. Monitor Student-t, EVT, conditional diagnostics and scenarios; review on limit breaches, adverse correlations or a 99%/250-day Basel red signal. Scenario feasibility does not guarantee future compliance.
