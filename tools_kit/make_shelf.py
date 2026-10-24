"""make_shelf.py -- turn imported package MODELDEF blocks into ModelSwapper entries.

Why the imported blocks cannot be used as they stand
----------------------------------------------------
A package's MODELDEF binds its model to its OWN sprite, with a row per frame:

    FrameIndex 1911 A 0 0      <- sprite 1911, frame A -> model frame 0
    FrameIndex 1911 B 0 1
    ...

ModelSwapper does not work that way. It puts our model on somebody else's
weapon, so the sprite is the HOST's (PISG, CHGG, SHTG...), and the animation is
driven at runtime by setting ModelFrame -- which is why every one of the 70
existing entries carries exactly one FrameIndex row plus the MSBL blanking row,
and why the shelf row carries a frameCount of up to 58.

So the package's frame table is not thrown away, it is READ: the first row says
which model frame the weapon's idle sprite shows, and that is the held frame.
The MD3 header says how many frames there are, and that is the ceiling the
engine needs -- RenderFrame rejects an out-of-range ModelFrame and the weapon
goes invisible, so the bound has to be right.

Emits, per model:
    a modeldef block   Path/Model/Skin/Scale/Offset/ZOffset + anchor row + MSBL
    a shelf row        archetype|MS_name|anchorSprite|0|heldFrame|frameCount

usage:
  python -B make_shelf.py <modeldefs_import_*.txt> ... > out.txt
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md3read import read_md3

BLOCK = re.compile(r'(^[ \t]*Model\s+\S+.*?^[ \t]*\})', re.S | re.M | re.I)
FIELD = lambda k: re.compile(r'^[ \t]*%s\s+(.+?)[ \t]*$' % k, re.M | re.I)
FI = re.compile(r'^[ \t]*FrameIndex\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)', re.M | re.I)

# gun name -> (archetype, anchor sprite). The archetypes and anchors are the ones
# RS_ForeignShelf already uses; nothing new is invented here.
KIND = [
    (r'1911|luger|pistol|auto9|beretta|taurus', ('pistol', 'PISG')),
    (r'revolver|taurusload', ('revolver', 'PISG')),
    (r'kar98|garand|rifle|stg44|bar\b|snipa', ('rifle', 'CHGG')),
    (r'supershotgun|ssg|doublebarrel', ('supershotgun', 'SHT2')),
    (r'assaultshotgun|shotgun|jackhammer|m37', ('shotgun', 'SHTG')),
    (r'mp40|tommy|pp41|ppsh|smg|uzi|tec9', ('smg', 'CHGG')),
    (r'mg42|machinegun|chaingun|minigun|chaing', ('machinegun', 'CHGG')),
    (r'rpg|m79|launcher|zooka|missile', ('launcher', 'MISG')),
    (r'grenade|nade|stick', ('grenade', 'MISG')),
    (r'bfg|nuker', ('bfg', 'BFGG')),
    (r'plasma|bolter|cryogun|reznator|tazer|electro', ('plasma', 'PLSG')),
    (r'railgun', ('railgun', 'PLSG')),
    (r'flame|flamethrower|flamecannon', ('flamethrower', 'PLSG')),
    (r'unmaker', ('unmaker', 'BFGG')),
    (r'saw|chainsaw', ('saw', 'SAWG')),
    (r'axe', ('axe', 'PUNG')),
    (r'dslayer|dsweap|sword', ('sword', 'PUNG')),
    (r'boot|kick', ('kick', 'PUNG')),
    (r'knife|melee|fist|canister|xplose|bolt', ('melee', 'PUNG')),
]


def kind(name):
    n = name.lower()
    for rx, v in KIND:
        if re.search(rx, n):
            return v
    return (None, None)


def one(field, text, default=None):
    m = FIELD(field).search(text)
    return m.group(1).strip() if m else default


blocks, rows, unknown, notmd3 = [], [], [], []
for path in [a for a in sys.argv[1:] if not a.startswith('--')]:
    text = open(path, encoding='utf-8', errors='replace').read()
    for b in BLOCK.findall(text):
        name = re.search(r'^[ \t]*Model\s+(\S+)', b, re.M | re.I).group(1)
        mpath = one('Path', b, '').strip('"')
        # 'Model 0 "x.md3"', NOT the block header 'Model MS_wolf_1911' -- a plain
        # field match on 'Model' finds the header first and the file comes back empty.
        mm = re.search(r'^[ \t]*Model\s+\d+\s+"([^"]+)"', b, re.M | re.I)
        mfile = mm.group(1) if mm else ''
        sm = re.search(r'^[ \t]*Skin\s+\d+\s+"([^"]+)"', b, re.M | re.I)
        skin = sm.group(1) if sm else ''
        if not (mpath and mfile):
            continue
        md3 = os.path.join(mpath, mfile)
        if not os.path.exists(md3):
            continue
        # These packages are not all MD3. Breach is the IQM showcase and a few
        # others declare MD2, and read_md3 does not crash politely on either --
        # it reads the header as MD3 and asks struct for a buffer of 1.6GB. The
        # shelf needs a real frame count, so anything that is not an MD3 is
        # reported rather than guessed at.
        if open(md3, 'rb').read(4) != b'IDP3':
            notmd3.append((name, mfile))
            continue
        nframes = read_md3(md3)['nframes']
        fi = FI.findall(b)
        held = int(fi[0][3]) if fi else 0
        if held >= nframes:
            held = 0
        arch, anchor = kind(name.split('_', 2)[-1] + ' ' + mfile)
        if not arch:
            unknown.append((name, mfile))
            continue
        keep = []
        for k in ('Scale', 'Offset', 'ZOffset'):
            v = one(k, b)
            if v:
                keep.append(f'\t{k} {v}')
        blocks.append(
            f'Model {name}\n{{\n'
            f'\tPath "{mpath}"\n'
            f'\tModel 0 "{mfile}"\n'
            + (f'\tSkin 0 "{skin}"\n' if skin else '')
            + ('\n'.join(keep) + '\n' if keep else '')
            + f'\tFrameIndex {anchor} A 0 {held}\n'
            f'\tFrameIndex MSBL A 0 9999\n'
            f'}}\n')
        rows.append(f'\t\t\t"{arch}|{name}|{anchor}|0|{held}|{nframes}",')

# Dedupe CASE-INSENSITIVELY. The build compares donor names that way and refuses
# the pack on a duplicate Model block, and two of these packages ship a FIST and a
# Fist that differ only in case -- as did my first prefix, 'bd', against the
# existing MS_BD_ entries.
seen = set()
ub, ur = [], []
for b, r in zip(blocks, rows):
    n = re.search(r'^Model (\S+)', b).group(1)
    if n.lower() in seen:
        continue
    seen.add(n.lower())
    ub.append(b)
    ur.append(r)

if '--rows' in sys.argv:
    print('\n'.join(ur))
else:
    print('\n'.join(ub))

sys.stderr.write(f'{len(ub)} models, {len(unknown)} unclassified\n')
for n, f in unknown[:12]:
    sys.stderr.write(f'   unclassified: {n} ({f})\n')
