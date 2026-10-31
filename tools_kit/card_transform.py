import sys, glob, os, itertools, json
import numpy as np
sys.path.insert(0, 'tools_kit')
from md3read import read_md3
import wmcard

RS = 'E:/DOOMWork/RS_VR_Weapons'
norm = lambda p: p.replace('\\', '/').lower()

cardof = {}
for c in wmcard.load(glob.glob(RS + '/WMCARD.*')):
    mod = c['keys'].get('model')
    if not mod:
        continue
    d, mesh = (list(mod) + [''])[:2]
    cardof[norm(os.path.join(RS, *d.split('/'), mesh))] = c['cls']

rs = {}
for f in glob.glob(RS + '/models/**/*.md3', recursive=True):
    try:
        m = read_md3(f)
    except Exception:
        continue
    rs.setdefault(sum(s['nverts'] for s in m['surfs']), []).append(norm(f))

ROTS = []
for perm in itertools.permutations(range(3)):
    for s in itertools.product((1, -1), repeat=3):
        R = np.zeros((3, 3))
        for i in range(3):
            R[i, perm[i]] = s[i]
        if abs(np.linalg.det(R) - 1) < 1e-9:
            ROTS.append(R)


def verts(p):
    m = read_md3(p)
    return np.vstack([s['xyz'][0] for s in m['surfs']])


def shape_match(A, B):
    da = np.sort(np.linalg.norm(A - A.mean(0), axis=1))
    db = np.sort(np.linalg.norm(B - B.mean(0), axis=1))
    return float(np.abs(da - db).max())


def axes(P):
    """Principal axes, ordered by spread. Rotation-equivariant, so the two
    meshes' axes correspond even though their vertex orders do not."""
    C = P - P.mean(0)
    w, v = np.linalg.eigh(np.cov(C.T))
    return v[:, np.argsort(-w)]


def resid(A, ca, B, cb, R):
    return float(np.abs(np.sort((A - ca) @ R.T, axis=0) - np.sort(B - cb, axis=0)).max())


out = {}
print(f'{"card":<20} {"our animated mesh":<38} {"shape":>6} {"fit":>7} {"rot":>6}  translation')
print('-' * 112)
solved = off = notsame = 0
for p in ('wolf', 'hacx', 'meat', 'bd'):
    for f in sorted(glob.glob(f'models/{p}/*/*.md3')):
        if any(x in f for x in ('_mag', '_round', '_stable')):
            continue
        try:
            B = verts(f)
        except Exception:
            continue
        src = next((c for c in rs.get(len(B), []) if c in cardof), None)
        if not src:
            continue
        A = verts(src)
        if A.shape != B.shape:
            continue
        sh = shape_match(A, B)
        if sh > 0.5:
            notsame += 1
            continue
        ca, cb = A.mean(0), B.mean(0)
        cands = list(ROTS)
        # principal-axis candidates: Rb @ Ra.T, with the four sign flips that keep det +1
        Ra, Rb = axes(A), axes(B)
        for sx, sy in itertools.product((1, -1), repeat=2):
            S = np.diag([sx, sy, sx * sy])
            R = Rb @ S @ Ra.T
            if abs(np.linalg.det(R) - 1) < 1e-6:
                cands.append(R)
        d, R = min(((resid(A, ca, B, cb, R), R) for R in cands), key=lambda x: x[0])
        t = cb - R @ ca
        ang = float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
        if d < 0.5:
            solved += 1
            out[cardof[src]] = dict(mesh=f.replace('\\', '/'), R=R.round(6).tolist(),
                                    t=t.round(4).tolist(), resid=round(d, 4))
            print(f'{cardof[src]:<20} {f:<38} {sh:6.2f} {d:7.3f} {ang:6.1f}  '
                  f'[{t[0]:7.2f} {t[1]:6.2f} {t[2]:7.2f}]')
        else:
            off += 1
            print(f'{cardof[src]:<20} {f:<38} {sh:6.2f} {d:7.3f} {ang:6.1f}  unsolved')
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print()
print(f'{solved} solved, {off} unsolved, {notsame} not the same mesh')
