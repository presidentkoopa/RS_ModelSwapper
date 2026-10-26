"""handfit_cards.py -- the per-gun hand table for a built set, from the cards, by the kit's own method.

The kit's method (hands/HAND_FITTING.md, align_free.py, fitall_free.py): take Ermac's already-posed
hand, keep the pose, and find the TRANSLATION that puts its measured gripping face (gripregions.json)
onto the target gun by ICP. What changes here is only the anchor: the search box is a tight window
round the card's own `palm` (gun hand) and `supportat` (support hand), where the kit searched a
28 x 10 x 23 cm box and its gun-hand fits wandered 3-5 cm.

Output: zscript/rsq/handtable.zs in the 1.96b format, a render sheet per gun (gun + both hands) and
a score per gun (median distance from the hand's contact face to the gun surface). Positions are
the controller frame, cm, F forward / L left / U up; hooks are (L, U, -F) as rsq_hands_gen does.

usage: python3 handfit_cards.py <build dir> <rs_vr_weapons root> <set>
"""
import os, sys, json
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gunview, hudrender                      # kit, unmodified
import card2quest as c2q, genpack

# 2026-10-25: these were upload paths that do not exist on this machine. The measured
# gripping faces ship in the Depot (tools/kit/gripregions.json) and Ermac's cut hand
# meshes inside the kit itself, where ermac.py already points -- the same two files the
# melee fits use.
# the owner's PC paths, overridable for any other machine (MS_GRIPREGIONS, MS_ERMAC_HANDS)
REGIONS_JSON = os.environ.get('MS_GRIPREGIONS', 'E:/DOOMWork/RSQ_WeaponDepot/tools/kit/gripregions.json')
ERMAC = os.environ.get('MS_ERMAC_HANDS', 'C:/Users/Command/Desktop/Quest_Weapons_Kit/kit/kit/ermac/hand')   # hand.md3 / hand2.md3, the frames the regions were measured on
PL = dict(scale=[-1.0, 1.0, 1.0], off=[0.0, -24.0, -10.0])                # Ermac's placement (ermac.PL)
REGIONS = json.load(open(REGIONS_JSON))['poses']

# Ermac pose -> the letter the shipped hand.md3 / hand2.md3 carry it under (1.96b MODELDEF.rsq comments)
GUN_LETTER = {6: 'A', 19: 'B', 30: 'C', 47: 'D', 95: 'E', 106: 'F', 113: 'G', 29: 'H'}
SUP_LETTER = {4: 'A', 15: 'B', 33: 'C', 80: 'D', 91: 'E'}
# measured gripping faces exist for: hand 19, 6, 30, 106; hand2 4, 15, 91. A gun type whose Ermac
# pose is not measured takes the nearest measured one (said in the report, never silently).
#   type -> (gun hand two-handed, gun hand one-handed, support pose, support kind, BD trigger letter)
POSE = {
    'pistol':       (19, 6, 4, 'same', 'C'),
    'revolver':     (19, 6, 4, 'same', 'C'),
    'shotgun':      (30, 30, 15, 'wrap', 'Q'),
    'breakaction':  (30, 30, 15, 'wrap', 'P'),      # Ermac ssg pose 47 / 33 unmeasured -> shotgun 30 / 15
    'rifle':        (106, 106, 15, 'wrap', 'O'),    # BD22 used plasma 106 for its rifles
    'smg':          (106, 106, 15, 'wrap', 'O'),
    'chaingun':     (106, 106, 15, 'wrap', 'I'),    # chaingun 84 / 70 unmeasured
    'launcher':     (106, 106, 15, 'wrap', 'G'),    # rocket 95 / 80 unmeasured
    'plasma':       (106, 106, 15, 'wrap', 'L'),
    'bfg':          (106, 106, 15, 'wrap', 'B'),    # bfg 113 / 98 unmeasured
    'railgun':      (106, 106, 15, 'wrap', 'O'),
    'flamethrower': (106, 106, 15, 'wrap', 'O'),
    'chainsaw':     (106, 106, 15, 'wrap', 'R'),    # chainsaw 29 / 14 unmeasured
    'grenade':      (6, 6, 4, 'same', ''),
}
GUN_DROP = -1.5          # fitall: the gun hand sits 1.5 cm lower than the ICP puts it (BD22's own table)


