#!/usr/bin/env python3
"""card_pump.py -- pump-shotgun reload rows for the MS 1.5 card donors, measured at the place each donor is DRAWN.

    python3 tools_kit/card_pump.py [--dry] [--only MS_BD_Shotgun,...]

2.0's pump rows came from tools_kit/gen_pump.py fed by the owner's kit survey (survey.json) and its own gun list.
MS 1.5 has the same facts per mesh in its cards (RSQ_WeaponDepot md3label): the pump part (surface, rest, axis,
travel, frames), the shell part, the bolt, the loading point and frame. This builds gen_pump's gun record from:

  the card          pump / bolt / shell surfaces, pump axis + travel, the loading frame (`load ... frame N`)
  the donor's block Scale, Offset, ZOffset, rest frame, skin -- the generated `modeldef`, i.e. the set's own
                    calibrated numbers (no placement of our own)
  the mesh          the pump's centre and the shell's place at the loading frame, carried to the ready pose with
                    the rigid fit gen_pump uses for its ejected shells (the gun moves while it loads)

and runs gen_pump.compute / modeldef / zs UNCHANGED (MODELSWAPPER on: the slot comes from the donor in hand).
The pump point (RSP_Rack.Frac) is measured from the donor's own states (Depot statephase.py on the source
MODELDEF + actor): in its fire-then-pump sequence, the first tic that shows a frame where the pump moves.

Writes zscript_depot/rsr/rsr_pump_guns.zs (whole), MODELDEF.rsrpump (whole: the card guns' layers + Ermac's
one-shell hold), zscript_depot/rsr/rsp_rack.ms.zs (whole), card_pump.report.md.
A gun is left out (and said why) when its card has no pump or no shell part, or the numbers fail gen_pump's checks.
"""
import argparse, glob, json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import gen_pump as GP  # noqa: E402
from rgeo import load_md3, to_flu  # noqa: E402

DEPOT = os.environ.get('RSQ_DEPOT', '/home/claude/rsq_weapondepot')
sys.path.insert(0, DEPOT + '/tools/hqt')
WELL = os.environ.get('MS_WELL', '/mnt/user-data/uploads/VR_WeaponSetRebuild')

V3 = r'\[\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\s*\]'


def card_parts(text):
    parts = {}
    for m in re.finditer(r'^\s{4}(\w+)\s+surf\s+(\d+)\s+rest\s+' + V3 + r'\s+axis\s+' + V3 + r'\s+travel\s+([\d.]+)\s+frames\s+(\S+)', text, re.M):
        a, b = (m.group(10).split('..') + ['-'])[:2]
        parts.setdefault(m.group(1), []).append(dict(
            surf=int(m.group(2)), rest=np.array([float(x) for x in m.group(3, 4, 5)]),
            axis=np.array([float(x) for x in m.group(6, 7, 8)]), travel=float(m.group(9)),
            frames=(int(a), int(b)) if a.isdigit() and b.isdigit() else None))
    load = re.search(r'^\s+load\s+' + V3 + r'\s+frame\s+(\d+)', text, re.M)
    return parts, (np.array([float(x) for x in load.group(1, 2, 3)]), int(load.group(4))) if load else None


def donor_blocks():
    t = open(os.path.join(ROOT, 'modeldef')).read()
    out = {}
    for m in re.finditer(r'Model (MS_\w+)\s*\{(.*?)\n\}', t, re.S):
        b = m.group(2)
        g = lambda k: re.search(r'^\s*%s\s+([^\n/]+)' % k, b, re.M | re.I)
        sc = [float(x) for x in g('Scale').group(1).split()] if g('Scale') else [1.0, 1.0, 1.0]
        of = [float(x) for x in g('Offset').group(1).split()] if g('Offset') else [0.0, 0.0, 0.0]
        zo = float(g('ZOffset').group(1)) if g('ZOffset') else 0.0
        out[m.group(1)] = dict(path=re.search(r'Path "([^"]+)"', b).group(1), model=re.search(r'Model 0 "([^"]+)"', b).group(1),
                               skin=(re.search(r'Skin 0 "([^"]+)"', b) or [None, None])[1], scale=tuple(sc),
                               off=(of[0], of[1], of[2] + zo), frame=int(re.search(r'FrameIndex \w{4} A 0 (\d+)', b).group(1)),
                               nointerp='NoInterpolation' in b,
                               skins={int(i): k for i, k in re.findall(r'SurfaceSkin\s+0\s+(\d+)\s+"([^"]+)"', b)})
    return out


def rigid(A, B):
    return GP.rigid(A, B)


