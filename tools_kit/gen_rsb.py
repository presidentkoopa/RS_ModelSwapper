"""RSR-BREAK: per-gun data for the break-open / revolver real VR reload (zscript/rsr/rsr_break.zs),
generated from each gun's own md3 (the hinge fitted from the set's own open frame).

  zscript/rsr/rsb_guns.zs   per gun: hinge, chambers, rounds in the hand, sprites, sounds, items
  MODELDEF.rsb.<set>        the gun's own model, re-keyed: the gun without its hinged part and
                            rounds (the gun's layer), the hinged part, each chamber's round
                            (main controller), the round in the off hand, the world casing /
                            dropped round
  models/.../rsb_vrev_loader.md3 (V+ only)  the V+ revolver's own speedloader (rev.md3 surface
                            14, one frame) split in two surfaces, loader and its six rounds, so the
                            empty loader can leave the rounds in the cylinder

Every position: cm in the weapon controller's frame, F forward, L left, U up (rgeo.py).
Rotations: right-handed about the axis; the hinge axis points so that opening is positive.

usage: gen_rsb.py <src dir>      (writes into <src dir>)
       gen_rsb.py --check <out dir>   (also renders check views of the fitted hinge)
"""

# Emit ModelSwapper's Index() -- the slot from the DONOR MODEL in hand -- instead of a
# standalone pack's, where the slot comes from the weapon's own class. Default off: the
# vanilla / plus / modern Quest packs are untouched. The ModelSwapper runner sets it.
MODELSWAPPER = False

import sys, os, json, math, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rgeo import load_md3, to_flu, pca, WS, K
from md3rel import rigid

S = 'C:/Users/Command/Desktop/Quest_Weapons_Kit/kit/kit'
V8 = S + '/team/reload_survey/_v8x/models/bd/'          # RS_BD22_Models_v8 meshes, as the pack ships them
VP = '/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/models/weapons/hud/'
RSQ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/_x/rsq/'   # the packs' own Ermac meshes (extracted)

# Ermac's off hand (MODELDEF.rsq RSQ_Hands: ammo_hand.md3 + his ammo model; Scale -1 1 1, Offset 0 -24 -10):
# which ammo_hand frame holds which of his models. Our round goes where his sits.
ERMAC = {'shell': (1, 'shot_shell.md3'), 'big': (3, 'mag_chaingun.md3'), 'cell': (5, 'mag_plasma.md3')}
HAND_STATE = {'shell': 'RsbShell', 'big': 'RsrHold', 'cell': 'RsbCell'}   # RSQ_Hands state of that pose (hands_hook.py)
PALM = np.array([-1.5, 2.0, -4.5])     # RSR.PalmGrab(): the middle of the closed hand, off-hand frame

# per gun. hinged / rounds: surface indices; open_frame: the set's own frame with the action open;
# rounds: one entry per chamber (surface, frame where that round sits in its chamber, rest fit)
GUNS = [
    dict(key='BD22/SSG', cls='SSG', set='bd', mesh=V8 + 'SSG/SSG.md3', path='models/bd/SSG', model='SSG.md3',
         skin='ssg.png', scale=(-1.0, 1.0, 1.0), off=(0.0, 0.0, -5.0), extra='\tNoInterpolation',
         ready=1, body=[1], hinged=[0], open_frame=22, chambers=[(2, 1), (3, 1)], hold='shell',
         spr='S', ready_sprite='SHTZ A',
         snd=dict(open=['SSG/Lever2', 'weapons/sshoto'], load='weapons/sshotl', close=['weapons/sshotc', 'SSG/Lever1'], chan=5),
         eject='bd', reserve='AmmoShell', loaded='SSGAmmo', per_load=1, cap=2, casing=None,
         unloaded='HasUnloadedSSG', reload_token='Reloading'),
    dict(key='BD22/GrenadeLauncher', cls='GrenadeLauncher', set='bd', mesh=V8 + 'M79/M79.md3', path='models/bd/M79',
         model='M79.md3', skin='M79.png', scale=(-1.0, 1.0, 1.0), off=(0.0, 0.0, -5.0), extra='\tNoInterpolation',
         ready=3, body=[1], hinged=[4], open_frame=15, chambers=[(3, 3)], hold='big',
         spr='G', ready_sprite='GRLN A',
         snd=dict(open=['GrenadeLauncher/Open'], load='GrenadeLauncher/Load', close=['GrenadeLauncher/Close'], chan=5),
         eject='bd', reserve='AmmoRocket', loaded='GLAmmo', per_load=1, cap=1, casing=None,
         unloaded='GLReloadToken', reload_token='Reloading'),
    dict(key='BD22/Revolver', cls='Revolver', set='bd', mesh=V8 + 'Revolver/Revolver.md3', path='models/bd/Revolver',
         model='Revolver.md3', skin='Revolver.png', scale=(-1.0, 1.0, 1.0), off=(0.0, 0.0, -5.0), extra='',
         ready=0, body=[0], hinged=[1, 2], open_frame=24, chambers=[(5, 0), (6, 0), (7, 0), (8, 0), (9, 0)], hold='shell',
         spr='R', ready_sprite='REVO A',
         snd=dict(open=['Revolver/Open'], load='Shotgun/Reload', close=['Revolver/Close'], chan=5),
         eject='bd', reserve='AmmoShell', loaded='RevolverAmmo', per_load=1, cap=6, casing=None,
         unloaded='HasUnloadedRevolver', reload_token='Reloading'),
    dict(key='V+/VR_SuperShotgun', cls='VR_SuperShotgun', set='vp', mesh=VP + 'guns/ssg.md3', path='Models/Weapons/Hud/guns',
         model='ssg.md3', skin='WPN-GUNS.png', scale=(1.35, 1.35, 1.35), off=(0.0, 0.0, 0.0), extra='',
         ready=0, body=[5], hinged=[4], open_frame=12, chambers=[(2, 0), (3, 0)], hold='shell',
         spr='T', ready_sprite='SHT2 A',
         snd=dict(open=['weapons/sshoto'], load='weapons/sshotl', close=['weapons/sshotc'], chan=1),   # CHAN_WEAPON (A_OpenShotgun2 ...)
         eject='world', reserve='VR_Shell', loaded='VR_SSGAlt', per_load=1, cap=2, casing=(2, 0),
         reserve_holds_loaded=True),
    dict(key='V+/VR_Revolver', cls='VR_Revolver', set='vp', mesh=VP + 'gats/rev.md3', path='Models/Weapons/hud/gats',
         model='rev.md3', skin='WPN-REV.png', scale=(1.35, 1.35, 1.35), off=(0.0, 0.0, 0.0), extra='',
         ready=0, body=[0], hinged=[1, 3], open_frame=25, chambers=[], loader=(10, 26), hold='cell',
         spr='V', ready_sprite='REVL A',
         snd=dict(open=['weapons/9mmclip1'], load='weapons/9mmclip2', close=['weapons/9mmslide'], chan=0),   # CHAN_AUTO
         eject='world', reserve='Clip', loaded='VR_RevLoaded', per_load=6, cap=6, casing=(4, 20), rounds6=[4, 5, 6, 7, 8, 9]),
    dict(key='V+/VR_Revolver2', cls='VR_Revolver2', set='vp', mesh=VP + 'gats/rev.md3', path='Models/Weapons/hud/gats',
         model='rev.md3', skin='WPN-REV2.png', scale=(1.35, 1.35, 1.35), off=(0.0, 0.0, 0.0), extra='',
         ready=0, body=[0], hinged=[1, 3], open_frame=25, chambers=[], loader=(10, 26), hold='cell',
         spr='W', ready_sprite='REVL A',
         snd=dict(open=['weapons/9mmclip1'], load='weapons/9mmclip2', close=['weapons/9mmslide'], chan=0),
         eject='world', reserve='Clip', loaded='VR_RevLoaded2', per_load=6, cap=6, casing=(4, 20), rounds6=[4, 5, 6, 7, 8, 9]),
]
LOADER_MD3 = 'rsb_vrev_loader.md3'


