"""Measure the insertion stroke as the magazine's FINAL APPROACH to its seat.

Four measures have been tried for this number and each broke on a different gun:

  travel_clear          the part's whole journey. The Kar98's stripper clip is
                        parked inside the buttstock, so this read 43 units --
                        a metre and a third once scaled.
  last run of movement  breaks on the assault shotgun, whose magazine goes out
                        AND back inside one unbroken run (net displacement 0.01).
  furthest from seated  breaks on the BrutalDoom guns, which throw the spent
                        magazine clear off screen: 60 to 80 units of throw.
  the mag_in phase      what the generator used. It breaks on every gun whose
                        animation throws the old magazine clear, because the
                        phase spans the throw AND the arrival: 30 to 185 units.

What all four get wrong is that they measure a JOURNEY. The number the reload
needs is not a journey, it is the distance the player's hand covers on the way
in -- so it ends at the seat, and it starts where the magazine last stopped
moving toward it.

So: take d(f), the distance from the magazine to its own seated position, with
the gun held still. Find the last run of frames over which d decreases all the
way to zero. The stroke is d at the start of that run. Anything the animation
did before that run -- the throw, the parking, the off-screen arrival -- is
outside it by construction.

The seat is the magazine's position at the card's idle frame, which is where the
gun sits when it is not being reloaded, and that is the definition of seated.
"""
import os, re, sys
import numpy as np
sys.path.insert(0, 'tools_kit')
from md3read import read_md3
from md3label import kabsch

VB = r'\[\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\s*\]'


def track(mesh_path, surf_index, body_index=None):
    """The magazine's centroid per frame, with the gun stabilised on its body.

    Picking the body as "surface 0" is wrong often enough to matter: md3label
    labelled the Garand's surface 0 as its MAGAZINE, so stabilising on surface 0
    measured the magazine against itself and found no motion at all. The body is
    the surface named `body` where the mesh carries role names, and otherwise the
    one with the most vertices -- never the surface being measured.
    """
    m = read_md3(mesh_path)
    S = m['surfs']
    if surf_index >= len(S):
        return None
    if body_index is None or body_index >= len(S) or body_index == surf_index:
        named = [i for i, s in enumerate(S) if s['name'] == 'body' and i != surf_index]
        cand = [i for i in range(len(S)) if i != surf_index]
        if not cand:
            return None
        body_index = named[0] if named else max(cand, key=lambda i: S[i]['nverts'])
    B = S[body_index]['xyz']
    out = []
    for f in range(m['nframes']):
        R, t = kabsch(B[f], B[0])
        out.append((S[surf_index]['xyz'][f] @ R.T + t).mean(0))
    return np.array(out)


def insertion(P, lo, hi, tol=0.35):
    """Stroke and axis of the final approach, inside the card's mag_in window.

    The anchor is where the magazine ENDS -- P[hi], the end of the insertion
    phase -- not where it started the animation. A stripper clip does not go back
    where it came from, and neither does a magazine on a gun whose idle pose
    differs from its loaded pose, so "returns to its frame-0 position" finds no
    insertion at all on four of the six Wolfenstein rifles.

    From that anchor, walk BACKWARD while the magazine is getting closer to it
    frame by frame. The first frame that is not closer than its successor is
    where the final approach began; everything before it -- the spent magazine
    being thrown clear, the new one arriving from off screen -- is outside the
    window by construction.

    Returns (stroke, unit axis, (start, hi)), or (None, None, None).
    """
    lo = max(0, min(lo, len(P) - 1))
    hi = max(0, min(hi, len(P) - 1))
    if hi <= lo:
        return None, None, None
    end = P[hi]
    d = np.linalg.norm(P - end, axis=1)
    f = hi
    while f > lo and d[f - 1] >= d[f] - 1e-9:
        f -= 1
    start = f
    stroke = float(d[start])
    if stroke < tol:
        # The walk back collapsed: the magazine is in the same place at both ends
        # of the window, so there is no monotonic approach to find inside it. Fall
        # back to the window's own endpoints, which is what the generator measured
        # before this -- right for a gun whose mag_in phase is already clean (the
        # Garand), and no worse for one whose phase is not, since the ceiling check
        # is what rejects those either way.
        start = lo
        stroke = float(d[lo])
        if stroke < tol:
            return None, None, None
    v = P[start] - end
    n = float(np.linalg.norm(v))
    return stroke, (v / n if n > 1e-9 else None), (start, hi)


