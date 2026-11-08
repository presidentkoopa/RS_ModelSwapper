import os
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, sys
from md3read import read_md3
m = read_md3(sys.argv[1])
S = m['surfs']
body = max(range(len(S)), key=lambda i: S[i]['nverts'])
def kabsch(P, Q):
    pc, qc = P.mean(0), Q.mean(0)
    H = (P-pc).T @ (Q-qc)
    U, _, Vt = np.linalg.svd(H)
    dd = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1,1,dd])
    R = Vt.T @ D @ U.T
    return R, qc - R@pc
nf = m['nframes']
B = S[body]['xyz']
print(f"body = surface {body} ({S[body]['nverts']} verts). Residual motion of each surface after removing body's rigid motion per frame (model units, 1u=1cm*scale):")
res = {}
for i,s in enumerate(S):
    r=[]
    for f in range(nf):
        R,t = kabsch(B[0], B[f])
        back = (s['xyz'][f] - t) @ R    # bring frame f into body frame-0 space
        r.append(back.mean(0) - s['xyz'][0].mean(0))
    r=np.array(r); res[i]=r
    mag=np.linalg.norm(r,axis=1)
    print(f"  surf{i} v={s['nverts']:5d} size={np.round(s['xyz'][0].max(0)-s['xyz'][0].min(0),1)} c0={np.round(s['xyz'][0].mean(0),1)}  max resid={mag.max():5.2f} @f{mag.argmax()}  frames>0.5u: {[f for f in range(nf) if mag[f]>0.5]}")
print()
for i in res:
    mag=np.linalg.norm(res[i],axis=1)
    if mag.max()>0.5:
        k=mag.argmax(); ax=res[i][k]/mag[k]
        print(f"surf{i} peak axis {np.round(ax,2)} travel {mag.max():.2f}; per-frame displacement:")
        print("   "+" ".join(f"{f}:{mag[f]:.1f}" for f in range(nf)))
