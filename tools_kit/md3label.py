#!/usr/bin/env python3
"""
md3label.py -- read a weapon MD3, identify its parts from motion, and write:

  <out>/<name>.md3          the same model, lossless, with surfaces renamed to the vocabulary,
                            frames named by phase, and tags added (grip, mag_well, chamber,
                            eject, muzzle, support)
  <out>/<name>.card         the weapon manifest (VR_Weapon_Spec.md §5), axes in WPN = model
                            space at the idle frame
  <out>/<name>_<part>.md3   carved parts (one surface, one frame, local origin at the part's
                            seated centroid) for the parts the card lists under carve:
  <out>/<name>_sheet.png    render of the labelled result

Usage:  md3label.py in.md3 outdir name [--idle N] [--carve mag,round] [--assign surf=role,...]

The motion analysis is the one from diff.py/phase.py: the largest surface is the body, each
frame's body rigid motion is removed (Kabsch), and each other surface's residual centroid
travel is classified. --assign overrides any role the classifier gets wrong; the point is
that the owner confirms, the tool writes, and nothing is typed twice.

Vocabulary (surfaces): body slide mag round trigger hammer pump cyl bolt handle lever shell
Tags: tag_grip tag_support tag_mag_well tag_chamber tag_eject tag_muzzle
"""
import sys, struct, os, argparse
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VOCAB = ["body","slide","mag","round","trigger","hammer","pump","cyl","bolt","handle","lever","shell","case","barrel","loader","sight","stock","grip","bead"]

# ---------------------------------------------------------------- raw MD3 I/O (lossless)
def read_raw(path):
    d = open(path,'rb').read()
    hdr = struct.unpack_from('<4si64s9i', d, 0)
    (ident, ver, name, flags, nframes, ntags, nsurf, nskins, ofs_frames, ofs_tags, ofs_surf, ofs_eof) = hdr
    frames = [bytearray(d[ofs_frames+i*56: ofs_frames+(i+1)*56]) for i in range(nframes)]
    tags = [bytearray(d[ofs_tags+i*112: ofs_tags+(i+1)*112]) for i in range(nframes*ntags)]
    surfs = []
    o = ofs_surf
    for s in range(nsurf):
        sh = struct.unpack_from('<4s64s10i', d, o)
        (sid, sname, sflags, snf, nsh, nverts, ntris, ofs_tris, ofs_sh, ofs_st, ofs_xyz, ofs_end) = sh
        surfs.append(dict(
            name=sname.split(b'\0')[0].decode(errors='replace'), flags=sflags, nframes=snf,
            shaders=bytes(d[o+ofs_sh : o+ofs_sh+68*nsh]),
            tris=bytes(d[o+ofs_tris : o+ofs_tris+12*ntris]),
            st=bytes(d[o+ofs_st : o+ofs_st+8*nverts]),
            xyz=bytes(d[o+ofs_xyz : o+ofs_xyz+8*nverts*snf]),
            nverts=nverts, ntris=ntris, nsh=nsh))
        o += ofs_end
    return dict(name=name.split(b'\0')[0].decode(errors='replace'), version=ver, flags=flags,
                nframes=nframes, frames=frames, tags=tags, ntags=ntags, surfs=surfs)

def surf_xyz(s):
    raw = np.frombuffer(s['xyz'], dtype='<i2').reshape(s['nframes'], s['nverts'], 4)
    return raw[:,:,:3].astype(np.float64)/64.0

def surf_tris(s):
    return np.frombuffer(s['tris'], dtype='<i4').reshape(s['ntris'],3)

def pad(b, n):
    b = b.encode() if isinstance(b,str) else b
    return b[:n].ljust(n, b'\0')

