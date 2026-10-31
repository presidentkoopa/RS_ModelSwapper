"""genpack.py -- build a stock-QuestZDoom VR weapon pack (one per set) from the REMA cards and meshes.

    python -B genpack.py <rs_vr_weapons root> <quest kit src root> <out root> <set>   set: vanilla | plus | modern

Per gun: the card gives parts, axes, travel, grip, trigger, eject port, sounds, capacity; the mesh
gives the surfaces; the REMA MODELDEF gives the scale. This file places the gun on the Quest
controller (card2quest), computes the well mouth from the mesh, and feeds the kit's own
generator (gen_rsr.compute / modeldef / zs) so the Quest reload runtime gets the tables it
already understands. Weapon classes come from a template (no host mod, no DECORATE to splice).

Archetypes this pass: magazine-fed (feed part, kind slide) with or without a charging handle /
slide; everything else ships as a model with the stock (canned) reload and is listed as such.
"""
import sys, os, re, json, glob, shutil, zipfile, struct
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, '/mnt/user-data/uploads/Quest_Weapons_Kit/kit/kit/team/reload_merged/tools')   # gen_rsr, rgeo (kit, unmodified)
import card2quest as c2q
import gen_rsr, rgeo

WS = 1.02
CLEAR = 'rsr_clear.png'

# vanilla ammo the reserve maps to, by card magfamily / type
RESERVE = {'pistol': 'Clip', 'rifle': 'Clip', 'smg': 'Clip', '45': 'Clip', '9mm': 'Clip', '762': 'Clip', '556': 'Clip',
           'shotgun': 'Shell', '12ga': 'Shell', 'rocket': 'RocketAmmo', 'launcher': 'RocketAmmo',
           'plasma': 'Cell', 'cell': 'Cell', 'railgun': 'Cell', 'bfg': 'Cell', 'flamethrower': 'Cell', 'chaingun': 'Clip'}
# Doom's slots and selection orders by gun type (a set's own WM_Gun Default wins where it has them)
SLOT = {'chainsaw': 1, 'pistol': 2, 'revolver': 2, 'shotgun': 3, 'breakaction': 3, 'chaingun': 4, 'smg': 4, 'rifle': 4,
        'launcher': 5, 'grenade': 5, 'plasma': 6, 'flamethrower': 6, 'railgun': 6, 'bfg': 7}
ORDER = {'chainsaw': 2200, 'pistol': 1900, 'revolver': 1800, 'shotgun': 1300, 'breakaction': 400, 'chaingun': 700, 'smg': 800,
         'rifle': 750, 'launcher': 2500, 'grenade': 2600, 'plasma': 100, 'flamethrower': 150, 'railgun': 120, 'bfg': 2800}
# stock projectile for a card ShotClass that is not a Doom actor
PROJ = {'plasma': 'PlasmaBall', 'bfg': 'BFGBall', 'launcher': 'Rocket', 'railgun': None, 'flamethrower': 'PlasmaBall'}


# ---------------------------------------------------------------- sets
# THE VANILLA SET IS DOOM'S ARSENAL: the eight weapons, Doom's names, Doom's numbers, each the
# reloadable stand-in from the cards. Class names carry a Doom prefix because the engine forbids a
# second class named Pistol; the Tag / pickup name is Doom's.
VANILLA = [('DoomPistol', 'WM_M4A3', 'Pistol'), ('DoomShotgun', 'WM_PumpDoom', 'Shotgun'),
           ('DoomSuperShotgun', 'WM_SSG', 'Super Shotgun'), ('DoomChaingun', 'WM_Chaingun', 'Chaingun'),
           ('DoomRocketLauncher', 'WM_RocketLauncher', 'Rocket Launcher'), ('DoomPlasmaRifle', 'WM_PlasmaRifle', 'Plasma Rifle'),
           ('DoomBFG9000', 'WM_BFG', 'BFG 9000'), ('DoomChainsaw', 'WM_Chainsaw', 'Chainsaw')]
VANILLA_TAG = {c: t for c, _, t in VANILLA}
# Doom's own gunplay, exactly (zscript/actors/doom/doomweapons.zs): damage, pellets, spread, cycle tics, auto
DOOM_FIRE = {
    'DoomPistol':         dict(dmg=5, pellets=1, sh=5.6, sv=0.0, tics=10, auto=True,  proj=None),    # A_FirePistol: 5*1d3; PISG B 6 + C 4
    'DoomShotgun':        dict(dmg=5, pellets=7, sh=5.6, sv=0.0, tics=37, auto=False, proj=None),    # A_FireShotgun 7 x 5*1d3; SHTG cycle
    'DoomSuperShotgun':   dict(dmg=5, pellets=20, sh=11.2, sv=7.1, tics=53, auto=False, proj=None),  # A_FireShotgun2
    'DoomChaingun':       dict(dmg=5, pellets=1, sh=5.6, sv=0.0, tics=4, auto=True,  proj=None),     # A_FireCGun, 4 tics a shot
    'DoomRocketLauncher': dict(dmg=0, pellets=1, sh=0, sv=0, tics=20, auto=True, proj='Rocket'),     # MISG B 8 + 12
    'DoomPlasmaRifle':    dict(dmg=0, pellets=1, sh=0, sv=0, tics=3, auto=True, proj='PlasmaBall'),
    'DoomBFG9000':        dict(dmg=0, pellets=1, sh=0, sv=0, tics=20, auto=False, proj='BFGBall'),   # 40 charge tics in chargetics
    'DoomChainsaw':       dict(dmg=2, pellets=1, sh=0, sv=0, tics=4, auto=True, proj='saw'),
}


def set_members(root, which):
    """class -> card class, from the WMSHEET files (vanilla = Doom's eight, plus = plus_* + extras)"""
    out = {}
    if which == 'vanilla':
        return {c: card for c, card, _ in VANILLA}
    if which == 'modern':
        for w in c2q.load_cards(root):
            if w['src'].startswith('WMCARD.breach'):
                out[w['cls']] = w['cls']
        return out
    for f in sorted(glob.glob(os.path.join(root, 'WMSHEET.*'))):
        name = os.path.basename(f)
        is_plus = name.startswith('WMSHEET.plus_')
        if (which == 'plus') != is_plus:
            continue
        for cls in re.findall(r'^\s*gun\s+"(WM_\w+)"', open(f, encoding='latin-1').read(), re.M):
            card = cls.replace('WM_VP_', 'WM_') if cls.startswith('WM_VP_') else cls
            out[cls] = card
    return out


# ---------------------------------------------------------------- fire stats from the set's ZScript
STAT_RE = re.compile(r'^\s*(?:WM_Gun\.|Weapon\.|Inventory\.)?(\w+)\s+([^;]+);', re.M)


def gun_stats(root):
    """class -> dict of Default lines (WM_Gun.*, Weapon.*, Tag) from every zscript under the repo"""
    out = {}
    for f in glob.glob(os.path.join(root, '**', '*.zs'), recursive=True):
        t = open(f, encoding='latin-1').read()
        for m in re.finditer(r'class\s+(WM_\w+)\s*:\s*WM_\w+\s*\{(.*?)\n\}', t, re.S):
            cls, body = m.group(1), m.group(2)
            d = re.search(r'Default\s*\{(.*?)\n\t\}', body, re.S)
            if not d:
                continue
            st = {}
            for k, v in STAT_RE.findall(d.group(1)):
                st[k.lower()] = v.strip()
            out[cls] = st
    return out


