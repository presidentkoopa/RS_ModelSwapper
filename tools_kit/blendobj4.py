import bpy, sys, re
out = sys.argv[sys.argv.index('--out')+1]

# --frame N exports the scene AT that frame instead of at the rest pose. The guns
# were all exported at frame 0, which is where an author parks the parts that the
# reload moves -- the Kar98's stripper clip and its five cartridges sit inside the
# buttstock there. One frame per call, stacked afterwards by md3_stack.py, is what
# turns a static mesh into something md3label can classify by motion.
if '--frame' in sys.argv:
    bpy.context.scene.frame_set(int(sys.argv[sys.argv.index('--frame')+1]))

# --frames A B exports the whole range from ONE Blender launch, writing <out-dir>/fNN.obj.
# Thirty-four guns at fifteen to twenty-six frames each is six hundred launches done one
# frame at a time, and Blender costs seconds just to start. This does it in thirty-four.
FRANGE = None
if '--frames' in sys.argv:
    k = sys.argv.index('--frames')
    FRANGE = (int(sys.argv[k+1]), int(sys.argv[k+2]))

# namedcard.py reads a role off the surface name. The blends are inconsistent about
# WHERE the meaningful name lives: the Wolfenstein ones name the meshes MP40.001 and
# the armatures Magazine/Trigger/Handle; the HacX and Meatgrinder ones name the meshes
# Mag/Frame/Trigger/bolt/clip and the armatures Armature.001. Renaming blindly to the
# armature threw away 'Mag' on the AssaultShotgun. So take whichever name carries a
# role, preferring the mesh's own.
ROLE = re.compile(r'cyl|crane|yoke|ejector|extractor|hammer|release|latch|thumbpiece|trigger'
                  r'|bulletcase|case|hull|brass|bullet|round|cartridge|slide|mag|clip'
                  r'|pump|forend|foregrip|bolt|barrel|body|frame|receiver|sight|stock'
                  r'|grip|handle|loader|lever|shell', re.I)

used = {}
for o in list(bpy.data.objects):
    if o.type != 'MESH': continue
    mine = o.name
    par = o.parent.name if o.parent else ''
    # A name made only of Blender primitives is not meaningful, even though 'Cylinder'
    # contains 'cyl' and 'Cube' looks like nothing. Without this test the MG42's meshes
    # (Cylinder.000, Cylinder.022 ...) looked like they carried roles, so the fallback
    # to its armatures -- which really are named Magazine and Trigger -- never ran.
    def meaningful(n):
        if not n: return False
        if not re.sub(r'(cylinder|cube|sphere|plane|circle|object|mesh|icosphere|torus|cone'
                      r'|untitled|model|smdimporter|reference|gun|main_part)|[\d._\s-]', '', n.lower()):
            return False
        return bool(ROLE.search(n))
    pick = mine if meaningful(mine) else (par if meaningful(par) else mine)
    pick = pick.replace(' ', '_')
    used[pick] = used.get(pick, 0) + 1
    o.name = pick if used[pick] == 1 else "%s_%d" % (pick, used[pick])

# A scene whose objects are all on hidden or excluded view layers gives select_all no
# context to poll and it raises, killing the export before a single frame is written
# (br_plasma_f). Nothing here depends on the selection -- the export is
# export_selected_objects=False -- so a failure to deselect is not a reason to stop.
try:
    bpy.ops.object.select_all(action='DESELECT')
except RuntimeError:
    pass

def _write(path):
    bpy.ops.wm.obj_export(filepath=path, export_selected_objects=False, export_materials=False,
                          export_triangulated_mesh=True, export_normals=True, export_uv=True,
                          apply_modifiers=True, export_object_groups=False)

if FRANGE:
    import os
    d = out if os.path.isdir(out) else os.path.dirname(out)
    for _f in range(FRANGE[0], FRANGE[1] + 1):
        bpy.context.scene.frame_set(_f)
        _write(os.path.join(d, "f%02d.obj" % _f))
    print("@@@FRAMES %d %d" % FRANGE)
else:
    _write(out)
print("@@@OK")
