"""Instruments and blood: needle, syringe, PRP, test tube, micropipettes, catheter, ultrasound probe."""
import math
import random

from .core import circle, ellipse, f, group, part, path, polar, pt, smooth_closed, smooth_open


def needle():
    """Long fine needle pointing right with a bevelled tip. viewBox 0 0 1000 40, tip at (1000, 20)."""
    g = [path("M0,15 L968,15 L1000,20 L968,25 L0,25 Z", class_="m-steel"),
         path("M0,17.6 L962,17.6", fill="none", stroke="#FFFFFF", stroke_width="1.6", opacity=".8"),
         path("M968,15 L1000,20 L978,21.5 Z", fill="#AEB7BE"),
         path("M0,15 L0,25", fill="none", stroke="#78828A", stroke_width="1")]
    return part("m-needle", "0 0 1000 40", "Fine steel needle, tip on the right", "".join(g), {"tip": (1000, 20), "shaft": (700, 20)})


def syringe():
    """Syringe filled with straw-coloured PRP, needle to the right. viewBox 0 0 1000 120, needle tip at (1000, 60)."""
    g = []
    # plunger rod and thumb rest
    g.append(path("M14,22 L30,22 L30,98 L14,98 Z", fill="url(#m-plastic)", stroke="#9AA6AD", stroke_width="1.2"))
    g.append(path("M30,52 L210,52 L210,68 L30,68 Z", fill="url(#m-plastic)", stroke="#9AA6AD", stroke_width="1.2"))
    # barrel with flange
    g.append(path("M120,14 L134,14 L134,106 L120,106 Z", fill="url(#m-plastic)", stroke="#9AA6AD", stroke_width="1.2"))
    g.append(path("M134,30 L520,30 Q532,30 536,42 L548,52 L548,68 L536,78 Q532,90 520,90 L134,90 Z", class_="m-glass"))
    # PRP inside, with platelets
    g.append(path("M222,35 L516,35 Q526,35 529,45 L541,55 L541,65 L529,75 Q526,85 516,85 L222,85 Z", class_="m-plasma", opacity=".92"))
    rnd = random.Random(5)
    for _ in range(46):
        x, y = rnd.uniform(232, 510), rnd.uniform(41, 79)
        g.append(ellipse(x, y, 3.2, 1.9, rnd.uniform(0, 180), class_="m-plt"))
    # rubber plunger tip
    g.append(path("M206,33 L224,33 L224,87 L206,87 Z", fill="#6B6F73", stroke="#4E5256", stroke_width="1"))
    for x in (211, 219):
        g.append(path(f"M{x},33 L{x},87", fill="none", stroke="#8A8E92", stroke_width="1.2"))
    # graduations
    for k in range(12):
        x = 250 + k * 22
        g.append(path(f"M{x},30 L{x},{40 if k % 2 else 46}", fill="none", stroke="#7D8A91", stroke_width="1"))
    g.append(path("M140,36 L520,36", class_="m-glass-hi"))
    # hub and needle
    g.append(path("M548,50 L600,48 L606,52 L606,68 L600,72 L548,70 Z", fill="#E9EEF0", stroke="#9AA6AD", stroke_width="1"))
    g.append(path("M606,56 L972,56 L1000,60 L972,64 L606,64 Z", class_="m-steel"))
    g.append(path("M606,58.3 L966,58.3", fill="none", stroke="#FFFFFF", stroke_width="1.2", opacity=".8"))
    return part("m-syringe", "0 0 1000 120", "Syringe of straw-coloured PRP with a long fine needle, tip on the right", "".join(g),
                {"tip": (1000, 60), "needle": (800, 60), "barrel": (380, 60), "plasma": (380, 60), "plunger": (110, 60)})


def prp_cloud():
    """PRP released into tissue: platelets in straw-coloured plasma, growth factors spreading out. viewBox 0 0 400 300."""
    rnd = random.Random(9)
    g = [ellipse(200, 150, 175, 125, 0, fill="url(#m-prp-cloud-g)"), ellipse(200, 150, 95, 70, 0, fill="url(#m-prp-cloud-g)")]
    for _ in range(38):
        a, r = rnd.uniform(0, 6.283), 105 * math.sqrt(rnd.uniform(0, 1))
        x, y = 200 + r * math.cos(a) * 1.25, 150 + r * math.sin(a) * 0.9
        g.append(ellipse(x, y, rnd.uniform(5.5, 7.2), rnd.uniform(3.2, 4.2), rnd.uniform(0, 180), class_="m-plt"))
        if rnd.random() < 0.55:  # pseudopods of an activated platelet
            for k in range(3):
                b = rnd.uniform(0, 6.283)
                g.append(path(f"M{pt((x, y))}l{f(6 * math.cos(b))},{f(6 * math.sin(b))}", fill="none", stroke="#D8BB62", stroke_width=".8"))
    gf = []
    for _ in range(170):
        a, r = rnd.uniform(0, 6.283), 150 * math.sqrt(rnd.uniform(0.05, 1))
        x, y = 200 + r * math.cos(a) * 1.2, 150 + r * math.sin(a) * 0.88
        gf.append(circle(x, y, rnd.uniform(2.0, 3.2), class_="m-gf" if rnd.random() < 0.7 else "m-gf2", opacity=f"{max(0.25, 1 - r / 175):.2f}"))
    g.append(group(gf, filter="url(#m-glow)"))
    return part("m-prp-cloud", "0 0 400 300", "PRP in tissue: platelets in plasma releasing growth factors (dots) that spread out",
                "".join(g), {"platelets": (200, 150), "growth_factors": (282, 118), "edge": (40, 170)})


