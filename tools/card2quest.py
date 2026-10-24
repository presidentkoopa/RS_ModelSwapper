"""card2quest.py -- REMA WMCARD -> Quest (stock QZD 17.x) weapon geometry + placement.

Stage 1 (this file): per weapon
  * resolve `base =` variants
  * HUD MODELDEF Scale from the REMA MODELDEF world scale (world = hud x 0.34)
  * HUD Offset so the card's `palm` sits on the Quest grip reference
  * the reload table numbers the Quest runtime wants, in F/L/U cm (rgeo.to_flu chain)
  * a side/bottom check sheet per gun with the measured points marked
Writes <out>/quest_geometry.json and <out>/sheets/<cls>.png

usage: python -B card2quest.py <rs_vr_weapons root> <out dir> [class ...]
"""
import sys, os, re, json, glob
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, '/mnt/user-data/uploads/Quest_Weapons_Kit/kit/kit/tool/hands')   # gunview, hudrender (kit, unmodified)
import wmcard, hudrender, gunview

WS = 1.02                               # vr_weaponScale the kit measured with
K = np.array([0.0, 5.0, 30.0])
WORLD_PER_HUD = 0.34                    # REMA MODELDEF world scale = HUD scale x 0.34 (card header)
GRIP_REF = np.array([-5.5, 0.0, -8.5])  # F/L/U cm: where the Quest gun hand's grip centre sits (kit support.py C0)


# ---------------------------------------------------------------- the chain (rgeo.to_flu, inlined)
def to_flu(v, scale, off):
    v = np.atleast_2d(np.asarray(v, float))
    xs, ys, zs = scale; xo, yo, zo = off
    r = np.stack([v[:, 0], v[:, 2], v[:, 1]], 1) * WS
    p = np.stack([r[:, 2], r[:, 1], -r[:, 0]], 1)
    p = p * np.array([xs, zs, ys]) + np.array([xo, zo, yo]) + K
    return np.stack([-p[:, 2], -p[:, 0], p[:, 1]], 1)


def dir_flu(d, scale):
    """a direction through the same chain (no offsets), unit"""
    a = to_flu(np.zeros(3), scale, (0, 0, 0))[0]
    b = to_flu(np.asarray(d, float), scale, (0, 0, 0))[0]
    u = b - a
    return u / (np.linalg.norm(u) + 1e-12)


def offset_for(palm, scale, target=GRIP_REF):
    """MODELDEF Offset (x, y, zoff) that puts model point `palm` at F/L/U `target`"""
    xs, ys, zs = scale
    px, py, pz = np.asarray(palm, float)
    # F = x ws ys - yo - 30 ; L = -(y ws xs) - xo ; U = z ws zs + zo + 5
    yo = px * WS * ys - 30 - target[0]
    xo = -(py * WS * xs) - target[1]
    zo = target[2] - 5 - pz * WS * zs
    return (round(float(xo), 4), round(float(yo), 4), round(float(zo), 4))


# ---------------------------------------------------------------- REMA MODELDEF scales
def modeldef_scales(root):
    t = open(os.path.join(root, 'MODELDEF.txt'), encoding='latin-1').read()
    for sub in ('plus/MODELDEF.txt', 'RS_Modern/MODELDEF.txt', 'RS_Modern/MODELDEF.breach', 'bd22/MODELDEF.txt'):
        p = os.path.join(root, sub)
        if os.path.exists(p):
            t += '\n' + open(p, encoding='latin-1').read()
    out = {}
    for cls, b in re.findall(r'Model\s+(\S+)\s*\{(.*?)\n\}', t, re.S):
        mdl = re.search(r'Model\s+0\s+"([^"]+)"', b)
        sc = re.search(r'^\s*Scale\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)', b, re.M)
        if mdl and sc:
            out.setdefault(os.path.basename(mdl.group(1)).lower(), tuple(float(x) for x in sc.groups()))
    return out


def modeldef_info(root):
    """class -> dict(scale, models=[(file, frame), ...]) from REMA's MODELDEFs: the rest frame of an
    IQM rig is Breach's own Ready frame (MK18 25, MP5 109, Benelli 59), and a prop may be several
    models (the suppressed MK18: gun + silencer + laser)."""
    t = open(os.path.join(root, 'MODELDEF.txt'), encoding='latin-1').read()
    for sub in ('plus/MODELDEF.txt', 'RS_Modern/MODELDEF.txt', 'RS_Modern/MODELDEF.breach', 'bd22/MODELDEF.txt'):
        p = os.path.join(root, sub)
        if os.path.exists(p):
            t += '\n' + open(p, encoding='latin-1').read()
    out = {}
    for cls, b in re.findall(r'Model\s+(\S+)\s*\{(.*?)\n\}', t, re.S):
        sc = re.search(r'^\s*Scale\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)', b, re.M)
        models = dict((int(i), f) for i, f in re.findall(r'^\s*Model\s+(\d+)\s+"([^"]+)"', b, re.M))
        frames = dict((int(i), int(fr)) for i, fr in re.findall(r'^\s*FrameIndex\s+\S+\s+\S+\s+(\d+)\s+(\d+)', b, re.M))
        if sc and models:
            out.setdefault(cls, dict(scale=tuple(float(x) for x in sc.groups()),
                                     models=[(models[i], frames.get(i, 0)) for i in sorted(models)]))
    return out


