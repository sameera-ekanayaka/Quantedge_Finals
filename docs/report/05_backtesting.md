# Section 5: Backtesting

**Owner:** Tharindu Dhanushka
**Code:** `src/backtest.py`, tested in `tests/test_backtest.py`
**App page:** Backtesting
**Reproduce:** `python -m src.backtest`

A 99% VaR model promises a loss bigger than the forecast on about 1 day in
100. We check that promise on days the model has not seen, for the final
portfolio (`final_weights()`, Section 8), on data to 27 Oct 2026. We ask two
questions: are there the right number of breaches (coverage), and do they
arrive one at a time rather than in clusters (independence)?

## 5.1 Set-up

- **Out of sample.** The forecast for day t uses only the 500 returns before
  it. A unit test checks a crash never sits inside its own forecast window.
- **500-day window (about two years).** It is above the Basel one-year
  minimum, leaves five observations in the 1% tail, and puts the first
  forecast on 14 Nov 2006, so all of 2008 is tested out of sample. The app
  also offers 250 and 1000 days as a robustness check.
- **Refitting.** Historical and normal VaR are refit daily. Student t, Monte
  Carlo (20,000 draws, fixed seed) and EVT are refit every 21 trading days
  and held in between, since each fit takes 0.1 to 0.3 seconds.
- **Sample.** 5,018 forecast days, 14 Nov 2006 to 27 Oct 2026.

## 5.2 Tests

- **Kupiec** compares x breaches in n days with the target rate p = 1 - alpha:
  LR_pof = -2 ln[ (1-p)^(n-x) p^x / ((1-x/n)^(n-x) (x/n)^x) ], chi-squared(1).
- **Christoffersen independence** compares the chance of a breach after a
  breach (pi_11) with the chance after a quiet day (pi_01), chi-squared(1).
  **Conditional coverage** adds the two statistics, chi-squared(2).
- **Basel traffic light**, defined for 99% VaR over 250 days: 0 to 4 breaches
  green, 5 to 9 yellow, 10 or more red. We apply it to the last 250 days. For
  the whole range we use the binomial rule the zones come from (green below
  95% cumulative probability, red from 99.99%); a test checks it reproduces
  the official table. At 90% and 95% the light does not apply and the app
  says so.
- **ES check (extra).** The Acerbi and Szekely Z2 statistic is near 0 when
  breach losses match the forecast ES and positive when ES is too low. Its
  cut-offs (0.7 yellow, 1.8 red) are for 97.5%, so we treat them as
  indicative.

## 5.3 Results

**At 99%** (50.2 breaches expected)

| Model | Breaches | Kupiec p | Indep. p | Whole range | Last 250 days | ES Z2 |
|---|---|---|---|---|---|---|
| Historical simulation | 67 | 0.023 | <0.001 | Yellow | Green (4) | +0.51 |
| Parametric (normal) | 105 | <0.001 | <0.001 | Red | Yellow (6) | +1.75 |
| Parametric (Student t) | 41 | 0.179 | <0.001 | Green | Green (4) | -0.08 |
| Monte Carlo (Student t) | 41 | 0.179 | <0.001 | Green | Green (4) | -0.04 |
| EVT (GPD) | 56 | 0.418 | <0.001 | Green | Green (4) | +0.60 |

Conditional coverage is rejected for every model (p < 0.001).

**At 95%** (250.9 expected), breaches and Kupiec p are: historical 277
(0.096), normal 270 (0.221), Student t 257 (0.694), Monte Carlo 261 (0.516),
EVT 284 (0.036). Independence is rejected for every model (p < 0.001).

**Breaches at 99% by period**

| Period | Days | Expected | Historical | Normal | Student t | EVT |
|---|---|---|---|---|---|---|
| 2008 financial crisis | 146 | 1.5 | 12 | 16 | 15 | 14 |
| March 2020 Covid crash | 24 | 0.2 | 7 | 8 | 5 | 7 |
| 2022 rate hikes | 251 | 2.5 | 5 | 12 | 3 | 4 |
| Calm days | 4,597 | 46.0 | 43 | 69 | 18 | 31 |

## 5.4 What this means

1. **The normal model fails at 99%:** 105 breaches against 50, red over the
   whole range, and breaches deeper than it expects (Z2 = +1.75). This is the
   fat-tail problem from Section 3, confirmed out of sample. It passes at 95%,
   so a 95% backtest alone would hide it.
2. **Student t, Monte Carlo and EVT pass Kupiec at 99%.** EVT is closest
   (56 against 50, p = 0.42). Student t is right only on average: too cautious
   in calm years (18 against 46) and too slow in 2008 (15 in 146 days). Monte
   Carlo draws from the same fitted Student t, so it gives the same count.
3. **Historical VaR is breached a little too often** (67 against 50,
   p = 0.02), which is why Section 8 monitors the daily limit with Student t
   or EVT instead.
4. **Every model fails independence.** Breaches bunch in 2008 and March 2020
   because a fixed 500-day window reacts slowly when volatility jumps. This is
   the main finding: it points to a conditional model (GARCH-filtered HS or
   GARCH-EVT) as the next step, and it is why the stress tests in Section 6
   carry as much weight as VaR.
5. **No red zone.** Over the last 250 days every model except the normal one
   is green, so the memo's trigger for changing our mind has not been hit.

## 5.5 Limitations

- **Low power.** At 99% over 250 days only 2.5 breaches are expected, so one
  year can rarely reject a bad model. We test over 20 years and by period;
  the short stress periods give only rough p-values.
- **Held forecasts.** Monthly refits keep a forecast fixed for up to 20 days.
- **Fixed weights.** The backtest rebalances daily; Section 6 uses buy and
  hold.
