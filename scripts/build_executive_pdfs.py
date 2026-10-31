"""Build and enforce single-page executive PDFs from the submission sources."""

from pathlib import Path

import pymupdf
from markdown_pdf import MarkdownPdf, Section

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "report"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, source, size in [
        ("committee_memo", "docs/report/08_committee_memo.md", 10),
        ("tearsheet", "docs/tearsheet.md", 8),
    ]:
        pdf = MarkdownPdf(toc_level=0)
        pdf.m_d.enable("table")
        css = (
            "@page {margin:12mm;} "
            f"body {{font-size:{size}pt;line-height:1.1;}} "
            "table {font-size:8pt;} h1 {font-size:14pt;} "
            "h2,h3 {font-size:11pt;}"
        )
        pdf.add_section(Section((ROOT / source).read_text(), toc=False), user_css=css)
        target = OUT / f"{name}.pdf"
        pdf.save(str(target))
        with pymupdf.open(target) as doc:
            if len(doc) != 1:
                raise ValueError(f"{name} must be one page; got {len(doc)}")
        print(f"{target}: one page")


if __name__ == "__main__":
    main()
