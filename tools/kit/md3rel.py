"""Per-frame motion of each md3 surface relative to a reference surface (the gun body).
usage: md3rel.py file.md3 [refsurf] [refframe]"""
import struct, sys
import numpy as np

def load(path):
    d = open(path, 'rb').read()
    nfr, ntag, nsurf, nskin, ofr, otag, osurf, oeof = struct.unpack_from('<8i', d, 76)
    surfs = []
    off = osurf
    for s in range(nsurf):
        name = d[off + 4:off + 68].split(b'\0')[0].decode('latin1')
        flags, snfr, nsh, nv, nt, otri, osh, ost, oxyz, oend = struct.unpack_from('<10i', d, off + 68)
        xyz = np.frombuffer(d, dtype='<i2', count=snfr * nv * 4, offset=off + oxyz).reshape(snfr, nv, 4)[:, :, :3] / 64.0
        surfs.append((name, xyz.astype(float)))
        off += oend
    return nfr, surfs

def rigid(A, B):
    """R, t with B ~ A @ R.T + t"""
    ca, cb = A.mean(0), B.mean(0)
    H = (A - ca).T @ (B - cb)
    U, S, Vt = np.linalg.svd(H)
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, cb - ca @ R.T

if __name__ == '__main__':
    path = sys.argv[1]
    ref = int(sys.argv[2]) if len(sys.argv) > 2 else None
    rf = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    nfr, surfs = load(path)
    if ref is None:
        ref = max(range(len(surfs)), key=lambda i: surfs[i][1].shape[1])
    body = surfs[ref][1]
    print('ref surface', ref, surfs[ref][0], 'ref frame', rf)
    for f in range(nfr):
        R, t = rigid(body[f], body[rf])   # maps frame f -> ref frame pose
        res = np.abs(body[f] @ R.T + t - body[rf]).max()
        row = []
        for i, (n, xyz) in enumerate(surfs):
            if i == ref:
                continue
            p = xyz[f] @ R.T + t
            dv = (p - xyz[rf]).mean(0)
            row.append('%s(%+.1f %+.1f %+.1f)' % (n[:5], dv[0], dv[1], dv[2]))
        print('f%2d bodyfit %.2f  ' % (f, res) + ' '.join(row))
