"""TEST ONLY: scope-toggle proof sheet: per gun, lens ON / after alt fire OFF / after alt fire ON again (crops of the left eye)."""
import sys
from PIL import Image, ImageDraw
O, out, fps = sys.argv[1], sys.argv[2], sys.argv[3]
rows = [('Sniper (Ruger)', 'dump_tg_Sniper', ('f00072', 'f00120', 'f00180')),
        ('RailGun', 'dump_tg_RailGun', ('f00084', 'f00132', 'f00180'))]
T = 360; W = 3 * T; H = 60 + len(rows) * (T + 24) + 20
sh = Image.new('RGB', (W, H), (20, 20, 20)); d = ImageDraw.Draw(sh)
d.text((8, 6), 'BD22 VR scope-toggle (lane-scope): alt fire toggles the live 3x scope. QZD 17.3 rig, left eye, eye 8 cm behind eyepiece. RIG ONLY, NOT HEADSET-CONFIRMED', fill=(255, 255, 255))
d.text((8, 22), 'columns: ON (selected) | OFF after alt fire (plain glass, no camera render) | ON again after alt fire (same 3x: lens target 46x55 / 48x54 px both times)', fill=(200, 200, 200))
d.text((8, 38), fps, fill=(255, 220, 120))
for k, (name, dd, fr) in enumerate(rows):
    y = 60 + k * (T + 24); d.text((8, y), name, fill=(255, 220, 120))
    for j, f in enumerate(fr):
        im = Image.open('%s/%s/%s.png' % (O, dd, f)).crop((300, 300, 660, 660))
        sh.paste(im, (j * T, y + 14))
sh.save(out); print(out)
