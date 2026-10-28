"""TEST/BUILD helper (2.0 integration r2): give every PuristRifle block that draws Rifle.md3 the Rifle's M203 (model 1)
exactly as the Rifle's own matching block has it. Match = the Rifle block with its model-1 lines removed is the Purist
block (whitespace-normalised). Prints what it did; rewrites src/MODELDEF.purist in place."""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import re, glob, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else _DP.SRC
pat = re.compile(r'^Model\s+(\S+)[ \t]*\n\{(.*?)^\}', re.M | re.S)
def is_m1(line):
    s = line.strip()
    return bool(re.match(r'(Model|Skin)\s+1\s', s) or re.match(r'SurfaceSkin\s+1\s', s) or re.match(r'FrameIndex\s+\S+\s+\S+\s+1\s', s))
def norm(body, drop_m1):
    out = []
    for l in body.splitlines():
        s = l.split('//')[0].strip()
        if not s or (drop_m1 and is_m1(l)): continue
        out.append(' '.join(s.split()))
    return out
rifle = []
for f in sorted(glob.glob(SRC + '/MODELDEF*')):
    if f.endswith('.purist'): continue
    t = open(f, encoding='latin-1').read()
    for m in pat.finditer(t):
        if m.group(1) == 'Rifle' and 'M203.md3' in m.group(2):
            rifle.append((f, t[:m.start()].count('\n') + 1, m.group(2)))
pf = SRC + '/MODELDEF.purist'
t = open(pf, encoding='latin-1').read()
out, last, done = [], 0, 0
for m in pat.finditer(t):
    if m.group(1) != 'PuristRifle' or '"Rifle.md3"' not in m.group(2) or 'M203.md3' in m.group(2): continue
    pn = norm(m.group(2), False)
    hits = [r for r in rifle if norm(r[2], True) == pn]
    ln = t[:m.start()].count('\n') + 1
    if len(hits) != 1:
        print('PuristRifle block line %d: %d matching Rifle blocks, left alone' % (ln, len(hits))); continue
    f, rl, body = hits[0]
    out.append(t[last:m.start(2)]); out.append(body); last = m.end(2); done += 1
    print('PuristRifle block line %d <- Rifle block %s:%d (M203 added, %d model-1 lines)' % (ln, f, rl, sum(is_m1(l) for l in body.splitlines())))
out.append(t[last:])
open(pf, 'w', encoding='latin-1').write(''.join(out))
print('blocks given the M203:', done)
