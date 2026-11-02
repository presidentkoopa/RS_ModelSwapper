#!/usr/bin/env python3
"""gen_rsrl.py: the Rusted Legacy hand-reload rows, generated from the measured cards.

Writes  src/zscript/rsrl/rsrl_table.zs   (one row per reload gate of his, all numbers measured)
and patches every A_CheckImmersiveReloadActionN in src/zscript/weapons/*.txt so that, in VR with
rsrl_handreload on, the gate asks RSRL_Reload (src/zscript/rsrl/rsrl_reload.zs) instead of his
3-unit touch test, then calls HIS OWN setReloadStep(...) with HIS OWN arguments. Outside VR, or
with rsrl_handreload 0, his original code runs untouched.

Where every number comes from (controller frame, cm, forward/left/up):
  seat, approach axis, stroke ....... cards/<gun>/rl_<gun>.json  piece.seat / piece.approach  (rl_measure.py, mesh)
  seated piece long axis ............ the card's piece model at piece.seat_frame, PCA (mesh, here)
  piece in the off hand ............. modeldefs/weapons/fist.txt "holding ammo" block: ammo_hand frame k +
                                      the piece model frame 0, Scale -1 1 1, Offset 0 -24 -10 (mesh, here)
  palm of the empty off hand ........ models/hand/hand.md3 frame 1 (his fist), centroid of the front 10 cm (mesh, here)
  moving parts (slide, pump, barrel,  cards  parts[].rest / axis / travel / rot  (rl_measure.py, mesh)
    lever, lid)
  gate -> setReloadStep args ........ zscript/weapons/<gun>.txt (parsed)
Tolerances are BD22's RSR numbers (sets/bd22q/src/zscript/rsr/vreload.zs): capture side 3.5,
leave side 5.5, grab 7, racked 0.85 of travel. Rotating parts (rot > 5 deg) count 0.6 of their
chord, because the hand follows an arc and the chord is measured at the end of the rotation.

  RSQ_RL=sets/rusted_legacy/src python3 sets/rusted_legacy/tools/gen_rsrl.py
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.dirname(HERE)
SRC = os.path.join(SET, 'src')
os.environ.setdefault('RSQ_RL', SRC)
sys.path.insert(0, HERE)
import rl_measure as R  # noqa: E402
import md3label  # noqa: E402

# his offhand fist "holding ammo" block: piece model and ammo_hand frame per gun (fist.txt, parsed by eye
# and checked below against the file)
INHAND = {
    'pistol': ('mag_pistol', 0), 'shotgun': ('shot_shell', 1), 'ssg': ('shot_shell2', 2),
    'chaingun': ('mag_chaingun', 3), 'rocket': ('pod_rocket', 4), 'plasma': ('mag_plasma', 5),
    'bfg': ('pod_bfg', 6), 'heatwave': ('pod_heat', 7), 'incinerator': ('flame_can', 8),
    'hellshotgun': ('shot_shell', 1),
}
FILES = {
    'pistol': 'pistol', 'shotgun': 'shotgun', 'ssg': 'ssg', 'chaingun': 'chaingun',
    'rocket': 'rocketlauncher', 'plasma': 'plasmarifle', 'bfg': 'bfg9000', 'heatwave': 'heatwave',
    'incinerator': 'incinerator', 'hellshotgun': 'hellshotgun',
}
# what each of his gates is, by hand: insert the piece, or move a part.
#   ('insert',)                      the piece into its seat along the approach axis
#   ('stroke', part, sense, ret)     grab the part's rest point (sense +1) or its moved point (sense -1)
#                                    and move it along +axis (or back); ret: then return (a pump)
#   ('pull',)                        grab the seated piece and draw it out along -approach (his ReleaseCan)
GATES = {
    'pistol': {1: ('insert',), 2: ('stroke', 'slide', 1, False)},
    'shotgun': {1: ('insert',), 2: ('stroke', 'shotgun_pump', 1, True)},
    'ssg': {1: ('stroke', 'ssg_barrel', 1, False), 2: ('insert',), 3: ('stroke', 'ssg_barrel', -1, False)},
    'chaingun': {1: ('insert',)},
    'plasma': {1: ('insert',)},
    'rocket': {1: ('insert',)},
    'heatwave': {1: ('insert',)},
    'hellshotgun': {1: ('insert',), 2: ('stroke', 'hellshotgun_chamber', 1, False)},
    'incinerator': {1: ('stroke', 'flamethrower_lever', 1, False), 2: ('pull',), 3: ('insert',),
                    4: ('stroke', 'flamethrower_lever', -1, False)},
    'bfg': {1: ('stroke', 'bfg_case', 1, False), 2: ('insert',), 3: ('stroke', 'bfg_case', -1, False)},
}
ORDER = ['pistol', 'shotgun', 'ssg', 'chaingun', 'plasma', 'rocket', 'hellshotgun', 'incinerator', 'bfg', 'heatwave']

RACKED, ROT_NEED = 0.85, 0.60


def pts(path, frame):
    m = R.md3(path)
    return np.vstack([R.to_flu(md3label.surf_xyz(s)[frame]) for s in m['surfs']])


def long_axis(X):
    c = X.mean(0)
    w, V = np.linalg.eigh((X - c).T @ (X - c))
    a = V[:, -1]
    return c, a / np.linalg.norm(a)


def check_fist():
    txt = open(os.path.join(SRC, 'modeldefs/weapons/fist.txt')).read()
    for gun, (piece, k) in INHAND.items():
        if '"%s.md3"' % piece not in txt:
            sys.exit('fist.txt has no %s.md3 (gun %s)' % (piece, gun))


def gate_args(gun):
    """his setReloadStep(...) argument text per gate, parsed from his file"""
    txt = open(os.path.join(SRC, 'zscript/weapons/%s.txt' % FILES[gun]), newline='').read()
    out = {}
    for m in re.finditer(r'action void A_CheckImmersiveReloadAction(\d+)\(\)\s*\{', txt):
        body = txt[m.end():m.end() + 4000]
        depth, i = 1, 0
        while depth:
            depth += {'{': 1, '}': -1}.get(body[i], 0)
            i += 1
        s = re.findall(r'invoker\.setReloadStep\(([^)]*)\)', body[:i])
        if len(set(s)) != 1:
            sys.exit('%s gate %s: setReloadStep calls %r' % (gun, m.group(1), s))
        out[int(m.group(1))] = s[0].strip()
    return out


def v(x):
    return '(%.3f, %.3f, %.3f)' % tuple(x)


def main():
    check_fist()
    palm_X = pts('models/hand/hand.md3', 1)
    palm = palm_X[palm_X[:, 0] >= palm_X[:, 0].max() - 10].mean(0)
    rows, report, rid = [], [], 0
    gate_ids = {}
    for gun in ORDER:
        card = json.load(open(os.path.join(SET, 'cards', gun, 'rl_%s.json' % gun)))
        args = gate_args(gun)
        if sorted(args) != sorted(GATES[gun]):
            sys.exit('%s: his gates %s, the table has %s' % (gun, sorted(args), sorted(GATES[gun])))
        pc = card['piece']
        seat = np.array(pc['seat'])
        ap = pc['approach']
        A = np.array(ap['axis'], float)
        A /= np.linalg.norm(A)
        # the approach axis in the card points from the mouth to the seat (approach pos = seat - A*stroke)
        mouth = np.array(ap['pos'])
        if np.dot(seat - mouth, A) < 0:
            A = -A
        stroke = float(ap['stroke'])
        # the piece's long axis as it enters the mouth (his animation's frame there): the tilt test compares to this
        _, seat_ax = long_axis(pts(pc['model'], ap['from_frame']))
        piece, k = INHAND[gun]
        hc, hax = long_axis(pts('models/ammo_hand/%s.md3' % piece, 0))
        parts = {p['name']: p for p in card['parts']}
        for g in sorted(GATES[gun]):
            spec = GATES[gun][g]
            r = dict(id=rid, gun=gun, gate=g, args=args[g])
            if spec[0] == 'insert':
                r.update(kind=0, seat=seat, axis=A, len=stroke, inhand=hc, inaxis=hax, seataxis=seat_ax)
                report.append('%-11s gate%d insert  seat %s  axis %s  stroke %.2f  in-hand %s  axis %s  mouth axis %s'
                              % (gun, g, v(seat), v(A), stroke, v(hc), v(hax), v(seat_ax)))
            elif spec[0] == 'pull':
                need = RACKED * stroke
                r.update(kind=1, grab=seat, dir=-A, need=need, ret=0)
                report.append('%-11s gate%d pull    grab %s  dir %s  need %.2f (0.85 x stroke %.2f)'
                              % (gun, g, v(seat), v(-A), need, stroke))
            else:
                _, pname, sense, ret = spec
                p = parts[pname]
                D = np.array(p['axis'], float)
                D /= np.linalg.norm(D)
                rest = np.array(p['rest'])
                T = float(p['travel'])
                rot = p.get('rot') or 0
                frac = ROT_NEED if rot > 5 else RACKED
                grab = rest if sense > 0 else rest + D * T
                d = D if sense > 0 else -D
                r.update(kind=1, grab=grab, dir=d, need=frac * T, ret=1 if ret else 0)
                report.append('%-11s gate%d stroke  %s %s  grab %s  dir %s  need %.2f (%.2f x travel %.2f, rot %.1f)%s'
                              % (gun, g, pname, 'out' if sense > 0 else 'back', v(grab), v(d), frac * T, frac, T,
                                 rot, '  then return' if ret else ''))
            rows.append(r)
            gate_ids[(gun, g)] = rid
            rid += 1

    out = ['// GENERATED by sets/rusted_legacy/tools/gen_rsrl.py from the measured cards. Do not edit by hand.',
           '// Controller frame, cm (forward, left, up). Sources: see the tool header.',
           '// off-hand palm (models/hand/hand.md3 frame 1, front 10 cm, mesh): %s' % v(palm),
           '']
    for line in report:
        out.append('//   ' + line)
    out += ['', 'extend class RSRL_Reload', '{',
            '\tconst ROWS = %d;' % len(rows),
            '\tstatic Vector3 Palm() { return %s; }' % v(palm), '',
            '\tstatic RSRL_Row Row(int id)', '\t{', '\t\tlet r = new("RSRL_Row");', '\t\tr.id = id;',
            '\t\tswitch (id)', '\t\t{']
    for r in rows:
        out.append('\t\tcase %d:\t// %s gate %d -> setReloadStep(%s)' % (r['id'], r['gun'], r['gate'], r['args']))
        out.append('\t\t\tr.name = "%s %d";' % (r['gun'], r['gate']))
        out.append('\t\t\tr.kind = %d;' % r['kind'])
        if r['kind'] == 0:
            out.append('\t\t\tr.seat = %s; r.axis = %s; r.len = %.3f;' % (v(r['seat']), v(r['axis']), r['len']))
            out.append('\t\t\tr.inHand = %s; r.inAxis = %s; r.seatAxis = %s;'
                       % (v(r['inhand']), v(r['inaxis']), v(r['seataxis'])))
        else:
            out.append('\t\t\tr.grab = %s; r.dir = %s; r.need = %.3f; r.ret = %d;'
                       % (v(r['grab']), v(r['dir']), r['need'], r['ret']))
        out.append('\t\t\tbreak;')
    out += ['\t\tdefault:', '\t\t\treturn null;', '\t\t}', '\t\treturn r;', '\t}', '}', '']
    os.makedirs(os.path.join(SRC, 'zscript/rsrl'), exist_ok=True)
    open(os.path.join(SRC, 'zscript/rsrl/rsrl_table.zs'), 'w').write('\n'.join(out))

    # patch his gates (idempotent: an existing RSRL line is replaced)
    for gun in ORDER:
        fn = os.path.join(SRC, 'zscript/weapons/%s.txt' % FILES[gun])
        args_of = gate_args(gun)
        txt = open(fn, newline='').read()
        nl = '\r\n' if '\r\n' in txt else '\n'
        txt = re.sub(r'\r?\n\t\t// RSRL[^\r\n]*\r?\n\t\tif \(RSRL_Reload\.On[^\r\n]*', '', txt)

        def rep(m):
            g = int(m.group(1))
            rid = gate_ids[(gun, g)]
            c = ('\t\t// RSRL (RSQ Weapon Depot): measured hand reload, row %d; his touch test below runs '
                 'outside VR or with rsrl_handreload 0' % rid)
            i = ('\t\tif (RSRL_Reload.On(invoker)) { bool rsDone; Vector3 rsAt; [rsDone, rsAt] = RSRL_Reload.Gate(invoker, %d, '
                 '!invoker.ImmersiveAmmoGrab || invoker.owner.CountInv("grabbedAmmo") > 0); invoker.showWeaponMarker(rsAt); '
                 'if (rsDone) invoker.setReloadStep(%s); return; }' % (rid, args_of[g]))
            return m.group(0) + nl + c + nl + i
        txt = re.sub(r'action void A_CheckImmersiveReloadAction(\d+)\(\)\s*\{', rep, txt)
        open(fn, 'w', newline='').write(txt)
    print('\n'.join(report))
    print('palm', v(palm), ' rows', len(rows))


if __name__ == '__main__':
    main()
