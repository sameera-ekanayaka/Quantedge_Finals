# Section 3: Value at Risk, Expected Shortfall, and Risk Budgeting

**Owner:** Aadhila Anees  
**Mandate:** USD 10,000,000 Serendib University Endowment Fund  
**Evaluation Sample:** November 18, 2004 – October 2026 (5,518 trading days)

---

## 3.1 Executive Summary & Core Risk Philosophy

For an institutional endowment supporting scholarships, faculty endowments, and capital projects, **capital preservation takes precedence over gain maximization**. As stated by the Serendib Investment Committee:
> *"Avoiding large losses is more important than maximizing gains."*  
> *"A good investment decision is not the one with the highest expected return — it is the one whose downside you have actually measured, tested, and can defend."*

This chapter measures, tests, and defends the downside risk of the candidate portfolios across **Value at Risk (VaR)**, **Expected Shortfall (ES)**, and **Euler Risk Budgeting**.

---

## 3.2 Value at Risk (VaR) Methodological Framework

Value at Risk ($\text{VaR}_\alpha$) represents the maximum expected loss over a 1-day horizon at confidence level $\alpha \in \{0.90, 0.95, 0.99\}$, such that:
$$P(L \ge \text{VaR}_\alpha) \le 1 - \alpha$$
where $L = -R_p$ denotes portfolio loss. All risk metrics are reported as **positive loss fractions** and scaled to the **USD 10,000,000** endowment pool.

We implemented and compared three fundamental methodologies:

### 1. Historical Simulation (Non-Parametric)
Calculates the empirical quantile directly from the 5,518 observed daily return realizations:
$$\text{VaR}_\alpha^{\text{Hist}} = -\hat{q}_{1 - \alpha}(R_p)$$
- **Advantage:** Completely free of distributional assumptions; captures real historical fat tails and crash correlations (including the 2008 GFC and March 2020 COVID shock).
- **Limitation:** Cannot predict losses worse than the worst event observed in the sample; sensitive to historical window length.

### 2. Parametric Gaussian (Normal) Model
Assumes portfolio returns follow a Gaussian distribution $R_p \sim \mathcal{N}(\mu_p, \sigma_p^2)$:
$$\text{VaR}_\alpha^{\text{Normal}} = -\mu_p + z_\alpha \sigma_p, \quad z_\alpha = \Phi^{-1}(\alpha)$$
- **Drift Assumption:** While daily mean drift $\mu_p \approx 0.02\%$ can be included, setting $\mu_p = 0$ provides a conservative institutional standard.

### 3. Parametric Student's $t$ Model (Leptokurtic Tail)
Captures return kurtosis (fat tails) by fitting degrees of freedom $\nu$, location $\mu$, and scale $s$ via Maximum Likelihood Estimation (MLE):
$$\text{VaR}_\alpha^{t} = -\mu - s \cdot t_{\nu}^{-1}(1 - \alpha)$$

### 4. Monte Carlo Simulation
Draws $N = 100,000$ pseudorandom return paths from the fitted Student's $t$ distribution with a fixed seed (`seed = 42`) for 100% reproducibility.

---

## 3.3 Empirical VaR & ES Results: The Risk Parity Recommendation

Across the candidate portfolios, the **Risk Parity** portfolio exhibits the highest resilience and lowest tail risk for the endowment fund. The table below presents 1-day downside metrics across all four methods on the USD 10M portfolio:

