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
