"""bd22_mg.py -- the BD21 Machinegun (M249, over-under launcher) into RS_Brutal22WeaponsQ, in the pack's
own architecture. Runs AFTER bd22_plus.py apply (works in build/bd22/src).

Sources, and nothing else:
  parent   BD21's Machinegun.txt (owner, 2026-10-24): behaviour, numbers, sounds (renamed where BD22
           renamed them -- a table below, each checked in brutal22test6's SNDINFO).
  mesh     BD21's Machinegun.md3 / .png (br_vr PK3_pbr), its own surfaces: alt-pipe = the launcher
           tube, alt-trig-reload = latch, alt-trig = launcher trigger, alt-frame = launcher frame.
           Frame 4 (MGN1 A, Ready) IS REMA's machinegun_wm.md3 (rigid residual 0.0000 cm, t = 52.88 F).
  card     REMA WMCARD.bd22 BD_Machinegun: palm, supportat, latch grab, launcher bore and load point,
           carried by that translation; tube travel measured on the BD21 frames (9.69) vs card 9.50.
  module   the pack's own M203 (zscript/rsr/rsr_m203.zs, built from this very launcher): made per-gun
           (gun 1 = Rifle, gun 2 = Machinegun) by exact-match edits; nothing the rifle does changes.
Launcher ammo follows the pack's "Rifle Underbarrel Ammo" option (rsm_ammo), as asked.
Menu: "Machinegun replaces MG42" (rsq_mg_replaces_mg42, server, off) -- on, every MG42 spawn/drop is
the Machinegun (CheckReplacement); off, both exist (slot 4, cheats / spawners / this option).

    python3 bd22_mg.py
"""
import os, re, sys, json, shutil
import numpy as np
sys.path.insert(0, '/home/claude/c2q')
sys.path.insert(0, '/mnt/user-data/uploads/Quest_Weapons_Kit/kit/kit/team/reload_merged/tools')
import genpack, rgeo, carve_by_ref, wmcard, handfit_cards

OUT = '/home/claude/c2q/build/bd22/'
S = OUT + 'src/'
BR = '/mnt/user-data/uploads/VR_WeaponSetRebuild/br_vr/PK3_pbr/'
BD21 = '/mnt/user-data/attachments/c9d0fd42-99b1-5808-a0b8-8328fb4227ef/dc8c5c60-Machinegun.txt'
REMA = '/home/claude/presidentkoopa/rs_vr_weapons/bd22/'
SCALE, OFF, ZOFF = (-1.0, 1.0, 1.0), (0.0, 0.0), -5.0
READY_FRAME = 4            # MGN1 A

# BD21 -> BD22 sound names (each right-hand side checked in brutal22test6 SNDINFO.*)
SND = {'"GRLLO1"': '"Rifle/Grenade1"', '"GRLLO2"': '"Rifle/Grenade2"', '"insertshell"': '"GrenadeLauncher/Load"',
       '"weapons/empty"': '"Weapon/Empty"', '"weapons/firegrenade"': '"GrenadeLauncher/Fire"'}

log = {}


def once(lines, pred, what):
    hits = [i for i, l in enumerate(lines) if pred(l)]
    if len(hits) != 1:
        raise SystemExit('%s: found %d times' % (what, len(hits)))
    return hits[0]


def edit(path, pairs):
    """exact-match edits; each old text must occur once"""
    t = open(path).read()
    for old, new in pairs:
        if t.count(old) != 1:
            raise SystemExit('%s: %r found %d times' % (path, old[:60], t.count(old)))
        t = t.replace(old, new)
    open(path, 'w').write(t)


