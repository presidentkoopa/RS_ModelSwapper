"""fix_layer_skins.py -- every skin a shipped MODELDEF lump names must be in the pk3.

    python -B tools_kit/fix_layer_skins.py [--dry]

Found 2026-10-25 when build_quest.py started checking EVERY shipped MODELDEF lump, not only
modeldef / .bd22 / .rsq: ModelSwapper's own break-open and pump layers (MODELDEF.rsb,
MODELDEF.rsrpump, written by gen_rsb.py / gen_pump.py on the owner's PC) named 89 files the pk3
did not carry, on main as well:

  rsr_clear.png  the clear skin that hides a surface (the hinged part, the rounds, the pump):
                 never copied beside the meshes. A missing skin does not hide the surface.
  rev.png        V+'s revolver texture name; ModelSwapper's MS_Revolver draws rev.md3 with
                 WPN-REV.png, so its reload layers drew with no texture.

rsr_clear.png is copied from BD22Q's (8x8, alpha 0 everywhere -- checked here). Any other
missing skin is replaced only from RENAME, where each entry says whose skin it is; anything
else is reported and fails the run. gen_rsb.py / gen_pump.py run only on the owner's machine
(their inputs are paths there), so they are not changed here; this is re-run after them.
"""
import os, re, shutil, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLEAR = os.path.join(ROOT, 'models/depot_bd/bd/M79/rsr_clear.png')
# (lump, Path, skin named) -> skin it must be, and why
RENAME = {
    ('MODELDEF.rsb', 'models/hud/Revolver', 'rev.png'): 'WPN-REV.png',   # MS_Revolver's own skin (modeldef), break slot 3 is MS_Revolver only
}


def exists(p):
    """as the engine finds it: names inside a pk3 are case-insensitive"""
    sys.path.insert(0, HERE)
    import placement_audit
    return os.path.exists(placement_audit.resolve(p))


def refs(text):
    path = ''
    for n, line in enumerate(text.split('\n')):
        m = re.match(r'^\s*Path\s+"([^"]+)"', line)
        if m:
            path = m.group(1).replace('\\', '/').rstrip('/'); continue
        m = re.match(r'^\s*(?:Skin\s+\d+|SurfaceSkin\s+\d+\s+\d+)\s+"([^"]+)"', line)
        if m and '/' not in m.group(1):
            yield n, path, m.group(1)


def main(dry):
    from PIL import Image
    im = Image.open(CLEAR).convert('RGBA')
    if im.getextrema()[3] != (0, 0):
        sys.exit('%s is not fully clear' % CLEAR)
    bad = 0
    for p in sorted(glob.glob(os.path.join(ROOT, 'MODELDEF.*'))):
        lump = os.path.basename(p)
        lines = open(p, encoding='utf-8', errors='replace').read().split('\n')
        changed = False
        for n, path, skin in list(refs('\n'.join(lines))):
            if exists(os.path.join(ROOT, path, skin)):
                continue
            if skin == 'rsr_clear.png':
                print('%s: %s/rsr_clear.png <- BD22Q\'s clear skin' % (lump, path))
                if not dry:
                    shutil.copy2(CLEAR, os.path.join(ROOT, path, skin))
                continue
            new = RENAME.get((lump, path, skin))
            if new and exists(os.path.join(ROOT, path, new)):
                lines[n] = lines[n].replace('"%s"' % skin, '"%s"' % new)
                changed = True
                continue
            print('%s: %s/%s MISSING, no rule' % (lump, path, skin)); bad += 1
        if changed:
            print('%s: renamed per RENAME' % lump)
            if not dry:
                open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    if bad:
        sys.exit('%d skins with no rule' % bad)


if __name__ == '__main__':
    main('--dry' in sys.argv)
