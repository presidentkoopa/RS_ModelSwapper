"""Lift named surfaces out of an MD3 into a model of their own, re-origined.

Why this exists
---------------
An attachment -- a scope, a laser, a suppressor, a bipod -- is usually modelled welded into one
gun and nowhere else. To make it a COMPONENT you have to be able to take it out and carry it to
other guns, and that means two things this does and `md3_carve_surface.py` does not:

  * pulling whole surfaces into a NEW file, not a new surface in the same file;
  * moving the origin, because an attachment is positioned by a mount point, and a mount point
    is only useful if it is the model's own (0,0,0).

Everything else is preserved byte for byte: positions (re-quantised only by the shift), UVs,
packed normals, shader names, surface names, frame count.

The origin
----------
--origin takes a point in the SOURCE model's own units, and the written model is shifted so
that point lands on (0,0,0). Use --at-centre-of to compute it instead, from the centroid of a
named surface -- for a scope, the ocular glass, because the eye is what the optics relate to.

MD3 positions are int16 at 1/64 unit and clamp at +-512 units, so a shift that pushes geometry
past that range is refused rather than silently wrapped.

usage:
  python -B md3_extract.py in.md3 out.md3 --surfaces leupold_scope,scope_rings,ScopeGlass \\
      [--at-centre-of ScopeGlass | --origin X Y Z] [--name Scope]
"""
import argparse
import struct


def pad(s, n):
    b = s.encode('latin-1')[:n - 1]
    return b + b'\0' * (n - len(b))


def parse(d):
    nfr, ntags, nsurf, nskin = struct.unpack_from('<4i', d, 76)
    ofs = struct.unpack_from('<i', d, 100)[0]
    frames = d[struct.unpack_from('<i', d, 92)[0]:][:nfr * 56]
    surfs = []
    for _ in range(nsurf):
        name = d[ofs + 4:ofs + 68].split(b'\0')[0].decode('latin-1')
        sfr, nsh, nv, nt = struct.unpack_from('<4i', d, ofs + 72)
        o_tri, o_sh, o_st, o_xyz, o_end = struct.unpack_from('<5i', d, ofs + 88)
        surfs.append(dict(
            name=name, nfr=sfr, nsh=nsh, nv=nv, nt=nt,
            tris=d[ofs + o_tri:ofs + o_tri + nt * 12],
            shaders=d[ofs + o_sh:ofs + o_sh + nsh * 68],
            st=d[ofs + o_st:ofs + o_st + nv * 8],
            xyz=d[ofs + o_xyz:ofs + o_xyz + sfr * nv * 8]))
        ofs += o_end
    return dict(nfr=nfr, frames=frames, surfs=surfs)


def centroid(s, frame=0):
    n = s['nv']
    acc = [0, 0, 0]
    for k in range(n):
        x, y, z = struct.unpack_from('<3h', s['xyz'], (frame * n + k) * 8)
        acc[0] += x; acc[1] += y; acc[2] += z
    return [a / 64.0 / n for a in acc]


def shift(s, d):
    q = [int(round(v * 64)) for v in d]
    out = bytearray(s['xyz'])
    for k in range(len(out) // 8):
        x, y, z = struct.unpack_from('<3h', out, k * 8)
        nx, ny, nz = x - q[0], y - q[1], z - q[2]
        for v in (nx, ny, nz):
            if not -32768 <= v <= 32767:
                raise SystemExit('shift pushes a vertex outside the MD3 range')
        struct.pack_into('<3h', out, k * 8, nx, ny, nz)
    s['xyz'] = bytes(out)


def build(m, name):
    body = b''
    for s in m['surfs']:
        o_tri = 108
        o_sh = o_tri + len(s['tris'])
        o_st = o_sh + len(s['shaders'])
        o_xyz = o_st + len(s['st'])
        o_end = o_xyz + len(s['xyz'])
        body += (b'IDP3' + pad(s['name'], 64)
                 + struct.pack('<9i', 0, s['nfr'], s['nsh'], s['nv'], s['nt'],
                               o_tri, o_sh, o_st, o_xyz)
                 + struct.pack('<i', o_end)
                 + s['tris'] + s['shaders'] + s['st'] + s['xyz'])
    hdr = 108
    o_frames = hdr
    o_tags = o_frames + len(m['frames'])
    o_surf = o_tags
    o_eof = o_surf + len(body)
    head = (b'IDP3' + struct.pack('<i', 15) + pad(name, 64)
            + struct.pack('<9i', 0, m['nfr'], 0, len(m['surfs']), 0,
                          o_frames, o_tags, o_surf, o_eof))
    return head + m['frames'] + body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('infile')
    ap.add_argument('outfile')
    ap.add_argument('--surfaces', required=True, help='comma-separated surface names, in order')
    ap.add_argument('--at-centre-of', default='', help='re-origin on this surface\'s centroid')
    ap.add_argument('--origin', type=float, nargs=3, default=None)
    ap.add_argument('--name', default='extract')
    a = ap.parse_args()

    src = parse(open(a.infile, 'rb').read())
    want = [w.strip() for w in a.surfaces.split(',') if w.strip()]
    have = {s['name']: s for s in src['surfs']}
    missing = [w for w in want if w not in have]
    if missing:
        raise SystemExit('not in %s: %s\n  present: %s'
                         % (a.infile, ', '.join(missing), ', '.join(have)))
    out = dict(nfr=src['nfr'], frames=src['frames'], surfs=[have[w] for w in want])

    org = a.origin
    if a.at_centre_of:
        if a.at_centre_of not in have:
            raise SystemExit('--at-centre-of: no surface %r' % a.at_centre_of)
        org = centroid(have[a.at_centre_of])
    if org:
        for s in out['surfs']:
            shift(s, org)

    data = build(out, a.name)
    open(a.outfile, 'wb').write(data)

    # verify by re-reading what was written, never by trusting the writer
    chk = parse(open(a.outfile, 'rb').read())
    print('%s  %d bytes' % (a.outfile, len(data)))
    print('  frames %d  surfaces %d' % (chk['nfr'], len(chk['surfs'])))
    tot = 0
    for s, w in zip(chk['surfs'], want):
        if s['name'] != w:
            raise SystemExit('surface order/name mismatch: %r != %r' % (s['name'], w))
        c = centroid(s)
        print('    %-22s %5d verts %5d tris   centroid %7.2f %7.2f %7.2f'
              % (s['name'], s['nv'], s['nt'], c[0], c[1], c[2]))
        tot += s['nt']
    srctot = sum(have[w]['nt'] for w in want)
    if tot != srctot:
        raise SystemExit('triangle count changed: %d -> %d' % (srctot, tot))
    if org:
        print('  origin moved to the source point %.3f %.3f %.3f' % tuple(org))


main()