# ---------------------------------------------------------------- cards
def load_cards(root):
    files = sorted(glob.glob(os.path.join(root, 'WMCARD.*'))) + sorted(glob.glob(os.path.join(root, 'RS_Modern', 'WMCARD.*')))
    ws = wmcard.load(files)
    by = {w['cls']: w for w in ws}
    # resolve base = : copy everything, then overlay the variant's own keys
    for w in ws:
        b = w['keys'].get('base')
        if b and b in by:
            src = by[b]
            keys = dict(src['keys']); keys.update({k: v for k, v in w['keys'].items() if k != 'base'})
            w['keys'] = keys
            if not w['grip']: w['grip'] = dict(src['grip'])
            if not w['parts']: w['parts'] = src['parts']; w['order'] = list(src['order'])
            w['variant_of'] = b
    return ws


def model_path(root, w):
    m = w['keys'].get('model')
    if not m:
        return None
    d, f = (m if isinstance(m, list) else [None, m])
    if d is None:
        return None
    for base in (root, os.path.join(root, 'RS_Modern')):
        p = os.path.join(base, d, f)
        if os.path.exists(p):
            return p
    return os.path.join(root, d, f)


def rest_frame(w, path=None):
    """the rest frame: the card's `restframe` if it has one, else the first frame after
    which the body stops turning (HQT motion.py's test): a raise ends where consecutive-
    frame body rotation drops under 2 degrees. IQM: 0."""
    if 'restframe' in w['keys']:
        return int(w['keys']['restframe'])
    if not path or path.lower().endswith('.iqm'):
        return 0
    surfs = hudrender.load(path)
    tris, X = max(surfs, key=lambda s: s[1].shape[1])
    nf = X.shape[0]
    def kab(P, Q):
        pc, qc = P.mean(0), Q.mean(0); H = (P - pc).T @ (Q - qc); U, _, Vt = np.linalg.svd(H)
        d = np.sign(np.linalg.det(Vt.T @ U.T)); return Vt.T @ np.diag([1, 1, d]) @ U.T
    for f in range(1, nf):
        R = kab(X[f - 1], X[f]); ang = np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
        if ang < 2.0:
            return f - 1
    return 0


# ---------------------------------------------------------------- geometry per gun
def geometry(w, scale, off):
    g = {}
    grip = w['grip']
    for k in ('palm', 'triggerat', 'supportat', 'seat'):
        if k in grip:
            g[k] = to_flu(grip[k], scale, off)[0].round(3).tolist()
    g['rake_deg'] = grip.get('rake')
    for k in ('muzzle', 'ejectport'):
        if k in w['keys'] and isinstance(w['keys'][k], list):
            g[k] = to_flu(w['keys'][k], scale, off)[0].round(3).tolist()
    for k in ('barrel', 'ejectdir'):
        if k in w['keys'] and isinstance(w['keys'][k], list):
            g[k] = dir_flu(w['keys'][k], scale).round(3).tolist()
    parts = {}
    for name in w['order']:
        p = w['parts'][name]; d = p['dof']; kk = p['keys']
        q = dict(role=kk.get('role'), subject=kk.get('subject'), surfaces=p['surfaces'], kind=d.get('kind'))
        if 'grab' in kk and isinstance(kk['grab'], list):
            q['grab'] = to_flu(kk['grab'], scale, off)[0].round(3).tolist()
        if 'grabradius' in kk:
            q['grab_radius_cm'] = round(float(kk['grabradius']) / WORLD_PER_HUD * abs(scale[1]) * 0 + float(kk['grabradius']) * (1.0 / 0.34), 2)  # map units -> cm (34 units = 1 m)
        if d.get('kind') == 'slide':
            ax = dir_flu(d['axis'], scale)
            q['axis'] = ax.round(3).tolist()
            q['travel_cm'] = round(float(d.get('distance', 0)) * WS * abs(scale[1]), 3)
            if kk.get('role') == 'feed':
                # the card's axis points OUT (the way the part slides out); Quest wants IN
                q['insert_dir'] = (-ax).round(3).tolist()
        elif d.get('kind') == 'hinge':
            q['hinge_axis'] = dir_flu(d['axis'], scale).round(3).tolist()
            if 'pivot' in d:
                q['hinge_point'] = to_flu(d['pivot'], scale, off)[0].round(3).tolist()
            q['open_deg'] = d.get('degrees')
        parts[name] = q
    g['parts'] = parts
    return g


