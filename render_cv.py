#!/usr/bin/env python3
"""Render markdown CVs to styled PDF (Inter) and/or HTML (JetBrains Mono).

Usage:
    python3 render_cv.py pdf path/to/cv.md [--compact]
    python3 render_cv.py html yw_cv_full-stack-developer.md
    python3 render_cv.py both yw_cv_full-stack-developer.md [--compact]
    python3 render_cv.py all [--compact]

- PDF uses Inter (sans-serif), single-column, ATS-friendly.
- HTML uses JetBrains Mono (monospace), dark theme.
  Fonts embedded as base64 so the file is fully self-contained.
  Always writes index.html.
- A {{DATE}} token anywhere in the markdown is replaced with
  today's date in US format (M/D/YYYY) at render time.
- `all` renders every CV artifact at once: PDF + HTML for
  yw_cv_full-stack-developer.md, and PDF only for
  yw_cv_technical-consultant.md, yw_cv_full-stack-entwickler.md,
  and yw_cv_digitalisierungs-berater.md.

Paths are resolved relative to this script, so you can run it
from anywhere.
"""
import argparse
import base64
import os
import sys
from datetime import date

import markdown
from weasyprint import CSS
from weasyprint import HTML

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

ALL_TARGETS = [
    ("yw_cv_full-stack-developer.md", "both"),
    ("yw_cv_technical-consultant.md", "pdf"),
    ("yw_cv_full-stack-entwickler.md", "pdf"),
    ("yw_cv_digitalisierungs-berater.md", "pdf"),
]

WEB_FONTS_CACHE = {}


def _validate_path(path: str, allowed_dir: str = HERE) -> str:
    """Validate path is within allowed directory and exists."""
    resolved = os.path.abspath(os.path.realpath(path))
    allowed = os.path.abspath(allowed_dir)
    if not resolved.startswith(allowed + os.sep):
        raise ValueError(
            f"Path '{path}' resolves outside allowed directory "
            f"'{allowed}'"
        )
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"File not found: {path}")
    return resolved


def _load_md(md_path: str) -> str:
    """Load and process markdown file."""
    validated_path = _validate_path(md_path)
    with open(validated_path, encoding="utf-8") as f:
        text = f.read()

    today = date.today()
    date_str = f"{today.month}/{today.day}/{today.year}"
    text = text.replace("{{DATE}}", date_str)

    return markdown.markdown(
        text, extensions=["extra", "sane_lists"]
    )


def _get_b64_font(fname: str) -> str:
    """Get base64-encoded font, using cache."""
    if fname not in WEB_FONTS_CACHE:
        fpath = _validate_path(os.path.join(FONT_DIR, fname))
        with open(fpath, "rb") as f:
            WEB_FONTS_CACHE[fname] = base64.b64encode(f.read()).decode()
    return WEB_FONTS_CACHE[fname]


def render_pdf(md_path: str, compact: bool = False) -> bool:
    """Render markdown to PDF.

    Returns:
        True if successful, False otherwise.
    """
    try:
        md_path = _validate_path(md_path)
        base = os.path.splitext(md_path)[0]
        html_body = _load_md(md_path)
        pdf_css = PDF_CSS_COMPACT if compact else PDF_CSS

        doc = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'></head>"
            f"<body>{html_body}</body></html>"
        )
        HTML(string=doc, base_url=HERE).write_pdf(
            f"{base}.pdf",
            stylesheets=[CSS(filename=pdf_css, base_url=HERE)]
        )
        print(f"Rendered {base}.pdf")
        return True
    except Exception as e:
        print(f"Error rendering PDF: {e}", file=sys.stderr)
        return False


def render_html(md_path: str) -> bool:
    """Render markdown to HTML with embedded fonts.

    Returns:
        True if successful, False otherwise.
    """
    try:
        md_path = _validate_path(md_path)
        base = os.path.splitext(md_path)[0]

        with open(WEB_CSS, encoding="utf-8") as f:
            web_css = f.read()

        for fname in WEB_FONTS:
            b64 = _get_b64_font(fname)
            web_css = web_css.replace(
                f"url('fonts/{fname}')",
                f"url(data:font/woff2;base64,{b64})"
            )

        html_out = os.path.join(
            os.path.dirname(md_path) or ".", "index.html"
        )
        full_html = (
            f"<!DOCTYPE html><html lang='en'><head>"
            f"<meta charset='utf-8'>"
            f"<meta name='viewport' "
            f"content='width=device-width, initial-scale=1'>"
            f"<title>{os.path.basename(base)}</title>"
            f"<style>{web_css}</style></head>"
            f"<body>{_load_md(md_path)}</body></html>"
        )

        with open(html_out, "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"Rendered {html_out}")
        return True
    except Exception as e:
        print(f"Error rendering HTML: {e}", file=sys.stderr)
        return False


def render_all(compact: bool = False) -> bool:
    """Render all CV artifacts.

    Returns:
        True if all renders succeeded, False otherwise.
    """
    success = True
    for fname, command in ALL_TARGETS:
        md_path = os.path.join(HERE, fname)
        if command in ("pdf", "both"):
            if not render_pdf(md_path, compact=compact):
                success = False
        if command in ("html", "both"):
            if not render_html(md_path):
                success = False
    return success


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Render markdown CVs to PDF and/or HTML."
    )
    ap.add_argument(
        "command",
        choices=["pdf", "html", "both", "all"],
        help="what to render: pdf, html, both, or all (every CV artifact)"
    )
    ap.add_argument(
        "file",
        nargs="?",
        help="markdown file to render (omit for 'all')"
    )
    ap.add_argument(
        "--compact",
        action="store_true",
        help="use the tightened single-page A4 PDF layout "
        "(pdf/both/all only)"
    )
    args = ap.parse_args()

    if args.command == "all":
        success = render_all(compact=args.compact)
        sys.exit(0 if success else 1)
    else:
        if not args.file:
            ap.error("the 'file' argument is required for pdf/html/both")

        md_path = os.path.join(HERE, args.file)
        if args.command in ("pdf", "both"):
            if not render_pdf(md_path, compact=args.compact):
                sys.exit(1)
        if args.command in ("html", "both"):
            if not render_html(md_path):
                sys.exit(1)
