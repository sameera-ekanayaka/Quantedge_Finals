# Section 6: Stress tests

**Owner:** Tharindu Dhanushka
**Code:** `src/stress.py`, tested in `tests/test_stress.py`
**App page:** Stress tests
**Reproduce:** `python -m src.stress`

Numbers are for the four candidate portfolios on data to 27 Oct 2026. They
will be rerun on the frozen weights.

## 6.1 Why stress tests

VaR and ES describe a normal bad day. Section 5 showed that every model lets
breaches pile up when a crisis starts. Stress tests answer the committee's
question directly: if 2008 happened again tomorrow, how much of the USD 10m
would we lose?

## 6.2 Method

- **Historical replays** use real daily returns for three periods set in
  `src/config.py`: the 2008 financial crisis (1 Sep 2008 to 31 Mar 2009),
  the March 2020 Covid crash (19 Feb to 23 Mar 2020) and the 2022 rate hikes
  (calendar 2022).
- **Buy and hold.** We invest at the close before the first day and hold.
  Weights drift with prices and nothing is rebalanced mid-crisis, which is how
  a quarterly-rebalanced fund would actually experience it.
- For each replay we report the total return, the USD P&L, the deepest fall
  inside the period (max drawdown), the worst single day, and each ETF's
  contribution. Contributions add up exactly to the total.
- **Our own scenario (an assumption, not data).** An inflation surprise pushes
  yields up about 250bp, so stocks and bonds fall together and nothing hedges.
  This is the failure we found in round 1, when the stock-bond hedge broke.

| ETF | Shock | Reason |
|---|---|---|
| SPY | -25% | Higher real rates cut equity valuations, about 1.4 times the 2022 fall |
| EFA | -25% | Developed markets move with the US, as in 2022 |
| EEM | -30% | A strong dollar and capital outflows hit emerging markets hardest |
| AGG | -15% | 250bp rise in yields times a duration of about 6 years |
| GLD | -5% | Rising real yields weigh on gold, so it does not hedge |
| XLE | 0% | Energy rose 64% in 2022; we assume no gain, so it cannot rescue us |
| XLK | -35% | Long-duration tech falls most when rates rise, as in 2022 |

The shocks can be edited on the app page.

- **Reverse stress test.** How many times worse would our scenario have to be
  before the portfolio lost the crisis loss limit? We propose a limit of 10%
  of the fund (USD 1m) in one crisis; the final number is set in the memo.

## 6.3 Results: risk parity

| Scenario | Type | Return | P&L (USD) | Max drawdown | Worst day | SPY |
|---|---|---|---|---|---|---|
| 2008 financial crisis | Replay | -8.7% | -866,810 | -17.7% | -5.76% (10 Oct 2008) | -36.9% |
| March 2020 Covid crash | Replay | -12.7% | -1,266,817 | -15.7% | -5.73% (12 Mar 2020) | -33.4% |
| 2022 rate hikes | Replay | -8.9% | -893,372 | -15.2% | -2.63% (13 Jun 2022) | -18.2% |
| Inflation shock | Assumption | -16.4% | -1,643,756 | | | -25.0% |

## 6.4 Results: every candidate

| Scenario | Equal weight | Minimum variance | Maximum Sharpe | Risk parity |
|---|---|---|---|---|
| 2008 financial crisis | -19.0% | -5.6% | -5.2% | -8.7% |
| March 2020 Covid crash | -21.4% | -9.6% | -9.9% | -12.7% |
| 2022 rate hikes | -7.2% | -12.5% | -12.6% | -8.9% |
| Inflation shock | -18.8% | -16.0% | -17.2% | -16.4% |
| Reverse stress multiple at 10% | 0.53 | 0.62 | 0.58 | 0.61 |

## 6.5 What this means

1. **Diversification works in equity crashes.** In 2008 risk parity lost 8.7%
   while SPY lost 36.9%. AGG (+1.9 points) and GLD (+1.4 points) offset part of
   the equity losses.
2. **It does not work when rates rise.** In 2022 AGG fell 13% and was the
   largest single drag on risk parity (-7.1 points of the -8.9%). The two
   bond-heavy candidates, minimum variance and maximum Sharpe, lost the most
   in 2022 (-12.5% and -12.6%), the reverse of their ranking in 2008 and 2020.
   XLE, up 64%, was the only real hedge.
3. **Our inflation scenario breaks a 10% limit for every candidate.** Risk
   parity would lose 16.4%, and a scenario only 0.61 times as severe would
   already hit the limit. No mix of these seven ETFs under the current
   mandate keeps an inflation shock of this size under 10%.
4. **Short crises are not small crises.** March 2020 lasted 24 trading days
   but cost risk parity more (-12.7%) than the six months of 2008 in our
   window (-8.7%). In 2008 AGG and GLD added to returns; in March 2020 both
   fell slightly in the dash for cash (-0.8 and -0.4 points), so nothing
   offset the equity losses.

**For the decision layer.** Either the crisis loss limit is set nearer 15%
than 10%, or the mandate gives more room to assets that hold up when rates
rise (energy, or a smaller bond floor). That trade-off goes to the committee
memo; it is a choice, not a modelling result.

## 6.6 Limitations

- **The 2008 window starts on 1 Sep 2008.** It misses the fall from the
  October 2007 peak, so the 2008 replay understates the full bear market.
- **History does not repeat exactly.** Correlations in the next crisis can be
  different. That is why we add a scenario of our own.
- **The hypothetical shocks are judgement**, set out in the table above. They
  are instant, so there is no path or drawdown, and the reverse stress test
  assumes every shock scales in proportion.
- **No transaction costs or liquidity effects.** ETF spreads widened sharply in
  March 2020, which would make selling in a crisis costlier than shown.