# ---------------------------------------------------------------- sheet
def sheet(path, frame, scale, off, geo, out, title):
    it = dict(path=path, frame=frame, scale=list(scale), off=list(off), color=[150, 155, 170])
    marks = []
    col = {'palm': (255, 200, 60), 'triggerat': (255, 90, 90), 'supportat': (120, 230, 140), 'muzzle': (255, 255, 255), 'ejectport': (230, 120, 255)}
    for k, c in col.items():
        if k in geo:
            marks.append((*geo[k], k, c))
    for n, p in geo['parts'].items():
        if 'grab' in p:
            marks.append((*p['grab'], n[:8], (80, 200, 230)))
        if 'hinge_point' in p:
            marks.append((*p['hinge_point'], 'hinge', (255, 80, 80)))
    marks.append((*GRIP_REF.tolist(), 'GRIP_REF', (255, 255, 0)))
    from PIL import Image
    a = out + '.side.png'; b = out + '.bottom.png'
    gunview.view([it], a, 'side', px=5, marks=marks, title=title)
    gunview.view([it], b, 'bottom', px=5, marks=marks, title=title)
    A, B = Image.open(a), Image.open(b)
    O = Image.new('RGB', (max(A.width, B.width), A.height + B.height)); O.paste(A, (0, 0)); O.paste(B, (0, A.height)); O.save(out)
    os.remove(a); os.remove(b)


def main(root, out, only):
    os.makedirs(os.path.join(out, 'sheets'), exist_ok=True)
    scales = modeldef_scales(root)
    ws = load_cards(root)
    rep = {}
    for w in ws:
        cls = w['cls']
        if only and cls not in only:
            continue
        mp = model_path(root, w)
        if not mp or not os.path.exists(mp):
            rep[cls] = dict(error='no model file: %s' % mp); print('!!', cls, rep[cls]['error']); continue
        base = os.path.basename(mp).lower()
        ws_ = scales.get(base)
        if ws_ is None:
            rep[cls] = dict(error='no MODELDEF scale for %s' % base); print('!!', cls, rep[cls]['error']); continue
        hud = tuple(round(s / WORLD_PER_HUD, 4) for s in ws_)
        # Quest HUD convention (every kit gun): x mirrored. Keep REMA's magnitude, force the sign.
        scale = (-abs(hud[0]), abs(hud[1]), abs(hud[2]))
        mirrored_in_rema = hud[0] > 0
        off = offset_for(w['grip']['palm'], scale)
        geo = geometry(w, scale, off)
        fr = rest_frame(w, mp)
        rec = dict(cls=cls, variant_of=w.get('variant_of'), type=w['keys'].get('type'), model=os.path.relpath(mp, root).replace('\\', '/'),
                   skin=w['keys'].get('skin'), rest_frame=fr, rema_world_scale=ws_, hud_scale=scale, rema_x_positive=mirrored_in_rema,
                   offset=off, capacity=w['keys'].get('capacity'), magfamily=w['keys'].get('magfamily'),
                   sounds={k: v for k, v in w['keys'].items() if k.endswith('sound')},
                   magmodel=w['keys'].get('magmodel'), magcenter=w['keys'].get('magcenter'), **geo)
        rep[cls] = rec
        try:
            if not mp.lower().endswith('.iqm'):
                sheet(mp, fr, scale, off, geo, os.path.join(out, 'sheets', cls + '.png'), cls)
                rec['sheet'] = 'sheets/%s.png' % cls
            else:
                rec['sheet'] = 'IQM: sheet needs gunview.load_iqm (kit); skipped in stage 1'
        except Exception as e:
            rec['sheet_error'] = repr(e)
        feed = [n for n, p in geo['parts'].items() if p['role'] == 'feed']
        act = [n for n, p in geo['parts'].items() if p['role'] == 'action']
        print('%-20s scale %s off %s  palm->%s  feed %s  action %s%s' % (cls, scale, off, geo.get('palm'), feed, act,
              '  [REMA x+]' if mirrored_in_rema else ''))
    json.dump(rep, open(os.path.join(out, 'quest_geometry.json'), 'w'), indent=1)
    print('wrote', os.path.join(out, 'quest_geometry.json'))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
