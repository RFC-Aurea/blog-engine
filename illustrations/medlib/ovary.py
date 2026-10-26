"""Ovarian follicles at every stage (drawn cell by cell) and ovary cross-sections."""
import math
import random

from .core import (area, cell_layer, circle, dist, ellipse, ellipse_pts, fibres, group, inside, packed_cells, part,
                   path, poisson, polar, pt, resample, normals, draw_cells, sector_cells, smooth_closed, smooth_open,
                   vessel_tree, f)


def oocyte(cx, cy, r, rnd, gv=True):
    """Egg: cytoplasm with fine granules and (in growing follicles) the germinal vesicle nucleus."""
    g = [circle(cx, cy, r, class_="m-oo")]
    for _ in range(int(r * r * 0.05)):
        a, rr = rnd.uniform(0, 6.283), r * math.sqrt(rnd.uniform(0, 0.85))
        g.append(circle(cx + rr * math.cos(a), cy + rr * math.sin(a), max(0.35, r * 0.018), fill="#D9B999", opacity="0.5"))
    if gv:
        nx, ny = cx + r * 0.14, cy - r * 0.08
        g.append(circle(nx, ny, r * 0.34, class_="m-gv"))
        g.append(circle(nx + r * 0.05, ny - r * 0.04, r * 0.1, class_="m-nl"))
    return g


