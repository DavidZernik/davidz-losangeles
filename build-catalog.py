#!/usr/bin/env python3
"""Compile reference/items.json into assistant/portfolio-catalog.md so the
avatar knows every piece on the site. Each piece is tagged with its job era
so the avatar can weave in David's real human color (never invented)."""
import json, re
from pathlib import Path

ROOT = Path(__file__).parent
items = json.loads((ROOT / "reference/items.json").read_text())

def era_of(slug, brand):
    s = (slug + " " + brand).lower()
    if "emory" in s or "patient-reengagement" in s: return "Emory Healthcare (current)"
    if "amex" in s or "american express" in s: return "American Express years"
    if "query-studio" in s or "tmobile" in s or "t-mobile" in s: return "T-Mobile contract"
    if s.startswith("glo-") or "glo " in s or brand.lower() == "glo": return "YogaGlo, his first job"
    if "blue-shield" in s or "unitedhealthcare" in s: return "his independent year"
    if any(k in s for k in ["att-", "at&t", "directv", "toyota", "sunday-ticket", "sundayticket",
                            "ufc", "starz", "showtime", "cinemax", "nbc", "cbs", "spotify",
                            "hbo", "movies-extra", "oxygen", "titan", "fiber", "samsung",
                            "iphone", "march-madness", "nfl"]):
        return "the agency years (Omnicom)"
    return ""  # unknown: describe the work, no era color

lines = []
for it in items:
    era = era_of(it["slug"], it.get("brand", ""))
    desc = (it.get("desc") or (it["body"][0] if it.get("body") else ""))[:140]
    era_part = f" | era: {era}" if era else ""
    lines.append(f"- {it['title']} | brand: {it.get('brand') or 'n/a'} | page: /{it['slug']}{era_part} | {desc}")

out = f"""# Portfolio catalog ({len(items)} pieces on davidz-losangeles.com)

Every piece below is live on the site. When one comes up, mention it by name
and say it is on the portfolio (for example, "the Toyota Mirai page on the
site"). Do not read URLs aloud. When a piece has an era tag, weave in the
human color from the matching job in the "what each job was actually like"
notes. If a piece has no era tag, just describe the work itself and do not
guess where or when it was made.

{chr(10).join(lines)}
"""
(ROOT / "assistant/portfolio-catalog.md").write_text(out)
tagged = sum(1 for l in lines if "| era:" in l)
print(f"catalog: {len(items)} pieces, {tagged} era-tagged, {len(out)} chars")
