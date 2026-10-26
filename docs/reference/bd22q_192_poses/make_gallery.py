#!/usr/bin/env python3
"""BD22 VR Weapons 1.92 hand-pose reference gallery, rendered on the QuestZDoom 17.3 Linux rig.

TEST/REFERENCE ONLY. Reads the rig and the packs, writes only under this directory.
  python3 make_gallery.py                 # every gun
  python3 make_gallery.py Rifle,SSG       # just these (index.json is rebuilt from all <Class>.json present)

One engine run per gun (flock -o -s /home/claude/rig.lock, one engine at a time). In that run:
give the gun, wait SELECT tics, pose the gun, press the off grip on the bore line so the engine
steadies it (WF_TWOHANDSTABILIZED: 1.92 then shows the support hand), then for each view hold the
camera (qz_hmd) with the models on, then with r_drawplayersprites 0. The left eye is dumped every
EVERY frames; the dump sequence is split where consecutive frames change, the last frame of each
on/off segment is kept, and the on-minus-off difference gives the box of gun + hands to crop.
"""
import os, re, sys, json, math, glob, shutil, subprocess, zipfile
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
RIGDIR = os.environ.get('B22_RIG', os.path.join(DEPOT, 'tools/rig/build/rig'))
IWAD = os.environ.get('B22_IWAD', '/home/claude/gamedata/doom2.wad')
BD22 = os.environ.get('B22_BD22', '/home/claude/gamedata/brutal22test6.pk3')
VOX = os.environ.get('B22_VOX', '/home/claude/gamedata/BD_VoxelPack.pk3')
PK3 = os.environ.get('B22_PK3', os.path.join(DEPOT, 'tools/rig/build/BD22Q_192.pk3'))
INI = HERE + '/rig_qzdoom.ini'     # copy of tools/rig/engine/config/qzdoom.ini; copied fresh per run so the shared rig ini is never written
PROBE = HERE + '/probe192.pk3'      # logs held weapon, ready flag, two-hand flag, hand layers (probe192/)
if not os.path.exists(PROBE):	# built from probe192/ on first run (the pk3 is not committed)
	with zipfile.ZipFile(PROBE, 'w', zipfile.ZIP_DEFLATED) as _z:
		for _r, _, _fs in os.walk(HERE + '/probe192'):
			for _f in _fs: _z.write(os.path.join(_r, _f), os.path.relpath(os.path.join(_r, _f), HERE + '/probe192'))
WORK = HERE + '/work'
RES = int(os.environ.get('QZ_RES', '960'))
EVERY = 2
SELECT = 200          # tics after 'use' before posing (README: ~150+)
HOLD_ON, HOLD_OFF = 45, 30
OUT_W = 720
JPG_Q = 88

# BD22 slot order (brutal22test6 KEYCONF setslot, rifle class), restricted to classes 1.92 gives hands to:
# every class in 1.92's zscript/rsq/handtable.zs Index(), plus BD22's fists (Melee_Attacks) and the
# hand grenade, which 1.92 draws with Ermac's own fist / grenade hand (hands.zs OwnHand).
SLOTS = [('BrutalAxe', 1), ('Chain_saw', 1), ('Melee_Attacks', 1),
         ('BrutalPistol', 2), ('BrutalSMG', 2), ('MP40', 2), ('Revolver', 2),
         ('Shot_Gun', 3), ('AssaultShotgun', 3), ('SSG', 3),
         ('Sniper', 4), ('Rifle', 4), ('Minigun', 4), ('MG42', 4),
         ('IncendiaryLauncher', 5), ('GrenadeLauncher', 5), ('Rocket_Launcher', 5), ('Devastator', 5),
         ('Plasma_Gun', 6), ('RailGun', 6),
         ('NukeLauncher', 7), ('BFG10k', 7), ('BIG_FUCKING_GUN', 7),
         ('HellishMissileLauncher', 8), ('Unmaker', 8),
         ('Flamethrower2', 9), ('HandGrenades', 0)]

# ---------------------------------------------------------------- parsed from the packs
def read_zip(path, name):
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.lower() == name.lower():
                return z.read(n).decode('latin-1')
    return None

