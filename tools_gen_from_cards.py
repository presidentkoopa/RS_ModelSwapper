#!/usr/bin/env python3
"""tools_gen_from_cards.py -- re-point ModelSwapper's donor systems at cards/ (MS 1.5, 2026-10-31).

Reads every cards/<set>/<gun>/<label>.card and writes the four places a donor lives:
  1. modeldef               one `Model MS_<PREFIX>_<Gun>` block per card (Path cards/<set>/<gun>, the card's
                            labelled mesh, the skin(s) found in the folder). Scale/Offset/ZOffset/Angle/Pitch/Roll
                            are COPIED from the source mod's own MODELDEF block for that mesh (found by matching the
                            card mesh to the staged well mesh vertex-for-vertex, then that mesh's block). The card
                            mesh keeps the source mesh's origin, so the source numbers place it exactly as its mod did.
                            No match -> Scale 1, Offset 0, flagged PLACEMENT in the report.
  2. zscript.txt (+ quest/) the empty donor classes `class MS_X : Actor {}` between the GEN markers.
  3. zscript/RS_ForeignModels.zs   SHELF[] rows  "family|MS_X|ANCHOR|0|restFrame|frameCount"  and NAMES[] rows.
  4. gen_from_cards.report.md      what was generated, what was guessed (family), what has no placement.

Family (ModelSwapper's archetype vocabulary) comes from the card's archetype + the gun's name; see FAMILY().
Run from the repo root:  python3 tools_gen_from_cards.py [--well /path/to/VR_WeaponSetRebuild]
"""
import sys, os, re, glob, argparse, struct
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'tools_kit'))
try:
    from md3read import read_md3
except Exception:  # the Depot's reader, if tools_kit lacks one
    sys.path.insert(0, '/home/claude/rsq_weapondepot/tools/hqt'); from md3read import read_md3

PREFIX = {'vplus': 'VP', 'aliens': 'AE', 'meatgrinder': 'MG', 'brutalwolf': 'BW', 'hacx': 'HX', 'bd21': 'BD',
          'chex': 'CX', 'cola': 'Cola', 'd64': 'D64', 'voidwalker': 'HV', 'hocus': 'HP', 'pirate': 'PD',
          'robocop': 'RC', 'universal_voxel': 'UV', 'zblood': 'ZB', 'punchout': 'PO'}
SKIP_SETS = {'hdvr'}          # owner, 2026-10-31: skip
WELL_DIR = {'vplus': '_01_DOOM_VanillaVRPlus_ErmacPack', 'aliens': 'Aliens-Eradication-VR-addon',
            'meatgrinder': 'BR_VR_MeatGrinder', 'brutalwolf': 'BrutalWolf', 'hacx': 'HacX', 'bd21': 'br_vr/PK3_pbr',
            'chex': 'Chex-Quest-VR-Weapons', 'cola': 'Cola-3-VR-Weapons', 'd64': 'D64Retribution',
            'voidwalker': 'heretic-voidwalker', 'hocus': 'Hocus-Doom-VR', 'pirate': 'pirate-doom-vr',
            'robocop': 'Robocop-Retribution', 'universal_voxel': 'Universal_Doom_VoxelWeapons_VR',
            'zblood': 'ZBlood-VR/ZBlood-VR-Weapons', 'punchout': 'virtual-punch-out'}
# family -> stock anchor sprite (from the 1.x SHELF)
ANCHOR = {'pistol': 'PISG', 'revolver': 'PISG', 'rifle': 'CHGG', 'sniper': 'CHGG', 'shotgun': 'SHTG',
          'supershotgun': 'SHT2', 'saw': 'SAWG', 'chaingun': 'CHGG', 'plasma': 'PLSG', 'rocket': 'MISG',
          'bfg': 'BFGG', 'smg': 'CHGG', 'machinegun': 'CHGG', 'launcher': 'MISG', 'grenade': 'MISG',
          'railgun': 'PLSG', 'flamethrower': 'PLSG', 'unmaker': 'BFGG', 'melee': 'PUNG', 'axe': 'PUNG',
          'kick': 'PUNG', 'sword': 'PUNG'}


