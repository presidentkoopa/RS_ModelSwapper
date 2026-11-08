"""carve_by_ref.py -- split an animated MD3's surfaces into parts using a reference mesh that already
has those parts carved (REMA's *_wm.md3), when the two meshes are the same vertices (ICP residual 0).

Every vertex of the target is labelled with the part of the reference vertex it coincides with (after
the rigid transform between the two poses); each target surface is then split into one surface per
label, triangles going with the majority label of their corners, vertices duplicated where a triangle
straddles. All frames are kept; shader names are kept. Surface names become the part names.

    carve(ref_md3, target_md3, out_md3, parts) -> dict(surfaces=[(name, nv)], frames, unlabelled)
    parts: {ref surface name: part name}; reference surfaces not listed keep their own name
"""
import struct, sys
import numpy as np
from scipy.spatial import cKDTree
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genpack


def read_md3(path):
    d = open(path, 'rb').read()
    nfr, ntag, nsurf, nskin, ofr, otag, osurf, oeof = struct.unpack_from('<8i', d, 76)
    frames = d[ofr:ofr + nfr * 56]
    tags = d[otag:otag + nfr * ntag * 112]
    surfs = []; off = osurf
    for s in range(nsurf):
        name = d[off + 4:off + 68].split(b'\0')[0].decode('latin1')
        flags, snfr, nsh, nv, nt, otri, osh, ost, oxyz, oend = struct.unpack_from('<10i', d, off + 68)
        tris = np.frombuffer(d, dtype='<i4', count=nt * 3, offset=off + otri).reshape(nt, 3).copy()
        shaders = d[off + osh:off + osh + nsh * 68]
        st = np.frombuffer(d, dtype='<f4', count=nv * 2, offset=off + ost).reshape(nv, 2).copy()
        xyzn = np.frombuffer(d, dtype='<i2', count=snfr * nv * 4, offset=off + oxyz).reshape(snfr, nv, 4).copy()
        surfs.append(dict(name=name, flags=flags, tris=tris, shaders=shaders, nsh=nsh, st=st, xyzn=xyzn))
        off += oend
    return dict(nfr=nfr, ntag=ntag, frames=frames, tags=tags, surfs=surfs, name=d[8:72])


def write_md3(path, m):
    out = bytearray(b'IDP3' + struct.pack('<i', 15) + m['name'] + struct.pack('<i', 0))
    nfr = m['nfr']; nsurf = len(m['surfs'])
    hdr_end = 108
    ofr = hdr_end; otag = ofr + len(m['frames']); osurf = otag + len(m['tags'])
    out += struct.pack('<8i', nfr, m['ntag'], nsurf, 0, ofr, otag, osurf, 0)
    out += m['frames'] + m['tags']
    for s in m['surfs']:
        nv, nt = len(s['st']), len(s['tris'])
        o_tri = 108; o_sh = o_tri + nt * 12; o_st = o_sh + len(s['shaders']); o_xyz = o_st + nv * 8; o_end = o_xyz + nfr * nv * 8
        out += b'IDP3' + s['name'].encode('latin1')[:63].ljust(64, b'\0')
        out += struct.pack('<10i', s['flags'], nfr, s['nsh'], nv, nt, o_tri, o_sh, o_st, o_xyz, o_end)
        out += s['tris'].astype('<i4').tobytes() + s['shaders'] + s['st'].astype('<f4').tobytes() + s['xyzn'].astype('<i2').tobytes()
    struct.pack_into('<i', out, 104, len(out))
    open(path, 'wb').write(bytes(out))


def kabsch(A, B):
    ca, cb = A.mean(0), B.mean(0); H = (A - ca).T @ (B - cb); U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T)); Rm = Vt.T @ np.diag([1, 1, d]) @ U.T
    return Rm, cb - Rm @ ca


def carve(ref_md3, target_md3, out_md3, parts, frame=0, tol=0.05):
    nr, rs = genpack.md3_surfaces(ref_md3)
    ref_pts = np.vstack([s['xyz'][0] for s in rs])
    ref_lab = np.concatenate([[parts.get(s['name'], s['name'])] * s['nv'] for s in rs])
    tgt = read_md3(target_md3)
    tgt_pts = np.vstack([s['xyzn'][frame, :, :3].astype(float) / 64.0 for s in tgt['surfs']])
    # rigid transform ref -> target, by ICP from the centroids
    tree = cKDTree(tgt_pts); Rm = np.eye(3); t = tgt_pts.mean(0) - ref_pts.mean(0)
    for _ in range(60):
        P = ref_pts @ Rm.T + t; d, idx = tree.query(P); Rm, t = kabsch(ref_pts, tgt_pts[idx])
    rtree = cKDTree(ref_pts @ Rm.T + t)
    d, ridx = rtree.query(tgt_pts)
    unl = int((d > tol).sum())
    lab = ref_lab[ridx]
    # split each target surface by label
    new = []; base = 0
    for s in tgt['surfs']:
        nv = len(s['st']); L = lab[base:base + nv]; base += nv
        tl = [max(set(L[tri]), key=list(L[tri]).count) for tri in s['tris']]
        for name in sorted(set(tl)):
            tris = s['tris'][[i for i, x in enumerate(tl) if x == name]]
            used = np.unique(tris); remap = {int(v): i for i, v in enumerate(used)}
            new.append(dict(name=name if name not in [n['name'] for n in new] else name + '#' + str(len(new)), flags=s['flags'],
                            tris=np.vectorize(lambda v: remap[int(v)])(tris), shaders=s['shaders'], nsh=s['nsh'],
                            st=s['st'][used], xyzn=s['xyzn'][:, used, :]))
    # body first, then the parts, in a stable order
    new.sort(key=lambda s: (s['name'] != 'body', s['name']))
    tgt['surfs'] = new
    write_md3(out_md3, tgt)
    return dict(surfaces=[(s['name'], len(s['st'])) for s in new], frames=tgt['nfr'], unlabelled=unl,
                rot_deg=float(np.degrees(np.arccos(np.clip((np.trace(Rm) - 1) / 2, -1, 1)))))


if __name__ == '__main__':
    print(carve(sys.argv[1], sys.argv[2], sys.argv[3], {}))
