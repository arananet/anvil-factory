"""Shared helpers for the ANVIL v2 film scripts: materials, primitives, text, keyframes, render setup.
Everything is procedural and deterministic. Palette: paper, ink green, teal."""
import bpy, math, random
from mathutils import Vector

# linear RGB values; view transform is Standard so these read close to their sRGB look
PAPER = (0.80, 0.76, 0.64, 1)
CARD = (0.93, 0.91, 0.84, 1)
INK = (0.030, 0.150, 0.105, 1)
SAGE = (0.22, 0.34, 0.27, 1)
TEAL = (0.03, 0.80, 0.72, 1)
DIM = (0.30, 0.42, 0.40, 1)

_state = {"interp": "BEZIER"}


def reset(fps=30):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(7)
    sc = bpy.context.scene
    sc.render.fps = fps
    return sc


def setup_render(sc, res_pct=100, samples=6):
    r = sc.render
    r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y = 1920, 1080
    r.resolution_percentage = res_pct
    r.fps = 30
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGB'
    r.use_motion_blur = False
    sc.eevee.taa_render_samples = samples
    sc.eevee.use_raytracing = False
    sc.eevee.use_shadows = False   # soft contact shadows are built as geometry (see contact_shadow); real shadow maps are too slow on software GL
    sc.cycles.seed = 7
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.render.use_overwrite = False       # resumable: frames that exist are skipped
    sc.render.use_placeholder = False
    sc.use_nodes = False


