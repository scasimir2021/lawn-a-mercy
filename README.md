# Lawn-A-Mercy Landscaping — public website

Professional public site for Lawn-A-Mercy Landscaping in Lawrenceville,
Georgia. Plain HTML, CSS, and vanilla JavaScript; no compile step.

- Live: <https://scasimir2021.github.io/lawn-a-mercy/>
- Repository: <https://github.com/scasimir2021/lawn-a-mercy>
- Content: `data/site.json`
- Trio contract: `trio/CONTRACT.md`

## Preview

```powershell
python -m http.server 8080
```

Open <http://localhost:8080>.

## Validate

```powershell
python -m pip install -r tools/requirements.txt
python tools/trio_publish.py validate
node --check assets/js/site.js
git diff --check
```

## Content update

Use `tools/trio_update.py` for common JSON-backed changes:

```powershell
python tools/trio_update.py --instagram https://www.instagram.com/example/ --instagram-handle @example
python tools/trio_update.py --add-service --service "Seasonal cleanup"
```

Trio dashboard users choose **Quick Steer → Improve → Lawn public site**. The
worker edits and validates locally without committing. **Apps → Publish** is the separate public
confirmation that validates and pushes `main`.

## Work catalog

Project placeholders remain visible until real work is approved. Follow
`assets/work/README.md`. Never copy internal customer records or photos into
this public repository automatically.
