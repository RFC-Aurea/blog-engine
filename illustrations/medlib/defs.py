"""Shared <defs> and CSS of the medical library: medical colours, depth filters, tissue textures.

Colour key (textbook convention): rose-pink muscle, deeper red-pink lining, cream-salmon ovarian stroma, golden
granulosa cells and follicle fluid, pale cream egg cytoplasm, lilac-white zona pellucida, purple nuclei and
chromosomes, red arteries, blue veins, straw-yellow plasma, dark red blood cells, grey-blue glass and steel.
"""
import random

CSS = """
.m-oo{fill:url(#m-ooplasm);stroke:#D3AE90;stroke-width:.6}
.m-gv{fill:url(#m-gv);stroke:#9D83BF;stroke-width:.5}
.m-nl{fill:#5E3D8E}
.m-zona{fill:url(#m-zona);stroke:#C9B6D2;stroke-width:.6}
.m-zona-st{fill:none;stroke:#D9CCE0;stroke-width:.5;opacity:.8}
.m-pg{fill:url(#m-pg);stroke:#D2A27E;stroke-width:.4}
.m-gc{fill:url(#m-gc);stroke:#C9913F;stroke-width:.4}
.m-cum{fill:url(#m-cum);stroke:#C9913F;stroke-width:.4}
.m-gcn{fill:#8B5E9F;opacity:.82}
.m-bm{fill:none;stroke:#C78A6A;stroke-width:.8}
.m-th{fill:url(#m-th);stroke:#D48A74;stroke-width:.35}
.m-thn{fill:#A9637F;opacity:.7}
.m-the{fill:#F4CBBC}
.m-fib{fill:none;stroke:#DC9E8D;stroke-width:.7;opacity:.55;stroke-linecap:round}
.m-antrum{fill:url(#m-antrum)}
.m-cap{fill:none;stroke:#C8323C;stroke-width:1;stroke-linecap:round;opacity:.85}
.m-lut{fill:url(#m-lut);stroke:#C08A22;stroke-width:.45}
.m-lutn{fill:#9C6A7E;opacity:.6}
.m-art{fill:none;stroke:#C8323C;stroke-linecap:round;stroke-linejoin:round}
.m-vein{fill:none;stroke:#3F6DB5;stroke-linecap:round;stroke-linejoin:round;opacity:.92}
.m-se{fill:url(#m-se);stroke:#CF9583;stroke-width:.35}
.m-sen{fill:#9A6A8E;opacity:.7}
.m-te{fill:url(#m-te);stroke:#C8A6A6;stroke-width:.6}
.m-ten{fill:url(#m-nuc);stroke:#7E5A9E;stroke-width:.3}
.m-icm{fill:url(#m-icm);stroke:#BF8EA6;stroke-width:.6}
.m-icmn{fill:url(#m-nuc);stroke:#6E4A92;stroke-width:.3}
.m-bc{fill:url(#m-blastocoel)}
.m-glass{fill:url(#m-glass);stroke:#8EA3AF;stroke-width:1.2}
.m-glass-hi{fill:none;stroke:#FFFFFF;stroke-width:2.2;opacity:.75;stroke-linecap:round}
.m-glass-lumen{fill:url(#m-lumen);stroke:#A9BAC3;stroke-width:.8}
.m-steel{fill:url(#m-steel);stroke:#78828A;stroke-width:.8}
.m-plasma{fill:url(#m-plasma)}
.m-plt{fill:url(#m-plt);stroke:#C6A651;stroke-width:.5}
.m-gf{fill:#E3962D}
.m-gf2{fill:#D86A3C}
.m-rbc{fill:url(#m-rbc-cell);stroke:#9B2630;stroke-width:.5}
.m-shade{fill:url(#m-rim)}
.m-hi{fill:url(#m-hi)}
"""

