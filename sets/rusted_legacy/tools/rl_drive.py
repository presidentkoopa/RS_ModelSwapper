#!/usr/bin/env python3
"""TEST ONLY: drive every Rusted Legacy hand reload in the QuestZDoom 17.3 rig (tools/rig/bin/qz).

The rows are read back from the generated src/zscript/rsrl/rsrl_table.zs, so nothing is typed in.
Rig frame facts this uses (checked by a calibration run, 2026-11-02, rsrl_debug 2):
  - tools/rig/rig.py lpose(F, L, U, pitch=30): the off controller at gun-frame cm (F, L, U), oriented
    like the gun controller
  - a point c held in the off hand lands at controller + (c.F, -c.L, c.U): the engine mirrors the left hand
  - raising lpose pitch by t turns that offset nose-up: F' = F cos t - U sin t, U' = F sin t + U cos t
For an insert the off hand is pitched so the piece lies along the mouth axis (best |cos| over -90..90),
then walked in along the approach axis: outside the mouth, half way, home, 0.3 past. For a stroke the
palm goes to the part and moves along its axis in 4 steps (and back, for the pump).

  python3 sets/rusted_legacy/tools/rl_drive.py [gun ...]      (needs work/rl/rsrl.pk3 built from src/)
Env: RL_IWAD (default /home/claude/gamedata/freedoom2.wad), RL_PK3, RL_DUMP=<dir> to dump frames.
"""
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.dirname(HERE)
DEPOT = os.path.dirname(os.path.dirname(SET))
RIGDIR = os.path.join(DEPOT, 'tools', 'rig')
sys.path.insert(0, RIGDIR)
import rig  # noqa: E402

IWAD = os.environ.get('RL_IWAD', '/home/claude/gamedata/freedoom2.wad')
PK3 = os.environ.get('RL_PK3', os.path.join(DEPOT, 'work', 'rl', 'rsrl.pk3'))
OUT = os.path.join(DEPOT, 'work', 'rl', 'logs')

CLS = {'pistol': 'RLPistol', 'shotgun': 'RLShotgun', 'ssg': 'RLSuperShotgun', 'chaingun': 'RLChaingun',
       'plasma': 'RLPlasmaRifle', 'rocket': 'RLRocketLauncher', 'hellshotgun': 'HellShotgun',
       'incinerator': 'RLIncinerator', 'bfg': 'RLBFG9000', 'heatwave': 'RLHeatwave'}
# how to spend some of the loaded ammo so a reload is allowed
FIRE = {'chaingun': 25, 'plasma': 25, 'incinerator': 40, 'heatwave': 25, 'bfg': 60, 'rocket': 6}
AWAY = rig.lpose(-25, 30, -30)
NEG = bool(os.environ.get('RL_NEG'))	# RL_NEG=1: every motion done the wrong way; no gate may pass


def vec(s):
    return tuple(float(x) for x in s.strip('() ').split(','))


def rows():
    t = open(os.path.join(SET, 'src/zscript/rsrl/rsrl_table.zs')).read()
    palm = vec(re.search(r'static Vector3 Palm\(\) \{ return (\([^)]*\))', t).group(1))
    out = []
    for m in re.finditer(r'case (\d+):\t// (\S+) gate (\d+)[^\n]*\n(.*?)break;', t, re.S):
        r = dict(id=int(m.group(1)), gun=m.group(2), gate=int(m.group(3)))
        for k, val in re.findall(r'r\.(\w+) = ([^;]+);', m.group(4)):
            r[k] = vec(val) if val.startswith('(') else (val.strip('"') if val.startswith('"') else float(val))
        out.append(r)
    return palm, out


def held(c, t):
    """a point held in the off hand -> gun-frame offset from the off controller, pitched t degrees"""
    F, L, U = c[0], -c[1], c[2]
    cs, sn = math.cos(math.radians(t)), math.sin(math.radians(t))
    return (F * cs - U * sn, L, F * sn + U * cs)


def pose_for(target, c, t):
    o = held(c, t)
    return rig.lpose(target[0] - o[0], target[1] - o[1], target[2] - o[2], pitch=30.0 + t)


def best_pitch(inaxis, mouth):
    best = (-1, 0, 0)
    for t in range(-90, 91):
        a = held(inaxis, t)
        best = max(best, (round(abs(sum(a[i] * mouth[i] for i in range(3))), 3), -abs(t), t))
    return best[2], math.degrees(math.acos(min(1, best[0])))


def gate_script(r, palm):
    s, note = [], ''
    if r['kind'] == 0:
        t, left = best_pitch(r['inAxis'], r['seatAxis'])
        if NEG:		# the wrong way: the piece turned 60 degrees off its mouth axis
            t += 60
        note = 'pitch %+d (piece %.0f deg off the mouth axis after it)' % (t, left)
        for a in (r['len'] + 3, r['len'] * 0.5, 0.0, -0.3):
            p = tuple(r['seat'][i] - r['axis'][i] * a for i in range(3))
            s.append('qz_lhand "%s"; wait 8;' % pose_for(p, r['inHand'], t))
    else:
        g, d, need = r['grab'], r['dir'], r['need']
        if NEG:		# the wrong way: the part pushed against its travel
            d = tuple(-x for x in d)
        path = [k / 4.0 * (need + 0.6) for k in range(5)]
        if r['ret']:
            path += [path[-1] * (1 - k / 4.0) for k in range(1, 5)]
        for x in path:
            p = tuple(g[i] + d[i] * x for i in range(3))
            s.append('qz_lhand "%s"; wait 6;' % pose_for(p, palm, 0))
    s.append('qz_lhand "%s"; wait 45;' % AWAY)
    return ' '.join(s), note


