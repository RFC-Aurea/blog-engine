#!/usr/bin/env python3
"""Cluster data/keywords_raw.json into data/topics.json (one cluster = one future post).

Usage: python3 scripts/build_topics.py [--min-volume 20]

Keeps the status (used / blocked) of clusters that already exist in topics.json.
"""
import math
import re
import sys
from datetime import date

from common import contains_keyword, core_words, load_json, save_json, similarity

DROP = re.compile(r"\b(reddit|quora|hindi|tamil|urdu|marathi|telugu|kannada|bengali|nhs|uk|india|"
                  r"ahmedabad|mumbai|delhi|pune|bangalore|chennai|hyderabad|ayurveda|ayurvedic|ka |ke |kya|"
                  r"kaise|hota|ilaj|lakshan|matlab|gynoveda|near me|youtube|pdf|meme|tiktok|usg|calculator calculator)\b")
RFC_HINT = re.compile(r"\b(40|41|42|43|44|45|46|47|48|50|over 35|over 40|after 40|older|perimenopaus|menopaus|"
                      r"recurrent|repeated|implantation failure|low amh|diminished|poor ovarian|high fsh|"
                      r"premature ovarian|poi|pof|prp|rejuvenat|stem cell|donor|surroga|plus size|bmi|obes|"
                      r"immunolog|nk cell|intralipid|endometritis|failed ivf|libido|vaginal)\b")
FORMAT_RULES = [
    (r"\bvs\b|\bversus\b|\bor\b.*\b(ivf|iui|freez)", "comparison"),
    (r"\b(costs?|prices?|insurance|covered|coverage|afford\w*|financ\w*|how much)\b", "cost-breakdown"),
    (r"\bmyth", "myth-vs-fact"),
    (r"\b(right for me|candidate|should i)\b", "decision-guide"),
    (r"\b(level|levels|range|chart|normal|number|score|grade|grading|count)\b", "number-explained"),
    (r"\b(timeline|process|steps|step by step|what to expect|day by day|week by week|how long)\b", "step-by-step"),
    (r"\b(types|options|ways|tips|causes|reasons|foods|supplements)\b", "numbered-list"),
    (r"\b(symptom|symptoms|signs|diagnos)\b", "condition-guide"),
    (r"\b(at 4\d|over 4\d|after 4\d|at 3\d)\b", "patient-scenarios"),
    (r"\b(success rate|study|research|new)\b", "research-roundup"),
    (r"^(can|does|do|is|will|are|could)\b", "straight-answer"),
    (r"^how to\b", "step-by-step"),
]


PLACES = set("""usa us america american united states state alabama alaska arizona arkansas california colorado
connecticut delaware florida georgia hawaii idaho illinois indiana iowa kansas kentucky louisiana maine maryland
massachusetts michigan minnesota mississippi missouri montana nebraska nevada hampshire jersey mexico york
carolina dakota ohio oklahoma oregon pennsylvania rhode island tennessee texas utah vermont virginia washington
wisconsin wyoming nyc nj ny ca tx fl la sf chicago houston dallas austin atlanta boston miami seattle denver
phoenix philadelphia san diego francisco los angeles brooklyn manhattan queens bronx long westchester
canada mexico near""".split())
MALE = re.compile(r"\b(male|males|men|man|sperm|semen|testosterone in men|varicocele|azoospermia)\b")


def norm_core(k):
    return frozenset(w for w in core_words(k) if w not in PLACES)


