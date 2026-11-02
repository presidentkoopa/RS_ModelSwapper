#!/usr/bin/env python3
"""gen_hudfast.py: compile his watch and gun-display state chains into plain ZScript functions.

His DoomWeaponZ.Tick destroys and re-creates all 17 HUD layers every tic (10 watch, 7 gun display), and each
new layer runs a chain of up to 13 A_JumpIf states to pick its sprite frame; the numbers are found by turning
ammo, health and armor into strings every tic. On a Quest that is 17 PSprite objects and a dozen strings of
garbage per tic, plus ~150 VM action calls.

This reads his own states (zscript/weapons/weaponhud.txt, weaponhud2.txt) and writes, for every state label,
a function that follows exactly the same jumps and returns the frame his chain would show this tic:
    code = (sprite index into RSH_SPRITES) << 8 | frame << 1 | bright,  or -1 for an invisible frame
so the layers can be created once and only have their sprite and frame set when they change
(zscript/rsrl/rsrl_hudfast.zs). Nothing about what is drawn is decided here: it is his chains, compiled.
rsrl_hudcheck 1 runs his original path every tic and compares it with the compiled one (rig: tools/rl_hudcheck.py).

  python3 sets/rusted_legacy/tools/gen_hudfast.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), 'src')


def strip(t):
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    return re.sub(r'//[^\n]*', '', t)


def parse(path):
    t = strip(open(os.path.join(SRC, path), newline='').read())
    t = t[t.index('States'):]
    labels, order, cur = {}, [], None
    for raw in t.splitlines():
        line = raw.strip()
        if not line or line in ('{', '}', 'States'):
            continue
        m = re.match(r'^(\w+):$', line)
        if m:
            cur = m.group(1)
            labels[cur] = []
            order.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r'^(goto|Goto)\s+(\w+)\s*;?$', line)
        if m:
            labels[cur].append(('goto', m.group(2)))
            continue
        if re.match(r'^(loop|Loop|stop|Stop)\s*;?$', line):
            labels[cur].append(('loop' if line.lower().startswith('loop') else 'stop',))
            continue
        m = re.match(r'^(\w{4})\s+(\w+)\s+(-?\d+)\s*(Bright)?\s*(.*?);?$', line)
        if not m:
            sys.exit('%s: cannot read %r' % (path, line))
        spr, frames, tics, bright, act = m.groups()
        if len(frames) != 1:
            sys.exit('%s: multi-frame line %r' % (path, line))
        tics = int(tics)
        act = act.strip().rstrip(';')
        j = re.match(r'^A_JumpIf\((.*),\s*"(\w+)"\)$', act)
        if act and not j and not act.startswith('A_Overlay'):
            sys.exit('%s: unhandled action %r' % (path, act))
        if tics != 0:
            if j or act.startswith('A_Overlay'):
                sys.exit('%s: action on a shown frame %r' % (path, line))
            labels[cur].append(('show', spr, frames, bool(bright)))
        elif j:
            labels[cur].append(('jump', j.group(1).strip(), j.group(2)))
        elif act.startswith('A_Overlay'):
            labels[cur].append(('ovl', act))
        elif spr != 'TNT1':
            sys.exit('%s: zero-tic sprite %r' % (path, line))
    return labels, order


def compile_file(path, sprites, out):
    labels, order = parse(path)

    def fn(l):
        return 'RSH_' + l

    for i, l in enumerate(order):
        body = []
        ended = False
        for it in labels[l]:
            if it[0] == 'jump':
                cond = it[1].replace('invoker.', '')
                if it[2] not in labels:
                    sys.exit('%s: jump to unknown %s' % (path, it[2]))
                body.append('\t\tif (%s) return %s();' % (cond, fn(it[2])))
            elif it[0] == 'show':
                if it[1] == 'TNT1':
                    body.append('\t\treturn -1;')
                else:
                    if it[1] not in sprites:
                        sprites.append(it[1])
                    body.append('\t\treturn %d;\t// %s %s%s' % ((sprites.index(it[1]) << 8) | ((ord(it[2]) - 65) << 1) | int(it[3]),
                                                             it[1], it[2], ' Bright' if it[3] else ''))
                ended = True
                break
            elif it[0] == 'goto':
                body.append('\t\treturn %s();' % fn(it[1]))
                ended = True
                break
            elif it[0] in ('loop', 'stop'):
                sys.exit('%s: %s with no shown frame in %s' % (path, it[0], l))
        if not ended:
            if i + 1 >= len(order):
                sys.exit('%s: %s falls off the end' % (path, l))
            body.append('\t\treturn %s();' % fn(order[i + 1]))
        out.append('\tint %s()\n\t{\n%s\n\t}' % (fn(l), '\n'.join(body)))
    # no label may reach itself without showing a frame
    def walk(l, seen):
        if l in seen:
            sys.exit('%s: %s loops without a shown frame' % (path, l))
        seen = seen | {l}
        for it in labels[l]:
            if it[0] == 'jump':
                walk(it[2], seen)
            elif it[0] in ('show',):
                return
            elif it[0] == 'goto':
                walk(it[1], seen)
                return
        i = order.index(l)
        walk(order[i + 1], seen)
    for l in order:
        walk(l, set())
    return labels


def main():
    sprites = []
    out = []
    w = compile_file('zscript/weapons/weaponhud.txt', sprites, out)
    g = compile_file('zscript/weapons/weaponhud2.txt', sprites, out)
    ovl = [(l, it[1]) for lab in (w, g) for l, items in lab.items() for it in items if it[0] == 'ovl']
    z = ['// GENERATED by sets/rusted_legacy/tools/gen_hudfast.py from his weaponhud.txt and weaponhud2.txt.',
         '// Each function is one of his state labels: the same jumps, returning the frame his chain shows.',
         '// Do not edit by hand.', '//', '// His overlay style calls, applied once when a layer is made (rsrl_hudfast.zs):']
    z += ['//   %s: %s' % o for o in ovl]
    z += ['', 'extend class DoomWeaponZ', '{', '\tconst RSH_NSPRITES = %d;' % len(sprites),
          '\tstatic name RSH_SpriteName(int i)', '\t{', '\t\tswitch (i)', '\t\t{']
    z += ['\t\tcase %d: return \'%s\';' % (i, s) for i, s in enumerate(sprites)]
    z += ['\t\t}', '\t\treturn \'TNT1\';', '\t}', '']
    z += out
    z += ['}', '']
    open(os.path.join(SRC, 'zscript/rsrl/rsrl_hudfast_table.zs'), 'w').write('\n'.join(z))
    print('%d labels compiled, %d sprites' % (len(out), len(sprites)))
    for o in ovl:
        print('overlay call in', o[0], ':', o[1])


if __name__ == '__main__':
    main()
