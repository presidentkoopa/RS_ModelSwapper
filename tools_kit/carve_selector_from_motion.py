"""Derive md3_carve_surface's selector from a surface's own internal motion.

Nine guns on the shelf have their moving part welded into a single surface -- the
Chex zorch propulsor, Zion's super shotgun, pistol, rocket launcher and gauss
cannon, and the universal chaingun. Walking their frames shows the part plainly:
1729 of the super shotgun's 2784 vertices move, 8418 of the zorch propulsor's
10111. md3label cannot carve them, because its carve works on surfaces that
already carry a role, and carve_by_ref cannot, because it needs a reference mesh
with the parts already split and there is none for Zion.

md3_carve_surface CAN split one surface, given a slab crossed with a cylinder.
This writes nothing and carves nothing: it measures which vertices move and
reports the slab and cylinder that enclose them, as the arguments to pass. The
carve itself stays the tool that already does carving.

Method: stabilise every frame onto frame 0 on the surface's own largest rigid
cluster -- the vertices that stay still relative to each other -- then take the
vertices whose residual exceeds the threshold. The slab axis is the one along
which the moving set is most separated from the still set, because that is the
axis a slab can actually cut on.
"""
import os, re, sys
import numpy as np
sys.path.insert(0, 'tools_kit')
from md3read import read_md3
from md3label import kabsch

AX = ('x', 'y', 'z')


def moving_mask(V, thresh=2.0, rounds=3):
    """Which vertices move, after stabilising on the surface's own rigid part.

    Fitting every frame on ALL the vertices lets a large moving group drag the
    fit and hide itself. So fit, drop the worst movers, and fit again on what is
    left -- after a few rounds the reference is the part that holds still.
    """
    nf = len(V)
    keep = np.ones(len(V[0]), bool)
    resid = np.zeros(len(V[0]))
    for _ in range(rounds):
        resid = np.zeros(len(V[0]))
        for f in range(1, nf):
            R, t = kabsch(V[f][keep], V[0][keep])
            resid = np.maximum(resid, np.linalg.norm(V[f] @ R.T + t - V[0], axis=1))
        nxt = resid <= thresh
        if nxt.sum() < 20 or (nxt == keep).all():
            break
        keep = nxt
    return resid > thresh, resid


def selector(V, mask):
    """Slab and cylinder enclosing the moving vertices, in raw model units."""
    P = V[0][mask]
    Q = V[0][~mask]
    if len(P) < 4:
        return None
    # The slab axis is the one on which the moving set overlaps the still set
    # least -- the only axis a slab bound can separate them on.
    best, bestax = -1.0, 0
    for i in range(3):
        lo, hi = P[:, i].min(), P[:, i].max()
        inside = ((Q[:, i] >= lo) & (Q[:, i] <= hi)).mean() if len(Q) else 0.0
        score = (hi - lo) * (1.0 - inside)
        if score > best:
            best, bestax = score, i
    i = bestax
    other = [j for j in range(3) if j != i]
    c = P[:, other].mean(0)
    r = float(np.linalg.norm(P[:, other] - c, axis=1).max())
    return dict(axis=AX[i], lo=float(P[:, i].min()), hi=float(P[:, i].max()),
                centre=(float(c[0]), float(c[1])), radius=r,
                nmove=int(mask.sum()), ntotal=int(len(mask)))


def main(names):
    md = open('modeldef', encoding='utf-8', errors='replace').read()
    for n in names:
        m = re.search(r'(?ms)^Model\s+' + re.escape(n) + r'\s*\r?\n\{(.*?)^\}', md)
        if not m:
            print(f'{n}: not in modeldef'); continue
        p = re.search(r'Path\s+"([^"]+)"', m.group(1))
        f = re.search(r'Model\s+0\s+"([^"]+)"', m.group(1))
        path = os.path.join(p.group(1).rstrip('/'), f.group(1))
        if not os.path.exists(path):
            print(f'{n}: mesh missing at {path}'); continue
        mm = read_md3(path)
        if len(mm['surfs']) != 1:
            print(f'{n}: {len(mm["surfs"])} surfaces -- not a welded one, skipped'); continue
        V = mm['surfs'][0]['xyz']
        if mm['nframes'] < 2:
            print(f'{n}: one frame, nothing to walk'); continue
        mask, resid = moving_mask(V)
        s = selector(V, mask)
        print(f'\n{n}   {len(V[0])} verts, {mm["nframes"]} frames   mesh {path}')
        if not s:
            print('   no moving cluster above 2.0 units'); continue
        print(f'   {s["nmove"]} of {s["ntotal"]} vertices move, up to {resid.max():.2f} units')
        print(f'   python -B tools_kit/md3_carve_surface.py "{path}" "{path}" \\')
        print(f'       --surface 0 --name mag --slab-axis {s["axis"]} '
              f'--slab {s["lo"]:.2f} {s["hi"]:.2f} \\')
        print(f'       --centre {s["centre"][0]:.2f} {s["centre"][1]:.2f} '
              f'--radius {s["radius"]:.2f} --dry-run')


if __name__ == '__main__':
    main(sys.argv[1:])
