"""Generate ModelSwapper's magazine-reload table, and the donor lookup that drives it.

gen_modelswapper.py runs genpack's per-gun loop over an explicit list of classes.
It had no driver, so the list that produced the shipped table was never written
down and the table could not be regenerated -- and the one function the generator
did not own, the donor lookup, was hand-written into its output and reverted on
every run. This is that driver. It owns three things the generator cannot know:

  WHERE THE SCALES COME FROM.  c2q.modeldef_scales wants <root>/MODELDEF.txt.
    ModelSwapper's lump is named `modeldef`, and the scales for the guns REMA
    measured live in RS_VR_Weapons. The table is keyed on the mesh FILENAME rather
    than the class, so the sources concatenate -- REMA FIRST, because where both
    name the same mesh REMA's is the scale its cards were measured against. The
    order is not cosmetic: with ModelSwapper's first, MS_Pistol's well comes out
    15 cm from where the shipped table has it.

  WHERE THE MESHES ARE.  A card measured for one package can name a mesh that
    ships in another: the BD22 cards were measured against the static `_wm` copies
    under RS_VR_Weapons/bd22, while the mesh we ship is the animated one in our
    own models/. Hence a search path rather than one root.

  WHICH DONORS CLAIM A SLOT.  A slot is geometry, measured off one mesh. Every
    model on the shelf that IS that mesh reloads identically, so each claims the
    slot -- the plasma rifle's is shared by several names. Same vertex count is a
    candidate and never a conclusion (card_match.py: three pairs matched on count
    alone and were different guns); the sorted distances from the centroid are
    invariant to rotation and translation, so they settle it.

The gun list is not hand-written either: every carded class is offered, and the
generator's own gates decide. A gun is in because its measurements survived
them, and the report says what each gate did. Because the driver writes the table
and the donor lookup in the same run, slot numbers are free to move -- the two
sides can never drift apart.

usage: python -B tools_kit/run_modelswapper.py [out.zs]
       default out: zscript_depot/rsr/rsr_guns.ms.zs
"""
import os, re, sys, io, json, glob, contextlib
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
REMA = os.path.abspath(os.path.join(ROOT, '..', 'RS_VR_Weapons'))
sys.path.insert(0, os.path.join(ROOT, 'tools_kit'))
sys.dont_write_bytecode = True

import card2quest as c2q
import genpack as gp
from md3read import read_md3

# A CARD'S SCALE COMES FROM THE MODELDEF IT WAS MEASURED AGAINST.
#
# Both packages give a Scale for some of the same meshes, and they disagree. Which is
# right is not a matter of order: it depends on which modeldef the card in hand was
# written against.
#
#   our own WMCARD.shelf      run_shelf_cards.py reads ModelSwapper's `modeldef` for
#                             every donor's dir, mesh and skin, so a shelf card's
#                             numbers are in ModelSwapper's scale.
#   REMA's WMCARD.01_pistol   measured in RS_VR_Weapons against its MODELDEF.txt and
#   and the rest              its sub-modeldefs.
#
# So the table is built per mesh: a mesh only ever named by shelf cards takes
# ModelSwapper's scale, and anything REMA carded takes REMA's. Getting this backwards
# is not subtle -- MS_Pistol's well moves 15 cm, off the gun it was measured on.
REMA_SCALES = [os.path.join(REMA, 'MODELDEF.txt'),
               os.path.join(REMA, 'plus', 'MODELDEF.txt'),
               os.path.join(REMA, 'RS_Modern', 'MODELDEF.txt'),
               os.path.join(REMA, 'RS_Modern', 'MODELDEF.breach'),
               os.path.join(REMA, 'bd22', 'MODELDEF.txt')]
OUR_SCALES = [os.path.join(ROOT, 'modeldef')]
SCALE_SOURCES = REMA_SCALES + OUR_SCALES
# the lumps whose cards were measured against ModelSwapper's own modeldef
OUR_LUMPS = ('WMCARD.shelf',)

# Our own tree first -- the mesh we ship is the animated one. REMA's static `_wm`
# measurement copies are the fallback, and are never packed (build.ps1 refuses them).
MESH_ROOTS = [REMA, os.path.join(REMA, 'bd22'),
              os.path.join(REMA, 'plus'), os.path.join(REMA, 'RS_Modern')]

OUT = os.path.join(ROOT, 'zscript_depot', 'rsr', 'rsr_guns.ms.zs')
SLOTS_JSON = os.path.join(ROOT, 'reload_slots.json')


