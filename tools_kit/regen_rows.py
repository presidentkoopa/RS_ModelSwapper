"""regen_rows.py -- each card-measured donor gets a reload row made at the placement it is DRAWN at.

    python -B tools_kit/regen_rows.py [--dry] [--only MS_A,MS_B]

WHY
ModelSwapper's older reload rows (slots 3-30) were made by genpack.py from the cards at the card's
placement (its `palm` on the Quest grip reference) and several donors share one row; each donor
is drawn at its own block's placement, which handfit_cards.py fitted its HAND to (measured: the
shipped hooks land on the palm at the donor's placement, e.g. brt_RPG 4 cm vs 26 cm at the row's).
So the hands and the drawing agree and the reload row is the odd one out -- up to 1.4 m off
(placement_audit.py). And no MODELDEF ever drew those rows' layers: mid-reload the gun vanished.

WHAT
For every donor with a reload slot whose OWN card is on a real mesh (not a _wm rebuild) and whose
drawn mesh IS that mesh, the kit's own chain is run at the donor's placement and rest frame:
card2quest.geometry -> genpack.build_gun -> gen_rsr.compute / zs / modeldef. Run at the card's
placement the same chain gives back the shipped rows to 0.001 cm (checked on MS_Pistol), so this
is the generator ModelSwapper's rows came from, pointed at where the gun actually is.

Each regenerated donor gets its OWN reload slot (appended; SlotForDonor re-pointed) -- a shared
row can only fit one placement, and the donors not regenerated keep the old rows untouched.
Layer blocks go to MODELDEF.cards (regenerated whole), from the donor's own mesh folder and skin.
Names that were the cards' own (sounds, ammo) become ModelSwapper's: no ammo names (the mod's own
two stores), foley aliased by gun type onto the shipped ms/bd22 foley. Re-runnable: a donor that
already has a generated slot (sprite in the QV.. / QW.. range) is rewritten in place.
Run tools_kit/fix_layer_skins.py after (rsr_clear.png beside each mesh).
"""
import os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import card2quest as C, genpack as G, gen_rsr
import lift_common as L, placement_audit as PA
from lift_common import add_slot_for_donor, count_of

B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
CODES = ['V' + c for c in B36] + ['W' + c for c in B36]        # QV0M ... QWZM: this tool's sprites
SKIP_SLOTS = {1, 2, 17}                                         # the Aliens set's rows (lift_aliens.py)
# foley by card type -> the ms/bd22 foley already shipped (lift_bd22.py)
FOLEY = {'pistol': 'pistol', 'revolver': 'pistol', 'smg': 'smg', 'rifle': 'rifle', 'machinegun': 'rifle',
         'chaingun': 'rifle', 'shotgun': 'assaultshotgun', 'plasma': 'plasmagun', 'cell': 'plasmagun',
         'railgun': 'railgun', 'launcher': 'rocketlauncher', 'rocket': 'rocketlauncher', 'flamethrower': 'rocketlauncher'}


def donor_slots(rsr):
    out = {}
    for d, s in re.findall(r'donor == "(\w+)"\)\s*return (\d+);', rsr):
        out.setdefault(d, int(s))
    return out


def candidates(only=None):
    rsr = open(os.path.join(ROOT, 'zscript_depot/rsr/rsr_guns.ms.zs')).read()
    # class names are case-insensitive in the engine; the cards were not always written with the
    # donor's spelling (WMCARD.ww2 "MS_wolf_Kar98" is the donor MS_wolf_KAR98)
    # and where a donor has two cards (a _wm rebuild's and one measured on its own mesh,
    # card_leftovers.py), the one on a real mesh is the one that describes what is drawn
    cards = {}
    for w in C.load_cards(ROOT):
        k = w['cls'].lower()
        wm = '_wm' in os.path.basename(C.model_path(ROOT, w) or '').lower()
        if k not in cards or not wm:
            cards[k] = w
    blocks = PA.donor_blocks(); rest = PA.shelf_rest()
    out, notes = [], []
    for d, s in sorted(donor_slots(rsr).items(), key=lambda kv: kv[1]):
        if only and d not in only:
            continue
        if s in SKIP_SLOTS or d.startswith('MS_PU_') or d.startswith('MS_BD22_') or d.startswith('MS_alien_') or d not in blocks:
            continue
        w = cards.get(d.lower())
        if not w:
            notes.append((d, 'no card')); continue
        cm = PA.resolve(C.model_path(ROOT, w) or '')
        if not os.path.exists(cm) or '_wm' in os.path.basename(cm).lower():
            notes.append((d, 'card mesh is a _wm rebuild')); continue
        body = blocks[d]
        path = re.search(r'Path\s+"([^"]+)"', body).group(1); model = re.search(r'Model\s+0\s+"([^"]+)"', body).group(1)
        dm = PA.resolve(os.path.join(ROOT, path, model))
        if not os.path.exists(dm) or open(dm, 'rb').read() != open(cm, 'rb').read():
            notes.append((d, 'drawn mesh is not the card\'s file')); continue
        sk = re.search(r'^\s*Skin\s+0\s+"([^"]+)"', body, re.M)
        sc, of = PA.placement(body)
        out.append(dict(donor=d, slot=s, card=w, mesh=dm, path=path, model=model, skin=sk.group(1) if sk else None,
                        scale=tuple(sc), off=tuple(of), frame=rest.get(d, 0)))
    return out, notes


