"""Write a flat one-frame MD3 quad: a billboard for a HUD layer.

Why this exists
---------------
A psprite layer only reaches Weapon.ModifyBobLayer3D -- the hook that places a layer in the
weapon controller's 3D frame -- if the layer resolves to a MODEL. The engine splits the two
paths on exactly that: PreparePlayerSprites3D does `if (!smf) continue;` and
PreparePlayerSprites2D does `if (smf) continue;` (hw_weapon.cpp:927 and :842). A model-less
layer gets only ModifyBobLayer, a Vector2 SCREEN-space bob, which is screen-locked.

So anything that has to sit at a measured point in the hand's frame -- a collimated reticle, a
muzzle glow, a laser dot, a floating readout -- cannot be a plain sprite. It has to be a mesh,
and the smallest honest mesh is two triangles.

Units: one model unit is one centimetre for a block drawn at Scale -1 1 1, because the hand
transform scales by 0.01 and the controller frame is metres. --size is therefore the quad's
width in centimetres.

The quad lies in the model's X/Z plane facing -Y, centred on its own origin, UV 0..1 with
(0,0) at the top left, so a square texture lands square.

usage:
  python -B md3_quad.py out.md3 --skin RQRTA0.png [--size 1.2] [--name reticle]
"""
import argparse
import struct


def pad(s, n):
    b = s.encode('latin-1')[:n - 1]
    return b + b'\0' * (n - len(b))


def enc_normal(nx, ny, nz):
    import math
    lat = int(round(math.degrees(math.acos(max(-1.0, min(1.0, nz)))) * 255 / 360)) & 255
    lng = int(round(math.degrees(math.atan2(ny, nx)) * 255 / 360)) & 255
    return (lat << 8) | lng


def quad(out, skin, size, name):
    h = size / 2.0
    # x right, z up, facing -y; wound so the front face is the one you see from -y
    pos = [(-h, 0.0, -h), (h, 0.0, -h), (h, 0.0, h), (-h, 0.0, h)]
    st = [(0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]
    tris = [(0, 1, 2), (0, 2, 3)]
    n = enc_normal(0.0, -1.0, 0.0)

    tri_b = b''.join(struct.pack('<3i', *t) for t in tris)
    st_b = b''.join(struct.pack('<2f', u, v) for u, v in st)
    xyz_b = b''.join(struct.pack('<3hH', int(round(x * 64)), int(round(y * 64)),
                                 int(round(z * 64)), n) for x, y, z in pos)
    sh_b = pad(skin, 64) + struct.pack('<i', 0)

    ofs_tri = 108
    ofs_sh = ofs_tri + len(tri_b)
    ofs_st = ofs_sh + len(sh_b)
    ofs_xyz = ofs_st + len(st_b)
    ofs_end = ofs_xyz + len(xyz_b)
    surf = (struct.pack('<4s', b'IDP3') + pad(name, 64)
            + struct.pack('<9i', 0, 1, 1, len(pos), len(tris),
                          ofs_tri, ofs_sh, ofs_st, ofs_xyz)
            + struct.pack('<i', ofs_end)
            + tri_b + sh_b + st_b + xyz_b)

    radius = (h * h * 2) ** 0.5
    frame = struct.pack('<3f3f3ff16s', -h, 0.0, -h, h, 0.0, h, 0.0, 0.0, 0.0,
                        radius, pad('idle', 16))
    hdr = 108
    ofs_frames = hdr
    ofs_tags = ofs_frames + len(frame)
    ofs_surf = ofs_tags
    ofs_eof = ofs_surf + len(surf)
    head = (struct.pack('<4si', b'IDP3', 15) + pad(out.split('/')[-1].split('\\')[-1], 64)
            + struct.pack('<9i', 0, 1, 0, 1, 0, ofs_frames, ofs_tags, ofs_surf, ofs_eof))
    data = head + frame + surf
    open(out, 'wb').write(data)
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outfile')
    ap.add_argument('--skin', required=True, help='shader name written into the surface')
    ap.add_argument('--size', type=float, default=1.2, help='width in cm (default 1.2)')
    ap.add_argument('--name', default='quad', help='surface name')
    a = ap.parse_args()
    data = quad(a.outfile, a.skin, a.size, a.name)

    # verify by re-reading what was written, not by trusting the writer
    nf, nt, ns, nsk = struct.unpack_from('<4i', data, 76)
    off = struct.unpack_from('<i', data, 100)[0]
    sname = data[off + 4:off + 68].split(b'\0')[0].decode('latin-1')
    nv, ntri = struct.unpack_from('<2i', data, off + 80)
    sh = data[off + struct.unpack_from('<i', data, off + 92)[0]:][:64].split(b'\0')[0].decode('latin-1')
    ost = struct.unpack_from('<i', data, off + 96)[0]
    uv = [struct.unpack_from('<2f', data, off + ost + k * 8) for k in range(nv)]
    print('%s  %d bytes' % (a.outfile, len(data)))
    print('  frames %d  surfaces %d  -> surface %r  %d verts / %d tris  shader %r'
          % (nf, ns, sname, nv, ntri, sh))
    print('  uv %s' % (uv,))
    print('  %.2f cm across, in the model X/Z plane facing -Y' % a.size)
    assert (nf, ns, nv, ntri) == (1, 1, 4, 2), 'the written file is not a one-frame quad'


main()
