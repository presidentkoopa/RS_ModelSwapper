"""refit_outliers.py -- re-fit the hand rows that fail hand_gap badly, by the current method, minimally.

    MS_GRIPREGIONS=<gripregions.json> MS_ERMAC_HANDS=<Ermac models/hand> \\
        python3 -B tools_kit/refit_outliers.py [--write] [--render OUTDIR] DONOR ...

Owner, 2026-10-26: a new FBX-skeleton fitter is coming, so only the poses that look broken are
re-fitted, and only until they pass hand_gap. The method is handfit_cards.py's (the kit's): keep
Ermac's pose (same frame, same rotation -- these rows have none), and find the TRANSLATION that puts
his measured gripping face (gripregions.json `contact`) onto this gun's surface by trimmed ICP
(handfit_cards.icp_translate). The search is anchored where the hand is drawn now (its contact face at
the row's hook) in a tight window, so the hand slides onto the part it was meant to hold rather than
jumping to another. The gun hand then sits GUN_DROP lower, as every fitted row does. A result is kept
only if tools_kit/hand_gap.py, the gate's own check, passes with it.
"""
import os, re, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import handfit_cards as HF
import hand_gap as G

GUN_POSE = {v: k for k, v in HF.GUN_LETTER.items()}       # letter -> Ermac hand.md3 frame
SUP_POSE = {v: k for k, v in HF.SUP_LETTER.items()}        # letter -> Ermac hand2.md3 frame
WIN = {'gun': (9.0, 5.0, 9.0), 'support': (6.0, 6.0, 6.0)}   # handfit_cards' windows (F, L, U half sizes, cm)


def gun_item(donor, blocks):
    b = blocks[donor]
    sc, off, fr = G.placement(b)
    base = re.search(r'Path\s+"([^"]+)"', b).group(1)
    items = []
    for n, mdl in re.findall(r'^[ \t]*Model\s+(\d+)\s+"([^"]+)"', b, re.M):
        p = G.resolve(os.path.join(ROOT, base, mdl))
        frm = re.search(r'FrameIndex\s+\w+\s+A\s+%s\s+(\d+)' % n, b)
        if os.path.exists(p) and (frm or n == '0'):
            items.append(dict(path=p, frame=int(frm.group(1)) if frm else fr, scale=sc, off=off, color=[150, 155, 170]))
    return items


def shift_of(hook):
    """a hook (L, U, -F) on Ermac's placement -> the F, L, U shift it is (handfit_cards.hand_item)"""
    return np.array([-hook[2], hook[0], hook[1]], float)


def hook_of(shift):
    return [round(float(shift[1]), 3), round(float(shift[2]), 3), round(float(-shift[0]), 3)]


def refit(donor, blocks, slot, tb, lt):
    i = slot[donor]
    gp = G.gaps(donor, blocks, slot, tb, lt)
    items = gun_item(donor, blocks)
    pts = np.concatenate([HF.surface_points(it) for it in items])
    out = {}
    for name, hk, rot, key in (('gun', 'GunHook', 'GunRot', 'hand:%d' % GUN_POSE[G.row(tb, i, 'GunTwo')]),
                               ('support', 'SupportHook', 'SupportRot', 'hand2:%d' % SUP_POSE[G.row(tb, i, 'Support')])):
        if gp.get(name) is None or gp[name] <= (G.MAX_GUN if name == 'gun' else G.MAX_SUPPORT):
            continue                    # this hand passes: left exactly as it is (minimal)
        if np.abs(G.row(tb, i, rot)).max() > 0:
            out[name] = None            # a turned hand: not this method's (minigun_fit.rot_hook)
            continue
        old = shift_of(G.row(tb, i, hk))
        patch = HF.contact_patch(key)
        now = patch + old
        c = now.mean(0)
        dst = []
        for grow in (1.0, 1.5, 2.0):     # the kit's window first; wider only when it holds no gun at all
            w = np.array(WIN[name]) * grow
            dst = HF.box(pts, f=(c[0] - w[0], c[0] + w[0]), l=(c[1] - w[1], c[1] + w[1]), u=(c[2] - w[2], c[2] + w[2]))
            if len(dst) >= 20:
                break
        if len(dst) < 20:
            out[name] = dict(why='no gun surface within %.0f cm of the hand' % (2 * max(WIN[name])))
            continue
        t, err = HF.icp_translate(patch, dst, old)
        if name == 'gun':
            t = t + np.array([0, 0, HF.GUN_DROP])
        out[name] = dict(old=G.row(tb, i, hk).tolist(), new=hook_of(t), moved=round(float(np.linalg.norm(t - old)), 2), err=round(err, 2), pose=key, window=round(grow, 1))
    return out


