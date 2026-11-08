"""BUILD helper (2.0 int r2, port lane bug): the butt-strike / pistol-whip hit points of the guns moved to the FBX hand
(r9..r12 ports) never moved with them. For each gun: its gun_move (tools/handfit/poses/<Class>.json; MODELDEF numbers after
the move) -> R, t = port_gun.rigid_move from the original placement (Scale -1 1 1, Offset 0 0, ZOffset -5: the same chain
melee.zs Place() assumes), and writes RSVR_MeleeMove.Apply rows (controller F / L / U cm), as melee_r12.py does for melee.
Checks R, t against the json's own R / t where it has them. butt_move.py [--write]"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, sys, json, re, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = _DP.SET
sys.path.insert(0, os.path.join(_DP.TOOLS, 'handfit', 'port')); import port_gun as pg
KIND = [('RIFLEBUTT', 'Rifle'), ('SGBUTT', 'Shot_Gun'), ('SSGBUTT', 'SSG'), ('ASGBUTT', 'AssaultShotgun'), ('MP40BUTT', 'MP40'),
        ('SMGBUTT', 'BrutalSMG'), ('MGBUTT', 'Machinegun'), ('MG42BUTT', 'MG42'), ('PISTOL', 'BrutalPistol'), ('REVOLVER', 'Revolver')]
rows = []
for k, cls in KIND:
    gm = json.load(open(os.path.join(_DP.POSES, '%s.json' % cls)))['gun_move']
    p = gm.get('place') or gm.get('modeldef_place') or [gm[a] for a in ('Offset_x', 'Offset_y', 'ZOffset', 'AngleOffset', 'PitchOffset', 'RollOffset')]
    R, t = pg.rigid_move(dict(scale=[-1, 1, 1], off=[0, 0, -5]), np.asarray(p, float))
    chk = ''
    if 'R' in gm:
        chk = 'json R/t diff %.2e / %.2e' % (np.abs(R - np.array(gm['R'])).max(), np.abs(t - np.array(gm['t'])).max())
    print('%-14s %-15s place %s  t %s  %s' % (cls, k, np.round(p, 3).tolist(), np.round(t, 3).tolist(), chk))
    rows.append('\t\tif (k == RSVR_Hand.%s && pf == 0)\t// %s (gun_move, tools/handfit/poses/%s.json)\n\t\t\treturn (%.6f * p.x + %.6f * p.y + %.6f * p.z + %.4f, %.6f * p.x + %.6f * p.y + %.6f * p.z + %.4f, %.6f * p.x + %.6f * p.y + %.6f * p.z + %.4f);'
                % ((k, cls, cls) + tuple(np.r_[R[0], t[0], R[1], t[1], R[2], t[2]])))
if '--write' in sys.argv:
    f = os.path.join(ROOT, 'src/zscript/rsvr/melee.zs'); tx = open(f, encoding='latin-1').read()
    a = '\tstatic Vector3 Apply(int k, int pf, Vector3 p)\n\t{\n'
    assert tx.count(a) == 1 and 'RSVR_Hand.RIFLEBUTT' not in tx
    tx = tx.replace(a, a + '\t\t// 2.0 int r2: the butt strike / pistol whip guns, moved to the FBX hand by the r9..r12 ports (tools/int20_rig/butt_move.py)\n' + '\n'.join(rows) + '\n')
    open(f, 'w', encoding='latin-1').write(tx); print('written', f)
