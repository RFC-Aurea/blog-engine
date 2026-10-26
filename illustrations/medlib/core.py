"""Geometry, SVG and cell helpers shared by every part of the medical illustration library."""
import math
import random

PARTS = {}  # id -> {"viewBox", "what", "anchors": {name: [x, y]}}, written to illustrations/medical_parts.json


def part(pid, vb, what, body, anchors=None):
    """Register a <symbol>. anchors are named points in the symbol's own viewBox, for aiming label leader lines."""
    PARTS[pid] = {"viewBox": vb, "what": what,
                  "anchors": {k: [round(v[0], 1), round(v[1], 1)] for k, v in (anchors or {}).items()}}
    return f'<symbol id="{pid}" viewBox="{vb}" overflow="visible">\n{body}\n</symbol>'


# ---------------------------------------------------------------- numbers and points
def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pt(p):
    return f"{f(p[0])},{f(p[1])}"


def polar(cx, cy, r, a):
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ---------------------------------------------------------------- paths
def smooth_closed(pts):
    """Closed smooth path through pts (Catmull-Rom converted to cubic Beziers)."""
    n = len(pts)
    d = f"M{pt(pts[0])}"
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{pt(c1)} {pt(c2)} {pt(p2)}"
    return d + "Z"


def smooth_open(pts):
    d = f"M{pt(pts[0])}"
    n = len(pts)
    for i in range(n - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{pt(c1)} {pt(c2)} {pt(p2)}"
    return d


def poly_d(pts):
    return "M" + "L".join(pt(p) for p in pts) + "Z"


def catmull(points, n=12):
    """Sample a Catmull-Rom spline through points."""
    out = []
    P = [points[0]] + list(points) + [points[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(tuple(points[-1]))
    return out


def resample(pts, step, closed=True):
    """Points every `step` units along a polyline."""
    seq = list(pts) + ([pts[0]] if closed else [])
    out, carry = [], 0.0
    for i in range(len(seq) - 1):
        a, b = seq[i], seq[i + 1]
        L = dist(a, b)
        t = carry
        while t < L:
            out.append(lerp(a, b, t / L))
            t += step
        carry = t - L
    return out


def normals(pts, closed=True):
    """Unit outward-ish normal (left of travel direction) at each point."""
    n = len(pts)
    out = []
    for i in range(n):
        a = pts[i - 1] if (closed or i > 0) else pts[i]
        b = pts[(i + 1) % n] if (closed or i < n - 1) else pts[i]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        out.append((dy / L, -dx / L))
    return out


def tube(center, widths, n=10):
    """Closed outline of a tube along a centreline with a width at each centre point (interpolated)."""
    c = catmull(center, n)
    w = []
    for i in range(len(center) - 1):
        for k in range(n):
            t = k / n
            w.append(widths[i] * (1 - t) + widths[i + 1] * t)
    w.append(widths[-1])
    left, right = [], []
    for i, p in enumerate(c):
        a = c[max(i - 1, 0)]
        b = c[min(i + 1, len(c) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        left.append((p[0] + nx * w[i] / 2, p[1] + ny * w[i] / 2))
        right.append((p[0] - nx * w[i] / 2, p[1] - ny * w[i] / 2))
    return left + right[::-1], c, w, left, right


def ellipse_pts(cx, cy, rx, ry, rot=0, n=48, wobble=0.0, seed=1, freqs=(3, 5, 7)):
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in freqs]
    wts = [0.5, 0.3, 0.2] + [0.15] * 8
    out = []
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + wobble * sum(wts[k] * math.sin(fq * a + ph[k]) for k, fq in enumerate(freqs))
        x, y = rx * r * math.cos(a), ry * r * math.sin(a)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def inside(poly, p):
    x, y = p
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            c = not c
    return c


def area(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                   for i in range(len(poly)))) / 2


def centroid(poly):
    return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))


# ---------------------------------------------------------------- svg element helpers
def attrs(kw):
    return " ".join(f'{k.rstrip("_").replace("_", "-")}="{v}"' for k, v in kw.items())


def path(d, **kw):
    return f'<path d="{d}" {attrs(kw)}/>'


def circle(cx, cy, r, **kw):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" {attrs(kw)}/>'


def ellipse(cx, cy, rx, ry, rot=0, **kw):
    tr = f' transform="rotate({f(rot)} {f(cx)} {f(cy)})"' if rot else ""
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}"{tr} {attrs(kw)}/>'


def group(items, **kw):
    return f"<g {attrs(kw)}>" + "".join(items) + "</g>"