def sheet_stats(root):
    """class -> the WMSHEET gun block (lower-case keys, strings), its `class` block flattened as
    class_<key>; the `instead` look block skipped. Vanilla and plus sheets alike."""
    out = {}
    for f in sorted(glob.glob(os.path.join(root, 'WMSHEET.*'))):
        cur = None; block = None
        for raw in open(f, encoding='latin-1'):
            line = raw.split('#', 1)[0].strip()
            if not line:
                continue
            m = re.match(r'^gun\s+"(\w+)"', line)
            if m:
                cur = out.setdefault(m.group(1), {}); block = None; continue
            if cur is None:
                continue
            if line == 'end':
                if block: block = None
                else: cur = None
                continue
            if '=' not in line:
                block = line.split()[0]; continue
            k, v = [x.strip() for x in line.split('=', 1)]
            if block == 'instead':
                continue
            cur[(block + '_' if block else '') + k.lower()] = v
    return out


# the set's own projectiles (RS_Ballistics) -> Doom's: the look lane is not carried to Quest
SHOTCLASS = {'RSB_BFGBall': 'BFGBall', 'RSB_BFGBallHeavy': 'BFGBall', 'RSB_PlasmaBall': 'PlasmaBall',
             'RSB_PlasmaBallCarbine': 'PlasmaBall', 'RSB_Rocket': 'Rocket', 'RSB_RocketRPG': 'Rocket',
             'WM_LauncherGrenade': 'Rocket', 'WM_BolterBolt': 'PlasmaBall', 'WM_UnmakerBolt': 'PlasmaBall'}


def num(s, i=0, default=0.0):
    try:
        return float(re.split(r'\s*,\s*', s)[i])
    except Exception:
        return default


# ---------------------------------------------------------------- mesh
def md3_surfaces(path):
    d = open(path, 'rb').read()
    nfr, ntag, nsurf, nskin, ofr, otag, osurf, oeof = struct.unpack_from('<8i', d, 76)
    out = []; off = osurf
    for s in range(nsurf):
        name = d[off + 4:off + 68].split(b'\0')[0].decode('latin1')
        flags, snfr, nsh, nv, nt, otri, osh, ost, oxyz, oend = struct.unpack_from('<10i', d, off + 68)
        xyz = np.frombuffer(d, dtype='<i2', count=snfr * nv * 4, offset=off + oxyz).reshape(snfr, nv, 4)[:, :, :3].astype(float) / 64.0
        shader = d[off + osh:off + osh + 64].split(b'\0')[0].decode('latin1') if nsh else ''
        out.append(dict(i=s, name=name, nv=nv, xyz=xyz, shader=shader))
        off += oend
    return nfr, out


def iqm_mesh_names(path):
    d = open(path, 'rb').read()
    h = struct.unpack_from('<27I', d, 16)
    ntext, otext, nmesh, omesh = h[3], h[4], h[5], h[6]
    txt = d[otext:otext + ntext]
    def s(o): return txt[o:txt.index(b'\0', o)].decode('latin1')
    return [s(struct.unpack_from('<6I', d, omesh + i * 24)[0]) for i in range(nmesh)]


def bake_iqm(w, mp, outdir, model_dir, root):
    """Modern (IQM) gun -> one-frame MD3 split by the card's joints (iqm2md3.bake). The card's
    parts get their baked surface names; the baked file ships in place of the IQM. Returns
    (baked path in the pack, surfaces, notes)."""
    import iqm2md3
    k, parts = w['keys'], w['parts']
    aslist = lambda v: v if isinstance(v, list) else ([v] if v else [])
    drop = [str(x) for x in aslist(k.get('hidesurface'))]
    drop_joints = [str(x) for x in aslist(k.get('hidejoint'))]
    joint_parts = {n: parts[n]['keys']['joint'] for n in w['order'] if 'joint' in parts[n]['keys']}
    mesh_parts = {sname: n for n in w['order'] for sname in parts[n]['surfaces']}
    # materials -> the files that are really there (glass.bmp vs glass.png, truncated names)
    files = os.listdir(os.path.dirname(mp))
    notes = []
    def material(mat):
        if mat in files:
            return mat
        stem = os.path.splitext(mat)[0].lower()
        for f in files:
            if os.path.splitext(f)[0].lower() == stem or (len(stem) >= 8 and os.path.splitext(f)[0].lower().startswith(stem)):
                notes.append('material %s -> %s' % (mat, f)); return f
        notes.append('material %s: no file' % mat); return mat
    # the rest frame and the model list come from REMA's MODELDEF for the card's prop (Breach's
    # own Ready frame: 0 pistols, 25 rifles, 109 MP5, 59 Benelli; MK18S = gun + silencer + laser)
    info_md = c2q.modeldef_info(root).get(str(k.get('prop', '')).strip('"'))
    frame = 0; extra = []
    if info_md:
        frame = info_md['models'][0][1]
        extra = [(os.path.join(os.path.dirname(mp), f), fr) for f, fr in info_md['models'][1:]]
    else:
        notes.append('no REMA MODELDEF block for prop %s: frame 0 assumed' % k.get('prop'))
    base = os.path.splitext(os.path.basename(mp))[0] + ('_%d' % frame if frame else '') + ('_x%d' % len(extra) if extra else '') + '_q.md3'
    dst = os.path.join(outdir, model_dir, base)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    names, counts, info = iqm2md3.bake(mp, dst, frame, joint_parts, drop=drop, drop_joints=drop_joints, mesh_parts=mesh_parts, material=material, extra=extra)
    for n in w['order']:
        mine = [sn for sn in names if sn == n or sn.startswith(n + '#')]
        if mine:
            parts[n]['surfaces'] = mine
    notes.append('baked %s frame %d%s -> %s: %s%s' % (os.path.basename(mp), frame, ' + ' + ', '.join(os.path.basename(e[0]) for e in extra) if extra else '', base,
                 ', '.join('%s %d verts' % kv for kv in counts.items()),
                 '; dropped %d tris of %s' % (info['dropped_tris'], drop_joints) if info['dropped_tris'] else ''))
    for n, j in joint_parts.items():
        if n not in counts:
            notes.append('part %s: joint %s owns no vertices (%s)' % (n, j, 'joint missing' if j not in info['joints'] else 'empty'))
    for f in files:
        if f.lower().endswith(('.png', '.bmp', '.jpg', '.tga')):
            shutil.copy2(os.path.join(os.path.dirname(mp), f), os.path.join(outdir, model_dir, f))
    return dst, notes


def surf_index(names, want):
    """card surface name -> index (exact, then case-insensitive, then prefix)"""
    for i, n in enumerate(names):
        if n == want: return i
    for i, n in enumerate(names):
        if n.lower() == want.lower(): return i
    for i, n in enumerate(names):
        if n.lower().startswith(want.lower()) or want.lower().startswith(n.lower()): return i
    return None


# Extra roots a card's mesh path may resolve against, searched after `root` itself.
# A card measured for one package can name a mesh that ships in another: the BD22
# cards were measured against RS_VR_Weapons' static `_wm` copies under its bd22/,
# while the mesh a pack ships is the animated one in its own models/. Empty by
# default, so a caller that sets nothing behaves exactly as before; a driver fills
# it with the packages whose trees the cards in hand reach into.
MESH_ROOTS = []


def find_mesh(root, d, f):
    """a card's (dir, file) -> the first path that exists, over root then MESH_ROOTS"""
    first = os.path.join(root, d or '', f)
    if os.path.exists(first):
        return first
    for r in MESH_ROOTS:
        p = os.path.join(r, d or '', f)
        if os.path.exists(p):
            return p
    return first


