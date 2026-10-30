# Serendib University Endowment Fund: Portfolio Tear Sheet

**Mandate:** USD 10,000,000 Capital Pool | **Recommended Portfolio:** Maximum Sharpe | **Sample:** Nov 2004 to Oct 2026 (5,518 days)

---

### 1. Asset Allocation & Mandate Weights

| Ticker | Asset Class / Fund Name | Target Weight | Capital (USD) | Mandate Limit | Status |
|---|---|---|---|---|---|
| **SPY** | US Large Cap Equities (S&P 500) | 9.55% | \$955,000 | Max 60% | Pass |
| **EFA** | Developed International Equities | 0.00% | \$0 | Max 20% | Pass |
| **EEM** | Emerging Market Equities | 0.00% | \$0 | Max 10% | Pass |
| **AGG** | US Aggregate Fixed Income (Core Anchor) | 58.85% | \$5,885,000 | Min 30%, Max 60% | Pass |
| **GLD** | SPDR Gold Shares (Inflation Hedge) | 15.00% | \$1,500,000 | Max 15% | Pass |
| **XLE** | Energy Select Sector | 1.60% | \$160,000 | Max 10% | Pass |
| **XLK** | Technology Select Sector | 15.00% | \$1,500,000 | Max 15% | Pass |
| **Total** | **Serendib Endowment Portfolio** | **100.00%** | **\$10,000,000** | **Long-only, No Leverage** | **Pass** |

---

### 2. Performance & Risk-Adjusted Summary

- **Annual Return:** **7.4% a year** (Meets endowment hurdle: spending 4.9% + inflation 2.5% = 7.4%; NACUBO average target is 7.3%).
- **Sharpe Ratio:** **0.79** (Highest risk-adjusted return across all candidate portfolios).
- **Annual Volatility:** **6.2%** (Conservative risk profile dominated by 58.85% core fixed income).
- **Maximum Drawdown:** **-18.3%** (Comparable to Minimum Variance at -17.8%, while generating +0.9% additional yield annually).

---

### 3. Tail Risk Metrics (1-Day Horizon on USD 10M Capital)

| Risk Framework | 95% 1-Day VaR | 95% 1-Day ES | 99% 1-Day VaR | 99% 1-Day ES | Tail Gap (ES - VaR) |
|---|---|---|---|---|---|
| **Parametric Normal (Gaussian)** | 0.71% (\$71,300) | 0.90% (\$90,100) | 1.02% (\$102,000) | 1.17% (\$117,300) | 0.15% (\$15,300) |
| **Historical Simulation** | 0.66% (\$66,200) | 1.02% (\$102,300) | 1.16% (\$116,300) | 1.73% (\$173,400) | 0.57% (\$57,100) |
| **Parametric Student-t** | 0.61% (\$60,600) | 0.98% (\$98,100) | **1.16% (\$115,700)** | **1.73% (\$172,600)** | 0.57% (\$56,900) |
| **Extreme Value Theory (EVT GPD)** | 0.65% (\$64,637) | 1.02% (\$102,200) | **1.22% (\$122,044)** | **1.73% (\$172,578)** | 0.51% (\$50,534) |

*Observation:* Normal models underestimate deep tail risk by \$55k+ at 99% ES. Daily risk monitoring is governed by Student-t and EVT.

---

### 4. Stress Testing & Crisis Scenario Losses

| Scenario | Nature | Period / Assumption | Portfolio Loss (%) | Capital Impact (USD) |
|---|---|---|---|---|
| **2008 Global Financial Crisis** | Historical Replay | 2007-10 to 2009-03 | -5.2% | -\$520,000 |
| **March 2020 COVID-19 Shock** | Historical Replay | 2020-02 to 2020-03 | -9.9% | -\$990,000 |
| **2022 Joint Rate Hiking Cycle** | Historical Replay | 2022-01 to 2022-12 | **-12.6%** | **-\$1,260,000** |
| **Stagflationary Inflation Shock** | Synthetic / Hypothetical | Equities -20%, Bonds -10%, Gold +10% | **-17.2%** | **-\$1,720,000** |

*Worst Historical Replay:* 2022 rate hikes (-12.6%), driven by simultaneous declines in equities and fixed income.

---

### 5. Risk Policy Limits & Committee Governance

| Governing Policy Limit | Mandated Limit Level | Final Portfolio Level | Compliance Status |
|---|---|---|---|
| **One-Day 99% Value at Risk (VaR)** | USD 150,000 (1.50%) | **USD 116,000 (1.16%)** | **Compliant (PASS)** |
| **One-Day 99% Expected Shortfall (ES)** | USD 200,000 (2.00%) | **USD 173,000 (1.73%)** | **Compliant (PASS)** |
| **Maximum Crisis Replay Loss** | USD 1,500,000 (15.00%) | **12.6% (USD 1,260,000)** | **Compliant (PASS)** |

**Committee Action Protocol:**  
- If persistent inflation materializes, rotate capital from XLK into XLE (each 1% shifted lowers inflation shock drawdown by ~0.35%).
- Maintain tolerance-band rebalancing ($\pm 2.5\%$) quarterly to eliminate daily transaction slippage.