def FAMILY(arche, gun):
    """ModelSwapper family for a card. NAME FIRST (the card archetype is often md3label's default), archetype last."""
    g = gun.lower(); a = (arche or '').lower()
    def has(*ks): return any(k in g for k in ks)
    if has('bfg', 'lazdevice', 'nuker'): return 'bfg'
    if has('unmaker'): return 'unmaker'
    if has('railgun'): return 'railgun'
    if has('superpistol'): return 'pistol'
    if has('zooka'): return 'rocket'
    if has('garand'): return 'rifle'
    if has('tommy'): return 'smg'
    if g in ('melee', 'stick') or has('hx_melee'): return 'melee'
    if has('ssg', 'super', 'sawedoff', 'doublebarrel'): return 'supershotgun'
    if has('flame', 'm260b', 'napalm', 'incendiary'): return 'flamethrower'
    if has('rpg', 'rocket', 'zorchpropulsor', 'sidewinder', 'hellish', 'missile', 'phoenixrod'): return 'rocket'
    if has('machinegun', 'buzzsaw', 'mg42', 'bar'): return 'machinegun'
    if has('chainsaw', 'spork', 'grinder') or g == 'saw': return 'saw'
    if has('axe'): return 'axe'
    if has('boot', 'kick'): return 'kick'
    if has('sword', 'cutlass', 'dragonslayer'): return 'sword'
    if has('knife', 'pitchfork', 'spoon', 'fist', 'glove', 'gauntlet', 'staff', 'mace', 'frypan', 'loader', 'piledriver_melee'): return 'melee'
    if has('grenade', 'bomb', 'tnt', 'satchel', 'carddeck', 'voodoo', 'zippo', 'grog', 'doll') or a == 'thrown': return 'grenade'
    if has('revolver') or g == 'rev': return 'revolver'
    if has('smg', 'tec9', 'mp40', 'tommygun', 'uzi', 'mp5'): return 'smg'
    if has('chaingun', 'minigun', 'rapidzorcher', 'smartgun', 'm56', 'gatling'): return 'chaingun'
    if has('m79', 'm32', 'mortar', 'cannon', 'launcher'): return 'launcher'
    if has('plasma', 'phasing', 'tesla', 'lifeleech', 'cryo', 'particle', 'skullrod', 'm27', 'bolter'): return 'plasma'
    if has('shotgun', 'largezorcher', 'ksg', 'blunderbuss', 'trench', 'piledriver', 'm37'): return 'shotgun'
    if has('rifle', 'm16', 'm41a', 'pulserifle', 'kar98', 'stg44', 'crossbow', 'musket', 'nock', 'cobra', 'repeater', 'sniper'): return 'rifle'
    if has('pistol', 'auto9', 'minizorcher', 'wand', 'blaster', 'dragonclaw', 'flaregun', 'luger', 'm4a3', 'glock', 'superpistol'): return 'pistol'
    if a.startswith('revolver'): return 'revolver'
    if a.startswith('shotgun_break'): return 'supershotgun'
    if a.startswith('shotgun'): return 'shotgun'
    if a.startswith('rifle') or a == 'crossbow': return 'rifle'
    if a in ('chaingun', 'minigun', 'rifle_belt'): return 'chaingun'
    if a.startswith('launcher'): return 'launcher'
    if a == 'energy': return 'plasma'
    if a == 'flamethrower': return 'flamethrower'
    if a == 'melee': return 'melee'
    if a.startswith('pistol') or a == 'flintlock': return 'pistol'
    return None


def place_lines(pl):
    """MODELDEF lines from a placement.json entry. Offset comes last of the three position keys so an explicit
    zoffset still wins when present (the engine takes whichever of Offset.z / ZOffset came last)."""
    f3 = lambda v: ' '.join('%.4f' % float(x) for x in v)
    out = ['\tScale %s' % f3(pl['scale']), '\tOffset %s' % f3(pl['offset'])]
    if pl.get('zoffset') is not None: out.append('\tZOffset %.4f' % float(pl['zoffset']))
    for key, tag in (('angle', 'AngleOffset'), ('pitch', 'PitchOffset'), ('roll', 'RollOffset')):
        if pl.get(key) is not None: out.append('\t%s %.4f' % (tag, float(pl[key])))
    return out