# ------------------------------------------------------------------ geometry
def geometry():
    n, ts = genpack.md3_surfaces(BR + 'Models/Weapons/Hud/Machinegun/Machinegun.md3')
    names = [s['name'] for s in ts]
    X = lambda v: rgeo.to_flu(np.asarray(v, float).reshape(-1, 3), SCALE, (OFF[0], OFF[1], 0.0))
    _, rs = genpack.md3_surfaces(REMA + 'models/bd22/machinegun_wm.md3')
    A = np.vstack([s['xyz'][0] for s in rs]); B = np.vstack([s['xyz'][READY_FRAME] for s in ts])
    from scipy.spatial import cKDTree
    tree = cKDTree(B); Rm = np.eye(3); t = B.mean(0) - A.mean(0)
    for _ in range(60):
        d, idx = tree.query(A @ Rm.T + t); Rm, t = carve_by_ref.kabsch(A, B[idx])
    d, _ = tree.query(A @ Rm.T + t)
    card = [w for w in wmcard.load([REMA + 'WMCARD.bd22']) if w['cls'] == 'BD_Machinegun'][0]
    C = lambda v: X(Rm @ np.asarray(v, float) + t)[0]
    pipe = X(ts[names.index('alt-pipe')]['xyz'][READY_FRAME]); frame = X(ts[names.index('alt-frame')]['xyz'][READY_FRAME])
    body = X(ts[names.index('M249_lowpoly')]['xyz'][READY_FRAME])
    bore = C(card['keys']['_barrel:launcher']['muzzle'])
    # travel: the tube's centroid along F relative to the body, over the BD21 frames
    c0 = pipe.mean(0) - body.mean(0); travel = 0.0
    for f in range(n):
        c = X(ts[names.index('alt-pipe')]['xyz'][f]).mean(0) - X(ts[names.index('M249_lowpoly')]['xyz'][f]).mean(0)
        travel = max(travel, float((c - c0)[0]))
    g = dict(rigid_mean=float(d.mean()), rigid_max=float(d.max()), t=t.round(3).tolist(),
             axis_l=round(float(bore[1]), 3), axis_u=round(float(bore[2]), 3),
             frame_front=round(float(frame[:, 0].max()), 3), tube_rear=round(float(pipe[:, 0].min()), 3),
             tube_front=round(float(pipe[:, 0].max()), 3), travel=round(travel, 3), travel_card=float(card['parts']['launchertube']['dof']['distance']),
             palm=C(card['grip']['palm']).round(3).tolist(), supportat=C(card['grip']['supportat']).round(3).tolist(),
             latch=C(card['parts']['launcherlatch']['keys']['grab']).round(3).tolist(),
             loadat=C(card['keys']['_load:grenade']['at']).round(3).tolist(), surfaces=names,
             fwd_hook=rgeo.shift_hook(SCALE, np.array([1.0, 0, 0])).round(4).tolist())
    log['geometry'] = g
    return g, ts, names


# ------------------------------------------------------------------ assets + MODELDEF
def assets(g, names):
    d = S + 'models/bd/Machinegun/'; os.makedirs(d, exist_ok=True)
    shutil.copy(BR + 'Models/Weapons/Hud/Machinegun/Machinegun.md3', d + 'Machinegun.md3')
    shutil.copy(BR + 'Models/Weapons/Hud/Machinegun/Machinegun.png', d + 'Machinegun.png')
    shutil.copy(S + 'models/bd/Rifle/rsr_clear.png', d + 'rsr_clear.png')
    # the gun's own block from br_vr (BD21 keys), pack style; then MG42's shared blocks (grenade, boot,
    # fists) copied for the new class -- those keys are the same sprites on every BD gun
    src = open(BR + 'Modeldef.Machinegun.def').read().replace('\r\n', '\n')
    blocks = re.findall(r'Model Machinegun\s*\n\{.*?\n\}', src, re.S)
    gun = blocks[0].replace('Path "Models/Weapons/Hud/Machinegun"', 'Path "models/bd/Machinegun"')
    frames = re.findall(r'FrameIndex\s+(\w+)\s+(\w)\s+0\s+(\d+)', gun)
    md = open(S + 'MODELDEF.bd.txt').read()
    mg42 = re.findall(r'(?ms)^Model MG42\s*\n\{.*?\n\}', md)
    shared = [b.replace('Model MG42', 'Model Machinegun', 1) for b in mg42 if 'HitlersBuzzsaw' not in b]
    # the world pickup: no MGN1 Z sprite exists in BD22 -- the gun mesh on the floor (RSR_DroppedMag scale)
    sc = 34.0 * 0.01 * 1.02
    c = np.vstack([s['xyz'][READY_FRAME] for s in []]) if False else None
    pick = ('Model Machinegun\n{\n\tPath "models/bd/Machinegun"\n\tModel 0 "Machinegun.md3"\n\tSkin 0 "Machinegun.png"\n'
            '\tScale %.4f %.4f %.4f\n\tOffset 0.0 0.0 0.0\n\tZOffset 2.0\n\tAngleOffset 90\n\tFrameIndex MGN1 Z 0 %d\n}\n' % (sc, sc, sc, READY_FRAME))
    with open(S + 'MODELDEF.bd.txt', 'a') as f:
        f.write('\n// ---- 1.97: the BD21 Machinegun (c2q/bd22_mg.py). Keys are BD21\'s own (br_vr Modeldef.Machinegun.def).\n')
        f.write(gun + '\n\n' + '\n\n'.join(shared) + '\n\n// the floor pickup (BD22 ships no MGN1 Z sprite)\n' + pick)
    log['modeldef'] = dict(gun_frames=len(frames), shared_blocks=len(shared))
    return frames


