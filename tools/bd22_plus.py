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
# THE RELEASE VERSION, in one place. readme() builds both the title and the pk3 name
# from it, so the two cannot say different things -- which is how a stale pk3 on the
# Desktop cost a diagnosis on 2026-10-24. The repo folder stays sets/bd22q_1.97:
# renaming it would break check_plan.py and PLAN.md for nothing.
VERSION = '1.99'

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
    # 2026-10-24: the other stocked guns. The MP40 and the SMG rigid-fit their wm mesh at 0.0000,
    # same as the four above.
    ('MP40BUTT', ["'MP40'"], ['MP40', 'MP42', 'PP40'], 2, (24.8, 0.2, -3.1), (-1.2, 0.0, -3.5),
     'MP40.md3 frame 2'),
    ('SMGBUTT', ["'BrutalSMG'"], ['SMGF', 'SMGR', 'VSMG'], 3, (18.6, -0.3, -1.2), (0.6, 0.0, -10.4),
     'BrutalSMG.md3 frame 3'),
    # THE MACHINEGUN, and why it took a second pass. Its fit came out at 11.26 where everyone
    # else's was 0.0000 and I called that "the lookup is finding the wrong model". It is the right
    # model: the fit stacks every surface's vertices in order and calls the correspondence
    # identity, and this pair SPLITS THE MESH DIFFERENTLY --
    #     Machinegun.md3     6 surfaces [104, 1014, 106, 3470, 58, 11996]
    #     machinegun_wm.md3  7 surfaces [104, 1014, 106, 3470, 58, 415, 11581]
    # 16748 either way, so the stack is the same length and nothing complained, but the body is not
    # in the same order and one rigid transform over the lot is least-squares nonsense. Fitting
    # only the five surfaces that correspond one for one gives frame 4 at residual 0.0000, and
    # MODELDEF.bd.txt says the same thing independently: `FrameIndex MGN1 A 0 4`, MGN1 A being the
    # sprite this gun's Ready state holds. One sprite, not three: it is BD21's and has no dual.
    # The butt is measured off `M249_lowpoly` ALONE -- the model carries an `alt-` block of 4694
    # vertices about 40 units below the gun, and a span taken over everything measures the pair.
    ('MGBUTT', ["'Machinegun'"], ['MGN1'], 4, (20.1, 0.0, 4.3), (-1.4, 0.0, 2.0),
     'Machinegun.md3 frame 4, surface M249_lowpoly'),
    # THE MG42, matched by POSITION. HitlersBuzzsaw.md3 is [18912, 60] against buzzsaw_wm.md3's
    # [3059, 15853, 60]: no surface corresponds by index, so the order-identity Kabsch above gave
    # 24.26 and I twice wrote the gun off. The answer was already in this file -- `rigid()` is ICP
    # with a cKDTree, correspondence by POSITION rather than by order, and the geometry stage has
    # been reporting this very mesh at mean 0.0 cm, max 0.0 cm, rotation 1.7e-06 deg all along.
    # Run per frame: frame 0 matches at 0.0000 and frames 1 and 2 at 0.0105, and MODELDEF agrees
    # independently -- `FrameIndex HBUS A 0 0`, HBUS A being the sprite the Ready loop holds.
    # PBUS is the same frames again: it is what BD22 draws in Purist mode, so both are ready.
    ('MG42BUTT', ["'MG42'"], ['HBUS', 'PBUS'], 0, (21.6, -1.0, 1.2), (-10.8, -0.1, 1.6),
     'HitlersBuzzsaw.md3 frame 0'),
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

BRUTAL DOOM v22, IN VR, ON A QUEST. As an addon, on the stock engine.

Not a port and not a fork. Brutal Doom stays Brutal Doom: this loads after it, replaces none of
its guns, and with its options off behaves exactly as it shipped. What it adds is hands -- you
reload by pulling the magazine out and pushing a fresh one home, you bash with the gun you are
holding, and the brass leaves the port it is supposed to leave.

AND IT RUNS ON STOCK QUESTZDOOM 17.3. No engine changes, no patched build, no fork required.
That constraint is the point of the whole thing, and it is why anything here runs on your
headset instead of on one machine.


WHERE THIS CAME FROM
--------------------
TeamBeef brought Doom to VR and built the community that made the rest of it possible. Everyone
here found it through them.

Emawind's QuestZDoom is the engine this targets -- the one that put GZDoom on a standalone
headset. Ermac's DoomXR is the other half of the lineage, and the hands you are wearing are his.

REMA, our own GZDoom fork, is named for the two of them -- eRmac and EMAwind. REMA is where VR
reloading was worked out: real magazines, measured wells, a hand that takes hold of a part and
moves it. REMA can do things stock QuestZDoom cannot, because we wrote them into it.

This pack is that work coming BACK. Everything REMA taught us, carried to the stock engine and
made to run there -- a little more of it each release. Where stock cannot do what REMA does, it
says so plainly here rather than faking it.


LOAD ORDER
----------
    doom2.wad  ->  brutal22test6.pk3  ->  BD_VoxelPack.pk3  ->  %(pk3)s

Doom 2, not Freedoom: BD_VoxelPack's voxeldef names Doom 2's own sprites and Freedoom fails on it.


RELOADING, WITH YOUR HANDS
--------------------------
  magazine    12 guns -- Rifle, Pistol, SMG, MP40, Assault Shotgun, Railgun, Plasma,
              Sniper, Rocket Launcher, and the MG42's belt drum, the Flamethrower's
              canister and the Unmaker's skull
  pump        the Shotgun
  break-open  the SSG, the Grenade Launcher, the Shotvolver, and the slug revolver

Take the magazine out with your off hand, bring a fresh one up, push it home. Break guns swing
open, take a round at a time or a speedloader, and a flick of the wrist shuts them.

Brutal Doom never reloads the MG42, the Flamethrower or the Unmaker at all. Their drum, canister
and skull were carved out of their own meshes so they could come off.


MELEE
-----
  GUN BASH          your kick key, with a gun in your hands, bashes with the gun instead of
                    kicking. Brutal Doom's own kick damage; the boot is simply not drawn.
                    Pick its impact effect and its colour in the menu.
  PISTOL WHIP       swing a pistol or a revolver and it hits what it passes through.
  BUTT STRIKE       drive the stock forward with both hands on it. All eight stocked guns:
                    Rifle, Shotgun, SSG, Assault Shotgun, MP40, SMG, Machinegun, MG42.
                    OFF by default -- two hands on a rifle is also how you aim one, so this is
                    the one most likely to go off when you did not mean it. Turn it on and judge.
  FISTS             a real punch with either hand, and punching a switch works it.
  AXE / DRAGONSLAYER  swing them; two hands and the edge leading bite harder.

It reads your arm, not your body. Walking, strafing and turning move the gun and are subtracted;
only the swing counts.

Out of VR, or with these turned off, Brutal Doom's own melee is untouched.


EVERY GUN SHOOTS LIKE ITSELF
----------------------------
Behind the Ballistics switch -- Stock / Low / Max. Stock is Brutal Doom's own and nothing of ours.

  RECOIL        22 guns, each from its own cartridge: bullet weight, muzzle velocity, powder and
                the loaded gun's weight. An MG42 and a Kar98k fire the same round out of a 25 lb
                gun and a 9 lb gun, and the numbers say so. In VR this moves the GUN IN YOUR
                HANDS, never your aim and never the camera.
  MUZZLE FLASH  18 guns, each with its own light. The SSG throws 760 units of near-white; the
                SMG throws a sixth of that; the Unmaker throws red.
  FLASH TAIL    14 guns -- the room answering the shot, with separate indoor and outdoor
                recordings. Your rifle cracks differently in a corridor than it does under sky.
  THE ROUND     11 guns draw the round in flight, at the size and the speed its cartridge says.
                340 m/s for a 9mm, 900 for 5.56 -- which is fast, so you see a streak.
  IMPACT        a sound for the material you hit -- concrete, metal, wood, glass, pipe, tech,
                lava. A ricochet, per gun, when the round comes in shallow: a magnum skips off
                stone inside 20 degrees where a rifle needs 14. Buckshot never ricochets, because
                nine pellets would be nine ricochets. A light on the hot surfaces.
  BRASS         out of the gun's own ejection port, measured off the mesh, for 9 guns -- and
                three different ways: flicked from a side port, thrown down a chute (the MG42
                ejects through the floor of its receiver, which is what an MG42 does), or tipped
                out by hand from a cylinder or a broken breech. Sized to the round it fired.


OPTIONS
-------
Options -> BD22 VR Weapons. %(nmenu)d rows, including Reloading (VR or Stock), what grabs the
ammo, where a new magazine comes from, reload assist, the per-gun scopes, the dual-wield and
voxel pages, and "Reload: tuning and debug" for the capture zones and a step-by-step print.

Every option defaults to how Brutal Doom behaves, or to the gentler setting, except the VR hands
and reloading themselves. Turn Reloading to "Stock (BD22)" and the guns reload as they always did.


CREDITS
-------
Brutal Doom v22 is Sergeant_Mark_IV's. It is the mod that reinvented Doom and brought a
generation back to it, and this is an addon to it that ships none of its guns.

TeamBeef built Doom VR and the community around it.
Emawind's QuestZDoom is the engine. Ermac's DoomXR is the other half of REMA, and the hands are
his (Rusted Legacy, MIT -- models/rsq/LICENSE_RustedLegacy_MIT.txt).
The BD21 Machinegun and slug revolver are Brutal Doom 21's, brought forward.
Reload foley, impact and tail sounds the mod itself has none of come from RS_Ballistics and
RS_VR_Weapons.


WHAT STOCK CANNOT DO, SAID PLAINLY
----------------------------------
Some of what REMA does has not crossed, and will not until the engine does:

  * Recoil's ROLL and its backward shove. The one hook that carries roll is resolved on the
    weapon's own class, and this pack does not own Brutal Doom's weapons; ZScript cannot add an
    override to them. Tested, not assumed. Yaw and pitch are the whole channel here.
  * Impact PARTICLE BURSTS, heat shimmer, volumetric smoke, wall damage, flash blindness and
    ear ringing. All of them are REMA renderer or engine features with no stock equivalent.
  * Per-part motion at runtime -- a slide that rides back under its own power. On stock a part
    moves only if the motion is baked into the mesh's frames.


KNOWN GAPS
----------
  * A dropped partial drum costs the reserve nothing.
  * The Shotvolver's cylinder has five chambers and a capacity of six; that is how Brutal Doom
    counts it, and loading a round at a time inherits it.
  * The Machinegun's HUD is its model: its sprite lumps are placeholders.
  * The MP40, the Minigun and the Machinegun throw their brass from the body, not a port: there
    is no ejection port modelled in those three meshes to measure.

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


# F5 -- the round in flight. RS_Ballistics' own btracer.obj: one hexagonal tube, 80 units long and
# 7 across, drawn at eight sizes so a buckshot pellet is a stub and a 7.62 is a long streak. Its
# MODELDEF comes across verbatim in shape -- only the class name and the path change -- because a
# model is an ordinary asset; it is the PARTICLE bursts that are a REMA renderer feature and stay
# behind. RSBM is a 1x1 transparent lump: GZDoom has to hang a model on a sprite frame, and TNT1 is
# special-cased out of drawing, so the sprite is a mount point that draws nothing.
BULLET_SIZES = [
    ('A', 0.2500, 0.2286, 'pistol -- a 9mm, .45 or .38 in flight: a short thin dart'),
    ('B', 0.3250, 0.2714, 'smg -- the same round out of a submachine gun'),
    ('C', 0.4250, 0.2857, 'intermediate -- 5.56, 7.92 Kurz: the assault-rifle streak'),
    ('D', 0.5750, 0.3286, 'rifle -- full-power: 7.62, .30-06, 7.62x54R'),
    ('E', 0.7250, 0.4143, 'heavy -- 9.3x74R and the extreme machine-gun look'),
    ('F', 0.1250, 0.1714, 'pellet -- one pellet of buckshot: a stub'),
    ('G', 0.8000, 0.4571, 'tracer -- long and bright, the round you are meant to read'),
    ('H', 1.0000, 0.5571, 'tracerheavy -- the mesh at its full authored size'),
]