def prp_tube():
    """Blood tube after the centrifuge: plasma on top, thin platelet-rich buffy coat, red cells below.
    viewBox 0 0 160 480."""
    g = []
    g.append(path("M42,14 L118,14 Q124,14 124,22 L124,58 L36,58 L36,22 Q36,14 42,14 Z", fill="#E8EDF0", stroke="#9AA6AD", stroke_width="1.2"))
    for y in (24, 34, 44):
        g.append(path(f"M38,{y} L122,{y}", fill="none", stroke="#C9D3D8", stroke_width="1.4"))
    tube_d = "M40,58 L120,58 L120,400 Q120,456 80,456 Q40,456 40,400 Z"
    inner = "M46,60 L114,60 L114,398 Q114,448 80,448 Q46,448 46,398 Z"
    g.append(path(tube_d, class_="m-glass"))
    g.append(f'<clipPath id="m-prp-tube-clip"><path d="{inner}"/></clipPath>')
    fill = [path("M40,110 L120,110 L120,262 L40,262 Z", class_="m-plasma"),
            path("M40,262 L120,262 L120,276 L40,276 Z", fill="url(#m-buffy)"),
            path("M40,276 L120,276 L120,470 L40,470 Z", fill="url(#m-rbc)")]
    rnd = random.Random(3)
    for _ in range(26):
        fill.append(ellipse(rnd.uniform(50, 110), rnd.uniform(263, 275), 2.6, 1.5, rnd.uniform(0, 180), class_="m-plt"))
    fill.append(path("M40,110 Q80,104 120,110", fill="none", stroke="#D9AF45", stroke_width="1.2"))
    g.append(f'<g clip-path="url(#m-prp-tube-clip)">' + "".join(fill) + "</g>")
    g.append(path("M54,70 L54,420", class_="m-glass-hi", stroke_width="4", opacity=".55"))
    return part("m-prp-tube", "0 0 160 480", "Centrifuged blood tube: plasma (top), platelet layer (thin white band), red cells (bottom)",
                "".join(g), {"plasma": (112, 186), "platelets": (114, 269), "red_cells": (112, 360), "cap": (120, 36)})


def holding_pipette():
    """Glass holding pipette coming from the left; fire-polished tip at x=480. viewBox 0 0 500 160, tip centre (480, 80)."""
    g = [path("M0,36 L462,36 Q492,36 492,80 Q492,124 462,124 L0,124 Z", class_="m-glass"),
         path("M0,72 L470,72 Q476,72 476,80 Q476,88 470,88 L0,88 Z", class_="m-glass-lumen"),
         path("M6,46 L450,46", class_="m-glass-hi"),
         path("M6,116 L455,116", fill="none", stroke="#9FB3BE", stroke_width="1.5", opacity=".7")]
    return part("m-holding-pipette", "0 0 500 160", "Glass holding pipette, tip on the right", "".join(g), {"tip": (492, 80), "body": (260, 60)})


def biopsy_pipette():
    """Glass biopsy pipette coming from the right; open tip at x=16. viewBox 0 0 500 160, tip centre (16, 80)."""
    g = [path("M22,30 L500,30 L500,130 L22,130 Q14,130 14,122 L14,38 Q14,30 22,30 Z", class_="m-glass", opacity=".8"),
         path("M24,46 L500,46 L500,114 L24,114 Z", class_="m-glass-lumen", opacity=".35"),
         path("M30,37 L494,37", class_="m-glass-hi", stroke_width="2"),
         path("M30,123 L494,123", fill="none", stroke="#9FB3BE", stroke_width="1.4", opacity=".7")]
    return part("m-biopsy-pipette", "0 0 500 160", "Glass biopsy pipette, open tip on the left (see-through, so cells inside show)",
                "".join(g), {"tip": (14, 80), "body": (330, 34), "lumen": (90, 80)})


def build():
    return [needle(), syringe(), prp_cloud(), prp_tube(), holding_pipette(), biopsy_pipette()]
