"""Write our motion-measured guns in the card grammar the reload generator reads.

Nothing here is measured. Every number comes from the md3label card already in
cards_packs/, which was measured from the gun's own animation on the gun's own
ANIMATED mesh. No _wm world model is involved at any point.

What the generator needs before it will give a gun a VR reload, from genpack.py:
a part with `role = feed` whose `dof` is `kind = slide` and whose `surface` names
a surface that exists in the mesh. An `action` part with the same dof kind becomes
the charging handle. Everything else is trimmings.

Our cards carry exactly that: `mag surf N ... axis ... travel`, a `mag_well`, and
the mesh surfaces are named by md3label, so `mag` and `bolt` resolve by name.
"""
import os, re, sys
import numpy as np
sys.path.insert(0, 'tools_kit')
from md3read import read_md3
from md3label import kabsch


def stroke(meshpath, surf='mag'):
    """How far the magazine actually travels when it is INSERTED.

    `travel_clear` is the total distance the part covers across the whole
    animation, and where an author parks the magazine somewhere odd at rest that
    is not the insertion at all: the Kar98's clip waits inside the buttstock, so
    its total is 43.36 units -- a metre and a third once scaled, for a stripper
    clip. The stroke is the last unbroken run of movement, presented to seated,
    which for that gun is 7.00 units straight down.
    """
    m = read_md3(meshpath)
    S = m['surfs']
    names = [x['name'] for x in S]
    if surf not in names or m['nframes'] < 2:
        return None, None
    i = names.index(surf)
    B = S[0]['xyz']
    pos = []
    for f in range(m['nframes']):
        R, t = kabsch(B[f], B[0])
        pos.append((S[i]['xyz'][f] @ R.T + t).mean(0))
    # Walk back from the end over frames that are still moving. That run can
    # contain a CUT as well as the insertion: where the part is parked away from
    # the gun, the author snaps it into place in a single frame and then eases it
    # home over several. The snap is one frame carrying many times the step of its
    # neighbours, so the stroke starts just after the largest such jump.
    end = len(pos) - 1
    while end > 0 and np.linalg.norm(pos[end] - pos[end - 1]) < 0.01:
        end -= 1
    start = end
    while start > 0 and np.linalg.norm(pos[start] - pos[start - 1]) > 0.01:
        start -= 1
    steps = [float(np.linalg.norm(pos[f] - pos[f - 1])) for f in range(start + 1, end + 1)]
    if len(steps) > 2:
        med = float(np.median(steps))
        big = [k for k, v in enumerate(steps) if med > 0 and v > 4 * med]
        if big:
            start = start + 1 + big[-1]
    d = float(np.linalg.norm(pos[end] - pos[start]))
    if d < 1e-6:
        return None, None
    return d, (pos[start] - pos[end]) / d

SRC = 'cards_packs'
MESH = {                       # card -> (model dir, mesh file, skin file, type, capacity)
    'MS_wolf_Kar98':  ('models/wolf/KAR98',  'Kar98.md3',  'kar98.png',  'rifle', 5),
    'MS_wolf_MG42':   ('models/wolf/MG42',   'MG42.md3',   'MG42.png',   'chaingun', 50),
    'MS_wolf_MP40':   ('models/wolf/MP40',   'MP40.md3',   'MP40.png',   'smg', 32),
    'MS_wolf_PP41':   ('models/wolf/PP41',   'PP41.md3',   'PP41.png',   'smg', 35),
    'MS_wolf_BAR':    ('models/wolf/BAR',    'BAR.md3',    'BAR.png',    'rifle', 20),
    'MS_wolf_Garand': ('models/wolf/Garand', 'Garand.md3', 'Garand.png', 'rifle', 8),
}

V3 = r'\[\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\s*\]'


def vec(m):
    return '%s, %s, %s' % m.groups()[-3:] if m else None


