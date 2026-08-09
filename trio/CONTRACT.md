# Trio public-site contract

## Two different Lawn-A-Mercy apps

| Target | Purpose | Source | Deployment |
|---|---|---|---|
| `lawn-a-mercy` | Private clients, jobs, invoices, schedules, photos | `C:/trio/Projects/lawn_a_mercy` | pc-black `:4080`, systemd `lawn-care` |
| `lawn-a-mercy-public` | Public marketing, services, social links, approved work catalog | this repository | GitHub Pages from `scasimir2021/lawn-a-mercy:main` |

Ambiguous words must not cross the boundary. Website, social, SEO, gallery,
catalog, or public copy means `lawn-a-mercy-public`. Client, invoice, job,
prospect, schedule, or customer photo means the private manager.

## Content source

The page renders from `data/site.json`. Ordinary copy, phone, service, social,
and approved catalog changes should not require HTML edits. The stable public
URL is `https://scasimir2021.github.io/lawn-a-mercy/`.

`runtime.remote_config_url` stays empty in GitHub-only mode. A future remote
config must be public HTTPS, CORS-enabled, validated, and must never expose the
dashboard, private manager, or customer database.

## Trio Change UI flow

1. Choose **Improve → Lawn public site** in Quick Steer.
2. Trio dispatches Codex on dev-desktop with this repo as project root.
3. Worker edits only this repo and validates locally without committing.
4. Worker does **not** commit or push.
5. Apps → Publish shows exact pending files and revision.
6. Operator confirms the public deployment.
7. `tools/trio_publish.py` refuses stale revisions, unexpected paths, remote
   divergence, invalid content, and unapproved gallery images; then pushes.
8. GitHub Pages deploys and Trio reports the Actions/live URLs.

## Permanent QR routing

Printed QR codes route through `/go/`. `assets/qr/socials.svg` points to
`/go/?to=socials`, which reads current config and displays active profiles.
Social destinations can change without reprinting as long as the base URL and
`/go/` route remain stable.

`assets/qr/website.svg` points to `/go/?to=website`, which resolves through
`routes.website` to the canonical homepage. The public `/qr/` page displays
both official codes, their full destinations, and downloadable PNG copies.
Keep the website route under the public GitHub Pages origin; never route a
printed code into Trio's private apps.

## Public-image rule

Never auto-export internal photos. Public images belong in `assets/work/` only
after Steven approves both image and copy. Strip location metadata. Each live
portfolio item requires:

```json
{
  "image": "assets/work/example.webp",
  "approved_for_public": true,
  "published": true
}
```

Rollback uses `git revert <commit>` in this standalone repo followed by the
same confirmed publish flow. Never use force-push or destructive reset.

## Permanent social hub

`https://scasimir2021.github.io/lawn-a-mercy/go/?to=socials`

Printed QR codes encode this URL and nothing else. `routes.socials` must keep
pointing at it unless there is a deliberate, reprint-funded migration.

## Safe mutable fields

Trio may change these without review:

- `brand.*` copy
- `contact.phone`, `contact.email`, service area
- `social.*` and `social_handles.*`
- `services[]`
- `theme.*` approved hex colors

## Remote config limits

A partial JSON override may be pulled from `runtime.remote_config_url`. The
endpoint must be HTTPS and CORS-enabled, the poll interval must be at least 5
seconds, and a failed fetch keeps the last known good config rather than
blanking the page. Never put secrets or tokens into browser-fetched JSON.

## Character asset

`assets/hero/crew-approved.svg` is an SVG control shell around the approved
advertisement artwork. The PNG inside preserves facial likeness better than
automated vector tracing. Trio may scale or reposition this SVG but must not
regenerate the people unless explicitly asked.