def surface_points(it, per_tri=True):
    """align.surface_points, verbatim logic"""
    pts = []
    for tris, raw in gunview.item_mesh(it):
        v = gunview.to_fl(hudrender.to_local(raw, it))
        pts.append(v)
        if per_tri:
            pts.append((v[tris[:, 0]] + v[tris[:, 1]] + v[tris[:, 2]]) / 3)
            for w in (0.25, 0.75):
                pts.append(v[tris[:, 0]] * w + v[tris[:, 1]] * (1 - w))
                pts.append(v[tris[:, 1]] * w + v[tris[:, 2]] * (1 - w))
                pts.append(v[tris[:, 2]] * w + v[tris[:, 0]] * (1 - w))
    return np.concatenate(pts)


def box(p, f, l, u):
    m = (p[:, 0] > f[0]) & (p[:, 0] < f[1]) & (p[:, 1] > l[0]) & (p[:, 1] < l[1]) & (p[:, 2] > u[0]) & (p[:, 2] < u[1])
    return p[m]


def icp_translate(src, dst, t0, iters=40, keep=0.8):
    """align.icp_translate, verbatim logic"""
    tree = cKDTree(dst)
    t = np.array(t0, float)
    for _ in range(iters):
        d, idx = tree.query(src + t)
        k = np.argsort(d)[:max(10, int(len(d) * keep))]
        step = (dst[idx[k]] - (src[k] + t)).mean(0)
        t += step
        if np.linalg.norm(step) < 1e-3:
            break
    d, _ = tree.query(src + t)
    return t, float(np.median(d))


def hand_item(mesh, frame, shift=(0, 0, 0), color=(225, 170, 135)):
    f, l, u = shift
    return dict(path='%s/%s.md3' % (ERMAC, mesh), frame=frame, hook=[round(l, 2), round(u, 2), round(-f, 2)], rot=[0, 0, 0], color=list(color), **PL)


def hand_points(key):
    rec = REGIONS[key]
    return surface_points(hand_item(rec['mesh'], rec['frame']), per_tri=False)


def contact_patch(key):
    return np.array(REGIONS[key]['contact'], float)


def stored_patch(key, r=3.0, pad=4.0, nang=48, step=0.4):
    """align_free.stored_patch, verbatim logic"""
    rec = REGIONS[key]
    c, a, rad = np.array(rec['point'], float), np.array(rec['axis'], float), float(rec['radius'])
    t = np.array([1., 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1., 0])
    e1 = np.cross(a, t); e1 /= np.linalg.norm(e1)
    e2 = np.cross(a, e1)
    t0, t1 = rec['extent']
    ts = np.arange(t0 - pad, t1 + pad + 1e-9, step)
    th = np.arange(nang) * (2 * np.pi / nang)
    ring = np.outer(np.cos(th), e1) * rad + np.outer(np.sin(th), e2) * rad
    pts = (c + np.einsum('i,j->ij', ts, a)[:, None, :] + ring[None, :, :]).reshape(-1, 3)
    d, _ = cKDTree(hand_points(key)).query(pts)
    return pts[d < r]


def section(gpts_tris, f):
    """support.section: where the gun's surface crosses the plane F = f"""
    pts = []
    for v, tris in gpts_tris:
        a, b, d = v[tris[:, 0]], v[tris[:, 1]], v[tris[:, 2]]
        for p, q in ((a, b), (b, d), (d, a)):
            s = (p[:, 0] - f) * (q[:, 0] - f)
            m = s < 0
            if m.any():
                w = (f - p[m, 0]) / (q[m, 0] - p[m, 0])
                pts.append(p[m] + (q[m] - p[m]) * w[:, None])
    return np.concatenate(pts) if pts else np.zeros((0, 3))


def front_point(gpts_tris, f, lmax=4.0):
    """support.front_point: the cross-section's middle if thin enough to wrap, else 2.5 cm above its underside"""
    v = section(gpts_tris, f)
    m = abs(v[:, 1]) < lmax
    if not m.any():
        return None, (0, 0)
    lo = v[m, 2].min()
    us = np.sort(v[m, 2]); hi = lo
    for u in us:
        if u - hi > 2.0:
            break
        hi = u
    u = lo + min(2.5, (hi - lo) / 2)
    return [f, 0.0, round(float(u), 2)], (float(lo), float(hi))


def fit_gun(gun_pts, palm, key):
    """the gun hand: its measured contact face onto the gun, searched in a tight window round the card palm"""
    patch = contact_patch(key)
    dst = box(gun_pts, f=(palm[0] - 9, palm[0] + 9), l=(palm[1] - 5, palm[1] + 5), u=(palm[2] - 9, palm[2] + 9))
    if len(dst) < 20:
        return None, None, 'no gun surface round the palm'
    t0 = np.asarray(palm) - patch.mean(0)
    t, err = icp_translate(patch, dst, t0)
    t = t + np.array([0, 0, GUN_DROP])
    return t, err, ''