# ---------------------------------------------------------------- geometry

def flu(m, si, f, g):
    return to_flu(m[si]['xyz'][f], g['scale'], g['off'])


def surfs(m, sis, f, g):
    return np.concatenate([flu(m, i, f, g) for i in sis])


def body_fix(m, g, f):
    """R, t taking frame f onto the gun body's ready pose (the set's HUD animation tilts the gun)"""
    return rigid(surfs(m, g['body'], f, g), surfs(m, g['body'], g['ready'], g))


def rot(axis, deg):
    a = np.array(axis, float) / np.linalg.norm(axis)
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    x, y, z = a
    return np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                     [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                     [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])


def axis_angle(R):
    ang = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2))))
    ax = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    return ax / np.linalg.norm(ax), ang


def hinge(m, g):
    """axis (unit, opening positive), angle, a point on the axis: from the hinged part's motion
    between the ready frame and the set's own open frame (body-fixed)"""
    f = g['open_frame']
    R, t = body_fix(m, g, f)
    H0 = surfs(m, g['hinged'], g['ready'], g)
    H1 = surfs(m, g['hinged'], f, g) @ R.T + t
    Rh, th = rigid(H0, H1)
    a, ang = axis_angle(Rh)
    # the axis line: points p with Rh p + th = p (least squares, closest to the hinged part's rear)
    A = Rh - np.eye(3)
    p, *_ = np.linalg.lstsq(A, -th, rcond=None)
    p = p - a * np.dot(p - H0.mean(0), a)     # the point on the axis level with the part's middle
    res = np.abs(H0 @ Rh.T + th - H1).max()
    # snap tiny components (the survey's axes are axis-aligned to 0.001)
    a = np.where(np.abs(a) < 0.02, 0.0, a); a /= np.linalg.norm(a)
    return a, ang, p, res


def rigid_xform(R, t, p):
    return p @ R.T + t


def round_axis(pts):
    """a round's centre, its axis from base (rim) to tip, its length; the rim end is the wider one"""
    c, vt, s = pca(pts)
    ax = vt[0]
    tt = (pts - c) @ ax
    rad = np.linalg.norm((pts - c) - np.outer(tt, ax), axis=1)
    hi = rad[tt > 0.6 * tt.max()].max()
    lo = rad[tt < 0.6 * tt.min()].max()
    if hi > lo + 0.05:      # the + end is wider: that is the rim
        ax = -ax
        tt = -tt
    return c, ax, tt.max() - tt.min(), c + ax * tt.min(), c + ax * tt.max()


