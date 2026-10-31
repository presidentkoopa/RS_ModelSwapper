#!/usr/bin/env python3
"""tools_placement_from_1x.py -- placement.json for the MS 1.5 donors (2026-10-31).

For every donor in gen_from_cards.report.md: the MODELDEF Scale/Offset(/Angle/Pitch/Roll) that put the CARD mesh
(original origin, as md3label wrote it) where the 1.x donor sat.

  Only the 36 STAMPED 1.x blocks (origin: centred, models/hud/*) count as placements; the unstamped imports carry the
  source mod's own numbers and are ignored here.
  1x-identical    the card mesh IS the 1.x donor mesh (frame-0 vertices equal): the 1.x block's numbers verbatim.
  1x-compensated  the 1.x mesh is the card mesh shifted by a constant t (tools_md3_reorigin centred it): the 1.x
                  Offset is undone with tools_md3_compensate's own replica of the engine matrix:
                      Off_old = Off_src + S*R*c'   (c = the centring shift)   =>   Off_card = compensate(-t, ...)
                  where t = card_f0 - old_f0 (so c == t).
  family-ref:X    no 1.x donor for this mesh: X is a placed donor of the same family; Scale is X's scaled so the
                  grip->muzzle length matches in world units, Angle/Pitch/Roll are X's, Offset puts this card's grip
                  point where X's grip point lands.
  none            no grip line on the card (and no 1.x donor): nothing to place from.

Reads: /tmp/claude-0/old_modeldef.txt (archive modeldef), /tmp/claude-0/oldtree/models (archive meshes),
       gen_from_cards.report.md, cards/, zscript/RS_ForeignModels.zs (families).
Writes: placement.json, PLACEMENT_NOTES.md.  Edits nothing else.
"""
import os, re, sys, glob, json
import numpy as np
R = os.path.dirname(os.path.abspath(__file__)); os.chdir(R)
sys.path.insert(0, R); sys.path.insert(0, '/home/claude/rsq_weapondepot/tools/hqt')
from tools_md3_compensate import compensate
from md3read import read_md3

OLD_MD = '/tmp/claude-0/old_modeldef.txt'; OLD_TREE = '/tmp/claude-0/oldtree/'


def field(text, key, n):
    m = re.search(r'^\s*%s\s+(.+)$' % key, text, re.M)
    if not m: return None
    v = m.group(1).split('//')[0].split()
    return tuple(float(x) for x in v[:n]) if n > 1 else float(v[0])


def numbers(body):
    scale = field(body, 'Scale', 3) or (1.0, 1.0, 1.0)
    off = list(field(body, 'Offset', 3) or (0.0, 0.0, 0.0))
    zo = field(body, 'ZOffset', 1)
    if zo is not None:  # engine: whichever of Offset.z / ZOffset comes LAST wins
        io_, iz = body.find('Offset'), body.find('ZOffset')
        if iz > io_ or io_ < 0: off[2] = zo
    return dict(scale=list(scale), offset=off, angle=field(body, 'AngleOffset', 1) or 0.0,
                pitch=field(body, 'PitchOffset', 1) or 0.0, roll=field(body, 'RollOffset', 1) or 0.0)


def world(p, n):
    """Where MD3 point p lands (MODELDEF xyz) under numbers n: Off + S*R*p'."""
    return np.array(compensate(tuple(p), tuple(n['scale']), tuple(n['offset']), n['angle'], n['pitch'], n['roll'])[0])


def sig(m): return (m['nframes'], tuple(s['xyz'].shape[1] for s in m['surfs']))
def f0(m): return np.concatenate([s['xyz'][0] for s in m['surfs']], axis=0)


