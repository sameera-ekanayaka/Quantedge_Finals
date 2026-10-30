# Section 6: Stress tests

**Owner:** Tharindu Dhanushka
**Code:** `src/stress.py`, tested in `tests/test_stress.py`
**App page:** Stress tests
**Reproduce:** `python -m src.stress`

Numbers are for the final portfolio (`final_weights()`, the Maximum Sharpe mix
in Section 8) on data to 27 Oct 2026, with the other candidates for
comparison.

## 6.1 Why stress tests

VaR and ES describe a normal bad day. Section 5 shows that every model lets
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

- **Crisis loss limit: 15% of the fund (USD 1.5m)**, as set in the committee
  memo (Section 8). The reverse stress test asks how many times as severe our
  scenario would have to be to reach it.

## 6.3 Results: final portfolio

| Scenario | Type | Return | P&L (USD) | Max drawdown | Worst day | SPY |
|---|---|---|---|---|---|---|
| 2008 financial crisis | Replay | -5.2% | -517,024 | -14.6% | -5.86% (10 Oct 2008) | -36.9% |
| March 2020 Covid crash | Replay | -9.9% | -989,191 | -12.8% | -5.28% (12 Mar 2020) | -33.4% |
| 2022 rate hikes | Replay | -12.6% | -1,264,453 | -17.2% | -2.45% (13 Jun 2022) | -18.2% |
| Inflation shock | Assumption | -17.2% | -1,721,500 | | | -25.0% |

**Contribution by ETF, in points of return**

| Scenario | SPY | AGG | GLD | XLE | XLK |
|---|---|---|---|---|---|
| 2008 financial crisis | -3.5 | +2.0 | +1.6 | -0.7 | -4.6 |
| March 2020 Covid crash | -3.2 | -0.8 | -0.5 | -0.9 | -4.6 |
| 2022 rate hikes | -1.7 | -7.7 | -0.1 | +1.0 | -4.2 |
| Inflation shock | -2.4 | -8.8 | -0.8 | 0.0 | -5.3 |

EFA and EEM have zero weight, so they contribute nothing.

## 6.4 Results: every candidate

| Scenario | Equal weight | Minimum variance | Maximum Sharpe (final) | Risk parity |
|---|---|---|---|---|
| 2008 financial crisis | -19.0% | -5.6% | -5.2% | -8.7% |
| March 2020 Covid crash | -21.4% | -9.6% | -9.9% | -12.7% |
| 2022 rate hikes | -7.2% | -12.5% | -12.6% | -8.9% |
| Inflation shock | -18.8% | -16.0% | -17.2% | -16.4% |
| Reverse stress multiple at 15% | 0.80 | 0.94 | 0.87 | 0.91 |

## 6.5 What this means

1. **Diversification works in equity crashes.** In 2008 the final portfolio
   lost 5.2% while SPY lost 36.9%. AGG (+2.0 points) and GLD (+1.6 points)
   paid for most of the equity losses.
2. **It does not work when rates rise.** In 2022 AGG fell 13% and, at 59% of
   the fund, cost 7.7 points of the 12.6% loss. That is why the two bond-heavy
   candidates (Maximum Sharpe and Minimum variance) lose least in 2008 and
   2020 but most in 2022. XLE, up 64% that year, was the only hedge, and the
   final portfolio holds just 1.6% of it.
3. **Every historical replay ends inside the 15% limit, but 2022 does not stay
   inside it.** The year ended at -12.6%, yet the deepest fall within it was
   -17.2% (to October 2022). A fund that judged the limit on peak-to-trough
   loss, rather than the loss over the whole episode, would have breached it.
4. **Our inflation scenario breaks the 15% limit for every candidate.** The
   final portfolio loses 17.2% (USD 1.72m). AGG is USD 883k of that and XLK
   USD 525k. The scenario only needs to be 0.87 times as severe to hit the
   limit. Minimum variance comes closest to passing (0.94).
5. **Short crises are not small crises.** March 2020 lasted 24 trading days
   but cost almost twice the six months of 2008 in our window (-9.9% against
   -5.2%), because AGG and GLD fell too in the dash for cash instead of
   offsetting the equity losses.

**For the decision layer.** The limit should be defined as the loss over a
crisis, not peak-to-trough, or the 2022 replay already breaches it. The
largest single risk is rates through AGG; the next is XLK. Section 8 sets out
what we would change if inflation picks up.

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
