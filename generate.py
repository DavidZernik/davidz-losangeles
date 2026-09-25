#!/usr/bin/env python3
"""Generate the editorial bento site (Instrument Serif + Geist) into site/."""
import json, html
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
SITE = ROOT / "site"
items = json.loads((ROOT / "reference/items.json").read_text())
by = {it["slug"]: it for it in items}


def thumb(src: str, w: int, h: int) -> str:
    """A small WebP of an image, cropped exactly the way its card shows it.

    The grid used to load every project's full-size image (38 MB for the
    homepage) and shrink it in the browser. Cards show the image with
    object-fit: cover anchored top center, so the crop here is the same: fill
    the box, keep the top, trim the sides evenly. Rebuilt only when the source
    changes. Anything Pillow can't open (SVG) is used as is.
    """
    source = SITE / src
    # Beside its source: every project folder has a 0.jpg, so a shared thumbs
    # folder named by file would collide.
    out = source.parent / "thumbs" / f"{source.stem}-{w}x{h}.webp"
    if out.exists() and out.stat().st_mtime >= source.stat().st_mtime:
        return str(out.relative_to(SITE))
    try:
        im = Image.open(source)
        im.seek(0)
        im = im.convert("RGBA")
    except Exception:
        return src
    flat = Image.new("RGB", im.size, "white")
    flat.paste(im, mask=im.getchannel("A"))
    scale = max(w / flat.width, h / flat.height)
    flat = flat.resize((max(w, round(flat.width * scale)),
                        max(h, round(flat.height * scale))), Image.LANCZOS)
    left = (flat.width - w) // 2
    flat = flat.crop((left, 0, left + w, h))
    out.parent.mkdir(parents=True, exist_ok=True)
    flat.save(out, "WEBP", quality=80, method=6)
    return str(out.relative_to(SITE))

# ---- brand logo wall ----
LOGOS = [
    ("Toyota","toyota.png"),("AT&T","att.png"),("DirecTV","directv.png"),("American Express","amex.png"),
    ("HBO Max","hbomax.png"),("Game of Thrones","got.png"),("Showtime","showtime.png"),("Cinemax","cinemax.png"),
    ("STARZ","starz.png"),("TBS","tbs.png"),("NBC","nbc.png"),("CBS Sports","cbssports.png"),
    ("SiriusXM","siriusxm.png"),("Spotify","spotify.png"),
    ("NFL","nfl.png"),("NHL","nhl.png"),("NCAA","ncaa.png"),("UFC","ufc.png"),
    ("UnitedHealthcare","unitedhealthcare.png"),("Blue Shield of California","blue-shield-ca.png"),
    ("Novo Nordisk","novo-nordisk.png"),("Aimmune","aimmune.png"),("Emory Healthcare","emory-healthcare.png"),
    ("PNC","pnc.png"),("Samsung","samsung.png"),("IBM","ibm.jpeg"),("T-Mobile","tmobile.png"),
    ("TinyMCE","tiny.png"),("Glo","glo.jpeg"),("Brilliant Earth","brilliant-earth.png"),
    ("Decathlon","decathlon.png"),("Waste Management","waste-management.png"),
    ("Petite 'n Pretty","petitenpretty.png"),("Save Khaki United","savekhaki.svg"),
    ("The Podcast Fellowship","podcastfellowship.png"),
    ("UCLA","ucla.jpeg"),("University of Phoenix","university-of-phoenix.jpeg"),
]

# hero product screenshot + featured tooling pieces
HERO_PRODUCT = "emory-healthcare-email-calendar-tool"
# Detail pages whose creative breaks out wide (big app screenshots only)
WIDE_CREATIVES = {"emory-healthcare-email-calendar-tool"}
# Detail pages where the screenshots lead, before the write-up
IMAGES_FIRST = {"zoutcomes-sfmc-ai-agent"}
FEATURED = ["zoutcomes-sfmc-ai-agent", "emory-healthcare-email-kpi-dashboard", "patient-reengagement-audience-pipeline"]
N_PIECES = len(items)

ARW = '<span class="arw">&rarr;</span>'
def esc(s): return html.escape(s, quote=True)

def head(title, desc, home, og_image, css="styles.css", brand=True):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <script>document.documentElement.classList.add('js')</script>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:type" content="website" />
  {og_image}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{css}" />
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header" id="top">
  <div class="wrap header-inner{'' if brand else ' header-inner--end'}">
    {'<a class="brand" href="' + home + '">David Z.</a>' if brand else ''}
    <nav class="nav" aria-label="Primary">
      <a href="{home}#work">Work</a>
      <a href="resume.html">Resume</a>
      <a href="{home}#brands">Brands</a>
      <a class="nav-cta" href="mailto:david@blueinboxllc.com">Contact&nbsp;<span class="arw">&rarr;</span></a>
    </nav>
  </div>
