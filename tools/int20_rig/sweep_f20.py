"""TEST ONLY (2.0 integration lane): select / fire / alt fire for every gun, one held frame each.
sweep.py <pk3> <tag> <ballistics 0|1> [Gun,Gun,...]"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import glob, os, re, shutil, subprocess, sys
from PIL import Image
R = (_DP.WORK + '/int20_rig')
OUTF = (_DP.WORK + '/out' + '/final20')
ALL = ['Melee_Attacks', 'BrutalAxe', 'Chain_saw', 'DSweap', 'BrutalPistol', 'BrutalRevolver', 'Revolver', 'BrutalSMG', 'MP40',
       'Shot_Gun', 'SSG', 'AssaultShotgun', 'Sniper', 'Rifle', 'Minigun', 'MG42', 'Machinegun', 'GrenadeLauncher',
       'IncendiaryLauncher', 'Rocket_Launcher', 'Devastator', 'HellishMissileLauncher', 'Plasma_Gun', 'Railgun', 'BFG10k',
       'BIG_FUCKING_GUN', 'NukeLauncher', 'Unmaker', 'Flamethrower2', 'FlameCannon', 'HandGrenades']
MELEE = {'Melee_Attacks', 'BrutalAxe', 'Chain_saw', 'DSweap'}
SIDE = '0.0 1.68 -0.40 20 -70 0'; FWD = '0.25 1.3 -0.3 30 0 0'
pk3, tag, bal = sys.argv[1], sys.argv[2], sys.argv[3]
guns = sys.argv[4].split(',') if len(sys.argv) > 4 else ALL
def mark(t, n):
    m = re.search(r'INT MARK int_mark_%s t\d+ rounds (\d+) pierce (\d+) dots (\d+) puffs (\d+) sparks (\d+) proj (\d+) dmg (\d+)/\d+ lines (\d+) main (\S+) off (\S+) ammo1 (-?\d+) ammo2 (-?\d+) psp (\d+) alt (\d+)' % n, t)
    if not m: return None
    v = m.groups()
    return dict(rounds=int(v[0]), pierce=int(v[1]), dots=int(v[2]), proj=int(v[5]), dmg=int(v[6]), lines=int(v[7]), main=v[8],
                a1=int(v[10]), a2=int(v[11]), psp=int(v[12]), alt=int(v[13]))
for g in guns:
    d = '%s/dump_%s_%s' % (R, tag, g); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    s = ('wait 100; god; notarget; rsq_extra_weapons 1; rsr_debug 1; %s sv_rsq_player_ballistics %s; qz_rhand "%s"; give ammo; give %s; wait 2; use %s; '
         'wait 150; netevent int_mark_sel; qz_rhand "%s"; wait 10; netevent int_mark_pre; qz_rtrigger 1; wait 8; qz_rtrigger 0; wait 45; netevent int_mark_fire; '
         '+altattack; wait 8; -altattack; wait 70; netevent int_mark_alt; wait 3; quit' % (os.environ.get('EXTRA', ''), bal, SIDE, g, g, FWD))
    if os.environ.get('ALTFIRST'):	# alt fire before the main shot empties a one-round gun
        s = s.replace('netevent int_mark_pre; ', 'netevent int_mark_pre; +altattack; wait 8; -altattack; wait 70; netevent int_mark_alt; ', 1).replace('netevent int_mark_alt; wait 3; quit', 'wait 3; quit')
    if os.environ.get('SELONLY'):	# held frame only (variant check): stop at the select mark
        s = s.split('netevent int_mark_sel;')[0] + 'netevent int_mark_sel; wait 3; quit'
    name = '%s_%s' % (tag, g)
    env = dict(os.environ, QZ_RES='480', QZ_DUMP_EVERY='20', QZ_DUMP_DIR=d)
    subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh'), name, pk3, '300', s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
    fr = sorted(glob.glob(d + '/*.ppm'))
    png = ''
    ft = {int(a): int(b) for a, b in re.findall(r'B22 FRAME (\d+) t (\d+)', t)}
    ms = re.search(r'INT MARK int_mark_sel t(\d+)', t)
    if fr and ms:	# the dumped frame whose tic is closest before the select mark (gun held, not yet fired)
        want = int(ms.group(1)) - 4
        def tic(f):
            n = int(os.path.basename(f)[1:6]); k = min(ft, key=lambda a: abs(a - n)) if ft else n
            return ft.get(k, n) + (n - k)
        fr = sorted(fr, key=lambda f: abs(tic(f) - want))
        os.makedirs(OUTF, exist_ok=True); png = '%s/%s_%s.png' % (OUTF, tag, g)
        Image.open(fr[0]).save(png)
    shutil.rmtree(d, ignore_errors=True)	# owner's rule: no raw .ppm left behind
    t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
    errs = [l for l in t.splitlines() if re.search(r'VM abort|Script error|exception', l) and 'voxeldef' not in l]
    sel, pre, fire, alt = mark(t, 'sel'), mark(t, 'pre'), mark(t, 'fire'), mark(t, 'alt')
    why = []
    okS = sel and sel['main'].lower() == g.lower()
    if not okS: why.append('selected %s' % (sel and sel['main']))
    used = lambda a, b: (b['a1'] < a['a1']) or (b['a2'] < a['a2'])
    okF = bool(fire and pre and (used(pre, fire) or fire['proj'] or fire['dots'] or fire['rounds'] or fire['dmg'] or (g in MELEE and fire['psp'] > 2)))
    if not okF: why.append('no shot seen')
    if alt and alt['alt'] == 0: altv = 'n/a (no AltFire state)'; okA = True
    else:
        okA = bool(alt and (used(fire, alt) or alt['proj'] or alt['dots'] or alt['rounds'] or alt['psp'] > 2))
        altv = 'yes' if okA else 'nothing seen'
        if not okA: why.append('alt: nothing seen')
    if errs: why.append('ERR ' + errs[0][:90])
    ok = okS and okF and okA and not errs
    dif = re.search(r'INT DIFF int_mark_alt t\d+ (.*)', t); dif = dif.group(1)[:150] if dif else ''
    if alt and alt['alt'] and dif.strip(): okA = True; altv = 'tokens: ' + dif; why = [w for w in why if not w.startswith('alt')]; ok = okS and okF and not errs
    fd = fire and 'ammo %d/%d->%d/%d proj %d dots %d rounds %d pierce %d dmg %d' % (pre['a1'], pre['a2'], fire['a1'], fire['a2'], fire['proj'], fire['dots'], fire['rounds'], fire['pierce'], fire['dmg'])
    if os.environ.get('SELONLY'):
        print('%-28s %s | held as %s | %s | %s' % (g, 'HELD' if okS and not errs else 'FAIL', sel and sel['main'], '; '.join(w for w in why if w.startswith('selected') or w.startswith('ERR')), os.path.basename(png) or 'NO FRAME'), flush=True); continue
    print('%-24s %s | fire: %s | alt: %s | %s | %s' % (g, 'PASS' if ok else 'FAIL', fd, altv, '; '.join(why), os.path.basename(png) or 'NO FRAME'), flush=True)
