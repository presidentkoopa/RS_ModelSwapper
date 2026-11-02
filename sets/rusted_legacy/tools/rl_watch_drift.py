#!/usr/bin/env python3
"""rl_watch_drift.py: how far his wrist watch is from the wrist it is worn on, in every frame his guns draw.

His watch (modeldefs/holohud.txt) is its own set of layers with ONE w_dial frame per gun (the gun hand's
Ready pose); the gun hand (hand.md3, the gun's MODELDEF) changes frame through firing, pumping and
reloading. w_dial frame k is made for hand.md3 frame k (checked: 0.7-1.5 cm off the wrist for every k).
For each weapon sprite frame in the gun's MODELDEF (all blocks, every alt sprite), this fits the wrist
(hand vertices within 6 cm of the dial at the watch frame) rigidly onto the same vertices in the frame
drawn, and reports how far the dial centre is from where that wrist would carry it. Mesh measured.

  python3 sets/rusted_legacy/tools/rl_watch_drift.py [gun ...] [-v]
"""
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.dirname(HERE)
os.environ.setdefault('RSQ_RL', os.path.join(SET, 'src'))
sys.path.insert(0, HERE)
import rl_measure as R  # noqa: E402
import md3label  # noqa: E402

GUNS = ['pistol', 'shotgun', 'ssg', 'chaingun', 'plasma', 'rocket', 'hellshotgun', 'incinerator', 'bfg', 'heatwave',
        'chainsaw']
PL = dict(scale=[-1, 1, 1], off=[0, -24, -10])
FILES = {'pistol': 'pistol', 'shotgun': 'shotgun', 'ssg': 'ssg', 'chaingun': 'chaingun', 'plasma': 'plasmarifle',
         'rocket': 'rocketlauncher', 'hellshotgun': 'hellshotgun', 'incinerator': 'incinerator', 'bfg': 'bfg9000',
         'heatwave': 'heatwave', 'chainsaw': 'chainsaw'}


def watch_frame(actor):
    """the dial mesh (w_dial.md3, or w_dial2.md3 for shotgun, SSG, hell shotgun, BFG) and its frame"""
    b = R.actor_blocks(os.path.join(R.MOD, 'modeldefs/holohud.txt'), actor)
    return (re.search(r'Model\s+0\s+"([^"]+)"', b[0]).group(1),
            int(re.search(r'FrameIndex\s+\S+\s+\S\s+0\s+(\d+)', b[0]).group(1)))


def hand_frames(gun):
    """(sprite, letter) -> hand.md3 frame, over every block of the gun's MODELDEF (Model n reassigned in order)"""
    t = open(os.path.join(R.MOD, 'modeldefs/weapons/%s.txt' % FILES[gun]), errors='replace').read()
    t = re.sub(r'//[^\n]*', '', t)
    out = {}
    for b in re.findall(r'Model\s+' + R.ACTOR[gun] + r'\s*\{(.*?)\n\}', t, re.S):
        slots = {}
        for line in b.splitlines():
            m = re.match(r'\s*Model\s+(\d+)\s+"([^"]+)"', line)
            if m:
                slots[int(m.group(1))] = m.group(2).lower()
            for s, l, slot, fr in re.findall(r'FrameIndex\s+(\w{4})\s+(\w)\s+(\d+)\s+(\d+)', line):
                if slots.get(int(slot)) == 'hand.md3':
                    out[(s, l)] = int(fr)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    verbose = '-v' in sys.argv
    hand = R.md3('models/hand/hand.md3')
    H = [np.vstack([R.to_flu(md3label.surf_xyz(s)[f]) for s in hand['surfs']]) for f in range(hand['nframes'])]
    res = {}
    for gun in args or GUNS:
        wmesh, wf = watch_frame(R.ACTOR[gun])
        dial = R.md3('models/common/' + wmesh)
        D = np.vstack([R.flu_pl(md3label.surf_xyz(s)[wf], PL) for s in dial['surfs']])
        c = D.mean(0)
        idx = np.where(np.linalg.norm(H[wf] - c, axis=1) < 6.0)[0]
        P = H[wf][idx]
        hf = hand_frames(gun)
        drift = {}
        for key, f in sorted(hf.items()):
            if f >= len(H):
                drift[key] = (f, None)
                continue
            Q = H[f][idx]
            pc, qc = P.mean(0), Q.mean(0)
            U, S, Vt = np.linalg.svd((P - pc).T @ (Q - qc))
            d = np.sign(np.linalg.det(Vt.T @ U.T))
            Rm = Vt.T @ np.diag([1, 1, d]) @ U.T
            drift[key] = (f, float(np.linalg.norm(Rm @ (c - pc) + qc - c)))
        res[gun] = (wf, drift)
        vals = [v for _, v in drift.values() if v is not None]
        far = sorted(((v, k) for k, (f, v) in drift.items() if v is not None and v > 1.5), reverse=True)
        print('%-11s watch frame %3d, %3d gun frames: on the wrist (<=1.5 cm) %3d, off %3d, worst %.1f cm %s'
              % (gun, wf, len(drift), sum(v <= 1.5 for v in vals), len(far), max(vals) if vals else 0,
                 ''.join(far[0][1]) if far else ''))
        if verbose:
            for v, k in far:
                print('    %s%s hand frame %d: %.1f cm' % (k[0], k[1], drift[k][0], v))
    return res


if __name__ == '__main__':
    main()
