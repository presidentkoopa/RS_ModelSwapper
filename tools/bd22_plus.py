"""bd22_plus.py -- the BD22 flagship's Plus toggles: real VR reloads for the three BD22 guns that Brutal
Doom itself never reloads (MG42 belt drum, Flamethrower2 canister, Unmaker skull), built into
RS_Brutal22WeaponsQ 1.96b's own architecture (vreload.zs / gen_rsr tables / rsr_patch-style DECORATE
patch / MODELDEF.rsr), each behind a menu row. Off = Brutal Doom exactly as shipped.

Sources, and nothing else:
  mesh      1.96b's own gun mesh (src/models/bd/<gun>), carved by reference against REMA's *_wm.md3
            (same vertices, rigid residual ~0.01 cm; carve_by_ref.py) so the drum / canister / skull are
            their own surfaces; all frames kept.
  card      REMA's WMCARD.bd22 feed part (slide axis, travel, grab) and magcenter, carried onto the
            1.96b mesh by the same rigid transform; capacity from WMSHEET.bd22 (the owner's own
            numbers: BD22 has none -- flagged in the README).
  parent    BD22's DECORATE: the gun's ammo type, AmmoUse and Ready loop, read from brutal22test6.

Stage 1 (this file, `geometry`): survey records + gen_rsr GUNS entries + the carved meshes to ship.
    python3 bd22_plus.py geometry   -> build/bd22/plus_geometry.json, build/bd22/models/*_rsr.md3
"""
import os, sys, json
import numpy as np
from scipy.spatial import cKDTree
TOOLS = os.path.dirname(os.path.abspath(__file__))                 # this repo's tools/
KIT = os.path.join(TOOLS, 'kit')                                   # gen_rsr.py, rgeo.py
sys.path.insert(0, TOOLS)
sys.path.insert(0, KIT)
import genpack, carve_by_ref, rgeo

REPO = os.path.dirname(TOOLS)
SRC = 'E:/DOOMWork/_buildtemp/rs_brutal22weaponsq/src/'            # RS_Brutal22WeaponsQ 1.96b src @ 27bef2b
                                                                   # (the repo's runtime/ is a 33-file subset, not the snapshot)
REMA = 'E:/DOOMWork/RS_VR_Weapons/bd22/'                           # RS_VR_Weapons checkout, bd22/
OUT = 'E:/DOOMWork/_buildtemp/rsq_bd22/'                           # build dir (outside the repo)
BD22SRC = 'E:/DOOMWork/_buildtemp/bd22src/'                        # brutal22test6.pk3 extracted (actors/Weapons/*.dec)
SCALE, OFF = (-1.0, 1.0, 1.0), (0.0, 0.0, 0.0)        # MODELDEF.bd.txt: all three guns

# the three toggles: 1.96b class -> sources
PLUS = {
    # F6 reload foley. Brutal Doom never reloads these three, so it has no sound for it -- and
    # neither does REMA's bd22 set. Each name below is one BD22 ALREADY HAS, checked in
    # brutal22test6's own SNDINFO, and is REFERENCED, not declared: this pack always loads after
    # brutal22test6, so naming its sounds costs nothing and ships no files. (REMA renames its copies
    # to bd22/... because that set is standalone and a bare `Pistol/Reload1` would collide with the
    # mod's own and silently lose on load order. That reasoning does not apply to an addon.)
    #   MG42        the drum is a big box magazine -> the USAS-12's drum (USASOUT / USASIN)
    #   Flamethrower a canister is a heavy cylinder -> the railgun's cell (RGREL1 / RGREL2)
    #   Unmaker     the gun itself answers the skull: it dies as it leaves, wakes as it seats
    # Alternatives, if any of these sound wrong in the headset: Chaingun/belt (MINIBELT, the literal
    # belt), Chaingun/beltQuiet, Plasma/Reload1-2, Flamer/Select, MG42/Draw.
    'MG42': dict(card='BD_Buzzsaw', ref='buzzsaw_wm.md3', mesh='HitlersBuzzsaw/HitlersBuzzsaw.md3',
                 part='magazine', ref_parts={'magazine': 'magazine'}, ready_frame=0,
                 snd_out='rsr/drumout', snd_in='rsr/drumin', snd_land='rsr/bigdrop',
                 toggle='rsq_plus_mg42', label='MG42: Belt Drum Reload',
                 reserve='Clip2', magammo='RSQ_MG42Drum', nomag='RSQ_NoDrum_MG42', ammouse=1,
                 ready_sprites=['HBUS A'], spr=('RQXM', 'RQXP', 'RQXW')),
    'Flamethrower2': dict(card='BD_Flamethrower', ref='flamethrower_wm.md3', mesh='Flamethrower2/Flamethrower2.md3',
                 part='canister', ref_parts={'canister': 'magazine'}, ready_frame=0,
                 snd_out='rsr/canout', snd_in='rsr/canin', snd_land='rsr/bigdrop',
                 toggle='rsq_plus_flamer', label='Flamethrower: Canister Reload',
                 reserve='Gas', magammo='RSQ_FlamerCanister', nomag='RSQ_NoCanister_Flamer', ammouse=1,
                 ready_sprites=['FLMT A', '2LMT A'], spr=('RQYM', 'RQYP', 'RQYW')),
    'Unmaker': dict(card='BD_Unmaker', ref='unmaker_wm.md3', mesh='Unmaker/Unmaker.md3',
                 part='skull', ref_parts={'skull': 'magazine', 'skull2': 'magazine'}, ready_frame=0,
                 snd_out='Unmaker/Stop', snd_in='Unmaker/Start', snd_land='rsr/bigdrop',
                 toggle='rsq_plus_unmaker', label='Unmaker: Skull Reload',
                 reserve='SoulAmmo', magammo='RSQ_UnmakerSkull', nomag='RSQ_NoSkull_Unmaker', ammouse=2,
                 ready_sprites=['UNHG A', '2NHG A'], spr=('RQWM', 'RQWP', 'RQWW')),
}


def card_block(name):
    """the REMA card: keys + the feed part (wmcard.py's reader)"""
    import wmcard
    cards = {w["cls"]: w for w in wmcard.load([REMA + "WMCARD.bd22"])}
    return cards[name]


def sheet_capacity(name):
    t = open(REMA + 'WMSHEET.bd22', encoding='latin1').read()
    s = t.find('gun "%s"' % name); e = t.find('\nend', s)
    for ln in t[s:e].splitlines():
        if ln.strip().startswith('capacity'):
            return int(ln.split('=')[1].split('#')[0])
    raise SystemExit('no capacity on the sheet for ' + name)


def rigid(ref_md3, tgt_md3, frame=0):
    """R, t with  tgt = R @ ref + t  (ICP from the centroids; the meshes are the same vertices)"""
    _, rs = genpack.md3_surfaces(ref_md3)
    _, ts = genpack.md3_surfaces(tgt_md3)
    A = np.vstack([s['xyz'][0] for s in rs]); B = np.vstack([s['xyz'][frame] for s in ts])
    tree = cKDTree(B); Rm = np.eye(3); t = B.mean(0) - A.mean(0)
    for _ in range(60):
        d, idx = tree.query(A @ Rm.T + t); Rm, t = carve_by_ref.kabsch(A, B[idx])
    d, _ = tree.query(A @ Rm.T + t)
    return Rm, t, float(d.mean()), float(d.max())


def geometry():
    os.makedirs(OUT + 'models', exist_ok=True)
    out = {}
    for cls, p in PLUS.items():
        ref = REMA + 'models/bd22/' + p['ref']
        mesh = SRC + 'models/bd/' + p['mesh']
        carved = OUT + 'models/' + os.path.basename(p['mesh']).replace('.md3', '_rsr.md3')
        cv = carve_by_ref.carve(ref, mesh, carved, p['ref_parts'])
        Rm, t, dmean, dmax = rigid(ref, mesh, 0)
        card = card_block(p['card'])
        part = card['parts'][p['part']]
        axis_out = np.array([float(x) for x in part['dof']['axis']])
        grab = np.array([float(x) for x in part['keys']['grab']])
        magc = np.array([float(x) for x in card['keys']['magcenter']])
        # into the 1.96b mesh, then into the controller frame (F, L, U) through the gun's own MODELDEF
        X = lambda v: rgeo.to_flu((Rm @ v + t)[None, :], SCALE, OFF)[0]
        D = lambda v: rgeo.to_flu((Rm @ v)[None, :], SCALE, OFF)[0] - rgeo.to_flu(np.zeros((1, 3)), SCALE, OFF)[0]
        ins = -D(axis_out); ins /= np.linalg.norm(ins)
        nsurf, surfs = genpack.md3_surfaces(carved)
        names = [s['name'] for s in surfs]
        mag_idx = [i for i, n in enumerate(names) if n == 'magazine']
        depth, base, top, hw = genpack.mouth_depth(surfs, p['ready_frame'], SCALE, OFF, mag_idx, None, ins)
        travel = float(part['dof']['distance'])
        rec = dict(cls=cls, card=p['card'], carved=carved, surfaces=cv['surfaces'], frames=cv['frames'],
                   unlabelled=cv['unlabelled'], rigid=dict(mean_cm=round(dmean, 4), max_cm=round(dmax, 4), rot_deg=cv['rot_deg']),
                   capacity=sheet_capacity(p['card']), ammouse=p['ammouse'],
                   survey=dict(parts=dict(magazine=dict(well_point=top.round(3).tolist(), insert_dir=ins.round(4).tolist(),
                                                        insert_depth_cm=depth, base_point=base.round(3).tolist(),
                                                        half_width_cm=round(hw, 2), card_travel_cm=travel,
                                                        card_grab=X(grab).round(3).tolist(), card_magcenter=X(magc).round(3).tolist()))),
                   palm=X(np.array([float(x) for x in card['grip']['palm']])).round(3).tolist(),
                   supportat=X(np.array([float(x) for x in card['grip']['supportat']])).round(3).tolist(),
                   mag_idx=mag_idx, names=names)
        out[cls] = rec
        print('%-14s carve %s unlabelled=%d rigid mean %.4f max %.4f rot %.2f deg' % (cls, cv['surfaces'], cv['unlabelled'], dmean, dmax, cv['rot_deg']))
        print('   well %s  in %s  mouth %.2f  base %s  hw %.1f  travel(card) %.1f  cap %d' % (
            top.round(2), ins.round(3), depth, base.round(2), hw, travel, rec['capacity']))
    json.dump(out, open(OUT + 'plus_geometry.json', 'w'), indent=1)
    return out


if __name__ == '__main__':
    if sys.argv[1:] == ['geometry']:
        geometry()


# ======================================================================= stage 2: apply
# Writes a patched copy of 1.96b's src (OUT/src) -- the pack's own files, every change an exact-match
# edit or an append, listed here -- and zips it. 1.96b's repo is never written.
import shutil, zipfile, importlib, re, glob

OUT_SRC = OUT + 'src/'
WAIT = [
    '\tRSR_Wait:\t\t// the gun as the script shows it ("####" "#"); the script runs every tic',
    '\t\t"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE)',
    '\t\t"####" "#" 0 A_GiveInventory("RSR_Tick", 1)',
    '\t\t"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill")',
    '\t\t"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done")',
    '\t\tGoto RSR_Wait',
]
# BD22's own ammo checks and shots: a guard goes after each check and before each shot
GUARD_AFTER = re.compile(r'A_JumpIfNoAmmo\s*\(')
GUARD_BEFORE = re.compile(r'A_FireBullets\s*\(.*FBF_USEAMMO|A_FireCustomMissile\s*\(\s*"(FlamethrowerProjectile|UnmakerLaser)')
import re


def once(lines, pred, what):
    hits = [i for i, l in enumerate(lines) if pred(l)]
    if len(hits) != 1:
        raise SystemExit('%s: found %d times' % (what, len(hits)))
    return hits[0]


def actor_span(lines, cls):
    a = once(lines, lambda l: re.match(r'\s*ACTOR\s+%s\b' % cls, l, re.I) is not None, 'ACTOR ' + cls)
    depth = 0; b = None
    for i in range(a, len(lines)):
        depth += lines[i].count('{') - lines[i].count('}')
        if depth == 0 and i > a:
            b = i; break
    return a, b


def rsr_block(cls, p, cap):
    mag, nomag, fill, empty = 'RSQ_Mag_' + cls, 'RSQ_NoMag_' + cls, 'RSQ_Fill_' + cls, 'RSQ_Empty_' + cls
    S = lambda s: '\t\t"####" "#" 0 ' + s
    L = ['\t// posefix rsr (1.97): real VR reload (zscript/rsr/vreload.zs) on a gun Brutal Doom never reloads.',
         '\t// The %s is a COUNTER over BD22\'s own ammo (zscript/rsq/counters.zs, capacity %d -- the owner\'s' % (p['part'], cap),
         '\t// REMA number; BD22 has none): firing and the reserve are BD22\'s, untouched. With VR reloading',
         '\t// off (rsr_reload 0, or not in VR) the counter is idle and nothing below changes the gun.',
         '\tReload:',
         S('A_TakeInventory("Reloading", 1)'),
         S('A_JumpIfInventory("%s", 0, "Ready")\t// full' % mag),
         S('A_JumpIfInventory("%s", 1, "RSR_Start")' % p['reserve']),
         '\t\tGoto Ready\t// nothing in the reserve',
         '\tRSR_Start:',
         S('A_TakeInventory("RSR_Go", 1)'),
         S('A_GiveInventory("RSR_Start", 1)'),
         S('A_JumpIfInventory("RSR_Go", 1, "RSR_Out")'),
         '\t\tGoto Ready\t// RSR_Stock: BD22 has no reload for this gun',
         '\tRSR_Out:',
         S('A_TakeInventory("RSR_Go", 1)'),
         S('A_JumpIfInventory("%s", 1, "RSR_Wait")\t// already out' % nomag),
         S('A_GiveInventory("RSR_MagOut", 1)\t// the %s comes off (its own sound)' % p['part']),
         S('A_TakeInventory("%s", 0)\t// its rounds go with it; the reserve is BD22\'s pool and loses none' % mag),
         S('A_GiveInventory("%s", 1)' % nomag),
         ] + WAIT + [
         '\tRSR_Fill:\t\t// seated: the counter takes the reserve\'s count, up to its capacity (counters.zs)',
         S('A_TakeInventory("RSR_Seated", 1)'),
         S('A_TakeInventory("%s", 1)' % nomag),
         S('A_GiveInventory("%s", 1)' % fill),
         S('A_GiveInventory("RSR_Filled", 1)'),
         '\t\tGoto RSR_Wait',
         '\tRSR_Done:',
         S('A_TakeInventory("RSR_Done", 1)'),
         S('A_TakeInventory("Reloading", 1)'),
         S('A_ReFire'),
         '\t\tGoto Ready',
         ]
    return L