def write_rows(changes):
    p = os.path.join(ROOT, 'zscript_depot/rsq/handtable.zs')
    t = open(p, encoding='utf-8').read()
    for (fn, i), v in changes.items():
        m = re.search(r'(static Vector3 %s\(int i\)\s*\{)(.*?)(\n\t\})' % fn, t, re.S)
        body = m.group(2)
        for axis, val in zip('xyz', v):
            am = re.search(r'static const double %s\[\] = \{(.*?)\};' % axis, body, re.S)
            vals = [x.strip() for x in am.group(1).split(',')]
            vals[i] = '%.3f' % val
            body = body[:am.start(1)] + ', '.join(vals) + body[am.end(1):]
        t = t[:m.start(2)] + body + t[m.end(2):]
    open(p, 'w', encoding='utf-8', newline='\n').write(t)


def render(donor, blocks, slot, tb, lt, outdir, tag):
    import hudrender as H
    i = slot[donor]
    items = gun_item(donor, blocks)
    hp = dict(scale=[-1.0, 1.0, 1.0], off=[0.0, -24.0, -10.0])
    trig = G.row(tb, i, 'Trigger')
    for key, hk, rot, col in ((('RQGT', trig) if trig else ('RQGS', G.row(tb, i, 'GunTwo')), 'GunHook', 'GunRot', [225, 170, 135]),
                              (('RQSP', G.row(tb, i, 'Support')), 'SupportHook', 'SupportRot', [235, 140, 120])):
        mesh, f = lt[key]
        items.append(dict(hp, path=mesh, frame=f, hook=list(G.row(tb, i, hk)), rot=list(G.row(tb, i, rot)), color=col))
    P = np.concatenate([H.to_local(xyz[min(it['frame'], len(xyz) - 1)], it) for it in items for _, xyz in H.load(it['path'])])
    c = (P.min(0) + P.max(0)) / 2
    r = float(np.ptp(P, 0).max())
    r_ = G.gaps(donor, blocks, slot, tb, lt)
    title = '%s %s: gun hand %.2f cm, support %.2f cm from the gun' % (donor, tag, r_['gun'], r_['support'])
    outs = []
    for view, e in (('side', (1.0, 0.25, 0.0)), ('below', (0.55, -0.75, 0.35))):
        outs.append(H.render(items, os.path.join(outdir, '%s_%s_%s.png' % (donor, tag, view)), eye=tuple(c + np.array(e) * r * 2.2),
                             look=tuple(c), W=480, H=360, fov=45, title=title))
    return outs


def main(argv):
    names = [x for x in argv if not x.startswith('--')]
    outdir = argv[argv.index('--render') + 1] if '--render' in argv else None
    names = [x for x in names if x != outdir]
    md = open(os.path.join(ROOT, 'modeldef'), encoding='utf-8', errors='replace').read()
    blocks = G.donor_blocks(md)
    slot, tb = G.tables()
    lt = G.letters()
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        before = {d: render(d, blocks, slot, tb, lt, outdir, 'BEFORE') for d in names}
    changes, report = {}, {}
    for d in names:
        r = refit(d, blocks, slot, tb, lt)
        report[d] = r
        for name, fn in (('gun', 'GunHook'), ('support', 'SupportHook')):
            if r.get(name) and 'new' in r[name]:
                changes[(fn, slot[d])] = r[name]['new']
                if name == 'gun':
                    changes[('GunHookTwo', slot[d])] = r[name]['new']
        print(d, json.dumps(r))
    if '--write' in argv:
        write_rows(changes)
        slot, tb = G.tables()
        for d in names:
            ok, lines = G.check(d)
            print('  %-26s %s  %s' % (d, 'PASS' if ok else 'FAIL', '; '.join(lines)))
        if outdir:
            from PIL import Image
            for d in names:
                after = render(d, blocks, slot, tb, lt, outdir, 'AFTER')
                ims = [Image.open(x) for x in before[d] + after]
                w, h = ims[0].size
                sheet = Image.new('RGB', (w * 2, h * 2))
                for k, im in enumerate(ims):
                    sheet.paste(im, ((k // 2) * w, (k % 2) * h))
                fn = os.path.join(outdir, 'refit_%s.png' % d)
                sheet.save(fn)
                print('  sheet', fn)
    json.dump(report, open(os.path.join(outdir or '.', 'refit_report.json'), 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1:])