| Confidence ($\alpha$) | Methodology | 1-Day VaR (%) | 1-Day VaR (USD) | 1-Day ES (%) | 1-Day ES (USD) | Tail Gap (ES - VaR) |
|---|---|---|---|---|---|---|
| **95%** | **Historical Simulation** | **0.724%** | **$72,400** | **1.172%** | **$117,200** | **0.448% ($44,800)** |
| 95% | Parametric (Normal) | 0.814% | $81,400 | 1.028% | $102,800 | 0.214% ($21,400) |
| 95% | Parametric (Student's $t$) | 0.680% | $68,000 | 1.106% | $110,600 | 0.426% ($42,600) |
| 95% | Monte Carlo ($N=100\text{k}$) | 0.682% | $68,200 | 1.093% | $109,300 | 0.411% ($41,100) |
| **99%** | **Historical Simulation** | **1.356%** | **$135,600** | **2.084%** | **$208,400** | **0.727% ($72,700)** |
| 99% | Parametric (Normal) | 1.163% | $116,300 | 1.336% | $133,600 | 0.173% ($17,300) |
| 99% | Parametric (Student's $t$) | 1.304% | $130,400 | 1.957% | $195,700 | 0.652% ($65,200) |
| 99% | Monte Carlo ($N=100\text{k}$) | 1.295% | $129,500 | 1.898% | $189,800 | 0.603% ($60,300) |

---

## 3.4 Why the Risk Models Disagree (Critical Institutional Analysis)

A crucial requirement of the competition brief is explaining **where and why these models diverge**:

1. **The Gaussian Tail Underestimation at 99%:**  
   At $95\%$, the Normal model overstates VaR ($0.814\%$ vs. $0.724\%$ Historical) because the central bell curve is broader than the peaked empirical distribution (peaked center, leptokurtosis).  
   However, at $99\%$, the Normal model **drastically understates loss**:
   - Normal $99\%$ VaR is **$1.163\%$ ($116,300)**, whereas Historical VaR is **$1.356\%$ ($135,600)**.
   - Even worse, Normal $99\%$ ES is only **$1.336\%$ ($133,600)** compared to Historical ES of **$2.084\%$ ($208,400)** — an alarming **$74,800 blind spot**!
   - *Reason:* Financial asset returns display excess kurtosis ($K > 3$) and heavy tails. Normal distributions assign virtually zero probability to $4\sigma$ and $5\sigma$ events, which occur regularly in real financial markets.

2. **The Student's $t$ Correction:**  
   Fitting degrees of freedom ($\hat{\nu} \approx 4.5$) adjusts the tail thickness. At $99\%$, the Student's $t$ VaR of **$1.304\%$** and ES of **$1.957\%$** closely match historical crash dynamics, bridging the gap between parametric tractability and real-world fat tails.

---

## 3.5 Expected Shortfall (CVaR): The Coherent Risk Measure

The Investment Committee must not rely solely on VaR. We model **Expected Shortfall (ES / CVaR)** alongside VaR for two foundational reasons:

1. **Subadditivity and Coherence:**  
   Artzner et al. (1999) proved that Value at Risk is **not a coherent risk measure** because it violates the axiom of subadditivity:
   $$\text{VaR}_\alpha(X + Y) \not\le \text{VaR}_\alpha(X) + \text{VaR}_\alpha(Y)$$
   In non-normal or skewed asset regimes, combining assets can mathematically yield a portfolio VaR that exceeds the sum of individual VaRs, falsely penalizing diversification.  
   Expected Shortfall is rigorously **subadditive, convex, and coherent**:
   $$\text{ES}_\alpha(X + Y) \le \text{ES}_\alpha(X) + \text{ES}_\alpha(Y)$$

2. **Tail Severity Blindness of VaR:**  
   VaR answers only *"where does the tail start?"* It provides zero information about how deep losses penetrate beyond that threshold.  
   Expected Shortfall answers: *"When a crisis breaches our risk limit, what is our expected loss?"*  
   On our USD 10M Risk Parity fund at $99\%$, VaR indicates a threshold of $\$135,600$, but Expected Shortfall reveals the average loss during breaches is **$\$208,400$** — a tail severity gap of **$\$72,700$**.

---

## 3.6 Risk Budgeting & Euler Attribution (From Metrics to Decisions)

To satisfy Layer 8.6 (*Practical Investor Layer*), we decompose portfolio risk into asset-level contributions using **Euler's Homogeneous Function Theorem**.

Because VaR and ES are positive homogeneous of degree 1 ($\rho(c \cdot w) = c \cdot \rho(w)$), total risk decomposes additively:
$$\rho(w) = \sum_{i=1}^n w_i \frac{\partial \rho(w)}{\partial w_i} = \sum_{i=1}^n \text{Component Risk}_i$$

### Asset-Level Risk Attribution Table (USD 10M Risk Parity Portfolio at 95% Confidence)

| Ticker | Role / Asset Class | Capital Weight ($w_i$) | Marginal VaR ($\frac{\partial \text{VaR}}{\partial w_i}$) | Component VaR ($w_i \cdot \text{MVaR}$) | % Contribution to VaR (%RC) | Marginal ES ($\frac{\partial \text{ES}}{\partial w_i}$) | Component ES ($w_i \cdot \text{MES}$) | % Contribution to ES (%RC) |
|---|---|---|---|---|---|---|---|---|
| **SPY** | US Large-Cap Equities | 7.60% | 1.54% | 0.012% | **14.33%** | 2.38% | 0.018% | **15.40%** |
| **EFA** | Dev. International Equities | 6.64% | 1.78% | 0.012% | **14.51%** | 2.62% | 0.017% | **14.85%** |
| **EEM** | Emerging Market Equities | 5.25% | 2.25% | 0.012% | **14.51%** | 3.30% | 0.017% | **14.78%** |
| **AGG** | US Investment-Grade Bonds | 54.87% | 0.21% | 0.011% | **13.97%** | 0.22% | 0.012% | **10.36%** |
| **GLD** | Gold / Real Assets | 13.06% | 0.88% | 0.011% | **14.06%** | 1.31% | 0.017% | **14.64%** |
| **XLE** | Energy Sector | 5.67% | 2.07% | 0.012% | **14.41%** | 3.12% | 0.018% | **15.10%** |
| **XLK** | Technology Sector | 6.91% | 1.67% | 0.012% | **14.21%** | 2.52% | 0.017% | **14.87%** |
| **Total** | **Portfolio** | **100.00%** | — | **0.814%** | **100.00%** | — | **1.172%** | **100.00%** |

### Key Institutional Takeaways from Risk Budgeting:
1. **Capital Allocation $\neq$ Risk Allocation:**  
   In a standard $60/40$ equity-bond portfolio, equities consume over $85\%$ of portfolio risk. In our **Risk Parity** design, although Bonds (`AGG`) represent **$54.87\%$ of capital**, they generate only **$10.36\%$ to $13.97\%$ of total portfolio tail risk**.
2. **Shock Absorber Role of AGG & GLD:**  
   `AGG` exhibits a Marginal VaR of just $0.21\%$ and Marginal ES of $0.22\%$, acting as a volatility anchor. Gold (`GLD`) carries low marginal tail risk ($1.31\%$) relative to equities, providing essential tail hedging.
3. **Equities Position Sizing Discipline:**  
   Because Emerging Markets (`EEM`) and Energy (`XLE`) carry the highest Marginal ES ($3.30\%$ and $3.12\%$), their capital allocations must be strictly restrained to $\approx 5.25\% - 5.67\%$ so that no single asset dominates the endowment's risk budget.

---

## 3.7 Recommendation for the Investment Committee

1. **Adopt Historical and Student's $t$ ES as Primary Risk Anchors:**  
   Do not rely on Gaussian VaR for capital reserve calculations. Set the endowment's 1-day risk tolerance limit at **$2.08\%$ ($208,400) at 99% Expected Shortfall**.
2. **Implement Risk Parity Allocation:**  
   The Risk Parity structure balances tail contributions equally ($\approx 14.3\%$ risk contribution per asset), preventing equity drawdown contagion while meeting conservative institutional objectives.
