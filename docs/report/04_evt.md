# Section 4: Extreme Value Theory (EVT) and Tail Risk

**Owner:** Praveen Madawalage  
**Mandate:** USD 10m Serendib University Endowment Fund | **Sample:** 19 Nov 2004 to 27 Oct 2026 (5,518 days)  
**Code:** `src/evt.py`, tested in `tests/test_evt.py` | **App page:** Extreme Value Theory

For an endowment, the core fiduciary objective is avoiding catastrophic losses. Gaussian models assume extreme crashes are virtually impossible, while Historical Simulation cannot extrapolate beyond past data. Peaks-Over-Threshold (POT) Extreme Value Theory overcomes both by modeling tail exceedances directly.

## 4.1 Theoretical Foundation: Peaks-Over-Threshold (POT)

Under the Pickands-Balkema-de Haan Theorem, exceedances $Y = X - u$ above threshold $u$ converge to the **Generalized Pareto Distribution (GPD)**:

$$G_{\xi, \sigma}(y) = 1 - \left(1 + \frac{\xi y}{\sigma}\right)^{-1/\xi} \quad (\xi \neq 0)$$

where $\xi$ is the shape parameter and $\sigma > 0$ is the scale parameter:
- **$\xi > 0$ (Fréchet / Heavy-tailed):** Tails decay as a power law $P(X > x) \sim x^{-1/\xi}$. Most financial return series exhibit fat tails and crash risk.
- **$\xi = 0$ (Gumbel):** Thin exponential tails (Gaussian).
- **$\xi < 0$ (Weibull):** Bounded tails with a finite endpoint.

## 4.2 Threshold Selection and Diagnostic Evidence

Selecting threshold $u$ balances an empirical bias-variance trade-off: setting $u$ too low violates GPD convergence, while setting $u$ too high inflates MLE variance.

We set $u$ at the **90th percentile of losses** ($u = 0.45\%$, giving $N_u = 552$ tail observations across 5,518 trading days). Three diagnostics confirm this threshold is defensible:

1. **Mean Excess Linearity:** Empirical mean excess $e(u) = E[X - u \mid X > u]$ slopes upward linearly above $u \approx 0.45\%$, confirming the GPD tail domain.
2. **Parameter Stability:** Across thresholds from 75% to 98%, fitted shape $\hat{\xi}$ stays within about 2 standard errors ($\pm 2\text{ SE} \approx \pm 0.10$, $\text{shape\_se} \approx 0.050$), and modified scale $\sigma^*(u) = \sigma(u) - \xi u$ stabilizes above $0.45\%$.
3. **Q-Q Fit:** Theoretical GPD quantiles track empirical exceedances closely along the 45-degree line, validating fit without systematic bias.

| Metric | Equal Weight | Minimum Variance | Maximum Sharpe (Final) | Risk Parity |
|---|---|---|---|---|
| **90th Percentile Rule** | 0.78% | 0.41% | **0.45%** | 0.49% |
| **95th Percentile Rule** | 1.14% | 0.60% | **0.66%** | 0.72% |
| **Selected Threshold ($u$)** | 0.78% | 0.41% | **0.45%** | 0.49% |
| **Exceedance Count ($N_u$)** | 552 days | 552 days | **552 days** | 552 days |
| **Fitted Shape ($\hat{\xi}$)** | 0.2352 | 0.1921 | **0.1843** | 0.2053 |

On the final Maximum Sharpe portfolio, MLE estimation yields $\hat{\xi} = 0.1843$ and $\hat{\sigma} = 0.002696$, confirming heavy-tailed Fréchet behavior.

## 4.3 EVT VaR and Expected Shortfall

With exceedance fraction $\hat{p}_u = N_u / N = 10.0\%$, closed-form EVT Value at Risk and Expected Shortfall are:

$$\text{VaR}_\alpha^{\text{EVT}} = u + \frac{\hat{\sigma}}{\hat{\xi}}\left[\left(\frac{\hat{p}_u}{1 - \alpha}\right)^{\hat{\xi}} - 1\right], \quad \text{ES}_\alpha^{\text{EVT}} = \frac{\text{VaR}_\alpha^{\text{EVT}} + \hat{\sigma} - \hat{\xi} u}{1 - \hat{\xi}}$$

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
2. **Body vs. Tail Alignment:** At 95% confidence, EVT ES (\$102,200) matches Historical Simulation (\$102,300) almost to the dollar. GPD modeling does not distort central risk, but adds precision in sparse tails.
3. **Tail Gap & Capital Policy:** At 99%, the EVT Tail Gap is **\$50,534**: when breaches occur, losses extend 41.4% deeper than VaR. This supports the Section 8 policy: use **Expected Shortfall (\$173k)** for capital sizing and adopt the proposed **USD 200,000 daily ES limit**.
