#!/usr/bin/env python3
"""Record a published post: ledger, topic status, run log.

Usage:
  python3 scripts/record.py runs/<run> published <post_id> <live_url>
  python3 scripts/record.py runs/<run> draft <draft_id>
  python3 scripts/record.py runs/<run> blocked "<reason>"      (quality gate stopped the topic)
"""
import json
import sys
from datetime import datetime, timezone

from common import ROOT, load_json, save_json, split_source


def main():
    run = (ROOT / sys.argv[1]).resolve()
    status = sys.argv[2]
    fm, _ = split_source((run / "post.md").read_text(encoding="utf-8")) if (run / "post.md").exists() else ({}, "")
    topics = load_json("data/topics.json", {"clusters": []})
    cid = fm.get("cluster_id")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if status == "published":
        post_id, url = sys.argv[3], sys.argv[4]
        pub = load_json("data/published.json", {"posts": []})
        pub["posts"].insert(0, {
            "brand": fm["brand"], "title": fm["title"], "slug": fm["slug"], "date": fm["date"],
            "category": fm["category"], "post_id": post_id, "url": url, "source": "engine",
            "pillar": fm["pillar"], "format": fm["format"], "title_shape": fm["title_shape"],
            "primary_keyword": fm["primary_keyword"]["term"], "cluster_id": cid,
            "secondary_keywords": [k["term"] for k in fm["secondary_keywords"]]})
        save_json("data/published.json", pub)
        secondary = {k["term"].lower() for k in fm["secondary_keywords"]}
        for c in topics["clusters"]:
            if c["id"] == cid:
                c["status"], c["note"] = "used", f"published {fm['date']} {url}"
            elif c["status"] == "available" and c["primary"].lower() in secondary:
                c["status"], c["note"] = "used", f"secondary keyword of {url}"
        save_json("data/topics.json", topics)
        result = {"status": "published", "post_id": post_id, "url": url, "at": now}
    elif status == "draft":
        result = {"status": "draft", "draft_id": sys.argv[3], "at": now}
    elif status == "blocked":
        reason = sys.argv[3]
        for c in topics["clusters"]:
            if c["id"] == cid:
                c["status"], c["note"] = "blocked", reason
        save_json("data/topics.json", topics)
        result = {"status": "blocked", "reason": reason, "at": now}
    else:
        raise SystemExit(__doc__)
    (run / "result.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    line = f"| {fm.get('date', now[:10])} | {fm.get('brand', '?')} | {status} | {fm.get('title', '')} | " \
           f"{fm.get('primary_keyword', {}).get('term', '')} | {result.get('url') or result.get('reason') or ''} |\n"
    log = ROOT / "runs" / "log.md"
    if not log.exists():
        log.write_text("| date | brand | status | title | keyword | url / reason |\n|---|---|---|---|---|---|\n")
    with log.open("a", encoding="utf-8") as f:
        f.write(line)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