def write_raw(m, path, frame_names, tag_list):
    """tag_list: list of (name, per-frame (origin[3], axis[3][3])) -- appended to existing tags."""
    nframes = m['nframes']
    ntags = m['ntags'] + len(tag_list)
    out = bytearray()
    hdr_size = 108
    frames = bytearray()
    for i, f in enumerate(m['frames']):
        f = bytearray(f); f[40:56] = pad(frame_names[i], 16); frames += f
    tags = bytearray()
    for i in range(nframes):
        for t in range(m['ntags']):
            tags += m['tags'][i*m['ntags']+t]
        for (tname, per) in tag_list:
            org, ax = per[i]
            tags += pad(tname, 64) + struct.pack('<3f', *org) + struct.pack('<9f', *np.asarray(ax).reshape(9))
    surfs = bytearray()
    for s in m['surfs']:
        body = bytearray()
        ofs_tris = 108
        body += s['tris']; ofs_sh = ofs_tris + len(s['tris'])
        body += s['shaders']; ofs_st = ofs_sh + len(s['shaders'])
        body += s['st']; ofs_xyz = ofs_st + len(s['st'])
        body += s['xyz']; ofs_end = ofs_xyz + len(s['xyz'])
        sh = struct.pack('<4s64s10i', b'IDP3', pad(s['name'],64), s['flags'], s['nframes'], s['nsh'],
                         s['nverts'], s['ntris'], ofs_tris, ofs_sh, ofs_st, ofs_xyz, ofs_end)
        surfs += sh + body
    ofs_frames = hdr_size
    ofs_tags = ofs_frames + len(frames)
    ofs_surf = ofs_tags + len(tags)
    ofs_eof = ofs_surf + len(surfs)
    out += struct.pack('<4si64s9i', b'IDP3', m['version'], pad(m['name'],64), m['flags'], nframes, ntags,
                       len(m['surfs']), 0, ofs_frames, ofs_tags, ofs_surf, ofs_eof)
    out += frames + tags + surfs
    open(path,'wb').write(out)

def write_single(src_surf, name, xyz_local, path):
    """One-surface, one-frame MD3 for a carved part. xyz_local: (nverts,3) floats."""
    nv = src_surf['nverts']
    raw = np.frombuffer(src_surf['xyz'], dtype='<i2').reshape(src_surf['nframes'], nv, 4)
    normals = raw[0,:,3]
    q = np.clip(np.round(xyz_local*64.0), -32768, 32767).astype('<i2')
    v = np.zeros((nv,4), dtype='<i2'); v[:,:3] = q; v[:,3] = normals
    mn, mx = xyz_local.min(0), xyz_local.max(0); rad = float(np.linalg.norm(xyz_local,axis=1).max())
    frame = struct.pack('<3f3f3ff16s', *mn, *mx, 0,0,0, rad, pad(name,16))
    s = dict(src_surf); s['name']=name; s['nframes']=1; s['xyz']=v.tobytes()
    m = dict(name=name, version=15, flags=0, nframes=1, frames=[bytearray(frame)], tags=[], ntags=0, surfs=[s])
    write_raw(m, path, [name], [])

# ---------------------------------------------------------------- analysis
def kabsch(P,Q):
    pc,qc=P.mean(0),Q.mean(0); H=(P-pc).T@(Q-qc); U,_,Vt=np.linalg.svd(H)
    d=np.sign(np.linalg.det(Vt.T@U.T)); R=Vt.T@np.diag([1,1,d])@U.T; return R, qc-R@pc

def unit(v):
    n=np.linalg.norm(v); return v/n if n>1e-9 else v

def analyse(m, idle, exclude=()):
    S=[dict(xyz=surf_xyz(s), nverts=s['nverts'], name=s['name']) for s in m['surfs']]
    # 'exclude' holds surfaces the caller has already named something other than the
    # body (see --assign in main). Without it the biggest surface wins regardless,
    # and a belt drum or a split slab ends up as the frame everything is measured in.
    body=max([i for i in range(len(S)) if i not in exclude] or list(range(len(S))),
             key=lambda i:S[i]['nverts'])
    B=S[body]['xyz']; nf=m['nframes']
    # everything in WPN = body space at the idle frame
    Rs=[kabsch(B[f], B[idle]) for f in range(nf)]   # maps frame f body -> idle body
    def to_wpn(i,f):
        R,t=Rs[f]; return S[i]['xyz'][f]@R.T + t
    rest={i: to_wpn(i,idle).mean(0) for i in range(len(S))}
    resid={}
    for i in range(len(S)):
        resid[i]=np.array([to_wpn(i,f).mean(0)-rest[i] for f in range(nf)])
    # whole-gun sway per frame (rotation angle)
    sway=[]; cant=[]
    for f in range(nf):
        R,t=Rs[f]; ang=np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1)))
        w=np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]]); w=w/(np.linalg.norm(w)+1e-9)
        shift=np.linalg.norm(B[f].mean(0)-B[idle].mean(0))
        # raise/lower: a pitch about Y with a big translation. Anything else is a baked cant.
        sway.append(ang if (abs(w[1])>0.9 and shift>0.5) else 0.0); cant.append(ang if not (abs(w[1])>0.9 and shift>0.5) else 0.0)
    return S, body, Rs, to_wpn, rest, resid, sway, cant