def part_surfaces(root, w, part, names, surfs, rest_frame, feed=True):
    """A card part's surfaces -> mesh surface indices: by name where the name is the
    mesh's own, and BY MEASUREMENT where it is not.

    card_from_motion works from motion rather than from the author's naming, so it
    writes a part's ROLE as its surface name -- `surface = mag`. The gun's own mesh
    carries the author's names: Lipas, Runko, Cube, m41a_magazine, weapon.005. The
    name can therefore never resolve, and that one string comparison rejected 23
    measured guns outright.

    Two independent measurements already in the card resolve it:

      the carved part mesh  md3label carved the moving part out to its own file
                            (magmodel). A carve copies that surface's vertices, so
                            the carved file's VERTEX COUNT is the surface's.
      the part's centre     magcenter, or the part's own grab point, is that
                            surface's centroid in the gun's frame at the card's
                            REST frame. The rest frame matters: frame 0 of a
                            32-frame reload is mid-animation, and measuring the
                            Rifle there put its magazine 11 units from its own
                            magcenter and picked the wrong surface.

    Where both are available they agree. Across the shelf the centre lands within
    0.007 units of the surface the vertex count picks while the next-nearest
    surface is 3 to 27 units away, and where the count is ambiguous (frame-stacked
    duplicate surfaces -- the chex zorchers) the centre picks from among its own
    candidates. Where they disagree, this returns nothing: a guessed magazine sends
    the player's hand to the wrong part of the gun, which is worse than no VR
    reload at all.

    Returns (indices, note). indices is None when the part cannot be resolved, and
    the note says which evidence was used or what disagreed -- printed per gun, so
    a resolution is always visible rather than assumed.
    """
    idx = [surf_index(names, s) for s in part['surfaces']]
    if all(i is not None for i in idx):
        return idx, 'by name'

    nv = [s['xyz'][0].shape[0] for s in surfs]
    cand = None
    # The carve and magcenter are the MAGAZINE's evidence. Any other part (the charging handle)
    # is found by its own grab point alone: given the magazine's, it resolved to the magazine.
    mm = w['keys'].get('magmodel') if feed else None
    if isinstance(mm, list) and mm[0]:
        mp = find_mesh(root, mm[0], mm[1])
        if os.path.exists(mp):
            try:
                import md3read
                n = md3read.read_md3(mp)['surfs'][0]['xyz'][0].shape[0]
                cand = [i for i, v in enumerate(nv) if v == n]
            except Exception:
                cand = None

    centre = (w['keys'].get('magcenter') if feed else None) or part['keys'].get('grab') or part.get('grab')
    near = None
    if centre is not None:
        try:
            c = np.asarray([float(x) for x in centre], float)
            d = [float(np.linalg.norm(s['xyz'][min(rest_frame, s['xyz'].shape[0] - 1)].mean(0) - c))
                 for s in surfs]
            order = sorted(range(len(d)), key=lambda i: d[i])
            near = (order[0], d[order[0]], d[order[1]] if len(order) > 1 else None)
        except Exception:
            near = None

    if cand is not None and len(cand) == 1 and near is not None and near[0] != cand[0]:
        return None, ('evidence disagrees: carved mesh says surface %d, the card\'s centre says %d'
                      % (cand[0], near[0]))
    if near is not None and (cand is None or near[0] in cand):
        i = near[0]
        # A magazine is a part of a gun, never the bulk of it. The biggest surface in
        # a gun mesh is its body; driving that as the magazine would take the whole
        # gun out of the player's hand. A rule, not taste -- and no gun on the shelf
        # trips it today, so it is here as the guard for the next card, not a filter.
        if i == int(np.argmax(nv)):
            return None, ('resolved to surface %d (%s), which is the gun\'s largest -- that is '
                          'its body, not its %s' % (i, names[i], 'magazine'))
        return [i], ('by %s (centre off %.3f, next surface %.2f away)'
                     % ('carved mesh and centre' if cand else 'centre', near[1],
                        near[2] if near[2] is not None else -1))
    if cand is not None and len(cand) == 1:
        return cand, 'by the carved mesh\'s vertex count'
    return None, ('unresolved: %s names no surface of %s' % (part['surfaces'], names))


def mouth_depth(surfs, frame, scale, off, mag_idx, well, ins):
    """the kit's well mouth: lowest body point (along -insert) inside a tube of the magazine's half
    width about the insert axis, below the magazine's top. Returns (depth cm, base point, mag top)"""
    mag = np.concatenate([rgeo.to_flu(surfs[i]['xyz'][frame], scale, off) for i in mag_idx])
    body = np.concatenate([rgeo.to_flu(s['xyz'][frame], scale, off) for s in surfs if s['i'] not in mag_idx])
    c = mag.mean(0)
    s_ = (mag - c) @ ins
    span = s_.max() - s_.min()
    top = mag[s_ >= s_.max() - 0.1 * span].mean(0)
    base = mag[s_ <= s_.min() + 0.1 * span].mean(0)
    perp = (mag - c) - np.outer((mag - c) @ ins, ins)
    hw = float(np.percentile(np.linalg.norm(perp, axis=1), 95))
    q = body - top
    sq = q @ ins
    pq = q - np.outer(sq, ins)
    m = (np.linalg.norm(pq, axis=1) <= hw + 0.5) & (sq <= 0) & (sq >= -(span + 2))
    smin = float(sq[m].min()) if m.any() else 0.0
    return round(-smin, 2), base, top, hw


