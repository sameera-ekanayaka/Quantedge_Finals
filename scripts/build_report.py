"""Stitch the numbered report sections into one report.

Owner: Sameera Ekanayaka

Usage:
    python scripts/build_report.py          # markdown only
    python scripts/build_report.py --pdf    # markdown and PDF
    python scripts/build_report.py --pdf --strict   # fail if outside 7-15 pages

The PDF needs the packages in requirements-report.txt. Outputs go to
build/report/, which is not committed.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "docs" / "report"
OUT_DIR = ROOT / "build" / "report"

TITLE = "Serendib University Endowment Fund"
SUBTITLE = "A conservative USD 10m portfolio and its risk"
TEAM = "Team Nexora"
MEMBERS = [
    "Imasha Karunathilaka",
    "Aadhila Anees",
    "Sameera Ekanayaka",
    "Praveen Madawalage",
    "Tharindu Dhanushka",
]

# Same order as docs/report/README.md
SECTIONS = [
    ("01_data.md", "Data"),
    ("02_mandate_portfolio.md", "Mandate and portfolio"),
    ("03_var_es_risk_budget.md", "VaR, ES and risk budget"),
    ("04_evt.md", "Extreme value theory"),
    ("05_backtesting.md", "Backtesting"),
    ("06_stress_tests.md", "Stress tests"),
    ("07_assumptions_limitations.md", "Assumptions and limitations"),
    ("08_committee_memo.md", "Committee memo"),
]

MIN_PAGES = 7
MAX_PAGES = 15
# Rough figure for 11pt text with some tables, used when there is no PDF
WORDS_PER_PAGE = 400

CSS = """
body { font-family: sans-serif; font-size: 11pt; line-height: 1.35; }
h1 { font-size: 17pt; margin-top: 18pt; }
h2 { font-size: 13pt; }
h3 { font-size: 11.5pt; }
table { border-collapse: collapse; font-size: 9.5pt; }
th, td { border: 1px solid #999; padding: 2pt 5pt; }
code { font-size: 9.5pt; }
"""

TITLE_CSS = """
body { font-family: sans-serif; text-align: center; }
h1 { font-size: 24pt; margin-top: 180pt; }
h2 { font-size: 15pt; font-weight: normal; }
p { font-size: 12pt; }
"""


def title_page(today: date) -> str:
    members = "<br>\n".join(MEMBERS)
    return (
        f"# {TITLE}\n\n"
        f"## {SUBTITLE}\n\n"
        f"**{TEAM}**\n\n"
        f"{members}\n\n"
        f"{today.strftime('%d %B %Y')}\n"
    )


def placeholder(number: int, name: str, title: str) -> str:
    return f"# Section {number}: {title}\n\nTODO: `{name}` has not been written yet.\n"


def collect_sections(report_dir: Path = REPORT_DIR) -> tuple[list[str], list[str]]:
    """Return the section texts in order and the names of missing files."""
    texts, missing = [], []
    for number, (name, title) in enumerate(SECTIONS, start=1):
        path = report_dir / name
        if path.exists() and path.read_text(encoding="utf-8").strip():
            texts.append(path.read_text(encoding="utf-8").strip() + "\n")
        else:
            texts.append(placeholder(number, name, title))
            missing.append(name)
    return texts, missing


def count_words(text: str) -> int:
    # Ignore table rules like |---|---| so they do not count as words
    return len([w for w in re.findall(r"\S+", text) if re.search(r"\w", w)])


def estimate_pages(text: str) -> float:
    return count_words(text) / WORDS_PER_PAGE


def build_pdf(title_md: str, body_md: str, path: Path, root: Path) -> int:
    """Write the PDF and return the number of body pages (title page left out)."""
    try:
        import pymupdf
        from markdown_pdf import MarkdownPdf, Section
    except ImportError:
        sys.exit("PDF needs: pip install -r requirements-report.txt")

    pdf = MarkdownPdf(toc_level=2)
    pdf.m_d.enable("table")
    pdf.add_section(Section(title_md, toc=False), user_css=TITLE_CSS)
    # One section for the body so sections flow on without blank half pages
    pdf.add_section(Section(body_md, root=str(root)), user_css=CSS)
    pdf.meta["title"] = TITLE
    pdf.meta["author"] = TEAM
    pdf.save(str(path))

    with pymupdf.open(str(path)) as doc:
        return doc.page_count - 1


def check_pages(pages: float) -> bool:
    return MIN_PAGES <= pages <= MAX_PAGES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pdf", action="store_true", help="also build the PDF")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit with an error if sections are missing or the length is off",
    )
    parser.add_argument("--out", type=Path, default=OUT_DIR, help="output folder")
    args = parser.parse_args(argv)

    texts, missing = collect_sections()
    title_md = title_page(date.today())
    body_md = "\n\n".join(texts)

    args.out.mkdir(parents=True, exist_ok=True)
    md_path = args.out / "report.md"
    md_path.write_text(title_md + "\n\n" + body_md, encoding="utf-8")
    print(f"Wrote {md_path}")

    if missing:
        print(f"Missing sections ({len(missing)}), marked TODO:")
        for name in missing:
            print(f"  - {name}")

    if args.pdf:
        pdf_path = args.out / "report.pdf"
        pages = build_pdf(title_md, body_md, pdf_path, REPORT_DIR)
        print(f"Wrote {pdf_path.name}: {pages} pages plus the title page")
    else:
        pages = estimate_pages(body_md)
        print(f"About {pages:.1f} pages (estimate, use --pdf for the real count)")

    if check_pages(pages):
        print(f"Length OK: inside the {MIN_PAGES} to {MAX_PAGES} page limit")
    elif pages < MIN_PAGES:
        print(f"Too short: the brief asks for at least {MIN_PAGES} pages")
    else:
        print(f"Too long: the brief allows at most {MAX_PAGES} pages")

    if args.strict and (missing or not check_pages(pages)):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
