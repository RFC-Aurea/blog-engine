#!/usr/bin/env python3
"""Build a Wix "Create Draft Post" payload from runs/<run>/post.md.

Usage: python3 scripts/build_post.py runs/<run> [--draft]

Writes, inside the run folder:
  payload.json   body for POST https://www.wixapis.com/blog/v3/draft-posts (one line, compact)
  expected.json  what the live post should contain (used by verify_live.py)
  preview.html   a local approximation of the post with brand colours, for a visual check
"""
import html
import json
import re
import sys

from common import ROOT, config, split_source, strip_md

INLINE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)|\*\*|\*")


class Builder:
    def __init__(self, brand_cfg, fm):
        self.b = brand_cfg
        self.fm = fm
        self.colors = brand_cfg["colors"]
        self.color_body = config().get("color_body_text", True)
        self.n = 0
        self.h2 = []          # (anchor, plain text)
        self.faq = []         # (question, answer plain)
        self.links = []
        self.images = []
        self.in_faq = False

    # ---------- ids ----------
    def nid(self):
        self.n += 1
        return f"e{self.n:03d}"

    # ---------- inline ----------
    def runs(self, text, bold=False, italic=False, link=None):
        out, pos = [], 0
        for m in INLINE.finditer(text):
            if m.start() > pos:
                out.append([text[pos:m.start()], bold, italic, link])
            tok = m.group(0)
            if tok == "**":
                bold = not bold
            elif tok == "*":
                italic = not italic
            else:
                out.extend(self.runs(m.group(1), bold, italic, m.group(2)))
            pos = m.end()
        if pos < len(text):
            out.append([text[pos:], bold, italic, link])
        merged = []
        for r in out:
            if merged and merged[-1][1:] == r[1:]:
                merged[-1][0] += r[0]
            elif r[0]:
                merged.append(r)
        return merged

    def text_nodes(self, text, color=None, force_bold=False):
        nodes = []
        for t, bold, italic, link in self.runs(text):
            decos = []
            if bold or force_bold:
                decos.append({"type": "BOLD", "fontWeightValue": 700})
            if italic:
                decos.append({"type": "ITALIC", "italicData": True})
            c = color or (self.colors["body"] if (self.color_body or link) else None)
            if c:
                decos.append({"type": "COLOR", "colorData": {"foreground": c}})
            if link:
                internal = link.startswith(self.b["domain"]) or link.startswith("/")
                decos.append({"type": "LINK", "linkData": {"link": {
                    "url": link, "target": "SELF" if internal else "BLANK"}}})
                decos.append({"type": "UNDERLINE"})
                self.links.append(link)
            node = {"type": "TEXT", "id": "", "nodes": [], "textData": {"text": t, "decorations": decos}}
            nodes.append(node)
        return nodes

    # ---------- blocks ----------
    def para(self, text):
        return {"type": "PARAGRAPH", "id": self.nid(), "nodes": self.text_nodes(text), "paragraphData": {}}

    def spacer(self):
        return {"type": "PARAGRAPH", "id": self.nid(), "nodes": [], "paragraphData": {}}

    def heading(self, level, text, anchor=None):
        color = {2: self.colors["h2"], 3: self.colors["h3"], 4: self.colors["h4"]}[level]
        if level == 3 and self.in_faq:
            color = self.colors["faq_h3"]
        return {"type": "HEADING", "id": anchor or self.nid(),
                "nodes": self.text_nodes(text, color=color),
                "headingData": {"level": level, "textStyle": {"textAlignment": "AUTO"}}}

    def list_node(self, items, ordered):
        lis = [{"type": "LIST_ITEM", "id": self.nid(), "nodes": [self.para(i)]} for i in items]
        if ordered:
            return {"type": "ORDERED_LIST", "id": self.nid(), "nodes": lis, "orderedListData": {"indentation": 0}}
        return {"type": "BULLETED_LIST", "id": self.nid(), "nodes": lis, "bulletedListData": {"indentation": 0}}

    def table(self, rows):
        ncol = max(len(r) for r in rows)
        rows = [r + [""] * (ncol - len(r)) for r in rows]
        lens = [max(8, min(60, max(len(strip_md(r[c])) for r in rows))) for c in range(ncol)]
        tr = []
        for ri, r in enumerate(rows):
            cells = []
            for cell in r:
                cdata = {}
                if ri == 0:
                    cdata = {"cellStyle": {"backgroundColor": self.b.get("table_header_bg", "#F4F3F0")}}
                cells.append({"type": "TABLE_CELL", "id": self.nid(), "nodes": [{
                    "type": "PARAGRAPH", "id": self.nid(), "paragraphData": {},
                    "nodes": self.text_nodes(cell, force_bold=(ri == 0))}], "tableCellData": cdata})
            tr.append({"type": "TABLE_ROW", "id": self.nid(), "nodes": cells})
        return {"type": "TABLE", "id": self.nid(), "nodes": tr, "tableData": {
            "dimensions": {"colsWidthRatio": [l * 10 for l in lens], "rowsHeight": [0] * len(rows),
                           "colsMinWidth": [120] * ncol},
            "rowHeader": True}}

    def image(self, key):
        img = self.fm["images"][key]
        self.images.append(img)
        return {"type": "IMAGE", "id": self.nid(), "nodes": [], "imageData": {
            "containerData": {"width": {"size": "CONTENT"}, "alignment": "CENTER", "textWrap": True},
            "image": {"src": {"id": img["wix_id"]}, "width": int(img["width"]), "height": int(img["height"])},
            "altText": img["alt"]}}

    def toc(self):
        items = []
        for anchor, text in self.h2:
            items.append({"type": "LIST_ITEM", "id": self.nid(), "nodes": [{
                "type": "PARAGRAPH", "id": self.nid(), "paragraphData": {}, "nodes": [{
                    "type": "TEXT", "id": "", "nodes": [], "textData": {"text": text, "decorations": [
                        {"type": "ANCHOR", "anchorData": {"anchor": anchor}},
                        {"type": "COLOR", "colorData": {"foreground": self.colors["toc_link"]}},
                        {"type": "UNDERLINE"}]}}]}]})
        label = {"type": "PARAGRAPH", "id": self.nid(), "paragraphData": {}, "nodes": [{
            "type": "TEXT", "id": "", "nodes": [], "textData": {"text": "In this article", "decorations": [
                {"type": "BOLD", "fontWeightValue": 700},
                {"type": "COLOR", "colorData": {"foreground": self.colors["h2"]}}]}}]}
        lst = {"type": "BULLETED_LIST", "id": self.nid(), "nodes": items, "bulletedListData": {"indentation": 0}}
        sp = self.spacer()
        self.toc_ids = {label["id"], lst["id"], sp["id"]}
        self.toc_label_id = label["id"]
        return [label, lst, sp]

    # ---------- document ----------
    def parse_blocks(self, body):
        """Markdown body -> list of (kind, data) blocks."""
        blocks, lines, i = [], body.split("\n"), 0
        while i < len(lines):
            line = lines[i].rstrip()
            s = line.strip()
            if not s:
                i += 1
                continue
            m = re.match(r"^(#{2,4})\s+(.*?)\s*(?:\{#([a-z0-9-]+)\})?$", s)
            if s.startswith("# "):
                raise SystemExit(f"H1 found in body (the title is the H1): {s[:60]}")
            if m:
                blocks.append(("h", (len(m.group(1)), m.group(2), m.group(3))))
                i += 1
                continue
            if re.fullmatch(r"\[\[(TOC|IMAGE1|IMAGE2)\]\]", s):
                blocks.append((s[2:-2].lower(), None))
                i += 1
                continue
            if re.match(r"^[-*]\s+", s) or re.match(r"^\d+[.)]\s+", s):
                ordered = bool(re.match(r"^\d+[.)]\s+", s))
                pat = r"^\d+[.)]\s+" if ordered else r"^[-*]\s+"
                items = []
                while i < len(lines) and re.match(pat, lines[i].strip()):
                    items.append(re.sub(pat, "", lines[i].strip()))
                    i += 1
                blocks.append(("ol" if ordered else "ul", items))
                continue
            if s.startswith("|"):
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                        rows.append(cells)
                    i += 1
                blocks.append(("table", rows))
                continue
            if s.startswith(">"):
                q = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    q.append(lines[i].strip().lstrip(">").strip())
                    i += 1
                blocks.append(("quote", " ".join(q)))
                continue
            p = []
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^(#{1,4}\s|[-*]\s|\d+[.)]\s|\||>|\[\[)", lines[i].strip()):
                p.append(lines[i].strip())
                i += 1
            blocks.append(("p", " ".join(p)))
        return blocks

    def build(self, body):
        blocks = self.parse_blocks(body)
        for kind, data in blocks:
            if kind == "h" and data[0] == 2:
                if not data[2]:
                    raise SystemExit(f"H2 without {{#anchor}}: {data[1]}")
                self.h2.append((data[2], strip_md(data[1])))
        nodes, self.in_faq, toc_done = [], False, False
        cur_q = None
        for kind, data in blocks:
            if kind == "h":
                level, text, anchor = data
                if level == 2:
                    self.in_faq = anchor == "faq"
                    if nodes and not (nodes[-1]["type"] == "PARAGRAPH" and not nodes[-1]["nodes"]):
                        nodes.append(self.spacer())
                if self.in_faq and level == 3:
                    cur_q = [strip_md(text), []]
                    self.faq.append(cur_q)
                elif level == 2:
                    cur_q = None
                nodes.append(self.heading(level, text, anchor if level == 2 else None))
            elif kind == "p":
                nodes.append(self.para(data))
                if cur_q is not None:
                    cur_q[1].append(strip_md(data))
            elif kind in ("ul", "ol"):
                nodes.append(self.list_node(data, kind == "ol"))
                if cur_q is not None:
                    cur_q[1].append(" ".join(strip_md(x) for x in data))
            elif kind == "table":
                nodes.append(self.table(data))
            elif kind == "quote":
                nodes.append({"type": "BLOCKQUOTE", "id": self.nid(), "nodes": [self.para(data)],
                              "blockquoteData": {"indentation": 1}})
            elif kind == "toc":
                nodes.extend(self.toc())
                toc_done = True
            elif kind in ("image1", "image2"):
                nodes.extend([self.image(kind.upper()), self.spacer()])
        if not toc_done:
            raise SystemExit("[[TOC]] is missing")
        return nodes


def compact_runs(text_nodes):
    out = []
    for t in text_nodes:
        flags, link = "", None
        for d in t["textData"]["decorations"]:
            if d["type"] == "BOLD":
                flags += "b"
            elif d["type"] == "ITALIC":
                flags += "i"
            elif d["type"] == "LINK":
                link = d["linkData"]["link"]["url"]
        r = [t["textData"]["text"]]
        if flags or link:
            r.append(flags)
        if link:
            r.append(link)
        out.append(r)
    return out


def to_compact(nodes, bld):
    """Full Ricos nodes -> compact block list expanded again by templates/publish.js."""
    doc = []
    for n in nodes:
        t = n["type"]
        if n["id"] in getattr(bld, "toc_ids", ()):
            if n["id"] == bld.toc_label_id:
                doc.append(["toc", [[a, txt] for a, txt in bld.h2]])
            continue
        if t == "PARAGRAPH":
            doc.append(["p", compact_runs(n["nodes"])] if n["nodes"] else ["sp"])
        elif t == "HEADING":
            lv = n["headingData"]["level"]
            color = n["nodes"][0]["textData"]["decorations"][-1]["colorData"]["foreground"] if n["nodes"] else None
            doc.append(["h", lv, n["id"] if lv == 2 else None, color, compact_runs(n["nodes"])])
        elif t in ("BULLETED_LIST", "ORDERED_LIST"):
            doc.append(["ul" if t == "BULLETED_LIST" else "ol",
                        [compact_runs(li["nodes"][0]["nodes"]) for li in n["nodes"]]])
        elif t == "TABLE":
            doc.append(["table", n["tableData"]["dimensions"]["colsWidthRatio"],
                        [[compact_runs(cell["nodes"][0]["nodes"]) for cell in row["nodes"]] for row in n["nodes"]]])
        elif t == "IMAGE":
            d = n["imageData"]
            doc.append(["img", d["image"]["src"]["id"], d["image"]["width"], d["image"]["height"], d["altText"]])
        elif t == "BLOCKQUOTE":
            doc.append(["q", compact_runs(n["nodes"][0]["nodes"])])
        else:
            raise SystemExit(f"no compact form for node type {t}")
    return doc


def seo_data(fm, b, cfg_all, faq):
    url = b["post_base"] + fm["slug"]
    writer = cfg_all["writer"]
    hero = fm["images"][fm.get("hero", "IMAGE1")]
    person = {"@type": "Person", "name": writer["name"],
              "url": b["domain"] + ("/our-doctors" if b["short"] == "RFC" else "/about-aurea"),
              "jobTitle": "Reproductive Endocrinologist, Founder and Medical Director",
              "worksFor": {"@type": "MedicalClinic", "name": b["name"], "url": b["domain"]}}
    graph = [{
        "@type": "MedicalWebPage",
        "@id": url + "#webpage",
        "url": url,
        "headline": fm["title"],
        "name": fm["meta_title"],
        "description": fm["meta_description"],
        "datePublished": fm["date"],
        "dateModified": fm["date"],
        "lastReviewed": fm["date"],
        "inLanguage": "en-US",
        "author": person,
        "reviewedBy": person,
        "publisher": {"@type": "MedicalClinic", "name": b["name"], "url": b["domain"]},
        "image": "https://static.wixstatic.com/media/" + hero["wix_id"],
        "keywords": ", ".join([fm["primary_keyword"]["term"]] + [k["term"] for k in fm["secondary_keywords"]]),
        "medicalAudience": {"@type": "MedicalAudience", "audienceType": "Patient"},
        "citation": [e["url"] for e in fm.get("citations", [])],
        "mainEntityOfPage": url,
    }]
    if faq:
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": " ".join(a)}}
            for q, a in faq]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    kws = [{"term": fm["primary_keyword"]["term"], "isMain": True}] + [
        {"term": k["term"], "isMain": False} for k in fm["secondary_keywords"]]
    return {
        "tags": [
            {"type": "title", "children": fm["meta_title"], "custom": False, "disabled": False},
            {"type": "meta", "props": {"name": "description", "content": fm["meta_description"]},
             "children": "", "custom": False, "disabled": False},
            {"type": "meta", "props": {"property": "og:title", "content": fm["meta_title"]},
             "children": "", "custom": False, "disabled": False},
            {"type": "meta", "props": {"property": "og:description", "content": fm["meta_description"]},
             "children": "", "custom": False, "disabled": False},
            {"type": "script", "props": {"type": "application/ld+json"}, "children": ld,
             "custom": False, "disabled": False},
        ],
        "settings": {"preventAutoRedirect": False, "keywords": kws[: cfg_all["post_rules"]["seo_keywords_max"]]},
    }


