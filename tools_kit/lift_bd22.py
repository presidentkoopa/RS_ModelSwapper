"""lift_bd22.py -- put BD22Q's guns on the ModelSwapper shelf with BD22Q's own reload data.

    python -B tools_kit/lift_bd22.py <RS_Brutal22WeaponsQ/src> <gun> [<gun> ...]
        gun = a BD22 weapon class (BrutalPistol, Rifle, ...) or `all`

WHY THIS IS A LIFT AND NOT A MEASUREMENT
BD22Q's meshes ship inside this repo byte for byte (models/depot_bd/bd/), and ModelSwapper
draws Brutal Doom meshes at BD22's own placement (Scale -1 1 1, Offset 0, ZOffset -5). Every
number in BD22's reload table, hand table and reload MODELDEF was measured on those files at
that placement, and BD22Q loads and reloads with them. So nothing here is computed: each row
is copied from BD22's generated tables into ModelSwapper's, keyed by the donor model instead
of BD22's class name. The only values changed are the ones that named BD22's own items, which
do not exist on a foreign mod (see OVERRIDES).

WHAT IT WRITES (all regenerated from BD22 on every run; refuses if a donor is already lifted)
  modeldef                          the donor block: BD22's mesh, skin and placement, resting on
                                    BD22's own ready frame
  MODELDEF.bd22                     BD22's reload layers for the gun (gun without its magazine,
                                    the magazine alone, in the hand, on the floor), re-keyed from
                                    BD22's class to the donor class. A_ChangeModel gives the
                                    foreign weapon the DONOR's MODELDEF, so the gun layers must be
                                    the donor's or they draw nothing.
  zscript.txt, quest/zscript.txt    the donor stub
  zscript/RS_ForeignModels.zs       shelf row + display name
  zscript/RS_ForeignAnim.zs         ready clip (desktop)
  zscript_depot/rsr/rsr_guns.ms.zs  one new reload slot per gun + its sprites and tokens
  zscript_depot/rsq/handtable.zs    one new hand slot per gun
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lift_common import read, write, bd22_blocks, frames_of, append_rows, add_slot_for_donor, count_of, array_len, insert_after_array_head, md3_frames
import rsr_table as T
import lift_common as L

# BD22 class -> (donor suffix, shelf archetype, display name)
GUNS = {
    'BrutalPistol':   ('Pistol', 'pistol', 'BD22 Pistol'),
    'Rifle':          ('Rifle', 'rifle', 'BD22 Assault Rifle'),
    'BrutalSMG':      ('SMG', 'smg', 'BD22 SMG'),
    'MP40':           ('MP40', 'smg', 'BD22 MP40'),
    'AssaultShotgun': ('AssaultShotgun', 'shotgun', 'BD22 Assault Shotgun'),
    'RailGun':        ('RailGun', 'plasma', 'BD22 Railgun'),
    'Plasma_Gun':     ('PlasmaGun', 'plasma', 'BD22 Plasma Gun'),
    'Sniper':         ('Ruger', 'rifle', 'BD22 Ruger Mini-14'),
    'Rocket_Launcher': ('RocketLauncher', 'launcher', 'BD22 Rocket Launcher'),
    'Shot_Gun':       ('Shotgun', 'shotgun', 'BD22 Shotgun'),
    'SSG':            ('SSG', 'supershotgun', 'BD22 Super Shotgun'),
    'Revolver':       ('Revolver', 'revolver', 'BD22 Revolver'),
    'GrenadeLauncher': ('M79', 'launcher', 'BD22 Grenade Launcher'),
}
# Reload foley per gun: (out, in, back, fwd) as paths under the RS_VR_Weapons repo (W:) or
# RS_Brutal22WeaponsQ's src (B: -- BD22Q's own rack sounds). BD22 itself borrows Brutal
# Doom's sound names, which exist only when Brutal Doom is loaded; ModelSwapper loads beside
# anything, so it ships its own, under ms/ names that no mod can collide with.
RIFLE = ('W:sounds/rifles/RCOUT.ogg', 'W:sounds/rifles/RCIN.ogg', 'W:sounds/rifles/RCKBCK.ogg', 'W:sounds/rifles/RCKFWD.ogg')
SMG = ('W:sounds/rifles/RCOUT.ogg', 'W:sounds/rifles/RCIN.ogg', 'B:sounds/rsr/rsrslide.wav', 'B:sounds/rsr/rsrsmgfw.wav')
CELL = ('W:sounds/plasma/PLCOUT.ogg', 'W:sounds/plasma/PLCIN.ogg', None, None)
FOLEY = {
    'BrutalPistol': ('W:sounds/pistols/9mmclip1.wav', 'W:sounds/pistols/9mmclip2.wav', 'W:sounds/pistols/9mmslide.wav', 'W:sounds/pistols/PSNAP.ogg'),
    'Rifle': RIFLE, 'Sniper': RIFLE, 'AssaultShotgun': RIFLE, 'BrutalSMG': SMG, 'MP40': SMG,
    'RailGun': CELL, 'Plasma_Gun': CELL,
    'Rocket_Launcher': ('W:sounds/launchers/RLCOUT.ogg', 'W:sounds/launchers/RLCIN.ogg', None, None),
}
# break-open guns: (open, a round in, close)
BREAK_FOLEY = {
    'SSG': ('W:sounds/shotguns/DoubleBarrel/DSDBOPN.ogg', 'W:sounds/shotguns/DoubleBarrel/CLIPINSS.ogg', 'W:sounds/shotguns/DoubleBarrel/DSDBCLS.ogg'),
    'Revolver': ('W:sounds/revolvers/DBOPN.ogg', 'W:sounds/revolvers/DBLOD.ogg', 'W:sounds/revolvers/DBCLS.ogg'),
    'GrenadeLauncher': ('W:sounds/launchers/UBL/DSGROPEN.ogg', 'W:sounds/launchers/UBL/DSGRLOAD.ogg', 'W:sounds/launchers/UBL/DSGRCLOS.ogg'),
}
# pump guns: (a shell in at the port, the pump back, the pump forward)
PUMP_FOLEY = {
    'Shot_Gun': ('W:sounds/shotguns/DoomPump/SHOTLOAD1.ogg', 'W:sounds/shotguns/DoomPump/shotcycle.wav', None),
}
RELOAD = os.environ.get('RS_VR_RELOAD', os.path.join(os.path.dirname(ROOT), 'presidentkoopa', 'rs_vr_reload'))
WEAPONS = os.environ.get('RS_VR_WEAPONS', os.path.join(os.path.dirname(ROOT), 'presidentkoopa', 'rs_vr_weapons'))


def write_foley(src, guns):
    """SNDINFO.ms rows + files for each gun (skips a gun whose rows are already there)"""
    import shutil
    p = os.path.join(ROOT, 'SNDINFO.ms')
    os.makedirs(os.path.join(ROOT, 'sounds/ms'), exist_ok=True)
    if os.path.exists(p):
        t = read(p).rstrip('\n')
    else:
        # a clean checkout has no SNDINFO.ms yet: start it with the magazine landing every
        # gun's magdrop alias points at (RS_VR_Reload's bounce, as the shipped file has it)
        for k in (1, 2, 3):
            shutil.copy2(os.path.join(RELOAD, 'sounds/wm/DSBOUNC%d.ogg' % k), os.path.join(ROOT, 'sounds/ms'))
        t = ('// ModelSwapper\'s own reload foley. Every name is under ms/, so it cannot collide with a\n'
             '// name the loaded mod defines. Files: RS_VR_Weapons, RS_VR_Reload (the magazine landing).\n\n'
             '$random ms/magdrop { ms/magdrop1 ms/magdrop2 ms/magdrop3 }\n'
             'ms/magdrop1         sounds/ms/DSBOUNC1.ogg\n'
             'ms/magdrop2         sounds/ms/DSBOUNC2.ogg\n'
             'ms/magdrop3         sounds/ms/DSBOUNC3.ogg')
    for g in guns:
        if g not in FOLEY or ('ms/bd22/%s/magout' % GUNS[g][0].lower()) in t:
            continue
        rows = ['', '// BD22 %s (tools_kit/lift_bd22.py)' % g]
        for what, f in zip(('magout', 'magin', 'slideback', 'slidefwd'), FOLEY[g]):
            if not f:
                continue
            base = WEAPONS if f.startswith('W:') else src
            sf = os.path.join(base, f[2:])
            if not os.path.exists(sf):
                sys.exit('foley file missing: %s' % sf)
            shutil.copy2(sf, os.path.join(ROOT, 'sounds/ms', os.path.basename(sf)))
            rows.append('%-36s sounds/ms/%s' % (sndname(g, what), os.path.basename(sf)))
        rows.append('$alias %s ms/magdrop' % sndname(g, 'magdrop'))
        t += '\n' + '\n'.join(rows)
    for g in guns:
        if g not in BREAK_FOLEY or ('ms/bd22/%s/open' % GUNS[g][0].lower()) in t:
            continue
        rows = ['', '// BD22 %s break-open (tools_kit/lift_bd22.py)' % g]
        for what, f in zip(('open', 'load', 'close'), BREAK_FOLEY[g]):
            sf = os.path.join(WEAPONS if f.startswith('W:') else src, f[2:])
            if not os.path.exists(sf):
                sys.exit('foley file missing: %s' % sf)
            shutil.copy2(sf, os.path.join(ROOT, 'sounds/ms', os.path.basename(sf)))
            rows.append('%-36s sounds/ms/%s' % (sndname(g, what), os.path.basename(sf)))
        rows.append('$alias %s ms/magdrop' % sndname(g, 'rounddrop'))
        t += '\n' + '\n'.join(rows)
    for g in guns:
        if g not in PUMP_FOLEY or ('ms/bd22/%s/shellin' % GUNS[g][0].lower()) in t:
            continue
        rows = ['', '// BD22 %s pump (tools_kit/lift_bd22.py)' % g]
        for what, f in zip(('shellin', 'pumpback', 'pumpfwd'), PUMP_FOLEY[g]):
            if not f:
                continue
            base = WEAPONS if f.startswith('W:') else src
            sf = os.path.join(base, f[2:])
            if not os.path.exists(sf):
                sys.exit('foley file missing: %s' % sf)
            shutil.copy2(sf, os.path.join(ROOT, 'sounds/ms', os.path.basename(sf)))
            rows.append('%-36s sounds/ms/%s' % (sndname(g, what), os.path.basename(sf)))
        rows.append('$alias %s ms/magdrop' % sndname(g, 'shelldrop'))
        t += '\n' + '\n'.join(rows)
    write(p, t + '\n')


# guns whose slide / bolt locks back on an empty gun (BD22 README "lock back when fired dry")
SLIDELOCK = {'BrutalPistol', 'Rifle', 'BrutalSMG', 'AssaultShotgun'}
# the stock sprite each archetype's donors anchor on (the first shelf row of that archetype)
ANCHOR_DEFAULT = 'PISG'


def donor(cls):
    return 'MS_BD22_' + GUNS[cls][0]


def sndname(cls, what):
    return 'ms/bd22/%s/%s' % (GUNS[cls][0].lower(), what)


# ------------------------------------------------------------------ BD22 side
def bd22_index(src, table):
    """class -> index from a generated table's Index(Weapon w)"""
    t = read(os.path.join(src, table))
    f = next(f for f in T.functions(t) if f['name'] == 'Index')
    return {c: int(n) for c, n in re.findall(r"(?:n == '|w is ')(\w+)'\)\s*return (\d+);", f['body'])}


