#!/usr/bin/env python3
"""card_break.py -- break-open / revolver reload rows for the MS 1.5 card donors, measured from the cards at the
place each donor is DRAWN.

    python3 tools_kit/card_break.py [--dry]

2.0 ran tools_kit/gen_rsb.py through run_break.py with three hand-written GUNS entries. This writes the same GUNS
entries from the MS 1.5 cards (RSQ_WeaponDepot md3label) and runs gen_rsb unchanged:

  card part hinge* / barrel* / cyl* / cylinder* / ejector that turns (rot)  -> hinged
  card part shell* / round* / case* seen at the rest frame                   -> chambers (surface, rest frame)
  card part loader (a speedloader) + case* hidden at rest                    -> loader (surface, the frame it sits
                                                                                closest to the cylinder), rounds6
  card parts hidden at rest (shells shown only while loading)               -> hidden in the gun's layer
  surfaces that are no card part                                            -> body (gen_rsb's frame correction)
  open frame: the frame the hinged part is turned furthest from rest (body-fixed fit, measured here)
  placement (Path/Model/Skin, Scale, Offset + ZOffset, rest frame): the donor's own generated block in `modeldef`
  ready sprite: the donor's shelf anchor; sounds: the 2.0 foley set of its kind (SNDINFO.ms)

Ammo: ModelSwapper rows name no items -- the gun and its ammo are the loaded mod's (rsr_break.zs WeaponStore).
A gun the card gives no round for (zblood sawed-off, UV SSG D4) or no measured hinge (Robocop M32, Cola revolver's
rounds are one surface) is left on the mod's own reload and said so.
Writes zscript_depot/rsr/rsb_guns.zs and MODELDEF.rsb whole, card_break.report.md.
"""
import os, re, sys, glob, shutil, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import card_pump as CP  # noqa: E402
import gen_rsb  # noqa: E402
from rgeo import load_md3  # noqa: E402
from md3rel import rigid  # noqa: E402

HINGED = re.compile(r'^(hinge|barrel|cyl|cylinder|ejector)\d*$')
ROUND = re.compile(r'^(shell|round|case)\d*$')
SND = {'shell': 'ssg', 'big': 'm79', 'cell': 'revolver', 'rev': 'revolver'}
LETTERS = 'MNOPQRSTUVWXYZ'


def parse(text):
    parts = []
    for m in re.finditer(r'^\s{4}(\w+)\s+surf\s+(\d+)\s+rest.*?frames\s+(\S+?)(?:\s|$)(.*)$', text, re.M):
        name, surf, fr, tail = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        a, b = (fr.split('..') + ['-'])[:2]
        parts.append(dict(name=name, surf=surf, a=None if a == '-' else int(a), b=None if b == '-' else int(b),
                          rot='rot ' in tail, hidden='HIDDEN at idle' in tail,
                          appears=[int(x) for x in re.findall(r'appears (\d+)\.\.(\d+)', tail)[0]] if 'appears' in tail else None))
    arch = (re.search(r'archetype\s+(\S+)', text) or [None, ''])[1]
    return parts, arch


def turned(m, body, hinged, f0, f, sc, off):
    fl = lambda sis, fr: np.concatenate([gen_rsb.to_flu(m[i]['xyz'][fr], sc, off) for i in sis])
    R, t = rigid(fl(body, f), fl(body, f0))
    Rh, _ = rigid(fl(hinged, f0), fl(hinged, f) @ R.T + t)
    return np.degrees(np.arccos(np.clip((np.trace(Rh) - 1) / 2, -1, 1)))


