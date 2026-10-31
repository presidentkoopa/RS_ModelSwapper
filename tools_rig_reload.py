#!/usr/bin/env python3
"""tools_rig_reload.py -- drive one hand magazine reload of a ModelSwapper donor on the QuestZDoom rig.

    python3 tools_rig_reload.py --donor MS_BD_Rifle --weapon RwAssaultRifle --extra doomablo.pk3 [--tag t]

The reload geometry is NOT typed in: the slot comes from RSR_Guns.SlotForDonor and the well / axis / mouth /
magazine-in-hand numbers from the same RSR_Guns tables the pack runs (zscript_depot/rsr/rsr_guns.ms.zs).
The off-hand moves are the Depot rig's magazine driver (RSQ_WeaponDepot tools/rig/mags.py: script / at),
reused through its rig.lpose; the gun hand stays at the rig's rest pose, the frame those tables are in.

Sequence (mags.py's): select, fire, press reload, grip the off hand at a pouch, bring the magazine to the
mouth + 3 cm, half way in, seated, release. Pass = the log's reload phases (rsr ... A -> B, rsr_debug) reach
the end of a reload, zero script errors from the pack. A contact sheet of the dumped frames is written too.
"""
import argparse, os, re, subprocess, sys, glob, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get('RSQ_DEPOT', '/home/claude/rsq_weapondepot') + '/tools/rig')
import rig  # noqa: E402  (Depot rig helpers: lpose)
import tools_rig_check as rc  # noqa: E402  (pk3 build, shelf, rig paths)

GUNS = os.path.join(HERE, 'zscript_depot/rsr/rsr_guns.ms.zs')


def slot_for(donor):
    t = open(GUNS).read()
    m = re.search(r'if \(donor == "%s"\)\s+return (\d+);' % re.escape(donor), t)
    return int(m.group(1)) if m else 0


def table(fn, i):
    """case i of `static <type> fn(int i)` in rsr_guns.ms.zs, as a tuple of floats (or one float)"""
    t = open(GUNS).read()
    body = re.search(r'static \w+ %s\(int i\)\s*\{(.*?)\n\t\}' % fn, t, re.S).group(1)
    m = re.search(r'case %d:\s*return \(?([^;]*?)\)?;' % i, body)
    v = [float(x) for x in m.group(1).split(',')]
    return v[0] if len(v) == 1 else tuple(v)


def at(W, A, T, d, mirror=True):
    # mags.py at(): the left hand is the gun hand mirrored in L; a side well also turns the hand 180 about U
    side = abs(A[1]) > 0.5
    T2 = (-T[0], T[1], T[2]) if side else (T[0], -T[1] if mirror else T[1], T[2])
    p = [W[k] + A[k] * d - T2[k] for k in range(3)]
    return rig.lpose(*p, yaw=180.0 if side else 0.0)


PROBE_DIR = os.path.join(HERE, 'tools_kit/probe_rsb')


def probe_pk3():
    import zipfile
    p = '/tmp/claude-0/ms_probe_rsb.pk3'
    with zipfile.ZipFile(p, 'w') as z:
        for f in ('zscript.txt', 'MAPINFO.txt'):
            z.write(os.path.join(PROBE_DIR, f), f)
    return p


def rig_run(a, picks, script, tag, every='12'):
    d = os.path.join(rc.SHOTS, 'rigreload_%s_%s_%s' % (a.tag, tag, a.donor)); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    args = ['./qz', '-iwad', rc.IWAD, '-file'] + [os.path.abspath(x) for x in a.extra] + [rc.PK3, probe_pk3(), '-warp', '1',
            '-nomonsters', '-nosound', '+set', 'rs_foreignmodels_dump', 'true', '+set', 'rsq_hands', '1', '+set', 'rs_fm_picks', '"%s"' % picks, '+' + script]
    env = dict(os.environ, QZ_RES='320', QZ_DUMP_EVERY=every, QZ_DUMP_DIR=d)
    with open(os.path.join(d, 'out.txt'), 'w') as fo:
        try:
            subprocess.run(args, cwd=rc.RIG, env=env, stdout=fo, stderr=subprocess.STDOUT, timeout=400)
        except subprocess.TimeoutExpired:
            pass
    return d, open(os.path.join(d, 'out.txt'), errors='ignore').read()


