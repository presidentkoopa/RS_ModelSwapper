"""Split one MD3 surface in two along a geometric selector, without changing the mesh.

Why this exists
---------------
A piece of a gun that the game has to treat on its own -- a scope lens that takes a
camera texture, a bulb that goes dark when it is shot, a panel that is hidden by a
clear skin -- has to be its OWN MD3 surface, because MODELDEF's only per-piece lever
is `SurfaceSkin <model> <surface> <image>`. Most purchased meshes do not split that
way: the lens is welded into the scope body as a few hundred triangles of one big
surface. This takes those triangles out into a surface of their own.

Nothing about the mesh changes. The triangles that move keep their winding, their
UVs, their packed normals and their shader name, byte for byte; the triangles that
stay are untouched; the total triangle count across the file is the same before and
after. Only the surface they live in, and therefore the vertex indices that address
them, are different. (Vertices that no triangle references after the split are
dropped from the compacted surfaces -- they drew nothing before either. The count is
reported.)

The selector
------------
A slab crossed with a cylinder, which is what nearly every lens, bulb, muzzle crown,
drum or button actually is:

    * a SLAB: lo <= p[slab_axis] <= hi
    * a CYLINDER about an axis parallel to slab_axis, passing through the two
      remaining coordinates (centre), of the given radius

Coordinates are read in a frame of the caller's choosing: each MD3 model unit
(int16/64) is multiplied by --scale and shifted by --offset, per axis. That is how a
measurement taken in some other frame -- centimetres in a VR weapon controller's
frame, say, after a MODELDEF Scale / Offset / ZOffset -- can be used directly as the
selector, instead of being converted back into raw model units by hand.

A triangle moves only when ALL THREE of its vertices are selected. A triangle with
one vertex outside stays where it is. That is deliberate: it means the split never
invents or deletes geometry and never leaves a seam straddling two surfaces, and it
is why the carved patch is a little SMALLER than the selector circle -- the ring of
triangles that bridge the selection's edge to its surroundings stay behind. Check the
reported triangle count against what you expected before trusting the result.

--project-uv (OFF by default)
-----------------------------
A camera texture, or any image meant to be seen flat through the carved piece, needs
the new surface's UVs to span 0..1 across the patch. An authored mesh almost never
unwraps a lens that way -- it will be a handful of scattered strips somewhere in the
gun's atlas, and a camera texture laid over those UVs is a smear, not a picture.
--project-uv replaces the NEW surface's UVs with a planar projection onto the plane
perpendicular to slab_axis, normalised over the patch's own bounding box, so (0,0)
and (1,1) are its corners. This is LOSSY -- the carved piece can no longer show the
part of the original skin it used to show -- so it is never done unless asked for.

Usage
-----
    python -B md3_carve_surface.py IN.md3 OUT.md3 --surface N --name NEWNAME \
        --slab-axis {x,y,z} --slab LO HI --centre A B --radius R \
        [--scale SX SY SZ] [--offset OX OY OZ] [--tol T] [--project-uv] [--dry-run]

--centre's two numbers are the coordinates on the two axes that are NOT slab-axis,
in their natural order (slab-axis x -> centre is y z; y -> x z; z -> x y).

--tol defaults to half an MD3 position quantum on the slab axis (scale/128), because
MD3 stores positions as int16 sixty-fourths: a slab bound that lands between two
quantised vertex planes would otherwise include or exclude a whole ring of the mesh
on a rounding accident.

MD3 layout, for the next reader
-------------------------------
    header   ident@0 version@4 name@8(64) flags@72
             numFrames@76 numTags@80 numSurfaces@84 numSkins@88
             ofsFrames@92 ofsTags@96 ofsSurfaces@100 ofsEof@104
    surface  ident@0 name@4(64) flags@68 numFrames@72 numShaders@76 numVerts@80
             numTriangles@84 ofsTriangles@88 ofsShaders@92 ofsST@96
             ofsXYZNormal@100 ofsEnd@104              (all relative to the surface)
    vertex   int16 x, y, z in 1/64 model units, then a 2-byte encoded normal.

ofsSurfaces is at 100, not 88. 88 is numSkins. Getting that wrong reads the surface
list out of the middle of the frame data and the file looks corrupt for no reason.
"""