def follicle(cx, cy, R, stage, seed=0, rot=0.0):
    """One follicle in section. stage: primordial | primary | secondary | early_antral | antral | cl | albicans.
    Returns (svg, anchors)."""
    rnd = random.Random(seed)
    g, an = [], {"centre": (cx, cy)}
    if stage == "primordial":
        ro = R * 0.7
        g += oocyte(cx, cy, ro, rnd)
        n = rnd.randint(5, 7)
        g += sector_cells(cx, cy, ro * 1.01, R, n, rnd, "m-pg", "m-gcn", a_start=rnd.uniform(0, 6.28), gap=R * 0.12, nuc=0.32)
        an["egg"] = (cx, cy)
    elif stage == "primary":
        ro = R * 0.56
        g.append(circle(cx, cy, R * 0.99, class_="m-bm"))
        g += sector_cells(cx, cy, R * 0.64, R * 0.97, rnd.randint(14, 17), rnd, "m-gc", "m-gcn", a_start=rnd.uniform(0, 6.28),
                          gap=R * 0.05, nuc=0.27, flat=False)
        g.append(circle(cx, cy, R * 0.62, class_="m-zona"))
        g += oocyte(cx, cy, ro, rnd)
        an["egg"] = (cx, cy)
        an["granulosa"] = polar(cx, cy, R * 0.8, -0.8)
    elif stage in ("secondary", "early_antral"):
        early = stage == "early_antral"
        ro = R * (0.27 if early else 0.33)
        zr = ro * 1.2
        g.append(circle(cx, cy, R, class_="m-the"))
        g += cell_layer(cx, cy, R * 0.86, R * 1.0, R * 0.075, rnd, "m-th", "m-thn", nuc=0.26, flat=True)
        for _ in range(4):
            a = rnd.uniform(0, 6.28)
            g.append(path(f"M{pt(polar(cx, cy, R * 0.93, a))}A{f(R * 0.93)},{f(R * 0.93)} 0 0,1 {pt(polar(cx, cy, R * 0.93, a + 0.5))}", class_="m-cap"))
        g.append(circle(cx, cy, R * 0.855, class_="m-bm"))
        g += cell_layer(cx, cy, zr, R * 0.85, R * (0.085 if early else 0.1), rnd, "m-gc", "m-gcn", nuc=0.28)
        if early:  # first pools of follicle fluid between the granulosa cells
            for k in range(rnd.randint(3, 4)):
                a = rot + 0.9 + k * 1.05 + rnd.uniform(-0.2, 0.2)
                c = polar(cx, cy, R * 0.6, a)
                pts = ellipse_pts(c[0], c[1], R * rnd.uniform(0.09, 0.14), R * rnd.uniform(0.06, 0.09), math.degrees(a) + 90, 16, 0.25, seed + k)
                g.append(path(smooth_closed(pts), class_="m-antrum", stroke="#E7C67A", stroke_width=".5"))
        g.append(circle(cx, cy, zr, class_="m-zona"))
        g += oocyte(cx, cy, ro, rnd)
        an.update(egg=(cx, cy), granulosa=polar(cx, cy, R * 0.6, -0.6), theca=polar(cx, cy, R * 0.93, -0.3))
    elif stage == "antral":
        # theca externa (fibrous), theca interna (cells and capillaries), basement membrane, membrana granulosa,
        # antrum, cumulus oophorus with corona radiata around the egg
        g.append(circle(cx, cy, R * 1.05, class_="m-the"))
        g += fibres(cx, cy, R * 0.95, R * 1.04, int(R * 2.2), rnd, "m-fib", (R * 0.08, R * 0.2))
        g += cell_layer(cx, cy, R * 0.86, R * 0.95, R * 0.042, rnd, "m-th", "m-thn", nuc=0.26, flat=True, gap=0.6)
        for k in range(10):
            a = rnd.uniform(0, 6.28)
            rr = R * rnd.uniform(0.885, 0.93)
            g.append(path(f"M{pt(polar(cx, cy, rr, a))}A{f(rr)},{f(rr)} 0 0,1 {pt(polar(cx, cy, rr, a + rnd.uniform(0.15, 0.4)))}",
                          class_="m-cap", stroke_width=f(max(0.8, R * 0.012))))
        g.append(circle(cx, cy, R * 0.858, class_="m-bm"))
        g += cell_layer(cx, cy, R * 0.7, R * 0.855, R * 0.046, rnd, "m-gc", "m-gcn", nuc=0.27, gap=0.55)
        antrum = ellipse_pts(cx, cy, R * 0.705, R * 0.7, 0, 72, 0.012, seed)
        g.append(path(smooth_closed(antrum), class_="m-antrum", stroke="#DDB45E", stroke_width=".7"))
        g.append(ellipse(cx - R * 0.18, cy - R * 0.26, R * 0.3, R * 0.16, -20, fill="#FFFFFF", opacity="0.45", filter="url(#m-blur6)"))
        # cumulus mound
        th = math.radians(rot)
        ec = polar(cx, cy, R * 0.43, th)
        er, zr = R * 0.15, R * 0.185
        mound_r = R * 0.29

        def in_mound(p):
            if dist(p, ec) < mound_r:
                return dist(p, ec) > zr + R * 0.045
            a = math.atan2(p[1] - cy, p[0] - cx)
            da = (a - th + math.pi) % (2 * math.pi) - math.pi
            r = dist(p, (cx, cy))
            return abs(da) < 0.36 * (1 - (0.72 - r / R) * 0.8) and R * 0.5 < r < R * 0.72
        pts = poisson(in_mound, (cx - R, cy - R, cx + R, cy + R), R * 0.048, rnd)
        g += draw_cells(packed_cells(pts, R * 0.046, gap=0.55), "m-cum", "m-gcn", rnd, 0.27)
        # corona radiata: one row of tall cells on the zona
        g += sector_cells(ec[0], ec[1], zr, zr + R * 0.05, int(2 * math.pi * zr / (R * 0.034)), rnd, "m-cum", "m-gcn",
                          gap=R * 0.006, nuc=0.22, flat=False)
        g.append(circle(ec[0], ec[1], zr, class_="m-zona"))
        g.append(circle(ec[0], ec[1], er * 1.02, fill="#FBF6F2", opacity="0.9"))
        g += oocyte(ec[0], ec[1], er, rnd)
        an.update(egg=ec, zona=polar(ec[0], ec[1], zr * 0.93, th + 2.2), cumulus=polar(cx, cy, R * 0.62, th + 0.18),
                  corona=polar(ec[0], ec[1], zr + R * 0.03, th - 1.9), antrum=polar(cx, cy, R * 0.32, th + math.pi),
                  granulosa=polar(cx, cy, R * 0.78, th + math.pi * 0.75), theca_interna=polar(cx, cy, R * 0.905, th + math.pi * 0.62),
                  theca_externa=polar(cx, cy, R * 1.0, th + math.pi * 0.55), vessel=polar(cx, cy, R * 0.91, th - 2.2))
    elif stage == "cl":
        outline = ellipse_pts(cx, cy, R, R * 0.93, rot, 90, 0.06, seed, freqs=(9, 13, 17, 4))
        g.append(path(smooth_closed(outline), fill="#F2C6A6", stroke="#C99A55", stroke_width="1"))
        core = ellipse_pts(cx, cy, R * 0.4, R * 0.33, rot + 20, 30, 0.18, seed + 3)
        pts = poisson(lambda p: inside(outline, p) and not inside(core, p) and dist(p, (cx, cy)) < R * 0.97,
                      (cx - R * 1.1, cy - R * 1.1, cx + R * 1.1, cy + R * 1.1), R * 0.1, rnd)
        g += draw_cells(packed_cells(pts, R * 0.095, gap=0.7), "m-lut", "m-lutn", rnd, 0.24)
        g.append(path(smooth_closed(core), fill="#F5E6CF", stroke="#D3B07A", stroke_width=".8"))
        for _ in range(int(R * 0.5)):
            p = polar(cx, cy, rnd.uniform(0, R * 0.28), rnd.uniform(0, 6.28))
            g.append(circle(p[0], p[1], R * 0.022, fill="#C8404B", opacity="0.5"))
        an.update(corpus_luteum=polar(cx, cy, R * 0.7, -0.7))
    elif stage == "albicans":
        outline = ellipse_pts(cx, cy, R, R * 0.8, rot, 60, 0.12, seed, freqs=(5, 9, 13))
        g.append(path(smooth_closed(outline), fill="#F7EEEA", stroke="#D9C2B8", stroke_width="0.9"))
        for k in range(6):
            inner = ellipse_pts(cx, cy, R * (0.85 - k * 0.13), R * 0.8 * (0.85 - k * 0.13), rot + k * 11, 40, 0.16, seed + k, freqs=(5, 9, 13))
            g.append(path(smooth_closed(inner), fill="none", stroke="#E3D3CC", stroke_width="0.8"))
    return "".join(g), an


