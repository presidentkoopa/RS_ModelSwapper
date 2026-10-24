#!/usr/bin/env python3
"""namedcard.py model.md3 Name archetype > Name.card
Card for a GOLD model: surfaces are named in the source, so roles come from the names and
geometry from the mesh (single frame is fine). WPN space = file space (bore +X, up +Z) -- run
obj2md3.py with the right --axes first. Role words: VR_Weapon_Spec.md §5 plus crane/ejector/latch."""
import os
import sys, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from md3read import read_md3

NAMES = [  # (regex on surface name, role)
    # 'cyl' was a bare substring, so Blender's default primitive name -- Cylinder,
    # Cylinder.001 -- became a revolver cylinder. That gave the MG42 four cylinders
    # and a spurious chamber/eject/load, with 'chambers 0' as the tell. Require the
    # name to be something other than the untouched primitive.
    (r'cyl(?!inder\.?\d*$)', 'cyl'), (r'crane|yoke', 'crane'), (r'ejector|extractor', 'ejector'), (r'hammer', 'hammer'),
    (r'release|latch|thumbpiece', 'latch'), (r'trigger', 'trigger'), (r'bulletcase|case|hull|brass', 'case'),
    (r'bullet|round|cartridge', 'round'), (r'slide', 'slide'),
    # 'clip' is a magazine by another name -- the HacX UZI calls its magazine
    # 'clip' and its release 'clipRelease', and with only 'mag' in this table the
    # tool saw a magazine and called it nothing. Order matters: clipRelease must
    # hit 'release' above before this line turns it into a magazine.
    # ...but 'mag' as a bare substring also swallows the magazine's FURNITURE. The
    # Chaingun names its feed panels mag_cover, mag_cover.001..003 and got four
    # magazines, one of them 61 units long. A cover, well, housing, guide or feed
    # is the hole the magazine goes into, never the magazine, so it stays a part.
    (r'(?:mag|clip)(?!\w*(?:cover|well|hous|guide|catch|port|chute|feed|plate|lip))', 'mag'),
    (r'pump|forend|foregrip', 'pump'),
    (r'bolt', 'bolt'), (r'barrel', 'barrel'), (r'body|frame|receiver', 'body'), (r'sight', 'sight'), (r'stock', 'stock'),
    (r'grip|handle', 'grip'), (r'loader', 'loader'), (r'lever', 'lever'),
]
def role_of(name):
    n = name.lower()
    # A name made only of Blender's default primitives carries no role. Stripping them
    # leaves nothing, and that is the test -- a bare substring match on 'cyl' turned
    # every Cylinder into a revolver cylinder, which gave the MG42 four of them and a
    # chamber/eject/load it has no business having ('chambers 0' was the tell). The
    # compound names the exporter makes, Cylinder.000_Cylinder.010, need this rather
    # than a lookahead.
    if not re.sub(r'(cylinder|cube|sphere|plane|circle|object|mesh|icosphere|torus|cone)'
                  r'|[\d._\s-]', '', n):
        return 'part'
    for rx, r in NAMES:
        if re.search(rx, n): return r
    return 'part'

def pca(P):
    c = P.mean(0); w, v = np.linalg.eigh(np.cov((P - c).T)); return c, v[:, 2], v[:, 0]   # centroid, long axis, thin axis
def f3(v): return "[" + ", ".join(f"{x:.2f}" for x in v) + "]"
def ax(v): return "[" + ", ".join(f"{x:.3f}" for x in v) + "]"

m = read_md3(sys.argv[1]); name = sys.argv[2]; arche = sys.argv[3]
S = m['surfs']; X = {s['name']: s['xyz'][0] for s in S}
roles = {s['name']: role_of(s['name']) for s in S}
# The largest surface is USUALLY the receiver -- but not always, and forcing it
# to 'body' unconditionally ate the MG42's belt drum, which outweighs every piece
# of the gun it hangs off. Once a body is split into bore-slabs the biggest piece
# is arbitrary anyway. So only a surface whose own name does not already say what
# it is may be claimed for the body; a mag, slide or trigger keeps its role.
# Only a name that marks a DETACHABLE or MOVING piece blocks the claim. Authors
# routinely call a whole gun 'Handle' -- the MP40, Kar98, Tommy and STG44 all do --
# so treating 'grip'/'handle'/'stock'/'barrel' as disqualifying handed the STG44's
# 34-unit receiver the role 'grip' and left the body to a scrap.
_KEEPS_ROLE = {'mag', 'slide', 'bolt', 'trigger', 'hammer', 'round',
               'case', 'latch', 'cyl', 'crane', 'ejector', 'pump'}
