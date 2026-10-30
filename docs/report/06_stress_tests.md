# Section 6: Stress tests

**Owner:** Tharindu Dhanushka
**Code:** `src/stress.py`, tested in `tests/test_stress.py`
**App page:** Stress tests
**Reproduce:** `python -m src.stress`

VaR describes a normal bad day, and Section 5 shows every model lets breaches
pile up when a crisis starts. Stress tests answer the committee directly: if
2008 happened again, how much of the USD 10m would we lose? Numbers are for
the final portfolio (`final_weights()`, Section 8) on data to 27 Oct 2026.

## 6.1 Method

- **Historical replays** of three periods from `src/config.py`: 2008 (1 Sep
  2008 to 31 Mar 2009), the Covid crash (19 Feb to 23 Mar 2020) and the 2022
  rate hikes (calendar year). We buy at the close before the first day and
  hold, so weights drift and nothing is rebalanced mid-crisis, as for a fund
  that rebalances quarterly. ETF contributions add up exactly to the total.
- **Our own scenario (an assumption, not data):** an inflation surprise lifts
  yields about 250bp, so stocks and bonds fall together. This is the
  stock-bond hedge failure we found in round 1. The shocks can be edited in
  the app.

| ETF | Shock | Reason |
|---|---|---|
| SPY, EFA | -25% | Higher real rates cut valuations, about 1.4 times 2022 |
| EEM | -30% | Strong dollar and capital outflows |
| AGG | -15% | 250bp rise in yields times a duration of about 6 |
| GLD | -5% | Rising real yields, so no hedge |
| XLE | 0% | Rose 64% in 2022; we assume no help |
| XLK | -35% | Long-duration tech falls most when rates rise |

- **Limit.** The crisis loss limit is 15% of the fund (USD 1.5m), measured
  over the whole crisis window (Section 8). The reverse stress test asks how
  many times as severe our scenario must be to reach it.

## 6.2 Results

**Final portfolio**

| Scenario | Return | P&L (USD) | Max drawdown | Worst day | SPY |
|---|---|---|---|---|---|
| 2008 financial crisis | -5.2% | -517,024 | -14.6% | -5.86% (10 Oct 2008) | -36.9% |
| March 2020 Covid crash | -9.9% | -989,191 | -12.8% | -5.28% (12 Mar 2020) | -33.4% |
| 2022 rate hikes | -12.6% | -1,264,453 | -17.2% | -2.45% (13 Jun 2022) | -18.2% |
| Inflation shock (assumption) | -17.2% | -1,721,500 | | | -25.0% |

**Contribution by ETF, in points of return** (EFA and EEM have zero weight)

| Scenario | SPY | AGG | GLD | XLE | XLK |
|---|---|---|---|---|---|
| 2008 financial crisis | -3.5 | +2.0 | +1.6 | -0.7 | -4.6 |
| March 2020 Covid crash | -3.2 | -0.8 | -0.5 | -0.9 | -4.6 |
| 2022 rate hikes | -1.7 | -7.7 | -0.1 | +1.0 | -4.2 |
| Inflation shock | -2.4 | -8.8 | -0.8 | 0.0 | -5.3 |

**Every candidate**

| Scenario | Equal weight | Min. variance | Max. Sharpe (final) | Risk parity |
|---|---|---|---|---|
| 2008 financial crisis | -19.0% | -5.6% | -5.2% | -8.7% |
| March 2020 Covid crash | -21.4% | -9.6% | -9.9% | -12.7% |
| 2022 rate hikes | -7.2% | -12.5% | -12.6% | -8.9% |
| Inflation shock | -18.8% | -16.0% | -17.2% | -16.4% |
| Reverse stress multiple at 15% | 0.80 | 0.94 | 0.87 | 0.91 |

## 6.3 What this means

1. **Diversification works in equity crashes.** In 2008 the portfolio lost
   5.2% while SPY lost 36.9%, as AGG (+2.0 points) and GLD (+1.6) offset most
   of the equity losses.
2. **It fails when rates rise.** In 2022 AGG, at 59% of the fund, cost 7.7 of
   the 12.6 points. So the bond-heavy candidates (Maximum Sharpe, Minimum
   variance) lose least in 2008 and 2020 but most in 2022. XLE, up 64% that
   year, was the only hedge, and we hold 1.6% of it.
3. **Every replay ends inside 15%, but 2022 does not stay inside it.** The
   deepest fall within the year was 17.2% (to 20 Oct 2022). That is why the
   limit is measured over the whole crisis window, not peak to trough.
4. **Our inflation scenario breaks 15% for every candidate.** The portfolio
   loses 17.2% (USD 1.72m), of which AGG is USD 883k and XLK USD 525k. A
   scenario 0.87 times as severe already reaches the limit.
5. **Short crises are not small.** March 2020 lasted 24 trading days but cost
   almost twice our 2008 window (-9.9% against -5.2%), because AGG and GLD
   fell too in the dash for cash.

The largest single risk is rates through AGG, then XLK. Section 8 sets out
what we would change if inflation picks up.

## 6.4 Limitations

- **The 2008 window starts on 1 Sep 2008**, so it misses the fall from the
  October 2007 peak and understates the full bear market.
- **History will not repeat exactly**, which is why we add our own scenario.
  Its shocks are judgement, applied instantly (no path or drawdown), and the
  reverse stress test assumes they scale in proportion.
- **No transaction costs or liquidity effects.** ETF spreads widened sharply
  in March 2020, so selling in a crisis would cost more than shown.
