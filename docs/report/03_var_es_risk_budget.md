# Section 3: VaR, Expected Shortfall and risk budget

All estimates are one-day positive losses on USD 10m. VaR is a loss quantile; ES measures average loss beyond that quantile. ES is coherent under its population definition; finite-sample estimates remain uncertain. Historical daily VaR/ES are hard constraints in the final construction, while other models are independent monitoring estimates.

## 3.1 Methods and results

Historical simulation uses the empirical quantile and tail mean. Gaussian VaR/ES use the sample mean and variance; Student t fits degrees of freedom, location and scale. The original Monte Carlo samples that fitted portfolio-level t and is retained as a parametric reference. Its agreement with Student t is expected, not independent corroboration. The new joint ETF bootstrap instead samples entire seven-ETF return vectors before applying weights, preserving empirical contemporaneous dependence. Static estimates use 100,000 draws, seed 42. It is close to historical simulation by design, ignores serial dependence and cannot generate unseen crash regimes. GARCH-filtered alternatives are evaluated in Section 5.

| Confidence   | Model                  | VaR    | ES     |
|:-------------|:-----------------------|:-------|:-------|
| 95%          | Historical simulation  | 0.662% | 1.023% |
| 95%          | Parametric (normal)    | 0.713% | 0.901% |
| 95%          | Parametric (Student t) | 0.606% | 0.981% |
| 95%          | Monte Carlo            | 0.606% | 0.969% |
| 95%          | Joint ETF bootstrap    | 0.660% | 1.025% |
| 95%          | EVT / GPD              | 0.646% | 1.022% |
| 99%          | Historical simulation  | 1.163% | 1.734% |
| 99%          | Parametric (normal)    | 1.020% | 1.173% |
| 99%          | Parametric (Student t) | 1.157% | 1.726% |
| 99%          | Monte Carlo            | 1.152% | 1.674% |
| 99%          | Joint ETF bootstrap    | 1.169% | 1.735% |
| 99%          | EVT / GPD              | 1.220% | 1.726% |

To convert a decimal risk estimate into dollars, multiply by USD 10m. Across all new documents percentages use consistent rounding and dollar amounts are derived from full-precision estimates. Normal 99% ES is about USD 117,310 versus EVT USD 172,578: an approximate USD 55,268 gap. This is a model comparison, not an error bound. The dashboard shows grouped VaR/ES bars and a numeric table at the selected confidence.

## 3.2 Concentration and attribution

| ETF   | weight   | component_var   | component_es   | pct_es_contrib   |
|:------|:---------|:----------------|:---------------|:-----------------|
| SPY   | 9.55%    | 0.300%          | 0.376%         | 21.67%           |
| EFA   | 0.00%    | 0.000%          | 0.000%         | 0.00%            |
| EEM   | 0.00%    | 0.000%          | 0.000%         | 0.00%            |
| AGG   | 58.85%   | 0.266%          | 0.365%         | 21.04%           |
| GLD   | 15.00%   | 0.240%          | 0.277%         | 15.95%           |
| XLE   | 1.60%    | 0.060%          | 0.083%         | 4.80%            |
| XLK   | 15.00%   | 0.526%          | 0.634%         | 36.54%           |

Technology is only 15% of capital but about 36.5% of historical ES. Historical ES contributions sum to portfolio ES through tail conditional expectations. Historical component VaR is a local approximation around the empirical quantile and need not reconcile exactly; it must not be presented as exact Euler allocation. Parametric Gaussian contributions use Euler derivatives. A large bond weight reduces ordinary volatility but creates rate and correlation risk, as 2022 demonstrates. The mean tail contains only about 55 days at 99%, so concentration figures are imprecise.