_cand = [s for s in S if role_of(s['name']) not in _KEEPS_ROLE] or S
body = max(_cand, key=lambda s: s['nverts'])['name']; roles[body] = 'body'
B = X[body]; bore = np.array([1.0, 0, 0]); down = np.array([0, 0, -1.0])
out = [f"weapon {name}", f"  archetype   {arche}        # from source names", f"  model       {name}.md3   space WPN   idle_frame 0",
       f"  bore        {ax(bore)}   down {ax(down)}", "  parts"]
count = {}
rounds = [n for n in roles if roles[n] == 'round']; cases = [n for n in roles if roles[n] == 'case']
cyl = next((n for n in roles if roles[n] == 'cyl'), None)
boreZ = None
if cyl:
    cc = X[cyl].mean(0)
    if rounds:  # the chamber in line with the barrel is the top one
        top = max(rounds, key=lambda n: X[n].mean(0)[2]); boreZ = X[top].mean(0)[2]
    else: boreZ = cc[2]
if boreZ is None: boreZ = B[B[:, 0] > B[:, 0].max() - 3][:, 2].mean()
for i, s in enumerate(S):
    n = s['name']; r = roles[n]; P = X[n]; c, lng, thin = pca(P); size = P.max(0) - P.min(0)
    count[r] = count.get(r, 0) + 1; label = r if count[r] == 1 else f"{r}{count[r]}"
    if r == 'body': continue
    extra = ""
    if r == 'cyl':
        extra = f"  rot 360deg axis {ax(bore)}  chambers {len(rounds)}   # revolves about the bore-parallel axis through rest"
        c = np.array([c[0], cc[1], cc[2]])
    elif r == 'crane':
        low = P[P[:, 2] < P[:, 2].min() + 0.6]; piv = np.array([low[:, 0].mean(), low[:, 1].mean(), P[:, 2].min() + 0.3])
        extra = f"  rot 90deg axis {ax(bore)}  pivot {f3(piv)}   # cylinder swings out to the left (-Y) about this"
    elif r == 'ejector':
        extra = f"  travel {size[0] * 0.35:.2f}  dir {ax(-bore)}   # rod pushed rearward through the swung-out cylinder"
    elif r == 'hammer':
        low = P[P[:, 2] < P[:, 2].min() + 0.8]; piv = low.mean(0)
        extra = f"  rot 35deg axis [0.000, 1.000, 0.000]  pivot {f3(piv)}"
    elif r == 'trigger':
        top = P[P[:, 2] > P[:, 2].max() - 0.8]; piv = top.mean(0)
        extra = f"  rot 20deg axis [0.000, 1.000, 0.000]  pivot {f3(piv)}"
    elif r == 'latch':
        extra = f"  travel {size[0] * 0.25:.2f}  dir {ax(bore)}   # thumb pushes the release forward"
    elif r in ('round', 'case'):
        extra = f"  chamber {count[r]}   # seated; hide to show empty"
    out.append(f"    {label:<8} surf {i}  rest {f3(c)}  axis {ax(lng)}  size {f3(size)}{extra}")
muzzle = np.array([B[:, 0].max(), 0.0, boreZ])
out.append(f"    muzzle    {f3(muzzle)}")
if cyl:
    rear = np.array([X[cyl][:, 0].min(), cc[1], cc[2]])
    out.append(f"    chamber   {f3(np.array([X[cyl][:, 0].max(), 0.0, boreZ]))}   # top chamber mouth")
    out.append(f"    eject     {f3(rear)}  normal {ax(-bore)}   # cylinder rear face; cases leave here when swung out")
    out.append(f"    load      {f3(rear)}   # rounds/speedloader go in the rear face when swung out")
# grip: lowest third of the body along Z
G = B[B[:, 2] < B[:, 2].min() + (B[:, 2].max() - B[:, 2].min()) * 0.33]; gc, glng, _ = pca(G)
if glng[2] > 0: glng = -glng
hi = G[G[:, 2] > G[:, 2].max() - 0.5].mean(0); lo = G[G[:, 2] < G[:, 2].min() + 0.5].mean(0)
trig = next((n for n in roles if roles[n] == 'trigger'), None); tp = X[trig].mean(0) if trig else hi
out.append(f"  grip        line {f3(hi)} {f3(lo)}  trigger {f3(tp)}   # centroid-based; owner's hand fit supersedes")
out.append(f"  support     feature palm {f3(hi + np.array([4, 0, 0]))}   # one-handed gun; placeholder")
out.append("  phases\n    idle         0..0")
out.append(f"  authoring   surfaces_named_in_source yes  tags_in_source 0  frame_names_in_source no  verts {sum(s['nverts'] for s in S)}  frames {m['nframes']}")
print("\n".join(out))
