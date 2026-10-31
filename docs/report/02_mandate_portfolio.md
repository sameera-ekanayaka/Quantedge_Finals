# Section 2: Mandate and portfolio choice

**Owner:** Imasha Karunathilaka
**Code:** `src/portfolio.py` and `src/kpis.py`, tested in `tests/test_mandate.py`, `tests/test_candidates.py`, `tests/test_kpis.py`, `tests/test_tradeoffs.py`, `tests/test_min_es.py`, `tests/test_final_weights.py` and `tests/test_portfolio_page.py`
**App page:** Portfolio
**Reproduce:** `streamlit run app.py`, then open the Portfolio page. The final weights are in `final_weights()`.

The committee told us that avoiding large losses matters more than making large gains. So we did not look for the best return. We looked for a portfolio whose worst case we can measure and defend. This section sets the rules (the mandate), explains how we built five candidates, and shows why we chose one. Numbers use 5,518 trading days from 19 Nov 2004 to 27 Oct 2026. The average risk free rate over this time is 1.79% a year.

**Read this first.** The weights were chosen on the same 2004 to 2026 data that we use to measure them. So every return and risk figure in this section is historical and in-sample. We did not test weights chosen on one period against another period.

## 2.1 The mandate

| Decision | Our choice | Reason |
|---|---|---|
| Horizon | Long term. Rebalance every quarter in practice. | An endowment lasts for many years. |
| Return objective | About 7% a year | See below |
| Style | Long only, no leverage | The fund cannot borrow or short. |
| One-day 99% VaR limit | 1.5% of the fund (USD 150k) | Proposed in Section 8 |
| One-day 99% ES limit | 2.0% of the fund (USD 200k) | Proposed in Section 8 |
| Crisis loss limit | 15% of the fund (USD 1.5m), measured over the whole crisis window | See below |