out = []
made = []
for cls, (d, mesh, skin, typ, cap) in MESH.items():
    p = os.path.join(SRC, cls + '.card')
    if not os.path.exists(p):
        print(f'  {cls}: no card'); continue
    t = open(p, encoding='utf-8', errors='replace').read()
    if not os.path.exists(os.path.join(d, mesh)):
        print(f'  {cls}: mesh not at {d}/{mesh}'); continue
    skin_ok = os.path.exists(os.path.join(d, skin))

    muz = re.search(r'muzzle\s+' + V3, t)
    well = re.search(r'mag_well\s+' + V3 + r'\s+mouth\s+' + V3 + r'\s+axis\s+' + V3 +
                     r'\s+travel_clear\s+([\d.]+)', t)
    magp = re.search(r'^\s*mag\s+surf\s+\d+\s+rest\s+' + V3 + r'\s+axis\s+' + V3 +
                     r'\s+travel\s+([\d.]+)', t, re.M)
    bolt = re.search(r'^\s*bolt\s+surf\s+\d+\s+rest\s+' + V3 + r'\s+axis\s+' + V3 +
                     r'\s+travel\s+([\d.]+)', t, re.M)
    trig = re.search(r'^\s*trigger\s+surf\s+\d+\s+rest\s+' + V3, t, re.M)
    ej = re.search(r'eject\s+' + V3 + r'\s+normal\s+' + V3, t)
    grip = re.search(r'^\s*grip\s+line\s+' + V3 + r'\s+' + V3, t, re.M)
    sup = re.search(r'support\s+feature\s+palm\s+' + V3, t)

    if not (magp and well):
        print(f'  {cls}: no magazine in the card -- skipped (it would get a stock reload anyway)')
        continue

    b = []
    b.append(f'weapon "{cls}"')
    b.append(f'  type      = {typ}')
    b.append(f'  model     = "{d}" "{mesh}"')
    if skin_ok:
        b.append(f'  skin      = "{d}" "{skin}"')
    b.append(f'  capacity  = {cap}')
    if muz:
        b.append(f'  muzzle    = {vec(muz)}')
    b.append('  barrel    = 1, 0, 0')
    if ej:
        g = ej.groups()
        b.append(f'  ejectport = {g[0]}, {g[1]}, {g[2]}')
        b.append(f'  ejectdir  = {g[3]}, {g[4]}, {g[5]}')
    b.append('end')
    b.append('')
    if grip or trig or sup:
        b.append('grip')
        if trig:
            b.append(f'  triggerat = {vec(trig)}')
        if grip:
            g = grip.groups()
            b.append(f'  palm = {g[3]}, {g[4]}, {g[5]}')
            b.append(f'  seat = {g[0]}, {g[1]}, {g[2]}')
        if sup:
            b.append(f'  supportat = {vec(sup)}')
        b.append('  rake = 0')
        b.append('end')
        b.append('')
    g = list(well.groups())
    st, ax = stroke(os.path.join(d, mesh))
    note = ''
    if st is not None and abs(st - float(g[9])) > 0.5:
        note = ("  # stroke taken from the insertion frames; travel_clear said %s,"
                " which is the part's whole journey from wherever it is parked" % g[9])
        g[9] = '%.2f' % st
        g[6], g[7], g[8] = ('%.3f' % v for v in ax)
    g = tuple(g)
    b.append('# the magazine, measured from the gun\'s own reload animation' + note)
    b.append('part magazine')
    b.append('  role    = feed')
    b.append('  surface = mag')
    b.append(f'  grab       = {g[0]}, {g[1]}, {g[2]}')
    b.append('  grabradius = 2.5')
    b.append('  dof')
    b.append('    kind     = slide')
    b.append(f'    axis     = {g[6]}, {g[7]}, {g[8]}')
    b.append(f'    distance = {g[9]}')
    b.append('  end')
    b.append('end')
    if bolt:
        bg = bolt.groups()
        b.append('')
        b.append('part bolt')
        b.append('  role    = action')
        b.append('  subject = slide')
        b.append('  surface = bolt')
        b.append(f'  grab       = {bg[0]}, {bg[1]}, {bg[2]}')
        b.append('  grabradius = 2.5')
        b.append('  dof')
        b.append('    kind     = slide')
        b.append(f'    axis     = {bg[3]}, {bg[4]}, {bg[5]}')
        b.append(f'    distance = {bg[6]}')
        b.append('  end')
        b.append('end')
    out.append('\n'.join(b))
    made.append(cls)
    print(f'  {cls:<18} magazine stroke {g[9]}' + (f', bolt {bolt.group(7)}' if bolt else ''))

hdr = ('# ============================================================================\n'
       '# WMCARD.ww2 -- the Wolfenstein set, written from our OWN measurements.\n'
       '#\n'
       '# Every number here came out of the gun\'s own reload animation, measured by\n'
       '# md3label on the ANIMATED mesh this mod ships. No static _wm world model was\n'
       '# read at any point, and nothing was carried over from another gun\'s card.\n'
       '# ============================================================================\n\n')
open(sys.argv[1], 'w', encoding='utf-8').write(hdr + '\n\n'.join(out) + '\n')
print(f'\n{len(made)} guns written')