def handtable():
    t = read_zip(PK3, 'zscript/rsq/handtable.zs')
    idx = {m.group(1).lower(): int(m.group(2)) for m in re.finditer(r"if \(w is '(\w+)'\)\s*return (\d+);", t)}
    funcs = {}
    for m in re.finditer(r'static (String|Vector3) (\w+)\(int i\)\s*\{(.*?)\n\t\}', t, re.S):
        kind, fn, body = m.groups()
        arrs = re.findall(r'static const (?:String|double) (\w)\[\] = \{(.*?)\};', body)
        if kind == 'String':
            funcs[fn] = [s.strip().strip('"') for s in arrs[0][1].split(',')]
        else:
            cols = [[float(v) for v in a[1].split(',')] for a in arrs]
            funcs[fn] = list(zip(*cols))
    return idx, funcs, t

def row(i, funcs):
    if i <= 0:
        return None
    return {fn: (list(v[i]) if isinstance(v[i], tuple) else v[i]) for fn, v in funcs.items()}

def labels():
    lang = {}
    for l in read_zip(BD22, 'language.enu').splitlines():
        m = re.match(r'\s*(\w+)\s*=\s*"(.*?)"', l)
        if m:
            lang.setdefault(m.group(1).upper(), m.group(2))
    tags = {}
    with zipfile.ZipFile(BD22) as z:
        for n in z.namelist():
            if n.lower().startswith('actors/') and n.lower().endswith(('.dec', '.txt')):
                t = z.read(n).decode('latin-1')
                for m in re.finditer(r'(?im)^\s*actor\s+(\w+)[^\n]*\n(.*?)(?=^\s*actor\s|\Z)', t, re.S):
                    tm = re.search(r'(?im)^\s*tag\s+"\$?([^"]*)"', m.group(2))
                    if tm:
                        tags.setdefault(m.group(1).lower(), (tm.group(1), n))
    out = {}
    for c, _ in SLOTS:
        tg = tags.get(c.lower())
        out[c] = (lang.get(tg[0].upper(), tg[0]) if tg else c, tg[0] if tg else None)
    return out

def modeldef_blocks(cls):
    """every 'Model <cls>' block in the 1.92 pk3's MODELDEF lumps: [file, first line, text]"""
    res = []
    with zipfile.ZipFile(PK3) as z:
        for n in sorted(z.namelist()):
            if not os.path.basename(n).upper().startswith('MODELDEF'):
                continue
            lines = z.read(n).decode('latin-1').splitlines()
            k = 0
            while k < len(lines):
                if re.match(r'(?i)^\s*model\s+%s\s*(//.*)?$' % re.escape(cls), lines[k]):
                    j, depth, started = k, 0, False
                    while j < len(lines):
                        depth += lines[j].count('{') - lines[j].count('}')
                        started = started or '{' in lines[j]
                        if started and depth <= 0:
                            break
                        j += 1
                    res.append([n, k + 1, '\n'.join(lines[k:j + 1])])
                    k = j
                k += 1
    return res

def hand_frame_lines(r):
    """the MODELDEF.rsq FrameIndex lines (RSQ_GunSide) this gun's hand frames use"""
    t = read_zip(PK3, 'MODELDEF.rsq').splitlines()
    want = []
    if r:
        for s, f in (('RQGS', r['GunOne']), ('RQGS', r['GunTwo']), ('RQGT', r['Trigger']), ('RQGU', r['Trigger']), ('RQSP', r['Support'])):
            if f:
                want.append((s, f))
    out = []
    for n, l in enumerate(t):
        m = re.match(r'\s*FrameIndex (RQ\w\w) (\w) ', l)
        if m and (m.group(1), m.group(2)) in want:
            out.append('MODELDEF.rsq:%d: %s' % (n + 1, l.strip()))
    return out

# ---------------------------------------------------------------- poses (stage metres, degrees)
def look(cam, tgt):
    """qz_hmd string: camera at cam looking at tgt (yaw 0 looks -z, yaw +90 looks -x, pitch < 0 down)"""
    dx, dy, dz = (tgt[k] - cam[k] for k in range(3))
    yaw = math.degrees(math.atan2(-dx, -dz))
    pitch = math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    return '%.4f %.4f %.4f %.2f %.2f 0' % (cam[0], cam[1], cam[2], pitch, yaw)

