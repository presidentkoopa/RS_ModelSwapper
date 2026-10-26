"""shell_stack_render.py -- render the off hand holding a grab of 1-4 shells, from the tables the engine reads
(rsr_pump_guns.zs HandHook / HandRot, rsp_stack.ms.zs, MODELDEF.rsrpump's shell surface), as rsr_pump.zs
RSP_Handler.Place places layers 2210-2213.   python3 -B tools_kit/shell_stack_render.py OUT.png"""
import sys, os, re, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import hudrender as H


def unturn(a, v):
    cx, sx, cy, sy, cz, sz = (math.cos(math.radians(a[0])), math.sin(math.radians(a[0])), math.cos(math.radians(a[1])),
                              math.sin(math.radians(a[1])), math.cos(math.radians(a[2])), math.sin(math.radians(a[2])))
    r0 = np.array((cx * cz + sx * sy * sz, -cx * sz + sx * sy * cz, sx * cy)); r1 = np.array((cy * sz, cy * cz, -sy))
    r2 = np.array((-sx * cz + cx * sy * sz, sx * sz + cx * sy * cz, cx * cy))
    return r0 * v[0] + r1 * v[1] + r2 * v[2]


def main(out):
    t = open(os.path.join(ROOT, 'zscript_depot/rsr/rsr_pump_guns.zs')).read()
    v3 = lambda fn: np.array([float(x) for x in re.search(r'static Vector3 %s\(int i\).*?case 1:\s*return \(([^)]+)\)' % fn, t, re.S).group(1).split(',')])
    s = open(os.path.join(ROOT, 'zscript_depot/rsr/rsp_stack.ms.zs')).read()
    D = np.array([float(x) for x in re.search(r'Dir\(\) \{ return \(([^)]+)\)', s).group(1).split(',')])
    sp = float(re.search(r'case 1:\s*return ([\d.]+)', s).group(1))
    hook, rot, sc = v3('HandHook'), list(v3('HandRot')), [1.35, 1.35, 1.35]
    orig = H.load
    H.load = lambda p: [orig(p)[2]] if p.endswith('shotgun.md3') else orig(p)
    from PIL import Image
    tiles = []
    for n in (1, 2, 3, 4):
        items = [dict(path=os.path.join(ROOT, 'models/rsq/ammo_hand.md3'), frame=1, scale=[-1, 1, 1], off=[0, -24, -10], color=[225, 170, 135])]
        for k in range(n):
            d = D * sp * k
            h = hook + unturn(rot, np.array([-d[1] / sc[0], d[2] / sc[2], -d[0] / sc[1]]))
            items.append(dict(path=os.path.join(ROOT, 'models/hud/Shotgun/shotgun.md3'), frame=12, scale=sc, off=[0, 0, 0],
                              hook=list(h), rot=rot, color=[200, 60, 50] if k == 0 else [230, 150, 40]))
        P = np.concatenate([H.to_local(xyz[it['frame']], it) for it in items for _, xyz in H.load(it['path'])])
        c = (P.min(0) + P.max(0)) / 2; r = float(np.ptp(P, 0).max())
        for e in ((0.9, 0.5, 0.4), (-0.7, 0.3, 0.9)):
            fn = out.replace('.png', '_%d_%d.png' % (n, len(tiles) % 2))
            H.render(items, fn, eye=tuple(c + np.array(e) * r * 1.6), look=tuple(c), W=400, H=300, fov=45,
                     title='Shells per grab %d (MS_Shotgun)' % n)
            tiles.append(fn)
    ims = [Image.open(x) for x in tiles]
    sheet = Image.new('RGB', (800, 1200))
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % 2) * 400, (k // 2) * 300))
    sheet.save(out)
    for x in tiles:
        os.remove(x)
    print(out)


if __name__ == '__main__':
    main(sys.argv[1])
