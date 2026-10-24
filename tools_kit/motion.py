#!/usr/bin/env python3
"""motion.py -- per-surface rigid motion relative to the body, with rotation and appearance.
usage: motion.py model.md3 [idle_frame]"""
import os
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from md3read import read_md3

def kabsch(P, Q):
    pc, qc = P.mean(0), Q.mean(0); H = (P-pc).T @ (Q-qc); U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T)); R = Vt.T @ np.diag([1, 1, d]) @ U.T; return R, qc - R @ pc

def rot_axis_angle(R):
    ang = np.degrees(np.arccos(np.clip((np.trace(R)-1)/2, -1, 1)))
    w = np.array([R[2,1]-R[1,2], R[0,2]-R[2,0], R[1,0]-R[0,1]]); n = np.linalg.norm(w)
    return ang, (w/n if n > 1e-9 else np.zeros(3))

m = read_md3(sys.argv[1]); S = m['surfs']; nf = m['nframes']
body = max(range(len(S)), key=lambda i: S[i]['nverts'])
B = S[body]['xyz']
# idle: first frame after which consecutive body rotation < 2 deg (raise ends), else 0
idle = int(sys.argv[2]) if len(sys.argv) > 2 else 0
if len(sys.argv) <= 2:
    for f in range(1, nf):
        a, _ = rot_axis_angle(kabsch(B[f-1], B[f])[0])
        if a < 2.0: idle = f-1; break
Rs = [kabsch(B[f], B[idle]) for f in range(nf)]
def to_wpn(i, f): R, t = Rs[f]; return S[i]['xyz'][f] @ R.T + t
print(f"{sys.argv[1]}: frames={nf} surfaces={len(S)} body=surf{body} ({S[body]['nverts']} v) idle={idle}")
sway = [rot_axis_angle(Rs[f][0])[0] for f in range(nf)]
print("  body sway vs idle (deg):", " ".join(f"{f}:{sway[f]:.0f}" for f in range(nf) if sway[f] > 2) or "none")
for i, s in enumerate(S):
    X = [to_wpn(i, f) for f in range(nf)]
    ext = [X[f].max(0) - X[f].min(0) for f in range(nf)]
    size_idle = ext[idle]; diag = [np.linalg.norm(e) for e in ext]
    visible = [f for f in range(nf) if diag[f] > 0.5]
    if diag[idle] < 0.5:
        print(f"  surf{i:<2} {s['name'][:22]:<22} v={s['nverts']:5d}  HIDDEN at idle; appears frames {visible[:3]}..{visible[-3:] if visible else ''} size {np.round(ext[visible[0]],1) if visible else '-'}")
        continue
    if i == body:
        print(f"  surf{i:<2} {s['name'][:22]:<22} v={s['nverts']:5d}  BODY size {np.round(size_idle,1)}"); continue
    c0 = X[idle].mean(0); best_t = 0; best_tf = idle; best_r = 0; best_rf = idle; raxis = np.zeros(3); tdir = np.zeros(3)
    act = []
    for f in range(nf):
        if diag[f] < 0.5: continue
        R, t = kabsch(X[idle], X[f]); ang, ax = rot_axis_angle(R)
        d = X[f].mean(0) - c0; dn = np.linalg.norm(d)
        if dn > best_t: best_t, best_tf, tdir = dn, f, d/dn
        if ang > best_r: best_r, best_rf, raxis = ang, f, ax
        if dn > 0.5 or ang > 3: act.append(f)
    kind = "static"
    if best_r > 15 and best_t < 0.35*best_r: kind = "HINGE/ROTATES"
    elif best_t > 2: kind = "SLIDES"
    elif best_t > 0.3 or best_r > 3: kind = "small motion"
    print(f"  surf{i:<2} {s['name'][:22]:<22} v={s['nverts']:5d}  size {np.round(size_idle,1)}  rest {np.round(c0,1)}  {kind}: travel {best_t:.1f} dir {np.round(tdir,2)} @f{best_tf}; rot {best_r:.0f}deg axis {np.round(raxis,2)} @f{best_rf}; active {act[:4]}..{act[-2:] if len(act)>4 else ''}")