def scale_table(paths):
    """mesh -> MODELDEF Scale, under BOTH its full path and its bare filename.

    A BASENAME IS NOT A MESH IDENTITY. `Pistol.md3` is shipped by hdvr, vplus, d64 and
    others, and `shotgun.md3` by as many again; keyed on the filename alone they all
    collect whichever block the reader happened to see first, and four guns ended up
    measured at another mod's scale. The full path -- which every Model block gives, as
    `Path` plus `Model 0` -- is unique, so it is the key that is tried first. The bare
    name stays as the fallback, for a card naming a mesh no block on the shelf does.
    """
    out = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        t = open(p, encoding='latin-1').read()
        for _cls, b in re.findall(r'Model\s+(\S+)\s*\{(.*?)\n\}', t, re.S):
            pth = re.search(r'Path\s+"([^"]+)"', b)
            mdl = re.search(r'Model\s+0\s+"([^"]+)"', b)
            sc = re.search(r'^\s*Scale\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)', b, re.M)
            if not (mdl and sc):
                continue
            v = tuple(float(x) for x in sc.groups())
            if pth:
                out.setdefault(mesh_key(pth.group(1), mdl.group(1)), v)
            out.setdefault(os.path.basename(mdl.group(1)).lower(), v)
    return out


def mesh_key(d, f):
    """the lookup key for a mesh: its path, normalised -- `models/wolf/MP40/MP40.md3`"""
    return (str(d or '').replace('\\', '/').strip('/') + '/' +
            str(f).replace('\\', '/')).lower().lstrip('/')


def cards_by_lump():
    """lump filename -> the classes it declares"""
    out = {}
    for p in sorted(os.listdir(ROOT)):
        if p.startswith('WMCARD.'):
            t = open(os.path.join(ROOT, p), encoding='utf-8', errors='replace').read()
            out[p] = set(re.findall(r'(?m)^weapon "([^"]+)"', t))
    return out


def scales(_root=None):
    """the per-mesh scale table, each mesh taking the scale of the modeldef the card
    that names it was measured against (see the comment on REMA_SCALES).

    AND IN THE CONVENTION THE CALLER EXPECTS. gen_modelswapper divides every scale by
    c2q.WORLD_PER_HUD, because REMA's MODELDEF carries the WORLD scale and the card's
    numbers are in the HUD scale, which is 1/0.34 of it. Our own `modeldef` does not
    work that way: its blocks ARE the HUD models the player holds, so its Scale is
    already the HUD scale -- which is why handfit_cards hands the same number straight
    to c2q.geometry without touching it.

    Dividing it again made every gun our modeldef owns 2.94x too big: the MP40 came out
    193 cm instead of 66, the Garand 360 instead of 122, the RPG 301 instead of 102.
    That is the whole reason nine shipped slots had wells a metre from the grip -- not
    their cards, which measure their own meshes correctly, and not the rest frame.
    So our scales are converted INTO the world convention here, and the generator's
    division gives back exactly the HUD scale they already were.
    """
    rema, ours = scale_table(REMA_SCALES), scale_table(OUR_SCALES)
    ours = {k: tuple(v * c2q.WORLD_PER_HUD for v in sc) for k, sc in ours.items()}
    bylump = cards_by_lump()
    oursonly = set().union(*[bylump.get(l, set()) for l in OUR_LUMPS]) if OUR_LUMPS else set()
    remacarded = set().union(*[v for l, v in bylump.items() if l not in OUR_LUMPS]) or set()
    # which meshes each group's cards name
    def meshes(classes):
        got = set()
        for w in c2q.load_cards(ROOT):
            if w['cls'] in classes:
                m = w['keys'].get('model')
                if isinstance(m, list) and len(m) > 1:
                    got.add(mesh_key(m[0], m[1]))
        return got
    # OUR MODELDEF WINS WHEREVER WE HAVE ONE, because it is the one the engine draws
    # with. A reload geometry computed at a scale the game does not use would put the
    # well somewhere the gun is not. REMA's is the fallback, for the measurement meshes
    # our own modeldef never names.
    #
    # This used to be the other way round, and had to be: before our scales were
    # converted into the world convention above, taking ours first divided a HUD scale
    # by 0.34 and moved MS_Pistol's well 15 cm. With that fixed the two agree on all but
    # four meshes, and on those four the hand fit -- which reads our modeldef directly,
    # as handfit_cards always has -- was already using ours. Now the reload does too,
    # so hands and reload can no longer disagree about how big a gun is.
    _ = meshes(oursonly), meshes(remacarded)      # provenance, kept for the report
    out = dict(rema)
    out.update(ours)
    return out


def carded_classes():
    b = cards_by_lump()
    return sorted(set().union(*b.values())) if b else []


# ---------------------------------------------------------------- the shelf, by mesh
def signature(path):
    """(total vertex count, sorted distances from the centroid) -- invariant to any
    rotation or translation, so two meshes with the same signature are the same gun."""
    m = read_md3(path)
    P = np.vstack([s['xyz'][0] for s in m['surfs']])
    return P.shape[0], np.sort(np.linalg.norm(P - P.mean(0), axis=1))