def compute(g):
    m = load_md3(g['mesh'])
    g['nsurf'] = len(m)
    g['nframes'] = m[0]['xyz'].shape[0]
    a, ang, P, res = hinge(m, g)
    g['axis'], g['open_deg'], g['hinge'], g['hinge_res'] = a, ang, P, res
    # the chambers: each round seated in the CLOSED gun; T_rest takes the round's mesh frame
    # to that pose (identity when the set shows it seated in the ready frame)
    ch = []
    for si, fr in g['chambers']:
        R, t = body_fix(m, g, fr)
        pts = flu(m, si, fr, g) @ R.T + t
        c, ax, ln, base, tip = round_axis(pts)
        ch.append(dict(surf=si, frame=fr, R0=R, t0=t, base=base, tip=tip, bore=ax, length=ln))
    g['ch'] = ch
    if g.get('loader'):
        si, fr = g['loader']
        R, t = body_fix(m, g, fr)
        # the loader sits on the OPEN cylinder in that frame: back to the closed cylinder
        Rh, th = rigid(surfs(m, g['hinged'], g['ready'], g), surfs(m, g['hinged'], fr, g) @ R.T + t)
        Ri = Rh.T
        R0 = Ri @ R
        t0 = Ri @ (t - th)
        pts = flu(m, si, fr, g) @ R0.T + t0
        comps = components(m[si])
        rounds_v = np.concatenate([c for c in comps if len(c) <= 8])
        body_v = np.concatenate([c for c in comps if len(c) > 8])
        rp = pts[rounds_v]
        bp = pts[body_v]
        # the loader's axis: the cylinder's (the rounds are parallel to it)
        _, rax, _, _, _ = round_axis(rp)
        # the rounds' tips: the furthest along the axis; the loader's knob: the body's rear
        if np.dot(bp.mean(0) - rp.mean(0), rax) > 0:
            rax = -rax                       # base (the loader body) behind the tips
        tipd = (rp @ rax).max()
        based = (bp @ rax).min()
        cen = rp.mean(0)
        tip = cen + rax * (tipd - cen @ rax)
        base = cen + rax * (based - cen @ rax)
        g['loaderinfo'] = dict(surf=si, frame=fr, R0=R0, t0=t0, base=base, tip=tip, bore=rax,
                               length=float(tipd - based), rounds_v=rounds_v, body_v=body_v)
        ch.append(dict(surf=si, frame=fr, R0=R0, t0=t0, base=base, tip=tip, bore=rax, length=float(tipd - based), loader=True))
    # world casing (the set's own spent round, thrown out as the set's own animation throws it)
    if g.get('casing'):
        si, fr = g['casing']
        c = m[si]['xyz'][fr].mean(0)
        g['casing_c'] = c
    # each round's centre in the hand: Ermac's
    hf, hm = ERMAC[g['hold']]
    em = load_md3(RSQ + hm)
    ep = np.concatenate([to_flu(s['xyz'][0], (-1, 1, 1), (0, -24, -10)) for s in em])
    ec, eax, eln, ebase, etip = round_axis(ep)
    if g['hold'] == 'shell':
        pass
    elif g['hold'] in ('big', 'cell'):
        # his magazine / cell: the long axis, top up (its top end -> our tip)
        _, vt, _ = pca(ep)
        eax = vt[0] if vt[0][2] > 0 else -vt[0]
    g['ermac'] = dict(frame=hf, c=ec, axis=eax)
    # the hand transform for chamber 0's round (every chamber's round is the same round)
    r = ch[0]
    Rh = align(r['bore'], eax)
    mid = (r['base'] + r['tip']) / 2
    if r.get('loader'):
        mid = r['base'] + r['bore'] * 2.0       # the speedloader is held by its body, rounds up
        hold_at = ec
    elif g['hold'] == 'shell':
        hold_at = ec
    else:
        hold_at = ec + eax * (0.25 * eln)       # held lower: its tip clear of the fingers
    th = hold_at - Rh @ mid
    g['hand'] = dict(R=Rh, t=th)
    # in the off-hand frame: the round's base and tip
    g['hand_base'] = Rh @ r['base'] + th
    g['hand_tip'] = Rh @ r['tip'] + th
    # the speedloader: how far its rounds go into the cylinder (its tip from the cylinder's rear face)
    if g.get('loader'):
        cyl = surfs(m, [1], g['ready'], g)
        rear = cyl[:, 0].min()
        g['loader_depth'] = float(r['tip'][0] - rear)
    push(g, m)
    return g, m


PUSH_BIN = 2.0      # cm
PUSH_NBIN = 25


def push(g, m):
    """Where the off hand can push the hinged part shut: the part's open-side face (the face
    that leads as it opens), as an angle about the hinge per distance from the axis, closed.
    Only the part in front of the hinge (within 90 deg of its middle) counts."""
    a = g['axis']
    P = g['hinge']
    # the part's surface, sampled densely (its triangles), closed, about the hinge
    pts = []
    rng = np.random.default_rng(1)
    for si in g['hinged']:
        v = flu(m, si, g['ready'], g)
        tr = m[si]['tris']
        A, B, C = v[tr[:, 0]], v[tr[:, 1]], v[tr[:, 2]]
        area = np.linalg.norm(np.cross(B - A, C - A), axis=1) / 2
        n = np.clip((area / 0.25).astype(int), 1, 200)
        for k in range(len(tr)):
            u = rng.random((n[k], 2))
            fl = u.sum(1) > 1
            u[fl] = 1 - u[fl]
            pts.append(A[k] + np.outer(u[:, 0], B[k] - A[k]) + np.outer(u[:, 1], C[k] - A[k]))
    H = np.concatenate(pts) - P
    z = H @ a
    V = H - np.outer(z, a)
    rho = np.linalg.norm(V, axis=1)
    far = V[rho > 0.6 * rho.max()]
    c = far.mean(0)
    r0 = c / np.linalg.norm(c)
    phi = np.degrees(np.arctan2(np.cross(r0, V) @ a, V @ r0))
    ok = (np.abs(phi) < 75) & (rho > 3.0)
    edge = []
    for b in range(PUSH_NBIN):
        sel = ok & (rho >= b * PUSH_BIN) & (rho < (b + 1) * PUSH_BIN)
        edge.append(float(phi[sel].max()) if sel.sum() >= 3 else -999.0)
    # gaps between covered distances: interpolated
    idx = [b for b, e in enumerate(edge) if e > -900]
    for b in range(idx[0], idx[-1] + 1):
        if edge[b] < -900:
            lo = max(x for x in idx if x < b)
            hi = min(x for x in idx if x > b)
            edge[b] = edge[lo] + (edge[hi] - edge[lo]) * (b - lo) / (hi - lo)
    z0, z1 = float(z[ok].min() - 3), float(z[ok].max() + 3)
    r0_, r1_ = float(max(3.0, rho[ok].min() - 2)), float(rho[ok].max() + 3)
    # away from where the rounds go in: a break action is pushed on its barrel(s) in front of
    # the breech (8 cm and more from the hinge); a swing-out cylinder on its front half
    if abs(a[0]) > 0.5:
        mid = float(np.dot(np.mean([c['base'] + (c['tip'] - c['base']) * 0.5 for c in g['ch']], 0) - P, a))
        rear = float(np.dot(np.mean([c['base'] for c in g['ch']], 0) - P, a))
        if rear > mid:
            z1 = min(z1, mid)
        else:
            z0 = max(z0, mid)
    else:
        r0_ = max(r0_, 8.0)
    g['push'] = dict(ref=r0, z0=z0, z1=z1, r0=r0_, r1=r1_, edge=edge)


