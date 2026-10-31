"""rack_frac.py -- where in each pump donor's FIRE its pump starts, measured from the donor's own mesh.

    python -B tools_kit/rack_frac.py [--dry]

Writes zscript_depot/rsr/rsp_rack.ms.zs: RSP_Rack.Frac(donor), the fraction of the fire animation's
tics at which the pump begins to move (-1: not measured). The join (RS_ForeignReload.zs, "the pump
after a shot") holds a foreign shotgun at that point of the mod's OWN fire states -- the same
fraction ModelSwapper's animation uses to lay a donor's clip over a mod's states by tic -- while
the off hand works the pump; then the mod's own states carry on. (Owner, 2026-10-25: "Hold at the
mod's pump".)

Measured, per donor:
  the pump's motion  md3label's part that slides along the bore (`slide` / `pump`), frames a..b,
                     from the donor's motion card (cards_*/), or md3label run now on the mesh the
                     donor's MODELDEF block draws, at its rest frame (into cards_left/).
  the fire timeline  the donor's fire clip in RS_ForeignAnim.zs, expanded per tic; for a donor with
                     no clip, md3label's `fire` phase that contains frame a, one tic per frame.
  Frac               the first tic of that timeline showing a frame in a..b, over its length.
A donor with no measured pump motion, or whose pump is not inside its fire, gets -1: no hold, the
mod's own pump runs, and this prints why.
"""
import os, re, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import placement_audit as PA

DIRS = ('cards_hud', 'cards_shelf', 'cards_packs', 'cards_bd', 'cards_left')
OUT = os.path.join(ROOT, 'zscript_depot/rsr/rsp_rack.ms.zs')


def pump_donors():
    t = open(os.path.join(ROOT, 'zscript_depot/rsr/rsr_pump_guns.zs')).read()
    return [d for d, _ in re.findall(r'donor == "(\w+)"\)\s*return (\d+);', t)]


def clip_tics(spec):
    out = []
    for step in spec.split(','):
        f, t = step.split('@')
        t = int(t)
        if '-' in f:
            a, b = (int(x) for x in f.split('-'))
            rng = range(a, b + 1) if b >= a else range(a, b - 1, -1)
        else:
            rng = [int(f)]
        for x in rng:
            out += [x] * t
    return out


def motion_card(d, body):
    for dd in DIRS:
        p = os.path.join(ROOT, dd, d + '.card')
        if os.path.exists(p):
            return p, dd
    path = re.search(r'Path\s+"([^"]+)"', body).group(1)
    model = re.search(r'Model\s+0\s+"([^"]+)"', body).group(1)
    src = PA.resolve(os.path.join(ROOT, path, model))
    rest = next(int(f) for s, f in re.findall(r'FrameIndex\s+(\w{4})\s+\S\s+0\s+(\d+)', body) if s != 'MSBL')
    tmp = os.path.join(ROOT, 'cards_left', '.md3label')
    subprocess.run([sys.executable, '-B', os.path.join(HERE, 'md3label.py'), src, tmp, d, '--idle', str(rest)],
                   capture_output=True, text=True, cwd=ROOT)
    p = os.path.join(tmp, d + '.card')
    if not os.path.exists(p):
        return None, None
    q = os.path.join(ROOT, 'cards_left', d + '.card')
    open(q, 'w', newline='\n').write(open(p).read())
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    return q, 'md3label now'


def main(dry):
    blocks = PA.donor_blocks()
    anim = open(os.path.join(ROOT, 'zscript/RS_ForeignAnim.zs')).read()
    rows = []
    for d in pump_donors():
        if d not in blocks:
            print('  %-20s no MODELDEF block' % d); continue
        p, how = motion_card(d, blocks[d])
        if not p:
            print('  %-20s md3label failed' % d); rows.append((d, -1, 'not measured')); continue
        c = open(p).read()
        m = re.search(r'^\s*(?:slide|pump)\s+surf\s+(\d+)\s.*?frames\s+(\d+)\.\.(\d+)', c, re.M)
        if not m:
            print('  %-20s no pump motion in %s' % (d, os.path.relpath(p, ROOT)))
            rows.append((d, -1, 'no pump motion measured')); continue
        a, b = int(m.group(2)), int(m.group(3))
        fc = re.search(r'"%s\|fire\|([^|"]+)' % d, anim)
        if fc:
            tl, src = clip_tics(fc.group(1)), 'its fire clip'
        else:
            # the shot's cycle: from the last `fire` phase starting at or before the pump to the
            # end of the pump's own motion (md3label may label the stroke `rack`, after an idle)
            ph = [(int(x), int(y)) for x, y in re.findall(r'^\s*fire\s+(\d+)\.\.(\d+)', c, re.M)]
            ph = [w for w in ph if w[0] <= a]
            if not ph:
                print('  %-20s no fire phase before its pump %d..%d' % (d, a, b))
                rows.append((d, -1, 'no fire before its pump')); continue
            s0 = max(w[0] for w in ph)
            e0 = max(b, max(w[1] for w in ph if w[0] == s0))
            tl, src = list(range(s0, e0 + 1)), 'md3label fire %d to the pump\'s end %d' % (s0, e0)
        k = next((n for n, f in enumerate(tl) if a <= f <= b), None)
        if k is None:
            print('  %-20s pump %d..%d never shows in %s' % (d, a, b, src))
            rows.append((d, -1, 'pump frames not in its fire')); continue
        fr = k / float(len(tl))
        why = 'pump (surface %s) moves on frames %d..%d (%s, %s); first shown at tic %d of %d of %s' % (
            m.group(1), a, b, os.path.relpath(p, ROOT), how, k, len(tl), src)
        print('  %-20s %.3f  %s' % (d, fr, why))
        rows.append((d, fr, why))
    if dry:
        return
    L = ['// GENERATED by tools_kit/rack_frac.py -- do not edit by hand.',
         '// Where each pump donor\'s pump starts in its fire, as a fraction of the fire\'s tics (-1: none).',
         'class RSP_Rack abstract', '{', '\tclearscope static double Frac(String donor)', '\t{']
    for d, fr, why in rows:
        L.append('\t\t// %s' % why)
        L.append('\t\tif (donor == "%s")\treturn %.4f;' % (d, fr))
    L += ['\t\treturn -1;', '\t}', '}', '']
    open(OUT, 'w', newline='\n').write('\n'.join(L))


if __name__ == '__main__':
    main('--dry' in sys.argv)
