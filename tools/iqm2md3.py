"""iqm2md3.py -- bake a skinned IQM at one animation frame into an MD3 whose surfaces are split by
joint subtree, so a Quest pack can hide / move the parts a REMA card names by joint.

Skinning follows kit/tool/hands/gunview.py load_iqm (the kit's own reader, which the Modern cards
were measured with: "skinned exactly as the renderer skins it"). A triangle goes to the part whose
joint subtree owns most of its vertices' dominant weights. Meshes named in `drop` (the rig's view
arms) are left out. One frame only: the parts' motion comes from the card's dof, not the rig.

    bake(iqm_path, md3_path, frame, parts={'slide': 'j_slide', 'mag': 'j_mag1'}, drop=['v_hands.bmp'])
    -> list of surface names written, and a dict of per-part vertex counts
"""
import struct, sys
import numpy as np


def _trs(t, q, s):
    x, y, z, w = q
    n = np.sqrt(x * x + y * y + z * z + w * w) or 1.0
    x, y, z, w = x / n, y / n, z / n, w / n
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    M = np.eye(4)
    M[:3, :3] = R * np.array(s)[None, :]
    M[:3, 3] = t
    return M


def load(path, frame):
    d = open(path, 'rb').read()
    assert d[:16] == b'INTERQUAKEMODEL\0', path
    h = struct.unpack_from('<27I', d, 16)
    (ver, fsize, flags, ntext, otext, nmesh, omesh, nva, nvert, ova, ntri, otri, oadj, njoint, ojoint,
     npose, opose, nanim, oanim, nframe, nchan, oframe, obounds, ncom, ocom, next_, oext) = h
    txt = d[otext:otext + ntext]
    def s(o): return txt[o:txt.index(b'\0', o)].decode('latin1')
    arrays = {}
    for i in range(nva):
        typ, fl, fmt, size, off = struct.unpack_from('<5I', d, ova + i * 20)
        dt = {0: 'i1', 1: 'u1', 2: '<i2', 3: '<u2', 4: '<i4', 5: '<u4', 7: '<f4', 8: '<f8'}[fmt]
        arrays[typ] = np.frombuffer(d, dtype=dt, count=nvert * size, offset=off).reshape(nvert, size).astype(np.float64)
    pos = arrays[0]
    uv = arrays.get(1, np.zeros((nvert, 2)))
    nrm = arrays.get(2, np.zeros((nvert, 3)))
    tris = np.frombuffer(d, dtype='<u4', count=ntri * 3, offset=otri).reshape(ntri, 3).astype(np.int64)
    joints = []; jnames = []
    for i in range(njoint):
        name, parent = struct.unpack_from('<Ii', d, ojoint + i * 48)
        vals = struct.unpack_from('<10f', d, ojoint + i * 48 + 8)
        joints.append((parent, np.array(vals[0:3]), np.array(vals[3:7]), np.array(vals[7:10])))
        jnames.append(s(name))
    base = []
    for parent, t, q, sc in joints:
        m = _trs(t, q, sc)
        base.append(base[parent] @ m if parent >= 0 else m)
    invbase = [np.linalg.inv(m) for m in base]
    poses = []
    for i in range(npose):
        parent, mask = struct.unpack_from('<iI', d, opose + i * 88)
        off = np.array(struct.unpack_from('<10f', d, opose + i * 88 + 8))
        sc = np.array(struct.unpack_from('<10f', d, opose + i * 88 + 48))
        poses.append((parent, mask, off, sc))
    out_pos = pos.copy()
    if npose and nframe:
        frame = max(0, min(frame, nframe - 1))
        p = oframe + frame * nchan * 2
        glob = []
        for j, (parent, mask, off, sc) in enumerate(poses):
            ch = off.copy()
            for c in range(10):
                if mask & (1 << c):
                    ch[c] += struct.unpack_from('<H', d, p)[0] * sc[c]
                    p += 2
            m = _trs(ch[0:3], ch[3:7], ch[7:10])
            glob.append(glob[parent] @ m if parent >= 0 else m)
        skin = [glob[j] @ invbase[j] for j in range(len(glob))]
        idx = arrays[4].astype(int)
        w = arrays[5] / 255.0
        P = np.hstack([pos, np.ones((nvert, 1))])
        out_pos = np.zeros((nvert, 3))
        for k in range(4):
            M = np.stack([skin[i] for i in idx[:, k]])
            out_pos += w[:, k:k + 1] * np.einsum('nij,nj->ni', M, P)[:, :3]
    else:
        idx = arrays.get(4, np.zeros((nvert, 4))).astype(int); w = arrays.get(5, np.zeros((nvert, 4)))
    meshes = []
    for i in range(nmesh):
        name, mat, fv, nv, ft, nt = struct.unpack_from('<6I', d, omesh + i * 24)
        meshes.append(dict(name=s(name), mat=s(mat), fv=fv, nv=nv, ft=ft, nt=nt))
    dom = idx[np.arange(nvert), np.argmax(w, 1)] if nvert else np.zeros(0, int)
    return dict(pos=out_pos, uv=uv, nrm=nrm, tris=tris, meshes=meshes, jnames=jnames,
                jparent=[j[0] for j in joints], dom=dom, nframe=nframe)


def subtree(jnames, jparent, root):
    if root not in jnames:
        return set()
    r = jnames.index(root)
    out = {r}
    changed = True
    while changed:
        changed = False
        for j, p in enumerate(jparent):
            if p in out and j not in out:
                out.add(j); changed = True
    return out


