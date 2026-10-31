#!/usr/bin/env python3
"""card_mag.py -- magazine reload rows for the MS 1.5 card donors, measured at the place each donor is DRAWN.

    python3 tools_kit/card_mag.py [--dry] [--only MS_BD_Rifle,...]

2.0 made its magazine rows with tools_kit/regen_rows.py: card2quest.geometry -> genpack.build_gun -> gen_rsr, fed
by the old WMCARD cards. This feeds the SAME chain (regen_rows.main, unchanged) from the MS 1.5 cards
(RSQ_WeaponDepot md3label), translated part for part:

  card `mag`  surf N, rest, mag_well mouth   -> part role feed, slide; out-axis = mouth -> rest (the way it comes
                                                 out), distance = the magazine's own length along it, grab = rest
  card `slide` / `bolt` / `handle`          -> part role action, slide (a charging handle or slide the hand racks):
                                                 only a part that slides BACK along the bore (axis x <= -0.9) by 2+
                                                 units, as regen_rows.motion_handle requires; never on a shotgun
  card `grip line` / `trigger` / `support`   -> grip palm (the line's middle), triggerat, supportat
  card `muzzle`, `bore`, archetype           -> keys muzzle, barrel, type
and the donor's own generated block (Scale, Offset + ZOffset, rest frame, Path/Model/Skin) for the placement.

regen_rows then builds each gun, rewrites the donor's own slot in place (or gives it one), writes MODELDEF.cards
whole and the card sprites. Its checks stand: a magazine that resolves to the gun's body, or a well more than
40 cm from the grip, is held (the mod's own reload) and said so.
"""
import os, re, sys, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import regen_rows as RR  # noqa: E402
import card_pump as CP  # noqa: E402  (card part parser, donor blocks)

V3 = CP.V3
TYPE = {'pistol_mag': 'pistol', 'smg': 'smg', 'rifle': 'rifle', 'shotgun_mag': 'shotgun', 'shotgun_drum': 'shotgun',
        'energy': 'plasma', 'cell': 'plasma', 'launcher': 'launcher', 'rocket': 'rocket', 'chaingun': 'chaingun',
        'machinegun': 'machinegun', 'flamethrower': 'flamethrower', 'railgun': 'railgun', 'revolver': 'revolver'}


def card_to_w(donor, text, names, blk):
    parts, _ = CP.card_parts(text)
    mag = (parts.get('mag') or [None])[0]
    if not mag:
        return None, 'no magazine part on the card'
    mw = re.search(r'^\s+mag_well\s+' + V3 + r'\s+mouth\s+' + V3, text, re.M)
    rest = mag['rest']
    if mw:
        mouth = np.array([float(x) for x in mw.group(4, 5, 6)])
        out = rest - mouth
        if np.linalg.norm(out) < 0.5:
            out = -mag['axis'] if np.linalg.norm(mag['axis']) > 0 else np.array([0, 0, -1.0])
    else:
        out = mag['axis'] if np.linalg.norm(mag['axis']) > 0 else np.array([0, 0, -1.0])
    out = out / np.linalg.norm(out)
    arch = (re.search(r'archetype\s+(\S+)', text) or [None, ''])[1]
    typ = TYPE.get(arch, 'rifle')
    gl = re.search(r'^\s+grip\s+line\s+' + V3 + r'\s+' + V3 + r'\s+trigger\s+' + V3, text, re.M)
    grip = {}
    if gl:
        a = np.array([float(x) for x in gl.group(1, 2, 3)]); b = np.array([float(x) for x in gl.group(4, 5, 6)])
        grip['palm'] = ((a + b) / 2).round(3).tolist()
        grip['triggerat'] = [float(x) for x in gl.group(7, 8, 9)]
    sp = re.search(r'^\s+support\s+feature\s+\w+\s+' + V3, text, re.M)
    if sp:
        grip['supportat'] = [float(x) for x in sp.group(1, 2, 3)]
    mz = re.search(r'^\s+muzzle\s+' + V3, text, re.M)
    keys = dict(type=typ, barrel=[1.0, 0.0, 0.0], magcenter=rest.round(3).tolist(),
                model=[blk['path'], blk['model']], skin=[blk['path'], blk['skin']])   # the donor's own mesh and skin (genpack reads them)
    if mz:
        keys['muzzle'] = [float(x) for x in mz.group(1, 2, 3)]
    sn = names[mag['surf']] if mag['surf'] < len(names) else 'mag'
    W = {'mag': dict(name='mag', surfaces=[sn], keys=dict(role='feed', subject='magazine', grab=rest.round(3).tolist(), grabradius=2.5),
                     dof=dict(kind='slide', axis=out.round(4).tolist(), distance=float(mag.get('travel') or 0)))}
    order = ['mag']
    if typ not in ('shotgun',):
        for k in ('slide', 'bolt', 'handle'):
            for p in parts.get(k, []):
                if p['axis'][0] <= -0.9 and p['travel'] >= 2.0 and 'bolt' not in W:
                    W['bolt'] = dict(name='bolt', surfaces=[names[p['surf']] if p['surf'] < len(names) else k],
                                     keys=dict(role='action', subject='slide', grab=p['rest'].round(3).tolist(), grabradius=2.5),
                                     dof=dict(kind='slide', axis=p['axis'].round(4).tolist(), distance=float(p['travel'])))
                    order.append('bolt')
    return dict(cls=donor, keys=keys, grip=grip, parts=W, order=order), None


