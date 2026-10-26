"""Egg and embryo: mature (MII) egg with spindle and chromosomes, cleavage embryos, blastocysts."""
import math
import random

from .core import (circle, dist, draw_cells, ellipse, f, group, packed_cells, part, path, poisson, polar, pt,
                   sector_cells, smooth_closed, cell_layer)


def zona_ring(cx, cy, r_in, r_out, rnd, gap=None):
    """Zona pellucida: translucent glycoprotein shell with fine radial striations. gap = (angle, half_width)."""
    g = []
    if gap is None:
        g.append(circle(cx, cy, r_out, class_="m-zona"))
        g.append(circle(cx, cy, r_in, fill="#FFFFFF"))
    else:
        a, h = gap
        p1, p2 = polar(cx, cy, r_out, a + h), polar(cx, cy, r_out, a - h + 2 * math.pi)
        q1, q2 = polar(cx, cy, r_in, a - h + 2 * math.pi), polar(cx, cy, r_in, a + h)
        d = (f"M{pt(p1)}A{f(r_out)},{f(r_out)} 0 1,1 {pt(p2)}Q{pt(polar(cx, cy, (r_in + r_out) / 2 + 4, a - h))} {pt(q1)}"
             f"A{f(r_in)},{f(r_in)} 0 1,0 {pt(q2)}Q{pt(polar(cx, cy, (r_in + r_out) / 2 + 4, a + h))} {pt(p1)}Z")
        g.append(path(d, fill="#F1EAF3", stroke="#C9B6D2", stroke_width=".8"))
    st = []
    n = int(2 * math.pi * r_out / 3.2)
    for k in range(n):
        b = 2 * math.pi * k / n + rnd.uniform(-0.01, 0.01)
        if gap is not None and abs((b - gap[0] + math.pi) % (2 * math.pi) - math.pi) < gap[1] + 0.02:
            continue
        r0 = r_in + (r_out - r_in) * rnd.uniform(0.08, 0.3)
        r1 = r_out - (r_out - r_in) * rnd.uniform(0.08, 0.3)
        st.append(f"M{pt(polar(cx, cy, r0, b))}L{pt(polar(cx, cy, r1, b))}")
    g.append(path("".join(st), class_="m-zona-st"))
    g.append(circle(cx, cy, r_out, fill="none", stroke="#C9B6D2", stroke_width=".9"))
    if gap is None:
        g.append(circle(cx, cy, r_in, fill="none", stroke="#D5C7DC", stroke_width=".7"))
    return g


