# Y-O-W.github.io

My CV, served at **https://y-o-w.github.io**.

| File | Purpose |
|------|---------|
| `yw_cv_full-stack-developer.md` | CV content (source of truth) |
| `render_cv.py` | Renders the markdown into a styled HTML page and PDF |
| `pdf-inter.css` / `pdf-inter-compact.css` | PDF styling (Inter, A4) |
| `web-jetbrains.css` | HTML styling (JetBrains Mono, dark theme) |
| `fonts/` | Bundled Inter and JetBrains Mono `.woff2` files |
| `index.html` | Deployed page — self-contained, fonts embedded as base64 |
| `yw_cv_full-stack-developer.pdf` | Downloadable PDF |

## Local setup

Requires Python 3 and a few system libraries for PDF rendering:

```bash
brew install pango gdk-pixbuf libffi
python3 -m venv .venv
source .venv/bin/activate
pip install weasyprint markdown
```

## Updating the CV

Edit the markdown, re-render, and push:

```bash
source .venv/bin/activate
python3 render_cv.py yw_cv_full-stack-developer.md   # add --compact for a single-page A4 PDF
cp yw_cv_full-stack-developer.html index.html
git add -A && git commit -m "Update CV" && git push
```

A `{{DATE}}` token in the markdown is replaced with today's date (M/D/YYYY) at render time.

GitHub Pages serves the committed `index.html`.

## Optional: CI auto-build

`.github/workflows/deploy.yml` renders the CV on every push and deploys via GitHub Actions. To enable:

1. Go to repo **Settings → Pages → Source → GitHub Actions**.
2. Commit only the markdown — the workflow handles the rest.

Once enabled, you no longer need to commit `index.html` or the PDF.

## GitHub Pages setup

Settings → Pages → Build and deployment → Source: **Deploy from a branch** → `main` / root. The site goes live at https://y-o-w.github.io within a couple of minutes.
