# Section 3: VaR, Expected Shortfall and risk budget

**Owner:** Aadhila Anees
**Code:** `src/var_es.py` and `src/risk_budget.py`, tested in `tests/test_var_es.py` and `tests/test_risk_budget.py`
**App page:** Risk dashboard

All numbers are for the final portfolio (`final_weights()`), one day ahead,
on the USD 10m fund, using daily returns from Nov 2004 to Oct 2026.

## 3.1 Four ways to measure a bad day

VaR at 99% is the loss we expect to beat on only 1 day in 100. ES is the
average loss on those worst days, so it says how deep the tail goes once VaR
is breached. We measure both four ways:

- **Historical simulation** reads the quantile straight from the 5,518 real
  daily returns. It assumes this sample represents future risk and cannot see
  a loss worse than history, but it imposes no distributional form.
- **Parametric normal** fits a mean and a standard deviation.
- **Parametric Student t** fits the tail thickness as well. On our portfolio
  the fitted degrees of freedom is about 3.3, which is a very fat tail.
- **Monte Carlo** draws 100,000 returns from the fitted Student t with a fixed
  seed (42), so every run gives the same number.

## 3.2 Results

| Level | Method | VaR | VaR (USD) | ES | ES (USD) |
|---|---|---|---|---|---|
| 95% | Historical | 0.66% | 66,200 | 1.02% | 102,300 |
| 95% | Normal | 0.71% | 71,300 | 0.90% | 90,100 |
| 95% | Student t | 0.61% | 60,600 | 0.98% | 98,100 |
| 95% | Monte Carlo | 0.61% | 60,600 | 0.97% | 96,900 |
| 99% | Historical | 1.16% | 116,300 | 1.73% | 173,400 |
| 99% | Normal | 1.02% | 102,000 | 1.17% | 117,300 |
| 99% | Student t | 1.16% | 115,700 | 1.73% | 172,600 |
| 99% | Monte Carlo | 1.15% | 115,200 | 1.67% | 167,400 |

## 3.3 Why the models disagree

At 95% the normal model gives the highest VaR, because real returns are more
peaked in the middle than a bell curve. At 99% it flips: the normal model
gives the lowest VaR and by far the lowest ES. Its 99% ES of USD 117k is
**USD 56k below** what history shows (USD 173k). The returns have fat tails
(Section 1), and a normal curve gives almost no chance to the 4 and 5 standard
deviation days that happened in 2008 and 2020.

The Student t and Monte Carlo numbers land within 4% of history at 99%,
because they fit the tail. This is why the memo (Section 8) monitors the
daily limits with Student t, and why Section 5 finds the normal model breaches
twice as often as it should.

**Why ES as well as VaR.** VaR only says where the tail starts. ES says what
an average bad day in the tail costs, here USD 173k against a VaR of USD 116k.
ES is also coherent: the ES of a combined portfolio is never more than the sum
of its parts, so it never punishes diversification. VaR does not have this
property (Artzner et al., 1999).

## 3.4 Risk budget: where the tail risk comes from

Because VaR and ES scale with the weights, each asset's share of the total
can be split exactly (Euler allocation): weight times marginal risk, summed
over assets, gives the portfolio number. The table uses historical ES at 99%.

| ETF | Weight | Marginal ES | Contribution (USD) | Share of ES |
|---|---|---|---|---|
| SPY | 9.55% | 3.94% | 37,585 | 21.7% |
| AGG | 58.85% | 0.62% | 36,497 | 21.0% |
| GLD | 15.00% | 1.84% | 27,658 | 15.9% |
| XLE | 1.60% | 5.20% | 8,324 | 4.8% |
| XLK | 15.00% | 4.22% | 63,366 | 36.5% |
| **Total** | **100%** | | **173,429** | **100%** |

EFA and EEM have zero weight, so they add nothing. The parametric (normal)
split puts XLK at 36% too, so the main finding does not depend on the
method.

What this tells the committee:

1. **Capital is not risk.** AGG is 59% of the money but only 21% of the tail
   risk. XLK is 15% of the money but **37% of the tail risk**, the largest
   single source.
2. **XLK is the lever.** Its marginal ES is almost seven times AGG's, so it
   is the first position to cut if risk has to come down. This is the same
   conclusion the inflation shock reaches in Section 6.
3. **GLD earns its place.** It is as large as XLK but adds well under half as
   much tail risk, because it moves little with stocks.
