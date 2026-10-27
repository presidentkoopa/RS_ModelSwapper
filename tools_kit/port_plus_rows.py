"""port_plus_rows.py -- the five guns left on old _wm rows get the reload their own sets already have.

    python -B tools_kit/port_plus_rows.py [--dry]
    then: python -B tools_kit/regen_rows.py --only <donors>; python -B tools_kit/fix_layer_skins.py

WHY
The Unmaker, Flamethrower2, Bolter, TEC-9 and Hitler's Buzzsaw kept slots 5/8/9/10/11: rows made at the
card's placement with NO layers drawn (no MODELDEF names Q04M..Q0AM), so mid-reload the gun vanished
and the hand held nothing. regen_rows.py skipped them ("card mesh is a _wm rebuild"). Their reloads
already exist and are not re-measured here:
  * Unmaker, Flamethrower2, Bolter, TEC-9: the RS_VR_Weapons model cards that Vanilla+ borrows
    (WMSHEET.plus_*: model = WM_Unmaker / WM_Flamethrower / WM_Bolter / WM_Tec9), measured on the
    static *_wm.md3 that Vanilla+ ships, cut into named parts.
  * Buzzsaw: BD22 Weapons Q's MG42 belt-drum reload (Depot tools/bd22_plus.py 'MG42': card
    BD_Buzzsaw, ref buzzsaw_wm.md3, part magazine), carved from this same HitlersBuzzsaw.md3.

WHAT (per donor)
1. The transform from the reference (_wm) space to the mesh the donor DRAWS, at its rest frame:
   similarity fit (scale, rotation, translation) by vertex correspondence by POSITION (nearest
   neighbour, ICP from the centroids), then every reference vertex's distance to its partner.
2. The drawn mesh is carved by that correspondence (carve_by_ref): same vertices, all frames kept,
   its surfaces split and named as the reference's parts (mag, magazine, canister, flap/lever ...).
3. The card is carried through the transform (points p' = sR p + t, directions R d, lengths s*L) onto
   the drawn mesh, cls = the donor, and written to WMCARD.plusport. regen_rows.py then builds the row
   and its layers at the donor's own placement (the same chain as the 31 regenerated donors).
"""
import os, re, sys, json
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import genpack, carve_by_ref, placement_audit as PA

POINTS = {'muzzle', 'ejectport', 'magcenter', 'triggerat', 'supportat', 'palm', 'seat', 'grab', 'handseat',
          'at', 'pivot', 'exhaustport'}
DIRS = {'barrel', 'ejectdir', 'axis', 'dir', 'handaxis', 'exhaustdir', 'twistaxis'}
LENGTHS = {'distance', 'grabradius', 'magscale', 'roundscale', 'linkscale'}
NUM3 = re.compile(r'^\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*$')

V = 'models/vanilla'
# donor -> (reference mesh with named parts, source card file, source card name, card's recorded carry (or None))
GUNS = {
    'MS_BD_Unmaker':        (V + '/unmaker/Unmaker/unmaker_wm.md3', 'cards_carried/WM_Unmaker.card', 'WM_Unmaker', 'WM_Unmaker'),
    'MS_brt_Unmaker':       (V + '/unmaker/Unmaker/unmaker_wm.md3', 'cards_carried/WM_Unmaker.card', 'WM_Unmaker', 'WM_Unmaker'),
    'MS_BD_Flamethrower2':  (V + '/flamers/Flamethrower2/flamethrower2_wm.md3', 'WMCARD.13_flamethrower', 'MS_BD_Flamethrower2', None),
    'MS_brt_Flamethrower2': (V + '/flamers/Flamethrower2/flamethrower2_wm.md3', 'WMCARD.13_flamethrower', 'MS_BD_Flamethrower2', None),
    'MS_MG_Bolter':         (V + '/plasma/Bolter/bolter_wm.md3', 'WMCARD.08_cell', 'MS_MG_Bolter', None),
    'MS_meat_Bolter':       (V + '/plasma/Bolter/bolter_wm.md3', 'WMCARD.08_cell', 'MS_MG_Bolter', None),
    'MS_MG_Tec9':           (V + '/smgs/Tec9/tec9_wm.md3', 'WMCARD.07_smg', 'MS_MG_Tec9', None),
    'MS_meat_TEC9':         (V + '/smgs/Tec9/tec9_wm.md3', 'WMCARD.07_smg', 'MS_MG_Tec9', None),
    'MS_brt_HitlersBuzzsaw': ('models/bd22/bd22/buzzsaw_wm.md3', 'WMCARD.bd22', 'MS_Buzzsaw', None),
}