def blastocyst(pid, seed=3, hatching=False, what=""):
    """Day-5 blastocyst. ICM on the left (9 o'clock). hatching=True opens the zona at 3 o'clock with trophectoderm
    cells bulging out (as during a trophectoderm biopsy). viewBox 0 0 640 600, centre (300, 300)."""
    rnd = random.Random(seed)
    cx, cy = 300, 300
    Zo, Zi, Ti = 270, 250, 226
    g, an = [], {}
    gap = (0.0, 0.2) if hatching else None
    body = []
    if hatching:  # herniating trophectoderm bulge outside the zona
        hc, hr = (cx + Zo + 14, cy), 56
        body.append(path(smooth_closed([polar(hc[0], hc[1], hr, math.radians(a)) for a in range(0, 360, 15)]), class_="m-bc", stroke="#C8A6A6", stroke_width=".6"))
        body += sector_cells(hc[0], hc[1], hr - 20, hr, 8, rnd, "m-te", "m-ten", a_start=math.radians(-112), a_span=math.radians(224),
                             gap=1.6, nuc=0.28)
        an["herniated_cells"] = polar(hc[0], hc[1], hr - 10, math.radians(-60))
        an["herniation_tip"] = (hc[0] + hr, hc[1])
    body += zona_ring(cx, cy, Zi, Zo, rnd, gap)
    body.append(circle(cx, cy, Zi, class_="m-bc"))
    # trophectoderm: one layer of flat cells lining the zona
    n = 30
    skip = ()
    start = rnd.uniform(0, 0.2)
    if hatching:
        start = 0.22
        n = 28
        body += sector_cells(cx, cy, Ti, Zi - 1, n, rnd, "m-te", "m-ten", a_start=start, a_span=2 * math.pi - 0.44, gap=1.6, nuc=0.3)
    else:
        body += sector_cells(cx, cy, Ti, Zi - 1, n, rnd, "m-te", "m-ten", a_start=start, gap=1.6, nuc=0.3)
    an["trophectoderm"] = polar(cx, cy, (Ti + Zi) / 2, math.radians(-50))
    an["trophectoderm_2"] = polar(cx, cy, (Ti + Zi) / 2, math.radians(60))
    an["zona"] = polar(cx, cy, (Zi + Zo) / 2, math.radians(-118))
    an["zona_2"] = polar(cx, cy, (Zi + Zo) / 2, math.radians(128))
    an["blastocoel"] = (cx + 70, cy + 30)
    # inner cell mass against the wall at 9 o'clock
    th = math.pi
    mc = polar(cx, cy, 128, th)

    def in_icm(p):
        r = dist(p, (cx, cy))
        if r > Ti - 4:
            return False
        if dist(p, mc) < 92:
            return True
        a = math.atan2(p[1] - cy, p[0] - cx)
        da = (a - th + math.pi) % (2 * math.pi) - math.pi
        return abs(da) < 0.5 and r > 150
    pts = poisson(in_icm, (cx - Ti, cy - Ti, cx + Ti, cy + Ti), 24, rnd)
    body += draw_cells(packed_cells(pts, 23, gap=1.4), "m-icm", "m-icmn", rnd, 0.3)
    an["inner_cell_mass"] = polar(mc[0], mc[1], 40, -0.6)
    an["icm_centre"] = mc
    body.append(circle(cx, cy, Zo, class_="m-shade"))
    body.append(ellipse(cx - 90, cy - 150, 120, 55, -25, fill="#FFFFFF", opacity="0.5", filter="url(#m-blur14)"))
    g.append(group(body, filter="url(#m-shadow)"))
    return part(pid, "0 0 640 600", what, "".join(g), an)


def chromosome(cx, cy, L, w, rot, cls="m-chr"):
    """Metaphase chromosome: two sister chromatids joined at the centromere."""
    g = []
    for s in (-1, 1):
        d = (f"M{f(cx + s * w * 0.15)},{f(cy - L / 2)}Q{f(cx + s * w * 1.1)},{f(cy - L / 4)} {f(cx + s * w * 0.35)},{f(cy)}"
             f"Q{f(cx + s * w * 1.1)},{f(cy + L / 4)} {f(cx + s * w * 0.15)},{f(cy + L / 2)}"
             f"Q{f(cx + s * w * 0.75)},{f(cy + L / 2 + w * 0.3)} {f(cx + s * w * 1.0)},{f(cy + L / 2 - w * 0.4)}"
             f"Q{f(cx + s * w * 1.7)},{f(cy + L / 4)} {f(cx + s * w * 0.95)},{f(cy)}"
             f"Q{f(cx + s * w * 1.7)},{f(cy - L / 4)} {f(cx + s * w * 1.0)},{f(cy - L / 2 + w * 0.4)}"
             f"Q{f(cx + s * w * 0.75)},{f(cy - L / 2 - w * 0.3)} {f(cx + s * w * 0.15)},{f(cy - L / 2)}Z")
        g.append(path(d, fill="url(#m-chromo)", stroke="#4E2F7A", stroke_width=".5"))
    return f'<g transform="rotate({f(rot)} {f(cx)} {f(cy)})">' + "".join(g) + "</g>"