def candidates(only=None):
    blocks = CP.donor_blocks()
    rsr = open(os.path.join(ROOT, 'zscript_depot/rsr/rsr_guns.ms.zs')).read()
    slots = {}
    for d, s in re.findall(r'donor == "(\w+)"\)\s*return (\d+);', rsr):
        slots.setdefault(d, int(s))
    out, notes = [], []
    from rgeo import load_md3
    for card in sorted(glob.glob(os.path.join(ROOT, 'cards/*/*/*.card'))):
        if '.blend' in card or '/_' in card:
            continue
        text = open(card).read()
        if not re.search(r'^\s{4}mag\s+surf', text, re.M):
            continue
        rel = os.path.relpath(os.path.dirname(card), ROOT)
        donor = next((d for d, b in blocks.items() if b['path'] == rel and b['model'] == os.path.basename(card)[:-5] + '.md3'), None)
        if not donor or (only and donor not in only):
            continue
        b = blocks[donor]
        mesh = os.path.join(ROOT, b['path'], b['model'])
        names = [s['name'] for s in load_md3(mesh)]
        w, why = card_to_w(donor, text, names, b)
        if not w:
            notes.append((donor, why)); continue
        # a surface the set's own block leaves unskinned is not drawn by the engine: the layers keep it unseen
        out.append(dict(donor=donor, slot=slots.get(donor, 0), card=w, mesh=mesh, path=b['path'], model=b['model'],
                        skin=b['skin'], skins=[b['skins'].get(i, b['skin'] or 'rsr_clear.png') for i in range(len(names))] if b['skins'] else None, scale=tuple(b['scale']), off=tuple(b['off']), frame=b['frame']))
    return out, notes


def main():
    only = set(sys.argv[sys.argv.index('--only') + 1].split(',')) if '--only' in sys.argv else None
    RR.candidates = lambda _o=None: candidates(None)
    RR.ADD = []
    RR.main('--dry' in sys.argv, only)
    if '--dry' not in sys.argv:
        # the layers mask surfaces with rsr_clear.png, looked up in each layer's own Path (the card folder)
        import shutil
        md = open(os.path.join(ROOT, 'MODELDEF.cards')).read()
        for sec in re.split(r'\n(?=Model\s)', md):
            pm = re.search(r'Path\s+"([^"]+)"', sec)
            if pm and 'rsr_clear.png' in sec and os.path.isdir(os.path.join(ROOT, pm.group(1))):
                dst = os.path.join(ROOT, pm.group(1), 'rsr_clear.png')
                if not os.path.exists(dst):
                    shutil.copy(os.path.join(ROOT, 'reload_1x', 'rsr_clear.png'), dst)


if __name__ == '__main__':
    main()