def sim(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def suggest_format(k):
    for pat, fmt in FORMAT_RULES:
        if re.search(pat, k):
            return fmt
    return "deep-guide"


def score(volume, sd, cpc, intent, fmt, pillar_fit):
    vol = min(40.0, 10 * math.log10(max(volume, 1) + 1))
    diff = max(0.0, 30 * (1 - min(sd or 0, 60) / 60))
    fit = pillar_fit + (2 if intent and 1 in intent else 0)
    money = min(10.0, (cpc or 0) * 1.5)
    return round(vol + diff + min(fit, 20) + money, 1)


def owner(row):
    if MALE.search(row["keyword"]):
        return "aurea"
    if row["brand"] in ("rfc", "aurea"):
        return row["brand"]
    return "rfc" if RFC_HINT.search(row["keyword"]) else "aurea"


def slugify(k):
    return re.sub(r"[^a-z0-9]+", "-", k.lower()).strip("-")[:60]


def main():
    min_vol = int(sys.argv[sys.argv.index("--min-volume") + 1]) if "--min-volume" in sys.argv else 20
    raw = load_json("data/keywords_raw.json", {"rows": []})
    old = {c["id"]: c for c in load_json("data/topics.json", {"clusters": []})["clusters"]}
    pub = load_json("data/published.json", {"posts": []})["posts"]
    fits = {b: v.get("pillar_fit", {}) for b, v in load_json("config.json")["brands"].items()}
    rows = [r for r in raw["rows"] if (r.get("volume") or 0) >= min_vol and not DROP.search(r["keyword"].lower())]
    seen, uniq = set(), []
    for r in sorted(rows, key=lambda r: -(r.get("volume") or 0)):
        k = r["keyword"].lower().strip()
        if k not in seen:
            seen.add(k)
            uniq.append(dict(r, keyword=k))
    clusters = []
    for r in uniq:
        core = norm_core(r["keyword"])
        best = None
        for c in clusters:
            s = sim(core, c["_core"])
            if s >= 0.67 or (core <= c["_core"] and len(c["_core"] - core) <= 1 and len(core) >= 2) or \
                    (c["_core"] <= core and len(core - c["_core"]) <= 2 and len(c["_core"]) >= 2):
                if not best or s > best[0]:
                    best = (s, c)
        if best:
            best[1]["keywords"].append({"term": r["keyword"], "volume": r["volume"], "sd": r.get("sd")})
            best[1]["total_volume"] += r["volume"]
        else:
            pillar = "male-factor" if MALE.search(r["keyword"]) else r["pillar"]
            clusters.append({"_core": core, "primary": r["keyword"], "brand": owner(r), "pillar": pillar,
                             "volume": r["volume"], "sd": r.get("sd"), "cpc": r.get("cpc"),
                             "intent": r.get("intent"), "total_volume": r["volume"],
                             "keywords": [{"term": r["keyword"], "volume": r["volume"], "sd": r.get("sd")}]})
    out = []
    for c in clusters:
        cid = f"{c['brand']}-{slugify(c['primary'])}"
        fmt = suggest_format(c["primary"])
        status, note = "available", ""
        hit = next((p for p in pub if similarity(c["primary"], p["title"]) >= 0.6 or
                    (len(c["_core"]) >= 2 and contains_keyword(p["title"], c["primary"]))), None)
        if hit:
            status, note = "used", f"covered by existing post: {hit['title']}"
        if cid in old and old[cid]["status"] in ("used", "blocked"):
            status, note = old[cid]["status"], old[cid].get("note", note)
        out.append({"id": cid, "brand": c["brand"], "pillar": c["pillar"], "primary": c["primary"],
                    "volume": c["volume"], "sd": c["sd"], "cpc": c["cpc"], "total_volume": c["total_volume"],
                    "keywords": c["keywords"][:12], "suggested_format": fmt,
                    "score": score(c["total_volume"], c["sd"], c["cpc"], c["intent"], fmt,
                                   fits.get(c["brand"], {}).get(c["pillar"], 10)),
                    "status": status, "note": note})
    out.sort(key=lambda c: -c["score"])
    save_json("data/topics.json", {"updated": date.today().isoformat(), "min_volume": min_vol,
                                   "clusters": out})
    avail = [c for c in out if c["status"] == "available"]
    by = {}
    for c in avail:
        by[c["brand"]] = by.get(c["brand"], 0) + 1
    print(f"{len(uniq)} keywords -> {len(out)} clusters; available: {by}; "
          f"used/covered: {sum(c['status'] == 'used' for c in out)}")


if __name__ == "__main__":
    main()
