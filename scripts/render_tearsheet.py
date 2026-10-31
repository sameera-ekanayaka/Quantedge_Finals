"""Render docs/tearsheet.md to a single-page HTML tear sheet.

Usage:
    python scripts/render_tearsheet.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs" / "tearsheet.md"
HTML_PATH = ROOT / "docs" / "tearsheet.html"


def md_to_html(md_text: str) -> str:
    lines = md_text.strip().splitlines()
    html_lines = []
    in_table = False
    in_ul = False

    for line in lines:
        stripped = line.strip()

        # Horizontal rule
        if stripped == "---":
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            html_lines.append("<hr>")
            continue

        # Header 1
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{stripped[2:]}</h1>")
            continue

        # Header 3
        if stripped.startswith("### "):
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
            continue

        # Table row
        if stripped.startswith("|") and stripped.endswith("|"):
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False

            cells = [c.strip() for c in stripped[1:-1].split("|")]
            # Check if separator row
            if all(re.match(r"^:?-+:?$", c) for c in cells):
                continue

            if not in_table:
                in_table = True
                html_lines.append("<table><thead><tr>")
                for c in cells:
                    bold_c = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", c)
                    html_lines.append(f"<th>{bold_c}</th>")
                html_lines.append("</tr></thead><tbody>")
            else:
                html_lines.append("<tr>")
                for c in cells:
                    c_clean = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", c)
                    c_clean = c_clean.replace(r"\$", "$")
                    html_lines.append(f"<td>{c_clean}</td>")
                html_lines.append("</tr>")
            continue

        # If we exited a table
        if in_table and not (stripped.startswith("|") and stripped.endswith("|")):
            html_lines.append("</tbody></table>")
            in_table = False

        # Unordered list
        if stripped.startswith("- "):
            if not in_ul:
                in_ul = True
                html_lines.append("<ul>")
            content = stripped[2:]
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
            content = re.sub(r"\*(.*?)\*", r"<em>\1</em>", content)
            content = content.replace(r"\$", "$")
            html_lines.append(f"<li>{content}</li>")
            continue

        if in_ul and not stripped.startswith("- "):
            html_lines.append("</ul>")
            in_ul = False

        # Paragraphs or empty lines
        if stripped == "":
            continue

        p_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", stripped)
        p_text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", p_text)
        p_text = p_text.replace(r"\$", "$")
        html_lines.append(f"<p>{p_text}</p>")

    if in_table:
        html_lines.append("</tbody></table>")
    if in_ul:
        html_lines.append("</ul>")

    body_html = "\n".join(html_lines)

    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Serendib University Endowment Fund: Portfolio Tear Sheet</title>
<style>
  @page {{
    size: letter portrait;
    margin: 0.35in 0.4in;
  }}
  * {{
    box-sizing: border-box;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
      Roboto, Arial, sans-serif;
    color: #1a1a1a;
    background: #fff;
    margin: 0 auto;
    padding: 0;
    max-width: 8.2in;
    font-size: 8.2pt;
    line-height: 1.25;
  }}
  h1 {{
    font-size: 13pt;
    font-weight: 700;
    color: #0f2537;
    margin: 0 0 2pt 0;
    letter-spacing: -0.2px;
  }}
  h3 {{
    font-size: 8.8pt;
    font-weight: 700;
    color: #1b365d;
    margin: 4pt 0 2pt 0;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    border-bottom: 1.5px solid #1b365d;
    padding-bottom: 1pt;
  }}
  p {{
    margin: 2pt 0;
  }}
  hr {{
    border: 0;
    border-top: 1px solid #d0d7de;
    margin: 3pt 0;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 2pt 0 4pt 0;
    font-size: 7.8pt;
  }}
  th, td {{
    border: 1px solid #d0d7de;
    padding: 2pt 4pt;
    text-align: left;
  }}
  th {{
    background-color: #f6f8fa;
    color: #24292f;
    font-weight: 600;
  }}
  tr:nth-child(even) {{
    background-color: #fcfcfc;
  }}
  ul {{
    margin: 2pt 0 4pt 0;
    padding-left: 12pt;
  }}
  li {{
    margin-bottom: 1pt;
  }}
  strong {{
    color: #0f2537;
  }}
</style>
</head>
<body>
{body_html}
</body>
</html>
"""
    return template


def main():
    if not MD_PATH.exists():
        raise FileNotFoundError(f"Missing {MD_PATH}")
    md = MD_PATH.read_text(encoding="utf-8")
    html_out = md_to_html(md)
    HTML_PATH.write_text(html_out, encoding="utf-8")
    print(f"Rendered tear sheet to {HTML_PATH}")


if __name__ == "__main__":
    main()
