#!/usr/bin/env python3
"""Generate the editorial bento site (Instrument Serif + Geist) into site/."""
import json, html
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT / "site"
items = json.loads((ROOT / "reference/items.json").read_text())
by = {it["slug"]: it for it in items}

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
FEATURED = ["emory-healthcare-email-kpi-dashboard", "sfmc-query-studio-dedupe-sql", "patient-reengagement-journey-map"]
N_PIECES = len(items)
N_BRANDS = len({it["brand"] for it in items if it["brand"]})

ARW = '<span class="arw">&rarr;</span>'
def esc(s): return html.escape(s, quote=True)

def head(title, desc, home, og_image, css="styles.css"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
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
  <div class="wrap header-inner">
    <a class="brand" href="{home}">David Z.</a>
    <nav class="nav" aria-label="Primary">
      <a href="{home}#work">Work</a>
      <a href="{home}#about">About</a>
      <a href="resume.html">Resume</a>
      <a href="{home}#brands">Brands</a>
      <a class="nav-cta" href="mailto:david@blueinboxllc.com">Contact&nbsp;<span class="arw">&rarr;</span></a>
    </nav>
  </div>
</header>
<main id="main">
"""

# AI David widget: open on page load (same as resume.html); session still starts on click
WIDGET = """
<!-- AI David widget (open by default, click to start) -->
<div id="aiDavid" class="aid">
  <button id="aidBubble" class="aid-bubble" aria-label="Open AI David" hidden>
    <img src="assets/ai-david.webp" alt="" />
    <span class="aid-pill">Ask AI David</span>
  </button>
  <div id="aidCard" class="aid-card">
    <div class="aid-video-wrap">
      <video id="aidVideo" autoplay playsinline></video>
      <button id="aidStart" class="aid-preview" aria-label="Start talking to AI David">
        <img src="assets/ai-david.webp" alt="" />
        <span class="aid-play">&#9658;</span>
        <span class="aid-start-label">Start conversation</span>
      </button>
      <div id="aidStatus" class="aid-status" hidden>Connecting to AI David&hellip;</div>
      <span id="aidTimer" class="aid-timer" hidden>3:00</span>
      <span id="aidMic" class="aid-mic" hidden>Intro playing&hellip;</span>
      <button id="aidClose" class="aid-close" aria-label="Close AI David">&times;</button>
    </div>
    <div class="aid-foot">
      <span class="aid-disclaimer">AI twin with a stock face. The real David is not as handsome. And a British accent to make him sound refined.</span>
      <a href="mailto:dzernik@gmail.com">Email the real one</a>
    </div>
  </div>
</div>
<script type="module" src="ai-david.js"></script>
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
  (function () {
    var h = document.getElementById('top');
    var onScroll = function () { h.classList.toggle('scrolled', window.scrollY > 10); };
    onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
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
    f'<meta property="og:image" content="{hp["images"][0]}" />')

home += f'''  <section class="hero">
    <div class="wrap">
      <div class="bento">
        <div class="cell cell--headline reveal">
          <span class="hero-eyebrow">Los Angeles &middot; MarTech Architect</span>
          <h1 class="hero-title">Marketing technology, <em>architected</em> end&#8209;to&#8209;end.</h1>
          <p class="hero-sub">I'm David, a MarTech architect. I build and automate the systems, tools, and pipelines behind marketing at scale, with a specialty in Salesforce Marketing Cloud.</p>
          <p class="hero-sub">Recently that's meant a real-time KPI dashboard for send performance at Emory, automated QA tooling at SiriusXM that tests every link in an email before it ships, and a Marketing Cloud calendar app that gives the team one view of every journey and campaign.</p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="#work">See the work {ARW}</a>
            <a class="btn btn-ghost" href="mailto:david@blueinboxllc.com">Get in touch</a>
          </div>
        </div>
        <a class="cell cell--product reveal d2" href="{HERO_PRODUCT}.html" aria-label="{esc(hp['title'])}">
          <span class="product-cap"><span class="dot"></span>SFMC-powered &middot; built by David</span>
          <img class="product-shot" src="{hp['images'][0]}" alt="{esc(hp['title'])}" />
        </a>
        <div class="cell cell--mint reveal d3">
          <div class="stat-num">{N_PIECES}</div>
          <div class="stat-label">campaigns, tools &amp; pages shipped</div>
        </div>
        <div class="cell cell--ink reveal d4">
          <div class="stat-num">{N_BRANDS}+</div>
          <div class="stat-label">brands across entertainment, finance, healthcare, sports &amp; tech</div>
        </div>
        <div class="cell cell--photo reveal d5">
          <img src="assets/hero-desk.jpg" alt="David's workspace" />
        </div>
      </div>
    </div>
  </section>

  <section class="section about" id="about">
    <div class="wrap">
      <div class="about-grid">
        <p class="about-kicker">Data in,<br />polished sends out.</p>
        <div class="about-body">
          <p>I'm a MarTech architect specializing in <strong>Salesforce Marketing Cloud</strong>. After more than three years at <strong>American Express</strong> working on SFMC, web development, dynamic email, QA, and interactive tools, I'm now an SFMC Architect at <strong>Emory Healthcare</strong>.</p>
          <p>I architect and build the full stack of a Marketing Cloud program: CloudPages, automations, SQL queries, AMPscript and SSJS, journeys, dashboards, and internal tools for large-scale healthcare marketing. The kind of platform work that makes every send faster, cleaner, and measurable.</p>
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
          <div class="feat-shot"><img loading="lazy" src="{it['images'][0]}" alt="{esc(it['title'])}" /></div>
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
          <div class="work-thumb"><img loading="lazy" src="{it['images'][0]}" alt="{esc(it['title'])}" /></div>
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
home += FOOT.replace("</footer>", "</footer>" + WIDGET, 1)
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

    page = head(f'{esc(it["title"])} · David Z.', esc(meta_desc), "index.html",
                f'<meta property="og:image" content="{it["images"][0]}" />')
    page += f'''  <article class="detail">
    <div class="wrap wrap-narrow">
      <a class="back-link" href="index.html#work"><span class="arw">&larr;</span>&nbsp;All work</a>
      <header class="detail-head">
        {tag}
        <h1 class="detail-title">{esc(it["title"])}</h1>
      </header>
{body_block}      <div class="creatives{wide_cls}">
{imgs}
      </div>
      {pager}
    </div>
  </article>
'''
    page += FOOT
    (SITE / f'{it["slug"]}.html').write_text(page)

print(f"Generated index.html + {len(items)} detail pages")