MOTION_DIRS = ('cards_shelf', 'cards_hud', 'cards_packs', 'cards_bd', 'cards_left')
V3 = r'\[\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\s*\]'


def motion_handle(w):
    """The charging handle from the donor's own motion card, for a card that has none.

    The shelf's cards (WMCARD.shelf) were written from md3label's motion cards with the magazine
    only: card_from_motion read a `bolt` and never a `slide`, and md3label names a rifle's handle
    `slide`. The motion card is still on disk. Its part is used only when the evidence says it is
    this gun's handle in this card's frame: the motion card's magazine rest is the card's magazine
    grab (same mesh, same frame, to 0.05 units), the part slides BACK along the bore (axis x <= -0.9;
    a part going forward is not a handle the hand pulls) by 2 units or more, and the gun is not a
    shotgun (a shotgun's slide is its pump: the pump reload's). Returns the part, or None."""
    if str(w['keys'].get('type', '')).lower() in ('shotgun', 'pump', 'supershotgun'):
        return None
    mag = next((p for p in w['parts'].values() if p['keys'].get('role') == 'feed'), None)
    if not mag or any(p['keys'].get('role') == 'action' for p in w['parts'].values()):
        return None
    g = np.array([float(x) for x in mag['keys']['grab']])
    for d in MOTION_DIRS:
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        f = next((x for x in os.listdir(dd) if x.lower() == w['cls'].lower() + '.card'), None)
        if not f:
            continue
        t = open(os.path.join(dd, f), encoding='utf-8', errors='replace').read()
        m = re.search(r'^\s*mag\s+surf\s+\d+\s+rest\s+' + V3, t, re.M)
        if not m or np.linalg.norm(np.array([float(x) for x in m.groups()]) - g) > 0.05:
            continue
        s = re.search(r'^\s*(slide|bolt)\s+surf\s+\d+\s+rest\s+' + V3 + r'\s+axis\s+' + V3 + r'\s+travel\s+([\d.]+)', t, re.M)
        if not s:
            return None
        v = [float(x) for x in s.groups()[1:]]
        if v[3] > -0.9 or v[6] < 2.0:
            return None
        return dict(name='bolt', surfaces=['bolt'], keys=dict(role='action', subject='slide', grab=v[0:3], grabradius=2.5),
                    dof=dict(kind='slide', axis=v[3:6], distance=v[6]), src='%s/%s' % (d, f))
    return None


def build(c, codes_used):
    w = c['card']
    hp = motion_handle(w)
    if hp:
        w = dict(w, parts=dict(w['parts'], bolt=hp), order=list(w['order']) + ['bolt'])
    geo = C.geometry(w, c['scale'], c['off'])
    rec = dict(hud_scale=c['scale'], offset=c['off'], rest_frame=c['frame'], parts=geo['parts'], type=w['keys'].get('type'))
    nfr, surfs = G.md3_surfaces(c['mesh']); names = [s['name'] for s in surfs]
    code = c.get('code') or next(x for x in CODES if x not in codes_used)
    spr = dict(gun='Q%sR' % code, m='Q%sM' % code, p='Q%sP' % code, w='Q%sW' % code, pick='Q%sS' % code)
    g, sv = G.build_gun(ROOT, w, c['donor'], rec, names, surfs, nfr, spr)
    if not g:
        return None, sv, code
    g['mesh'] = c['mesh']
    comp = gen_rsr.compute(dict(g), {g['key']: sv})
    # the layers draw from the donor's own folder with its own skin (the same file as the card's)
    comp['path'], comp['model'] = c['path'], c['model']
    if c['skin'] and 'skins' not in comp:
        comp['skin'] = c['skin']
    return comp, None, code