def card_text(path, name):
    t = open(os.path.join(ROOT, path), encoding='utf-8', errors='replace').read()
    m = re.search(r'(?ms)^weapon\s+"%s"\s*$.*?(?=^weapon\s+"|\Z)' % re.escape(name), t)
    return m.group(0)


def pts(path, frame=0):
    _, ss = genpack.md3_surfaces(os.path.join(ROOT, path))
    return np.vstack([s['xyz'][min(frame, s['xyz'].shape[0] - 1)] for s in ss])


def umeyama(A, B):
    ca, cb = A.mean(0), B.mean(0); A0, B0 = A - ca, B - cb
    U, S, Vt = np.linalg.svd(B0.T @ A0 / len(A))
    D = np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))])
    R = U @ D @ Vt; s = np.trace(np.diag(S) @ D) / (A0 ** 2).sum(1).mean()
    return s, R, cb - s * R @ ca


def solve(ref, tgt):
    """ref -> tgt similarity by nearest-position correspondence (vertex ORDER is never used)"""
    tree = cKDTree(tgt)
    s, R, t = 1.0, np.eye(3), tgt.mean(0) - ref.mean(0)
    for _ in range(80):
        _, idx = tree.query(s * ref @ R.T + t)
        s, R, t = umeyama(ref, tgt[idx])
    d, _ = tree.query(s * ref @ R.T + t)
    back, _ = cKDTree(s * ref @ R.T + t).query(tgt)
    return s, R, t, d, back


def carry(text, s, R, t, donor, mesh):
    def conv(line):
        m = re.match(r'^(\s*)([a-z_]+)(\s*=\s*)(.*?)(\s*(?:#.*)?)$', line)
        if not m:
            return line
        ind, key, eq, val, tail = m.groups()
        v3 = NUM3.match(val)
        if v3 and (key in POINTS or key in DIRS):
            p = np.array([float(x) for x in v3.groups()])
            q = s * R @ p + t if key in POINTS else R @ p
            return '%s%s%s%.3f, %.3f, %.3f%s' % (ind, key, eq, q[0], q[1], q[2], tail)
        if key in LENGTHS and re.match(r'^-?[\d.]+$', val):
            return '%s%s%s%.3f%s' % (ind, key, eq, float(val) * s, tail)
        return line
    out = [conv(l) for l in text.splitlines()]
    d, b = os.path.split(mesh)
    out = [re.sub(r'^weapon\s+"[^"]+"', 'weapon "%s"' % donor, l) for l in out]
    out = [re.sub(r'^(\s*model\s*=\s*).*$', r'\g<1>"%s" "%s"' % (d, b), l) for l in out]
    return '\n'.join(out).rstrip() + '\n'


def uncarry(text, cls):
    """cards_carried/<cls>.card -> the card in its _wm space again (its own recorded move, inverted)"""
    tf = json.load(open(os.path.join(ROOT, 'card_transforms.json')))[cls]
    R = np.array(tf['R']); t = np.array(tf['t'])
    return carry(text, 1.0, R.T, -R.T @ t, cls, 'x/x').replace('model     = "x" "x"', 'model     = "-" "-"')