def patch_dec(cls, p, text, cap):
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    a, b = actor_span(lines, cls)
    empty = 'RSQ_Empty_' + cls
    guard = '\t\t"####" "#" 0 A_JumpIfInventory("%s", 1, "Reload")\t// posefix rsr: the %s is empty' % (empty, p['part'])
    # 1. the Flamethrower's "Reload:" is an alias of ReadyDry: it goes (ours below replaces it)
    if cls == 'Flamethrower2':
        k = once(lines, lambda l: l.strip() == 'Reload:', 'Flamethrower2 Reload alias')
        assert lines[k - 1].strip() == 'ReadyDry:', lines[k - 1]
        del lines[k]
        a, b = actor_span(lines, cls)
    # 2. the Ready hook: the reload key (BD22's ACS gives "Reloading") after the first A_WeaponReady of Ready
    r = once(lines[a:b], lambda l: l.strip() in ('Ready:',), cls + ' Ready label') + a
    w = next(i for i in range(r, b) if 'A_WeaponReady' in lines[i])
    lines.insert(w + 1, '\t\t"####" "#" 0 A_JumpIfInventory("Reloading", 1, "Reload")\t// posefix rsr: the reload key')
    a, b = actor_span(lines, cls)
    # 3. guards: after each A_JumpIfNoAmmo, before each shot
    out = []; n_after = n_before = 0
    for i, l in enumerate(lines):
        if a < i < b and GUARD_BEFORE.search(l) and 'posefix' not in l:
            out.append(guard); n_before += 1
        out.append(l)
        if a < i < b and GUARD_AFTER.search(l):
            out.append(guard); n_after += 1
    lines = out
    a, b = actor_span(lines, cls)
    # 4. the RSR states, first inside States {
    s = next(i for i in range(a, b) if lines[i].strip() == 'States')
    assert lines[s + 1].strip() == '{', lines[s + 1]
    lines[s + 2:s + 2] = rsr_block(cls, p, cap)
    if 'posefix' not in lines[0]:
        lines.insert(0, '// posefix: BD22 brutal22test6 file. Lines marked "posefix" are the only changes ("rsr": real VR reload).')
    return nl.join(lines), dict(guards_after_check=n_after, guards_before_shot=n_before)


def merge_tables(old, new, newcls):
    """append the new guns' cases to every switch of RSR_Guns in the pack's rsr_guns.bd.zs"""
    m = re.search(r'return (\d+); \}', old); n0 = int(m.group(1)); n1 = n0 + len(newcls)
    old = old.replace('clearscope static int Count() { return %d; }' % n0, 'clearscope static int Count() { return %d; }' % n1, 1)
    # Index
    idx_new = '\n'.join("\t\tif (n == '%s')\treturn %d;" % (c, n0 + 1 + k) for k, c in enumerate(newcls))
    old = re.sub(r"(\t\tif \(n == '[^']+'\)\treturn %d;\n)" % n0, r'\1' + idx_new + '\n', old, count=1)
    # every switch: take the new file's cases for 1..k, renumber, append before the switch's closing brace
    fn_old = {m.group(1): m for m in re.finditer(r'clearscope static \w+ (\w+)\(int i\)\n\t\{\n\t\tswitch \(i\)\n\t\t\{\n(.*?)\n\t\t\}', old, re.S)}
    fn_new = {m.group(1): m.group(2) for m in re.finditer(r'static \w+ (\w+)\(int i\)\n\t\{\n\t\tswitch \(i\)\n\t\t\{\n(.*?)\n\t\t\}', new, re.S)}
    out = old; added = {}
    for name, mo in sorted(fn_old.items(), key=lambda kv: -kv[1].start(2)):
        if name not in fn_new:
            continue
        cases = [l for l in fn_new[name].split('\n') if l.strip().startswith('case')]
        ren = [re.sub(r'case (\d+):', lambda m: 'case %d:' % (n0 + int(m.group(1))), l) for l in cases]
        out = out[:mo.end(2)] + '\n' + '\n'.join(ren) + out[mo.end(2):]
        added[name] = len(ren)
    missing = [n for n in fn_new if n not in fn_old]
    # RSR_GunSprites: a sprite name is only known to the engine if some actor's states use it -- the
    # pack ships no RQ** lumps. Merging the switches but not this list is fatal at load:
    # "Unknown sprite RQXM in model definition for MG42" (gen_rsr writes the list, we append its lines).
    sp_new = re.search(r'class RSR_GunSprites : Actor.*?\tSpawn:\n(.*?)\n\t\tStop;', new, re.S)
    sp_old = re.search(r'class RSR_GunSprites : Actor.*?\tSpawn:\n.*?(?=\n\t\tStop;)', out, re.S)
    if not sp_new or not sp_old:
        raise SystemExit('rsr_guns.bd.zs: RSR_GunSprites Spawn block not found (new=%s, old=%s)'
                         % (bool(sp_new), bool(sp_old)))
    out = out[:sp_old.end()] + '\n' + sp_new.group(1) + out[sp_old.end():]
    added['sprites'] = [l.split()[0] for l in sp_new.group(1).split('\n') if l.strip()]
    # the held-rounds classes
    held = [l for l in new.split('\n') if l.startswith('class RSR_Held_')]
    out = out.rstrip('\n') + '\n' + '\n'.join(held) + '\n'
    return out, added, missing


COUNTERS = '''// counters.zs (1.97) -- magazine COUNTERS for guns Brutal Doom never reloads (MG42 belt drum,
// Flamethrower2 canister, Unmaker skull). BD22's firing and ammo are untouched: the counter
// mirrors the reserve going down shot by shot, and when it is empty the gun's Reload runs
// (actors/Weapons/*.dec, "posefix rsr"). The real VR reload (vreload.zs) swaps the part; on
// the seat the counter takes the reserve's count up to its capacity. Idle unless VR reloading
// is on (RSR.WantsHands), so with it off the guns are Brutal Doom's exactly.

class RSQ_Counters : EventHandler
{
	static const Name GUN[] = { %(guns)s };
	static const Name MAG[] = { %(mags)s };
	static const Name RES[] = { %(res)s };
	static const int CAP[] = { %(caps)s };
	int lastRes[MAXPLAYERS][%(n)d];
	bool inited[MAXPLAYERS][%(n)d];

	override void WorldTick()
	{
		for (int pn = 0; pn < MAXPLAYERS; pn++)
		{
			if (!playeringame[pn]) continue;
			PlayerPawn mo = players[pn].mo;
			if (!mo) continue;
			let w = players[pn].ReadyWeapon;
			for (int g = 0; g < GUN.Size(); g++)
			{
				class<Inventory> mag = MAG[g]; class<Inventory> res = RES[g];
				class<Inventory> empty = "RSQ_Empty_" .. GUN[g]; class<Inventory> fill = "RSQ_Fill_" .. GUN[g];
				class<Inventory> nomag = "RSQ_NoMag_" .. GUN[g];
				if (!mag || !res || !empty || !fill || !nomag) continue;
				bool held = w && w.GetClassName() == GUN[g];
				int r = mo.CountInv(res);
				if (!held || !RSR_ReloadHandler.WantsHands(mo))
				{
					mo.TakeInventory(empty, 1);
					lastRes[pn][g] = r;
					continue;
				}
				if (!inited[pn][g])
				{
					inited[pn][g] = true;
					SetCount(mo, mag, min(CAP[g], r));
					mo.TakeInventory(nomag, 1);
				}
				int d = lastRes[pn][g] - r;
				if (d > 0)
					SetCount(mo, mag, max(0, mo.CountInv(mag) - d));
				if (mo.CountInv(fill) > 0)
				{
					mo.TakeInventory(fill, 1);
					SetCount(mo, mag, min(CAP[g], r));
					mo.TakeInventory(nomag, 1);
				}
				bool e = mo.CountInv(mag) <= 0 && r > 0;
				if (e) mo.GiveInventory(empty, 1); else mo.TakeInventory(empty, 1);
				lastRes[pn][g] = r;
			}
		}
	}

	static void SetCount(PlayerPawn mo, class<Inventory> it, int n)
	{
		int c = mo.CountInv(it);
		if (n > c) mo.GiveInventory(it, n - c);
		else if (n < c) mo.TakeInventory(it, c - n);
	}
}

%(items)s
'''


def apply():
    geo = json.load(open(OUT + 'plus_geometry.json'))
    if os.path.exists(OUT_SRC):
        shutil.rmtree(OUT_SRC)
    shutil.copytree(SRC, OUT_SRC)
    log = {}
    sys.path.insert(0, KIT)
    import gen_rsr
    guns = []
    for cls, p in PLUS.items():
        r = geo[cls]
        gdir = p['mesh'].split('/')[0]
        model = os.path.basename(r['carved'])
        shutil.copy(r['carved'], OUT_SRC + 'models/bd/%s/%s' % (gdir, model))
        clear = OUT_SRC + 'models/bd/%s/rsr_clear.png' % gdir
        if not os.path.exists(clear):
            shutil.copy(SRC + 'models/bd/Rifle/rsr_clear.png', clear)
        g = dict(key='BD22/' + cls, cls=cls, set='bd', mesh=r['carved'], path='models/bd/' + gdir, model=model,
                 skin=p['mesh'].split('/')[1].replace('.md3', '.png'), scale=SCALE, off=OFF, extra='\tNoInterpolation\n',
                 ready_frame=0, mag_surfs=r['mag_idx'], handle_surfs=[], bolt_surfs=[], ready_sprites=p['ready_sprites'],
                 spr_gun=p['spr'][0], spr_part=p['spr'][1], spr_world=p['spr'][2], handle_mode=None, handle_part=None, bolt_part=None,
                 grip='base', back_at=1.0, snd=dict(out=p.get('snd_out', ''), inn=p.get('snd_in', ''), back='', fwd='', land=p.get('snd_land', '')),
                 reserve=p['reserve'], magammo='RSQ_Mag_' + cls, nomag='RSQ_NoMag_' + cls, charge='never', charge_token='',
                 reload_token='Reloading', chan=5)
        guns.append(gen_rsr.compute(g, {g['key']: r['survey']}))
    # tables
    z = gen_rsr.zs(guns); z = z if isinstance(z, str) else '\n'.join(z)
    tp = OUT_SRC + 'zscript/rsr/rsr_guns.bd.zs'
    merged, added, missing = merge_tables(open(tp).read(), z, list(PLUS))
    open(tp, 'w').write(merged)
    log['tables'] = dict(added=added, functions_new_only=missing)
    # MODELDEF.rsr
    md = ''
    for g in guns:
        m = gen_rsr.modeldef(g); md += (m if isinstance(m, str) else '\n'.join(m)) + '\n'
    with open(OUT_SRC + 'MODELDEF.rsr', 'a') as f:
        f.write('\n// ---- 1.97: the drum / canister / skull reloads (tools: c2q/bd22_plus.py)\n' + md)
    # F6 foley for the three reloads BD22 has no sound for. Same pattern SNDINFO.rsr already uses
    # for its racking sounds ("where BD22 has none", from RS_Main): our own rsr/ names, our own
    # copies of the files. The owner allowed RS_VR_Weapons' library for what BD22 lacks
    # (2026-10-24). Declared under rsr/, never under wm/ or BD22's own names -- REMA's SNDINFO
    # says why: a bare `Pistol/Reload1` collides the moment both packs load and the last one wins
    # silently, on load order.
    sd = OUT_SRC + 'sounds/rsr/'
    os.makedirs(sd, exist_ok=True)
    lines = ['', "// 1.97: the drum / canister / skull reloads. BD22 never reloads these three and has",
             '// no foley for it; neither does REMA\'s bd22 set. From RS_VR_Weapons, with the owner\'s',
             '// say-so, under our own names so nothing collides.']
    for nm, src_rel, why in FOLEY:
        shutil.copy(RSVRW + src_rel, sd + os.path.basename(src_rel))
        lines.append('%-14s sounds/rsr/%s\t// %s' % (nm, os.path.basename(src_rel), why))
    # a $random must be declared before the names it draws from (REMA's SNDINFO says so)
    drops = [n for n, _, _ in FOLEY if n.startswith('rsr/bigdrop')]
    lines.insert(4, '$random rsr/bigdrop { %s }' % ' '.join(drops))
    with open(OUT_SRC + 'SNDINFO.rsr', 'a') as f:
        f.write('\n'.join(lines) + '\n')
    log['foley'] = {n: os.path.basename(s) for n, s, _ in FOLEY}
    # DECORATE
    for cls, p in PLUS.items():
        fn = {'MG42': 'MG42.dec', 'Flamethrower2': 'Flamethrower.dec', 'Unmaker': 'Unmaker.dec'}[cls]
        src = OUT_SRC + 'actors/Weapons/' + fn
        if not os.path.exists(src):
            shutil.copy(BD22SRC + 'actors/Weapons/' + fn, src)       # BD22's own file, untouched by 1.96b
            log.setdefault('copied_from_bd22', []).append(fn)
        text = open(src, 'rb').read().decode('latin-1')
        new, st = patch_dec(cls, p, text, geo[cls]['capacity'])
        open(src, 'wb').write(new.encode('latin-1'))
        log[cls] = st
    # counters.zs
    items = []
    for cls, p in PLUS.items():
        cap = geo[cls]['capacity']
        items.append('class RSQ_Mag_%s : Inventory { Default { Inventory.MaxAmount %d; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }' % (cls, cap))
        for k in ('NoMag', 'Empty', 'Fill'):
            items.append('class RSQ_%s_%s : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }' % (k, cls))
    q = lambda xs: ', '.join("'%s'" % x for x in xs)
    open(OUT_SRC + 'zscript/rsq/counters.zs', 'w').write(COUNTERS % dict(
        guns=q(PLUS), mags=q('RSQ_Mag_' + c for c in PLUS), res=q(p['reserve'] for p in PLUS.values()),
        caps=', '.join(str(geo[c]['capacity']) for c in PLUS), n=len(PLUS), items='\n'.join(items)))
    zp = OUT_SRC + 'ZSCRIPT.rsvr'; zt = open(zp).read()
    anchor = '#include "zscript/rsr/rsr_guns.bd.zs"\n'
    assert zt.count(anchor) == 1
    open(zp, 'w').write(zt.replace(anchor, anchor + '#include "zscript/rsq/counters.zs"\n'))
    mp = OUT_SRC + 'MAPINFO.rsvr'; mt = open(mp).read()
    anchor = '"RSR_ReloadHandler", '
    assert mt.count(anchor) == 1
    open(mp, 'w').write(mt.replace(anchor, anchor + '"RSQ_Counters", '))
    json.dump(log, open(OUT + 'plus_apply.json', 'w'), indent=1)
    print(json.dumps(log, indent=1))


def pk3(path, drop=()):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT_SRC):
            for f in sorted(files):
                rel = os.path.relpath(os.path.join(root, f), OUT_SRC).replace(os.sep, '/')
                if any(rel.lower().startswith(d.lower()) for d in drop):
                    continue
                z.write(os.path.join(root, f), rel)
    print(path, os.path.getsize(path) >> 20, 'MB')