DEFS = """
<defs>
  <style>""" + CSS + """</style>
  <!-- depth: soft dark rim inside a shape -->
  <filter id="m-inner" x="-5%" y="-5%" width="110%" height="110%">
    <feComponentTransfer in="SourceAlpha" result="inv"><feFuncA type="table" tableValues="1 0"/></feComponentTransfer>
    <feGaussianBlur in="inv" stdDeviation="9" result="blur"/>
    <feFlood flood-color="#7A2E33" flood-opacity="0.36"/>
    <feComposite in2="blur" operator="in"/>
    <feComposite in2="SourceAlpha" operator="in" result="shade"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/></feMerge>
  </filter>
  <filter id="m-inner-soft" x="-5%" y="-5%" width="110%" height="110%">
    <feComponentTransfer in="SourceAlpha" result="inv"><feFuncA type="table" tableValues="1 0"/></feComponentTransfer>
    <feGaussianBlur in="inv" stdDeviation="4" result="blur"/>
    <feFlood flood-color="#7A3A33" flood-opacity="0.3"/>
    <feComposite in2="blur" operator="in"/>
    <feComposite in2="SourceAlpha" operator="in" result="shade"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/></feMerge>
  </filter>
  <filter id="m-inner-gold" x="-5%" y="-5%" width="110%" height="110%">
    <feComponentTransfer in="SourceAlpha" result="inv"><feFuncA type="table" tableValues="1 0"/></feComponentTransfer>
    <feGaussianBlur in="inv" stdDeviation="5" result="blur"/>
    <feFlood flood-color="#9A6A12" flood-opacity="0.32"/>
    <feComposite in2="blur" operator="in"/>
    <feComposite in2="SourceAlpha" operator="in" result="shade"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/></feMerge>
  </filter>
  <filter id="m-inner-grey" x="-5%" y="-5%" width="110%" height="110%">
    <feComponentTransfer in="SourceAlpha" result="inv"><feFuncA type="table" tableValues="1 0"/></feComponentTransfer>
    <feGaussianBlur in="inv" stdDeviation="6" result="blur"/>
    <feFlood flood-color="#5A5068" flood-opacity="0.22"/>
    <feComposite in2="blur" operator="in"/>
    <feComposite in2="SourceAlpha" operator="in" result="shade"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/></feMerge>
  </filter>
  <filter id="m-grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.15  0 0 0 0 0.18  0 0 0 0.5 -0.2" result="g"/>
    <feComposite in="g" in2="SourceAlpha" operator="in" result="gi"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="gi"/></feMerge>
  </filter>
  <filter id="m-blur2"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="m-blur6" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="m-blur14" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="m-glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="m-shadow" x="-10%" y="-10%" width="120%" height="130%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="10"/><feOffset dy="9" result="o"/>
    <feFlood flood-color="#6A4040" flood-opacity="0.14"/><feComposite in2="o" operator="in"/>
    <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>

  <!-- shared lighting overlays (objectBoundingBox, so they fit any shape) -->
  <radialGradient id="m-rim" cx="50%" cy="50%" r="50%">
    <stop offset="0.72" stop-color="#7A3232" stop-opacity="0"/><stop offset="1" stop-color="#7A3232" stop-opacity="0.2"/>
  </radialGradient>
  <radialGradient id="m-hi" cx="36%" cy="28%" r="45%">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.5"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
  </radialGradient>

  <!-- egg and follicle -->
  <radialGradient id="m-ooplasm" cx="40%" cy="36%" r="70%">
    <stop offset="0" stop-color="#FFF8F0"/><stop offset="0.65" stop-color="#F9E6D3"/><stop offset="1" stop-color="#EFCFB4"/>
  </radialGradient>
  <radialGradient id="m-gv" cx="38%" cy="34%" r="70%">
    <stop offset="0" stop-color="#EDE3F6"/><stop offset="1" stop-color="#C3ACDE"/>
  </radialGradient>
  <radialGradient id="m-nuc" cx="36%" cy="32%" r="75%">
    <stop offset="0" stop-color="#C7AEE2"/><stop offset="1" stop-color="#7E5CAE"/>
  </radialGradient>
  <radialGradient id="m-zona" cx="50%" cy="50%" r="50%">
    <stop offset="0.8" stop-color="#FBF7FB"/><stop offset="0.93" stop-color="#F0E8F2"/><stop offset="1" stop-color="#E2D6E6"/>
  </radialGradient>
  <radialGradient id="m-pg" cx="35%" cy="30%" r="80%">
    <stop offset="0" stop-color="#FBE6D2"/><stop offset="1" stop-color="#EDC4A2"/>
  </radialGradient>
  <radialGradient id="m-gc" cx="34%" cy="30%" r="80%">
    <stop offset="0" stop-color="#FCE3A8"/><stop offset="1" stop-color="#EBB45E"/>
  </radialGradient>
  <radialGradient id="m-cum" cx="34%" cy="30%" r="80%">
    <stop offset="0" stop-color="#FDEBC0"/><stop offset="1" stop-color="#EFC274"/>
  </radialGradient>
  <radialGradient id="m-th" cx="34%" cy="30%" r="80%">
    <stop offset="0" stop-color="#F8CDB9"/><stop offset="1" stop-color="#E9A189"/>
  </radialGradient>
  <radialGradient id="m-antrum" cx="44%" cy="38%" r="68%">
    <stop offset="0" stop-color="#FFFDF4"/><stop offset="0.7" stop-color="#FDF2CC"/><stop offset="1" stop-color="#F8E2A2"/>
  </radialGradient>
  <radialGradient id="m-lut" cx="34%" cy="30%" r="80%">
    <stop offset="0" stop-color="#FBE58E"/><stop offset="1" stop-color="#E5B53B"/>
  </radialGradient>
  <radialGradient id="m-se" cx="34%" cy="30%" r="80%">
    <stop offset="0" stop-color="#FBE2D7"/><stop offset="1" stop-color="#EDB9A7"/>
  </radialGradient>

  <!-- ovary -->
  <radialGradient id="m-cortex" cx="50%" cy="52%" r="55%">
    <stop offset="0" stop-color="#F0C0B0"/><stop offset="0.6" stop-color="#F7D6C9"/><stop offset="1" stop-color="#FBE5DB"/>
  </radialGradient>
  <radialGradient id="m-medulla" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#E8A898" stop-opacity="0.85"/><stop offset="0.7" stop-color="#EDB4A4" stop-opacity="0.6"/>
    <stop offset="1" stop-color="#EEB8A8" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="m-fade-g" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0.3" stop-color="#FFFFFF"/><stop offset="1" stop-color="#000000"/>
  </linearGradient>
  <mask id="m-fade-down" maskContentUnits="objectBoundingBox"><rect width="1" height="1" fill="url(#m-fade-g)"/></mask>
  <linearGradient id="m-mesovarium" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F1BBAC"/><stop offset="1" stop-color="#F6D3C8" stop-opacity="0"/>
  </linearGradient>

  <!-- embryo -->
  <radialGradient id="m-te" cx="34%" cy="30%" r="80%">
    <stop offset="0" stop-color="#FCEDE6"/><stop offset="1" stop-color="#EFCFC6"/>
  </radialGradient>
  <radialGradient id="m-icm" cx="34%" cy="30%" r="80%">
    <stop offset="0" stop-color="#F8DCE4"/><stop offset="1" stop-color="#E4AFC0"/>
  </radialGradient>
  <radialGradient id="m-blastocoel" cx="45%" cy="40%" r="65%">
    <stop offset="0" stop-color="#FFFFFF"/><stop offset="0.75" stop-color="#F8F3F4"/><stop offset="1" stop-color="#EFE6E8"/>
  </radialGradient>

  <!-- instruments and blood -->
  <linearGradient id="m-glass" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#E9F0F3" stop-opacity="0.95"/><stop offset="0.22" stop-color="#FFFFFF" stop-opacity="0.9"/>
    <stop offset="0.6" stop-color="#DCE6EB" stop-opacity="0.85"/><stop offset="1" stop-color="#B9C9D1" stop-opacity="0.95"/>
  </linearGradient>
  <linearGradient id="m-lumen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F7FAFB"/><stop offset="1" stop-color="#E3EBEF"/>
  </linearGradient>
  <linearGradient id="m-steel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#8E979E"/><stop offset="0.3" stop-color="#F5F7F8"/><stop offset="0.55" stop-color="#CDD3D8"/><stop offset="1" stop-color="#7F8990"/>
  </linearGradient>
  <linearGradient id="m-plastic" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F8FAFB"/><stop offset="0.5" stop-color="#E4EAED"/><stop offset="1" stop-color="#C3CDD2"/>
  </linearGradient>
  <linearGradient id="m-plasma" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#EDC65A"/><stop offset="0.45" stop-color="#FBE69E"/><stop offset="1" stop-color="#E9BE4E"/>
  </linearGradient>
  <radialGradient id="m-plt" cx="38%" cy="32%" r="75%">
    <stop offset="0" stop-color="#FFF8D8"/><stop offset="1" stop-color="#EBCF7C"/>
  </radialGradient>
  <linearGradient id="m-rbc" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#8E1F2A"/><stop offset="0.45" stop-color="#B9323C"/><stop offset="1" stop-color="#861B26"/>
  </linearGradient>
  <radialGradient id="m-rbc-cell" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#D9606A"/><stop offset="0.45" stop-color="#C8404B"/><stop offset="1" stop-color="#A82A35"/>
  </radialGradient>
  <linearGradient id="m-buffy" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FBF6E4"/><stop offset="1" stop-color="#EFE6CF"/>
  </linearGradient>
  <radialGradient id="m-prp-cloud-g" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#F5D46A" stop-opacity="0.95"/><stop offset="0.55" stop-color="#F7DC85" stop-opacity="0.6"/>
    <stop offset="1" stop-color="#FBEAB0" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="m-chromo" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#5A3889"/><stop offset="0.5" stop-color="#9A74C8"/><stop offset="1" stop-color="#5A3889"/>
  </linearGradient>
  <marker id="m-arrowhead" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="#5B5B5B"/>
  </marker>
""" + "\n".join([]) + "{STROMA}\n</defs>\n"