def main(dry):
    blocks = PA.donor_blocks(); rest = PA.shelf_rest()
    cards, report = [], {}
    for donor, (ref, cfile, cname, carried) in GUNS.items():
        body = blocks[donor]
        path = re.search(r'Path\s+"([^"]+)"', body).group(1); model = re.search(r'Model\s+0\s+"([^"]+)"', body).group(1)
        mesh = os.path.relpath(PA.resolve(os.path.join(ROOT, path, model)), ROOT).replace('\\', '/')
        fr = rest.get(donor, 0)
        A, B = pts(ref), pts(mesh, fr)
        s, R, t, d, back = solve(A, B)
        rot = float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
        rec = dict(ref=ref, mesh=mesh, frame=fr, nref=len(A), nmesh=len(B), scale=round(float(s), 6), rot_deg=round(rot, 4),
                   t=[round(float(x), 4) for x in t], max_ref_to_mesh=round(float(d.max()), 4),
                   max_mesh_to_ref=round(float(back.max()), 4), within_0_05=int((d <= 0.05).sum()))
        report[donor] = rec
        print('%-22s %s -> %s @f%d  verts %d/%d  scale %.5f rot %.3f t %s  max %.4f / %.4f'
              % (donor, ref, mesh, fr, len(A), len(B), s, rot, rec['t'], d.max(), back.max()))
        carve_fr = fr
        if fr and (d.max() > 0.05 or back.max() > 0.05):
            # a rest frame that is a pose (MS_BD_Unmaker rests on frame 4, tilted into its 'lower'): the
            # reference is matched to frame 0 by position, and frame 0 -> rest frame is the BODY's own
            # rigid move inside the same file (vertex i is vertex i across frames of one md3)
            A0 = pts(mesh, 0)
            s, R, t, d, back = solve(A, A0)
            _, ss = genpack.md3_surfaces(os.path.join(ROOT, mesh))
            body = max(ss, key=lambda x: x['xyz'].shape[1])
            s2, R2, t2 = umeyama(body['xyz'][0], body['xyz'][fr])
            rb = np.linalg.norm(s2 * body['xyz'][0] @ R2.T + t2 - body['xyz'][fr], axis=1)
            parts = {}
            for x in ss:
                if x is body: continue
                sp, Rp, tp = umeyama(x['xyz'][0], x['xyz'][fr])
                parts[x['name'] + '/%d' % x['xyz'].shape[1]] = dict(
                    off_body=round(float(np.linalg.norm(s2 * x['xyz'][0] @ R2.T + t2 - x['xyz'][fr], axis=1).max()), 3))
            rec.update(frame0=dict(scale=float(s), max=float(max(d.max(), back.max()))), body_f0_to_rest=dict(
                scale=round(float(s2), 5), rot_deg=round(float(np.degrees(np.arccos(np.clip((np.trace(R2) - 1) / 2, -1, 1)))), 3),
                t=[round(float(x), 3) for x in t2], max=round(float(rb.max()), 4)), parts_vs_body_at_rest=parts)
            print('   frame 0: scale %.5f max %.4f; body f0->f%d rot %.3f max %.4f; other surfaces off the body by %s'
                  % (s, max(d.max(), back.max()), fr, rec['body_f0_to_rest']['rot_deg'], rb.max(), parts))
            if max(d.max(), back.max()) > 0.05 or rb.max() > 0.05:
                print('   NOT the same vertices: left as it is'); continue
            R, t = R2 @ R, s2 * R2 @ t + t2; s = s * s2
            rot = float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
            d = np.maximum(d, rb.max()); back = d
            carve_fr = 0
        if d.max() > 0.05 or back.max() > 0.05 or abs(s - 1) > 1e-3:
            print('   NOT the same vertices: left as it is'); continue
        text = card_text(cfile, cname)
        if carried:
            text = uncarry(text, carried)
        cards.append('# %s: carried from %s (%s) by port_plus_rows.py.\n# %s -> %s frame %d: scale %.5f, rotation %.3f deg, '
                     't %s, every vertex within %.4f\n' % (donor, cname, cfile, ref, mesh, fr, s, rot, [round(float(x), 3) for x in t], max(d.max(), back.max()))
                     + carry(text, s, R, t, donor, mesh))
        if not dry:
            res = carve_by_ref.carve(os.path.join(ROOT, ref), os.path.join(ROOT, mesh), os.path.join(ROOT, mesh), {}, frame=carve_fr)
            # carve_by_ref names a second surface of one part 'name#k' (a part that spans two source
            # surfaces, e.g. the TEC-9's bolt). '#' starts a comment in a card, so: name_2, and the card
            # names every surface of the part
            m = carve_by_ref.read_md3(os.path.join(ROOT, mesh)); extra = {}
            for x in m['surfs']:
                if '#' in x['name']:
                    b = x['name'].split('#')[0]; extra.setdefault(b, []).append(b + '_%d' % (len(extra.get(b, [])) + 2))
                    x['name'] = extra[b][-1]
            if extra:
                carve_by_ref.write_md3(os.path.join(ROOT, mesh), m)
                for b, more in extra.items():
                    cards[-1] = re.sub(r'(?m)^(\s*surface\s*=\s*)%s(\s*)$' % re.escape(b),
                                       lambda mm: mm.group(0) + ''.join('\n%s%s' % (mm.group(1), n) for n in more), cards[-1])
            res['surfaces'] = [(str(x['name']), len(x['st'])) for x in m['surfs']]
            rec['carved'] = res
            print('   carved:', res['surfaces'], 'unlabelled', res['unlabelled'])
    if dry:
        return
    open(os.path.join(ROOT, 'WMCARD.plusport'), 'w', newline='\n').write(
        '# GENERATED by tools_kit/port_plus_rows.py -- do not edit by hand. Each donor\'s own set\'s reload card\n'
        '# (RS_VR_Weapons / Vanilla+ for four, BD22 Weapons Q\'s MG42 for the Buzzsaw), carried onto the mesh\n'
        '# the donor draws through a transform solved by vertex correspondence.\n\n' + '\n'.join(cards))
    json.dump(report, open(os.path.join(ROOT, 'plusport_transforms.json'), 'w'), indent=1)


if __name__ == '__main__':
    main('--dry' in sys.argv)
