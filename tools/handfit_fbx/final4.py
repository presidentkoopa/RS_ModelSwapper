"""Round 4 assembly (was run inline in the prototype, 2026-10-26; code unchanged): the Flamethrower2 support becomes the
open palm under the tank (results/Flamethrower2_under_D.json, run_under.py D); the pistol is round 3's.
Reads results/round3_final.json, writes results/round4_final.json."""
import json,numpy as np,solve,eval_under,os
LANE=solve.LANE
R=json.load(open(LANE+'/results/round3_final.json'))
d=json.load(open(LANE+'/results/Flamethrower2_under_D.json')); x=np.array(d['x'])
c,fld,Xg,gm=eval_under.ctx_for(d['T']); Xs,_=solve.hand_X(c,x)
m,r=eval_under.run('D',Xs)
f=R['Flamethrower2']; f['support_file']='Flamethrower2_under_D.json'; f['Xs']=Xs.tolist(); f['under']=m
f['rules']=[x_ for x_ in f['rules'] if x_[0].startswith('G')]+[list(a[:3]) for a in r]
for a in r: f['rule_sources'][a[0]]=a[3]
f['support_pose']='under (RS Avatar pose family cup/under; open palm cupped under the tank)'
json.dump(R,open(LANE+'/results/round4_final.json','w'),default=float)
print(' '.join(a[0]+a[2] for a in f['rules']))