def stroma_pattern():
    """Tileable ovarian stroma: whorled spindle cells (elongated nuclei) and faint fibres."""
    rnd = random.Random(41)
    S = 90
    items = []
    for _ in range(70):
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        a = rnd.uniform(-35, 35) + (25 if x + y > S else -15)
        L, w = rnd.uniform(3.4, 5.6), rnd.uniform(0.75, 1.1)
        for dx in (-S, 0, S):
            for dy in (-S, 0, S):
                X, Y = x + dx, y + dy
                if -8 < X < S + 8 and -8 < Y < S + 8:
                    items.append(f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{L:.1f}" ry="{w:.2f}" transform="rotate({a:.0f} {X:.1f} {Y:.1f})" fill="#B9737E" opacity="0.32"/>')
                    items.append(f'<path d="M{X - L * 2.2:.1f},{Y:.1f} q{L * 2.2:.1f},{rnd.uniform(-1.5, 1.5):.1f} {L * 4.4:.1f},0" transform="rotate({a:.0f} {X:.1f} {Y:.1f})" fill="none" stroke="#D99B8F" stroke-width="0.5" opacity="0.4"/>')
    return (f'<pattern id="m-stroma" width="{S}" height="{S}" patternUnits="userSpaceOnUse">' + "".join(items) + "</pattern>")


def defs():
    return DEFS.replace("{STROMA}", stroma_pattern())