# ---------------------------------------------------------------- cells
def poisson(inside_fn, bbox, spacing, rnd, k=24, seeds=None):
    """Bridson Poisson-disk sampling inside a region: points at least `spacing` apart."""
    x0, y0, x1, y1 = bbox
    cs = spacing / math.sqrt(2)
    gw, gh = int((x1 - x0) / cs) + 2, int((y1 - y0) / cs) + 2
    grid = {}
    pts, active = [], []

    def ok(p):
        gx, gy = int((p[0] - x0) / cs), int((p[1] - y0) / cs)
        for i in range(gx - 2, gx + 3):
            for j in range(gy - 2, gy + 3):
                q = grid.get((i, j))
                if q is not None and dist(p, q) < spacing:
                    return False
        return True

    def add(p):
        pts.append(p)
        active.append(p)
        grid[(int((p[0] - x0) / cs), int((p[1] - y0) / cs))] = p

    for s in (seeds or []):
        if inside_fn(s) and ok(s):
            add(s)
    tries = 0
    while not pts and tries < 5000:
        p = (rnd.uniform(x0, x1), rnd.uniform(y0, y1))
        if inside_fn(p):
            add(p)
        tries += 1
    while active:
        i = rnd.randrange(len(active))
        p = active[i]
        for _ in range(k):
            a = rnd.uniform(0, 2 * math.pi)
            r = rnd.uniform(spacing, 2 * spacing)
            q = (p[0] + r * math.cos(a), p[1] + r * math.sin(a))
            if x0 <= q[0] <= x1 and y0 <= q[1] <= y1 and inside_fn(q) and ok(q):
                add(q)
                break
        else:
            active.pop(i)
    return pts


