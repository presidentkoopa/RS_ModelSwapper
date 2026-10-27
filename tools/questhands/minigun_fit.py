import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))  # F12: the kit's own folder (was a scratchpad path)
import align, handfit, support, ermac, guns, gunview, hudrender, fitall
import numpy as np
P=np.array([[0,-1,0],[0,0,1],[-1,0,0]],float)   # FLU -> local (x=-L, y=U, z=-F)
def rot_hook(c_flu, t_flu, Rw):
    """hook + engine rotation that turn Ermac's hand (placed by his block) by Rw
    (FLU) about c and move c to t"""
    Sx=np.diag([-1.0,1,1]); off=np.array([0,-10,-24.0]); K=np.array([0,5,30.0])
    Rl=P@Rw@P.T
    R=Sx@Rl@Sx
    ypr=support.euler_yxz(R)
    R=support.rot(ypr)
    c=P@np.array(c_flu); t=P@np.array(t_flu)
    hook=np.linalg.inv(R)@np.linalg.inv(Sx)@(Rl@(off+K-c)+t-off-K)
    return [round(float(x),2) for x in hook],[round(float(x),2) for x in ypr]
def frame(a,u):
    a=np.array(a,float); a/=np.linalg.norm(a); u=np.array(u,float); u-=a*(u@a); u/=np.linalg.norm(u)
    return np.stack([a,np.cross(u,a),u],1)
if __name__=='__main__':
    gE,hE=align.ermac_points('chaingun',2); patch=align.held_patch(gE,hE)
    c=patch.mean(0)
    v=align.surface_points(guns.item('Minigun'))
    h=align.box(v,f=(28,39),l=(11,29),u=(-12,1))
    t=h.mean(0)
    print('ermac handle centre',c.round(2),'our handle centre',t.round(2))
    # Ermac's handle runs along F with the palm on top; ours runs out to the left, rising
    a=np.array([0,0.88,0.47])
    Rw=frame(a,(0,-0.47,0.88))@frame((1,0,0),(0,0,1)).T
    hook,ypr=rot_hook(c,t,Rw)
    print('hook',hook,'rot',ypr)
    gt,_,_=align.fit('Minigun','plasma',1,dict(f=(-22,6),l=(-5,5),u=(-24,-1)))
    gt=gt+np.array([0,0,-1.5])
    items=[dict(path=ermac.path('hand/hand.md3'),frame=106,hook=align.hook_from_shift(gt),color=[225,170,135],**ermac.PL),
           dict(path=ermac.path('hand/hand2.md3'),frame=70,hook=hook,rot=ypr,color=[120,200,140],**ermac.PL)]
    handfit.sheet('Minigun',items,handfit.out('fit_Minigun.png'),'Minigun')
    import json
    d=json.load(open(handfit.FITS))
    d['Minigun']={'gun_set':'plasma','gun_shift':gt.round(2).tolist(),'sup_set':'chaingun','where':['handle'],
                  'sup_hook':hook,'sup_rot':ypr,'target':t.round(2).tolist()}
    json.dump(d,open(handfit.FITS,'w'),indent=1)
