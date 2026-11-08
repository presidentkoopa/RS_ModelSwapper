import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
from PIL import Image, ImageDraw
rows = [('Sniper (Ruger XM21)', 'dump_sn7', 'f00033', 'f00054', 'f00099', 'in lens 46x55 px / outside 15x18 = 3.07x across, 3.06x up (area 2.98x); tilt < 0.3 deg'),
        ('RailGun', 'dump_rg2', 'f00057', 'f00105', 'f00135', 'in lens 48x54 px / outside 15x18 = 3.2x across, 3.0x up (area 2.92x); tilt ~1 deg')]
T = 300; W = 4 * T; H = len(rows) * (T + 40) + 40
sh = Image.new('RGB', (W, H), (20, 20, 20)); d = ImageDraw.Draw(sh)
d.text((8, 8), 'BD22 VR scope-3x (branch lane-scope): QZD 17.3 rig, left eye, 960x960, default cvars (fresh names). RIG ONLY, NOT HEADSET-CONFIRMED', fill=(255, 255, 255))
d.text((8, 22), 'cols: rest pose (eye ~30 cm off, picture already on) | eye 8 cm behind eyepiece, steady | lens zoom x1.4 (magenta = 8u target at 256u; same target 15x18 px outside, right) | turning 10 deg', fill=(200, 200, 200))
for k, (name, dd, a, b, c, txt) in enumerate(rows):
    y = 40 + k * (T + 40)
    d.text((8, y), name + ': ' + txt, fill=(255, 220, 120))
    A = Image.open('%s/%s.png' % (dd, a)); B = Image.open('%s/%s.png' % (dd, b)); C = Image.open('%s/%s.png' % (dd, c))
    sh.paste(A.resize((T, T)), (0, y + 16)); sh.paste(B.resize((T, T)), (T, y + 16))
    sh.paste(B.crop((395, 400, 615, 620)).resize((T, T), Image.NEAREST), (2 * T, y + 16))
    sh.paste(C.resize((T, T)), (3 * T, y + 16))
sh.save((_DP.WORK + '/out' + '/scope_3x.png')); print('ok')
