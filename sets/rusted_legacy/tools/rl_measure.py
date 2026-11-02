"""rl_measure.py -- measure a Rusted Legacy gun where Ermac's game DRAWS it, and render it.

Everything is read from his files; nothing is typed in by hand except which of his own
surface names is which part (his names are already the parts: 'slide', 'shotgun_pump' ...).

  * the block: the gun's first non-PBR "with both hands" MODELDEF block (falls back to
    "with hand"). Its //Ready FrameIndex row gives the frame of every model slot at rest.
  * the frame: controller frame, cm, F forward / L left / U up -- the kit's own chain
    (hudrender.to_local -> gunview.to_fl, vr_weaponScale 1.02), Scale/Offset from the block.
  * moving parts: each surface's travel against the gun body, over every gun-mesh frame the
    block uses, with the body's own rigid motion removed (Kabsch).
  * the reload piece (model slot 1): seated where the Ready row draws it; its approach is the
    last position it holds, in the reload state's own frame order, before it reaches the seat.
  * grip / support: gripmeasure.measure() on the hand.md3 / hand2.md3 pose the Ready row uses --
    the cylinder Ermac's own hand closes on.
  * phases: which mesh frames each of his weapon states plays (from the zscript).

usage: RSQ_RL=<his dev build> python3 sets/rusted_legacy/tools/rl_measure.py <gun> [...]   (gun keys in GUNS)
writes sets/rusted_legacy/cards/<gun>/rl_<gun>.card / .json / .png (RL_OUT overrides the set folder)
"""
import os, re, sys, json
import numpy as np
from PIL import Image, ImageDraw

# Depot tools only: tools/depot.py, tools/hqt (md3label, gripmeasure), the fitter core (gunview, hudrender)
TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools')
sys.path.insert(0, os.path.abspath(TOOLS))
import depot
sys.path.insert(0, os.path.join(depot.TOOLS, 'hqt'))
sys.path.insert(0, depot.HANDS_TOOL)
import gunview, hudrender, gripmeasure, md3label

# his dev build stays outside the repo: RSQ_RL (or RSQ_ERMAC's parent)
MOD = depot.need(depot.RL, 'RSQ_RL (Ermac\'s Rusted Legacy dev build)') + os.sep
if not depot.ERMAC:
    depot.ERMAC = os.path.join(MOD, 'models')          # gripmeasure reads his hands from here