def hands_on_line(grip, yaw, d=0.12):
    """main controller at grip, level, aimed at yaw; off controller d m ahead on that line, so the
    engine's two-hand steadying (VrInputDefault.cpp: aim = main -> off) keeps the gun level at yaw"""
    x = -math.sin(math.radians(yaw)) * d
    z = -math.cos(math.radians(yaw)) * d
    r = '%.4f %.4f %.4f 30 %.1f 0' % (grip[0], grip[1], grip[2], yaw)   # pitch 30 = level after vr_weaponRotate -30
    l = '%.4f %.4f %.4f 30 %.1f 0' % (grip[0] + x, grip[1], grip[2] + z, yaw)
    return r, l

def gun_frame_point(grip, p):
    """a point in the gun hand's frame (metres forward, left, up) for a gun aimed -z: stage xyz"""
    return (grip[0] - p[1], grip[1] + p[2], grip[2] - p[0])

FAR = {}
NOTES = {
    'Sniper': '1.92 has a hand row for it, but 1.92 switches the sniper off for good (zscript/nosniper/nosniper.zs: its model is gone; '
              'a given Sniper is swapped for the Rifle the next tic, even with rsq_extra_weapons 1). Not renderable.',
    'HandGrenades': 'not in handtable.zs: 1.92 draws Ermac\'s grenade hand (OwnHand "Nade") on the main hand, the off hand open. '
                    'The VR grenade is never WF_WEAPONREADY while held (probe state busy); no throw was made.',
    'Melee_Attacks': 'not in handtable.zs: 1.92 draws Ermac\'s fist in both hands (OwnHand "Fist").',
}
SKIP = {'Sniper'}
# what the rendered set shows (looked at, 2026-10-26); kept here so a re-run keeps them
SEEN = {
    'BrutalAxe': 'one hand on the haft; no support hand in 1.92 (Support "")',
    'Chain_saw': 'support hand on the top handle; the support close-up is crowded by the handle (see side / front34)',
    'BrutalPistol': 'two-hand cup grip (support "A", shown by closeness, no grip press)',
    'Revolver': 'two-hand cup grip (support "A", shown by closeness, no grip press)',
    'Rifle': 'support hand under the M203 tube (1.30 pose C)',
    'Minigun': 'support hand on the carry handlebar (Support E, rotated 95 deg); the grip close-up is crowded by the body',
    'IncendiaryLauncher': 'support hand open, palm under the tube, not closed round it',
    'Rocket_Launcher': 'support hand open, fingers spread under the tube',
    'Devastator': 'support hand open beside the foregrip, not closed on it',
    'NukeLauncher': 'support hand open under the body',
    'BFG10k': 'support hand open under the body; grip close-up dark (black gun)',
    'BIG_FUCKING_GUN': 'support hand open under the body',
    'HellishMissileLauncher': 'support hand open under the body; the grip hand is mostly hidden by the gun in every view',
    'Unmaker': 'support hand open, fingers spread under the body',
}
GRIP_LOW = {'HellishMissileLauncher', 'Rocket_Launcher', 'NukeLauncher', 'BFG10k', 'BIG_FUCKING_GUN', 'IncendiaryLauncher'}
G = (0.0, 1.40, -0.55)     # world grip for views 3-7: level, aimed -z (along the start corridor)

