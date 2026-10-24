"""Which of OUR shipped models is the same mesh as a gun the cards already measure.

Same vertex count is a candidate, never a conclusion -- three pairs matched on
count alone and turned out to be different guns. The sorted distances from the
centroid are invariant to any rotation or translation, so they settle it.
"""
import sys, glob, os, re
import numpy as np
sys.path.insert(0, 'tools_kit')
from md3read import read_md3
import wmcard

RS = 'E:/DOOMWork/RS_VR_Weapons'
norm = lambda p: p.replace('\\', '/').lower()

# the guns genpack reports as having a real VR reload, and their slots
RELOADING = {}
gen = open(sys.argv[1], encoding='utf-8', errors='replace').read()
for cls, slot in re.findall(r"n == '(\w+)'\)\s*return (\d+)", gen):
    RELOADING[cls] = int(slot)

cardof = {}
for c in wmcard.load(glob.glob(RS + '/WMCARD.*')):
    mod = c['keys'].get('model')
    if not mod:
        continue
    d, mesh = (list(mod) + [''])[:2]
    cardof[norm(os.path.join(RS, *d.split('/'), mesh))] = c['cls']

# a card class may be the Vanilla+ copy (WM_VP_X) of a Vanilla card (WM_X)
def slot_for(cls):
    if cls in RELOADING:
        return cls, RELOADING[cls]
    vp = 'WM_VP_' + cls[3:]
    if vp in RELOADING:
        return vp, RELOADING[vp]
    return None, None

rs = {}
for f in glob.glob(RS + '/models/**/*.md3', recursive=True):
    try:
        m = read_md3(f)
    except Exception:
        continue
    rs.setdefault(sum(s['nverts'] for s in m['surfs']), []).append(norm(f))


def sig(P):
    return np.sort(np.linalg.norm(P - P.mean(0), axis=1))


# every model modeldef actually names, so we only consider what ships
md = open('modeldef', encoding='utf-8', errors='replace').read()
owner = {}
for blk in re.finditer(r'(?ms)^Model\s+(\S+)\s*\r?\n\{(.*?)^\}', md):
    name, body = blk.group(1), blk.group(2)
    p = re.search(r'Path\s+"([^"]+)"', body)
    f = re.search(r'Model\s+\d+\s+"([^"]+)"', body)
    if p and f:
        owner.setdefault(norm(os.path.join(p.group(1), f.group(1))), name)

print(f'{"card":<22} {"slot":>4}  {"our model":<28} {"our mesh":<38}')
print('-' * 100)
found = {}
for path, name in sorted(owner.items()):
    if not os.path.exists(path):
        continue
    try:
        m = read_md3(path)
    except Exception:
        continue
    B = np.vstack([s['xyz'][0] for s in m['surfs']])
    for cand in rs.get(len(B), []):
        cls = cardof.get(cand)
        if not cls:
            continue
        used, slot = slot_for(cls)
        if slot is None:
            continue
        A = np.vstack([s['xyz'][0] for s in read_md3(cand)['surfs']])
        if A.shape != B.shape or float(np.abs(sig(A) - sig(B)).max()) > 0.5:
            continue
        found.setdefault(slot, []).append(name)
        print(f'{used:<22} {slot:>4}  {name:<28} {path}')
        break

print()
print(f'{len(found)} of {len(RELOADING)} reloading guns have one of our models'
      f' ({sum(len(v) for v in found.values())} models in all)')
missing = sorted(set(RELOADING.values()) - set(found))
if missing:
    inv = {v: k for k, v in RELOADING.items()}
    print('no model for: ' + ', '.join(f'{inv[s]} (slot {s})' for s in missing))
import json
json.dump(found, open(sys.argv[2], 'w'), indent=1)
