#!/usr/bin/env python3
"""Turn a figure spec (RUN/img/imageN.json) into the HTML that scripts/render_image.js renders.

  python3 scripts/figure.py RUN/img/image1.json        # writes RUN/img/image1.html
  python3 scripts/figure.py --anchors m-ovary-section  # lists a part's anchor names and points

Spec (canvas 1200x630, white):
{
  "parts":  [{"use": "m-ovary-section", "name": "ov", "x": 150, "y": 100, "width": 720,
              "rotate": 0, "flip": false, "opacity": 1},
             {"use": "m-syringe", "name": "sy", "width": 460, "rotate": 35, "pin": ["tip", [352, 223]]}],
  "labels": [{"text": "Resting follicles", "sub": "optional second line", "x": 520, "y": 52,
              "align": "start|middle|end", "to": "ov.resting_follicles"  (or [x, y] on the canvas, or a list of them)}],
  "panels": [{"text": "A", "x": 24, "y": 44}],
  "svg": "optional raw SVG drawn above the parts and below the labels (arrows, brackets)"
}
Parts come from illustrations/medical.svg (catalogue: illustrations/medical_parts.json). A label's "to" names an
anchor of a placed part ("<part name>.<anchor>"); the leader line runs from the label to that exact point, so it ends on
the structure named. Keep labels on white space: the renderer fails a label that sits on a drawing.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = json.loads((ROOT / "illustrations" / "medical_parts.json").read_text())
FONT, SUB = 19, 17


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def place(p):
    meta = PARTS[p["use"]]
    _, _, vw, vh = [float(v) for v in meta["viewBox"].split()]
    w = float(p["width"])
    h = w * vh / vw
    rot = float(p.get("rotate", 0))
    flip = bool(p.get("flip", False))
    if "pin" in p:  # put a named anchor of the part on a canvas point (after flip and rotation)
        name, (tx, ty) = p["pin"]
        ax, ay = meta["anchors"][name]
        dx, dy = ax * w / vw - w / 2, ay * h / vh - h / 2
        if flip:
            dx = -dx
        a = math.radians(rot)
        cx, cy = tx - (dx * math.cos(a) - dy * math.sin(a)), ty - (dx * math.sin(a) + dy * math.cos(a))
        x, y = cx - w / 2, cy - h / 2
    else:
        x, y = float(p["x"]), float(p["y"])
        cx, cy = x + w / 2, y + h / 2

    def tf(ax, ay):
        px, py = x + ax * w / vw, y + ay * h / vh
        if flip:
            px = 2 * cx - px
        a = math.radians(rot)
        dx, dy = px - cx, py - cy
        return (cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))

    trs = []
    if rot:
        trs.append(f"rotate({rot:g} {cx:.1f} {cy:.1f})")
    if flip:
        trs.append(f"matrix(-1 0 0 1 {2 * cx:.1f} 0)")
    tr = f' transform="{" ".join(trs)}"' if trs else ""
    op = f' opacity="{p["opacity"]}"' if "opacity" in p else ""
    svg = f'<use href="#{p["use"]}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{tr}{op}/>'
    return svg, {k: tf(*v) for k, v in meta["anchors"].items()}


def text_box(lab):
    """Approximate box of a label (refined by the renderer's real measurements)."""
    lines = [(lab["text"], FONT)] + ([(lab["sub"], SUB)] if lab.get("sub") else [])
    w = max(len(t) * s * 0.52 for t, s in lines)
    h = FONT + (SUB + 4 if lab.get("sub") else 0)
    x, y = float(lab["x"]), float(lab["y"])
    al = lab.get("align", "start")
    x0 = x if al == "start" else x - w if al == "end" else x - w / 2
    return x0, y - FONT * 0.8, w, h


def leader_start(box, target):
    x0, y0, w, h = box
    tx, ty = target
    # leave from the side of the label facing the target
    if tx < x0 - 4:
        return (x0 - 7, y0 + FONT * 0.42)
    if tx > x0 + w + 4:
        return (x0 + w + 7, y0 + FONT * 0.42)
    return (min(max(tx, x0 + 6), x0 + w - 6), y0 - 5 if ty < y0 else y0 + h + 6)


def build(spec):
    anchors, uses = {}, []
    for p in spec.get("parts", []):
        svg, an = place(p)
        uses.append(svg)
        for k, v in an.items():
            anchors[f'{p.get("name", p["use"])}.{k}'] = v
    out = []
    for lab in spec.get("labels", []):
        box = text_box(lab)
        tos = lab.get("to") or []
        if isinstance(tos, str) or (isinstance(tos, list) and tos and isinstance(tos[0], (int, float))):
            tos = [tos]
        for t in tos:
            if isinstance(t, str):
                if t not in anchors:
                    sys.exit(f"unknown anchor {t}; known: {', '.join(sorted(anchors))}")
                t = anchors[t]
            s = leader_start(box, t)
            out.append(f'<path class="leader" d="M{s[0]:.1f},{s[1]:.1f} L{t[0]:.1f},{t[1]:.1f}"/>'
                       f'<circle class="leader-dot" cx="{t[0]:.1f}" cy="{t[1]:.1f}" r="3.2"/>')
        al = {"start": "start", "middle": "middle", "end": "end"}[lab.get("align", "start")]
        out.append(f'<text class="m-label" x="{lab["x"]}" y="{lab["y"]}" text-anchor="{al}">{esc(lab["text"])}</text>')
        if lab.get("sub"):
            out.append(f'<text class="m-label-sub" x="{lab["x"]}" y="{float(lab["y"]) + SUB + 5}" text-anchor="{al}">{esc(lab["sub"])}</text>')
    for pn in spec.get("panels", []):
        out.append(f'<text class="m-panel" x="{pn["x"]}" y="{pn["y"]}">{esc(pn["text"])}</text>')
    style = (".m-label{font-size:19px;font-weight:500;fill:#2E2A27 !important}"
             ".m-label-sub{font-size:17px;font-weight:400;fill:#6B635C !important}"
             ".m-panel{font-size:26px;font-weight:700;fill:#2E2A27 !important}"
             ".leader{fill:none;stroke:#5A5450;stroke-width:1.15}.leader-dot{fill:#3F3A36}")
    return ("<!doctype html><html><head><meta charset=\"utf-8\"><style>{{BASE_CSS}}" + style + "</style></head><body>\n"
            '<svg class="canvas" viewBox="0 0 1200 630" xmlns="http://www.w3.org/2000/svg">\n{{MEDICAL}}\n'
            '<rect class="bg" width="1200" height="630"/>\n' + "\n".join(uses) + "\n" + spec.get("svg", "") + "\n"
            + "\n".join(out) + "\n</svg></body></html>\n"), anchors


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--anchors":
        meta = PARTS[sys.argv[2]]
        print(sys.argv[2], "viewBox", meta["viewBox"], "-", meta["what"])
        for k, v in meta["anchors"].items():
            print(f"  {k}: {v}")
        return
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    html, _ = build(json.loads(src.read_text()))
    dst = src.with_suffix(".html")
    dst.write_text(html)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
