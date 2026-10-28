"""TEST ONLY (2.0 int r2): a butt strike on the rig. Both hands on the gun (off grip held: the engine's steadying), a monster
summoned in front, then the gun hand swung forward over the front hand (the stock leading, pivoting about the front hand).
Logs the butt point every tic (buttprobe.pk3) and every hit. butt.py <pk3> <tag> <Gun,...> [frames 0/1]"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, re, sys, math, glob, shutil, subprocess
from PIL import Image, ImageDraw
R = (_DP.WORK + '/int20_rig')
OUT = (_DP.WORK + '/out' + '/int20/butt_r2')
pk3, tag, guns = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
frames = len(sys.argv) > 4 and sys.argv[4] == '1'
L = (0.217, 1.38, -0.636) if os.environ.get('MODE', 'pitch') == 'pitch' else (0.22, 1.05, -0.60); r = float(os.environ.get('BR', '0.45'))
T0, T1, N = float(os.environ.get('TH0', '30')), float(os.environ.get('TH1', '89')), int(os.environ.get('NST', '1'))
MODE = os.environ.get('MODE', 'pitch')	# pitch: the gun hand stays put and pitches the muzzle down fast, so the stock (behind the hand) swings forward
RHP = (0.25, 1.30, -0.30)
def rh(th):
    if MODE == 'pitch':
        return '%.4f %.4f %.4f %.1f 0 0' % (RHP + (th,))
    t = math.radians(th); return '%.4f %.4f %.4f %.1f 0 0' % (L[0], L[1] + r * math.sin(t), L[2] + r * math.cos(t), min(th, 89.0))
os.makedirs(OUT, exist_ok=True)
for g in guns:
    sw = ''.join('qz_rhand "%s"; wait %s; ' % (rh(T0 + (T1 - T0) * i / N), os.environ.get('SW', '2')) for i in range(1, N + 1))
    s = ('wait 100; god; notarget; rsq_hands 1; rsq_extra_weapons 1; rsq_butt 1; screenblocks 12; crosshair 0; qz_rhand "%s"; give ammo; give %s; wait 2; use %s; wait 150; '
         'qz_lhand "%.4f %.4f %.4f 0 0 0"; wait 10; qz_lgrip 1; wait 20; summon %s; wait 30; give INT20Loud; %s wait 30; quit'
         % (rh(T0), g, g, L[0], L[1], L[2], os.environ.get('MON', 'Cyberdemon'), sw))
    name = 'butt_%s_%s' % (tag, g)
    d = '%s/bdump_%s' % (R, name)
    env = dict(os.environ)
    if frames:
        shutil.rmtree(d, ignore_errors=True); os.makedirs(d); env.update(QZ_RES='480', QZ_DUMP_EVERY='1', QZ_DUMP_DIR=d, QZ_HMD=os.environ.get('HMD', '0.85 1.30 -0.50 0 90 0'))
    subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh'), name, pk3, '300', s, R + '/int20dump.pk3', R + '/buttprobe.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
    er = [l for l in t.splitlines() if re.search(r'VM abort|Script error|exception', l) and 'voxeldef' not in l.lower()]
    loud = t.split('INT BUTT')[0]
    bl = re.findall(r'INT BUTT t(\d+) k (\d+) steady (\d+) butt (\S+) (\S+) (\S+) hand (\S+) (\S+) (\S+)', t)
    hits = re.findall(r'INT HIT .*', t)
    print('%-15s steady %s | butt samples %d | hits %d | errors %s' % (g, sorted(set(x[2] for x in bl)), len(bl), len(hits), er[:2] or 'none'), flush=True)
    for h in hits[:4]: print('    ' + h[:300], flush=True)
    if frames:
        fr = sorted(glob.glob(d + '/*.ppm'))
        ft = sorted((int(a), int(b)) for a, b in re.findall(r'B22 FRAME (\d+) t (\d+)', t))
        off = (int(os.path.basename(fr[-1])[1:6]) - ft[-1][0]) if (fr and ft) else 0
        def tic(f):
            n = int(os.path.basename(f)[1:6]) - off; lo = [x for x in ft if x[0] <= n]
            return lo[-1][1] if lo else -1
        hit = re.search(r'INT HIT t(\d+)', t); th = int(hit.group(1)) if hit else 318
        win = [f for f in fr if th - 12 <= tic(f) <= th + 2]
        pick = [win[int(k * (len(win) - 1) / 4)] for k in range(5)] if len(win) >= 5 else win
        ims = []
        for f in pick:
            im = Image.open(f).convert('RGB'); z = im.crop((120, 120, 360, 360)).resize((320, 320))
            ImageDraw.Draw(z).text((4, 300), 't%d (x2 crop)' % tic(f), fill=(255, 255, 0)); ims.append(z)
        if ims:
            sh = Image.new('RGB', (320 * len(ims), 320)); [sh.paste(im, (320 * k, 0)) for k, im in enumerate(ims)]
            ImageDraw.Draw(sh).text((4, 4), '%s %s (blue dot = the butt point the melee code uses)' % (g, tag), fill=(255, 255, 0)); sh.save('%s/%s_%s.png' % (OUT, tag, g))
        shutil.rmtree(d, ignore_errors=True)