def views(cls, r, kind, far=1.0):
    """kind: 'two' (steadied: support hand), 'one' (gun hand only), 'fist', 'nade'"""
    v = []
    two = kind == 'two'
    sp = r['SupportPoint'] if r else None
    has_sup = two and sp and sp[2] > -50
    # size of the gun from the support point (fallback 25 cm), to place the cameras
    reach = max(0.25, (sp[0] if has_sup else 0.20) + 0.10)
    C = gun_frame_point(G, (reach * 0.55, 0, 0.0))            # rough centre of gun + hands
    dist = (0.30 + reach * 0.95) * far
    FAR_L = '0.0000 0.1000 2.5000 30 0 0'                    # off hand behind the player, out of every view
    def wp(yaw=0.0, grip=G):
        if kind == 'two':
            return hands_on_line(grip, yaw)
        rr = '%.4f %.4f %.4f 30 %.1f 0' % (grip[0], grip[1], grip[2], yaw)
        if kind in ('fist', 'nade'):     # Ermac's fist / grenade hand: the off hand shown beside it
            return rr, '%.4f %.4f %.4f 30 %.1f 0' % (grip[0] - 0.22, grip[1], grip[2], yaw)
        return rr, FAR_L
    # 1 side: README "side-on in front of the eye": gun hand at (0.0 1.68 -0.40), yaw -70, default head;
    #   level bore (steadied) instead of README's 20-degree controller pitch
    r1, l1 = wp(-70.0, (0.0, 1.68, -0.40))
    v.append(dict(view='side', hmd='0 1.6 %.2f 0 0 0' % (0.25 * far - 0.25), rhand=r1, lhand=l1))   # head moved back on a re-shoot when the gun ran off the frame
    # 2 eye: the player's own view (gate --shots): head 1.6 m, pitched 40 down; controllers at rest
    r2, l2 = wp(0.0, (0.25, 1.30, -0.30))
    v.append(dict(view='eye', hmd='0 1.6 0 -40 0 0', rhand=r2, lhand=l2))
    r3, l3 = wp(0.0)
    # 3 top-down, 4 bottom-up, 5 front three-quarter (muzzle end, right, above)
    v.append(dict(view='top', hmd=look((C[0] + 0.001, C[1] + dist, C[2]), C), rhand=r3, lhand=l3))
    v.append(dict(view='bottom', hmd=look((C[0] + 0.001, C[1] - dist, C[2]), C), rhand=r3, lhand=l3))
    a = math.radians(40)
    v.append(dict(view='front34', hmd=look((C[0] + dist * math.sin(a) * 0.9, C[1] + dist * 0.35, C[2] - dist * math.cos(a) * 0.9), C), rhand=r3, lhand=l3))
    # 6 grip hand close-up: from the right, a little above and behind
    gh = G
    if cls in GRIP_LOW:    # bulky body over the grip: look from the right and below
        v.append(dict(view='grip', hmd=look((gh[0] + 0.26, gh[1] - 0.14, gh[2] + 0.06), (gh[0], gh[1] - 0.03, gh[2] - 0.03)), rhand=r3, lhand=l3, closeup=0.62))
    else:
        v.append(dict(view='grip', hmd=look((gh[0] + 0.26, gh[1] + 0.06, gh[2] + 0.08), (gh[0], gh[1] - 0.02, gh[2] - 0.03)), rhand=r3, lhand=l3, closeup=0.62))
    # 7 support hand close-up: from the right and below, at 1.92's SupportPoint
    if has_sup:
        S = gun_frame_point(G, sp)
        side = -1.0 if sp[1] > 0.05 else 1.0     # support point well left of the bore (minigun handlebar): look from the left
        v.append(dict(view='support', hmd=look((S[0] + 0.22 * side, S[1] - 0.14, S[2] + 0.04), S), rhand=r3, lhand=l3, closeup=0.62))
    return v

# ---------------------------------------------------------------- one engine run
def console(cls, vs, kind):
    s = ('wait 100; god; notarget; screenblocks 12; crosshair 0; con_notifytime 0; give Infrared; rsq_extra_weapons 1; '
         'give ammo; give %s; wait 2; use %s; ' % (cls, cls))
    s += 'r_drawplayersprites 0; qz_hmd "%s"; qz_rhand "%s"; qz_lhand "%s"; wait %d; ' % (MARKER, vs[0]['rhand'], vs[0]['lhand'], SELECT)
    if kind == 'two':
        s += 'qz_lgrip 1; wait 20; '
    for k, v in enumerate(vs):
        s += 'qz_rhand "%s"; qz_lhand "%s"; qz_hmd "%s"; r_drawplayersprites 1; echo G192VIEW %d on; wait %d; ' % (
            v['rhand'], v['lhand'], v['hmd'], k, HOLD_ON)
        s += 'r_drawplayersprites 0; echo G192VIEW %d off; wait %d; echo G192VIEW %d end; ' % (k, HOLD_OFF, k)
    s += 'quit'
    return s

