import struct, sys, json
import numpy as np

def read_md3(path):
    d = open(path,'rb').read()
    ident, ver = struct.unpack_from('<4si', d, 0)
    name = d[8:72].split(b'\0')[0].decode(errors='replace')
    flags, nframes, ntags, nsurf, nskins, ofs_frames, ofs_tags, ofs_surf, ofs_eof = struct.unpack_from('<9i', d, 72)
    frames=[]
    for i in range(nframes):
        o = ofs_frames + i*56
        mn = struct.unpack_from('<3f', d, o); mx = struct.unpack_from('<3f', d, o+12); org = struct.unpack_from('<3f', d, o+24)
        rad = struct.unpack_from('<f', d, o+36)[0]; fname = d[o+40:o+56].split(b'\0')[0].decode(errors='replace')
        frames.append(dict(min=mn,max=mx,origin=org,radius=rad,name=fname))
    tags=[]
    for i in range(nframes*ntags):
        o = ofs_tags + i*112
        tname = d[o:o+64].split(b'\0')[0].decode(errors='replace')
        tags.append(tname)
    surfs=[]
    o = ofs_surf
    for s in range(nsurf):
        sid = d[o:o+4]; sname = d[o+4:o+68].split(b'\0')[0].decode(errors='replace')
        sflags, snf, nsh, nverts, ntris, ofs_tris, ofs_sh, ofs_st, ofs_xyz, ofs_end = struct.unpack_from('<10i', d, o+68)
        shaders=[d[o+ofs_sh+i*68:o+ofs_sh+i*68+64].split(b'\0')[0].decode(errors='replace') for i in range(nsh)]
        tris = np.frombuffer(d, dtype='<i4', count=ntris*3, offset=o+ofs_tris).reshape(ntris,3)
        raw = np.frombuffer(d, dtype='<i2', count=snf*nverts*4, offset=o+ofs_xyz).reshape(snf,nverts,4)
        xyz = raw[:,:,:3].astype(np.float64)/64.0
        surfs.append(dict(name=sname, nverts=nverts, ntris=ntris, shaders=shaders, xyz=xyz, tris=tris))
        o += ofs_end
    return dict(name=name, version=ver, nframes=nframes, ntags=ntags, tags=sorted(set(tags)), frames=frames, surfs=surfs)

if __name__=='__main__':
    m = read_md3(sys.argv[1])
    print(f"model '{m['name']}' v{m['version']} frames={m['nframes']} tags={m['ntags']} {m['tags']} surfaces={len(m['surfs'])}")
    f0=m['frames'][0]; print("frame0 bbox min",np.round(f0['min'],1),"max",np.round(f0['max'],1), "name", repr(f0['name']))
    names = [f['name'] for f in m['frames']]
    print("frame names (unique, in order):", [n for i,n in enumerate(names) if i==0 or names[i-1]!=n][:40])
    tot=0
    for s in m['surfs']:
        tot+=s['nverts']
        c = s['xyz'].mean(axis=1)           # per-frame centroid
        disp = np.linalg.norm(c - c[0], axis=1)
        ext = s['xyz'][0].max(axis=0)-s['xyz'][0].min(axis=0)
        print(f"  {s['name']:<28} v={s['nverts']:5d} t={s['ntris']:5d} sh={s['shaders']}  size={np.round(ext,1)}  c0={np.round(c[0],1)}  maxmove={disp.max():.2f} @f{disp.argmax()}")
    print("total verts", tot)