def pump_frac(donor, lock, pump_frames):
    """first tic of the donor's own fire-then-pump showing a pump frame, over that sequence's length"""
    import statephase as SP
    L = lock.get(donor) or {}
    src = L.get('srcfile'); blk = L.get('block_name')
    if not src or not blk or not pump_frames:
        return -1.0, 'no source block / no pump frames'
    setdir = os.path.join(WELL, src.split('/')[0])
    mds = [p for p in glob.glob(setdir + '/**/*', recursive=True) if os.path.isfile(p) and os.path.getsize(p) < 400000
           and re.search(r'Model\s+%s\b' % re.escape(blk), open(p, errors='ignore').read())]
    acts = [p for p in glob.glob(setdir + '/**/*', recursive=True) if os.path.isfile(p) and os.path.getsize(p) < 3000000
            and not p.lower().endswith(('.md3', '.png', '.jpg', '.def')) and re.search(r'(?im)^\s*actor\s+%s\b' % re.escape(blk), open(p, errors='ignore').read())]
    if not mds or not acts:
        return -1.0, 'source MODELDEF or actor not found'
    ph = SP.phases(mds[0], acts[0], blk)
    a, b = pump_frames
    fire = next((ph[k] for k in ph if k.lower() == 'fire'), None)
    if not fire:
        return -1.0, 'no Fire state'
    # the donor's own pump: Fire, then the first state after it that shows a pump frame (BD: Pump1)
    seq = list(fire)
    if not any(a <= f <= b for f in seq):
        names = list(ph)
        i = next(k for k, n in enumerate(names) if n.lower() == 'fire')
        nxt = next((ph[n] for n in names[i + 1:] if any(a <= f <= b for f in ph[n])), None)
        if not nxt:
            return -1.0, 'the pump frames %d..%d are in no state after Fire' % (a, b)
        seq += nxt
    t0 = next(k for k, f in enumerate(seq) if a <= f <= b)
    return round(t0 / len(seq), 4), 'tic %d of %d (Fire%s, %s %s)' % (t0, len(seq), '' if t0 < len(fire) else ' + its pump state',
                                                                     os.path.relpath(mds[0], WELL), os.path.relpath(acts[0], WELL))


def rack_20(donor):
    rep = os.path.join(ROOT, 'reload_names.report.md')
    if not os.path.exists(rep):
        return None, None
    import subprocess
    r20 = subprocess.run(['git', 'show', 'origin/ms20:zscript_depot/rsr/rsp_rack.ms.zs'], cwd=ROOT, capture_output=True, text=True).stdout
    for l in open(rep):
        c = [x.strip() for x in l.split('|')]
        if len(c) > 6 and c[6] == donor and (c[5].startswith('exact') or c[5].startswith('moved ')):
            m = re.search(r'donor == "%s"\)\s*return ([\d.]+);' % re.escape(c[3]), r20)
            if m:
                return float(m.group(1)), "2.0's rack_frac on the same mesh (%s, %s)" % (c[3], c[5].split()[0])
    return None, None


def find_port(m, rf, skip, grip_x):
    """the loading port of a gun whose mesh has no shell: the longest stretch of OPEN underside behind the
    grip (body vertices there sit high: the tube channel is open), measured at the rest frame"""
    v = np.concatenate([m[i]['xyz'][rf] for i in range(len(m)) if i not in skip])
    x0 = float(v[:, 0].min())
    bins = []
    for x in np.arange(x0, grip_x, 1.0):
        sl = v[(v[:, 0] >= x) & (v[:, 0] < x + 1.0)]
        bins.append((x + 0.5, float(sl[:, 2].min()) if len(sl) else None))
    zs = [z for _, z in bins if z is not None]
    if not zs:
        return None
    floor = float(min(zs))          # the solid underside (the stock's bottom); open where it sits 3+ units higher
    run, best = [], []
    for x, z in bins:
        if z is None or z > floor + 3.0:
            run.append((x, z))
            if len(run) > len(best):
                best = list(run)
        else:
            run = []
    best = [(x, z) for x, z in best if z is not None]
    if len(best) < 3:
        return None
    return np.array([(best[0][0] + best[-1][0]) / 2, 0.0, min(z for _, z in best)]), (best[0][0], best[-1][0], floor)


