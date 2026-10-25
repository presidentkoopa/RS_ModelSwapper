"""lift_aliens.py -- give ModelSwapper's Aliens meshes the Aliens set's own reload, hands and placement.

    python -B tools_kit/lift_aliens.py <RSQ_WeaponDepot/sets/aliens/src> [--dry]

WHY A LIFT
The five Aliens gun meshes ModelSwapper shelves (models/alien/<gun>, and the re-centred copies
in models/hud/AE_<gun>) are the Aliens set's own files, byte for byte. The Aliens Quest set
fitted its reload rows, reload layers and hands to those files at its own placement. So nothing
here is measured: rows are copied, keyed to ModelSwapper's donors, and only the fields that
named the Aliens TC's own items change (see OVERRIDES).

WHAT IT REPLACES
ModelSwapper's earlier Aliens reload rows came from the _wm pipeline (RS_VR_Weapons world-mesh
cards: other split meshes, other numbers, and no MODELDEF for their layers at all). Those rows
are REPLACED IN PLACE -- same slot numbers, so nothing else moves. Guns with no row get one
appended. Shelf rows, picks and names are not touched: the donors already exist.

PLACEMENT
MS_alien_rifle / _smartgun / _shotgun were drawn somewhere other than where the Aliens set draws
them; the hands and reload rows are fitted to the Aliens set's placement, so those three donor
blocks take it. The re-centred MS_AE_* copies already sit there (checked below by mesh shift:
their Offset = the set's Offset + the re-centring shift) and are left alone.

HANDS
Ermac's hand.md3 in the Aliens set is the BD22Q one with ten more frames (a trigger pose and a
squeeze per Aliens gun). Those ten are appended to models/rsq/hand.md3 (md3_frames.py: the 46
frames already there keep their indices), given new RQGS / RQGT / RQGU / RQSP letters where
ModelSwapper's hand MODELDEF has none for the frame, and each Aliens hand row's letters are
re-keyed by FRAME, not by letter.

WRITES modeldef, MODELDEF.aliens (new), MODELDEF.rsq, models/rsq/hand.md3, models/alien/*/rsr_clear.png
(and any other layer skin missing), zscript_depot/rsq/hands.zs (pose states),
zscript_depot/rsq/handtable.zs, zscript_depot/rsr/rsr_guns.ms.zs, zscript_depot/rsr/rsr_pump_guns.zs,
SNDINFO.ms. Re-running is a no-op apart from rows, which it rewrites to the same values.
"""
import os, re, shutil, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lift_common import ARR, read_row, set_row, slot_of, max_slot, tc_index, block_of, get_line, frame_names, LETTERS
import rsr_table as T
import md3_frames as M3
from lift_common import blocks, frames_of, read, write, add_slot_for_donor, count_of

# Aliens class -> (kind, MS mesh folder, [donors]); the first donor is the models/alien one
GUNS = {
    'M4A3Pistol_3D':       ('rsr', 'pistol', ['MS_alien_pistol', 'MS_AE_Pistol']),
    'PulseRifle_3D':       ('rsr', 'rifle', ['MS_alien_rifle']),
    'Smartgun_3D':         ('rsr', 'smartgun', ['MS_alien_smartgun']),
    'M240Flamethrower_3D': ('rsr', 'flamer', ['MS_alien_flamer', 'MS_AE_Flamer']),
    'NewShotgun_3D':       ('pump', 'shotgun', ['MS_alien_shotgun', 'MS_AE_Shotgun']),
}
# the TC's reload sounds are lumps of the Aliens TC itself; ModelSwapper loads beside anything,
# so its own foley (already shipped for BD22, sounds/ms) is aliased, plus the set's bolt.
FOLEY = {
    'M4A3Pistol_3D': dict(magout='ms/bd22/pistol/magout', magin='ms/bd22/pistol/magin',
                          slideback='ms/bd22/pistol/slideback', slidefwd='ms/bd22/pistol/slidefwd'),
    'PulseRifle_3D': dict(magout='ms/bd22/rifle/magout', magin='ms/bd22/rifle/magin',
                          slideback='FILE:sounds/rsr/rsrboltbk.ogg', slidefwd='FILE:sounds/rsr/rsrboltfw.ogg'),
    'Smartgun_3D': dict(magout='ms/bd22/rifle/magout', magin='ms/bd22/rifle/magin'),
    'M240Flamethrower_3D': dict(magout='ms/bd22/rocketlauncher/magout', magin='ms/bd22/rocketlauncher/magin'),
    'NewShotgun_3D': dict(shellin='ms/bd22/shotgun/shellin', pumpback='ms/bd22/shotgun/pumpback'),
}
SLIDELOCK = {'M4A3Pistol_3D'}   # the M4A3's slide locks back on empty (ModelSwapper's row already said so)


