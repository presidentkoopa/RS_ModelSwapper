"""TEST ONLY (2.0 int r2): where the melee code's butt point is, against the drawn gun. Static two-hand hold (the support
lane's hold: gun hand 0.25 1.30 -0.30 pitch 30, off hand at the gun's SupportPoint, grip held), no monster, side + eye cameras;
buttprobe.pk3 draws a blue dot at RSVR_Hand.Place(BladeOut(k)) every tic. buttmark.py <pk3> <tag> <Gun,...>"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, re, sys, glob, shutil, subprocess
from PIL import Image, ImageDraw
R = (_DP.WORK + '/int20_rig')
OUT = (_DP.WORK + '/out' + '/int20/butt_r2')
SUP = {'Rifle': '0.2170 1.3800 -0.6360 30.0 0.0 0.0', 'Shot_Gun': '0.1640 1.2770 -0.7310 30.0 0.0 0.0', 'AssaultShotgun': '0.1520 1.2480 -0.7460 30.0 0.0 0.0', 'MG42': '0.2050 1.3930 -0.6260 30.0 0.0 0.0', 'Machinegun': '0.1860 1.3060 -0.7280 30.0 0.0 0.0'}
VIEWS = {'side': '1.10 1.30 -0.45 0 90 0', 'top': '0.25 1.75 -0.40 -80 0 0'}
pk3, tag, guns = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
os.makedirs(OUT, exist_ok=True)
for g in guns:
    row = []
    for v, hmd in VIEWS.items():
        name = 'bm_%s_%s_%s' % (tag, g, v); d = '%s/bmdump_%s' % (R, name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        sup = SUP.get(g, os.environ.get('SUPP', '0.2170 1.3800 -0.6360 30.0 0.0 0.0'))
        s = ('wait 100; god; notarget; rsq_hands 1; rsq_extra_weapons 1; rsq_butt 1; screenblocks 12; crosshair 0; qz_rhand "0.2500 1.3000 -0.3000 30 0 0"; give ammo; give %s; wait 2; use %s; wait 150; '
             'qz_lhand "%s"; wait 10; qz_lgrip 1; wait 60; quit' % (g, g, sup))
        env = dict(os.environ, QZ_RES='480', QZ_DUMP_EVERY='1', QZ_DUMP_DIR=d, QZ_HMD=hmd)
        subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh'), name, pk3, '300', s, R + '/int20dump.pk3', R + '/buttprobe.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
        fr = sorted(glob.glob(d + '/*.ppm'))
        bl = re.findall(r'INT BUTT t(\d+) k (\d+) steady (\d+) butt (\S+ \S+ \S+)', t)
        if fr:
            im = Image.open(fr[-3]).convert('RGB').resize((400, 400)); ImageDraw.Draw(im).text((4, 4), '%s %s %s: blue dot = butt point (steady %s)' % (g, tag, v, bl[-1][2] if bl else '?'), fill=(255, 255, 0)); row.append(im)
        shutil.rmtree(d, ignore_errors=True)
        print(g, v, 'last butt', bl[-1] if bl else None, flush=True)
    if row:
        sh = Image.new('RGB', (400 * len(row), 400)); [sh.paste(im, (400 * k, 0)) for k, im in enumerate(row)]; sh.save('%s/mark_%s_%s.png' % (OUT, tag, g))
