# Submission validation — 31 October 2026

Validated `fix/submission-audit`, starting at `d1ab425`, with the subsequent PDF equation-formatting corrections.

- Fresh Python 3.12 virtual environment: installed `requirements-dev.txt` and `requirements-report.txt` successfully. Playwright was installed separately for browser verification only.
- Clean checkout automated checks: 147 tests passed; Ruff passed; `pip check` found no broken requirements. One upstream Streamlit/Pandas deprecation warning remains.
- PDF build: `python scripts/build_report.py --pdf --strict` passed with 15 physical pages, including the cover. `python scripts/build_executive_pdfs.py` produced a one-page committee memo and one-page tear sheet.
- Visual review: reviewed report page layouts and the executive PDFs; corrected literal LaTeX in the EVT, stress and assumptions sections to PDF-compatible mathematical notation. The tear sheet is dense but fits on one page.
- Local browser smoke check: Home and all seven analysis pages loaded in Chromium without displayed Streamlit exceptions at the default settings. This checks page loading, not every control combination.
- Deployment verification remains outstanding: the configured proxy returned HTTP 403 to CONNECT for `nexora-serendib.streamlit.app`. This is an environment access restriction, not evidence of an application failure. Local tests cannot establish the deployed revision or production behavior.

Before submission, open the deployed URL from an allowed browser, confirm the merged revision, visit every page, and exercise confidence, method and date-range controls. Check that charts finish loading and no application exceptions appear.