# ---------------------------------------------------------------- per gun -> gen_rsr record
def build_gun(root, w, cls, geo_rec, surfs_names, surfs, nfr, spr):
    """returns (gen_rsr GUNS entry, survey record) for a magazine gun, or None"""
    parts = w['parts']
    feed = [n for n in w['order'] if parts[n]['keys'].get('role') == 'feed' and parts[n]['dof'].get('kind') == 'slide']
    if not feed:
        return None, 'no feed part'
    fname = feed[0]; fp = parts[fname]
    if not fp['surfaces']:
        return None, 'feed part %s names no surface (joint / baked part)' % fname
    act = [n for n in w['order'] if parts[n]['keys'].get('role') == 'action' and parts[n]['dof'].get('kind') == 'slide']
    hinged = [n for n in w['order'] if parts[n]['keys'].get('role') == 'action' and parts[n]['dof'].get('kind') == 'hinge']
    scale, off, fr = tuple(geo_rec['hud_scale']), tuple(geo_rec['offset']), geo_rec['rest_frame']
    mag_idx, how = part_surfaces(root, w, fp, surfs_names, surfs, fr)
    if mag_idx is None:
        return None, 'feed part %s: %s' % (fname, how)
    feed_how = how
    ins = np.array(geo_rec['parts'][fname]['insert_dir'], float)
    depth, base, top, hw = mouth_depth(surfs, fr, scale, off, mag_idx, None, ins)
    magp = dict(well_point=top.round(3).tolist(), insert_dir=ins.round(4).tolist(), insert_depth_cm=depth,
                base_point=base.round(3).tolist(), half_width_cm=round(hw, 2))
    # THE WELL MUST BE WITHIN REACH OF THE HAND HOLDING THE GUN.
    #
    # Every gun is placed so that its card's grip palm sits at GRIP_REF, the centre of
    # the Quest gun hand. So the distance from the well to GRIP_REF is the distance from
    # the player's own grip to the hole the magazine goes into, directly comparable
    # across every gun on the shelf -- and on a real gun that is a hand's span, not a
    # stride. Measured across the shelf it splits cleanly: 32 guns land between 4 and
    # 40 cm, and the rest between 43 cm and 1.9 m. Nothing sits near the line.
    #
    # A well a metre from the grip is not a magazine well. It means something upstream
    # is wrong for that gun -- its card's palm point, its MODELDEF scale, or a rest
    # frame that catches the magazine already ejected (the Kar98's stripper clip is 45
    # units out of the gun at frame 0 and 10 at frame 21). The measurement is wrong in
    # a way this cannot repair, so the gun is HELD: it keeps the mod's own canned
    # reload, which works, instead of being sent a VR reload that reaches into
    # thin air.
    #
    # 40 cm, not tighter: an RPG is loaded at the mouth of the tube and a Garand's
    # en-bloc goes in ahead of the trigger guard, and both are a real arm's reach from
    # the grip. Tighter would hold guns whose geometry is sound.
    reach = float(np.linalg.norm(top - c2q.GRIP_REF))
    well_frame = fr
    if reach > 40.0:
        # SECOND CHANCE, AT THE FRAME WHERE THE MAGAZINE IS IN THE GUN.
        #
        # The rest frame is found by when the body stops turning after a raise. That is
        # the right frame for the gun's pose, but it says nothing about where the
        # magazine is, and on a gun whose reload throws the spent one clear of the
        # screen the magazine at that frame is already out: the Kar98's stripper clip
        # sits 45 units off the body at its rest frame and 10 at frame 21. Measuring
        # the well off a magazine in mid-air puts the well in mid-air with it.
        #
        # Seated is measurable, not a guess: the frame where the magazine's centroid is
        # closest to the body's. Tried only when the rest frame's answer already failed,
        # so every gun that passes first time keeps the number it has always had.
        mag_c = np.concatenate([surfs[i]['xyz'] for i in mag_idx], axis=1)
        body_s = [s for s in surfs if s['i'] not in mag_idx]
        if body_s and mag_c.shape[0] > 1:
            nf2 = min([mag_c.shape[0]] + [s['xyz'].shape[0] for s in body_s])
            d = [float(np.linalg.norm(mag_c[f].mean(0)
                                      - np.concatenate([s['xyz'][f] for s in body_s]).mean(0)))
                 for f in range(nf2)]
            seated = int(np.argmin(d))
            if seated != fr:
                d2, b2, t2, h2 = mouth_depth(surfs, seated, scale, off, mag_idx, None, ins)
                r2 = float(np.linalg.norm(t2 - c2q.GRIP_REF))
                if r2 <= 40.0:
                    depth, base, top, hw, reach, well_frame = d2, b2, t2, h2, r2, seated
                    magp = dict(well_point=top.round(3).tolist(), insert_dir=ins.round(4).tolist(),
                                insert_depth_cm=depth, base_point=base.round(3).tolist(),
                                half_width_cm=round(hw, 2))
    if reach > 40.0:
        return None, ('well %s is %.0f cm from the grip hand, at its rest frame and at '
                      'the frame its magazine is seated -- a magazine well is a hand\'s '
                      'span away, so this gun\'s placement is wrong'
                      % (np.round(top, 1).tolist(), reach))
    survey = dict(parts={'magazine': magp})
    handle_idx = []
    handle_how = ''
    if act:
        ap = parts[act[0]]
        handle_idx = [i for i in (surf_index(surfs_names, s) for s in ap['surfaces']) if i is not None]
        if not handle_idx:
            # the same role-name-for-surface problem as the feed part; the handle is
            # optional, so an unresolved one leaves the gun a magazine-only reload
            # rather than rejecting it
            hi, handle_how = part_surfaces(root, w, ap, surfs_names, surfs, fr, feed=False)
            handle_idx = hi or []
        g_ = geo_rec['parts'][act[0]]
        survey['parts']['handle'] = dict(grab_point=g_['grab'], pull_dir=g_['axis'], travel_cm=g_['travel_cm'])
    k = w['keys']
    snd = lambda n: k.get(n, '') if isinstance(k.get(n, ''), str) else ''
    model = k['model'] if isinstance(k['model'], list) else [None, k['model']]
    skin = k.get('skin') if isinstance(k.get('skin'), list) else [model[0], k.get('skin')]
    typ = k.get('type', '')
    fam = str(k.get('magfamily', typ)).lower()
    reserve = RESERVE.get(fam, RESERVE.get(typ, 'Clip'))
    g = dict(key=cls, cls=cls, set='q', mesh=find_mesh(root, model[0], model[1]), ship_mesh=None,
             path=model[0], model=model[1], skin=skin[1], scale=scale, off=off, extra='\tNoInterpolation\n',
             ready_frame=fr, mag_surfs=mag_idx, handle_surfs=handle_idx, bolt_surfs=[],
             ready_sprites=['%s A' % spr['gun']], spr_gun=spr['m'], spr_part=spr['p'], spr_world=spr['w'],
             handle_mode='layers' if handle_idx else None, handle_part='handle' if handle_idx else None, bolt_part=None,
             grip='mesh', back_at=0.85 if handle_idx else 1.0,
             snd=dict(out=snd('magoutsound'), inn=snd('maginsound'), back=snd('rackapexsound'), fwd=snd('rackresetsound'), land=snd('magdropsound') or 'wm/magdrop'),
             reserve=reserve, magammo='WMQ_Mag_%s' % cls, nomag='RSR_NoMag_%s' % cls,
             charge='token' if handle_idx else 'never', charge_token='RSR_Charge' if handle_idx else '',
             reload_token='', chan=5, capacity=int(k.get('capacity', 10)), model_dir=model[0], skin_file=skin[1])
    # slide / bolt lock when empty. The card says so only where its rack cycle is declared
    # (cycle rack ... holdopen = whenempty|never); the rest is REMA's synthesised grammar, so the
    # default here is a RULE, not card data: a part named like a slide or bolt holds open, a
    # charging handle does not. Reported per gun so it can be checked.
    ho = (k.get('_cycle:rack') or {}).get('holdopen')
    if ho is not None:
        g['slide_lock'] = str(ho).lower() == 'whenempty'; g['slide_lock_src'] = 'card'
    else:
        an = act[0].lower() if act else ''
        g['slide_lock'] = bool(act) and ('slide' in an or an.startswith('bolt'))
        g['slide_lock_src'] = 'default rule (part %s)' % (an or 'none')
    g['notes'] = ['action part %s is a hinge: not driven (the Quest handle is a straight pull)' % n for n in hinged]
    # How each part's surfaces were resolved, so a measured resolution is never silent.
    g['feed_surf_src'] = feed_how
    # The frame the well was measured at: the rest frame, or the frame the magazine is
    # seated at where the rest frame put the well out of the player's reach.
    g['well_frame'] = well_frame
    if well_frame != fr:
        g['notes'].append('well measured at frame %d, where its magazine is seated '
                          '(the rest frame %d has it out of the gun)' % (well_frame, fr))
    if handle_how:
        g['handle_surf_src'] = handle_how
    return g, survey


# ---------------------------------------------------------------- weapon class template
# Doom's own gunplay by gun type: the cards carry none (REMA's engine does the shooting), so this
# is a RULE table, overridden by a set's own WM_Gun Default numbers where it has them (Modern).
# (damage, pellets, spread_h, spread_v, tics, auto, projectile)
FIRE = {
    'pistol':       dict(dmg=5,  pellets=1,  sh=4.0,  sv=2.0, tics=10, auto=True,  proj=None),
    'revolver':     dict(dmg=20, pellets=1,  sh=2.0,  sv=1.0, tics=18, auto=False, proj=None),
    'smg':          dict(dmg=5,  pellets=1,  sh=5.6,  sv=2.0, tics=4,  auto=True,  proj=None),
    'rifle':        dict(dmg=8,  pellets=1,  sh=3.0,  sv=1.5, tics=5,  auto=True,  proj=None),
    'shotgun':      dict(dmg=5,  pellets=7,  sh=5.6,  sv=0.0, tics=20, auto=False, proj=None),
    'breakaction':  dict(dmg=5,  pellets=20, sh=11.2, sv=7.1, tics=24, auto=False, proj=None),
    'chaingun':     dict(dmg=5,  pellets=1,  sh=5.6,  sv=0.0, tics=4,  auto=True,  proj=None),
    'plasma':       dict(dmg=0,  pellets=1,  sh=0,    sv=0,   tics=3,  auto=True,  proj='PlasmaBall'),
    'launcher':     dict(dmg=0,  pellets=1,  sh=0,    sv=0,   tics=20, auto=False, proj='Rocket'),
    'bfg':          dict(dmg=0,  pellets=1,  sh=0,    sv=0,   tics=20, auto=False, proj='BFGBall'),
    'railgun':      dict(dmg=150, pellets=1, sh=0,    sv=0,   tics=30, auto=False, proj='rail'),
    'flamethrower': dict(dmg=0,  pellets=1,  sh=0,    sv=0,   tics=4,  auto=True,  proj='FatShot'),
    'grenade':      dict(dmg=0,  pellets=1,  sh=0,    sv=0,   tics=20, auto=False, proj='Grenade'),
    'chainsaw':     dict(dmg=2,  pellets=1,  sh=0,    sv=0,   tics=4,  auto=True,  proj='saw'),
}
TYPE_HINT = [('chainsaw', 'chainsaw'), ('bfg', 'bfg'), ('rocket', 'launcher'), ('rpg', 'launcher'), ('launcher', 'launcher'),
             ('plasma', 'plasma'), ('machinegun', 'chaingun'), ('chaingun', 'chaingun'), ('minigun', 'chaingun'),
             ('pump', 'shotgun'), ('ssg', 'breakaction'), ('supershotgun', 'breakaction'), ('shotgun', 'shotgun'),
             ('pistol', 'pistol'), ('revolver', 'revolver'), ('smg', 'smg'), ('rifle', 'rifle'), ('rail', 'railgun'), ('flame', 'flamethrower')]


