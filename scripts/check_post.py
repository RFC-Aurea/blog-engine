#!/usr/bin/env python3
"""Quality gate for runs/<run>/post.md. Exit code 1 = the post must not be published.

Usage: python3 scripts/check_post.py runs/<run> [--update <postId>]

Writes runs/<run>/checks.json (the self-audit) and prints a summary.
Hard failures block publishing. Warnings are reported but do not block.
"""
import hashlib
import html
import json
import re
import sys

from common import (ROOT, brand_allowed_urls, config, contains_keyword, core_words, load_json,
                    similarity, split_source, strip_md, words)

SHARED_BANNED = [
    "game-changer", "game changer", "groundbreaking", "revolutionary", "in today's world", "dive into",
    "journey", "landscape", "it's important to note", "comprehensive", "crucial", "delve", "navigate",
    "navigating", "realm", "cutting-edge", "cutting edge", "pivotal", "foster", "leverage", "robust",
    "streamline", "moreover", "furthermore", "it's worth noting", "unlock", "empower", "embark",
    "testament", "tapestry", "holistic approach", "at the end of the day", "in conclusion",
]
BRAND_BANNED = {
    "rfc": ["futile", "futility", "too late", "the door is closed", "give up", "not worth pursuing",
            "your only option", "unfortunately", "sadly", "the hard truth", "hopeless", "no chance",
            "refusing to sell you cycles"],
    "aurea": ["$7,500", "7,500 per cycle", "99% accuracy", "<10%", "less than 10% medication",
              "comparable success rates", "usa's first", "us's first", "first in the us", "first in the u.s",
              "america's first", "nation's first"],
}


