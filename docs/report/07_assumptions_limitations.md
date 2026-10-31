# Section 7: Assumptions and Limitations

**Owner:** Praveen Madawalage  
**Mandate:** USD 10m Serendib University Endowment Fund | **Status:** Model Risk Governance

Quantitative risk models are simplifications of non-stationary financial markets. The Serendib Endowment mandate instructs that avoiding large losses takes priority over maximizing returns. Fulfilling this duty requires transparency regarding model limits and how we govern them.

## 7.1 Layer-by-Layer Assumptions and Mitigations

### 1. Portfolio Construction (Layers 0 & 1)
- **Costless Daily Rebalancing:** Models assume continuous rebalancing without transaction friction.  
  *Mitigation:* The endowment implements calendar-quarter rebalancing to target weights.
- **Stationarity of Return Moments:** Covariances over 2004-2026 are assumed representative. Macro regime shifts alter distributions.  
  *Mitigation:* We enforce strict structural mandate bounds: a 30% floor on US Aggregate Bonds (AGG) and single-asset caps (GLD 15%, XLK 15%, XLE 10%).

### 2. Data Pipeline & Cleaning (Layer 1)
- **Sample Horizon (Nov 2004 to Oct 2026):** Starting on 19 Nov 2004 (GLD inception) omits the 2000-2002 dot-com crash.  
  *Mitigation:* The 22-year common sample (5,518 days) spans three major crises: 2008 GFC, March 2020 COVID, and 2022 rate hikes.
- **Calendar Alignment:** Forward-filling missing prices up to 3 days could dampen volatility.  
  *Mitigation:* The audit (`data/clean/cleaning_report.json`) confirms 0 days required fill across our liquid ETF universe.

### 3. Tail Risk Modeling (Layers 2, 3 & 4)
- **Distributional Assumptions:** Normal models assume thin tails, severely understating tail losses (Normal 99% ES is USD 117k vs. USD 173k Historical/EVT, a USD 56k blindspot). Student-t assumes tail symmetry.  
  *Mitigation:* We mandate Expected Shortfall (coherent, subadditive) as the binding constraint.
- **Square-Root-of-Time Scaling ($\sqrt{T}$):** Extrapolating 1-day risk to multi-day horizons assumes i.i.d. returns, ignoring volatility clustering.  
  *Mitigation:* Multi-week reserves are calibrated directly against empirical crisis drawdowns.
- **EVT Asymptotic Validity:** GPD is an asymptotic limit theorem ($n \to \infty, u \to \infty$).  
  *Mitigation:* Threshold $u = 0.45\%$ (90th percentile) provides 552 observations, verified by Mean Excess linearity, parameter stability within $\pm 2\text{ SE}$, and Q-Q diagnostics.

### 4. Backtesting and Validation (Layer 5)
- **Binomial Test Power in Finite Samples:** At 99% confidence over 250 days, expected breaches are only 2.5 days, giving Kupiec tests low power to detect underestimation (Type II error).  
  *Mitigation:* We backtest over the full 22-year history (5,518 days; with the 500-day estimation window, the out-of-sample forecast count is approximately 5,018 days), combine coverage with independence tests, and monitor Basel traffic lights.

### 5. Stress Testing and Macro Scenarios (Decision Layer)
- **Crisis Repeatability & Hedge Breakdown:** Past drawdowns may not repeat. In 2022, stocks and bonds fell concurrently.  
  *Mitigation:* We test a synthetic Stagflation Shock. XLE performed well during the 2022 inflation episode (+64%), but we do not assume that result will repeat (Section 2 treats one-year energy performance as unreliable). The inflation scenario assigns XLE a 0% shock, reflecting our conservative stance. Gold (GLD, -0.8% in 2022) is resilient in equity crashes but constrained by real rates. Protocol: rotate XLK into XLE if inflation accelerates.

## 7.2 Governance Checklist for Investment Committee

| Risk Dimension | Model Vulnerability | Institutional Defense / Guardrail |
|---|---|---|
| **Execution Drag** | Transaction friction from turnover | Calendar-quarter rebalancing to target weights |
| **Model Misspecification** | Gaussian tail undercounting | Mandatory use of EVT GPD and Expected Shortfall for sizing |
| **Hedge Breakdown** | Stock-bond correlation flips positive | Dedicated inflation stress test; protocol to rotate XLK into XLE |
| **Horizon Extrapolation** | $\sqrt{T}$ scaling underestimates clustering | Sizing multi-week liquidity buffers on empirical stress drawdowns |