def _surface_epithelium(outline, size, rnd):
    """One row of cuboidal cells along the ovary surface."""
    pts = resample(outline, size)
    ns = normals(pts)
    out = []
    for p, n in zip(pts, ns):
        # n points outwards for a counter-clockwise outline; cells sit just inside the edge
        c = (p[0] - n[0] * size * 0.45, p[1] - n[1] * size * 0.45)
        a = math.degrees(math.atan2(n[1], n[0]))
        out.append(ellipse(c[0], c[1], size * 0.42, size * 0.5, a, class_="m-se"))
        out.append(ellipse(c[0] - n[0] * size * 0.05, c[1] - n[1] * size * 0.05, size * 0.2, size * 0.17, a, class_="m-sen"))
    return out


def ovary_section(pid, kind, seed, what):
    """Ovary cut lengthwise: surface epithelium, tunica albuginea, cortex with follicles, medulla with vessels,
    hilum and mesovarium. kind: normal | prp | poi | pcos | stimulated. viewBox 0 0 1000 640."""
    rnd = random.Random(seed)
    W, H = 1000, 640
    cx, cy, rx, ry = 500, 300, 420, 238
    outline = ellipse_pts(cx, cy, rx, ry, 0, 120, 0.022, seed)
    if kind == "poi":
        outline = ellipse_pts(cx, cy, rx * 0.86, ry * 0.8, -3, 120, 0.035, seed)
    # outline is clockwise in SVG coordinates (y down) -> normals() gives inward; flip to outward
    g, an = [], {}
    o = outline
    # hilum vessels leaving the ovary (they fade out below it)
    stubs = []
    for dx, cls, w in ((-20, "m-vein", 5), (-7, "m-art", 3.6), (9, "m-vein", 4.4), (21, "m-art", 3.2)):
        stubs.append(path(smooth_open([(cx + dx * 1.5 + 26, cy + ry + 58), (cx + dx * 1.2 + 8, cy + ry + 24), (cx + dx, cy + ry * 0.85)]),
                          class_=cls, stroke_width=str(w)))
    g.append(group(stubs, mask="url(#m-fade-down)"))
    body = []
    body.append(path(smooth_closed(o), fill="#FAE6DD", stroke="#C78E7E", stroke_width="1.6"))
    inner = ellipse_pts(cx, cy, rx - 16, ry - 14, 0, 120, 0.022, seed) if kind != "poi" else ellipse_pts(cx, cy, rx * 0.86 - 14, ry * 0.8 - 12, -3, 120, 0.035, seed)
    if kind == "pcos":
        inner = ellipse_pts(cx, cy, rx - 26, ry - 24, 0, 120, 0.022, seed)
    body.append(path(smooth_closed(inner), fill="url(#m-cortex)"))
    body.append(path(smooth_closed(inner), fill="url(#m-stroma)"))
    # medulla: looser, more vascular centre
    mrx, mry = (rx * 0.5, ry * 0.42) if kind != "poi" else (rx * 0.42, ry * 0.36)
    mcy = cy + ry * 0.12
    body.append(ellipse(cx, mcy, mrx * 1.15, mry * 1.2, 0, fill="url(#m-medulla)"))
    vt, tips = vessel_tree((cx - 4, cy + ry * 0.84), -math.pi / 2, ry * 0.34, 3.6, 3, rnd, coil=2.4, spread=0.8)
    vt2, tips2 = vessel_tree((cx + 14, cy + ry * 0.84), -math.pi / 2 + 0.85, ry * 0.32, 3.0, 3, rnd, coil=2.2, spread=0.75)
    vt3, tips3 = vessel_tree((cx - 22, cy + ry * 0.84), -math.pi / 2 - 0.9, ry * 0.32, 3.0, 3, rnd, coil=2.2, spread=0.75)
    body.append(group(vt + vt2 + vt3, opacity=".78"))
    an["medulla"] = (cx + mrx * 0.15, mcy + mry * 0.35)
    an["vessels"] = tips[0] if tips else (cx, mcy)
    an["vessels_left"] = min(tips + tips2 + tips3, key=lambda q: q[0])
    an["vessels_right"] = max(tips + tips2 + tips3, key=lambda q: q[0])
    an["hilum"] = (cx, cy + ry * 0.92)
    # follicles: named ones first, then resting follicles filling the outer cortex
    placed = []

    def put(u, v, R, stage, name=None, rot=0.0):
        x, y = cx + u * rx, cy + v * ry
        svg, fa = follicle(x, y, R, stage, rnd.randrange(10 ** 6), rot)
        body.append(svg)
        placed.append((x, y, R))
        if name:
            for k, val in fa.items():
                an[f"{name}.{k}"] = val
        return fa

    # textbook (illustrative) scale: follicles drawn larger than life so their cells read
    if kind == "normal":
        put(0.44, -0.06, 104, "antral", "antral", rot=200)
        put(-0.62, 0.22, 64, "cl", "corpus_luteum", rot=10)
        put(-0.16, 0.36, 50, "early_antral", "early_antral", rot=300)
        put(-0.06, -0.48, 40, "secondary", "secondary")
        put(0.66, 0.5, 34, "secondary", "secondary2")
        put(-0.5, -0.42, 25, "primary", "primary")
        put(0.22, 0.62, 23, "primary", "primary2")
        put(-0.86, -0.1, 21, "primary", "primary3")
        n_rest, band, rsize = 20, (0.83, 0.92), (13, 16)
    elif kind == "prp":
        put(0.46, -0.04, 100, "antral", "antral", rot=200)
        put(-0.3, 0.3, 56, "early_antral", "early_antral", rot=300)
        put(0.02, -0.46, 40, "secondary", "secondary")
        put(0.64, 0.52, 34, "secondary", "secondary2")
        put(-0.74, 0.12, 25, "primary", "primary")
        put(0.2, 0.62, 24, "primary", "primary2")
        put(-0.22, -0.66, 21, "primary", "primary3")
        n_rest, band, rsize = 24, (0.83, 0.92), (13, 16)
    elif kind == "poi":
        put(0.3, -0.2, 36, "secondary", "growing")
        put(-0.35, 0.34, 30, "albicans", "albicans")
        put(0.22, 0.44, 24, "albicans", "albicans2", rot=40)
        n_rest, band, rsize = 5, (0.72, 0.84), (13, 15)
    elif kind == "pcos":
        for k in range(13):
            a = math.radians(-170 + k * 27)
            put(0.78 * math.cos(a), 0.72 * math.sin(a), rnd.uniform(26, 31), "early_antral", f"small_follicle_{k}", rot=math.degrees(a) + 180)
        n_rest, band, rsize = 8, (0.88, 0.94), (11, 13)
    elif kind == "stimulated":
        for k, (u, v, sz) in enumerate(((-0.45, -0.05, 0.36), (0.12, -0.28, 0.33), (0.55, 0.12, 0.35), (-0.05, 0.42, 0.28), (0.72, -0.45, 0.22), (-0.78, 0.38, 0.2))):
            put(u, v, ry * sz, "antral", f"follicle_{k}", rot=rnd.uniform(0, 360))
        n_rest, band, rsize = 8, (0.9, 0.95), (11, 13)
    rest = []
    tries = 0
    while len(rest) < n_rest and tries < 20000:
        tries += 1
        a = rnd.uniform(0, 2 * math.pi)
        s = rnd.uniform(*band)
        sx = rx * (0.86 if kind == "poi" else 1)
        sy = ry * (0.8 if kind == "poi" else 1)
        x, y = cx + s * sx * math.cos(a), cy + s * sy * math.sin(a)
        R = rnd.uniform(*rsize)
        if all(dist((x, y), (px, py)) > R + pr + 5 for px, py, pr in placed):
            svg, fa = follicle(x, y, R, "primordial", rnd.randrange(10 ** 6))
            body.append(svg)
            placed.append((x, y, R))
            rest.append((x, y))
    if rest:
        # anchor the resting follicles label to one near the top-left quarter
        rest.sort(key=lambda p: (p[1] - (cy - ry)) + abs(p[0] - (cx - rx * 0.35)) * 0.6)
        an["resting_follicles"] = rest[0]
        an["resting_follicles_2"] = rest[1] if len(rest) > 1 else rest[0]
        for nm, (dx, dy) in {"resting_top": (0, -1), "resting_right": (1, 0), "resting_bottom": (0, 1), "resting_left": (-1, 0),
                             "resting_top_left": (-0.7, -0.7), "resting_top_right": (0.7, -0.7)}.items():
            an[nm] = max(rest, key=lambda q: ((q[0] - cx) / rx) * dx + ((q[1] - cy) / ry) * dy)
    body += _surface_epithelium(o, 7.5, rnd)
    an["surface"] = polar(cx, cy, 0, 0)
    an["cortex"] = (cx - rx * 0.62, cy - ry * 0.55)
    an["tunica"] = o[100]
    body.append(path(smooth_closed(o), class_="m-shade"))
    body.append(ellipse(cx - rx * 0.32, cy - ry * 0.55, rx * 0.4, ry * 0.18, -8, fill="#FFFFFF", opacity="0.28", filter="url(#m-blur14)"))
    g.append(group(body, filter="url(#m-shadow)"))
    an.pop("surface", None)
    return part(pid, f"0 0 {W} {H}", what, "".join(g), an), rest