# ---------------------------------------------------------------- F2: Shot/Revolver Reload
# rsb_guns.zs says "generated by tools/gen_rsb.py" -- that generator is in no checkout here, and
# assemble.py only stubs the table, so this stage appends to it the way merge_tables appends to
# rsr_guns.bd.zs: indices 1..6 are never touched, so the 2026-10-13 speedloader patch survives.
#
# That patch put BD22's Revolver (index 3) on a speedloader and left its five per-chamber rows
# unused -- and overwrote k=0 of Base/Tip with the mean of the five rims. Index 7 is the same gun
# loaded a round at a time: index 3's rows verbatim, Chambers 5, Loader false, and the five seats,
# whose k=0 is recovered as 5*mean - sum(the four survivors) and checked against the cylinder's own
# five-fold symmetry before it is used. Index() picks 3 or 7 from rsb_revolver_feed.
REV_FEED = '''
	// 1.97: Shot/Revolver Reload (rsb_revolver_feed) -- 0 the speedloader, 1 a round at a time.
	// Server, not user: Index() is clearscope static with no player to read a user cvar against.
	clearscope static bool PerRound()
	{
		let cv = CVar.FindCVar('rsb_revolver_feed');
		return cv && cv.GetInt() != 0;
	}

'''


# BD21 -> BD22 sound names for the slug revolver. Each right-hand side was found in brutal22test6's
# own SNDINFO; each left-hand side was not. RELO1/RELO2 are in BD22 already and stay. "Tired" is NOT
# in BD22's SNDINFO either, but BD22's own AssaultShotgun/Axe/Grenades play it at StopSprintTired, so
# the parent's line is left exactly as BD22 itself writes it.
REV2_SND = {'"REVOFIR"': '"Revolver/Fire"', '"REVOHAM"': '"Revolver/Hammer"',
            '"REVOFIRpump"': '"Revolver/Hammer"',          # BD22's own Revolver PickupSound
            '"insertshell"': '"Revolver/Reload"', '"weapons/empty"': '"Weapon/Empty"',
            '"KICK"': '"Kick/Swing"'}
# BD21 -> BD22 class names (parsed: every `actor <name>` in brutal22test6)
REV2_CLS = {'"SubMachineGunSelected"': '"SMGSelected"'}

# The RSB contract, as rsr_break.zs states it and 1.96b's own patched Revolver.dec shows it. Reserve
# is Clip2 (BD21's Weapon.AmmoType1), the cylinder is RevolverAmmo, cap 6. The casing is BD22's
# SSGCaseSpawner -- 1.96b's choice for this very cylinder; BD21 fires RifleCAseSpawn inside its own
# insert loop, which is its quirk of ejecting as it loads, not an eject step.
REV2_RSB = '''	// RSR-BREAK: real VR reload, break-open / revolver (zscript/rsr/rsr_break.zs).
	// Not in VR, or with Real reload off, RSB_Start goes straight on into the gun's own reload.
	RSB_Start:
		"####" "#" 0 A_TakeInventory("RSB_Go", 1)
		"####" "#" 0 A_GiveInventory("RSB_Start", 1)
		"####" "#" 0 A_JumpIfInventory("RSB_Go", 1, "RSB_Open")
		Goto RSB_Stock
	RSB_Open:
		"####" "#" 0 A_TakeInventory("RSB_Go", 1)
		"####" "#" 0 A_TakeInventory("Reloading", 1)
		"####" "#" 0 A_GiveInventory("Pumping", 1)		// as BD21's own reload does
	RSB_Wait:		// the gun as the script shows it ("####" "#"); the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE)
		"####" "#" 0 A_GiveInventory("RSB_Tick", 1)
		"####" "#" 0 A_JumpIfInventory("RSB_EjectT", 1, "RSB_Eject")
		"####" "#" 0 A_JumpIfInventory("RSB_LoadT", 1, "RSB_Load")
		"####" "#" 0 A_JumpIfInventory("RSB_TopUpT", 1, "RSB_TopUp")
		"####" "#" 0 A_JumpIfInventory("RSB_Done", 1, "RSB_Done")
		Goto RSB_Wait
	RSB_Eject:		// one casing per spent round, as 1.96b ejects this cylinder
		"####" "#" 0 A_TakeInventory("RSB_EjectT", 1)
		"####" "#" 0 A_FireCustomMissile("SSGCaseSpawner",0,0,-10, -20)
		"####" "#" 0 A_JumpIfInventory("RSB_EjectT", 1, "RSB_Eject")
		Goto RSB_Wait
	RSB_Load:		// one shell into one chamber: BD21's own step of its InsertingShells loop
		"####" "#" 0 A_TakeInventory("RSB_LoadT", 1)
		"####" "#" 0 A_JumpIfInventory("RevolverAmmo", 6, "RSB_Wait")
		"####" "#" 0 A_JumpIfInventory("Clip2", 1, 1)
		Goto RSB_Wait
		"####" "#" 0 A_Giveinventory("RevolverAmmo", 1)
		"####" "#" 0 A_Takeinventory("Clip2", 1, TIF_NOTAKEINFINITE)
		Goto RSB_Wait
	RSB_TopUp:		// the speedloader: BD21's own loop to its cap of 6
		"####" "#" 0 A_TakeInventory("RSB_TopUpT", 1)
	RSB_TopUp1:
		"####" "#" 0 A_JumpIfInventory("RevolverAmmo", 6, "RSB_Wait")
		"####" "#" 0 A_JumpIfInventory("Clip2", 1, 1)
		Goto RSB_Wait
		"####" "#" 0 A_Giveinventory("RevolverAmmo", 1)
		"####" "#" 0 A_Takeinventory("Clip2", 1, TIF_NOTAKEINFINITE)
		Goto RSB_TopUp1
	RSB_Done:		// the player shut it by hand, so no close animation -- BD21 has no NeedToHammer
		REVO A 0 A_TakeInventory("RSB_Done", 1)
		Goto Ready
'''

REV2_ROSTER = '''
	// 1.97: the slug revolver (BD21 Revolver2) in place of BD22's Shotvolver, when the option is on
	override void CheckReplacement(ReplaceEvent e)
	{
		if (!e.Replacee) return;
		let mg = CVar.FindCVar('rsq_mg_replaces_mg42');
		if (mg && mg.GetInt() != 0 && e.Replacee.GetClassName() == 'MG42')
			e.Replacement = 'Machinegun';
		let sv = CVar.FindCVar('rsq_slug_replaces_shotvolver');
		if (sv && sv.GetInt() != 0 && e.Replacee.GetClassName() == 'Revolver')
			e.Replacement = 'Revolver2';
	}
'''


def rsb_rows(text, fname):
    """{case number: return expression} for one RSB_Guns switch"""
    m = re.search(r'\tclearscope static [\w<>]+ %s\(int i(?:, int k)?\)\n\t\{\n\t\tswitch \([^)]*\)\n\t\t\{\n(.*?)\n\t\t\}' % fname, text, re.S)
    if not m:
        raise SystemExit('rsb_guns.zs: no switch for %s' % fname)
    rows = {int(c): v for c, v in re.findall(r'case (\d+):\s*return ([^;]+);', m.group(1))}
    return m, rows


def rsb_fifth(text, fname):
    """the chamber row the speedloader patch overwrote: 5*mean - the four that survived, then checked
    against the cylinder's five-fold symmetry (the seats must sit at 72 deg on one radius)."""
    _, rows = rsb_rows(text, fname)
    V = lambda s: np.array([float(x) for x in s.strip('() ').split(',')])
    mean, four = V(rows[24]), [V(rows[k]) for k in (25, 26, 27, 28)]
    fifth = 5 * mean - sum(four)
    pts = np.array([fifth] + four)
    off = pts[:, 1:] - pts[:, 1:].mean(0)
    rad = np.linalg.norm(off, axis=1)
    ang = np.sort(np.degrees(np.arctan2(off[:, 1], off[:, 0])) % 360)
    gaps = np.diff(np.concatenate([ang, [ang[0] + 360]]))
    if np.ptp(rad) > 0.15 or abs(gaps - 72.0).max() > 2.0:
        raise SystemExit('rsb_guns.zs %s: recovered seat fails the cylinder (radii %s, gaps %s)'
                         % (fname, rad.round(3), gaps.round(2)))
    return fifth, dict(radius_cm=round(float(rad.mean()), 3), radius_spread_cm=round(float(np.ptp(rad)), 3),
                       gaps_deg=[round(float(g), 2) for g in gaps])


# F4 -- the gun bash on BD22's own kick.
#
# The owner's "quick melee move like you see in left 4 dead or a modern shooter" (2026-10-24). It is
# a BUTTON, not a gesture, and that is the point: a gun is a thing you hold still and point, so
# gesture detection on one starts far worse off than the axe did -- and BD22's own melee history is
# a list of that going wrong (speed alone made RAISING the axe a hit; rsvr_melee_up at 0.55 still cut
# on the upswing). A button has no false positives at all.
#
# BD22 already has the trigger: +zoom gives the Kicking token and DEFAULTWEAPON's Ready jumps to
# DoKick, from every weapon. So the bash is a branch at the top of DoKick, taken when a gun is held.
# BD22's own KickAttack still decides the result, so its gore rules are untouched; what changes is
# that no boot is drawn, the quake is lighter, and the impact gets one of the owner's RS_CombatFX
# effects at the contact point.
#
# Load order decides where each class can live: ZSCRIPT is compiled BEFORE DECORATE, so a ZScript
# class cannot inherit BD22's KickAttack (DECORATE), while DECORATE can name a ZScript class. Hence
# the attack actor is DECORATE and everything that has to read a cvar is ZScript.
FX = [
    # (id, RS_CombatFX folder, the owner's pick order). Scale is computed from the art: every effect
    # is drawn at RSH0's 96 px frame, which the owner set as the standard on 2026-10-24.
    ('RSS3', 'sparks'),
    ('RSU1', 'puffs'),
    ('RSU4', 'puffs'),
    ('RSU5', 'puffs'),
    ('RSH0', 'hitflash'),
]
FXROOT = 'E:/DOOMWork/RS_CombatFX'
RSVRW = 'E:/DOOMWork/RS_VR_Weapons/'

# F6 -- foley for the three reloads Brutal Doom has no sound for, because it never reloads them.
# REMA's bd22 set has none either, so these come from the wider RS_VR_Weapons library, which the
# owner allowed for exactly this (2026-10-24: "you cvan use rs vr weapons souinds for sthings we
# dont have sounds for"). wm/magdrop/large is described in its own SNDINFO as "a chaingun box, a
# rocket magazine, a canister" -- written for this case. The Unmaker keeps BD22's own Unmaker/Start
# and Unmaker/Stop, which are the same UNMSTA / UNMSTO lumps RS_VR_Weapons ships, so no file moves.
FOLEY = [
    ('rsr/drumout', 'sounds/chainguns/MGCHAIN.ogg', 'MG42 belt drum out (the V+ minigun box)'),
    ('rsr/drumin', 'sounds/chainguns/MGLOAD.ogg', 'MG42 belt drum home'),
    ('rsr/canout', 'sounds/launchers/RLCOUT.ogg', 'Flamethrower canister out (the V+ rocket canister)'),
    ('rsr/canin', 'sounds/launchers/RLCIN.ogg', 'Flamethrower canister home'),
    ('rsr/bigdrop1', 'sounds/magdrops/DSAOUNC1.ogg', 'a big magazine hitting the floor'),
    ('rsr/bigdrop2', 'sounds/magdrops/DSAOUNC2.ogg', ''),
    ('rsr/bigdrop3', 'sounds/magdrops/DSAOUNC3.ogg', ''),
]
FXSTD = 96.0

# RSH0's red is what the owner's headshot mod already uses, so ours is tintable (owner, 2026-10-24:
# "that color is for headshot mod i use seporatelui"). A luminance->colour ramp keeps the flash's
# shape and only moves its hue; 0 leaves the art alone.
TINTS = [('Original', ''), ('Blue', '[0,0,0]:[80,170,255]'), ('Green', '[0,0,0]:[90,255,120]'),
         ('Amber', '[0,0,0]:[255,190,70]'), ('White', '[0,0,0]:[255,255,255]')]


# F4 -- rows the page was missing. NOT a restructure: the owner's page keeps its name, its title and
# its order. (An earlier pass moved it onto tools/README.md's shared-page standard -- one runtime page
# called "RS VR Weapons" with each set's rows in an AddOptionMenu block, so two packs loaded together
# share one page. The owner never loads two packs together, so that bought nothing and cost him his
# menu. Reverted 2026-10-24; the README standard does not apply to this pack.)
#
# Each row below is an insertion after an existing line. Ranges on the two sliders are the code's own:
# rsr_assist is clamp(x, 0.5, 3.0) in rsr_assist.zs; rsvr_melee_swing is max(0.2, x) in melee.zs,
# which gives the floor but no ceiling, so 3.0 is a menu limit only -- the console can still go past.
ADDED_ROWS = [
    # (the line to insert after, the new row, the cvar it needs)
    ('\tOption "Grab ammo with", "rsr_grab_with", "RSR_GrabWith"\n',
     '\tOption "New magazine from", "rsr_pouch", "RSR_Pouch"\n', 'rsr_pouch'),
    ('\tOption "Shotgun Shells Per Insert", "rsr_shell_credit", "RSR_ShellCredit"\n',
     '\tSlider "Reload assist", "rsr_assist", 0.5, 3.0, 0.1\n', 'rsr_assist'),
    ('\tOption "Punch Switches Open", "rsq_punch_use", "OnOff"\n',
     '\tSlider "Melee swing strength", "rsvr_melee_swing", 0.2, 3.0, 0.1\n', 'rsvr_melee_swing'),
]