BULLET_ZS = '''// bullet.zs (1.97, F6) -- GENERATED by tools/bd22_plus.py bullet. Do not edit by hand.
//
// The round you can see. F5 built this and could never fire it: it was written to RIDE a player
// projectile, and every cartridge gun in Brutal Doom is HITSCAN -- there is no projectile to ride.
// It shipped as dead code. It now flies the shot itself, from the muzzle to the point the hitscan
// actually landed, which WorldHitscanFired hands us as e.AttackPos and e.DamagePosition.
//
// RS_Ballistics' own btracer.obj at the size its cartridge calls for. Purely a look: it never
// collides, never damages, never blocks. It turns to face its own velocity, which is what
// USEACTORPITCH / USEACTORROLL in the MODELDEF are for -- the tube lies along the flight instead
// of wherever the gun pointed when it spawned.
//
// SPEED IS THE AUTHORED ONE AND THAT MEANS IT IS FAST. `ballistics.speed` is metres per second --
// 340 for a 9mm, 900 for 5.56 -- which at vr_vunits_per_meter is 330 to 874 MAP UNITS PER TIC. A
// round crosses an ordinary room in about one tic, so what you see is a streak, not a dart. That
// is what a real tracer looks like and it is what the data says, so it is not quietly slowed
// here. `rsq_round_speed` is the slider if you want to read it in the headset: 1.0 is the data,
// lower is slower. It does not touch where anything lands -- the hitscan has already hit.
//
// Eleven guns name a model to draw. The rockets, the plasma and both BFGs say `look = none` in
// their roundlook and correctly get nothing: they are projectiles and already have their own.
//
// Rides rsq_ballistics like the rest of the pack's effects.

class RSQ_Bullet : Actor
{
\tDefault
\t{
\t\t+NOINTERACTION;
\t\t+NOBLOCKMAP;
\t\t+NOGRAVITY;
\t\t+DONTSPLASH;
\t\tRenderStyle "Normal";
\t}

\tVector3 step;
\tint ttl;

\t// point it along a velocity, so the tube lies on the flight
\tvoid FaceVel(Vector3 v)
\t{
\t\tdouble sp = v.Length();
\t\tif (sp <= 0)
\t\t\treturn;
\t\tangle = VectorAngle(v.x, v.y);
\t\tpitch = -asin(clamp(v.z / sp, -1, 1));
\t}

\t// +NOINTERACTION means nothing moves this actor for us, which is the point: it must not
\t// collide with anything on the way. So it is walked by hand and retired on arrival.
\toverride void Tick()
\t{
\t\tif (ttl <= 0)
\t\t{
\t\t\tDestroy();
\t\t\treturn;
\t\t}
\t\tttl--;
\t\tSetOrigin(pos + step, true);
\t}

\t// per gun: the frame its roundlook names, and the speed its ballistics give in map units a tic
\tstatic int FrameOf(Name gun)
\t{
%(frames)s\t\treturn -1;
\t}

\tstatic double SpeedOf(Name gun)
\t{
%(speeds)s\t\treturn 0;
\t}

\tstatic void Fire(Actor src, Vector3 from, Vector3 to, Name gun)
\t{
\t\tint fr = FrameOf(gun);
\t\tdouble sp = SpeedOf(gun);
\t\tif (!src || fr < 0 || sp <= 0)
\t\t\treturn;
\t\tVector3 d = level.Vec3Diff(from, to);
\t\tdouble dist = d.Length();
\t\tif (dist < 1)
\t\t\treturn;
\t\tlet cv = CVar.FindCVar('rsq_round_speed');
\t\tdouble k = cv ? clamp(cv.GetFloat(), 0.02, 1.0) : 1.0;
\t\tsp *= k;
\t\tlet b = RSQ_Bullet(Actor.Spawn('RSQ_Bullet', from));
\t\tif (!b)
\t\t\treturn;
\t\tb.frame = fr;
\t\t// Step by dist/ttl, NOT by the raw speed. At 777 units a tic a 400-unit shot has ttl 1,
\t\t// and a raw step would fly it 777 units -- clean past the wall it just hit. Dividing the
\t\t// distance by the whole tics instead lands it exactly on the impact; the only tic that is
\t\t// slower than the authored speed is the last one.
\t\tb.ttl = max(1, int(ceil(dist / sp)));
\t\tb.step = d / b.ttl;
\t\tb.FaceVel(b.step);
\t}

\tStates
\t{
\tSpawn:
\t\tRSBM A -1;\t\t// the frame is set by Fire(); RSBM draws nothing on its own
\t\tStop;
\t}
}
'''


FLASH_ZS = '''// flash.zs (1.97, F5) -- GENERATED by tools/bd22_plus.py flash. Do not edit by hand.
//
// A muzzle flash that is this gun's muzzle flash. Brutal Doom draws the same flash sprite for
// everything; REMA's sheet gives every gun a `flashprofile`, and RS_Ballistics' flash blocks give
// each profile a light -- radius, and a colour. The SSG throws 760 units of near-white; the SMG
// throws 160. That difference is the whole point.
//
// WHAT CROSSED AND WHAT DID NOT. A flash block also carries bursts, cones, powder, barrel heat and
// a sound tail. The bursts resolve PARTICLEDEFS particles, which are a REMA RENDERER feature
// (hw_gpuparticlebuffer, hw_meshparticles) and cannot run here. The tail is a whole interior /
// exterior sound set, 5+ variants a gun, and is NOT done. What crossed is the light, which is the
// part you see first and the part that costs nothing.
//
// It rides the ballistics dial, not its own row: this is an effect, and Stock means Brutal Doom's
// own and nothing of ours.

class RSQ_Flash : Actor
{
	Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; +DONTSPLASH; RenderStyle "None"; }

	int life;

	static void Fire(PlayerPawn mo, int radius, Color col, int tics)
	{
		if (!mo || radius <= 0)
			return;
		// at the hand in VR, since that is where the gun is; at the pawn otherwise
		Vector3 at = mo.pos + (0, 0, mo.height * 0.7);
		if (RSVR_VRHand.InVR(mo))
			at = RSVR_VRHand.HandPos(mo);
		let f = RSQ_Flash(Actor.Spawn('RSQ_Flash', at, NO_REPLACE));
		if (!f)
			return;
		f.life = max(1, tics);
		f.A_AttachLight('rsqflash', DynamicLight.PointLight, col, radius, 0);
	}

	override void Tick()
	{
		life--;
		if (life <= 0)
			Destroy();
	}
}

class RSQ_FlashHandler : EventHandler
{
	Array<String> cls;
	Array<int> rad;
	Array<int> col;
	Array<int> len;
	Array<String> tin;
	Array<String> tex;
	Array<double> tvol;

	override void OnRegister()
	{
%(table)s	}

	// THE TAIL: the room answering the shot, indoors or out. `rsb/tail/<set>` is not
	// itself a sound -- only /int and /ext are -- so both names are resolved at build
	// time and the one over the muzzle is picked here, the way RS_Ballistics picks it:
	// on whether the ceiling at that point is sky. Three of the nine sets have no
	// interior recording, and for those the generator has already put the exterior in
	// both slots, so nothing here can name a sound that does not exist.
	//
	// ON THE PAWN, ONE CHANNEL, NO OVERLAP, deliberately. A held trigger would stack
	// tails into mush; RS stops the previous through a SoundHandle, which this engine
	// does not have (stock S_StartSoundAt returns void). A new sound on the same actor
	// and channel replaces the old, which is the same behaviour by the only route there
	// is. It costs the half metre between the pawn and the muzzle, on an echo.
	static void Tail(PlayerPawn mo, String sin, String sex, double vol)
	{
		if (!mo || vol <= 0 || sin == "")
			return;
		Vector3 at = RSVR_VRHand.InVR(mo) ? RSVR_VRHand.HandPos(mo) : mo.pos;
		let sec = mo.Level.PointInSector(at.xy);
		bool openSky = sec && sec.GetTexture(Sector.ceiling) == skyflatnum;
		mo.A_StartSound(openSky ? sex : sin, CHAN_7, 0, min(vol, 1.0));
	}

	void Shot(PlayerPawn mo)
	{
		if (!mo || !mo.player || RSQ_Ballistics.FxLevel() <= 0)
			return;
		let w = mo.player.ReadyWeapon;
		if (!w)
			return;
		String n = w.GetClassName();
		for (int i = 0; i < cls.Size(); i++)
			if (cls[i] ~== n)
			{
				RSQ_Flash.Fire(mo, rad[i], Color(col[i]), len[i]);
				Tail(mo, tin[i], tex[i], tvol[i]);
				return;
			}
	}

	override bool WorldHitscanPreFired(WorldEvent e)
	{
		Shot(PlayerPawn(e.Thing));
		return false;
	}

	override bool WorldRailgunPreFired(WorldEvent e)
	{
		Shot(PlayerPawn(e.Thing));
		return false;
	}

	override void WorldThingSpawned(WorldEvent e)
	{
		if (e.Thing && e.Thing.bMissile)
			Shot(PlayerPawn(e.Thing.target));
	}
}
'''


