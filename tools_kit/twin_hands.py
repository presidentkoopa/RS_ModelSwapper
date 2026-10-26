"""twin_hands.py -- a shelf donor that draws EXACTLY a lifted set's gun takes that gun's hand slot.

    python -B tools_kit/twin_hands.py [--dry]

The shelf has older blocks of the same meshes BD22Q ships (Brutal Doom v21's, brt_, d64_ ...). Some
are byte-for-byte the same geometry, moved only by their own Offset, so they draw the SAME vertices at
the SAME place in the controller frame on the SAME rest frame as the lifted MS_BD22_ donor. Their hand
rows came from the older card fits (tools_kit/handfit_cards.py), which BD22Q's own fit (the 1.92 set,
owner: "perfect") replaced: on the rig MS_BD_M79 -- the model ModelSwapper puts on BD22's own
GrenadeLauncher by default -- held its gun hand above the stock and its support hand at the muzzle
(owner's headset finding 3, 2026-10-26), while MS_BD22_M79 draws 1.92's poses exactly.

A hand row is a pose IN THE CONTROLLER FRAME, so two donors whose meshes coincide there must share it.
This proves the coincidence from each block's own MODELDEF (Path, Model 0, Scale, Offset, ZOffset, the
FrameIndex rest frame -- hudrender.to_local, RenderHUDModel's transform) and, for every twin within
TOL, points RSQ_HandTable.SlotForDonor at the lifted donor's slot. Nothing is typed in; RSQ_GunMoves
reads the same slot: Pivot comes from the placement (identical by the check), Mirrored from the Scale x
sign (checked equal, or the twin is refused). Blends (NoInterpolation) may differ: it only gates
RSQ_GunMoves.Frame(), keyed by BD22Q's own sprites, and the Quest build pins the gun layer to the
donor's one rest frame (rig probe, 2026-10-26: BD22's Rifle firing kept sprite and frame), so it moves
no hand there.

The twin's old row stays in the arrays (a slot number never moves: dual-wield copies index them too).
Re-run after any lift; idempotent.
"""
import os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import hudrender as H
from lift_common import donor_blocks

TOL = 0.0005            # metres: half a millimetre, every vertex
LIFTED = ('MS_BD22_',)  # sets whose hand rows are the owner's reference (BD22Q 1.92)


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
    ni = re.search(r'^[ \t]*NoInterpolation\b', body, re.M | re.I) is not None
    return sc[:3], off[:3], int(fr.group(1)) if fr else 0, ni


def drawn(body):
    """every vertex of the block's model 0 on its rest frame, in the controller frame (m)"""
    path = re.search(r'Path\s+"([^"]+)"', body)
    mdl = re.search(r'Model\s+0\s+"([^"]+)"', body)
    if not path or not mdl:
        return None
    f = os.path.join(ROOT, path.group(1), mdl.group(1))
    if not os.path.exists(f):
        return None
    sc, off, fr, _ = placement(body)
    surf = H.load(f)
    v = np.concatenate([x[min(fr, len(x) - 1)] for _, x in surf])
    return H.to_local(v, {'scale': sc, 'off': off}, ws=1.0)


def main(dry):
    blocks = donor_blocks(open(os.path.join(ROOT, 'modeldef'), encoding='utf-8', errors='replace').read())
    p = os.path.join(ROOT, 'zscript_depot/rsq/handtable.zs')
    t = open(p, encoding='utf-8').read()
    slot = {d: int(s) for d, s in re.findall(r'donor == "(\w+)"\)\s*return (\d+);', t)}
    refs = {d: drawn(blocks[d]) for d in blocks if d.startswith(LIFTED) and d in slot}
    refs = {d: v for d, v in refs.items() if v is not None}
    changes = []
    for d in sorted(blocks):
        if d.startswith(LIFTED) or d.startswith('MS_PU_'):
            continue
        try:
            v = drawn(blocks[d])
        except Exception:
            continue
        if v is None:
            continue
        for r, rv in refs.items():
            if rv.shape != v.shape:
                continue
            gap = float(np.abs(rv - v).max())
            if gap > TOL:
                continue
            s1, _, _, n1 = placement(blocks[d]); s2, _, _, n2 = placement(blocks[r])
            if (s1[0] > 0) != (s2[0] > 0):
                print('%-26s ~ %-22s gap %.5f m but the Scale x sign differs (GunMoves.Mirrored) -- left' % (d, r, gap))
                continue
            changes.append((d, r, slot.get(d), slot[r], gap))
    for d, r, old, new, gap in changes:
        line = '\t\tif (donor == "%s")\treturn %d;\t// = %s, drawn identically (tools_kit/twin_hands.py, %.5f m)' % (d, new, r, gap)
        pat = re.compile(r'^[ \t]*if \(donor == "%s"\)\s*return \d+;.*$' % re.escape(d), re.M)
        if pat.search(t):
            t = pat.sub(lambda m: line, t, count=1)
        else:
            k = t.index('\t\treturn 0;', t.index('static int SlotForDonor'))
            t = t[:k] + line + '\n' + t[k:]
        print('%-26s hand slot %-4s -> %d (%s), max vertex gap %.5f m' % (d, old if old else '-', new, r, gap))
    if not dry:
        open(p, 'w', newline='\n', encoding='utf-8').write(t)
    print('%d twins%s' % (len(changes), ' (dry run)' if dry else ' written'))


if __name__ == '__main__':
    main('--dry' in sys.argv)
