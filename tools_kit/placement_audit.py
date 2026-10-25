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
from lift_common import donor_blocks, placement, vec, resolve, frame0, shelf_rest
import lift_common as L
import card2quest as C


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