import argparse
import math
import struct
import sys

HDR = struct.Struct('<4si64si8i')   # ident, version, name, flags, 8 ints
SURF = struct.Struct('<4s64s10i')   # ident, name, flags, numFrames, numShaders,
                                    # numVerts, numTris, ofsTris, ofsShaders,
                                    # ofsST, ofsXYZ, ofsEnd
FRAME_SIZE = 56
TAG_SIZE = 112
SHADER_SIZE = 68
AXES = {'x': 0, 'y': 1, 'z': 2}


# ----------------------------------------------------------------------------- read

def parse(data):
    (ident, ver, name, flags, nfr, ntag, nsurf, nskin,
     ofr, otag, osurf, oend) = HDR.unpack_from(data, 0)
    if ident != b'IDP3':
        raise ValueError('not an MD3 (ident %r)' % ident)
    frames = [data[ofr + i * FRAME_SIZE: ofr + (i + 1) * FRAME_SIZE] for i in range(nfr)]
    tagbytes = ntag * TAG_SIZE
    tags = [data[otag + i * tagbytes: otag + (i + 1) * tagbytes] for i in range(nfr)]
    surfs = []
    off = osurf
    for _ in range(nsurf):
        (sid, sname, sflags, snfr, nsh, nv, nt,
         otri, osh, ost, oxyz, send) = SURF.unpack_from(data, off)
        if sid != b'IDP3':
            raise ValueError('surface ident %r at %d' % (sid, off))
        if snfr != nfr:
            raise ValueError('surface frame count %d != %d' % (snfr, nfr))
        surfs.append(dict(
            name=sname, flags=sflags, nsh=nsh, nv=nv, nt=nt,
            shaders=data[off + osh: off + osh + nsh * SHADER_SIZE],
            tris=data[off + otri: off + otri + nt * 12],
            st=data[off + ost: off + ost + nv * 8],
            xyz=[data[off + oxyz + f * nv * 8: off + oxyz + (f + 1) * nv * 8]
                 for f in range(nfr)],
        ))
        off += send
    return dict(ver=ver, name=name, flags=flags, nfr=nfr, ntag=ntag, nskin=nskin,
                frames=frames, tags=tags, surfs=surfs)


def build(m):
    nfr = m['nfr']
    body_frames = b''.join(m['frames'])
    body_tags = b''.join(m['tags'])
    blobs = []
    for s in m['surfs']:
        ofs_sh = SURF.size
        ofs_tri = ofs_sh + len(s['shaders'])
        ofs_st = ofs_tri + len(s['tris'])
        ofs_xyz = ofs_st + len(s['st'])
        xyz = b''.join(s['xyz'])
        ofs_end = ofs_xyz + len(xyz)
        head = SURF.pack(b'IDP3', s['name'], s['flags'], nfr, s['nsh'], s['nv'], s['nt'],
                         ofs_tri, ofs_sh, ofs_st, ofs_xyz, ofs_end)
        blobs.append(head + s['shaders'] + s['tris'] + s['st'] + xyz)
    ofr = HDR.size
    otag = ofr + len(body_frames)
    osurf = otag + len(body_tags)
    oend = osurf + sum(len(b) for b in blobs)
    head = HDR.pack(b'IDP3', m['ver'], m['name'], m['flags'], nfr, m['ntag'],
                    len(m['surfs']), m['nskin'], ofr, otag, osurf, oend)
    return head + body_frames + body_tags + b''.join(blobs)


def tri_list(s):
    return list(struct.unpack_from('<%di' % (s['nt'] * 3), s['tris'], 0))


