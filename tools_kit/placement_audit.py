"""placement_audit.py -- does each reloadable donor DRAW its gun where its reload rows and hands think it is?

    python -B tools_kit/placement_audit.py [--json out.json]

A reload row (zscript_depot/rsr/rsr_guns.ms.zs) carries the placement it was generated at (its Scale
and Offset fields: card2quest.py turns card points into controller cm through that placement), and
the hand rows of the older guns were fitted by handfit_cards.py against the same placement and the
card's rest frame. The donor block in `modeldef` is what is DRAWN. Where the two disagree, the hand
reaches for a magazine well and a grip that are not where the gun is.

Per donor with a reload row, this prints:
  mesh   same    the card's mesh and the donor's are the same file content
         shift   the donor's is the card's re-centred (pure translation; Offset should compensate)
         other   a different mesh (rows measured on another mesh -- e.g. a _wm rebuild)
  dpos   cm between where the row's placement puts the mesh and where the donor block puts it
         (largest over the mesh's frame-0 vertices, through card2quest.to_flu)
  frame  the card's rest frame (card2quest.rest_frame) / the donor's rest frame (shelf row)
"""
import os, re, sys, json, glob
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import lift_aliens as L
import card2quest as C


def donor_blocks():
    md = open(os.path.join(ROOT, 'modeldef'), encoding='utf-8', errors='replace').read()
    out = {}
    for m in re.finditer(r'^Model\s+(\w+)\s*\n\{(.*?)^\}', md, re.S | re.M):
        out.setdefault(m.group(1), m.group(2))
    return out


def placement(body):
    sc = [float(x) for x in re.search(r'^\s*Scale\s+([^\n/]+)', body, re.M).group(1).split()]
    om = re.search(r'^\s*Offset\s+([^\n/]+)', body, re.M)
    off = [float(x) for x in om.group(1).split()] if om else [0.0, 0.0, 0.0]
    off += [0.0] * (3 - len(off))
    z = re.search(r'^\s*ZOffset\s+([-\d.]+)', body, re.M)
    if z:
        off[2] = float(z.group(1))
    return sc, off


def vec(s):
    return [float(x) for x in s.strip('()').split(',')]


def resolve(p):
    """the file as the engine finds it: lump names are case-insensitive, Linux paths are not"""
    if os.path.exists(p):
        return p
    cur = '/'
    for part in os.path.abspath(p).strip('/').split('/'):
        hit = [x for x in os.listdir(cur) if x.lower() == part.lower()] if os.path.isdir(cur) else []
        if not hit:
            return p
        cur = os.path.join(cur, hit[0])
    return cur


def frame0(p, f=0):
    import genpack as gp
    p = resolve(p)
    s = gp.md3_surfaces(p)[1]
    f = min(f, s[0]['xyz'].shape[0] - 1)
    return np.concatenate([x['xyz'][f] for x in s])


def shelf_rest():
    t = open(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs')).read()
    return {m.group(1): int(m.group(2)) for m in re.finditer(r'"\w+\|(\w+)\|\w{4}\|\d+\|(\d+)\|\d+"', t)}


def audit():
    rsr = open(os.path.join(ROOT, 'zscript_depot/rsr/rsr_guns.ms.zs')).read()
    slots = {}
    for d, s in re.findall(r'donor == "(\w+)"\)\s*return (\d+);', rsr):
        slots.setdefault(d, int(s))
    cards = {w['cls']: w for w in C.load_cards(ROOT)}
    blocks = donor_blocks(); rest = shelf_rest()
    out = []
    for d, s in sorted(slots.items(), key=lambda kv: (kv[1], kv[0])):
        if d.startswith('MS_PU_') or d not in blocks:
            continue
        row = L.read_row(rsr, s)
        rsc, roff = vec(row['Scale'][1]), vec(row['Offset'][1])
        dsc, doff = placement(blocks[d])
        dp = os.path.join(ROOT, re.search(r'Path\s+"([^"]+)"', blocks[d]).group(1), re.search(r'Model\s+0\s+"([^"]+)"', blocks[d]).group(1))
        w = cards.get(d)
        r = dict(donor=d, slot=s, row_scale=rsc, row_off=roff, donor_scale=dsc, donor_off=doff, donor_frame=rest.get(d))
        cp = C.model_path(ROOT, w) if w else None
        if not cp or not os.path.exists(cp) or not os.path.exists(dp):
            r['mesh'] = 'nocard' if not w else 'missing'
            out.append(r); continue
        cf = C.rest_frame(w, cp)
        r['card_frame'] = cf
        a, b = frame0(cp), frame0(dp)
        if a.shape != b.shape:
            r['mesh'] = 'other'
        else:
            sh = b - a
            r['mesh'] = 'same' if np.abs(sh).max() < 1e-4 else ('shift' if np.ptp(sh, 0).max() < 1e-3 else 'other')
        if r['mesh'] in ('same', 'shift'):
            pa = C.to_flu(frame0(cp, cf), rsc, roff)
            pb = C.to_flu(frame0(dp, r['donor_frame'] or 0), dsc, doff)
            r['dpos_cm'] = round(float(np.linalg.norm(pa - pb, axis=1).max()), 2)
        out.append(r)
    return out


if __name__ == '__main__':
    rows = audit()
    for r in rows:
        print('%-26s slot %2d  mesh %-7s dpos %6s cm  frame card %s / donor %s' % (
            r['donor'], r['slot'], r['mesh'], r.get('dpos_cm', '-'), r.get('card_frame', '-'), r.get('donor_frame')))
    if '--json' in sys.argv:
        json.dump(rows, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
