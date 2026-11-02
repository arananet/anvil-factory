"""Sections 1 to 6: the factory line scene. One shared builder, one animator per section.
Line axis is +X. Camera mostly sits at -Y. Table top is z = 0.8."""
import math
from common import *

POST_X = [-6 + 3 * i for i in range(5)]     # five station posts
GANTRY_X = 10.0
GATE_X = 15.5
TABLE_X0, TABLE_X1 = -11.0, 19.0
HEAD_X = -9.0
TOP = 0.8


class Line: pass


def build_line(sc, cam, gate=True, reviewers=False, archive=False):
    L = Line()
    ink, sage = mat("Ink", INK, 0.7), mat("Sage", SAGE, 0.8)
    # ---- table
    L.table = empty("TableRoot", (0, 0, 0))
    cx, ln = (TABLE_X0 + TABLE_X1) / 2, TABLE_X1 - TABLE_X0
    box("TableBody", (ln, 2.2, 0.68), (cx, 0, 0.34), ink, L.table)
    box("TableTop", (ln + 0.2, 2.5, 0.12), (cx, 0, 0.74), sage, L.table)
    box("TableRail", (ln, 0.07, 0.012), (cx, 0, TOP + 0.002), teal("RailTeal", 1.4), L.table)
    for i in range(int(ln // 2)):
        box(f"Tick{i}", (0.05, 0.9, 0.01), (TABLE_X0 + 1 + 2 * i, 0, TOP + 0.003), mat(f"TickM{i}", CARD, 0.9), L.table)
    shadow_soft(cx, 0.0, ln + 0.2, 2.5, 0.0, L.table, 6, 0.2, 0.08, (-0.3, 0.35))
    # ---- station posts with caps and swing arms
    L.posts = []
    for i, x in enumerate(POST_X):
        root = empty(f"Post{i}", (x, -1.9, 0))
        box("Col", (0.36, 0.36, 2.6), (0, 0, 1.3), ink, root)
        box("Base", (0.8, 0.8, 0.12), (0, 0, 0.06), ink, root)
        shadow_soft(0, 0, 0.8, 0.8, 0.0, root, 4, 0.18, 0.1, (-0.2, 0.2))
        capm = teal(f"Cap{i}")
        box("Cap", (0.52, 0.52, 0.26), (0, 0, 2.72), capm, root)
        pivot = empty(f"ArmPivot{i}", (0, 0, 2.3), root)
        pivot.rotation_euler = (math.radians(80), 0, 0)
        box("Arm", (0.16, 1.95, 0.16), (0, 0.97, 0), ink, pivot)
        tipm = teal(f"Tip{i}")
        box("Tip", (0.26, 0.26, 0.26), (0, 1.95, 0), tipm, pivot)
        L.posts.append(dict(root=root, cap=capm, tip=tipm, pivot=pivot, x=x))
    # ---- gantry
    L.gantry = empty("GantryRoot", (GANTRY_X, 0, 0))
    gm = teal("GantryStrip")
    for s in (-1, 1):
        box("GUp", (0.32, 0.32, 3.3), (0, s * 1.9, 1.65), ink, L.gantry)
        shadow_soft(0, s * 1.9, 0.5, 0.5, 0.0, L.gantry, 3, 0.15, 0.1, (-0.2, 0.2))
    box("GBeam", (0.34, 4.1, 0.32), (0, 0, 3.35), ink, L.gantry)
    box("GStrip", (0.1, 3.6, 0.08), (0, 0, 3.15), gm, L.gantry)
    L.gantry_m = gm
    # ---- gate
    if gate:
        L.gate = empty("GateRoot", (GATE_X, 0, 0))
        gm2 = teal("GateTeal")
        for s in (-1, 1):
            box("GatePost", (0.34, 0.34, 2.7), (0, s * 1.6, 1.35), ink, L.gate)
        box("GateBeam", (0.36, 3.6, 0.3), (0, 0, 2.65), ink, L.gate)
        L.leaves = []
        for s in (-1, 1):
            lf = empty(f"Leaf{s}", (0.0, s * 0.62, 0), L.gate)
            box("LeafPanel", (0.1, 1.24, 1.55), (0.0, 0, TOP + 0.85), mat("Leaf", INK, 0.6), lf)
            box("LeafEdge", (0.14, 0.07, 1.55), (0.0, -s * 0.6, TOP + 0.85), gm2, lf)
            L.leaves.append((lf, s))
        L.gate_m = gm2
    # ---- reviewers
    if reviewers:
        L.reviewers = []
        L.rev_m = []
        for k in range(5):
            a = math.radians(18 + 72 * k)
            x, y = GANTRY_X + 3.4 * math.cos(a), 3.4 * math.sin(a)
            base = TOP if abs(y) < 1.3 else 0.0
            root = empty(f"Reviewer{k}", (x, y, base))
            box("RCol", (0.3, 0.3, 2.3), (0, 0, 1.15), ink, root)
            box("RBase", (0.7, 0.7, 0.1), (0, 0, 0.05), ink, root)
            shadow_soft(0, 0, 0.7, 0.7, 0.0, root, 3, 0.15, 0.1, (-0.2, 0.2))
            m = teal(f"RevHead{k}")
            prim("uv_sphere", "RHead", (0, 0, 2.6), m, root, radius=0.36, segments=24, ring_count=12)
            L.reviewers.append((root, x, y, base, a))
            L.rev_m.append(m)
    # ---- memory archive and quarantine
    if archive:
        build_archive(L, ink)
    return L


def make_piece(parent_loc, with_components):
    ink = mat("PieceInk", INK, 0.6)
    p = empty("Piece", parent_loc)
    box("PieceBody", (0.78, 0.78, 0.5), (0, 0, 0), ink, p)
    shadow_soft(0, 0, 0.78, 0.78, -0.245, p, 3, 0.1, 0.12, (-0.1, 0.1))
    box("PieceBand", (0.8, 0.8, 0.07), (0, 0, 0.0), teal("PieceBand", 2.5), p)
    comps = []
    defs = [("cube", (0.0, 0.0, 0.45), 'box', (0.34, 0.34, 0.34), CARD),
            ("plate", (0.0, 0.0, 0.0), 'box', (0.1, 0.5, 0.46), SAGE),
            ("disc", (0.0, 0.0, 0.0), 'cyl', None, CARD),
            ("orb", (0.0, 0.0, 0.0), 'orb', None, TEAL),
            ("mast", (0.0, 0.0, 0.0), 'box', (0.07, 0.07, 0.6), CARD)]
    finals = [(0.0, 0.0, 0.42), (0.44, 0.0, 0.0), (-0.12, 0.12, 0.31), (0.0, -0.46, 0.0), (-0.22, -0.15, 0.55)]
    for i, (n, _, kind, sz, col) in enumerate(defs):
        m = mat(f"Comp{i}", col, 0.5, 0.0, TEAL)
        if kind == 'box':
            c = box(n, sz, finals[i], m, p)
        elif kind == 'cyl':
            c = prim("cylinder", n, finals[i], m, p, radius=0.2, depth=0.09, vertices=32)
        else:
            c = prim("uv_sphere", n, finals[i], m, p, radius=0.17, segments=24, ring_count=12)
        if not with_components:
            c.scale = (0.001,) * 3
        comps.append((c, m, finals[i]))
    return p, comps


def build_archive(L, ink):
    ax, ay = 12.5, 5.2
    L.arch = empty("Archive", (ax, ay, 0))
    box("SideL", (0.14, 0.9, 2.7), (-1.85, 0, 1.35), ink, L.arch)
    box("SideR", (0.14, 0.9, 2.7), (1.85, 0, 1.35), ink, L.arch)
    box("Back", (3.8, 0.08, 2.7), (0, 0.42, 1.35), mat("ArchBack", SAGE, 0.9), L.arch)
    shadow_soft(0, 0, 3.8, 0.9, 0.0, L.arch, 5, 0.18, 0.08, (-0.3, 0.3))
    for t in range(4):
        box(f"Shelf{t}", (3.8, 0.9, 0.1), (0, 0, 0.05 + t * 0.85), ink, L.arch)
    L.slots = []
    for t in range(3):
        for s in range(4):
            sx = (-1.2 + 0.8 * s)
            sz = 0.1 + t * 0.85 + 0.27
            m = mat(f"Learn{t}{s}", TEAL, 0.4, 0.0, TEAL)
            b = box("Learning", (0.6, 0.6, 0.46), (sx, 0, sz), m, L.arch)
            b.scale = (0.001,) * 3
            L.slots.append((b, m, (sx, 0, sz)))
    # quarantine lane behind glass
    qx = 17.8
    L.quar = empty("Quarantine", (qx, ay, 0))
    box("QFloor", (3.3, 1.4, 0.1), (0, 0, 0.05), ink, L.quar)
    shadow_soft(0, 0, 3.3, 1.4, 0.0, L.quar, 5, 0.18, 0.08, (-0.3, 0.3))
    box("QBack", (3.3, 0.08, 2.4), (0, 0.66, 1.25), mat("QBackM", SAGE, 0.9), L.quar)
    gl = glass("Glass")
    box("GlassPane", (3.2, 0.04, 2.3), (0, -0.66, 1.2), gl, L.quar)
    box("GlassSide", (0.04, 1.3, 2.3), (-1.6, 0, 1.2), gl, L.quar)
    box("GlassSideR", (0.04, 1.3, 2.3), (1.6, 0, 1.2), gl, L.quar)
    for x in (-1.6, 1.6):
        for z in (0.1, 2.35):
            box("RimH", (0.1, 1.4, 0.1), (x, 0, z), ink, L.quar)
        box("RimV", (0.1, 0.1, 2.35), (x, -0.66, 1.2), ink, L.quar)
    for z in (0.1, 2.35):
        box("RimF", (3.3, 0.1, 0.1), (0, -0.66, z), ink, L.quar)
    shine = mat("Shine", (1, 1, 1, 1), 0.2, 2.0, (1, 1, 1, 1), alpha=0.22)
    for i, (cx, w) in enumerate(((-0.6, 0.25), (0.2, 0.12))):
        box("Shine", (w, 0.02, 2.0), (cx, -0.69, 1.2), shine, L.quar, rot=(0, math.radians(22), 0))
    L.quar_blocks = []
    dm = mat("QBlock", DIM, 0.6, 0.5, DIM)
    for i in range(5):
        bx = -1.2 + 0.6 * i
        b = box("Proposal", (0.46, 0.46, 0.4), (bx, 0.1, 0.1 + 0.25), dm, L.quar)
        L.quar_blocks.append((b, bx))


def ease_track(f0, f1, steps=6):
    return [f0 + (f1 - f0) * i / steps for i in range(steps + 1)]


# ------------------------------------------------------------------ section animators
def s1(sc, n):
    cam, tg = camera(sc, 28, (-20, -34, 16), (4, 0, 1.0))
    L = build_line(sc, cam, gate=True)
    T = lambda f: max(1, round(f * n))
    kloc(cam, 1, (-20, -34, 16)); kloc(cam, T(0.88), (-1.0, -21.5, 7.5)); kloc(cam, n, (-0.6, -21.4, 7.45))
    kloc(tg, 1, (4, 0, 1.0)); kloc(tg, T(0.88), (4, 0, 2.4)); kloc(tg, n, (4, 0, 2.45))
    kloc(L.table, 1, (0, 0, -1.4)); kloc(L.table, T(0.05), (0, 0, -1.4)); kloc(L.table, T(0.30), (0, 0, 0))
    for i, p in enumerate(L.posts):
        a, b = 0.28 + i * 0.085, 0.28 + i * 0.085 + 0.10
        kloc(p["root"], 1, (p["x"], -1.9, -3.2)); kloc(p["root"], T(a), (p["x"], -1.9, -3.2)); kloc(p["root"], T(b), (p["x"], -1.9, 0))
        set_emit(p["cap"], 0.0, T(b) - 1); set_emit(p["cap"], 7.0, T(b) + 3); set_emit(p["cap"], 2.2, T(b) + 14)
    for r, a in ((L.gantry, 0.72), (L.gate, 0.80)):
        loc = tuple(r.location)
        kloc(r, 1, (loc[0], 0, -4)); kloc(r, T(a), (loc[0], 0, -4)); kloc(r, T(a + 0.12), loc)
    set_emit(L.gantry_m, 0.0, 1); set_emit(L.gantry_m, 0.0, T(0.84)); set_emit(L.gantry_m, 2.0, T(0.90))
    set_emit(L.gate_m, 0.0, 1); set_emit(L.gate_m, 0.0, T(0.92)); set_emit(L.gate_m, 2.0, T(0.97))
    # polish advisory 3: the opening title is full ink color from frame 1 and at full scale by 0.15 of the section
    tm = mat("TitleInk", INK, 0.7)
    t, k = text("Title", "ANVIL", 7.5, (6, 0, 6.4), tm, face=cam, extrude=0.12)
    kscl(t, 1, (k * 0.97,) * 3); kscl(t, T(0.15), (k,) * 3); kscl(t, n, (k * 1.03,) * 3)
    return n


def s2(sc, n):
    L = build_line(sc, None, gate=True)
    T = lambda f: max(1, round(f * n))
    cam, tg = camera(sc, 35, (-19, -8.5, 3.2), (-16, 0, 2.2))
    card, frame = make_card()
    # polish advisory 4: the card starts in frame, its face is tipped toward the camera through the flight (X tilt
    # 78 -> 0 degrees, small Z yaw) and the camera rides beside it, so the card is the subject at every frame.
    d = math.radians
    path = [(0.0, (-21.0, -1.4, 4.4), (d(78), 0, d(-20))), (0.25, (-17.5, -1.2, 3.6), (d(68), 0, d(-8))),
            (0.55, (-13.0, -0.5, 2.4), (d(42), 0, d(3))), (0.70, (-9.4, 0, 1.2), (d(14), 0, d(1))),
            (0.74, (HEAD_X, 0, 0.92), (0, 0, 0)), (0.80, (HEAD_X, 0, 0.815), (0, 0, 0.03)),
            (0.85, (HEAD_X, 0, 0.865), (0, 0, 0)), (0.90, (HEAD_X, 0, 0.815), (0, 0, 0)), (1.0, (HEAD_X, 0, 0.815), (0, 0, 0))]
    for f, loc, rot in path:
        kloc(card, T(f) if f > 0 else 1, loc); krot(card, T(f) if f > 0 else 1, rot)
    set_emit(frame, 0.0, 1); set_emit(frame, 0.0, T(0.76)); set_emit(frame, 4.5, T(0.86))
    # camera: rides about 5.5 units off the card with the target just ahead of it (card sits left of center),
    # then a gentle push in as the card lands
    for f, c, g in ((0.0, (-20.2, -6.9, 4.9), (-19.8, 0, 4.2)), (0.25, (-16.6, -6.6, 4.3), (-16.3, 0, 3.5)),
                    (0.55, (-12.0, -6.0, 3.3), (-11.8, 0, 2.4)), (0.70, (-11.0, -6.4, 2.7), (-9.2, 0, 1.2)),
                    (0.92, (-10.4, -5.6, 2.4), (-8.7, 0, 1.0)), (1.0, (-10.2, -5.2, 2.35), (-8.6, 0, 1.0))):
        kloc(cam, T(f) if f > 0 else 1, c); kloc(tg, T(f) if f > 0 else 1, g)
    tm = mat("TxtInk", INK, 0.7)
    t, k = text("T", "One intake", 2.1, (-7.0, 0, 1.9), tm, face=cam)
    kscl(t, 1, (0.001,) * 3); kscl(t, T(0.55), (0.001,) * 3); kscl(t, T(0.67), (k,) * 3); kscl(t, n, (k * 1.04,) * 3)
    return n


def make_card():
    card = empty("Card", (-27, -1.6, 5.4))
    box("CardFace", (1.5, 0.8, 0.03), (0, 0, 0), mat("CardPaper", CARD, 0.9), card)
    for i in range(3):
        box("CardLine", (0.9 - 0.2 * (i == 2), 0.05, 0.012), (-0.2 + 0.0, 0.2 - 0.17 * i, 0.02), mat(f"CL{i}", INK, 0.7), card)
    fm = teal("CardGlow")
    box("CardEdge", (1.58, 0.88, 0.02), (0, 0, -0.012), fm, card)
    return card, fm


def build_doc(parent_loc):
    """Spec document: three panels + eight text lines. Returns pieces for animation."""
    doc = empty("Doc", parent_loc)
    pm = mat("DocPaper", CARD, 0.9)
    box("P1", (1.5, 0.8, 0.03), (0, 0, 0), pm, doc)
    p2 = box("P2", (1.5, 0.7, 0.03), (0, 0.4, 0), pm, doc)
    p3 = box("P3", (1.5, 0.7, 0.03), (0, -0.4, 0), pm, doc)
    em = teal("DocEdge")
    box("DocEdge", (1.58, 0.88, 0.02), (0, 0, -0.012), em, doc)
    lines = []
    rows = [0.98, 0.78, 0.58, 0.28, 0.08, -0.12, -0.5, -0.72, -0.94]
    for i, y in enumerate(rows):
        w = 1.1 if i % 3 != 2 else 0.8
        m = mat(f"DL{i}", INK if i % 3 else TEAL, 0.6, 0.0 if i % 3 else 1.5, TEAL)
        ln = box("DocLine", (w, 0.05, 0.012), (0, y, 0.022), m, doc)
        lines.append((ln, y, w))
    return doc, p2, p3, lines


def s3(sc, n):
    L = build_line(sc, None, gate=True)
    T = lambda f: max(1, round(f * n))
    cam, tg = camera(sc, 35, (-10, -7.5, 5.5), (-9, 0, 0.8))
    kloc(cam, 1, (-10.5, -7.0, 5.0)); kloc(cam, n, (-9.2, -3.0, 9.0))
    kloc(tg, 1, (-9, 0.2, 0.8)); kloc(tg, n, (-9, 0.0, 0.8))
    doc, p2, p3, lines = build_doc((HEAD_X, 0, 0.815))
    # unfold panel by panel: P2 first, then P3
    for pn, s, a in ((p2, 1, 0.08), (p3, -1, 0.22)):
        kloc(pn, 1, (0, s * 0.4, 0)); kloc(pn, T(a), (0, s * 0.4, 0)); kloc(pn, T(a + 0.14), (0, s * 0.75, 0))
        kscl(pn, 1, (1.5, 0.001, 0.03)); kscl(pn, T(a), (1.5, 0.001, 0.03)); kscl(pn, T(a + 0.14), (1.5, 0.7, 0.03))
    for i, (ln, y, w) in enumerate(lines):
        a = 0.42 + 0.50 * i / len(lines)
        b = a + 0.07
        kscl(ln, 1, (0.001, 0.05, 0.012)); kscl(ln, T(a), (0.001, 0.05, 0.012)); kscl(ln, T(b), (w, 0.05, 0.012))
        kloc(ln, 1, (-0.55, y, 0.022)); kloc(ln, T(a), (-0.55, y, 0.022)); kloc(ln, T(b), (-0.55 + w / 2, y, 0.022))
    # posts stay dark until the last line is drawn, then post one flickers on
    p0 = L.posts[0]["cap"]
    set_emit(p0, 0.0, 1); set_emit(p0, 0.0, T(0.955)); set_emit(p0, 6.0, T(0.97)); set_emit(p0, 1.0, T(0.985)); set_emit(p0, 7.0, n)
    tm = mat("TxtInk", INK, 0.7)
    t, k = text("T", "The spec comes first", 4.6, (-9.0, 2.3, 0.95), tm, face=cam)
    kscl(t, 1, (0.001,) * 3); kscl(t, T(0.12), (0.001,) * 3); kscl(t, T(0.26), (k,) * 3); kscl(t, n, (k * 1.03,) * 3)
    return n


def s4(sc, n):
    L = build_line(sc, None, gate=True)
    T = lambda f: max(1, round(f * n))
    cam, tg = camera(sc, 35, (-9.5, -12.5, 3.0), (-9, 0, 2.5))
    linear(True)
    kloc(cam, 1, (-9.6, -12.7, 3.0)); kloc(cam, T(0.10), (-9.0, -12.5, 3.0)); kloc(cam, T(0.97), (9.0, -12.0, 3.0)); kloc(cam, n, (9.4, -12.0, 3.0))
    kloc(tg, 1, (-8.8, 0, 2.5)); kloc(tg, T(0.10), (-8.6, 0, 2.5)); kloc(tg, T(0.97), (9.8, 0, 2.5)); kloc(tg, n, (10.2, 0, 2.5))
    linear(False)
    doc, p2, p3, lines = build_doc((HEAD_X, 0, 0.815))
    for pn, s in ((p2, 1), (p3, -1)):
        pn.location = (0, s * 0.75, 0); pn.scale = (1.5, 0.7, 0.03)
    piece, comps = make_piece((HEAD_X, 0, 1.05), False)
    piece.scale = (0.001,) * 3
    # fold: the spec shrinks into the piece
    kscl(doc, 1, (1, 1, 1)); kscl(doc, T(0.05), (1, 1, 1)); kscl(doc, T(0.11), (0.36, 0.34, 6.0))
    kloc(doc, 1, (HEAD_X, 0, 0.815)); kloc(doc, T(0.05), (HEAD_X, 0, 0.815)); kloc(doc, T(0.11), (HEAD_X, 0, 1.05))
    kscl(doc, T(0.112), (0.001,) * 3)
    kscl(piece, 1, (0.001,) * 3); kscl(piece, T(0.09), (0.001,) * 3); kscl(piece, T(0.113), (1, 1, 1))
    xs = [HEAD_X] + POST_X + [GANTRY_X]
    for cyc in range(5):
        t0 = 0.10 + 0.15 * cyc
        arr, dep = t0 + 0.05, t0 + 0.15
        x_prev, x_i = xs[cyc], xs[cyc + 1]
        kloc(piece, T(t0 + 0.0 if cyc else 0.115), (x_prev, 0, 1.05)); kloc(piece, T(arr), (x_i, 0, 1.05)); kloc(piece, T(dep - 0.005), (x_i, 0, 1.05))
        p = L.posts[cyc]
        set_emit(p["cap"], 0.0, T(arr) - 1); set_emit(p["cap"], 8.0, T(arr) + 2); set_emit(p["cap"], 8.0, T(t0 + 0.11)); set_emit(p["cap"], 0.0, T(t0 + 0.14))
        set_emit(p["tip"], 0.0, T(arr) - 1); set_emit(p["tip"], 7.0, T(arr) + 2); set_emit(p["tip"], 0.0, T(t0 + 0.14))
        krot(p["pivot"], 1, (math.radians(80), 0, 0)); krot(p["pivot"], T(arr), (math.radians(80), 0, 0))
        krot(p["pivot"], T(t0 + 0.08), (math.radians(-22), 0, 0)); krot(p["pivot"], T(t0 + 0.10), (math.radians(-22), 0, 0))
        krot(p["pivot"], T(t0 + 0.14), (math.radians(80), 0, 0))
        c, cm, fin = comps[cyc]
        a, b = T(t0 + 0.085), T(t0 + 0.115)
        kscl(c, 1, (0.001,) * 3); kscl(c, a, (0.001,) * 3)
        kloc(c, 1, (0, -0.18, 0.45)); kloc(c, a, (0, -0.18, 0.45))
        kscl(c, b, COMP_SCALE[cyc]); kloc(c, b, fin)
        set_emit(cm, 0.0, a); set_emit(cm, 6.0, b); set_emit(cm, 0.4, T(t0 + 0.145))
    set_emit(L.gantry_m, 0.0, 1); set_emit(L.gantry_m, 0.0, T(0.90)); set_emit(L.gantry_m, 2.5, T(0.98))
    tm = mat("TxtInk", INK, 0.7)
    # polish advisory 1: arm tips and caps top out at z 4.37 (pivot 2.3 + arm 1.95 + tip) at y -1.9; the camera is at
    # z 3.0 and 12 units off, so the title band is z 4.9 to 5.7 at y 0 (about 40 px clear of the highest tip and 40 px
    # inside the top edge). The title rides with the camera in x (linear, same speed) so it stays on screen all section.
    t, k = text("T", "Stations build", 5.2, (-3.0, 0, 5.28), tm, face=cam)
    linear(True)
    for f in (0.05, 0.97):
        cx_ = -9.0 + 18.0 * (f - 0.10) / 0.87
        kloc(t, T(f), (cx_ - 1.0, 0, 5.28))
    kloc(t, n, (9.4 - 1.0, 0, 5.28))
    linear(False)
    kscl(t, 1, (0.001,) * 3); kscl(t, T(0.05), (0.001,) * 3); kscl(t, T(0.13), (k,) * 3); kscl(t, n, (k,) * 3)
    return n


COMP_SCALE = [(1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)]


def piece_done(at, bob=False):
    p, comps = make_piece(at, True)
    for c, m, fin in comps:
        set_emit(m, 0.4)
    return p, comps


def s5(sc, n):
    L = build_line(sc, None, gate=True, reviewers=True)
    T = lambda f: max(1, round(f * n))
    cx, cy, rad = GANTRY_X, 0.0, 11.0
    cam, tg = camera(sc, 35, (0, 0, 0), (GANTRY_X, 0, 1.6))
    steps = 24
    for i in range(steps + 1):
        u = i / steps
        ang = math.radians(-150 + 130 * u)
        z = 1.5 + 2.6 * smooth(u)
        kloc(cam, 1 + round(u * (n - 1)), (cx + rad * math.cos(ang), cy + rad * math.sin(ang), z))
    kloc(tg, 1, (GANTRY_X, 0, 1.5)); kloc(tg, n, (GANTRY_X, 0, 1.9))
    piece, comps = piece_done((GANTRY_X, 0, 1.05))
    kloc(piece, 1, (GANTRY_X, 0, 1.05)); kloc(piece, T(0.5), (GANTRY_X, 0, 1.08)); kloc(piece, n, (GANTRY_X, 0, 1.05))
    krot(piece, 1, (0, 0, 0)); krot(piece, n, (0, 0, math.radians(14)))
    on = T(0.30)
    for m in L.rev_m:
        set_emit(m, 0.0, 1); set_emit(m, 0.0, on - 1); set_emit(m, 9.0, on + 3); set_emit(m, 4.0, T(0.92)); set_emit(m, 1.0, n)
    set_emit(L.gantry_m, 2.0, 1); set_emit(L.gantry_m, 6.0, on + 3)
    tm = teal("ScanM", 6.0)
    for k, (root, x, y, base, a) in enumerate(L.reviewers):
        dx, dy = GANTRY_X - x, 0 - y
        d = math.hypot(dx, dy)
        px, py = GANTRY_X - dx / d * 1.35, 0 - dy / d * 1.35   # point on the line from post to piece, 1.35 from the piece
        ang = math.atan2(dy, dx)
        sm = teal(f"ScanM{k}", 0.0)
        bar = box(f"Scan{k}", (1.5, 0.03, 0.9), (px, py, 2.3), sm, rot=(0, 0, ang + math.pi / 2))
        bar.scale = (1.5, 0.03, 0.05)
        kscl(bar, 1, (0.001,) * 3); kscl(bar, T(0.38), (0.001,) * 3); kscl(bar, T(0.40), (1.5, 0.03, 0.05))
        kloc(bar, T(0.40), (px, py, 2.4)); kloc(bar, T(0.62), (px, py, 0.95)); kloc(bar, T(0.84), (px, py, 2.4))
        kscl(bar, T(0.85), (1.5, 0.03, 0.05)); kscl(bar, T(0.87), (0.001,) * 3)
        set_emit(sm, 7.0, 1)
    t, k = text("T", "Five reviewers in parallel", 7.4, (GANTRY_X, 0, 5.4), mat("TxtInk", INK, 0.7), face=cam)
    kscl(t, 1, (0.001,) * 3); kscl(t, T(0.08), (0.001,) * 3); kscl(t, T(0.22), (k,) * 3); kscl(t, n, (k,) * 3)
    return n


def s6(sc, n):
    L = build_line(sc, None, gate=True, reviewers=False, archive=True)
    T = lambda f: max(1, round(f * n))
    cam, tg = camera(sc, 35, (14.3, -8.5, 2.6), (15.2, 0, 1.9))
    kloc(cam, 1, (14.0, -8.6, 2.6)); kloc(cam, T(0.36), (14.9, -8.7, 2.7)); kloc(cam, T(0.66), (15.4, -17.0, 5.2)); kloc(cam, n, (15.9, -17.6, 5.5))
    kloc(tg, 1, (15.0, 0, 1.9)); kloc(tg, T(0.36), (15.4, 0, 1.9)); kloc(tg, T(0.66), (15.2, 2.5, 1.7)); kloc(tg, n, (15.3, 2.6, 1.7))
    piece, comps = piece_done((13.2, 0, 1.05))
    # hover while waiting at the closed gate, then pass through once approved
    for f, x, z in ((1, 13.2, 1.05), (0.12, 13.2, 1.10), (0.26, 13.2, 1.05), (0.38, 13.2, 1.08), (0.46, 15.5, 1.05), (0.56, 19.0, 1.05), (1.0, 19.2, 1.05)):
        kloc(piece, T(f) if f > 1 else 1, (x, 0, z))
    # approving hand: a thumbs up built from ink green forms, rising beside the gate
    ink = mat("HandInk", INK, 0.6)
    hand = empty("Hand", (13.6, -2.4, -2.0))
    box("Forearm", (0.34, 0.34, 3.2), (0, 0, -1.6), ink, hand)
    box("Fist", (0.55, 0.42, 0.48), (0, 0, 0.1), ink, hand)
    for i in range(4):
        box("Finger", (0.5, 0.12, 0.12), (0, -0.25, -0.05 + 0.12 * i), ink, hand)
    th = empty("ThumbPivot", (0.0, 0, 0.3), hand)
    box("Thumb", (0.15, 0.17, 0.46), (0, 0, 0.2), ink, th)
    kloc(hand, 1, (13.6, -2.4, -2.0)); kloc(hand, T(0.05), (13.6, -2.4, -2.0)); kloc(hand, T(0.20), (13.6, -2.4, 1.2))
    for f, a in ((1, 0), (0.20, 0), (0.25, 30), (0.30, -10), (0.34, 30), (0.38, 0)):
        krot(hand, T(f) if f > 1 else 1, (math.radians(a) * 0.5, 0, math.radians(-a) * 0.3))
        krot(th, T(f) if f > 1 else 1, (math.radians(a), 0, 0))
    kloc(hand, T(0.46), (13.6, -2.4, 1.2)); kloc(hand, T(0.58), (13.6, -2.4, -2.0))
    # gate opens after the approval
    for lf, s in L.leaves:
        kloc(lf, 1, (0, s * 0.62, 0)); kloc(lf, T(0.34), (0, s * 0.62, 0)); kloc(lf, T(0.45), (0, s * 2.35, 0))
    set_emit(L.gate_m, 0.5, 1); set_emit(L.gate_m, 0.5, T(0.33)); set_emit(L.gate_m, 7.0, T(0.40)); set_emit(L.gate_m, 3.0, T(0.60))
    # verified learnings slot into the shelves one by one
    for i, (b, m, fin) in enumerate(L.slots):
        a = 0.52 + 0.036 * i
        e = a + 0.06
        sx, sy, sz = fin
        kscl(b, 1, (0.001,) * 3); kscl(b, T(a), (0.001,) * 3); kscl(b, T(a) + 3, (0.6, 0.6, 0.46))
        kloc(b, 1, (sx, -3.4, sz + 1.2)); kloc(b, T(a), (sx, -3.4, sz + 1.2)); kloc(b, T((a + e) / 2), (sx, -1.2, sz + 0.5)); kloc(b, T(e), fin)
        set_emit(m, 0.0, 1); set_emit(m, 0.0, T(a)); set_emit(m, 8.0, T(a) + 4); set_emit(m, 8.0, T(e)); set_emit(m, 2.6, T(e) + 18)
    # unverified proposals bob behind the glass; two nudge the pane toward the shelves and are held back
    for i, (b, bx) in enumerate(L.quar_blocks):
        z0 = 0.35
        for j in range(8):
            f = 1 + round((j / 7) * (n - 1))
            zz = z0 + 0.07 * math.sin(j * 1.7 + i * 1.3)
            kloc(b, f, (bx, 0.1, zz))
    for i in (0, 1):
        b, bx = L.quar_blocks[i]
        # replace keys with a nudge toward -x, pushing at the glass edge and returning
        for j, f in enumerate((0.55, 0.62, 0.69, 0.76, 0.83, 0.90, 0.97)):
            x = bx - (0.35 if j % 2 == 0 else 0.0)
            kloc(b, T(f), (x, 0.1, 0.35 + 0.02 * j))
    # polish advisory 2: both captions ride the camera (parented, 4 units in front, so nothing in the scene can touch
    # them) in the clear top band of the frame, side by side and staggered, never one column. Each sits on the side
    # of the line its subject is on: "Verified memory." left over the archive, "A human approves." right over the gate
    # and the quarantine. Geometry tops stay at or below about y 300 px in every sampled frame; captions live in y 85 to
    # 255 px. Pixel to camera space: 466.7 px per unit at 4 units. Wording unchanged.
    t1, k1 = text("T1", "A human approves.", 1.52, (0.7286, 0.8785, -4.0), mat("TxtInk", INK, 0.7), parent=cam)
    kscl(t1, 1, (0.001,) * 3); kscl(t1, 6, (0.001,) * 3); kscl(t1, T(0.07), (k1,) * 3); kscl(t1, n, (k1,) * 3)
    t2, k2 = text("T2", "Verified memory.", 1.36, (-0.771, 0.696, -4.0), mat("TxtInk2", INK, 0.7), parent=cam)
    kscl(t2, 1, (0.001,) * 3); kscl(t2, T(0.40), (0.001,) * 3); kscl(t2, T(0.47), (k2,) * 3); kscl(t2, n, (k2,) * 3)
    return n


ANIMATORS = {1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6}


def shadow_soft(cx, cy, w, d, z, parent, layers, grow, alpha, off):
    """Same footprint as the old coarse call, rendered with twice the layers for a smoother falloff."""
    return contact_shadow(cx, cy, w, d, z, parent, layers * 2, grow / 2, alpha / 2, off)
