# Y-O-W.github.io

My CV, served at **https://y-o-w.github.io**.

- `yw_cv_full-stack-developer.md` — the content (source of truth)
- `render_cv.py` + `*.css` + `fonts/` — renderer that turns the markdown into a
  styled HTML page and PDF
- `index.html` — the deployed page (HTML version, JetBrains Mono, self-contained)
- `yw_cv_full-stack-developer.pdf` — downloadable PDF (Inter, A4)

## Updating the CV

Edit the markdown, re-render, and push:

```bash
python3 render_cv.py yw_cv_full-stack-developer.md   # add --compact for 1-page PDF
cp yw_cv_full-stack-developer.html index.html
git add -A && git commit -m "Update CV" && git push
```

GitHub Pages serves the committed `index.html` (this is "Option A").

## Optional: auto-build (Option B)

`.github/workflows/deploy.yml` renders the CV on every push and deploys it, so
you only need to commit the markdown. To switch to it: repo **Settings → Pages →
Source → GitHub Actions**. After that you can stop committing `index.html`.

## First-time Pages setup

Settings → Pages → Build and deployment → Source: **Deploy from a branch** →
`main` / root. The site goes live at https://y-o-w.github.io within a minute or
two.

## Local dependencies

```bash
brew install pango gdk-pixbuf libffi
pip3 install weasyprint markdown
```
