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
sys.path.insert(0, '/home/claude/c2q')
sys.path.insert(0, '/mnt/user-data/uploads/Quest_Weapons_Kit/kit/kit/team/reload_merged/tools')
import genpack, carve_by_ref, rgeo

SRC = '/home/claude/presidentkoopa/rs_brutal22weaponsq/src/'
REMA = '/home/claude/presidentkoopa/rs_vr_weapons/bd22/'
OUT = '/home/claude/c2q/build/bd22/'
SCALE, OFF = (-1.0, 1.0, 1.0), (0.0, 0.0, 0.0)        # MODELDEF.bd.txt: all three guns

# the three toggles: 1.96b class -> sources
PLUS = {
    'MG42': dict(card='BD_Buzzsaw', ref='buzzsaw_wm.md3', mesh='HitlersBuzzsaw/HitlersBuzzsaw.md3',
                 part='magazine', ref_parts={'magazine': 'magazine'}, ready_frame=0,
                 toggle='rsq_plus_mg42', label='MG42: Belt Drum Reload',
                 reserve='Clip2', magammo='RSQ_MG42Drum', nomag='RSQ_NoDrum_MG42', ammouse=1,
                 ready_sprites=['HBUS A'], spr=('RQXM', 'RQXP', 'RQXW')),
    'Flamethrower2': dict(card='BD_Flamethrower', ref='flamethrower_wm.md3', mesh='Flamethrower2/Flamethrower2.md3',
                 part='canister', ref_parts={'canister': 'magazine'}, ready_frame=0,
                 toggle='rsq_plus_flamer', label='Flamethrower: Canister Reload',
                 reserve='Gas', magammo='RSQ_FlamerCanister', nomag='RSQ_NoCanister_Flamer', ammouse=1,
                 ready_sprites=['FLMT A', '2LMT A'], spr=('RQYM', 'RQYP', 'RQYW')),
    'Unmaker': dict(card='BD_Unmaker', ref='unmaker_wm.md3', mesh='Unmaker/Unmaker.md3',
                 part='skull', ref_parts={'skull': 'magazine', 'skull2': 'magazine'}, ready_frame=0,
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
import shutil, zipfile, importlib, re

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
    sys.path.insert(0, '/mnt/user-data/uploads/Quest_Weapons_Kit/kit/kit/team/reload_merged/tools')
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
    # DECORATE
    for cls, p in PLUS.items():
        fn = {'MG42': 'MG42.dec', 'Flamethrower2': 'Flamethrower.dec', 'Unmaker': 'Unmaker.dec'}[cls]
        src = OUT_SRC + 'actors/Weapons/' + fn
        if not os.path.exists(src):
            shutil.copy('/home/claude/bd22src/actors/Weapons/' + fn, src)       # BD22's own file, untouched by 1.96b
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


if __name__ == '__main__':
    if sys.argv[1:2] == ['apply']:
        apply()
    if sys.argv[1:2] == ['pk3']:
        pk3(sys.argv[2])
