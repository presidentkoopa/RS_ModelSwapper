#!/usr/bin/env python3
"""render_set_hands.py <set> [...]  -- one contact sheet per set: every weapon's donor with the hands it will wear.

    RSQ_ERMAC=<folder with hand/hand.md3 + hand2.md3> python3 tools/ms/render_set_hands.py generic_weapons weapons_of_saturn

Reads the set's profile rows (zscript/RS_ForeignModels.zs ProfileDonor, via build_pk3.SETS), each donor's block in
`modeldef` (placement, rest frame) and its hand row in zscript_depot/rsq/handtable.zs (RSQ_HandTable: GunOne letter ->
Ermac frame, GunHook -> where; Support likewise), and draws gun + gun hand + support hand side and bottom through the
kit's own placement chain (gunview / hudrender), the way the hand sheets are drawn. Writes work/handfit/sets/<set>/<Class>.png
and work/handfit/sets/<set>.png (the grid). A donor with no hand row is drawn bare and labelled so.
"""
import os, sys, re
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'ms')); sys.path.insert(0, os.path.join(ROOT, 'tools', 'kit')); sys.path.insert(0, os.path.join(ROOT, 'tools', 'handfit', 'core', 'hands_tool'))
import gunview  # noqa: E402
import handfit_donors as D  # noqa: E402
import handfit_cards as HC  # noqa: E402
import build_pk3 as B  # noqa: E402

LETTER_FRAME = {v: k for k, v in HC.GUN_LETTER.items()}
SUP_FRAME = {v: k for k, v in HC.SUP_LETTER.items()}


def table():
    s = open(os.path.join(ROOT, 'zscript_depot', 'rsq', 'handtable.zs'), encoding='utf-8').read()
    slot = {}
    for k, v in re.findall(r'if \(donor == "(MS_\w+)"\)\s*return (\d+);', s):
        slot.setdefault(k, v)   # the FIRST match wins, as SlotForDonor returns it: a fit written at the top beats an alias
    def strs(fn):
        return [x.strip().strip('"') for x in re.search(r'static String %s\(int i\)\s*\{\s*static const String v\[\] = \{([^}]*)\}' % fn, s, re.S).group(1).split(',')]
    def vecs(fn):
        body = re.search(r'static Vector3 %s\(int i\)\s*\{(.*?)\n\t\}' % fn, s, re.S).group(1)
        xyz = [[float(v) for v in re.search(r'static const double %s\[\] = \{([^}]*)\}' % ax, body).group(1).split(',')] for ax in 'xyz']
        return list(zip(*xyz))
    return dict(slot={k: int(v) for k, v in slot.items()}, one=strs('GunOne'), two=strs('GunTwo'), sup=strs('Support'), hook=vecs('GunHook'), shook=vecs('SupportHook'))


def hook_to_t(h):
    """hands.zs hook (L, U, -F) -> the kit's translation (F, L, U)"""
    return np.array([-h[2], h[0], h[1]])


def profile_rows(setname):
    zs = open(os.path.join(ROOT, 'zscript', 'RS_ForeignModels.zs'), encoding='utf-8').read()
    a = zs.index('static string ProfileDonor'); b = zs.index('};', a)
    rows = re.findall(r'"([^"|]+)\|(MS_\w+)"', zs[a:b])
    want = B.SETS[setname]['classes']; d = dict(rows)
    return [(c, d[c]) for c in want if c in d]   # in the set's own order


def main():
    from PIL import Image, ImageDraw
    ermac = os.environ.get('RSQ_ERMAC') or sys.exit('set RSQ_ERMAC (hand/hand.md3 + hand2.md3)')
    HC.ERMAC = os.path.join(ermac, 'hand')
    T = table()
    for setname in sys.argv[1:]:
        out = os.path.join(ROOT, 'work', 'handfit', 'sets', setname); os.makedirs(out, exist_ok=True)
        tiles = []
        for cls, donor in profile_rows(setname):
            b = D.block(donor); it = D.item(b); gi = dict(it); gi.pop('ao', None)
            hands = []; label = '%s -> %s' % (cls, donor)
            i = T['slot'].get(donor, 0)
            if i > 0:
                g = T['two'][i] or T['one'][i]
                if g: hands.append(HC.hand_item('hand', LETTER_FRAME[g], hook_to_t(T['hook'][i])))
                sp = T['sup'][i]
                if sp: hands.append(HC.hand_item('hand2', SUP_FRAME[sp], hook_to_t(T['shook'][i]), color=(120, 200, 140)))
                label += '  [row %d: gun %s%s]' % (i, g or '-', (' + support ' + sp) if sp else '')
            elif donor.endswith('_Fist'):
                label += '  [the fist is the hand]'
            else:
                label += '  [NO HAND]'
            a = os.path.join(out, cls + '.side.png'); bb = os.path.join(out, cls + '.bottom.png')
            gunview.view([gi] + hands, a, 'side', px=4, title=label)
            gunview.view([gi] + hands, bb, 'bottom', px=4, title=label)
            A, Bm = Image.open(a), Image.open(bb)
            O = Image.new('RGB', (max(A.width, Bm.width), A.height + Bm.height), (40, 44, 60)); O.paste(A, (0, 0)); O.paste(Bm, (0, A.height))
            O.save(os.path.join(out, cls + '.png')); os.remove(a); os.remove(bb); tiles.append((cls, O))
            print(label)
        # the grid: two columns
        W = max(t.width for _, t in tiles); H = max(t.height for _, t in tiles); cols = 2; rows = (len(tiles) + cols - 1) // cols
        G = Image.new('RGB', (cols * W, rows * H), (30, 32, 44))
        for k, (cls, t) in enumerate(tiles): G.paste(t, ((k % cols) * W, (k // cols) * H))
        G.save(os.path.join(ROOT, 'work', 'handfit', 'sets', setname + '.png')); print('->', os.path.join('work', 'handfit', 'sets', setname + '.png'), G.size)


if __name__ == '__main__':
    main()