# ------------------------------------------------------------------ table surgery
# ------------------------------------------------------------------ main
def main(src, which):
    guns = list(GUNS) if which == ['all'] else which
    for g in guns:
        if g not in GUNS:
            sys.exit('unknown BD22 gun %s (known: %s)' % (g, ', '.join(GUNS)))

    p_rsr = os.path.join(ROOT, 'zscript_depot/rsr/rsr_guns.ms.zs')
    p_hand = os.path.join(ROOT, 'zscript_depot/rsq/handtable.zs')
    rsr = read(p_rsr); hand = read(p_hand)
    p_pump = os.path.join(ROOT, 'zscript_depot/rsr/rsr_pump_guns.zs')
    pump = read(p_pump)
    for g in guns:
        if any('"%s"' % donor(g) in t for t in (rsr, pump, read(os.path.join(ROOT, 'zscript_depot/rsr/rsb_guns.zs')))):
            sys.exit('%s is already lifted -- git checkout the files first' % donor(g))

    b_rsr = read(os.path.join(src, 'zscript/rsr/rsr_guns.bd.zs'))
    b_hand = read(os.path.join(src, 'zscript/rsq/handtable.zs'))
    b_md = read(os.path.join(src, 'MODELDEF.bd.txt'))
    b_mdr = read(os.path.join(src, 'MODELDEF.rsr'))
    ridx = bd22_index(src, 'zscript/rsr/rsr_guns.bd.zs')
    b_pump = read(os.path.join(src, 'zscript/rsr/rsr_pump_guns.zs'))
    pidx = bd22_index(src, 'zscript/rsr/rsr_pump_guns.zs')
    pump_blocks = bd22_blocks(read(os.path.join(src, 'MODELDEF.rsrpump')))
    p_rsb = os.path.join(ROOT, 'zscript_depot/rsr/rsb_guns.zs')
    rsb = read(p_rsb)
    b_rsb = read(os.path.join(src, 'zscript/rsr/rsb_guns.zs'))
    bidx = bd22_index(src, 'zscript/rsr/rsb_guns.zs')
    rsb_blocks = bd22_blocks(read(os.path.join(src, 'MODELDEF.rsb')))
    n_rsb = max([0] + [int(x) for x in re.findall(r'donor == "\w+"\)\s*return (\d+);', rsb)])
    n_pump = max([0] + [int(x) for x in re.findall(r'donor == "\w+"\)\s*return (\d+);', pump)])
    hidx = bd22_index(src, 'zscript/rsq/handtable.zs')
    md_blocks = bd22_blocks(b_md)
    rsr_blocks = bd22_blocks(b_mdr)

    sprites_b = []
    md_add, layer_add, stubs, shelf, names, clips, sprites, tokens, report = [], [], [], [], [], [], [], [], []
    n_rsr = count_of(rsr)
    n_hand = array_len(hand, 'GunOne') - 1
    for g in guns:
        d = donor(g)
        if g not in ridx and g not in pidx and g not in bidx:
            report.append('%s: no BD22 magazine or pump reload row -- skipped' % g); continue
        mine, spr, pspr = [], {}, {}
        if g in ridx:
            i = ridx[g]
            row = T.row(b_rsr, i)
            spr = {k: row[k].strip("'") for k in ('SprGun', 'SprPart', 'SprWorld')}
            mine += [b for b in rsr_blocks if any(s in spr.values() for s, *_ in frames_of(b['body']))]
        if g in pidx:
            prow = T.row(b_pump, pidx[g])
            pspr = {k: prow[k].strip("'") for k in ('SprGun', 'SprPart', 'SprWorld')}
            # the hand's own pose block (models/rsq) is shared by every pump gun and already ships
            mine += [b for b in pump_blocks if any(s in pspr.values() for s, *_ in frames_of(b['body']))
                     and 'models/rsq"' not in b['body']]
        bspr = {}
        if g in bidx:
            brow = T.row(b_rsb, bidx[g])
            bspr = {k: brow[k].strip("'") for k in ('SprGun', 'SprPart', 'SprWorld')}
            mine += [b for b in rsb_blocks if any(s in bspr.values() for s, *_ in frames_of(b['body']))
                     and 'models/rsq"' not in b['body']]
        if not mine:
            report.append('%s: no reload layer blocks for %s %s %s' % (g, spr, pspr, bspr)); continue
        guns_spr = {spr.get('SprGun'), pspr.get('SprGun'), bspr.get('SprGun')} - {None}
        rf = int(next(f for b in mine for s, l, _, f in frames_of(b['body']) if s in guns_spr))
        path = re.search(r'Path\s+"([^"]+)"', mine[0]['body']).group(1)
        for b in mine:
            t = b['text']
            if b['cls'] == g:
                t = re.sub(r'^([ \t]*Model\s+)%s\b' % re.escape(g), r'\g<1>%s' % d, t, flags=re.M)
            t = t.replace('Path "models/bd/', 'Path "models/depot_bd/bd/')
            layer_add.append(t)
        # ---- the donor block: BD22's own gun block, resting on BD22's ready frame
        # the gun's own block: same class AND the same mesh its reload layers use (a class can
        # have several blocks -- the Ruger's also binds a grenade model)
        lmesh = re.search(r'Model\s+0\s+"([^"]+)"', mine[0]['body']).group(1).lower()
        cand = [b for b in md_blocks + [r for r in rsr_blocks if r not in mine] if b['cls'] == g and re.search(r'Path\s+"([^"]+)"', b['body'])
                and re.search(r'Path\s+"([^"]+)"', b['body']).group(1).rstrip('/').lower() == path.rstrip('/').lower()
                and (re.search(r'Model\s+0\s+"([^"]+)"', b['body']) or [None, ''])[1].lower() == lmesh]
        if not cand:
            report.append('%s: no MODELDEF.bd.txt block for %s/%s' % (g, path, lmesh)); continue
        gb = max(cand, key=lambda b: len(frames_of(b['body'])))
        keep = [l.strip() for l in gb['body'].splitlines()
                if re.match(r'\s*(Path|Model\s+\d|Skin|SurfaceSkin|Scale|Offset|ZOffset|NoInterpolation)\b', l, re.I)]
        keep = [l.replace('"models/bd/', '"models/depot_bd/bd/') for l in keep]
        arch = GUNS[g][1]
        anchor = shelf_anchor(arch)
        nframes = md3_frames(os.path.join(ROOT, path.replace('models/bd/', 'models/depot_bd/bd/'),
                                          re.search(r'Model\s+0\s+"([^"]+)"', gb['body']).group(1)))
        md_add.append('Model %s\n{\n\t// BD22Q\'s own %s: mesh, skin and placement exactly as BD22Q ships them\n\t// (tools_kit/lift_bd22.py); resting on BD22\'s ready frame %d\n%s\n\tFrameIndex %s A 0 %d\n\tFrameIndex MSBL A 0 9999\n}\n'
                      % (d, g, rf, '\n'.join('\t' + l for l in keep), anchor, rf))
        stubs.append('class %s : Actor {}' % d)
        shelf.append('"%s|%s|%s|0|%d|%d",' % (arch, d, anchor, rf, nframes))
        names.append('"%s|%s",' % (d, GUNS[g][2]))
        clips.append('"%s|ready|%d@1|-1|-1|-1",' % (d, rf))
        # ---- pump table row
        pslot = None
        if g in pidx:
            n_pump += 1
            pov = dict(Reserve='""', Loaded='""', Cap='0', WaitLabels='""', ReadySprite='"%s A"' % anchor,
                       SndShell='"%s"' % sndname(g, 'shellin'), SndBack='"%s"' % sndname(g, 'pumpback'),
                       SndFwd='"%s"' % sndname(g, 'pumpfwd') if PUMP_FOLEY.get(g, (0, 0, 0))[2] else '""',
                       SndLand='"%s"' % sndname(g, 'shelldrop'))
            pump = append_rows(pump, b_pump, pidx[g], n_pump, pov)
            pump = add_slot_for_donor(pump, d, n_pump)
            pslot = n_pump
        bslot = None
        if g in bidx:
            n_rsb += 1
            bov = dict(Reserve='""', Loaded='""', Unloaded='""', ReloadToken='""', Cls="'%s'" % d,
                       ReadySprite='"%s A"' % anchor,
                       SndOpen='"%s"' % sndname(g, 'open'), SndLoad='"%s"' % sndname(g, 'load'),
                       SndClose='"%s"' % sndname(g, 'close'), SndOpen2='""', SndClose2='""')
            rsb = append_rows(rsb, b_rsb, bidx[g], n_rsb, bov)
            rsb = add_slot_for_donor(rsb, d, n_rsb)
            bslot = n_rsb
            sprites_b.append('\t\t%s A 0;\t// %s (BD22 %s)' % (bspr['SprGun'], d, g))
            sprites_b.append('\t\t%s ABCDEFGHIJ 0;' % bspr['SprPart'])
            sprites_b.append('\t\t%s ABC 0;' % bspr['SprWorld'])
        if g not in ridx:
            i = None
            if g in hidx:
                n_hand += 1
                hand = append_rows(hand, b_hand, hidx[g], n_hand, {})
                hand = add_slot_for_donor(hand, d, n_hand)
            report.append('%-16s -> %-22s pump slot %s, break slot %s (BD22 %s), hand slot %s (BD22 %s), ready frame %d, %d frames, layers %d'
                          % (g, d, pslot, bslot, pidx.get(g) or bidx.get(g), n_hand if g in hidx else None, hidx.get(g), rf, nframes, len(mine)))
            continue
        # ---- reload table row
        n_rsr += 1
        ov = dict(MagAmmo='""', NoMag='"RSR_NoMag_%s"' % d, Reserve='""', ReloadToken='""', ChargeToken='"RSR_Charge"',
                  ReadySprites='"%s A"' % anchor,
                  SndOut='"%s"' % sndname(g, 'magout'), SndIn='"%s"' % sndname(g, 'magin'),
                  SndBack='"%s"' % sndname(g, 'slideback') if FOLEY.get(g, (0, 0, 0, 0))[2] else '""',
                  SndFwd='"%s"' % sndname(g, 'slidefwd') if FOLEY.get(g, (0, 0, 0, 0))[3] else '""',
                  SndLand='"%s"' % sndname(g, 'magdrop'),
                  SlideLock='true' if g in SLIDELOCK else 'false')
        rsr = append_rows(rsr, b_rsr, i, n_rsr, ov)
        rsr = add_slot_for_donor(rsr, d, n_rsr)
        sprites.append('\t\t%s %s 0;\t// %s (BD22 %s)' % (spr['SprGun'], 'ABC', d, g))
        sprites.append('\t\t%s %s 0;' % (spr['SprPart'], 'ABC'))
        sprites.append('\t\t%s A 0;' % spr['SprWorld'])
        tokens.append('class RSR_Held_%s : Inventory { Default { Inventory.MaxAmount 999; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }' % d)
        tokens.append('class RSR_NoMag_%s : RSVR_Token {}' % d)
        # ---- hand table row
        if g in hidx:
            n_hand += 1
            hand = append_rows(hand, b_hand, hidx[g], n_hand, {})
            hand = add_slot_for_donor(hand, d, n_hand)
            hslot = n_hand
        else:
            hslot = None
        report.append('%-16s -> %-22s reload slot %d (BD22 %d), hand slot %s (BD22 %s), ready frame %d, %d frames, layers %d'
                      % (g, d, n_rsr, i, hslot, hidx.get(g), rf, nframes, len(mine)))

    rsr = re.sub(r'(static int Count\(\) \{ return )\d+(; \})', r'\g<1>%d\2' % n_rsr, rsr)
    rsr = rsr.replace('\t\tStop;\n\t}\n}', '\n'.join(sprites) + '\n\t\tStop;\n\t}\n}', 1) if sprites else rsr
    if tokens:
        rsr = rsr.rstrip('\n') + '\n\n// BD22Q guns (tools_kit/lift_bd22.py)\n' + '\n'.join(tokens) + '\n'
    if sprites_b:
        rsb = rsb.replace('\t\tStop;\n\t}\n}', '\n'.join(sprites_b) + '\n\t\tStop;\n\t}\n}', 1)
    write(p_rsr, rsr); write(p_hand, hand); write(p_pump, pump); write(p_rsb, rsb)

    md = read(os.path.join(ROOT, 'modeldef')).rstrip('\n')
    write(os.path.join(ROOT, 'modeldef'), md + '\n\n// ---- BD22Q guns, lifted whole from RS_Brutal22WeaponsQ (tools_kit/lift_bd22.py)\n\n' + '\n'.join(md_add))
    p_l = os.path.join(ROOT, 'MODELDEF.bd22')
    if os.path.exists(p_l):
        write(p_l, read(p_l).rstrip('\n') + '\n\n' + '\n'.join(layer_add))
    else:
      write(p_l,
          '// GENERATED by tools_kit/lift_bd22.py from RS_Brutal22WeaponsQ MODELDEF.rsr -- do not edit by hand.\n'
          '// BD22Q\'s VR reload layers for the BD22 guns on the shelf. The weapon layer is the DONOR\'s\n'
          '// (A_ChangeModel), so the gun-without-magazine blocks are keyed to the donor class; the part,\n'
          '// hand and dropped-magazine blocks keep their own classes. Paths point at models/depot_bd/bd,\n'
          '// which holds BD22Q\'s meshes byte for byte.\n\n' + '\n'.join(layer_add))
    for zp in ('zscript.txt', 'quest/zscript.txt'):
        p = os.path.join(ROOT, zp); t = read(p)
        last = list(re.finditer(r'^class MS_\w+ : Actor \{\}\n', t, re.M))[-1]
        t = t[:last.end()] + '\n'.join(stubs) + '\n' + t[last.end():]
        write(p, t)
    p = os.path.join(ROOT, 'zscript/RS_ForeignModels.zs'); t = read(p)
    t = insert_after_array_head(t, 'static const string SHELF[] = {', shelf)
    t = insert_after_array_head(t, 'static const string NAMES[] = {', names)
    write(p, t)
    p = os.path.join(ROOT, 'zscript/RS_ForeignAnim.zs'); t = read(p)
    t = insert_after_array_head(t, 'static const string CLIP[] = {', clips)
    write(p, t)
    write_foley(src, guns)
    print('\n'.join(report))


