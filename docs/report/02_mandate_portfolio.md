# Section 2: Mandate and portfolio choice

**Owner:** Imasha Karunathilaka
**Code:** `src/portfolio.py` and `src/kpis.py`, tested in `tests/test_mandate.py`, `tests/test_candidates.py`, `tests/test_kpis.py`, `tests/test_tradeoffs.py`, `tests/test_min_es.py`, `tests/test_final_weights.py` and `tests/test_portfolio_page.py`
**App page:** Portfolio
**Reproduce:** `streamlit run app.py`, then open the Portfolio page. The final weights are in `final_weights()`.

The committee told us that avoiding large losses matters more than making large gains. So we did not look for the best return. We looked for a portfolio whose worst case we can measure and defend. This section sets the rules (the mandate), explains how we built five candidates, and shows why we chose one. Numbers use 5,518 trading days from 19 Nov 2004 to 27 Oct 2026. The average risk free rate over this time is 1.79% a year.

## 2.1 The mandate

| Decision | Our choice | Reason |
|---|---|---|
| Horizon | Long term. Rebalance every quarter in practice. | An endowment lasts for many years. |
| Return objective | About 7% a year | See below |
| Style | Long only, no leverage | The fund cannot borrow or short. |
| One-day 99% VaR limit | 1.5% of the fund (USD 150k) | Proposed in Section 8 |
| One-day 99% ES limit | 2.0% of the fund (USD 200k) | Proposed in Section 8 |
| Crisis loss limit | 15% of the fund (USD 1.5m), measured over the whole crisis window | See below |

**Return objective.** An endowment must pay its spending and keep up with inflation. The usual way to set a target is inflation plus the spending rate. The 2025 NACUBO-Commonfund study reports an average effective spending rate of 4.9% for fiscal year 2025 (page 3). Over the past 25 years the average spending rate was about 4.5%, and endowments that set a nominal return target averaged 7.3% (Mercer's summary of the same study). We assume spending of about 4.5% and general inflation of about 2.5%, which gives about 7%. The 2.5% inflation figure is our own assumption. Higher education costs have risen faster. The same summary says the Higher Education Price Index averaged 3.3% over 25 years, which gives a hurdle of about 7.8%. Our best conservative candidate earned 7.4% in the past, so it falls short of that higher hurdle. A conservative mix earns less than endowments that hold private assets, and we show this gap openly in 2.3.

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

**Crisis loss limit.** Our first idea was 10% of the fund. We tested it and no candidate meets it in all three historical crises (see 2.3). So we propose 15%, the same limit used in Sections 6 and 8. Every candidate except equal weight stays inside 15% in the three historical replays.

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
- Against the higher 7.8% hurdle, only equal weight (9.0%) clears it, and it has the worst losses. This is the price of a conservative mandate.
- The final portfolio's one-day 99% ES is USD 173k (1.73% of the fund), inside the USD 200k limit. Equal weight (3.4%) and risk parity (2.1%) are above the 2.0% ES limit.

## 2.4 Why we chose Maximum Sharpe

The final weights are SPY 9.6%, AGG 58.9%, GLD 15%, XLK 15% and XLE 1.6%. They are fixed in `final_weights()`, and a test fails if they stop matching the optimiser.

1. **Equal weight is too risky.** The committee puts losses first, and equal weight has twice the drawdown.
2. **Maximum Sharpe and minimum variance lose about the same in the three historical crises.** The gaps are 0.4 points or less (2008: -5.2% against -5.6%, March 2020: -9.9% against -9.6%, 2022: -12.6% against -12.5%).
3. **Maximum Sharpe earns more.** Return is 7.4% against 6.5%. Sharpe is 0.79 against 0.72, and Calmar is 0.41 against 0.37. The Sharpe gap is small, and we do not claim it is a proven difference.
4. **It has a cost.** In the inflation shock Maximum Sharpe loses 17.2%, about USD 120k more than minimum variance.
5. **Its beta to SPY is 0.29.** The information ratio is -0.33. This is expected for a portfolio that is mostly bonds, since it lags SPY in good years. SPY lost 36.9% over the 2008 window, while our portfolio lost 5.2%.

**Where the risk comes from.** Technology is 15% of the money but 35.9% of the risk. Bonds are 58.9% of the money and 21.5% of the risk. Gold adds 20.2% and SPY adds 18.9%.

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

Return and Sharpe fall a little, the 2022 loss gets slightly worse, and the inflation shock improves by only 0.4 points at the lowest cap. The money moves into SPY, which is also stock risk. So we kept 15%.

**What we did not do:**

- The weights were chosen on the same 2004 to 2026 data used to measure them. The 7.4% return is historical and probably too optimistic. We did not run a test where the weights are chosen on one period and measured on another.
- The headline return and risk numbers assume the weights are rebalanced every day. A real fund rebalances every quarter. The stress replays in Section 6 buy and hold.
- We ignore trading costs and fees.
- We measure risk over one day. We did not build a 10 to 20 day view.

**Sources:** NACUBO and Commonfund Institute (2026). Summary observations from the 2025 NACUBO-Commonfund Study of Endowments. Spending rate: page 3. Return objectives: page 6. Momjian, L. Insights from the 2025 NACUBO-Commonfund Study of Endowments. Mercer (Marsh). Source for the 25-year average spending rate of about 4.5% and the HEPI hurdle of about 7.8%.