def sname(s):
    return s['name'].rstrip(b'\0').decode('latin-1')


# ------------------------------------------------------------------------- selector

def positions(s, frame, scale, offset):
    """Vertices of one frame in the caller's frame: raw/64 * scale + offset."""
    out = []
    b = s['xyz'][frame]
    for i in range(s['nv']):
        x, y, z = struct.unpack_from('<hhh', b, i * 8)
        out.append((x / 64.0 * scale[0] + offset[0],
                    y / 64.0 * scale[1] + offset[1],
                    z / 64.0 * scale[2] + offset[2]))
    return out


def select(pos, axis, lo, hi, centre, radius, tol):
    """Indices inside the slab AND the cylinder."""
    oa = [k for k in (0, 1, 2) if k != axis]
    r2 = radius * radius
    keep = set()
    for i, p in enumerate(pos):
        if not (lo - tol <= p[axis] <= hi + tol):
            continue
        da = p[oa[0]] - centre[0]
        db = p[oa[1]] - centre[1]
        if da * da + db * db < r2:
            keep.add(i)
    return keep


# ---------------------------------------------------------------------------- carve

def compact(s, tris, frames):
    """A surface holding exactly `tris` (flat index list), vertices renumbered."""
    order = []
    remap = {}
    for v in tris:
        if v not in remap:
            remap[v] = len(order)
            order.append(v)
    st = b''.join(s['st'][v * 8:(v + 1) * 8] for v in order)
    xyz = [b''.join(s['xyz'][f][v * 8:(v + 1) * 8] for v in order) for f in range(frames)]
    packed = struct.pack('<%di' % len(tris), *[remap[v] for v in tris])
    return dict(name=s['name'], flags=s['flags'], nsh=s['nsh'], shaders=s['shaders'],
                nv=len(order), nt=len(tris) // 3, tris=packed, st=st, xyz=xyz), order


def project_uv(surf, order, pos, axis):
    """Planar UVs over the patch's own bounding box, for a camera texture."""
    oa = [k for k in (0, 1, 2) if k != axis]
    pts = [(pos[v][oa[0]], pos[v][oa[1]]) for v in order]
    u0 = min(p[0] for p in pts)
    u1 = max(p[0] for p in pts)
    v0 = min(p[1] for p in pts)
    v1 = max(p[1] for p in pts)
    du = (u1 - u0) or 1.0
    dv = (v1 - v0) or 1.0
    surf['st'] = b''.join(struct.pack('<ff', (p[0] - u0) / du, 1.0 - (p[1] - v0) / dv)
                          for p in pts)


def reproject(m, index, axis, scale=(1.0, 1.0, 1.0), offset=(0.0, 0.0, 0.0)):
    """Reproject ONE existing surface's UVs onto its own plane, 0..1, and carve nothing.

    The carve path projects because a freshly carved lens inherits UVs from wherever it sat on
    the gun's atlas, which is never a usable 0..1 map. A lens that is ALREADY its own surface
    has the same problem and nothing to carve: the railgun's "ScopeGlass" is 18 verts whose UVs
    are planar but cover 0.022 x 0.043 of its atlas, so a camera texture rendered into it would
    show a two-percent crop of the scene stretched over the glass.

    LOSSY, exactly as --project-uv is: the surface stops sampling whatever the artist painted
    there, so it needs a skin of its own afterwards.
    """
    s = m['surfs'][index]
    pos = positions(s, 0, scale, offset)
    project_uv(s, list(range(s['nv'])), pos, axis)
    return {'name': sname(s), 'nv': s['nv'], 'nt': s['nt']}


def carve(m, index, newname, axis, lo, hi, centre, radius, tol, do_project,
          scale=(1.0, 1.0, 1.0), offset=(0.0, 0.0, 0.0)):
    src = m['surfs'][index]
    pos = positions(src, 0, scale, offset)
    chosen = select(pos, axis, lo, hi, centre, radius, tol)
    tris = tri_list(src)
    moved, stayed = [], []
    for t in range(src['nt']):
        a, b, c = tris[t * 3], tris[t * 3 + 1], tris[t * 3 + 2]
        (moved if (a in chosen and b in chosen and c in chosen) else stayed).extend((a, b, c))
    if not moved:
        raise SystemExit('selector matched %d vertices but no whole triangle' % len(chosen))

    keep_surf, _ = compact(src, stayed, m['nfr'])
    new_surf, new_order = compact(src, moved, m['nfr'])
    new_surf['name'] = newname.encode('latin-1')[:63].ljust(64, b'\0')
    if do_project:
        project_uv(new_surf, new_order, pos, axis)

    m['surfs'][index] = keep_surf
    m['surfs'].append(new_surf)
    return dict(chosen=len(chosen), moved_tris=len(moved) // 3, moved_verts=new_surf['nv'],
                kept_tris=len(stayed) // 3, kept_verts=keep_surf['nv'],
                orphans=len(chosen) - len(set(moved)),
                src_tris_before=src['nt'], src_verts_before=src['nv'])


# ----------------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('infile')
    ap.add_argument('outfile')
    ap.add_argument('--surface', type=int, required=True, help='surface index to split')
    ap.add_argument('--name', default='', help='name of the new surface')
    ap.add_argument('--slab-axis', choices=('x', 'y', 'z'), default='x')
    ap.add_argument('--slab', type=float, nargs=2, default=(0.0, 0.0), metavar=('LO', 'HI'))
    ap.add_argument('--centre', type=float, nargs=2, default=(0.0, 0.0), metavar=('A', 'B'),
                    help='cylinder axis, on the two non-slab axes in order')
    ap.add_argument('--radius', type=float, default=0.0)
    ap.add_argument('--scale', type=float, nargs=3, default=(1.0, 1.0, 1.0))
    ap.add_argument('--offset', type=float, nargs=3, default=(0.0, 0.0, 0.0))
    ap.add_argument('--tol', type=float, default=None,
                    help='slab tolerance (default: half an MD3 quantum on that axis)')
    ap.add_argument('--project-uv', action='store_true',
                    help='LOSSY: replace the new surface UVs with a planar 0..1 projection')
    ap.add_argument('--dry-run', action='store_true', help='report, write nothing')
    ap.add_argument('--project-only', action='store_true',
                    help="LOSSY: reproject this surface's UVs 0..1 in place; carve nothing")
    a = ap.parse_args(argv)

    data = open(a.infile, 'rb').read()
    m = parse(data)
    axis = AXES[a.slab_axis]
    if not 0 <= a.surface < len(m['surfs']):
        raise SystemExit('surface %d out of range (%d surfaces)' % (a.surface, len(m['surfs'])))
    for s in m['surfs']:
        if sname(s) == a.name:
            raise SystemExit('a surface named %r already exists' % a.name)
    tol = a.tol if a.tol is not None else abs(a.scale[axis]) / 128.0

    before_surfs = len(m['surfs'])
    before_tris = sum(s['nt'] for s in m['surfs'])
    print('%s: %d surfaces, %d frames, %d triangles'
          % (a.infile, before_surfs, m['nfr'], before_tris))
    print('  splitting %d %r (%d verts, %d tris)'
          % (a.surface, sname(m['surfs'][a.surface]),
             m['surfs'][a.surface]['nv'], m['surfs'][a.surface]['nt']))
    print('  slab %s %.4f..%.4f (tol %.4f), cylinder centre %.4f %.4f radius %.4f'
          % (a.slab_axis, a.slab[0], a.slab[1], tol, a.centre[0], a.centre[1], a.radius))

    if a.project_only:
        before = m['surfs'][a.surface]['st']
        r = reproject(m, a.surface, axis, a.scale, a.offset)
        print('  reprojected surface %d %r: %d verts / %d tris, UVs now 0..1 on its own plane'
              % (a.surface, r['name'], r['nv'], r['nt']))
        if m['surfs'][a.surface]['st'] == before:
            raise SystemExit('reproject changed nothing -- wrong surface?')
        out = build(m)
        if a.dry_run:
            print('  dry run: nothing written')
            return 0
        open(a.outfile, 'wb').write(out)
        chk = parse(open(a.outfile, 'rb').read())
        cs = chk['surfs'][a.surface]
        import struct as _s
        uv = [_s.unpack_from('<2f', cs['st'], k * 8) for k in range(cs['nv'])]
        us = [q[0] for q in uv]; vs = [q[1] for q in uv]
        print('  verified: %d surfaces, surface %d u %.3f..%.3f v %.3f..%.3f'
              % (len(chk['surfs']), a.surface, min(us), max(us), min(vs), max(vs)))
        if len(chk['surfs']) != len(m['surfs']):
            raise SystemExit('surface count changed on a project-only run')
        return 0

    r = carve(m, a.surface, a.name, axis, a.slab[0], a.slab[1],
              a.centre, a.radius, tol, a.project_uv, a.scale, a.offset)
    print('  selected %d verts; %d whole triangles moved (%d selected verts were in no '
          'whole triangle)' % (r['chosen'], r['moved_tris'], r['orphans']))
    print('  source %d -> %d verts / %d -> %d tris'
          % (r['src_verts_before'], r['kept_verts'], r['src_tris_before'], r['kept_tris']))
    print('  new surface %r: %d verts / %d tris%s'
          % (a.name, r['moved_verts'], r['moved_tris'],
             '  [UVs projected]' if a.project_uv else ''))

    out = build(m)
    if a.dry_run:
        print('  dry run: nothing written')
        return 0
    open(a.outfile, 'wb').write(out)

    # ---- verify by re-reading what was actually written ----
    chk = parse(open(a.outfile, 'rb').read())
    after_tris = sum(s['nt'] for s in chk['surfs'])
    ok = True

    def check(label, got, want):
        nonlocal ok
        good = got == want
        ok = ok and good
        print('  %-34s %-10s %s' % (label, got, 'OK' if good else 'EXPECTED %s' % (want,)))

    print('verify %s' % a.outfile)
    check('surface count', len(chk['surfs']), before_surfs + 1)
    check('total triangles', after_tris, before_tris)
    check('new surface name', sname(chk['surfs'][-1]), a.name)
    check('new surface verts', chk['surfs'][-1]['nv'], r['moved_verts'])
    check('new surface tris', chk['surfs'][-1]['nt'], r['moved_tris'])
    check('frames', chk['nfr'], m['nfr'])
    check('shader bytes carried', chk['surfs'][-1]['shaders'],
          m['surfs'][a.surface]['shaders'])
    # every triangle of the new surface still has the same positions, normals and
    # (unless projected) the same UVs it had in the source
    src0 = parse(data)['surfs'][a.surface]
    new = chk['surfs'][-1]
    bad_xyz = bad_uv = 0
    srcpos = {}
    for i in range(src0['nv']):
        key = (src0['xyz'][0][i * 8:(i + 1) * 8], src0['st'][i * 8:(i + 1) * 8])
        srcpos.setdefault(key[0], set()).add(key[1])
    for i in range(new['nv']):
        vx = new['xyz'][0][i * 8:(i + 1) * 8]
        uv = new['st'][i * 8:(i + 1) * 8]
        if vx not in srcpos:
            bad_xyz += 1
        elif not a.project_uv and uv not in srcpos[vx]:
            bad_uv += 1
    check('new verts found in source', bad_xyz, 0)
    if not a.project_uv:
        check('new UVs unchanged', bad_uv, 0)
    print('  %s' % ('all checks passed' if ok else '*** CHECKS FAILED ***'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
