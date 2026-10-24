"""blendskin.py -- report the texture image each blend's meshes actually use.

Why this exists
---------------
The exported MD3s carried a skin name invented from the gun's key, so a model
called bd_MP40 asked for bd_MP40.png, which never existed; 59 of 89 models
referenced a texture that was nowhere on disk.

Guessing from filenames is not a fix. _ZMCwolf holds seven PNGs for sixteen
guns, so closest-name matching handed the 1911 kar98.png and the Tommy gun
MG42.png -- confidently, and wrongly. The blend knows which image its materials
use; nothing else does.

Run under Blender's own Python:
  blender.exe file.blend --background --python blendskin.py

Prints one line per distinct image:  @@@SKIN <filename> <users>
"""
import bpy
import os
import collections

use = collections.Counter()
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    for slot in o.material_slots:
        mat = slot.material
        if not mat:
            continue
        # Node-based materials first; fall back to the legacy texture slots.
        if mat.use_nodes and mat.node_tree:
            for n in mat.node_tree.nodes:
                img = getattr(n, 'image', None)
                if img and img.filepath:
                    use[os.path.basename(bpy.path.abspath(img.filepath))] += 1
        for ts in getattr(mat, 'texture_slots', []) or []:
            tex = getattr(ts, 'texture', None)
            img = getattr(tex, 'image', None) if tex else None
            if img and img.filepath:
                use[os.path.basename(bpy.path.abspath(img.filepath))] += 1

# Any image loaded in the file at all, as a last resort -- a material whose image
# was packed or relinked still shows up here.
if not use:
    for img in bpy.data.images:
        if img.filepath and img.size[0]:
            use[os.path.basename(bpy.path.abspath(img.filepath))] += 1

for name, n in use.most_common():
    print(f"@@@SKIN {name} {n}")
if not use:
    print("@@@SKIN - 0")