# ---- 1.x blocks, keyed by (path, file) lowercase
old_blocks = {}; unplaced_blocks = {}
for m in re.finditer(r'^Model (MS_\w+)\n\{\n(.*?)^\}', open(OLD_MD).read(), re.S | re.M):
    name, body = m.group(1), m.group(2)
    p = re.search(r'Path\s+"([^"]+)"', body); f = re.search(r'Model\s+0\s+"([^"]+)"', body)
    if not p or not f or name.startswith('MS_PU_'): continue
    key = (p.group(1).replace('\\', '/').strip('/').lower(), f.group(1).lower())
    # ONLY the stamped blocks were placed in a hand (tools_reorigin_all.py, models/hud/*). The other 1.x blocks are raw
    # imports carrying the source mod's flat-HUD numbers -- the very thing we are replacing.
    if 'origin: centred' in body: old_blocks.setdefault(key, []).append((name, numbers(body)))
    else: unplaced_blocks.setdefault(key, []).append((name, numbers(body)))
# ---- 1.x meshes by signature
old_mesh = {}
for p in glob.glob(OLD_TREE + 'models/**/*.md3', recursive=True):
    try: m = read_md3(p)
    except Exception: continue
    rel = os.path.relpath(p, OLD_TREE).replace('\\', '/')
    old_mesh.setdefault(sig(m), []).append((rel, m))
# ---- families from the generated SHELF
fam = {}
for f_, n in re.findall(r'"(\w+)\|(MS_\w+)\|', open('zscript/RS_ForeignModels.zs').read()): fam.setdefault(n, f_)
# ---- donors
donors = []
for line in open('gen_from_cards.report.md'):
    m = re.match(r'\| (MS_\w+) \| (\w+)/(\w+) \|', line)
    if m: donors.append(m.groups())

out = {}; verify = []
cards_info = {}
for name, sset, gun in donors:
    d = 'cards/%s/%s' % (sset, gun)
    card = [c for c in glob.glob(d + '/*.card') if '.blend' not in c][0]
    txt = open(card).read(); lab = os.path.basename(card)[:-5]
    mesh = read_md3(os.path.join(d, lab + '.md3'))
    g = re.search(r'grip\s+line\s+\[([^\]]+)\]\s+\[([^\]]+)\]', txt)
    grip = np.array([float(x) for x in g.group(1).split(',')]) if g else None
    mu = re.search(r'muzzle\s+\[([^\]]+)\]', txt)
    muzzle = np.array([float(x) for x in mu.group(1).split(',')]) if mu else None
    cards_info[name] = dict(grip=grip, muzzle=muzzle, mesh=mesh, dir=d)
    cf = f0(mesh); placed = None
    for rel, om in old_mesh.get(sig(mesh), []):
        of = f0(om)
        if of.shape != cf.shape: continue
        delta = cf - of
        t = delta.mean(axis=0); spread = np.abs(delta - t).max()
        key = (os.path.dirname(rel).lower(), os.path.basename(rel).lower())
        blocks = old_blocks.get(key, [])
        if not blocks: continue
        bname, n = blocks[0]
        if spread < 1.0 / 64 + 1e-6 and np.abs(t).max() < 1.0 / 64 + 1e-6:
            placed = dict(n, method='1x-identical', ref=bname, note='card mesh == 1.x mesh %s' % rel); break
        if spread < 2.0 / 64 + 1e-6:  # pure translation (MD3 grid quantisation allows 1/64 per axis)
            new_off, _ = compensate(tuple(-t), tuple(n['scale']), tuple(n['offset']), n['angle'], n['pitch'], n['roll'])
            placed = dict(scale=n['scale'], offset=[round(x, 4) for x in new_off], angle=n['angle'], pitch=n['pitch'], roll=n['roll'],
                          method='1x-compensated', ref=bname, note='1.x mesh %s = card - t, t=%s' % (rel, [round(x, 4) for x in t]))
            # verification: the same mesh point lands at the same world spot under both
            if grip is not None and len(verify) < 4:
                w_old = world(grip - t, n); w_new = world(grip, placed)
                verify.append((name, bname, w_old.round(4).tolist(), w_new.round(4).tolist(), float(np.abs(w_old - w_new).max())))
            break
    if placed: out[name] = placed

# ---- family references: one placed donor per family (prefer 1x-identical, then 1x-compensated), must have grip+muzzle
refs = {}
for name in out:
    f_ = fam.get(name); ci = cards_info[name]
    if f_ and ci['grip'] is not None and ci['muzzle'] is not None:
        cur = refs.get(f_)
        if cur is None or (out[name]['method'] == '1x-identical' and out[cur]['method'] != '1x-identical'): refs[f_] = name
