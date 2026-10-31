# Section 8: Committee memo

**Owner:** Sameera Ekanayaka, with the recommendation from Imasha Karunathilaka
**Weights:** `final_weights()` in `src/portfolio.py`

## 8.1 Recommendation

We recommend the **Maximum Sharpe** portfolio, with the crisis loss limit
raised from 10% to 15% of the fund.

| SPY | EFA | EEM | AGG | GLD | XLE | XLK |
|---|---|---|---|---|---|---|
| 9.55% | 0% | 0% | 58.85% | 15% | 1.6% | 15% |

## 8.2 Why this portfolio

- **It meets our base return objective.** It has historically earned **7.4% a
  year** (Nov 2004 to Oct 2026). Our base objective is about 7%: the 25-year
  average spending rate of about 4.5% plus our 2.5% inflation assumption. It
  only approximately meets the stricter 7.4% hurdle from the latest 4.9%
  effective spending rate, and falls short of the 7.8% hurdle using 3.3%
  higher-education inflation. These are sensitivities, not promised returns.
- **It has the best risk-adjusted return** of the candidates (Sharpe 0.79)
  with a maximum drawdown of -18.3%, close to Minimum variance (-17.8%) while
  earning about 0.9 points a year more.
- **Its crisis losses match the calmest candidate.** In the historical
  replays it lost 5.2% in 2008, 9.9% in March 2020 and 12.6% in 2022.
  Minimum variance lost 5.6%, 9.6% and 12.5%.
- **The diversification is real.** AGG and GLD have correlations near zero
  with the equity ETFs (Section 1), and they carry most of the weight.

## 8.3 Key risks

- **Stocks and bonds falling together.** This is what hurt in 2022, and it is
  our inflation shock (an assumption, not data): a loss of **17.2%, about
  USD 1.72m**. XLK alone is USD 525k of that.
- **Interest rates.** Almost 59% is in AGG, so a large rise in yields is the
  single biggest driver of losses.
- **The return is in-sample.** The weights were chosen on the same 2004 to
  2026 data the 7.4% is measured on, so the future return is likely lower.
- **Rebalancing.** The headline figures assume daily rebalancing. Quarterly
  rebalancing returns 7.3% with a -18.7% maximum drawdown, versus 7.4% and
  -18.3% daily, so the historical difference is small (`rebalancing_comparison`).
- **Daily risk.** One-day 99% Student t VaR is 1.16% (USD 116k) and ES is
  1.73% (USD 173k). The normal model understates both: in the backtest
  (Section 5) it breaches twice as often as it should.

## 8.4 Limits we propose

| Limit | Level | Final portfolio |
|---|---|---|
| One-day 99% VaR | USD 150k (1.5%) | USD 116k |
| One-day 99% ES | USD 200k (2.0%) | USD 173k |
| Loss in one crisis | USD 1.5m (15%) | 12.6% worst replay (2022) |

A 10% crisis limit is breached in 2022 (12.6%), and even Minimum variance
loses 12.5% that year, so no candidate can meet it. We propose 15%, measured
as the loss over the whole crisis window. Inside 2022 the fall from peak to
trough reached 17.2% (to 20 Oct 2022), so a peak-to-trough limit would already
be breached. The inflation shock (17.2%) also exceeds it, and we say so
openly rather than set the limit to fit.

We monitor the daily limits with Student t and EVT VaR and ES. At 99%, Student
t and EVT pass the Kupiec coverage test, with 41 and 56 breaches against 50.2
expected. Neither passes the independence or conditional-coverage tests:
breaches cluster in crises for every model. The limits are therefore monitoring
triggers, not proof that losses arrive independently or that the models are
fully reliable.

## 8.5 What would change our mind

- **Inflation picks up.** We cut XLK. AGG is close to its 60% cap, so the
  weight would move mostly to XLE: each point moved from XLK to XLE lowers the
  shock loss by about 0.35 points, and about 6.5 points brings it inside 15%.
- **The stock-bond correlation turns positive and stays there**, which would
  remove the hedge this portfolio relies on.
- **The backtest moves into the Basel red zone.** Today every model except
  the normal one is green over the last 250 days.
- **The committee wants a lower drawdown over return.** Then Minimum variance
  is the fallback: almost the same crisis losses, about 0.9 points less return.