def engine(tag, script, secs):
    d = os.path.join(WORK, tag)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    files = [BD22, VOX, PK3, PROBE]
    shutil.copy(INI, d + '/qzdoom.ini')
    cmd = ['flock', '-o', '-s', os.environ.get('RIG_LOCK', '/tmp/rig.lock'), 'timeout', str(secs), RIGDIR + '/qz', '-config', d + '/qzdoom.ini', '-iwad', IWAD,
           '-file'] + files + ['-nosound', '-warp', '1', '-skill', '3', '+logfile', d + '/log.txt', '+' + script]
    env = dict(os.environ, QZ_HMD=MARKER, QZ_RES=str(RES), QZ_DUMP_EVERY=str(EVERY), QZ_DUMP_DIR=d, EGL_PLATFORM='surfaceless',
               LIBGL_ALWAYS_SOFTWARE='1')
    cmd = ['stdbuf', '-oL', '-eL'] + cmd
    import time
    with open(d + '/out.txt', 'w') as fo, open(d + '/stamps.txt', 'w') as fs:
        pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=RIGDIR, env=env, text=True, errors='replace')
        for line in pr.stdout:
            fo.write(line)
            if line.startswith('G192VIEW'):
                fs.write('%.6f %s' % (time.time(), line))
        rc = pr.wait()
    return d, rc, open(d + '/out.txt', errors='replace').read()

def frac_changed(a, b, thr=30):
    df = ImageChops.difference(a, b).convert('L').point(lambda p: 255 if p > thr else 0)
    return df.histogram()[255] / float(a.size[0] * a.size[1])

MARKER = '0 1.6 0 89.9 0 0'     # camera straight up at the start room's ceiling while the gun selects

def segments(d, nviews):
    """Each view: models on (echo 'on'), then models off (echo 'off'), then echo 'end'. The echo lines
    are timestamped as they arrive (stamps.txt); a frame file's mtime says when it was written.
    'on' frame = the last frame written before the 'off' echo, 'off' frame = the last before 'end'."""
    fs = sorted(glob.glob(d + '/f*.ppm'))
    mt = [os.stat(f).st_mtime for f in fs]
    st = {}
    for l in open(d + '/stamps.txt'):
        t, _, k, what = l.split()[:4]
        st[(int(k), what)] = float(t)
    picks, blocks = [], []
    def last_before(t):
        c = [i for i in range(len(fs)) if mt[i] < t]
        return c[-1] if c else None
    for k in range(nviews):
        if (k, 'off') not in st or (k, 'end') not in st:
            picks.append((None, None)); continue
        on, off = last_before(st[(k, 'off')]), last_before(st[(k, 'end')])
        if on is not None and st.get((k, 'on')) and mt[on] < st[(k, 'on')]:
            on = None      # no frame was written while the models were on
        picks.append((on, off)); blocks.append((st.get((k, 'on')), st[(k, 'end')]))
    ims = {}
    for on, off in picks:
        for i in (on, off):
            if i is not None and i not in ims:
                ims[i] = Image.open(fs[i]).convert('RGB')
    return fs, ims, blocks, picks

