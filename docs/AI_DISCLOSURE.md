# AI disclosure

Each person adds a row for any AI tool they used on their part. The same
table goes into the report.

| Tool | Purpose | How we validated the output | Parts that were AI-assisted |
|---|---|---|---|
| Claude / Gemini Coding Assistant | Mathematical implementation of GPD POT formulas, Plotly visualizations, Streamlit test scaffolding | Unit testing against known synthetic GPD distributions (test_evt.py), manual formula verification against Pickands-Balkema-de Haan theorem, verification of monotonicity and subadditivity | Mathematical draft of closed-form POT VaR/ES in `src/evt.py`, interactive Plotly chart scaffolding in `app/pages/4_evt.py` |