def snd(cls, what):
    return 'ms/aliens/%s/%s' % (GUNS[cls][1], what)


# ------------------------------------------------------------------ generic row read / write
# ------------------------------------------------------------------ MODELDEF helpers
def md3_frame0(p):
    _ = struct
    import numpy as np
    sys.path.insert(0, os.path.join(SRC_TOOLS))
    import genpack as gp
    return np.concatenate([s['xyz'][0] for s in gp.md3_surfaces(p)[1]])


SRC_TOOLS = None


def tc_gun_block(src, cls, mesh):
    """the TC's ready block for the gun: same class, same mesh, its FrameIndex on frame 0"""
    for fn in sorted(os.listdir(src)):
        if not fn.lower().startswith('modeldef.') or not fn.lower().endswith('.txt'):
            continue
        for b in blocks(read(os.path.join(src, fn))):
            mm = re.search(r'Model\s+0\s+"([^"]+)"', b['body'])
            if b['cls'] == cls and mm and mm.group(1).lower() == mesh.lower() and get_line(b['body'], 'Offset'):
                return b, fn
    return None, None


# ------------------------------------------------------------------ hands
def hand_letters(md_text, mesh, sprites):
    """{sprite: {letter: frame}} for the hand blocks of `mesh`"""
    out = {s: {} for s in sprites}
    for b in blocks(md_text):
        if not re.search(r'Model\s+0\s+"%s"' % re.escape(mesh), b['body']):
            continue
        for s, l, _, f in frames_of(b['body']):
            if s in out:
                out[s][l] = int(f)
    return out