def build_noshell(donor, card, blk, lock, parts, pump):
    """a pump gun whose mesh has no shell: the pump stroke and hand loading without a drawn shell of the gun's
    own (the hand shows Ermac's shell: RSP_Guns.OwnShell false). Port: find_port; push: along the bore."""
    text = open(card).read()
    mesh = os.path.join(ROOT, blk['path'], blk['model'])
    m = load_md3(mesh)
    sc, of, rf = blk['scale'], blk['off'], blk['frame']
    rides = [p for k in ('barrel', 'bolt', 'slide') for p in parts.get(k, []) if p['frames'] == pump['frames'] and abs(p['travel'] - pump['travel']) < 0.5]
    gl = re.search(r'^\s+grip\s+line\s+' + V3, text, re.M)
    grip_x = float(gl.group(1)) if gl else float(pump['rest'][0])
    fp = find_port(m, rf, [pump['surf']] + [p['surf'] for p in rides] + [p['surf'] for k in ('trigger', 'grip') for p in parts.get(k, [])], grip_x)
    if fp is None:
        return None, 'no shell mesh, and no open underside behind the grip to load through'
    port_m, (xa, xb, floor) = fp
    if not re.search(r'archetype\s+shotgun_pump', text):
        return None, 'no shell mesh, and not a pump shotgun (its pump part is something else)'
    if xb - xa > 16.0:
        return None, 'no shell mesh; the open underside behind the grip runs %.0f units (x %.1f..%.1f): too long for a loading port, not trusted' % (xb - xa, xa, xb)
    port = to_flu(port_m[None, :], sc, of)[0]
    bore = to_flu(np.array([[1.0, 0, 0]]), sc, (0, 0, 0))[0] - to_flu(np.zeros((1, 3)), sc, (0, 0, 0))[0]
    bore = bore / np.linalg.norm(bore)
    pump_c = to_flu(m[pump['surf']]['xyz'][rf], sc, of).mean(0)
    pull = -bore
    travel = pump['travel'] * 1.02 * abs(sc[1])
    from rgeo import shift_hook, pca
    g = dict(key=donor, cls=donor, set='ms', mesh=mesh, path=blk['path'], model=blk['model'], skin=blk['skin'] or 'rsr_clear.png',
             scale=sc, off=of, extra='\tNoInterpolation\n' if blk['nointerp'] else '', ready_frame=rf, nsurf=len(m),
             pump_surfs=[pump['surf']], bolt_surfs=[p['surf'] for p in rides], shell_surf=-1, shell_frame=rf,
             lead=tuple(bore), depth=6.0, own_shell=False,
             ready_sprite='', spr_gun='', spr_part='', spr_world='', waits='',
             snd=dict(shell=('', 0), back=('', 0), fwd=('', 0), land=''), reserve='', magammo='', eject_frames=[], eject_hooks=[])
    g['grab'] = pump_c; g['pull'] = pull; g['travel'] = float(travel)
    g['pump_hook'] = shift_hook(sc, pull); g['support_hook'] = shift_hook(GP.HAND_SCALE, pull)
    g['bolt_ratio'] = 1.0 if rides else 0.0
    g['port'] = port; g['push'] = bore; g['shell_ref'] = port; g['lead_v'] = bore
    g['port_hook'] = np.zeros(3); g['push_hook'] = shift_hook(sc, bore); g['shell_len'] = 6.0
    # the shell in the hand is Ermac's own (MODELDEF hold RQUN B): its middle and crimp axis in the off-hand frame
    es = load_md3(os.path.join(ROOT, 'models', 'rsq', 'shot_shell.md3'))
    ep = to_flu(es[0]['xyz'][0], GP.HAND_SCALE, GP.HAND_OFF)
    ec, evt, _ = pca(ep); ea = evt[0]
    t = (ep - ep.mean(0)) @ ea; hi = t > (t.max() + t.min()) / 2
    if np.linalg.norm((ep[hi] - ep.mean(0)) - np.outer(t[hi], ea), axis=1).max() > np.linalg.norm((ep[~hi] - ep.mean(0)) - np.outer(t[~hi], ea), axis=1).max():
        ea = -ea
    g['shell_in_hand'] = ep.mean(0); g['axis_in_hand'] = ea; g['ermac_mid'] = GP.mid(ep, ea)
    g['hand_hook'] = np.zeros(3); g['hand_rot'] = np.zeros(3)
    g['world_scale'] = (0.0, 0.0, 0.0); g['world_off'] = (0.0, 0.0, 0.0)
    frac, how = pump_frac(donor, lock, pump['frames'])
    if frac < 0:
        f2, how2 = rack_20(donor)
        if f2 is not None:
            frac, how = f2, how2
    return dict(g=g, sv=None, frac=frac, frac_how=how + '; no shell mesh: port = open underside x %.1f..%.1f' % (xa, xb), port=port, pump=pump_c, travel=travel, noshell=True), None

