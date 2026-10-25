"""Split a generated WMCARD lump into strokes we believe and strokes we do not.

The generator takes the insertion stroke from the card's `mag_in` phase. On guns
whose reload animation throws the spent magazine clear of the screen, that phase
also contains the arrival of the new one from off-screen, and the stroke comes
out at 30 to 185 units -- a metre or more once scaled, for a pistol magazine.

The ceiling comes from the well and the magazine, both measured off the same
mesh and the same card:

    seat -> mouth of the magazine well, plus the magazine's own length along
    the insertion axis

Past that the magazine would have left the gun entirely, so the hand cannot have
stroked further. Either half alone is too tight a ceiling: the magazine starts
below the well and the hand carries it up, so the stroke is longer than the well
is deep, and longer than a short clip.

Tested against the six Wolfenstein strokes the kit itself blessed -- Kar98 5.91,
MG42 9.59, MP40 7.78, PP41 7.16, BAR 11.02, Garand 9.31 -- all six pass, so the
check is not merely rejecting everything.

A gun that fails is measured and carded; only this one number is wrong. It is
held out rather than shipped, because a wrong stroke drives the player's hand to
the wrong place, which is worse than no VR reload at all.
"""
import os, re, sys
import numpy as np
sys.path.insert(0, 'tools_kit')
from md3read import read_md3

V = r'(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)'
VB = r'\[\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\s*\]'


def ceiling(card_path, model_dir, mesh):
    """seat->mouth depth + magazine length along the insertion axis."""
    if not os.path.exists(card_path):
        return None
    c = open(card_path, encoding='utf-8', errors='replace').read()
    w = re.search(r'mag_well\s+' + VB + r'\s+mouth\s+' + VB + r'\s+axis\s+' + VB, c)
    if not w:
        return None
    g = [float(x) for x in w.groups()]
    seat, mouth, axis = np.array(g[0:3]), np.array(g[3:6]), np.array(g[6:9])
    depth = float(np.linalg.norm(mouth - seat))
    p = os.path.join(model_dir, mesh)
    if not os.path.exists(p):
        return None
    n = np.linalg.norm(axis)
    if n < 1e-9:
        return None
    # The card names the magazine by SURFACE INDEX ("mag surf 4"). The original
    # mesh's surfaces are unnamed -- it is md3label's own output copy that carries
    # role names -- so the index is what resolves here, not the name.
    si = re.search(r'(?m)^\s*mag\s+surf\s+(\d+)', c)
    if not si:
        return None
    i = int(si.group(1))
    m = read_md3(p)
    if i >= len(m['surfs']):
        return None
    d = m['surfs'][i]['xyz'][0] @ (axis / n)
    L = float(d.max() - d.min())
    return depth, L, depth + L


def main(src, cards_dir, keep_path, review_path):
    t = open(src, encoding='utf-8', errors='replace').read()
    hdr = t.split('weapon "')[0]
    keep, drop = [], []
    for chunk in re.split(r'(?m)^weapon "', t)[1:]:
        name = chunk.split('"', 1)[0]
        body = 'weapon "' + chunk
        md = re.search(r'model\s+=\s+"([^"]+)"\s+"([^"]+)"', body)
        di = re.search(r'distance = ([\d.]+)', body)
        if not (md and di):
            drop.append((name, 'no magazine dof', 0.0, None, None)); continue
        stroke = float(di.group(1))
        r = ceiling(os.path.join(cards_dir, name + '.card'), md.group(1), md.group(2))
        if r is None:
            drop.append((name, 'no mag_well or no mag surface', stroke, None, None)); continue
        depth, L, ceil = r
        if stroke < 0.5:
            drop.append((name, 'stroke is zero', stroke, depth, L)); continue
        if stroke > ceil + 0.5:
            drop.append((name, 'stroke exceeds well depth + magazine length',
                         stroke, depth, L)); continue
        keep.append((name, body, stroke, depth, L))

    open(keep_path, 'w', encoding='utf-8').write(hdr + ''.join(b for _, b, _, _, _ in keep))
    with open(review_path, 'w', encoding='utf-8') as fh:
        fh.write('# Magazine strokes held back for review\n\n')
        fh.write('These guns are measured and carded. The one number that is wrong is the\n')
        fh.write('insertion stroke: it came from the card\'s mag_in phase, and on a gun whose\n')
        fh.write('animation throws the spent magazine clear of the screen that phase catches\n')
        fh.write('the throw, not the insertion.\n\n')
        fh.write('The ceiling is the well depth (seat to mouth) plus the magazine\'s own\n')
        fh.write('length along the insertion axis -- past that the magazine has left the gun.\n\n')
        fh.write(f'{"gun":<30} {"stroke":>8} {"well":>7} {"mag":>7} {"ceiling":>8}  reason\n')
        fh.write('-' * 96 + '\n')
        for n, why, st, dep, L in sorted(drop, key=lambda x: -(x[2] or 0)):
            c = f'{dep + L:.2f}' if dep is not None and L is not None else '-'
            fh.write(f'{n:<30} {st:>8.2f} '
                     f'{(f"{dep:.2f}" if dep is not None else "-"):>7} '
                     f'{(f"{L:.2f}" if L is not None else "-"):>7} {c:>8}  {why}\n')

    print(f'kept   {len(keep):>3}  -> {keep_path}')
    print(f'held   {len(drop):>3}  -> {review_path}')
    for n, b, st, dep, L in keep:
        print(f'   {n:<30} stroke {st:>6.2f}   (well {dep:.2f} + mag {L:.2f} = {dep + L:.2f})')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
