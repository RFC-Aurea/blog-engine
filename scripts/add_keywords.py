#!/usr/bin/env python3
"""Append Ubersuggest rows to data/keywords_raw.json (skips duplicates), then rebuild topics.

Usage: python3 scripts/add_keywords.py <rows.json> --brand rfc|aurea|shared --pillar <pillar> --seed "<seed>"
rows.json: [{"keyword": "...", "volume": 90, "sd": 21, "cpc": 1.2, "intent": [1]}, ...]
Only copy rows exactly as Ubersuggest returned them (volume >= 30).
"""
import json
import subprocess
import sys
from datetime import date

from common import ROOT, load_json, save_json


def arg(name):
    return sys.argv[sys.argv.index(name) + 1]


def main():
    rows = json.loads(open(sys.argv[1], encoding="utf-8").read())
    raw = load_json("data/keywords_raw.json", {"source": "Ubersuggest", "calls": [], "rows": []})
    have = {r["keyword"].lower() for r in raw["rows"]}
    added = 0
    for r in rows:
        k = r["keyword"].lower().strip()
        if k in have or not isinstance(r.get("volume"), (int, float)):
            continue
        raw["rows"].append({"brand": arg("--brand"), "pillar": arg("--pillar"), "seed": arg("--seed"),
                            "keyword": k, "volume": r["volume"], "sd": r.get("sd"), "cpc": r.get("cpc"),
                            "intent": r.get("intent"), "added": date.today().isoformat()})
        have.add(k)
        added += 1
    raw["calls"].append({"brand": arg("--brand"), "pillar": arg("--pillar"), "seeds": [arg("--seed")], "ok": True,
                         "rows_kept": added, "date": date.today().isoformat()})
    save_json("data/keywords_raw.json", raw)
    print(f"added {added} new keywords")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_topics.py")], check=True)


if __name__ == "__main__":
    main()
