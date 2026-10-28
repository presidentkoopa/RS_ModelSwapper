"""TEST ONLY (rig, never ships): 2.0.1, the Moonlight on BD22's pistol ammo (Clip1, 3 a shot), owner 2026-10-28 06:46.

python3 rig_moonpistol.py <pk3> [jobs]   jobs: fire,hand,hand9,feed9,stock,dual,gone,start,hud (default all)
Every run goes through the 2.0 lane's run.sh (doom2 -> brutal22test6 -> BD_VoxelPack -> pack, `flock -o -x
$RSQ_RIGLOCK`, the fresh default ini ini.f20 copied in before each run). Counts come from the int20 dump
probe (`netevent int_cnt_<item>` -> `INT CNT t<n> <item>=<count>`). The hand reload drives the Depot's break-open
geometry the way tools/int20_rig/rsweep.py does (the B22 BREAK / B22 CH lines of a first, open-only run).
"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '../../../../tools'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, re, subprocess, sys, glob
S = _DP.WORK
R = S + '/int20_rig'
D = _DP.RIG
sys.path.insert(0, D)
import handrot as h
import numpy as np
os.environ['INT20_INI'] = R + '/ini.f20'
pk3 = sys.argv[1]
JOBS = sys.argv[2].split(',') if len(sys.argv) > 2 else ['fire', 'hand', 'hand9', 'feed9', 'stock', 'dual', 'gone', 'start', 'hud']
PRE = 'wait 120; god; notarget; rsq_extra_weapons 1; rsr_debug 1; '
CNT = 'netevent int_cnt_Clip1; netevent int_cnt_BrutalRevolverCylinder; netevent int_cnt_BrutalRevolverCylinderOff; wait 2; '


def run(name, s, secs=300, env=None):
    e = dict(os.environ); e.update(env or {})
    subprocess.run([R + '/run.sh', name, pk3, str(secs), s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=e)
    return open('%s/logs/%s.log' % (R, name), errors='replace').read()


def errs(t):
    return [l for l in t.splitlines() if re.search(r'VM execution aborted|VM abort|Script error|exception', l, re.I)
            and 'voxeldef' not in l.lower() and 'BD_VoxelPack' not in l]


def show(tag, t, pat):
    print('=== %s' % tag)
    for l in t.splitlines():
        if re.search(pat, l):
            print('   ', l.strip()[:200])
    print('    pack script errors:', errs(t)[:5] or 'none', flush=True)


SHOW = r'MP |INT CNT t\d+ (Clip1|BrutalRevolverCylinder\w*)=|RSQ moon|^rsb t\d+ gun \d+: \w+ -> \w+|RSQ ontop|[Uu]nknown|RevolverRounds'
FAR = '-0.25 1.3 -0.3 30 0 0'; RH = '0.25 1.3 -0.3 %s %s %s'
FIRE1 = 'qz_rtrigger 1; wait 3; qz_rtrigger 0; wait 12; '


def setup(clip, cyl, feed=0, real=1):
    return (PRE + 'rsr_reload %d; rsb_revolver_feed %d; give BrutalRevolver; take Clip1 999; give Clip1 %d; take BrutalRevolverCylinder 9; '
            'give BrutalRevolverCylinder %d; use BrutalRevolver; wait 90; ' % (real, feed, clip, cyl))


if 'fire' in JOBS:
    # six pulls only: a seventh on an empty cylinder goes on to the reload (NoAmmo), which is the reload jobs' business
    s = setup(60, 6) + 'echo MP BEFORE_SHOT; ' + CNT + FIRE1 + 'echo MP AFTER_ONE_SHOT; ' + CNT + FIRE1 * 5 + 'echo MP AFTER_SIX_SHOTS; ' + CNT + 'quit'
    show('fire', run('mp_fire', s), SHOW)


def hand(tag, clip, feed):
    # the open-only run gives the geometry; the load run carries the round (speedloader or one round per chamber)
    def script(load):
        return (setup(clip, 0, feed) + 'echo MP BEFORE_HAND_RELOAD; ' + CNT + '+reload; wait 4; -reload; wait 30; %s qz_lhand "%s"; wait 10; '
                'qz_rhand "%s"; wait 4; qz_rhand "%s"; wait 40; echo MP AFTER_HAND_RELOAD; %s quit' % (load, FAR, RH % (70, 0, 0), RH % (30, 0, 0), CNT))
    t = run('mp_open_' + tag, script(''))
    m = re.search(r'B22 BREAK gun (\d+) nch (\d+) theta \S+ hb (\S+) (\S+) (\S+) ht (\S+) (\S+) (\S+)', t)
    if not m:
        show(tag + ' NEVER OPENED', t, SHOW); return
    hb = np.array([float(x) for x in m.group(3, 4, 5)]); ht = np.array([float(x) for x in m.group(6, 7, 8)])
    ch = [(np.array([float(x) for x in a[0:3]]), np.array([float(x) for x in a[3:6]]), float(a[6]))
          for a in re.findall(r'B22 CH \d+ tip (\S+) (\S+) (\S+) bore (\S+) (\S+) (\S+) depth (\S+)', t)]
    load = ''
    for tk, bk, dep in ch:
        a = ht - hb
        p1 = h.place(ht, a, tk - bk * (dep + 1.0), bk)[0]; p2 = h.place(ht, a, tk - bk * (dep * 0.5), bk)[0]; p3 = h.place(ht, a, tk, bk)[0]
        load += ('qz_lhand "%s"; wait 10; qz_ltrigger 1; wait 10; qz_lhand "%s"; wait 12; qz_lhand "%s"; wait 10; '
                 'qz_lhand "%s"; wait 15; qz_ltrigger 0; wait 10; ' % (FAR, p1, p2, p3))
    print('--- %s: gun %s, %d chamber target(s) driven' % (tag, m.group(1), len(ch)))
    show(tag, run('mp_' + tag, script(load), 900), SHOW)


if 'hand' in JOBS:
    hand('hand', 60, 0)		# speedloader, 60 in reserve: 18 move
if 'hand9' in JOBS:
    hand('hand9', 9, 0)		# speedloader, only 9: 3 shots
if 'feed9' in JOBS:
    hand('feed9', 9, 1)		# a round at a time, only 9: 3 chambers take a round, then the hand gets none

if 'stock' in JOBS:
    s = setup(60, 0, 0, 0) + 'echo MP BEFORE_STOCK_RELOAD; ' + CNT + '+reload; wait 4; -reload; wait 80; echo MP AFTER_STOCK_RELOAD; ' + CNT + \
        'take Clip1 999; give Clip1 10; take BrutalRevolverCylinder 9; wait 5; echo MP BEFORE_STOCK_RELOAD_10; ' + CNT + \
        '+reload; wait 4; -reload; wait 80; echo MP AFTER_STOCK_RELOAD_10; ' + CNT + 'quit'
    show('stock', run('mp_stock', s), SHOW)

if 'dual' in JOBS:
    R2, L2 = '0.22 1.3 -0.35 %d 0 0', '-0.22 1.3 -0.35 %d 0 0'
    s = (PRE + 'rsr_reload 1; qz_hmd "0 1.6 0 -20 0 0"; qz_rhand "%s"; qz_lhand "%s"; give BrutalRevolver; use BrutalRevolver; wait 60; '
         'summon BrutalRevolver; wait 3; qz_lstick "0 1"; wait 15; qz_lstick "0 0"; wait 5; give StartDualWield; wait 80; '
         'take Clip1 999; give Clip1 60; take BrutalRevolverCylinder 9; give BrutalRevolverCylinder 6; take BrutalRevolverCylinderOff 9; '
         'give BrutalRevolverCylinderOff 6; wait 5; echo MP DUAL_HELD; printinv; ' + CNT +
         'qz_ltrigger 1; wait 3; qz_ltrigger 0; wait 15; ' * 6 + 'echo MP OFF_EMPTY; ' + CNT +
         'qz_lhand "%s"; wait 8; qz_lhand "%s"; wait 70; echo MP AFTER_FLICK_OFF; ' + CNT +
         'take BrutalRevolverCylinder 9; wait 3; qz_rhand "%s"; wait 8; qz_rhand "%s"; wait 90; echo MP AFTER_FLICK_MAIN; ' + CNT + 'quit') \
        % (R2 % 30, L2 % 30, L2 % -70, L2 % 30, R2 % -70, R2 % 30)
    show('dual', run('mp_dual', s, 300), SHOW + r'|RSQ_Off_BrutalRevolver|BrutalRevolver ')

if 'gone' in JOBS:
    s = (PRE + 'echo MP SUMMON; summon RevolverRounds; wait 3; echo MP GIVE; give RevolverRounds 5; wait 3; rsq_moonlight_pistol 1; '
         'map map01; wait 40; echo MP MAP01; netevent rsq_moon_count; wait 3; map map07; wait 40; echo MP MAP07; netevent rsq_moon_count; wait 3; '
         'rsq_moonlight_pistol 0; quit')
    show('gone', run('mp_gone', s, 300), SHOW + r'|^MP ')

if 'start' in JOBS:
    s = PRE + 'playerclass "$TAGBD_CLASS_PISTOL"; '
    for a, b in ((0, 0), (1, 0), (1, 1)):
        s += 'rsq_moonlight_pistol %d; rsq_moonlight_two %d; map map01; wait 120; echo MP START pistol %d two %d; %s' % (a, b, a, b, CNT)
    s += 'rsq_moonlight_pistol 0; rsq_moonlight_two 0; quit'
    show('start', run('mp_start', s, 300), SHOW)

if 'hud' in JOBS:
    fr = S + '/mp_hud'
    for f in glob.glob(fr + '/*'):
        os.remove(f)
    os.makedirs(fr, exist_ok=True)
    s = (PRE.replace('god;', 'god; screenblocks 10;') + 'rsr_reload 0; give BrutalRevolver; take Clip1 999; give Clip1 57; take BrutalRevolverCylinder 9; '
         'give BrutalRevolverCylinder 6; use BrutalRevolver; wait 90; ' + FIRE1 * 2 + 'rsq_hud_ammo 0; wait 40; echo MP HUD; netevent rsq_ontop; ' + CNT + 'wait 30; quit')
    show('hud', run('mp_hud', s, 300, {'QZ_RES': '480', 'QZ_DUMP_EVERY': '10', 'QZ_DUMP_DIR': fr}), SHOW)
    print('    frames:', len(glob.glob(fr + '/*')), fr)
