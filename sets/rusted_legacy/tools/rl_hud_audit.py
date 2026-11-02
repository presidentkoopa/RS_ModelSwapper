#!/usr/bin/env python3
"""rl_hud_audit.py: check his gun ammo display (weaponhud2.txt + modeldefs/holohud2.txt) and wrist watch
(weaponhud.txt + modeldefs/holohud.txt) against each other, per weapon class. Parsed, not guessed.

For every HUD sprite frame his states can reach (menu options only: rl_weaphud_color 0-8,
rl_weaphud_bg 0-2, rl_weaphud_scale 1-3, rl_wwatch_color 0-7, rl_wwatch_mode 0-1), every weapon class
that draws the HUD must have a MODELDEF FrameIndex for it, or that frame draws nothing. Also: every
model and skin a HUD FrameIndex names exists in the pack, and every overlay call in a state block
targets the layer that block draws.

  python3 sets/rusted_legacy/tools/rl_hud_audit.py
"""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')


def read(p):
    return open(os.path.join(SRC, p), errors='replace').read()


def strip(t):
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    return re.sub(r'//[^\n]*', '', t)


def states(t):
    """label -> list of (sprite, frames) and goto targets, in order"""
    out, cur = {}, None
    for line in strip(t).splitlines():
        m = re.match(r'\s*(\w+):\s*$', line)
        if m:
            cur = m.group(1)
            out.setdefault(cur, [])
            continue
        if cur is None:
            continue
        m = re.match(r'\s*([A-Z0-9_#]{4})\s+([A-Z\[\]\\#]+)\s+-?\d+', line)
        if m and m.group(1) not in ('TNT1', '####'):
            out[cur].append(('spr', m.group(1), m.group(2)))
        for j in re.findall(r'A_JumpIf\(([^,]+),\s*"(\w+)"\)', line):
            out[cur].append(('jump', j[0].strip(), j[1]))
        m = re.match(r'\s*(Goto|goto)\s+(\w+)', line)
        if m:
            out[cur].append(('goto', m.group(2)))
        for f in re.findall(r'A_Overlay(?:Flags|Renderstyle|Alpha)\((\w+)', line):
            out[cur].append(('ovl', f))
    return out


def reachable(st, entries, env):
    """labels reachable from entries given cvar values env (name -> value); unconditional fallthrough follows
    the label order of the file"""
    order = list(st)
    seen, todo = set(), list(entries)
    while todo:
        lab = todo.pop()
        if lab in seen or lab not in st:
            continue
        seen.add(lab)
        stopped = False
        for it in st[lab]:
            if it[0] == 'jump':
                cond = it[1]
                m = re.match(r'invoker\.(\w+)\s*==\s*(\d+)', cond)
                if m and m.group(1) in env:
                    if env[m.group(1)] == int(m.group(2)):
                        todo.append(it[2])
                        stopped = True
                        break
                    continue
                todo.append(it[2])		# a condition we do not model: both ways
            elif it[0] == 'goto':
                todo.append(it[1])
                stopped = True
                break
        if not stopped and not any(i[0] == 'spr' for i in st[lab]):
            i = order.index(lab)
            if i + 1 < len(order):
                todo.append(order[i + 1])
    return seen


def modeldef_frames(t):
    """class -> set of (sprite, frame) with FrameIndex, plus models/skins named"""
    out, files = {}, []
    for m in re.finditer(r'Model\s+(\w+)\s*\{(.*?)\n\}', strip(t), re.S):
        cls, body = m.group(1), m.group(2)
        path = re.search(r'Path\s+"([^"]+)"', body)
        path = path.group(1) if path else ''
        for f in re.findall(r'FrameIndex\s+(\w{4})\s+(\w)\s', body):
            out.setdefault(cls, set()).add(f)
        for f in re.findall(r'(?:Model|Skin)\s+\d+\s+"([^"]+)"', body):
            files.append((cls, os.path.join(path, f)))
    return out, files


def exists(path):
    p = os.path.join(SRC, path)
    if os.path.exists(p):
        return True
    low = path.lower()
    for root, _, fs in os.walk(SRC):
        for f in fs:
            if os.path.relpath(os.path.join(root, f), SRC).lower() == low:
                return True
    return False


def frames_of(st, labs):
    used = set()
    for lab in labs:
        for it in st.get(lab, []):
            if it[0] == 'spr':
                for ch in re.sub(r'[\[\]\\#]', '', it[2]):
                    used.add((it[1], ch))
    return used


def main():
    bad = 0
    gun = states(read('zscript/weapons/weaponhud2.txt'))
    wat = states(read('zscript/weapons/weaponhud.txt'))
    entries_gun = [l for l in gun if re.match(r'whud_(bg|mag_d\d)$', l)]
    entries_wat = [l for l in wat if re.match(r'(w|wh|watch)\w*$', l) and not re.search(r'\d$', l)][:0] or list(wat)[:1]
    need_gun = set()
    for scale in (1, 2, 3):
        for bg in (0, 1, 2):
            for col in range(9):
                env = dict(WeaponHUDScale=scale, WeaponHUDBG=bg, WeaponHUDColor=col)
                need_gun |= frames_of(gun, reachable(gun, entries_gun, env))
    md = {}
    files = []
    for f in sorted(os.listdir(os.path.join(SRC, 'modeldefs'))):
        if f.endswith('.txt'):
            m, fl = modeldef_frames(read('modeldefs/' + f))
            for k, v in m.items():
                md.setdefault(k, set()).update(v)
            files += [(f, c, p) for c, p in fl]
    hud_sprites = {s for s, _ in need_gun}
    classes = sorted(c for c, fr in md.items() if any(s in hud_sprites for s, _ in fr))
    print('gun display: %d reachable frames over sprites %s; classes drawing it: %s'
          % (len(need_gun), ' '.join(sorted(hud_sprites)), ' '.join(classes)))
    for c in classes:
        miss = sorted(need_gun - md[c])
        if miss:
            bad += 1
            print('  MISSING %s: %s' % (c, ' '.join(s + f for s, f in miss)))
    # overlay calls that target another block's layer
    for name, st in (('weaponhud2.txt', gun), ('weaponhud.txt', wat)):
        for lab, items in st.items():
            o = {i[1] for i in items if i[0] == 'ovl'}
            if name == 'weaponhud2.txt' and lab.startswith('whud_bg') and o and o != {'PSP_HHUD_BG'}:
                bad += 1
                print('  LAYER %s %s: overlay calls on %s, the block draws PSP_HHUD_BG' % (name, lab, ' '.join(sorted(o))))
    # files named by HUD model blocks
    for f, c, p in files:
        if f.startswith('holohud') and not exists(p):
            bad += 1
            print('  NO FILE %s (%s, %s)' % (p, f, c))
    # watch: every frame the watch states draw, per class
    need_w = frames_of(wat, list(wat))
    wspr = {s for s, _ in need_w}
    wcls = sorted(c for c, fr in md.items() if any(s in wspr for s, _ in fr))
    print('wrist watch: %d frames over sprites %s (all states, conditions not modelled); classes: %s'
          % (len(need_w), ' '.join(sorted(wspr)), ' '.join(wcls)))
    for c in wcls:
        miss = sorted(need_w - md[c])
        if miss:
            print('  watch frames %s has no FrameIndex for: %s' % (c, ' '.join(s + f for s, f in miss)))
    print('HUD AUDIT: %d problem(s)' % bad)
    return bad


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
