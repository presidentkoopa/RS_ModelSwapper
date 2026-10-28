"""TEST ONLY (2.0 int r2, owner job 3): hand reload of the IncendiaryLauncher, NukeLauncher and Minigun with NO backpack.
Real-play order: the gun first, then (3 tics later, as a later pickup) its reserve ammo through the normal pickup cap;
counts (reserve item, magazine) printed before the reload, and after. rl3.py <pk3> [Gun,...]"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, re, subprocess, sys
R = (_DP.WORK + '/int20_rig')
D = _DP.RIG
os.environ.update(B22_BUILD=R, B22_RIG=R + '/bin', B22_IWAD=(_DP.GAMEDATA + '/doom2.wad'))
sys.path.insert(0, D)
import rig
rig.OUT = R + '/logs'
import mags
pk3 = sys.argv[1]; only = sys.argv[2].split(',') if len(sys.argv) > 2 else ['IncendiaryLauncher', 'NukeLauncher', 'Minigun']
g = mags.tables()
for i in sorted(g):
    c = mags.CLS[i]
    if c not in only: continue
    res = g[i]['reserve']; cnt = 'netevent int_cnt_%s; wait 2; ' % res
    s = mags.with_pouch(mags.script(i, g[i]))
    s = s.replace('give %s; give %s 400; use %s; wait 80; ' % (c, res, c),
                  'give %s; wait 3; give %s 400; use %s; wait 80; %s' % (c, res, c, cnt), 1)
    s = s.replace('+reload;', cnt + '+reload;', 1).replace('quit', cnt + 'give %s 400; wait 5; ' % res + cnt + 'quit')
    assert s.count('int_cnt') == 4, s
    name = 'r2rl_%s' % c
    subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh'), name, pk3, '300', s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
    ph = re.findall(r'rsr t(\d+) gun %d: (\w+) -> (\w+)' % i, t)
    trail = '>'.join([ph[0][1]] + [b for _, a, b in ph]) if ph else '(never started)'
    cn = re.findall(r'INT CNT t(\d+) (.*?) main state', t)
    er = [l for l in t.splitlines() if re.search(r'VM abort|Script error|exception', l) and 'voxeldef' not in l.lower()]
    print('%-20s trail %s' % (c, trail), flush=True)
    labels = ['after the gun and a 400 pickup', 'before the reload', 'after the reload', 'after another 400 pickup']
    for k, (tt, x) in enumerate(cn): print('    t%s %-32s %s (reserve item = pouch + up to 10 lent from the magazine)' % (tt, labels[k] if k < 4 else '', x.strip()), flush=True)
    for l in re.findall(r'^rsq t\d+ %s: .*' % c, t, re.M)[:2] + re.findall(r'^rsq t\d+ %s: .*' % c, t, re.M)[-2:]: print('    ' + l, flush=True)
    print('    errors:', er[:3] or 'none', '| refused:', re.findall(r'rsr t\d+: reload refused.*', t)[:1] or 'no', flush=True)
