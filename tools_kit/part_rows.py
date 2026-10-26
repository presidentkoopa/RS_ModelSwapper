"""part_rows.py -- a multi-part donor block draws every part, not just Model 0.

    python3 -B tools_kit/part_rows.py [--dry] [--prefix MS_zion_] [--render OUTDIR]

The engine draws a block's Model k only on a sprite frame that has a FrameIndex row for k. Several
imported blocks carry their rest-pose row for Model 0 alone (the same pattern as BD22 Rifle's M203,
fixed in lift_bd22.rest_rows), so their extra parts -- a chaingun's barrel, the BFG's orb, a plasma
rifle's mod -- were never drawn and the support hand closed on nothing.

For each block in `modeldef` with Model 1.. but FrameIndex rows for Model 0 only (the MSBL blank row
aside), each extra model gets a row on the same sprite and frame letter, at Model 0's frame (clamped to
that mesh's frame count), PROVIDED it is measured to belong there: every connected piece (triangle
island) of the part must chain back to the base mesh through gaps of at most TOUCH mesh units. A
part with a piece left floating off the gun at that frame (Zion's SSG shells sit 20+ units below the
gun until its reload brings them up) is reported, not written.
--render writes a before / after sheet per block (tools_kit/hudrender.py, the block's own Scale and
Offset) and one contact sheet.
"""
import os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rgeo import load_md3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOUCH = 3.5            # mesh units: Zion's chaingun barrel tubes chain to the gun at 2.3-2.6, the turret's at <= 3.2


def blocks(t, prefix):
    for m in re.finditer(r'^Model\s+(%s\w*)\s*\{.*?^\}' % re.escape(prefix), t, re.M | re.S):
        yield m.group(1), m.group(0)


def frames(path, mesh):
    return load_md3(os.path.join(ROOT, path, mesh))


def islands(s, f):
    n = s['xyz'].shape[1]
    par = list(range(n))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for a, b, c in s['tris']:
        for x, y in ((a, b), (b, c)):
            rx, ry = find(x), find(y)
            if rx != ry:
                par[rx] = ry
    g = {}
    for v in range(n):
        g.setdefault(find(v), []).append(v)
    return [s['xyz'][f][idx] for idx in g.values()]


def floating(B, part, f):
    """the part's islands grown onto the base through gaps <= TOUCH: (gaps of those left, largest gap used)"""
    isl = [p for s in part for p in islands(s, f)]
    acc, left, worst = [B], list(range(len(isl))), 0.0
    grew = True
    while grew:
        grew = False
        A = np.concatenate(acc)
        for i in list(left):
            d = float(np.sqrt(((isl[i][:, None, :] - A[None, :, :]) ** 2).sum(-1)).min())
            if d <= TOUCH:
                acc.append(isl[i]); left.remove(i); grew = True
                worst = max(worst, d)
    A = np.concatenate(acc)
    return [float(np.sqrt(((isl[i][:, None, :] - A[None, :, :]) ** 2).sum(-1)).min()) for i in left], worst


def plan(name, blk):
    models = dict((int(k), v) for k, v in re.findall(r'^\s*Model\s+(\d+)\s+"([^"]+)"', blk, re.M))
    if len(models) < 2:
        return None
    rows = re.findall(r'^[ \t]*FrameIndex\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)[^\n]*$', blk, re.M)
    real = [r for r in rows if r[0] != 'MSBL']
    if not real or {int(r[2]) for r in real} != {0}:
        return None
    path = re.search(r'Path\s+"([^"]+)"', blk).group(1)
    base = frames(path, models[0])
    add, notes = [], []
    for spr, let, _, fr in real:
        f0 = int(fr)
        B = np.concatenate([s['xyz'][f0] for s in base])
        for k in sorted(models):
            if k == 0:
                continue
            pm = frames(path, models[k])
            n = pm[0]['xyz'].shape[0]
            f = min(f0, n - 1)
            loose, worst = floating(B, pm, f)
            if not loose:
                add.append((spr, let, k, f))
                notes.append('Model %d %s f%d: every piece chains to the gun (largest gap %.2f u)' % (k, models[k], f, worst))
            else:
                notes.append('Model %d %s f%d: %d piece(s) float %.1f-%.1f u off the gun: NOT written'
                             % (k, models[k], f, len(loose), min(loose), max(loose)))
    return dict(path=path, models=models, rows=real, add=add, notes=notes)