def crop(on, off, aspect=4 / 3, centre=None):
    df = ImageChops.difference(on, off).convert('L').point(lambda p: 255 if p > 24 else 0)
    bb = df.getbbox()
    W, H = on.size
    if not bb:
        return None, None
    if centre:     # close-up: the camera looks straight at the hand, so it is at the frame centre
        w = W * centre; h = w / aspect
        bb = (W / 2 - w / 2, H / 2 - h / 2, W / 2 + w / 2, H / 2 + h / 2)
        box = tuple(int(round(v)) for v in bb)
        if not df.crop(box).getbbox():
            return None, None
        im = on.crop(box)
        return im.resize((OUT_W, int(round(OUT_W / aspect))), Image.LANCZOS), list(box)
    x0, y0, x1, y1 = bb
    edge = x0 <= 1 or y0 <= 1 or x1 >= W - 1 or y1 >= H - 1
    w, h = x1 - x0, y1 - y0
    m = 0.10
    x0, x1, y0, y1 = x0 - w * m, x1 + w * m, y0 - h * m, y1 + h * m
    w, h = x1 - x0, y1 - y0
    if w / h < aspect:
        c = (x0 + x1) / 2; w = h * aspect; x0, x1 = c - w / 2, c + w / 2
    else:
        c = (y0 + y1) / 2; h = w / aspect; y0, y1 = c - h / 2, c + h / 2
    w, h = x1 - x0, y1 - y0
    w = max(w, 160); h = max(h, 120)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    # keep inside the frame
    if x0 < 0: x1 -= x0; x0 = 0
    if y0 < 0: y1 -= y0; y0 = 0
    if x1 > W: x0 -= x1 - W; x1 = W
    if y1 > H: y0 -= y1 - H; y1 = H
    box = tuple(int(round(v)) for v in (max(0, x0), max(0, y0), min(W, x1), min(H, y1)))
    im = on.crop(box)
    im = im.resize((OUT_W, int(round(OUT_W * im.size[1] / im.size[0]))), Image.LANCZOS)
    return im, list(box) + (['edge'] if edge else [])

def probe_lines(text):
    return [l for l in text.splitlines() if l.startswith('G192 ') or l.startswith('G192VIEW')]

def check(text, cls, kind):
    """held weapon / ready / steadied, read from the probe across every view"""
    ls = probe_lines(text)
    after = False
    bad = []
    for l in ls:
        if l.startswith('G192VIEW 0 on'):
            after = True
        if not after or not l.startswith('G192 '):
            continue
        m = re.match(r'G192 (\d+) ready (\S+) pending (\S+) state (\S+) two (\d) sup (\S+) gun (\S+)', l)
        if not m:
            continue
        held, st, two = m.group(2), m.group(4), m.group(5)
        if held.lower() != cls.lower():
            bad.append('held %s' % held)
        if st != 'READY':
            bad.append('state %s at tic %s' % (st, m.group(1)))
        if kind == 'two' and (two != '1' or m.group(6) in ('none', '0')):
            bad.append('not steadied/support hidden at tic %s' % m.group(1))
    return sorted(set(bad))

def kind_of(cls, r):
    if cls == 'Melee_Attacks':
        return 'fist'
    if cls == 'HandGrenades':
        return 'nade'
    if r and r['Support']:
        return 'two'
    return 'one'

WHOLE = ('side', 'top', 'bottom', 'front34')     # not 'eye': the arm always enters from the frame edge there

def shoot(cls, idx, funcs, lab, far=None):
    if far is None:
        far = FAR.get(cls, 1.0)
    info = shoot1(cls, idx, funcs, lab, far)
    if far < 1.2 and any(v.get('crop_box') and 'edge' in v['crop_box'] for v in info['views'] if v['view'] in WHOLE):
        return shoot(cls, idx, funcs, lab, far * 1.5)     # gun ran off the frame: same set, cameras 1.5x further
    return info

