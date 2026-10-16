#!/usr/bin/env python3
"""Compare what Wix returned after publishing with what build_post.py expected.

Usage: python3 scripts/verify_live.py runs/<run>
Reads runs/<run>/expected.json and runs/<run>/live_summary.json (the object returned by templates/publish.js).
Exit code 1 if something important is wrong (the run must report it and fix or unpublish).
"""
import json
import sys

from common import ROOT, content_hash


def main():
    run = (ROOT / sys.argv[1]).resolve()
    exp = json.loads((run / "expected.json").read_text())
    live = json.loads((run / "live_summary.json").read_text())
    problems, notes = [], []

    def need(name, ok, detail=""):
        (notes if ok else problems).append(f"{'OK  ' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail else ""))

    local = content_hash(json.loads((run / "compact.json").read_text(encoding="utf-8")))
    need("Wix received exactly the local post content", live.get("inputHash") == local,
         f"{live.get('inputHash')} vs {local}")
    need("slug", live.get("slug") == exp["slug"], f"{live.get('slug')} vs {exp['slug']}")
    need("title", live.get("title") == exp["title"])
    need("writer is Dr. Merhi", live.get("memberId") == exp["member_id"], str(live.get("memberId")))
    need("category", exp["category_id"] in (live.get("categoryIds") or []))
    need("H2 anchors kept", live.get("h2") == exp["h2_anchors"], f"{live.get('h2')}")
    need("TOC links point to H2 anchors", sorted(set(live.get("anchors") or [])) == sorted(set(exp["toc_anchors"])))
    need("H3 count", live.get("h3") == exp["h3_count"], f"{live.get('h3')} vs {exp['h3_count']}")
    need("links kept", live.get("links") == exp["link_count"], f"{live.get('links')} vs {exp['link_count']}")
    need("2 images in body", live.get("images") == exp["image_ids"], f"{live.get('images')}")
    kws = live.get("seoKeywords") or []
    need("main SEO keyword set", any(k.get("isMain") and k.get("term") == exp["seo_main_keyword"] for k in kws),
         json.dumps(kws))
    tags = live.get("seoTagTypes") or []
    need("SEO title, description and schema tags present",
         any(t.startswith("title") for t in tags) and "meta:description" in tags and
         any(t.startswith("script") for t in tags), str(tags))
    if exp["publish"]:
        need("post is live", bool(live.get("url")), str(live.get("url")))
        need("live URL uses the SEO slug", (live.get("url") or "").endswith("/post/" + exp["slug"]),
             f"{live.get('url')} (fix: update the draft's seoSlug to '{exp['slug']}' and publish it again)")
    print("\n".join(notes + problems))
    print("\nVERIFIED" if not problems else f"\n{len(problems)} PROBLEM(S)")
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
