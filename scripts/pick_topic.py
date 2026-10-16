#!/usr/bin/env python3
"""Pick the brand to publish now and the best unused topic for it.

Usage: python3 scripts/pick_topic.py [--date YYYY-MM-DD] [--brand rfc|aurea] [--skip cluster-id,...]

The weekday schedule in config.json says which brands publish on a day (Sunday has two). Without --brand the
first scheduled brand that has no engine post dated that day is picked.
Prints JSON: brands_today, still_to_publish, brand, top candidates (cluster, suggested format, allowed title shapes),
and recent history.
Exit code 2 when the engine is paused, 3 when every brand scheduled for the day is already published.
"""
import json
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

from common import config, core_words, load_json, similarity

FORMATS = ["deep-guide", "comparison", "numbered-list", "straight-answer", "myth-vs-fact", "step-by-step",
           "number-explained", "cost-breakdown", "research-roundup", "decision-guide", "condition-guide",
           "patient-scenarios"]
SHAPES_FOR = {
    "deep-guide": ["T1", "T10", "T12"], "comparison": ["T4"], "numbered-list": ["T3", "T10"],
    "straight-answer": ["T2", "T12"], "myth-vs-fact": ["T11"], "step-by-step": ["T6", "T9"],
    "number-explained": ["T5", "T2"], "cost-breakdown": ["T7"], "research-roundup": ["T10", "T1"],
    "decision-guide": ["T8"], "condition-guide": ["T1", "T10", "T3"], "patient-scenarios": ["T12", "T3"],
}


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def brands_for(day, cfg):
    return cfg["schedule"][DAYS[day.weekday()]]


def main():
    cfg = config()
    if cfg.get("paused"):
        print(json.dumps({"paused": True}))
        sys.exit(2)
    day = date.fromisoformat(arg("--date")) if arg("--date") else datetime.now(ZoneInfo(cfg["timezone"])).date()
    pub = load_json("data/published.json", {"posts": []})["posts"]
    today = brands_for(day, cfg)
    done = {p["brand"] for p in pub if p.get("source") == "engine" and p["date"] == day.isoformat()}
    left = [b for b in today if b not in done]
    if not arg("--brand") and not left:
        print(json.dumps({"date": day.isoformat(), "weekday": DAYS[day.weekday()], "brands_today": today,
                          "still_to_publish": [], "note": "every brand scheduled today is already published"}))
        sys.exit(3)
    brand = arg("--brand") or left[0]
    skip = set((arg("--skip") or "").split(",")) - {""}
    mine = [p for p in sorted(pub, key=lambda p: p["date"], reverse=True) if p["brand"] == brand]
    engine = [p for p in mine if p.get("pillar")]
    recent_pillars = [p["pillar"] for p in engine[:4]]
    recent_formats = [p["format"] for p in engine[:8]]
    recent_shapes = [p["title_shape"] for p in engine[:6]]
    clusters = load_json("data/topics.json", {"clusters": []})["clusters"]
    cands = []
    for c in clusters:
        if c["status"] != "available" or c["brand"] != brand or c["id"] in skip:
            continue
        if c["pillar"] in recent_pillars:
            continue
        top = max(((similarity(c["primary"], p["title"]), p["title"]) for p in pub), default=(0, ""))
        if top[0] >= 0.6:
            continue
        # Penalise clusters close to a post this brand already has (shares >= 2 and >= half of the core words).
        pc = set(core_words(c["primary"]))
        close = [p["title"] for p in mine if len(pc & set(core_words(p["title"]))) >= max(2, len(pc) / 2)]
        adj = c["score"] - 8 * min(2, len(close))
        fmt = c["suggested_format"]
        last = recent_formats[0] if recent_formats else None
        if fmt == last or recent_formats.count(fmt) >= 2:
            fmt = next(f for f in FORMATS if f != last and recent_formats.count(f) < 2)
        shapes = [s for s in SHAPES_FOR[fmt] if s not in recent_shapes] or SHAPES_FOR[fmt]
        cands.append({"cluster_id": c["id"], "primary": c["primary"], "pillar": c["pillar"],
                      "volume": c["volume"], "sd": c["sd"], "cluster_volume": c["total_volume"],
                      "score": c["score"], "adjusted_score": adj, "near_existing": close[:3], "format": fmt, "title_shapes": shapes,
                      "variants": [k["term"] for k in c["keywords"][:8]],
                      "closest_existing_title": top[1], "closest_similarity": round(top[0], 2)})
    cands.sort(key=lambda x: -x["adjusted_score"])
    cands = cands[:5]
    print(json.dumps({"date": day.isoformat(), "weekday": DAYS[day.weekday()], "brands_today": today,
                      "still_to_publish": left, "brand": brand, "candidates": cands,
                      "recent": {"pillars": recent_pillars, "formats": recent_formats, "title_shapes": recent_shapes,
                                 "last_titles": [p["title"] for p in mine[:5]]}}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