def classify(S, body, rest, resid, bore, down):
    """Return role per surface index. Heuristic, overridable with --assign."""
    roles={body:'body'}; info={}
    nf=len(resid[body])
    bodyW=S[body]['xyz'][0]  # only extents used
    for i in range(len(S)):
        if i==body: continue
        mag=np.linalg.norm(resid[i],axis=1); k=int(mag.argmax()); ax=unit(resid[i][k]) if mag[k]>0 else np.zeros(3)
        ext=S[i]['xyz'][0].max(0)-S[i]['xyz'][0].min(0)
        info[i]=dict(travel=float(mag.max()), axis=ax, frames=[f for f in range(nf) if mag[f]>0.5], size=ext,
                     bore_travel=float((resid[i]@bore).max()), down_travel=float((resid[i]@down).max()))
    # 1. the magazine: largest travel along 'down' with a big part
    cands=[i for i in info if info[i]['down_travel']>8 and max(info[i]['size'])>6]
    if cands:
        mi=max(cands, key=lambda i:info[i]['down_travel']); roles[mi]='mag'
    # 2. slide / bolt / pump: travel along the bore, long part
    for i in info:
        if i in roles: continue
        if info[i]['travel']>2 and abs(info[i]['axis']@bore)>0.85 and max(info[i]['size'])>8: roles[i]='slide'
    # 3. rounds: small part that moves along the bore at some point (chambering), may also ride the mag
    for i in info:
        if i in roles: continue
        if max(info[i]['size'])<6 and info[i]['bore_travel']>2: roles[i]='round'
    # 4. trigger vs hammer: both small, thin, short travel. Hammer sits in the top quarter of the body.
    top=rest[body][2]  # body centroid height
    zs=[rest[i][2] for i in info]
    for i in info:
        if i in roles: continue
        tr=info[i]['travel']; sz=info[i]['size']
        if 0.3<tr<2.5 and min(sz)<1.2:
            roles[i]='hammer' if rest[i][2]>top+ (max(sz)) else 'trigger'
        elif tr<=0.3: roles[i]='body'
        else: roles[i]='part'
    return roles, info

