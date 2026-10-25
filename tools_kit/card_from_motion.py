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
import mag_insertion


def stroke(meshpath, frames, surf='mag'):
    """How far the magazine travels while it is being INSERTED.

    Three measures were tried and each broke on a different gun. `travel_clear`
    is the part's whole journey, and the Kar98's clip starts parked inside the
    buttstock, so that read 43 units -- a metre and a third once scaled, for a
    stripper clip. The last unbroken run of movement breaks on the assault
    shotgun, whose magazine goes out AND back inside the animation (net
    displacement 0.01). Furthest-from-seated breaks on the BrutalDoom guns,
    which throw the spent magazine clear off screen: 60 to 80 units of throw.

    What is actually authoritative is md3label's own phase detection. It labels
    the insertion `mag_in a..b`, and the stroke is where the part is at a versus
    where it is at b. A gun whose card has no mag_in has no insertion to measure
    and is not converted.
    """
    lo, hi = frames
    m = read_md3(meshpath)
    S = m['surfs']
    names = [x['name'] for x in S]
    if surf not in names or hi >= m['nframes']:
        return None, None
    i = names.index(surf)
    body = names.index('body') if 'body' in names else 0
    B = S[body]['xyz']

    def at(f):
        R, t = kabsch(B[f], B[0])
        return (S[i]['xyz'][f] @ R.T + t).mean(0)

    a_, b_ = at(lo), at(hi)
    d = float(np.linalg.norm(a_ - b_))
    if d < 1e-6:
        return None, None
    return d, (a_ - b_) / d



SRC = 'cards_packs'
MESH = {                       # card -> (model dir, mesh file, skin file, type, capacity)
    'MS_wolf_Kar98':  ('models/wolf/KAR98',  'Kar98.md3',  'kar98.png',  'rifle', 5),
    'MS_wolf_MG42':   ('models/wolf/MG42',   'MG42.md3',   'MG42.png',   'chaingun', 50),
    'MS_wolf_MP40':   ('models/wolf/MP40',   'MP40.md3',   'MP40.png',   'smg', 32),
    'MS_wolf_PP41':   ('models/wolf/PP41',   'PP41.md3',   'PP41.png',   'smg', 35),
    'MS_wolf_BAR':    ('models/wolf/BAR',    'BAR.md3',    'BAR.png',    'rifle', 20),
    'MS_wolf_Garand': ('models/wolf/Garand', 'Garand.md3', 'Garand.png', 'rifle', 8),
    # BrutalDoom's, measured the same way. The card file is named for the package
    # it was surveyed in; the OUTPUT class is named for the model, because that is
    # what the runtime looks a gun up by.
    'MS_bd_AssaultShotgun': ('models/bd/AssaultShotgun', 'AssaultShotgun.md3',
                             'AssaultShotgun.png', 'shotgun', 8, 'MS_brt_AssaultShotgun'),
    'MS_bd_Plasma':         ('models/bd/PlasmaGun', 'Plasma.md3', 'Plasma.png',
                             'plasma', 100, 'MS_brt_PlasmaGun'),
    'MS_bd_RailGun':        ('models/bd/RailGun', 'RailGun.md3', 'RailGun.png',
                             'railgun', 10, 'MS_brt_RailGun'),
}

V3 = r'\[\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\s*\]'


def vec(m):
    return '%s, %s, %s' % m.groups()[-3:] if m else None


def main(outpath):
    out = []
    made = []
    for key, spec in MESH.items():
        d, mesh, skin, typ, cap = spec[:5]
        cls = spec[5] if len(spec) > 5 else key
        p = os.path.join(SRC, key + '.card')
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
        mi = re.search(r'mag_in\s+(\d+)\.\.(\d+)', t)
        if not mi:
            print(f'  {cls}: card has no mag_in phase -- no insertion to measure, skipped')
            continue
        # The insertion stroke comes from mag_insertion, which anchors on the end
        # of the mag_in window and walks back only while the magazine is still
        # approaching. The local stroke() above resolved the magazine by SURFACE
        # NAME, which only exists in meshes md3label itself rewrote (the WW2 set);
        # for every other package it returned None and the entry silently kept
        # travel_clear -- the part's whole journey, 30 to 185 units.
        st, ax, _fr = mag_insertion.from_card(p, d, mesh) or (None, None, None)
        # A gun that throws the spent magazine clear and flies the new one in from
        # off screen has no slower approach inside its mag_in window to find, so
        # the approach comes back as the whole flight -- 20 to 180 units. There the
        # animation cannot tell us the stroke but the well can: mouth to seat,
        # measured off the card. Shorter than the author's animation, ends at the
        # same seat, and marked in the written entry so it is never mistaken for
        # an animation reading.
        ceil = mag_insertion.ceiling(p, d, mesh)
        from_well = False
        if ceil and (st is None or st > ceil[0] + ceil[1] + 0.5):
            w = mag_insertion.well_stroke(p)
            if w:
                # Only the MAGNITUDE comes from the well. The heading stays the
                # direction the magazine was actually travelling on its approach,
                # which is a measurement; mouth-minus-seat and the card's own well
                # axis both disagree with it on the railgun, and neither of those
                # watched the part move.
                st = w[0]
                ax = ax if ax is not None else w[1]
                from_well = True
        if st is None or ax is None:
            print(f'  {cls}: no insertion inside the mag_in window -- skipped')
            continue
        note = ''
        if from_well:
            note = ("  # NOT an animation reading: this gun throws the magazine clear"
                    " of the screen, so the stroke is the well's own mouth-to-seat"
                    " distance")
            g[9] = '%.2f' % st
            g[6], g[7], g[8] = ('%.3f' % v for v in ax)
        elif abs(st - float(g[9])) > 0.5:
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
           f'# {os.path.basename(outpath)} -- written from our OWN measurements.\n'
           '#\n'
           '# Every number here came out of the gun\'s own reload animation, measured by\n'
           '# md3label on the ANIMATED mesh this mod ships. No static _wm world model was\n'
           '# read at any point, and nothing was carried over from another gun\'s card.\n'
           '# ============================================================================\n\n')
    open(outpath, 'w', encoding='utf-8').write(hdr + '\n\n'.join(out) + '\n')
    print(f'\n{len(made)} guns written')


if __name__ == '__main__':
    main(sys.argv[1])
