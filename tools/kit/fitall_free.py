"""`fitall.run()` without Ermac's gun meshes.

Same table, same boxes, same ICP, same drop, same check sheet. The one change is
where the gripping face comes from: `align_free.stored_patch()` (measured once per
pose by `gripmeasure.py`) instead of `align.held_patch()` (which reads Ermac's own
gun). `fitall.py` is untouched and still behaves exactly as it did.

usage:
  python -B fitall_free.py [class ...]      # the BD22 table, gun-free
  from fitall_free import run               # run(cls) -> (record, gun shift, support shift)
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import guns                      # before align: align re-points sys.path at kit/melee
import align, align_free, handfit, support, handtable, ermac, fitall

S = handfit.S
GUN_DROP = fitall.GUN_DROP       # one table of drops, shared with the old path
GRIPBOX = dict(f=(-22, 6), l=(-5, 5), u=(-24, -1))


def hand_centroid(sset, which):
    """unchanged from fitall.hand_centroid -- the hand mesh only, no gun"""
    return fitall.hand_centroid(sset, which)


def run(cls):
    gs, ss, where = handtable.TABLE[cls]
    # the gun hand holds a grip, not a tube, so its stand-in is the measured contact
    # face; the support hand on a forend gets the cylinder. See align_free.contact_patch.
    t, err, _ = align_free.fit(cls, gs, 1, GRIPBOX, kind='contact')
    t = t + np.array([0, 0, GUN_DROP.get(cls, -1.5)])
    r = {'gun_set': gs, 'gun_shift': t.round(2).tolist(), 'gun_err': round(err, 2),
         'sup_set': ss, 'where': list(where), 'sup_rot': [0, 0, 0], 'from': 'stored grip region'}
    if where[0] == 'same':
        t2 = t.copy(); err2 = 0.0
        r['target'] = (hand_centroid(ss, 2) + t2).round(2).tolist()
    elif where[0] == 'wrap':
        patch = align_free.stored_patch(align_free.pose_key(ss, 2))
        fp, (lo, hi) = support.front_point(cls, where[1])
        if hi - lo > 6:
            reg = dict(f=(fp[0] - 10, fp[0] + 10), l=(-7, 7), u=(lo - 3, lo + 3.5))
        else:
            reg = dict(f=(fp[0] - 10, fp[0] + 10), l=(-7, 7), u=(fp[2] - 8, fp[2] + 8))
        t0 = np.array(fp) - patch.mean(0)
        t2, err2, _ = align_free.fit(cls, ss, 2, reg, t0=t0)
        t2[1] = -patch.mean(0)[1]          # centred across the gun, as fitall does
        r['target'] = fp
    elif where[0] == 'vgrip':
        gO = align.surface_points(guns.item(cls))
        b = align.box(gO, f=where[1], l=(-4, 4), u=where[2])
        c = b.mean(0)
        t2 = c - hand_centroid(ss, 2); err2 = 0.0
        r['target'] = c.round(2).tolist()
    else:
        return r, t, None
    r['sup_shift'] = np.round(t2, 2).tolist()
    r['sup_err'] = round(float(err2), 2)
    return r, t, t2


if __name__ == '__main__':
    only = sys.argv[1:]
    res = {}
    for cls in handtable.TABLE:
        if only and cls not in only:
            continue
        r, t, t2 = run(cls)
        res[cls] = r
        print(cls, r, flush=True)
        if t2 is not None:
            handfit.sheet(cls, handfit.hand_items(r['gun_set'], t, r['sup_set'], t2),
                          S + '/hands/fitfree_%s.png' % cls, cls + ' (gun-free)')
    json.dump(res, open(S + '/hands/fits_free.json', 'w'), indent=1)
