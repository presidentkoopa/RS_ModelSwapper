"""hand_gap.py -- how far each hand sits from the gun it holds, from the tables the engine reads.

    python -B tools_kit/hand_gap.py [donor ...] [--max-support CM] [--max-gun CM] [--json out.json]

For a donor: the gun is its MODELDEF block (every Model N on its FrameIndex frame, Scale, Offset, ZOffset); the hands are
MODELDEF.rsq's hand meshes on the frames RSQ_HandTable names for its slot (gun hand: Trigger letter ->
RQGT, else GunTwo -> RQGS, as hands.zs shows it while steadied; support: Support -> RQSP), placed at
GunHook / SupportHook with GunRot / SupportRot. RenderHUDModel's chain (hudrender.to_local), at rest.

The gap is the CLOSEST APPROACH of the hand's mesh to the gun's surface (triangles sampled every
~0.5 cm), in cm. A hand that holds the gun touches it (gap ~0, or negative contact shown as 0);
the owner's "support hand detached" (MS_BD_M79's old row) measured 4.2 cm here. Exit 1 when a donor
is over the limits -- run_gate.py uses this as its "support on the gun" check.
"""
import os, re, sys, json
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import hudrender as H
from lift_common import donor_blocks

MAX_SUPPORT = 1.5    # cm
MAX_GUN = 1.5        # cm


def tables():
    t = open(os.path.join(ROOT, 'zscript_depot/rsq/handtable.zs'), encoding='utf-8').read()
    slot = {d: int(s) for d, s in re.findall(r'donor == "(\w+)"\)\s*return (\d+);', t)}
    out = {}
    for m in re.finditer(r'static (String|Vector3) (\w+)\(int i\)\s*\{(.*?)\n\t\}', t, re.S):
        arrs = dict(re.findall(r'static const (?:double|String) (\w)\[\] = \{(.*?)\};', m.group(3), re.S))
        out[m.group(2)] = {k: [x.strip().strip('"') for x in v.split(',')] for k, v in arrs.items()}
    return slot, out


def row(tb, i, name):
    a = tb[name]
    if 'v' in a:
        return a['v'][i] if i < len(a['v']) else ''
    return np.array([float(a[k][i]) for k in 'xyz'])


def letters():
    """MODELDEF.rsq: (sprite, letter) -> (mesh file, frame) for the gun-side hands"""
    t = open(os.path.join(ROOT, 'MODELDEF.rsq'), encoding='latin-1').read()
    out = {}
    for m in re.finditer(r'Model\s+RSQ_GunSide\s*\{(.*?)\}', t, re.S):
        b = m.group(1)
        mesh = re.search(r'Model\s+0\s+"([^"]+)"', b).group(1)
        path = re.search(r'Path\s+"([^"]+)"', b).group(1)
        for spr, let, fr in re.findall(r'FrameIndex\s+(\w{4})\s+(\S)\s+0\s+(\d+)', b):
            out[(spr, let)] = (os.path.join(ROOT, path, mesh), int(fr))
    return out


def placement(body):
    def nums(key):
        m = re.search(r'^[ \t]*%s\s+([-\d.eE]+(?:[ \t]+[-\d.eE]+)*)' % key, body, re.M | re.I)
        return [float(x) for x in m.group(1).split()] if m else None
    sc = nums('Scale') or [1.0, 1.0, 1.0]
    off = (nums('Offset') or [0.0, 0.0, 0.0]) + [0.0] * 3
    z = nums('ZOffset')
    if z:
        off[2] = z[0]
    fr = re.search(r'FrameIndex\s+\w+\s+A\s+0\s+(\d+)', body)
    return sc[:3], off[:3], int(fr.group(1)) if fr else 0


def surface(path, frame, item, step=0.005):
    """triangle surface samples (metres, controller frame) of every surface of a mesh on a frame"""
    pts = []
    for tris, xyz in H.load(path):
        v = H.to_local(xyz[min(frame, len(xyz) - 1)], item, ws=1.0)
        a, b, c = v[tris[:, 0]], v[tris[:, 1]], v[tris[:, 2]]
        pts.append(v)
        L = np.maximum(np.linalg.norm(b - a, axis=1), np.linalg.norm(c - a, axis=1))
        n = np.clip((L / step).astype(int), 1, 12)
        for k in range(1, 13):
            sel = n >= k
            if not sel.any():
                break
            for j in range(0, k + 1):
                u = j / max(k, 1); w = (k - j) / max(k, 1)
                if u + w > 1:
                    continue
                pts.append(a[sel] + (b[sel] - a[sel]) * u * 0.999 + (c[sel] - a[sel]) * w * 0.999)
    return np.concatenate(pts)