# ---------------------------------------------------------------- main
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('name')
    ap.add_argument('--idle', type=int, default=None, help='idle frame (default: first frame with no sway)')
    ap.add_argument('--carve', default='mag,round')
    ap.add_argument('--assign', default='', help='surf=role,... overrides')
    ap.add_argument('--archetype', default='pistol_mag', help='pistol_mag | shotgun_pump | revolver_topbreak | shotgun_break')
    ap.add_argument('--no-stabilize-check', action='store_true')
    ap.add_argument('--bore', default='1,0,0'); ap.add_argument('--down', default='0,0,-1')
    a=ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    m=read_raw(a.src)
    nf=m['nframes']
    # idle: first frame whose body pose is shared by the most frames (the sway-free pose)
    S0=[surf_xyz(s) for s in m['surfs']]; body0=max(range(len(S0)), key=lambda i:S0[i].shape[1])
    if a.idle is None:
        # the raise ends where consecutive-frame body rotation first drops under 2 degrees
        B=S0[body0]; a.idle=0
        for f in range(1,nf):
            ang=np.degrees(np.arccos(np.clip((np.trace(kabsch(B[f-1],B[f])[0])-1)/2,-1,1)))
            if ang<2.0: a.idle=f-1; break
    # Read --assign BEFORE picking the body. The body is chosen as the surface with
    # the most verts, and on the MG42 that is the belt drum -- bigger than anything
    # it hangs off. classify() then builds no motion record for the body, so
    # '--assign 2=mag' left the drum a magazine with no entry in info and the run
    # died on a KeyError. A surface the caller has explicitly called something else
    # is not a candidate for the body.
    _assign={int(kv.split('=')[0]): kv.split('=')[1] for kv in filter(None, a.assign.split(','))}
    S, body, Rs, to_wpn, rest, resid, sway, cant = analyse(
        m, a.idle, exclude={i for i, r in _assign.items() if r != 'body'})
    bore=unit(np.array([float(x) for x in a.bore.split(',')])); down=unit(np.array([float(x) for x in a.down.split(',')]))
    roles, info = classify(S, body, rest, resid, bore, down)
    roles.update(_assign)
    # unique names: body, body2 ...
    seen={}; names={}
    for i in range(len(S)):
        r=roles[i]; seen[r]=seen.get(r,0)+1; names[i]= r if seen[r]==1 else f"{r}{seen[r]}"
    for i,s in enumerate(m['surfs']): s['name']=names[i]
    # ---- phases from motion
    by_role={}
    for i in range(len(S)):
        if roles[i] not in by_role and roles[i] != 'body': by_role[roles[i]]=i
    def trav(role,f): i=by_role.get(role); return float(np.linalg.norm(resid[i][f])) if i is not None else 0.0
    fnames=[]
    def moving(role,f,thr=0.5): return trav(role,f)>thr
    if a.archetype == 'pistol_mag':
        state='raise'
        for f in range(nf):
            if sway[f]>15 and f<a.idle: fnames.append(f"raise_{f}"); continue
            if sway[f]>15 and f>a.idle: fnames.append(f"lower_{f}"); continue
            if f==a.idle: fnames.append("idle"); state='idle'; continue
            mg=moving('mag',f,1.0); sl=moving('slide',f); tr=moving('trigger',f,0.3) or moving('hammer',f,0.3); rd=moving('round',f)
            nxt=lambda role: trav(role, f+1) if f+1<nf else 0.0
            if state in ('idle','battery') and tr: state='fire'; fnames.append(f"fire_{f}"); continue
            if state=='fire':
                if sl or rd: fnames.append(f"fire_{f}"); continue
                state='idle'; fnames.append("idle"); continue
            if mg and not moving('mag',f-1,1.0): state='mag_out'; fnames.append("mag_out"); continue
            if mg: state='mag_in'; fnames.append(f"mag_in_{f}"); continue
            if sl and state in ('idle',) and nxt('mag')>1: state='slide_lock'; fnames.append("slide_lock"); continue
            if sl and state=='slide_lock': fnames.append("slide_lock"); continue
            if state=='mag_in' and sl: state='rack'; fnames.append(f"rack_{f}"); continue
            if state=='rack' and (sl or rd): fnames.append(f"rack_{f}"); continue
            if state=='rack': state='battery'; fnames.append("battery"); continue
            if sl: fnames.append(f"rack_{f}"); continue
            fnames.append("idle")
    else:
        # GENERIC: name each frame by the most significant thing happening, from the role list.
        # pump/bolt/lever moving -> pump_n ; barrel/cyl rotating -> open_n/close_n ; a case appearing
        # and moving -> eject_n ; a shell/round/loader appearing -> load_n ; trigger/hammer -> fire_n
        def vis(i,f):
            e=S[i]['xyz'][f].max(0)-S[i]['xyz'][f].min(0); return np.linalg.norm(e)>0.5
        roles_of=lambda r:[i for i in range(len(S)) if roles[i]==r]
        def any_moving(r,thr=0.5): return any(np.linalg.norm(resid[i][f])>thr and vis(i,f) for i in roles_of(r))
        def any_rot(r,thr=5):
            for i in roles_of(r):
                if not vis(i,f): continue
                R,t=kabsch(S[i]['xyz'][a.idle]@Rs[a.idle][0].T+Rs[a.idle][1], to_wpn(i,f)); ang=np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1)))
                if ang>thr: return True
            return False
        prev_open=False
        def rot_about(i,f):
            R,t=kabsch(to_wpn(i,a.idle), to_wpn(i,f)); ang=np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1)))
            w=np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]]); n=np.linalg.norm(w); return ang,(w/n if n>1e-9 else w)
        def hinge_open(f):
            # a barrel/cyl/hinge part rotated > 10 deg about an axis NOT along the bore (a cylinder
            # indexing on cock turns about the bore and is not an opening)
            for r in ('barrel','cyl','hinge'):
                for i in roles_of(r):
                    if not vis(i,f): continue
                    ang,w=rot_about(i,f)
                    if ang>10 and abs(w@bore)<0.7: return True
            return False
        for f in range(nf):
            if sway[f]>15 and f<a.idle: fnames.append(f"raise_{f}"); continue
            if sway[f]>15 and f>=nf-3: fnames.append(f"lower_{f}"); continue
            if f==a.idle: fnames.append("idle"); continue
            opened = hinge_open(f)
            if opened and not prev_open: fnames.append(f"open_{f}"); prev_open=True; continue
            if not opened and prev_open: fnames.append(f"close_{f}"); prev_open=False; continue
            if any(vis(i,f) and not vis(i,a.idle) and np.linalg.norm(resid[i][f])>1 for i in roles_of('case')): fnames.append(f"eject_{f}"); continue
            # a pump STROKE: the pump's travel changing between frames. A shell moving while the pump
            # stands still is a load. (A carrier shell rides the bolt during the stroke; that is the stroke.)
            def delta(r):
                return max([abs(np.linalg.norm(resid[i][f]) - np.linalg.norm(resid[i][f-1])) for i in roles_of(r)] + [0.0]) if f>0 else 0.0
            stroking = delta('pump')>0.3 or delta('bolt')>0.3 or delta('lever')>0.3
            if stroking: fnames.append(f"pump_{f}"); continue
            if any(vis(i,f) and not vis(i,a.idle) for i in roles_of('loader')+roles_of('round')) or any_moving('shell',1.0): fnames.append(f"load_{f}"); continue
            if any_moving('trigger',0.3) or any_moving('hammer',0.3) or any_rot('hammer',5): fnames.append(f"fire_{f}"); continue
            if opened: fnames.append(f"open_{f}"); continue
            fnames.append("idle")
    # ---- measurements in WPN
    card=[]
    card.append(f"weapon {a.name}")
    card.append(f"  archetype   {a.archetype}        # owner-confirmed")
    card.append(f"  model       {a.name}.md3   space WPN   idle_frame {a.idle}")
    card.append(f"  bore        {bore.round(3).tolist()}   down {down.round(3).tolist()}")
    card.append("  parts")
    for i in range(len(S)):
        if roles[i]=='body': continue
        d=info[i]; c=rest[i]
        e0=S[i]['xyz'][a.idle].max(0)-S[i]['xyz'][a.idle].min(0); hidden=np.linalg.norm(e0)<0.5
        # rotation relative to body at the frame of max travel
        X0=to_wpn(i,a.idle); Xk=to_wpn(i, int(np.argmax(np.linalg.norm(resid[i],axis=1))))
        R,t=kabsch(X0,Xk); ang=np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1))); w=np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]]); w=w/(np.linalg.norm(w)+1e-9)
        extra = f"  rot {ang:.0f}deg axis {np.round(w,2).tolist()}" if ang>5 else ""
        if hidden:
            vis_f=[f for f in range(nf) if np.linalg.norm(S[i]['xyz'][f].max(0)-S[i]['xyz'][f].min(0))>0.5]
            extra = f"  HIDDEN at idle; appears {vis_f[0]}..{vis_f[-1]}" if vis_f else "  HIDDEN always"
        card.append(f"    {names[i]:<8} surf {i}  rest {np.round(c,2).tolist()}  axis {np.round(d['axis'],3).tolist()}  travel {d['travel']:.2f}  frames {d['frames'][0] if d['frames'] else '-'}..{d['frames'][-1] if d['frames'] else '-'}{extra}")
    # tags
    tagdefs=[]
    def tag_per_frame(p_wpn, axis_wpn):
        per=[]
        for f in range(nf):
            R,t=Rs[f]                     # frame f -> idle; invert for idle -> frame f
            Ri=R.T; p=Ri@(p_wpn-t); ax=np.array([Ri@axis_wpn[0],Ri@axis_wpn[1],Ri@axis_wpn[2]])
            per.append((p,ax))
        return per
    I=np.eye(3)
    frame_axes=lambda fwd,up: np.array([unit(fwd), unit(np.cross(up,fwd)), unit(up)])
    # chamber: round's position when chambered (max travel along bore)
    if 'round' in by_role:
        i=by_role['round']; f=int(np.argmax(resid[i]@bore)); chamber=rest[i]+resid[i][f]
        card.append(f"  ports")
        card.append(f"    chamber   {np.round(chamber,2).tolist()}  frame {f}")
        W=np.vstack([to_wpn(body,a.idle)]); half=(W[:,1].max()-W[:,1].min())/2
        eject=chamber+np.array([0,half,0]); card.append(f"    eject     {np.round(eject,2).tolist()}  normal [0.0, 1.0, 0.0]   # chamber + half width, +Y = right; owner confirms side")
        tagdefs.append(("tag_chamber", tag_per_frame(chamber, frame_axes(bore,-down))))
        tagdefs.append(("tag_eject", tag_per_frame(eject, frame_axes(np.array([0,1,0]),-down))))
    if 'mag' in by_role:
        i=by_role['mag']; W=to_wpn(i,a.idle); mouth=W[np.argmax(W@(-down))]  # top of mag at rest
        card.append(f"    mag_well  {np.round(rest[i],2).tolist()}  mouth {np.round(mouth,2).tolist()}  axis {np.round(info[i]['axis'],3).tolist()}  travel_clear {info[i]['travel']:.2f}")
        tagdefs.append(("tag_mag_well", tag_per_frame(rest[i], frame_axes(-info[i]['axis'],bore))))
    # muzzle: body point furthest along bore among points near the bore line (top half)
    barrels=[i for i in range(len(S)) if roles[i] in ('barrel','body')]
    W=np.vstack([to_wpn(i,a.idle) for i in barrels]); top=W[W@(-down) > np.median(W@(-down))]; muz=top[np.argmax(top@bore)]
    # The grip search below looks for body vertices behind and under the trigger.
    # 'body' is a single surface, which was fine until a gun too big for the MD3
    # caps got split into bore-slabs: the Kar98's largest slab spans x 58..116 and
    # its trigger is at x 33, so the search found nothing and argmin blew up on an
    # empty array. A split body is still one body -- take every slab.
    _bodies=[i for i in range(len(S)) if roles[i]=='body'] or [body]
    W=np.vstack([to_wpn(i,a.idle) for i in _bodies])
    card.append(f"    muzzle    {np.round(muz,2).tolist()}")
    tagdefs.append(("tag_muzzle", tag_per_frame(muz, frame_axes(bore,-down))))
    # grip: body points below the trigger along 'down'
    grips=[i for i in range(len(S)) if roles[i]=='grip']
    if grips:
        # a separate grip surface: its own extent along 'down' is the grip line
        G=to_wpn(grips[0],a.idle); trg=rest[by_role['trigger']] if 'trigger' in by_role else G.mean(0)
        gl0=G[np.argmin(G@down)]; gl1=G[np.argmax(G@down)]; grip=G.mean(0)
        card.append(f"  grip        line {np.round(gl0,2).tolist()} {np.round(gl1,2).tolist()}  trigger {np.round(trg,2).tolist()}   # from the grip surface")
        tagdefs.append(("tag_grip", tag_per_frame(grip, frame_axes(bore,-down))))
    else:
        # no grip surface: the body below the trigger (or below the body's own centre)
        ref = rest[by_role['trigger']] if 'trigger' in by_role else rest[body]
        trg = ref
        # the wrist: body points within 12 units behind the trigger and below the bore line
        along=W@bore; refa=ref@bore
        sel=W[(along < refa) & (along > refa-12) & ((W@down) > (ref@down)-1.0)]
        if len(sel) < 10: sel=W[(W@down) > (ref@down)+1.0]
        if len(sel) < 10: sel = W[(W@down) > (ref@down)]
        # Three narrowing filters in a row and nothing guaranteeing a survivor --
        # the last one still returns empty on a gun whose body sits entirely above
        # its trigger, and mean/argmin of an empty array ends the run. The whole
        # body is a poor grip but an honest one, and the card says as much.
        if len(sel) < 1: sel = W
        grip=sel.mean(0)
        gl0=sel[np.argmin(sel@down)]; gl1=sel[np.argmax(sel@down)]
        card.append(f"  grip        line {np.round(gl0,2).tolist()} {np.round(gl1,2).tolist()}  trigger {np.round(trg,2).tolist()}   # centroid-based; owner's hand fit supersedes")
        tagdefs.append(("tag_grip", tag_per_frame(grip, frame_axes(bore,-down))))
    # support: pistol -> none (one-handed), placeholder under the frame ahead of the trigger
    pumps=[i for i in range(len(S)) if roles[i]=='pump']
    if pumps:
        sup=rest[pumps[0]]
        # a pump taller than it is wide below the bore line has a vertical grip: a fist on a post
        ext=np.vstack([to_wpn(i,a.idle) for i in pumps]); e=ext.max(0)-ext.min(0)
        hold = "vgrip" if (e@np.abs(down)) > 0.6*(e@np.abs(bore)) else "bar"
        card.append(f"  support     feature {hold} {np.round(sup,2).tolist()}  axis {np.round(info[pumps[0]]['axis'],3).tolist()}  travel {info[pumps[0]]['travel']:.2f}   # the pump: the support hand works it")
    else:
        sup=rest[body]+bore*4; card.append(f"  support     feature palm {np.round(sup,2).tolist()}   # one-handed gun; placeholder")
    shells=[i for i in range(len(S)) if roles[i]=='shell']
    if shells:
        i=shells[0]; k=int(np.argmin([np.linalg.norm(to_wpn(i,f).mean(0)-rest[body]) for f in range(nf)]))
        port=to_wpn(i,k).mean(0); card.append(f"    load      {np.round(port,2).tolist()}  frame {k}   # where the shell ends up: the loading port")
        tagdefs.append(("tag_load", tag_per_frame(port, frame_axes(bore,-down))))
    tagdefs.append(("tag_support", tag_per_frame(sup, frame_axes(bore,-down))))
    carve=[c for c in a.carve.split(',') if c in by_role]
    card.append(f"  carve       {' '.join(carve)}")
    card.append("  phases")
    runs=[];
    for f,n in enumerate(fnames):
        base=n.rstrip('0123456789_')
        if runs and runs[-1][0]==base: runs[-1][2]=f
        else: runs.append([base,f,f])
    for base,f0,f1 in runs: card.append(f"    {base:<12} {f0}..{f1}")
    cf=[f for f in range(nf) if cant[f]>2]
    if cf: card.append(f"  baked_cant   frames {cf[0]}..{cf[-1]} up to {max(cant):.1f} deg   # psprite-era hand sway; removed in {a.name}_stable.md3")
    card.append(f"  authoring   surfaces_named_in_source no  tags_in_source {m['ntags']}  frame_names_in_source no  verts {sum(s['nverts'] for s in m['surfs'])}")
    open(os.path.join(a.out,a.name+'.card'),'w').write('\n'.join(card)+'\n')
    # ---- write labelled md3
    write_raw(m, os.path.join(a.out,a.name+'.md3'), fnames, tagdefs)
    # ---- stabilized copy: every surface rewritten in idle-body space, so only parts move
    import copy
    ms=copy.deepcopy(m)
    for i,s_ in enumerate(ms['surfs']):
        raw=np.frombuffer(s_['xyz'],dtype='<i2').reshape(s_['nframes'],s_['nverts'],4).copy()
        for f in range(nf):
            W=to_wpn(i,f); raw[f,:,:3]=np.clip(np.round(W*64.0),-32768,32767).astype('<i2')
        s_['xyz']=raw.tobytes()
        # frame bboxes
    for f in range(nf):
        allv=np.vstack([to_wpn(i,f) for i in range(len(S))]); fr=bytearray(ms['frames'][f])
        fr[0:12]=struct.pack('<3f',*allv.min(0)); fr[12:24]=struct.pack('<3f',*allv.max(0)); fr[24:36]=struct.pack('<3f',0,0,0)
        fr[36:40]=struct.pack('<f',float(np.linalg.norm(allv,axis=1).max())); ms['frames'][f]=fr
    stable_tags=[(tn,[(per[a.idle][0],per[a.idle][1])]*nf) for tn,per in tagdefs]
    write_raw(ms, os.path.join(a.out,a.name+'_stable.md3'), fnames, stable_tags)
    # ---- carves
    for role in carve:
        i=by_role[role]; W=to_wpn(i,a.idle); c=W.mean(0)
        write_single(m['surfs'][i], role, W-c, os.path.join(a.out,f"{a.name}_{role}.md3"))
        card.append(f"  carved      {role}  seat_origin {np.round(c,2).tolist()}  file {a.name}_{role}.md3")
    open(os.path.join(a.out,a.name+'.card'),'w').write('\n'.join(card)+'\n')
    print('\n'.join(card))
    print("\nframe names:", fnames)
    print("tags:", [t for t,_ in tagdefs])

if __name__=='__main__': main()
