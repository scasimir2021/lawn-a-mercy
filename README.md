# Lawn-A-Mercy Landscaping — GitHub Pages + Trio

Plain HTML + CSS + vanilla JS. No build step.

## Preview
`python -m http.server 8080` then open http://localhost:8080

## Before printing QR codes
Set the permanent GitHub Pages URL and regenerate SVG QR files:
```bash
pip install -r tools/requirements.txt
python tools/trio_update.py --base-url https://YOUR_GITHUB_USERNAME.github.io/lawn-a-mercy
```

## Publish
Create a public `lawn-a-mercy` repo, push this folder, then GitHub Settings → Pages → Source: GitHub Actions. Workflow included.

## Trio updates
Everything important is in `data/site.json`. Example:
```bash
python tools/trio_update.py --phone 678-238-4010 --publish
```
For near-real-time changes, point `runtime.remote_config_url` at a public CORS-enabled Trio JSON endpoint. The browser polls it every 5 seconds.

## SVG swap points
- `assets/brand/logo.svg` — replace freely
- `assets/qr/*.svg` — vector QR files
- future service icons can also be individual SVGs

`assets/hero/crew-art.png` is the current raster crew art. It is intentionally isolated so we can later replace it with layered Steven/Nick/gear SVG or transparent PNG assets without touching the page layout.