def build(donor, card, blk, lock):
    text = open(card).read()
    parts, load = card_parts(text)
    pump = (parts.get('pump') or [None])[0]; shell = (parts.get('shell') or [None])[0]
    if not pump:
        return None, 'no pump part on the card'
    if not shell or not load:
        return build_noshell(donor, card, blk, lock, parts, pump)
    mesh = os.path.join(ROOT, blk['path'], blk['model'])
    m = load_md3(mesh)
    sc, of, rf = blk['scale'], blk['off'], blk['frame']
    lf = load[1]
    # the shell at the loading frame, carried into the ready pose: the body's rigid move lf -> rf
    body = [i for i in range(len(m)) if i not in (pump['surf'], shell['surf'])]
    B_l = np.concatenate([to_flu(m[i]['xyz'][lf], sc, of) for i in body])
    B_r = np.concatenate([to_flu(m[i]['xyz'][rf], sc, of) for i in body])
    R, t = rigid(B_l, B_r)
    sh_l = to_flu(m[shell['surf']]['xyz'][lf], sc, of)
    port = (sh_l @ R.T + t).mean(0)
    pump_c = to_flu(m[pump['surf']]['xyz'][rf], sc, of).mean(0)
    pull = to_flu(pump['axis'][None, :] + 0, sc, (0, 0, 0))[0] - to_flu(np.zeros((1, 3)), sc, (0, 0, 0))[0]
    pull = pull / np.linalg.norm(pull)
    bore = to_flu(np.array([[1.0, 0, 0]]), sc, (0, 0, 0))[0] - to_flu(np.zeros((1, 3)), sc, (0, 0, 0))[0]
    bore = bore / np.linalg.norm(bore)
    if np.dot(pull, bore) > 0:
        pull = -pull            # a pump goes BACK, against the bore
    travel = pump['travel'] * GP.np.float64(1.02) * abs(sc[1])
    bolt = (parts.get('bolt') or [None])[0]
    sv = {donor: dict(parts=dict(pump=dict(grab_point=pump_c.tolist(), pull_dir=pull.tolist(), travel_cm=float(travel)),
                                  shell=dict(port_centroid=port.tolist(), push_dir=bore.tolist()),
                                  **({'bolt': dict(travel_cm=float(bolt['travel'] * 1.02 * abs(sc[1])))} if bolt else {})))}
    shell_len = float(np.ptp(to_flu(m[shell['surf']]['xyz'][lf], sc, of) @ bore))
    g = dict(key=donor, cls=donor, set='ms', mesh=mesh, path=blk['path'], model=blk['model'], skin=blk['skin'] or 'rsr_clear.png',
             scale=sc, off=of, extra='\tNoInterpolation\n' if blk['nointerp'] else '', ready_frame=rf,
             pump_surfs=[pump['surf']], bolt_surfs=[bolt['surf']] if bolt else [], shell_surf=shell['surf'], shell_frame=lf,
             lead=tuple(bore), depth=round(max(1.5, shell_len * 1.05), 2),
             ready_sprite='', spr_gun='', spr_part='', spr_world='', waits='',
             snd=dict(shell=('', 0), back=('', 0), fwd=('', 0), land=''), reserve='', magammo='', eject_frames=[])
    frac, how = pump_frac(donor, lock, pump['frames'])
    if frac < 0:
        # 2.0 measured the pump point on the SAME mesh (tools_kit/rack_frac.py): timing is the mesh's, not the
        # placement's, so it carries over where reload_names matched the mesh exactly ('exact' / 'moved')
        f2, how2 = rack_20(donor)
        if f2 is not None:
            frac, how = f2, how2
    return dict(g=g, sv=sv, frac=frac, frac_how=how, port=port, pump=pump_c, travel=travel), None


