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
import rsr_table as T

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
WEAPONS = os.environ.get('RS_VR_WEAPONS', os.path.join(os.path.dirname(ROOT), 'presidentkoopa', 'rs_vr_weapons'))


def write_foley(src, guns):
    """SNDINFO.ms rows + files for each gun (skips a gun whose rows are already there)"""
    import shutil
    p = os.path.join(ROOT, 'SNDINFO.ms'); t = read(p).rstrip('\n')
    os.makedirs(os.path.join(ROOT, 'sounds/ms'), exist_ok=True)
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
    write(p, t + '\n')


# guns whose slide / bolt locks back on an empty gun (BD22 README "lock back when fired dry")
SLIDELOCK = {'BrutalPistol', 'Rifle', 'BrutalSMG', 'AssaultShotgun'}
# the stock sprite each archetype's donors anchor on (the first shelf row of that archetype)
ANCHOR_DEFAULT = 'PISG'


def donor(cls):
    return 'MS_BD22_' + GUNS[cls][0]


def sndname(cls, what):
    return 'ms/bd22/%s/%s' % (GUNS[cls][0].lower(), what)


def read(p):
    return open(p, encoding='utf-8', errors='replace').read()


def write(p, t):
    open(p, 'w', encoding='utf-8', newline='\n').write(t)


# ------------------------------------------------------------------ BD22 side
def bd22_index(src, table):
    """class -> index from a generated table's Index(Weapon w)"""
    t = read(os.path.join(src, table))
    f = next(f for f in T.functions(t) if f['name'] == 'Index')
    return {c: int(n) for c, n in re.findall(r"(?:n == '|w is ')(\w+)'\)\s*return (\d+);", f['body'])}


def bd22_blocks(text):
    """every Model block with the comment lines just above it"""
    out = []
    for m in re.finditer(r'((?:^[ \t]*//[^\n]*\n)*)^[ \t]*Model\s+(\S+)\s*\n?\s*\{(.*?)^[ \t]*\}', text, re.S | re.M):
        out.append(dict(comment=m.group(1), cls=m.group(2), body=m.group(3), text=m.group(0)))
    return out


def frames_of(body):
    return re.findall(r'FrameIndex\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)', body)


# ------------------------------------------------------------------ table surgery
def append_rows(target, source, src_idx, new_idx, overrides):
    """append source row src_idx to every accessor of target as row new_idx"""
    tf = T.functions(target)
    sf = {f['name']: f for f in T.functions(source)}
    edits = []
    for f in tf:
        name = f['name']
        if name in ('Index', 'HandOf', 'DonorInHand', 'SlotForDonor', 'Count'):
            continue
        body = f['body']
        if 'switch' in body:
            if name in overrides:
                val = overrides[name]
            else:
                val = T.cases(sf[name]['body']).get(src_idx) if name in sf else None
            if val is None:
                continue
            last = list(re.finditer(r'^[ \t]*case\s+\d+:[^\n]*\n', body, re.M))
            if not last:
                continue
            at = f['start'] + (len(target[f['start']:f['end']]) - len(body) - 1) + last[-1].end()
            # recompute absolute: body begins at end-1-len(body)
            body_abs = f['end'] - 1 - len(body)
            at = body_abs + last[-1].end()
            edits.append((at, '\t\tcase %d:\treturn %s;\n' % (new_idx, val)))
        else:
            body_abs = f['end'] - 1 - len(body)
            for am in re.finditer(r'static const (\w+) (\w+)\[\] = \{(.*?)\};', body, re.S):
                typ, arr, items = am.group(1), am.group(2), [x.strip() for x in am.group(3).split(',')]
                if name in overrides:
                    val = overrides[name]
                else:
                    val = None
                    if name in sf:
                        sm = re.search(r'static const \w+ %s\[\] = \{(.*?)\};' % arr, sf[name]['body'], re.S)
                        if sm:
                            sitems = [x.strip() for x in sm.group(1).split(',')]
                            if src_idx < len(sitems):
                                val = sitems[src_idx]
                default = {'bool': 'false', 'String': '""', 'string': '""'}.get(typ, '0')
                pad = [default] * max(0, new_idx - len(items))
                add = pad + [val if val is not None else default]
                close = body_abs + am.start(3) + len(am.group(3))
                edits.append((close, ', ' + ', '.join(add)))
    for at, s in sorted(edits, reverse=True):
        target = target[:at] + s + target[at:]
    return target


