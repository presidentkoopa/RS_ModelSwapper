"""Round 3 gun MODELDEF placement (was run inline in the prototype; code unchanged): per gun, the rigid gun move of the
fit (x_gun) expressed as MODELDEF Offset / ZOffset / Angle / Pitch / RollOffset (gunplace.fit, exact).
Reads results/round3_final.json, writes results/gun_modeldef_R3.json (final6.py replaces the Flamethrower2 entry)."""
import numpy as np,json,os,solve,scene,gunview,hudrender,gunplace
LANE=solve.LANE
R=json.load(open(os.path.join(LANE,'results','round3_final.json'))); out={}
for cls,lm in (('BrutalPistol','BrutalPistol'),('Flamethrower2','Flamethrower2@nozzle')):
    x=np.array(R[cls]['x_gun']); ctx=solve.Ctx(lm,'R',None,'gunhand'); Rg,tg=solve.gun_T(ctx,x)
    it=scene.GUNS[cls]; V=np.concatenate([s['xyz'][it['frame']] for s in scene.md3_full(it['path'])])
    P=gunview.to_fl(hudrender.to_local(V,it)); r=gunplace.fit(it,solve.gmove(ctx,Rg,tg,P)); out[cls]=r; print(cls,r)
json.dump(out,open(os.path.join(LANE,'results','gun_modeldef_R3.json'),'w'),indent=1)
