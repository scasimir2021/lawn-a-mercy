# Lawn-A-Mercy public website — agent rules

This standalone nested Git repository is the PUBLIC marketing site. It is not
the internal Lawn-A-Mercy manager.

## Identity and boundaries

- Public source: `C:/trio/Projects/lawn_a_mercy_public`
- Public repo: `scasimir2021/lawn-a-mercy`, branch `main`
- Live URL: `https://scasimir2021.github.io/lawn-a-mercy/`
- Internal manager source: `C:/trio/Projects/lawn_a_mercy`
- Internal live app: pc-black `:4080`, systemd `lawn-care`

Never read or copy internal clients, addresses, invoices, notes, schedules,
database files, or customer photos into this repository. A portfolio image may
ship only after Steven explicitly approves it and its config item has both
`approved_for_public: true` and `published: true`.

## Editing

- Content, social URLs, services, and portfolio metadata live in
  `data/site.json`.
- Layout lives in `index.html`, `assets/css/site.css`, and
  `assets/js/site.js`.
- Permanent QR routing lives under `go/`; printed QR destinations must remain
  stable.
- The complete-site QR uses `/go/?to=website`; `/qr/` is the public printable
  page for website and social codes plus downloadable PNG copies.
- Keep `runtime.remote_config_url` empty unless a reviewed public HTTPS+CORS
  config service exists. Never point it at the private manager or dashboard.

Validate every change:

```powershell
python tools/trio_publish.py validate
node --check assets/js/site.js
git diff --check
```

Trio Change UI workers edit and validate this repo but do not commit or push.
Apps → Publish is the separate operator-confirmed public deployment gate.
Never force-push, reset, merge remote divergence automatically, or stage files
outside the allowlist in `tools/trio_publish.py`.
