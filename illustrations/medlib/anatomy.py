"""Sperm and the female reproductive tract (uterus, cervix, tubes, ovaries), plus the HSG and embryo-transfer views."""
import math
import random

from .core import (catmull, circle, dist, ellipse, ellipse_pts, f, group, inside, lerp, packed_cells, part, path,
                   poisson, polar, pt, smooth_closed, smooth_open, tube, draw_cells)
from .ovary import follicle


# ---------------------------------------------------------------- sperm
def _head_shape(hx, cy, hl, hw):
    """Sperm head outline (flat view), front at hx: a rounded oval that tapers toward the neck at hx + hl."""
    head = []
    for i in range(72):
        t = i / 72 * 2 * math.pi
        u = (1 - math.cos(t)) / 2                      # 0 at front, 1 at back
        half = hw / 2 * max(0.0, 1 - (2 * u - 1) ** 2) ** 0.5 * (1 - 0.38 * u ** 2.4)
        head.append((hx + u * hl, cy - half if t < math.pi else cy + half))
    return head


def _acrosome(head, hx, cy, hl, hw):
    """Cap over the front ~55 % of the head, its back edge gently curved."""
    back_x = hx + hl * 0.56
    top = [p for p in head[:37] if p[0] <= back_x]
    bot = [p for p in head[36:] if p[0] <= back_x]
    edge = [(back_x, cy - hw * 0.36), (back_x - hl * 0.035, cy), (back_x, cy + hw * 0.36)]
    return top + edge + bot


