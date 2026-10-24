#!/usr/bin/env python3
"""obj2md3.py in.obj out.md3 skin.png [--axes zxy]
One MD3 surface per OBJ object (o ...), one frame. --axes maps OBJ (x,y,z) -> MD3 file (x,y,z):
'zxy' means file x = obj z, file y = obj x, file z = obj y (a proper rotation, bore +X, up +Z)."""
import sys, os, struct, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md3label import pad

def enc_normal(n):
    n = n / (np.linalg.norm(n) + 1e-9)
    lat = int(round(np.degrees(np.arccos(np.clip(n[2], -1, 1))) * 255 / 360)) & 255
    lng = int(round(np.degrees(np.arctan2(n[1], n[0])) * 255 / 360)) & 255
    return (lat << 8) | lng

def main():
    src, out, skin = sys.argv[1:4]
    axes = 'zxy'
    if '--axes' in sys.argv: axes = sys.argv[sys.argv.index('--axes') + 1]
    V, VT, VN = [], [], []
    objs = {}; order = []; cur = None
    for ln in open(src, errors='replace'):
        t = ln.split()
        if not t: continue
        if t[0] == 'v': V.append([float(x) for x in t[1:4]])
        elif t[0] == 'vt': VT.append([float(x) for x in t[1:3]])
        elif t[0] == 'vn': VN.append([float(x) for x in t[1:4]])
        elif t[0] == 'o': cur = t[1]; objs.setdefault(cur, []); order.append(cur)
        elif t[0] == 'f' and cur is not None:
            corners = []
            for c in t[1:]:
                p = (c.split('/') + ['', ''])[:3]
                corners.append((int(p[0]) - 1, int(p[1]) - 1 if p[1] else -1, int(p[2]) - 1 if p[2] else -1))
            for i in range(1, len(corners) - 1):
                objs[cur].append((corners[0], corners[i], corners[i + 1]))
    V = np.array(V); VT = np.array(VT) if VT else np.zeros((0, 2)); VN = np.array(VN) if VN else np.zeros((0, 3))
    idx = {'x': 0, 'y': 1, 'z': 2}
    def remap(p): return np.array([p[idx[axes[0]]], p[idx[axes[1]]], p[idx[axes[2]]]])
    surfs = []
    for name in order:
        tris = objs[name]
        if not tris: continue
        vmap = {}; verts = []; sts = []; nrm = []; tri_idx = []
        for tri in tris:
            ids = []
            for c in tri:
                if c not in vmap:
                    vmap[c] = len(verts)
                    verts.append(remap(V[c[0]])); sts.append(VT[c[1]] if c[1] >= 0 else (0, 0)); nrm.append(remap(VN[c[2]]) if c[2] >= 0 else (0, 0, 1))
                ids.append(vmap[c])
            tri_idx.append(ids)
        verts = np.array(verts); tri_idx = np.array(tri_idx, dtype='<i4')
        if len(verts) > 4096 or len(tri_idx) > 8192:
            print(f"WARNING {name}: {len(verts)} verts / {len(tri_idx)} tris exceeds MD3 limits (4096/8192)")
        xyz = np.zeros((len(verts), 4), dtype='<i2')
        xyz[:, :3] = np.clip(np.round(verts * 64.0), -32768, 32767)
        xyz[:, 3] = [enc_normal(np.array(n)) for n in nrm]
        st = np.array([[s[0], 1.0 - s[1]] for s in sts], dtype='<f4')   # OBJ v is bottom-up; MD3 is top-down
        surfs.append(dict(name=name.replace('Mag357_', ''), nverts=len(verts), ntris=len(tri_idx), nsh=1,
                          shaders=pad(skin, 64) + struct.pack('<i', 0), tris=tri_idx.tobytes(), st=st.tobytes(), xyz=xyz.tobytes(), flags=0, nframes=1))
    allv = np.vstack([np.frombuffer(s['xyz'], dtype='<i2').reshape(-1, 4)[:, :3].astype(float) / 64 for s in surfs])
    frame = struct.pack('<3f3f3ff16s', *allv.min(0), *allv.max(0), 0, 0, 0, float(np.linalg.norm(allv, axis=1).max()), pad('idle', 16))
    # write
    o = bytearray(); hdr = 108
    frames = bytearray(frame); tags = bytearray()
    body = bytearray()
    for s in surfs:
        ofs_tris = 108; b = bytearray(s['tris']); ofs_sh = ofs_tris + len(b); b += s['shaders']; ofs_st = ofs_sh + len(s['shaders']); b += s['st']; ofs_xyz = ofs_st + len(s['st']); b += s['xyz']; ofs_end = ofs_xyz + len(s['xyz'])
        body += struct.pack('<4s64s10i', b'IDP3', pad(s['name'], 64), 0, 1, 1, s['nverts'], s['ntris'], ofs_tris, ofs_sh, ofs_st, ofs_xyz, ofs_end) + b
    ofs_frames = hdr; ofs_tags = ofs_frames + len(frames); ofs_surf = ofs_tags; ofs_eof = ofs_surf + len(body)
    o += struct.pack('<4si64s9i', b'IDP3', 15, pad(out.split('/')[-1], 64), 0, 1, 0, len(surfs), 0, ofs_frames, ofs_tags, ofs_surf, ofs_eof) + frames + body
    open(out, 'wb').write(o)
    print(f"{out}: {len(surfs)} surfaces, {sum(s['nverts'] for s in surfs)} verts; bbox {allv.min(0).round(1)} {allv.max(0).round(1)}")
    for s in surfs: print(f"   {s['name']:<16} v={s['nverts']:5d} t={s['ntris']:5d}")

if __name__ == '__main__': main()