</header>
<main id="main">
"""

FOOT = """</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <p class="footer-lead">Let's build something that <em>sends</em>.</p>
      <div>
        <a class="footer-mail" href="mailto:david@blueinboxllc.com">david@blueinboxllc.com&nbsp;<span class="arw">&rarr;</span></a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 David Z. &middot; Los Angeles</span>
      <span>Salesforce Marketing Cloud &middot; Email &middot; MarTech</span>
    </div>
  </div>
</footer>
<script>
  // Grid images fade in over a placeholder once they arrive; one already in
  // the cache is shown at once.
  document.querySelectorAll('.work-thumb img, .feat-shot img').forEach(function (img) {
    var done = function () { img.parentNode.classList.add('loaded'); };
    if (img.complete && img.naturalWidth) done();
    else { img.addEventListener('load', done); img.addEventListener('error', done); }
  });
  (function () {
    var h = document.getElementById('top');
    var onScroll = function () { h.classList.toggle('scrolled', window.scrollY > 10); };
    onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
  })();
  (function () {
    var imgs = document.querySelectorAll('.creative img');
    if (!imgs.length) return;
    var box = document.createElement('div');
    box.className = 'lightbox';
    box.innerHTML = '<button class="lightbox-close" aria-label="Close image">&times;</button><img alt="" />';
    document.body.appendChild(box);
    var boxImg = box.querySelector('img');
    function open(src, alt) {
      boxImg.src = src; boxImg.alt = alt || '';
      box.scrollTop = 0;
      box.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function close() {
      box.classList.remove('open');
      document.body.style.overflow = '';
    }
    imgs.forEach(function (img) {
      img.addEventListener('click', function () { open(img.src, img.alt); });
    });
    box.addEventListener('click', function (e) { if (e.target !== boxImg) close(); });
    box.querySelector('.lightbox-close').addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  })();
</script>
</body>
</html>
"""

# ==================== HOMEPAGE ====================
hp = by[HERO_PRODUCT]
home = head(
    "David Z. · MarTech Architect specializing in Salesforce Marketing Cloud",
    "David Z. is a MarTech architect in Los Angeles specializing in Salesforce Marketing Cloud. Building CloudPages, automations, SQL, journeys, and internal tools.",
    "index.html",
    f'<meta property="og:image" content="{hp["images"][0]}" />',
    brand=False)

home += f'''  <section class="hero">
    <div class="wrap">
      <div class="bento">
        <div class="cell cell--headline reveal">
          <p class="hero-name">David Z.</p>
          <span class="hero-eyebrow">Los Angeles &middot; MarTech Architect</span>
          <h1 class="hero-title">Marketing technology, <em>architected</em> end&#8209;to&#8209;end.</h1>
          <p class="hero-sub">I'm David, a MarTech architect and email developer. I build and automate the systems, tools, and pipelines behind marketing at scale, with a specialty in Salesforce Marketing Cloud.</p>
          <p class="hero-sub">Recently that's meant a real-time KPI dashboard for send performance at Emory, automated QA tooling at SiriusXM that tests every link in an email before it ships, and a Marketing Cloud calendar app that gives the team one view of every journey and campaign.</p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="#work">See the work {ARW}</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section" id="work">
    <div class="wrap">
      <div class="section-head">
        <h2 class="section-title">Built for the <em>platform</em></h2>
        <p class="section-sub">Internal SFMC tools and dashboards I designed and coded, not just emails, but the systems around them.</p>
      </div>
      <div class="featured-grid">
'''

for slug in FEATURED:
    it = by[slug]
    brand = f'<span class="feat-brand">{esc(it["brand"])}</span>' if it["brand"] else ""
    desc = esc(it["desc"] or (it["body"][0] if it["body"] else ""))
    home += f'''        <a class="feat" href="{slug}.html">
          <div class="feat-shot"><img loading="lazy" width="800" height="500" src="{thumb(it['images'][0], 800, 500)}" alt="{esc(it['title'])}" /></div>
          <div class="feat-body">{brand}<h3 class="feat-title">{esc(it['title'])}</h3><p class="feat-desc">{desc}</p></div>
        </a>
'''

home += f'''      </div>

      <div class="section-head" style="margin-top:64px">
        <h2 class="section-title">Selected <em>campaigns</em></h2>
        <p class="section-sub">{N_PIECES} pieces: email, landing pages, and creative for brands across every industry.</p>
      </div>
      <div class="work-grid">
'''

featured_set = set(FEATURED) | {HERO_PRODUCT}
for it in items:
    if it["slug"] in featured_set:
        continue
    tag = f'<span class="card-tag">{esc(it["brand"])}</span>' if it["brand"] else ""
    home += f'''        <a class="work-item" href="{it['slug']}.html">
          <div class="work-thumb"><img loading="lazy" width="640" height="480" src="{thumb(it['images'][0], 640, 480)}" alt="{esc(it['title'])}" /></div>
          <div class="work-meta">{tag}<h3>{esc(it['title'])}</h3></div>
        </a>
'''

logos = "\n".join(
    f'        <li class="logo-cell"><img loading="lazy" src="assets/logos/{f}" alt="{esc(n)}" /></li>'
    for n, f in LOGOS)

home += f'''      </div>
    </div>
  </section>

  <section class="section section-brands" id="brands">
    <div class="wrap">
      <div class="section-head">
        <h2 class="section-title">Brands I've <em>worked with</em></h2>
        <p class="section-sub">Campaigns, content, and platform work spanning many industries. Some were direct clients; others I worked on through agencies, subcontracts, and partnerships &mdash; building and shipping against the brand's own assets and campaigns.</p>
      </div>
      <ul class="logo-grid" role="list">
{logos}
      </ul>
    </div>
  </section>
'''
home += FOOT
(SITE / "index.html").write_text(home)

# ==================== DETAIL PAGES ====================
for idx, it in enumerate(items):
    prev_it = items[idx - 1] if idx > 0 else None
    next_it = items[idx + 1] if idx < len(items) - 1 else None
    imgs = "\n".join(
        f'        <figure class="creative"><img loading="lazy" src="{src}" alt="{esc(it["title"])} {i+1}" /></figure>'
        for i, src in enumerate(it["images"]))
    body = it.get("body", [])
    body_html = "\n".join(
        f'        <p class="built-with">{esc(p)}</p>' if p.strip().startswith("Built with:")
        else f'        <p>{esc(p)}</p>'
        for p in body)
    body_block = f'      <div class="detail-body">\n{body_html}\n      </div>\n' if body else ""
    meta_desc = body[0] if body else it["title"]
    meta_desc = (meta_desc[:157] + "…") if len(meta_desc) > 158 else meta_desc
    tag = f'<span class="detail-tag">{esc(it["brand"])}</span>' if it["brand"] else ""

    pager = '<div class="pager">'
    pager += (f'<a class="pager-link prev" href="{prev_it["slug"]}.html"><span class="arw">&larr;</span>&nbsp;{esc(prev_it["title"])}</a>'
              if prev_it else '<span></span>')
    pager += (f'<a class="pager-link next" href="{next_it["slug"]}.html">{esc(next_it["title"])}&nbsp;<span class="arw">&rarr;</span></a>'
              if next_it else '<span></span>')
    pager += '</div>'

    # Only the big SFMC calendar app screenshot breaks out wide; everything else stays normal.
    wide_cls = " creatives--wide" if it["slug"] in WIDE_CREATIVES else ""
    demo_url = it.get("demo_url")
    demo_label = it.get("demo_label", "Try the live demo")
    demo_cta = (f'\n        <a class="btn btn-primary" href="{demo_url}" target="_blank" rel="noopener">{demo_label} {ARW}</a>'
                if demo_url else "")
    creatives_block = f'      <div class="creatives{wide_cls}">\n{imgs}\n      </div>\n'
    main_block = (creatives_block + body_block) if it["slug"] in IMAGES_FIRST else (body_block + creatives_block)

    page = head(f'{esc(it["title"])} · David Z.', esc(meta_desc), "index.html",
                f'<meta property="og:image" content="{it["images"][0]}" />')
    page += f'''  <article class="detail">
    <div class="wrap wrap-narrow">
      <a class="back-link" href="index.html#work"><span class="arw">&larr;</span>&nbsp;All work</a>
      <header class="detail-head">
        {tag}
        <h1 class="detail-title">{esc(it["title"])}</h1>{demo_cta}
      </header>
{main_block}      {pager}
    </div>
  </article>
'''
    page += FOOT
    (SITE / f'{it["slug"]}.html').write_text(page)

print(f"Generated index.html + {len(items)} detail pages")
