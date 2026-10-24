"""import_vrpack.py -- import a finished VR weapon package whole: models, textures, MODELDEF.

Why this exists
---------------
These packages are already done. Each one holds Models/<Gun>/<gun>.md3 with its
texture beside it and a Modeldef.<Gun>.def that declares the Path, the Skin, the
Scale/Offset/ZOffset and a full FrameIndex table mapping sprite frames to model
frames. The meshes are animated -- BrutalWolf up to 29 frames, br_vr up to 75.

Everything a weapon needs is in there and was in there the whole time. Exporting
the blends again produced untextured meshes with no frame mapping and no
MODELDEF, and then guessing textures by filename put kar98.png on the 1911.

So: copy the tree, rewrite the model NAME and the Path, and keep every other
line byte for byte. Scale, Offset, ZOffset and the FrameIndex table are the
author's measurements and are not ours to recompute.

Blocks that share a Path are the same model (the packages repeat a block per
quick-attack sprite set), so they collapse to one MS_ name.

usage:
  python -B import_vrpack.py <pack-root> <prefix> <dest-under-models> [--dry-run]
    e.g. import_vrpack.py E:/DOOMWork/VR_WeaponSetRebuild/BrutalWolf wolf wolf
"""
import os
import re
import shutil
import sys

BLOCK = re.compile(r'(^[ \t]*Model\s+\S+[ \t]*\r?\n?[ \t]*\{.*?^[ \t]*\})',
                   re.S | re.M | re.I)
PATH = re.compile(r'^([ \t]*Path\s+")([^"]+)(")', re.M | re.I)
NAME = re.compile(r'^([ \t]*Model\s+)(\S+)', re.M | re.I)
MODELFILE = re.compile(r'^[ \t]*Model\s+\d+\s+"([^"]+)"', re.M | re.I)
SKINFILE = re.compile(r'^[ \t]*Skin\s+\d+\s+"([^"]+)"', re.M | re.I)


def ident(path):
    """A stable MS_ name from the package Path, e.g. Models/KAR98/ -> KAR98."""
    return re.sub(r'[^A-Za-z0-9]', '', path.strip('/\\').split('/')[-1].split('\\')[-1])


def main():
    root, prefix, dest = sys.argv[1], sys.argv[2], sys.argv[3]
    dry = '--dry-run' in sys.argv
    out_root = os.path.join('models', dest)

    defs = [os.path.join(dp, f)
            for dp, _, fs in os.walk(root)
            for f in fs if f.lower().startswith('modeldef') and not f.startswith('-')]
    blocks, seen, missing = [], {}, []
    for d in sorted(defs):
        text = open(d, encoding='utf-8', errors='replace').read()
        for b in BLOCK.findall(text):
            mp = PATH.search(b)
            if not mp:
                continue
            rel = mp.group(2).strip().replace('\\', '/').strip('/')
            key = ident(rel)
            msname = f'MS_{prefix}_{key}'
            src_dir = os.path.join(root, *rel.split('/'))
            if not os.path.isdir(src_dir):
                # some packages spell the folder differently in the def than on disk
                cands = [p for p in
                         (os.path.join(dp, dn) for dp, dns, _ in os.walk(root) for dn in dns)
                         if os.path.basename(p).lower() == key.lower()]
                if not cands:
                    missing.append((os.path.basename(d), rel))
                    continue
                src_dir = cands[0]
            newpath = f'{out_root}/{key}'.replace('\\', '/')
            nb = PATH.sub(lambda m: m.group(1) + newpath + m.group(3), b)
            nb = NAME.sub(lambda m: m.group(1) + msname, nb, count=1)
            blocks.append((msname, nb))
            seen.setdefault(msname, src_dir)

    # copy each model folder once
    copied = 0
    for msname, src in sorted(seen.items()):
        key = msname.split('_', 2)[2]
        dst = os.path.join(out_root, key)
        if not dry:
            os.makedirs(dst, exist_ok=True)
            for f in os.listdir(src):
                p = os.path.join(src, f)
                if os.path.isfile(p):
                    shutil.copy2(p, os.path.join(dst, f))
        copied += 1

    # verify every Model/Skin a block names is now present at the new Path
    unresolved = []
    for msname, b in blocks:
        key = msname.split('_', 2)[2]
        dst = os.path.join(out_root, key)
        for rx in (MODELFILE, SKINFILE):
            for f in rx.findall(b):
                if not dry and not os.path.exists(os.path.join(dst, f)):
                    low = {x.lower() for x in os.listdir(dst)} if os.path.isdir(dst) else set()
                    if f.lower() not in low:
                        unresolved.append((msname, f))

    text = '\n'.join(b for _, b in blocks)
    print(f'{root}')
    print(f'  modeldef files read : {len(defs)}')
    print(f'  model blocks        : {len(blocks)}  ({len(seen)} distinct models)')
    print(f'  folders copied      : {copied} -> {out_root}/')
    print(f'  def Path not on disk: {len(missing)}')
    for d, r in missing[:8]:
        print(f'      {d}: {r}')
    print(f'  asset refs missing  : {len(unresolved)}')
    for n, f in unresolved[:8]:
        print(f'      {n}: {f}')
    if not dry:
        open(f'modeldefs_import_{prefix}.txt', 'w', encoding='utf-8').write(text + '\n')
        print(f'  wrote modeldefs_import_{prefix}.txt')


main()
