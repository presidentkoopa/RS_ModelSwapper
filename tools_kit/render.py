import os
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from md3read import read_md3
m=read_md3(sys.argv[1]); S=m['surfs']; body=max(range(len(S)), key=lambda i:S[i]['nverts']); B=S[body]['xyz']
def kabsch(P,Q):
    pc,qc=P.mean(0),Q.mean(0); H=(P-pc).T@(Q-qc); U,_,Vt=np.linalg.svd(H); d=np.sign(np.linalg.det(Vt.T@U.T)); R=Vt.T@np.diag([1,1,d])@U.T; return R,qc-R@pc
# rotate frame-0 body space so the slide axis (-0.71,0,0.71)=back is drawn as -X: rotate by 45deg about Y
th=np.radians(float(sys.argv[4]) if len(sys.argv)>4 else 45); Rv=np.array([[np.cos(th),0,-np.sin(th)],[0,1,0],[np.sin(th),0,np.cos(th)]])
pal=['#d62728','#1f77b4','#ff7f0e','#2ca02c','#9467bd','#8c564b','#e377c2','#17becf','#bcbd22','#7f7f7f','#aec7e8','#ffbb78']
cols={i:pal[i%len(pal)] for i in range(len(S))}; cols[body]='#999999'
lab={i:f'surf{i} {S[i]["name"][:12]}' for i in range(len(S))}
frames=[int(x) for x in sys.argv[2].split(',')]
import os; IDLE=int(os.environ.get('IDLE','0'))
fig,axs=plt.subplots(1,len(frames),figsize=(4.2*len(frames),4.2))
for ax,f in zip(np.atleast_1d(axs),frames):
    R,t=kabsch(B[IDLE],B[f])
    for i,s in enumerate(S):
        P=((s['xyz'][f]-t)@R)@Rv.T
        tri=P[s['tris']]
        # light from +Y (viewer side): shade by normal y
        n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); ny=n[:,1]/(np.linalg.norm(n,axis=1)+1e-9)
        order=np.argsort(tri[:,:,1].mean(1))  # painter's: far (low y) first
        polys=tri[order][:,:,[0,2]]
        base=np.array(matplotlib.colors.to_rgb(cols[i]))
        shade=(0.45+0.55*np.clip(ny[order],0,1))[:,None]*base[None,:]
        ax.add_collection(PolyCollection(polys,facecolors=shade,edgecolors='none'))
    ax.autoscale(); ax.set_aspect('equal'); ax.margins(0.05); ax.set_title(f"frame {f}"); ax.axis('off')
h=[plt.Line2D([],[],color=cols[i],lw=6,label=lab[i]) for i in cols]
fig.legend(handles=h,loc='lower center',ncol=min(6,len(h)),fontsize=7,frameon=False)
plt.tight_layout(rect=(0,0.06,1,1)); plt.savefig(sys.argv[3],dpi=110)