def main_skin(dn):
    """The folder's main texture: the biggest image that is not a render sheet or a muzzle flash."""
    c = [f for f in dn['skins'] if not f.lower().startswith('sheet') and not re.search(r'mf\d*\.|flash|muzzle|_n\.|_r\.|_m\.|_ao\.|_bm\.', f.lower())]
    c = c or dn['skins']
    return max(c, key=lambda f: os.path.getsize(os.path.join(dn['dir'], f)))


def actor_index(roots):
    """{lower actor name: its text} from every DECORATE/ZScript text file under roots."""
    idx = {}
    for root in roots:
        for p in glob.glob(root + '/**/*', recursive=True):
            if not os.path.isfile(p) or os.path.getsize(p) > 3000000 or '/.git/' in p: continue
            if os.path.splitext(p)[1].lower() in ('.png', '.jpg', '.md3', '.md2', '.wav', '.ogg', '.kvx', '.flac', '.mp3', '.pk3', '.wad', '.zip', '.blend', '.psd', '.tga', '.iqm', '.bmp', '.def'): continue
            try: t = open(p, errors='ignore').read()
            except Exception: continue
            if 'States' not in t and 'states' not in t: continue
            t = re.sub(r'//[^\n]*', '', t); t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
            heads = [(m.start(), m.group(1)) for m in re.finditer(r'(?im)^\s*(?:actor|class)\s+(\w+)', t)]
            for k, (pos, name) in enumerate(heads):
                end = heads[k + 1][0] if k + 1 < len(heads) else len(t)
                idx.setdefault(name.lower(), []).append(t[pos:end])
    return idx


def labels(text):
    lab = {}; open_ = []; last_row = True
    for line in text.splitlines():
        st = line.strip()
        for m in re.finditer(r'([A-Za-z_][\w.]*)\s*:(?!:)', st.split('"')[0]):
            # stacked labels (Ready: / Ready3:) share the rows that follow them
            if last_row: open_ = []
            open_.append(m.group(1).lower()); lab.setdefault(open_[-1], []); last_row = False
        m = re.match(r'^(?:[A-Za-z_][\w.]*\s*:\s*)*(\w{4})\s+"?([A-Z\[\]\\#]+)"?\s+(-?\d+)', st)
        if m and open_:
            for L in open_: lab[L].append((m.group(1).upper(), m.group(2)))
            # Universal Doom swaps the sprite at runtime: A_ReplaceSprite("cvar","CHGA,CGD4") -- each listed
            # sprite plays with the same letter
            rs = re.search(r'A_ReplaceSprite\s*\(\s*"[^"]*"\s*,\s*"([^"]+)"', st, re.I)
            if rs:
                for sp in rs.group(1).split(','):
                    for L in open_: lab[L].append((sp.strip().upper(), m.group(2)))
            last_row = True
    return lab


def _ready_in(lab, B):
    for want in ('ready', 'ready.loop', 'readyloop'):
        for spr, letters in lab.get(want, []):
            f = B.get((spr, letters[0]))
            if f is not None: return f, '%s %s%s' % (want, spr, letters[0])
    for L in sorted(lab):
        if 'ready' not in L or L in ('ready', 'ready.loop', 'readyloop') or 'empty' in L: continue
        for spr, letters in lab[L]:
            f = B.get((spr, letters[0]))
            if f is not None: return f, '%s %s%s' % (L, spr, letters[0])
    return None, None