def gaps(donor, blocks, slot, tb, lt):
    i = slot.get(donor)
    if not i or donor not in blocks:
        return None
    body = blocks[donor]
    sc, off, fr = placement(body)
    # every model the block draws (BD22's Rifle carries its M203 as Model 1, and the support hand
    # holds that tube); each Model N on the frame its FrameIndex rows give it
    base = re.search(r'Path\s+"([^"]+)"', body).group(1)
    parts = []
    for n, mdl in re.findall(r'^[ \t]*Model\s+(\d+)\s+"([^"]+)"', body, re.M):
        gp = os.path.join(ROOT, base, mdl)
        frm = re.search(r'FrameIndex\s+\w+\s+A\s+%s\s+(\d+)' % n, body)
        if os.path.exists(gp) and (frm or n == '0'):
            parts.append(surface(gp, int(frm.group(1)) if frm else fr, {'scale': sc, 'off': off}))
    if not parts:
        return None
    gun = cKDTree(np.concatenate(parts))
    res = {'slot': i}
    hp = dict(scale=[-1.0, 1.0, 1.0], off=[0.0, -24.0, -10.0])
    trig = row(tb, i, 'Trigger'); two = row(tb, i, 'GunTwo'); sup = row(tb, i, 'Support')
    for name, key, hook, rot in (('gun', ('RQGT', trig) if trig else ('RQGS', two), 'GunHook', 'GunRot'),
                                 ('support', ('RQSP', sup), 'SupportHook', 'SupportRot')):
        if not key[1] or key not in lt:
            res[name] = None
            continue
        mesh, f = lt[key]
        item = dict(hp, hook=list(row(tb, i, hook)), rot=list(row(tb, i, rot)))
        pts = surface(mesh, f, item, step=0.01)
        d, _ = gun.query(pts)
        res[name] = round(float(d.min()) * 100, 2)
        c = pts.mean(0) * 100          # local x right, y up, z back (cm) -> F, L, U
        res[name + '_at'] = [round(float(-c[2]), 1), round(float(-c[0]), 1), round(float(c[1]), 1)]
        res[name + '_frame'] = '%s %s (%s %d)' % (key[0], key[1], os.path.basename(mesh), f)
    return res


def reference_of(donor, blocks):
    """the lifted donor (MS_BD22_) whose every drawn vertex this donor's block coincides with, if any
    -- the pose the owner signed off for that mesh at that place (twin_hands.py's test)"""
    import twin_hands as TW
    if donor.startswith(TW.LIFTED) or donor not in blocks:
        return None
    v = TW.drawn(blocks[donor])
    if v is None:
        return None
    for r in blocks:
        if r.startswith(TW.LIFTED):
            rv = TW.drawn(blocks[r])
            if rv is not None and rv.shape == v.shape and float(np.abs(rv - v).max()) <= TW.TOL:
                return r
    return None


def check(donor, max_gun=MAX_GUN, max_support=MAX_SUPPORT, max_shift=2.0):
    """run_gate.py's hand check: (ok, lines). Each hand touches the gun (closest approach), and a
    donor drawn exactly like a lifted BD22Q gun holds it where BD22Q does (every hand centre)."""
    blocks = donor_blocks(open(os.path.join(ROOT, 'modeldef'), encoding='utf-8', errors='replace').read())
    slot, tb = tables()
    lt = letters()
    r = gaps(donor, blocks, slot, tb, lt)
    if r is None:
        return True, ['no hand row: no hands drawn']
    ok, out = True, []
    for k, lim in (('gun', max_gun), ('support', max_support)):
        if r.get(k) is None:
            continue
        bad = r[k] > lim
        ok &= not bad
        out.append('%s hand %.2f cm from the gun (%s)%s' % (k, r[k], r.get(k + '_frame'), '  OVER %.1f' % lim if bad else ''))
    ref = reference_of(donor, blocks)
    if ref:
        rr = gaps(ref, blocks, slot, tb, lt)
        for k in ('gun', 'support'):
            if r.get(k + '_at') and rr and rr.get(k + '_at'):
                s = float(np.linalg.norm(np.array(r[k + '_at']) - np.array(rr[k + '_at'])))
                bad = s > max_shift
                ok &= not bad
                out.append('%s hand %.1f cm from %s\'s (drawn identically)%s' % (k, s, ref, '  OVER %.1f' % max_shift if bad else ''))
    return ok, out


def main(argv):
    opt = lambda k, d: next((argv[j + 1] for j, x in enumerate(argv) if x == k), d)
    ms, mg = float(opt('--max-support', MAX_SUPPORT)), float(opt('--max-gun', MAX_GUN))
    skip = {opt(k, None) for k in ('--max-support', '--max-gun', '--json', '--like', '--max-shift')}
    names = [x for x in argv if not x.startswith('--') and x not in skip]
    blocks = donor_blocks(open(os.path.join(ROOT, 'modeldef'), encoding='utf-8', errors='replace').read())
    slot, tb = tables()
    lt = letters()
    names = names or ([] if opt('--like', None) else sorted(slot))
    out, bad = {}, 0
    for d in names:
        r = gaps(d, blocks, slot, tb, lt)
        if r is None:
            print('%-26s no hand slot or no block' % d)
            continue
        out[d] = r
        over = [k for k, lim in (('gun', mg), ('support', ms)) if r.get(k) is not None and r[k] > lim]
        bad += 1 if over else 0
        print('%-26s slot %3d  gun hand %5s cm  support %5s cm%s' % (d, r['slot'], r.get('gun'), r.get('support'),
              '   OVER: ' + ' '.join(over) if over else ''))
    ref = opt('--like', None)
    if ref:
        # --like A=B,...: each donor's hands must sit where the reference donor's do (the lifted set's
        # pose the owner signed off), every hand centre within --max-shift cm
        lim = float(opt('--max-shift', 2.0))
        for pair in ref.split(','):
            a, b = pair.split('=')
            ra, rb = gaps(a, blocks, slot, tb, lt), gaps(b, blocks, slot, tb, lt)
            for k in ('gun', 'support'):
                if ra and rb and ra.get(k + '_at') and rb.get(k + '_at'):
                    s = float(np.linalg.norm(np.array(ra[k + '_at']) - np.array(rb[k + '_at'])))
                    bad += 1 if s > lim else 0
                    print('%-26s %-8s at F L U %s, %s at %s: %.1f cm apart%s' % (a, k, ra[k + '_at'], b, rb[k + '_at'], s, '   OVER' if s > lim else ''))
    if opt('--json', None):
        json.dump(out, open(opt('--json', None), 'w'), indent=1)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
