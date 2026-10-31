# Replacement-submission validation — 31 October 2026

Final decision: **ADJUST scenario-loss limit to 18%, retaining the original allocation**. This limit was selected after examining results and is not independently calibrated. It applies to five tested scenario losses, not maximum drawdown.

The final construction enforces full investment, original asset bounds, 99% historical daily VaR ≤ 1.5%, historical ES ≤ 2.0% and each scenario loss ≤ 18%. Both the solver output and frozen rounded targets pass independent constraint checks. The original PDF is archived separately; current sources integrate the audit response, walk-forward validation, GARCH models, joint ETF bootstrap, EVT sensitivity and intervals, policy benchmark and second scenario.

157 tests passed, including construction and rounded-target feasibility, conditional forecast prefix invariance and the extended page at all three confidence levels. Ruff and Black formatting are checked. PDF generation enforces 7–15 report pages including cover and exactly one page each for memo and tear sheet. Visual review covers page layouts, tables and formulas.

Research limitations remain explicit: Maximum Sharpe does not beat Minimum variance on walk-forward Sharpe; all compared models reject independence; the retained maximum drawdown exceeds 18%; stress/threshold assumptions and IID bootstrap limitations persist. These outcomes are not represented as cured by adding models.

Production verification remains required after merge. This environment cannot reach the Streamlit host through its configured network policy. Local browser and AppTest checks do not establish the deployed revision. Open every page, exercise confidence/method/date controls, check the 18% default scenario limit and verify the Extended validation page after deployment. Reboot Streamlit if stale imports appear.

Final packaging: report 10 physical pages including cover; memo 1 page; tear sheet 1 page. The final comparison includes all original risk-model backtests plus the three model extensions on common dates. The main Risk/EVT pages passed all 24 confidence/method combinations. A fresh local browser loaded Portfolio, Risk, EVT, Stress and Extended validation without displayed exceptions and confirmed the scenario slider default is 0.18. Earlier-submission PDF hashes were verified before archiving; current files have new checksums.
