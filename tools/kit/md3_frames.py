"""md3_frames.py -- append another copy's frames to an MD3, by frame name, bytes untouched.

    python -B tools_kit/md3_frames.py <dst.md3> <src.md3> [--check]

Ermac's hand.md3 travels in each Quest set with only the frames that set needs (BD22Q: 46,
Aliens: 16). Same mesh -- same vertex count, triangles, UVs and the shared frames identical to
the bit (checked: frame0/1/19/29/30/106). ModelSwapper ships one hand mesh for every set, so the
frames a set has and the shipped mesh lacks are APPENDED: every frame already in it keeps its
index, so no FrameIndex line already shipped moves. Refuses if the topology differs or if a
frame of the same name already in dst differs from src's."""
import struct, sys

HDR = '<4si64s9i'   # ident ver name flags nf ntag nsurf nskin ofsFrames ofsTags ofsSurf ofsEnd
SHDR = '<4s64siiiiiiiiii'   # ident name flags nf nshader nvert ntri ofsTri ofsShader ofsSt ofsXyz ofsEnd


def parse(p):
    d = open(p, 'rb').read()
    h = list(struct.unpack_from(HDR, d, 0))
    nf, ntag, nsurf = h[4], h[5], h[6]
    if ntag:
        sys.exit('%s: has tags -- not handled' % p)
    frames = [d[h[8] + i * 56:h[8] + (i + 1) * 56] for i in range(nf)]
    surfs, o = [], h[10]
    for _ in range(nsurf):
        s = list(struct.unpack_from(SHDR, d, o))
        nv = s[5]
        blocks = {k: d[o + s[i]:o + s[i] + n] for k, i, n in (
            ('tri', 7, s[6] * 12), ('shader', 8, s[4] * 68), ('st', 9, nv * 8))}
        xyz = [d[o + s[10] + f * nv * 8:o + s[10] + (f + 1) * nv * 8] for f in range(nf)]
        surfs.append(dict(h=s, blocks=blocks, xyz=xyz, nv=nv))
        o += s[11]
    return dict(h=h, frames=frames, surfs=surfs)


def name(fr):
    return fr[40:56].split(b'\0')[0].decode()


def build(m):
    h = list(m['h']); nf = len(m['frames'])
    h[4] = nf
    out_surf = b''
    for s in m['surfs']:
        sh = list(s['h']); sh[3] = nf
        o = struct.calcsize(SHDR)
        # the blocks in the ORIGINAL file's order (Ermac's: shaders, triangles, UVs, vertices)
        order = sorted((('tri', 7), ('shader', 8), ('st', 9)), key=lambda kv: s['h'][kv[1]])
        body = b''
        for k, i in order:
            sh[i] = o; o += len(s['blocks'][k]); body += s['blocks'][k]
        sh[10] = o; o += nf * s['nv'] * 8
        sh[11] = o
        out_surf += struct.pack(SHDR, *sh) + body + b''.join(s['xyz'])
    h[8] = struct.calcsize(HDR)
    # no tags: ofsTags is left as the file had it (Ermac's carry a stale value; nothing reads it)
    h[10] = h[8] + nf * 56
    h[11] = h[10] + len(out_surf)
    return struct.pack(HDR, *h) + b''.join(m['frames']) + out_surf


def append(dst, src, check=False):
    a, b = parse(dst), parse(src)
    if len(a['surfs']) != len(b['surfs']) or any(
            x['nv'] != y['nv'] or x['blocks']['tri'] != y['blocks']['tri'] or x['blocks']['st'] != y['blocks']['st']
            for x, y in zip(a['surfs'], b['surfs'])):
        sys.exit('%s and %s are not the same mesh' % (dst, src))
    have = {name(f): i for i, f in enumerate(a['frames'])}
    added = []
    for j, fr in enumerate(b['frames']):
        n = name(fr)
        if n in have:
            i = have[n]
            if any(x['xyz'][i] != y['xyz'][j] for x, y in zip(a['surfs'], b['surfs'])):
                sys.exit('frame %s differs between %s and %s' % (n, dst, src))
            continue
        a['frames'].append(fr)
        for x, y in zip(a['surfs'], b['surfs']):
            x['xyz'].append(y['xyz'][j])
        added.append((len(a['frames']) - 1, n))
    if check:
        return added
    if added:
        open(dst, 'wb').write(build(a))
        # read back: the old frames byte for byte, the new ones equal src's
        c, old = parse(dst), parse(src)
        assert [name(f) for f in c['frames']][:len(have)] == list(have)
        for i, n in added:
            j = [name(f) for f in old['frames']].index(n)
            assert all(x['xyz'][i] == y['xyz'][j] for x, y in zip(c['surfs'], old['surfs']))
    return added


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    for i, n in append(sys.argv[1], sys.argv[2], '--check' in sys.argv):
        print('%3d %s' % (i, n))