def preview_html(fm, b, nodes):
    c = b["colors"]

    def txt(n):
        t = html.escape(n["textData"]["text"])
        style, href, anchor = [], None, None
        for d in n["textData"]["decorations"]:
            if d["type"] == "BOLD":
                t = f"<b>{t}</b>"
            elif d["type"] == "ITALIC":
                t = f"<i>{t}</i>"
            elif d["type"] == "COLOR":
                style.append(f"color:{d['colorData']['foreground']}")
            elif d["type"] == "UNDERLINE":
                style.append("text-decoration:underline")
            elif d["type"] == "LINK":
                href = d["linkData"]["link"]["url"]
            elif d["type"] == "ANCHOR":
                anchor = "#" + d["anchorData"]["anchor"]
        t = f'<span style="{";".join(style)}">{t}</span>'
        if href or anchor:
            t = f'<a href="{html.escape(href or anchor)}">{t}</a>'
        return t

    def render(n):
        kids = "".join(render(k) if k["type"] != "TEXT" else txt(k) for k in n.get("nodes", []))
        t = n["type"]
        if t == "PARAGRAPH":
            return f"<p>{kids or '&nbsp;'}</p>"
        if t == "HEADING":
            lv = n["headingData"]["level"]
            return f'<h{lv} id="{n["id"]}">{kids}</h{lv}>'
        if t == "BULLETED_LIST":
            return f"<ul>{kids}</ul>"
        if t == "ORDERED_LIST":
            return f"<ol>{kids}</ol>"
        if t == "LIST_ITEM":
            return f"<li>{kids}</li>"
        if t == "BLOCKQUOTE":
            return f"<blockquote>{kids}</blockquote>"
        if t == "TABLE":
            return f"<table>{kids}</table>"
        if t == "TABLE_ROW":
            return f"<tr>{kids}</tr>"
        if t == "TABLE_CELL":
            bg = n.get("tableCellData", {}).get("cellStyle", {}).get("backgroundColor")
            return f'<td style="{"background:" + bg if bg else ""}">{kids}</td>'
        if t == "IMAGE":
            d = n["imageData"]
            key = next((k for k, v in fm["images"].items() if v["wix_id"] == d["image"]["src"]["id"]), "")
            src = fm["images"].get(key, {}).get("preview_src") or ""
            return (f'<figure><img src="{html.escape(src)}" alt="{html.escape(d["altText"])}">'
                    f'<figcaption>{key} · alt: {html.escape(d["altText"])}</figcaption></figure>')
        return kids

    body = "".join(render(n) for n in nodes)
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(fm['title'])}</title>
<style>body{{font-family:Georgia,serif;max-width:740px;margin:40px auto;padding:0 16px;line-height:1.6;color:#000}}
h1{{font-size:34px;line-height:1.2}} h2{{font-size:26px;margin-top:28px}} h3{{font-size:20px}}
table{{border-collapse:collapse;width:100%;font-size:15px}} td{{border:1px solid #ccc;padding:8px;vertical-align:top}}
img{{max-width:100%;background:#eee;min-height:120px;display:block}} figcaption{{font-size:12px;color:#666}}
blockquote{{border-left:3px solid #ccc;margin-left:0;padding-left:16px}}
.meta{{font:13px/1.4 sans-serif;color:#555;border:1px dashed #bbb;padding:10px;margin-bottom:24px}}</style></head>
<body><div class="meta"><b>{html.escape(b['name'])}</b> · by Dr. Zaher Merhi · {html.escape(fm['category'])}<br>
SEO title: {html.escape(fm['meta_title'])}<br>Meta description: {html.escape(fm['meta_description'])}<br>
URL: {html.escape(b['post_base'] + fm['slug'])}</div>
<h1>{html.escape(fm['title'])}</h1>{body}</body></html>"""


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    run = (ROOT / sys.argv[1]).resolve()
    publish = "--draft" not in sys.argv
    cfg_all = config()
    fm, body = split_source((run / "post.md").read_text(encoding="utf-8"))
    b = cfg_all["brands"][fm["brand"]]
    bld = Builder(b, fm)
    nodes = bld.build(body)
    cat = b["categories"].get(fm["category"])
    if not cat:
        raise SystemExit(f"unknown category for {fm['brand']}: {fm['category']}")
    hero = fm["images"][fm.get("hero", "IMAGE1")]
    draft = {
        "title": fm["title"],
        "excerpt": fm["excerpt"],
        "memberId": cfg_all["writer"]["member_id"],
        "categoryIds": [cat],
        "hashtags": fm.get("hashtags", []),
        "commentingEnabled": True,
        "language": "en",
        "seoSlug": fm["slug"],
        "seoData": seo_data(fm, b, cfg_all, bld.faq),
        "media": {"wixMedia": {"image": {"id": hero["wix_id"]}}, "displayed": True, "custom": True,
                  "altText": hero["alt"]},
        "richContent": {"nodes": nodes},
    }
    payload = {"draftPost": draft, "publish": publish, "fieldsets": ["URL"]}
    (run / "payload.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    slim = {k: v for k, v in draft.items() if k != "richContent"}
    colors = {"body": b["colors"]["body"], "colorBody": cfg_all.get("color_body_text", True),
              "toc": b["colors"]["toc_link"], "tocLabel": b["colors"]["h2"], "domain": b["domain"],
              "headerBg": b.get("table_header_bg", "#F4F3F0")}
    compact = {"publish": publish, "colors": colors, "draftPost": slim, "doc": to_compact(nodes, bld)}
    (run / "compact.json").write_text(json.dumps(compact, ensure_ascii=False, separators=(",", ":")),
                                      encoding="utf-8")
    expected = {
        "site_id": b["site_id"],
        "slug": fm["slug"],
        "title": fm["title"],
        "member_id": cfg_all["writer"]["member_id"],
        "category_id": cat,
        "h2_anchors": [a for a, _ in bld.h2],
        "h2_count": len(bld.h2),
        "h3_count": sum(1 for n in nodes if n["type"] == "HEADING" and n["headingData"]["level"] == 3),
        "toc_anchors": [a for a, _ in bld.h2],
        "link_count": len(bld.links),
        "image_ids": [i["wix_id"] for i in bld.images],
        "faq_count": len(bld.faq),
        "seo_main_keyword": fm["primary_keyword"]["term"],
        "meta_title": fm["meta_title"],
        "publish": publish,
    }
    (run / "expected.json").write_text(json.dumps(expected, indent=1, ensure_ascii=False), encoding="utf-8")
    (run / "preview.html").write_text(preview_html(fm, b, nodes), encoding="utf-8")
    size = (run / "payload.json").stat().st_size
    print(json.dumps({"ok": True, "payload_bytes": size, "compact_bytes": (run / "compact.json").stat().st_size, "nodes": len(nodes), "h2": len(bld.h2),
                      "faq": len(bld.faq), "links": len(bld.links), "publish": publish}))


if __name__ == "__main__":
    main()
