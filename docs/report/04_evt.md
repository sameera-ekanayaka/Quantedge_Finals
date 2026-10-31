# Section 4: Extreme Value Theory (EVT) and Tail Risk

**Owner:** Praveen Madawalage  
**Mandate:** USD 10m Serendib University Endowment Fund | **Sample:** 19 Nov 2004 to 27 Oct 2026 (5,518 days)  
**Code:** `src/evt.py`, tested in `tests/test_evt.py` | **App page:** Extreme Value Theory

For an endowment, the core fiduciary objective is avoiding catastrophic losses. Gaussian models assume extreme crashes are virtually impossible, while Historical Simulation cannot extrapolate beyond past data. Peaks-Over-Threshold (POT) Extreme Value Theory overcomes both by modeling tail exceedances directly.

## 4.1 Theoretical Foundation: Peaks-Over-Threshold (POT)

Under the Pickands-Balkema-de Haan Theorem, exceedances Y = X − u above threshold u converge to the **Generalized Pareto Distribution (GPD)**:

G<sub>ξ,σ</sub>(y) = 1 − (1 + ξy/σ)<sup>−1/ξ</sup>, for ξ ≠ 0 and y ≥ 0 with 1 + ξy/σ > 0.

where ξ is the shape parameter and σ > 0 is the scale parameter:
- **ξ > 0 (Fréchet / Heavy-tailed):** Tails decay as a power law P(X > x) ∼ x<sup>−1/ξ</sup>. Most financial return series exhibit fat tails and crash risk.
- **ξ = 0 (Gumbel):** Unbounded exponential tail.
- **ξ < 0 (Weibull):** Bounded tail with a finite endpoint.

## 4.2 Threshold Selection and Diagnostic Evidence

Selecting threshold u balances an empirical bias-variance trade-off: setting u too low violates GPD convergence, while setting u too high inflates MLE variance.

We selected the **90th percentile of losses** as the threshold (u = 0.45%, giving N<sub>u</sub> = 552 tail observations across 5,518 trading days) after reviewing three diagnostic plots:

1. **Mean Excess Plot:** Empirical mean excess e(u) = E[X − u | X > u] slopes upward approximately linearly above u ≈ 0.45%, which is consistent with the GPD assumption.
2. **Parameter Stability Plot:** Across thresholds from 75% to 98%, fitted shape ξ̂ stays within about 2 standard errors (±2 SE ≈ ±0.10, shape_se ≈ 0.050), and modified scale σ*(u) = σ(u) − ξu is broadly stable above 0.45%.
3. **Q-Q Plot:** Theoretical GPD quantiles track empirical exceedances reasonably along the 45-degree line.

The diagnostics are broadly consistent with the selected threshold, although threshold uncertainty and finite-sample error remain. The threshold is not automatically optimized; it is a percentile-based choice whose adequacy is assessed visually.

| Metric | Equal Weight | Minimum Variance | Maximum Sharpe (Final) | Risk Parity |
|---|---|---|---|---|
| **90th Percentile Rule** | 0.78% | 0.41% | **0.45%** | 0.49% |
| **95th Percentile Rule** | 1.14% | 0.60% | **0.66%** | 0.72% |
| **Selected Threshold (u)** | 0.78% | 0.41% | **0.45%** | 0.49% |
| **Exceedance Count (N<sub>u</sub>)** | 552 days | 552 days | **552 days** | 552 days |
| **Fitted Shape (ξ̂)** | 0.2352 | 0.1921 | **0.1843** | 0.2053 |

On the final Maximum Sharpe portfolio, MLE estimation yields ξ̂ = 0.1843 and σ̂ = 0.002696, confirming heavy-tailed Fréchet behavior.

## 4.3 EVT VaR and Expected Shortfall

With exceedance fraction p̂<sub>u</sub> = N<sub>u</sub>/N = 10.0%, closed-form EVT Value at Risk and Expected Shortfall are:

VaR<sub>α</sub> = u + (σ̂/ξ̂)[(p̂<sub>u</sub>/(1 − α))<sup>ξ̂</sup> − 1]; ES<sub>α</sub> = (VaR<sub>α</sub> + σ̂ − ξ̂u)/(1 − ξ̂).

The ES expression requires ξ̂ < 1. At ξ̂ = 0, the continuous
limit is VaR<sub>α</sub> = u + σ̂ log(p̂<sub>u</sub>/(1 − α)) and
ES<sub>α</sub> = VaR<sub>α</sub> + σ̂. For ξ̂ ≥ 1,
the fitted GPD has infinite theoretical ES.

The table compares 1-day tail risk metrics on the **USD 10m Maximum Sharpe Portfolio**:

| Level | Methodology | 1-Day VaR (%) | 1-Day VaR ($) | 1-Day ES (%) | 1-Day ES ($) | Tail Gap (ES - VaR) |
|---|---|---|---|---|---|---|
| **95%** | Normal (Gaussian) | 0.71% | \$71,300 | 0.90% | \$90,100 | \$18,800 |
| | Historical Simulation | 0.66% | \$66,200 | 1.02% | \$102,300 | \$36,100 |
| | **EVT (POT / GPD)** | **0.65%** | **\$64,637** | **1.02%** | **\$102,200** | **\$37,563** |
| **99%** | Normal (Gaussian) | 1.02% | \$102,000 | 1.17% | \$117,300 | \$15,300 |
| | Historical Simulation | 1.16% | \$116,300 | 1.73% | \$173,400 | \$57,100 |
| | Student-t | 1.16% | \$115,700 | 1.73% | \$172,600 | \$56,900 |
| | **EVT (POT / GPD)** | **1.22%** | **\$122,044** | **1.73%** | **\$172,578** | **\$50,534** |

## 4.4 Practical Committee Takeaways

1. **Gaussian Blindspot:** At 99% confidence, Normal VaR predicts a daily loss of \$102k, while EVT projects \$122k. More critically, Normal ES (\$117k) understates tail loss by **\$55,278 (-32.0%)**. Sizing capital on Gaussian models leaves the fund dangerously under-buffered.
2. **Body vs. Tail Alignment:** At 95% confidence, EVT ES (\$102,200) matches Historical Simulation (\$102,300) almost to the dollar. This agreement is a consistency check, not evidence of improved precision; tail estimates remain sensitive to the threshold and sample.
3. **Tail Gap & Capital Policy:** At 99%, the EVT Tail Gap is **\$50,534**: when breaches occur, losses extend 41.4% deeper than VaR. This supports the Section 8 policy: use **Expected Shortfall (\$173k)** for capital sizing and adopt the proposed **USD 200,000 daily ES limit**.