def run_break(a):
    """Depot brk.py, against ModelSwapper: run 1 opens the action and the probe prints the opened chambers;
    run 2 takes a round to each chamber (handrot.place, as brk.py) and flicks the gun hand to shut it."""
    import numpy as np
    import handrot as h  # Depot tools/rig
    t0 = open(os.path.join(HERE, 'zscript_depot/rsr/rsb_guns.zs')).read()
    m = re.search(r'if \(donor == "%s"\)\s+return (\d+);' % re.escape(a.donor), t0)
    if not m: sys.exit('%s has no break-open slot in RSB_Guns' % a.donor)
    print('donor %s -> break slot %s' % (a.donor, m.group(1)))
    if not a.no_build: print('pk3', rc.build_pk3())
    sh = rc.shelf(); fam, idx = sh[a.donor]; fist = sh['MS_BD_Fist'][1]
    picks = ';%s:%s:%d:%d;rsq_hands:melee:%d:%d;' % (a.weapon, fam, idx, idx, fist, fist)
    pre = ('wait 120; god; qz_hmd "%s"; rsr_reload 1; rsr_debug 1; give ammo; give %s; wait 2; use %s; wait 170; '
           '+attack; wait 3; -attack; wait 40; +reload; wait 4; -reload; wait 40; ' % (a.hmd, a.weapon, a.weapon))
    d1, t1 = rig_run(a, picks, pre + 'quit', 'open', every='40')
    mb = re.search(r'B22 BREAK gun (\d+) nch (\d+) theta \S+ hb (\S+) (\S+) (\S+) ht (\S+) (\S+) (\S+)', t1)
    print('open:', [l for l in t1.splitlines() if re.match(r'rsb t', l)][:6])
    if not mb: sys.exit('the action never reached OPEN (no B22 BREAK line): ' + d1)
    hb = np.array([float(x) for x in mb.group(3, 4, 5)]); ht = np.array([float(x) for x in mb.group(6, 7, 8)])
    ch = [(np.array([float(x) for x in c[0:3]]), np.array([float(x) for x in c[3:6]]), float(c[6]))
          for c in re.findall(r'B22 CH \d+ tip (\S+) (\S+) (\S+) bore (\S+) (\S+) (\S+) depth (\S+)', t1)]
    FAR = '-0.25 1.3 -0.3 30 0 0'; RH = '0.25 1.3 -0.3 %s %s %s'
    load = ''
    for tk, bk, dep in ch:
        ax = ht - hb
        p1 = h.place(ht, ax, tk - bk * (dep + 1.0), bk)[0]
        p2 = h.place(ht, ax, tk - bk * (dep * 0.5), bk)[0]
        p3 = h.place(ht, ax, tk, bk)[0]
        load += ('qz_lhand "%s"; wait 10; qz_ltrigger 1; wait 10; qz_lhand "%s"; wait 12; qz_lhand "%s"; wait 10; '
                 'qz_lhand "%s"; wait 15; qz_ltrigger 0; wait 10; ' % (FAR, p1, p2, p3))
    fl = tuple(float(x) for x in a.flick.split())
    s = pre + load + 'qz_lhand "%s"; wait 10; qz_rhand "%s"; wait 4; qz_rhand "%s"; wait 60; quit' % (FAR, RH % fl, RH % (30, 0, 0))
    d2, t2 = rig_run(a, picks, s, 'load')
    ma = re.search(r'^\s+%s\s+slot\s+-?\d+\s+->\s+\S+\s+(MS_\w+)' % re.escape(a.weapon), t2, re.M)
    errs = sorted(set(l.strip() for l in t2.splitlines() if rc.ERR.search(l) and not rc.ENGINE_NOISE.search(l)))
    print('applied donor:', ma.group(1) if ma else None)
    print('chambers:', len(ch))
    for l in [l for l in t2.splitlines() if re.match(r'rsb t', l)][:14]: print('   ', l[:150])
    print('pack errors:', len(errs)); [print('   ', e[:160]) for e in errs[:5]]
    print('frames in', d2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--donor', required=True)
    ap.add_argument('--weapon', required=True, help='the mod weapon class to hold (e.g. RwAssaultRifle)')
    ap.add_argument('--extra', nargs='*', default=[])
    ap.add_argument('--tag', default='reload')
    ap.add_argument('--no-build', action='store_true')
    ap.add_argument('--kind', default='mag', choices=['mag', 'break'], help='mag = magazine (RSR_Guns); break = break-open / revolver (RSB_Guns, Depot brk.py)')
    ap.add_argument('--flick', default='70 0 0', help='break: gun-hand rotation that flicks the action shut (brk.py default)')
    ap.add_argument('--hmd', default='0 1.6 0 -45 -25 0', help='head pose for the frames (pitch down, yaw right: looks at the gun at the rig rest pose)')
    a = ap.parse_args()
    if a.kind == 'break':
        return run_break(a)
    i = slot_for(a.donor)
    if not i:
        sys.exit('%s has no reload slot in RSR_Guns (no measured magazine reload)' % a.donor)
    W, A, M, T = table('Well', i), table('Axis', i), table('Mouth', i), table('TopInHand', i)
    print('donor %s -> reload slot %d: well %s axis %s mouth %.2f top-in-hand %s' % (a.donor, i, W, A, M, T))
    if not a.no_build:
        print('pk3', rc.build_pk3())
    sh = rc.shelf()
    fam, idx = sh[a.donor]; fist = sh['MS_BD_Fist'][1]
    picks = ';%s:%s:%d:%d;rsq_hands:melee:%d:%d;' % (a.weapon, fam, idx, idx, fist, fist)
    pouch = rig.lpose(0, 40, -30)
    s = ('wait 120; god; qz_hmd "%s"; rsr_reload 1; rsr_grab_with 0; rsr_debug 1; give ammo; give %s; wait 2; use %s; wait 170; '
         '+attack; wait 12; -attack; wait 25; +reload; wait 4; -reload; wait 30; '
         'qz_lhand "%s"; wait 10; qz_ltrigger 1; wait 12; '
         'qz_lhand "%s"; wait 15; qz_lhand "%s"; wait 15; qz_lhand "%s"; wait 25; qz_ltrigger 0; wait 60; quit'
         % (a.hmd, a.weapon, a.weapon, pouch, at(W, A, T, M + 3), at(W, A, T, M * 0.5), at(W, A, T, 0)))
    d = os.path.join(rc.SHOTS, 'rigreload_%s_%s' % (a.tag, a.donor)); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    args = ['./qz', '-iwad', rc.IWAD, '-file'] + [os.path.abspath(x) for x in a.extra] + [rc.PK3, '-warp', '1',
            '-nomonsters', '-nosound', '+set', 'rs_foreignmodels_dump', 'true', '+set', 'rsq_hands', '1', '+set', 'rs_fm_picks', '"%s"' % picks,
            '+logfile', os.path.join(d, 'log.txt'), '+' + s]
    env = dict(os.environ, QZ_RES=os.environ.get('QZ_RES', '320'), QZ_DUMP_EVERY='12', QZ_DUMP_DIR=d)
    with open(os.path.join(d, 'out.txt'), 'w') as fo:
        try:
            subprocess.run(args, cwd=rc.RIG, env=env, stdout=fo, stderr=subprocess.STDOUT, timeout=400)
        except subprocess.TimeoutExpired:
            pass
    t = open(os.path.join(d, 'out.txt'), errors='ignore').read()
    m = re.search(r'^\s+%s\s+slot\s+-?\d+\s+->\s+\S+\s+(MS_\w+)' % re.escape(a.weapon), t, re.M)
    ph = re.findall(r'rsr t\d+ gun %d: (\w+) -> (\w+)' % i, t)
    trail = ([ph[0][0]] + [b for _, b in ph]) if ph else []
    errs = sorted(set(l.strip() for l in t.splitlines() if rc.ERR.search(l) and not rc.ENGINE_NOISE.search(l)))
    join = [l.strip() for l in t.splitlines() if '[MSJOIN]' in l]
    print('applied donor:', m.group(1) if m else None)
    print('MSJOIN:', join[:4])
    print('reload phases:', ' > '.join(trail) or '(none)')
    print('pack errors:', len(errs)); [print('   ', e[:160]) for e in errs[:5]]
    print('frames:', len(glob.glob(d + '/*.ppm')), 'in', d)


if __name__ == '__main__':
    main()