def shoot1(cls, idx, funcs, lab, far):
    i = idx.get(cls.lower(), 0)
    r = row(i, funcs)
    kind = kind_of(cls, r)
    vs = views(cls, r, kind, far)
    script = console(cls, vs, kind)
    secs = 60 + (SELECT + 40 + len(vs) * (HOLD_ON + HOLD_OFF)) // 12
    d, rc, text = engine(cls, script, max(secs, 150))
    fs, ims, segs, picks = segments(d, len(vs))
    errs = [l for l in text.splitlines() if re.search(r'Script error|VM abort|exception', l) and 'voxeldef' not in l]
    ver = 'QZDoom version 4.14.3' in text
    problems = check(text, cls, kind)
    wrong = any(p.startswith('held ') for p in problems)
    out = []
    if len(picks) < len(vs):
        problems.append('segmentation: %d view blocks for %d views' % (len(picks), len(vs)))
    for k, v in enumerate(vs):
        ent = dict(v)
        on, off = picks[k] if k < len(picks) else (None, None)
        ent['file'] = None
        if wrong:
            pass
        elif on is None or off is None:
            problems.append('%s: no models-on frame' % v['view'])
        else:
            im, box = crop(ims[on], ims[off], centre=v.get('closeup'))
            ent['frames'] = [os.path.basename(fs[on]), os.path.basename(fs[off])]
            ent['crop_box'] = box
            if im is not None:
                fn = '%s_%s.jpg' % (cls, v['view'])
                im.save(os.path.join(HERE, fn), quality=JPG_Q, optimize=True)
                ent['file'] = fn
            else:
                problems.append('%s: nothing differs between models on and off' % v['view'])
        out.append(ent)
    lab_s, tag = lab[cls]
    info = dict(
        **{'class': cls}, label=lab_s, bd22_tag=tag, handtable_index=i, kind=kind,
        support_shown=(kind == 'two' and bool(r and r['SupportPoint'][2] > -50)),
        handtable_row=r, handtable_source='%s:zscript/rsq/handtable.zs' % os.path.basename(PK3),
        modeldef_hand_frames=hand_frame_lines(r), modeldef_hand_common='MODELDEF.rsq RSQ_GunSide blocks: Model 0 "hand.md3" (gun hand) / "hand2.md3" (support), Skin "hand.png", Scale -1.0 1.0 1.0, Offset 0.0 -24.0 -10.0',
        modeldef_gun_blocks=modeldef_blocks(cls),
        rig=dict(engine=RIGDIR + '/qz', engine_ok=ver, rc=rc, res=RES, dump_every=EVERY, select_tics=SELECT,
                 load_order=[IWAD, BD22, VOX, PK3, PROBE], console=script,
                 fixed_cvars='rig config/qzdoom.ini: vr_two_handed_weapons=true vr_weaponRotate=-30 playerclass=$TAGBD_CLASS_RIFLE; give Infrared (light amp) for brightness',
                 script_errors=errs[:5], probe=probe_lines(text)[-12:]),
        camera_scale=far, notes='; '.join(x for x in (NOTES.get(cls, ''), SEEN.get(cls, '')) if x), views=out, problems=problems)
    json.dump(info, open(os.path.join(HERE, cls + '.json'), 'w'), indent=1)
    return info

def build_index():
    idx = []
    for cls, slot in SLOTS:
        p = os.path.join(HERE, cls + '.json')
        if not os.path.exists(p):
            continue
        j = json.load(open(p))
        e = {'class': cls, 'label': j['label'], 'slot': slot}
        for v in j['views']:
            e[v['view']] = v.get('file')
        e['support_shown'] = j['support_shown']
        e['notes'] = '; '.join(x for x in [j.get('notes', ''), '; '.join(p for p in j['problems'] if not p.startswith('state busy'))] if x)
        e['json'] = cls + '.json'
        idx.append(e)
    json.dump(idx, open(os.path.join(HERE, 'index.json'), 'w'), indent=1)
    return idx

if __name__ == '__main__':
    if sys.argv[1:] == ['--index']:
        build_index(); sys.exit(0)
    idx, funcs, _ = handtable()
    lab = labels()
    only = sys.argv[1].split(',') if len(sys.argv) > 1 else [c for c, _ in SLOTS]
    for c in only:
        if c in SKIP:
            lab_s, tag = lab[c]
            json.dump({'class': c, 'label': lab_s, 'bd22_tag': tag, 'handtable_index': idx.get(c.lower(), 0),
                       'handtable_row': row(idx.get(c.lower(), 0), funcs), 'modeldef_gun_blocks': modeldef_blocks(c),
                       'support_shown': False, 'notes': NOTES[c], 'views': [], 'problems': ['not rendered']},
                      open(os.path.join(HERE, c + '.json'), 'w'), indent=1)
            print('%-24s skipped: %s' % (c, NOTES[c][:60]), flush=True)
            continue
        info = shoot(c, idx, funcs, lab)
        print('%-24s %-6s views %d problems %s' % (c, info['kind'], sum(1 for v in info['views'] if v.get('file')), info['problems']), flush=True)
    build_index()