def _clip(poly, nx, ny, c):
    """Keep the part of poly where nx*x + ny*y <= c."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        da = nx * a[0] + ny * a[1] - c
        db = nx * b[0] + ny * b[1] - c
        if da <= 0:
            out.append(a)
        if (da <= 0) != (db <= 0):
            t = da / (da - db)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def packed_cells(points, radius, gap=0.9, bounds=None):
    """Voronoi-like packed cells around each point (round at free edges). bounds(p) -> [(nx, ny, c)] extra
    half-planes (for example the walls of a ring). Returns [(centre, polygon)]."""
    cells = []
    cs = radius
    grid = {}
    for i, p in enumerate(points):
        grid.setdefault((int(p[0] // cs), int(p[1] // cs)), []).append(i)
    for i, p in enumerate(points):
        poly = [(p[0] + radius * math.cos(2 * math.pi * k / 14), p[1] + radius * math.sin(2 * math.pi * k / 14))
                for k in range(14)]
        gx, gy = int(p[0] // cs), int(p[1] // cs)
        for a in range(gx - 2, gx + 3):
            for b in range(gy - 2, gy + 3):
                for j in grid.get((a, b), ()):
                    if j == i:
                        continue
                    q = points[j]
                    dx, dy = q[0] - p[0], q[1] - p[1]
                    if dx * dx + dy * dy > 4 * radius * radius:
                        continue
                    L = math.hypot(dx, dy) or 1e-6
                    nx, ny = dx / L, dy / L
                    c = nx * (p[0] + q[0]) / 2 + ny * (p[1] + q[1]) / 2 - gap / 2
                    poly = _clip(poly, nx, ny, c)
                    if len(poly) < 3:
                        break
        if bounds:
            for nx, ny, c in bounds(p):
                poly = _clip(poly, nx, ny, c - gap / 2)
        if len(poly) >= 3 and area(poly) > radius * radius * 0.12:
            cells.append((p, _simplify(poly, radius * 0.18)))
    return cells


def _simplify(poly, tol):
    out = [poly[0]]
    for p in poly[1:]:
        if dist(p, out[-1]) > tol:
            out.append(p)
    if len(out) > 3 and dist(out[0], out[-1]) < tol:
        out.pop()
    return out if len(out) >= 3 else poly


def ring_bounds(cx, cy, r_in, r_out):
    """Half-planes that keep a cell between two circles (tangent walls at the cell's angle)."""
    def b(p):
        a = math.atan2(p[1] - cy, p[0] - cx)
        ux, uy = math.cos(a), math.sin(a)
        return [(ux, uy, ux * cx + uy * cy + r_out), (-ux, -uy, -(ux * cx + uy * cy) - r_in)]
    return b


def draw_cells(cells, cls, nuc_cls=None, rnd=None, nuc=0.3, flat_axis=None, nuc_off=0.12):
    """cells from packed_cells -> svg. nuc: nucleus radius as a share of the cell size. flat_axis(p) -> angle for
    elongated nuclei (flattened cells)."""
    rnd = rnd or random.Random(0)
    out = []
    for c, poly in cells:
        out.append(f'<path class="{cls}" d="{smooth_closed(poly)}"/>')
        if nuc_cls:
            size = math.sqrt(area(poly))
            cx, cy = centroid(poly)
            cx += rnd.uniform(-nuc_off, nuc_off) * size
            cy += rnd.uniform(-nuc_off, nuc_off) * size
            r = size * nuc * rnd.uniform(0.85, 1.12)
            if flat_axis:
                out.append(ellipse(cx, cy, r * 1.7, r * 0.62, math.degrees(flat_axis((cx, cy))), class_=nuc_cls))
            else:
                out.append(ellipse(cx, cy, r, r * rnd.uniform(0.8, 0.95), rnd.uniform(0, 180), class_=nuc_cls))
    return out


def cell_layer(cx, cy, r_in, r_out, spacing, rnd, cls, nuc_cls, nuc=0.3, flat=False, gap=0.8):
    """A ring of packed cells between r_in and r_out (granulosa, theca, trophectoderm...)."""
    pts = poisson(lambda p: r_in + spacing * 0.35 <= dist(p, (cx, cy)) <= r_out - spacing * 0.35,
                  (cx - r_out, cy - r_out, cx + r_out, cy + r_out), spacing, rnd)
    cells = packed_cells(pts, spacing * 0.95, gap=gap, bounds=ring_bounds(cx, cy, r_in, r_out))
    axis = (lambda p: math.atan2(p[1] - cy, p[0] - cx) + math.pi / 2) if flat else None
    return draw_cells(cells, cls, nuc_cls, rnd, nuc, axis)


def sector_cells(cx, cy, r0, r1, n, rnd, cls, nuc_cls, a_start=0.0, a_span=2 * math.pi, gap=1.0, nuc=0.3,
                 flat=True, skip=()):
    """n cells in one row between r0 and r1 (a single cell layer like trophectoderm or flat pregranulosa cells)."""
    out = []
    for k in range(n):
        if k in skip:
            continue
        a0 = a_start + a_span * k / n
        a1 = a_start + a_span * (k + 1) / n
        rm = (r0 + r1) / 2
        ga = gap / rm
        b0, b1 = a0 + ga / 2, a1 - ga / 2
        q0, q1 = r0 + gap * 0.3, r1 - gap * 0.3
        jj = lambda: rnd.uniform(-0.07, 0.07) * (q1 - q0)
        steps = max(2, int((b1 - b0) * rm / ((q1 - q0) * 0.9)))
        outer = [polar(cx, cy, q1 + jj(), b0 + (b1 - b0) * s / steps) for s in range(steps + 1)]
        inner = [polar(cx, cy, q0 + jj(), b1 - (b1 - b0) * s / steps) for s in range(steps + 1)]
        poly = outer + [polar(cx, cy, (q0 + q1) / 2, b1 + ga * 0.15)] + inner + [polar(cx, cy, (q0 + q1) / 2, b0 - ga * 0.15)]
        out.append(f'<path class="{cls}" d="{smooth_closed(poly)}"/>')
        if nuc_cls:
            am = (b0 + b1) / 2 + rnd.uniform(-0.15, 0.15) * (b1 - b0)
            t = q1 - q0
            c = polar(cx, cy, rm + rnd.uniform(-0.05, 0.05) * t, am)
            if flat:
                out.append(ellipse(c[0], c[1], min(t * 0.95, (b1 - b0) * rm * 0.3), t * nuc, math.degrees(am) + 90, class_=nuc_cls))
            else:
                out.append(ellipse(c[0], c[1], t * nuc, t * nuc * 0.9, math.degrees(am), class_=nuc_cls))
    return out


def fibres(cx, cy, r_in, r_out, n, rnd, cls, length=(10, 22)):
    """Tangential fibre strokes in a ring (theca externa, tunica, zona striations use radial=True elsewhere)."""
    out = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(r_in, r_out)
        L = rnd.uniform(*length) / r
        p0, p1, p2 = polar(cx, cy, r, a), polar(cx, cy, r + rnd.uniform(-1.2, 1.2), a + L / 2), polar(cx, cy, r, a + L)
        out.append(f'<path class="{cls}" d="M{pt(p0)}Q{pt(p1)} {pt(p2)}"/>')
    return out


def vessel_tree(start, angle, length, width, depth, rnd, cls_art="m-art", cls_vein="m-vein", coil=0.0,
                spread=0.55, vein_offset=None):
    """Branching artery with a companion vein. Returns (svg list, tip points)."""
    arts, veins, tips = [], [], []

    def grow(p, a, L, w, d):
        pts = [p]
        q = p
        steps = 6
        for s in range(steps):
            a += rnd.uniform(-0.18, 0.18)
            q = (q[0] + math.cos(a) * L / steps, q[1] + math.sin(a) * L / steps)
            if coil:
                q = (q[0] + math.cos(a + math.pi / 2) * coil * math.sin(s * 2.2), q[1] + math.sin(a + math.pi / 2) * coil * math.sin(s * 2.2))
            pts.append(q)
        arts.append((pts, w))
        off = vein_offset if vein_offset is not None else w * 1.3
        vp = [(x + math.cos(a + math.pi / 2) * off, y + math.sin(a + math.pi / 2) * off) for x, y in pts]
        veins.append((vp, w * 1.2))
        if d <= 0:
            tips.append(pts[-3])  # a point on the last branch, a little before its end
            return
        for side in (-1, 1):
            grow(q, a + side * spread * rnd.uniform(0.6, 1.2), L * rnd.uniform(0.55, 0.75), w * 0.68, d - 1)

    grow(start, angle, length, width, depth)
    out = []
    for pts, w in veins:
        out.append(f'<path class="{cls_vein}" d="{smooth_open(pts)}" stroke-width="{f(w)}"/>')
    for pts, w in arts:
        out.append(f'<path class="{cls_art}" d="{smooth_open(pts)}" stroke-width="{f(w)}"/>')
    return out, tips
