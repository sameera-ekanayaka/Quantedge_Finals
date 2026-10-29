# Section 7: Assumptions and Limitations

**Owner:** Praveen Madawalage  
**Mandate:** USD 10,000,000 Serendib University Endowment Fund  
**Status:** Non-negotiable, explicitly graded chapter

---

## 7.1 Executive Statement on Model Risk Governance

Quantitative risk models provide invaluable structure for institutional decision-making, but they are simplifications of complex, non-stationary financial systems. For the **Serendib University Endowment Fund**, the governing fiduciary mandate states:
> *"Avoiding large losses is more important than maximizing gains."*

Fulfilling this mandate requires complete transparency regarding the assumptions that power our algorithms, the boundaries where our mathematical formulations break down, and the governance mechanisms established to prevent model failure from impairing endowment capital.

This section provides a rigorous audit of assumptions, limitations, and mitigations across every layer of the investment engine.

---

## 7.2 Layer 0 & 1: Mandate Decisions and Portfolio Construction

### 1. Costless Daily Rebalancing
- **Core Assumption:** Portfolio allocations are rebalanced continuously at zero transaction cost, zero bid-ask spread slippage, and zero market impact.
- **Vulnerability & Limitation:** For a real USD 10,000,000 portfolio, daily rebalancing is operationally impractical and financially dilutive. In market sell-offs, rebalancing into crashing risk assets incurs severe execution drag and liquidity penalties.
- **Institutional Mitigation:** The endowment implements **tolerance-band rebalancing** rather than calendar daily rebalancing. Asset weights are allowed to drift within a $\pm 2.5\%$ corridor around target weights before triggering rebalancing trades, typically executed quarterly.

### 2. Stationarity of Risk-Return Moments
- **Core Assumption:** Sample means, standard deviations, and correlation matrices computed over the 2004–2026 sample provide unbiased estimates of future asset returns.
- **Vulnerability & Limitation:** The investment landscape undergoes macroeconomic regime shifts. The 2009–2021 post-GFC era was characterized by unprecedented central bank quantitative easing and near-zero rates, conditions that will not persist in an era of persistent fiscal deficits and deglobalization.
- **Institutional Mitigation:** We do not rely on unconstrained mean-variance optimization (which notoriously functions as an "error maximizer"). Instead, we impose strict mandate limits: a **30% minimum floor on US Aggregate Bonds (AGG)** and individual sector/asset caps (10% on EEM/XLE, 15% on XLK/GLD).

---

## 7.3 Data Pipeline and Empirical Hygiene

### 1. Sample Horizon Selection (Nov 2004 – Oct 2026)
- **Core Assumption:** Commencing the dataset on November 18, 2004 aligns the trading histories of all seven ETFs while providing 5,518 trading days of rich multi-regime market dynamics.
- **Vulnerability & Limitation:** The 2000–2002 dot-com equity collapse is omitted because SPDR Gold Shares (GLD) did not list until late 2004.
- **Institutional Mitigation:** The 22-year common sample spans three profound crisis regimes: the 2008 Global Financial Crisis (systemic banking collapse), the March 2020 COVID shock (liquidity freeze), and the 2022 global rate-hiking cycle (joint stock-bond drawdown).

### 2. Price Imputation and Calendar Alignment
- **Core Assumption:** Forward-filling missing ETF prices up to a 3-day maximum resolves exchange holiday divergences without altering return volatility.
- **Vulnerability & Limitation:** Forward-filling artificially records zero daily returns on closed exchanges, dampening empirical variance.
- **Institutional Mitigation:** Our cleaning report (`data/clean/cleaning_report.json`) verifies that 0 days required forward-filling across the equity and commodity ETF series, as all components trade concurrently on synchronized US exchanges.

---

## 7.4 Layers 2 & 3: VaR and Expected Shortfall Modeling