def add_slot_for_donor(target, name, slot):
    f = next(f for f in T.functions(target) if f['name'] == 'SlotForDonor')
    body_abs = f['end'] - 1 - len(f['body'])
    m = list(re.finditer(r'^[ \t]*return 0;', f['body'], re.M))[-1]
    at = body_abs + m.start()
    return target[:at] + '\t\tif (donor == "%s")\treturn %d;\n' % (name, slot) + target[at:]


def count_of(target):
    m = re.search(r'static int Count\(\) \{ return (\d+); \}', target)
    return int(m.group(1)) if m else None


def array_len(target, fname):
    f = next(f for f in T.functions(target) if f['name'] == fname)
    m = re.search(r'static const \w+ \w+\[\] = \{(.*?)\};', f['body'], re.S)
    return len(m.group(1).split(','))


# ------------------------------------------------------------------ main
def main(src, which):
    guns = list(GUNS) if which == ['all'] else which
    for g in guns:
        if g not in GUNS:
            sys.exit('unknown BD22 gun %s (known: %s)' % (g, ', '.join(GUNS)))

    p_rsr = os.path.join(ROOT, 'zscript_depot/rsr/rsr_guns.ms.zs')
    p_hand = os.path.join(ROOT, 'zscript_depot/rsq/handtable.zs')
    rsr = read(p_rsr); hand = read(p_hand)
    for g in guns:
        if '"%s"' % donor(g) in rsr:
            sys.exit('%s is already lifted -- git checkout the files first' % donor(g))

    b_rsr = read(os.path.join(src, 'zscript/rsr/rsr_guns.bd.zs'))
    b_hand = read(os.path.join(src, 'zscript/rsq/handtable.zs'))
    b_md = read(os.path.join(src, 'MODELDEF.bd.txt'))
    b_mdr = read(os.path.join(src, 'MODELDEF.rsr'))
    ridx = bd22_index(src, 'zscript/rsr/rsr_guns.bd.zs')
    hidx = bd22_index(src, 'zscript/rsq/handtable.zs')
    md_blocks = bd22_blocks(b_md)
    rsr_blocks = bd22_blocks(b_mdr)

    md_add, layer_add, stubs, shelf, names, clips, sprites, tokens, report = [], [], [], [], [], [], [], [], []
    n_rsr = count_of(rsr)
    n_hand = array_len(hand, 'GunOne') - 1
    for g in guns:
        d = donor(g)
        if g not in ridx:
            report.append('%s: no BD22 magazine reload row -- skipped' % g); continue
        i = ridx[g]
        row = T.row(b_rsr, i)
        spr = {k: row[k].strip("'") for k in ('SprGun', 'SprPart', 'SprWorld')}
        # ---- the gun's reload layers, re-keyed to the donor
        mine = [b for b in rsr_blocks if any(s in spr.values() for s, *_ in frames_of(b['body']))]
        if not mine:
            report.append('%s: no MODELDEF.rsr blocks for %s' % (g, spr)); continue
        rf = int(next(f for s, l, _, f in frames_of(mine[0]['body']) if s == spr['SprGun']))
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
        # ---- reload table row
        n_rsr += 1
        ov = dict(MagAmmo='""', NoMag='"RSR_NoMag_%s"' % d, Reserve='""', ReloadToken='""',
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
    rsr = rsr.rstrip('\n') + '\n\n// BD22Q guns (tools_kit/lift_bd22.py)\n' + '\n'.join(tokens) + '\n'
    write(p_rsr, rsr); write(p_hand, hand)

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


def insert_after_array_head(t, head, rows):
    """APPEND at the array's end. A saved pick is an index into its archetype's rows, in
    array order, so a row inserted ahead of existing ones would move every player's pick."""
    start = t.index(head) + len(head)
    close = t.index('};', start)
    body = t[start:close].rstrip()
    if not body.endswith(','):
        body += ','
    return t[:start] + body + '\n\t\t\t// BD22Q guns (tools_kit/lift_bd22.py)\n' + '\n'.join('\t\t\t' + r for r in rows).rstrip(',') + '\n\t\t' + t[close:]


def shelf_anchor(arch):
    t = read(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs'))
    m = re.search(r'"%s\|MS_\w+\|(\w{4})\|' % re.escape(arch), t)
    return m.group(1) if m else ANCHOR_DEFAULT


def md3_frames(p):
    import struct
    return struct.unpack_from('<i', open(p, 'rb').read(), 76)[0]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