def components(s):
    n = len(s['xyz'][0])
    par = list(range(n))

    def fd(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for a, b, c in s['tris']:
        for x, y in ((a, b), (b, c)):
            ra, rb = fd(x), fd(y)
            if ra != rb:
                par[ra] = rb
    comps = {}
    for v in range(n):
        comps.setdefault(fd(v), []).append(v)
    return [np.array(c) for c in comps.values()]


def align(u, v):
    """the rotation taking unit u onto unit v (shortest)"""
    u = np.array(u, float) / np.linalg.norm(u)
    v = np.array(v, float) / np.linalg.norm(v)
    c = np.dot(u, v)
    w = np.cross(u, v)
    sn = np.linalg.norm(w)
    if sn < 1e-9:
        if c > 0:
            return np.eye(3)
        p = np.array([0, 0, 1.0]) if abs(u[2]) < 0.9 else np.array([1.0, 0, 0])
        return rot(np.cross(u, p), 180)
    return rot(w / sn, math.degrees(math.atan2(sn, c)))


# ---------------------------------------------------------------- md3 out (the V+ speedloader, split)

def md3_cut_loader(path, si, fr, rounds_v, body_v, out):
    """a one-frame md3 of surface si of path at frame fr, in two surfaces: the loader, its rounds.
    Same vertices, UVs, normals and triangles as the set's own mesh."""
    d = open(path, 'rb').read()
    nfr, ntag, nsurf, nskin, ofr, otag, osurf, oeof = struct.unpack_from('<8i', d, 76)
    off = osurf
    for s in range(nsurf):
        flags, snfr, nsh, nv, nt, otri, osh, ost, oxyz, oend = struct.unpack_from('<10i', d, off + 68)
        if s == si:
            break
        off += oend
    name = d[off + 4:off + 68]
    shader = d[off + osh:off + osh + 68]
    tris = np.frombuffer(d, '<i4', nt * 3, off + otri).reshape(nt, 3)
    st = np.frombuffer(d, '<f4', nv * 2, off + ost).reshape(nv, 2)
    xyz = np.frombuffer(d, '<i2', snfr * nv * 4, off + oxyz).reshape(snfr, nv, 4)[fr]
    frame = d[ofr + fr * 56:ofr + fr * 56 + 56]
    parts = []
    for nm, vs in ((b'rsb_loader', body_v), (b'rsb_rounds', rounds_v)):
        vs = np.sort(vs)
        remap = -np.ones(nv, int)
        remap[vs] = np.arange(len(vs))
        keep = [t for t in tris if remap[t[0]] >= 0 and remap[t[1]] >= 0 and remap[t[2]] >= 0]
        assert all(remap[t].min() >= 0 for t in keep)
        T = np.array([remap[t] for t in keep], '<i4')
        hdr_len = 108
        b_sh = shader
        b_tri = T.tobytes()
        b_st = st[vs].astype('<f4').tobytes()
        b_xyz = xyz[vs].astype('<i2').tobytes()
        o_sh = hdr_len
        o_tri = o_sh + len(b_sh)
        o_st = o_tri + len(b_tri)
        o_xyz = o_st + len(b_st)
        o_end = o_xyz + len(b_xyz)
        h = b'IDP3' + nm.ljust(64, b'\0') + struct.pack('<10i', 0, 1, 1, len(vs), len(T), o_tri, o_sh, o_st, o_xyz, o_end)
        parts.append(h + b_sh + b_tri + b_st + b_xyz)
    body = b''.join(parts)
    o_frames = 108
    o_surf = o_frames + 56
    hdr = b'IDP3' + struct.pack('<i', 15) + b'rsb_vrev_loader'.ljust(64, b'\0') + struct.pack(
        '<9i', 0, 1, 0, 2, 0, o_frames, o_surf, o_surf, o_surf + len(body))
    data = hdr + frame + body
    open(out, 'wb').write(data)
    return len(data)


# ---------------------------------------------------------------- MODELDEF

def modeldef(g):
    clear = 'rsr_clear.png'
    out = ['', '// RS real VR reload, break-open / revolver (zscript/rsr/rsr_break.zs, tools/gen_rsb.py): %s.' % g['key'],
           '// The gun\'s own model and frames; pieces shown or hidden by a clear skin.']
    n = g['nsurf']

    def block(cls, keys, show, comment, model=None, path=None, nsurf=None, scale=None, off=None, flags='', skin=None):
        sc = scale or g['scale']
        of = off or g['off']
        b = ['', '// ' + comment, 'Model %s' % cls, '{', '\tPath "%s"' % (path or g['path']), '\tModel 0 "%s"' % (model or g['model'])]
        for si in range(nsurf if nsurf is not None else n):
            own = skin or (g['skins'][si] if g.get('skins') and model is None and si < len(g['skins']) else g['skin'])   # per-surface skins (MS 1.5 blocks)
            b.append('\tSurfaceSkin 0 %d "%s"' % (si, own if si in show else clear))
        b += ['\tScale %.4f %.4f %.4f' % tuple(sc), '\tOffset %.4f %.4f 0.0' % (of[0], of[1]), '\tZOffset %.4f' % of[2]]
        if g['extra'] and scale is None:
            b.append(g['extra'])
        if flags:
            b.append('\t' + flags)
        for spr, fr, mf in keys:
            b.append('\tFrameIndex %s %s 0 %d' % (spr, fr, mf))
        b.append('}')
        return b

    rnd = set()
    for c in g['ch']:
        if not c.get('loader'):
            rnd.add(c['surf'])
    hide_gun = set(g['hinged']) | rnd | set(g.get('rounds6', [])) | ({g['loader'][0]} if g.get('loader') else set())
    if g['key'] == 'V+/VR_SuperShotgun':
        hide_gun |= {0, 1}          # its new shells (collapsed at rest anyway)
    hide_gun |= set(g.get('hide', []))   # parts the card measures hidden at rest (card_break.py)
    sg, sp, sw = g['sprites']
    out += block(g['cls'], [(sg, 'A', g['ready'])], [i for i in range(n) if i not in hide_gun],
                 'the gun without its hinged part and rounds (the gun\'s layer while the action is open)')
    out += block('RSB_GunParts', [(sp, 'A', g['ready'])], g['hinged'], 'the hinged part (main controller), turned about the hinge')
    letters = 'BCDEFG'
    for k, c in enumerate(g['ch']):
        if c.get('loader'):
            continue
        out += block('RSB_GunParts', [(sp, letters[k], c['frame'])], [c['surf']], 'chamber %d: its round (surface %d)' % (k, c['surf']))
        if k == 0:
            out += block('RSQ_Hands', [(sp, 'H', c['frame'])], [c['surf']], 'the round in the off hand (off controller)')
            out += block('RSB_Round', [(sw, 'A', c['frame'])], [c['surf']], 'a round let go of (world)',
                         scale=g['world_scale'], off=g['world_off'], flags='USEACTORPITCH\n\tUSEACTORROLL')
    if g.get('loader'):
        lp = g['loader_path']
        # the cut loader md3: surface 0 the loader, 1 its rounds
        out += block('RSB_GunParts', [(sp, 'B', 0)], [1], 'the loader\'s rounds, in the cylinder', model=LOADER_MD3, path=lp, nsurf=2)
        out += block('RSB_GunParts', [(sp, 'I', 0)], [0, 1], 'the speedloader seated on the cylinder', model=LOADER_MD3, path=lp, nsurf=2)
        out += block('RSQ_Hands', [(sp, 'H', 0)], [0, 1], 'the speedloader in the off hand', model=LOADER_MD3, path=lp, nsurf=2)
        out += block('RSQ_Hands', [(sp, 'J', 0)], [0], 'the empty speedloader in the off hand', model=LOADER_MD3, path=lp, nsurf=2)
        out += block('RSB_Round', [(sw, 'A', 0)], [0], 'the empty speedloader let go of (world)', model=LOADER_MD3, path=lp, nsurf=2,
                     scale=g['world_scale'], off=g['loader_world_off'], flags='USEACTORPITCH\n\tUSEACTORROLL')
        out += block('RSB_Round', [(sw, 'B', 0)], [0, 1], 'the full speedloader let go of (world)', model=LOADER_MD3, path=lp, nsurf=2,
                     scale=g['world_scale'], off=g['loader_world_off'], flags='USEACTORPITCH\n\tUSEACTORROLL')
    if g.get('casing'):
        si, fr = g['casing']
        out += block('RSB_Casing', [(sw, 'C', fr)], [si], 'a spent round thrown out (world), as the set\'s own frames throw it',
                     scale=g['world_scale'], off=g['casing_off'], flags='USEACTORPITCH\n\tUSEACTORROLL')
    return out


def world_place(g, centre_md3):
    """world model block placement that puts an md3 point at the actor's origin"""
    VU = 34.0
    sc = VU * 0.01 * WS * abs(g['scale'][1])
    hud = to_flu(np.eye(3), g['scale'], (0, 0, 0)) - to_flu(np.zeros((1, 3)), g['scale'], (0, 0, 0))
    sgn = np.sign(np.diag(hud))
    ws = (sc * sgn[0], sc * sgn[1], sc * sgn[2])
    c = centre_md3
    wo = (-sc * sgn[0] * c[0], -sc * sgn[1] * c[1], -sc * sgn[2] * c[2] / 1.2)
    return ws, wo


# ---------------------------------------------------------------- zscript tables

def v3(a):
    return '(%.4f, %.4f, %.4f)' % tuple(float(x) for x in a)


def zs(guns):
    L = ['// generated by tools/gen_rsb.py (RSR-BREAK) -- do not edit by hand',
         '// Real VR reload, break-open guns and revolvers: per gun. Positions cm in the weapon',
         '// controller\'s frame (F, L, U); turns right-handed about the axis, opening positive.',
         '', 'class RSB_Guns abstract', '{']
    # WHICH GUN IS IN YOUR HANDS, and how that question is answered.
    #
    # A standalone pack's weapon IS the gun, so the slot comes from the weapon's own
    # class. ModelSwapper's does not: the weapon belongs to whatever mod is loaded and
    # only its MODEL is ours, so the slot comes from the DONOR MODEL WORN BY THAT HAND.
    # That is the whole reason its reload works on a mod nobody has written yet.
    #
    # MODELSWAPPER is default-off, so every standalone set emits what it always did.
    if MODELSWAPPER:
        L += ['\tclearscope static int Index(Weapon w)', '\t{', '\t\tif (!w)', '\t\t\treturn 0;',
              '\t\treturn SlotForDonor(DonorInHand(HandOf(w)));', '\t}', '',
              '\tclearscope static int HandOf(Weapon w)', '\t{',
              '\t\treturn 0;\t\t// the gun hand; the off hand is 1 when dual wielding lands',
              '\t}', '',
              '\t// The donor model worn by this hand, as RS_ForeignModelHandler published it.',
              '\t//',
              '\t// NOT ServiceIterator. Service.GetString is `play`; this function is `clearscope`,',
              '\t// because the pump module calls Index() from Places() / Place(), which the engine',
              '\t// reaches through Weapon.ModifyBobLayer3D -- declared `virtual ui`; and the facts',
              '\t// themselves live on a StaticEventHandler, which is `native play`. Three scopes,',
              '\t// none able to reach the others, and no Service variant bridges them.',
              '\t//',
              '\t// `struct CVar native` carries no scope qualifier at all, so FindCVar / GetString',
              '\t// are callable from every one of the three. Empty when no model is worn, which',
              '\t// SlotForDonor answers with 0 -- the stock reload -- so this is inert on a weapon',
              '\t// that has none of our models on it.',
              '\tclearscope static string DonorInHand(int hand)', '\t{',
              "\t\tlet cv = CVar.FindCVar(hand == 1 ? 'ms_donor_off' : 'ms_donor_main');",
              '\t\treturn cv ? cv.GetString() : "";', '\t}', '',
              '\tclearscope static int SlotForDonor(string donor)', '\t{',
              '\t\tif (donor.Length() == 0)', '\t\t\treturn 0;']
        for i, g in enumerate(guns, 1):
            L.append('\t\tif (donor == "%s")\treturn %d;' % (g['cls'], i))
        L += ['\t\treturn 0;', '\t}', '']
    else:
        L += ['\tclearscope static int Index(Weapon w)', '\t{', '\t\tif (!w)', '\t\t\treturn 0;', '\t\tName n = w.GetClassName();']
        for i, g in enumerate(guns, 1):
            L.append("\t\tif (n == '%s')\treturn %d;" % (g['cls'], i))
        L += ['\t\treturn 0;', '\t}', '']

    def table(name, typ, vals, fmt, comment=''):
        if comment:
            L.append('\t// ' + comment)
        L.append('\tclearscope static %s %s(int i)' % (typ, name))
        L.append('\t{')
        L.append('\t\tswitch (i)')
        L.append('\t\t{')
        for i, v in enumerate(vals, 1):
            L.append('\t\tcase %d:\treturn %s;' % (i, fmt(v)))
        L.append('\t\t}')
        dflt = {'Vector3': '(0, 0, 0)', 'double': '0', 'int': '0', 'String': '""', 'Name': "'None'", 'bool': 'false'}[typ]
        L.append('\t\treturn %s;' % dflt)
        L.append('\t}')
        L.append('')

    def table2(name, typ, vals, fmt, comment=''):
        """per gun, per chamber k"""
        if comment:
            L.append('\t// ' + comment)
        L.append('\tclearscope static %s %s(int i, int k)' % (typ, name))
        L.append('\t{')
        L.append('\t\tswitch (i * 8 + k)')
        L.append('\t\t{')
        for i, vs in enumerate(vals, 1):
            for k, v in enumerate(vs):
                L.append('\t\tcase %d:\treturn %s;' % (i * 8 + k, fmt(v)))
        L.append('\t\t}')
        dflt = {'Vector3': '(0, 0, 0)', 'double': '0', 'int': '0', 'String': '""', 'Name': "'None'", 'bool': 'false'}[typ]
        L.append('\t\treturn %s;' % dflt)
        L.append('\t}')
        L.append('')

    st = lambda s: '"%s"' % s
    nm = lambda s: "'%s'" % s
    fl = lambda x: '%.4f' % x
    it = lambda x: '%d' % x
    table('Hinge', 'Vector3', [g['hinge'] for g in guns], v3, 'a point of the hinge axis')
    table('Axis', 'Vector3', [g['axis'] for g in guns], v3, 'the hinge axis, opening positive')
    table('OpenDeg', 'double', [g['open_deg'] for g in guns], fl, 'how far it opens (the set\'s own open frame)')
    table('Chambers', 'int', [len(g['ch']) for g in guns], it, 'chambers (one: a speedloader fills the cylinder)')
    table('Loader', 'bool', [bool(g.get('loader')) for g in guns], lambda x: 'true' if x else 'false')
    # Does the EMPTIED speedloader stay in the hand? rsr_break.zs asks at the moment the last
    # chamber is filled:
    #     SetHand(mo, RSB_Guns.Loader(i) && RSB_Guns.LoaderEmptyInHand(i) ? RSB.EMPTYLOADER : RSB.FREE)
    # This generator never emitted it, so the pack it built could not compile against the
    # runtime it ships beside (rsr_break.zs:861 Unknown function LoaderEmptyInHand).
    # Default FALSE: the hand goes free, which is what every gun here did before this table
    # existed, so a gun that does not set it behaves exactly as it does today. Only a gun with
    # a speedloader is ever asked -- Loader(i) gates it.
    table('LoaderEmptyInHand', 'bool', [bool(g.get('loader_empty_in_hand')) for g in guns],
          lambda x: 'true' if x else 'false')
    table2('Base', 'Vector3', [[c['base'] for c in g['ch']] for g in guns], v3, 'a seated round\'s base (rim), closed gun')
    table2('Tip', 'Vector3', [[c['tip'] for c in g['ch']] for g in guns], v3, 'a seated round\'s tip, closed gun')
    table2('Bore', 'Vector3', [[c['bore'] for c in g['ch']] for g in guns], v3, 'into the chamber, closed gun')
    # rest transforms (rows) of each chamber's round
    table2('Rest0', 'Vector3', [[c['R0'][0] for c in g['ch']] for g in guns], v3, 'the round\'s mesh frame -> seated, closed: rows, translation')
    table2('Rest1', 'Vector3', [[c['R0'][1] for c in g['ch']] for g in guns], v3)
    table2('Rest2', 'Vector3', [[c['R0'][2] for c in g['ch']] for g in guns], v3)
    table2('RestT', 'Vector3', [[c['t0'] for c in g['ch']] for g in guns], v3)
    table('Hand0', 'Vector3', [g['hand']['R'][0] for g in guns], v3, 'seated round -> off-hand frame (Ermac\'s hold): rows, translation')
    table('Hand1', 'Vector3', [g['hand']['R'][1] for g in guns], v3)
    table('Hand2', 'Vector3', [g['hand']['R'][2] for g in guns], v3)
    table('HandT', 'Vector3', [g['hand']['t'] for g in guns], v3)
    table('HandBase', 'Vector3', [g['hand_base'] for g in guns], v3, 'the round in the off hand: base, tip (off-hand frame)')
    table('HandTip', 'Vector3', [g['hand_tip'] for g in guns], v3)
    table('HoldState', 'String', [HAND_STATE[g['hold']] for g in guns], st, 'the free hand\'s pose holding it (RSQ_Hands state)')
    table('Scale', 'Vector3', [g['scale'] for g in guns], v3, 'MODELDEF Scale, Offset x y + ZOffset of the gun\'s own block')
    table('Offset', 'Vector3', [g['off'] for g in guns], v3)
    table('SprGun', 'Name', [g['sprites'][0] for g in guns], nm)
    table('SprPart', 'Name', [g['sprites'][1] for g in guns], nm)
    table('SprWorld', 'Name', [g['sprites'][2] for g in guns], nm)
    table('ReadySprite', 'String', [g['ready_sprite'] for g in guns], st)
    table('SndOpen', 'String', [g['snd']['open'][0] for g in guns], st, 'the set\'s own sounds, on its own slot')
    table('SndOpen2', 'String', [g['snd']['open'][1] if len(g['snd']['open']) > 1 else '' for g in guns], st)
    table('SndLoad', 'String', [g['snd']['load'] for g in guns], st)
    table('SndClose', 'String', [g['snd']['close'][0] for g in guns], st)
    table('SndClose2', 'String', [g['snd']['close'][1] if len(g['snd']['close']) > 1 else '' for g in guns], st)
    table('Channel', 'int', [g['snd']['chan'] for g in guns], it)
    table('Reserve', 'String', [g['reserve'] for g in guns], st, 'the set\'s own items')
    table('Loaded', 'String', [g['loaded'] for g in guns], st)
    table('PerLoad', 'int', [g['per_load'] for g in guns], it)
    table('Cap', 'int', [g['cap'] for g in guns], it)
    table('WorldEject', 'bool', [g['eject'] == 'world' for g in guns], lambda x: 'true' if x else 'false',
          'spent rounds: the set\'s own casing actors (weapon state RSB_Eject), or the set\'s own round thrown (RSB_Casing)')
    table('Casing', 'Vector3', [g.get('casing_flu', (0, 0, 0)) for g in guns], v3, 'where the thrown round\'s centre sits in its chamber')
    table('Cls', 'Name', [g['cls'] for g in guns], nm)
    table('Unloaded', 'String', [g.get('unloaded', '') for g in guns], st, 'the set\'s "nothing in the chambers" (no casings) item')
    table('ReserveHoldsLoaded', 'bool', [bool(g.get('reserve_holds_loaded')) for g in guns], lambda x: 'true' if x else 'false',
          'the reserve still counts the loaded rounds (V+ super shotgun: firing takes them)')
    table('ReloadToken', 'String', [g.get('reload_token', '') for g in guns], st, 'what the off hand\'s reload button gives (BD22: its ACS reload token)')
    table('LoaderDepth', 'double', [g.get('loader_depth', 0) for g in guns], fl, 'the speedloader\'s rounds in the cylinder (cm)')
    table('PushRef', 'Vector3', [g['push']['ref'] for g in guns], v3, 'the off hand pushing it shut: angle 0, the hinged part\'s extent')
    table('PushZ0', 'double', [g['push']['z0'] for g in guns], fl)
    table('PushZ1', 'double', [g['push']['z1'] for g in guns], fl)
    table('PushR0', 'double', [g['push']['r0'] for g in guns], fl)
    table('PushR1', 'double', [g['push']['r1'] for g in guns], fl)
    L.append('\t// the hinged part\'s open-side face (deg about the hinge, closed) at a distance from the axis')
    L.append('\tclearscope static double PushEdge(int i, double rho)')
    L.append('\t{')
    L.append('\t\tint b = int(rho / %.1f);' % PUSH_BIN)
    L.append('\t\tif (b < 0 || b >= %d)' % PUSH_NBIN)
    L.append('\t\t\treturn -999;')
    L.append('\t\tstatic const double e[] = {')
    rows = []
    for g in guns:
        rows.append('\t\t\t' + ', '.join('%.1f' % x for x in g['push']['edge']))
    L.append(',\n'.join(rows))
    L.append('\t\t};')
    L.append('\t\treturn i >= 1 && i <= %d ? e[(i - 1) * %d + b] : -999;' % (len(guns), PUSH_NBIN))
    L.append('\t}')
    L.append('}')
    L.append('')
    L.append('// the rounds the ejector threw that were still live, held until a speedloader is home (the set')
    L.append('// tops up, so the count ends where its own reload ends)')
    for g in guns:
        if g.get('loader'):
            L.append('class RSB_Held_%s : Inventory { Default { Inventory.MaxAmount 999; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }' % g['cls'])
    L.append('')
    L.append('// every sprite the break reload shows (MODELDEF.rsb), so the engine knows them; never given')
    L.append('class RSB_Sprites : Actor')
    L.append('{')
    L.append('\tStates')
    L.append('\t{')
    L.append('\tSpawn:')
    for g in guns:
        sg, sp, sw = g['sprites']
        L.append('\t\t%s A 0;' % sg)
        L.append('\t\t%s ABCDEFGHIJ 0;' % sp)
        L.append('\t\t%s ABC 0;' % sw)
    L.append('\t\tRQHN JKL 0;')
    L.append('\t\tStop;')
    L.append('\t}')
    L.append('}')
    return L


def main(out, check=None):
    guns = []
    for g in GUNS:
        g = dict(g)
        g, m = compute(g)
        c = g['spr']
        g['sprites'] = ('RB%sG' % c, 'RB%sP' % c, 'RB%sW' % c)
        # world placement of the round let go of: chamber 0's round centre at the origin
        if g['ch'] and not g['ch'][0].get('loader'):
            si, fr = g['ch'][0]['surf'], g['ch'][0]['frame']
            g['world_scale'], g['world_off'] = world_place(g, m[si]['xyz'][fr].mean(0))
        if g.get('loader'):
            li = g['loaderinfo']
            g['loader_path'] = g['path']
            xyz = m[li['surf']]['xyz'][li['frame']]
            g['world_scale'], g['loader_world_off'] = world_place(g, xyz[li['body_v']].mean(0))
        if g.get('casing'):
            si, fr = g['casing']
            xyz = m[si]['xyz'][fr]
            _, g['casing_off'] = world_place(g, xyz.mean(0))
            if 'world_scale' not in g:
                g['world_scale'], _ = world_place(g, xyz.mean(0))
            # the thrown round's centre in its chamber, closed gun (the set's frame, body- and hinge-fixed)
            R, t = body_fix(m, g, fr)
            Rh, th = rigid(surfs(m, g['hinged'], g['ready'], g), surfs(m, g['hinged'], fr, g) @ R.T + t)
            p = flu(m, si, fr, g) @ R.T + t
            g['casing_flu'] = Rh.T @ (p.mean(0) - th)
        guns.append(g)
        print('%-22s hinge %s axis %s open %.1f deg (fit res %.2f cm) chambers %d' % (
            g['key'], np.round(g['hinge'], 2), np.round(g['axis'], 3), g['open_deg'], g['hinge_res'], len(g['ch'])))
        for k, cc in enumerate(g['ch']):
            print('    ch%d surf %d base %s tip %s bore %s len %.1f' % (k, cc['surf'], np.round(cc['base'], 2), np.round(cc['tip'], 2),
                                                                     np.round(cc['bore'], 3), cc['length']))
        print('    hand base %s tip %s' % (np.round(g['hand_base'], 2), np.round(g['hand_tip'], 2)))
        if check:
            check_views(g, m, check)
    os.makedirs(out + '/zscript/rsr', exist_ok=True)
    open(out + '/zscript/rsr/rsb_guns.zs', 'w').write('\n'.join(zs(guns)) + '\n')
    for stn in sorted({g['set'] for g in guns}):
        lines = []
        for g in guns:
            if g['set'] == stn:
                lines += modeldef(g)
        open(out + '/MODELDEF.rsb.' + stn, 'w').write('\n'.join(lines) + '\n')
    lg = [g for g in guns if g.get('loader')][0]
    li = lg['loaderinfo']
    n = md3_cut_loader(lg['mesh'], li['surf'], li['frame'], li['rounds_v'], li['body_v'], out + '/' + LOADER_MD3)
    print('loader md3', n, 'bytes')
    rep = {g['key']: dict(hinge=list(map(float, g['hinge'])), axis=list(map(float, g['axis'])), open_deg=g['open_deg'],
                          hinge_fit_res_cm=g['hinge_res'],
                          chambers=[dict(surf=c['surf'], base=list(map(float, c['base'])), tip=list(map(float, c['tip'])),
                                         bore=list(map(float, c['bore']))) for c in g['ch']]) for g in guns}
    json.dump(rep, open(out + '/rsb_geometry.json', 'w'), indent=1)


def check_views(g, m, outdir):
    """the hinged part turned by the fitted hinge vs the set's own open frame (body-fixed)"""
    from rview import view
    R, t = body_fix(m, g, g['open_frame'])
    Rh = rot(g['axis'], g['open_deg'])
    P = g['hinge']
    parts = []
    for si in g['body']:
        parts.append((flu(m, si, g['ready'], g), m[si]['tris'], (150, 150, 150)))
    for si in g['hinged']:
        p0 = flu(m, si, g['ready'], g)
        parts.append(((p0 - P) @ Rh.T + P, m[si]['tris'], (230, 140, 50)))
        parts.append((flu(m, si, g['open_frame'], g) @ R.T + t + np.array([0, 0, 0.0]), m[si]['tris'], (60, 200, 230)))
    marks = [tuple(P) + ('hinge', (255, 60, 60))]
    for k, c in enumerate(g['ch']):
        b = (c['base'] - P) @ Rh.T + P
        tp = (c['tip'] - P) @ Rh.T + P
        marks.append(tuple(b) + ('b%d' % k, (255, 255, 0)))
        marks.append(tuple(tp) + ('t%d' % k, (255, 120, 255)))
    nm = g['key'].replace('/', '_').replace('+', 'P')
    view(parts, '%s/chk_%s_side.png' % (outdir, nm), 'side', px=8, marks=marks, title=g['key'] + ' fitted hinge (orange) vs open frame (cyan)')


if __name__ == '__main__':
    if sys.argv[1] == '--check':
        os.makedirs(sys.argv[2], exist_ok=True)
        main(sys.argv[2], check=sys.argv[2])
    else:
        main(sys.argv[1])
