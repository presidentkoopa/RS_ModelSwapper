"""TEST ONLY (2.0 int r2, owner job 4): PuristRifle held with the off hand on the M203 (eye + side), then secondary fire.
puristcap.py <pk3> <tag> [Gun,...]   (default PuristRifle,Rifle: the Rifle is the reference for the hold and the alt)"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import glob, os, re, shutil, subprocess, sys
from PIL import Image, ImageDraw
R = (_DP.WORK + '/int20_rig')
OUT = (_DP.WORK + '/out' + '/int20/purist_r2')
VIEWS = {'eye': '0.25 1.45 0.15 -25 0 0', 'side': '0.85 1.30 -0.50 0 90 0'}	# the support lane's rigsheet cameras
RH = '0.2500 1.3000 -0.3000 30 0 0'
SUP = '0.2170 1.3800 -0.6360 30.0 0.0 0.0'	# Rifle SupportPoint (support192 s192.ht_row) -> rig.lpose; PuristRifle uses the Rifle's row (handtable `is`)
pk3, tag = sys.argv[1], sys.argv[2]; guns = sys.argv[3].split(',') if len(sys.argv) > 3 else ['PuristRifle', 'Rifle']
os.makedirs(OUT, exist_ok=True)
def mark(t, n):
    m = re.search(r'INT MARK int_mark_%s t(\d+) rounds (\d+) pierce (\d+) dots (\d+) puffs (\d+) sparks (\d+) proj (\d+) dmg (\d+)/\d+ lines (\d+) main (\S+) off (\S+) ammo1 (-?\d+) ammo2 (-?\d+) psp (\d+) alt (\d+)' % n, t)
    d = re.search(r'INT DIFF int_mark_%s t\d+ (.*)' % n, t)
    return (m.groups() if m else None), (d.group(1).strip() if d else '')
for g in guns:
    row = []
    for view, hmd in VIEWS.items():
        d = '%s/pdump_%s_%s_%s' % (R, tag, g, view); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        s = ('wait 100; god; notarget; rsq_hands 1; rsq_extra_weapons 1; rsr_reload 1; rsr_debug 1; screenblocks 12; crosshair 0; qz_rhand "%s"; give ammo; give %s; wait 2; use %s; wait 150; '
             'qz_lhand "%s"; wait 10; qz_lgrip 1; wait 40; netevent int_mark_held; wait 2; +altattack; wait 8; -altattack; wait 50; netevent int_mark_alt; wait 3; quit' % (RH, g, g, SUP))
        name = 'pu_%s_%s_%s' % (tag, g, view)
        env = dict(os.environ, QZ_RES='480', QZ_DUMP_EVERY='1', QZ_DUMP_DIR=d, QZ_HMD=hmd, QZ_SNDLOG='1')
        subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh'), name, pk3, '400', s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
        ft = sorted((int(a), int(b)) for a, b in re.findall(r'B22 FRAME (\d+) t (\d+)', t))
        fr = sorted(glob.glob(d + '/*.ppm'))
        off = (int(os.path.basename(fr[-1])[1:6]) - ft[-1][0]) if (fr and ft) else 0
        def tic(f):
            n = int(os.path.basename(f)[1:6]) - off
            lo = [x for x in ft if x[0] <= n]
            return lo[-1][1] if lo else -1
        h, _ = mark(t, 'held'); a, dif = mark(t, 'alt')
        if h and fr:
            th = int(h[0]); ta = int(a[0]) if a else th + 60
            held = min(fr, key=lambda f: abs(tic(f) - (th - 2)))
            after = min(fr, key=lambda f: abs(tic(f) - (th + 14)))	# 12 tics into the secondary-fire press
            for f, lab in ((held, 'held'), (after, 'alt +12 tics')):
                im = Image.open(f).convert('RGB').resize((400, 400)); ImageDraw.Draw(im).text((4, 4), '%s %s %s t%d' % (g, view, lab, tic(f)), fill=(255, 255, 0)); row.append(im)
        shutil.rmtree(d, ignore_errors=True)	# no raw .ppm left
        er = [l for l in t.splitlines() if re.search(r'VM abort|Script error|exception', l) and 'voxeldef' not in l.lower()]
        seg = t.split('INT MARK int_mark_held', 1)[-1].split('INT MARK int_mark_alt', 1)[0]
        snd = sorted(set(re.findall(r'QZSND \d+ (\S+)', seg)))
        print('    sounds in the alt window:', snd or 'none', flush=True)
        if a:
            print('%-12s %-4s alt window: proj %s rounds %s dots %s dmg %s ammo1 %s ammo2 %s psp-changes %s | inventory changed: %s | errors %s'
                  % (g, view, a[6], a[1], a[3], a[7], a[11], a[12], a[13], dif or 'nothing', er[:2] or 'none'), flush=True)
        else:
            print(g, view, 'NO MARK', er[:2], flush=True)
    if row:
        sh = Image.new('RGB', (400 * len(row), 400)); [sh.paste(im, (400 * k, 0)) for k, im in enumerate(row)]
        sh.save('%s/%s_%s.png' % (OUT, tag, g))