_LABELS = {}
def ready_frame(block, idx):
    """The mesh frame the source shows at Ready: the Ready state of the actor named by the block, or --
    when the block's model name is not that weapon (a renamed or pasted copy: BW '_Axe2', the boot inside
    the RPG) -- of the actor whose Ready state shows a sprite this block binds. Through the block's
    FrameIndex. None if nothing resolves (reported, never guessed)."""
    if not block: return None, 'no source block'
    B = {(b.group(1).upper(), b.group(2).upper()): int(b.group(3)) for b in re.finditer(r'FrameIndex\s+(\w{4})\s+([A-Za-z\[\]\\])\s+0\s+(\d+)', block['body'], re.I)}	# model 0 only (a glove on model 1 has its own frames)
    texts = idx.get(block['name'].lower(), [])
    for text in texts:	# the same actor name can exist in several mods (BD SSG, MeatGrinder SSG)
        f, how = _ready_in(labels(text), B)
        if f is not None: return f, how
    text = texts[0] if texts else None
    sprites = {k[0] for k in B}
    for name, tl in idx.items():
      for k, t in enumerate(tl):
        if not any(sp in t for sp in sprites): continue
        lab = _LABELS.get((name, k))
        if lab is None: lab = _LABELS[(name, k)] = labels(t)
        if not ('select' in lab and 'deselect' in lab): continue	# weapons only
        f, how = _ready_in(lab, B)
        if f is not None: return f, '%s (actor %s)' % (how, name)
    return None, ('Ready frame not in block %s' % block['name']) if text else ('actor %s not found' % block['name'])

# donors with no block of their own that copy another donor's rows (owner, 2026-10-31)
COPY_ROWS = {'MS_D64_Boot': 'MS_BD_Boot'}

def sig(m): return (m['nframes'], tuple(s['xyz'].shape[1] for s in m['surfs']))
def f0(m): return np.concatenate([s['xyz'][0].ravel() for s in m['surfs']])


