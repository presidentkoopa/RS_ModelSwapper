"""TEST ONLY (2.0 integration lane): hand reloads with the Depot's drivers (mags.py / pump.py / brk.py geometry),
every run through run.sh (shared lock, pristine ini). rsweep.py <pk3> [mag|pump|brk|all] [only,...]"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, re, subprocess, sys
R = (_DP.WORK + '/int20_rig')
D = _DP.RIG
os.environ.update(B22_BUILD=R, B22_RIG=R + '/bin', B22_IWAD=(_DP.GAMEDATA + '/doom2.wad'))
sys.path.insert(0, D)
import rig, mags, handrot as h
pk3 = sys.argv[1]; what = sys.argv[2] if len(sys.argv) > 2 else 'all'; only = sys.argv[3].split(',') if len(sys.argv) > 3 else None
def run(name, s, secs=300):
    subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh'), name, pk3, str(secs), s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return open('%s/logs/%s.log' % (R, name), errors='replace').read()
def errs(t): return [l for l in t.splitlines() if re.search(r'VM abort|Script error|exception', l) and 'voxeldef' not in l]
def cnt(t, item): return [int(x) for x in re.findall(r'INT CNT t\d+ %s=(-?\d+)' % item, t)]
if what in ('mag', 'all'):
    g = mags.tables()
    for i in sorted(g):
        c = mags.CLS[i]
        if only and c not in only: continue
        s = mags.with_pouch(mags.script(i, g[i]))
        if os.environ.get('BACKPACK'): s = s.replace('give %s;' % c, 'give Backpack; give %s;' % c, 1)
        if os.environ.get('BACKPACK'): c2 = c + '_bp'
        t = run('rl_mag_%s' % (c + ('_bp' if os.environ.get('BACKPACK') else '')), s)
        ph = re.findall(r'rsr t(\d+) gun %d: (\w+) -> (\w+)' % i, t)
        trail = '>'.join([ph[0][1]] + [b for _, a, b in ph]) if ph else ''
        t0 = int(ph[0][0]) if ph else 10**9
        ups = [(int(a), int(b)) for tt, a, b in re.findall(r'B22 W (\d+) mag (-?\d+) -> (-?\d+)', t) if int(tt) >= t0 and int(b) > int(a) >= 0]
        ok = bool(ups) and not errs(t)
        print('%-24s %s | trail %s | mag %s | %s' % (c, 'PASS' if ok else 'FAIL', trail[:110], ups[:1] or 'no refill seen',
              (errs(t) or re.findall(r'rsr t\d+: reload refused.*', t) or [''])[0][:90]), flush=True)
if what in ('pump', 'all') and (not only or 'Shot_Gun' in only):
    src = open(D + '/pump.py').read().split('rig.run(')[0]
    # the live table (probe 'B22 PUMP 1' on this pack), not pump.py's older constants
    src = src.replace('PORT = (19.0, 0.0, -2.8); PUSH = (1.0, 0.0, 0.0)', 'PORT = (23.187, 7.333, -3.842); PUSH = (0.996, 0.067, 0.059)')
    src = src.replace('GRAB = (40.1, 0.0, -2.8); PULL = (-1.0, 0.0, -0.002)', 'GRAB = (44.203, 8.748, -2.605); PULL = (-0.996, -0.067, -0.061)')
    ns = {'__file__': D + '/pump.py'}; exec(compile(src, 'pump.py', 'exec'), ns)
    s = ns['s'].replace('quit', 'netevent int_cnt_ShotgunAmmo; wait 3; quit').replace('+reload; wait 4; -reload; wait 25; ', 'netevent int_cnt_ShotgunAmmo; +reload; wait 4; -reload; wait 25; ', 1)
    t = run('rl_pump_Shot_Gun', s, 600)
    c = cnt(t, 'ShotgunAmmo'); lines = re.findall(r'^rsp t\d+.*', t, re.M)
    ok = len(c) == 2 and c[1] > c[0] and not errs(t)
    print('%-24s %s | tube %s | %s' % ('Shot_Gun (pump)', 'PASS' if ok else 'FAIL', c, '; '.join(l[:60] for l in lines[:4])), flush=True)
if what in ('brk', 'all'):
    FAR = '-0.25 1.3 -0.3 30 0 0'; RH = '0.25 1.3 -0.3 %s %s %s'
    for cl, ammo, mag in [('SSG', 'AmmoShell', 'SSGAmmo'), ('GrenadeLauncher', 'AmmoRocket', 'GLAmmo'),
                          ('Revolver', 'AmmoShell', 'RevolverAmmo'), ('BrutalRevolver', 'RevolverRounds', 'BrutalRevolverCylinder')]:
        if only and cl not in only: continue
        def script(load):
            return ('wait 120; god; rsq_extra_weapons 1; rsr_reload 1; rsr_debug 1; give %s; give %s 100; use %s; wait 90; '
                    'qz_rtrigger 1; wait 3; qz_rtrigger 0; wait 30; qz_rtrigger 1; wait 3; qz_rtrigger 0; wait 40; netevent int_cnt_%s; '
                    '+reload; wait 4; -reload; wait 30; %s qz_lhand "%s"; wait 10; qz_rhand "%s"; wait 4; qz_rhand "%s"; wait 40; netevent int_cnt_%s; wait 3; quit'
                    % (cl, ammo, cl, mag, load, FAR, RH % (70, 0, 0), RH % (30, 0, 0), mag))
        t = run('rl_open_%s' % cl, script(''))
        m = re.search(r'B22 BREAK gun (\d+) nch (\d+) theta \S+ hb (\S+) (\S+) (\S+) ht (\S+) (\S+) (\S+)', t)
        if not m:
            print('%-24s FAIL | never opened (no B22 BREAK) | %s' % (cl, (errs(t) or [''])[0][:90]), flush=True); continue
        import numpy as np
        hb = np.array([float(x) for x in m.group(3, 4, 5)]); ht = np.array([float(x) for x in m.group(6, 7, 8)])
        ch = [(np.array([float(x) for x in a[0:3]]), np.array([float(x) for x in a[3:6]]), float(a[6]))
              for a in re.findall(r'B22 CH \d+ tip (\S+) (\S+) (\S+) bore (\S+) (\S+) (\S+) depth (\S+)', t)]
        load = ''
        for tk, bk, dep in ch:
            a = ht - hb
            p1 = h.place(ht, a, tk - bk * (dep + 1.0), bk)[0]; p2 = h.place(ht, a, tk - bk * (dep * 0.5), bk)[0]; p3 = h.place(ht, a, tk, bk)[0]
            load += ('qz_lhand "%s"; wait 10; qz_ltrigger 1; wait 10; qz_lhand "%s"; wait 12; qz_lhand "%s"; wait 10; '
                     'qz_lhand "%s"; wait 15; qz_ltrigger 0; wait 10; ' % (FAR, p1, p2, p3))
        t = run('rl_brk_%s' % cl, script(load), 900)
        c = cnt(t, mag); rsb = re.findall(r'^rsb t\d+ gun \d+: \w+ -> \w+', t, re.M)
        trail = '>'.join(x.split(': ')[1].split(' -> ')[1] for x in rsb)
        ok = len(c) == 2 and c[1] > c[0] and not errs(t)
        print('%-24s %s | chambers %d | %s %s | trail %s | %s' % (cl, 'PASS' if ok else 'FAIL', len(ch), mag, c, trail[:80], (errs(t) or [''])[0][:80]), flush=True)