def script(gun, rs, palm):
    c = CLS[gun]
    n = FIRE.get(gun, 0)
    fire = ('+attack; wait %d; -attack; wait 80;' % n) if n else '+attack; wait 3; -attack; wait 12; +attack; wait 3; -attack; wait 12;'
    s = ('wait 60; god; give all; rl_ammograb 0; rl_imreload 1; rsrl_handreload 1; rsrl_debug %s; wait 40; use %s; wait 150; %s '
         'qz_lhand "%s"; +reload; wait 4; -reload; wait 40; +reload; wait 4; -reload; wait 30; ' % (os.environ.get('RL_DEBUG', '1'), c, fire, AWAY))
    if os.environ.get('RL_HMD'):
        s += 'qz_hmd "%s"; wait 10; ' % os.environ['RL_HMD']
    notes = []
    for r in rs:
        g, note = gate_script(r, palm)
        s += 'echo RSRLTEST gate %d; ' % r['gate'] + g + ' '
        notes.append((r['gate'], note))
    return s + 'echo RSRLTEST end; wait 20; quit', notes


def run(gun, rs, palm):
    os.makedirs(OUT, exist_ok=True)
    log = os.path.join(OUT, '%s.log' % gun)
    if os.path.exists(log):
        os.remove(log)
    scr, notes = script(gun, rs, palm)
    ini = os.path.join(RIGDIR, 'bin', 'config', 'qzdoom.ini')
    keep = open(ini, 'rb').read()
    env = dict(os.environ, QZ_RES=os.environ.get('QZ_RES', '200'), EGL_PLATFORM='surfaceless', LIBGL_ALWAYS_SOFTWARE='1')
    if os.environ.get('RL_DUMP'):
        d = os.path.join(os.environ['RL_DUMP'], gun)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        env.update(QZ_DUMP_DIR=d, QZ_DUMP_EVERY=os.environ.get('RL_DUMP_EVERY', '4'))
    try:
        subprocess.run(['timeout', '300', os.path.join(RIGDIR, 'bin', 'qz'), '-iwad', IWAD, '-file', os.path.abspath(PK3),
                        '-nosound', '-warp', '1', '-skill', '3', '+logfile', log, '+' + scr],
                       cwd=os.path.join(RIGDIR, 'bin'), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        open(ini, 'wb').write(keep)		# the rig writes into the tracked ini
    t = open(log, errors='replace').read()
    errs = [l for l in t.splitlines() if re.search(r'VM abort|Script error|exception|error', l, re.I)
            and 'GL_' not in l]
    ev = [l for l in t.splitlines() if l.startswith('RSRL') or 'RSRLTEST' in l]
    done = [r['gate'] for r in rs if re.search(r'RSRL %s %d: (SEATED|DONE)' % (gun, r['gate']), t)]
    if os.environ.get('RL_DUMP'):
        sheet(gun, scr, d)
    return dict(gun=gun, gates=[r['gate'] for r in rs], done=done, errs=errs[:5], events=ev, notes=notes)


def sheet(gun, scr, d):
    """frames from the first gate to the end, 24 evenly spaced, into work/rl/frames/<gun>.png (frame
    numbers are mapped to tics by the script's total wait, so the start is approximate)"""
    from PIL import Image, ImageDraw
    fs = sorted(f for f in os.listdir(d) if f.endswith('.ppm'))
    if not fs:
        return
    waits = [int(x) for x in re.findall(r'wait (\d+)', scr)]
    pre = [int(x) for x in re.findall(r'wait (\d+)', scr.split('echo RSRLTEST gate')[0])]
    k0 = int(len(fs) * sum(pre) / max(1, sum(waits)))
    sel = fs[k0:]
    sel = [sel[int(i * (len(sel) - 1) / 23)] for i in range(24)] if len(sel) > 24 else sel
    w, h = Image.open(os.path.join(d, fs[0])).size
    S = Image.new('RGB', (w * 6, h * ((len(sel) + 5) // 6)))
    for i, f in enumerate(sel):
        im = Image.open(os.path.join(d, f)).convert('RGB')
        ImageDraw.Draw(im).text((4, 4), '%s %s' % (gun, f[:-4]), fill=(255, 255, 0))
        S.paste(im, ((i % 6) * w, (i // 6) * h))
    os.makedirs(os.path.join(DEPOT, 'work', 'rl', 'frames'), exist_ok=True)
    S.save(os.path.join(DEPOT, 'work', 'rl', 'frames', '%s.png' % gun))


def main():
    palm, allrows = rows()
    guns = sys.argv[1:] or list(CLS)
    res = []
    for gun in guns:
        rs = [r for r in allrows if r['gun'] == gun]
        r = run(gun, rs, palm)
        res.append(r)
        print('%-11s gates %s done %s errors %d' % (gun, r['gates'], r['done'], len(r['errs'])))
        for g, n in r['notes']:
            if n:
                print('   gate %d: %s' % (g, n))
        for e in r['events']:
            print('   ' + e)
        for e in r['errs']:
            print('   ERR ' + e)
    if NEG:
        ok = all(not r['done'] and not r['errs'] for r in res)
        print('WRONG WAY: NO GATE PASSED, NO ERRORS' if ok else 'WRONG WAY: SOME GATE PASSED')
        return
    ok = all(r['done'] == r['gates'] and not r['errs'] for r in res)
    print('ALL GATES DONE, NO ERRORS' if ok else 'NOT ALL DONE')


if __name__ == '__main__':
    main()