BASH_ZS = '''// bash.zs (1.97) -- the gun bash: BD22's own kick, with a gun in your hands instead of a boot.
// The trigger is BD22's: +zoom gives Kicking and DEFAULTWEAPON's DoKick runs. Our branch is taken
// only in VR, only with the option on, and only when what you are holding is not already a melee
// weapon -- so the axe, the Dragonslayer, the chainsaw and the fists keep BD22's kick exactly.
//
// RSQ_BashAsk is the pack's own handshake idiom (rsr_break.zs RSB_Call): Inventory.TryPickup runs
// SYNCHRONOUSLY inside A_GiveInventory, so a 0-tic DECORATE state can ask ZScript a question and
// branch on the answer in the same tic. The token is never kept.

// play, not the default data context: PlayerInt and InVR are both play functions
// ("Can't call play function PlayerInt from data context").
class RSQ_Bash abstract play
{
	// not a gun = BD22's kick, untouched
	static bool IsMelee(Name n)
	{
		return n == 'BrutalAxe' || n == 'DSweap' || n == 'Chain_saw' || n == 'Melee_Attacks';
	}

	static bool Wanted(PlayerPawn mo)
	{
		if (!mo || !mo.player || mo.health <= 0)
			return false;
		if (RSQ.PlayerInt(mo, 'rsq_bash', 1) == 0)
			return false;
		if (!RSVR_VRHand.InVR(mo))
			return false;			// desktop keeps the boot
		let w = mo.player.ReadyWeapon;
		return w && !IsMelee(w.GetClassName());
	}
}

class RSQ_BashGo : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }

class RSQ_BashAsk : Inventory
{
	Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET }
	override bool TryPickup(in out Actor toucher)
	{
		let mo = PlayerPawn(toucher);
		if (mo && RSQ_Bash.Wanted(mo))
			mo.GiveInventory('RSQ_BashGo', 1);
		return false;			// never kept
	}
}

// the impact: the effect the owner picked, at the point the bash landed. DECORATE's
// RSQ_BashAttack spawns this; this picks which of the five to draw, and tints RSH0.
class RSQ_BashFX : Actor
{
	Default { +NOINTERACTION; +NOBLOCKMAP; +DONTSPLASH; RenderStyle "Add"; Alpha 1.0; }

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		int n = RSQ.PlayerInt(PlayerPawn(target), 'rsq_bash_fx', %(deffx)d);
		static const Name FXC[] = { %(classes)s };
		if (n < 0 || n >= %(nfx)d)
			n = %(deffx)d;
		let a = Spawn(FXC[n], pos, ALLOW_REPLACE);
		if (a)
		{
			a.target = target;
			int t = RSQ.PlayerInt(PlayerPawn(target), 'rsq_bash_tint', 0);
			if (FXC[n] == 'RSQ_FX_RSH0' && t > 0 && t < %(ntint)d)
				a.A_SetTranslation(String.Format("RSQ_BashTint%%d", t));
		}
		Destroy();
	}
}

%(actors)s'''

BASH_DEC = '''// 1.97: the gun bash (tools/bd22_plus.py bash). BD22's own KickAttack decides the result --
// same damage, same DamageType Kick, so its gore, its obituary and its KickHasHit all still apply.
// The only addition is the impact effect at the point it landed. ZSCRIPT is compiled before
// DECORATE, so this has to live here to inherit KickAttack, and it names the ZScript FX actor.
ACTOR RSQ_BashAttack : KickAttack
{
	Obituary "$OBBD_KICK"
	States
	{
	Death:
	Crash:
		TNT1 A 0 A_SpawnItemEx("RSQ_BashFX", 0, 0, 0, 0, 0, 0, 0, SXF_NOCHECKPOSITION|SXF_TRANSFERPOINTERS)
		Goto Super::Death
	XDeath:
		TNT1 A 0 A_SpawnItemEx("RSQ_BashFX", 0, 0, 0, 0, 0, 0, 0, SXF_NOCHECKPOSITION|SXF_TRANSFERPOINTERS)
		Goto Super::XDeath
	}
}
'''

# the branch at the top of BD22's DoKick, and the bash itself. "####" "#" keeps the gun on screen:
# no A_GunFlash("KickFlash"), so no boot is drawn over the weapon you are holding.
BASH_STATES = '''	// 1.97: the gun bash (zscript/rsq/bash.zs). Not VR, option off, or a melee weapon in hand:
	// RSQ_BashGo is never given and BD22's own kick below runs untouched.
	RSQ_BashCheck:
		TNT1 A 0 A_TakeInventory("RSQ_BashGo", 1)
		TNT1 A 0 A_GiveInventory("RSQ_BashAsk", 1)
		TNT1 A 0 A_JumpIfInventory("RSQ_BashGo", 1, "RSQ_Bash")
		Goto RSQ_BashStock
	RSQ_Bash:
		"####" "#" 0 A_TakeInventory("RSQ_BashGo", 1)
		"####" "#" 0 A_PlaySound("Kick/Swing", 5)
		"####" "#" 0 A_WeaponReady(WRF_NOFIRE|WRF_NOSWITCH)
		"####" "#" 2 A_WeaponReady(WRF_NOFIRE|WRF_NOSWITCH)
		"####" "#" 0 A_Quake(1, 3, 0, 8, "")
		"####" "#" 0 A_JumpIfInventory("PowerStrength", 1, 2)
		"####" "#" 0 A_FireCustomMissile("RSQ_BashAttack", 0, 0, 0, -7)
		"####" "#" 0 A_Jump(256, 1)
		"####" "#" 0 A_FireCustomMissile("SuperKickAttack", 0, 0, 0, -7)
		"####" "#" 6 A_WeaponReady(WRF_NOFIRE|WRF_NOSWITCH)
		TNT1 A 0 A_TakeInventory("Kicking", 1)
		TNT1 A 0 A_JumpIfInventory("ExecuteDownedEnemy", 1, "DoExecution")
		TNT1 A 0 A_JumpIfInventory("GoFatality", 1, "Steady")
		Goto GoingToReady
	RSQ_BashStock:
'''


# F4 -- the pistol whip. Unlike the bash this IS a gesture, because a pistol is the one gun you
# genuinely swing: one hand, light, and nothing about aiming it looks like a sideways chop. It
# reuses melee.zs wholesale -- the sample history in the body frame, the speed and direction gates,
# the backswing rejection, the swept segment, the per-swing strike list -- by adding two kinds to
# it, which is all the axe and the Dragonslayer are.
#
# The segments are measured on each gun's mesh at ITS OWN ready frame, in model units, because that
# is what BladeIn/BladeOut are (the axe's are "BrutalAxe.md3 frame 5 = AXEG A"). The ready frame is
# not frame 0: it is whatever MODELDEF binds the gun's Ready sprite to -- BrutalPistol's is frame 3
# (2IST/PIST), the Revolver's frame 0 (REVO/2EVO). Revolver2 has no Model block of its own; it
# rides the Revolver's by sprite, so it shares the geometry.
WHIP = [
    # kind, classes, ready sprites, md3 frame, BladeIn, BladeOut, source
    ('PISTOL', ["'BrutalPistol'"], ['PIST', '2IST'], 3, (26.2, 0.0, -7.0), (44.2, 0.0, -0.2),
     'BrutalPistol.md3 frame 3'),
    ('REVOLVER', ["'Revolver'", "'Revolver2'"], ['REVO', '2EVO'], 0, (29.4, 0.1, -1.5), (50.2, 0.0, 2.4),
     'Revolver.md3 frame 0'),
]


# F4 -- the two-handed butt strike. The hard one, and it ships OFF.
#
# Two hands CANNOT be the gate: two hands on a rifle is how you hold a rifle, so it is the aiming
# posture, not an intent -- "two hands + motion" is precisely the false-positive case. And the axe's
# must-point-DOWN test is exactly wrong here, because a butt strike drives forward and up.
#
# What separates the blow is the BUTT LEADING. The gun pivots about the front hand, so the stock
# outruns the muzzle. Walking moves both ends alike (and melee.zs has already cancelled body motion
# by measuring in the pawn's own frame); raising or lowering the gun moves both ends together; only
# the pivot makes the butt the fast end. So the test is: both hands on the gun (the engine's own
# WF_TWOHANDSTABILIZED, via RSVR_VRHand.Steadied -- the same flag hands.zs draws the support hand
# from, so the damage and the hands the player sees can never disagree), the butt moving forward in
# the body frame, and the butt outrunning the muzzle.
#
# Ready frames were found the way bd22_mg.py found the Machinegun's: REMA's <gun>_wm.md3 is the gun
# at its ready pose, in its own coordinate frame, so the frame is the one with the lowest residual
# after a rigid fit -- all four land at 0.0000. (Several frames tie, because the idle pose repeats
# across animation frames; the frame is not unique but the geometry is.) Their Ready states say
# "####" and name no sprite, so the pose check gates on each gun's OWN idle sprite instead, taken
# from the MODELDEF lines that point at that frame -- never the shared PLAY / RIFF ones.
BUTT = [
    # kind, classes, own idle sprites, ready frame, BladeIn (forward), BladeOut (the butt), source
    ('RIFLEBUTT', ["'Rifle'"], ['RIFG', '2IFG', 'RI2G'], 3, (25.1, 0.1, 6.3), (2.5, 0.5, -1.0),
     'Rifle.md3 frame 3'),
    ('SGBUTT', ["'Shot_Gun'"], ['SHTN', '2HTN', 'SHTA'], 4, (23.7, 0.0, -5.4), (0.9, 0.0, -10.7),
     'ShotGun.md3 frame 4'),
    ('SSGBUTT', ["'SSG'"], ['VSSG', 'SHT2', 'VSHZ'], 1, (27.9, 0.1, -2.8), (15.3, 0.1, -7.0),
     'SSG.md3 frame 1'),
    ('ASGBUTT', ["'AssaultShotgun'"], ['USAS', '2SAS', 'A12P'], 4, (20.0, 0.0, -2.6), (-1.7, 0.0, -6.0),
     'AssaultShotgun.md3 frame 4'),
]


