"""Carry a hand-measured RS_VR_Weapons card onto our animated mesh.

Every measured number in a card lives in the frame of the mesh it was measured
against -- the static _wm copy. card_transforms.json holds the rigid move that
carries that frame onto the animated mesh we actually ship. Applying it is not a
blanket multiply: a POINT must be rotated and shifted, a DIRECTION only rotated
(shifting a unit vector makes it meaningless), and a LENGTH left alone, because
a rigid move does not scale anything.

Fields are classified below by what they are, not by guessing from their names at
runtime -- an unknown field is reported, never silently copied as if it were safe.
"""
import json, os, re, sys
import numpy as np

POINTS = {'muzzle', 'ejectport', 'magcenter', 'triggerat', 'supportat', 'palm',
          'seat', 'grab', 'handseat', 'at', 'pivot', 'exhaustport'}
DIRS = {'barrel', 'ejectdir', 'axis', 'dir', 'handaxis', 'exhaustdir', 'twistaxis'}
# an extent is not a point: a rigid move cannot change how big a thing is,
# only which axis each dimension lies along, so rotate it and take magnitudes
SIZES = {'grabsize', 'size'}
SCALARS = {'rake', 'grabradius', 'distance', 'detach', 'take', 'capacity',
           'magscale', 'roundscale', 'linkscale'}
PASS = {'hand', 'type', 'prop', 'magfamily', 'kind', 'role', 'subject', 'surface',
        'firesound', 'drysound', 'magoutsound', 'maginsound', 'rackapexsound',
        'rackresetsound', 'magdropsound', 'model', 'skin', 'magmodel', 'magskin',
        'roundmodel', 'roundskin',
        'casing', 'firesfrom', 'hands', 'mechanism', 'linkmodel', 'linkskin',
        'closesound', 'opensound', 'loadsound', 'cycleoutsound',
        'spinsound', 'spinupsound', 'spindownsound'}

NUM3 = re.compile(r'^\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*$')


def main():
    tf = json.load(open(sys.argv[1]))
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    RS = 'E:/DOOMWork/RS_VR_Weapons'
    cards = {}
    for f in sorted(os.listdir(RS)):
        if not f.startswith('WMCARD.'):
            continue
        text = open(os.path.join(RS, f), encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'(?ms)^weapon\s+"([^"]+)".*?(?=^weapon\s+"|\Z)', text):
            cards[m.group(1)] = (f, m.group(0))

    done, unknown_fields, missing = 0, set(), []
    for cls, info in sorted(tf.items()):
        if cls not in cards:
            missing.append(cls)
            continue
        src_file, body = cards[cls]
        R = np.array(info['R'])
        t = np.array(info['t'])
        mesh = info['mesh']

        def conv(line):
            m = re.match(r'^(\s*)([a-z_]+)(\s*=\s*)(.*?)(\s*(?:#.*)?)$', line)
            if not m:
                return line
            ind, key, eq, val, tail = m.groups()
            v3 = NUM3.match(val)
            if v3:
                p = np.array([float(x) for x in v3.groups()])
                if key in POINTS:
                    q = R @ p + t
                elif key in DIRS:
                    q = R @ p
                elif key in SIZES:
                    q = np.abs(R @ p)
                else:
                    unknown_fields.add(key)
                    return line
                return f'{ind}{key}{eq}{q[0]:.3f}, {q[1]:.3f}, {q[2]:.3f}{tail}'
            if key not in POINTS | DIRS | SCALARS | PASS:
                unknown_fields.add(key)
            return line

        lines = [conv(l) for l in body.splitlines()]
        head = [
            f'# {cls}, carried from {src_file} onto the ANIMATED mesh.',
            f'# source card measured against the static _wm copy;',
            f'#   rotation {np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1))):.1f} deg,'
            f' translation [{t[0]:.2f}, {t[1]:.2f}, {t[2]:.2f}], fit residual {info["resid"]}',
            f'# points rotated and shifted; directions rotated only; lengths untouched.',
        ]
        # repoint the model at ours
        d, b = os.path.split(mesh)
        lines = [re.sub(r'^(\s*model\s*=\s*).*$', rf'\g<1>"{d}" "{b}"', l) for l in lines]
        open(os.path.join(out_dir, f'{cls}.card'), 'w', encoding='utf-8').write(
            '\n'.join(head + lines) + '\n')
        done += 1

    print(f'{done} cards carried over -> {out_dir}')
    if missing:
        print(f'no card body found for: {", ".join(missing)}')
    if unknown_fields:
        print(f'fields left untouched because they are not classified: '
              f'{", ".join(sorted(unknown_fields))}')


main()