def shelf_models():
    """donor model name -> its mesh path, from the modeldef we ship"""
    md = open(os.path.join(ROOT, 'modeldef'), encoding='utf-8', errors='replace').read()
    out = {}
    for blk in re.finditer(r'(?ms)^Model\s+(\S+)\s*\r?\n\{(.*?)^\}', md):
        name, body = blk.group(1), blk.group(2)
        p = re.search(r'Path\s+"([^"]+)"', body)
        f = re.search(r'Model\s+0\s+"([^"]+)"', body)
        if p and f:
            out[name] = os.path.join(ROOT, p.group(1).rstrip('/'), f.group(1))
    return out


def donors_for(slot_mesh, shelf, cache):
    """every shelf model that is provably the same mesh as this slot's"""
    try:
        want = signature(slot_mesh)
    except Exception:
        return []
    hit = []
    for name, path in sorted(shelf.items()):
        if not os.path.exists(path):
            continue
        if name not in cache:
            try:
                cache[name] = signature(path)
            except Exception:
                cache[name] = None
        s = cache[name]
        if not s or s[0] != want[0]:
            continue
        if float(np.abs(s[1] - want[1]).max()) <= 0.5:
            hit.append(name)
    return hit


# ---------------------------------------------------------------- the donor lookup
def lookup_zs(slot_donors):
    """DonorInHand / SlotForDonor / Index, emitted here rather than hand-written into
    the generator's output -- where every regeneration reverted it."""
    L = []
    a = L.append
    a('')
    a('\t// ModelSwapper\'s Index(). A standalone pack\'s weapon IS the gun, so a generated')
    a('\t// Index() matches on the weapon\'s class. Here the weapon belongs to whatever mod')
    a('\t// is loaded and only its MODEL is ours, so the slot comes from the model in hand.')
    a('\t//')
    a('\t// Written by tools_kit/run_modelswapper.py together with the table above, so the')
    a('\t// two can never disagree about what slot a gun is.')
    a('\tclearscope static int Index(Weapon w)')
    a('\t{')
    a('\t\tif (!w) return 0;')
    a('\t\treturn SlotForDonor(DonorInHand(HandOf(w)));')
    a('\t}')
    a('')
    a('\tclearscope static int HandOf(Weapon w)')
    a('\t{')
    a('\t\treturn 0;')
    a('\t}')
    a('')
    a('\t// The donor model worn by this hand, as RS_ForeignModelHandler published it.')
    a('\t//')
    a('\t// NOT ServiceIterator: Service.GetString is `play`, this function is `clearscope`')
    a('\t// (rsr_pump.zs calls Index() from Places() / Place(), which the engine reaches')
    a('\t// through Weapon.ModifyBobLayer3D -- `virtual ui`), and the facts live on a')
    a('\t// StaticEventHandler, which is `native play`. Three scopes, none able to reach the')
    a('\t// others. `struct CVar native` has no scope qualifier, so it is readable from all')
    a('\t// three.')
    a('\t//')
    a('\t// Empty when no model is worn -- SlotForDonor answers 0 for that, which is the')
    a('\t// stock reload, so nothing here changes a weapon with no model of ours on it.')
    a('\tclearscope static string DonorInHand(int hand)')
    a('\t{')
    a("\t\tlet cv = CVar.FindCVar(hand == 1 ? 'ms_donor_off' : 'ms_donor_main');")
    a('\t\treturn cv ? cv.GetString() : "";')
    a('\t}')
    a('')
    a('\t// Several models are the same mesh under different names, so each claims the slot')
    a('\t// and reloads identically whichever the player picks. FIRST MATCH WINS, so a')
    a('\t// donor appears once: the lowest slot that measured it.')
    a('\tclearscope static int SlotForDonor(string donor)')
    a('\t{')
    a('\t\tif (donor.Length() == 0) return 0;')
    seen = set()
    for slot in sorted(slot_donors):
        for d in slot_donors[slot]:
            if d in seen:
                continue
            seen.add(d)
            a('\t\tif (donor == "%s")\treturn %d;' % (d, slot))
    a('\t\treturn 0;')
    a('\t}')
    return L