def fit_support(gun_pts, gpt, supportat, key):
    """the support hand: the cylinder stand-in (fitall_free's wrap branch) fitted round the card's
    own supportat -- the owner's measured point -- in a tight window, not the kit's front_point guess"""
    patch = stored_patch(key)
    fp = [float(x) for x in supportat]
    reg = dict(f=(fp[0] - 6, fp[0] + 6), l=(fp[1] - 6, fp[1] + 6), u=(fp[2] - 6, fp[2] + 6))
    dst = box(gun_pts, **reg)
    if len(dst) < 20:
        return None, None, None, 'no gun surface at the support point'
    t0 = np.asarray(fp) - patch.mean(0)
    t, err = icp_translate(patch, dst, t0)
    return t, err, fp, ''


def gun_tris(it):
    return [(gunview.to_fl(hudrender.to_local(raw, it)), tris) for tris, raw in gunview.item_mesh(it)]


def table_zs(rows):
    """RSQ_HandTable in the 1.96b layout. rows: list of dicts(cls, one, two, sup, hook, rot, shook, srot, spoint, trig)"""
    L = ['// generated by c2q/handfit_cards.py from the set\'s cards -- do not edit by hand',
         '// Per gun: gun-hand frame (one hand, two hands), its hook and rotation, support frame, its hook',
         '// and rotation (ModifyBobLayer3D units), and where the support hand holds the gun',
         '// (metres in the gun hand\'s frame: forward, left, up). Ermac\'s poses, moved onto each gun',
         '// by the kit\'s ICP anchored on the card\'s palm / supportat.', 'class RSQ_HandTable abstract', '{',
         '\tclearscope static int Index(Weapon w)', '\t{', '\t\tif (!w)', '\t\t\treturn 0;']
    for i, r in enumerate(rows, 1):
        L.append("\t\tif (w is '%s')\treturn %d;" % (r['cls'], i))
    L += ['\t\treturn 0;', '\t}', '']
    def strs(name, key):
        L.extend(['\tclearscope static String %s(int i)' % name, '\t{',
                  '\t\tstatic const String v[] = { "", %s };' % ', '.join('"%s"' % r[key] for r in rows),
                  '\t\treturn i > 0 && i < v.Size() ? v[i] : "";', '\t}', ''])
    def vecs(name, key):
        xs = ', '.join('%.3f' % r[key][0] for r in rows); ys = ', '.join('%.3f' % r[key][1] for r in rows); zs = ', '.join('%.3f' % r[key][2] for r in rows)
        L.extend(['\tclearscope static Vector3 %s(int i)' % name, '\t{',
                  '\t\tstatic const double x[] = { 0, %s };' % xs, '\t\tstatic const double y[] = { 0, %s };' % ys,
                  '\t\tstatic const double z[] = { 0, %s };' % zs,
                  '\t\tif (i <= 0 || i >= x.Size())', '\t\t\treturn (0, 0, 0);', '\t\treturn (x[i], y[i], z[i]);', '\t}', ''])
    strs('GunOne', 'one'); strs('GunTwo', 'two'); strs('Support', 'sup')
    vecs('GunHook', 'hook'); vecs('GunRot', 'rot'); vecs('SupportHook', 'shook'); vecs('SupportRot', 'srot'); vecs('SupportPoint', 'spoint')
    strs('Trigger', 'trig')
    vecs('GunHookTwo', 'hook'); vecs('GunRotTwo', 'rot')
    L += ['}', '']
    return '\n'.join(L)


