"""Generate ModelSwapper's reload table for an explicit list of guns.

genpack.py builds STANDALONE Quest packs, so it starts from a set -- vanilla,
plus, modern -- and a set decides which guns a pack contains. ModelSwapper has no
sets. It has a shelf of models and puts any of them on any weapon, so the only
question is which guns have been measured, and we already know.

Everything else here is genpack's: its card loader, its scale and offset
maths, its build_gun, and the kit's own gen_rsr.compute / gen_rsr.zs. The single
thing skipped is set_members, because that is the part that does not apply.

usage: gen_ms.py <root> <out.zs> <class> [class ...]
"""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.getcwd(), 'tools_kit'))
import genpack as gp
import card2quest as c2q
import gen_rsr


def main(root, out, classes):
    cards = {w['cls']: w for w in c2q.load_cards(root)}
    scales = c2q.modeldef_scales(root)
    guns, surveys, report = [], {}, []
    b36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    for i, cls in enumerate(classes):
        w = cards.get(cls)
        if not w:
            report.append((cls, 'no card')); continue
        model = w['keys']['model'] if isinstance(w['keys']['model'], list) else [None, w['keys']['model']]
        mp = os.path.join(root, model[0], model[1])
        if not os.path.exists(mp):
            report.append((cls, 'mesh not found: %s' % mp)); continue
        # modeldef_scales keys on the MESH FILENAME, not the class
        ws_ = scales.get(os.path.basename(model[1]).lower())
        if not ws_:
            report.append((cls, 'no MODELDEF scale')); continue
        hud = tuple(round(s / c2q.WORLD_PER_HUD, 4) for s in ws_)
        scale = ((-1.0 if ws_[0] < 0 else 1.0) * abs(hud[0]), abs(hud[1]), abs(hud[2]))
        off = c2q.offset_for(w['grip']['palm'], scale)
        fr = c2q.rest_frame(w, mp)
        geo = c2q.geometry(w, scale, off)
        rec = dict(hud_scale=scale, offset=off, rest_frame=fr, parts=geo['parts'],
                   type=w['keys'].get('type'))
        code = b36[i // 36] + b36[i % 36]
        spr = dict(gun='Q%sR' % code, m='Q%sM' % code, p='Q%sP' % code,
                   w='Q%sW' % code, pick='Q%sS' % code)
        nfr, surfs = gp.md3_surfaces(mp)
        names = [s['name'] for s in surfs]
        g, sv = gp.build_gun(root, w, cls, rec, names, surfs, nfr, spr)
        if not g:
            report.append((cls, sv)); continue
        g['mesh'] = mp
        guns.append(g)
        surveys[cls] = sv
        report.append((cls, 'VR reload: %s' % ('magazine + handle' if g.get('handle_surfs') else 'magazine')))

    comp = [gen_rsr.compute(dict(g), {g['key']: surveys[g['cls']]}) for g in guns]
    zl = gen_rsr.zs(comp)
    sl = ['', "\t// the action locks open on an empty gun (card holdopen, or the default rule)",
          '\tclearscope static bool SlideLock(int i)', '\t{',
          '\t\tstatic const bool v[] = { false, %s };' % ', '.join(
              'true' if g.get('slide_lock') else 'false' for g in comp),
          '\t\treturn i > 0 && i < v.Size() && v[i];', '\t}']
    close = zl.index('}')
    zl = zl[:close] + sl + zl[close:]
    open(out, 'w', encoding='utf-8').write('\n'.join(zl) + '\n')

    for cls, what in report:
        print('  %-24s %s' % (cls, what))
    print('\n%d of %d guns generated -> %s' % (len(comp), len(classes), out))
    return [g['cls'] for g in comp]


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