def main(out=OUT):
    c2q.modeldef_scales = scales
    gp.MESH_ROOTS = MESH_ROOTS
    import gen_modelswapper as gms
    gms.c2q.modeldef_scales = scales

    classes = carded_classes()
    print('%d mesh scales from %d MODELDEF sources; %d carded classes offered\n'
          % (len(scales()), sum(1 for p in SCALE_SOURCES if os.path.exists(p)), len(classes)))

    # One gun at a time: at least one mesh on the shelf makes genpack.md3_surfaces read
    # past the end of its own buffer, and a single bad mesh must not take the run down.
    kept, held = [], []
    for cls in classes:
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                got = gms.main(ROOT, out + '.probe', [cls])
        except Exception as e:
            held.append((cls, '%s: %s' % (type(e).__name__, str(e)[:90]))); continue
        line = [l.strip() for l in buf.getvalue().splitlines() if l.strip().startswith(cls)]
        why = line[0][len(cls):].strip() if line else 'not generated'
        (kept if got else held).append((cls, why))
    if os.path.exists(out + '.probe'):
        os.remove(out + '.probe')

    # ONE SLOT PER MESH. Two cards can measure the same gun -- a recolour and its base,
    # or our shelf card beside REMA's. Their reload geometry is the same mesh's geometry,
    # and SlotForDonor takes the first match, so the second slot is a row nothing can
    # ever reach. Keep the first and say which card it was, rather than leaving dead
    # rows for a later session to puzzle over.
    cards0 = {w['cls']: w for w in c2q.load_cards(ROOT)}
    order, dropped, sigs = [], [], []
    for cls, _why in kept:
        m = cards0[cls]['keys']['model']
        try:
            s = signature(gp.find_mesh(ROOT, m[0], m[1]))
        except Exception:
            s = None
        same = None
        if s is not None:
            for prev, ps in sigs:
                if ps is not None and ps[0] == s[0] and float(np.abs(ps[1] - s[1]).max()) <= 0.5:
                    same = prev
                    break
        if same:
            dropped.append((cls, 'same mesh as %s, which already has the slot' % same))
        else:
            order.append(cls)
            sigs.append((cls, s))
    held += dropped

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        made = gms.main(ROOT, out, order)
    assert made == order, 'the run over all kept guns did not match the per-gun pass'

    # the donors, by mesh identity
    shelf, cache = shelf_models(), {}
    cards = {w['cls']: w for w in c2q.load_cards(ROOT)}
    slot_donors, extra = {}, 0
    for i, cls in enumerate(order, 1):
        m = cards[cls]['keys']['model']
        mesh = gp.find_mesh(ROOT, m[0], m[1])
        d = donors_for(mesh, shelf, cache)
        if cls in shelf and cls not in d:
            d.append(cls)
        slot_donors[i] = sorted(d)
        extra += len(d)

    # Splice the lookup in before RSR_Guns' OWN closing brace -- the first line that is a
    # bare `}` after `class RSR_Guns`. Not the last one in the file: gen_rsr writes
    # RSR_GunSprites and a RSR_Held_ class per gun after it, so the last `}` put the
    # lookup inside an Actor, where it compiled as nothing and the engine refused the
    # pack with "Unknown function DonorInHand".
    zl = open(out, encoding='utf-8').read().split('\n')
    start = next(i for i, l in enumerate(zl) if l.startswith('class RSR_Guns'))
    # gen_rsr writes its own Index(Weapon) that matches on the weapon's CLASS, which is
    # right for a standalone pack. Ours answers from the model in hand, so it REPLACES
    # that one -- two of them is "Attempt to redefine 'Index'" and the pack does not load.
    gi = next((i for i, l in enumerate(zl)
               if i > start and l.strip().startswith('clearscope static int Index(')), None)
    if gi is not None:
        gend = next(i for i, l in enumerate(zl) if i > gi and l.rstrip() == '\t}')
        head = gi
        while head > start and zl[head - 1].lstrip().startswith('//'):
            head -= 1
        zl = zl[:head] + zl[gend + 1:]
    close = next(i for i, l in enumerate(zl) if i > start and l.rstrip() == '}')
    zl = zl[:close] + lookup_zs(slot_donors) + zl[close:]
    open(out, 'w', encoding='utf-8').write('\n'.join(zl))

    json.dump({str(k): v for k, v in slot_donors.items() if v},
              open(SLOTS_JSON, 'w'), indent=1)

    print('%d guns reload by hand, in %d slots:' % (len(order), len(order)))
    for i, cls in enumerate(order, 1):
        d = slot_donors[i]
        print('  %-3d %-28s %s' % (i, cls, ('%d model%s: %s' % (len(d), '' if len(d) == 1 else 's',
                                                                ', '.join(d))) if d else '(no shelf model)'))
    print('\n%d carded classes HELD, with the reason:' % len(held))
    for cls, why in held:
        print('  %-28s %s' % (cls, why))
    claimed = sorted({d for v in slot_donors.values() for d in v})
    print('\n%d models on the shelf reload by hand -> %s' % (len(claimed), out))
    print('slot map -> %s' % SLOTS_JSON)
    return order, held


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else OUT)