def flash():
    """F5: a per-gun muzzle flash light, from the sheet's flashprofile."""
    if os.path.exists(OUT_SRC + 'zscript/rsq/flash.zs'):
        raise SystemExit('flash: this tree already has it -- re-run apply() first')
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
    fl = {}
    for m in re.finditer(r'(?ms)^flash (\S+)[^\n]*\n(.*?)^end', defs):
        d = {}
        for k, v in re.findall(r'^\s*(\w+)\s*=\s*([^\n#]+)', m.group(2), re.M):
            d[k] = v.strip()
        fl[m.group(1)] = d
    RSBALL = 'E:/DOOMWork/RS_Ballistics/'
    rows, log, skipped, tails = '', {}, [], set()
    for card, cls in CARD2CLS:
        p = guns.get(card, {}).get('flashprofile', 'none')
        b = fl.get(p)
        if p == 'none' or not b or 'light' not in b or 'lightcolor' not in b:
            skipped.append('%s (%s)' % (cls, p))
            continue
        lt = [x.strip() for x in b['light'].split(',')]
        rgb = [int(float(x)) for x in b['lightcolor'].split(',')][:3]
        radius = int(float(lt[0]))
        tics = int(float(lt[2])) if len(lt) > 2 else 2
        packed = (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
        # the TAIL off the same block, resolved to its two real alias names here rather
        # than concatenated at runtime. Optional: the energy weapons have a light and no tail,
        # because a plasma bolt has no report.
        tl = [x.strip() for x in b['tail'].split(',')] if b.get('tail') else []
        base = tl[0] if tl else ''
        tvolume = float(tl[1]) if len(tl) > 1 else 1.0
        s_in = s_ex = ''
        if base:
            leaf = base.split('/')[-1]
            has_int = os.path.isdir(RSBALL + 'sounds/rsb/tail/%s/int' % leaf)
            s_ex = base + '/ext'
            s_in = base + '/int' if has_int else s_ex
            tails.add(base)
        rows += ('\t\tcls.Push("%s"); rad.Push(%d); col.Push(0x%06X); len.Push(%d);'
                 ' tin.Push("%s"); tex.Push("%s"); tvol.Push(%.2f);\t// %s\n'
                 % (cls, radius, packed, tics, s_in, s_ex, tvolume, p))
        log[cls] = dict(profile=p, radius=radius, color=rgb, tics=tics,
                        tail=base or None, tail_int=s_in or None, tail_ext=s_ex or None,
                        tail_volume=tvolume if base else None)
    # Shot() looks a gun up in this one table, and the table only holds guns that have a
    # LIGHT, so a gun with a tail and no light would never be reached. Nothing is in that state
    # today; this refuses to ship quietly if that changes.
    for card2, cls2 in CARD2CLS:
        pr = guns.get(card2, {}).get('flashprofile', 'none')
        bb = fl.get(pr) or {}
        if bb.get('tail') and cls2 not in log:
            raise SystemExit('flash: %s has a tail (%s) and no light, so it would never play'
                             % (cls2, bb['tail']))

    # the sounds. Each set is a folder of folders -- <set>/int and <set>/ext -- and three sets
    # have no int, so this copies what is there and no more.
    import shutil
    n_files, rooms = 0, {}
    for s in sorted(tails):
        leaf = s.split('/')[-1]
        rooms[s] = []
        for room in ('int', 'ext'):
            src = RSBALL + 'sounds/rsb/tail/%s/%s' % (leaf, room)
            if not os.path.isdir(src):
                continue
            rooms[s].append(room)
            dst = OUT_SRC + 'sounds/rsb/tail/%s/%s' % (leaf, room)
            os.makedirs(dst, exist_ok=True)
            for f in os.listdir(src):
                if os.path.isfile(src + '/' + f):
                    shutil.copy(src + '/' + f, dst + '/' + f)
                    n_files += 1
        if 'ext' not in rooms[s]:
            raise SystemExit('flash: tail set %s has no exterior, which every gun falls back to' % s)
    snd = open(RSBALL + 'SNDINFO.txt', encoding='latin-1').read()
    keep = []
    for ln in snd.splitlines():
        s2 = ln.strip()
        hit = False
        for x in sorted(tails):
            for room in rooms[x]:
                nm = x + '/' + room
                if re.match(re.escape(nm) + r'\d*\s', s2) or \
                   re.match(r'\$(random|limit)\s+' + re.escape(nm) + r'\d*(\s|\{|$)', s2):
                    hit = True
                    break
            if hit:
                break
        if hit:
            keep.append(ln)
    # every alias a gun can name must actually be a $random set, or the shot is silent
    for cls2, v in log.items():
        for nm in (v.get('tail_int'), v.get('tail_ext')):
            if nm and not re.search(r'(?m)^\$random ' + re.escape(nm) + r'\s*\{', snd):
                raise SystemExit('flash: %s names tail %s and SNDINFO has no $random for it'
                                 % (cls2, nm))
    want = set()
    for ln in keep:
        mm = re.match(r'^\s*\S+\s+(sounds/\S+\.ogg)\s*$', ln)
        if mm:
            want.add(mm.group(1))
    gone = sorted(f for f in want if not os.path.exists(OUT_SRC + f))
    if gone:
        raise SystemExit('flash: SNDINFO would name %d tail sounds the pack does not ship: %s'
                         % (len(gone), gone[:4]))
    with open(OUT_SRC + 'SNDINFO.rsq', 'a') as f:
        f.write('\n// 1.97 F5: the flash TAIL -- the room answering the shot, /int and /ext per\n'
                '// set. Lifted from RS_Ballistics with full paths, as the impact sounds were.\n'
                + '\n'.join(keep) + '\n')

    open(OUT_SRC + 'zscript/rsq/flash.zs', 'w').write(FLASH_ZS % dict(table=rows))
    zp = OUT_SRC + 'ZSCRIPT.rsvr'
    zt = open(zp).read()
    a = '#include "zscript/rsq/rounds.zs"\n'
    if zt.count(a) != 1:
        raise SystemExit('ZSCRIPT.rsvr: the rounds include is not there once (impacts must run first)')
    open(zp, 'w').write(zt.replace(a, a + '#include "zscript/rsq/flash.zs"\n'))
    mp = OUT_SRC + 'MAPINFO.rsvr'
    mt = open(mp).read()
    k = '"RSQ_Recoil", '
    if mt.count(k) != 1:
        raise SystemExit('MAPINFO.rsvr: RSQ_Recoil is not registered once (recoil must run first)')
    open(mp, 'w').write(mt.replace(k, k + '"RSQ_FlashHandler", '))
    st = dict(guns=len(log), skipped=skipped, tail_sets=sorted(tails),
              tail_guns=len([1 for v in log.values() if v.get('tail')]),
              tail_files=n_files, ext_only=sorted(k for k, v in rooms.items()
                                                 if 'int' not in v), table=log)
    json.dump(st, open(OUT + 'flash_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py flash\n')
    print(json.dumps(dict(guns=len(log), skipped=skipped), indent=1))


def bullet():
    """F6: the round in flight, flying the hitscan itself. F5 built it to ride a projectile and
    every cartridge gun is hitscan, so it never fired and was left out of the pipeline."""
    rb = 'E:/DOOMWork/RS_Ballistics/'
    md = OUT_SRC + 'models/rsb/'
    os.makedirs(md, exist_ok=True)
    for f in ('btracer.obj', 'btracer.png'):
        shutil.copy(rb + 'models/bullet/' + f, md + f)
    sd = OUT_SRC + 'sprites/'
    os.makedirs(sd, exist_ok=True)
    for fr, _, _, _ in BULLET_SIZES:
        shutil.copy(rb + 'sprites/RSBM%s0.png' % fr, sd + 'RSBM%s0.png' % fr)
    blocks = ''
    for fr, sx, sy, why in BULLET_SIZES:
        blocks += ('Model RSQ_Bullet\t// %s\n{\n\tPath "models/rsb"\n\tModel 0 "btracer.obj"\n'
                   '\tSurfaceSkin 0 0 "btracer.png"\n\tScale %.4f %.4f %.4f\n'
                   '\tDontCullBackfaces\n\tUSEACTORPITCH\n\tUSEACTORROLL\n'
                   '\tFrameIndex RSBM %s 0 0\n}\n\n' % (why, sx, sy, sy, fr))
    open(OUT_SRC + 'MODELDEF.rsbullet', 'w').write(
        '// 1.97 F6: the round in flight (tools/bd22_plus.py bullet). RS_Ballistics\' btracer.obj,\n'
        '// one tube at eight sizes. RSBM is a 1x1 transparent lump -- a mount point that draws\n'
        '// nothing, because GZDoom has to hang a model on a sprite frame.\n\n' + blocks)

    # WHICH frame and WHICH speed are both in the data, so neither is typed here:
    #   roundlook.look = model, RSBM<letter>     the size the cartridge is drawn at
    #   ballistics.speed                         metres per second
    # m/s -> map units a tic is speed * vr_vunits_per_meter / 35. The 34 is the cvar's default
    # and is also what casings.zs assumes when the cvar is unreadable.
    defs = open(rb + 'RSBDEFS.txt', encoding='latin-1').read()
    sheet = open(REMA + 'WMSHEET.bd22', encoding='latin-1').read()

    def kindof(kind):
        out = {}
        for mm in re.finditer(r'(?ms)^%s (\S+)[^\n]*\n(.*?)^end' % kind, defs):
            d = {}
            for k, v in re.findall(r'^\s*(\w+)\s*=\s*([^\n#]+)', mm.group(2), re.M):
                d[k] = v.strip()
            out[mm.group(1)] = d
        return out

    rnds, looks, ball = kindof('round'), kindof('roundlook'), kindof('ballistics')
    guns, cur = {}, None
    for ln in sheet.splitlines():
        s = ln.split('#')[0].strip()
        mm = re.match(r'gun\s+"([^"]+)"', s)
        if mm:
            cur = mm.group(1)
            guns[cur] = {}
            continue
        mm = re.match(r'(\w+)\s*=\s*(.+)$', s)
        if mm and cur:
            guns[cur][mm.group(1)] = mm.group(2).strip().strip('"')

    sizes = {fr for fr, _, _, _ in BULLET_SIZES}
    frames, speeds, log, skipped = '', '', {}, []
    for card, cls in CARD2CLS:
        pr = guns.get(card, {}).get('roundprofile')
        if not pr:
            continue
        look = rnds.get(pr, {}).get('roundlook') or (pr if pr in looks else None)
        la = looks.get(look, {}).get('look', '') if look else ''
        mm = re.match(r'model\s*,\s*RSBM(\w)', la)
        if not mm:
            skipped.append('%s (%s: look %s)' % (cls, pr, la or 'no roundlook'))
            continue
        letter = mm.group(1).upper()
        if letter not in sizes:
            raise SystemExit('bullet: %s names RSBM%s and there is no such size' % (cls, letter))
        bn = rnds.get(pr, {}).get('ballistics') or (pr if pr in ball else None)
        sp = ball.get(bn, {}).get('speed') if bn else None
        if not sp:
            skipped.append('%s (%s: no ballistics speed)' % (cls, pr))
            continue
        upt = float(sp) * 34.0 / 35.0
        frames += ("\t\tif (gun == '%s')\n\t\t\treturn %d;\t// RSBM%s\n"
                   % (cls, ord(letter) - 65, letter))
        speeds += ("\t\tif (gun == '%s')\n\t\t\treturn %.1f;\t// %s m/s\n"
                   % (cls, upt, sp))
        log[cls] = dict(round=pr, frame='RSBM' + letter, speed_ms=float(sp),
                        units_per_tic=round(upt, 1))
    if not log:
        raise SystemExit('bullet: no gun resolved a model to draw')

    open(OUT_SRC + 'zscript/rsq/bullet.zs', 'w').write(
        BULLET_ZS % dict(frames=frames, speeds=speeds))
    zp = OUT_SRC + 'ZSCRIPT.rsvr'
    zt = open(zp).read()
    a = '#include "zscript/rsq/rounds.zs"\n'
    if zt.count(a) != 1:
        raise SystemExit('ZSCRIPT.rsvr: the rounds include is not there once (impacts runs first)')
    open(zp, 'w').write(zt.replace(a, a + '#include "zscript/rsq/bullet.zs"\n'))

    with open(OUT_SRC + 'CVARINFO.rsq', 'a') as f:
        f.write('\n// 1.97 F6: the round in flight. 1.0 is RS_Ballistics\' authored speed, which is\n'
                '// 330 to 874 map units a tic -- a streak, because that is what a real round is.\n'
                '// Lower to read it in the headset. It cannot change where anything lands: the\n'
                '// hitscan has already hit by the time this is drawn.\n'
                'user float rsq_round_speed = 1.0;\n')

    # the call site: the same event the impact already uses, so the two cannot disagree about
    # where the shot went
    p2 = OUT_SRC + 'zscript/rsq/ballistics.zs'
    t2 = open(p2).read()
    old = "\t\td /= len;\n\t\tImpact(e.Thing, e.DamagePosition - d * min(12, len), d, 24);\n"
    if t2.count(old) != 1:
        raise SystemExit('ballistics.zs: the WorldHitscanFired body is not as expected')
    t2 = t2.replace(old,
                    "\t\td /= len;\n"
                    "\t\t// 1.97 F6: the round itself, muzzle to where the shot actually landed.\n"
                    "\t\t// Same event as the impact below, so the two cannot disagree about it.\n"
                    "\t\tif (e.Thing.player && e.Thing.player.ReadyWeapon)\n"
                    "\t\t\tRSQ_Bullet.Fire(e.Thing, e.AttackPos, e.DamagePosition,\n"
                    "\t\t\t\te.Thing.player.ReadyWeapon.GetClassName());\n"
                    "\t\tImpact(e.Thing, e.DamagePosition - d * min(12, len), d, 24);\n")
    open(p2, 'w').write(t2)

    st = dict(guns=log, skipped=skipped)
    json.dump(st, open(OUT + 'bullet_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py bullet\n')
    print(json.dumps(dict(guns=len(log), skipped=len(skipped)), indent=1))


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

    # THE WEIGHT IS AUTHORED, NOT DERIVED (2026-10-24). Deriving it from kinetic energy --
    # (roundmass * speed^2) normalised on the 9mm, cube-rooted -- looked principled and was wrong
    # exactly where it mattered. `WorldHitscanFired` is raised once per PELLET: it is called from
    # inside P_LineAttack, and A_FireBullets calls P_LineAttack once per bullet. BD22's Shot_Gun,
    # SSG and AssaultShotgun all carry `shotpellets = 9` on the sheet. So one shotgun blast ran
    # Spall() NINE times at k = 1.659 -- on the order of fifteen times a 9mm's spall for one
    # trigger pull -- when RS_Ballistics says a buckshot pellet is 0.45, and says it in words:
    # "buckshot is per pellet, with no ricochet sound or light per pellet". The energy of nine
    # pellets together is not the weight of one of them.
    #
    # RSBDEFS' own `scale` IS the per-pellet authority, so read it rather than invent one. It
    # also reaches further than the ballistics chain did: roundprofile -> round.roundlook ->
    # roundlook.impact resolves 17 of 25 guns where energy resolved 10, picking up the rockets,
    # the plasma and both BFGs, which had no weight at all. The 8 it does not reach have no
    # roundprofile: four are melee or thrown, two are flamers that say outright "A FLAME IS NOT A
    # BULLET", and the Railgun and Unmaker name only a `trail`, which carries no `impact` key.
    def kindof(kind):
        out = {}
        for m in re.finditer(r'(?ms)^%s (\S+)[^\n]*\n(.*?)^end' % kind, defs):
            d = {}
            for k, v in re.findall(r'^\s*(\w+)\s*=\s*([^\n#]+)', m.group(2), re.M):
                d[k] = v.strip()
            out[m.group(1)] = d
        return out

    rnds, looks, imps = kindof('round'), kindof('roundlook'), kindof('impact')
    rows, log = '', {}
    for card, cls in CARD2CLS:
        g = guns.get(card, {})
        p = g.get('roundprofile')
        if not p:
            continue
        # a missing `round` block falls through to the roundlook of the same name, which is how
        # rocket / plasma_ball / bfg_ball / bfg_heavy / rocket_rpg resolve at all
        look = rnds.get(p, {}).get('roundlook') or (p if p in looks else None)
        base = looks.get(look, {}).get('impact') if look else None
        blk = imps.get(base) if base else None
        if not blk:
            continue
        k = round(float(blk.get('scale', '1.0').split(',')[0]), 3)
        rows += "\t\tcase '%s':\treturn %.3f;\t// %s -> impact %s\n" % (cls, k, p, base)
        log[cls] = dict(round=p, roundlook=look, impact=base, scale=k)
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
             '\t\t// NB the parameter is named `tracer` but RSQ_Tracer passes the SHOOTER:\n'
             '\t\t// h.Impact(shooter, lastPos, ...). Going through .target here finds nothing on a\n'
             '\t\t// player and every gun silently weighed 1.0.\n'
             '\t\tName gun = \'None\';\n'
             '\t\tif (tracer && tracer.player && tracer.player.ReadyWeapon)\n'
             '\t\t\tgun = tracer.player.ReadyWeapon.GetClassName();\n'
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
    txt = README % dict(ver=VERSION, pk3='BD22Q_%s.pk3' % VERSION.replace('.', ''),
                        nrsr=int(m.group(1)), nmenu=rows)
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
    log['slug_hands'] = slug_hands()
    json.dump(log, open(OUT + 'rev_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:          # bd22_mg.py opened it; this stage runs last
        f.write('then tools/bd22_plus.py revolver\n')
    print(json.dumps(log, indent=1))


# ---------------------------------------------------------------------------------------------
# F6: the ejection port, per gun.
#
# 1.38 gave four guns a hand-tuned port and left the rest throwing brass from the pawn. The
# obvious way to finish it was REMA's card: all 25 carry an `ejectport`. That way is WRONG, and
# the card says so itself -- every one of the 25 is annotated
#       "side measured (286 vertices on -y against 292 on +y) ... the point and the direction
#        are estimates"
# so what was measured is the SIDE, by counting vertices on each wall, and the point is a guess.
# Carried onto the held model by the exact rigid transform (residual 0.0000) it misses all four
# hand-tuned ports -- BrutalPistol by 3.8 cm, BrutalSMG by 10.8 cm. A guess transformed exactly
# is still a guess, so the card's point is not used here.
#
# WHAT IS MEASURED: the port is in the mesh. The model-makers named it --
#       Rifle     surface `ejectport`      Shot_Gun  surface `eject`
#       SSG       surface `Open`           Revolver  five surfaces `shells`, one per chamber
# -- and where nobody named it, it is still there as a HOLE: weld the ready frame's vertices and
# every edge used by one triangle only is a boundary, and the boundaries close into loops.
#
# THE PROOF, on the two guns that have both a modelled port and a hand-tuned number:
#       BrutalPistol    a 3.9 x 0.2 x 0.3 slot, 10 verts, facing right and up   0.84 units away
#       AssaultShotgun  a 7.8 x 0.7 x 2.0 slot, 10 verts, the same signature    0.44 units away
# Under a unit and a half on both, so the holes are the ports. On Shot_Gun the two readings agree
# with each other to 0.06 units (named surface 41.96, boundary loop 41.97), which is the third
# check. The four hand-tuned ports are NOT touched: they are the thing this was measured against.
#
# NOT DONE, and why -- these four have no port in their mesh to find:
#       MP40      every slot in `korpus` is mirrored at +-1.44: the receiver tube's cooling
#                 slots, not a port. `zamek` is the bolt (y +1.2 = the left-side handle).
#       Minigun   91 loops, all of them bores in `Pipe`. Six barrels and no port.
#       Machinegun  an M249 body with no port loop. Its ready frame IS now settled: 4.
#       MG42      no port loop, and buzzsaw_wm.md3 splits the body 3059+15853 where the pack's
#                 HitlersBuzzsaw.md3 has one surface of 18912, so no frame can be fitted either.
# Guessing those four would put brass somewhere arbitrary on the gun, which is what the card does.
#
# HOW IT LEAVES. RSBDEFS is explicit that two of these are not thrown at all:
#       ejecta brass_357          "dumped from a cylinder, not thrown by a port: slow, no glow"
#       ejecta hull_12ga_magnum   "the Super Shotgun's hulls, dumped from an open breech"
# so the Revolver, the Shotvolver and the SSG drop their cases down and back, slowly, instead of
# flicking them out to the right.

# ---------------------------------------------------------------------------------------------
# F6 item 9: the Shotvolver's hands, and the bug the hand-fit sheet turned up.
#
# Revolver2 is NOT in RSQ_HandTable.Index, and `Revolver2 : BrutalWeapon` so `w is 'Revolver'`
# does not catch it. It falls through to `return 0` -- index 0, the UNFITTED default. Its hands
# have been wrong in VR since F2 built the gun, and nothing said so because nothing checks.
#
# It draws sprite REVO on the Revolver's own mesh and has no MODELDEF block of its own, so its
# fit IS the Revolver's: index 17. That is a fact about the mesh, not a judgement.
#
# The sheet is for the owner to sign or reject. It renders that mesh at its ready frame with the
# gun's own points carried off REMA's card by the rigid transform (residual 0.0000; MODELDEF
# agrees -- `FrameIndex REVO A 0 0`). Note what it is NOT: the gun hand is FITTED FRESH to the
# card's palm for the picture, because handtable stores a runtime hook rather than a mesh-space
# placement. So the sheet shows where the card says the hand goes, not a readback of the shipped
# hook. The support hand is drawn at the same point as the gun hand, which is not a shortcut --
# row 17 carries GunHook and SupportHook as the IDENTICAL vector, because on a revolver the off
# hand cups the shooting hand rather than the gun. handfit_cards.fit_support says the same thing
# the hard way: "no gun surface at the support point". REMA's card says it in words, of the
# pistol: "PALM AND SUPPORTAT ARE THE SAME POINT ON PURPOSE ... two hands on a pistol cup each
# other on the handle's axis".
SLUG_FRAME = 0
SLUG_CARD = dict(palm=(-11.190, -0.104, -7.209), supportat=(-8.626, -0.104, -8.734),
                 triggerat=(-2.827, 0.039, -5.580), muzzle=(13.226, -0.031, 2.960))


def slug_hands():
    """Revolver2 -> the Revolver's hand fit, plus the check sheet."""
    import handfit_cards
    import hudrender
    import gunview
    from PIL import Image
    st = {}
    mesh = OUT_SRC + 'models/bd/Revolver/Revolver.md3'
    Rm, tv, mean, mx = rigid(REMA + 'models/bd22/revolver_wm.md3', mesh, SLUG_FRAME)
    if mean > 0.05:
        raise SystemExit('Revolver: the wm fit is %.4f, not ~0; the sheet would be drawn on the '
                         'wrong geometry' % mean)
    P = {k: (Rm @ np.array(v) + tv) for k, v in SLUG_CARD.items()}
    _, surfs = genpack.md3_surfaces(mesh)
    sh = [s for s in surfs if s['name'] == 'shells']
    if len(sh) != 5:
        raise SystemExit('Revolver: %d `shells` surfaces, expected 5 (one per chamber)' % len(sh))
    cyl = np.vstack([np.asarray(s['xyz'][SLUG_FRAME], float).mean(0) for s in sh]).mean(0)

    # the one line that matters
    hz = OUT_SRC + 'zscript/rsq/handtable.zs'
    t = open(hz).read()
    old = "\t\tif (w is 'Revolver')\treturn 17;"
    if t.count(old) != 1:
        raise SystemExit('handtable.zs: the Revolver row is not there exactly once')
    if "'Revolver2'" in t:
        raise SystemExit('handtable.zs: Revolver2 is already in; this stage has run twice')
    t = t.replace(old, old + "\n\t\tif (w is 'Revolver2')\treturn 17;"
                  "\t// 1.97: the Shotvolver draws sprite REVO on this same mesh and has no"
                  " MODELDEF of its own, so it is the Revolver's fit. Without this line it fell"
                  " through to 0, the unfitted default.")
    open(hz, 'w').write(t)
    st['handtable'] = "Revolver2 -> 17 (was falling through to 0, unfitted)"

    # the sheet
    ht = open(hz).read()

    def row_str(fn, i=17):
        m = re.search(r'static String %s\(int i\)\n\t\{\n\t\tstatic const String v\[\] = \{(.*?)\};'
                      % fn, ht, re.S)
        return [x.strip().strip('"') for x in m.group(1).split(',')][i]

    def row_vec(fn, i=17):
        m = re.search(r'static Vector3 %s\(int i\)\n\t\{\n\t\tstatic const double x\[\] = \{(.*?)\};\n'
                      r'\t\tstatic const double y\[\] = \{(.*?)\};\n'
                      r'\t\tstatic const double z\[\] = \{(.*?)\};' % fn, ht, re.S)
        return [float(g.split(',')[i]) for g in m.groups()]

    it = dict(path=mesh, frame=SLUG_FRAME, scale=[-1.0, 1.0, 1.0], off=[0.0, 0.0, -5.0],
              color=[150, 155, 170])
    gun_pts = handfit_cards.surface_points(it)
    two = [k for k, v in handfit_cards.GUN_LETTER.items() if v == row_str('GunTwo')][0]
    sup = [k for k, v in handfit_cards.SUP_LETTER.items() if v == row_str('Support')][0]
    tg, err, why = handfit_cards.fit_gun(gun_pts, P['palm'], 'hand:%d' % two)
    if tg is None:
        raise SystemExit('Revolver2 gun hand: ' + str(why))
    hk, sk = row_vec('GunHook'), row_vec('SupportHook')
    if hk != sk:
        raise SystemExit('handtable 17: GunHook %s and SupportHook %s differ, so the off hand is '
                         'NOT on the shooting hand and this sheet must fit it properly' % (hk, sk))
    items = [it, handfit_cards.hand_item('hand', two, np.array(tg)),
             handfit_cards.hand_item('hand2', sup, np.array(tg), color=(120, 200, 140))]

    # gunview draws the MESH through hudrender.to_local -> to_fl (the controller frame, cm) but
    # takes `marks` RAW. md3 units land nowhere near the gun.
    def fl(p):
        return tuple(gunview.to_fl(hudrender.to_local(np.array([p], float), it))[0])

    marks = [(*fl(P['palm']), 'palm', (255, 200, 60)),
             (*fl(P['supportat']), 'support', (120, 230, 140)),
             (*fl(P['triggerat']), 'trigger', (255, 120, 120)),
             (*fl(cyl), 'cylinder', (120, 160, 255)),
             (*fl(P['muzzle']), 'muzzle', (230, 230, 230))]
    os.makedirs(OUT + '_hands', exist_ok=True)
    a, b = OUT + '_hands/Revolver2.side.png', OUT + '_hands/Revolver2.bottom.png'
    gunview.view(items, a, 'side', px=5, marks=marks, title='Shotvolver (Revolver2) hands')
    gunview.view(items, b, 'bottom', px=5, marks=marks, title='Shotvolver (Revolver2) hands')
    A, B = Image.open(a), Image.open(b)
    O = Image.new('RGB', (max(A.width, B.width), A.height + B.height))
    O.paste(A, (0, 0))
    O.paste(B, (0, A.height))
    O.save(OUT + '_hands/Revolver2.png')
    os.remove(a)
    os.remove(b)
    st['sheet'] = '_hands/Revolver2.png'
    st['letters'] = dict(one=row_str('GunOne'), two=row_str('GunTwo'), sup=row_str('Support'),
                         trig=row_str('Trigger'))
    st['fit_err_cm'] = round(float(err), 2)
    st['wm_fit'] = dict(mean=round(mean, 4), max=round(mx, 4), frame=SLUG_FRAME)
    st['marks_cm'] = {lab: [round(x, 2) for x in m[:3]]
                      for m in marks for lab in [m[3]]}
    # the cylinder is also the casings port: two separate measurements that must agree
    st['cross_check'] = ('the cylinder reads F %.2f cm here and the casings stage put the '
                         'Revolver port at F 7.9 cm, measured independently'
                         % fl(cyl)[0])
    return st


# ---------------------------------------------------------------------------------------------
# F6 item 2, the rest of it: FOUR CARTRIDGES SHARE ONE CASING.
#
# BD22 throws `EmptyBrass` for the Rifle (5.56), the Minigun (5.56), the Machinegun (7.62) and
# the MG42 (7.92) at one size, and its 9mm brass is 2.25 map units long -- 6.6 cm at
# vr_vunits_per_meter 34, about three and a half times a real 9mm case. What it DOES get right,
# and what I assumed it got wrong: its three casings are already three sprite sets at three
# scales and three colours -- a 12-gauge hull really is red and 2.6x a pistol case today. The
# gap is between the rifle calibres, not between a hull and a 9mm.
#
# Each casing is scaled to the length of the round the gun actually fires, anchored on BD22's own
# 12-gauge so the shotgun is unchanged and everything else is measured against it:
#     mu per mm = (23 px * Scale 0.25) / 70.06 mm        BD22's ShotgunCasing, its own art
#     scale     = mm * (mu per mm) / this sprite's px
# Sprite widths are measured off brutal22test6.pk3 (C4S1 15, C4S2 23, C4S3 24, CLIN 17 px).
#
# WHERE THE LENGTHS COME FROM, because they are not all from one place:
#   19.20  RS_Ballistics' own casing_9mm.md3
#   44.70  its casing_rifle.md3
#   51.00  the same mesh at the 7.62 MODELDEF scale (44.70 * 0.03741 / 0.03279) -- RS's own ruler
#   70.06  its shell_12ga.md3
#   57.00  the real 7.92x57 Mauser. NOT RS's: `ejecta ww2_mg42` is the 9mm mesh at scale 1.35,
#          a 25.9 mm case, which is not a Mauser round. RS's own profile is wrong here.
#   76.20  the real 12ga 3" magnum. NOT RS's: `hull_12ga` and `hull_12ga_magnum` differ ONLY in
#          portsmoke and wisp, both PARTICLEDEFS keys, so on stock the two are byte-identical
#          and the magnum would read as a standard hull.
#
# NOT CHANGED, deliberately: the Revolver. REMA's sheet gives it `brass_357`, but BD22's Revolver
# takes `Weapon.AmmoType1 "AmmoShell"`, carries `shotpellets = 9`, and fires SSGCaseSpawner -- it
# is a BUCKSHOT revolver and the red hull it throws is correct. A .357 case here would be a
# regression dressed as a fix.
CASE_ANCHOR = (23, 0.25, 70.06)          # BD22's ShotgunCasing: sprite px, its Scale, hull mm
CASE_SIZES = [
    # casing class, sprite px, mm, label, the gun classes that throw it
    ('PistolCasing', 15, 19.20, '9x19, casing_9mm.md3',
     ['BrutalPistol', 'BrutalSMG', 'MP40']),
    ('EmptyBrass', 24, 44.70, '5.56x45, casing_rifle.md3',
     ['Rifle', 'Minigun']),
    ('EmptyBrass', 24, 51.00, '7.62x51, the same mesh at its 7.62 MODELDEF scale',
     ['Machinegun']),
    ('EmptyBrass', 24, 57.00, '7.92x57 Mauser, the real round: RS has no mesh for it',
     ['MG42']),
    ('ShotgunCasing', 23, 76.20, '12ga 3in magnum, the real round: RS cannot tell it from 2.75in',
     ['SSG']),
]


# How the case leaves, which is three different things and not two:
#   SIDE  flicked out of a port in the receiver wall, to the gun's right. The default.
#   DOWN  thrown out of a chute in the receiver FLOOR, under its own gas pressure. The MG42.
#   TIP   not thrown at all -- tipped out by the shooter, slowly. RSBDEFS is explicit:
#         `brass_357` is "dumped from a cylinder, not thrown by a port: slow, no glow" and
#         `hull_12ga_magnum` is "dumped from an open breech". A belt gun at 1200 rpm is NOT
#         this, which is why DOWN exists separately: same direction, nothing like the speed.
SIDE, DOWN, TIP = 0, 1, 2

EJECT = [
    # class, the class whose MODELDEF block holds the mesh, REMA wm, ready frame (residual 0.0000
    # against it), surface(s) OR a hole box, what it is, how the case leaves
    ('Shot_Gun', 'Shot_Gun', 'shotgun_wm.md3', 4, ['eject'], None,
     'the port the model-maker named `eject`', SIDE),
    ('SSG', 'SSG', 'ssg_wm.md3', 1, ['Open'], None,
     'the break-open breech, surface `Open`', TIP),
    ('Revolver', 'Revolver', 'revolver_wm.md3', 0, ['shells'], None,
     'the cylinder: the mean of its five `shells`', TIP),
    # the Shotvolver draws on sprite REVO and has no MODELDEF block of its own: it IS the
    # Revolver's mesh, so it is the Revolver's port.
    ('Revolver2', 'Revolver', 'revolver_wm.md3', 0, ['shells'], None,
     'the Shotvolver, on the Revolver\'s own mesh', TIP),
    # THE MG42, once its mesh could be matched at all (see BUTT). Nobody named its port and it
    # has none in either wall -- the regular loops down its flank at x 68..108 are the barrel
    # jacket's cooling slots, which is what fooled me into writing it off. A real MG42 ejects
    # DOWNWARD, and the chute is there in the floor of the receiver: one flat opening, 10.1 long
    # and 2.8 wide, centred on the gun (y -0.04) and below the bore (z -0.57), directly under the
    # breech. The box below is the rule that picks it, and the stage stops if it ever picks two:
    # a down-facing loop under the bore, near the breech, centred, and of a size a 7.92 case fits.
    ('MG42', 'MG42', 'buzzsaw_wm.md3', 0, None,
     dict(axis=2, facing=(0.6, 1.0), z=(-5.0, 2.0), x=(35.0, 55.0), off_centre=(0.0, 1.5),
          long=(5.0, 15.0), wide=(1.0, 6.0)),
     'the chute in the receiver floor, the hole itself', DOWN),
]
WEAPON_SCALE = 1.02          # vr_weaponScale's default, the scale melee.zs's Place() applies


def md3_tris(path):
    """genpack.md3_surfaces keeps the vertices and drops the triangles; a hole needs both."""
    import struct
    d = open(path, 'rb').read()
    nsurf, osurf = struct.unpack_from('<8i', d, 76)[2], struct.unpack_from('<8i', d, 76)[6]
    out, off = [], osurf
    for _ in range(nsurf):
        nt, otri, oend = struct.unpack_from('<10i', d, off + 68)[4], \
            struct.unpack_from('<10i', d, off + 68)[5], struct.unpack_from('<10i', d, off + 68)[9]
        out.append(np.frombuffer(d, dtype='<i4', count=nt * 3, offset=off + otri).reshape(nt, 3).copy())
        off += oend
    return out


def boundary_loops(V, T):
    """Every closed boundary of one surface: weld by position, take the edges that belong to a
    single triangle, walk them into connected groups. A modelled port IS one of these."""
    _, inv = np.unique(np.round(V, 3), axis=0, return_inverse=True)
    W, edge = inv[T], {}
    for a, b, c in W:
        for u, v in ((a, b), (b, c), (c, a)):
            k = (u, v) if u < v else (v, u)
            edge[k] = edge.get(k, 0) + 1
    adj = {}
    for u, v in [k for k, m in edge.items() if m == 1]:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    pos = {}
    for i, w in enumerate(inv):
        pos.setdefault(w, V[i])
    seen, out = set(), []
    for start in adj:
        if start in seen:
            continue
        stack, grp = [start], []
        seen.add(start)
        while stack:
            k = stack.pop()
            grp.append(k)
            for m in adj[k]:
                if m not in seen:
                    seen.add(m)
                    stack.append(m)
        P = np.vstack([pos[g] for g in grp])
        c = P.mean(0)
        nrm = np.zeros(3) if P.shape[0] < 3 else np.linalg.svd(P - c, full_matrices=False)[2][2]
        out.append((c, P.max(0) - P.min(0), len(grp), nrm))
    return out


def eject_port(cls, frame, names, hole=None):
    """Where the brass leaves, in the held model's own units and then in the (forward, left, up)
    cm casings.zs speaks -- Place()'s arithmetic read backwards: f = .01*(ws*m.x - 30),
    r = .01*(-ws*m.y), u = .01*(ws*m.z), and casings' L is melee's -R.

    `names`: the surface the model-maker named the port. `hole`: a box the port's boundary loop
    must fall in, for a gun where nobody named it -- and exactly one loop must, or this stops."""
    md = open(OUT_SRC + 'MODELDEF.bd.txt', encoding='latin-1').read()
    b = re.search(r'(?mi)^Model %s\s*$.*?^\}' % re.escape(cls), md, re.S)
    if not b:
        raise SystemExit('MODELDEF.bd.txt: no block for ' + cls)
    pa = re.search(r'Path\s+"([^"]+)"', b.group(0)).group(1)
    mo = re.search(r'Model 0 "([^"]+)"', b.group(0)).group(1)
    path = OUT_SRC + pa + '/' + mo
    n, surfs = genpack.md3_surfaces(path)
    if frame >= n:
        raise SystemExit('%s: frame %d but the mesh has %d' % (cls, frame, n))
    if hole:
        found = []
        for s, t in zip(surfs, md3_tris(path)):
            for c, span, nv, nrm in boundary_loops(np.asarray(s['xyz'][frame], float), t):
                if all(lo <= v <= hi for v, (lo, hi) in
                       ((abs(nrm[hole['axis']]), hole['facing']), (c[2], hole['z']),
                        (c[0], hole['x']), (abs(c[1]), hole['off_centre']),
                        (span[0], hole['long']), (span[1], hole['wide']))):
                    found.append((c, span, nv))
        if len(found) != 1:
            raise SystemExit('%s: the port box matches %d boundary loops, not 1: %s'
                             % (cls, len(found), [(np.round(f[0], 2).tolist()) for f in found]))
        c, span, nv = found[0]
        port = (WEAPON_SCALE * c[0] - 30.0, WEAPON_SCALE * c[1], WEAPON_SCALE * c[2])
        return c, port, nv, '%s/%s' % (pa, mo)
    hit = [s for s in surfs if s['name'] in names]
    if not hit:
        raise SystemExit('%s: no surface named %s (it has %s)'
                         % (cls, names, [s['name'] for s in surfs]))
    c = np.vstack([np.asarray(s['xyz'][frame], float).mean(0) for s in hit]).mean(0)
    port = (WEAPON_SCALE * c[0] - 30.0, WEAPON_SCALE * c[1], WEAPON_SCALE * c[2])
    return c, port, len(hit), '%s/%s' % (pa, mo)


def casings():
    """F6: the three guns whose ejection port is actually in the mesh, and the two that dump."""
    p = OUT_SRC + 'zscript/rsq/casings.zs'
    t = open(p).read()
    st, lines = {}, ''
    for cls, meshcls, wm, fr, names, hole, what, mode in EJECT:
        c, port, nsurf, mesh = eject_port(meshcls, fr, names, hole)
        port = tuple(round(x, 1) + 0.0 for x in port)       # round FIRST: -0.026 prints as -0.0
        test = "if (w is '%s')" % cls
        tabs = max(1, (40 - (8 + len(test)) + 3) // 4)      # `return` at column 40, as the four above
        lines += ("\t\t%s%sreturn (%.1f, %.1f, %.1f);\t// 1.97: %s\n"
                  % (test, '\t' * tabs, port[0], port[1], port[2], what))
        st[cls] = dict(mesh=mesh, ready_frame=fr, ref=wm, surfaces=names, surface_count=nsurf,
                       model_units=[round(float(x), 3) for x in c],
                       port_cm=[round(x, 1) for x in port], measured=what,
                       leaves=['flicked out of a side port', 'thrown down a chute',
                               'tipped out by hand'][mode])

    # the header names the four 1.38 shipped with; it is not the four any more
    head = "// ready frame (kitbash/ports.png).\n"
    if t.count(head) != 1:
        raise SystemExit('casings.zs: the 1.38 header is not there exactly once')
    t = t.replace(head, head +
                  "// 1.97: and of the pump gun, the SSG, the Revolver and the Shotvolver. Those four are\n"
                  "// measured off the held mesh -- the surface the model-maker named, or the hole itself --\n"
                  "// NOT from WMCARD.bd22, whose ejectport every one of the 25 cards annotates \"the point\n"
                  "// and the direction are estimates\", and which misses all four of the ports above by\n"
                  "// between 0.8 and 10.8 cm. See tools/bd22_plus.py casings for the measurement and the\n"
                  "// four guns whose mesh has no port in it at all.\n")

    anchor = "\t\tif (w is 'AssaultShotgun')\t\treturn (16.0, -1.4, -0.6);\n\t\treturn (0, 0, 0);\n"
    if t.count(anchor) != 1:
        raise SystemExit('casings.zs: the four hand-tuned ports are not there as expected')
    t = t.replace(anchor, "\t\tif (w is 'AssaultShotgun')\t\treturn (16.0, -1.4, -0.6);\n"
                  + lines + "\t\treturn (0, 0, 0);\n")

    # per-cartridge casing size (CASE_SIZES above)
    px_a, sc_a, mm_a = CASE_ANCHOR
    mupermm = px_a * sc_a / mm_a
    sz, szlog = '', {}
    for casing, px, mm, why, classes in CASE_SIZES:
        s = round(mm * mupermm / px, 4)
        for cls in classes:
            sz += ("\t\tif (gun == '%s' && casing == '%s')\n\t\t\treturn %.4f;"
                   "\t// 1.97: %s\n" % (cls, casing, s, why))
            szlog[cls] = dict(casing=casing, mm=mm, scale=s, source=why)
    t = t.replace("\t// the player who fired:",
                  "\t// 1.97: BD22 throws one EmptyBrass for the Rifle (5.56), the Minigun (5.56),\n"
                  "\t// the Machinegun (7.62) and the MG42 (7.92), and its 9mm brass is 2.25 map\n"
                  "\t// units -- about three and a half times a real case. Each casing is scaled to\n"
                  "\t// the round the gun actually fires, anchored on BD22's OWN 12-gauge (23 px at\n"
                  "\t// Scale 0.25 for a 70.06 mm hull), so the shotgun is unchanged and everything\n"
                  "\t// else is measured against it. 0 = leave BD22's own size alone.\n"
                  "\t//\n"
                  "\t// The Revolver is deliberately NOT here. REMA's sheet calls it brass_357, but\n"
                  "\t// BD22's Revolver takes AmmoType1 \"AmmoShell\", carries shotpellets = 9 and\n"
                  "\t// fires SSGCaseSpawner: it is a BUCKSHOT revolver and its red hull is right.\n"
                  "\tstatic double Size(Name gun, Name casing)\n\t{\n" + sz + "\t\treturn 0;\n\t}\n\n"
                  "\t// the player who fired:", 1)
    st['_sizes'] = szlog

    # how the case leaves: three things, not two
    thr = ''.join("\t\tif (w is '%s')\n\t\t\treturn %s;\n" % (cls, ['SIDE', 'DOWN', 'TIP'][m])
                  for cls, _, _, _, _, _, _, m in EJECT if m)
    t = t.replace("\t// the player who fired:",
                  "\t// 1.97: not every gun throws its case the same way, and it is three things.\n"
                  "\t// SIDE is flicked out of a port in the receiver wall, which is the default and\n"
                  "\t// what 1.38 wrote. DOWN is thrown out of a chute in the receiver FLOOR under the\n"
                  "\t// gun's own gas -- the MG42, whose port is exactly that and nothing in either\n"
                  "\t// wall. TIP is not thrown at all: RSBDEFS calls brass_357 \"dumped from a\n"
                  "\t// cylinder, not thrown by a port: slow, no glow\" and hull_12ga_magnum \"dumped\n"
                  "\t// from an open breech\", so the shooter tips those out. A belt gun at 1200 rpm is\n"
                  "\t// NOT that, which is why DOWN is its own: the same direction, nothing like the speed.\n"
                  "\tconst SIDE = 0;\n\tconst DOWN = 1;\n\tconst TIP = 2;\n\n"
                  "\tstatic int Throw(Weapon w)\n\t{\n" + thr + "\t\treturn SIDE;\n\t}\n\n"
                  "\t// the player who fired:", 1)

    old = ("\t\t// out to the right and up, a little back, as each gun's own casing speed\n"
           "\t\tVector3 d = -L * 0.75 + U * frandom(0.45, 0.7) - F * frandom(0.05, 0.25);\n")
    if t.count(old) != 1:
        raise SystemExit('casings.zs: the flick is not there exactly once')
    t = t.replace(old,
                  "\t\t// out of the port, each gun its own way, at its own casing speed\n"
                  "\t\tVector3 d;\n"
                  "\t\tdouble slow = 1.0;\n"
                  "\t\tint mode = Throw(w);\n"
                  "\t\tif (mode == TIP)\n\t\t{\n"
                  "\t\t\td = -U * frandom(0.8, 1.0) - F * frandom(0.1, 0.3) + L * frandom(-0.25, 0.25);\n"
                  "\t\t\tslow = frandom(0.35, 0.5);\n"
                  "\t\t}\n"
                  "\t\telse if (mode == DOWN)\n"
                  "\t\t\td = -U * frandom(0.85, 1.0) - F * frandom(0.0, 0.2) + L * frandom(-0.3, 0.3);\n"
                  "\t\telse\n"
                  "\t\t\td = -L * 0.75 + U * frandom(0.45, 0.7) - F * frandom(0.05, 0.25);\n")

    # the MG42's links come out of that same chute, and are EmptyBrass's own subclass, but the
    # filter matches on the exact class name so they were never caught. (Minigun, Machinegun and
    # the MG42 all spawn them; the two with no port return early on Port() == (0, 0, 0).)
    old = ("\t\tif (n != 'PistolCasing' && n != 'EmptyBrass' && n != 'ShotgunCasing')\n")
    if t.count(old) != 1:
        raise SystemExit('casings.zs: the class filter is not there exactly once')
    t = t.replace(old, "\t\tif (n != 'PistolCasing' && n != 'EmptyBrass' && n != 'ShotgunCasing'\n"
                       "\t\t\t&& n != 'MGLinks')\n")

    # Size() runs HERE, at spawn, and not in Place(): Place returns early on Port() == (0,0,0),
    # and the Machinegun, the Minigun and the MP40 have no port, so a casing from those three
    # would never be reached. Scaling is also the one thing that is right whether or not we know
    # where the brass came out of.
    old = "\t\tpend.Push(c);\n"
    if t.count(old) != 1:
        raise SystemExit('casings.zs: the pend.Push is not there exactly once')
    t = t.replace(old,
                  "\t\tdouble sz = Size(mo.player.ReadyWeapon ? mo.player.ReadyWeapon.GetClassName()"
                  " : 'None', n);\n"
                  "\t\tif (sz > 0)\n\t\t\tc.A_SetScale(sz, sz);\n"
                  "\t\tpend.Push(c);\n")
    old = "\t\tc.vel = d * spd + mo.vel;\n"
    if t.count(old) != 1:
        raise SystemExit('casings.zs: the velocity line is not there exactly once')
    t = t.replace(old, "\t\tc.vel = d * spd * slow + mo.vel;\n")
    open(p, 'w').write(t)

    st['_not_done'] = {
        'MP40': 'every korpus slot is mirrored at +-1.44 (the tube\'s cooling slots); `zamek` is the bolt',
        'Minigun': '91 boundary loops, all bores in `Pipe`: six barrels and no port',
        'Machinegun': 'an M249 body with no port loop (its ready frame is settled: 4)',
        'MG42': 'no port loop, and buzzsaw_wm.md3 splits the body 3059+15853 against one surface of 18912',
    }
    st['_card_rejected'] = ('WMCARD.bd22 ejectport: all 25 say "the point and the direction are '
                            'estimates"; carried exactly it misses the four hand-tuned ports by '
                            '0.8 to 10.8 cm')
    json.dump(st, open(OUT + 'casings_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py casings\n')
    print(json.dumps(st, indent=1))


# ---------------------------------------------------------------------------------------------
# F6 item 4: what a round does when it ARRIVES.
#
# Until now the entire difference between guns at a hit was one scalar on three particle counts.
# The pack had NO impact sound, NO ricochet and NO impact light -- grep ballistics.zs for
# A_StartSound or A_AttachLight before this stage and the count is zero. RS_Ballistics has all
# three, and all three are plain ZScript calls that stock GZDoom 4.14.3 makes, so they cross.
#
# WHAT CROSSES AND WHAT DOES NOT. Of the 21 keys in an `impact` block, 8 cross cleanly (`sound`,
# `tail`, `glance` degrees, `light`, `lightcolor`, `scale`, `vary`, `maybe`); `bursts` crosses in
# shape but not texture (40 of the ~44 our guns name resolve a PARTICLEDEFS particle, a REMA
# renderer feature); `hotspot` crosses as mechanism with nothing left to carry; `mark` has only a
# lossy stand-in. Nine are hard NO and are left behind rather than faked: `damage` and
# `glancedamage` (the engine's RGBA wall-damage brushes -- soot, hole depth, heat, wet -- painted
# onto geometry; stock has no surface-paint channel), `heat` (a post-process shimmer),
# `smokevolume` and `volume` (VOLUMEDEFS emissive/volumetric smoke), `exposure` and `hearing`
# (the engine's sensory impulses -- flash blindness and ear ringing), `ripple` (SpawnShockwave)
# and `push` (which shoves smoke volumes, of which there are none here).
#
# SOUND IS PER MATERIAL, NOT PER GUN. Checked across all eight bullet bases our guns resolve to:
# every one of them names the same sound for a given material. So there is one table of 15, not
# eight tables. Ricochet and light ARE per gun, and that is where the character lives: a magnum
# skips off stone inside 20 degrees where a rifle needs 14, and nine buckshot pellets never
# ricochet at all -- RSBDEFS is explicit that buckshot carries "no ricochet sound or light per
# pellet", which is also why the shotguns are absent from both tables below.
HIT_SOUNDS = [
    # the pack's RSQ_Surfaces.Of() answers one of these, or `concrete` when nothing matches
    (['concrete', 'dirt', 'brick', 'marble', 'tile'], 'rsb/impact/concrete'),
    (['metal'], 'rsb/impact/metal'),
    (['wood'], 'rsb/impact/wood'),
    (['glass', 'screen', 'light'], 'rsb/glass'),
    (['tech'], 'rsb/impact/electric'),
    (['pipe'], 'rsb/impact/pipe'),
    (['lava'], 'rsb/flame/hiss'),
    # liquid and slime are `sound = none` in every block: a round into water is the splash's job
]
HIT_SNDDIRS = ['impact_concrete', 'impact_metal', 'impact_wood', 'glass', 'ricochet',
               'impact_electric', 'impact_pipe', 'flame']
HIT_SNDSETS = ['rsb/impact/concrete', 'rsb/impact/metal', 'rsb/impact/wood', 'rsb/glass',
               'rsb/ricochet', 'rsb/impact/electric', 'rsb/impact/pipe', 'rsb/flame/hiss']
# the surfaces that take the wider, metallic ricochet angle, per RSBDEFS' own .metal/.pipe/.tech
HIT_HARD = ['metal', 'pipe', 'tech']

HIT_ZS = '''// hit.zs (1.97, F6) -- GENERATED by tools/bd22_plus.py hits. Do not edit by hand.
//
// What a round does when it ARRIVES: the sound, the ricochet and the light. Until this file the
// pack had none of the three -- every gun's impact differed by one multiplier on three particle
// counts and nothing else. The numbers are RS_Ballistics' own `impact` blocks, reached by
// roundprofile -> round.roundlook -> roundlook.impact, and only the keys stock GZDoom can make
// good on are carried.
//
// SOUND IS PER MATERIAL. Every one of the eight bullet bases our guns resolve to names the same
// sound for a given material, so this is one table and not eight. RICOCHET AND LIGHT ARE PER
// GUN, and that is where a gun's character at the far end actually lives.
//
// THE SHOTGUNS ARE ABSENT FROM RICOCHET AND LIGHT ON PURPOSE. WorldHitscanFired is raised once
// per pellet and BD22's shotguns throw nine, so a per-pellet ricochet would be nine ricochets
// off one trigger pull. RSBDEFS says the same in words -- buckshot carries "no ricochet sound or
// light per pellet" -- and its buckshot blocks carry no `glance` and no `light`.
//
// Rides rsq_ballistics, the same dial as the rest of the pack's effects: at Stock it is silent
// and dark, because Stock means Brutal Doom's own and nothing of ours.
class RSQ_ImpactLight : Actor
{
\tDefault
\t{
\t\t+NOINTERACTION;
\t\t+NOBLOCKMAP;
\t\t+NOGRAVITY;
\t\t+DONTSPLASH;
\t\tRenderStyle "None";
\t}
\tStates
\t{
\tSpawn:
\t\tTNT1 A 1;
\t\tStop;
\t}
}

// `play`, not the default data scope: At() spawns the light actor, and Spawn is a play
// function. The pack's own RSM is declared the same way for the same reason.
class RSQ_Hit abstract play
{
\t// per MATERIAL. "" means the data says `sound = none` -- liquid and slime, where the
\t// splash is the sound.
\tstatic String SoundFor(Name s)
\t{
%(sounds)s\t\treturn "rsb/impact/concrete";
\t}

\t// degrees of grazing angle inside which the round skips off instead of biting, per gun.
\t// 0 = this gun never ricochets.
\tstatic double Glance(Name gun, Name s)
\t{
\t\tbool hard = %(hard)s;
%(glance)s\t\treturn 0;
\t}

\t// radius, and the tics it lives, of the flash a round strikes off a surface. Only the hot
\t// surfaces are lit, which is RSBDEFS' own choice and keeps this cheap on a Quest.
\tstatic int LightRadius(Name gun, Name s)
\t{
%(lightrad)s\t\treturn 0;
\t}

\tstatic int LightTics(Name s)
\t{
%(lighttics)s\t\treturn 3;
\t}

\tstatic Color LightTint(Name s)
\t{
%(lighttint)s\t\treturn Color(255, 190, 120);
\t}

\tstatic void At(Actor src, Vector3 pos, Vector3 n, Vector3 dir, Name s, Name gun)
\t{
\t\tif (!src)
\t\t\treturn;
\t\tlet l = Actor.Spawn('RSQ_ImpactLight', pos);
\t\tif (!l)
\t\t\treturn;

\t\t// the ricochet first: it decides which sound this hit makes. The test is RS_Ballistics'
\t\t// own -- the shallower the angle onto the surface, the more likely the round skips --
\t\t// and dir dot n is the cosine of the angle off the surface's face.
\t\tdouble g = Glance(gun, s);
\t\tbool ric = g > 0 && abs(dir dot n) < sin(g);
\t\tString snd = ric ? "rsb/ricochet" : SoundFor(s);
\t\tif (snd != "")
\t\t\tl.A_StartSound(snd, CHAN_AUTO, CHANF_OVERLAP, 1.0);

\t\tint rad = LightRadius(gun, s);
\t\tif (rad > 0)
\t\t{
\t\t\tl.A_AttachLight('rsqhit', DynamicLight.PointLight, LightTint(s), rad, 0,
\t\t\t\tDynamicLight.LF_ATTENUATE);
\t\t\tl.tics = LightTics(s);
\t\t}
\t\telse
\t\t\tl.tics = 1;
\t}
}
'''


def hits():
    """F6: impact sound, ricochet and light -- the three the pack had none of."""
    import shutil
    defs = open(RSVRW + '../RS_Ballistics/RSBDEFS.txt', encoding='latin-1').read() \
        if os.path.exists(RSVRW + '../RS_Ballistics/RSBDEFS.txt') \
        else open('E:/DOOMWork/RS_Ballistics/RSBDEFS.txt', encoding='latin-1').read()
    RSB = 'E:/DOOMWork/RS_Ballistics/'
    sheet = open(REMA + 'WMSHEET.bd22', encoding='latin-1').read()

    def kindof(kind, text=None):
        out = {}
        for m in re.finditer(r'(?ms)^%s (\S+)[^\n]*\n(.*?)^end' % kind, text or defs):
            d = {}
            for k, v in re.findall(r'^\s*(\w+)\s*=\s*([^\n#]+)', m.group(2), re.M):
                d[k] = v.strip()
            out[m.group(1)] = d
        return out

    guns, cur = {}, None
    for ln in sheet.splitlines():
        s = ln.split('#')[0].strip()
        m = re.match(r'gun\s+"([^"]+)"', s)
        if m:
            cur = m.group(1)
            guns[cur] = {}
            continue
        m = re.match(r'(\w+)\s*=\s*(.+)$', s)
        if m and cur:
            guns[cur][m.group(1)] = m.group(2).strip().strip('"')

    rnds, looks, imps = kindof('round'), kindof('roundlook'), kindof('impact')
    st = {'guns': {}, 'skipped': []}
    glance, lightrad = '', ''
    for card, cls in CARD2CLS:
        p = guns.get(card, {}).get('roundprofile')
        look = rnds.get(p, {}).get('roundlook') or (p if p in looks else None) if p else None
        base = looks.get(look, {}).get('impact') if look else None
        if not base or base not in imps:
            st['skipped'].append('%s (%s)' % (cls, p or 'no roundprofile'))
            continue
        soft, hard = imps.get(base, {}), imps.get(base + '.metal', {})
        gs = soft.get('glance', '').split(',')[0].strip()
        gh = hard.get('glance', '').split(',')[0].strip()
        row = dict(impact=base)
        if gs or gh:
            glance += ("\t\tif (gun == '%s')\n\t\t\treturn hard ? %s : %s;\t// impact %s\n"
                       % (cls, gh or gs or '0', gs or '0', base))
            row['glance'] = dict(soft=gs or None, hard=gh or None)
        lh = hard.get('light', '')
        if lh:
            r = lh.split(',')[0].strip()
            lightrad += ("\t\tif (gun == '%s' && hard_surface(s))\n\t\t\treturn %s;\t// impact %s.metal\n"
                         % (cls, r, base))
            row['light_metal'] = lh
        if row.get('glance') or row.get('light_metal'):
            st['guns'][cls] = row

    sounds = ''
    for mats, snd in HIT_SOUNDS:
        sounds += ("\t\tif (%s)\n\t\t\treturn \"%s\";\n"
                   % (' || '.join("s == '%s'" % m for m in mats), snd))
    sounds += "\t\tif (s == 'liquid' || s == 'slime')\n\t\t\treturn \"\";\n"

    # the material-wide lights, straight off the blocks that carry them
    tintrows, ticrows = '', ''
    seen = {}
    for mat in ('tech', 'screen', 'light', 'lava'):
        for b in ('pistol_9mm', 'rifle', 'magnum'):
            blk = imps.get('%s.%s' % (b, mat))
            if blk and 'light' in blk:
                seen[mat] = (blk['light'], blk.get('lightcolor', '255,190,120'))
                break
    for mat, (lt, lc) in seen.items():
        r, _, tc = [x.strip() for x in lt.split(',')][:3]
        rgb = [int(float(x)) for x in lc.split(',')][:3]
        lightrad += ("\t\tif (s == '%s')\n\t\t\treturn %s;\t// every gun, on %s\n" % (mat, r, mat))
        ticrows += "\t\tif (s == '%s')\n\t\t\treturn %s;\n" % (mat, tc)
        tintrows += ("\t\tif (s == '%s')\n\t\t\treturn Color(%d, %d, %d);\n" % (mat, *rgb))

    zs = HIT_ZS % dict(sounds=sounds, glance=glance, lightrad=lightrad,
                       lighttics=ticrows, lighttint=tintrows,
                       hard=' || '.join("s == '%s'" % h for h in HIT_HARD))
    zs = zs.replace('hard_surface(s)', '(%s)' % ' || '.join("s == '%s'" % h for h in HIT_HARD))
    open(OUT_SRC + 'zscript/rsq/hit.zs', 'w').write(zs)

    # the sounds: copy the sets we name, and lift their SNDINFO verbatim (full paths, so a short
    # lump name in another package cannot shadow them -- RS's own reason for writing them that way)
    snd = open(RSB + 'SNDINFO.txt', encoding='latin-1').read()
    keep, n_files = [], 0
    for d in HIT_SNDDIRS:
        src, dst = RSB + 'sounds/rsb/' + d, OUT_SRC + 'sounds/rsb/' + d
        if not os.path.isdir(src):
            raise SystemExit('hits: no sound folder %s' % src)
        os.makedirs(dst, exist_ok=True)
        for f in os.listdir(src):
            shutil.copy(src + '/' + f, dst + '/' + f)
            n_files += 1
    # MATCH THE SET NAME EXACTLY, not as a prefix. `rsb/impact/metal` prefixes
    # `rsb/impact/metalthin`, so a plain startswith lifted six metalthin definitions whose .ogg
    # files are not shipped -- SNDINFO pointing at lumps that are not there. Caught by walking
    # every `name  sounds/....ogg` line in the result and checking the file is in the pack.
    def wanted(s):
        for x in HIT_SNDSETS:
            if re.match(re.escape(x) + r'\d+\s', s):          # a numbered variation
                return True
            if re.match(r'\$(random|limit)\s+' + re.escape(x) + r'(\s|\{|$)', s):
                return True
        return False

    for ln in snd.splitlines():
        if wanted(ln.strip()):
            keep.append(ln)
    if not keep:
        raise SystemExit('hits: no SNDINFO lines matched the sets being shipped')
    want_files = set()
    for ln in keep:
        m = re.match(r'^\s*\S+\s+(sounds/\S+\.ogg)\s*$', ln)
        if m:
            want_files.add(m.group(1))
    gone = sorted(f for f in want_files if not os.path.exists(OUT_SRC + f))
    if gone:
        raise SystemExit('hits: SNDINFO would name %d sounds the pack does not ship: %s'
                         % (len(gone), gone[:4]))
    with open(OUT_SRC + 'SNDINFO.rsq', 'a') as f:
        f.write('\n// 1.97 F6: impact sounds, lifted from RS_Ballistics with their full paths, so a\n'
                '// short lump name in another package cannot shadow them (RS\'s own reasoning).\n'
                + '\n'.join(keep) + '\n')
    st['sounds'] = dict(files=n_files, sndinfo_lines=len(keep), sets=HIT_SNDSETS)

    # the call site
    p = OUT_SRC + 'zscript/rsq/ballistics.zs'
    t = open(p).read()
    old = ("\t\tSpall(t.HitLocation + n * 2, n, surf.Of(t.HitTexture, flat),\n"
           "\t\t\t(FxLevel() >= 2 ? 1.8 : 1.0) * RSQ_Rounds.Scale(gun));\n")
    if t.count(old) != 1:
        raise SystemExit('ballistics.zs: the Spall call is not there exactly once')
    t = t.replace(old,
                  "\t\tName sname = surf.Of(t.HitTexture, flat);\n"
                  "\t\tVector3 hp = t.HitLocation + n * 2;\n"
                  "\t\t// 1.97 F6: the sound, the ricochet and the light, which the pack had none of\n"
                  "\t\tRSQ_Hit.At(tracer, hp, n, dir, sname, gun);\n"
                  "\t\tSpall(hp, n, sname, (FxLevel() >= 2 ? 1.8 : 1.0) * RSQ_Rounds.Scale(gun));\n")
    open(p, 'w').write(t)

    zp = OUT_SRC + 'ZSCRIPT.rsvr'
    zt = open(zp).read()
    a = '#include "zscript/rsq/rounds.zs"\n'
    if zt.count(a) != 1:
        raise SystemExit('ZSCRIPT.rsvr: the rounds include is not there once (impacts runs first)')
    open(zp, 'w').write(zt.replace(a, a + '#include "zscript/rsq/hit.zs"\n'))

    json.dump(st, open(OUT + 'hits_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py hits\n')
    print(json.dumps(dict(guns=len(st['guns']), skipped=len(st['skipped']),
                          sound_files=n_files, sndinfo=len(keep)), indent=1))


POSE_ZS = '''// pose.zs (1.97, F7) -- GENERATED by tools/bd22_plus.py pose. Do not edit by hand.
//
// THE SPINE. `VR_MELEE_ON_QUESTZDOOM_2026-10-24.md` Part Two section 9 calls this "the single
// highest-leverage thing in the three codebases": a per-player pose history, fed once a tic by a
// netevent from the console player, read ONLY from the history by everyone INCLUDING THE SENDER.
//
// WHY IT HAS TO EXIST. Stock QuestZDoom writes AttackPos / OffhandPos and their three angles on
// the CONSOLE PLAYER'S PAWN ONLY, from the renderer (hw_vrmodes.cpp:432-446), and never sends
// them. For every other player on this machine those fields hold class defaults -- zero -- and
// OverrideAttackPosDir is false. So anything the simulation decides from the hand is decided from
// data only one machine has, and the moment a second player swings, the two machines disagree.
// melee.zs has been reading RSVR_VRHand.HandPos directly since 1.11. That is correct for one
// player and wrong for two.
//
// AND IT IS NOT ONLY ABOUT NETPLAY. Reading from a stamped history also makes the arithmetic
// dt-correct -- a velocity is a difference over the gap the stamps actually record, not over an
// assumed single tic -- and it DELETES the snap-turn and teleport special cases instead of tuning
// them, because the hand is differenced in the body's frame and a turn of the body with the arm
// still reads as nothing. melee.zs carries a hand-tuned patch for exactly that:
//     if (havePrev && (abs(deltaangle(lastAngle, mo.angle)) > 12 || (mo.pos - prevPos).Length() > 64))
//         settle = 2;
// The document's own trap table records an 8-deg/tic snap-turn flush failing in the saber because
// "a smooth-turn player above 280 deg/s trips it every tic, killing swings ... and below it, the
// turn is not subtracted at all". A threshold is the wrong shape of answer; this is the right one.
//
// CREDIT AND SHAPE. This is RS_ShieldSawQ's SSQ_Pose, which the document names as the thing to
// copy, adapted to carry BOTH hands because this pack swings the gun hand (melee.zs) and the off
// hand (fists, dual). Its hard-won details are kept and so are the reasons:
//
//   - THE AXES ARE BUILT IN PLACE, not returned. A function returning three Vector3s comes back
//     all zeros on QZD 17.3's VM (SHIELD found this 2026-10-22, same fault as `out Vector3`).
//   - Array<Vector3> is not allowed by this VM either, so the ring is fixed-size arrays.
//   - The sender runs in WorldTick, NOT UiTick. SSQ_Pose's own header says UiTick and its
//     shipping code does not: HandDir / OffhandDir are play scope and cannot be called from ui.
//   - Z IS NOT METRIC. OffhandPos.Z is divided by pixelstretch where X and Y are not
//     (hw_openxrdevice.cpp:606-608), so the same real swing measures ~20% slower straight up than
//     straight out. Vel() returns Doom space, correct in DIRECTION; Speed() puts pixelstretch back
//     into the MAGNITUDE only, which is the number a threshold should be compared against.
class RSQ_Pose play
{
\tconst N = 8;
\tconst MAIN = 0;
\tconst OFF = 1;

\tVector3 pos[8];\t\t// newest first, absolute map units
\tVector3 bod[8];\t\t// where the BODY was for that sample
\tdouble byaw[8];\t\t// and which way it faced
\tint stamp[8];\t\t// Level.maptime when it arrived, 0 = none
\tVector3 F, L, U;\t// the controller's forward / left / up, unit, map space
\tbool left;\t\t\t// the sender plays left-handed (vr_control_scheme >= 10)
\tint buttons;\t\t// the sender's button bits for this sample
\tint count;

\tvoid Push(Vector3 p, Vector3 body, double bodyYaw, double yaw, double pitch, double roll,
\t\tint btn, int now)
\t{
\t\tfor (int k = N - 1; k > 0; k--)
\t\t{
\t\t\tpos[k] = pos[k - 1];
\t\t\tstamp[k] = stamp[k - 1];
\t\t\tbod[k] = bod[k - 1];
\t\t\tbyaw[k] = byaw[k - 1];
\t\t}
\t\tpos[0] = p;
\t\tstamp[0] = now;
\t\tbod[0] = body;
\t\tbyaw[0] = bodyYaw;
\t\t// built HERE, in place: three Vector3 returns come back zeroed on this VM
\t\tdouble cp = cos(pitch);
\t\tF.x = cp * cos(yaw); F.y = cp * sin(yaw); F.z = sin(pitch);
\t\tdouble l0x = cos(yaw + 90), l0y = sin(yaw + 90), l0z = 0;
\t\tdouble u0x = F.y * l0z - F.z * l0y;
\t\tdouble u0y = F.z * l0x - F.x * l0z;
\t\tdouble u0z = F.x * l0y - F.y * l0x;
\t\tdouble cr = cos(roll), sr = sin(roll);
\t\tL.x = l0x * cr + u0x * sr; L.y = l0y * cr + u0y * sr; L.z = l0z * cr + u0z * sr;
\t\tU.x = u0x * cr - l0x * sr; U.y = u0y * cr - l0y * sr; U.z = u0z * cr - l0z * sr;
\t\tbuttons = btn;
\t\tif (count < N)
\t\t\tcount++;
\t}

\t// three tics of slack: a sender that stops sending (stowed, out of VR, menu) goes stale
\t// rather than leaving the last pose to be read as live
\tclearscope bool Fresh(int now) const
\t{
\t\treturn count > 0 && now - stamp[0] <= 3;
\t}

\t// THE ARM'S OWN MOTION, NOT THE BODY'S. pos[] is absolute, so a difference taken off it
\t// carries the player's travel and his turn as well. Doom run speed is about 583 units/sec,
\t// which is many times any swing threshold -- walking forward with the gun out would read as
\t// a permanent swing, and a snap turn is worse: the hand is ~20 units off the body axis, so
\t// 45 degrees in one tic is 15 units, about 525 units/sec, out of nothing.
\tVector3 Rel(int k) const
\t{
\t\tVector3 d = pos[k] - bod[k];
\t\tdouble c = cos(byaw[k]), s = sin(byaw[k]);
\t\treturn (d.x * c + d.y * s, d.y * c - d.x * s, d.z);
\t}

\t// ...and back into the frame the player faces NOW, because callers compare against world
\t// directions. A turn of the body with the arm still reads as nothing, which is what it is.
\tVector3 Turn(Vector3 v) const
\t{
\t\tdouble c = cos(byaw[0]), s = sin(byaw[0]);
\t\treturn (v.x * c - v.y * s, v.x * s + v.y * c, v.z);
\t}

\t// map units per tic, over the gap the STAMPS record -- not an assumed single tic
\tVector3 Vel() const
\t{
\t\tif (count < 2 || stamp[0] == stamp[1])
\t\t\treturn (0, 0, 0);
\t\treturn Turn(Rel(0) - Rel(1)) / (stamp[0] - stamp[1]);
\t}

\t// the same over a 2-sample window starting k back; zero if the history is not that deep
\tVector3 VelAt(int k) const
\t{
\t\tif (k + 2 >= count || stamp[k] == stamp[k + 2])
\t\t\treturn (0, 0, 0);
\t\treturn Turn(Rel(k) - Rel(k + 2)) / (stamp[k] - stamp[k + 2]);
\t}

\t// the TRUE speed of a velocity: pixelstretch back into the magnitude only, because the
\t// direction is already right in Doom space. This is what a threshold compares against.
\tclearscope double Speed(Vector3 v, double ps) const
\t{
\t\tdouble zt = v.z * ps;
\t\treturn sqrt(v.x * v.x + v.y * v.y + zt * zt);
\t}

\t// the fastest 2-sample window in the last six: a swing's peak, not wherever it happened to
\t// be on the tic somebody asked. The release of a throw is already the slowing-down part.
\tVector3 PeakVel(double ps) const
\t{
\t\tVector3 best = (0, 0, 0);
\t\tdouble bl = 0;
\t\tfor (int k = 0; k < 6; k++)
\t\t{
\t\t\tVector3 v = VelAt(k);
\t\t\tdouble l = Speed(v, ps);
\t\t\tif (l > bl)
\t\t\t{
\t\t\t\tbl = l;
\t\t\t\tbest = v;
\t\t\t}
\t\t}
\t\treturn best;
\t}
}

// The packing, and the engine reads. Three ints is what SendNetworkEvent carries, so one event
// per hand per tic: arg0 position, arg1 angles + buttons, arg2 the hand index and handedness.
class RSQ_PoseNet abstract play
{
\tstatic clearscope int ClampI(int v, int lo, int hi)
\t{
\t\treturn v < lo ? lo : (v > hi ? hi : v);
\t}

\t// x, y relative to the pawn in quarter units (11 bits signed each), z in quarter units
\t// (10 bits signed). +-256 units of reach horizontally, +-128 vertically, at 0.25 resolution.
\tstatic clearscope int PackPos(Vector3 rel)
\t{
\t\tint x = ClampI(int(round(rel.x * 4)), -1024, 1023) & 0x7FF;
\t\tint y = ClampI(int(round(rel.y * 4)), -1024, 1023) & 0x7FF;
\t\tint z = ClampI(int(round(rel.z * 4)), -512, 511) & 0x3FF;
\t\treturn x | (y << 11) | (z << 22);
\t}

\tstatic clearscope Vector3 UnpackPos(int a)
\t{
\t\tint x = a & 0x7FF;
\t\tif (x >= 1024)
\t\t\tx -= 2048;
\t\tint y = (a >> 11) & 0x7FF;
\t\tif (y >= 1024)
\t\t\ty -= 2048;
\t\tint z = (a >> 22) & 0x3FF;
\t\tif (z >= 512)
\t\t\tz -= 1024;
\t\treturn (x / 4.0, y / 4.0, z / 4.0);
\t}

\t// yaw 10 bits over 360, pitch 10 bits over -90..90, roll 10 bits over -180..180, then two
\t// button bits: attack and altattack, which is what a melee gate ever asks about.
\tstatic clearscope int PackAng(double yaw, double pitch, double roll, int btn)
\t{
\t\tint iy = ClampI(int(round((yaw % 360.0 + 360.0) % 360.0 / 360.0 * 1023.0)), 0, 1023);
\t\tint ip = ClampI(int(round((pitch + 90.0) / 180.0 * 1023.0)), 0, 1023);
\t\tint ir = ClampI(int(round(((roll + 180.0) % 360.0 + 360.0) % 360.0 / 360.0 * 1023.0)), 0, 1023);
\t\treturn iy | (ip << 10) | (ir << 20) | ((btn & 3) << 30);
\t}

\tstatic clearscope double, double, double, int UnpackAng(int a)
\t{
\t\tdouble yaw = (a & 0x3FF) / 1023.0 * 360.0;
\t\tdouble pitch = ((a >> 10) & 0x3FF) / 1023.0 * 180.0 - 90.0;
\t\tdouble roll = ((a >> 20) & 0x3FF) / 1023.0 * 360.0 - 180.0;
\t\tint btn = (a >> 30) & 3;
\t\treturn yaw, pitch, roll, btn;
\t}

\t// the roll of the controller's real left axis about F, measured against the horizontal left,
\t// so the receiver's Push() rebuilds exactly the L and U the sender had
\tstatic clearscope double RollOf(Vector3 F, Vector3 Lreal)
\t{
\t\tdouble yaw = atan2(F.y, F.x);
\t\tVector3 L0 = (cos(yaw + 90), sin(yaw + 90), 0);
\t\tVector3 U0 = (F.y * L0.z - F.z * L0.y, F.z * L0.x - F.x * L0.z, F.x * L0.y - F.y * L0.x);
\t\treturn atan2(Lreal dot U0, Lreal dot L0);
\t}
}

class RSQ_PoseHandler : EventHandler
{
\tRSQ_Pose main[MAXPLAYERS];
\tRSQ_Pose off[MAXPLAYERS];

\tstatic clearscope RSQ_PoseHandler Get()
\t{
\t\treturn RSQ_PoseHandler(EventHandler.Find('RSQ_PoseHandler'));
\t}

\t// what everything downstream should call, instead of RSVR_VRHand.HandPos
\tstatic clearscope RSQ_Pose Of(PlayerPawn mo, int hand)
\t{
\t\tlet h = Get();
\t\tif (!h || !mo || !mo.player)
\t\t\treturn null;
\t\tint i = mo.PlayerNumber();
\t\tif (i < 0 || i >= MAXPLAYERS)
\t\t\treturn null;
\t\treturn hand == RSQ_Pose.OFF ? h.off[i] : h.main[i];
\t}

\toverride void OnRegister()
\t{
\t\tfor (int i = 0; i < MAXPLAYERS; i++)
\t\t{
\t\t\tmain[i] = new('RSQ_Pose');
\t\t\toff[i] = new('RSQ_Pose');
\t\t}
\t}

\t// EVERY PEER RUNS THIS, including the sender. That is the whole point: one code path, one
\t// set of numbers, and the machine that owns the controller is not a special case.
\toverride void NetworkProcess(ConsoleEvent e)
\t{
\t\tif (e.Name != "rsq-pose")
\t\t\treturn;
\t\tint i = e.Player;
\t\tif (i < 0 || i >= MAXPLAYERS || !playeringame[i] || !players[i].mo)
\t\t\treturn;
\t\tlet mo = players[i].mo;
\t\tdouble yaw, pitch, roll;
\t\tint btn;
\t\t[yaw, pitch, roll, btn] = RSQ_PoseNet.UnpackAng(e.Args[1]);
\t\tint hand = e.Args[2] & 1;
\t\tlet p = hand == RSQ_Pose.OFF ? off[i] : main[i];
\t\tif (!p)
\t\t\treturn;
\t\tp.Push(mo.pos + RSQ_PoseNet.UnpackPos(e.Args[0]), mo.pos, mo.angle,
\t\t\tyaw, pitch, roll, btn, Level.maptime);
\t\tp.left = (e.Args[2] & 2) != 0;
\t}

\t// The sender, in WorldTick, for THIS machine's console player only. Not UiTick: HandDir and
\t// OffDir are play scope and a ui hook cannot call them. (SSQ_Pose's own header says UiTick
\t// and its shipping code does not -- the code is right.)
\toverride void WorldTick()
\t{
\t\tif (consoleplayer < 0 || consoleplayer >= MAXPLAYERS || !playeringame[consoleplayer])
\t\t\treturn;
\t\tlet p = players[consoleplayer];
\t\tif (!p)
\t\t\treturn;
\t\tlet mo = PlayerPawn(p.mo);
\t\tif (!mo || !RSVR_VRHand.InVR(mo))
\t\t\treturn;
\t\tdouble ps = mo.Level.pixelstretch;
\t\tif (ps <= 0)
\t\t\tps = 1.2;
\t\tint btn = ((p.cmd.buttons & BT_ATTACK) != 0 ? 1 : 0)
\t\t\t| ((p.cmd.buttons & BT_ALTATTACK) != 0 ? 2 : 0);
\t\tint lh = LeftHanded() ? 2 : 0;
\t\tSend(mo, RSVR_VRHand.HandPos(mo), RSVR_VRHand.HandDir(mo, 0, 0, ps),
\t\t\tRSVR_VRHand.HandDir(mo, 90, 0, ps), btn, RSQ_Pose.MAIN | lh);
\t\tSend(mo, RSVR_VRHand.OffPos(mo), RSVR_VRHand.OffDir(mo, 0, 0, ps),
\t\t\tRSVR_VRHand.OffDir(mo, 90, 0, ps), btn, RSQ_Pose.OFF | lh);
\t}

\tstatic clearscope bool LeftHanded()
\t{
\t\tlet cv = CVar.FindCVar('vr_control_scheme');
\t\treturn cv && cv.GetInt() >= 10;
\t}

\tvoid Send(PlayerPawn mo, Vector3 hand, Vector3 F, Vector3 Lreal, int btn, int flags)
\t{
\t\tdouble yaw = atan2(F.y, F.x);
\t\tdouble pitch = asin(clamp(F.z, -1, 1));
\t\tdouble roll = RSQ_PoseNet.RollOf(F, Lreal);
\t\tEventHandler.SendNetworkEvent("rsq-pose", RSQ_PoseNet.PackPos(hand - mo.pos),
\t\t\tRSQ_PoseNet.PackAng(yaw, pitch, roll, btn), flags);
\t}
}
'''

def pose():
    """F7: the pose spine. A per-player, per-hand history fed by a once-a-tic netevent from the
    console player and read only from the history, by everyone including the sender.

    `VR_MELEE_ON_QUESTZDOOM_2026-10-24.md` Part Two section 9 names this the single
    highest-leverage thing in the three codebases. This stage only LAYS it; moving melee.zs onto
    it is the step after, and until that happens melee still reads RSVR_VRHand directly."""
    open(OUT_SRC + 'zscript/rsq/pose.zs', 'w').write(POSE_ZS)
    # REGISTER IT. A plain EventHandler that is not in MAPINFO's AddEventHandlers never runs --
    # it compiles, ships, and does nothing, which is exactly what the first build of this did
    # (an instrumented run printed zero of either half). It goes FIRST in the list: its
    # NetworkProcess fills the history at the top of the tic, before anything reads it.
    mp = OUT_SRC + 'MAPINFO.rsvr'
    mt = open(mp).read()
    a = '\tAddEventHandlers = "'
    if mt.count(a) != 1:
        raise SystemExit('MAPINFO.rsvr: the AddEventHandlers line is not there exactly once')
    if 'RSQ_PoseHandler' in mt:
        raise SystemExit('MAPINFO.rsvr: RSQ_PoseHandler is already registered; pose has run twice')
    open(mp, 'w').write(mt.replace(a, a + 'RSQ_PoseHandler", "'))
    zp = OUT_SRC + 'ZSCRIPT.rsvr'
    zt = open(zp).read()
    # after vrhand.zs, whose statics it calls, and before melee.zs, which will read it next
    a = '#include "zscript/rsvr/vrhand.zs"\n'
    if zt.count(a) != 1:
        raise SystemExit('ZSCRIPT.rsvr: the vrhand include is not there exactly once')
    open(zp, 'w').write(zt.replace(a, a + '#include "zscript/rsq/pose.zs"\n'))
    st = dict(file='zscript/rsq/pose.zs', samples=8, hands=['main', 'off'],
              event='rsq-pose', sender='WorldTick, console player only',
              reader='NetworkProcess, every peer including the sender',
              reference='RS_ShieldSawQ zscript/ssq/pose.zs + state.zs SendPose/NetworkProcess',
              note='melee.zs is NOT on it yet; it still reads RSVR_VRHand directly')
    json.dump(st, open(OUT + 'pose_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py pose\n')
    print(json.dumps(st, indent=1))


def spine():
    """F7: melee.zs onto the pose spine. Must run AFTER butt/whip (they edit the same file) and
    after pose (it writes the class this reads)."""
    p = OUT_SRC + 'zscript/rsvr/melee.zs'
    t = open(p).read()
    st = {}

    def once(old, new, what):
        nonlocal t
        if t.count(old) != 1:
            raise SystemExit('melee.zs: %s is not there exactly once' % what)
        t = t.replace(old, new)

    # ---- 1 & 2: the hand, and the body frame that goes with it
    once("""\tbool Frame(PlayerPawn mo)
\t{
\t\tif (!RSVR_VRHand.InVR(mo))
\t\t\treturn false;
\t\tps = mo.Level.pixelstretch;
\t\tif (ps <= 0)
\t\t\tps = 1.2;
\t\tfH = RSVR_VRHand.HandPos(mo);
\t\tfF = RSVR_VRHand.HandDir(mo, 0, 0, ps);
\t\tfR = -RSVR_VRHand.HandDir(mo, 90, 0, ps);
\t\tfU = RSVR_VRHand.HandDir(mo, 0, 90, ps);
""",
         """\t// 1.97 F7: THE HAND COMES OUT OF THE POSE HISTORY, not out of the engine fields.
\t// RSVR_VRHand.HandPos reads AttackPos, which stock QuestZDoom writes on the CONSOLE
\t// PLAYER'S PAWN ONLY and never sends: for every other player it is zero, so a second
\t// player's melee resolved from nothing. RSQ_PoseHandler fills a stamped history on every
\t// machine from one netevent a tic, and this reads that -- on the sender's machine too, so
\t// there is one code path and no special case for the player holding the controller.
\t//
\t// `bod` and `byaw` are the body pose recorded WITH this hand sample. That is the whole
\t// reason the snap-turn patch could be deleted: the controller pose is written by the
\t// renderer at the end of a frame and the pawn's angle changes in the tic after, so
\t// converting an old hand reading with a new body angle invented a swing out of a turn.
\t// Matching each sample to its own body pose removes that at the source.
\tbool Frame(PlayerPawn mo)
\t{
\t\tlet ph = RSQ_PoseHandler.Of(mo, RSQ_Pose.MAIN);
\t\tif (!ph || !ph.Fresh(mo.Level.maptime))
\t\t\treturn false;
\t\tps = mo.Level.pixelstretch;
\t\tif (ps <= 0)
\t\t\tps = 1.2;
\t\tfH = ph.pos[0];
\t\tfF = ph.F;
\t\tfR = -ph.L;
\t\tfU = ph.U;
\t\tpBod = ph.bod[0];
\t\tpByaw = ph.byaw[0];
\t\tpStamp = ph.stamp[0];
""", 'the Frame() body')

    # the fields the new Frame() writes
    once("\ttransient Vector3 fH;\n",
         "\ttransient Vector3 fH;\n"
         "\ttransient Vector3 pBod;\t\t// 1.97 F7: the body pose recorded WITH this hand sample\n"
         "\ttransient double pByaw;\n"
         "\ttransient int pStamp;\n", 'the fH field')

    # BodyFrame uses the sample's own body pose, not the pawn's live one
    once("""\tstatic Vector3 BodyFrame(PlayerPawn mo, Vector3 p)
\t{
\t\tVector3 d = p - mo.pos;
\t\tdouble c = cos(mo.angle), s = sin(mo.angle);
\t\treturn (d.x * c + d.y * s, -d.x * s + d.y * c, d.z);
\t}""",
         """\t// 1.97 F7: against the body pose that came WITH the sample (pBod / pByaw), not against
\t// the pawn's live position and angle. Those two are a tic apart -- the hand is written by
\t// the renderer at the end of a frame, the pawn turns in the tic after -- and that gap is
\t// what used to turn a snap turn into a swing.
\tVector3 BodyFrame(PlayerPawn mo, Vector3 p)
\t{
\t\tVector3 d = p - pBod;
\t\tdouble c = cos(pByaw), s = sin(pByaw);
\t\treturn (d.x * c + d.y * s, -d.x * s + d.y * c, d.z);
\t}""", 'BodyFrame')

    # ---- 3: the patch goes
    once("""\t\t// a snap turn or a teleport moves the hand without a swing
\t\tif (havePrev && (abs(Actor.deltaangle(lastAngle, mo.angle)) > 12 || (mo.pos - prevPos).Length() > 64))
\t\t\tsettle = 2;
\t\tlastAngle = mo.angle;
\t\tif (settle > 0)
\t\t{
\t\t\tsettle--;
\t\t\tReset();
\t\t}

""",
         """\t\t// 1.97 F7: THE SNAP-TURN AND TELEPORT PATCH IS GONE, not retuned. It threw away two
\t\t// tics whenever the pawn turned more than 12 degrees or moved more than 64 units, which
\t\t// is the shape of fix the melee document records failing in the saber: above about
\t\t// 280 deg/s a smooth-turn player trips it EVERY tic and loses every swing, and below the
\t\t// threshold the turn is not subtracted at all. BodyFrame now converts each sample with
\t\t// the body pose recorded beside it, so a turn cancels arithmetically and there is
\t\t// nothing left to throw away.

""", 'the snap-turn patch')

    # ---- 4: divide by the gap the stamps record
    once("""\t\t\tprevRel = BodyFrame(mo, bout);
\t\t\tprevRelIn = BodyFrame(mo, bin);
\t\t\thavePrev = true;""",
         """\t\t\tprevRel = BodyFrame(mo, bout);
\t\t\tprevRelIn = BodyFrame(mo, bin);
\t\t\tprevStamp = pStamp;
\t\t\thavePrev = true;""", 'the first-sample init')

    once("""\t\tVector3 rel = BodyFrame(mo, bout);
\t\tVector3 vel = rel - prevRel;
\t\tprevRel = rel;
\t\tVector3 relIn = BodyFrame(mo, bin);
\t\tVector3 velIn = relIn - prevRelIn;
\t\tprevRelIn = relIn;
\t\tdouble speed = vel.Length();""",
         """\t\t// 1.97 F7: per TIC, over the gap the stamps actually record. This used to be a bare
\t\t// difference, which is a velocity only while no tic is ever missed; a dropped tic read as
\t\t// a swing twice as fast as it was. A gap of 0 would divide by zero, so it is floored at 1.
\t\tint gap = max(1, pStamp - prevStamp);
\t\tVector3 rel = BodyFrame(mo, bout);
\t\tVector3 vel = (rel - prevRel) / gap;
\t\tprevRel = rel;
\t\tVector3 relIn = BodyFrame(mo, bin);
\t\tVector3 velIn = (relIn - prevRelIn) / gap;
\t\tprevRelIn = relIn;
\t\tprevStamp = pStamp;
\t\tdouble speed = vel.Length();""", 'the per-tic step')

    once("\tdouble lastAngle;\n\tint settle;\n",
         "\tint prevStamp;\t\t// 1.97 F7: the stamp of the sample prevRel was taken from\n",
         'the settle fields')

    # Reset() must forget the stamp too, or the first swing after a reset divides by a stale gap
    once("\t\tcount = 0;\n\t\thavePrev = false;\n",
         "\t\tcount = 0;\n\t\thavePrev = false;\n\t\tprevStamp = 0;\n", 'Reset')

    if 'settle' in t or 'lastAngle' in t:
        raise SystemExit('melee.zs: settle / lastAngle still referenced after the migration')
    open(p, 'w').write(t)
    st['reads'] = 'RSQ_PoseHandler.Of(mo, RSQ_Pose.MAIN), newest sample'
    st['deleted'] = 'the snap-turn / teleport settle patch, and lastAngle'
    st['body_frame'] = 'pBod / pByaw, the body pose recorded with the sample'
    st['dt'] = 'velocity divided by the stamp gap, floored at 1'
    st['unchanged'] = ("rise = vel.z/speed and fwd = vel.x/speed stay BODY-frame reads, so the "
                       "spine's Turn() is deliberately NOT applied")
    json.dump(st, open(OUT + 'spine_apply.json', 'w'), indent=1)
    with open(OUT + '.generated', 'a') as f:
        f.write('then tools/bd22_plus.py spine\n')
    print(json.dumps(st, indent=1))


def sync():
    """Copy the built src/ into the set and write the stamp check_plan.py reads.

    This replaces a hand-run robocopy. That is the point: the stamp has to be written by the
    thing that does the copy, or it certifies nothing. The old stamp lived in the BUILD dir
    (OUT + '.generated') while check_plan.py looked in the SET, so the check passed on a file
    nothing had touched since the day it was created."""
    import shutil
    src = OUT_SRC.rstrip('/')
    dst = os.path.join(REPO, 'sets', 'bd22q_1.97', 'src')
    if not os.path.isdir(src):
        raise SystemExit('sync: no build at %s -- run the pipeline first' % src)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    n = sum(len(f) for _, _, f in os.walk(dst))
    stages = ''
    sp = OUT + '.generated'
    if os.path.exists(sp):
        stages = open(sp).read()
    stamp = os.path.join(REPO, 'sets', 'bd22q_1.97', '.generated')
    open(stamp, 'w').write(
        'bd22q %s -- generated, do not hand-edit sets/bd22q_1.97/src\n'
        '%d files, written by tools/bd22_plus.py sync at %s\n\n%s'
        % (VERSION, n, __import__('datetime').datetime.now().isoformat(timespec='seconds'), stages))
    st = dict(files=n, dest='sets/bd22q_1.97/src', stamp='sets/bd22q_1.97/.generated')
    print(json.dumps(st, indent=1))


if __name__ == '__main__':
    if sys.argv[1:2] == ['apply']:
        apply()
    if sys.argv[1:2] == ['revolver']:
        revolver()
    if sys.argv[1:2] == ['flash']:
        flash()
    if sys.argv[1:2] == ['bullet']:
        bullet()
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
    if sys.argv[1:2] == ['casings']:
        casings()
    if sys.argv[1:2] == ['hits']:
        hits()
    if sys.argv[1:2] == ['pose']:
        pose()
    if sys.argv[1:2] == ['spine']:
        spine()
    if sys.argv[1:2] == ['sync']:
        sync()
    if sys.argv[1:2] == ['pk3']:
        pk3(sys.argv[2])