def main(dry, only):
    p_rsr = os.path.join(ROOT, 'zscript_depot/rsr/rsr_guns.ms.zs'); rsr = open(p_rsr).read()
    # MODELDEF.cards, the sprite list and the foley section are written WHOLE: every donor is always
    # built, and --only only narrows the report (a filtered build once wrote one gun and dropped 31)
    cands, notes = candidates(None)
    shelf = open(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs')).read()
    used = set(re.findall(r"'Q([VW][0-9A-Z])M'", rsr))
    md, sprites, tokens, snd = [], {}, [], []
    report = []
    for c in cands:
        d = c['donor']
        old = L.read_row(rsr, c['slot'])
        mine = re.match(r"'Q([VW][0-9A-Z])M'", old['SprGun'][1])
        if mine:
            c['code'] = mine.group(1)
        try:
            comp, why, code = build(c, used)
        except Exception as e:
            report.append('%-26s build error: %s' % (d, e)); continue
        if comp is None:
            report.append('%-26s no VR reload from its card: %s (keeps slot %d)' % (d, why, c['slot'])); continue
        used.add(code)
        new = L.read_row('\n'.join(gen_rsr.zs([comp])), 1)
        typ = str(c['card']['keys'].get('type', 'rifle')).lower()
        fol = 'ms/bd22/%s' % FOLEY.get(typ, 'rifle')
        alias = 'ms/card/%s' % d[3:].lower()
        anchor = re.search(r'"\w+\|%s\|(\w{4})\|' % d, shelf).group(1)
        has_handle = comp['handle_mode'] is not None
        v = {k: x for k, x in new.items() if k not in ('Index',)}
        v.update(MagAmmo=('case', '""'), Reserve=('case', '""'), ReloadToken=('case', '""'),
                 NoMag=('case', '"RSR_NoMag_%s"' % d), ReadySprites=('case', '"%s A"' % anchor),
                 SndOut=('case', '"%s/magout"' % alias), SndIn=('case', '"%s/magin"' % alias),
                 SndBack=('case', '"%s/slideback"' % alias if has_handle else '""'),
                 SndFwd=('case', '"%s/slidefwd"' % alias if has_handle else '""'),
                 SndLand=('case', '"%s/magdrop"' % alias),
                 SlideLock=('arr', {'v': 'true' if comp.get('slide_lock') else 'false'}))
        if mine:
            slot = c['slot']
        else:
            slot = count_of(rsr) + 1
            rsr = re.sub(r'(static int Count\(\) \{ return )\d+(; \})', r'\g<1>%d\2' % slot, rsr)
            rsr = re.sub(r'^[ \t]*if \(donor == "%s"\)\s*return \d+;\n' % d, '', rsr, flags=re.M)
            rsr = add_slot_for_donor(rsr, d, slot)
        rsr = L.set_row(rsr, slot, v)
        tokens.append('RSR_NoMag_%s' % d)
        lines = gen_rsr.modeldef(comp)
        md += lines
        for l in lines:
            m = re.match(r'\s*FrameIndex\s+(\w{4})\s+(\S)\s', l)
            if m:
                sprites.setdefault(m.group(1), set()).add(m.group(2))
        for what in ('magout', 'magin', 'slideback', 'slidefwd', 'magdrop'):
            src = 'ms' if what == 'magdrop' else fol
            if what in ('slideback', 'slidefwd') and FOLEY.get(typ) in ('plasmagun', 'railgun', 'rocketlauncher', None):
                src = 'ms/bd22/rifle'          # those foley sets have no rack: a handle racks like a rifle
            snd.append('$alias %s/%s %s/%s' % (alias, what, src, what))
        report.append('%-26s slot %2d -> %2d  %s, frame %d, handle %s, well %.0f cm from the grip'
                      % (d, c['slot'], slot, 'rewritten' if mine else 'own row', c['frame'], comp['handle_mode'],
                         np.linalg.norm(np.array(comp['well']) - C.GRIP_REF)))
    for d, why in notes:
        report.append('%-26s left: %s' % (d, why))
    print('\n'.join(r for r in report if not only or r.split()[0] in only))
    if dry:
        return
    # sprite registration + NoMag tokens (a MODELDEF naming an unknown sprite stops the pk3 loading)
    rsr = re.sub(r'\n// Card-regenerated guns \(tools_kit/regen_rows\.py\).*', '', rsr, flags=re.S).rstrip('\n') + '\n'
    rsr += '\n// Card-regenerated guns (tools_kit/regen_rows.py)\n'
    rsr += ''.join('class %s : RSVR_Token {}\n' % n for n in sorted(set(tokens)) if not re.search(r'^class %s\b' % n, rsr, re.M | re.I))
    rsr += ('class RSR_Sprites_Cards : Actor\n{\n\tStates\n\t{\n\tSpawn:\n%s\n\t\tStop;\n\t}\n}\n'
            % '\n'.join('\t\t%s %s 0;' % (s, ''.join(sorted(l))) for s, l in sorted(sprites.items())))
    open(p_rsr, 'w', newline='\n').write(rsr)
    open(os.path.join(ROOT, 'MODELDEF.cards'), 'w', newline='\n').write(
        '// GENERATED by tools_kit/regen_rows.py -- do not edit by hand. Reload layers for the card-measured\n'
        '// donors, made by the kit\'s gen_rsr at each donor\'s own placement and drawn from its own folder.\n'
        + '\n'.join(md) + '\n')
    p_s = os.path.join(ROOT, 'SNDINFO.ms'); s = open(p_s).read()
    s = re.sub(r'\n// ---- card-regenerated guns \(tools_kit/regen_rows\.py\).*', '', s, flags=re.S).rstrip('\n')
    open(p_s, 'w', newline='\n').write(s + '\n\n// ---- card-regenerated guns (tools_kit/regen_rows.py)\n' + '\n'.join(snd) + '\n')


if __name__ == '__main__':
    only = set(sys.argv[sys.argv.index('--only') + 1].split(',')) if '--only' in sys.argv else None
    main('--dry' in sys.argv, only)
