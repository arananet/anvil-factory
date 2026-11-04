"""Entry point. blender -b -P film.py -- <section 1..7> <frames> <outdir> [res_pct] [first last]
Builds the section procedurally, then renders its PNG sequence (existing frames are skipped)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from common import *

a = sys.argv[sys.argv.index("--") + 1:]
section, nframes, outdir = int(a[0]), int(a[1]), a[2]
res = int(a[3]) if len(a) > 3 else 100
sc = reset()
setup_render(sc, res)
world(sc)
if section == 7:
    from scene_proof import s7 as anim
else:
    from scene_line import ANIMATORS
    anim = ANIMATORS[section]
floor(sc)
key_light(sc)
anim(sc, nframes)
# every fcurve gets a smooth, deterministic interpolation already; clamp the frame range
sc.frame_start, sc.frame_end = 1, nframes
if len(a) > 5:
    sc.frame_start, sc.frame_end = int(a[4]), int(a[5])
os.makedirs(outdir, exist_ok=True)
sc.render.filepath = os.path.join(outdir, "f_")
t = time.time()
bpy.ops.render.render(animation=True)
print(f"SECTION_RENDER_DONE s{section} frames={sc.frame_end - sc.frame_start + 1} seconds={time.time() - t:.1f}")