def noshell_modeldef(g):
    """gen_pump.modeldef without the gun-shell blocks (the shell alone at the port, in the hand, dropped)"""
    g2 = dict(g, shell_surf=g['pump_surfs'][0])
    out, keep, cur = [], True, []
    for l in GP.modeldef(g2):
        if l.startswith('// ') and l != GP.modeldef(g2)[0]:
            keep = not ('shell' in l)
        if keep:
            out.append(l)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dry', action='store_true'); ap.add_argument('--only', default='')
    a = ap.parse_args()
    only = set(x for x in a.only.split(',') if x)
    GP.ERMAC = os.path.join(ROOT, 'models', 'ammo_hand') + '/'     # Ermac's shell (shot_shell.md3), from the 2.0 branch
    GP.MODELSWAPPER = True
    blocks = donor_blocks()
    lock = json.load(open(os.path.join(ROOT, 'sources.lock.json')))
    shelf = open(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs')).read()
    guns, rep = [], ['# Pump rows from the cards (tools_kit/card_pump.py)', '', '| donor | result |', '|---|---|']
    for card in sorted(glob.glob(os.path.join(ROOT, 'cards/*/*/*.card'))):
        if '.blend' in card or '/_' in card:
            continue
        txt = open(card).read()
        if not re.search(r'^\s{4}pump\s+surf', txt, re.M):
            continue
        rel = os.path.relpath(os.path.dirname(card), ROOT)
        donor = next((d for d, b in blocks.items() if b['path'] == rel and b['model'] == os.path.basename(card)[:-5] + '.md3'), None)
        if not donor or (only and donor not in only):
            continue
        try:
            r, why = build(donor, card, blocks[donor], lock)
        except Exception as e:
            r, why = None, 'error: %s' % e
        if not r:
            rep.append('| %s | left out: %s |' % (donor, why)); continue
        g = r['g']; n = len(guns)
        code = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[n]
        g['spr_gun'], g['spr_part'], g['spr_world'] = 'QP%sG' % code, 'QP%sP' % code, 'QP%sW' % code
        g['ready_sprite'] = '%s A' % re.search(r'"\w+\|%s\|(\w{4})\|' % donor, shelf).group(1)
        try:
            if not r.get('noshell'):
                GP.compute(g, r['sv'])
        except Exception as e:
            rep.append('| %s | left out: gen_pump refused: %s |' % (donor, e)); continue
        g['frac'] = r['frac']
        guns.append(g)
        rep.append('| %s | slot %d: port %s, pump %s, travel %.2f cm, pump point %s (%s) |' % (
            donor, n + 1, np.round(r['port'], 2).tolist(), np.round(r['pump'], 2).tolist(), r['travel'], r['frac'], r['frac_how']))
    print('\n'.join(rep))
    if a.dry or not guns:
        return
    zs = GP.zs(guns)
    sprites = ''.join('\t\t%s %s 0;\n' % (s, l) for g in guns for s, l in ((g['spr_gun'], 'A'), (g['spr_part'], 'ABC'), (g['spr_world'], 'A')))
    zs += ['', '// the sprites the card guns\' pump layers name (a MODELDEF naming an unknown sprite stops the pk3 loading)',
           'class RSP_Sprites_Cards : Actor', '{', '\tStates', '\t{', '\tSpawn:', sprites.rstrip('\n'), '\t\tStop;', '\t}', '}']
    open(os.path.join(ROOT, 'zscript_depot/rsr/rsr_pump_guns.zs'), 'w').write(
        '// GENERATED by tools_kit/card_pump.py from the MS 1.5 cards (gen_pump.py unchanged) -- do not edit by hand.\n' + '\n'.join(zs) + '\n')
    md = ['// GENERATED by tools_kit/card_pump.py (gen_pump.modeldef, unchanged) -- the card guns\' pump layers.']
    for g in guns:
        lines = GP.modeldef(g) if g.get('own_shell', True) else noshell_modeldef(g)
        md += lines
    open(os.path.join(ROOT, 'MODELDEF.rsrpump'), 'w').write('\n'.join(md) + '\n' + GP.HANDS_MODELDEF)
    # the layers mask surfaces with rsr_clear.png, looked up in each layer's own Path (the card folder)
    import shutil
    for sec in re.split(r'\n(?=Model\s)', '\n'.join(md)):
        pm = re.search(r'Path\s+"([^"]+)"', sec)
        if pm and 'rsr_clear.png' in sec and os.path.isdir(os.path.join(ROOT, pm.group(1))) \
                and not os.path.exists(os.path.join(ROOT, pm.group(1), 'rsr_clear.png')):
            shutil.copy(os.path.join(ROOT, 'reload_1x', 'rsr_clear.png'), os.path.join(ROOT, pm.group(1), 'rsr_clear.png'))
    rk = ['// GENERATED by tools_kit/card_pump.py -- do not edit by hand.',
          '// Where each pump donor\'s pump starts in its fire-then-pump, as a fraction of those tics (-1: none).',
          'class RSP_Rack abstract', '{', '\tclearscope static double Frac(String donor)', '\t{']
    for g in guns:
        rk.append('\t\tif (donor == "%s")\treturn %.4f;' % (g['cls'], g['frac']))
    rk += ['\t\treturn -1;', '\t}', '}']
    open(os.path.join(ROOT, 'zscript_depot/rsr/rsp_rack.ms.zs'), 'w').write('\n'.join(rk) + '\n')
    open(os.path.join(ROOT, 'card_pump.report.md'), 'w').write('\n'.join(rep) + '\n')


if __name__ == '__main__':
    main()