def world(sc, color=PAPER, strength=0.55, seen=(0.87, 0.82, 0.66, 1)):
    """Paper world. Camera rays see a bright paper horizon; lighting uses a softer ambient."""
    w = bpy.data.worlds.new("Paper")
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    amb = nt.nodes.new("ShaderNodeBackground"); amb.inputs[0].default_value = color; amb.inputs[1].default_value = strength
    vis = nt.nodes.new("ShaderNodeBackground"); vis.inputs[0].default_value = seen; vis.inputs[1].default_value = 1.0
    lp = nt.nodes.new("ShaderNodeLightPath")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    nt.links.new(amb.outputs[0], mx.inputs[1]); nt.links.new(vis.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    sc.world = w


_shadow = {}


def contact_shadow(cx, cy, w, d, z=0.0, parent=None, layers=10, grow=0.09, alpha=0.045, off=(0.0, 0.0)):
    """Soft shadow built as stacked translucent slabs of growing size: cheap on software GL."""
    if "m" not in _shadow:
        _shadow["m"] = mat("ShadowBlob", (0.02, 0.03, 0.02, 1), 1.0, 0.0, alpha=alpha)
    out = []
    for i in range(layers):
        k = grow * (layers - i)
        out.append(box("Shadow", (w + 2 * k, d + 2 * k, 0.001), (cx + off[0], cy + off[1], z + 0.003 + 0.0008 * i), _shadow["m"], parent))
    return out


def key_light(sc, strength=3.0, rot=(math.radians(48), math.radians(8), math.radians(28))):
    ld = bpy.data.lights.new("Key", 'SUN')
    ld.energy = strength
    ld.angle = math.radians(14)   # wide angle gives the soft shadow
    ob = bpy.data.objects.new("Key", ld)
    sc.collection.objects.link(ob)
    ob.rotation_euler = rot
    return ob


def mat(name, color, rough=0.85, emit=0.0, emit_color=None, metallic=0.0, alpha=1.0):
    """Light weight node tree (Diffuse + Emission) so the software GL render stays fast."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.name = "Diffuse"
    em = nt.nodes.new("ShaderNodeEmission"); em.name = "Emit"
    ad = nt.nodes.new("ShaderNodeAddShader")
    df.inputs["Color"].default_value = color
    df.inputs["Roughness"].default_value = rough
    em.inputs["Color"].default_value = emit_color or color
    em.inputs["Strength"].default_value = emit
    nt.links.new(df.outputs[0], ad.inputs[0]); nt.links.new(em.outputs[0], ad.inputs[1])
    last = ad
    if alpha < 1.0:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader"); mx.name = "Alpha"
        mx.inputs[0].default_value = alpha
        nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(ad.outputs[0], mx.inputs[2])
        last = mx
        m.surface_render_method = 'BLENDED'
    nt.links.new(last.outputs[0], out.inputs[0])
    return m


def teal(name, strength=0.0):
    return mat(name, TEAL, 0.5, strength, TEAL)


def glass(name):
    return mat(name, (0.75, 0.92, 0.9, 1), 0.2, 0.0, alpha=0.16)


def set_emit(m, strength, frame=None):
    s = m.node_tree.nodes["Emit"].inputs["Strength"]
    s.default_value = strength
    if frame is not None:
        s.keyframe_insert("default_value", frame=frame)


def set_color(m, color, frame):
    s = m.node_tree.nodes["Diffuse"].inputs["Color"]
    s.default_value = color
    s.keyframe_insert("default_value", frame=frame)


def _link(ob, parent=None):
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    return ob


def empty(name, loc=(0, 0, 0), parent=None):
    ob = bpy.data.objects.new(name, None)
    ob.location = loc
    return _link(ob, parent)


_cube = {}


def _unit_cube():
    if "m" not in _cube:
        me = bpy.data.meshes.new("unit_cube")
        v = [(-.5, -.5, -.5), (.5, -.5, -.5), (.5, .5, -.5), (-.5, .5, -.5),
             (-.5, -.5, .5), (.5, -.5, .5), (.5, .5, .5), (-.5, .5, .5)]
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        me.from_pydata(v, [], f)
        me.update()
        me.materials.append(None)   # one slot, linked per object so materials can be animated individually
        _cube["m"] = me
    return _cube["m"]


def box(name, size, loc, m, parent=None, rot=(0, 0, 0)):
    ob = bpy.data.objects.new(name, _unit_cube())
    ob.scale = size
    ob.location = loc
    ob.rotation_euler = rot
    _link(ob, parent)
    ob.material_slots[0].link = 'OBJECT'
    ob.material_slots[0].material = m
    return ob


def prim(kind, name, loc, m, parent=None, **kw):
    getattr(bpy.ops.mesh, f"primitive_{kind}_add")(location=loc, **kw)
    ob = bpy.context.active_object
    ob.name = name
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(m)
    if parent is not None:
        ob.parent = parent
    return ob


def text(name, body, width, loc, m, parent=None, face=None, extrude=0.05):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = body
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    cu.size = 1.0
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(m)
    _link(ob, parent)
    ob.location = loc
    bpy.context.view_layer.update()
    k = width / ob.dimensions.x
    ob.scale = (k, k, k)
    if face is not None:
        c = ob.constraints.new('TRACK_TO')
        c.target = face
        c.track_axis = 'TRACK_Z'
        c.up_axis = 'UP_Y'
    return ob, k


def key(ob, path, frame, value, idx=-1):
    setattr(ob, path, value)
    ob.keyframe_insert(path, index=idx, frame=frame)


def kloc(ob, f, v): key(ob, "location", f, v)
def kscl(ob, f, v): key(ob, "scale", f, v)
def krot(ob, f, v): key(ob, "rotation_euler", f, v)


def linear(on=True):
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR' if on else 'BEZIER'


def camera(sc, lens=35, loc=(0, 0, 0), target=(0, 0, 0)):
    cd = bpy.data.cameras.new("Cam")
    cd.lens = lens
    cd.clip_end = 400
    cd.dof.use_dof = False
    cam = bpy.data.objects.new("Cam", cd)
    sc.collection.objects.link(cam)
    cam.location = loc
    tg = empty("CamTarget", target)
    c = cam.constraints.new('TRACK_TO')
    c.target = tg
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
    sc.camera = cam
    return cam, tg


def floor(sc):
    box("Floor", (400, 400, 0.2), (0, 0, -0.1), mat("PaperFloor", PAPER, 1.0))


def lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def finish_anim(sc, n):
    sc.frame_start = 1
    sc.frame_end = n