def from_card(card_path, model_dir, mesh):
    """Read the magazine's surface index and mag_in window from the card, then measure."""
    if not os.path.exists(card_path):
        return None
    c = open(card_path, encoding='utf-8', errors='replace').read()
    si = re.search(r'(?m)^\s*mag\s+surf\s+(\d+)', c)
    mi = re.findall(r'mag_in\s+(\d+)\.\.(\d+)', c)
    if not (si and mi):
        return None
    p = os.path.join(model_dir, mesh)
    if not os.path.exists(p):
        return None
    P = track(p, int(si.group(1)))
    if P is None:
        return None
    # A card can label more than one mag_in window. The FIRST is not always the insertion: the
    # rocket launchers' first (6..7) is the rocket twitching with the shot's recoil, 1.6 units,
    # and the load is 19..33 (measured, models/hud/RocketLauncher/RPG.md3 surface 7: 53.6 units
    # out at frame 24, seated at 34). The insertion is the window with the longest approach.
    best = None
    for a, b in mi:
        r = insertion(P, int(a), int(b))
        if r and r[0] is not None and (best is None or r[0] > best[0]):
            best = r
    return best


def well_stroke(card_path):
    """Mouth to seat of the magazine well: the insertion with no animation at all.

    Some guns never show an insertion the animation can be read from. The
    flamethrowers, Aliens' pistol and rifle, the Chex zorchers and the Vanilla+
    multi-gun sheet all move the magazine 20 to 180 units across the whole of
    their mag_in window -- the spent magazine is thrown clear and the new one
    flies in from off screen, with no slower approach inside that to find.

    For those the animation cannot tell us the stroke, but the GUN can. The
    magazine well is measured in the card: its mouth and its seat. The insertion
    is the distance between them, which is the shortest honest answer and errs
    the safe way -- a stroke shorter than the author's animation leaves the
    player's hand nearer the gun, and it still ends exactly at the seat.

    Returns (distance, unit axis) or None.

    The DIRECTION stays the card's measured magazine axis, not mouth minus seat.
    Those two disagree on the railgun -- the measured axis is (-0.707, 0, -0.707)
    and mouth-minus-seat is (-0.850, -0.288, 0.441), a different direction with
    the Z sign flipped -- and the measured one is the authority, since the mouth
    is a geometric construction and the axis came off the gun's own motion. So
    the well supplies the magnitude and the animation still supplies the heading.
    """
    c = open(card_path, encoding='utf-8', errors='replace').read()
    w = re.search(r'mag_well\s+' + VB + r'\s+mouth\s+' + VB + r'\s+axis\s+' + VB, c)
    if not w:
        return None
    g = [float(x) for x in w.groups()]
    seat, mouth, axis = np.array(g[0:3]), np.array(g[3:6]), np.array(g[6:9])
    n = float(np.linalg.norm(mouth - seat))
    an = float(np.linalg.norm(axis))
    if n < 0.35 or an < 1e-9:
        return None
    return n, axis / an


def ceiling(card_path, model_dir, mesh):
    """Well depth (seat to mouth) + the magazine's length along the insertion axis."""
    c = open(card_path, encoding='utf-8', errors='replace').read()
    w = re.search(r'mag_well\s+' + VB + r'\s+mouth\s+' + VB + r'\s+axis\s+' + VB, c)
    si = re.search(r'(?m)^\s*mag\s+surf\s+(\d+)', c)
    if not (w and si):
        return None
    g = [float(x) for x in w.groups()]
    depth = float(np.linalg.norm(np.array(g[3:6]) - np.array(g[0:3])))
    axis = np.array(g[6:9])
    n = np.linalg.norm(axis)
    m = read_md3(os.path.join(model_dir, mesh))
    i = int(si.group(1))
    if n < 1e-9 or i >= len(m['surfs']):
        return None
    d = m['surfs'][i]['xyz'][0] @ (axis / n)
    return depth, float(d.max() - d.min())
