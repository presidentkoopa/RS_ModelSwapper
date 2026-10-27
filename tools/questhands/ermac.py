import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))  # F12: the kit's own folder (was a scratchpad path)
import os
# F12: Ermac's Force Unleashed models/ folder (doom-force-unleashed_devbuild/models: hand/hand.md3,
# hand/hand2.md3 and the gun meshes named in SETS). Not vendored in the Depot; set RSQ_ERMAC.
# Was the hard-coded upload path /mnt/user-data/uploads/DOOMWork/_old/doom-force-unleashed_devbuild/models/.
E = os.environ.get('RSQ_ERMAC')
def path(rel):
    if not E:
        raise SystemExit("questhands: RSQ_ERMAC is not set. Point it at Ermac's doom-force-unleashed_devbuild/models/ "
                         "folder (hand/hand.md3, hand/hand2.md3, his gun meshes); it is not in the Depot.")
    p = os.path.join(E, rel)
    if not os.path.exists(p):
        raise SystemExit('questhands: Ermac asset %s not found under RSQ_ERMAC=%s' % (rel, E))
    return p
# Ermac's ready (gun frame, hand.md3 frame, hand2.md3 frame), from his "with both hands" blocks
SETS = {
 'pistol': ('pistol/berreta.md3', 0, 19, 4, 6),       # last: hand.md3 frame for one hand
 'shotgun': ('shotgun/shotgun.md3', 0, 30, 15, 30),
 'ssg': ('ssg/ssg.md3', 0, 47, 33, 47),
 'chaingun': ('chaingun/chaingun.md3', 0, 84, 70, 84),
 'rocket': ('rocketlauncher/rocketlauncher.md3', 0, 95, 80, 95),
 'plasma': ('plasmarifle/plasma_rifle.md3', 0, 106, 91, 106),
 'bfg': ('bfg9000/bfg9000.md3', 0, 113, 98, 113),
 'flamer': ('incinerator/flamethrower.md3', 0, 151, 136, 151),
}
PL = dict(scale=[-1.0, 1.0, 1.0], off=[0.0, -24.0, -10.0])
def items(name, hook=(0,0,0), two=True):
    g, gf, h1, h2, h1one = SETS[name]
    out = [dict(path=path(g), frame=gf, color=[150,155,170], **PL),
           dict(path=path('hand/hand.md3'), frame=h1 if two else h1one, color=[225,170,135], **PL)]
    if two:
        out.append(dict(path=path('hand/hand2.md3'), frame=h2, color=[120,200,140], **PL))
    return out
