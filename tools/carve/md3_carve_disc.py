"""Carve (or delete) the triangles of one MD3 surface that lie in a TILTED disc: a plane at any angle.

Why this exists
---------------
md3_carve_surface.py selects with a slab crossed with a cylinder, both along one of the model's own
x / y / z axes. That works while the piece faces down an axis. A lens on a mesh whose scope sits at
45 degrees in model space (BD22's RailGun.md3: its eyepiece glass faces (0.71, 0.02, -0.70) in the
model's frame 0) cannot be boxed that way without taking half the scope tube with it.

This selects around an arbitrary plane instead:

    * a centre point C and a unit normal N (the lens axis);
    * a BAND of signed distance along N:   lo <= (p - C) . N <= hi
    * a RADIUS about the axis through C along N:   |(p - C) - ((p - C) . N) N| <= radius

The plane can be given by hand (--centre X Y Z --normal NX NY NZ), or taken from another surface of
the same file (--plane-from-surface S): its vertex centroid and the smallest-variance direction of its
vertices (PCA), in the chosen --frame. That is how "the faces lying on the scope's own glass" is said
without measuring the glass by hand. The normal's sign from PCA is arbitrary: the tool prints it, and
--flip turns it round, so the band's lo/hi mean what you think they mean. Read the dry run first.

Coordinates are the MD3's own (int16 / 64), times --scale plus --offset per axis, exactly as in
md3_carve_surface.py, in ONE frame (--frame, default 0). Pick the frame the piece is measured in (for a
HUD gun, its ready frame): an animated mesh can put the same triangle somewhere else in frame 0.

What happens to the selected triangles
--------------------------------------
A triangle is selected only when ALL THREE of its vertices are inside the band and the radius (the
same whole-triangle rule as md3_carve_surface.py: no seams, no invented geometry).

    --name NEW   split them into a new surface NEW, appended last (byte-identical triangles, UVs,
                 normals and shader). The mesh is unchanged; MODELDEF can then SurfaceSkin it.
    --delete     drop them from the file. Use this for faces that should never draw (a lens cap
                 welded over glass that is already its own surface). Every MODELDEF that uses the
                 file is then right without edits, and the surface count does not change.

Exactly one of --name / --delete. Every frame keeps every remaining vertex; vertices no triangle
references afterwards are dropped and counted.

Usage
-----
    python -B md3_carve_disc.py IN.md3 OUT.md3 --surface N (--name NEW | --delete) \
        (--plane-from-surface S | --centre X Y Z --normal NX NY NZ) [--flip] \
        --band LO HI --radius R [--frame F] [--scale SX SY SZ] [--offset OX OY OZ] [--dry-run]

Example (BD22 RailGun, 2026-10-27; the 24-triangle cap over the eyepiece glass, ready frame 3):
    python -B md3_carve_disc.py RailGun.md3 RailGun.md3 --surface 0 --delete \
        --plane-from-surface 1 --frame 3 --band -0.15 0.25 --radius 1.65
"""
import argparse
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md3_carve_surface import parse, build, compact, tri_list, sname, positions  # noqa: E402


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def unit(v):
    n = math.sqrt(dot(v, v))
    if n == 0:
        raise SystemExit('zero-length normal')
    return (v[0] / n, v[1] / n, v[2] / n)


def plane_of(pts):
    """Centroid and smallest-variance direction (PCA) of a point set, without numpy."""
    k = len(pts)
    c = tuple(sum(p[i] for p in pts) / k for i in range(3))
    cov = [[0.0] * 3 for _ in range(3)]
    for p in pts:
        d = sub(p, c)
        for i in range(3):
            for j in range(3):
                cov[i][j] += d[i] * d[j]
    # smallest eigenvector: power iteration on (trace*I - cov), whose largest eigenvector it is
    t = cov[0][0] + cov[1][1] + cov[2][2]
    M = [[(t if i == j else 0.0) - cov[i][j] for j in range(3)] for i in range(3)]
    best = None
    for seed in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
        v = seed
        for _ in range(500):
            v = unit(tuple(sum(M[i][j] * v[j] for j in range(3)) for i in range(3)))
        # Rayleigh quotient on cov: the smaller, the better
        cv = tuple(sum(cov[i][j] * v[j] for j in range(3)) for i in range(3))
        q = dot(v, cv)
        if best is None or q < best[0]:
            best = (q, v)
    return c, best[1]


def select(pos, centre, normal, lo, hi, radius):
    keep = set()
    r2 = radius * radius
    for i, p in enumerate(pos):
        d = sub(p, centre)
        a = dot(d, normal)
        if not lo <= a <= hi:
            continue
        rr = dot(d, d) - a * a
        if rr <= r2:
            keep.add(i)
    return keep


def carve_disc(m, index, centre, normal, lo, hi, radius, frame, newname=None, delete=False,
               scale=(1.0, 1.0, 1.0), offset=(0.0, 0.0, 0.0)):
    src = m['surfs'][index]
    pos = positions(src, frame, scale, offset)
    chosen = select(pos, centre, normal, lo, hi, radius)
    tris = tri_list(src)
    moved, stayed, moved_ids = [], [], []
    for t in range(src['nt']):
        a, b, c = tris[t * 3], tris[t * 3 + 1], tris[t * 3 + 2]
        if a in chosen and b in chosen and c in chosen:
            moved.extend((a, b, c))
            moved_ids.append(t)
        else:
            stayed.extend((a, b, c))
    if not moved:
        raise SystemExit('selector matched %d vertices but no whole triangle' % len(chosen))
    # where the selected triangles actually lie, so the dry run can be checked against the band
    al = [dot(sub(pos[v], centre), normal) for v in moved]
    rr = [math.sqrt(max(0.0, dot(sub(pos[v], centre), sub(pos[v], centre)) - x * x))
          for v, x in zip(moved, al)]
    keep_surf, _ = compact(src, stayed, m['nfr'])
    m['surfs'][index] = keep_surf
    info = dict(chosen=len(chosen), tris=len(moved) // 3, ids=moved_ids,
                along=(min(al), max(al)), rmax=max(rr),
                kept_tris=len(stayed) // 3, kept_verts=keep_surf['nv'],
                src_tris=src['nt'], src_verts=src['nv'])
    if not delete:
        new_surf, _ = compact(src, moved, m['nfr'])
        new_surf['name'] = newname.encode('latin-1')[:63].ljust(64, b'\0')
        m['surfs'].append(new_surf)
        info['new_verts'] = new_surf['nv']
    return info