def gun_type(cls, card_keys):
    t = str(card_keys.get('type', '') or '').lower()
    if t in FIRE:
        return t, 'card'
    lc = cls.lower()
    for hint, typ in TYPE_HINT:
        if hint in lc:
            return typ, 'class name'
    return 'pistol', 'fallback'


def weapon_zs(cls, g, st, spr, has_rsr, slot, order, card_keys, typ):
    """one weapon, stock ZScript 4.10. Fire from FIRE[type] unless the set's own WM_Gun Default has
    numbers; the sounds from the card; the Quest reload's weapon-side states (rsr_patch.bd_block,
    in ZScript) with the canned reload as RSR_Stock."""
    f = dict(DOOM_FIRE.get(cls) or FIRE[typ])
    if cls in DOOM_FIRE:
        st = {k: v for k, v in st.items() if k in ('capacity', 'firesound', 'firesfrom', 'class_ammo', 'chargetics', 'releasetics')}
    if 'shotdamage' in st:
        f['dmg'] = int(num(st['shotdamage'], 0, f['dmg']))
    if 'shotpellets' in st:
        f['pellets'] = int(num(st['shotpellets'], 0, f['pellets']))
    if 'shotspread' in st:
        f['sh'], f['sv'] = num(st['shotspread'], 0, f['sh']), num(st['shotspread'], 1, f['sv'])
    if 'firetics' in st:
        f['tics'] = max(1, int(num(st['firetics'], 0, f['tics'])))
    if 'fullauto' in st:
        f['auto'] = st['fullauto'].strip().lower().startswith('t')
    notes = []
    if 'shotclass' in st and st['shotclass'].strip('" ') and f['proj'] not in ('saw', 'rail'):
        sc = st['shotclass'].strip('" ')
        f['proj'] = SHOTCLASS.get(sc, sc if sc in ('PlasmaBall', 'Rocket', 'BFGBall') else None) or f['proj']
        notes.append('shotclass %s -> %s' % (sc, f['proj']))
    melee = f['proj'] == 'saw' or st.get('firesfrom', '') == 'none'
    if melee:
        f['proj'] = 'saw'
    # firesfrom = reserve: the gun has no magazine (belt / cell fed straight from the reserve); no reload at all
    from_reserve = st.get('firesfrom', '') == 'reserve'
    per_shot = int(num(st.get('roundspershot', '1'), 0, 1))
    for k in ('altmode', 'altburst', 'chargetics', 'spinuptics'):
        if k in st:
            notes.append('%s %s not carried' % (k, st[k]))
    cap = g['capacity'] if g else int(card_keys.get('capacity', 0) or 0)
    if cap <= 0 and not melee:
        cap = {'launcher': 1, 'bfg': 40, 'breakaction': 2}.get(typ, 10)
    reserve = g['reserve'] if g else RESERVE.get(typ, 'Clip')
    mag = 'WMQ_Mag_%s' % cls
    tag = VANILLA_TAG.get(cls) or (st.get('class_name') or st.get('tag') or '"%s"' % cls.replace('WM_VP_', '').replace('WM_', '')).strip('"')
    if st.get('class_ammo'):
        reserve = st['class_ammo'].strip('"')
    sg = spr['gun']
    cs = lambda n: card_keys.get(n, '') if isinstance(card_keys.get(n, ''), str) else ''
    fs = (g and g['snd']) or {}
    firesound = cs('firesound') or st.get('firesound', '').strip('"')
    S = lambda tics, act='': '\t\t%s A %d%s;' % (sg, tics, (' ' + act) if act else '')
    if f['proj'] == 'saw':
        fire = 'A_Saw'
    elif f['proj'] == 'rail':
        fire = 'A_RailAttack(%d, 0, true, "", "", RGF_FULLBRIGHT)' % f['dmg']
    elif f['proj']:
        fire = 'A_FireProjectile("%s")' % f['proj']
    else:
        fire = 'A_FireBullets(%.1f, %.1f, %d, %d, "BulletPuff", FBF_USEAMMO)' % (f['sh'], f['sv'], f['pellets'], f['dmg'])
    L = []
    if not melee and not from_reserve:
        L += ['class %s : Ammo { Default { Inventory.MaxAmount %d; Ammo.BackpackMaxAmount %d; +INVENTORY.IGNORESKILL } }' % (mag, cap, cap), '']
    L += ['class %s : WMQ_Gun' % cls, '{', '\tDefault', '\t{',
          '\t\tTag "%s";' % tag, '\t\tWeapon.SlotNumber %d;' % slot, '\t\tWeapon.SelectionOrder %d;' % order,
          '\t\tInventory.PickupMessage "Picked up the %s";' % tag]
    if melee:
        L += ['\t\tWeapon.Kickback 0;', '\t\t+WEAPON.MELEEWEAPON']
    elif from_reserve:
        L += ['\t\tWeapon.AmmoType1 "%s";' % reserve, '\t\tWeapon.AmmoUse1 %d;' % per_shot, '\t\tWeapon.AmmoGive1 %d;' % max(cap, 20)]
    else:
        L += ['\t\tWeapon.AmmoType1 "%s";' % mag, '\t\tWeapon.AmmoUse1 %d;' % per_shot, '\t\tWeapon.AmmoGive1 %d;' % cap,
              '\t\tWeapon.AmmoType2 "%s";' % reserve, '\t\tWeapon.AmmoUse2 0;', '\t\tWeapon.AmmoGive2 %d;' % (cap * 2),
              '\t\tWMQ_Gun.Capacity %d;' % cap]
    L += ['\t\tWMQ_Gun.FireSound "%s";' % firesound, '\t\tWMQ_Gun.DrySound "%s";' % (cs('drysound') or 'wm/dry'),
          '\t\tWMQ_Gun.MagOutSound "%s";' % fs.get('out', ''), '\t\tWMQ_Gun.MagInSound "%s";' % fs.get('inn', ''),
          '\t\tWMQ_Gun.RackSound "%s";' % fs.get('back', ''),
          '\t}', '', '\tStates', '\t{',
          '\tSpawn:', '\t\t%s A -1;' % spr['pick'], '\t\tStop;',
          '\tReady:', S(1, 'A_WeaponReady(%s)' % ('WRF_ALLOWRELOAD' if not melee else '0')), '\t\tLoop;',
          '\tDeselect:', S(1, 'A_Lower(12)'), '\t\tLoop;',
          '\tSelect:', S(1, 'A_Raise(12)'), '\t\tLoop;']
    if melee:
        L += ['\tFire:', S(0, 'A_StartSound(invoker.fireSound, CHAN_WEAPON)'), S(f['tics'], fire), S(0, 'A_ReFire'), '\t\tGoto Ready;',
              '\t}', '}', '']
        return L, notes
    L += ['\tFire:', S(0, 'A_JumpIfNoAmmo("Dry")'), S(0, 'A_StartSound(invoker.fireSound, CHAN_WEAPON)')]
    if 'chargetics' in st:
        L += [S(int(num(st['chargetics'], 0, 20)))]
    L += [S(f['tics'], fire)]
    if 'releasetics' in st:
        L += [S(int(num(st['releasetics'], 0, 0)))]
    if f['auto']:
        L += [S(0, 'A_ReFire')]
    if from_reserve:
        L += ['\t\tGoto Ready;', '\tDry:', S(0, 'A_StartSound(invoker.drySound, CHAN_WEAPON)'), S(8), '\t\tGoto Ready;', '\t}', '}', '']
        return L, notes
    L += ['\t\tGoto Ready;',
          '\tDry:', S(0, 'A_StartSound(invoker.drySound, CHAN_WEAPON)'), S(8), '\t\tGoto Ready;',
          '\tReload:', S(0, 'A_JumpIfInventory("%s", %d, "Ready")' % (mag, cap)),
          S(0, 'A_JumpIfInventory("%s", 1, "%s")' % (reserve, 'RSR_Start' if has_rsr else 'RSR_Stock')), '\t\tGoto Ready;']
    if has_rsr:
        L += rsr_states(cls, sg, mag, reserve, cap, bool(g['handle_surfs']))
    L += ['\tRSR_Stock:\t\t// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun',
          S(10, 'A_StartSound(invoker.magOutSound, CHAN_WEAPON)'), S(10), S(10, 'A_StartSound(invoker.magInSound, CHAN_WEAPON)'),
          '\tRSR_StockFill:', S(0, 'A_JumpIfInventory("%s", %d, "RSR_StockDone")' % (mag, cap)),
          S(0, 'A_JumpIfInventory("%s", 1, "RSR_StockFillA")' % reserve), '\t\tGoto RSR_StockDone;',
          '\tRSR_StockFillA:', S(0, 'A_GiveInventory("%s", 1)' % mag), S(0, 'A_TakeInventory("%s", 1, TIF_NOTAKEINFINITE)' % reserve),
          '\t\tGoto RSR_StockFill;',
          '\tRSR_StockDone:', S(8), '\t\tGoto Ready;',
          '\t}', '}', '']
    return L, notes