# ------------------------------------------------------------------ DECORATE
def decorate():
    t = open(BD21, 'rb').read().decode('latin-1').replace('\r\n', '\n')
    for a, b in SND.items():
        t = t.replace(a, b)
    lines = t.split('\n')
    # slot like MG42 (BD22 KEYCONF setslot 4 ... MG42): KEYCONF.rsq addslot below
    # the launcher by hand (RSM): mirror Rifle.dec's 1.30/1.33 states
    alt = once(lines, lambda l: l.strip() == 'AltFire:', 'AltFire label')
    k = alt + next(i for i, l in enumerate(lines[alt:alt + 8]) if l.strip() == 'MGN1 A 0 A_JumpIfInventory("FiredMGGrenade", 1, "ReloadGrenade")')
    lines[k:k + 1] = ['\t\t\tMGN1 A 0 A_JumpIfInventory("RSM_VR", 1, "RSM_AltGrenade")\t// 1.97 rsm: loaded by hand in VR (zscript/rsr/rsr_m203.zs)',
                      lines[k]]
    # the shot: with RSM the round is the loaded one
    k = once(lines, lambda l: 'A_FireCustomMissile("ShortGrenade", 0, 1, 0, 0)' in l, 'launcher shot')
    lines.insert(k + 1, '\t\t\tMGN1 A 0 A_TakeInventory("RFGLoaded", 1)\t// 1.97 rsm')
    # BD21's own launcher reload: out of VR only
    k = once(lines, lambda l: l.strip() == 'ReloadGrenade:', 'ReloadGrenade label')
    lines[k + 1:k + 1] = ['\t\t\tMGN1 A 0 A_JumpIfInventory("RSM_VR", 1, "Ready")\t// 1.97 rsm: by hand in VR']
    # the reload key: BD21 reloads the launcher only; in VR, nothing (the belt feeds from the reserve)
    rl = once(lines, lambda l: l.strip() == 'Reload:', 'Reload label')
    k = rl + next(i for i, l in enumerate(lines[rl:rl + 6]) if 'A_JumpIfInventory("FiredMGGrenade", 1, "ReloadGrenade")' in l)
    lines.insert(k, '\t\t\tMGN1 A 0 A_JumpIfInventory("RSM_VR", 1, "Ready")\t// 1.97 rsm')
    # the RSM states (from Rifle.dec 1.30/1.33, this gun's sprite)
    k = once(lines, lambda l: l.strip() == 'ReloadGrenade:', 'ReloadGrenade label 2')
    rsm = ['\t\t// 1.97 rsm (zscript/rsr/rsr_m203.zs): in VR with real reload the launcher is loaded by hand',
           '\t\t// (the tube slid forward, a round put in, the tube pulled back); empty, its trigger only clicks.',
           '\t\tRSM_AltGrenade:',
           '\t\t\tMGN1 A 0 A_JumpIfInventory("RFGLoaded", 1, "RSM_Fire")',
           '\t\tRSM_Dry:',
           '\t\t\tMGN1 A 0 A_StartSound("Weapon/Empty", CHAN_AUTO)',
           '\t\tRSM_DryHold:\t// one click a press',
           '\t\t\tMGN1 A 1',
           '\t\t\tMGN1 A 0 A_JumpIf(CountInv("FiredSecondary") > 0, "RSM_DryHold")',
           '\t\t\tGoto Ready3',
           '\t\tRSM_Fire:\t// BD21\'s own shot (AltFire after its checks)',
           '\t\t\tMGN1 A 0 A_PlaySound("GrenadeLauncher/Fire")',
           '\t\t\tTNT1 A 0 ACS_NamedExecuteAlways("MGGrenadeCheck")',
           '\t\t\tMGN1 A 0 A_FireCustomMissile("RedFlareSpawn",-5,0,0,0)',
           '\t\t\tTNT1 AAAAAA 0 BRIGHT A_FireCustomMissile("ShotgunParticles", random(-16,16), 0, -1, random(-9,9))',
           '\t\t\tMGN2 A 0 BRIGHT A_FireCustomMissile("ShortGrenade", 0, 1, 0, 0)',
           '\t\t\tMGN1 A 0 A_TakeInventory("RFGLoaded", 1)',
           '\t\t\tMGN1 A 0 A_SetPitch(-5.0 + pitch)',
           '\t\t\tMGN1 A 0 A_Recoil(8)',
           '\t\t\tMGN2 BC 1 BRIGHT A_SetPitch(1.0 + pitch)',
           '\t\t\tMGN2 DEF 1 A_SetPitch(1.0 + pitch)',
           '\t\t\tMGN1 A 0 A_GiveInventory("FiredMGGrenade", 1)',
           '\t\t\tMGN1 A 10',
           '\t\t\tMGN1 A 0 A_Refire',
           '\t\t\tgoto Ready']
    lines[k:k] = rsm
    hdr = ['// 1.97: Brutal Doom v21\'s Machinegun (the owner\'s Machinegun.txt), in BD22: sounds BD22 renamed are renamed',
           '// here (GRLLO1/2 -> Rifle/Grenade1/2, insertshell -> GrenadeLauncher/Load, weapons/empty -> Weapon/Empty);',
           '// lines marked "1.97 rsm" are the only other changes (the launcher loaded by hand in VR). c2q/bd22_mg.py.']
    text = '\n'.join(hdr + lines)
    os.makedirs(S + 'actors/Weapons', exist_ok=True)
    open(S + 'actors/Weapons/Machinegun.dec', 'wb').write(text.encode('latin-1'))
    # the pack loads its weapon files how? -- 1.96b's patched .dec files override BD22's by lump path; a NEW
    # file needs an include: DECORATE.rsqmg
    open(S + 'DECORATE.rsqmg', 'w').write('// 1.97: the BD21 Machinegun (c2q/bd22_mg.py)\n#include "actors/Weapons/Machinegun.dec"\n')
    kc = S + 'KEYCONF.rsq'
    with open(kc, 'a') as f:
        f.write('\n// 1.97: the Machinegun on slot 4 with the MG42 (BD22 KEYCONF setslot 4 ... MG42)\naddslot 4 Machinegun\n')
    log['decorate'] = 'actors/Weapons/Machinegun.dec, DECORATE.rsqmg, KEYCONF.rsq addslot 4'