def parse_blocks(text):
    out = []
    for m in re.finditer(r'Model\s+(\w+)\s*\{(.*?)\}', text, re.S | re.I):
        body = m.group(2)
        p = re.search(r'Path\s+"([^"]+)"', body, re.I); f = re.search(r'Model\s+0\s+"([^"]+)"', body, re.I)
        if not p or not f: continue
        out.append(dict(name=m.group(1), path=p.group(1).replace('\\', '/').strip('/'), file=f.group(1), body=body))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--well', default='/mnt/user-data/uploads/VR_WeaponSetRebuild'); ap.add_argument('--extra', nargs='*', default=['/home/claude/rs_aliens_vr-weaponsq'], help='more roots holding the sets'' own MODELDEFs (the Aliens Q repo)')
    ap.add_argument('--actors', nargs='*', default=sorted(glob.glob('/home/claude/parents/*')), help='parent mods (text lumps) read for actor states only, never for MODELDEF blocks')
    ap.add_argument('--set-extra', nargs='*', default=['meatgrinder=/mnt/user-data/uploads/__Games/MeatGrinder/BR_VR_MeatGrinder', 'vplus=/home/claude/parents/alek'], help='SET=DIR: more MODELDEF/actor files that belong to that one set only (owner\'s D: copy where the well copy is short)')
    ap.add_argument('--placement', default='placement.json', help='per-donor Scale/Offset table (the placement agent writes it); missing file = skipped')
    a = ap.parse_args(); os.chdir(HERE)
    placement = {}
    if os.path.exists(a.placement):
        import json
        try: placement = json.load(open(a.placement))
        except Exception as e: print('placement.json unreadable:', e); placement = {}
    SET_EXTRA = {}
    for kv in a.set_extra:
        k, v = kv.split('=', 1); SET_EXTRA.setdefault(k, []).append(v)
    # ---- the well: every staged mesh by signature, every MODELDEF block by (path,file)
    well_mesh = {}; well_blocks = {}
    for p in [q for root in [a.well] + [v for vs in SET_EXTRA.values() for v in vs] for q in glob.glob(root + '/**/*.md3', recursive=True)]:
        try: m = read_md3(p)
        except Exception: continue
        well_mesh.setdefault(sig(m), []).append((p, m))
    for p in [q for root in [a.well] + a.extra + [v for vs in SET_EXTRA.values() for v in vs] for q in glob.glob(root + '/**/*', recursive=True)]:
        if not os.path.isfile(p) or os.path.getsize(p) > 400000 or '/.git/' in p: continue
        if os.path.splitext(p)[1].lower() in ('.png', '.jpg', '.md3', '.md2', '.wav', '.ogg', '.kvx', '.flac', '.mp3', '.pk3', '.wad', '.zip', '.blend', '.psd', '.tga', '.iqm', '.bmp'): continue
        try: t = open(p, errors='ignore').read()
        except Exception: continue
        if 'frameindex' not in t.lower() and 'model 0' not in t.lower(): continue
        for b in parse_blocks(t):
            b['dir'] = os.path.dirname(p)
            well_blocks.setdefault((os.path.dirname(p), b['path'].lower(), b['file'].lower()), []).append(b)
    idx = actor_index([a.well] + a.extra + a.actors + [v for vs in SET_EXTRA.values() for v in vs])
    # ---- cards
    donors = []; report = []
    for card in sorted(glob.glob('cards/*/*/*.card')):
        if '.blend' in card: continue
        d = os.path.dirname(card); parts = d.split('/'); sset, gun = parts[1], parts[2]
        if sset in SKIP_SETS or gun.startswith('_'): continue
        lab = os.path.basename(card)[:-5]; mesh = os.path.join(d, lab + '.md3')
        if not os.path.exists(mesh): continue
        txt = open(card).read()
        arche = (re.search(r'archetype\s+(\S+)', txt) or [None, ''])[1]
        idle = int((re.search(r'idle_frame\s+(\d+)', txt) or [None, '0'])[1])
        m = read_md3(mesh); nfr = m['nframes']
        fam = FAMILY(arche, gun)
        # source block: match the card mesh to a well mesh, then that mesh's MODELDEF block
        src = None; srcfile = None
        _own = os.path.join(a.well, WELL_DIR[sset])
        for p, wm in sorted(well_mesh.get(sig(m), []), key=lambda t: not t[0].startswith(_own)):
            if np.array_equal(f0(wm), f0(m)):
                srcfile = p
                rel = os.path.relpath(p, a.well).replace('\\', '/')
                setdir = os.path.join(a.well, WELL_DIR[sset])
                exact = [b for (mdir, bpath, bfile), bl in well_blocks.items() for b in bl if bfile == os.path.basename(p).lower() and rel.lower().endswith(bpath + '/' + bfile) and (mdir.startswith(setdir) or any(mdir.startswith(x) for x in (a.extra if sset == 'aliens' else []) + SET_EXTRA.get(sset, [])))]
                same_set = [b for (mdir, bpath, bfile), bl in well_blocks.items() for b in bl if bfile == os.path.basename(p).lower() and (mdir.startswith(setdir) or any(mdir.startswith(x) for x in (a.extra if sset == 'aliens' else []) + SET_EXTRA.get(sset, [])))]
                cands = exact + [b for b in same_set if b not in exact]
                # the set's own well folder wins over add-on sources (alek's DoomGuns, the D: copies);
                # inside each tier prefer the block whose actor's Ready state resolves
                own = [b for b in cands if b.get('dir', '').startswith(setdir)]
                tier = own or cands
                src = next((b for b in tier if ready_frame(b, idx)[0] is not None), (tier or [None])[0])
                if src: break
        if src is None:
            # carved or re-encoded card mesh: same frame count and same whole-mesh frame-0 bounds,
            # inside this set's own well folder (never another set's)
            setdir = os.path.join(a.well, WELL_DIR[sset])
            allv = np.concatenate([s_['xyz'][0] for s_ in m['surfs']]); lo, hi = allv.min(0), allv.max(0)
            best = None
            for key, lst in well_mesh.items():
                if key[0] != nfr: continue
                for p, wm in lst:
                    if not p.startswith(setdir): continue
                    wv = np.concatenate([s_['xyz'][0] for s_ in wm['surfs']])
                    err = max(np.abs(wv.min(0) - lo).max(), np.abs(wv.max(0) - hi).max())
                    if err < 0.5 and (best is None or err < best[0]): best = (err, p)
            if best:
                p = best[1]; srcfile = p
                rel = os.path.relpath(p, a.well).replace('\\', '/')
                exact = [b for (mdir, bpath, bfile), bl in well_blocks.items() for b in bl if bfile == os.path.basename(p).lower() and rel.lower().endswith(bpath + '/' + bfile) and (mdir.startswith(setdir) or any(mdir.startswith(x) for x in (a.extra if sset == 'aliens' else []) + SET_EXTRA.get(sset, [])))]
                same_set = [b for (mdir, bpath, bfile), bl in well_blocks.items() for b in bl if bfile == os.path.basename(p).lower() and (mdir.startswith(setdir) or any(mdir.startswith(x) for x in SET_EXTRA.get(sset, [])))]
                cands = exact + [b for b in same_set if b not in exact]
                own = [b for b in cands if b.get('dir', '').startswith(setdir)]
                tier = own or cands
                src = next((b for b in tier if ready_frame(b, idx)[0] is not None), (tier or [None])[0])
        card_idle = idle; rf, rwhy = ready_frame(src, idx)
        if rf is not None and rf < nfr: idle = rf
        skins = sorted(f for f in os.listdir(d) if f.lower().endswith(('.png', '.jpg', '.tga')))
        name = 'MS_%s_%s' % (PREFIX[sset], ''.join(w.capitalize() for w in re.split(r'[_\-]', gun)))
        donors.append(dict(name=name, set=sset, gun=gun, dir=d, mesh=os.path.basename(mesh), arche=arche, fam=fam,
                           idle=idle, nfr=nfr, rf=rf, rwhy=rwhy, card_idle=card_idle, src=src, srcfile=srcfile, skins=skins))
    with open('ready_frames.report.md', 'w') as fo:
        fo.write('# Rest frame per donor: OG MODELDEF Ready state vs card idle\n\n| donor | card idle | OG Ready frame | how |\n|---|---|---|---|\n')
        for dn in donors:
            fo.write('| %s | %d | %s | %s |\n' % (dn['name'], dn['card_idle'], '-' if dn['rf'] is None else dn['rf'], dn['rwhy']))
    byname = {dn['name']: dn for dn in donors}
    for dst, srcn in COPY_ROWS.items():
        if dst in byname and srcn in byname and byname[dst]['src'] is None:
            byname[dst]['src'] = byname[srcn]['src']; byname[dst]['copied_from'] = srcn
    # ---- modeldef
    head = open('modeldef').read().split('\nModel ', 1)[0]
    head = '\n'.join(l for l in head.splitlines() if not l.startswith('// ---- GENERATED by tools_gen_from_cards.py')).rstrip() + '\n'
    out = [head, '// ---- GENERATED by tools_gen_from_cards.py from cards/ (MS 1.5). Do not edit below; edit the cards.\n']
    for dn in donors:
        b = dn['src']; lines = ['Model %s' % dn['name'], '{',
                                '\t// source: %s' % ((os.path.relpath(dn['srcfile'], a.well) if dn['srcfile'].startswith(a.well) else 'add-on ' + dn['srcfile']) if dn['srcfile'] else 'no well match -> PLACEMENT needed'),
                                '\tPath "%s"' % dn['dir'], '\tModel 0 "%s"' % dn['mesh']]
        pl = placement.get(dn['name'])
        dn['placement'] = ('%s (%s)' % (pl.get('method', '?'), pl.get('ref', '-'))) if pl else ''
        if pl: lines.append('\t// placement: %s (%s)%s' % (pl.get('method', '?'), pl.get('ref', '-'), (' -- ' + pl['note']) if pl.get('note') else ''))
        if b:
            body = b['body']
            sk = re.findall(r'^\s*(SurfaceSkin\s+0\s+\d+\s+"[^"]+"|Skin\s+0\s+"[^"]+")', body, re.M | re.I)
            sk = [s for s in sk if re.search(r'"([^"]+)"', s).group(1) in dn['skins'] or re.search(r'"([^"]+)"', s).group(1).lower() in [x.lower() for x in dn['skins']]]
            if not sk and dn['skins']:
                sk = ['Skin 0 "%s"' % main_skin(dn)]; dn['skin_note'] = 'source skin %s not in folder; used %s' % (re.findall(r'Skin\s+0\s+"([^"]+)"', body)[:1], main_skin(dn))
            lines += ['\t' + s.strip() for s in sk]
            if not pl:
                for key in ('Scale', 'Offset', 'ZOffset', 'AngleOffset', 'PitchOffset', 'RollOffset'):
                    mm = re.search(r'^\s*%s\s+([^\n/]+)' % key, body, re.M | re.I)
                    if mm: lines.append('\t%s %s' % (key, mm.group(1).strip()))
            if re.search(r'NoInterpolation', body, re.I): lines.append('\tNoInterpolation')
        else:
            if dn['skins']: lines.append('\tSkin 0 "%s"' % main_skin(dn))
            if not pl: lines += ['\tScale 1.0 1.0 1.0', '\tOffset 0.0 0.0 0.0']
        if pl:
            lines += place_lines(pl)
        anchor = ANCHOR.get(dn['fam'] or '', 'PISG')
        lines += ['\tFrameIndex %s A 0 %d' % (anchor, min(dn['idle'], dn['nfr'] - 1)), '\tFrameIndex MSBL A 0 9999', '}', '']
        out.append('\n'.join(lines))
    open('modeldef', 'w').write('\n'.join(out))
    # ---- zscript.txt donor classes (both copies)
    for zf in ('zscript.txt', 'quest/zscript.txt'):
        if not os.path.exists(zf): continue
        t = open(zf).read()
        gen = '// GEN-DONORS-BEGIN (tools_gen_from_cards.py)\n' + '\n'.join('class %s : Actor {}' % dn['name'] for dn in donors) + '\n// GEN-DONORS-END\n'
        t = re.sub(r'// GEN-DONORS-BEGIN.*?// GEN-DONORS-END\n', '', t, flags=re.S)
        # every 1.x donor stub, wherever it sits in the file (the imports appended their own lists): one GEN block replaces them all
        first = re.search(r'^class MS_\w+ : Actor \{\}\n', t, re.M)
        t = re.sub(r'^class MS_\w+ : Actor \{\}\n', '', t, flags=re.M)
        t = re.sub(r'^(// -{3,}.*\n)+(?=\n*(// -{3,}|$))', '', t, flags=re.M) if False else t
        pos = first.start() if first else len(t)
        t = t[:pos] + gen + t[pos:]
        open(zf, 'w').write(t)
    # ---- SHELF and NAMES
    zs = 'zscript/RS_ForeignModels.zs'; t = open(zs).read()
    shelf = ',\n'.join('\t\t\t"%s|%s|%s|0|%d|%d"' % (dn['fam'], dn['name'], ANCHOR.get(dn['fam'], 'PISG'), min(dn['idle'], dn['nfr'] - 1), dn['nfr']) for dn in donors if dn['fam'])
    names = ',\n'.join('\t\t\t"%s|%s %s"' % (dn['name'], dn['set'], dn['gun']) for dn in donors)
    t = re.sub(r'(static const string SHELF\[\] = \{\n).*?(\n\t\t\};)', lambda m: m.group(1) + shelf + m.group(2), t, count=1, flags=re.S)
    t = re.sub(r'(static const string NAMES\[\] = \{\n).*?(\n\t\t\};)', lambda m: m.group(1) + names + m.group(2), t, count=1, flags=re.S)
    open(zs, 'w').write(t)
    # ---- report
    rep = ['# gen_from_cards report', '', '| donor | set/gun | family | source block | placement | skins |', '|---|---|---|---|---|---|']
    for dn in donors:
        rep.append('| %s | %s/%s | %s | %s | %s | %s |' % (dn['name'], dn['set'], dn['gun'], dn['fam'] or '**NONE (not shelved)**',
                   ('%s::%s' % (os.path.relpath(dn['srcfile'], a.well), dn['src']['name'])) if dn['src'] else (('mesh matched, no block: ' + os.path.relpath(dn['srcfile'], a.well)) if dn['srcfile'] else '**PLACEMENT needed**'),
                   dn.get('placement') or '(source numbers)', ', '.join(dn['skins'][:3]) + (' -- ' + dn['skin_note'] if dn.get('skin_note') else '')))
    open('gen_from_cards.report.md', 'w').write('\n'.join(rep) + '\n')
    print('placed from %s: %d' % (a.placement, sum(1 for d in donors if d.get('placement'))))
    print('donors', len(donors), '| shelved', sum(1 for d in donors if d['fam']), '| with source block', sum(1 for d in donors if d['src']), '| placement needed', sum(1 for d in donors if not d['srcfile']))


if __name__ == '__main__': main()