for name, sset, gun in donors:
    if name in out: continue
    ci = cards_info[name]; f_ = fam.get(name); ref = refs.get(f_)
    FALLBACK = {'melee': 'axe', 'kick': 'axe', 'sword': 'axe'}   # one-handed tools: the axe's placement when the family has no stamped donor
    fb = None
    if not ref and f_ in FALLBACK and FALLBACK[f_] in refs: ref = refs[FALLBACK[f_]]; fb = FALLBACK[f_]
    if ci['grip'] is None or ci['muzzle'] is None:
        out[name] = dict(method='none', note='no grip line/muzzle on the card' + ('' if ref else '; no family reference either')); continue
    if not ref:
        out[name] = dict(method='none', note='no placed (stamped) 1.x reference in family %s' % f_); continue
    rn = out[ref]; rc = cards_info[ref]
    Lref = float(np.linalg.norm(rc['muzzle'] - rc['grip'])); Lnew = float(np.linalg.norm(ci['muzzle'] - ci['grip']))
    k = Lref / Lnew if Lnew > 1e-6 else 1.0
    scale = [s * k for s in rn['scale']]              # keeps the family's mirroring sign
    n0 = dict(scale=scale, offset=[0, 0, 0], angle=rn['angle'], pitch=rn['pitch'], roll=rn['roll'])
    off = world(rc['grip'], rn) - world(ci['grip'], n0)
    out[name] = dict(scale=[round(s, 4) for s in scale], offset=[round(x, 4) for x in off], angle=rn['angle'], pitch=rn['pitch'], roll=rn['roll'],
                     method='family-ref:' + ref, ref=ref,
                     note=('family %s' % f_ + (' (no stamped donor; FALLBACK via %s)' % fb if fb else '')) + '; grip->muzzle %.1f vs ref %.1f (k=%.3f); grip lands where the ref grip lands' % (Lnew, Lref, k) if True else 'family %s; grip->muzzle %.1f vs ref %.1f (k=%.3f); grip lands where the ref grip lands' % (f_, Lnew, Lref, k))

json.dump(out, open('placement.json', 'w'), indent=1)
from collections import Counter
cnt = Counter(v['method'].split(':')[0] for v in out.values())
notes = ['# PLACEMENT_NOTES (tools_placement_from_1x.py, 2026-10-31)', '',
         'Formula (tools_md3_compensate.py, the engine-matrix replica): `world = S*R*P + Off`, `Off_new = Off_old + S*R*c\'` for a mesh shifted by -c.',
         'tools_md3_reorigin centred each 1.x mesh on its rest centroid c, so 1.x mesh = card mesh - c. The card mesh keeps the original origin,',
         'so its Offset is the 1.x Offset with that compensation UNDONE: `Off_card = compensate(-t, Scale, Off_1x, Angle, Pitch, Roll)`, t = card_f0 - old_f0.',
         'ZOffset in a 1.x block overrides Offset.z when it comes after it (engine: last one wins), as tools_reorigin_all.py did.', '',
         '## Counts: ' + ', '.join('%s %d' % kv for kv in sorted(cnt.items())), '',
         '## Verification (grip point under old mesh+old numbers vs card mesh+new numbers; must coincide)']
for v in verify: notes.append('- %s (ref %s): old %s  new %s  max|d| = %.5f' % v)
notes += ['', '## Family references', ''] + ['- %s -> %s (%s)' % (f_, r, out[r]['method']) for f_, r in sorted(refs.items())]
notes += ['', '## Not placed'] + ['- %s: %s' % (k, v['note']) for k, v in out.items() if v['method'] == 'none']
open('PLACEMENT_NOTES.md', 'w').write('\n'.join(notes) + '\n')
print(dict(cnt)); print('verify:', [(v[0], v[4]) for v in verify]); print('unplaced:', [k for k, v in out.items() if v['method'] == 'none'])
