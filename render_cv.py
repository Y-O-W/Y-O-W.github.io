#!/usr/bin/env python3
"""Render markdown CVs to styled PDF (Inter) and/or HTML (JetBrains Mono).

Usage:
    python3 render_cv.py pdf path/to/cv.md [--compact]
    python3 render_cv.py html yw_cv_full-stack-developer.md
    python3 render_cv.py both yw_cv_full-stack-developer.md [--compact]

- PDF uses Inter (sans-serif), single-column, ATS-friendly.
- HTML uses JetBrains Mono (monospace), dark theme, fonts embedded as base64
  so the file is fully self-contained and portable. Always writes index.html.
- A {{DATE}} token anywhere in the markdown is replaced with today's date
  in US format (M/D/YYYY) at render time.

Paths are resolved relative to this script, so you can run it from anywhere.
"""
import sys, os, base64, argparse
from datetime import date
import markdown
from weasyprint import HTML, CSS

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


def _load_md(md_path):
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    today = date.today()
    text = text.replace("{{DATE}}", f"{today.month}/{today.day}/{today.year}")
    return markdown.markdown(text, extensions=["extra", "sane_lists"])


def render_pdf(md_path, compact=False):
    base = os.path.splitext(md_path)[0]
    html_body = _load_md(md_path)
    pdf_css = PDF_CSS_COMPACT if compact else PDF_CSS
    doc = (f"<!DOCTYPE html><html><head><meta charset='utf-8'></head>"
           f"<body>{html_body}</body></html>")
    HTML(string=doc, base_url=HERE).write_pdf(
        f"{base}.pdf", stylesheets=[CSS(filename=pdf_css, base_url=HERE)])
    print(f"Rendered {base}.pdf")


def render_html(md_path):
    html_body = _load_md(md_path)
    base = os.path.splitext(md_path)[0]
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
    print(f"Rendered {html_out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Render markdown CVs to PDF and/or HTML.")
    ap.add_argument("command", choices=["pdf", "html", "both"],
                    help="what to render: pdf, html, or both")
    ap.add_argument("file", help="markdown file to render")
    ap.add_argument("--compact", action="store_true",
                    help="use the tightened single-page A4 PDF layout (pdf/both only)")
    args = ap.parse_args()

    if args.command in ("pdf", "both"):
        render_pdf(args.file, compact=args.compact)
    if args.command in ("html", "both"):
        render_html(args.file)
