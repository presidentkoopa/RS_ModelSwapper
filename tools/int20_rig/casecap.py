"""TEST ONLY: shotgun casings in flight, eye + side camera. casecap.py <pk3> <tag> <Gun,...>"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import glob, os, re, shutil, subprocess, sys
from PIL import Image, ImageDraw
R = (_DP.WORK + '/int20_rig')
OUT = (_DP.WORK + '/out' + '/int20/casings_r2')
VIEWS = {'eye': '0.25 1.45 0.15 -25 0 0', 'side': '0.85 1.30 -0.50 0 90 0'}	# the support lane's rigsheet cameras
ZOOM = {'eye': (280, 20), 'side': (200, 40)}	# 160 px boxes round the port (480 px frames)
ZOOMG = {('SSG', 'side'): (40, 250), ('Revolver', 'side'): (40, 250), ('SSG', 'eye'): (60, 250), ('Revolver', 'eye'): (60, 250)}
RH = '0.2500 1.3000 -0.3000 30 0 0'
SUP = {'AssaultShotgun': '0.1520 1.2480 -0.7460 30.0 0.0 0.0', 'Shot_Gun': '0.1640 1.2770 -0.7310 30.0 0.0 0.0',
       'SSG': '0.1810 1.2430 -0.4780 30.0 0.0 0.0', 'Revolver': '0.1860 1.2200 -0.3430 30.0 0.0 0.0', 'Rifle': '0.2170 1.3800 -0.6360 30.0 0.0 0.0'}	# support192 s192.ht_row('SupportPoint') -> rig.lpose
ACT = {'AssaultShotgun': '+attack; wait 4; -attack; wait 40; ', 'Rifle': '+attack; wait 4; -attack; wait 40; ',
       'Shot_Gun': 'qz_rtrigger 1; wait 4; qz_rtrigger 0; wait 20; qz_rtrigger 1; wait 4; qz_rtrigger 0; wait 40; ',	# 2nd pull: the set's own pump throws the hull
       'SSG': 'qz_rtrigger 1; wait 4; qz_rtrigger 0; wait 30; +reload; wait 4; -reload; wait 40; ',	# the breech opens: the hulls tip out
       'Revolver': 'qz_rtrigger 1; wait 4; qz_rtrigger 0; wait 30; +reload; wait 4; -reload; wait 40; '}
pk3, tag, guns = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
os.makedirs(OUT, exist_ok=True)
for g in guns:
    for view, hmd in VIEWS.items():
        d = '%s/cdump_%s_%s_%s' % (R, tag, g, view); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        s = ('wait 100; god; notarget; rsq_hands 1; rsq_extra_weapons 1; rsq_ballistics 2; rsr_reload 1; screenblocks 12; crosshair 0; qz_rhand "%s"; give ammo; give %s; wait 2; use %s; wait 150; '
             'qz_lhand "%s"; wait 10; qz_lgrip 1; wait 30; %s quit' % (RH, g, g, SUP[g], ACT[g]))
        if os.environ.get('NOGRIP'): s = s.replace('qz_lgrip 1;', '')
        if g == 'Shot_Gun':	# the set's hand pump throws the hull: fire, then the off hand pumps (pump.py with the live table, as rsweep.py)
            sys.path.insert(0, _DP.RIG); import handrot as hr
            GRAB = (44.203, 8.748, -2.605); PULL = (-0.996, -0.067, -0.061); PALM = (-1.5, 2.0, -4.5)
            pp = lambda f: hr.place(PALM, (1, 0, 0), tuple(GRAB[k] + PULL[k] * 6.4 * f for k in range(3)), (1, 0, 0))[0]
            s = ('wait 100; god; notarget; rsq_hands 1; rsq_extra_weapons 1; rsq_ballistics 2; rsr_reload 1; rsr_grab_with 0; screenblocks 12; crosshair 0; qz_rhand "%s"; '
                 'give Shot_Gun; give AmmoShell 40; wait 2; use Shot_Gun; wait 150; qz_lhand "%s"; wait 10; +attack; wait 3; -attack; wait 8; '
                 'qz_lhand "%s"; wait 6; qz_ltrigger 1; wait 8; qz_lhand "%s"; wait 10; qz_lhand "%s"; wait 10; qz_ltrigger 0; wait 40; quit' % (RH, pp(0), pp(0), pp(1.0), pp(0)))
        name = 'cc_%s_%s_%s' % (tag, g, view)
        env = dict(os.environ, QZ_RES='480', QZ_DUMP_EVERY='1', QZ_DUMP_DIR=d, QZ_HMD=hmd)
        subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh'), name, pk3, '700', s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
        cs = re.findall(r'INT CASE t(\d+) (\S+) age (\d+) scale (\S+)', t)
        ft = sorted((int(a), int(b)) for a, b in re.findall(r'B22 FRAME (\d+) t (\d+)', t))
        fr = sorted(glob.glob(d + '/*.ppm'))
        off = (int(os.path.basename(fr[-1])[1:6]) - ft[-1][0]) if (fr and ft) else 0	# dumps start before the first RenderOverlay
        def tic(f):
            n = int(os.path.basename(f)[1:6]) - off
            lo = [x for x in ft if x[0] <= n]; hi = [x for x in ft if x[0] >= n]
            if lo and hi and hi[0][0] != lo[-1][0]:
                return lo[-1][1] + (hi[0][1] - lo[-1][1]) * (n - lo[-1][0]) / (hi[0][0] - lo[-1][0])
            return (lo or hi)[-1][1] if (lo or hi) else 0
        print('  dumps', len(fr), 'last FRAME', ft[-1] if ft else None)
        pick = []
        if cs:
            t0 = int(cs[0][0]) - int(cs[0][2])	# spawn tic of the first casing
            win = [f for f in fr if t0 - 1 <= tic(f) <= t0 + int(os.environ.get("WIN", "18"))]
            pick = win[:int(os.environ.get('NPICK', '8'))]
        ims = []
        for f in pick:
            src = Image.open(f).convert('RGB')
            im = src.resize((320, 320)); ImageDraw.Draw(im).text((4, 4), '%s %s t%.0f' % (g, view, tic(f)), fill=(255, 255, 0))
            zx, zy = ZOOMG.get((g, view), ZOOM[view]); z = src.crop((zx, zy, zx + 160, zy + 160)).resize((320, 320), Image.NEAREST); ImageDraw.Draw(z).text((4, 4), 'x3 zoom', fill=(255, 255, 0))
            col = Image.new('RGB', (320, 640)); col.paste(im, (0, 0)); col.paste(z, (0, 320)); ImageDraw.Draw(col).rectangle((zx * 2 // 3, zy * 2 // 3, (zx + 160) * 2 // 3, (zy + 160) * 2 // 3), outline=(0, 255, 255)); ims.append(col)
        if ims:
            strip = Image.new('RGB', (320 * len(ims), 640)); [strip.paste(im, (320 * k, 0)) for k, im in enumerate(ims)]
            strip.save('%s/%s_%s_%s.png' % (OUT, tag, g, view))
        import numpy as np
        reds = []
        for f in fr:
            a = np.asarray(Image.open(f).convert('RGB')).astype(int)
            reds.append(int(((a[..., 0] > 150) & (a[..., 1] < 60) & (a[..., 2] < 60)).sum()))
        if reds:
            print('  red>1000 tics', [round(tic(fr[i])) for i in range(len(fr)) if reds[i] > 1000 and i > 5][:40])
            k = int(np.argmax(reds[5:])) + 5; print('  max red px %d at frame %d tic %.0f' % (reds[k], k, tic(fr[k])))
            if os.environ.get('REDPICK') and reds[k] > 200:
                im = Image.open(fr[k]).convert('RGB'); im.save('%s/%s_%s_%s_maxred.png' % (OUT, tag, g, view))
        shutil.rmtree(d, ignore_errors=True)	# no raw .ppm left
        sc = sorted(set(x[3] for x in cs))
        print('%-15s %-4s casings %d scale %s frames %d %s' % (g, view, len(set((x[0], x[1]) for x in cs if x[2] == '1')), sc, len(ims), '' if ims else 'NO CASING FRAME'), flush=True)
