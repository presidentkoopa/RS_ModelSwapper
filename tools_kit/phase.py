import os
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from md3read import read_md3
m=read_md3(sys.argv[1]); S=m['surfs']; body=4; B=S[body]['xyz']; nf=m['nframes']
def kabsch(P,Q):
    pc,qc=P.mean(0),Q.mean(0); H=(P-pc).T@(Q-qc); U,_,Vt=np.linalg.svd(H); d=np.sign(np.linalg.det(Vt.T@U.T)); R=Vt.T@np.diag([1,1,d])@U.T; return R,qc-R@pc
# body principal axes (bore direction guess = longest)
P=B[0]-B[0].mean(0); w,v=np.linalg.eigh(P.T@P); order=np.argsort(w)[::-1]; ax=v[:,order]
print("body principal axes (longest first):", np.round(ax.T,2), "extents", np.round(np.sqrt(w[order]/len(P))*2,1))
Rs=[kabsch(B[0],B[f]) for f in range(nf)]
def rel(i,f):
    R,t=Rs[f]; return ((S[i]['xyz'][f]-t)@R).mean(0)-S[i]['xyz'][0].mean(0)
for i in [0,5,1,3,2]:
    print(f"surf{i}: frame -> displacement vector (model space)")
    for f in range(nf):
        d=rel(i,f); n=np.linalg.norm(d)
        if n>0.3: print(f"   f{f:2d} {n:5.1f}  dir {np.round(d/n,2)}")
# rigid body motion itself: how much does the whole gun move/rotate per frame?
print("whole-gun motion (body) per frame: translation of centroid, rotation angle deg")
for f in range(nf):
    R,t=Rs[f]; ang=np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1))); c=B[f].mean(0)-B[0].mean(0)
    print(f"   f{f:2d} move {np.linalg.norm(c):5.1f} rot {ang:5.1f}")