def mii_egg(pid, seed=4, cumulus=True, what=""):
    """Mature (metaphase II) egg: cumulus cells, zona, perivitelline space, first polar body, ooplasm, spindle with
    chromosomes lined up at the equator near the polar body. viewBox 0 0 640 640, centre (320, 320)."""
    rnd = random.Random(seed)
    cx, cy = 320, 320
    Zo, Zi, Ro = 262, 230, 200
    an = {}
    body = []
    if cumulus:  # loose cumulus cells left around part of the zona
        def in_cum(p):
            r = dist(p, (cx, cy))
            a = math.atan2(p[1] - cy, p[0] - cx)
            lim = 300 + 14 * math.sin(3 * a + 1) + 10 * math.sin(5 * a)
            return Zo + 4 < r < lim and not (-2.2 < a < -0.8)
        pts = poisson(in_cum, (cx - 320, cy - 320, cx + 320, cy + 320), 15, rnd)
        pts = [p for p in pts if rnd.random() < 0.88]
        body += draw_cells(packed_cells(pts, 14, gap=1.2), "m-cum", "m-gcn", rnd, 0.3)
        an["cumulus"] = polar(cx, cy, 285, math.radians(150))
    body += zona_ring(cx, cy, Zi, Zo, rnd)
    an["zona"] = polar(cx, cy, (Zi + Zo) / 2, math.radians(-160))
    body.append(circle(cx, cy, Zi, fill="#FDFBFA"))
    # first polar body at 1 o'clock in the perivitelline space
    pa = math.radians(-62)
    pb = polar(cx, cy, Ro + 13, pa)
    body.append(circle(pb[0], pb[1], 23, fill="url(#m-ooplasm)", stroke="#D3AE90", stroke_width=".8"))
    for k in range(5):
        q = polar(pb[0], pb[1], rnd.uniform(0, 9), rnd.uniform(0, 6.28))
        body.append(circle(q[0], q[1], 2.2, fill="url(#m-chromo)"))
    an["polar_body"] = pb
    # ooplasm
    body.append(circle(cx, cy, Ro, class_="m-oo"))
    gr = []
    for _ in range(1500):
        a, r = rnd.uniform(0, 6.283), Ro * math.sqrt(rnd.uniform(0, 0.96))
        gr.append(f"M{f(cx + r * math.cos(a))},{f(cy + r * math.sin(a))}h.01")
    body.append(path("".join(gr), fill="none", stroke="#D7B796", stroke_width="1.8", stroke_linecap="round", opacity=".55"))
    cg = []
    for k in range(120):  # cortical granules under the membrane
        a = 2 * math.pi * k / 120 + rnd.uniform(-0.02, 0.02)
        r = Ro - rnd.uniform(4, 9)
        cg.append(f"M{f(cx + r * math.cos(a))},{f(cy + r * math.sin(a))}h.01")
    body.append(path("".join(cg), fill="none", stroke="#C7A07C", stroke_width="3", stroke_linecap="round", opacity=".6"))
    an["egg"] = (cx - 60, cy + 70)
    # meiotic spindle just under the polar body, chromosomes aligned at its equator
    sc = polar(cx, cy, Ro - 52, pa + 0.12)
    sa = math.degrees(pa + 0.12)
    L, Wd = 86, 64
    sp = []
    for k in range(-5, 6):
        y = k * Wd / 11
        sp.append(f"M{f(-L / 2)},{f(y * 0.25)}Q0,{f(y * 1.5)} {f(L / 2)},{f(y * 0.25)}")
    spindle = path("".join(sp), fill="none", stroke="#7FA9A0", stroke_width="1.2", opacity=".95")
    halo = ellipse(0, 0, L / 2 + 6, Wd / 2 + 4, 0, fill="#E6F1EE", opacity=".8")
    chrom = "".join(chromosome(rnd.uniform(-2.5, 2.5), -Wd * 0.38 + k * Wd * 0.76 / 6, 15, 3.6, 90 + rnd.uniform(-15, 15)) for k in range(7))
    body.append(f'<g transform="translate({f(sc[0])} {f(sc[1])}) rotate({f(sa)})">{halo}{spindle}<g transform="rotate(90)">{chrom}</g></g>')
    an["spindle"] = polar(sc[0], sc[1], L / 2 - 4, pa + 0.12 + math.pi)
    an["chromosomes"] = sc
    body.append(circle(cx, cy, Zo, class_="m-shade"))
    body.append(ellipse(cx - 100, cy - 140, 120, 50, -25, fill="#FFFFFF", opacity="0.5", filter="url(#m-blur14)"))
    return part(pid, "0 0 640 640", what, group(body, filter="url(#m-shadow)"), an)


def build():
    return [blastocyst("m-blastocyst", 3, False, "Day-5 blastocyst: inner cell mass (left), trophectoderm, fluid cavity, zona pellucida"),
            blastocyst("m-blastocyst-hatching", 5, True, "Blastocyst with the zona opened on the right and trophectoderm cells bulging out (biopsy site)"),
            mii_egg("m-egg-mii", 4, True, "Mature (MII) egg with cumulus cells, zona, polar body, spindle and chromosomes"),
            mii_egg("m-egg-mii-bare", 6, False, "Mature (MII) egg without cumulus cells (as for ICSI)")]