**Return objective.** An endowment must pay its spending and keep up with inflation. The usual way to set a target is inflation plus the spending rate. The 2025 NACUBO-Commonfund study reports an average effective spending rate of 4.9% for fiscal year 2025 (page 3). Over the past 25 years the average spending rate was about 4.5%, and endowments that set a nominal return target averaged 7.3% (Mercer's summary of the same study). We assume spending of about 4.5% and general inflation of about 2.5%. This gives our base objective of about 7% a year. The 2.5% inflation figure is our own assumption. We use two stricter hurdles as reference points. With the latest spending rate of 4.9%, the hurdle is about 7.4%. With higher education inflation of 3.3% (the Higher Education Price Index over 25 years), it is about 7.8%. The 7.4% that our chosen portfolio earned in the past is a result, not a target. It meets the base objective, only matches the first stricter hurdle, and falls short of the second. A conservative mix earns less than endowments that hold private assets, and we show this gap openly in 2.3.

**Income.** The client also wants income. Our returns use adjusted close prices, so they include the effect of dividends and bond interest, and they show the total return of each ETF. We did not model the cash yield or the yearly spending payments, so we do not state an income figure. The portfolio is 58.85% bonds, which is where most of its income comes from. We treat income as a limitation and not as a result.

**Weight limits.** These are our own judgement. They keep the fund conservative and stop one ETF from dominating.

| ETF | Minimum | Maximum |
|---|---|---|
| SPY | 0% | 40% |
| EFA | 0% | 30% |
| EEM | 0% | 10% |
| AGG | 30% | 60% |
| GLD | 0% | 15% |
| XLE | 0% | 10% |
| XLK | 0% | 15% |

**Why these limits.** The limits are our judgement, not the output of a model. Each one has a reason. Bonds have a 30% floor and a 60% cap. The floor keeps a stable core in a fund that puts losses first. The cap stops the fund from relying on one asset class, which matters because bonds fell together with stocks in 2022. SPY is capped at 40% so that stocks cannot dominate. EFA is capped at 30% to keep some room for other countries. Emerging markets are capped at 10% because they are riskier and we want the fund to stay conservative. Gold is capped at 15% because it is a diversifier and not a source of growth. The two sector funds are capped because they are concentrated bets. Energy gets 10%. Technology gets 15%, a little more, and Section 2.5 shows that lowering this cap barely changes the result. Some limits matter more than others. In Maximum Sharpe, gold and technology sit exactly at their caps and bonds are just below theirs, so the result depends on our choices.

**Crisis loss limit.** Our first idea was 10% of the fund. We tested it and no candidate meets it in all three historical crises (see 2.3). Even the calmest candidate loses 12.5% in 2022, so a 10% limit cannot be met inside this mandate. We propose 15% (USD 1.5m), the same limit used in Sections 6 and 8. We think this is fair for a conservative investor for four reasons. First, we did not set it to fit our result. The worst historical loss of the final portfolio is 12.6%, which is 2.4 points below the limit. Second, in each crisis the final portfolio lost far less than SPY alone: 5.2% against 36.9% in 2008, 9.9% against 33.4% in March 2020, and 12.6% against 18.2% in 2022. Third, the limit is measured the same way for every portfolio, as the loss over the whole crisis window. Inside 2022 the fall from peak to trough reached 17.2%, which is above 15%, and we say so openly. Fourth, a limit is a trigger for the committee to review the portfolio, not a promise that losses stay below it. The inflation shock (17.2%) is also above the limit and we report it openly. Every candidate except equal weight stays inside 15% in the three historical replays.

## 2.2 How we built the candidates

All five candidates follow the same weight limits. The optimiser stops with an error if it fails, so no wrong result is used quietly.

- **Equal weight.** The closest allowed mix to 1/7 in each ETF. Plain 1/7 breaks the 30% bond floor.
- **Minimum variance.** The calmest allowed mix.
- **Maximum Sharpe.** The best return for each unit of risk, using the 1.79% risk free rate.
- **Risk parity.** The mix where each ETF adds the same share of the total risk. The optimiser reached this exactly: every ETF contributes 14.3%.
- **Minimum ES.** The allowed mix with the lowest historical 95% expected shortfall, solved as a linear programme. It gives the same weights as minimum variance, because the caps on AGG (60%) and GLD (15%) decide the answer.

We also drew the efficient frontier under the same limits. It uses the average yearly return, so it sits a little above the compound returns in the tables. Statistics use log returns. Portfolio returns use simple returns, because log returns do not add across assets.

## 2.3 The trade-off: return against risk

All numbers are historical and in-sample. Stress losses are measured over the whole crisis window. The inflation shock is our own assumption, not data.

| Candidate | Return | Volatility | Max drawdown | 1-day ES 99% | 2008 | Mar 2020 | 2022 | Inflation shock |
|---|---|---|---|---|---|---|---|---|
| Equal weight | 9.0% | 12.8% | -35.4% | 3.4% | -19.0% | -21.4% | -7.2% | -18.7% |
| Minimum variance | 6.5% | 6.7% | -17.8% | 1.7% | -5.6% | -9.6% | -12.5% | -16.0% |
| Maximum Sharpe | 7.4% | 7.2% | -18.3% | 1.7% | -5.2% | -9.9% | -12.6% | -17.2% |
| Risk parity | 7.0% | 8.1% | -23.0% | 2.1% | -8.7% | -12.7% | -8.9% | -16.4% |
| Minimum ES | 6.5% | 6.7% | -17.8% | 1.7% | -5.6% | -9.6% | -12.5% | -16.0% |

What the table shows:

- Equal weight earns the most but its worst fall is 35.4%. It also breaks the 15% limit in 2008 and March 2020.
- No candidate keeps every historical crisis under 10%. Minimum variance and Maximum Sharpe both lose about 12.5% in 2022, because stocks and bonds fell together that year. Risk parity loses 12.7% in March 2020.
- The 2022 loss is lower for equal weight and risk parity. This is probably because they hold more energy, which rose that year. It is a one year effect, so we do not treat energy as a hedge.
- Every candidate loses more than 15% in the inflation shock. This is a hypothetical stress and we report it openly.
- Only Maximum Sharpe reaches the 7% target (7.4%). Minimum variance is about half a point short (6.5%).
- Against the two stricter hurdles, 7.4% (latest spending rate) and 7.8% (higher education inflation), Maximum Sharpe only matches the first and falls short of the second. Only equal weight (9.0%) clears both, and it has the worst losses. This is the price of a conservative mandate.- The final portfolio's one-day 99% ES is USD 173k (1.73% of the fund), inside the USD 200k limit. Equal weight (3.4%) and risk parity (2.1%) are above the 2.0% ES limit.

## 2.4 Why we chose Maximum Sharpe

The final weights are SPY 9.6%, AGG 58.9%, GLD 15%, XLK 15% and XLE 1.6%. They are fixed in `final_weights()`, and a test fails if they stop matching the optimiser.

1. **Equal weight is too risky.** The committee puts losses first, and equal weight has twice the drawdown.
2. **Maximum Sharpe and minimum variance lose about the same in the three historical crises.** The gaps are 0.4 points or less (2008: -5.2% against -5.6%, March 2020: -9.9% against -9.6%, 2022: -12.6% against -12.5%).
3. **Maximum Sharpe earns more.** Return is 7.4% against 6.5%. Sharpe is 0.79 against 0.72, and Calmar is 0.41 against 0.37. The Sharpe gap is small, and we do not claim it is a proven difference.
4. **It has a cost.** In the inflation shock Maximum Sharpe loses 17.2%, about USD 120k more than minimum variance.
5. **Its beta to SPY is 0.29.** The information ratio is -0.33. This is expected for a portfolio that is mostly bonds, since it lags SPY in good years. SPY lost 36.9% over the 2008 window, while our portfolio lost 5.2%.

### Diversification

The committee asked to see the benefit of diversification. We measure it in two ways, using the full 2004 to 2026 history.

The first way compares risk. If every ETF moved together, the portfolio's volatility would equal the weighted average of the ETF volatilities, which is 11.5%. The portfolio's actual volatility is 7.2%. So mixing the ETFs removes about 37% of the risk, and the diversification ratio is 1.6.

The second way looks at correlations. Bonds (AGG) have a correlation of about zero with the stock ETFs: 0.00 with SPY, 0.00 with XLK, 0.04 with EFA and -0.01 with EEM. Gold is also low (0.07 with SPY and 0.06 with XLK). The stock ETFs, by contrast, move closely together (SPY with XLK 0.91, SPY with EFA 0.88, SPY with XLE 0.70). So the benefit comes from bonds and gold, not from spreading across stock funds. The stock part of the portfolio (SPY, XLK and XLE, about 26% of the money) is not diversified on its own.

Two cautions. These are averages over 22 years. In 2022 stocks and bonds fell together, so the near zero correlation does not hold in every period, and our inflation shock assumes this. Also, a large part of the ratio comes from the 58.85% in bonds, which have low volatility (5.2% a year) to begin with.

**Reproduce:** the ratio is the weighted average of the asset volatilities from `asset_stats` divided by the portfolio volatility, using `final_weights()`, in `src/portfolio.py`.

### Maximum Sharpe against Minimum variance

These two are the closest candidates, so this is the choice a judge will test.

| | Minimum variance | Maximum Sharpe |
|---|---|---|
| Holdings | SPY 25%, AGG 60%, GLD 15% | SPY 9.6%, AGG 58.9%, GLD 15%, XLK 15%, XLE 1.6% |
| Annual return | 6.5% | 7.4% |
| Annual volatility | 6.7% | 7.2% |
| Sharpe | 0.72 | 0.79 |
| Sortino | 1.02 | 1.13 |
| Calmar | 0.37 | 0.41 |
| Max drawdown | -17.8% | -18.3% |
| 1-day ES at 99% | 1.7% | 1.7% |
| 2008 | -5.6% | -5.2% |
| March 2020 | -9.6% | -9.9% |
| 2022 | -12.5% | -12.6% |
| Inflation shock (assumption) | -16.0% | -17.2% |

What Maximum Sharpe gives: 0.9 points more return a year, which is what lets it reach the 7% base objective. It also holds four ETFs above 5%, against three.

What it costs: a max drawdown 0.5 points deeper, and an inflation shock loss 1.2 points larger (about USD 120k). In the three historical crises the two are within 0.4 points of each other.

Concentration: Minimum variance gets 51.5% of its variance from SPY alone. Maximum Sharpe gets about 36% of its risk from XLK. Both depend on one ETF, so neither is clearly more diversified.

We do not claim the gap in Sharpe is proven, because both are in-sample. We would switch to Minimum variance if the committee ranks the inflation shock above the 7% objective.

**Where the risk comes from.** We used Aadhila's risk budget (Section 3), which splits the risk of the final portfolio between the ETFs. Technology is 15% of the money but about 36% of the risk. This is the same under the normal method (36.0%) and historical ES at 99% (36.5%), so it does not depend on the method. The historical VaR attribution is a local approximation around the sample quantile and gives XLK 37.8%; it does not reconcile exactly to portfolio VaR. Bonds are 58.9% of the money but only about 21% of the risk. Gold adds 15.9% of the tail loss, less than its 20.1% share under the normal method, so it helps a little on the worst days. SPY adds 21.7%. The historical numbers use about 55 bad days at 99%, so we read them as rough. **Reproduce:** `risk_budget(returns, final_weights(), alpha=0.99, method='historical')` in `src/risk_budget.py`.
**Verdict for the committee:** accept with an adjusted risk limit (Section 8).

## 2.5 What we tested and what we did not

**Lower caps on technology.** We reran Maximum Sharpe with a lower cap on XLK.

| XLK cap | Return | Sharpe | 2022 loss | Inflation shock |
|---|---|---|---|---|
| 15% (chosen) | 7.4% | 0.786 | -12.6% | -17.2% |
| 12% | 7.3% | 0.775 | -12.8% | -17.1% |
| 10% | 7.2% | 0.767 | -12.8% | -17.0% |
| 8% | 7.2% | 0.758 | -12.9% | -16.9% |
| 5% | 7.1% | 0.745 | -13.1% | -16.8% |

**Reproduce:** `xlk_cap_test(returns, rf_annual)` in `src/portfolio.py`

Return and Sharpe fall a little, the 2022 loss gets slightly worse, and the inflation shock improves by only 0.4 points at the lowest cap. The money moves into SPY, which is also stock risk. So we kept 15%.

**What we did not do:**

- The weights were chosen on the same 2004 to 2026 data used to measure them. The 7.4% return is historical and probably too optimistic. We did not run a test where the weights are chosen on one period and measured on another.
- The headline numbers assume the weights are reset every day, but a real fund rebalances every quarter. We checked this with `rebalancing_comparison`. For the final portfolio the quarterly return is 7.3% against 7.4%, the max drawdown is -18.7% against -18.3%, and the 1-day 99% ES is 1.71% against 1.73%. The difference is small, so we keep the daily figures as the headline. The stress replays in Section 6 already use buy and hold. **Reproduce:** `rebalancing_comparison(returns, final_weights(), rf_annual)` in `src/portfolio.py`.
- We ignore trading costs and fees.
- We measure risk over one day. We did not build a 10 to 20 day view.

## 2.6 Why a conservative endowment should accept this portfolio

The committee asked what can go wrong, how bad losses could become, and how confident we are. Our answer:

- **What it offers.** Historically 7.4% a year with 7.2% volatility, close to our 7% base objective, with a Sharpe ratio of 0.79.
- **How bad it got.** In the three historical crises it lost 5.2%, 9.9% and 12.6% over the crisis window (at most USD 1.26m on USD 10m), against 36.9%, 33.4% and 18.2% for SPY alone. The one day 99% expected shortfall is 1.73% of the fund (USD 173k), inside the USD 200k limit.
- **What remains.** Stocks and bonds can fall together, as in 2022. Our own inflation shock costs 17.2% (USD 1.72m), above the 15% limit. Technology causes about 36% of the risk with 15% of the money.
- **How confident we are.** Less than the numbers suggest. The weights were chosen on the same 2004 to 2026 data, trading costs are not included, and the quarterly rebalancing check shows a small drop in return.
- **Our request.** Accept the portfolio with a crisis loss limit of 15%, and review it if the inflation shock or the technology risk becomes a concern.

## 2.7 Other risks we considered

These come from our own tests. They are not forecasts.

- **Interest rates.** Bonds are 58.85% of the fund. A fast rise in yields is the biggest single risk, as in 2022. Section 6 assumes bonds fall 15% in our inflation shock.
- **Inflation.** Our inflation shock costs 17.2% (USD 1.72m), above the 15% limit. Section 8 says we would move money from technology into energy if inflation persists.
- **Stock and bond correlation.** The portfolio relies on bonds and gold to offset stocks. If stocks and bonds move together for a long time, that protection is weaker. This is why 2022 is our worst historical replay.
- **Concentration.** Technology is 15% of the money and about 36% of the portfolio's risk, so a fall in technology shares matters more than its weight suggests.
- **Model risk.** Our risk estimates come from history. Section 5 shows that breaches cluster in crises for every model, so the limits are monitoring triggers and not guarantees.

**Sources:** NACUBO and Commonfund Institute (2026). Summary observations from the 2025 NACUBO-Commonfund Study of Endowments. Spending rate: page 3. Return objectives: page 6. Momjian, L. Insights from the 2025 NACUBO-Commonfund Study of Endowments. Mercer (Marsh). Source for the 25-year average spending rate of about 4.5% and the HEPI hurdle of about 7.8%.
