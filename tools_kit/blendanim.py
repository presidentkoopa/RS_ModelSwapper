"""blendanim.py -- report a .blend's animation: frame range, and which objects move.

Why this exists
---------------
The blend-file guns were exported at their rest pose only, one frame. That is
fine for a mesh but it throws away the thing that makes a reload readable: a
part that is fused into the gun at frame 0 is often clear of it halfway through
the animation. The Kar98's stripper clip and its five cartridges sit parked
inside the buttstock at rest; somewhere in the reload they are out in the open,
and that frame is where a clean carve and an honest seat come from.

Run under Blender's own Python:
  blender.exe file.blend --background --python blendanim.py
"""
import bpy

sc = bpy.context.scene
f0, f1 = sc.frame_start, sc.frame_end
print(f"ANIM range {f0}..{f1}")

meshes = [o for o in bpy.data.objects if o.type == 'MESH']
print(f"ANIM meshes {len(meshes)}")

# World-space centroid per object per frame. An object that never moves relative
# to the others is furniture; one that travels is a part the reload acts on.
track = {o.name: [] for o in meshes}
for f in range(f0, f1 + 1):
    sc.frame_set(f)
    for o in meshes:
        dg = bpy.context.evaluated_depsgraph_get()
        me = o.evaluated_get(dg).to_mesh()
        if len(me.vertices):
            c = [0.0, 0.0, 0.0]
            for v in me.vertices:
                w = o.matrix_world @ v.co
                c[0] += w.x; c[1] += w.y; c[2] += w.z
            n = len(me.vertices)
            track[o.name].append((f, c[0] / n, c[1] / n, c[2] / n))
        o.evaluated_get(dg).to_mesh_clear()

for name, pts in track.items():
    if not pts:
        continue
    xs = [p[1] for p in pts]; ys = [p[2] for p in pts]; zs = [p[3] for p in pts]
    travel = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    print(f"ANIM obj {name}\ttravel {travel:.3f}\tframes {pts[0][0]}..{pts[-1][0]}")
