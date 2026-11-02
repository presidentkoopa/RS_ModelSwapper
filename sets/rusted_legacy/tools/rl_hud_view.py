#!/usr/bin/env python3
"""rl_hud_view.py: can the player read his gun ammo display and his watch? Measured on the meshes.

For each gun: the panel (models/common/ammo_hud_bg.md3 with the gun's holohud2.txt Scale/Offset) and the
watch dial (w_dial.md3, holohud.txt) in the controller frame (cm, F/L/U, same chain as rl_measure.py), the
gun and both hands at Ready (the card's frames), and two eyes:
  rig   (-30, 25, 30): tools/rig defaults, head (0 1.6 0) and gun hand (0.25 1.3 -0.3, pitch 30 = level)
  aim   (-35,  0,  9): the eye behind the gun at sight height, gun raised to aim
Reported: the share of the panel / dial hidden behind the gun or the hands from each eye (rays to a 9 x 5
grid on the face), how far the panel is from the nearest gun or hand vertex, and the viewing angle (0 =
face on). Nothing is changed.

  python3 sets/rusted_legacy/tools/rl_hud_view.py [gun ...]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.dirname(HERE)
os.environ.setdefault('RSQ_RL', os.path.join(SET, 'src'))
sys.path.insert(0, HERE)
import rl_measure as R  # noqa: E402
import md3label  # noqa: E402

EYES = {'rig': np.array([-30.0, 25.0, 30.0]), 'aim': np.array([-35.0, 0.0, 9.0])}
GUNS = ['pistol', 'shotgun', 'ssg', 'chaingun', 'plasma', 'rocket', 'hellshotgun', 'incinerator', 'bfg', 'heatwave',
        'chainsaw']


def mesh_tris(m):
    T = []
    for slot in (0, 2, 3):
        if slot not in m['models'] or slot not in m['ready_frames']:
            continue
        mm = R.md3(m['models'][slot])
        f = m['ready_frames'][slot]
        if f >= mm['nframes']:
            continue
        for s in mm['surfs']:
            x = md3label.surf_xyz(s)[f]
            if not R.visible(x):
                continue
            v = R.to_flu(x)
            t = md3label.surf_tris(s)
            T.append(np.stack([v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]], 1))
    return np.concatenate(T)


def blocked(eye, pts, T):
    """for each point, does the segment eye -> point hit a triangle (Moller-Trumbore, all triangles at once)"""
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    e1, e2 = b - a, c - a
    out = []
    for p in pts:
        d = p - eye
        L = np.linalg.norm(d)
        d = d / L
        h = np.cross(d, e2)
        det = np.einsum('ij,ij->i', e1, h)
        ok = np.abs(det) > 1e-9
        inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
        s = eye - a
        u = np.einsum('ij,ij->i', s, h) * inv
        q = np.cross(s, e1)
        v = (q @ d) * inv
        t = np.einsum('ij,ij->i', e2, q) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0.05) & (t < L - 0.3)
        out.append(bool(hit.any()))
    return np.array(out)


def face_grid(X, n):
    """9 x 5 points on the face of a flat mesh X with normal n"""
    c = X.mean(0)
    w, V = np.linalg.eigh(np.cov((X - c).T))
    a1, a2 = V[:, 2], V[:, 1]
    p1, p2 = (X - c) @ a1, (X - c) @ a2
    g = [c + a1 * (p1.min() + (p1.max() - p1.min()) * (i + .5) / 9) + a2 * (p2.min() + (p2.max() - p2.min()) * (j + .5) / 5)
         for i in range(9) for j in range(5)]
    return np.array(g) + n * 0.05


def main():
    guns = sys.argv[1:] or GUNS
    rows = []
    for gun in guns:
        m = R.measure(gun)
        hud = R.measure_hud(m, R.ACTOR[gun])
        T = mesh_tris(m)
        V = T.reshape(-1, 3)
        line = ['%-11s' % gun]
        for key, lab in (('gun_display', 'panel'), ('wrist_watch', 'watch')):
            h = hud.get(key)
            if not h or '_X' not in h:
                line.append('%s: none' % lab)
                continue
            X = h['_X']
            c = X.mean(0)
            n = np.array(h['facing'])
            pts = face_grid(X, n)
            gap = float(np.min(np.linalg.norm(V[None, :, :] - X[::max(1, len(X) // 60), None, :], axis=2)))
            parts = []
            for en, eye in EYES.items():
                hid = blocked(eye, pts, T).mean()
                v = eye - c
                ang = np.degrees(np.arccos(abs(np.dot(v / np.linalg.norm(v), n))))
                parts.append('%s hidden %3.0f%% at %2.0f deg' % (en, 100 * hid, ang))
            line.append('%s gap %.1f cm, %s' % (lab, gap, '; '.join(parts)))
            rows.append(dict(gun=gun, what=lab, centre=[round(x, 2) for x in c], gap=round(gap, 2), detail=parts))
        print('  '.join(line))
    out = os.path.join(SET, 'cards', 'hud_view.json')
    if len(guns) == len(GUNS):
        json.dump(rows, open(out, 'w'), indent=1)
        print('wrote', os.path.relpath(out))


if __name__ == '__main__':
    main()
