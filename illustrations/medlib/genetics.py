"""Chromosomes and DNA: a banded karyotype (normal or with an extra chromosome) and DNA double helices."""
import math
import random

from .core import f, group, part, path, pt

# relative lengths (chr1 = 1.0) and centromere position (share of length from the top) of human chromosomes
CHROMS = {
    "1": (1.0, 0.49), "2": (0.97, 0.39), "3": (0.80, 0.46), "4": (0.77, 0.27), "5": (0.73, 0.27), "6": (0.69, 0.35),
    "7": (0.64, 0.37), "8": (0.58, 0.32), "9": (0.56, 0.35), "10": (0.54, 0.30), "11": (0.54, 0.40), "12": (0.53, 0.27),
    "13": (0.46, 0.13), "14": (0.43, 0.14), "15": (0.41, 0.15), "16": (0.36, 0.41), "17": (0.33, 0.30), "18": (0.32, 0.22),
    "19": (0.24, 0.45), "20": (0.26, 0.43), "21": (0.19, 0.26), "22": (0.21, 0.28), "X": (0.63, 0.39), "Y": (0.23, 0.22),
}
ROWS = [["1", "2", "3", "4", "5"], ["6", "7", "8", "9", "10", "11", "12", "X"], ["13", "14", "15", "16", "17", "18"],
        ["19", "20", "21", "22"]]


def homolog(x, y, L, c, w, rnd, hi=False):
    """One banded chromosome standing upright, top at y; c = centromere share."""
    cy = y + L * c
    fill = "#E0D0F0" if not hi else "#F6D0D4"
    band = "#56378A" if not hi else "#A8303F"
    g = [f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(L * c)}" rx="{f(w / 2)}" fill="{fill}" stroke="{band}" stroke-width=".5"/>',
         f'<rect x="{f(x)}" y="{f(cy)}" width="{f(w)}" height="{f(L * (1 - c))}" rx="{f(w / 2)}" fill="{fill}" stroke="{band}" stroke-width=".5"/>']
    yy = y + w * 0.45
    while yy < y + L - w * 0.45:
        h = rnd.uniform(0.8, 2.6)
        if abs(yy - cy) > 1.6 and rnd.random() < 0.55:
            g.append(f'<rect x="{f(x + w * 0.06)}" y="{f(yy)}" width="{f(w * 0.88)}" height="{f(min(h, y + L - w * 0.45 - yy))}" fill="{band}" opacity=".78"/>')
        yy += h + rnd.uniform(0.6, 2.2)
    return "".join(g)


def karyotype(pid, extra=None, sex="XX", what=""):
    """Karyogram: 23 pairs in four rows, centromeres lined up on each row, like a lab report.
    extra = a chromosome drawn three times (tinted), e.g. '21'. sex XY puts X and Y in the X slot.
    viewBox 0 0 420 300."""
    W, H, tall, w, gap, slot = 420, 300, 92, 7.6, 2.2, 51
    g, an = [], {}
    y = 4
    for names in ROWS:
        pmax = max(tall * CHROMS[n][0] * CHROMS[n][1] for n in names)
        qmax = max(tall * CHROMS[n][0] * (1 - CHROMS[n][1]) for n in names)
        cl = y + pmax  # centromere line of this row
        x0 = (W - slot * len(names)) / 2
        for i, nm in enumerate(names):
            kinds = [nm] * (3 if nm == extra else 2)
            if nm == "X" and sex == "XY":
                kinds = ["X", "Y"]
            sx = x0 + slot * i + slot / 2
            total = len(kinds) * w + (len(kinds) - 1) * gap
            for k, kn in enumerate(kinds):
                L, c = CHROMS[kn]
                L *= tall
                g.append(homolog(sx - total / 2 + k * (w + gap), cl - L * c, L, c, w, random.Random(sum(map(ord, kn)) * 7),
                                 hi=(len(kinds) == 3)))
            an[f"chr{nm}"] = (sx + total / 2 + 1, cl)
        y = cl + qmax + 12
    if extra:
        an["extra"] = an[f"chr{extra}"]
    an["all"] = (W / 2, H / 2)
    return part(pid, f"0 0 {W} {H}", what, "".join(g), an)


def dna(pid, broken=False, length=560, what=""):
    """DNA double helix lying horizontally; broken=True cuts both strands in places (fragmentation).
    viewBox 0 0 600 120."""
    rnd = random.Random(21 if broken else 20)
    g = []
    cy, amp, per = 60, 30, 92
    x0 = 20
    breaks = [(190, 216), (380, 402)] if broken else []

    def gap(x):
        return any(a <= x <= b for a, b in breaks)

    rungs = []
    for k in range(int(length / 11)):
        x = x0 + k * 11 + 5
        if gap(x):
            continue
        y1 = cy + amp * math.sin(2 * math.pi * (x - x0) / per)
        y2 = cy - amp * math.sin(2 * math.pi * (x - x0) / per)
        col = ["#E3A33B", "#5FA8C9", "#D8605A", "#7FB77E"][k % 4]
        col2 = ["#5FA8C9", "#E3A33B", "#7FB77E", "#D8605A"][k % 4]
        ym = (y1 + y2) / 2
        rungs.append(f'<path d="M{f(x)},{f(y1)}L{f(x)},{f(ym)}" stroke="{col}" stroke-width="3.2" stroke-linecap="round"/>')
        rungs.append(f'<path d="M{f(x)},{f(ym)}L{f(x)},{f(y2)}" stroke="{col2}" stroke-width="3.2" stroke-linecap="round"/>')
    g += rungs
    for sgn, col, w in ((1, "#4E6FB3", 7), (-1, "#7C55A8", 7)):
        segs, cur = [], []
        for k in range(int(length) + 1):
            x = x0 + k
            if gap(x):
                if cur:
                    segs.append(cur)
                cur = []
                continue
            cur.append((x, cy + sgn * amp * math.sin(2 * math.pi * (x - x0) / per)))
        if cur:
            segs.append(cur)
        for sgm in segs:
            d = "M" + "L".join(pt(p) for p in sgm[::3] + [sgm[-1]])
            g.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
            g.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" opacity=".45" transform="translate(0,-1.6)"/>')
    an = {"helix": (x0 + 60, cy - amp), "strand": (x0 + 120, cy + amp * math.sin(2 * math.pi * 100 / per))}
    if broken:
        an["break"] = ((breaks[0][0] + breaks[0][1]) / 2, cy)
        an["break_2"] = ((breaks[1][0] + breaks[1][1]) / 2, cy)
    return part(pid, "0 0 600 120", what, "".join(g), an)


def build():
    return [karyotype("m-karyotype", None, "XX", "Normal karyotype: 23 pairs (46 chromosomes), banded"),
            karyotype("m-karyotype-xy", None, "XY", "Normal male karyotype: 22 pairs plus X and Y"),
            karyotype("m-karyotype-trisomy21", "21", "XX", "Karyotype with an extra chromosome 21 (tinted): 47 chromosomes"),
            dna("m-dna", False, what="Intact DNA double helix"),
            dna("m-dna-broken", True, what="DNA double helix with breaks in both strands (fragmented)")]