def main(src, dry):
    global SRC_TOOLS
    SRC_TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(src)))), 'tools')
    report = []
    # ---------------- hands: one mesh for every set
    ms_hand = os.path.join(ROOT, 'models/rsq/hand.md3')
    added = M3.append(ms_hand, os.path.join(src, 'models/rsq/hand.md3'), check=dry)
    for f in ('hand2.md3',):
        if M3.append(os.path.join(ROOT, 'models/rsq', f), os.path.join(src, 'models/rsq', f), check=True):
            sys.exit('%s: the Aliens copy has frames ModelSwapper\'s lacks -- extend the lift' % f)
    report.append('hand.md3: %d frames appended %s' % (len(added), [n for _, n in added]))
    ms_names = frame_names(ms_hand) if not dry else frame_names(ms_hand) + [n for _, n in added]
    al_names = frame_names(os.path.join(src, 'models/rsq/hand.md3'))
    al2_names = frame_names(os.path.join(src, 'models/rsq/hand2.md3'))
    ms2_names = frame_names(os.path.join(ROOT, 'models/rsq/hand2.md3'))
    tc_md = read(os.path.join(src, 'MODELDEF.ae'))
    p_rsq = os.path.join(ROOT, 'MODELDEF.rsq'); rsq = read(p_rsq)
    tc_h = hand_letters(tc_md, 'hand.md3', ('RQGS', 'RQGT', 'RQGU'))
    tc_h2 = hand_letters(tc_md, 'hand2.md3', ('RQSP',))
    ms_h = hand_letters(rsq, 'hand.md3', ('RQGS', 'RQGT', 'RQGU'))
    ms_h2 = hand_letters(rsq, 'hand2.md3', ('RQSP',))
    remap, new_lines, new_states = {}, [], []

    def letter_for(spr, ms_map, frame_name, names):
        fi = names.index(frame_name)
        for l, f in ms_map[spr].items():
            if f == fi:
                return l
        l = next(c for c in LETTERS if c not in ms_map[spr])
        ms_map[spr][l] = fi
        new_lines.append((spr, l, fi, frame_name))
        return l
    for spr in ('RQGS',):
        remap[spr] = {l: letter_for(spr, ms_h, al_names[f], ms_names) for l, f in sorted(tc_h[spr].items())}
    # trigger and squeeze go in pairs under ONE letter (hands.zs: "Trg" / "Sqz" .. Trigger(i))
    remap['RQGT'] = {}
    for l, f in sorted(tc_h['RQGT'].items()):
        ft, fs = ms_names.index(al_names[f]), ms_names.index(al_names[tc_h['RQGU'][l]])
        have = [k for k, v in ms_h['RQGT'].items() if v == ft and ms_h['RQGU'].get(k) == fs]
        if have:
            remap['RQGT'][l] = have[0]; continue
        k = next(c for c in LETTERS if c not in ms_h['RQGT'] and c not in ms_h['RQGU'])
        ms_h['RQGT'][k] = ft; ms_h['RQGU'][k] = fs
        new_lines += [('RQGT', k, ft, al_names[f]), ('RQGU', k, fs, al_names[tc_h['RQGU'][l]])]
        remap['RQGT'][l] = k
    remap['RQSP'] = {l: letter_for('RQSP', ms_h2, al2_names[f], ms2_names) for l, f in sorted(tc_h2['RQSP'].items())}
    report.append('hand letters (Aliens -> ModelSwapper): %s' % remap)
    if new_lines and not dry:
        gs = [l for l in new_lines if l[0] != 'RQSP']
        sp = [l for l in new_lines if l[0] == 'RQSP']
        def add_to_block(text, mesh, spr0, lines):
            if not lines:
                return text
            for b in blocks(text):
                if re.search(r'Model\s+0\s+"%s"' % re.escape(mesh), b['body']) and spr0 in b['body']:
                    add = ''.join('\tFrameIndex %s %s 0 %d\t// Ermac hand frame %s (Aliens set, tools_kit/lift_aliens.py)\n'
                                  % (s, l, fi, n) for s, l, fi, n in lines)
                    end = text.index(b['text']) + len(b['text']) - 1   # the closing brace
                    return text[:end] + add + text[end:]
            sys.exit('no %s block in MODELDEF.rsq' % mesh)
        rsq = add_to_block(rsq, 'hand.md3', 'RQGT', gs)
        rsq = add_to_block(rsq, 'hand2.md3', 'RQSP', sp)
        write(p_rsq, rsq)
        p_hz = os.path.join(ROOT, 'zscript_depot/rsq/hands.zs'); hz = read(p_hz)
        st = []
        for s, l, fi, n in new_lines:
            lab = {'RQGS': 'Gun', 'RQGT': 'Trg', 'RQGU': 'Sqz', 'RQSP': 'Sup'}[s] + l
            if re.search(r'^\s*%s:' % lab, hz, re.M):
                continue
            st.append('\t%s: %s %s -1; Stop;\t// Aliens set (tools_kit/lift_aliens.py)' % (lab, s, l))
        if st:
            at = re.search(r'^\tFist: RQGF A -1; Stop;', hz, re.M).start()
            hz = hz[:at] + '\n'.join(st) + '\n' + hz[at:]
            write(p_hz, hz)

    # ---------------- tables
    tc_rsr = read(os.path.join(src, 'zscript/rsr/rsr_guns.zs')); r_idx = tc_index(tc_rsr)
    tc_pump = read(os.path.join(src, 'zscript/rsr/rsr_pump_guns.zs')); p_idx = tc_index(tc_pump)
    tc_hand = read(os.path.join(src, 'zscript/rsq/handtable.zs')); h_idx = tc_index(tc_hand)
    p_rsr = os.path.join(ROOT, 'zscript_depot/rsr/rsr_guns.ms.zs'); rsr = read(p_rsr)
    p_pump = os.path.join(ROOT, 'zscript_depot/rsr/rsr_pump_guns.zs'); pump = read(p_pump)
    p_hand = os.path.join(ROOT, 'zscript_depot/rsq/handtable.zs'); hand = read(p_hand)
    p_md = os.path.join(ROOT, 'modeldef'); md = read(p_md)
    tc_layers = blocks(read(os.path.join(src, 'MODELDEF.rsr'))) + blocks(read(os.path.join(src, 'MODELDEF.rsrpump')))
    layer_out, spr_rsr, spr_pump, tokens, snd_rows = [], {}, {}, [], []
    shelf = read(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs'))
    ms_rsr_names = {f['name'] for f in T.functions(rsr)}
    for cls, (kind, folder, donors) in GUNS.items():
        tbl, idx = (tc_rsr, r_idx) if kind == 'rsr' else (tc_pump, p_idx)
        row = read_row(tbl, idx[cls])
        spr = [row[k][1].strip("'") for k in ('SprGun', 'SprPart', 'SprWorld')]
        mine = [b for b in tc_layers if any(s in spr for s, *_ in frames_of(b['body'])) and 'models/rsq"' not in b['body']]
        mesh = re.search(r'Model\s+0\s+"([^"]+)"', mine[0]['body']).group(1)
        tcb, tcf = tc_gun_block(src, cls, mesh)
        tc_scale, tc_off = get_line(tcb['body'], 'Scale'), get_line(tcb['body'], 'Offset')
        if tc_off != [float(x) for x in row['Offset'][1].strip('()').split(',')]:
            sys.exit('%s: the reload row\'s Offset %s is not the gun\'s %s (%s)' % (cls, row['Offset'][1], tc_off, tcf))
        anchor = re.search(r'"\w+\|%s\|(\w{4})\|' % donors[0], shelf).group(1)
        # ---- placement + a layer copy per donor
        tc_mesh = os.path.join(src, re.search(r'Path\s+"([^"]+)"', mine[0]['body']).group(1).replace('\\', '/'), mesh)
        tc_mesh = next(p for p in (tc_mesh, tc_mesh.replace('/weapons/', '/Weapons/')) if os.path.exists(p))
        for d in donors:
            bm = block_of(md, d)
            dpath = re.search(r'Path\s+"([^"]+)"', bm.group(1)).group(1)
            dmesh = os.path.join(ROOT, dpath, re.search(r'Model\s+0\s+"([^"]+)"', bm.group(1)).group(1))
            if d.startswith('MS_alien_'):
                if open(dmesh, 'rb').read() != open(tc_mesh, 'rb').read():
                    sys.exit('%s: %s is not the Aliens set\'s %s' % (d, dmesh, tc_mesh))
                body = bm.group(1)
                nb = re.sub(r'^([ \t]*Scale\s+)[^\n]*', r'\g<1>%s' % ' '.join('%g' % v for v in tc_scale), body, flags=re.M)
                nb = re.sub(r'^([ \t]*Offset\s+)[^\n]*', r'\g<1>%s' % ' '.join('%.1f' % v for v in tc_off), nb, flags=re.M)
                if nb != body:
                    report.append('%s: placement %s -> the Aliens set\'s %s %s'
                                  % (d, get_line(body, 'Offset'), tc_off, tcf))
                    nb = nb.replace('\n', '\n\t// placement: the Aliens set\'s own (%s), which its reload rows and hands are fitted to\n' % tcf, 1)
                    md = md[:bm.start(1)] + nb + md[bm.end(1):]
                d_off, d_path = tc_off, dpath
            else:
                # a re-centred copy: its Offset must be the set's plus the mesh shift
                import numpy as np
                sh = (md3_frame0(dmesh) - md3_frame0(tc_mesh))
                if np.ptp(sh, 0).max() > 1e-3:
                    sys.exit('%s: not a pure shift of %s' % (dmesh, tc_mesh))
                s = abs(tc_scale[1]); sh = sh.mean(0) * s
                want = (tc_off[0] + sh[1], tc_off[1] + sh[0], tc_off[2] - sh[2])
                have = get_line(bm.group(1), 'Offset')
                if max(abs(a - b) for a, b in zip(want, have)) > 0.01:
                    sys.exit('%s: Offset %s, expected %s (set placement + re-centring)' % (d, have, want))
                d_off, d_path = have, dpath
            # layers keyed to this donor: the gun-without-its-magazine blocks are the DONOR'S
            # (A_ChangeModel), drawn from the donor's own mesh folder at its own placement
            for b in mine:
                t = b['text']
                if b['cls'] == cls:
                    t = re.sub(r'^([ \t]*Model\s+)%s\b' % re.escape(cls), r'\g<1>%s' % d, t, flags=re.M)
                    t = re.sub(r'(Path\s+")[^"]+', r'\g<1>%s' % d_path, t)
                    t = re.sub(r'^([ \t]*Offset\s+)[^\n/]*', r'\g<1>%s' % ' '.join('%.3f' % v for v in d_off), t, flags=re.M)
                elif d != donors[0]:
                    continue        # parts / hand / floor copies are not per donor
                else:
                    t = re.sub(r'(Path\s+")models/weapons/%s' % folder, r'\g<1>models/alien/%s' % folder, t, flags=re.I)
                    t = re.sub(r'(Path\s+")[^"]*(weapons)[/\\]+(\w+)', lambda m: m.group(1) + 'models/alien/' + folder, t, flags=re.I)
                layer_out.append(t)
                # every skin a layer names must be in its folder
                lpath = re.search(r'Path\s+"([^"]+)"', t).group(1)
                spath = re.search(r'Path\s+"([^"]+)"', b['text']).group(1).replace('\\', '/')
                for sk in set(re.findall(r'(?:Skin|SurfaceSkin\s+\d+)\s+\d+\s+"([^"]+)"', t)):
                    dst = os.path.join(ROOT, lpath, sk)
                    srcf = next((p for p in (os.path.join(src, spath, sk), os.path.join(src, spath.replace('models/weapons', 'Models/Weapons'), sk)) if os.path.exists(p)), None)
                    if not os.path.exists(dst):
                        if not srcf:
                            sys.exit('%s: skin %s not in the set' % (cls, sk))
                        if not dry:
                            shutil.copy2(srcf, dst)
                        report.append('  skin %s -> %s' % (sk, os.path.relpath(dst, ROOT)))
                    elif srcf and open(dst, 'rb').read() != open(srcf, 'rb').read():
                        report.append('  NOTE skin %s differs from the set\'s copy (kept ModelSwapper\'s)' % os.path.relpath(dst, ROOT))
            for b in mine:
                for s, l, *_ in frames_of(b['body']):
                    (spr_rsr if kind == 'rsr' else spr_pump).setdefault(s, set()).add(l)
        # ---- the reload row, one per slot (the families share one slot, or have one each)
        vals = {k: v for k, v in row.items() if k not in ('Index', 'GrabLen', 'MagAmmo') or kind == 'rsr' and k == 'MagAmmo'}
        f = FOLEY[cls]

        def sv(what):
            return ('case', '"%s"' % snd(cls, what)) if what in f else ('case', '""')
        if kind == 'rsr':
            slots = sorted({slot_of(rsr, d) for d in donors} - {None})
            if not slots:
                n = count_of(rsr) + 1
                rsr = re.sub(r'(static int Count\(\) \{ return )\d+(; \})', r'\g<1>%d\2' % n, rsr)
                for d in donors:
                    rsr = add_slot_for_donor(rsr, d, n)
                slots = [n]
            for d in donors:
                if slot_of(rsr, d) is None:
                    rsr = add_slot_for_donor(rsr, d, slots[0])
            for sl in slots:
                old = read_row(rsr, sl)
                v = dict(vals)
                v.update(MagAmmo=('case', '""'), Reserve=('case', '""'), ReloadToken=('case', '""'),
                         NoMag=old.get('NoMag', ('case', '"RSR_NoMag_%s"' % donors[0])),
                         ReadySprites=('case', '"%s A"' % anchor),
                         SndOut=sv('magout'), SndIn=sv('magin'), SndBack=sv('slideback'), SndFwd=sv('slidefwd'),
                         SndLand=('case', '"%s"' % snd(cls, 'magdrop')),
                         SlideLock=('arr', {'v': 'true' if cls in SLIDELOCK else 'false'}))
                v = {k: x for k, x in v.items() if k in ms_rsr_names}
                rsr = set_row(rsr, sl, v)
                tokens.append(v['NoMag'][1].strip('"'))
                report.append('%-20s reload slot %d (Aliens %d) for %s, layers %d' % (cls, sl, idx[cls], donors, len(mine)))
        else:
            slots = sorted({slot_of(pump, d) for d in donors} - {None})
            if not slots:
                n = max_slot(pump) + 1
                for d in donors:
                    pump = add_slot_for_donor(pump, d, n)
                slots = [n]
            for d in donors:
                if slot_of(pump, d) is None:
                    pump = add_slot_for_donor(pump, d, slots[0])
            for sl in slots:
                v = dict(vals)
                v.update(Reserve=('case', '""'), Loaded=('case', '""'), Cap=('case', '0'), WaitLabels=('case', '""'),
                         ReadySprite=('case', '"%s A"' % anchor),
                         SndShell=sv('shellin'), SndBack=sv('pumpback'), SndFwd=sv('pumpfwd'),
                         SndLand=('case', '"%s"' % snd(cls, 'shelldrop')))
                pump = set_row(pump, sl, v)
                report.append('%-20s pump slot %d (Aliens %d) for %s, layers %d' % (cls, sl, idx[cls], donors, len(mine)))
        # ---- the hand row, written to every hand slot these donors use
        hr = read_row(tc_hand, h_idx[cls])
        pose = read_row(tc_hand, h_idx[cls])
        gp = pose['GunPose'][1]['v'].strip('"'); sp = pose['SupportPose'][1]['v'].strip('"'); tr = pose['Trigger'][1]['v'].strip('"')
        hv = {
            'GunOne': ('arr', {'v': '"%s"' % remap['RQGS'][gp] if gp else '""'}),
            'GunTwo': ('arr', {'v': '"%s"' % remap['RQGS'][gp] if gp else '""'}),
            'Support': ('arr', {'v': '"%s"' % remap['RQSP'][sp] if sp else '""'}),
            'Trigger': ('arr', {'v': '"%s"' % remap['RQGT'][tr] if tr else '""'}),
            'GunHook': hr['GunHook'], 'GunRot': hr['GunRot'], 'SupportHook': hr['SupportHook'], 'SupportRot': hr['SupportRot'],
            'GunHookTwo': hr['GunHook'], 'GunRotTwo': hr['GunRot'],
            'SupportPoint': ('arr', {'x': '0', 'y': '0', 'z': '0'}),
        }
        hslots = sorted({slot_of(hand, d) for d in donors} - {None})
        for d in donors:
            if slot_of(hand, d) is None:
                n = max_slot(hand) + 1
                hand = add_slot_for_donor(hand, d, n); hslots.append(n)
        for sl in hslots:
            hand = set_row(hand, sl, hv)
        report.append('%-20s hand slots %s (Aliens %d): pose %s->%s support %s->%s trigger %s->%s'
                      % (cls, hslots, h_idx[cls], gp, remap['RQGS'].get(gp), sp, remap['RQSP'].get(sp), tr, remap['RQGT'].get(tr)))
        # ---- foley
        snd_rows.append('// Aliens %s (tools_kit/lift_aliens.py)' % cls)
        for what, target in f.items():
            if target.startswith('FILE:'):
                sf = os.path.join(src, target[5:])
                if not dry:
                    shutil.copy2(sf, os.path.join(ROOT, 'sounds/ms', os.path.basename(sf)))
                snd_rows.append('%-36s sounds/ms/%s' % (snd(cls, what), os.path.basename(sf)))
            else:
                snd_rows.append('$alias %s %s' % (snd(cls, what), target))
        snd_rows.append('$alias %s ms/magdrop' % snd(cls, 'shelldrop' if kind == 'pump' else 'magdrop'))

    if dry:
        print('\n'.join(report)); return
    # ---------------- sprite registration (a MODELDEF naming an unknown sprite stops the pk3 loading)
    def reg(cls_name, sprs, comment):
        return ('\n// %s\nclass %s : Actor\n{\n\tStates\n\t{\n\tSpawn:\n%s\n\t\tStop;\n\t}\n}\n'
                % (comment, cls_name, '\n'.join('\t\t%s %s 0;' % (s, ''.join(sorted(l))) for s, l in sorted(sprs.items()))))
    rsr = re.sub(r'\n// Aliens set guns \(tools_kit/lift_aliens\.py\).*', '', rsr, flags=re.S).rstrip('\n') + '\n'
    # a NoMag token class for every slot whose class is not declared elsewhere in the file
    rsr += '\n// Aliens set guns (tools_kit/lift_aliens.py)\n' + ''.join(
        'class %s : RSVR_Token {}\n' % n for n in sorted(set(tokens)) if not re.search(r'^class %s\b' % n, rsr, re.M))
    rsr += reg('RSR_Sprites_Aliens', spr_rsr, 'the Aliens set\'s reload layer sprites (MODELDEF.aliens), so the engine knows them; never spawned')
    pump = re.sub(r'\n// the Aliens set\'s pump layer sprites.*', '', pump, flags=re.S).rstrip('\n') + '\n'
    pump += reg('RSP_Sprites_Aliens', spr_pump, 'the Aliens set\'s pump layer sprites (MODELDEF.aliens), so the engine knows them; never spawned')
    write(p_rsr, rsr); write(p_pump, pump); write(p_hand, hand); write(p_md, md)
    write(os.path.join(ROOT, 'MODELDEF.aliens'),
          '// GENERATED by tools_kit/lift_aliens.py from RSQ_WeaponDepot sets/aliens MODELDEF.rsr and\n'
          '// MODELDEF.rsrpump -- do not edit by hand. The Aliens set\'s VR reload layers for ModelSwapper\'s\n'
          '// Aliens meshes. The gun-without-its-magazine blocks are keyed to each DONOR (A_ChangeModel gives\n'
          '// the foreign weapon the donor\'s MODELDEF) and drawn from the donor\'s own mesh folder at its own\n'
          '// placement; the part, hand and floor blocks keep their classes. Same files, byte for byte.\n\n'
          + '\n'.join(layer_out))
    p_s = os.path.join(ROOT, 'SNDINFO.ms'); s = read(p_s)
    s = re.sub(r'\n// ---- Aliens set \(tools_kit/lift_aliens\.py\).*', '', s, flags=re.S).rstrip('\n')
    write(p_s, s + '\n\n// ---- Aliens set (tools_kit/lift_aliens.py)\n' + '\n'.join(snd_rows) + '\n')
    print('\n'.join(report))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], '--dry' in sys.argv)
