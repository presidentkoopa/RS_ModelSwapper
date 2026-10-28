"""make_pickup.py -- the Revolver's (Moonlight's) ammo pickup: six revolver rounds in a ring, made from
the pack's own 12-gauge shell mesh (owner 2026-10-27: "one shotgun shell cut down, nose rounded, six
arranged in a ring, recoloured").

    python3 -B tools/moonammo/make_pickup.py [--depot <depot>]

Writes src/models/rsq/moonammo/moon_rounds.md3 + its skins and src/sprites/RVRDA0.png (the 2D frame, an
orthographic render of the same mesh), and prints every number it used.

SOURCES (all measured here, nothing typed in):
  * the shell: src/models/rsq/casings/shell_12ga.md3 (the pack's 12 ga hull, 70.06 mm; surfaces base /
    hull / inner / primer, axis +x, primer at the low end, open mouth at the high end).
  * the round size: the Moonlight's own rounds, src/models/bd/Moonlight/rev.md3 surfaces 4-9 at frame 20
    (where they are drawn): PCA length and radius.
  * the ring: the Moonlight's chambers, reference/moonlight/measured.txt (radius 1.8-2.0 cm in the
    controller frame at Scale 1.35, vr_weaponScale 1.02) -> mesh units.
  * the colours: the Moonlight's texture WPN-REV.png: the brass of its own round (the texels its round
    surface maps to) for the cases; the gun's blue (the most common saturated hue of the whole sheet)
    for the noses (a polymer-coated bullet).
  * the pickup's world size: BD22's 4-shell pickup sprite SHELA0 (16 px at Scale 0.9, Ammo.dec) gives
    the ring's outer diameter in map units.

STEPS
  1. The shell's open mouth (surface `inner`) is deleted with the Depot's md3_carve_disc.py (--delete,
     a disc round the shell's axis covering the whole mouth); its now-empty surface is then dropped.
  2. Cut down: the hull's front ring moves back so case + nose = the Moonlight round's length.
  3. Nose: a new surface `nose`, a round nose (quarter-circle profile, length = the case radius) closing
     the hull's front ring to a point on the axis; normals are the sphere's.
  4. Scaled uniformly to the Moonlight round's radius, stood on end (+z up, the rim on z = 0) and copied
     six times round the z axis at the chamber radius (60 degrees apart, the first on +x).
"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '../../../../tools'))); import depot as _DP	# Depot paths (tools/depot.py)
import argparse, math, os, struct, subprocess, sys, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(REPO, 'src')
ap = argparse.ArgumentParser()
ap.add_argument('--depot', default=_DP.DEPOT)
ap.add_argument('--bd22', default=(_DP.GAMEDATA + '/brutal22test6.pk3'))
A = ap.parse_args()
KIT = os.path.join(A.depot, 'tools', 'kit')
sys.path.insert(0, KIT)
from md3_carve_surface import parse, build, sname, tri_list  # noqa: E402

SHELL = os.path.join(SRC, 'models/rsq/casings/shell_12ga.md3')
MOON = os.path.join(SRC, 'models/bd/Moonlight/rev.md3')
MOONTEX = os.path.join(SRC, 'models/bd/Moonlight/WPN-REV.png')
OUTD = os.path.join(SRC, 'models/rsq/moonammo')
os.makedirs(OUTD, exist_ok=True)


def verts(s, fr=0):
    b = s['xyz'][fr]
    return np.array([struct.unpack_from('<hhh', b, k * 8) for k in range(s['nv'])], float) / 64.0


def normals(s, fr=0):
    b = s['xyz'][fr]
    out = []
    for k in range(s['nv']):
        n = struct.unpack_from('<H', b, k * 8 + 6)[0]
        a = ((n >> 8) & 255) * 2 * math.pi / 255; c = (n & 255) * 2 * math.pi / 255
        out.append((math.cos(c) * math.sin(a), math.sin(c) * math.sin(a), math.cos(a)))
    return np.array(out)


def pack_normal(n):
    n = n / (np.linalg.norm(n) or 1)
    lat = int(round(math.acos(max(-1, min(1, n[2]))) * 255 / (2 * math.pi))) & 255
    lng = int(round(math.atan2(n[1], n[0]) * 255 / (2 * math.pi))) & 255
    return (lat << 8) | lng


def set_xyz(s, P, N):
    s['xyz'] = [b''.join(struct.pack('<hhhH', *[int(round(c * 64)) for c in p], pack_normal(n)) for p, n in zip(P, N))]


# ---- measure: the Moonlight round (frame 20, surfaces 4-9) and its chambers ------------------------------
moon = parse(open(MOON, 'rb').read())
lens, rads = [], []
for i in range(4, 10):
    v = verts(moon['surfs'][i], 20)
    c = v.mean(0); _, _, Vt = np.linalg.svd(v - c); ax = Vt[0]
    t = (v - c) @ ax; r = np.linalg.norm((v - c) - np.outer(t, ax), axis=1)
    lens.append(t.max() - t.min()); rads.append(r.max())
ROUND_L, ROUND_R = float(np.mean(lens)), float(np.mean(rads))
CM_PER_U = 1.35 * 1.02			# MODELDEF.rsqmoon Scale 1.35, vr_weaponScale 1.02 (rgeo.py: 1 md3 unit x scale x WS = 1 cm)
CHAMBER_CM = (1.8 + 2.0) / 2		# reference/moonlight/README.md "six chambers on radius 1.8-2.0 cm"
RING_U = CHAMBER_CM / CM_PER_U
print('Moonlight round (rev.md3 f20, surfaces 4-9): length %.3f u (%.2f cm), radius %.3f u (%.2f cm); chamber ring %.2f cm = %.3f u'
      % (ROUND_L, ROUND_L * CM_PER_U, ROUND_R, ROUND_R * CM_PER_U, CHAMBER_CM, RING_U))

# ---- 1. the shell's mouth out, with the Depot tool -----------------------------------------------------------
sh = parse(open(SHELL, 'rb').read())
names = [sname(s) for s in sh['surfs']]
iin, ihull, ibase, iprim = names.index('inner'), names.index('hull'), names.index('base'), names.index('primer')
vin = verts(sh['surfs'][iin]); vh = verts(sh['surfs'][ihull])
HULL_R = float(np.linalg.norm(vh[:, 1:], axis=1).max())
mouth_c = (vin.min(0) + vin.max(0)) / 2; half = (vin[:, 0].max() - vin[:, 0].min()) / 2 + 0.5
tmp = tempfile.mkdtemp()
cut = os.path.join(tmp, 'shell_cut.md3')
cmd = [sys.executable, '-B', os.path.join(KIT, 'md3_carve_disc.py'), SHELL, cut, '--surface', str(iin), '--delete',
       '--centre', '%.4f' % mouth_c[0], '0', '0', '--normal', '1', '0', '0', '--band', '%.4f' % -half, '%.4f' % half,
       '--radius', '%.4f' % (HULL_R + 0.5)]
print('$', ' '.join(cmd)); print(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip())
m = parse(open(cut, 'rb').read())
assert m['surfs'][iin]['nt'] == 0, 'the mouth was not wholly deleted'
m['surfs'] = [s for k, s in enumerate(m['surfs']) if k != iin]
names = [sname(s) for s in m['surfs']]; ihull, ibase, iprim = names.index('hull'), names.index('base'), names.index('primer')

# ---- 2. cut down -----------------------------------------------------------------------------------------
S = ROUND_R / HULL_R						# uniform scale: shell units -> Moonlight mesh units
X0 = min(verts(s)[:, 0].min() for s in m['surfs'])	# the primer face, the rear of the round
NOSE = HULL_R							# round nose: length = the case radius
X_MOUTH = X0 + ROUND_L / S - NOSE				# where the case ends, shell units
h = m['surfs'][ihull]; P = verts(h); N = normals(h)
old_front = P[:, 0].max()
P[P[:, 0] > (P[:, 0].min() + old_front) / 2, 0] = X_MOUTH
set_xyz(h, P, N)
print('shell: hull radius %.3f, rear %.3f, mouth %.3f -> case cut to %.3f (%.0f%% of the hull kept), nose %.3f; scale %.5f'
      % (HULL_R, X0, old_front, X_MOUTH, 100 * (X_MOUTH - P[:, 0].min()) / (old_front - P[:, 0].min()), NOSE, S))

# ---- 3. the nose -----------------------------------------------------------------------------------------
ring = P[P[:, 0] == X_MOUTH]
angs = sorted(set(round(math.degrees(math.atan2(p[2], p[1]))) % 360 for p in ring))	# whole degrees: the int16 grid scatters a vertex by ~0.05 deg
SEG = len(angs); RINGS = 6
nv, nn, uv, tris = [], [], [], []
for j in range(RINGS + 1):			# j = 0 at the mouth, RINGS at the tip
    phi = (math.pi / 2) * j / RINGS
    x = X_MOUTH + NOSE * math.sin(phi); r = HULL_R * math.cos(phi)
    for k in range(SEG + 1 if j < RINGS else 1):
        th = 2 * math.pi * k / SEG
        nv.append((x, r * math.cos(th), r * math.sin(th)))
        nn.append((math.sin(phi), math.cos(phi) * math.cos(th), math.cos(phi) * math.sin(th)))
        uv.append((k / SEG if j < RINGS else 0.5, j / RINGS))
row = SEG + 1
for j in range(RINGS):
    for k in range(SEG):
        a = j * row + k; b = a + 1; c = (j + 1) * row + k if j + 1 < RINGS else RINGS * row
        d = c + 1 if j + 1 < RINGS else RINGS * row
        tris += [(a, c, b)] if j + 1 == RINGS else [(a, c, b), (b, c, d)]
# winding: match the hull's (its first triangle's normal points out)
ht = tri_list(h); hp = verts(h)
t0 = hp[ht[0]], hp[ht[1]], hp[ht[2]]
out_h = np.cross(t0[1] - t0[0], t0[2] - t0[0]) @ (np.array([0, t0[0][1], t0[0][2]]))
nvp = np.array(nv); a, b, c = tris[0]
out_n = np.cross(nvp[b] - nvp[a], nvp[c] - nvp[a]) @ (nvp[a] - np.array([X_MOUTH, 0, 0]))
if (out_h > 0) != (out_n > 0):
    tris = [(a, c, b) for a, b, c in tris]
nose = dict(name=b'nose'.ljust(64, b'\0'), flags=0, nsh=h['nsh'], shaders=b'moon_nose.png'.ljust(64, b'\0') + h['shaders'][64:],
            nv=len(nv), nt=len(tris), tris=struct.pack('<%di' % (3 * len(tris)), *[i for t in tris for i in t]),
            st=b''.join(struct.pack('<ff', u, v) for u, v in uv), xyz=[])
set_xyz(nose, np.array(nv), np.array(nn))
m['surfs'].append(nose)
print('nose: %d segments (the hull ring\'s own %d angles), %d rings, %d verts, %d tris' % (SEG, SEG, RINGS, len(nv), len(tris)))

# ---- 4. stand it up, scale, six in a ring ------------------------------------------------------------
def stand(p):		# shell (x axis, rear at X0) -> round (z up, rim on z=0), Moonlight units
    return np.stack([p[:, 1], p[:, 2], p[:, 0] - X0], 1) * S
def stand_n(n):
    return np.stack([n[:, 1], n[:, 2], n[:, 0]], 1)
final = []
for s in m['surfs']:
    P0, N0 = stand(verts(s)), stand_n(normals(s))
    Ps, Ns, T, ST = [], [], [], b''
    for k in range(6):
        a = math.radians(60 * k); R = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
        Ps.append(P0 @ R.T + R @ np.array([RING_U, 0, 0])); Ns.append(N0 @ R.T)
        T += [i + k * s['nv'] for i in tri_list(s)]; ST += s['st']
    s2 = dict(s); s2['nv'] = 6 * s['nv']; s2['nt'] = 6 * s['nt']
    s2['tris'] = struct.pack('<%di' % len(T), *T); s2['st'] = ST
    set_xyz(s2, np.vstack(Ps), np.vstack(Ns)); final.append(s2)
m['surfs'] = final
m['nfr'] = 1
# frame header: bounds / origin / radius (md3 frame: mins 3f, maxs 3f, origin 3f, radius f, name 16s)
allp = np.vstack([verts(s) for s in final])
mn, mx = allp.min(0), allp.max(0)
m['frames'] = [struct.pack('<3f3f3ff16s', *mn, *mx, 0, 0, 0, float(np.linalg.norm(allp, axis=1).max()), b'rounds')]
m['ntag'] = 0; m['tags'] = [b'']
m['name'] = b'moon_rounds.md3'.ljust(64, b'\0')
open(os.path.join(OUTD, 'moon_rounds.md3'), 'wb').write(build(m))
print('pickup mesh: %s, surfaces %s, bounds %s .. %s Moonlight units' % (os.path.join(OUTD, 'moon_rounds.md3'),
      [(sname(s), s['nv'], s['nt']) for s in final], mn.round(3), mx.round(3)))

# ---- colours from the Moonlight's texture ------------------------------------------------------------------
tex = np.asarray(Image.open(MOONTEX).convert('RGB')).astype(float); TH, TW, _ = tex.shape
rs = moon['surfs'][4]; st = np.array([struct.unpack_from('<ff', rs['st'], k * 8) for k in range(rs['nv'])])
u0, u1 = st[:, 0].min(), st[:, 0].max(); v0, v1 = np.sort(st[:, 1])[[0, -1]]
box = tex[int(v0 * TH):int(math.ceil(v1 * TH)), int(u0 * TW):int(math.ceil(u1 * TW))].reshape(-1, 3)
hsv = np.array([Image.fromarray(np.uint8([[c]])).convert('HSV').getpixel((0, 0)) for c in box])
brass = box[(hsv[:, 1] > 150) & (hsv[:, 2] > 120) & (hsv[:, 0] > 15) & (hsv[:, 0] < 45)].mean(0)
allpx = tex.reshape(-1, 3); allh = np.asarray(Image.fromarray(np.uint8(tex)).convert('HSV')).reshape(-1, 3)
sat = allh[:, 1] > 120
hist = np.bincount(allh[sat, 0] // 8, minlength=32); hue = hist.argmax()
blue = allpx[sat & (allh[:, 0] // 8 == hue)].mean(0)
print('colours (WPN-REV.png %dx%d): round box u %.3f-%.3f v %.3f-%.3f -> brass %s from %d texels; the sheet\'s commonest saturated hue bin %d -> %s from %d texels'
      % (TW, TH, u0, u1, v0, v1, brass.round(0), int(((hsv[:, 1] > 150) & (hsv[:, 2] > 120) & (hsv[:, 0] > 15) & (hsv[:, 0] < 45)).sum()), hue, blue.round(0), int((sat & (allh[:, 0] // 8 == hue)).sum())))


def recolour(src, dst, rgb):
    # the shell's skins are flat (every UV of the mesh is 0.5, 0.5): keep their luminance pattern, take the hue
    im = np.asarray(Image.open(src).convert('RGB')).astype(float)
    lum = im.mean(2, keepdims=True); lum = lum / max(lum.mean(), 1)
    Image.fromarray(np.uint8(np.clip(lum * rgb, 0, 255))).save(dst)


CAS = os.path.join(SRC, 'models/rsq/casings')
recolour(os.path.join(CAS, 'casing_brass.png'), os.path.join(OUTD, 'moon_brass.png'), brass)		# base (rim, head)
recolour(os.path.join(CAS, 'shell_hull.png'), os.path.join(OUTD, 'moon_case.png'), brass * 0.92)	# hull = the case body, a shade under the head
nose_img = np.zeros((16, 16, 3))
for y in range(16):			# v 0 at the mouth, 1 at the tip: a little lighter toward the tip
    nose_img[y] = np.clip(blue * (0.85 + 0.3 * y / 15), 0, 255)
Image.fromarray(np.uint8(nose_img)).save(os.path.join(OUTD, 'moon_nose.png'))
Image.open(os.path.join(CAS, 'casing_primer.png')).save(os.path.join(OUTD, 'moon_primer.png'))

# ---- world size: BD22's SHELA0 (16 px, Scale 0.9) = the ring's outer diameter ----------------------------
import zipfile
with zipfile.ZipFile(A.bd22) as z:
    shel = Image.open(z.open('sprites/Items/Pickups/SHELA0.png'))
SHEL_W = shel.size[0] * 0.9
outer = float(np.linalg.norm(allp[:, :2], axis=1).max()) * 2
WSCALE = SHEL_W / outer
print('world: SHELA0 %d px x 0.9 = %.1f map units; ring outer diameter %.3f u -> MODELDEF Scale %.4f (height %.1f map units)'
      % (shel.size[0], SHEL_W, outer, WSCALE, (mx[2] - mn[2]) * WSCALE))

# ---- the 2D frame (sprite RVRD A): an orthographic 3/4 render of the same mesh, flat-lit --------------------
skins = {'base': os.path.join(OUTD, 'moon_brass.png'), 'hull': os.path.join(OUTD, 'moon_case.png'),
         'primer': os.path.join(OUTD, 'moon_primer.png'), 'nose': os.path.join(OUTD, 'moon_nose.png')}
PX = 4; Wd = int(math.ceil(SHEL_W)) * PX; Hd = int(math.ceil((mx[2] - mn[2]) * WSCALE * 1.6 + 6)) * PX
img = np.zeros((Hd, Wd, 4)); zb = np.full((Hd, Wd), -1e9)
el = math.radians(30); L = np.array([0.4, -0.5, 0.75]); L /= np.linalg.norm(L)
for s in final:
    col = np.asarray(Image.open(skins[sname(s)]).convert('RGB')).reshape(-1, 3).mean(0)
    V = verts(s) * WSCALE; T = np.array(tri_list(s)).reshape(-1, 3)
    # view from -y, raised 30 degrees: screen x = x, screen y = z cos(el) + y sin(el), depth = -y cos(el) + z sin(el)
    sx = V[:, 0] * PX + Wd / 2; sy = Hd - (V[:, 2] * math.cos(el) + V[:, 1] * math.sin(el)) * PX - Hd * 0.3
    dz = -V[:, 1] * math.cos(el) + V[:, 2] * math.sin(el)
    for a, b, c in T:
        n = np.cross(V[b] - V[a], V[c] - V[a]); nl = np.linalg.norm(n)
        if nl == 0: continue
        shade = 0.45 + 0.55 * abs(n @ L) / nl
        xs, ys = [sx[a], sx[b], sx[c]], [sy[a], sy[b], sy[c]]
        x0, x1 = int(max(min(xs), 0)), int(min(max(xs) + 1, Wd)); y0, y1 = int(max(min(ys), 0)), int(min(max(ys) + 1, Hd))
        den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(den) < 1e-9: continue
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                w0 = ((ys[1] - ys[2]) * (xx + .5 - xs[2]) + (xs[2] - xs[1]) * (yy + .5 - ys[2])) / den
                w1 = ((ys[2] - ys[0]) * (xx + .5 - xs[2]) + (xs[0] - xs[2]) * (yy + .5 - ys[2])) / den
                w2 = 1 - w0 - w1
                if min(w0, w1, w2) < 0: continue
                d = w0 * dz[a] + w1 * dz[b] + w2 * dz[c]
                if d > zb[yy, xx]:
                    zb[yy, xx] = d; img[yy, xx, :3] = col * shade; img[yy, xx, 3] = 255
spr = Image.fromarray(np.uint8(img)).resize((Wd // PX, Hd // PX), Image.LANCZOS)
bb = spr.getbbox(); spr = spr.crop(bb)
os.makedirs(os.path.join(SRC, 'sprites'), exist_ok=True)
from PIL import PngImagePlugin
info = PngImagePlugin.PngInfo(); info.add(b'grAb', struct.pack('>ii', spr.size[0] // 2, spr.size[1] - 1))	# centred, standing on the floor
spr.save(os.path.join(SRC, 'sprites', 'RVRDA0.png'), pnginfo=info)
print('sprite RVRDA0.png %dx%d (render of the mesh at the world scale, 1 px = 1 map unit)' % spr.size)
print('MODELDEF Scale %.4f' % WSCALE)
