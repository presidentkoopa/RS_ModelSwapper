import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))  # F12: the kit's own folder (was a scratchpad path)
import pk3model
import os
# F12: was S=<scratchpad>, the pack read from S/v7x (an extracted pack). Now Depot-relative / env:
HERE=os.path.dirname(os.path.abspath(__file__))
DEPOT=os.path.abspath(os.path.join(HERE,'..','..'))
# RSQ_GUNPACK: an extracted pack folder with MODELDEF.bd.txt and its models/. Default: tag 1.92 of
# RS_Brutal22WeaponsQ, which tools/rig/setup.sh checks out.
PACK=os.environ.get('RSQ_GUNPACK', os.path.join(DEPOT,'tools','rig','build','src','bd22q_192','src'))
OUT=os.environ.get('RSQ_QH_OUT', os.path.join(HERE,'out'))
READY = [('Rifle','RIFG','A'),('BrutalPistol','PIST','A'),('BrutalSMG','SMGS','A'),('MP40','MP40','A'),
 ('Sniper','X21G','A'),('AssaultShotgun','USAS','A'),('Shot_Gun','SHTN','A'),('Revolver','REVO','A'),
 ('SSG','SHTZ','A'),('Rocket_Launcher','MISG','A'),('RailGun','RAIL','A'),('Plasma_Gun','PRSG','F'),
 ('GrenadeLauncher','GRLN','A'),('Minigun','CHAG','A'),('BIG_FUCKING_GUN','BFGN','A'),('BFG10k','BG2G','A'),
 ('Unmaker','UNHG','A'),('FlameCannon','FLMG','A'),('Flamethrower2','FLMT','A'),('HellishMissileLauncher','RVCG','A'),
 ('IncendiaryLauncher','M202','A'),('MG42','HBUS','A'),('NukeLauncher','NKLG','A'),('Devastator','DEVA','A')]
_bl=None
def item(cls, spr=None, fr=None):
    global _bl
    if _bl is None:
        md=os.path.join(PACK,'MODELDEF.bd.txt')
        if not os.path.exists(md):
            raise SystemExit('questhands: no %s. Set RSQ_GUNPACK to an extracted pack folder, or run sh tools/rig/setup.sh '
                             '(it checks out the 1.92 pack this defaults to).' % md)
        _bl=pk3model.blocks(open(md,encoding='latin-1').read())
    if spr is None:
        for c,s,f in READY:
            if c==cls: spr,fr=s,f
    it=pk3model.lookup(_bl,cls,spr,fr,PACK)
    if it: it['key']=(spr,fr)
    if it and cls=='Sniper':
        # v8 placement (fill_tables.py): v4-v7 had the HK416 turned round
        it['scale']=[-1.35,1.35,1.35]; it['off']=[6.499,-3.835,10.913]
    return it