def scale_off(blk):
    sc = [float(x) for x in re.search(r"^\s*Scale[ \t]+(\S+)[ \t]+(\S+)[ \t]+(\S+)", blk, re.M).groups()]
    om = re.search(r"^\s*Offset[ \t]+(\S+)[ \t]+(\S+)[ \t]+(\S+)", blk, re.M)
    off = [float(x) for x in om.groups()] if om else [0.0, 0.0, 0.0]
    zm = re.search(r"^\s*ZOffset[ \t]+(\S+)", blk, re.M)
    if zm:
        off[2] = float(zm.group(1))
    return sc, off


def render(name, blk, p, outdir):
    import hudrender
    sc, off = scale_off(blk)
    cols = [(200, 200, 190), (230, 120, 60), (90, 170, 230), (120, 210, 110)]
    f0 = int(p['rows'][0][3])
    before = [dict(path=os.path.join(ROOT, p['path'], p['models'][0]), frame=f0, scale=sc, off=off, color=cols[0])]
    after = before + [dict(path=os.path.join(ROOT, p['path'], p['models'][k]), frame=f, scale=sc, off=off, color=cols[k % 4])
                      for _, _, k, f in p['add']]
    # the camera on the block's own extent, from the side and a little above
    pts = []
    for it in after:
        for tris, xyz in hudrender.load(it['path']):
            pts.append(hudrender.to_local(xyz[it['frame']], it))
    P = np.concatenate(pts)
    c = (P.min(0) + P.max(0)) / 2
    r = float(np.ptp(P, 0).max())
    kw = dict(eye=tuple(c + np.array([0.9, 0.45, 0.25]) * r * 1.4), look=tuple(c), W=480, H=360, fov=45)
    a = hudrender.render(before, os.path.join(outdir, '%s_BEFORE.png' % name), title='%s BEFORE: Model 0 only' % name, **kw)
    b = hudrender.render(after, os.path.join(outdir, '%s_AFTER.png' % name), title='%s AFTER: every part' % name, **kw)
    return a, b


def main():
    dry = '--dry' in sys.argv
    prefix = sys.argv[sys.argv.index('--prefix') + 1] if '--prefix' in sys.argv else 'MS_zion_'
    outdir = sys.argv[sys.argv.index('--render') + 1] if '--render' in sys.argv else None
    p_md = os.path.join(ROOT, 'modeldef')
    t = open(p_md, encoding='latin-1').read()
    pairs = []
    n = 0
    for name, blk in list(blocks(t, prefix)):
        p = plan(name, blk)
        if not p:
            continue
        n += 1
        print('%s' % name)
        for l in p['notes']:
            print('   ', l)
        if outdir:
            os.makedirs(outdir, exist_ok=True)
            pairs.append(render(name, blk, p, outdir))
        if p['add'] and not dry:
            last = re.findall(r'^[ \t]*FrameIndex\s+(?!MSBL)\S+\s+\S+\s+0\s+\d+[^\n]*\n', blk, re.M)[-1]
            extra = ''.join('\tFrameIndex %s %s %d %d\t// part_rows.py: measured on the base at this frame\n' % a for a in p['add'])
            nb = blk.replace(last, last + extra, 1)
            t = t.replace(blk, nb)
    if not dry:
        open(p_md, 'w', encoding='latin-1', newline='\n').write(t)
    print('%d block(s)%s' % (n, ' (dry run)' if dry else ''))
    if outdir and pairs:
        from PIL import Image
        ims = [(Image.open(a), Image.open(b)) for a, b in pairs]
        w, h = ims[0][0].size
        sheet = Image.new('RGB', (w * 2, h * len(ims)))
        for i, (a, b) in enumerate(ims):
            sheet.paste(a, (0, h * i)); sheet.paste(b, (w, h * i))
        cs = os.path.join(outdir, 'parts_before_after_sheet.png')
        sheet.save(cs)
        print('sheet', cs)


if __name__ == '__main__':
    main()