# ------------------------------------------------------------------ the M203 module, per gun
def module(g, frames):
    gz = S + 'zscript/rsr/rsr_m203_geo.zs'
    t = open(gz).read()
    # constants -> per-gun functions (gun 1 rifle = the file's own numbers, gun 2 machinegun)
    consts = dict(AXIS_L=('AxisL', g['axis_l']), AXIS_U=('AxisU', g['axis_u']), FRAME_FRONT=('FrameFront', g['frame_front']),
                  TUBE_REAR=('TubeRear', g['tube_rear']), TUBE_FRONT=('TubeFront', g['tube_front']), TRAVEL=('Travel', g['travel']),
                  ROUND_LEN=('RoundLen', None), ROUND_SEAT=('RoundSeat', None))
    rifle = {}
    for c in consts:
        m = re.search(r'\tconst %s = ([-\d.]+);' % c, t)
        rifle[c] = float(m.group(1))
    fns = ['\t// 1.97: per gun -- 1 = the rifle (the numbers above), 2 = the BD21 Machinegun (c2q/bd22_mg.py, measured on',
           '\t// its own mesh at MGN1 A: tube F %.2f..%.2f, travel %.2f (card %.2f), bore L %.2f U %.2f)' % (
               g['tube_rear'], g['tube_front'], g['travel'], g['travel_card'], g['axis_l'], g['axis_u'])]
    for c, (fn, mg) in consts.items():
        v = rifle[c] if mg is None else mg
        fns.append('\tclearscope static double %s(int gun) { return gun == 2 ? %.3f : %s; }' % (fn, v, c))
    old = '\tclearscope static Vector3 FwdHook() { return (0.0000, 0.0000, -1.0000); }'
    assert t.count(old) == 1
    fh = g['fwd_hook']
    t = t.replace(old, '\n'.join(fns) + '\n\tclearscope static Vector3 FwdHook(int gun) { return gun == 2 ? (%.4f, %.4f, %.4f) : (0.0000, 0.0000, -1.0000); }' % tuple(fh))
    # the no-tube twins: per gun
    old = '\tstatic void Names(out Array<Name> from, out Array<Name> to)\n\t{\n'
    assert t.count(old) == 1
    mgs = sorted({f[0] for f in frames})
    tw = ['\t// 1.97: the Machinegun\'s sprites and their no-tube twins (MODELDEF.rsm)',
          '\tstatic void NamesMG(out Array<Name> from, out Array<Name> to)', '\t{']
    twins = {}
    for i, sp in enumerate(mgs):
        twins[sp] = 'QU%02d' % i
        tw.append("\t\tfrom.Push('%s'); to.Push('%s');" % (sp, twins[sp]))
    tw.append('\t}\n')
    t = t.replace(old, '\n'.join(tw) + old)
    open(gz, 'w').write(t)
    # rsr_m203.zs: gun index on the state; every constant through it
    mz = S + 'zscript/rsr/rsr_m203.zs'
    t = open(mz).read()
    n0 = t.count('RSM_Geo.')
    for c, (fn, _) in consts.items():
        t = t.replace('RSM_Geo.%s' % c, 'RSM_Geo.%s(gun)' % fn)
    t = t.replace('RSM_Geo.FwdHook()', 'RSM_Geo.FwdHook(gun)')
    pairs = [
        ('\tclearscope static bool IsRifle(Weapon w)\n\t{\n\t\treturn w && w.GetClassName() == \'Rifle\';\n\t}',
         '\tclearscope static bool IsRifle(Weapon w)\n\t{\n\t\treturn w && w.GetClassName() == \'Rifle\';\n\t}\n\n'
         '\t// 1.97: the guns with a launcher the module works: 1 the rifle, 2 the BD21 Machinegun (c2q/bd22_mg.py)\n'
         '\tclearscope static int GunOf(Weapon w)\n\t{\n\t\tif (!w) return 0;\n\t\tName n = w.GetClassName();\n'
         '\t\tif (n == \'Rifle\') return 1;\n\t\tif (n == \'Machinegun\') return 2;\n\t\treturn 0;\n\t}'),
        ('class RSM_State play\n{\n', 'class RSM_State play\n{\n\tint gun;\t\t\t\t\t// 1.97: RSM.GunOf (1 rifle, 2 machinegun)\n'),
        ('\t\t\t\tRSM_NoTube.Names(f, t);', '\t\t\t\tif (gun == 2) RSM_NoTube.NamesMG(f, t); else RSM_NoTube.Names(f, t);'),
        ("\t\tRSR.SetPart(p, RSM.TUBE, parts, swapped, 'RQ2P', 0);\n\t\tRSR.SetPart(p, RSM.ROUND, parts, round, 'RQ2P', 1);",
         "\t\tRSR.SetPart(p, RSM.TUBE, parts, swapped, gun == 2 ? 'RQ3P' : 'RQ2P', 0);\n\t\tRSR.SetPart(p, RSM.ROUND, parts, round, gun == 2 ? 'RQ3P' : 'RQ2P', 1);"),
        ("\t\t\ts.active = vr && !dual && RSM.IsRifle(p.ReadyWeapon) && RSR_ReloadHandler.Wanted(mo);",
         "\t\t\tint gn = RSM.GunOf(p.ReadyWeapon);\t// 1.97\n\t\t\tif (gn != s.gun)\n\t\t\t{\n\t\t\t\ts.Reset();\n\t\t\t\ts.gun = gn;\n\t\t\t\ts.noTubeFrom.Clear(); s.noTubeTo.Clear();\n\t\t\t}\n"
         "\t\t\ts.active = vr && !dual && gn > 0 && RSR_ReloadHandler.Wanted(mo);"),
    ]
    for old, new in pairs:
        if t.count(old) != 1:
            raise SystemExit('rsr_m203.zs: %r found %d times' % (old[:50], t.count(old)))
        t = t.replace(old, new)
    # the handler's layer transform uses s.<field>: its RSM_Geo calls take s.gun
    t = re.sub(r'RSM_Geo\.(\w+)\(gun\)(?=[^\n]*\bs\.)', lambda m: 'RSM_Geo.%s(s.gun)' % m.group(1), t)
    # any RSM_Geo.X(gun) outside RSM_State (no `gun` in scope) -> check by hand below
    open(mz, 'w').write(t)
    log['module'] = dict(geo_refs=n0, twins=twins)
    # the sprites the new layers use
    sz = S + 'zscript/rsr/rsr_m203.zs'
    t = open(sz).read()
    old = '\t\tRQ2P AB 0;\n'
    assert t.count(old) == 1
    t = t.replace(old, old + '\t\tRQ3P AB 0;\t// 1.97: the Machinegun\'s tube and round\n' + ''.join('\t\t%s A 0;\n' % q for q in twins.values()))
    open(sz, 'w').write(t)
    return twins


