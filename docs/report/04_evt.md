# Section 4: Extreme Value Theory (EVT) and Tail Risk Modeling

**Owner:** Praveen Madawalage  
**Mandate:** USD 10,000,000 Serendib University Endowment Fund  
**Evaluation Sample:** November 18, 2004 to October 2026 (5,518 trading days)

---

## 4.1 Theoretical Foundation: The Pickands-Balkema-de Haan Theorem

For an institutional endowment, the primary existential threat is not day-to-day volatility, but rare, catastrophic tail events. Standard parametric models (such as Gaussian distributions) assume that tail probabilities decay exponentially, severely understating the likelihood of extreme crashes. Meanwhile, Historical Simulation is inherently bounded by the worst event observed in past data, rendering it incapable of extrapolating into unprecedented loss territory.

To solve this dilemma, we implement **Extreme Value Theory (EVT)** using the **Peaks-Over-Threshold (POT)** framework.

By the **Pickands-Balkema-de Haan Theorem (1974, 1975)**, for a broad class of underlying distribution functions $F$, as the threshold $u$ approaches the right endpoint of $F$, the excess distribution $F_u(y) = P(X - u \le y \mid X > u)$ converges unconditionally to the **Generalized Pareto Distribution (GPD)**:

$$G_{\xi, \sigma}(y) = \begin{cases} 
1 - \left(1 + \frac{\xi y}{\sigma}\right)^{-1/\xi} & \text{if } \xi \neq 0 \\ 
1 - \exp\left(-\frac{y}{\sigma}\right) & \text{if } \xi = 0 
\end{cases}$$

where:
- $\xi$ is the **tail index (shape parameter)** determining the rate of tail decay.
- $\sigma > 0$ is the **scale parameter** measuring tail dispersion.
- $y = x - u > 0$ represents the loss exceedance above threshold $u$.

### Tail Classification
- **$\xi > 0$ (Fréchet domain / Heavy-tailed):** The tail decays as a power law $P(X > x) \sim x^{-1/\xi}$. Financial asset returns universally belong to this class, exhibiting heavy tails, leptokurtosis, and persistent crash risk.
- **$\xi = 0$ (Gumbel domain / Exponential):** Thin tails (Gaussian, lognormal).
- **$\xi < 0$ (Weibull domain / Bounded):** Distributions with a finite upper bound.

---

## 4.2 Threshold Selection with Rigorous Evidence

The central operational challenge of Peaks-Over-Threshold modeling is selecting the threshold $u$:
- A threshold set **too low** introduces central distribution bias (violating asymptotic convergence to GPD).
- A threshold set **too high** leaves too few exceedances, inducing severe parameter variance in Maximum Likelihood Estimation (MLE).

The tournament brief explicitly mandates a **justified threshold (not picked arbitrarily)**. We establish threshold $u$ using three complementary lines of empirical evidence:

### 1. Mean Excess Function Linearity
The empirical mean excess function is defined as:
$$e(u) = E[X - u \mid X > u] = \frac{1}{N_u} \sum_{i: X_i > u} (X_i - u)$$
If the tail follows a GPD with $\xi < 1$, the theoretical mean excess function is linear in $u$:
$$e(u) = \frac{\sigma + \xi u}{1 - \xi}$$
A plot of $e(u)$ versus $u$ that is approximately linear above $u_0$ provides clear graphical evidence that GPD tail behavior begins at $u_0$.

### 2. Parameter Stability Diagnostics
By EVT properties, if exceedances follow $G_{\xi, \sigma}$ above $u_0$, then for any higher threshold $u > u_0$, the shape parameter $\xi$ remains constant, while the modified scale parameter:
$$\sigma^*(u) = \sigma(u) - \xi \cdot u$$
also remains constant. Computing MLE fits across a grid of candidate thresholds demonstrates stability above $u \approx 0.0045$.

### 3. Quantitative Cross-Validation with Benchmark Rules
We compare the selected threshold against standard institutional benchmark rules (the 90th and 95th percentiles of historical daily losses):

| Metric | Equal Weight | Minimum Variance | Maximum Sharpe | Risk Parity (Recommended) |
|---|---|---|---|---|
| **90th Percentile Rule** | 0.78% | 0.41% | 0.45% | **0.49%** |
| **95th Percentile Rule** | 1.14% | 0.60% | 0.66% | **0.72%** |
| **Selected Threshold ($u$)** | **0.78%** | **0.41%** | **0.45%** | **0.49%** |
| **Exceedance Count ($N_u$)** | 552 days | 552 days | 552 days | **552 days** |
| **Sample Share ($\hat{p}_u$)** | 10.0% | 10.0% | 10.0% | **10.0%** |

Setting $u$ at the 90th percentile provides 552 empirical crash observations (across 5,518 trading days), yielding statistical precision for MLE numerical convergence, while fitted shape parameter $\xi$ across candidate thresholds above $u$ stays within about 2 standard errors ($\text{shape\_se} \approx 0.051$, $\pm 2\text{ SE} \approx \pm 0.10$).

---

## 4.3 Maximum Likelihood Estimation and Goodness-of-Fit

With threshold $u$ established, we fit the GPD to the exceedance series $Y_i = L_i - u > 0$ using Maximum Likelihood Estimation with location fixed at $0$:

