"""TEST ONLY (2.0 int r2, owner job 2): the Shotvolver's secondary fire with NO option set by the test. Two inis:
'old' = the lane's pristine ini as an older build saved it (it holds rsa_rev_magnum=false), 'fresh' = that ini with every
rsa_ line removed. Player Ballistics = Bullet so each pellet / slug is a counted round. slugtest.py <pk3>"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, re, subprocess, sys
R = (_DP.WORK + '/int20_rig')
pk3 = sys.argv[1]
pr = open(R + '/ini.pristine').read()
inis = {'old': pr, 'fresh': ''.join(l for l in pr.splitlines(True) if not l.startswith('rsa_'))}
FWD = '0.25 1.3 -0.3 0 0 0'
for k, txt in inis.items():
    ini = '%s/ini.%s' % (R, k); open(ini, 'w').write(txt)
    s = ('wait 100; god; notarget; rsq_extra_weapons 1; sv_rsq_player_ballistics 1; qz_rhand "%s"; give Revolver; give AmmoShell 50; wait 2; use Revolver; wait 150; '
         'netevent int_mark_pre; +altattack; wait 40; -altattack; wait 60; netevent int_mark_alt; wait 2; qz_rtrigger 1; wait 6; qz_rtrigger 0; wait 60; netevent int_mark_fire; wait 3; quit' % FWD)
    name = 'slug_%s' % k
    subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh'), name, pk3, '300', s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=dict(os.environ, INT20_INI=ini))
    t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
    cv = re.findall(r'rsa_rev_\w+=\S+', open(R + '/bin/config/qzdoom.ini', errors='replace').read())
    for m in ('alt', 'fire'):
        x = re.search(r'INT MARK int_mark_%s t\d+ rounds (\d+) pierce \d+ dots (\d+) .*? dmg (\d+)/(\d+) .*? ammo1 (-?\d+) ammo2 (-?\d+)' % m, t)
        print('%-5s ini %-5s: rounds %s dots %s hits %s dmg %s ammo1 %s ammo2 %s' % (k, m, *(x.groups() if x else ['?'] * 6)), flush=True)
    print('      ini after the run:', cv, '| errors:', [l for l in t.splitlines() if re.search(r'VM abort|Script error', l) and 'voxeldef' not in l.lower()][:2] or 'none', flush=True)