### 1. Parametric Distributional Assumptions
- **Core Assumption:** Returns follow a parameterized analytical distribution (Gaussian or Student's $t$).
- **Vulnerability & Limitation:** Normal distributions dramatically underestimate tail kurtosis. At 99% confidence, Gaussian VaR understates daily portfolio downside by over \$24,000, and Expected Shortfall by nearly \$70,000 on a USD 10M base. Student's $t$ captures kurtosis but imposes tail symmetry, failing to model negative skewness during panics.
- **Institutional Mitigation:** We mandate that **Expected Shortfall (ES)** serve as the binding risk constraint rather than VaR alone. Expected Shortfall is a coherent, subadditive risk measure that penalizes tail clustering and severity.

### 2. Time-Horizon Scaling via $\sqrt{T}$
- **Core Assumption:** 1-day risk metrics can be extrapolated to 10-day or 20-day horizons by scaling by $\sqrt{T}$.
- **Vulnerability & Limitation:** Square-root-of-time scaling assumes that daily returns are independent and identically distributed (i.i.d.). In reality, volatility exhibits persistent autocorrelation (GARCH effects), and crash correlations compound non-linearly across multi-day horizons.
- **Institutional Mitigation:** Endowment multi-week liquidity reserves are sized against historical crisis drawdowns rather than scaled 1-day statistical quantiles.

---

## 7.5 Layer 4: Extreme Value Theory (EVT)

### 1. Asymptotic Threshold Selection
- **Core Assumption:** Portfolio loss exceedances above threshold $u$ adhere asymptotically to a Generalized Pareto Distribution (GPD).
- **Vulnerability & Limitation:** The Pickands-Balkema-de Haan theorem is an asymptotic limit theorem ($n \to \infty, u \to \infty$). In finite samples, setting $u$ too high leaves too few tail events for MLE stability, while setting $u$ too low violates GPD convergence.
- **Institutional Mitigation:** Threshold selection is substantiated by dual empirical diagnostics (Mean Excess linearity and Parameter Stability) anchored to the 90th percentile benchmark, providing 552 empirical crash observations for robust estimation.

### 2. Tail Stationarity
- **Core Assumption:** The tail index $\xi$ remains constant over time.
- **Vulnerability & Limitation:** Structural breaks, regulatory shifts, or algorithmic market microstructures can cause tail fatness to expand abruptly during novel shocks.
- **Institutional Mitigation:** EVT estimates are continuously backtested against out-of-sample data and validated against empirical crisis replays.

---

## 7.6 Layer 5: Backtesting and Model Validation

### 1. Statistical Power in Finite Horizons
- **Core Assumption:** Kupiec Proportion of Failures (POF) and Christoffersen independence tests provide definitive proof of model validity.
- **Vulnerability & Limitation:** At 99% confidence over a 250-day window, expected breaches are only 2.5 days. With so few observations, binomial tests suffer from low statistical power (Type II error), often failing to reject an inaccurate risk model.
- **Institutional Mitigation:** We conduct backtesting across the complete 22-year sample (over 5,000 days), assess sub-period performance during known market panics, and apply the Basel traffic-light classification framework.

---

## 7.7 Decision Layer: Stress Testing and Macro Scenarios

### 1. Historical Repeatability
- **Core Assumption:** Replaying the 2008 GFC (-50.6% equity peak-to-trough), March 2020 COVID shock (-33.7%), and 2022 rate hikes (-18.1% equity, -13.0% bonds) bounds plausible downside.
- **Vulnerability & Limitation:** Future crises will not replicate past market trajectories. Asset correlations that provided diversification historically can abruptly converge to unity.
- **Institutional Mitigation:** In addition to historical replays, we incorporate a synthetic **Stagflationary Inflation Shock** scenario where equities and fixed income decline simultaneously, directly exposing the structural failure mode of traditional 60/40 portfolios.

---

## 7.8 Summary Governance Checklist for Investment Committee

| Risk Dimension | Primary Vulnerability | Policy Action / Guardrail |
|---|---|---|
| **Liquidity & Execution** | Illiquid asset freezes during panics | 100% allocation in high-volume, liquid ETFs; minimum 30% AGG bond anchor |
| **Model Specification** | Gaussian underestimation of tail risk | Mandatory use of EVT GPD and Expected Shortfall for capital sizing |
| **Hedge Breakdown** | Stock-bond correlation flips positive | Inclusion of Gold (GLD) and Energy (XLE) as non-correlated inflation hedges |
| **Rebalancing Drag** | Transaction cost erosion from turnover | Rebalance quarterly on tolerance bands ($\pm 2.5\%$) rather than daily |