def rsr_states(cls, sg, mag, reserve, cap, handle):
    """the Quest runtime's weapon-side states: rsr_patch.bd_block / WAIT / fill_loop in ZScript
    (semicolons, label jumps), with this pack's own items. No chambered round is kept (keep 1);
    the charge token is given only when the gun was empty (rsr_patch charge='empty')."""
    nomag = 'RSR_NoMag_%s' % cls
    held = 'RSR_Held_%s' % cls
    def S0(a):      # the ; goes before any trailing comment
        a, _, c = a.partition('\t//')
        return '\t\t%s A 0 %s;%s' % (sg, a, ('\t//' + c) if c else '')
    L = ['\t// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.',
         '\tRSR_Start:', S0('A_TakeInventory("RSR_Go", 1)'), S0('A_GiveInventory("RSR_Start", 1)'),
         S0('A_JumpIfInventory("RSR_Go", 1, "RSR_Out")'), '\t\tGoto RSR_Stock;',
         '\tRSR_Out:', S0('A_TakeInventory("RSR_Go", 1)'),
         S0('A_JumpIfInventory("%s", 1, "RSR_Wait")\t// no magazine in the gun' % nomag)]
    if handle:
        L.append(S0('A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled")\t// a magazine in, the handle still to pull'))
    L += [S0('A_GiveInventory("RSR_MagOut", 1)\t// the magazine drops out'),
          '\tRSR_Unload:\t\t// its rounds are held aside; they come back when a magazine is home',
          S0('A_JumpIfInventory("%s", 1, "RSR_Unload1")' % mag),
          S0('A_GiveInventory("%s", 1)' % nomag), '\t\tGoto RSR_Wait;',
          '\tRSR_Unload1:', S0('A_TakeInventory("%s", 1)' % mag), S0('A_GiveInventory("%s", 1)' % held), '\t\tGoto RSR_Unload;',
          '\tRSR_Wait:\t\t// the gun as the script shows it; the script runs every tic',
          '\t\t"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);',
          '\t\t"####" "#" 0 A_GiveInventory("RSR_Tick", 1);',
          '\t\t"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");',
          '\t\t"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");', '\t\tGoto RSR_Wait;',
          '\tRSR_Fill:\t\t// the magazine is home', S0('A_TakeInventory("RSR_Seated", 1)'), S0('A_TakeInventory("%s", 1)' % nomag),
          '\tRSR_Return:\t\t// the held rounds first', S0('A_JumpIfInventory("%s", 1, "RSR_Return1")' % held), '\t\tGoto RSR_FillGo;',
          '\tRSR_Return1:', S0('A_TakeInventory("%s", 1)' % held), S0('A_GiveInventory("%s", 1)' % mag), '\t\tGoto RSR_Return;',
          '\tRSR_FillGo:']
    if handle:
        L += [S0('A_JumpIfInventory("%s", 1, "RSR_FillA")\t// the gun was not empty: no handle' % mag),
              S0('A_GiveInventory("RSR_Charge", 1)\t// it was empty: the handle is due (vreload.zs ChargeToken)')]
    L += ['\tRSR_FillA:', S0('A_JumpIfInventory("%s", %d, "RSR_Filled")' % (mag, cap)),
          S0('A_JumpIfInventory("%s", 1, "RSR_FillAa")' % reserve), '\t\tGoto RSR_Filled;',
          '\tRSR_FillAa:', S0('A_GiveInventory("%s", 1)' % mag), S0('A_TakeInventory("%s", 1, TIF_NOTAKEINFINITE)' % reserve), '\t\tGoto RSR_FillA;',
          '\tRSR_Filled:', S0('A_GiveInventory("RSR_Filled", 1)\t// the script: the handle if it is due, else done'), '\t\tGoto RSR_Wait;',
          '\tRSR_Done:', S0('A_TakeInventory("RSR_Done", 1)'), S0('A_TakeInventory("RSR_Charge", 1)'), '\t\tGoto Ready;']
    return L


BASE_ZS = '''// WMQ_Gun: the base of every weapon in this pack. Stock QuestZDoom 17.x, no engine changes.
// Fire comes from the set's own numbers (WMSHEET / the WM_Gun Default blocks); the VR reload is
// zscript/rsr (the tables rsr_guns.zs are generated from the REMA cards by genpack.py).
class WMQ_Gun : Weapon
{
	int capacity;
	String fireSound, drySound, magOutSound, magInSound, rackSound;
	property Capacity: capacity;
	property FireSound: fireSound;
	property DrySound: drySound;
	property MagOutSound: magOutSound;
	property MagInSound: magInSound;
	property RackSound: rackSound;

	Default
	{
		Weapon.Kickback 50;
		Weapon.BobStyle "Normal";
		+WEAPON.NOALERT
	}
}

// The punch (zscript/rsq/fists.zs lands one from the hand, the way the blow went): Doom's own
// fist numbers, 2 x 1d10, berserk x10. A short-lived projectile so it reaches about 32 units.
class WMQ_Punch : Actor
{
	Default
	{
		Projectile;
		+NOGRAVITY
		+FORCEXYBILLBOARD
		Radius 8;
		Height 8;
		Speed 16;
		DamageFunction (2 * random(1, 10));
		RenderStyle "None";
	}
	States
	{
	Spawn:
		TNT1 A 2;
		Stop;
	Death:
	XDeath:
		TNT1 A 1 A_StartSound("*fist", CHAN_WEAPON);
		Stop;
	}
}

class WMQ_PunchBerserk : WMQ_Punch
{
	Default
	{
		DamageFunction (20 * random(1, 10));
	}
}
'''


