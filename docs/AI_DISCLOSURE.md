# AI disclosure

Each person adds a row for any AI tool they used on their part. The same
table goes into the report.

| Tool | Purpose | How we validated the output | Parts that were AI-assisted |
|---|---|---|---|
| Claude / Gemini Coding Assistant | Mathematical implementation of GPD POT formulas, Plotly visualizations, Streamlit test scaffolding | Unit testing against known synthetic GPD distributions (test_evt.py), manual formula verification against Pickands-Balkema-de Haan theorem, verification of monotonicity and subadditivity | Mathematical draft of closed-form POT VaR/ES in `src/evt.py`, interactive Plotly chart scaffolding in `app/pages/4_evt.py` |

| Claude (Anthropic) | Step by step coding help, web research on endowment return targets, and drafting of report section 2 | Ran every unit test, ruff and black locally and in the CI. Checked the 4.9%, 4.5%, 7.3% and 7.8% figures against the NACUBO-Commonfund summary and Mercer's summary of the study. Compared the report numbers with the app output. All changes went through pull requests | Draft code for the optimisers, KPI functions, minimum ES solver, XLK cap test and the Portfolio page (`src/portfolio.py`, `src/kpis.py`, `app/pages/2_portfolio.py`) and their tests. First draft of `docs/report/02_mandate_portfolio.md` |