def entry(donor, card, blk, shelf, k):
    text = open(card).read()
    parts, arch = parse(text)
    mesh = os.path.join(ROOT, blk['path'], blk['model'])
    m = load_md3(mesh)
    n, nf = len(m), m[0]['xyz'].shape[0]
    ready = blk['frame']
    sc, off = blk['scale'], blk['off']
    hinged = sorted({p['surf'] for p in parts if HINGED.match(p['name']) and p['rot'] and p['a'] is not None})
    if not hinged:
        return None, 'no hinged part that turns on its card'
    loader = next((p for p in parts if p['name'] == 'loader'), None)
    rounds = [p for p in parts if ROUND.match(p['name'])]
    seen = [p for p in rounds if not p['hidden']]
    hidden = sorted({p['surf'] for p in parts if p['hidden']})
    if not seen and not loader:
        return None, 'no round on its card (no shell / round / case seen at rest, no speedloader)'
    if len(seen) == 1 and not loader and arch.startswith('revolver'):
        return None, 'its rounds are one surface on the card (%s): one chamber cannot stand for a cylinder' % seen[0]['name']
    body = [i for i in range(n) if i not in {p['surf'] for p in parts}]
    if not body:
        return None, 'every surface is a moving part: no body to hold the frames still'
    lo = min(p['a'] for p in parts if p['surf'] in hinged)
    hi = max(p['b'] for p in parts if p['surf'] in hinged)
    angs = [(turned(m, body, hinged, ready, f, sc, off), f) for f in range(lo, min(hi, nf - 1) + 1)]
    open_deg, open_frame = max(angs)
    if open_deg < 10:
        return None, 'its hinged part turns only %.0f deg in its frames' % open_deg
    if arch.startswith('launcher'):
        hold = 'big'
    elif loader:
        hold = 'cell'
    else:
        hold = 'shell'
    g = dict(key='MS15/%s' % donor, cls=donor, set='ms', mesh=mesh, path=blk['path'], model=blk['model'],
             skin=blk['skin'] or 'rsr_clear.png', scale=tuple(sc), off=tuple(off),
             extra='\tNoInterpolation' if blk['nointerp'] else '', ready=ready, body=body, hinged=hinged,
             open_frame=open_frame, hold=hold, spr=LETTERS[k],
             ready_sprite='%s A' % shelf[donor],
             eject='bd', reserve='', loaded='', casing=None, unloaded='', reload_token='Reloading')
    fam = 'm79' if hold == 'big' else ('revolver' if arch.startswith('revolver') else 'ssg')
    g['snd'] = dict(open=['ms/bd22/%s/open' % fam], load='ms/bd22/%s/load' % fam, close=['ms/bd22/%s/close' % fam], chan=5)
    if blk['skins']:
        g['skins'] = [blk['skins'].get(i, blk['skin'] or 'rsr_clear.png') for i in range(n)]
    if loader:
        cyl = [p['surf'] for p in parts if p['name'].startswith('cyl')] or hinged
        a, b = loader['appears'] or (loader['a'], loader['b'])
        # the frame it is home: closest to the (open) cylinder in that same frame
        d = [(np.linalg.norm(m[loader['surf']]['xyz'][f].mean(0) - np.concatenate([m[i]['xyz'][f] for i in cyl]).mean(0)), f)
             for f in range(a, b + 1)]
        g.update(chambers=[], loader=(loader['surf'], min(d)[1]), rounds6=sorted(p['surf'] for p in rounds), per_load=6, cap=6)
        why = 'speedloader surface %d home at frame %d' % (loader['surf'], g['loader'][1])
    else:
        g.update(chambers=[(p['surf'], ready) for p in seen], per_load=1, cap=len(seen))
        why = '%d chamber(s) %s' % (len(seen), [p['surf'] for p in seen])
    g['hide'] = [s for s in hidden if not (loader and s in g.get('rounds6', []) + [loader['surf']])]
    return g, 'body %s hinged %s open %.0f deg at frame %d, %s, hold %s' % (body, hinged, open_deg, open_frame, why, hold)


def main(dry):
    blocks = CP.donor_blocks()
    shelf_t = open(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs')).read()
    shelf = dict(re.findall(r'"\w+\|(MS_\w+)\|(\w{4})\|', shelf_t))
    guns, rep, k = [], [], 0
    for card in sorted(glob.glob(os.path.join(ROOT, 'cards/*/*/*.card'))):
        if '.blend' in card:
            continue
        text = open(card).read()
        arch = (re.search(r'archetype\s+(\S+)', text) or [None, ''])[1]
        if not (arch.startswith('revolver') or arch.endswith('_break')):
            continue
        rel = os.path.relpath(os.path.dirname(card), ROOT)
        donor = next((d for d, b in blocks.items() if b['path'] == rel and b['model'] == os.path.basename(card)[:-5] + '.md3'), None)
        if not donor:
            rep.append('%-22s %s: no donor block' % (os.path.basename(card), arch)); continue
        g, why = entry(donor, card, blocks[donor], shelf, k)
        if g is None:
            rep.append('%-22s left on the mod\'s own reload: %s' % (donor, why)); continue
        k += 1
        guns.append(g)
        rep.append('%-22s slot %d: %s' % (donor, k, why))
    print('\n'.join(rep))
    gen_rsb.RSQ = os.path.join(HERE, 'ermac') + os.sep       # Ermac's off-hand meshes (measured against, not shipped)
    gen_rsb.MODELSWAPPER = True
    gen_rsb.GUNS = guns
    out = tempfile.mkdtemp()
    gen_rsb.main(out)
    if dry:
        return
    shutil.copy(os.path.join(out, 'zscript/rsr/rsb_guns.zs'), os.path.join(ROOT, 'zscript_depot/rsr/rsb_guns.zs'))
    md = ['// GENERATED by tools_kit/card_break.py (gen_rsb from the MS 1.5 cards) -- do not edit by hand.']
    for f in sorted(glob.glob(os.path.join(out, 'MODELDEF.rsb.*'))):
        md.append(open(f).read())
    open(os.path.join(ROOT, 'MODELDEF.rsb'), 'w', newline='\n').write('\n'.join(md))
    for g in guns:
        if g.get('loader'):
            shutil.copy(os.path.join(out, gen_rsb.LOADER_MD3), os.path.join(ROOT, g['path'], gen_rsb.LOADER_MD3))
        dst = os.path.join(ROOT, g['path'], 'rsr_clear.png')
        if not os.path.exists(dst):
            shutil.copy(os.path.join(ROOT, 'reload_1x', 'rsr_clear.png'), dst)
    open(os.path.join(ROOT, 'card_break.report.md'), 'w').write(
        '# Break-open / revolver reloads from the MS 1.5 cards (tools_kit/card_break.py)\n\n' + '\n'.join('- ' + r for r in rep) + '\n')


if __name__ == '__main__':
    main('--dry' in sys.argv)