def main(build, root, which):
    rep = json.load(open(os.path.join(build, 'genpack_report.json')))
    cards = {w['cls']: w for w in c2q.load_cards(root)}
    members = genpack.set_members(root, which)
    md = open(os.path.join(build, 'MODELDEF.wmq')).read()
    import re
    blocks = {}
    for m in re.finditer(r'Model (\w+)\n\{(.*?)\n\}', md, re.S):
        blocks.setdefault(m.group(1), m.group(2))          # the HUD block comes first; the pickup block second
    rows = []; notes = {}
    os.makedirs(os.path.join(build, '_hands'), exist_ok=True)
    for cls, card_cls in members.items():
        w = cards.get(card_cls)
        b = blocks.get(cls)
        if not w or not b or 'palm' not in w['grip']:
            notes[cls] = 'no card palm / no model block'; continue
        path = re.search(r'Path "([^"]+)"', b).group(1); model = re.search(r'Model 0 "([^"]+)"', b).group(1)
        scale = [float(x) for x in re.search(r'Scale ([-\d. ]+)', b).group(1).split()]
        off = [float(x) for x in re.search(r'Offset ([-\d.]+) ([-\d.]+)', b).groups()]
        zoff = float(re.search(r'ZOffset ([-\d.]+)', b).group(1))
        fr = int(re.search(r'FrameIndex \w+ A 0 (\d+)', b).group(1))
        it = dict(path=os.path.join(build, path, model), frame=fr, scale=scale, off=[off[0], off[1], zoff], color=[150, 155, 170])
        typ, _ = genpack.gun_type(cls, w['keys'])
        two, one, sup, kind, trig = POSE.get(typ, POSE['rifle'])
        geo = c2q.geometry(w, tuple(scale), (off[0], off[1], zoff))
        palm = np.array(geo['palm'])
        gpt = gun_tris(it)
        gun_pts = surface_points(it)
        key1 = 'hand:%d' % two
        t, err, why = fit_gun(gun_pts, palm, key1)
        if t is None:
            notes[cls] = 'gun hand: ' + why; continue
        row = dict(cls=cls, one=GUN_LETTER[one], two=GUN_LETTER[two], sup=SUP_LETTER[sup], trig=trig,
                   hook=(round(t[1], 3), round(t[2], 3), round(-t[0], 3)), rot=(0, 0, 0), srot=(0, 0, 0))
        info = 'gun hand %s shift F%+.1f L%+.1f U%+.1f (contact face %.2f cm from the gun)' % (key1, t[0], t[1], t[2], err)
        if kind == 'same':
            t2 = t.copy(); sp = (palm / 100.0)
            info += '; support cups the gun hand'
        else:
            sa = geo.get('supportat')
            if not sa:
                notes[cls] = info + '; no supportat on card: support hand off'
                row.update(sup='', shook=(0, 0, 0), spoint=(0, 0, 0)); rows.append(row); continue
            t2, err2, fp, why2 = fit_support(gun_pts, gpt, sa, 'hand2:%d' % sup)
            if t2 is None:
                notes[cls] = info + '; support: ' + why2
                row.update(sup='', shook=(0, 0, 0), spoint=(0, 0, 0)); rows.append(row); continue
            sp = np.array(fp) / 100.0
            info += '; support hand2:%d at F %.1f (cylinder %.2f cm from the gun)' % (sup, fp[0], err2)
        row.update(shook=(round(t2[1], 3), round(t2[2], 3), round(-t2[0], 3)), spoint=tuple(np.round(sp, 3)))
        rows.append(row); notes[cls] = info
        # the check sheet: gun + both hands, side and bottom
        items = [it, hand_item('hand', two, t)]
        if kind != 'same' or True:
            items.append(hand_item('hand2', sup, t2, color=(120, 200, 140)))
        marks = [(*palm, 'palm', (255, 200, 60))]
        if geo.get('supportat'):
            marks.append((*geo['supportat'], 'support', (120, 230, 140)))
        try:
            from PIL import Image
            a = os.path.join(build, '_hands', cls + '.side.png'); bb = os.path.join(build, '_hands', cls + '.bottom.png')
            gunview.view(items, a, 'side', px=5, marks=marks, title='%s hands' % cls)
            gunview.view(items, bb, 'bottom', px=5, marks=marks, title='%s hands' % cls)
            A, B = Image.open(a), Image.open(bb)
            O = Image.new('RGB', (max(A.width, B.width), A.height + B.height)); O.paste(A, (0, 0)); O.paste(B, (0, A.height))
            O.save(os.path.join(build, '_hands', cls + '.png')); os.remove(a); os.remove(bb)
        except Exception as e:
            notes[cls] += '; sheet failed: %s' % e
    open(os.path.join(build, 'zscript/rsq/handtable.zs'), 'w').write(table_zs(rows))
    json.dump(dict(rows=rows, notes=notes), open(os.path.join(build, 'handfit_report.json'), 'w'), indent=1)
    for cls in members:
        print('%-24s %s' % (cls, notes.get(cls, '')))
    print('-> %d guns in the hand table' % len(rows))


if __name__ == '__main__':
    main(*sys.argv[1:4])
