"""TEST ONLY (never ships): scope-3x rig driver, Depot rig (QZD 17.3), exclusive $RSQ_RIGLOCK, ini restored.
Env: ALTSEQ (console after the eye is placed, e.g. alt-fire presses), TURN deg, TSTEP tics/step, EVERY dump interval, SECS, ROLL, HANDANG, SCOPE_OUT (logs/dumps; .ppm -> conv.py deletes them).
 drive.py <name> <pk3> <Gun> <rhand pitch> <eye off L cm> <eye off U cm> <dump 0/1> [extra console] [res]"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, sys, re, time, fcntl, subprocess, numpy as np
H = os.path.dirname(os.path.abspath(__file__))
os.environ.update(B22_IWAD=(_DP.GAMEDATA + '/doom2.wad'), B22_BD22=(_DP.GAMEDATA + '/brutal22test6.pk3'),
                  B22_VOX=(_DP.GAMEDATA + '/BD_VoxelPack.pk3'), B22_BUILD=os.environ.get('SCOPE_OUT', _DP.WORK + '/scope3x'), B22_NOPROBE='1')
os.makedirs(os.environ['B22_BUILD'] + '/logs', exist_ok=True)
sys.path.insert(0, _DP.RIG)
name, pk3, gun, pit, offL, offU, dump = sys.argv[1:8]
extra = sys.argv[8] if len(sys.argv) > 8 else ''
res = sys.argv[9] if len(sys.argv) > 9 else '960'
os.environ['B22_PK3'] = pk3
import rig, zipfile
TPK = os.environ["B22_BUILD"] + "/scope3x_probe.pk3"
with zipfile.ZipFile(TPK, "w") as z:
    for root, _, fs in os.walk(H + "/tpk"):
        for f in fs: z.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), H + "/tpk"))
WT = sys.argv[10] if len(sys.argv) > 10 else _DP.SET	# the set whose src/zscript/rsq/scope.zs holds the lens table
tx = open(WT + '/src/zscript/rsq/scope.zs').read()
def table(fn, i):
    k = tx.index('static Vector3 %s(int i)' % fn); seg = tx[k:tx.index('return', k)]
    return np.array([float(re.search(r'%s\[\] = \{([^}]*)\}' % a, seg).group(1).split(',')[i]) for a in 'flu'])
ix = {'RailGun': 1, 'Sniper': 2}.get(gun, 2)
L = table('Lens', ix); A = table('Axis', ix); A = A / np.linalg.norm(A)
tgt = L - 8.0 * A
c = tgt + np.array([float(os.environ.get('OFFF', '0')), float(offL), float(offU)])
R = rig.RHAND
import math as _m
rho = _m.radians(float(os.environ.get('ROLL', '0')) * float(os.environ.get('RSIGN', '1')))
sx, sy = -c[1] / 100, c[2] / 100	# stage x (right), y (up) of the eye in an unrolled hand
sx, sy = sx * _m.cos(rho) - sy * _m.sin(rho), sx * _m.sin(rho) + sy * _m.cos(rho)
hmd = '%.4f %.4f %.4f 0 0 0' % (R[0] + sx, R[1] + sy, R[2] - c[0] / 100)
if os.environ.get('HANDANG'):	# the hand basis the probe logged (AttackAngle, AttackPitch, AttackRoll): exact eye placement
    aa, ap, ar = [float(v) for v in os.environ['HANDANG'].split()]
    yaw = _m.radians(aa + 90); pit = _m.radians(ap); rol = _m.radians(ar)
    fwd = np.array([_m.cos(pit) * _m.cos(yaw), _m.cos(pit) * _m.sin(yaw), _m.sin(pit)])
    r0 = np.array([_m.sin(yaw), -_m.cos(yaw), 0]); u0 = np.cross(r0, fwd)
    right = r0 * _m.cos(rol) - u0 * _m.sin(rol); up = np.cross(right, fwd)
    w = (fwd * c[0] - right * c[1] + up * c[2]) / 100	# world (x, y, z), player facing +y
    hmd = '%.4f %.4f %.4f 0 0 0' % (R[0] + w[0], R[1] + w[2], R[2] - w[1])
print('lens', L, 'axis', A.round(4), 'eye target', tgt.round(2), 'hmd', hmd, flush=True)
if dump == '1':
    d = os.environ['B22_BUILD'] + '/dump_' + name
    os.makedirs(d, exist_ok=True)
    os.environ.update(QZ_RES=res, QZ_DUMP_EVERY=os.environ.get('EVERY','8'), QZ_DUMP_DIR=d)
else:
    os.environ['QZ_RES'] = res
import math
hd = np.array([float(v) for v in hmd.split()[:3]]); rh = np.array(R)
def rot(p, th):
    v = p - hd; c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
    return hd + np.array([v[0] * c + v[2] * s_, v[1], -v[0] * s_ + v[2] * c])
TURN = float(os.environ.get('TURN', '0'))
turn = ''
if TURN:
    for k in range(1, 21):
        th = TURN * k / 20; r = rot(rh, th)
        turn += 'qz_hmd "%.4f %.4f %.4f 0 %.2f 0"; qz_rhand "%.4f %.4f %.4f %s %.2f 0"; ' % (tuple(hd) + (th,) + tuple(r) + (pit, th)) + 'wait %s; ' % os.environ.get('TSTEP', '1')
    turn += 'wait 80; '
s = ('wait 100; god; notarget; rsq_hands 1; rsq_extra_weapons 1; screenblocks 12; crosshair 0; show_messages 0; con_notifytime 0; ' + extra +
     'qz_rhand "%.4f %.4f %.4f %s 0 %s"; give ammo; give %s; wait 2; use %s; wait 120; qz_hmd "%s"; wait 330; ' % (R + (pit, os.environ.get('ROLL', '0'), gun, gun, hmd)) + turn + os.environ.get('ALTSEQ', '') + 'wait 900; quit')
time.sleep(4)
with open(_DP.LOCK, 'a') as lf:
    fcntl.flock(lf, fcntl.LOCK_EX)
    try:
        rc, text = rig.run(name, s, int(os.environ.get('SECS', '75')), extra=[TPK])
    finally:
        subprocess.run(['git', '-C', _DP.DEPOT, 'checkout', '-q', 'tools/rig/bin/config/qzdoom.ini'])
open(os.environ['B22_BUILD'] + '/' + name + '.txt', 'w').write(text)
errs = [l for l in re.findall(r'Script error, "([^"]+)"', text) if 'BD_VoxelPack' not in l]
print('rc', rc, 'pack script errors', errs, 'VM abort' if 'VM execution aborted' in text else '')
for l in text.splitlines():
    if l.startswith(('RSQT', 'RSQFPS')) or 'rsq_scope' in l: print(l)