def follicle_part(pid, stage, R, seed, what, rot=200):
    S = R * 2.3
    svg, an = follicle(S / 2, S / 2, R, stage, seed, rot)
    body = group([svg, circle(S / 2, S / 2, R * 1.05, class_="m-shade")], filter="url(#m-shadow)")
    return part(pid, f"0 0 {f(S)} {f(S)}", what, body, an)


def build():
    out = []
    s, _ = ovary_section("m-ovary-section", "normal", 11, "Ovary cut lengthwise: resting, growing and antral follicles, corpus luteum, medulla vessels")
    out.append(s)
    s, _ = ovary_section("m-ovary-cortex-prp", "prp", 23, "Ovary cut lengthwise for PRP figures: many resting follicles under the surface, growing follicles, one antral follicle")
    out.append(s)
    s, _ = ovary_section("m-ovary-poi", "poi", 31, "Small ovary in premature ovarian insufficiency: very few resting follicles, one growing, scars")
    out.append(s)
    s, _ = ovary_section("m-ovary-pcos", "pcos", 41, "Polycystic ovary: thick capsule, a ring of many small follicles under the surface")
    out.append(s)
    s, _ = ovary_section("m-ovary-stimulated", "stimulated", 51, "Ovary after stimulation: several large fluid-filled follicles ready for egg retrieval")
    out.append(s)
    out.append(follicle_part("m-follicle-antral", "antral", 260, 7, "One antral follicle close-up: egg, corona, cumulus, granulosa, antrum, theca"))
    out.append(follicle_part("m-follicle-secondary", "secondary", 120, 8, "Secondary follicle: egg, zona, layers of granulosa cells, theca"))
    out.append(follicle_part("m-follicle-primary", "primary", 60, 9, "Primary follicle: egg ringed by one layer of granulosa cells"))
    out.append(follicle_part("m-follicle-primordial", "primordial", 40, 10, "Primordial (resting) follicle: egg with flat pregranulosa cells"))
    return out