def butt():
    """F4: the two-handed butt strike, as four more kinds in melee.zs. Ships off."""
    p = OUT_SRC + 'zscript/rsvr/melee.zs'
    t = open(p).read()
    st = {}

    def once(old, new, what):
        if t.count(old) != 1:
            raise SystemExit('melee.zs: %s is not there exactly once' % what)
        return t.replace(old, new)

    kd0 = 5
    t = once('\tconst REVOLVER = 4;\n',
             '\tconst REVOLVER = 4;\n' + ''.join('\tconst %s = %d;\n' % (k[0], kd0 + i)
                                                 for i, k in enumerate(BUTT)), 'the whip constants')
    t = once('\tconst WHIP_SWING = 3.2;\t\t// 1.97: a pistol is lighter than the axe\n',
             '\tconst WHIP_SWING = 3.2;\t\t// 1.97: a pistol is lighter than the axe\n'
             '\tconst BUTT_SWING = 3.6;\t\t// 1.97: a long gun is heavy and swung short\n', 'WHIP_SWING')
    ins = ''.join('\t\tif (k == %s)\n\t\t\treturn (%.1f, %.1f, %.1f);\t// 1.97: %s, toward the muzzle\n'
                  % (kd, g[0], g[1], g[2], src) for kd, _, _, _, g, _, src in BUTT)
    outs = ''.join('\t\tif (k == %s)\n\t\t\treturn (%.1f, %.1f, %.1f);\t// 1.97: %s, the butt\n'
                   % (kd, g[0], g[1], g[2], src) for kd, _, _, _, _, g, src in BUTT)
    t = once('\t\tif (k == AXE)\n\t\t\treturn (44, 0, 26);\t\t// top of the axe head\n',
             '\t\tif (k == AXE)\n\t\t\treturn (44, 0, 26);\t\t// top of the axe head\n' + ins, 'BladeIn')
    t = once('\t\tif (k == AXE)\n\t\t\treturn (55, 0, 16);\t\t// the axe\'s cutting edge\n',
             '\t\tif (k == AXE)\n\t\t\treturn (55, 0, 16);\t\t// the axe\'s cutting edge\n' + outs, 'BladeOut')
    kinds = ''.join('\t\tif (%s)\n\t\t\treturn %s;\n' % (' || '.join('n == %s' % c for c in cls), kd)
                    for kd, cls, _, _, _, _, _ in BUTT)
    t = once("\t\tif (n == 'DSweap')\n\t\t\treturn SWORD;\n",
             "\t\tif (n == 'DSweap')\n\t\t\treturn SWORD;\n"
             "\t\tif (RSQ.PlayerInt(mo, 'rsq_butt', 0) != 0)\n\t\t{\n"
             + ''.join('\t' + l + '\n' for l in kinds.rstrip('\n').split('\n')) + '\t\t}\n', 'KindOf')
    decl = ''.join('\ttransient SpriteID s%s;\n' % s for _, _, sp, _, _, _, _ in BUTT for s in sp)
    init = ''.join("\t\ts%s = Actor.GetSpriteIndex('%s');\n" % (s, s) for _, _, sp, _, _, _, _ in BUTT for s in sp)
    pose = ''.join('\t\tif (k == %s)\n\t\t\treturn %s;\n' % (kd, ' || '.join('s == s%s' % s for s in sp))
                   for kd, _, sp, _, _, _, _ in BUTT)
    t = once('\ttransient SpriteID sAXEG;\n', '\ttransient SpriteID sAXEG;\n' + decl, 'the sprite fields')
    t = once("\t\tsAXEG = Actor.GetSpriteIndex('AXEG');\n",
             "\t\tsAXEG = Actor.GetSpriteIndex('AXEG');\n" + init, 'InitSprites')
    t = once('\t\tif (k == SWORD)\n\t\t\treturn s == sDSLA;\n',
             '\t\tif (k == SWORD)\n\t\t\treturn s == sDSLA;\n' + pose, 'ReadyPose')
    isbutt = ' || '.join('k == %s' % k[0] for k in BUTT)
    t = once('\t\tdouble thr = (k == AXE ? AXE_SWING : k == SWORD ? SWORD_SWING : WHIP_SWING) * vu / 35.\n',
             '\t\tbool isButt = %s;\n'
             '\t\tdouble thr = (k == AXE ? AXE_SWING : k == SWORD ? SWORD_SWING\n'
             '\t\t\t: isButt ? BUTT_SWING : WHIP_SWING) * vu / 35.\n' % isbutt, 'the swing threshold')
    # the muzzle end's own motion, so the butt can be asked to outrun it
    t = once('\tVector3 prevRel;\t\t// 1.11: the blade tip in the BODY\'s frame last tic (forward, left, up)\n',
             '\tVector3 prevRel;\t\t// 1.11: the blade tip in the BODY\'s frame last tic (forward, left, up)\n'
             '\tVector3 prevRelIn;\t\t// 1.97: and the inner end, so a butt strike can be asked to lead\n',
             'prevRel')
    t = once('\t\t\tprevRel = BodyFrame(mo, bout);\n\t\t\thavePrev = true;\n',
             '\t\t\tprevRel = BodyFrame(mo, bout);\n\t\t\tprevRelIn = BodyFrame(mo, bin);\n'
             '\t\t\thavePrev = true;\n', 'the first-sample init')
    t = once('\t\tVector3 rel = BodyFrame(mo, bout);\n\t\tVector3 vel = rel - prevRel;\n\t\tprevRel = rel;\n',
             '\t\tVector3 rel = BodyFrame(mo, bout);\n\t\tVector3 vel = rel - prevRel;\n\t\tprevRel = rel;\n'
             '\t\tVector3 relIn = BodyFrame(mo, bin);\n\t\tVector3 velIn = relIn - prevRelIn;\n'
             '\t\tprevRelIn = relIn;\n', 'the per-tic body-frame step')
    t = once('\t\tbool backswing = rise > -clamp(Cv(mo, \'rsvr_melee_down\', 0.25), 0.0, 0.9);\n',
             '\t\tbool backswing = rise > -clamp(Cv(mo, \'rsvr_melee_down\', 0.25), 0.0, 0.9);\n'
             '\t\tif (isButt)\n\t\t{\n'
             '\t\t\t// 1.97 the butt strike. Not the axe\'s must-point-DOWN test: this blow drives\n'
             '\t\t\t// forward and up. And two hands is NOT the gate -- two hands on a rifle is how\n'
             '\t\t\t// you hold a rifle. What separates it is the butt LEADING: the gun pivots about\n'
             '\t\t\t// the front hand, so the stock outruns the muzzle. Walking moves both ends alike\n'
             '\t\t\t// (and the body frame has already cancelled it) and raising the gun moves both;\n'
             '\t\t\t// only the pivot does this.\n'
             '\t\t\tdouble fwd = speed > 0 ? vel.x / speed : 0;\n'
             '\t\t\tbackswing = !RSVR_VRHand.Steadied(mo)\n'
             '\t\t\t\t|| fwd < clamp(Cv(mo, \'rsvr_butt_fwd\', 0.5), 0.0, 1.0)\n'
             '\t\t\t\t|| velIn.Length() * clamp(Cv(mo, \'rsvr_butt_lead\', 1.3), 1.0, 4.0) > speed;\n'
             '\t\t}\n', 'the backswing test')
    t = once("\t\t\tLaunch(mo, mo.CountInv('PowerStrength') > 0 ? 'MeleeStrike1Berserked' : 'MeleeStrikeNormal', p, dir);\n"
             "\t\t\tif (power >= 2.0)\n\t\t\t\tLaunch(mo, 'MeleeStrikeNormal', p, dir);\n",
             "\t\t\tif (k == PISTOL || k == REVOLVER)\n\t\t\t{\n"
             "\t\t\t\tLaunch(mo, mo.CountInv('PowerStrength') > 0 ? 'MeleeStrike1Berserked' : 'MeleeStrikeNormal', p, dir);\n"
             "\t\t\t\tif (power >= 2.0)\n\t\t\t\t\tLaunch(mo, 'MeleeStrikeNormal', p, dir);\n\t\t\t}\n"
             "\t\t\telse\n\t\t\t{\n"
             "\t\t\t\t// 1.97 the butt strike: BD22's own kick, which is what a stock to the face is\n"
             "\t\t\t\t// and what the gun bash already lands.\n"
             "\t\t\t\tLaunch(mo, mo.CountInv('PowerStrength') > 0 ? 'SuperKickAttack' : 'KickAttack', p, dir);\n"
             "\t\t\t}\n", 'the strike result')
    open(p, 'w').write(t)
    with open(OUT_SRC + 'CVARINFO.rsq', 'a') as f:
        f.write('\n// 1.97: the two-handed butt strike. OFF by default: of the three melee moves this\n'
                '// is the one most likely to misfire, because two hands on a rifle is the aiming\n'
                '// posture, so it is the player\'s choice to turn on.\n'
                'user int rsq_butt = 0;\n'
                'user float rsvr_butt_fwd = 0.5;\t\t// of the butt\'s speed that must point forward\n'
                'user float rsvr_butt_lead = 1.3;\t// how much faster the butt must be than the muzzle\n')
    mp = OUT_SRC + 'MENUDEF.rsq'
    mt = open(mp).read()
    a = '\tOption "Gun Bash (kick key)", "rsq_bash", "OnOff"\n'
    if mt.count(a) != 1:
        raise SystemExit('MENUDEF.rsq: the gun bash row is not there once')
    open(mp, 'w').write(mt.replace(a, a + '\tOption "Two-Handed Butt Strike", "rsq_butt", "OnOff"\n'))
    st['kinds'] = {kd: dict(classes=[c.strip("'") for c in cls], sprites=sp, ready_frame=fr,
                            blade_in=list(bi), blade_out=list(bo), source=src)
                   for kd, cls, sp, fr, bi, bo, src in BUTT}
    st['gate'] = 'Steadied (WF_TWOHANDSTABILIZED) + butt forward >= rsvr_butt_fwd + butt outruns the muzzle by rsvr_butt_lead'
    st['default'] = 'rsq_butt = 0 (off)'
    json.dump(st, open(OUT + 'butt_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py butt\n')
    print(json.dumps(st, indent=1))


def whip():
    """F4: the pistol whip, as two more kinds in 1.96b's own melee.zs."""
    p = OUT_SRC + 'zscript/rsvr/melee.zs'
    t = open(p).read()
    st = {}

    def once(old, new, what):
        if t.count(old) != 1:
            raise SystemExit('melee.zs: %s is not there exactly once' % what)
        return t.replace(old, new)

    # the kinds, and how hard the swing has to be
    t = once('\tconst AXE = 1;\n\tconst SWORD = 2;\n',
             '\tconst AXE = 1;\n\tconst SWORD = 2;\n\tconst PISTOL = 3;\t\t// 1.97: the pistol whip\n'
             '\tconst REVOLVER = 4;\n', 'the kind constants')
    t = once('\tconst SWORD_SWING = 3.5;\n',
             '\tconst SWORD_SWING = 3.5;\n\tconst WHIP_SWING = 3.2;\t\t// 1.97: a pistol is lighter than the axe\n',
             'SWORD_SWING')
    # the striking segment, measured per gun
    ins = ''.join('\t\tif (k == %s)\n\t\t\treturn (%.1f, %.1f, %.1f);\t// 1.97: %s, just forward of the hand\n'
                  % (kd, g[0], g[1], g[2], src) for kd, _, _, _, g, _, src in WHIP)
    outs = ''.join('\t\tif (k == %s)\n\t\t\treturn (%.1f, %.1f, %.1f);\t// 1.97: %s, the muzzle\n'
                   % (kd, g[0], g[1], g[2], src) for kd, _, _, _, _, g, src in WHIP)
    t = once('\t\tif (k == AXE)\n\t\t\treturn (44, 0, 26);\t\t// top of the axe head\n',
             '\t\tif (k == AXE)\n\t\t\treturn (44, 0, 26);\t\t// top of the axe head\n' + ins, 'BladeIn')
    t = once('\t\tif (k == AXE)\n\t\t\treturn (55, 0, 16);\t\t// the axe\'s cutting edge\n',
             '\t\tif (k == AXE)\n\t\t\treturn (55, 0, 16);\t\t// the axe\'s cutting edge\n' + outs, 'BladeOut')
    # which weapon is which kind
    kinds = ''.join('\t\tif (%s)\n\t\t\treturn %s;\n' % (' || '.join('n == %s' % c for c in cls), kd)
                    for kd, cls, _, _, _, _, _ in WHIP)
    t = once("\t\tif (n == 'DSweap')\n\t\t\treturn SWORD;\n\t\treturn 0;\n",
             "\t\tif (n == 'DSweap')\n\t\t\treturn SWORD;\n" + kinds + '\t\treturn 0;\n', 'KindOf')
    # the ready pose: the gun is where the model shows it
    decl = ''.join('\ttransient SpriteID s%s;\n' % s for _, _, sp, _, _, _, _ in WHIP for s in sp)
    init = ''.join("\t\ts%s = Actor.GetSpriteIndex('%s');\n" % (s, s) for _, _, sp, _, _, _, _ in WHIP for s in sp)
    pose = ''.join('\t\tif (k == %s)\n\t\t\treturn %s;\n' % (kd, ' || '.join('s == s%s' % s for s in sp))
                   for kd, _, sp, _, _, _, _ in WHIP)
    t = once('\ttransient SpriteID sAXEG;\n', '\ttransient SpriteID sAXEG;\n' + decl, 'the sprite fields')
    t = once("\t\tsAXEG = Actor.GetSpriteIndex('AXEG');\n",
             "\t\tsAXEG = Actor.GetSpriteIndex('AXEG');\n" + init, 'InitSprites')
    t = once('\t\tif (k == SWORD)\n\t\t\treturn s == sDSLA;\n',
             '\t\tif (k == SWORD)\n\t\t\treturn s == sDSLA;\n' + pose, 'ReadyPose')
    # the threshold
    t = once('\t\tdouble thr = (k == AXE ? AXE_SWING : SWORD_SWING) * vu / 35.\n',
             '\t\tdouble thr = (k == AXE ? AXE_SWING : k == SWORD ? SWORD_SWING : WHIP_SWING) * vu / 35.\n',
             'the swing threshold')
    # the result: BD22's own punch, which is what the pack's fists already land
    t = once("\t\telse\n\t\t{\n\t\t\tLaunch(mo, 'DSAttack', p, dir);\n\t\t\tLaunch(mo, 'DSAttack2', p, dir);\n\t\t}\n",
             "\t\telse if (k == SWORD)\n\t\t{\n\t\t\tLaunch(mo, 'DSAttack', p, dir);\n"
             "\t\t\tLaunch(mo, 'DSAttack2', p, dir);\n\t\t}\n"
             "\t\telse\n\t\t{\n"
             "\t\t\t// 1.97 the pistol whip: BD22's own punch, which is what this pack's fists\n"
             "\t\t\t// already land (zscript/rsq/fists.zs), so its gore decides the result.\n"
             "\t\t\tLaunch(mo, mo.CountInv('PowerStrength') > 0 ? 'MeleeStrike1Berserked' : 'MeleeStrikeNormal', p, dir);\n"
             "\t\t\tif (power >= 2.0)\n"
             "\t\t\t\tLaunch(mo, 'MeleeStrikeNormal', p, dir);\n\t\t}\n", 'the strike result')
    open(p, 'w').write(t)
    st['kinds'] = {kd: dict(classes=[c.strip("'") for c in cls], sprites=sp, frame=fr,
                            blade_in=list(bi), blade_out=list(bo), source=src)
                   for kd, cls, sp, fr, bi, bo, src in WHIP}
    st['result'] = "MeleeStrikeNormal / MeleeStrike1Berserked, as fists.zs lands"
    json.dump(st, open(OUT + 'whip_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py whip\n')
    print(json.dumps(st, indent=1))


README = '''RS_Brutal22WeaponsQ -- bd22q %(ver)s
=====================================

VR hands, hand-driven reloading and VR melee for Brutal Doom v22, on stock QuestZDoom 17.3.
An ADDON: it needs Brutal Doom loaded, it replaces none of its guns, and with its options off it
behaves as Brutal Doom shipped.


LOAD ORDER
----------
    doom2.wad  ->  brutal22test6.pk3  ->  BD_VoxelPack.pk3  ->  %(pk3)s

Doom 2, not Freedoom: BD_VoxelPack's voxeldef names Doom 2's own sprites and Freedoom fails on it.
No engine changes. Stock QuestZDoom 17.3.


WHAT IT ADDS
------------
Hands on every Brutal Doom gun, and reloading you do WITH YOUR HANDS instead of a keypress:

  magazine    %(nrsr)d guns -- Rifle, Pistol, SMG, MP40, Assault Shotgun, Railgun, Plasma,
              Sniper, Rocket Launcher, and (new in 1.97) the MG42's belt drum, the
              Flamethrower's canister and the Unmaker's skull
  pump        the Shotgun
  break-open  the SSG, the Grenade Launcher, the Shotvolver, and the slug revolver

Take the magazine out with your off hand, bring a fresh one up, push it home. Break guns swing
open, take a round at a time or a speedloader, and a flick of the wrist shuts them.

NEW IN 1.97
  * The MG42 belt drum, the Flamethrower canister and the Unmaker skull now reload. Brutal Doom
    never reloads those three; the parts were carved out of their own meshes to do it.
  * The BD21 MACHINEGUN (M249 with an over-under launcher), on slot 4. Its launcher is loaded by
    hand. Menu row: "Machinegun replaces MG42".
  * The BD21 SLUG REVOLVER, on slot 2 beside the Shotvolver. Menu row: "Slug revolver replaces
    Shotvolver".
  * Both revolvers take a SPEEDLOADER or a ROUND AT A TIME, your choice: "Shot/Revolver Reload".
  * VR MELEE with a gun in your hands -- see below.


MELEE
-----
  GUN BASH          your kick key, with a gun in your hands, bashes with the gun instead of
                    kicking. Brutal Doom's own kick damage; the boot is simply not drawn.
                    Pick its impact effect and its colour in the menu.
  PISTOL WHIP       swing a pistol or a revolver and it hits what it passes through.
  BUTT STRIKE       drive the stock of a rifle or shotgun forward with both hands on it.
                    OFF by default -- two hands on a rifle is also how you aim one, so this is
                    the one most likely to go off when you did not mean it. Turn it on and judge.
  FISTS             a real punch with either hand, and punching a switch works it.
  AXE / DRAGONSLAYER  swing them; two hands and the edge leading bite harder.

Out of VR, or with these turned off, Brutal Doom's own melee is untouched.


OPTIONS
-------
Options -> BD22 VR Weapons. %(nmenu)d rows, including Reloading (VR or Stock), what grabs the
ammo, where a new magazine comes from, reload assist, the per-gun scopes, the dual-wield and
voxel pages, and "Reload: tuning and debug" for the capture zones and a step-by-step print.

Every option defaults to how Brutal Doom behaves, or to the gentler setting, except the VR hands
and reloading themselves. Turn Reloading to "Stock (BD22)" and the guns reload as they always did.


CREDITS
-------
Brutal Doom v22 is Sergeant_Mark_IV's; this pack is an addon to it and ships none of its guns.
The hands and much of the art are Ermac's (Rusted Legacy, MIT -- see
models/rsq/LICENSE_RustedLegacy_MIT.txt). The engine this targets is Emawind's QuestZDoom.
Reload foley the mod itself has none of comes from RS_VR_Weapons.
The BD21 Machinegun and slug revolver are Brutal Doom 21's, brought forward.


KNOWN GAPS
----------
  * A dropped partial drum costs the reserve nothing.
  * The Shotvolver's cylinder has five chambers and a capacity of six; that is how Brutal Doom
    counts it, and loading a round at a time inherits it.
  * The Machinegun's HUD is its model: its sprite lumps are placeholders.

Built from the RSQ Weapon Depot. Every number in it is measured off a mesh or parsed out of the
parent mod -- sets/bd22q_1.97/PROVENANCE.txt says what came from where and how to rebuild it.
'''


# F5 -- per-gun recoil, from REMA's WMSHEET and RS_Ballistics' recoil profiles.
#
# card -> BD22 actor. The sheet keys guns as BD_Pistol, BD22's actor is BrutalPistol, and nothing
# in either file links them. Each row below was checked twice: the class exists in brutal22test6
# (bar Machinegun, which this pack adds), and the card's REMA *_wm.md3 has the same vertex count as
# that class's own mesh -- 23 of 25 confirmed that way, and Chain_saw / Minigun by block name,
# their MODELDEF spelling differing in case only (ZScript names are case-insensitive).
CARD2CLS = [
    ('BD_Pistol', 'BrutalPistol'), ('BD_Revolver', 'Revolver'), ('BD_Shotgun', 'Shot_Gun'),
    ('BD_SSG', 'SSG'), ('BD_MP40', 'MP40'), ('BD_M79', 'GrenadeLauncher'),
    ('BD_FlameCannon', 'FlameCannon'), ('BD_Hellish', 'HellishMissileLauncher'),
    ('BD_Buzzsaw', 'MG42'), ('BD_Axe', 'BrutalAxe'), ('BD_Dragonslayer', 'DSweap'),
    ('BD_Chainsaw', 'Chain_saw'), ('BD_AssaultShotgun', 'AssaultShotgun'),
    ('BD_BFG', 'BIG_FUCKING_GUN'), ('BD_BFG10k', 'BFG10k'), ('BD_SMG', 'BrutalSMG'),
    ('BD_Flamethrower', 'Flamethrower2'), ('BD_Grenade', 'HandGrenades'),
    ('BD_Machinegun', 'Machinegun'), ('BD_Minigun', 'Minigun'), ('BD_Plasma', 'Plasma_Gun'),
    ('BD_RPG', 'Rocket_Launcher'), ('BD_Railgun', 'RailGun'), ('BD_Rifle', 'Rifle'),
    ('BD_Unmaker', 'Unmaker'),
]

RECOIL_ZS = '''// recoil.zs (1.97, F5) -- GENERATED by tools/bd22_plus.py recoil. Do not edit by hand.
//
// THE PACK IS RAISED TO ZSCRIPT 4.14 FOR THIS (ZSCRIPT.rsvr, by this stage). 1.96b declared 4.10,
// and a version gate hides anything the engine added later: WorldHitscanPreFired arrived with
// PR #2432 (2024-11-20), so at 4.10 it is invisible and overriding it is "Attempt to override
// non-existent virtual function". A `version` line in an INCLUDED file is not allowed -- the
// engine answers "Unexpected 'version'" -- so it has to be the root lump, for the whole pack.
// qzd17.3 is GZDoom 4.14.3, so 4.14 is what it actually offers, and the pack compiles clean at it.
//
// Per-gun recoil for BD22 on stock QuestZDoom 17.3. The numbers are REMA's: every gun's
// `recoilprofile` on WMSHEET.bd22, resolved against RS_Ballistics' own recoil blocks, where they
// were computed from free-recoil arithmetic rather than typed -- bullet weight, muzzle velocity,
// powder charge and the loaded gun's weight. An MG42 and a Kar98k fire the same cartridge out of a
// 25 lb gun and a 9 lb gun, and the numbers say so.
//
// IN VR THIS IS THE GUN MOVING IN YOUR HANDS, NOT YOUR AIM MOVING.
// Where a shot goes is decided by where the controller points; psp.x and psp.y rotate the MODEL.
// So `climb` and `drift` are carried here as what the gun visibly does, and `bloom` and `brace` --
// which are about where the rounds land and how a stance steadies them -- have nothing to act on
// and are not carried. Nothing here touches the camera; that is the standing rule.
//
// THE CHANNEL. hw_weapon.cpp renders the held model at
//     rotation + (psp.x / 4, (32 - psp.y) / -4, 0)
// so yaw degrees = psp.x / 4 and pitch degrees = (32 - psp.y) / 4, and there is NO ROLL. Every
// profile's `view` line is `back, rise, roll, tics`; only `rise` and `tics` can be honoured, so the
// roll and the backward shove are dropped rather than faked.
//
// WHY IT IS ADDITIVE AND REWRITTEN EVERY TIC. A_WeaponReady assigns psp.x = 0 and
// psp.y = WEAPONTOP on every tic it runs, A_Raise and A_Lower sweep the same channel through a
// weapon switch, and BD22's own Offset() lands here too. So the kick is held as our own state and
// ADDED after the weapon has had its say -- WorldTick is the last writer before the frame. Never
// assigned, or a weapon switch fights it.
//
// THE SHOT. This pack is an addon: BD22 owns the weapon code, so the shot is detected rather than
// known. WorldHitscanPreFired carries the shooter and the damage; a spawned missile whose target is
// the player covers the projectile guns.

class RSQ_RecoilDef
{
	// per shot
	double rise;		// view: degrees the muzzle snaps up
	int    riseTics;	// view: over how many tics
	double climb;		// degrees of standing climb a shot adds
	double drift;		// degrees of yaw walk
	int    driftPeriod;	// ... reversing every this many shots (2 never drifts)
	// recovery
	double recover;		// degrees a second back toward rest
	int    delay;		// after this many tics without a shot
	double maxPitch, maxYaw;
}

class RSQ_Recoil : EventHandler
{
	// rsq_recoil: 0 off, 1 on. Its own row, not the ballistics dial: this costs one float a tic,
	// the effects cost a frame budget, and they are not the same decision.
	static bool On(PlayerPawn mo)
	{
		return RSQ.PlayerInt(mo, 'rsq_recoil', 1) != 0;
	}

	Array<String> defCls;
	Array<RSQ_RecoilDef> defs;

	double pitch[MAXPLAYERS];
	double yaw[MAXPLAYERS];
	int    shots[MAXPLAYERS];
	int    idle[MAXPLAYERS];
	int    rising[MAXPLAYERS];
	double riseLeft[MAXPLAYERS];

	override void OnRegister()
	{
%(table)s	}

	RSQ_RecoilDef Find(Name cls)
	{
		String s = cls;
		for (int i = 0; i < defCls.Size(); i++)
			if (defCls[i] ~== s)
				return defs[i];
		return null;
	}

	void Kick(PlayerPawn mo)
	{
		if (!mo || !mo.player || !On(mo))
			return;
		let w = mo.player.ReadyWeapon;
		if (!w)
			return;
		let d = Find(w.GetClassName());
		if (!d)
			return;
		int n = mo.PlayerNumber();
		shots[n]++;
		idle[n] = 0;
		// the snap: spread over the profile's own tics so it is a push, not a teleport
		rising[n] = max(1, d.riseTics);
		riseLeft[n] = d.rise;
		// the climb: what walks up under sustained fire, capped by the profile
		pitch[n] = min(pitch[n] + d.climb, d.maxPitch);
		if (d.driftPeriod > 2)
		{
			// a fixed walk by shot number, no RNG -- the same every time, as REMA has it
			double s = ((shots[n] / d.driftPeriod) %% 2 == 0) ? 1.0 : -1.0;
			yaw[n] = clamp(yaw[n] + d.drift * s, -d.maxYaw, d.maxYaw);
		}
	}

	// bool, not void: the engine declares these as `virtual bool ... { return false; }` and the
	// return value is whether to BLOCK the shot. We only watch, so always false.
	override bool WorldHitscanPreFired(WorldEvent e)
	{
		Kick(PlayerPawn(e.Thing));
		return false;
	}

	override bool WorldRailgunPreFired(WorldEvent e)
	{
		Kick(PlayerPawn(e.Thing));
		return false;
	}

	override void WorldThingSpawned(WorldEvent e)
	{
		// the projectile guns: a missile the player just launched
		if (e.Thing && e.Thing.bMissile)
			Kick(PlayerPawn(e.Thing.target));
	}

	override void WorldTick()
	{
		for (int i = 0; i < MAXPLAYERS; i++)
		{
			if (!playeringame[i])
				continue;
			let mo = PlayerPawn(players[i].mo);
			if (!mo || !mo.player)
				continue;
			let w = mo.player.ReadyWeapon;
			RSQ_RecoilDef d = w ? Find(w.GetClassName()) : null;
			if (!d || !On(mo))
			{
				pitch[i] = 0; yaw[i] = 0; riseLeft[i] = 0; rising[i] = 0;
				continue;		// and nothing is written, so the channel is the weapon's own
			}
			// the snap pays itself out over its tics, then recovery takes over
			double add = 0;
			if (rising[i] > 0)
			{
				add = riseLeft[i] / rising[i];
				riseLeft[i] -= add;
				rising[i]--;
				pitch[i] = min(pitch[i] + add, d.maxPitch + d.rise);
			}
			else
			{
				idle[i]++;
				if (idle[i] > d.delay)
				{
					double back = d.recover / 35.0;
					pitch[i] = pitch[i] > 0 ? max(0.0, pitch[i] - back) : min(0.0, pitch[i] + back);
					yaw[i]   = yaw[i]   > 0 ? max(0.0, yaw[i]   - back) : min(0.0, yaw[i]   + back);
					if (pitch[i] == 0 && yaw[i] == 0)
						shots[i] = 0;
				}
			}
			let psp = mo.player.FindPSprite(PSP_WEAPON);
			if (!psp)
				continue;
			// ADD, never assign: the weapon has already written this channel this tic
			psp.x += yaw[i] * 4.0;
			psp.y -= pitch[i] * 4.0;
		}
	}
}
'''


ROUNDS_ZS = '''// rounds.zs (1.97, F5) -- GENERATED by tools/bd22_plus.py impacts. Do not edit by hand.
//
// How hard each gun's round hits a WALL, so a 9mm and a 12-gauge do not throw the same chips.
// Derived, not typed: RS_Ballistics' `ballistics <roundprofile>` blocks carry the round's mass in
// grains and its speed, and impact energy goes as mass x speed^2. Raw energy spans more than ten
// to one across these guns, which would be absurd as a particle count, so the scale is the CUBE
// ROOT of the energy ratio against the 9mm -- 9mm 1.00, buckshot 1.66, 7.62 2.21 -- and clamped.
//
// A gun whose round has no ballistics block (rockets, plasma, the BFG, the Unmaker) gets 1.0: they
// are not cartridges and their own explosions already carry the hit.
//
// RS_Ballistics' real impact blocks could not come: they name bursts, and a burst resolves a
// PARTICLEDEFS particle, which is a REMA RENDERER feature (hw_gpuparticlebuffer, hw_meshparticles)
// that stock QuestZDoom does not have. What crosses is the judgement, not the particle system.

class RSQ_Rounds abstract
{
	static double Scale(Name cls)
	{
		switch (cls)
		{
%(rows)s		}
		return 1.0;
	}
}
'''


def impacts():
    """F5: per-gun impact weight, and the Stock / Low / Max dial on the pack's own effects."""
    if 'RSQ_Rounds' in open(OUT_SRC + 'ZSCRIPT.rsvr').read():
        raise SystemExit('impacts: this tree already has it -- re-run apply() first')
    sheet = open(RSVRW + 'bd22/WMSHEET.bd22', encoding='latin-1').read()
    guns, cur = {}, None
    for ln in sheet.splitlines():
        s = ln.split('#')[0].strip()
        m = re.match(r'gun\s+"([^"]+)"', s)
        if m:
            cur = m.group(1); guns[cur] = {}; continue
        if cur:
            m = re.match(r'(\w+)\s*=\s*(.+)$', s)
            if m:
                guns[cur][m.group(1)] = m.group(2).strip().strip('"')
    defs = open('E:/DOOMWork/RS_Ballistics/RSBDEFS.txt', encoding='latin-1').read()
    # NB the header line often carries a trailing comment -- `recoil pistol_9mm   # the Pistolet`.
    # Matching \s*\n after the name silently found almost nothing and every cartridge lookup fell
    # through to the default. [^\n]* is what makes the block headers parse.
    ball = {}
    for m in re.finditer(r'(?ms)^ballistics (\S+)[^\n]*\n(.*?)^end', defs):
        d = {}
        for k, v in re.findall(r'(\w+)\s*=\s*([^\n#]+)', m.group(2)):
            d[k] = v.strip()
        ball[m.group(1)] = d

    def energy(p):
        b = ball.get(p)
        if not b or 'speed' not in b or 'roundmass' not in b:
            return None
        return float(b['roundmass']) * float(b['speed']) ** 2

    base = energy('pistol_9mm')
    if not base:
        raise SystemExit('impacts: no ballistics block for pistol_9mm to normalise against')
    # a gun's roundprofile is not always a cartridge name -- chaingun_556, machinegun_762 and
    # smg_9mm have no ballistics block of their own. Their RECOIL profile names the cartridge
    # (`cartridge = rifle_556`), which is the link RS_Ballistics itself uses, so fall back to it.
    rec = {}
    for m in re.finditer(r'(?ms)^recoil (\S+)[^\n]*\n(.*?)^end', defs):
        c = re.search(r'cartridge\s*=\s*(\S+)', m.group(2))
        if c:
            rec[m.group(1)] = c.group(1).strip()
    rows, log = '', {}
    for card, cls in CARD2CLS:
        g = guns.get(card, {})
        p = g.get('roundprofile')
        e = energy(p) if p else None
        src = p
        if e is None:
            alt = rec.get(g.get('recoilprofile', ''))
            if alt:
                e = energy(alt)
                src = '%s via %s' % (alt, g.get('recoilprofile'))
        if e is None:
            continue
        p = src
        k = round(min(2.5, max(0.6, (e / base) ** (1.0 / 3.0))), 3)
        rows += "\t\tcase '%s':\treturn %.3f;\t// %s\n" % (cls, k, p)
        log[cls] = dict(round=p, scale=k)
    open(OUT_SRC + 'zscript/rsq/rounds.zs', 'w').write(ROUNDS_ZS % dict(rows=rows))
    zp = OUT_SRC + 'ZSCRIPT.rsvr'
    zt = open(zp).read()
    a = '#include "zscript/rsq/recoil.zs"\n'
    if zt.count(a) != 1:
        raise SystemExit('ZSCRIPT.rsvr: the recoil include is not there once (recoil must run first)')
    open(zp, 'w').write(zt.replace(a, a + '#include "zscript/rsq/rounds.zs"\n'))

    # the dial, on the pack's own effects
    p = OUT_SRC + 'zscript/rsq/ballistics.zs'
    t = open(p).read()

    def once(old, new, what):
        if t.count(old) != 1:
            raise SystemExit('ballistics.zs: %s is not there exactly once' % what)
        return t.replace(old, new)

    t = once('\tconst MAX_TRACERS = 24;\n\tconst MAX_DEBRIS = 64;\n',
             '\t// 1.97 F5: these are the LOW budget, which is what 1.96b shipped. Max doubles them.\n'
             '\tconst MAX_TRACERS = 24;\n\tconst MAX_DEBRIS = 64;\n'
             '\tstatic int CapTracers() { return FxLevel() >= 2 ? MAX_TRACERS * 2 : MAX_TRACERS; }\n'
             '\tstatic int CapDebris()  { return FxLevel() >= 2 ? MAX_DEBRIS * 2 : MAX_DEBRIS; }\n',
             'the caps')
    t = once("\tstatic bool On()\n\t{\n\t\tlet cv = CVar.FindCVar('rsq_ballistics');\n"
             "\t\treturn cv && cv.GetInt() != 0;\n\t}\n",
             "\t// 1.97 F5: 0 Stock (BD22's own, nothing here runs), 1 Low, 2 Max.\n"
             "\t// NOT named Level(): that shadows ZScript's global Level inside this class and\n"
             "\t// every Level.SpawnParticle below stops compiling.\n"
             "\tstatic int FxLevel()\n\t{\n\t\tlet cv = CVar.FindCVar('rsq_ballistics');\n"
             "\t\treturn cv ? clamp(cv.GetInt(), 0, 2) : 0;\n\t}\n\n"
             "\tstatic bool On()\n\t{\n\t\treturn FxLevel() > 0;\n\t}\n",
             'On()')
    t = once('\t\tif (liveTracers >= MAX_TRACERS || a.GetMissileDamage(0, 1) <= 0)\n',
             '\t\tif (liveTracers >= CapTracers() || a.GetMissileDamage(0, 1) <= 0)\n',
             'the tracer cap test')
    t = once('\t\tfor (int i = 0; i < chips && liveDebris < MAX_DEBRIS; i++)\n',
             '\t\tfor (int i = 0; i < chips && liveDebris < CapDebris(); i++)\n',
             'the debris cap test')
    # Spall is where the counts are chosen, but it is handed only the surface -- it has no shooter
    # and no `tracer` in scope (an earlier attempt put the lookup here and the engine answered
    # "Unknown identifier 'Tracer'"). So the weight is computed at the CALL SITE, in Impact, which
    # does have the projectile, and passed in.
    t = once('\tvoid Spall(Vector3 at, Vector3 n, Name mat)\n',
             '\tvoid Spall(Vector3 at, Vector3 n, Name mat, double k = 1.0)\n', "Spall's signature")
    t = once('\t\tSpall(t.HitLocation + n * 2, n, surf.Of(t.HitTexture, flat));\n',
             '\t\t// 1.97 F5: the level dial, and the weight of the round that got here. Spall\'s\n'
             '\t\t// counts are per SURFACE; this is what makes a 12-gauge differ from a 9mm on the\n'
             '\t\t// same wall. Max is 1.8x Low, and Low is what 1.96b shipped.\n'
             '\t\tName gun = \'None\';\n'
             '\t\tif (tracer && tracer.target && tracer.target.player && tracer.target.player.ReadyWeapon)\n'
             '\t\t\tgun = tracer.target.player.ReadyWeapon.GetClassName();\n'
             '\t\tSpall(t.HitLocation + n * 2, n, surf.Of(t.HitTexture, flat),\n'
             '\t\t\t(FxLevel() >= 2 ? 1.8 : 1.0) * RSQ_Rounds.Scale(gun));\n',
             'the Spall call')
    t = once("\t\t\tc = Color(255, 130, 30); dust = 10; chips = 0; sparks = 4; break;\n\t\t}\n",
             "\t\t\tc = Color(255, 130, 30); dust = 10; chips = 0; sparks = 4; break;\n\t\t}\n\n"
             "\t\tdust = int(dust * k); chips = int(chips * k); sparks = int(sparks * k);\n",
             'the surface switch end')
    open(p, 'w').write(t)

    # the cvar becomes a three-way
    cp = OUT_SRC + 'CVARINFO.rsq'
    ct = open(cp).read()
    old = 'server bool rsq_ballistics = false;'
    if ct.count(old) != 1:
        raise SystemExit('CVARINFO.rsq: the ballistics bool is not there once')
    open(cp, 'w').write(ct.replace(
        old, 'server int rsq_ballistics = 0;\t// 1.97 F5: 0 Stock (BD22), 1 Low, 2 Max'))
    mp = OUT_SRC + 'MENUDEF.rsq'
    mt = open(mp).read()
    old = 'OptionValue "RSQ_Ballistics"\n{\n\t0, "Stock (BD22)"\n\t1, "Enhanced"\n}'
    if mt.count(old) != 1:
        raise SystemExit('MENUDEF.rsq: the Ballistics OptionValue is not as expected')
    open(mp, 'w').write(mt.replace(
        old, 'OptionValue "RSQ_Ballistics"\n{\n\t0, "Stock (BD22)"\n\t1, "Low"\n\t2, "Max"\n}'))
    st = dict(guns=len(log), scales=log, caps='Low 24/64 (as 1.96b), Max 48/128, counts x1.8')
    json.dump(st, open(OUT + 'impacts_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py impacts\n')
    print(json.dumps(dict(guns=len(log), caps=st['caps']), indent=1))


def recoil():
    """F5: the per-gun recoil table and handler, generated from WMSHEET + RSBDEFS.

    Run once per apply(). It APPENDS to CVARINFO.rsq and MENUDEF.rsq, so running it twice on the
    same tree declares rsq_recoil twice and the pack dies at load with "cvar 'rsq_recoil' already
    exists" -- which happened. apply() rebuilds src/ from scratch, so the guard is simply: if the
    cvar is already there, this tree has had the stage."""
    if 'rsq_recoil' in open(OUT_SRC + 'CVARINFO.rsq').read():
        raise SystemExit('recoil: this tree already has rsq_recoil -- re-run apply() first')
    sheet = open(RSVRW + 'bd22/WMSHEET.bd22', encoding='latin-1').read()
    guns, cur = {}, None
    for ln in sheet.splitlines():
        s = ln.split('#')[0].strip()
        m = re.match(r'gun\s+"([^"]+)"', s)
        if m:
            cur = m.group(1); guns[cur] = {}; continue
        if cur:
            m = re.match(r'(\w+)\s*=\s*(.+)$', s)
            if m:
                guns[cur][m.group(1)] = m.group(2).strip().strip('"')
    blocks, name, body = {}, None, []
    for ln in open('E:/DOOMWork/RS_Ballistics/RSBDEFS.txt', encoding='latin-1'):
        s = ln.split('#')[0].rstrip()
        m = re.match(r'^recoil\s+(\S+)\s*$', s)
        if m:
            name, body = m.group(1), []; continue
        if name is not None:
            if s.strip() == 'end':
                blocks[name] = dict(body); name = None; continue
            km = re.match(r'\s*(\w+)\s*=\s*(.+)$', s)
            if km:
                body.append((km.group(1), km.group(2).strip()))

    def nums(v, n, dflt=0.0):
        out = [float(x) for x in v.split(',')] if v else []
        return (out + [dflt] * n)[:n]

    rows, skipped, log = [], [], {}
    for card, cls in CARD2CLS:
        g = guns.get(card)
        if not g:
            raise SystemExit('recoil: WMSHEET has no gun %r' % card)
        prof = g.get('recoilprofile', 'none')
        if prof == 'none' or prof not in blocks:
            skipped.append('%s (%s): %s' % (cls, card, 'profile "none"' if prof == 'none' else 'no block ' + prof))
            continue
        b = blocks[prof]
        view = nums(b.get('view', ''), 4)
        mx = nums(b.get('max', ''), 2, 90.0)
        rec = nums(b.get('recover', ''), 2)
        dr = nums(b.get('drift', ''), 2)
        rows.append((cls, prof, dict(
            rise=view[1], riseTics=int(view[3]) or 1, climb=float(b.get('climb', 0) or 0),
            drift=dr[0], driftPeriod=int(dr[1]), recover=rec[0], delay=int(rec[1]),
            maxPitch=mx[0], maxYaw=mx[1])))
        log[cls] = dict(profile=prof, rise=view[1], tics=int(view[3]), climb=float(b.get('climb', 0) or 0),
                        max=mx, recover=rec, dropped_roll=view[2], dropped_back=view[0])
    body = ''
    for cls, prof, d in rows:
        body += ('\t\t{ let d = new("RSQ_RecoilDef");\n'
                 '\t\t  d.rise = %(rise).3f; d.riseTics = %(riseTics)d; d.climb = %(climb).3f;\n'
                 '\t\t  d.drift = %(drift).3f; d.driftPeriod = %(driftPeriod)d;\n'
                 '\t\t  d.recover = %(recover).3f; d.delay = %(delay)d;\n'
                 '\t\t  d.maxPitch = %(maxPitch).3f; d.maxYaw = %(maxYaw).3f;\n'
                 % d) + '\t\t  defCls.Push("%s"); defs.Push(d); }\t// %s\n' % (cls, prof)
    open(OUT_SRC + 'zscript/rsq/recoil.zs', 'w').write(RECOIL_ZS % dict(table=body))
    zp = OUT_SRC + 'ZSCRIPT.rsvr'
    zt = open(zp).read()
    anchor = '#include "zscript/rsq/bash.zs"\n'
    if zt.count(anchor) != 1:
        raise SystemExit('ZSCRIPT.rsvr: the bash include is not there once (bash must run first)')
    zt = zt.replace(anchor, anchor + '#include "zscript/rsq/recoil.zs"\n')
    # and the version gate, which has to be on the ROOT lump -- see recoil.zs's header
    ver = 'version "4.10"'
    if zt.count(ver) != 1:
        raise SystemExit('ZSCRIPT.rsvr: expected one %s to raise for the hitscan events' % ver)
    zt = zt.replace(ver, 'version "4.14"\t// 1.97 F5: WorldHitscanPreFired is 4.13+; qzd17.3 is 4.14.3')
    open(zp, 'w').write(zt)
    mp = OUT_SRC + 'MAPINFO.rsvr'
    mt = open(mp).read()
    a = '"RSQ_Counters", '
    if mt.count(a) != 1:
        raise SystemExit('MAPINFO.rsvr: the counters handler is not registered once')
    open(mp, 'w').write(mt.replace(a, a + '"RSQ_Recoil", '))
    with open(OUT_SRC + 'CVARINFO.rsq', 'a') as f:
        f.write('\n// 1.97 F5: per-gun recoil. Its own row, not the ballistics dial -- this costs one\n'
                '// float a tic, the effects cost a frame budget, and they are not the same decision.\n'
                'user int rsq_recoil = 1;\n')
    mn = OUT_SRC + 'MENUDEF.rsq'
    mt = open(mn).read()
    a = '\tOption "Ballistics", "rsq_ballistics", "RSQ_Ballistics"\n'
    if mt.count(a) != 1:
        raise SystemExit('MENUDEF.rsq: the Ballistics row is not there once')
    open(mn, 'w').write(mt.replace(a, a + '\tOption "Gun Recoil", "rsq_recoil", "OnOff"\n'))
    st = dict(guns=len(rows), skipped=skipped, table=log)
    json.dump(st, open(OUT + 'recoil_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py recoil\n')
    print(json.dumps(dict(guns=len(rows), skipped=skipped), indent=1))


def readme():
    """F6: the pack's own README, shipped in the pk3. Generated like everything else in src/, and
    the counts come out of the files rather than being retyped."""
    zs = open(OUT_SRC + 'zscript/rsr/rsr_guns.bd.zs').read()
    m = re.search(r'static int Count\(\) \{ return (\d+); \}', zs)
    if not m:
        raise SystemExit('rsr_guns.bd.zs: no Count()')
    mt = open(OUT_SRC + 'MENUDEF.rsq').read()
    page = re.search(r'OptionMenu "RSQ_Options"\n\{\n(.*?)\n\}\n', mt, re.S)
    if not page:
        raise SystemExit('MENUDEF.rsq: no RSQ_Options page')
    rows = len(re.findall(r'^\t(?:Option|Slider|Submenu) ', page.group(1), re.M))
    txt = README % dict(ver='1.97-pre', pk3='BD22Q_197pre.pk3', nrsr=int(m.group(1)), nmenu=rows)
    open(OUT_SRC + 'README.txt', 'w').write(txt)
    st = dict(reload_entries=int(m.group(1)), menu_rows=rows, bytes=len(txt))
    json.dump(st, open(OUT + 'readme_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py readme\n')
    print(json.dumps(st, indent=1))


def bash():
    """F4: BD22's kick becomes a gun bash when a gun is in your hands, with the owner's own
    RS_CombatFX impact. Runs after options()."""
    from PIL import Image
    st = {}
    # the art, at the owner's standard: every effect drawn at RSH0's 96 px frame
    sd = OUT_SRC + 'sprites/'
    os.makedirs(sd, exist_ok=True)
    scales, copied = {}, 0
    for eid, cat in FX:
        best, names = 0, []
        for p in sorted(glob.glob('%s/%s/%s*' % (FXROOT, cat, eid)), key=lambda s: os.path.basename(s).lower()):
            nm = os.path.basename(p)
            if not re.match(r'^%s[A-Za-z]0(\.png|\.lmp)?$' % eid, nm):
                continue            # <id>.png on its own is the catalog's strip, not a frame
            im = Image.open(p).convert('RGBA')
            best = max(best, im.width, im.height)
            # .lmp / no extension / a lowercase frame letter all become <ID><LETTER>0.png
            im.save(sd + nm[:len(eid) + 2].upper() + '.png')
            names.append(nm[:len(eid) + 2].upper())
            copied += 1
        if not names:
            raise SystemExit('bash: no frames found for %s in %s/%s' % (eid, FXROOT, cat))
        scales[eid] = (round(FXSTD / best, 3), sorted({n[len(eid)] for n in names}), best)
    st['sprites'] = dict(frames=copied, scale={k: v[0] for k, v in scales.items()},
                         source_px={k: v[2] for k, v in scales.items()})
    # one actor per effect, its frames and its measured scale
    acts = []
    for eid, cat in FX:
        sc, letters, _ = scales[eid]
        acts.append('class RSQ_FX_%s : RSQ_FXBase\n{\n\tDefault { Scale %.3f; }\t// %d px art at the 96 px standard\n'
                    '\tStates\n\t{\n\tSpawn:\n\t\t%s %s 2 Bright;\n\t\tStop;\n\t}\n}'
                    % (eid, sc, scales[eid][2], eid, ''.join(letters)))
    base = ('class RSQ_FXBase : Actor\n{\n\tDefault { +NOINTERACTION; +NOBLOCKMAP; +DONTSPLASH;\n'
            '\t\t+FORCEXYBILLBOARD; RenderStyle "Add"; Alpha 1.0; }\n}\n')
    zs = BASH_ZS % dict(classes=', '.join("'RSQ_FX_%s'" % e for e, _ in FX), nfx=len(FX),
                        deffx=0, ntint=len(TINTS), actors=base + '\n'.join(acts) + '\n')
    open(OUT_SRC + 'zscript/rsq/bash.zs', 'w').write(zs)
    zp = OUT_SRC + 'ZSCRIPT.rsvr'
    zt = open(zp).read()
    anchor = '#include "zscript/rsq/roster.zs"\n'
    if zt.count(anchor) != 1:
        raise SystemExit('ZSCRIPT.rsvr: the roster include is not there once (bd22_mg.py must run first)')
    open(zp, 'w').write(zt.replace(anchor, anchor + '#include "zscript/rsq/bash.zs"\n'))
    open(OUT_SRC + 'DECORATE.rsqbash', 'w').write(BASH_DEC)
    # the tints
    tl = ['// 1.97: the gun bash flash, tintable so RSH0 does not clash with the headshot mod the',
          '// owner runs separately (owner, 2026-10-24). 0 is the art as drawn and sets nothing.']
    for i, (nm, ramp) in enumerate(TINTS):
        if ramp:
            tl.append('RSQ_BashTint%d = "0:255=%%%s"' % (i, ramp))
    open(OUT_SRC + 'TRNSLATE.rsq', 'w').write('\n'.join(tl) + '\n')
    # BD22's DoKick: our branch first, its own body kept whole behind RSQ_BashStock
    dp = OUT_SRC + 'actors/Weapons/DEFAULTWEAPON.dec'
    dt = open(dp, 'rb').read().decode('latin-1')
    eol = '\r\n' if '\r\n' in dt else '\n'          # BD22's files are CRLF; match them
    anchor = '\tDoKick:' + eol
    if dt.count(anchor) != 1:
        raise SystemExit('DEFAULTWEAPON.dec: DoKick is not there exactly once')
    dt = dt.replace(anchor, anchor + BASH_STATES.replace('\n', eol))
    open(dp, 'wb').write(dt.encode('latin-1'))
    st['decorate'] = 'DEFAULTWEAPON.dec DoKick -> RSQ_BashCheck, RSQ_BashStock keeps BD22\'s own kick'
    # the options
    with open(OUT_SRC + 'CVARINFO.rsq', 'a') as f:
        f.write('\n// 1.97: the gun bash (BD22\'s kick, with the gun you are holding)\n'
                'user int rsq_bash = 1;\t\t\t// 0: the boot, as BD22 ships it\n'
                'user int rsq_bash_fx = 0;\t\t// which RS_CombatFX impact\n'
                'user int rsq_bash_tint = 0;\t\t// recolours the RSH0 flash only; 0 is the art as drawn\n')
    mp = OUT_SRC + 'MENUDEF.rsq'
    mt = open(mp).read()
    a = '\tOption "Punch Switches Open", "rsq_punch_use", "OnOff"\n'
    if mt.count(a) != 1:
        raise SystemExit('MENUDEF.rsq: the punch-switches row is not there once')
    mt = mt.replace(a, a + '\tOption "Gun Bash (kick key)", "rsq_bash", "OnOff"\n'
                          '\tOption "Bash Impact", "rsq_bash_fx", "RSQ_BashFXOpt"\n'
                          '\tOption "Bash Impact Colour", "rsq_bash_tint", "RSQ_BashTintOpt"\n')
    mt = mt.rstrip('\n') + '\n\nOptionValue "RSQ_BashFXOpt"\n{\n'
    for i, (eid, _) in enumerate(FX):
        mt += '\t%d, "%s"\n' % (i, eid)
    mt += '}\n\nOptionValue "RSQ_BashTintOpt"\n{\n'
    for i, (nm, _) in enumerate(TINTS):
        mt += '\t%d, "%s"\n' % (i, nm)
    mt += '}\n'
    open(mp, 'w').write(mt)
    st['options'] = 'rsq_bash, rsq_bash_fx (%s), rsq_bash_tint (%s)' % (
        '/'.join(e for e, _ in FX), '/'.join(n for n, _ in TINTS))
    json.dump(st, open(OUT + 'bash_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py bash\n')
    print(json.dumps(st, indent=1))


def options():
    """Adds the rows the page was missing, in place. Runs LAST, after bd22_mg.py and revolver(),
    which add their own rows by exact-match anchors."""
    mp = OUT_SRC + 'MENUDEF.rsq'
    t = open(mp).read()
    st = {}
    cvars = ''.join(open(OUT_SRC + f).read() for f in os.listdir(OUT_SRC) if f.startswith('CVARINFO.'))
    for _, row, cv in ADDED_ROWS:
        if not re.search(r'^(?:server|user) +\w+ +%s\b' % cv, cvars, re.M):
            raise SystemExit('MENUDEF.rsq: a row wants %s, which no CVARINFO declares' % cv)
    for anchor, row, cv in ADDED_ROWS:
        if t.count(anchor) != 1:
            raise SystemExit('MENUDEF.rsq: the anchor for %s is not there exactly once' % cv)
        t = t.replace(anchor, anchor + row)
    # RSR_Debug: 1.96b defines the page and nothing opens it, which in a headset means unreachable
    tail = '\tOption "Extra weapons with cheats", "rsq_extra_weapons", "OnOff"\n'
    if t.count(tail) != 1:
        raise SystemExit('MENUDEF.rsq: the last row of the page is not there exactly once')
    t = t.replace(tail, tail + '\tStaticText " "\n\tSubmenu "Reload: tuning and debug", "RSR_Debug"\n')
    open(mp, 'w').write(t)
    st['added'] = ['rsr_pouch (its OptionValue was defined but no row used it)', 'rsr_assist',
                   'rsvr_melee_swing', 'Submenu RSR_Debug (the page existed but nothing opened it)']
    st['page'] = 'unchanged otherwise: OptionMenu "RSQ_Options", Title "BD22 VR WEAPONS", the owner\'s order'
    json.dump(st, open(OUT + 'opt_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py options\n')
    print(json.dumps(st, indent=1))


def slug_revolver():
    """BD21's Revolver2 into the pack: its own file verbatim bar the renames below, the RSB states,
    the slot, and the menu row that makes it replace BD22's Shotvolver. It shares BD22's Revolver
    sprites (REVO/REVP/REVR), so it needs no sprite lumps and no MODELDEF of its own."""
    st = {}
    t = open(REPO.replace('\\', '/') + '/docs/BD21_Revolver2.txt', 'rb').read().decode('latin-1').replace('\r\n', '\n')
    for a, b in REV2_SND.items():
        t = t.replace(a, b)
    st['sounds'] = len(REV2_SND)
    for a, b in REV2_CLS.items():
        t = t.replace(a, b)
    # PuristGun: BD21's purist machinery -- nothing in the file jumps to it and BD22 has no
    # ClassicShotgun, so the dead state goes rather than warn at load.
    dead = re.search(r'\n *PuristGun:\n(?:.*\n)*?\t\tGoto Ready3\n', t)
    if not dead or t.count('PuristGun') != 1:
        raise SystemExit('BD21_Revolver2.txt: the dead PuristGun state is not there exactly once')
    t = t[:dead.start()] + '\n' + t[dead.end():]
    st['dropped'] = 'PuristGun (ClassicShotgun: not a BD22 class, state unreachable)'
    # its own reload, after its own checks, goes to RSB_Start; the rest of it becomes RSB_Stock
    anchor = ('\t\tREVO A 0 A_JumpIfInventory("TurboReload", 1, "TurboReload")//Check if reloads are disabled.\n'
              '\t\tREVR B 0 A_GiveInventory ("Pumping", 1)\n')
    if t.count(anchor) != 1:
        raise SystemExit('BD21_Revolver2.txt: the ReloadNormally anchor is not there exactly once')
    t = t.replace(anchor, anchor.split('\n')[0] + '\n\t\tGoto RSB_Start\n\tRSB_Stock:\n'
                  + '\t\tREVR B 0 A_GiveInventory ("Pumping", 1)\n')
    # the RSB states, right after the States opening brace
    sb = re.search(r'(ACTOR Revolver2 : BrutalWeapon\n(?:.*\n)*?\tStates\n\t\{\n)', t)
    if not sb:
        raise SystemExit('BD21_Revolver2.txt: no States block')
    t = t[:sb.end(1)] + REV2_RSB + t[sb.end(1):]
    open(OUT_SRC + 'actors/Weapons/Revolver2.dec', 'wb').write(t.encode('latin-1'))
    open(OUT_SRC + 'DECORATE.rsqrev', 'w').write(
        '// 1.97: the BD21 slug revolver (tools/bd22_plus.py revolver)\n#include "actors/Weapons/Revolver2.dec"\n')
    st['decorate'] = 'actors/Weapons/Revolver2.dec, DECORATE.rsqrev'
    # slot 2, with BD22's Revolver (its KEYCONF: setslot 2 ... Revolver ...)
    with open(OUT_SRC + 'KEYCONF.rsq', 'a') as f:
        f.write('\n// 1.97: the slug revolver on slot 2 with the Shotvolver (BD22 KEYCONF setslot 2 ... Revolver)\n'
                'addslotdefault 2 Revolver2\n')
    # the roster handler bd22_mg.py wrote: a second replacement beside the Machinegun's
    rp = OUT_SRC + 'zscript/rsq/roster.zs'
    rt = open(rp).read()
    old = re.search(r'\toverride void CheckReplacement\(ReplaceEvent e\)\n\t\{\n(?:.*\n)*?\t\}\n', rt)
    if not old:
        raise SystemExit('roster.zs: no CheckReplacement (bd22_mg.py must run first)')
    open(rp, 'w').write(rt[:old.start()] + REV2_ROSTER.lstrip('\n') + rt[old.end():])
    with open(OUT_SRC + 'CVARINFO.rsq', 'a') as f:
        f.write('\n// 1.97: roster\nserver bool rsq_slug_replaces_shotvolver = false;\t// every Shotvolver spawn is the slug revolver\n')
    mp = OUT_SRC + 'MENUDEF.rsq'
    mt = open(mp).read()
    a2 = '\tOption "Machinegun replaces MG42", "rsq_mg_replaces_mg42", "OnOff"\n'
    if mt.count(a2) != 1:
        raise SystemExit('MENUDEF.rsq: the Machinegun roster row is not there once')
    open(mp, 'w').write(mt.replace(a2, a2 + '\tOption "Slug revolver replaces Shotvolver", "rsq_slug_replaces_shotvolver", "OnOff"\n'))
    st['roster'] = 'rsq_slug_replaces_shotvolver (server, off); slot 2; RSB indices 8 (speedloader) / 9 (per round)'
    return st


def revolver():
    p = OUT_SRC + 'zscript/rsr/rsb_guns.zs'
    t = open(p).read()
    if 'case 7:' in t:
        raise SystemExit('rsb_guns.zs already has an index 7 -- apply() must run first')
    log = {}
    seats = {}
    for fname in ('Base', 'Tip'):
        seats[fname], log[fname] = rsb_fifth(t, fname)
    # Three new indices, all of them index 3's rows with named fields replaced:
    #   7  BD22's Revolver, a round at a time      8  the slug revolver, speedloader
    #   9  the slug revolver, a round at a time
    PERROUND = {'Chambers': ('5', "a round at a time: the cylinder's own five chambers"),
                'Loader': ('false', 'not the speedloader')}
    SLUG = {'Reserve': ('"Clip2"', "BD21 Revolver2's own Weapon.AmmoType1"),
            'Cls': ("'Revolver2'", '')}
    NEW = {7: dict(PERROUND), 8: dict(SLUG), 9: dict(PERROUND, **SLUG)}
    for fname in re.findall(r'\tclearscope static [\w<>]+ (\w+)\(int i\)\n', t):
        if fname == 'Index':
            continue
        m, rows = rsb_rows(t, fname)
        if 3 not in rows:
            continue                      # e.g. LoaderEmptyInHand: no case 3, the default stands
        out = ''
        for i, over in NEW.items():
            val, why = over.get(fname, (rows[3].strip(), ''))
            out += '\n\t\tcase %d:\treturn %s;%s' % (i, val, ('\t\t// %s' % why) if why else '')
        t = t[:m.end(1)] + out + t[m.end(1):]
    # per-chamber switches: the per-round indices get all five seats, the speedloader one just k=0
    for fname in re.findall(r'\tclearscope static [\w<>]+ (\w+)\(int i, int k\)\n', t):
        m, rows = rsb_rows(t, fname)
        if 24 not in rows:
            continue
        out = ''
        for i in NEW:
            for k in range(5 if i in (7, 9) else 1):
                if fname in seats and k == 0 and i in (7, 9):
                    v = '(%.4f, %.4f, %.4f)' % tuple(seats[fname])
                    why = '\t\t// recovered: 5*the patched mean - the four rows the patch left'
                else:
                    v, why = rows[24 + k].strip(), ''
                out += '\n\t\tcase %d:\treturn %s;%s' % (i * 8 + k, v, why)
        t = t[:m.end(1)] + out + t[m.end(1):]
    # Index(): each gun, picked by the option
    old = "\t\tif (n == 'Revolver')\treturn 3;"
    if t.count(old) != 1:
        raise SystemExit('rsb_guns.zs: Index() Revolver line not found once')
    t = t.replace(old, "\t\tif (n == 'Revolver')\treturn PerRound() ? 7 : 3;\n"
                       "\t\tif (n == 'Revolver2')\treturn PerRound() ? 9 : 8;\t// 1.97: the slug revolver")
    t = t.replace('\tclearscope static int Index(Weapon w)', REV_FEED.lstrip('\n') + '\tclearscope static int Index(Weapon w)', 1)
    open(p, 'w').write(t)
    # the option
    with open(OUT_SRC + 'CVARINFO.rsb', 'a') as f:
        f.write('\n// 1.97: Shot/Revolver Reload -- 0 the speedloader (as 1.96b shipped), 1 a round at a time\n'
                'server int rsb_revolver_feed = 0;\n')
    mp = OUT_SRC + 'MENUDEF.rsq'
    mt = open(mp).read()
    anchor = '\tOption "Shotvolver Slugshot Alt Fire", "rsa_rev_magnum", "OnOff"\n'
    if mt.count(anchor) != 1:
        raise SystemExit('MENUDEF.rsq: the Shotvolver row is not there once')
    mt = mt.replace(anchor, anchor + '\tOption "Shot/Revolver Reload", "rsb_revolver_feed", "RSB_RevFeed"\n')
    # `value, "Text"` -- the pack's own OptionValue form. `0 = "..."` parses as nothing and the menu
    # init dies silently (the engine stops right after "M_Init: Init menus." with no line in the log).
    mt = mt.rstrip('\n') + '\n\nOptionValue "RSB_RevFeed"\n{\n\t0, "Speedloader"\n\t1, "Per Round"\n}\n'
    open(mp, 'w').write(mt)
    log['option'] = 'rsb_revolver_feed (server, 0 = speedloader); menu row after the Shotvolver alt fire'
    log['slug'] = slug_revolver()
    json.dump(log, open(OUT + 'rev_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:          # bd22_mg.py opened it; this stage runs last
        f.write('then tools/bd22_plus.py revolver\n')
    print(json.dumps(log, indent=1))


if __name__ == '__main__':
    if sys.argv[1:2] == ['apply']:
        apply()
    if sys.argv[1:2] == ['revolver']:
        revolver()
    if sys.argv[1:2] == ['impacts']:
        impacts()
    if sys.argv[1:2] == ['recoil']:
        recoil()
    if sys.argv[1:2] == ['readme']:
        readme()
    if sys.argv[1:2] == ['butt']:
        butt()
    if sys.argv[1:2] == ['whip']:
        whip()
    if sys.argv[1:2] == ['bash']:
        bash()
    if sys.argv[1:2] == ['options']:
        options()
    if sys.argv[1:2] == ['pk3']:
        pk3(sys.argv[2])