def write_md3(path, surfaces, name='baked'):
    """surfaces: list of (name, xyz (nv,3), uv (nv,2), tris (nt,3)); one frame"""
    out = bytearray()
    out += b'IDP3' + struct.pack('<i', 15) + name.encode()[:63].ljust(64, b'\0') + struct.pack('<i', 0)
    nsurf = len(surfaces)
    hdr_end = 108
    allxyz = np.vstack([s[1] for s in surfaces]) if surfaces else np.zeros((1, 3))
    mn, mx = allxyz.min(0), allxyz.max(0)
    frame = struct.pack('<3f3f3ff16s', *mn, *mx, *((mn + mx) / 2), float(np.linalg.norm(mx - mn) / 2), b'frame0')
    out += struct.pack('<8i', 1, 0, nsurf, 0, hdr_end, hdr_end + len(frame), hdr_end + len(frame), 0)
    out += frame
    for sname, xyz, uv, tris, shname in surfaces:
        nv, nt = len(xyz), len(tris)
        shader = shname.encode()[:63].ljust(64, b'\0') + struct.pack('<i', 0)
        o_tri = 108; o_sh = o_tri + nt * 12; o_st = o_sh + 68; o_xyz = o_st + nv * 8; o_end = o_xyz + nv * 8
        out += b'IDP3' + sname.encode()[:63].ljust(64, b'\0') + struct.pack('<10i', 0, 1, 1, nv, nt, o_tri, o_sh, o_st, o_xyz, o_end)
        out += tris.astype('<i4').tobytes()
        out += shader
        out += uv.astype('<f4').tobytes()
        q = np.clip(np.round(xyz * 64.0), -32768, 32767).astype('<i2')
        rec = np.zeros((nv, 4), dtype='<i2'); rec[:, :3] = q
        out += rec.tobytes()
    struct.pack_into('<i', out, 104, len(out))
    open(path, 'wb').write(bytes(out))


def bake(iqm_path, md3_path, frame, parts, drop=(), drop_joints=(), mesh_parts=None, material=lambda m: m, extra=()):
    """extra: more (iqm_path, frame) sources (a prop's silencer / laser models) merged into the same MD3"""
    """parts: {part: root joint}; mesh_parts: {mesh/material name: part} for parts the card names by
    surface; drop: meshes left out; drop_joints: joint subtrees left out (a parked second magazine).
    Surfaces are one per (part, material), named part / part#1 ..., shader = material(name)."""
    srcs = [(iqm_path, frame)] + list(extra)
    groups = {}; dropped = 0; allj = []; nfr = 0
    for sp, sf in srcs:
        m = load(sp, sf); allj += m['jnames']; nfr = max(nfr, m['nframe'])
        _collect(m, parts, drop, drop_joints, mesh_parts, groups)
        dropped += groups.pop('__dropped__', 0)
    surfaces = []; counts = {}; seen = {}
    for (pname, mat) in sorted(groups, key=lambda k: (k[0] != 'body', k[0], k[1])):
        pos = np.vstack([g[0] for g in groups[(pname, mat)]]); uv = np.vstack([g[1] for g in groups[(pname, mat)]])
        tris = []; base = 0
        for g in groups[(pname, mat)]:
            tris.append(g[2] + base); base += len(g[0])
        tris = np.vstack(tris)
        k = seen.get(pname, 0); seen[pname] = k + 1
        sname = pname if k == 0 else '%s#%d' % (pname, k)
        surfaces.append((sname, pos, uv, tris, material(mat)))
        counts[pname] = counts.get(pname, 0) + int(len(pos))
    write_md3(md3_path, surfaces)
    return [s[0] for s in surfaces], counts, dict(dropped_tris=dropped, nframe=nfr, joints=allj)


def _collect(m, parts, drop, drop_joints, mesh_parts, groups):
    """one source's triangles into groups[(part, material)] as (pos, uv, tris) chunks"""
    part_of_joint = {}
    for pname, jroot in parts.items():
        for j in subtree(m['jnames'], m['jparent'], jroot):
            part_of_joint.setdefault(j, pname)
    gone = set()
    for jroot in drop_joints:
        gone |= subtree(m['jnames'], m['jparent'], jroot)
    vpart = np.array([part_of_joint.get(int(j), 'body') for j in m['dom']], dtype=object)
    vgone = np.array([int(j) in gone for j in m['dom']])
    local = {}; dropped = 0
    for mesh in m['meshes']:
        if mesh['name'] in drop or mesh['mat'] in drop:
            continue
        forced = (mesh_parts or {}).get(mesh['name']) or (mesh_parts or {}).get(mesh['mat'])
        t = m['tris'][mesh['ft']:mesh['ft'] + mesh['nt']]
        for tri in t:
            if vgone[tri].any():
                dropped += 1; continue
            if forced:
                p = forced
            else:
                names = [vpart[i] for i in tri]
                p = max(set(names), key=names.count)
            local.setdefault((p, mesh['mat'] or mesh['name']), []).append(tri)
    for key, tl in local.items():
        tris = np.array(tl)
        used = np.unique(tris)
        remap = {int(v): i for i, v in enumerate(used)}
        tri2 = np.vectorize(lambda v: remap[int(v)])(tris)
        groups.setdefault(key, []).append((m['pos'][used], m['uv'][used], tri2))
    groups['__dropped__'] = groups.get('__dropped__', 0) + dropped


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    parts = dict(a.split('=') for a in sys.argv[3:])
    print(bake(src, dst, 0, parts, drop=['v_hands.bmp'], drop_joints=['j_mag2'])[:2])
