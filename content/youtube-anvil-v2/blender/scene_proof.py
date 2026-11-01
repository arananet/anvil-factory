"""Section 7: proof scene. Imports assets/patch-one.glb, rises it on a plinth, separates the five
scene root groups along the stack axis in stack order and settles them back, while the camera orbits."""
import math, os
import bpy
from common import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLB = os.path.join(ROOT, "assets", "patch-one.glb")
# stack order, top to bottom
LAYERS = ["Top cover", "Comfort foam", "Sensing and processing board", "Adhesive layer", "Release liner"]


def s7(sc, n):
    T = lambda f: max(1, round(f * n))
    ink = mat("Ink", INK, 0.7)
    # plinth
    base = empty("PlinthRoot", (0, 0, 0))
    contact_shadow(0, 0, 4.0, 4.0, 0.0, base, 10, 0.08, 0.05, (-0.3, 0.3))
    prim("cylinder", "Plinth", (0, 0, 0.25), ink, base, radius=2.0, depth=0.5, vertices=64)
    ring = teal("PlinthRing", 3.0)
    prim("cylinder", "PlinthRing", (0, 0, 0.48), ring, base, radius=2.05, depth=0.04, vertices=64)
    prim("cylinder", "PlinthTop", (0, 0, 0.5), mat("PlinthTop", SAGE, 0.8), base, radius=1.85, depth=0.04, vertices=64)
    # patch
    before = set(bpy.data.objects.keys())
    bpy.ops.import_scene.gltf(filepath=GLB)
    imported = [o for o in bpy.data.objects if o.name not in before]
    groups = {}
    for o in bpy.data.objects:
        if o.name in LAYERS:
            groups[o.name] = o
    assert set(groups) == set(LAYERS), f"missing layers: {set(LAYERS) - set(groups)}"
    bpy.context.view_layer.update()
    # measure bounds in the glb's own frame (before parenting) to size the patch
    xs, ys, zs = [], [], []
    for o in imported:
        if o.type == 'MESH':
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c)
                xs.append(w.x); ys.append(w.y); zs.append(w.z)
    # a parent empty carries the scale and the rise; the glb nodes are parented under it
    top = empty("PatchRoot", (0, 0, 0))
    glb_roots = [o for o in imported if o.parent is None]
    for o in glb_roots:
        o.parent = top
    wid = max(max(xs) - min(xs), max(ys) - min(ys))
    s = 3.4 / wid
    top.scale = (s, s, s)
    bpy.context.view_layer.update()
    cxy = ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2)
    zmin = min(zs)
    for o in glb_roots:
        o.location.x -= cxy[0]; o.location.y -= cxy[1]; o.location.z -= zmin
    bpy.context.view_layer.update()
    rest_z = 0.54
    gap = 3.2 * (1.0)   # local units between layers when separated (scaled by s)
    order = list(reversed(LAYERS))      # bottom to top: Release liner is index 0
    base_loc = {nm: tuple(groups[nm].location) for nm in LAYERS}
    # rise from inside the plinth
    for f, z in ((1, -1.2), (0.03, -1.2), (0.20, rest_z)):
        top.location = (0, 0, z)
        top.keyframe_insert("location", frame=T(f) if f > 1 else 1)
    # separate top layer first, then downward; settle back bottom first
    for rank, nm in enumerate(LAYERS):                 # rank 0 = top cover
        idx = len(LAYERS) - 1 - rank                    # 0 for the bottom
        g = groups[nm]
        bx, by, bz = base_loc[nm]
        a = 0.36 + 0.025 * rank
        kloc(g, 1, (bx, by, bz)); kloc(g, T(a), (bx, by, bz))
        kloc(g, T(a + 0.12), (bx, by, bz + idx * gap))
        kloc(g, T(0.62 + 0.02 * idx), (bx, by, bz + idx * gap))
        kloc(g, T(0.62 + 0.02 * idx + 0.14), (bx, by, bz))
    # slow gentle spin of the plinth ring keeps the stage alive
    krot(base, 1, (0, 0, 0)); krot(base, n, (0, 0, math.radians(40)))
    # orbit
    cam, tg = camera(sc, 40, (0, -9, 3), (0, 0, 1.9))
    steps = 30
    for i in range(steps + 1):
        u = i / steps
        ang = math.radians(-50 + 150 * u)
        r = 9.0
        z = 3.0 + 1.1 * smooth(u * 2.5)      # slight rise at the start
        kloc(cam, 1 + round(u * (n - 1)), (r * math.sin(ang), -r * math.cos(ang), z))
    kloc(tg, 1, (0, 0, 0.0)); kloc(tg, T(0.30), (0, 0, 0.25)); kloc(tg, n, (0, 0, 0.25))
    # in-scene texts, parented to the camera so they hold the lower third while the orbit moves
    tm = mat("TxtInk", INK, 0.7)
    seq = [("Sentia", 1.2, 0.07, 0.34), ("sentia.info-693.workers.dev", 2.3, 0.38, 0.76), ("Designed and built end to end by ANVIL", 2.8, 0.80, 1.0)]
    for i, (body, w, a, b) in enumerate(seq):
        t, k = text(f"T{i}", body, w, (0, -0.55, -4.0), tm, parent=cam)
        t.rotation_euler = (0, 0, 0)
        kscl(t, 1, (0.001,) * 3)
        kscl(t, T(a), (0.001,) * 3); kscl(t, T(a) + 12, (k,) * 3)
        if b < 1.0:
            kscl(t, T(b) - 10, (k,) * 3); kscl(t, T(b), (0.001,) * 3)
        else:
            kscl(t, n, (k,) * 3)
    return n
