"""card_leftovers.py -- the reloadable donors still on _wm rows get cards measured from their OWN mesh.

    python -B tools_kit/card_leftovers.py [--dry] [--donor MS_A,MS_B]

WHY
regen_rows.py remakes a donor's reload row from its card, but only when the card was measured on the
mesh the donor is drawn with. Sixteen donors are left out (regen_rows "left:"): their only card is a
_wm world-model rebuild, or they have none. Their rows are the old _wm-derived ones.

WHAT
For each of them, the mesh the donor's MODELDEF block draws is measured by md3label at the donor's
own rest frame (the block's anchor FrameIndex): the parts from their motion, the reload's phases, the
magazine carved out. Checked: md3label on models/hud/RifleBD/Rifle.md3 at frame 3 writes, line for
line, the motion card already in cards_hud/MS_RifleBD.card. The cards go to cards_left/<donor>.card,
the carved magazine beside the donor's mesh, and card_from_motion turns every card with a measured
`mag_in` into WMCARD.left (cls = the donor). A mesh with no insertion in its animation gets no card
entry and keeps its row -- this says which and why; nothing is guessed. regen_rows.py prefers a
real-mesh card over a _wm one, so run it after, then fix_layer_skins.py.
"""
import os, re, sys, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import placement_audit as PA
import regen_rows as RR
import card_from_motion as cfm
import mag_insertion
import numpy as np
from run_shelf_cards import CAP

OUT = os.path.join(ROOT, 'cards_left')


def leftovers():
    # re-runnable: a donor this tool already carded is on a real-mesh card now, so it is no longer
    # in regen_rows' notes -- its card in cards_left/ keeps it on the list
    cands, notes = RR.candidates(None)
    left = [d for d, why in notes if why in ('no card', 'card mesh is a _wm rebuild')]
    return left + [c['donor'] for c in cands if os.path.exists(os.path.join(OUT, c['donor'] + '.card'))] + EXTRA


# --donor MS_A,MS_B: shelf models with no reload yet, measured the same way (then regen_rows --add)
EXTRA = sys.argv[sys.argv.index('--donor') + 1].split(',') if '--donor' in sys.argv else []


def main(dry):
    blocks = PA.donor_blocks()
    shelf = open(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs')).read()
    arch = {n: a for a, n in re.findall(r'"([a-z]+)\|(MS_\w+)\|', shelf)}
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, '.md3label')
    mesh = {}
    for d in leftovers():
        body = blocks[d]
        path = re.search(r'Path\s+"([^"]+)"', body).group(1)
        model = re.search(r'Model\s+0\s+"([^"]+)"', body).group(1)
        src = PA.resolve(os.path.join(ROOT, path, model))
        mdir = os.path.dirname(src)
        rest = next(int(f) for s, f in re.findall(r'FrameIndex\s+(\w{4})\s+\S\s+0\s+(\d+)', body) if s != 'MSBL')
        sk = re.search(r'^\s*Skin\s+0\s+"([^"]+)"', body, re.M)
        r = subprocess.run([sys.executable, '-B', os.path.join(HERE, 'md3label.py'), src, tmp, d,
                            '--idle', str(rest), '--carve', 'mag'], capture_output=True, text=True, cwd=ROOT)
        card = os.path.join(tmp, d + '.card')
        if r.returncode or not os.path.exists(card):
            print('  %-24s md3label failed: %s' % (d, (r.stderr or r.stdout).strip().splitlines()[-1:]))
            continue
        t = open(card).read()
        # the card names the mesh it measured: the donor's own file
        t = re.sub(r'^(\s*model\s+)\S+', lambda m: m.group(1) + model, t, count=1, flags=re.M)
        if not dry:
            open(os.path.join(OUT, d + '.card'), 'w', newline='\n').write(t)
        has_in = re.search(r'^\s*mag_in\s+\d+\.\.\d+', t, re.M) is not None
        has_mag = re.search(r'^\s*mag\s+surf\s+\d+', t, re.M) is not None
        if has_mag and not has_in:
            # md3label can label a whole cycle `fire` (the assault shotguns: frames 5..31) while
            # the magazine part's own line says when it moved. Measured in the gun's frame: if the
            # magazine goes out by 2 units or more and is home (within 0.5) by the end of its own
            # window, that window is its swap, and its insertion is read from it the usual way.
            mp = re.search(r'^\s*mag\s+surf\s+(\d+)\s.*?frames\s+(\d+)\.\.(\d+)', t, re.M)
            P = mag_insertion.track(src, int(mp.group(1))) if mp else None
            if P is not None:
                a, b = int(mp.group(2)), int(mp.group(3))
                dist = lambda f: float(np.linalg.norm(P[f] - P[rest]))
                out = max(dist(f) for f in range(a, b + 1))
                # md3label closes the window at its motion threshold; the part settles a frame or
                # two later -- followed while it still closes in, up to 4 frames
                while b + 1 < len(P) and b < int(mp.group(3)) + 4 and dist(b) > 0.5 and dist(b + 1) < dist(b):
                    b += 1
                home = dist(b)
                if out >= 2.0 and home <= 0.5:
                    t = re.sub(r'^(\s*phases\s*\n)', lambda m: m.group(1) + '    mag_in       %d..%d   # the magazine part\'s own window: out %.1f, home to %.2f (card_leftovers.py)\n' % (a, b, out, home), t, count=1, flags=re.M)
                    has_in = True
                    if not dry:
                        open(os.path.join(OUT, d + '.card'), 'w', newline='\n').write(t)
        print('  %-24s %s frame %d: %s' % (d, os.path.relpath(src, ROOT), rest,
              'magazine and its insertion measured' if has_in else
              'a magazine moves, but the animation has no insertion (no mag_in) -- keeps its row' if has_mag else
              'no magazine moves in its animation -- keeps its row'))
        if not has_in:
            continue
        carve = os.path.join(tmp, d + '_mag.md3')
        if os.path.exists(carve) and not dry:
            shutil.copy(carve, os.path.join(mdir, d + '_mag.md3'))
        a = arch.get(d, 'rifle')
        mesh[d] = (os.path.relpath(mdir, ROOT), os.path.basename(src), sk.group(1) if sk else '', a, CAP.get(a, 12), d)
    shutil.rmtree(tmp, ignore_errors=True)
    if dry or not mesh:
        return
    cfm.SRC = OUT
    cfm.ACTION_SLIDE = True
    cfm.MESH = mesh
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        cfm.main(os.path.join(ROOT, 'WMCARD.left'))
    finally:
        os.chdir(cwd)


if __name__ == '__main__':
    main('--dry' in sys.argv)
