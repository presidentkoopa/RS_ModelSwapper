import bpy, sys, re
out = sys.argv[sys.argv.index('--out')+1]

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

bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.obj_export(filepath=out, export_selected_objects=False, export_materials=False,
                      export_triangulated_mesh=True, export_normals=True, export_uv=True,
                      apply_modifiers=True, export_object_groups=False)
print("@@@OK")
