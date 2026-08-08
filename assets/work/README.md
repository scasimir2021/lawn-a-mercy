# Public work catalog

Only place operator-approved public images here. Never copy customer photos,
names, addresses, notes, EXIF location data, or internal Lawn-A-Mercy records
into this directory automatically.

For each approved project:

1. Remove location metadata from the image.
2. Use a neutral filename such as `mowing-cleanup-2026-08-01.webp`.
3. Add a matching item to `data/site.json` under `portfolio.items`.
4. Set `approved_for_public` and `published` to `true` only after Steven has
   approved the image and copy.

Example:

```json
{
  "title": "Front yard cleanup",
  "category": "Cleanup",
  "location": "Lawrenceville area",
  "description": "Overgrowth removal and a clean final pass.",
  "image": "assets/work/front-yard-cleanup.webp",
  "alt": "Freshly cleaned front yard with trimmed lawn edges",
  "approved_for_public": true,
  "published": true
}
```