def modeldef_rsm(g, frames, twins):
    """MODELDEF.rsm: the Machinegun without its tube (twins), the tube alone, the round at its breech"""
    i_pipe = g['surfaces'].index('alt-pipe')
    n = len(g['surfaces'])
    def skins(keep):
        return '\n'.join('\tSurfaceSkin 0 %d "%s"' % (i, 'Machinegun.png' if (i in keep) else 'rsr_clear.png') for i in range(n))
    hdr = '\tPath "models/bd/Machinegun"\n\tModel 0 "Machinegun.md3"\n'
    tail = '\tScale -1.0 1.0 1.0\n\tOffset 0.0 0.0 0.0\n\tZOffset -5\n\tNoInterpolation\n'
    out = ['\n// ---- 1.97: the BD21 Machinegun on the M203 module (c2q/bd22_mg.py)']
    # twins: every BD21 frame key, without the tube
    out.append('// the gun without its tube, keyed on the no-tube twin sprites (RSM_NoTube.NamesMG)')
    out.append('Model Machinegun\n{\n' + hdr + skins(set(range(n)) - {i_pipe}) + '\n' + tail +
               '\n'.join('\tFrameIndex %s %s 0 %s' % (twins[sp], fr, idx) for sp, fr, idx in frames) + '\n}')
    out.append('// the tube alone, at the gun (main controller; the module moves it by FwdHook per cm)')
    out.append('Model RSR_GunParts\n{\n' + hdr + skins({i_pipe}) + '\n' + tail + '\tFrameIndex RQ3P A 0 %d\n}' % READY_FRAME)
    # the round: the rifle's m203_round.md3 is authored at the rifle's breech; move it to this gun's
    # bore line and tube rear (FLU shift -> MODELDEF Offset: x = -dL, y = -dF, ZOffset += dU)
    rz = open(S + 'zscript/rsr/rsr_m203_geo.zs').read()
    r = {c: float(re.search(r'\tconst %s = ([-\d.]+);' % c, rz).group(1)) for c in ('AXIS_L', 'AXIS_U', 'TUBE_REAR')}
    dF = g['tube_rear'] - r['TUBE_REAR']; dL = g['axis_l'] - r['AXIS_L']; dU = g['axis_u'] - r['AXIS_U']
    out.append('// the round in the breech: the rifle\'s round mesh moved to this gun\'s bore (dF %.2f dL %.2f dU %.2f)' % (dF, dL, dU))
    out.append('Model RSR_GunParts\n{\n\tPath "models/bd/Rifle"\n\tModel 0 "m203_round.md3"\n\tSkin 0 "m203_round.png"\n'
               '\tScale -1.0 1.0 1.0\n\tOffset %.3f %.3f 0.0\n\tZOffset %.3f\n\tNoInterpolation\n\tFrameIndex RQ3P B 0 0\n}' % (-dL, -dF, -5 + dU))
    with open(S + 'MODELDEF.rsm', 'a') as f:
        f.write('\n'.join(out) + '\n')
    log['modeldef_rsm'] = dict(dF=round(dF, 2), dL=round(dL, 2), dU=round(dU, 2))


