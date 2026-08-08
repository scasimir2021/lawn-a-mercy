# Trio live-update contract

The page renders from `data/site.json`; ordinary updates do not require HTML edits.

## GitHub-only mode
Trio edits JSON and runs `python tools/trio_update.py --publish`. GitHub Pages redeploys.

## Near-real-time mode
Set `runtime.remote_config_url` to a public CORS-enabled JSON endpoint controlled by Trio. The page polls every `runtime.poll_seconds` (default 5 seconds) and falls back to the GitHub copy if the endpoint is offline.

## Permanent QR routing
Print `assets/qr/socials.svg`. It routes to `/go/?to=socials`, which reads the current config. Change TikTok/Instagram/LinkedIn later without reprinting the QR as long as the GitHub Pages base URL stays the same. Direct routes: `?to=instagram`, `?to=tiktok`, `?to=linkedin`, `?to=call`.