def _sperm_body(x0, cy, L, rnd, cut=True, wave=1.0):
    """Sperm swimming left, head front at (x0, cy), total length L (head about 1/12 of it, as in life x2 for legibility).
    Returns (svg list, anchors)."""
    s = L / 1000.0
    an = {}
    g = []
    hl, hw = 150 * s, 96 * s           # head length and width (flat view, paddle-shaped)
    hx = x0
    # head outline: blunt rounded front, widest at 40 %, tapering to the neck
    head = _head_shape(hx, cy, hl, hw)
    neck_x = hx + hl
    # tail centreline (from the neck to the end piece), a travelling wave growing toward the end
    n = 40
    cl = []
    for i in range(n + 1):
        t = i / n
        x = neck_x + t * (L - hl)
        amp = wave * (6 + 52 * t ** 1.4) * s
        y = cy + amp * math.sin(t * 2.6 * math.pi - 0.4) - amp * math.sin(-0.4) * (1 - t) ** 6
        cl.append((x, y))
    mid_end = 0.22                                     # midpiece: first ~22 % of the flagellum
    widths = []
    for i in range(n + 1):
        t = i / n
        if t < 0.015:
            w = 16 * s
        elif t < mid_end:
            w = 22 * s - 3 * s * t / mid_end
        elif t < 0.93:
            w = 13 * s * (1 - (t - mid_end) / (0.93 - mid_end)) ** 0.7 + 2.4 * s
        else:
            w = 2.2 * s
        widths.append(w)
    outline, c, w, left, right = tube(cl, widths, 4)
    # flagellum (principal piece + end piece) under the midpiece
    g.append(path(smooth_closed(outline[::2]), class_="m-flag"))
    # axoneme highlight along the tail
    k_mid = int(len(c) * mid_end)
    g.append(path(smooth_open(c[k_mid:-2:2]), fill="none", stroke="#FFFFFF", stroke_width=f(2.2 * s), opacity=".55"))
    # midpiece with its helix of mitochondria
    mp = tube(cl[: int(n * mid_end) + 2], widths[: int(n * mid_end) + 2], 4)
    g.append(path(smooth_closed(mp[0]), class_="m-midpiece"))
    mc = mp[1]
    for i in range(2, len(mc) - 2, 2):
        a, b = mc[i - 1], mc[i + 1]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        g.append(ellipse(mc[i][0], mc[i][1], 3.4 * s, mp[2][i] * 0.5, ang + 28, class_="m-mito"))
    # annulus ring where the midpiece ends
    ae = mc[-2]
    g.append(ellipse(ae[0], ae[1], 2.6 * s, mp[2][-2] * 0.55, 0, fill="#9C6B54"))
    # neck (connecting piece)
    g.append(path(smooth_closed([(neck_x - 8 * s, cy - 9 * s), (neck_x + 10 * s, cy - 9 * s), (neck_x + 14 * s, cy),
                                 (neck_x + 10 * s, cy + 9 * s), (neck_x - 8 * s, cy + 9 * s)]), fill="#D8C3D6", stroke="#9F86A6",
                  stroke_width=f(.8 * s)))
    # head: nucleus fills it, the acrosome caps the front 55 %
    g.append(path(smooth_closed(head), class_="m-sp-head"))
    nuc = [(hx + 10 * s + (p[0] - hx) * 0.9, cy + (p[1] - cy) * 0.84) for p in head]
    g.append(path(smooth_closed(nuc), class_="m-sp-nuc"))
    cap = _acrosome(head, hx, cy, hl, hw)
    g.append(path(smooth_closed(cap), class_="m-acro"))
    if cut:  # cut-away: tightly packed DNA strands inside the nucleus
        strands = []
        for r in range(6):
            yy = cy - hw * 0.3 + r * hw * 0.6 / 5
            pts = [(hx + hl * 0.1 + k * hl * 0.82 / 30, yy + 2.2 * s * math.sin(k * 1.3 + r)) for k in range(31)]
            pts = [q for q in pts if inside(nuc, q)]
            if len(pts) > 3:
                strands.append(path(smooth_open(pts), fill="none", stroke="#4E2E7A", stroke_width=f(1.5 * s), opacity=".6",
                                    stroke_linecap="round"))
        g.insert(len(g) - 1, group(strands))
    g.append(path(smooth_closed(head), fill="url(#m-hi)"))
    an["head"] = (hx + hl * 0.5, cy - hw * 0.05)
    an["acrosome"] = (hx + hl * 0.22, cy - hw * 0.3)
    an["nucleus"] = (hx + hl * 0.72, cy + hw * 0.08)
    an["neck"] = (neck_x + 4 * s, cy)
    an["midpiece"] = mc[len(mc) // 2]
    an["annulus"] = ae
    an["tail"] = c[int(len(c) * 0.55)]
    an["end_piece"] = c[int(len(c) * 0.97)]
    an["tip"] = c[-1]
    return g, an


def sperm(pid, cut=True, what=""):
    """One human sperm, head first (swimming left): acrosome cap, nucleus with packed DNA, neck, midpiece with
    mitochondrial helix, principal piece and end piece. viewBox 0 0 1200 300."""
    rnd = random.Random(17)
    g, an = _sperm_body(40, 150, 1120, rnd, cut)
    return part(pid, "0 0 1200 300", what, "".join(g), an)


def sperm_head_dna(pid, broken=False, what=""):
    """Sperm head close-up, cut open, with the DNA as strands: neatly packed (intact) or with breaks (fragmented).
    viewBox 0 0 600 380, head front on the left."""
    rnd = random.Random(23 if broken else 21)
    s = 2.4
    hx, cy, hl, hw = 30, 190, 150 * s, 96 * s
    head = _head_shape(hx, cy, hl, hw)
    nx = hx + hl
    g = []
    # neck and the start of the midpiece
    mp = tube([(nx + 18, cy), (nx + 60, cy + 2), (nx + 130, cy - 4), (nx + 200, cy + 6)], [34, 46, 44, 40], 6)
    g.append(path(smooth_closed(mp[0]), class_="m-midpiece", mask="url(#m-fade-right)"))
    for i in range(2, len(mp[1]) - 2, 2):
        a, b = mp[1][i - 1], mp[1][i + 1]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        g.append(ellipse(mp[1][i][0], mp[1][i][1], 7, mp[2][i] * 0.48, ang + 28, class_="m-mito", mask="url(#m-fade-right)"))
    g.append(path(smooth_closed([(nx - 14, cy - 16), (nx + 22, cy - 15), (nx + 26, cy), (nx + 22, cy + 15), (nx - 14, cy + 16)]),
                  fill="#D8C3D6", stroke="#9F86A6", stroke_width="1.2"))
    g.append(path(smooth_closed(head), class_="m-sp-head"))
    nuc = [(hx + 10 * s + (p[0] - hx) * 0.9, cy + (p[1] - cy) * 0.84) for p in head]
    g.append(path(smooth_closed(nuc), fill="#F1E8F6", stroke="#9C82BC", stroke_width="1.6"))
    # DNA strands: parallel looping fibres, packed side by side (protamine toroids)
    strands = []
    breaks = []
    rows = 9
    for r in range(rows):
        yy = cy - hw * 0.33 + r * (hw * 0.66) / (rows - 1)
        pts = []
        for k in range(46):
            x = hx + hl * 0.12 + k * (hl * 0.8) / 45
            pts.append((x, yy + 5.2 * math.sin(k * 1.3 + r * 0.9)))
        pts = [p for p in pts if inside(nuc, p)]
        if len(pts) < 4:
            continue
        if broken and r in (1, 3, 4, 6, 7):   # break this strand into pieces with gaps
            cuts = sorted(rnd.sample(range(3, len(pts) - 5), 2))
            if cuts[1] - cuts[0] < 6:
                cuts = [cuts[0], min(len(pts) - 5, cuts[0] + 8)]
            segs = [pts[:cuts[0]], [(x, y + 4) for x, y in pts[cuts[0] + 4:cuts[1]]], pts[cuts[1] + 4:]]
            for sg in segs:
                if len(sg) > 1:
                    strands.append(path(smooth_open(sg), fill="none", class_="m-dna-strand"))
            for cpt in cuts:
                breaks.append(lerp(pts[cpt], pts[cpt + 4], 0.5))
        else:
            strands.append(path(smooth_open(pts), fill="none", class_="m-dna-strand"))
    g.append(group(strands))
    for b in breaks:
        g.append(circle(b[0], b[1], 9, fill="none", stroke="#C8323C", stroke_width="2.2"))
    g.append(path(smooth_closed(_acrosome(head, hx, cy, hl, hw)), class_="m-acro", opacity=".42"))
    g.append(path(smooth_closed(head), fill="url(#m-hi)"))
    an = {"head": (hx + hl * 0.5, cy - hw * 0.42), "dna": (hx + hl * 0.7, cy + hw * 0.05), "midpiece": mp[1][len(mp[1]) // 2],
          "nucleus": (hx + hl * 0.72, cy + hw * 0.3), "acrosome": (hx + hl * 0.14, cy - hw * 0.25)}
    if breaks:
        an["break"] = breaks[0]
        an["break_2"] = breaks[-1]
    return part(pid, "0 0 600 380", what, "".join(g), an)


# ---------------------------------------------------------------- female reproductive tract (frontal section)
def _uterus_outline(cx, top, s):
    """Outer wall of the uterus and cervix (frontal), pear-shaped, fundus up."""
    pts = [(-150, 40), (-120, -6), (-60, -26), (0, -30), (60, -26), (120, -6), (150, 40), (158, 110), (146, 190),
           (118, 262), (82, 318), (58, 350), (52, 400), (56, 452), (60, 488), (-60, 488), (-56, 452), (-52, 400),
           (-58, 350), (-82, 318), (-118, 262), (-146, 190), (-158, 110)]
    return [(cx + x * s, top + y * s) for x, y in pts]


def _cavity(cx, top, s, scale=1.0):
    """Triangular uterine cavity tapering into the cervical canal."""
    pts = [(-92, 46), (-50, 40), (0, 44), (50, 40), (92, 46), (70, 110), (40, 190), (14, 262), (8, 300), (6, 380),
           (7, 470), (-7, 470), (-6, 380), (-8, 300), (-14, 262), (-40, 190), (-70, 110)]
    return [(cx + x * s * scale, top + y * s) for x, y in pts]


def _fallopian(cx, top, s, side, rnd):
    """Tube centreline from the uterine horn out to the fimbriae, hanging over the ovary."""
    m = side
    base = [(m * 120, 14), (m * 190, -10), (m * 260, -22), (m * 330, -18), (m * 392, 0), (m * 432, 36), (m * 446, 84),
            (m * 434, 128)]
    return [(cx + x * s, top + y * s) for x, y in base]


def tract(pid, kind="normal", what=""):
    """Female reproductive organs, frontal section: uterus (myometrium, endometrium, cavity), cervix and canal, top of
    the vagina, both fallopian tubes (isthmus, ampulla, fimbriae) and both ovaries with follicles, on their ligaments.
    kind: normal | hsg (contrast fills the cavity and both tubes and spills from the open ends; a catheter in the
    cervix) | transfer (embryo transfer catheter, an embryo placed in the cavity) | blocked (causes of tubal blockage:
    a scar plug closing the left tube at the isthmus, a right hydrosalpinx with a swollen fluid-filled ampulla and
    clubbed, closed fimbriae, filmy adhesions from that tube to the ovary, and endometriosis implants on the
    left broad ligament). viewBox 0 0 1200 760."""
    rnd = random.Random(31)
    cx, top, s = 600, 150, 1.0
    g, an = [], {}
    # broad ligament shadow behind everything
    g.append(path(smooth_closed([(cx - 470, top + 60), (cx - 300, top + 20), (cx, top + 40), (cx + 300, top + 20),
                                 (cx + 470, top + 60), (cx + 300, top + 250), (cx, top + 300), (cx - 300, top + 250)]),
                  fill="#FBEDE8", opacity=".7"))
    # ovarian ligaments (uterus to ovary)
    for m in (-1, 1):
        g.append(path(smooth_open([(cx + m * 135, top + 70), (cx + m * 230, top + 112), (cx + m * 300, top + 140)]),
                      fill="none", stroke="#E9B9A8", stroke_width="13", stroke_linecap="round"))
    # ovaries with follicles
    for m, name in ((-1, "ovary_left"), (1, "ovary_right")):
        ox, oy = cx + m * 365, top + 160
        o = ellipse_pts(ox, oy, 82, 50, m * -14, 72, 0.03, 5 + m)
        g.append(path(smooth_closed(o), fill="url(#m-cortex)", stroke="#C78E7E", stroke_width="1.4"))
        g.append(path(smooth_closed(o), fill="url(#m-stroma)"))
        for (u, v, R, st) in ((-0.38, -0.1, 20, "early_antral"), (0.2, 0.2, 14, "secondary"), (0.45, -0.28, 9, "primary"),
                              (-0.05, -0.45, 7, "primary"), (-0.6, 0.35, 7, "primary")):
            svg, fa = follicle(ox + m * u * 82, oy + v * 50, R, st, rnd.randrange(10 ** 6), 0)
            g.append(svg)
            if R == 20:
                an[f"{name}.follicle"] = fa["centre"]
        if m == 1:   # a mature follicle on the right ovary (the side that ovulates in the fertilization view)
            svg, fa = follicle(ox + 38, oy - 8, 30, "antral", 77, 150)
            g.append(svg)
            an["ovary_right.antral"] = fa["centre"]
            an["ovary_right.egg"] = fa["egg"]
        g.append(path(smooth_closed(o), class_="m-shade"))
        an[name] = (ox - m * 30, oy + 30)
    # fallopian tubes: muscular wall, folded lumen, fimbriae
    for m, name in ((-1, "tube_left"), (1, "tube_right")):
        cl = _fallopian(cx, top, s, m, rnd)
        hydro = kind == "blocked" and m == 1
        if hydro:  # hydrosalpinx: the ampulla swells into a thin-walled, fluid-filled sac with a sealed end
            cl = cl[:-1] + [(cl[-1][0] - 6, cl[-1][1] - 6)]
        widths = [26, 24, 28, 40, 54, 66, 72, 66] if hydro else [26, 24, 26, 34, 42, 50, 58, 60]
        o, c, w, L, R = tube(cl, widths, 8)
        if hydro:  # rounded, closed distal end
            g.append(circle(c[-1][0], c[-1][1], widths[-1] / 2, class_="m-tube"))
        g.append(path(smooth_closed(o), class_="m-tube"))
        lum_w = [3, 3, 6, 24, 40, 52, 58, 52] if hydro else [3, 3, 4, 7, 11, 15, 19, 22]
        lo = tube(cl, lum_w, 8)
        lum_cls = "m-contrast" if kind == "hsg" else "m-hydro" if hydro else "m-tube-lumen"
        if hydro:
            g.append(circle(c[-1][0], c[-1][1], lum_w[-1] / 2, class_="m-hydro"))
        g.append(path(smooth_closed(lo[0]), class_=lum_cls))
        if hydro:  # flattened remnants of the mucosal folds and a highlight on the stretched wall
            for i in range(int(len(c) * 0.45), len(c) - 4, 6):
                p, r = c[i], lo[2][i] / 2
                g.append(path(smooth_open([(p[0] - 4, p[1] - r + 2), (p[0] + 2, p[1] - r + 7), (p[0] + 6, p[1] - r + 2)]),
                              fill="none", stroke="#D98A8E", stroke_width="1.3", opacity=".6"))
            hp = c[int(len(c) * 0.72)]
            g.append(ellipse(hp[0] - 6, hp[1] - 18, 22, 7, -20, fill="#FFFFFF", opacity=".55"))
            an["hydrosalpinx"] = c[int(len(c) * 0.7)]
            an["_hyd_low"] = [((L[i][0] if L[i][1] > R[i][1] else R[i][0]), max(L[i][1], R[i][1]))
                              for i in range(int(len(c) * 0.55), int(len(c) * 0.85), 3)]
        if kind == "blocked" and m == -1:  # scar tissue plug closing the lumen at the isthmus
            i0 = int(len(c) * 0.16)
            cells = []
            for k in range(9):
                p = c[i0 + k]
                cells.append(ellipse(p[0], p[1], 7.5, 10.5, rnd.uniform(-30, 30), class_="m-scar"))
            g.append(group(cells))
            for k in range(8):
                p = c[i0 + 1 + k]
                g.append(path(f"M{f(p[0] - 5)},{f(p[1] - 4 + rnd.uniform(-2, 2))} l10,{f(rnd.uniform(3, 7))}", fill="none",
                              stroke="#B79A8F", stroke_width="1", opacity=".8"))
            an["tube_left.block"] = c[i0 + 4]
        if kind not in ("hsg",) and not hydro:  # mucosal folds of the ampulla
            for i in range(int(len(c) * 0.4), len(c) - 6, 3):
                p = c[i]
                g.append(path(smooth_open([(p[0] - 6, p[1] - lo[2][i] * 0.3), (p[0], p[1]), (p[0] + 5, p[1] + lo[2][i] * 0.3)]),
                              fill="none", stroke="#D98A8E", stroke_width="1.6", opacity=".7"))
        # fimbriae: finger-like fringe around the open end, reaching toward the ovary
        end = c[-1]
        ang = math.atan2(c[-1][1] - c[-4][1], c[-1][0] - c[-4][0])
        if hydro:  # clubbed fimbriae: stubby, fused nubs on the sealed end
            for k in range(5):
                a = ang + (k - 2) * 0.32
                q = (end[0] + math.cos(a) * 34, end[1] + math.sin(a) * 34)
                g.append(ellipse(q[0], q[1], 9, 6, math.degrees(a), class_="m-fimb"))
        for k in range(0 if hydro else 11):
            a = ang + (k - 5) * 0.2
            Lf = rnd.uniform(34, 52)
            p1 = (end[0] + math.cos(a) * Lf * 0.5 + rnd.uniform(-4, 4), end[1] + math.sin(a) * Lf * 0.5)
            p2 = (end[0] + math.cos(a + rnd.uniform(-0.2, 0.2)) * Lf, end[1] + math.sin(a) * Lf)
            ft = tube([(end[0] + math.cos(a) * 6, end[1] + math.sin(a) * 6), p1, p2], [12, 9, 5], 5)
            g.append(path(smooth_closed(ft[0]), class_="m-fimb"))
        an[name] = c[int(len(c) * 0.28)]
        an[name + ".isthmus"] = c[int(len(c) * 0.2)]
        an[name + ".ampulla"] = c[int(len(c) * 0.62)]
        an[name + ".fimbriae"] = (end[0] + math.cos(ang) * (38 if hydro else 40), end[1] + math.sin(ang) * (38 if hydro else 40))
        an[name + ".lumen"] = c[int(len(c) * 0.62)]
        an[name + ".end"] = end
    # uterus: myometrium with muscle bundles
    vag_at = len(g)
    ut = _uterus_outline(cx, top, s)
    g.append(path(smooth_closed(ut), class_="m-myo", filter="url(#m-inner-soft)"))
    g.append(path(smooth_closed(ut), fill="url(#m-myo-fibres)"))
    # endometrium lining the cavity, thicker in the body
    lining = _cavity(cx, top, s, 1.0)
    lin_out = [(cx + (x - cx) * 1.0 + (22 if x > cx else -22 if x < cx else 0) * (1 if y < top + 300 else 0.3),
                y + (-20 if y < top + 60 else 0)) for x, y in lining]
    g.append(path(smooth_closed(lin_out), class_="m-endo"))
    # endometrial glands (short coiled tubes in the lining)
    glands = []
    for i in range(len(lining)):
        a, b = lining[i], lin_out[i]
        if a[1] > top + 280:
            continue
        for t in (0.35, 0.7):
            q = lerp(a, b, 0.5)
            nxt = lining[(i + 1) % len(lining)]
            mid = lerp(lerp(a, nxt, t), lerp(b, lin_out[(i + 1) % len(lin_out)], t), 0.5)
            glands.append(ellipse(mid[0], mid[1], 2.2, 4.2, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + 90,
                                  fill="#F7D3D6", stroke="#C06070", stroke_width=".6"))
    g.append(group(glands))
    cav = [(cx + (x - cx) * 0.78, y + (14 if y < top + 60 else 0)) for x, y in _cavity(cx, top, s, 1.0)]
    if kind == "hsg":
        g.append(path(smooth_closed(cav), class_="m-contrast"))
        # contrast spilling from the open ends into the pelvis
        for m in (-1, 1):
            e = an["tube_left.end" if m < 0 else "tube_right.end"]
            spill = [(e[0] + m * 10, e[1] + 10), (e[0] + m * 42, e[1] + 40), (e[0] + m * 30, e[1] + 86), (e[0] + m * 70, e[1] + 120),
                     (e[0] + m * 96, e[1] + 92), (e[0] + m * 80, e[1] + 44), (e[0] + m * 52, e[1] + 6)]
            g.append(path(smooth_closed(spill), class_="m-contrast", opacity=".75", filter="url(#m-blur2)"))
            for k in range(9):
                d = (e[0] + m * rnd.uniform(30, 110), e[1] + rnd.uniform(20, 150))
                g.append(circle(d[0], d[1], rnd.uniform(2.5, 6), class_="m-contrast", opacity=".7"))
            an["spill_left" if m < 0 else "spill_right"] = (e[0] + m * 64, e[1] + 82)
        an["contrast"] = (cx, top + 120)
    else:
        g.append(path(smooth_closed(cav), class_="m-cavity"))
    # cervix: firmer, paler stroma around the canal, external os at the bottom
    cerv = [(cx - 58, top + 352), (cx + 58, top + 352), (cx + 60, top + 488), (cx - 60, top + 488)]
    canal = [(cx - 7, top + 300), (cx + 7, top + 300), (cx + 9, top + 488), (cx - 9, top + 488)]
    g.append(path(poly_rounded(canal), class_="m-contrast" if kind == "hsg" else "m-cavity"))
    for k in range(6):  # plicae palmatae, the folds of the cervical canal
        y = top + 320 + k * 26
        g.append(path(f"M{f(cx - 7)},{f(y)} l-12,8 M{f(cx + 7)},{f(y)} l12,8", fill="none", stroke="#CF8E8E", stroke_width="1.4"))
    # top of the vagina, cut open, with the fornices around the cervix
    vag = [(cx - 60, top + 470), (cx - 104, top + 500), (cx - 112, top + 600), (cx - 96, top + 640), (cx + 96, top + 640),
           (cx + 112, top + 600), (cx + 104, top + 500), (cx + 60, top + 470)]
    vag_in = [(cx - 60, top + 488), (cx - 84, top + 512), (cx - 88, top + 600), (cx - 80, top + 640), (cx + 80, top + 640),
              (cx + 88, top + 600), (cx + 84, top + 512), (cx + 60, top + 488)]
    gv = [path(smooth_open(vag), class_="m-vag"), path(smooth_open(vag_in), fill="#FBEFF0", stroke="#D79A9A", stroke_width="1.2")]
    g.insert(vag_at, group(gv, mask="url(#m-fade-down)"))
    an["uterus"] = (cx + 128, top + 210)
    an["myometrium"] = (cx - 128, top + 200)
    an["fundus"] = (cx, top - 18)
    an["lining"] = (lin_out[4][0] - 6, lin_out[4][1] + 30)
    an["lining_left"] = (lin_out[-1][0] + 2, lin_out[-1][1] + 16)
    an["cavity"] = (cx, top + 150)
    an["cervix"] = (cx + 44, top + 420)
    an["cervical_canal"] = (cx, top + 400)
    an["vagina"] = (cx + 98, top + 590)
    if kind == "blocked":
        # filmy adhesions: thin translucent bands tethering the swollen right tube to the right ovary
        low = an.pop("_hyd_low")
        ov = (cx + 365, top + 160)
        bands = []
        for k in range(5):
            a = low[min(k * len(low) // 5, len(low) - 1)]
            a = (a[0], a[1] - 3)
            b = (ov[0] - 56 + k * 18, ov[1] - 40 + rnd.uniform(-4, 4))
            mid = (lerp(a, b, 0.5)[0] + rnd.uniform(-10, 10), lerp(a, b, 0.5)[1])
            bands.append(path(smooth_open([a, mid, b]), fill="none", stroke="#E7D2C8", stroke_width=f(rnd.uniform(4, 7)),
                              opacity=".85", stroke_linecap="round"))
            bands.append(path(smooth_open([a, mid, b]), fill="none", stroke="#C9A79A", stroke_width=".9", opacity=".9"))
        g.append(group(bands))
        mid_a = low[len(low) // 2]
        an["adhesions"] = ((mid_a[0] + ov[0] - 20) / 2, (mid_a[1] + ov[1] - 40) / 2)
        # endometriosis implants: dark "powder-burn" and red spots on the left broad ligament, by the ovary
        spots = []
        for (u, v, r, col) in ((-250, 70, 9, "#6E2A33"), (-220, 98, 6, "#8E2F3A"), (-268, 112, 7, "#5E2630"),
                               (-200, 64, 5, "#B23A48"), (-238, 132, 5, "#8E2F3A"), (-184, 110, 6, "#6E2A33"),
                               (-280, 82, 4, "#B23A48")):
            spots.append(ellipse(cx + u, top + v, r * 1.3, r, rnd.uniform(0, 180), fill=col, stroke="#4A1E24",
                                 stroke_width=".6", opacity=".9"))
            spots.append(circle(cx + u - r * 0.3, top + v - r * 0.3, r * 0.3, fill="#FFFFFF", opacity=".25"))
        g.append(group(spots))
        an["endometriosis"] = (cx - 232, top + 96)
    if kind == "hsg":
        cat = tube([(cx, top + 330), (cx, top + 420), (cx + 4, top + 560), (cx + 30, top + 700), (cx + 70, top + 790)],
                   [7, 8, 9, 9, 9], 8)
        g.append(path(smooth_closed(cat[0]), class_="m-catheter"))
        g.append(ellipse(cx, top + 352, 12, 7, 0, fill="#E9EEF0", stroke="#9AA6AD", stroke_width="1"))  # balloon
        an["catheter"] = cat[1][int(len(cat[1]) * 0.62)]
    if kind == "transfer":
        cat = tube([(cx, top + 150), (cx, top + 300), (cx + 2, top + 470), (cx + 20, top + 640), (cx + 50, top + 790)],
                   [5, 6, 7, 8, 9], 8)
        g.append(path(smooth_closed(cat[0]), class_="m-catheter"))
        an["catheter"] = cat[1][int(len(cat[1]) * 0.7)]
        an["embryo"] = (cx + 30, top + 120)
    return part(pid, "0 0 1200 760", what, "".join(g), an)


def poly_rounded(pts):
    return smooth_closed(pts)


def build():
    return [sperm("m-sperm", True, "One sperm, head first: acrosome, nucleus with packed DNA, neck, midpiece, tail, end piece"),
            sperm("m-sperm-plain", False, "One sperm, head first, without the DNA cut-away (for scenes with several sperm)"),
            sperm_head_dna("m-sperm-head-dna", False, "Sperm head cut open: DNA strands neatly packed (intact)"),
            sperm_head_dna("m-sperm-head-dna-broken", True, "Sperm head cut open: DNA strands with breaks (fragmented DNA)"),
            tract("m-tract", "normal", "Uterus, cervix, top of vagina, both fallopian tubes and ovaries, frontal section"),
            tract("m-tract-hsg", "hsg", "HSG: catheter in the cervix, contrast fills the cavity and both tubes and spills out"),
            tract("m-tract-transfer", "transfer", "Embryo transfer: soft catheter through the cervix into the uterine cavity"),
            tract("m-tract-blocked", "blocked", "Blocked tubes: scar plug in the left isthmus, right hydrosalpinx with "
                  "clubbed fimbriae, adhesions to the right ovary, endometriosis implants on the left broad ligament")]
