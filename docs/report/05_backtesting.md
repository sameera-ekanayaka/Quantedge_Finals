# Section 5: Backtesting and conditional risk

## 5.1 Honest validation design

Risk forecasts use prior returns conditional on fixed weights. The weights themselves were chosen in sample; this is not an out-of-sample allocation test. A 500-day estimation window yields 5,018 forecasts from November 2006. The comparison below uses identical dates from January 2008 through October 2026: 4,735 forecasts. Allocation walk-forward validation is reported separately in Section 2.

Historical and Gaussian models refit daily. Original Student t, parametric Monte Carlo and EVT refit every 21 trading days and hold forecasts between fits. The joint ETF bootstrap also refits monthly, with 20,000 draws. Forecast CSVs record every return, VaR/ES and breach for the models below. The app's original Backtesting page also offers 250/500/1000-day windows and date controls.

## 5.2 GARCH extensions

GARCH(1,1) with constant mean uses Gaussian quasi-maximum-likelihood on the preceding 500 returns in percentage units, refitting every 21 days. Conditional variance updates daily using only the last observed residual. Filtered historical simulation estimates standardised residual-tail VaR/ES; GARCH-EVT fits the residual 90th-percentile loss tail. Transform these by next-day conditional volatility and mean. Convergence failures raise errors. Prefix-invariance tests ensure changing future returns cannot alter prior forecasts. Volatility filtering addresses time variation, but cannot guarantee independence or stable regimes.

<h2 style="page-break-before: always;">5.3 Tests and outcomes at 99%</h2>

| Model                     |   days |   breaches |   kupiec_p |     ind_p |      cc_p |
|:--------------------------|-------:|-----------:|-----------:|----------:|----------:|
| GARCH filtered HS         |   4735 |         63 |   0.02957  | 0.0001661 | 7.812e-05 |
| GARCH EVT                 |   4735 |         61 |   0.0563   | 0.0001134 | 9.412e-05 |
| Historical                |   4735 |         61 |   0.0563   | 9.939e-06 | 9.322e-06 |
| Unfiltered EVT            |   4735 |         51 |   0.5985   | 3.737e-08 | 2.313e-07 |
| Joint ETF bootstrap       |   4735 |         61 |   0.0563   | 4.738e-08 | 5.411e-08 |
| Parametric normal         |   4735 |         99 |   4.68e-11 | 1.046e-08 | 3.044e-17 |
| Parametric Student t      |   4735 |         40 |   0.27     | 2.005e-08 | 7.904e-08 |
| Monte Carlo (t reference) |   4735 |         40 |   0.27     | 5.51e-10  | 2.39e-09  |

Kupiec compares the observed breach frequency with 1 − α using a likelihood ratio with a chi-squared(1) reference. Christoffersen independence tests transition probabilities (chi-squared(1)); joint conditional coverage adds the two likelihood ratios (chi-squared(2)). At 99% over 250 days the Basel zones are green 0–4 breaches, yellow 5–9, red ≥10; these standard zones do not apply unchanged to other confidence levels. The extra ES Z2 check is indicative, with cutoffs derived for a different confidence level; it is not a formal calibrated approval test here.

**All models above reject independence and joint coverage at 5%.** GARCH improves independence p-values relative to the listed unfiltered baselines, but does not cure clustering. Filtered HS also rejects unconditional coverage; GARCH-EVT narrowly passes it. High coverage p-values do not validate allocation selection or prove model correctness. Monitor both historical/Student-t and EVT risk, plus conditional-model diagnostics; do not select a model solely because it passes one test. Limited expected tail counts weaken short-window tests.