# ------------------------------------------------------------------ hands
def hands(g):
    it = dict(path=S + 'models/bd/Machinegun/Machinegun.md3', frame=READY_FRAME, scale=list(SCALE), off=[OFF[0], OFF[1], ZOFF], color=[150, 155, 170])
    gun_pts = handfit_cards.surface_points(it); gpt = handfit_cards.gun_tris(it)
    # the MG42's letters (the pack's own belt gun): gun F / F, support B, trigger I
    two = [k for k, v in handfit_cards.GUN_LETTER.items() if v == 'F'][0]
    sup = [k for k, v in handfit_cards.SUP_LETTER.items() if v == 'B'][0]
    tg, err, why = handfit_cards.fit_gun(gun_pts, np.array(g['palm']), 'hand:%d' % two)
    if tg is None:
        raise SystemExit('gun hand: ' + why)
    t2, err2, fp, why2 = handfit_cards.fit_support(gun_pts, gpt, g['supportat'], 'hand2:%d' % sup)
    if t2 is None:
        raise SystemExit('support: ' + why2)
    row = dict(one='F', two='F', sup='B', trig='I', hook=(round(tg[1], 3), round(tg[2], 3), round(-tg[0], 3)),
               shook=(round(t2[1], 3), round(t2[2], 3), round(-t2[0], 3)), spoint=tuple(np.round(np.array(fp) / 100.0, 3)),
               err_gun=round(float(err), 2), err_sup=round(float(err2), 2))
    log['hands'] = row
    hz = S + 'zscript/rsq/handtable.zs'
    t = open(hz).read()
    old = "\t\tif (w is 'DSweap')\treturn 26;"
    assert t.count(old) == 1
    t = t.replace(old, old + "\n\t\tif (w is 'Machinegun')\treturn 27;\t// 1.97: the BD21 Machinegun (c2q/bd22_mg.py: kit ICP on the REMA card's palm / supportat)")
    def app(fn, kind, vals):
        nonlocal t
        if kind == 's':
            m = re.search(r'(static String %s\(int i\)\n\t\{\n\t\tstatic const String v\[\] = \{.*?)( \};)' % fn, t, re.S)
            t = t[:m.end(1)] + ', "%s"' % vals + t[m.end(1):]
        else:
            m = re.search(r'static Vector3 %s\(int i\)\n\t\{\n(\t\tstatic const double x\[\] = \{.*?)( \};\n)(\t\tstatic const double y\[\] = \{.*?)( \};\n)(\t\tstatic const double z\[\] = \{.*?)( \};\n)' % fn, t, re.S)
            x, y, z = vals
            t = (t[:m.end(1)] + ', %.3f' % x + t[m.end(1):m.end(3)] + ', %.3f' % y + t[m.end(3):m.end(5)] + ', %.3f' % z + t[m.end(5):])
    app('GunOne', 's', row['one']); app('GunTwo', 's', row['two']); app('Support', 's', row['sup']); app('Trigger', 's', row['trig'])
    app('GunHook', 'v', row['hook']); app('GunRot', 'v', (0, 0, 0)); app('SupportHook', 'v', row['shook']); app('SupportRot', 'v', (0, 0, 0))
    app('SupportPoint', 'v', row['spoint']); app('GunHookTwo', 'v', row['hook']); app('GunRotTwo', 'v', (0, 0, 0))
    open(hz, 'w').write(t)
    # the check sheet
    items = [it, handfit_cards.hand_item('hand', two, np.array(tg)), handfit_cards.hand_item('hand2', sup, np.array(t2), color=(120, 200, 140))]
    marks = [(*g['palm'], 'palm', (255, 200, 60)), (*g['supportat'], 'support', (120, 230, 140)), (*g['latch'], 'latch', (255, 120, 120)), (*g['loadat'], 'breech', (120, 160, 255))]
    os.makedirs(OUT + '_hands', exist_ok=True)
    import gunview
    from PIL import Image
    a, b = OUT + '_hands/Machinegun.side.png', OUT + '_hands/Machinegun.bottom.png'
    gunview.view(items, a, 'side', px=5, marks=marks, title='Machinegun hands'); gunview.view(items, b, 'bottom', px=5, marks=marks, title='Machinegun hands')
    A, B = Image.open(a), Image.open(b); O = Image.new('RGB', (max(A.width, B.width), A.height + B.height)); O.paste(A, (0, 0)); O.paste(B, (0, A.height))
    O.save(OUT + '_hands/Machinegun.png'); os.remove(a); os.remove(b)