# ---------------------------------------------------------------- main
def main(root, kit, out, which):
    members = set_members(root, which)
    cards = {w['cls']: w for w in c2q.load_cards(root)}
    stats = gun_stats(root)
    sheets = sheet_stats(root)
    scales = c2q.modeldef_scales(root)
    outdir = os.path.join(out, 'RSQ_%s' % which)
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    for d in ('zscript/rsr', 'zscript/rsq', 'zscript/rsvr', 'zscript/wmq', 'sounds'):
        os.makedirs(os.path.join(outdir, d), exist_ok=True)

    guns, surveys, weapons, modeldef_gun, report = [], {}, [], [], []
    slot_of = {}
    spr_names = set()
    slot_order = {}
    # Doom's weapons each replaced by ONE gun of the set: the first of its type in set order, a class
    # named *Doom* preferred (WM_PumpDoom over WM_PumpM37). The rest are extra slots / cheats.
    DOOM = {'pistol': 'Pistol', 'shotgun': 'Shotgun', 'breakaction': 'SuperShotgun', 'chaingun': 'Chaingun',
            'launcher': 'RocketLauncher', 'plasma': 'PlasmaRifle', 'bfg': 'BFG9000', 'chainsaw': 'Chainsaw'}
    PREF = {'M4A3', 'PlasmaRifle', 'RocketLauncher', 'BFG', 'Chaingun', 'PumpDoom', 'SSG', 'Chainsaw'}   # the Doom-weapon stand-ins
    rank = lambda c: 2 if c.replace('WM_VP_', '').replace('WM_', '') in PREF else 1 if 'doom' in c.lower() else 0
    replaces = {}
    for cls, card_cls in members.items():
        w = cards.get(card_cls)
        if w:
            t, _ = gun_type(cls, w['keys'])
            if t in DOOM and (t not in replaces or rank(cls) > rank(replaces[t])):
                replaces[t] = cls
    # a set with rifles / SMGs and no chaingun: its first rifle takes the chaingun pickup
    if 'chaingun' not in replaces:
        for cls, card_cls in members.items():
            w = cards.get(card_cls)
            if w and gun_type(cls, w['keys'])[0] in ('rifle', 'smg'):
                replaces['rifle' if gun_type(cls, w['keys'])[0] == 'rifle' else 'smg'] = cls; DOOM[gun_type(cls, w['keys'])[0]] = 'Chaingun'; break
    i = 0
    for cls, card_cls in members.items():
        w = cards.get(card_cls)
        if not w:
            report.append((cls, 'NO CARD')); continue
        mp = c2q.model_path(root, w)
        if not mp or not os.path.exists(mp):
            report.append((cls, 'no model %s' % mp)); continue
        i += 1
        base = os.path.basename(mp).lower()
        ws_ = scales.get(base)
        if ws_ is None:
            report.append((cls, 'no MODELDEF scale')); continue
        hud = tuple(round(s / c2q.WORLD_PER_HUD, 4) for s in ws_)
        # keep REMA's x sign: it is the un-mirroring of each mesh (a +x mesh forced to -x ejects left)
        scale = ((-1.0 if ws_[0] < 0 else 1.0) * abs(hud[0]), abs(hud[1]), abs(hud[2]))
        off = c2q.offset_for(w['grip']['palm'], scale)
        fr = c2q.rest_frame(w, mp)
        geo = c2q.geometry(w, scale, off)
        rec = dict(hud_scale=scale, offset=off, rest_frame=fr, parts=geo['parts'], type=w['keys'].get('type'))
        # sprite names: Q + two base36 digits + role letter
        b36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        code = b36[i // 36] + b36[i % 36]
        spr = dict(gun='Q%sR' % code, m='Q%sM' % code, p='Q%sP' % code, w='Q%sW' % code, pick='Q%sS' % code)
        is_iqm = mp.lower().endswith('.iqm')
        bake_notes = []
        model = w['keys']['model'] if isinstance(w['keys']['model'], list) else [None, w['keys']['model']]
        if is_iqm:
            mp_src = mp
            mp, bake_notes = bake_iqm(w, mp, outdir, model[0], root)
            w['keys']['model'] = [model[0], os.path.basename(mp)]
            w['keys'].pop('skin', None)      # the baked surfaces carry their material names
            fr = 0
        nfr, surfs = md3_surfaces(mp); names = [s['name'] for s in surfs]
        g, sv = build_gun(root, w, cls, rec, names, surfs, nfr, spr)
        if g:
            g['mesh'] = mp
            g['notes'] = bake_notes + g.get('notes', [])
            if is_iqm:
                g['skins'] = [x['shader'] for x in surfs]     # baked: each surface its own material
        baked_skins = [x['shader'] for x in surfs] if is_iqm else None
        st = dict(stats.get(cls, stats.get(card_cls, {})))
        st.update(sheets.get(cls) or sheets.get(card_cls) or {})
        typ, typ_src = gun_type(cls, w['keys'])
        if st.get('firesfrom') in ('reserve', 'none') and g:
            g, sv = None, 'fires from the %s (sheet firesfrom): no magazine' % st['firesfrom']
        # Doom's slots by type: the set's own SlotNumbers are REMA's dev lane (8, 9, 0), not a Quest layout
        slot = SLOT.get(typ, 1)
        slot_of[cls] = slot
        order = int(num(st.get('class_selectionorder', '0'), 0, 0)) or ORDER.get(typ, 1000)
        model = w['keys']['model'] if isinstance(w['keys']['model'], list) else [None, w['keys']['model']]
        skin = w['keys'].get('skin') if isinstance(w['keys'].get('skin'), list) else [model[0], w['keys'].get('skin')]
        # the gun's own MODELDEF block (ready frame on every state)
        skin_lines = [('\tSkin 0 "%s"' % skin[1]) if skin[1] else ''] if not baked_skins else \
            ['\tSurfaceSkin 0 %d "%s"' % (si, sk) for si, sk in enumerate(baked_skins)]
        modeldef_gun += ['Model %s' % cls, '{', '\tPath "%s"' % model[0], '\tModel 0 "%s"' % model[1]] + skin_lines + [
                         '\tScale %.4f %.4f %.4f' % scale, '\tOffset %.4f %.4f 0.0' % (off[0], off[1]), '\tZOffset %.4f' % off[2],
                         '\tNoInterpolation', '\tFrameIndex %s A 0 %d' % (spr['gun'], fr), '}', '',
                         '// its pickup in the world: the same mesh at REMA\'s world scale (HUD x 0.34)',
                         'Model %s' % cls, '{', '\tPath "%s"' % model[0], '\tModel 0 "%s"' % model[1]] + skin_lines + [
                         '\tScale %.4f %.4f %.4f' % tuple(abs(x) * c2q.WORLD_PER_HUD for x in scale), '\tZOffset 8.0', '\tAngleOffset 90',
                         '\tFrameIndex %s A 0 %d' % (spr['pick'], fr), '}', '']
        if g:
            g['type'] = w['keys'].get('type')
            g['capacity'] = int(w['keys'].get('capacity', 10))
            guns.append(g); surveys[cls] = sv
            report.append((cls, 'VR reload: magazine%s%s%s' % (' + handle' if g['handle_surfs'] else '',
                           ', slide lock %s [%s]' % (g['slide_lock'], g['slide_lock_src']) if g['handle_surfs'] else '',
                           ''.join('; ' + n for n in g.get('notes', [])))))
        else:
            report.append((cls, 'stock reload (%s)' % sv))
        # a render sheet per gun (side + bottom, Quest placement, grab points): the eyeball check
        try:
            os.makedirs(os.path.join(outdir, '_sheets'), exist_ok=True)
            c2q.sheet(mp, fr, scale, off, geo, os.path.join(outdir, '_sheets', cls + '.png'), '%s  [%s]' % (cls, which))
        except Exception as e:
            report.append((cls, 'sheet failed: %s' % e))
        ep = geo.get('ejectport')
        side = 'eject port %s (L %+.1f)' % ('RIGHT' if ep[1] < -0.3 else 'LEFT' if ep[1] > 0.3 else 'centre', ep[1]) if ep else 'no eject port on card'
        wl, notes = weapon_zs(cls, g, st, spr, bool(g), slot, order, w['keys'], typ)
        if replaces.get(typ) == cls:
            wl = [l.replace('class %s : WMQ_Gun' % cls, 'class %s : WMQ_Gun replaces %s' % (cls, DOOM[typ])) for l in wl]
            notes.append('replaces %s' % DOOM[typ])
        notes.append('scale x %+.3f (REMA sign); %s' % (scale[0], side))
        weapons += wl
        report[-1] = (report[-1][0], report[-1][1] + '; fire as %s [%s], slot %d%s' % (typ, typ_src, slot, ''.join('; ' + n for n in notes)))
        # files to ship
        ship = set([mp]) if mp.startswith(root) else set()
        for sk in (skin[1],):
            if sk: ship.add(os.path.join(root, model[0], sk))
        for f in ship:
            dst = os.path.join(outdir, os.path.relpath(f, root).replace('\\', '/'))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(f): shutil.copy2(f, dst)
        if g:
            open(os.path.join(outdir, model[0], CLEAR), 'wb').write(CLEAR_PNG)

    # ---- the reload tables and MODELDEF.rsr through the kit's own generator
    comp = [gen_rsr.compute(dict(g), {g['key']: surveys[g['cls']]}) for g in guns]
    names = [n for g in comp for n in (g['spr_gun'], g['spr_part'], g['spr_world'])]
    assert len(names) == len(set(names))
    zl = gen_rsr.zs(comp)
    # SlideLock: this pack's vreload.zs asks the table instead of BD22's fixed indexes (assemble.py)
    sl = ['', '\t// the action locks open on an empty gun (card holdopen, or genpack\'s default rule)',
          '\tclearscope static bool SlideLock(int i)', '\t{', '\t\tstatic const bool v[] = { false, %s };' % ', '.join(
              'true' if g.get('slide_lock') else 'false' for g in comp), '\t\treturn i > 0 && i < v.Size() && v[i];', '\t}']
    close = zl.index('}')
    zl = zl[:close] + sl + zl[close:]
    open(os.path.join(outdir, 'zscript/rsr/rsr_guns.zs'), 'w').write('\n'.join(zl) + '\n')
    md = []
    for g in comp:
        md += gen_rsr.modeldef(g)
    open(os.path.join(outdir, 'MODELDEF.rsr'), 'w').write('\n'.join(md) + '\n')
    open(os.path.join(outdir, 'MODELDEF.wmq'), 'w').write('// the guns themselves (genpack.py from the REMA cards)\n' + '\n'.join(modeldef_gun))
    # pickup sprites: every gun's Spawn shows a sprite the engine must know; declared by the class below
    spawn = ['class WMQ_Sprites : Actor', '{', '\tStates', '\t{', '\tSpawn:']
    for n in sorted({l.split()[0] for l in weapons if l.strip().startswith('Q') and l.strip().split()[0].endswith('S') and len(l.strip().split()[0]) == 4}):
        spawn.append('\t\t%s A 0;' % n)
    for n in sorted({l.strip().split()[0] for l in weapons if l.strip().startswith('Q') and len(l.strip().split()[0]) == 4}):
        spawn.append('\t\t%s A 0;' % n)
    spawn += ['\t\tStop;', '\t}', '}', '']
    open(os.path.join(outdir, 'zscript/wmq/weapons.zs'), 'w').write(BASE_ZS + '\n' + '\n'.join(spawn + weapons))
    # placeholder sprite lumps: a MODELDEF keys on sprite+frame and the engine wants a lump behind
    # each ("has no frames" otherwise, kit docs/RS_Quest_README.md). Our Q?? names are new, so
    # nothing real is shadowed; TNT1 and the hand sprites (no models here) are left alone.
    os.makedirs(os.path.join(outdir, 'sprites'), exist_ok=True)
    alltext = '\n'.join(weapons) + open(os.path.join(outdir, 'zscript/rsr/rsr_guns.zs')).read()
    frames = set(re.findall(r'^\s*(?:[A-Za-z_][\w.]*:\s*)?(Q[0-9A-Z]{2}[RMPWS])\s+([A-Z]+)\s+-?\d+', alltext, re.M))
    nlumps = 0
    for spr, fr in frames:
        for ch in fr:
            open(os.path.join(outdir, 'sprites', '%s%s0.png' % (spr, ch)), 'wb').write(CLEAR_PNG); nlumps += 1
    report.append(('(sprites)', '%d placeholder lumps' % nlumps))
    # sounds: every name the weapons and the reload tables use, resolved to SNDINFO + files
    import sndpack
    used = set(re.findall(r'"((?:wm|rsr|rs|vp|bd)/[A-Za-z0-9_/]+)"', '\n'.join(weapons)))
    used |= set(re.findall(r'"([A-Za-z0-9_]+/[A-Za-z0-9_/]+)"', open(os.path.join(outdir, 'zscript/rsr/rsr_guns.zs')).read()))
    used -= {'wm/dry/'}
    snd_ok, snd_bad = sndpack.resolve(used, [(os.path.join(root, 'SNDINFO.txt'), root),
                                             (os.path.join(root, 'RS_Modern/SNDINFO.txt'), os.path.join(root, 'RS_Modern')),
                                             (os.path.join(os.path.dirname(root.rstrip('/')), 'rs_vr_reload/SNDINFO.txt'), os.path.join(os.path.dirname(root.rstrip('/')), 'rs_vr_reload'))], outdir)
    report.append(('(sounds)', '%d resolved%s' % (len(snd_ok), ', UNRESOLVED: ' + ', '.join(snd_bad) if snd_bad else '')))
    # the player: Doom's own, starting with the fist and THIS set's pistol, Doom's slot layout with
    # the set's guns in it (the start gun is the player class's business, not a replacement's)
    by_slot = {}
    for cls in members:
        by_slot.setdefault(slot_of.get(cls, 1), []).append(cls)
    pl = ['', 'class RSQ_Player : DoomPlayer', '{', '\tDefault', '\t{', '\t\tPlayer.DisplayName "Doomguy";',
          '\t\tPlayer.StartItem "%s";' % (replaces.get('pistol') or next(iter(members))), '\t\tPlayer.StartItem "Fist";',
          '\t\tPlayer.StartItem "Clip", 50;']
    for sl in sorted(by_slot):
        pl.append('\t\tPlayer.WeaponSlot %d, %s;' % (sl, ', '.join('"%s"' % c for c in by_slot[sl]) + (', "Fist"' if sl == 1 else '')))
    if 1 not in by_slot:
        pl.append('\t\tPlayer.WeaponSlot 1, "Fist";')
    pl += ['\t}', '}', '']
    weapons += pl
    open(os.path.join(outdir, 'zscript/wmq/weapons.zs'), 'w').write(BASE_ZS + '\n' + '\n'.join(spawn + weapons))
    open(os.path.join(outdir, 'MAPINFO.player'), 'w').write('// the set\'s player: starts with its pistol\ngameinfo\n{\n\tPlayerClasses = "RSQ_Player"\n}\n')
    json.dump(dict(set=which, guns=[g['cls'] for g in comp], report=report, sounds=dict(ok=snd_ok, unresolved=snd_bad),
                   geometry={g['cls']: {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in g.items()
                                        if k in ('well', 'axis', 'mouth', 'grip', 'mag_len', 'grab', 'pull', 'travel', 'scale', 'off', 'ready_frame')} for g in comp}),
              open(os.path.join(outdir, 'genpack_report.json'), 'w'), indent=1)
    for cls, what in report:
        print('%-24s %s' % (cls, what))
    print('->', outdir, '%d guns, %d with VR reload' % (len([r for r in report if not r[0].startswith('(')]), len(comp)))
    return outdir


CLEAR_PNG = bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d4944415478da63f8ffff3f0300050001015a0ab6e30000000049454e44ae426082')

if __name__ == '__main__':
    main(*sys.argv[1:5])
