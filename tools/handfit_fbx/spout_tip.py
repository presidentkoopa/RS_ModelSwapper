"""Round 6: the Flamethrower2 flame outlet (spout tip) = centre of the front opening of the heat-shield cylinder
(surface 0, F 81.5-83, robust circle fit), moved with the fit's gun move into the controller frame. Replaces final6.py's
first estimate (the front-most surface-0 points: that was the igniter rod, L 4.06). headsetpack.py (LANEC_FLAMESPOUT)
writes this tip into zscript/rsq/flamespout.zs. (Was run inline in the prototype; code unchanged.)
Updates results/round6_final.json (tip_gun, tip_controller_cm, tip_note)."""
import numpy as np,scene,gunfield,json,solve,pump_rules,os
from scipy.optimize import least_squares
S=scene.item_verts(scene.GUNS['Flamethrower2']); P=gunfield.sample_surface(S[0][1],S[0][0],0.05)[0]
q=P[(P[:,0]>81.5)&(P[:,0]<83.0)&(np.abs(P[:,1])<4.8)&(P[:,2]<-0.5)]
r=least_squares(lambda p: np.hypot(q[:,1]-p[0],q[:,2]-p[1])-p[2],[0,-7,6],loss='soft_l1',f_scale=0.2)
fm=q[:,0].max(); print('shield front F %.2f ring centre L %.2f U %.2f r %.2f'%(fm,*r.x))
tip=np.array([fm,r.x[0],r.x[1]])
c,x=pump_rules.ctx_from('Z3'); Rg,tg=solve.gun_T(c,x); tc=solve.gmove(c,Rg,tg,tip[None])[0]; print('tip controller frame cm',tc.round(2))
p=os.path.join(solve.LANE,'results','round6_final.json')
R6=json.load(open(p)); R6['Flamethrower2'].update(tip_gun=tip.tolist(),tip_controller_cm=tc.tolist(),tip_note='flame outlet = centre of the front opening of the heat-shield cylinder (surface 0, F 81.5-83, circle fit r %.2f cm); the earlier bore_c landmark (L 4.06) was the igniter rod'%r.x[2]); json.dump(R6,open(p,'w'),default=float)