def ranges(ids):
    out, s = [], None
    for k, t in enumerate(ids):
        if s is None:
            s = t
        if k + 1 == len(ids) or ids[k + 1] != t + 1:
            out.append('%d' % s if s == t else '%d-%d' % (s, t))
            s = None
    return ' '.join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('infile')
    ap.add_argument('outfile')
    ap.add_argument('--surface', type=int, required=True, help='surface whose triangles are selected')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--name', help='split the selection into a new surface of this name')
    g.add_argument('--delete', action='store_true', help='drop the selection from the file')
    ap.add_argument('--plane-from-surface', type=int, default=None,
                    help='centre + normal from this surface (centroid, PCA) in --frame')
    ap.add_argument('--centre', type=float, nargs=3, default=None)
    ap.add_argument('--normal', type=float, nargs=3, default=None)
    ap.add_argument('--flip', action='store_true', help='reverse the normal')
    ap.add_argument('--band', type=float, nargs=2, required=True, metavar=('LO', 'HI'),
                    help='signed distance along the normal')
    ap.add_argument('--radius', type=float, required=True, help='distance from the axis')
    ap.add_argument('--frame', type=int, default=0)
    ap.add_argument('--scale', type=float, nargs=3, default=(1.0, 1.0, 1.0))
    ap.add_argument('--offset', type=float, nargs=3, default=(0.0, 0.0, 0.0))
    ap.add_argument('--dry-run', action='store_true', help='report, write nothing')
    a = ap.parse_args(argv)

    m = parse(open(a.infile, 'rb').read())
    ns = len(m['surfs'])
    if not 0 <= a.surface < ns:
        raise SystemExit('surface %d out of range (%d surfaces)' % (a.surface, ns))
    if not 0 <= a.frame < m['nfr']:
        raise SystemExit('frame %d out of range (%d frames)' % (a.frame, m['nfr']))
    if a.name and any(sname(s) == a.name for s in m['surfs']):
        raise SystemExit('a surface named %r already exists' % a.name)
    if a.plane_from_surface is not None:
        if a.centre or a.normal:
            raise SystemExit('give --plane-from-surface OR --centre/--normal, not both')
        ps = m['surfs'][a.plane_from_surface]
        centre, normal = plane_of(positions(ps, a.frame, a.scale, a.offset))
        src = 'surface %d %r' % (a.plane_from_surface, sname(ps))
    else:
        if not (a.centre and a.normal):
            raise SystemExit('need --plane-from-surface, or both --centre and --normal')
        centre, normal = tuple(a.centre), unit(tuple(a.normal))
        src = 'given'
    if a.flip:
        normal = (-normal[0], -normal[1], -normal[2])

    before = sum(s['nt'] for s in m['surfs'])
    print('%s: %d surfaces, %d frames, %d triangles' % (a.infile, ns, m['nfr'], before))
    print('  plane (%s, frame %d): centre %.4f %.4f %.4f  normal %.4f %.4f %.4f'
          % ((src, a.frame) + tuple(centre) + tuple(normal)))
    print('  band %.4f..%.4f along the normal, radius %.4f; surface %d %r (%d verts, %d tris)'
          % (a.band[0], a.band[1], a.radius, a.surface, sname(m['surfs'][a.surface]),
             m['surfs'][a.surface]['nv'], m['surfs'][a.surface]['nt']))
    r = carve_disc(m, a.surface, centre, normal, a.band[0], a.band[1], a.radius, a.frame,
                   newname=a.name, delete=a.delete, scale=a.scale, offset=a.offset)
    print('  selected %d triangles (ids %s), %d vertices in the disc'
          % (r['tris'], ranges(r['ids']), r['chosen']))
    print('  they lie %.4f..%.4f along the normal, at most %.4f from the axis'
          % (r['along'] + (r['rmax'],)))
    print('  surface %d now %d verts / %d tris (was %d / %d)'
          % (a.surface, r['kept_verts'], r['kept_tris'], r['src_verts'], r['src_tris']))
    if a.delete:
        print('  DELETED %d triangles' % r['tris'])
    else:
        print('  new surface %d %r: %d verts / %d tris' % (ns, a.name, r['new_verts'], r['tris']))
    if a.dry_run:
        print('  dry run: nothing written')
        return 0
    out = build(m)
    open(a.outfile, 'wb').write(out)
    chk = parse(open(a.outfile, 'rb').read())
    after = sum(s['nt'] for s in chk['surfs'])
    want = before - (r['tris'] if a.delete else 0)
    if after != want or len(chk['surfs']) != len(m['surfs']):
        raise SystemExit('verify FAILED: %d triangles / %d surfaces written' % (after, len(chk['surfs'])))
    print('  verified: %d surfaces, %d triangles, %d frames' % (len(chk['surfs']), after, chk['nfr']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