def shelf_anchor(arch):
    t = read(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs'))
    m = re.search(r'"%s\|MS_\w+\|(\w{4})\|' % re.escape(arch), t)
    return m.group(1) if m else ANCHOR_DEFAULT


def charge_tokens(dry=False):
    """Every reload row whose charge token is one of the source set's own item names (BD22's
    RifleReloadToken, MP40ReloadToken, ASGReloadToken, SniperReloadToken): ModelSwapper ships no
    such class, so the reload could never ask for the handle (ChargeRule 1 needs the token).
    The join gives RSR_Charge when the mod's gun ran dry; the row is pointed at it. The lift sets
    it for new rows; this fixes rows lifted before (python -B tools_kit/lift_bd22.py --charge-tokens)."""
    p = os.path.join(ROOT, 'zscript_depot/rsr/rsr_guns.ms.zs')
    rsr = open(p).read()
    for n in range(1, L.count_of(rsr) + 1):
        tok = L.read_row(rsr, n).get('ChargeToken')
        if tok and tok[1] not in ('""', '"RSR_Charge"'):
            print('  slot %d: ChargeToken %s -> "RSR_Charge"' % (n, tok[1]))
            rsr = L.set_row(rsr, n, {'ChargeToken': (tok[0], '"RSR_Charge"')})
    if not dry:
        open(p, 'w', newline='\n').write(rsr)


def refresh_hands(src, only=None, dry=False):
    """Re-copy every lifted donor's HAND row (GunOne .. Trigger, GunHookTwo / GunRotTwo) from a BD22Q
    src's own handtable.zs, by BD22 class, onto the donor's existing slot. The first lift copied
    BD22Q's table as it stood that day; BD22Q's poses moved on (1.92 is the owner's reference), and
    three rows here (AssaultShotgun, Revolver, Sniper) no longer matched any BD22Q release. Prints
    every field that changes.  python -B tools_kit/lift_bd22.py --hands <RS_Brutal22WeaponsQ/src> [gun ...] [--dry]"""
    p = os.path.join(ROOT, 'zscript_depot/rsq/handtable.zs')
    hand = read(p)
    b_hand = read(os.path.join(src, 'zscript/rsq/handtable.zs'))
    hidx = L.tc_index(b_hand)
    for g in (only or list(GUNS)):
        d = donor(g)
        s = L.slot_of(hand, d)
        if s is None or g not in hidx:
            print('  %-16s %-24s no slot here or no BD22 row -- left' % (g, d)); continue
        want = L.read_row(b_hand, hidx[g])
        have = L.read_row(hand, s)
        vals, diffs = {}, []
        for name, (kind, v) in want.items():
            if name not in have or kind != 'arr':
                continue
            for ax, x in v.items():
                y = have[name][1].get(ax)
                if y is not None and y.strip('"') != x.strip('"'):
                    try:
                        if abs(float(x) - float(y)) < 5e-4:
                            continue
                    except ValueError:
                        pass
                    diffs.append('%s.%s %s -> %s' % (name, ax, y, x))
            vals[name] = (kind, v)
        # BD22Q tables without GunHookTwo/GunRotTwo (1.92): the two-hand hook defaults to the hook
        for two, one in (('GunHookTwo', 'GunHook'), ('GunRotTwo', 'GunRot')):
            if two in have and two not in want and one in want:
                for ax, x in want[one][1].items():
                    if have[two][1].get(ax) != x:
                        diffs.append('%s.%s %s -> %s' % (two, ax, have[two][1].get(ax), x))
                vals[two] = ('arr', dict(want[one][1]))
        print('  %-16s %-24s slot %d <- BD22 row %d: %s' % (g, d, s, hidx[g], '; '.join(diffs) if diffs else 'same'))
        if diffs:
            hand = L.set_row(hand, s, vals)
    if not dry:
        write(p, hand)


if __name__ == '__main__' and '--hands' in sys.argv:
    k = sys.argv.index('--hands')
    rest = [x for x in sys.argv[k + 2:] if not x.startswith('--')]
    refresh_hands(sys.argv[k + 1], rest or None, '--dry' in sys.argv)
    sys.exit(0)


if __name__ == '__main__' and '--charge-tokens' in sys.argv:
    charge_tokens('--dry' in sys.argv)
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
