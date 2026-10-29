# Section 5: Backtesting

**Owner:** Tharindu Dhanushka
**Code:** `src/backtest.py`, tested in `tests/test_backtest.py`
**App page:** Backtesting
**Reproduce:** `python -m src.backtest`

All numbers below are for the risk parity candidate, the default on the risk
dashboard. They will be rerun on the frozen weights. Data runs to 27 Oct 2026.

## 5.1 What a backtest asks

A VaR model makes a promise: at 99%, the loss should be bigger than the
forecast on about 1 day in 100. A backtest checks that promise on days the
model has not seen. We ask two questions:

1. **Coverage.** Are there the right number of breaches? (Kupiec)
2. **Independence.** Do breaches arrive one at a time, or in clusters? A model
   that is breached five days in a row in a crisis is giving no warning when
   it matters most. (Christoffersen)

## 5.2 Set-up

- **Out of sample.** The forecast for day t uses only the 500 returns before
  day t. A test checks that a crash never sits inside its own forecast window.
- **Window of 500 days (about two years).** It is above the Basel minimum of
  one year, it leaves five observations in the 1% tail (250 days would leave
  2.5), and it puts the first forecast on 14 Nov 2006, so the whole 2008 crisis
  is tested out of sample. A 1000-day window would start in late 2008 and miss
  its first months. The app offers 250 and 1000 days to check the conclusions
  do not depend on this choice.
- **Refitting.** Historical and normal VaR are refit every day. Student t,
  Monte Carlo and EVT take 0.1 to 0.3 seconds per fit, so they are refit every
  21 trading days and the forecast is held in between. A month of new data
  moves a 500-day fit very little.
- **Models.** The four methods behind `var_es` (Section 3) and the EVT model
  from Section 4. Monte Carlo uses 20,000 draws per fit with the fixed seed.
- **Sample.** 5,018 forecast days, 14 Nov 2006 to 27 Oct 2026.

## 5.3 Tests

**Kupiec proportion of failures.** With x breaches in n days and target rate
p = 1 - alpha:

LR_pof = -2 ln[ (1-p)^(n-x) p^x / ((1-x/n)^(n-x) (x/n)^x) ], chi-squared with 1 df.

**Christoffersen independence.** Count day-to-day transitions (no breach to
breach, breach to breach and so on) and compare the chance of a breach after
a breach, pi_11, with the chance after a quiet day, pi_01. LR_ind is
chi-squared with 1 df. **Conditional coverage** is LR_pof + LR_ind with 2 df.

**Basel traffic light.** Defined for 99% VaR over 250 days: 0 to 4 breaches
green, 5 to 9 yellow, 10 or more red. We apply it to the last 250 days, as a
regulator would. For the whole 20-year range we use the rule the zones come
from: green while the binomial probability of that many breaches or fewer is
below 95%, red from 99.99%. A test checks this rule gives back the official
table at 250 days. **At 90% and 95% the traffic light does not apply** and the
app says so; Kupiec and Christoffersen are still shown.

**ES backtest (extra).** The Acerbi and Szekely Z2 statistic checks the ES
forecasts: Z2 near 0 means breach losses match forecast ES on average, and
positive values mean ES was too low. Their cut-offs (0.7 yellow, 1.8 red) are
for 97.5% over 250 days, so we treat them as indicative only.

## 5.4 Results at 99%

| Model | Breaches (50.2 expected) | Kupiec p | Independence p | Cond. coverage p | Whole range | Last 250 days | ES Z2 |
|---|---|---|---|---|---|---|---|
| Historical simulation | 70 | 0.008 | <0.001 | <0.001 | Yellow | Green (4) | +0.56 |
| Parametric (normal) | 103 | <0.001 | <0.001 | <0.001 | Red | Yellow (6) | +1.78 |
| Parametric (Student t) | 39 | 0.099 | <0.001 | <0.001 | Green | Green (1) | -0.23 |
| Monte Carlo (Student t) | 39 | 0.099 | <0.001 | <0.001 | Green | Green (1) | -0.20 |
| EVT (GPD) | 65 | 0.044 | <0.001 | <0.001 | Yellow | Yellow (5) | +0.81 |

## 5.5 Results at 95%

| Model | Breaches (250.9 expected) | Kupiec p | Independence p | ES Z2 |
|---|---|---|---|---|
| Historical simulation | 270 | 0.221 | <0.001 | +0.15 |
| Parametric (normal) | 248 | 0.851 | <0.001 | +0.26 |
| Parametric (Student t) | 256 | 0.742 | <0.001 | -0.06 |
| Monte Carlo (Student t) | 254 | 0.841 | <0.001 | -0.06 |
| EVT (GPD) | 275 | 0.124 | <0.001 | +0.20 |

## 5.6 Calm and stressed periods (99%)

| Period | Days | Expected | Historical | Normal | Student t | EVT |
|---|---|---|---|---|---|---|
| 2008 financial crisis | 146 | 1.5 | 14 | 19 | 12 | 15 |
| March 2020 Covid crash | 24 | 0.2 | 8 | 8 | 5 | 8 |
| 2022 rate hikes | 251 | 2.5 | 6 | 13 | 5 | 5 |
| Calm days | 4,597 | 46.0 | 42 | 63 | 17 | 37 |

## 5.7 What this means

1. **The normal model fails at 99%.** It is breached twice as often as it
   should be (103 against 50) and lands in the red zone over the whole range.
   Its breaches are also deeper than it expects (Z2 = +1.78). This is the
   fat-tail problem from Section 3, now confirmed out of sample. At 95% the
   same model passes Kupiec, which is why a 95% backtest alone would hide it.
2. **Student t is the only model that passes Kupiec at 99%**, but it gets there
   by being too cautious in calm years (17 breaches against 46 expected) and
   too slow in crises (12 in 146 days of 2008). Monte Carlo draws from the same
   fitted Student t, so it gives the same breaches, as it should.
3. **Every model fails the independence test**, at both 95% and 99%. Breaches
   bunch in 2008 and March 2020. This is the most important finding: a model
   with a fixed 500-day window reacts slowly when volatility jumps. It points
   to a conditional model (GARCH-filtered HS or GARCH-EVT) as the next step,
   and it is why we also rely on stress tests (Section 6) rather than VaR
   alone.
4. **Historical and EVT sit in the yellow zone** over 20 years but are green
   or borderline over the last 250 days. We would not call that a fix; it is a
   calm year.

**Recommendation for the risk limit.** Use the Student t (or Monte Carlo) 99%
model for the daily limit, since it is the only one with correct coverage, and
report historical ES alongside it. Do not use the normal model at 99%. Pair the
limit with the stress loss limit in Section 6, because no unconditional model
here warns in time when a crisis starts.

## 5.8 Limitations

- **Low power.** At 99% over 250 days we expect 2.5 breaches, so the tests can
  rarely reject a bad model on one year of data. That is why we test over 20
  years and by sub-period.
- **Overlapping evidence.** The stress periods are short, so their Kupiec
  p-values are rough.
- **Held forecasts.** Monthly refits for Student t, Monte Carlo and EVT keep the
  forecast fixed for up to 20 days. Daily refits would react a little faster.
- **Fixed weights.** The portfolio is rebalanced daily to fixed weights in the
  backtest. Section 6 uses buy and hold for crises.
- **Z2 cut-offs** are from a different confidence level and are indicative.
