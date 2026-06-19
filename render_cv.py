#!/usr/bin/env python3
"""Render markdown CVs to styled PDF (Inter) and HTML (JetBrains Mono).

Usage:
    python3 render_cv.py path/to/cv.md [more.md ...]

For each input it writes <name>.pdf and <name>.html next to the source.

- PDF uses Inter (sans-serif), single-column, ATS-friendly.
- HTML uses JetBrains Mono (monospace), dark theme, fonts embedded as base64
  so the file is fully self-contained and portable.
- A {{DATE}} token anywhere in the markdown is replaced with today's date
  in US format (M/D/YYYY) at render time.

Paths are resolved relative to this script, so you can run it from anywhere.
"""
import sys, os, base64, argparse
from datetime import date
import markdown
from weasyprint import HTML, CSS, default_url_fetcher

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
PDF_CSS = os.path.join(HERE, "pdf-inter.css")
PDF_CSS_COMPACT = os.path.join(HERE, "pdf-inter-compact.css")
WEB_CSS = os.path.join(HERE, "web-jetbrains.css")

WEB_FONTS = [
    "jetbrains-mono-latin-400-normal.woff2",
    "jetbrains-mono-latin-400-italic.woff2",
    "jetbrains-mono-latin-700-normal.woff2",
]


def render(md_path, compact=False):
    base = os.path.splitext(md_path)[0]
    with open(md_path, encoding="utf-8") as f:
        md_text = f.read()

    today = date.today()
    us_date = f"{today.month}/{today.day}/{today.year}"
    md_text = md_text.replace("{{DATE}}", us_date)

    html_body = markdown.markdown(md_text, extensions=["extra", "sane_lists"])

    # --- PDF (Inter) ---
    # base_url=HERE lets the @font-face url('fonts/..') refs resolve to the
    # bundled woff2 files regardless of where you run the script from.
    pdf_css = PDF_CSS_COMPACT if compact else PDF_CSS
    pdf_doc = (f"<!DOCTYPE html><html><head><meta charset='utf-8'></head>"
               f"<body>{html_body}</body></html>")
    HTML(string=pdf_doc, base_url=HERE).write_pdf(
        f"{base}.pdf", stylesheets=[CSS(filename=pdf_css, base_url=HERE)])

    # --- HTML (JetBrains Mono, self-contained) ---
    with open(WEB_CSS, encoding="utf-8") as f:
        web_css = f.read()
    for fname in WEB_FONTS:
        fpath = os.path.join(FONT_DIR, fname)
        with open(fpath, "rb") as ff:
            b64 = base64.b64encode(ff.read()).decode()
        web_css = web_css.replace(
            f"url('fonts/{fname}')",
            f"url(data:font/woff2;base64,{b64})")
    html_out = os.path.join(os.path.dirname(md_path) or ".", "index.html")
    full_html = (f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
                 f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
                 f"<title>{os.path.basename(base)}</title><style>{web_css}</style></head>"
                 f"<body>{html_body}</body></html>")
    with open(html_out, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Rendered {base}.pdf and {html_out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Render markdown CVs to PDF + HTML.")
    ap.add_argument("files", nargs="+", help="markdown file(s) to render")
    ap.add_argument("--compact", action="store_true",
                    help="use the tightened single-page A4 PDF layout")
    args = ap.parse_args()
    for path in args.files:
        render(path, compact=args.compact)