def main():
    run = (ROOT / sys.argv[1]).resolve()
    cfg_all = config()
    rules = cfg_all["post_rules"]
    fm, body = split_source((run / "post.md").read_text(encoding="utf-8"))
    brand = fm.get("brand")
    b = cfg_all["brands"][brand]
    sister = cfg_all["brands"]["aurea" if brand == "rfc" else "rfc"]["domain"]
    results = []

    def check(name, ok, detail="", hard=True):
        results.append({"check": name, "ok": bool(ok), "hard": hard, "detail": detail})

    # ---------- front matter ----------
    req = ["brand", "title", "slug", "meta_title", "meta_description", "excerpt", "category",
           "primary_keyword", "secondary_keywords", "images", "date", "cluster_id", "pillar", "format",
           "title_shape"]
    missing = [k for k in req if not fm.get(k)]
    check("front matter complete", not missing, ", ".join(missing))
    if missing:
        return finish(run, results)
    pk = fm["primary_keyword"]
    kw = pk["term"]
    check("primary keyword has real Ubersuggest volume and SD",
          isinstance(pk.get("volume"), (int, float)) and isinstance(pk.get("sd"), (int, float)),
          f"{kw}: volume={pk.get('volume')} sd={pk.get('sd')}")
    sec = fm["secondary_keywords"]
    check("2-3 secondary keywords with volume and SD",
          2 <= len(sec) <= 3 and all(isinstance(s.get("volume"), (int, float)) and
                                     isinstance(s.get("sd"), (int, float)) for s in sec),
          "; ".join(f"{s.get('term')} {s.get('volume')}/{s.get('sd')}" for s in sec))
    check("category exists on this site", fm["category"] in b["categories"], fm["category"])
    check("slug format", re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fm["slug"]) and len(fm["slug"]) <= 80,
          fm["slug"])
    mt, md, ex = fm["meta_title"], fm["meta_description"], fm["excerpt"]
    check(f"meta title <= {rules['meta_title_max']} chars", len(mt) <= rules["meta_title_max"], f"{len(mt)}: {mt}")
    check("meta title has primary keyword near the front", contains_keyword(mt[:45], kw), mt)
    check(f"meta description <= {rules['meta_description_max']} chars", len(md) <= rules["meta_description_max"],
          f"{len(md)}")
    check("meta description has primary keyword", contains_keyword(md, kw), md)
    check(f"excerpt <= {rules['excerpt_max']} chars", 40 <= len(ex) <= rules["excerpt_max"], f"{len(ex)}")
    check("title (H1) has primary keyword", contains_keyword(fm["title"], kw), fm["title"])
    check("title length <= 100", len(fm["title"]) <= 100, f"{len(fm['title'])}")

    # ---------- images ----------
    imgs = fm["images"]
    ok_imgs = all(k in imgs and imgs[k].get("wix_id") and imgs[k].get("width") and imgs[k].get("height")
                  and imgs[k].get("alt") for k in ("IMAGE1", "IMAGE2"))
    check("2 images uploaded to Wix with size and alt text", ok_imgs)
    if ok_imgs:
        alts = [imgs["IMAGE1"]["alt"], imgs["IMAGE2"]["alt"]]
        check(f"alt text under {rules['alt_text_max']} chars", all(len(a) < rules["alt_text_max"] for a in alts),
              str([len(a) for a in alts]))
        check("a keyword appears in an alt text",
              any(contains_keyword(a, k) for a in alts for k in [kw] + [s["term"] for s in sec]))
        check("wix image ids look like real Wix media ids",
              all(re.fullmatch(r"[0-9a-z]+_[0-9a-f]{32}~mv2\.(jpg|jpeg|png|webp)", imgs[k]["wix_id"]) for k in imgs),
              str([imgs[k]["wix_id"] for k in imgs]))
        check("no 'image of' in alt text", not any(re.match(r"(image|picture|photo) of", a.lower()) for a in alts),
              hard=False)
    check("[[IMAGE1]] and [[IMAGE2]] placed once each",
          body.count("[[IMAGE1]]") == 1 and body.count("[[IMAGE2]]") == 1)

    # ---------- structure ----------
    check("no H1 in body", not re.search(r"^#\s", body, re.M))
    check("[[TOC]] once", body.count("[[TOC]]") == 1)
    first_para = next((p.strip() for p in body.split("\n\n") if p.strip()), "")
    check("opens with **Quick answer:**", first_para.startswith("**Quick answer:**"), first_para[:60])
    check("Quick answer has primary keyword", contains_keyword(first_para, kw))
    h2 = re.findall(r"^##\s+(.*?)\s*(?:\{#([a-z0-9-]+)\})?\s*$", body, re.M)
    anchors = [a for _, a in h2]
    check("every H2 has an {#anchor}", all(anchors), str([t for t, a in h2 if not a]))
    check("H2 anchors unique", len(anchors) == len(set(anchors)))
    check("6-10 H2 sections", 6 <= len(h2) <= 10, str(len(h2)))
    check("primary keyword in >= 2 H2s", sum(contains_keyword(t, kw) for t, _ in h2) >= 2,
          str([t for t, _ in h2]))
    check("FAQ section {#faq}", "faq" in anchors)
    check("Bottom line section {#bottom-line}", "bottom-line" in anchors)
    faq_part = body.split("{#faq}")[1].split("\n## ")[0] if "{#faq}" in body else ""
    faqs = re.findall(r"^###\s+(.*)$", faq_part, re.M)
    check(f"{rules['faq_min']}-{rules['faq_max']} FAQ questions as H3",
          rules["faq_min"] <= len(faqs) <= rules["faq_max"], str(len(faqs)))
    check("FAQ questions end with ?", all(q.strip().endswith("?") for q in faqs))
    check("primary keyword in an FAQ question", any(contains_keyword(q, kw) for q in faqs))
    check("has a table with 3+ columns",
          any(len([c for c in l.strip().strip("|").split("|")]) >= 3 for l in body.split("\n")
              if l.strip().startswith("|")))
    check("has a numbered list", bool(re.search(r"^\d+[.)]\s", body, re.M)), hard=False)
    check("markdown bold markers balanced", body.count("**") % 2 == 0)
    check("no raw HTML", not re.search(r"<(a|p|div|span|h\d|img|script|table)\b", body, re.I))
    check("no bare URLs", not re.search(r"(?<!\()https?://\S+", re.sub(r"\[[^\]]*\]\([^)]*\)", "", body)))

    # ---------- words and keyword use ----------
    prose = strip_md(re.sub(r"\[\[[A-Z0-9]+\]\]|\{#[a-z0-9-]+\}|^#+\s|^\|[-:| ]+\|$", "", body, flags=re.M))
    wc = len(words(prose))
    check(f"word count {rules['words_min']}-{rules['words_max']}", rules["words_min"] <= wc <= rules["words_max"],
          str(wc))
    first100 = " ".join(words(prose)[:100])
    check("primary keyword in first 100 words", contains_keyword(first100, kw))
    pk_words = core_words(kw)
    text_core = core_words(prose)
    hits = sum(1 for i in range(len(text_core)) if text_core[i:i + len(pk_words)] == pk_words)
    density = hits * len(words(kw)) / max(wc, 1) * 100
    check("primary keyword density 0.5-2.5%", 0.5 <= density <= 2.5, f"{density:.2f}% ({hits} uses)", hard=False)

    # ---------- links ----------
    links = re.findall(r"\[([^\]]+)\]\(([^)\s]+)\)", body)
    allowed = brand_allowed_urls(brand)
    internal = [u for _, u in links if u.startswith(b["domain"]) or u.startswith("/")]
    bad_internal = sorted({u for u in internal if u.rstrip("/") not in allowed})
    check(f"internal links >= {rules['internal_links_min']}", len(set(internal)) >= rules["internal_links_min"],
          str(len(set(internal))))
    check("every internal link is a verified page or live post", not bad_internal, ", ".join(bad_internal))
    check("no 'click here' link text", not any(t.strip().lower() in ("click here", "here", "this link", "link")
                                               for t, _ in links))
    evidence = load_json(run / "evidence.json", {"sources": []})
    ev_urls = {s["url"].rstrip("/") for s in evidence.get("sources", []) if s.get("verified")}
    external = [u for _, u in links if not (u.startswith(b["domain"]) or u.startswith("/") or u.startswith(sister))]
    unverified = sorted({u for u in external if u.rstrip("/") not in ev_urls})
    check("every external link is a verified source in evidence.json", not unverified, ", ".join(unverified))
    research = {u for u in external if re.search(r"pubmed|ncbi\.nlm\.nih\.gov|doi\.org|academic\.oup|sciencedirect|"
                                                 r"springer|wiley|fertstert|thelancet|nejm|bmj|jamanetwork|"
                                                 r"frontiersin|mdpi|nature\.com|asrm\.org|reproductivefacts\.org|eshre|cdc\.gov|nih\.gov|acog\.org|"
                                                 r"cureus|who\.int", u)}
    check(f"at least {rules['citations_min']} research citations", len(research) >= rules["citations_min"],
          str(len(research)))
    check("citations listed in front matter match evidence",
          {c["url"].rstrip("/") for c in fm.get("citations", [])} <= ev_urls, hard=False)
    check("CTA links the booking page", b["cta_url"] in [u for _, u in links])

    # ---------- language ----------
    low = " " + prose.lower() + " "
    banned = SHARED_BANNED + BRAND_BANNED.get(brand, [])
    found = sorted({w for w in banned if re.search(r"(?<![a-z])" + re.escape(w.lower()) + r"(?![a-z])", low)})
    check("no banned words or unsupported claims", not found, ", ".join(found))
    if brand == "rfc":
        check("RFC: no named physician in the body", "merhi" not in low, hard=False)
    long_paras = [p[:50] for p in body.split("\n\n") if p.strip() and not p.strip().startswith(("|", "-", "#", "[["))
                  and not re.match(r"\d+[.)]\s", p.strip()) and len(re.findall(r"[.!?](\s|$)", p)) > 5]
    check("paragraphs are 5 sentences or fewer", not long_paras, "; ".join(long_paras), hard=False)

    # ---------- what is inside the images ----------
    # Images are labelled illustrations rendered from runs/<run>/img/imageN.html (rules/images.md).
    # Wix's file hash is the md5 of the stored bytes, so it proves Wix holds the exact picture that was reviewed.
    body_plain = strip_md(body)
    for k in ("IMAGE1", "IMAGE2"):
        im = imgs.get(k, {})
        src, png = run / im.get("source", "-"), run / im.get("file", "-")
        if not (src.is_file() and png.is_file()):
            check(f"{k}: source html and rendered png in the run folder", False, f"{im.get('source')} / {im.get('file')}")
            continue
        md5 = hashlib.md5(png.read_bytes()).hexdigest()
        check(f"{k}: Wix stored exactly the reviewed image (md5 = Wix hash)",
              md5 == im.get("md5") == im.get("wix_hash"), f"file {md5}, front matter {im.get('md5')}, Wix {im.get('wix_hash')}")
        rep = load_json(png.with_suffix(".report.json"), {})
        check(f"{k}: label check passed when rendered (no overlaps, nothing cut off)",
              rep.get("ok") is True and rep.get("md5") == md5, "; ".join(rep.get("problems", [])) or "no report for this file")
        texts = " ".join(html.unescape(re.sub(r"<[^>]+>", "", t))
                         for t in re.findall(r"<text\b[^>]*>(.*?)</text>", src.read_text(encoding="utf-8"), re.S))
        lowt = " " + texts.lower() + " "
        bad = sorted({w for w in banned if re.search(r"(?<![a-z])" + re.escape(w.lower()) + r"(?![a-z])", lowt)})
        check(f"{k}: no banned words in the image", not bad, ", ".join(bad))
        nums = {n for n in re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?", texts) if len(n.strip("$%")) > 1 or n[0] == "$" or n[-1] == "%"}
        missing = sorted(n for n in nums if n not in body_plain and n not in body)
        check(f"{k}: every number in the image also appears in the post", not missing, ", ".join(missing))

    # ---------- uniqueness ----------
    pub = load_json("data/published.json", {"posts": []})["posts"]
    if "--update" in sys.argv:  # re-checking a post that is already live: don't compare it with itself
        pub = [p for p in pub if p.get("post_id") != sys.argv[sys.argv.index("--update") + 1]]
    slugs = {p["slug"] for p in pub if p["brand"] == brand}
    check("slug not already used on this site", fm["slug"] not in slugs)
    sims = sorted(((similarity(fm["title"], p["title"]), p["title"]) for p in pub), reverse=True)[:1]
    top = sims[0] if sims else (0, "")
    check("title not too similar to any existing post (< 0.6)", top[0] < 0.6, f"{top[0]:.2f} vs '{top[1]}'")
    kw_dupes = [p["title"] for p in pub if contains_keyword(p["title"], kw) and p.get("primary_keyword") == kw]
    check("primary keyword not already targeted", not kw_dupes, "; ".join(kw_dupes))
    return finish(run, results)


def finish(run, results):
    hard_fail = [r for r in results if r["hard"] and not r["ok"]]
    warn = [r for r in results if not r["hard"] and not r["ok"]]
    out = {"pass": not hard_fail, "hard_failures": len(hard_fail), "warnings": len(warn), "checks": results}
    (run / "checks.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in results:
        mark = "OK  " if r["ok"] else ("FAIL" if r["hard"] else "WARN")
        print(f"{mark} {r['check']}" + (f" — {r['detail']}" if r["detail"] and not r["ok"] else ""))
    print(f"\n{'PASS' if not hard_fail else 'BLOCKED'}: {len(hard_fail)} hard failures, {len(warn)} warnings")
    sys.exit(0 if not hard_fail else 1)


if __name__ == "__main__":
    main()
