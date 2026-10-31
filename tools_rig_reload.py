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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--donor', required=True)
    ap.add_argument('--weapon', required=True, help='the mod weapon class to hold (e.g. RwAssaultRifle)')
    ap.add_argument('--extra', nargs='*', default=[])
    ap.add_argument('--tag', default='reload')
    ap.add_argument('--no-build', action='store_true')
    ap.add_argument('--hmd', default='0 1.6 0 -45 -25 0', help='head pose for the frames (pitch down, yaw right: looks at the gun at the rig rest pose)')
    a = ap.parse_args()
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
            '-nomonsters', '-nosound', '+set', 'rs_foreignmodels_dump', 'true', '+set', 'rs_fm_picks', '"%s"' % picks,
            '+logfile', os.path.join(d, 'log.txt'), '+' + s]
    env = dict(os.environ, QZ_RES='320', QZ_DUMP_EVERY='12', QZ_DUMP_DIR=d)
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