# ------------------------------------------------------------------ roster option
ROSTER = '''// roster.zs (1.97) -- guns added to the BD22 roster with an option to stand in for a BD22 gun
// (c2q/bd22_mg.py). Off (default): both exist. On: every spawn of the BD22 gun is the added gun
// (map pickups, spawners, drops). Server cvars: the playsim must agree.
class RSQ_Roster : EventHandler
{
	override void CheckReplacement(ReplaceEvent e)
	{
		if (!e.Replacee) return;
		let cv = CVar.FindCVar('rsq_mg_replaces_mg42');
		if (cv && cv.GetInt() != 0 && e.Replacee.GetClassName() == 'MG42')
			e.Replacement = 'Machinegun';
	}
}
'''


def roster():
    open(S + 'zscript/rsq/roster.zs', 'w').write(ROSTER)
    edit(S + 'ZSCRIPT.rsvr', [('#include "zscript/rsq/counters.zs"\n', '#include "zscript/rsq/counters.zs"\n#include "zscript/rsq/roster.zs"\n')])
    edit(S + 'MAPINFO.rsvr', [('"RSQ_Counters", ', '"RSQ_Counters", "RSQ_Roster", ')])
    with open(S + 'CVARINFO.rsq', 'a') as f:
        f.write('\n// 1.97: roster\nserver bool rsq_mg_replaces_mg42 = false;\t// every MG42 spawn is the BD21 Machinegun\n')
    edit(S + 'MENUDEF.rsq', [('\tOption "Rifle Underbarrel Ammo", "rsm_ammo", "RSM_Ammo"\n',
                              '\tOption "Rifle Underbarrel Ammo", "rsm_ammo", "RSM_Ammo"\n\tOption "Machinegun replaces MG42", "rsq_mg_replaces_mg42", "OnOff"\n')])
    log['roster'] = 'rsq_mg_replaces_mg42 (server), menu row after Rifle Underbarrel Ammo (its ammo option covers the Machinegun too)'


def sprites(frames):
    """dummy lumps for the BD21 sprite names (the HUD is the model; BD22 has no MGN1/MGN2/MGS1)"""
    from PIL import Image
    d = S + 'sprites/'; os.makedirs(d, exist_ok=True)
    img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    names = sorted({'%s%s0' % (sp, fr) for sp, fr, _ in frames} | {'MGN1Z0'})
    for nm in names:
        img.save(d + nm + '.png')
    log['dummy_sprites'] = len(names)


if __name__ == '__main__':
    g, ts, names = geometry()
    frames = assets(g, names)
    decorate()
    twins = module(g, frames)
    modeldef_rsm(g, frames, twins)
    hands(g)
    roster()
    sprites(frames)
    json.dump(log, open(OUT + 'mg_apply.json', 'w'), indent=1)
    print(json.dumps(log, indent=1))
