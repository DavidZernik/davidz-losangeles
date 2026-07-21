#!/usr/bin/env python3
"""Static-site generator for the David Z. portfolio (cloned off Wix).
Reads reference/manifest.json + downloads creatives, emits site/."""
import json, re, html, urllib.request, ssl
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT / "site"
MANIFEST = json.loads((ROOT / "reference/manifest.json").read_text())
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

# ---- pages we consider duplicates / non-portfolio: keep per user (they wanted all real ones) ----
SKIP = {"template", "home"}

def humanize(title, slug):
    t = title.strip()
    # keep already-nice titles (mixed case or has spaces & capitals)
    if t and (t != t.lower()) and (" " in t or "&" in t):
        return t
    base = (t or slug)
    base = re.sub(r'^copy-of-', '', base)
    base = base.replace("-", " ").replace("_", " ")
    base = re.sub(r'\s+', ' ', base).strip()
    # tidy known acronyms
    words = []
    ACR = {"att":"AT&T","amex":"Amex","directv":"DirecTV","hbo":"HBO","ncaa":"NCAA",
           "nfl":"NFL","nhl":"NHL","cbs":"CBS","nbc":"NBC","ufc":"UFC","tpf":"TPF",
           "toa":"TOA","sfmc":"SFMC","kpi":"KPI","sql":"SQL","tmo":"T-Mobile",
           "pnc":"PNC","wm":"WM","ngb":"NGB","uhc":"UHC"}
    for w in base.split(" "):
        lw = re.sub(r'[0-9]+$', '', w.lower())
        if lw in ACR:
            num = w[len(lw):]
            words.append(ACR[lw] + (" " + num if num else ""))
        else:
            words.append(w[:1].upper() + w[1:])
    return " ".join(words).strip() or slug

def brand_of(slug, title):
    s = (slug + " " + title).lower()
    for key, name in [("att","AT&T"),("amex","Amex"),("directv","DirecTV"),("hbo","HBO Max"),
        ("toyota","Toyota"),("glo","Glo"),("blueshield","Blue Shield"),("blue-shield","Blue Shield"),
        ("waste-management","Waste Management"),("emory","Emory Healthcare"),("pnc","PNC"),
        ("aimmune","Aimmune"),("brilliantearth","Brilliant Earth"),("brilliant","Brilliant Earth"),
        ("ncaa","NCAA"),("nfl","NFL"),("nhl","NHL"),("cbs","CBS Sports"),("nbc","NBC"),
        ("starz","STARZ"),("showtime","Showtime"),("spotify","Spotify"),("ozempic","Novo Nordisk"),
        ("unitedhealthcare","UnitedHealthcare"),("uhc","UnitedHealthcare"),("gameofthrones","HBO"),
        ("tmo","T-Mobile"),("tmobile","T-Mobile"),("truecrime","DirecTV"),("true-crime","DirecTV"),
        ("sundayticket","NFL"),("titangames","TBS"),("decalthon","Decathlon"),("ucla","UCLA"),
        ("ibm","IBM"),("fiber","AT&T"),("savekhaki","Save Khaki"),("acme","Acme")]:
        if key in s:
            return name
    return ""

def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        dest.write_bytes(r.read())

# ---- build item list with local asset paths ----
items = []
for rec in MANIFEST:
    slug = rec["slug"]
    if slug in SKIP or not rec["images"]:
        continue
    disp = humanize(rec["title"], slug)
    local = []
    for i, url in enumerate(rec["images"]):
        ext = url.rsplit(".", 1)[-1]
        rel = f"assets/work/{slug}/{i}.{ext}"
        try:
            download(url, SITE / rel)
            local.append(rel)
        except Exception as e:
            print(f"  ! {slug} img {i} failed: {e}")
    if local:
        items.append({"slug": slug, "title": disp, "brand": brand_of(slug, disp), "images": local})

print(f"Built {len(items)} portfolio items, {sum(len(i['images']) for i in items)} images downloaded")
(ROOT / "reference/items.json").write_text(json.dumps(items, indent=2))
