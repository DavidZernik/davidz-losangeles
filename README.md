# davidz-losangeles.com — off-Wix clone

A clean, dependency-free static clone of the Wix portfolio site. Plain HTML/CSS,
one folder, hosts free anywhere. Preserves the original URL structure
(`/gameofthrones`, `/attsamsung`, …) so existing links keep working.

## What's here

```
site/                     ← the actual website (deploy THIS folder)
  index.html              ← homepage: hero + work gallery + brand wall
  <slug>.html             ← 75 work detail pages (one per portfolio piece)
  styles.css              ← all styling
  assets/logos/           ← 25 client logos
  assets/work/<slug>/     ← creative screenshots per piece
build.py                  ← re-downloads creatives from the manifest
generate.py               ← regenerates all HTML from reference/items.json
reference/                ← scraped source, manifests, originals (not deployed)
```

## Preview locally

```bash
cd site
python3 -m http.server 8899
# open http://localhost:8899
```

## Regenerate (after editing titles, adding/removing pieces)

Edit `reference/items.json` (titles, brand tags, order), then:

```bash
python3 generate.py      # rebuilds index.html + all detail pages
```

## Deploy (pick one — all free, all keep your domain)

**Cloudflare Pages / Netlify (drag-and-drop):**
1. Zip or drag the `site/` folder into the dashboard.
2. Set your domain `davidz-losangeles.com` as a custom domain.
3. Update DNS at your registrar to point at the host (they give you records).

**GitHub Pages:**
1. `git init && git add site && git commit -m "site"`, push to a repo.
2. Settings → Pages → deploy from `/site`.

## Moving the domain off Wix

Your domain may be registered *through* Wix or just *pointed* at Wix. Check
which at your registrar. If it's registered through Wix, you can either transfer
it out (unlock + auth code) or just repoint the nameservers/DNS to the new host.
Either way the site content is now fully yours here.

## Notes

- Titles and URLs were rewritten to match each creative's actual content (verified
  by looking at every image), e.g. `gameofthrones` → `directv-hbo-cinemax-free-preview`,
  `copy-of-aimmune2` → `sfmc-query-studio-dedupe-sql`. These no longer match the old
  Wix slugs — if you want redirects from the old URLs, ask and I'll add a `_redirects`
  file (Netlify/Cloudflare) mapping them.
- To tweak a title, brand tag, or slug: edit `reference/items.json` and re-run
  `python3 generate.py`. To also rename the URL, change `slug` there and rename the
  matching `site/assets/work/<slug>/` folder.
- Logos are shown grayscale, color-on-hover. Remove the `filter: grayscale(1)`
  rule in `styles.css` (`.logo-cell img`) for full-color logos.
