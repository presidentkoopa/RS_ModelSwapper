import sys, json
sys.path.insert(0,'C:/Users/Command/Desktop/Quest_Weapons_Kit/kit/kit/melee')
import align, handfit, support, handtable, ermac, guns
import numpy as np
S=handfit.S
GUN_DROP={'Rocket_Launcher':-4.0}
def hand_centroid(sset, which):
    g,gf,h1,h2,_=ermac.SETS[sset]
    it=dict(path=ermac.E+('hand/hand.md3' if which==1 else 'hand/hand2.md3'),frame=h1 if which==1 else h2,**ermac.PL)
    return align.surface_points(it,per_tri=False).mean(0)
def run(cls):
    gs,ss,where=handtable.TABLE[cls]
    t,err,_=align.fit(cls,gs,1,dict(f=(-22,6),l=(-5,5),u=(-24,-1)))
    t=t+np.array([0,0,GUN_DROP.get(cls,-1.5)])
    r={'gun_set':gs,'gun_shift':t.round(2).tolist(),'gun_err':round(err,2),'sup_set':ss,'where':list(where),'sup_rot':[0,0,0]}
    if where[0]=='same':
        t2=t.copy(); err2=0.0
        r['target']=(hand_centroid(ss,2)+t2).round(2).tolist()
    elif where[0]=='wrap':
        gE,hE=align.ermac_points(ss,2); patch=align.held_patch(gE,hE)
        fp,(lo,hi)=support.front_point(cls,where[1])
        if hi-lo>6:
            reg=dict(f=(fp[0]-10,fp[0]+10),l=(-7,7),u=(lo-3,lo+3.5))
        else:
            reg=dict(f=(fp[0]-10,fp[0]+10),l=(-7,7),u=(fp[2]-8,fp[2]+8))
        t0=np.array(fp)-patch.mean(0)
        t2,err2,_=align.fit(cls,ss,2,reg,t0=t0)
        t2[1]=-patch.mean(0)[1]   # centred across the gun
        r['target']=fp
    elif where[0]=='vgrip':
        gO=align.surface_points(guns.item(cls))
        b=align.box(gO,f=where[1],l=(-4,4),u=where[2])
        c=b.mean(0)
        t2=c-hand_centroid(ss,2); err2=0.0
        r['target']=c.round(2).tolist()
    else:
        return r, t, None
    r['sup_shift']=np.round(t2,2).tolist(); r['sup_err']=round(float(err2),2)
    return r, t, t2
if __name__=='__main__':
    res={}
    only=sys.argv[1:]
    for cls in handtable.TABLE:
        if only and cls not in only: continue
        r,t,t2=run(cls)
        res[cls]=r
        print(cls, r, flush=True)
        if t2 is not None:
            handfit.sheet(cls,handfit.hand_items(r['gun_set'],t,r['sup_set'],t2),S+'/hands/fit_%s.png'%cls,cls)
    old={}
    try: old=json.load(open(S+'/hands/fits.json'))
    except Exception: pass
    old.update(res)
    json.dump(old,open(S+'/hands/fits.json','w'),indent=1)