$$\ln L(\xi, \sigma; Y) = -n_u \ln \sigma - \left(1 + \frac{1}{\xi}\right) \sum_{i=1}^{n_u} \ln\left(1 + \frac{\xi Y_i}{\sigma}\right)$$

### Fitted Parameters Across Candidate Portfolios
- **Risk Parity:** $\hat{\xi} = 0.2053$, $\hat{\sigma} = 0.003116$
- **Minimum Variance:** $\hat{\xi} = 0.1921$, $\hat{\sigma} = 0.002555$
- **Maximum Sharpe:** $\hat{\xi} = 0.1845$, $\hat{\sigma} = 0.002696$
- **Equal Weight:** $\hat{\xi} = 0.2352$, $\hat{\sigma} = 0.004870$

**Key Finding:** Across all portfolios, $\hat{\xi} \approx 0.18 - 0.24 > 0$. This confirms that Serendib's asset universe resides within the **heavy-tailed Fréchet domain**. The positive shape parameters indicate that Gaussian models will inevitably underpredict extreme endowment drawdowns.

### Goodness-of-Fit: Quantile-Quantile (Q-Q) Diagnostics
To validate model specification, empirical exceedance quantiles are plotted against theoretical GPD quantiles:
$$q_i^{\text{theo}} = G_{\hat{\xi}, \hat{\sigma}}^{-1}\left(\frac{i - 0.5}{N_u}\right) = \frac{\hat{\sigma}}{\hat{\xi}} \left[\left(1 - \frac{i - 0.5}{N_u}\right)^{-\hat{\xi}} - 1\right]$$
The Q-Q diagnostic tracks the 45-degree reference line closely across all exceedance percentiles, confirming that the Generalized Pareto model fits the tail structure without systematic bias.

---

## 4.4 Closed-Form Semi-Parametric VaR and Expected Shortfall

Using the fitted GPD parameters and the empirical exceedance probability $\hat{p}_u = N_u / N$, the unconditional tail probability is:
$$P(L > x) = P(L > u) P(L > x \mid L > u) = \hat{p}_u \left(1 + \frac{\hat{\xi}(x - u)}{\hat{\sigma}}\right)^{-1/\hat{\xi}}$$

Inverting this yields the closed-form **EVT Value at Risk**:
$$\text{VaR}_\alpha^{\text{EVT}} = u + \frac{\hat{\sigma}}{\hat{\xi}}\left[\left(\frac{\hat{p}_u}{1 - \alpha}\right)^{\hat{\xi}} - 1\right]$$

By the excess mean property of the Generalized Pareto Distribution, for $\hat{\xi} < 1$, the closed-form **EVT Expected Shortfall** is:
$$\text{ES}_\alpha^{\text{EVT}} = E[L \mid L > \text{VaR}_\alpha] = \frac{\text{VaR}_\alpha^{\text{EVT}} + \hat{\sigma} - \hat{\xi} u}{1 - \hat{\xi}}$$

---

## 4.5 Empirical Results: Comparing EVT with Competing Frameworks

The table below presents 1-day tail risk metrics at 95% and 99% confidence levels on the **USD 10,000,000 Risk Parity Portfolio**:

| Confidence ($\alpha$) | Methodology | 1-Day VaR (%) | 1-Day VaR ($) | 1-Day ES (%) | 1-Day ES ($) | Tail Gap (ES - VaR) |
|---|---|---|---|---|---|---|
| **95% Confidence** | Normal (Gaussian) | 0.81% | \$81,000 | 1.03% | \$103,000 | 0.22% (\$22,000) |
| | Historical Simulation | 0.72% | \$72,000 | 1.17% | \$117,000 | 0.45% (\$45,000) |
| | **EVT (POT / GPD)** | **0.72%** | **\$72,193** | **1.17%** | **\$117,395** | **0.45% (\$45,202)** |
| **99% Confidence** | Normal (Gaussian) | 1.16% | \$116,000 | 1.34% | \$134,000 | 0.18% (\$18,000) |
| | Historical Simulation | 1.36% | \$136,000 | 2.08% | \$208,000 | 0.72% (\$72,000) |
| | **EVT (POT / GPD)** | **1.41%** | **\$140,706** | **2.04%** | **\$203,603** | **0.63% (\$62,897)** |

### Institutional Insights for the Serendib Investment Committee:
1. **The Gaussian Failure at 99%:**  
   At 99% confidence, Normal VaR predicts a maximum daily loss of \$116,000, whereas EVT projects a tail exposure of **\$140,706** (a \$24,706 undercount). Even more critically, Normal Expected Shortfall (\$134,000) underestimates the average tail catastrophe by **\$69,603** (-34.2%). Relying on Gaussian risk models would dangerously under-capitalize the endowment.
2. **Body vs. Tail Alignment:**  
   At the 95% confidence level, EVT VaR (0.72%) matches Historical Simulation (0.72%) almost to the basis point. This indicates that the GPD model does not arbitrarily inflate risk in the central distribution; its power lies in **deep-tail extrapolation** where empirical observations become sparse.
3. **The Tail Gap (ES vs. VaR):**  
   At 99%, the EVT Tail Gap is **\$62,897**. When a tail breach occurs, losses do not stop at the VaR threshold - they extend an additional 44.7% deeper. This underscores why Serendib must base capital reserves on Expected Shortfall rather than VaR alone.
