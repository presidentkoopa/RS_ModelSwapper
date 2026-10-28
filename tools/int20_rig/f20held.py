"""TEST ONLY (2.0 final): one eye frame per weapon held, the off hand on the gun's SupportPoint (handtable row) with the grip
pressed (the engine's two-hand hold, when the support hand shows); Melee_Attacks / HandGrenades (no row): off hand free in view.
The run ENDS in the held pose, so the frame is the last dumps (no wall-clock timing). Every run through run.sh (rig.lock -x,
INT20_INI copied in). f20held.py <pk3> <outdir> <Class...>"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, sys, glob, shutil, subprocess, re
from PIL import Image
R = (_DP.WORK + '/int20_rig')
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'handfit', 'support192'); sys.path.insert(0, H)
sys.path.insert(0, _DP.RIG)
os.environ.setdefault('B22_IWAD', (_DP.GAMEDATA + '/doom2.wad')); os.environ.setdefault('B22_RIG', R + '/bin')
import s192, rig
ROW = {}
for l in open(os.path.join(_DP.SRC, 'zscript', 'rsq', 'handtable.zs')):
    if "if (w is '" in l and 'return' in l:
        ROW.setdefault(l.split("'")[1], int(l.split('return')[1].split(';')[0]))
ROW['Railgun'] = ROW['RailGun']
FREE = (15.0, 12.0, 0.0)
# one-hand guns steady by closeness (hands.zs: off hand within 13 cm, the Depot gate's CUP list) and the axe / fists / grenade:
# NO grip press (a pressed grip makes the engine aim the gun at the off hand, which sits behind the gun hand on these)
NOGRIP = {'BrutalPistol', 'Revolver', 'BrutalRevolver', 'BrutalAxe', 'Melee_Attacks', 'HandGrenades'}
EYE = os.environ.get('F20_EYE', '0.10 1.62 0.02 -35 0 0')
pk3, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
for g in sys.argv[3:]:
    sp = tuple(100 * s192.ht_row('SupportPoint', ROW[g])) if g in ROW else FREE
    rh = '%.4f %.4f %.4f 30 0 0' % rig.RHAND
    s = ('wait 100; god; notarget; rsq_extra_weapons 1; screenblocks 12; crosshair 0; qz_rhand "%s"; give ammo; give %s; wait 2; use %s; wait 150; '
         'qz_hmd "%s"; qz_lhand "%s"; wait 10; %swait 50; quit' % (rh, g, g, EYE, rig.lpose(*sp), '' if g in NOGRIP else 'qz_lgrip 1; '))
    d = '%s/dump_held_%s' % (R, g); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    env = dict(os.environ, QZ_RES='480', QZ_DUMP_EVERY='3', QZ_DUMP_DIR=d)
    subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh'), 'f20held_' + g, pk3, '300', s], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    fr = sorted(glob.glob(d + '/*.ppm')); png = ''
    if len(fr) >= 3: png = '%s/held_%s.png' % (out, g); Image.open(fr[-3]).save(png)
    shutil.rmtree(d, ignore_errors=True)	# no .ppm left
    t = open('%s/logs/f20held_%s.log' % (R, g), errors='replace').read()
    errs = [l for l in t.splitlines() if re.search(r'VM execution aborted|Script error|exception', l) and 'voxeldef' not in l]
    sel = re.findall(r'(?i)ReadyWeapon\W+(\w+)', t)
    print('%-24s frames %d support %s %s %s' % (g, len(fr), 'row %d' % ROW[g] if g in ROW else 'free', os.path.basename(png) or 'NO FRAME', errs[:1]), flush=True)