OUT = os.environ.get('RL_OUT', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PL = dict(scale=[-1.0, 1.0, 1.0], off=[0.0, -24.0, -10.0])

# role colours for the renders
COL = dict(body=(150, 155, 170), trigger=(230, 80, 80), hammer=(240, 140, 60), slide=(90, 170, 240),
           pump=(90, 170, 240), bolt=(200, 120, 240), lever=(200, 120, 240), barrel=(110, 210, 200),
           handle=(240, 220, 90), valve=(240, 220, 90), cyl=(110, 210, 200), case=(180, 180, 120),
           sight=(170, 170, 170), meter=(120, 255, 120), blade=(110, 210, 200), chamber=(200, 120, 240),
           deco=(170, 130, 130), piece=(255, 150, 40), ghost=(150, 100, 60),
           hand=(225, 170, 135), hand2=(120, 200, 140))

GUNS = {
    'pistol': dict(mdef='pistol.txt', zs='pistol.txt', archetype='pistol_mag', piece='mag',
                   roles=dict(hammer='hammer', trigger='trigger', slide='slide', berreta_body='body')),
    'shotgun': dict(mdef='shotgun.txt', zs='shotgun.txt', archetype='shotgun_pump', piece='shell',
                    roles=dict(shotgun='body', shotgun_trigger='trigger', shotgun_pump='pump', shotgun_breach='bolt')),
    'ssg': dict(mdef='ssg.txt', zs='ssg.txt', archetype='shotgun_break', piece='round', carrier='ssg_barrel',
                roles=dict(ssg_stock='body', ssg_stock_base='body', ssg_trigger='trigger', ssg_hammer_left='hammer',
                           ssg_hammer_right='hammer', ssg_barrel='barrel', ssg_barrel_base='barrel')),
    'chaingun': dict(mdef='chaingun.txt', zs='chaingun.txt', archetype='chaingun', piece='mag',
                     roles=dict(cg_body='body', cg_barrel='barrel', cg_barrel_ring1='barrel', cg_barrel_ring2='barrel',
                                cg_barrel_ring3='barrel', cg_trigger='trigger')),
    'plasma': dict(mdef='plasmarifle.txt', zs='plasmarifle.txt', archetype='energy', piece='mag',
                   roles=dict(plasma_rifle='body', plasma_rifle_trigger='trigger', plasma_rifle_pipes='deco',
                              plasma_rifle_heatsink='deco')),
    'rocket': dict(mdef='rocketlauncher.txt', zs='rocketlauncher.txt', archetype='launcher', piece='round',
                   roles=dict(rocketlauncher='body', rl_trigger='trigger')),
    'hellshotgun': dict(mdef='hellshotgun.txt', zs='hellshotgun.txt', archetype='shotgun_lever', piece='shell',
                        roles=dict(hellshotgun='body', hellteeth1='deco', hellhorn1='deco', hellshotgun_chamber='lever')),
    'incinerator': dict(mdef='incinerator.txt', zs='incinerator.txt', archetype='flamethrower', piece='canister',
                        roles={'flamethrower': 'body', 'flamethrower_trigger': 'trigger', 'flamethrower_bolts': 'deco',
                               'flamethrower.nozzle': 'barrel', 'flamethrower_lever': 'lever', 'flamethrower_valve': 'valve'}),
    'bfg': dict(mdef='bfg9000.txt', zs='bfg9000.txt', archetype='energy_pod', piece='pod', seat_at=11, bore=[1, 0, 0], muzzle_ring=dict(depth=3.0, umin=11.0),
                roles=dict(bfg='body', bfg_case='lever', bfg_trigger='trigger', bfg_meter='meter')),
    'heatwave': dict(mdef='heatwave.txt', zs='heatwave.txt', archetype='energy_cell', piece='cell',
                     roles=dict(gauss_base='body', blade_right='blade', blade_left='blade', gauss_trigger='trigger')),
    'chainsaw': dict(mdef='chainsaw.txt', zs='chainsaw.txt', archetype='melee', piece=None,
                     roles=dict(chainsaw='body', saw_handle='handle')),
}


# ------------------------------------------------------------------ MODELDEF
def blocks(path):
    """[(comment above, body text)] for every Model block"""
    s = open(path, errors='replace').read()
    out = []
    for m in re.finditer(r'((?://[^\n]*\n\s*)*)Model\s+\w+\s*\{(.*?)\n\}', s, re.S):
        out.append((m.group(1).strip().lower(), m.group(2)))
    return out


TMODEL = {}     # (sprite, frame) -> {slot: model path in effect at that FrameIndex line}


def parse_block(text):
    TMODEL.clear()
    path, models, fidx, ready = None, {}, [], None
    after_ready = False
    for line in text.splitlines():
        t = line.split('//')[0].strip()
        if '//' in line and 'ready' in line.split('//', 1)[1].lower():
            after_ready = True
        if t.lower().startswith('path'):
            path = t.split('"')[1]
        mm = re.match(r'Model\s+(\d+)\s+"([^"]+)"', t, re.I)
        if mm:
            models[int(mm.group(1))] = path + '/' + mm.group(2)
        for spr, fr, mi, mf in re.findall(r'FrameIndex\s+(\S+)\s+(\S)\s+(\d+)\s+(\d+)', t, re.I):
            fidx.append((spr.upper(), fr.upper(), int(mi), int(mf)))
            TMODEL.setdefault((spr.upper(), fr.upper()), {})[int(mi)] = models.get(int(mi))
            if after_ready and ready is None:
                ready = (spr.upper(), fr.upper())
    table = {}
    for spr, fr, mi, mf in fidx:
        table.setdefault((spr, fr), {})[mi] = mf
    # the model set as the Ready row sees it
    if ready:
        models = dict(models); models.update({k: v for k, v in TMODEL.get(ready, {}).items() if v})
    return models, table, ready, fidx


def pick_block(mdef):
    """the gun's first non-PBR 'with both hands' group (else 'with hand'): the headed block and
    every un-headed block after it (his reload rows often live in a second block)"""
    bl = blocks(MOD + 'modeldefs/weapons/' + mdef)
    for want in ('with both hands', 'with hand'):
        for k, (com, body) in enumerate(bl):
            last = com.splitlines()[-1] if com else ''
            if want in last and 'pbr' not in last:
                text = body
                for com2, body2 in bl[k + 1:]:
                    if com2.strip():
                        break
                    text += '\n' + body2
                return last, parse_block(text)
    return 'first block', parse_block(bl[0][1])


# ------------------------------------------------------------------ states (zscript)
def main_sprite(zs):
    """the 4-letter sprite the gun's Ready: state draws (his A_SetAltModel swaps it for the
    hand / PBR variants at run time, keeping the frame letter)"""
    s = open(MOD + 'zscript/weapons/' + zs, errors='replace').read()
    m = re.search(r'^\s*Ready:\s*$(.*?)^\s*\w+:\s*$', s, re.M | re.S)
    for sp in re.findall(r'^\s*([A-Z0-9]{4})\s+[A-Z\[\]#]+\s+-?\d', m.group(1), re.M):
        if sp != 'TNT1':
            return sp


def alt_sprites(zs, two_hands):
    """base sprite -> the sprite his A_SetAltModel swaps in for the block we read
    (2nd argument = 'with both hands'; the base sprite itself is 'with hand')"""
    s = open(MOD + 'zscript/weapons/' + zs, errors='replace').read()
    out = {}
    for sp, args in re.findall(r'^\s*([A-Z0-9]{4})\s+\S+\s+-?\d+\s+A_SetAltModel\(([^)]*)\)', s, re.M):
        a = re.findall(r'"([^"]+)"', args)
        if two_hands and len(a) > 1 and a[1] != '----':
            out[sp] = a[1]
    return out


def state_frames(zs, sprites=None):
    """{label: [(sprite, frame letter), in play order]} for every 4-letter weapon sprite"""
    s = open(MOD + 'zscript/weapons/' + zs, errors='replace').read()
    out, cur, cursp = {}, None, None
    for line in s.splitlines():
        t = line.split('//')[0].strip()
        m = re.match(r'^([A-Za-z_]\w*):\s*$', t)
        if m:
            cur = m.group(1); out.setdefault(cur, []); continue
        m = re.match(r'^(####|[A-Z0-9]{4})\s+([A-Z\[\]\\#]+)\s+-?\d', t)
        if m and cur:
            sp, frs = m.group(1), m.group(2)
            if sp != '####':
                cursp = sp
            sp = cursp
            if sp and sp != 'TNT1' and (sprites is None or sp in sprites):
                for c in frs:
                    if c != '#':
                        out[cur].append((sp, c))
    return {k: v for k, v in out.items() if v}


# ------------------------------------------------------------------ geometry
def md3(path):
    return md3label.read_raw(MOD + path)


def to_flu(xyz):
    return gunview.to_fl(hudrender.to_local(xyz, PL))


def affine():
    """model space -> FLU is affine: A v + b"""
    b = to_flu(np.zeros((1, 3)))[0]
    A = np.stack([to_flu(np.eye(3)[i:i + 1])[0] - b for i in range(3)], 1)
    return A, b


A_M, B_M = affine()
A_INV = np.linalg.inv(A_M)
def to_model(p):
    return A_INV @ (np.asarray(p) - B_M)


def kabsch(P, Q):
    pc, qc = P.mean(0), Q.mean(0)
    H = (P - pc).T @ (Q - qc)
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    return R, qc - R @ pc


def visible(x):
    return np.linalg.norm(x.max(0) - x.min(0)) > 0.05


def final_stroke(path, seat):
    """walking back from the seat: the first point >= 2 cm out, then on while the piece keeps
    coming along the same line (within 25 degrees) -- the straight last run into the seat"""
    back = [t for t in reversed(path) if np.linalg.norm(t[3] - seat) >= 0.3]
    if not back:
        return None
    k = next((i for i, t in enumerate(back) if np.linalg.norm(t[3] - seat) >= 2.0), len(back) - 1)
    best = back[k]; d0 = seat - best[3]; d0 /= np.linalg.norm(d0)
    for t in back[k + 1:]:
        d = seat - t[3]; n = np.linalg.norm(d)
        if n <= np.linalg.norm(seat - best[3]) or (d / n) @ d0 < np.cos(np.radians(25)):
            break
        best = t
    return best


ALT = {}


def r2(v):
    return [round(float(x), 2) for x in v]


# ------------------------------------------------------------------ measure one gun
def measure(key):
    g = GUNS[key]
    which, (models, table, ready, fidx) = pick_block(g['mdef'])
    global ALT
    ALT = alt_sprites(g['zs'], 'both' in which)
    rf = table[ready]
    gun = md3(models[0])
    gnf = gun['nframes']
    gidle = rf[0]
    S = [md3label.surf_xyz(s) for s in gun['surfs']]
    names = [s['name'] for s in gun['surfs']]
    roles = [g['roles'].get(n, 'deco') for n in names]
    body = max((i for i in range(len(S)) if roles[i] == 'body'), key=lambda i: S[i].shape[1])
    used = sorted({mf for (_, _), d in table.items() for mi, mf in d.items() if mi == 0 and mf < gnf})

    # parts: travel against the body, body rigid motion removed, in FLU at the idle pose
    parts = []
    for i in range(len(S)):
        if i == body:
            continue
        c0 = to_flu(S[i][gidle]).mean(0)
        best, bf, R_at = 0.0, gidle, None
        trav = {}
        for f in used:
            R, t = kabsch(S[body][f], S[body][gidle])           # frame f -> idle body space
            X = S[i][f] @ R.T + t
            if not visible(S[i][f]):
                continue
            c = to_flu(X).mean(0)
            d = np.linalg.norm(c - c0)
            trav[f] = d
            Rp, _ = kabsch(to_flu(S[i][gidle]), to_flu(X))
            ang = np.degrees(np.arccos(np.clip((np.trace(Rp) - 1) / 2, -1, 1)))
            if d + ang * 0.05 > best:
                best, bf, R_at = d + ang * 0.05, f, (c - c0, ang, Rp)
        mv = [f for f, d in trav.items() if d > 0.1]
        rec = dict(surf=i, name=names[i], role=roles[i], rest=r2(c0), verts=int(S[i].shape[1]))
        if R_at is not None and best > 0.1:
            d, ang, Rp = R_at
            w = np.array([Rp[2, 1] - Rp[1, 2], Rp[0, 2] - Rp[2, 0], Rp[1, 0] - Rp[0, 1]])
            n = np.linalg.norm(d)
            rec.update(travel=round(float(n), 2), axis=r2(d / n) if n > 1e-6 else [0, 0, 0],
                       rot=round(float(ang), 1), rot_axis=r2(w / (np.linalg.norm(w) + 1e-9)),
                       frames=[min(mv), max(mv)] if mv else [bf, bf], peak=int(bf))
        else:
            rec.update(travel=0.0, note='never moves in any frame the block plays')
        parts.append(rec)

    # bore, muzzle (FLU, idle)
    act = [p for p in parts if p['role'] in ('slide', 'pump', 'bolt') and p['travel'] > 1 and p.get('rot', 0) < 5]
    if g.get('bore'):
        bore = np.array(g['bore'], float); bore_src = 'controller forward (his body leans; set per gun)'
    elif act:
        bore = -np.array(act[0]['axis'], float); bore_src = f"{act[0]['role']} stroke ('{act[0]['name']}')"
    else:
        bsurf = [i for i in range(len(S)) if roles[i] == 'barrel'] or [body]
        bsurf = max(bsurf, key=lambda i: S[i].shape[1])
        Wb = to_flu(S[bsurf][gidle])
        bore = np.linalg.eigh((Wb - Wb.mean(0)).T @ (Wb - Wb.mean(0)))[1][:, -1]
        bore_src = f"long axis of '{names[bsurf]}'"
    if bore[0] < 0:
        bore = -bore
    front = [i for i in range(len(S)) if roles[i] in ('barrel', 'slide') and visible(S[i][gidle])] or \
            [i for i in range(len(S)) if roles[i] == 'body' and visible(S[i][gidle])]
    W = np.vstack([to_flu(S[i][gidle]) for i in front])
    a = W @ bore
    face = W[a > a.max() - 1.0]                 # the last centimetre of the barrel: its front face
    muzzle = face.mean(0)
    if g.get('muzzle_ring'):
        # a ring-shaped mouth (BFG): the centre of the circle through the front face's ring
        rg = g['muzzle_ring']
        P = W[(a > a.max() - rg['depth']) & (W[:, 2] > rg['umin'])]
        c = np.linalg.lstsq(np.c_[2 * P[:, 1:], np.ones(len(P))], (P[:, 1:] ** 2).sum(1), rcond=None)[0]
        muzzle = np.array([face[:, 0].mean(), c[0], c[1]])

    # hands
    hands = {}
    for slot, mesh in ((2, 'hand'), (3, 'hand2')):
        if slot in models and slot in rf and models[slot].endswith(mesh + '.md3'):
            hm = md3(models[slot])
            if rf[slot] < hm['nframes']:
                try:
                    r = gripmeasure.measure(mesh, rf[slot]); r.pop('contact')
                except SystemExit as e:
                    r = dict(error=str(e))
                r['frame'] = rf[slot]
                hands[mesh] = r

    # reload piece (slot 1)
    piece = None
    if g['piece'] and 1 in models:
        _pc = {}
        def pmesh(path):
            if path not in _pc:
                pm = md3(path); _pc[path] = ([md3label.surf_xyz(s) for s in pm['surfs']], pm['nframes'])
            return _pc[path]
        CUR = [models[1]]
        def ppos(f, path=None):
            pS, pnf = pmesh(path or CUR[0])
            if f >= pnf:
                return None
            X = np.vstack([x[f] for x in pS if visible(x[f])] or [np.zeros((0, 3))])
            return None if len(X) == 0 else to_flu(X)
        seat_f = rf.get(1, 999)
        seatX = ppos(seat_f)
        st = state_frames(g['zs'])
        # reload labels in his own play order; the slot-1 frame each sprite frame draws
        reload_labels = [l for l in st if re.search(r'reload|insert|load|openbarrel|closebarrel|openpanel|lever', l, re.I)]
        seq = []
        for l in reload_labels:
            for sp, c in st[l]:
                kk = (ALT.get(sp, sp), c)
                mf = table.get(kk, {}).get(1)
                if mf is not None:
                    seq.append((l, kk, mf))
        traj = []
        for l, c, mf in seq:
            if TMODEL.get(c, {}).get(1) != models[1]:
                continue          # another model sits in slot 1 on this frame (e.g. a different ammo load)
            X = ppos(mf)
            if X is not None:
                traj.append((l, c, mf, X.mean(0)))
        approach = None; pose = None
        if g.get('carrier') and traj:
            # BREAK-OPEN: the rounds ride the carrier (the barrel) while it opens, then leave it.
            # The chamber seat is the last frame they still sit still in the carrier; the loading
            # stroke is the run that follows, reversed (the way a fresh round goes in).
            ci = names.index(g['carrier'])
            first = None; seat_i = 0
            uniq = []
            for l, c, mf, p in traj:
                if not uniq or uniq[-1][2] != mf:
                    uniq.append((l, c, mf, p))
            def local(l, c, mf, p):
                gf = table.get(c, {}).get(0, gidle)
                R, t = kabsch(to_flu(S[ci][gf]), to_flu(S[ci][gidle]))
                return R @ p + t
            loc = [local(*u) for u in uniq]
            for k in range(len(uniq)):
                if np.linalg.norm(loc[k] - loc[0]) < 0.3:
                    seat_i = k
                else:
                    break
            far = max(range(seat_i, len(uniq)), key=lambda k: np.linalg.norm(uniq[k][3] - uniq[seat_i][3]))
            seat_f = uniq[seat_i][2]; seatX = ppos(seat_f)
            pose = dict(table.get(uniq[seat_i][1], {}))
            if far != seat_i:
                approach = uniq[far]
        if g.get('seat_at') is not None and traj:
            # the piece is set down somewhere other than its rest place (BFG: the open tray;
            # closing the panel then carries it home). Seat = that frame, gun drawn in that pose.
            hit = [t for t in traj if t[2] == g['seat_at']]
            seat_f = g['seat_at']; seatX = ppos(seat_f); pose = dict(table.get(hit[-1][1], {}))
            k = max(i for i, t in enumerate(traj) if t[2] == seat_f)
            approach = final_stroke(traj[:k + 1], seatX.mean(0))
        if seatX is None and traj:
            # Ready hides the piece: the seat is where the reload leaves it last
            seatX = ppos(traj[-1][2]); seat_f = traj[-1][2]
        if seatX is not None:
            seat = seatX.mean(0)
            if g.get('seat_at') is not None:
                pass
            elif not g.get('carrier'):
                # the run that ends ON the seat: the last time the piece arrives there
                ks = [k for k, t in enumerate(traj) if np.linalg.norm(t[3] - seat) < 0.3]
                arrive = next((k for k in reversed(ks) if k > 0 and np.linalg.norm(traj[k - 1][3] - seat) >= 0.3), None)
                if arrive is not None:
                    approach = final_stroke([t for t in traj[:arrive + 1]], seat)
            elif approach is not None:
                k = next(i for i, t in enumerate(traj) if t[2] == approach[2])
                j = max(i for i, t in enumerate(traj) if np.linalg.norm(t[3] - seat) < 0.3 and i > k) if any(
                    np.linalg.norm(t[3] - seat) < 0.3 for t in traj[k:]) else None
                if j is not None:
                    approach = final_stroke(traj[:j + 1], seat) or approach
            piece = dict(model=models[1], frames=pmesh(models[1])[1], seat_frame=int(seat_f), seat=r2(seat),
                         extent_cm=r2(seatX.max(0) - seatX.min(0)),
                         path=[dict(state=l, sprite=''.join(c), frame=int(mf), pos=r2(p)) for l, c, mf, p in traj])
            if approach:
                d = seat - approach[3]
                piece['approach'] = dict(from_frame=int(approach[2]), state=approach[0], pos=r2(approach[3]),
                                         stroke=round(float(np.linalg.norm(d)), 2), axis=r2(d / np.linalg.norm(d)))
            if pose:
                piece['pose_frames'] = pose      # the gun is OPEN at the seat: draw it that way
            piece['_seatX'] = seatX
            piece['_ghost'] = ppos(approach[2]) if approach else None

    st = state_frames(g['zs'])
    phases = {}
    for l, cs in st.items():
        fr = [table.get((ALT.get(sp, sp), c), {}).get(0) for sp, c in cs]
        fr = [f for f in fr if f is not None]
        if fr:
            phases[l] = sorted(set(fr))
    unused = sorted(set(range(gnf)) - {f for d in table.values() for mi, f in d.items() if mi == 0})

    return dict(gun=key, archetype=g['archetype'], block=which, ready_sprite=''.join(ready), ready_frames=rf,
                models=models, mesh=models[0], mesh_frames=gnf, idle_frame=gidle,
                bore=r2(bore), bore_src=bore_src, muzzle=r2(muzzle), parts=parts, hands=hands, piece=piece,
                phases=phases, unused_mesh_frames=unused)


# ------------------------------------------------------------------ HUD (his gun ammo display + wrist watch)
def actor_blocks(path, actor):
    s = open(path, errors='replace').read()
    return [b for b in re.findall(r'Model\s+' + actor + r'\s*\{(.*?)\n\}', s, re.S)]


def block_pl(text):
    sc = re.search(r'^\s*Scale\s+(\S+)\s+(\S+)\s+(\S+)', text, re.M)
    of = re.search(r'^\s*Offset\s+(\S+)\s+(\S+)\s+(\S+)', text, re.M)
    return dict(scale=[float(x) for x in sc.groups()] if sc else [1, 1, 1],
                off=[float(x) for x in of.groups()] if of else [0, 0, 0])


def flu_pl(xyz, pl):
    return gunview.to_fl(hudrender.to_local(xyz, pl))


def panel(path, frame, pl):
    """centre, facing normal (toward the eye side, -F), size of a flat HUD mesh"""
    m = md3(path); X = np.vstack([flu_pl(md3label.surf_xyz(s)[frame], pl) for s in m['surfs']])
    c = X.mean(0); w, V = np.linalg.eigh((X - c).T @ (X - c)); n = V[:, 0]
    if n[0] > 0:
        n = -n
    return c, n, X.max(0) - X.min(0), X


def measure_hud(m, actor):
    out = {}
    gb = actor_blocks(MOD + 'modeldefs/holohud2.txt', actor)
    if gb:
        pl = block_pl(gb[0])
        mods = dict((int(a), b) for a, b in re.findall(r'Model\s+(\d+)\s+"([^"]+)"', gb[0]))
        fr = re.search(r'FrameIndex\s+\S+\s+\S\s+0\s+(\d+)', gb[0])
        c, n, sz, X = panel('models/common/' + mods[0], int(fr.group(1)) if fr else 0, pl)
        out['gun_display'] = dict(mesh=mods[0], scale=pl['scale'], offset=pl['off'], centre=r2(c), facing=r2(n),
                                  size=r2(sz), _X=X)
    wb = actor_blocks(MOD + 'modeldefs/holohud.txt', actor)
    if wb:
        pl = block_pl(wb[0])
        fr = re.search(r'FrameIndex\s+(\S+)\s+(\S)\s+0\s+(\d+)', wb[0])
        f = int(fr.group(3))
        c, n, sz, X = panel('models/common/w_dial.md3', f, pl)
        # which hand wears it: the nearer hand mesh at Ready
        near = {}
        for slot, key in ((2, 'hand'), (3, 'hand2')):
            if slot in m['models'] and slot in m['ready_frames']:
                hm = md3(m['models'][slot]); hf = m['ready_frames'][slot]
                if hf < hm['nframes']:
                    H = np.vstack([to_flu(md3label.surf_xyz(sf)[hf]) for sf in hm['surfs']])
                    near[key] = float(np.min(np.linalg.norm(H - c, axis=1)))
        out['wrist_watch'] = dict(mesh='w_dial.md3', frame=f, sprite=fr.group(1) + fr.group(2), offset=pl['off'],
                                  centre=r2(c), facing=r2(n), size=r2(sz),
                                  worn_on='hand (gun hand; his watch frame is the gun hand\'s one-hand pose)' if near.get('hand', 99) < 3 else (min(near, key=near.get) if near else None),
                                  hand_gap_cm={k: round(v, 2) for k, v in near.items()}, _X=X)
    return out


# ------------------------------------------------------------------ card
def card(m):
    L = [f"weapon rl_{m['gun']}",
         f"  archetype   {m['archetype']}",
         f"  source      Rusted Legacy dev build (Ermac), {m['mesh']}  block '{m['block']}'  Ready {m['ready_sprite']} {m['ready_frames']}",
         f"  space       CTL  controller frame, cm, F forward L left U up (Scale -1 1 1, Offset 0 -24 -10, vr_weaponScale 1.02)",
         f"  model       {m['mesh']}   idle_frame {m['idle_frame']}   frames {m['mesh_frames']}",
         f"  bore        {m['bore']}   # from the {m['bore_src']}",
         "  parts"]
    for p in m['parts']:
        if p['travel']:
            L.append(f"    {p['role']:<8} surf {p['surf']} '{p['name']}'  rest {p['rest']}  axis {p['axis']}  travel {p['travel']}"
                     f"  frames {p['frames'][0]}..{p['frames'][1]}" + (f"  rot {p['rot']}deg axis {p['rot_axis']}" if p['rot'] > 5 else ''))
        else:
            L.append(f"    {p['role']:<8} surf {p['surf']} '{p['name']}'  rest {p['rest']}  STILL (no frame moves it)")
    L.append(f"    muzzle    {m['muzzle']}")
    for k, lab in (('hand', 'grip'), ('hand2', 'support')):
        h = m['hands'].get(k)
        if h and 'point' in h:
            L.append(f"  {lab:<11} {k}.md3 frame {h['frame']}  held_axis {h['axis']}  point {h['point']}  radius {h['radius']}  extent {h['extent']}   # Ermac's own hand, gripmeasure")
        elif h:
            L.append(f"  {lab:<11} {k}.md3 frame {h['frame']}  NOT MEASURED: {h['error']}")
        else:
            L.append(f"  {lab:<11} none in the Ready row")
    p = m['piece']
    if p:
        L.append(f"  piece       {p['model']}  seat_frame {p['seat_frame']}  seat {p['seat']}  size {p['extent_cm']}")
        if 'approach' in p:
            a = p['approach']
            L.append(f"    approach  from frame {a['from_frame']} ({a['state']}) at {a['pos']}  stroke {a['stroke']} cm  axis {a['axis']}")
        else:
            L.append("    approach  NONE: no reload state moves the piece onto its seat")
    L.append("  phases      # mesh frames each of his states plays")
    for k, v in m['phases'].items():
        L.append(f"    {k:<24} {v[0]}..{v[-1]}" if v == list(range(v[0], v[-1] + 1)) else f"    {k:<24} {v}")
    for k, lab in (('gun_display', 'ammo_hud'), ('wrist_watch', 'watch_hud')):
        h = m.get('hud', {}).get(k)
        if h:
            extra = f"  frame {h['frame']} ({h['sprite']})  worn_on {h['worn_on']}  gap {h['hand_gap_cm']}" if k == 'wrist_watch' else f"  Offset {h['offset']}"
            L.append(f"  {lab:<11} {h['mesh']}  centre {h['centre']}  facing {h['facing']}  size {h['size']}{extra}")
    if m['unused_mesh_frames']:
        L.append(f"  unused      mesh frames no state draws: {m['unused_mesh_frames']}")
    return '\n'.join(L) + '\n'


# ------------------------------------------------------------------ render
VIEWS = gunview.VIEWS


def tris_of(m):
    out = []
    gun = md3(m['models'][0])
    rfr = dict(m['ready_frames'])
    if m['piece'] and m['piece'].get('pose_frames'):
        rfr.update({k: v for k, v in m['piece']['pose_frames'].items() if k != 1})
    f0 = rfr[0]
    for i, s in enumerate(gun['surfs']):
        role = next((p['role'] for p in m['parts'] if p['surf'] == i), 'body')
        v = to_flu(md3label.surf_xyz(s)[f0]); t = md3label.surf_tris(s)
        out.append((v[t[:, 0]], v[t[:, 1]], v[t[:, 2]], np.array(COL.get(role, COL['deco']), float)))
    for slot, key in ((2, 'hand'), (3, 'hand2')):
        if slot in m['models'] and slot in rfr:
            hm = md3(m['models'][slot]); f = rfr[slot]
            if f < hm['nframes']:
                for s in hm['surfs']:
                    v = to_flu(md3label.surf_xyz(s)[f]); t = md3label.surf_tris(s)
                    out.append((v[t[:, 0]], v[t[:, 1]], v[t[:, 2]], np.array(COL[key], float)))
    for k, col in (('gun_display', (90, 230, 255)), ('wrist_watch', (245, 245, 245))):
        h = m.get('hud', {}).get(k)
        if h is not None and '_X' in h:
            X = h['_X']; path = 'models/common/' + h['mesh']
            hm = md3(path); f = h.get('frame', 0); off = 0
            pl = dict(scale=h.get('scale', PL['scale']), off=h['offset'])
            for sf in hm['surfs']:
                v = flu_pl(md3label.surf_xyz(sf)[f], pl); t = md3label.surf_tris(sf)
                out.append((v[t[:, 0]], v[t[:, 1]], v[t[:, 2]], np.array(col, float)))
    p = m['piece']
    if p:
        pm = md3(p['model'])
        for key, f in (('piece', p['seat_frame']), ('ghost', p.get('approach', {}).get('from_frame'))):
            if f is None or f >= pm['nframes']:
                continue
            for s in pm['surfs']:
                x = md3label.surf_xyz(s)[f]
                if not visible(x):
                    continue
                v = to_flu(x); t = md3label.surf_tris(s)
                out.append((v[t[:, 0]], v[t[:, 1]], v[t[:, 2]], np.array(COL[key], float)))
    return out


def marks(m):
    mk = [(*m['muzzle'], 'muzzle', (255, 60, 60))]
    for k, lab, c in (('hand', 'grip', (255, 240, 0)), ('hand2', 'support', (60, 255, 120))):
        h = m['hands'].get(k)
        if h and 'point' in h:
            mk.append((*h['point'], lab, c))
    for k, lab, c in (('gun_display', 'ammo hud', (90, 230, 255)), ('wrist_watch', 'watch', (245, 245, 245))):
        h = m.get('hud', {}).get(k)
        if h:
            mk.append((*h['centre'], lab, c))
    if m['piece']:
        mk.append((*m['piece']['seat'], 'seat', (255, 150, 40)))
        if 'approach' in m['piece']:
            mk.append((*m['piece']['approach']['pos'], 'from', (200, 140, 90)))
    return mk


def render(m, out):
    tr = tris_of(m)
    gunview.triangles = lambda items: tr
    panels = []
    for kind in ('side', 'top', 'front'):
        fn = out + f'_{kind}.png'
        gunview.view([None], fn, kind=kind, px=9, marks=marks(m), title=f"rl_{m['gun']}")
        panels.append(Image.open(fn))
    H = max(p.height for p in panels); Wd = sum(p.width for p in panels) + 8 * (len(panels) - 1)
    img = Image.new('RGB', (Wd, H), (25, 25, 32)); x = 0
    for p in panels:
        img.paste(p, (x, 0)); x += p.width + 8
    img.save(out + '.png')
    for kind in ('side', 'top', 'front'):
        os.remove(out + f'_{kind}.png')
    return out + '.png'


ACTOR = dict(pistol='RLPistol', shotgun='RLShotgun', ssg='RLSuperShotgun', chaingun='RLChaingun', plasma='RLPlasmaRifle',
             rocket='RLRocketLauncher', hellshotgun='HellShotgun', incinerator='RLIncinerator', bfg='RLBFG9000',
             heatwave='RLHeatwave', chainsaw='RLChainsaw')


def run(key):
    m = measure(key)
    m['hud'] = measure_hud(m, ACTOR[key])
    d = os.path.join(OUT, 'cards', key); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, f'rl_{key}.card'), 'w').write(card(m))
    png = render(m, os.path.join(d, f'rl_{key}'))
    if m['piece']:
        m['piece'].pop('_seatX', None); m['piece'].pop('_ghost', None)
    for h in m['hud'].values():
        h.pop('_X', None)
    json.dump(m, open(os.path.join(d, f'rl_{key}.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    return m, png


if __name__ == '__main__':
    for k in sys.argv[1:]:
        m, png = run(k)
        print(open(os.path.join(OUT, 'cards', k, f'rl_{k}.card')).read())
        print('render', png)
