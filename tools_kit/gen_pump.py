"""RSR-PUMP: the per-gun data for hand-loaded shells and a hand-worked pump (zscript/rsr/rsr_pump.zs),
from each gun's own md3, the reload survey and Ermac's shell hold. Writes:
  zscript/rsr/rsr_pump_guns.zs   per-gun geometry, hooks, sprites, sounds (both sets)
  MODELDEF.rsrpump.<set>         the gun's own model, re-keyed: the gun without its pump (and bolt),
                                 the pump / bolt / shell alone (main controller), the shell in the
                                 off hand, the dropped shell (world); V+ also its own ejected-shell frames
  MODELDEF.rsrpump.hands         Ermac's one-shell hold (ammo_hand frame 1) without his shell
  rsr_pump_geometry.json         the numbers, for the record
Every position: cm in the weapon controller's frame, F forward, L left, U up (rgeo.py).
No new mesh data: every block is the gun's own md3 (or Ermac's ammo_hand, already in the packs).

usage: gen_pump.py <out dir>
"""

# Emit ModelSwapper's Index() -- the slot from the DONOR MODEL in hand -- instead of a
# standalone pack's, where the slot comes from the weapon's own class. Default off: the
# vanilla / plus / modern Quest packs are untouched. The ModelSwapper runner sets it.
MODELSWAPPER = False

import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rgeo import load_md3, shift_hook, surf_flu, to_flu, solve_hook, pca

S = 'C:/Users/Command/Desktop/Quest_Weapons_Kit/kit/kit'
SURVEY = S + '/team/reload_survey/survey.json'
ERMAC = S + '/tool/vrmelee/models/rsq/'          # the packs' own copies (models/rsq), md5-identical to _assets_safe
HAND_SCALE, HAND_OFF = (-1.0, 1.0, 1.0), (0.0, -24.0, -10.0)   # Ermac's off-hand block (MODELDEF.rsq)
SHELL_POSE = 1          # ammo_hand frame 1: Ermac's one-shell hold (frame 2 holds two, 0 a pistol magazine)
VU = 34.0
CHAN_AUTO, CHAN_WEAPON = 0, 1

PUMPS = [
    dict(key='BD22/Shot_Gun', cls='Shot_Gun', set='bd',
         mesh=S + '/team/reload_survey/_v8x/models/bd/ShotGun/Shotgun.md3',
         path='models/bd/ShotGun', model='Shotgun.md3', skin='Shotgun.png', scale=(-1.0, 1.0, 1.0), off=(0.0, 0.0, -5.0),
         extra='\tNoInterpolation\n', ready_frame=4, pump_surfs=[4], bolt_surfs=[5], shell_surf=2,
         shell_frame=4,          # parked in the receiver, lying along the tube (crimp forward, +F)
         lead=(1.0, 0.0, 0.0),   # the shell's crimp end at shell_frame: it goes into the tube first
         depth=6.0,              # pushed this far past the port it is all in the tube (its length is 5.8)
         ready_sprite='SHTN A', spr_gun='RQUG', spr_part='RQUP', spr_world='RQUW',
         waits='RSP_LoadWait RSP_P1Wait RSP_P2Wait RSP_P3Wait RSP_Kick',
         snd=dict(shell=('Shotgun/Reload', 5), back=('Shotgun/Pump1', 5), fwd=('Shotgun/Pump2', 5), land='weapons/shell'),
         reserve='AmmoShell', magammo='ShotgunAmmo', eject_frames=[]),
    dict(key='V+/VR_Shotgun', cls='VR_Shotgun', set='vp',
         mesh='/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/models/weapons/hud/guns/shotgun.md3',
         path='Models/Weapons/Hud/guns', model='shotgun.md3', skin='WPN-GUNS.png', scale=(1.35, 1.35, 1.35), off=(0.0, 0.0, 0.0),
         extra='', ready_frame=0, pump_surfs=[1], bolt_surfs=[], shell_surf=2,
         shell_frame=12,         # the set's own frame with the shell at the (ejection) port; collapsed at rest
         lead=None,              # its long axis, the way it goes in
         depth=1.5,              # a little in and it is through the port (further, it shows through the far wall)
         ready_sprite='SHTG A', spr_gun='RQUH', spr_part='RQUQ', spr_world='RQUX',
         waits='RSP_LoadWait RSP_PWait',
         # the set's own: Shotgun/Reload (CHAN_AUTO) per shell, shotpump (CHAN_WEAPON) for the pump; no second pump sound
         snd=dict(shell=('Shotgun/Reload', CHAN_AUTO), back=('shotpump', CHAN_WEAPON), fwd=('', 0), land=''),
         reserve='VR_Shell', magammo='VR_ShotLoaded',
         eject_frames=[12, 13, 14, 15, 16, 17]),   # the set's own ejected shell (Fire, SHTG M-R)
]


def survey():
    d = json.load(open(SURVEY))
    return {g['id']: g for g in d['guns']}


def v3(a):
    return '(%.3f, %.3f, %.3f)' % tuple(float(x) for x in a)


def unit(v):
    v = np.array(v, float)
    return v / np.linalg.norm(v)


def rot_between(a, b):
    """the smallest rotation taking unit a to unit b (FLU, column form)"""
    a, b = unit(a), unit(b)
    v = np.cross(a, b); c = float(np.dot(a, b)); s = np.linalg.norm(v)
    if s < 1e-9:
        return np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K * ((1 - c) / (s * s))


def mid(p, a):
    """the middle of a shell along its axis (the vertex mean leans to the detailed brass end)"""
    c = p.mean(0); t = (p - c) @ a
    return c + a * ((t.max() + t.min()) / 2)


def compute(g, sv):
    s = sv[g['key']]
    m = load_md3(g['mesh'])
    sc, of = g['scale'], g['off']
    g['nsurf'] = len(m)
    # the pump
    pp = s['parts']['pump']
    g['grab'] = np.array(pp['grab_point'], float)
    g['pull'] = unit(pp['pull_dir'])
    g['travel'] = float(pp['travel_cm'])
    g['pump_hook'] = shift_hook(sc, g['pull'])                    # layer per cm back
    g['support_hook'] = shift_hook(HAND_SCALE, g['pull'])         # the support hand (rsq/hands.zs) per cm back
    g['bolt_ratio'] = 0.0
    if g['bolt_surfs']:
        b = s['parts']['bolt']
        g['bolt_ratio'] = float(b['travel_cm']) / g['travel']
    # the shell at the port: the shell surface at shell_frame, moved so its vertex mean is the
    # survey's port point (the gun's ready pose), then along the port's direction
    sh = s['parts']['shell']
    port = np.array(sh['port_centroid'], float)
    push = unit(sh.get('push_dir') or sh['approach_dir'])
    if g['set'] == 'vp':
        push = unit(sh['approach_dir'])            # V+: the set's own way in (f13 -> f12), the brief's (0.892, 0.429, -0.14)
    shp = surf_flu(m, g['shell_surf'], g['shell_frame'], sc, of)
    ref = shp.mean(0)
    lead = unit(g['lead']) if g['lead'] else pca(shp)[1][0]
    if np.dot(lead, push) < 0:
        lead = -lead
    g['port'] = port; g['push'] = push; g['shell_ref'] = ref; g['lead_v'] = lead
    g['port_hook'] = shift_hook(sc, port - ref)
    g['push_hook'] = shift_hook(sc, push)
    g['shell_len'] = float(np.ptp(shp @ lead))
    # the shell in the off hand: where Ermac's shell sits in his one-shell hold, its crimp end
    # out between thumb and index (his shell's narrower end), ours turned to match
    es = load_md3(ERMAC + 'shot_shell.md3')
    ep = to_flu(es[0]['xyz'][0], HAND_SCALE, HAND_OFF)
    ec, evt, _ = pca(ep)
    ea = evt[0]
    t = (ep - ep.mean(0)) @ ea
    hi = t > (t.max() + t.min()) / 2
    r_hi = np.linalg.norm((ep[hi] - ep.mean(0)) - np.outer(t[hi], ea), axis=1).max()
    r_lo = np.linalg.norm((ep[~hi] - ep.mean(0)) - np.outer(t[~hi], ea), axis=1).max()
    if r_hi > r_lo:            # the rim (wider) is the brass end: point ea at the crimp
        ea = -ea
    e_mid = mid(ep, ea)
    R = rot_between(lead, ea)
    c_from = mid(shp, lead)
    h, ypr = solve_hook(sc, of, R, c_from, e_mid)
    g['hand_hook'] = h; g['hand_rot'] = np.array(ypr)
    chk = to_flu(m[g['shell_surf']]['xyz'][g['shell_frame']], sc, of, hook=h, ypr=ypr)
    got_mid = mid(chk, ea)
    assert np.linalg.norm(got_mid - e_mid) < 0.05, ('hand hook', got_mid, e_mid)
    g['shell_in_hand'] = chk.mean(0)              # our reference point (vertex mean), off-hand frame
    g['axis_in_hand'] = ea
    assert np.linalg.norm((R @ (ref - c_from) + e_mid) - g['shell_in_hand']) < 0.05
    g['ermac_mid'] = e_mid
    # the dropped shell (world): its vertex mean at the actor's origin
    c = m[g['shell_surf']]['xyz'][g['shell_frame']].mean(0)
    wsc = VU * 0.01 * 1.02 * abs(sc[1])
    hud = to_flu(np.eye(3), sc, (0, 0, 0)) - to_flu(np.zeros((1, 3)), sc, (0, 0, 0))
    sgn = np.sign(np.diag(hud))
    g['world_scale'] = (wsc * sgn[0], wsc * sgn[1], wsc * sgn[2])
    g['world_off'] = (-wsc * sgn[0] * c[0], -wsc * sgn[1] * c[1], -wsc * sgn[2] * c[2] / 1.2)
    # V+: its own ejected shell, frame by frame, put on the gun as it is in the ready pose (the
    # fire animation moves the whole gun a little: take the body's own move out of each frame)
    g['eject_hooks'] = []
    if g['eject_frames']:
        body0 = surf_flu(m, 0, g['ready_frame'], sc, of)
        for f in g['eject_frames']:
            bf = surf_flu(m, 0, f, sc, of)
            Rr, tt = rigid(bf, body0)
            sc_f = surf_flu(m, g['shell_surf'], f, sc, of).mean(0)
            moved = Rr @ sc_f + tt
            g['eject_hooks'].append(shift_hook(sc, moved - sc_f))
    return g


def rigid(A, B):
    """R, t with R A + t ~ B (Kabsch)"""
    ca, cb = A.mean(0), B.mean(0)
    H = (A - ca).T @ (B - cb)
    U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1, 1, d])
    R = Vt.T @ D @ U.T
    return R, cb - R @ ca


def modeldef(g):
    clear = 'rsr_clear.png'
    out = ['// RSR-PUMP (zscript/rsr/rsr_pump.zs, tools/gen_pump.py): %s. The gun\'s own model and' % g['key'],
           '// frames; pieces shown or hidden by a clear skin (every surface has its own SurfaceSkin:',
           '// models_md3.cpp reads SurfaceSkin only when a block has no Skin).']

    def block(cls, keys, hide, comment, scale=None, off=None, flags=''):
        sc = scale or g['scale']
        of = off or g['off']
        b = ['', '// ' + comment, 'Model %s' % cls, '{', '\tPath "%s"' % g['path'], '\tModel 0 "%s"' % g['model']]
        for si in range(g['nsurf']):
            b.append('\tSurfaceSkin 0 %d "%s"' % (si, clear if si in hide else g['skin']))
        b += ['\tScale %.4f %.4f %.4f' % tuple(sc), '\tOffset %.4f %.4f 0.0' % (of[0], of[1]), '\tZOffset %.4f' % of[2]]
        if g['extra'] and scale is None:
            b.append(g['extra'].rstrip('\n'))
        if flags:
            b.append('\t' + flags)
        for spr, fr, mf in keys:
            b.append('\tFrameIndex %s %s 0 %d' % (spr, fr, mf))
        b.append('}')
        return b

    n = g['nsurf']
    allbut = lambda keep: [i for i in range(n) if i not in keep]
    rf = g['ready_frame']
    sp = g['spr_part']
    out += block(g['cls'], [(g['spr_gun'], 'A', rf)], g['pump_surfs'] + g['bolt_surfs'],
                 'the gun without its pump%s (they are on their own layers while the hand works it)' % (' and bolt' if g['bolt_surfs'] else ''))
    out += block('RSR_GunParts', [(sp, 'A', rf)], allbut(g['pump_surfs']), 'the pump alone (main controller)')
    if g['bolt_surfs']:
        out += block('RSR_GunParts', [(sp, 'B', rf)], allbut(g['bolt_surfs']), 'the bolt alone: it moves with the pump')
    keys = [(sp, 'C', g['shell_frame'])] + [(sp, 'DEFGHI'[k], f) for k, f in enumerate(g['eject_frames'])]
    out += block('RSR_GunParts', keys, allbut([g['shell_surf']]),
                 'the shell alone, at the loading port%s' % (' (D-I: the set\'s own ejected shell, Fire M-R)' if g['eject_frames'] else ''))
    out += block('RSQ_Hands', [(sp, 'C', g['shell_frame'])], allbut([g['shell_surf']]), 'the shell alone, in the off hand (off controller)')
    out += block('RSP_DroppedShell', [(g['spr_world'], 'A', g['shell_frame'])], allbut([g['shell_surf']]), 'a dropped shell (world)',
                 scale=g['world_scale'], off=g['world_off'], flags='USEACTORPITCH\n\tUSEACTORROLL')
    return out


HANDS_MODELDEF = '''
// RSR-PUMP: Ermac's one-shell hold (ammo_hand frame %d) without his shell: the gun's own shell is
// drawn in it on layer 2210 (rsr/rsr_pump.zs). ammo_hand.md3 is already in the packs (models/rsq).
Model RSQ_Hands
{
	Path "models/rsq"
	Model 0 "ammo_hand.md3"
	Skin 0 "hand.png"
	Scale -1.0 1.0 1.0
	Offset 0.0 -24.0 -10.0
	FrameIndex RQUN A 0 %d
}

// MS 1.5 (2026-10-31): the same hold WITH Ermac's own shell (shot_shell.md3, modelled in his hand's space), for a
// pump gun whose mesh has no shell of its own (RSP_Guns.OwnShell false): the hand still shows a round
Model RSQ_Hands
{
	Path "models/rsq"
	Model 0 "ammo_hand.md3"
	Skin 0 "hand.png"
	Model 1 "shot_shell.md3"
	Skin 1 "shells.png"
	Scale -1.0 1.0 1.0
	Offset 0.0 -24.0 -10.0
	FrameIndex RQUN B 0 %d
	FrameIndex RQUN B 1 0
}
''' % (SHELL_POSE, SHELL_POSE, SHELL_POSE)


def zs(guns):
    L = ['// generated by tools/gen_pump.py (RSR-PUMP) -- do not edit by hand',
         '// Hand-loaded shells and a hand-worked pump: per gun. Positions cm in the weapon controller\'s',
         '// frame (F, L, U); hooks are ModifyBobLayer3D translations for the gun\'s own MODELDEF placement.',
         '', 'class RSP_Guns abstract', '{']
    # WHICH GUN IS IN YOUR HANDS, and how that question is answered.
    #
    # A standalone pack's weapon IS the gun, so the slot comes from the weapon's own
    # class. ModelSwapper's does not: the weapon belongs to whatever mod is loaded and
    # only its MODEL is ours, so the slot comes from the DONOR MODEL WORN BY THAT HAND.
    # That is the whole reason its reload works on a mod nobody has written yet.
    #
    # MODELSWAPPER is default-off, so every standalone set emits what it always did.
    if MODELSWAPPER:
        L += ['\tclearscope static int Index(Weapon w)', '\t{', '\t\tif (!w)', '\t\t\treturn 0;',
              '\t\treturn SlotForDonor(DonorInHand(HandOf(w)));', '\t}', '',
              '\tclearscope static int HandOf(Weapon w)', '\t{',
              '\t\treturn 0;\t\t// the gun hand; the off hand is 1 when dual wielding lands',
              '\t}', '',
              '\t// The donor model worn by this hand, as RS_ForeignModelHandler published it.',
              '\t//',
              '\t// NOT ServiceIterator. Service.GetString is `play`; this function is `clearscope`,',
              '\t// because the pump module calls Index() from Places() / Place(), which the engine',
              '\t// reaches through Weapon.ModifyBobLayer3D -- declared `virtual ui`; and the facts',
              '\t// themselves live on a StaticEventHandler, which is `native play`. Three scopes,',
              '\t// none able to reach the others, and no Service variant bridges them.',
              '\t//',
              '\t// `struct CVar native` carries no scope qualifier at all, so FindCVar / GetString',
              '\t// are callable from every one of the three. Empty when no model is worn, which',
              '\t// SlotForDonor answers with 0 -- the stock reload -- so this is inert on a weapon',
              '\t// that has none of our models on it.',
              '\tclearscope static string DonorInHand(int hand)', '\t{',
              "\t\tlet cv = CVar.FindCVar(hand == 1 ? 'ms_donor_off' : 'ms_donor_main');",
              '\t\treturn cv ? cv.GetString() : "";', '\t}', '',
              '\tclearscope static int SlotForDonor(string donor)', '\t{',
              '\t\tif (donor.Length() == 0)', '\t\t\treturn 0;']
        for i, g in enumerate(guns, 1):
            L.append('\t\tif (donor == "%s")\treturn %d;' % (g['cls'], i))
        L += ['\t\treturn 0;', '\t}', '']
    else:
        L += ['\tclearscope static int Index(Weapon w)', '\t{', '\t\tif (!w)', '\t\t\treturn 0;', '\t\tName n = w.GetClassName();']
        for i, g in enumerate(guns, 1):
            L.append("\t\tif (n == '%s')\treturn %d;" % (g['cls'], i))
        L += ['\t\treturn 0;', '\t}', '']

    def table(name, typ, vals, fmt, args='int i', key='i'):
        L.append('\tclearscope static %s %s(%s)' % (typ, name, args))
        L.append('\t{')
        L.append('\t\tswitch (%s)' % key)
        L.append('\t\t{')
        for i, v in enumerate(vals, 1):
            L.append('\t\tcase %d:\treturn %s;' % (i, fmt(v)))
        L.append('\t\t}')
        dflt = {'Vector3': '(0, 0, 0)', 'double': '0', 'int': '0', 'String': '""', 'Name': "'None'", 'bool': 'false'}[typ]
        L.append('\t\treturn %s;' % dflt)
        L.append('\t}')
        L.append('')

    st = lambda s: '"%s"' % s
    f2 = lambda x: '%.3f' % x
    table('Grab', 'Vector3', [g['grab'] for g in guns], v3)              # the pump, forward (its centre)
    table('Pull', 'Vector3', [g['pull'] for g in guns], v3)              # the way it goes back
    table('Travel', 'double', [g['travel'] for g in guns], f2)
    table('PumpHook', 'Vector3', [g['pump_hook'] for g in guns], v3)     # layer 2120, per cm back
    table('BoltRatio', 'double', [g['bolt_ratio'] for g in guns], f2)    # layer 2121 (0: none)
    table('SupportHook', 'Vector3', [g['support_hook'] for g in guns], v3)   # rsq/hands.zs support hand, per cm back
    table('Port', 'Vector3', [g['port'] for g in guns], v3)              # the shell (vertex mean) at the loading port
    table('Push', 'Vector3', [g['push'] for g in guns], v3)              # the way it goes in
    table('Depth', 'double', [g['depth'] for g in guns], f2)             # past the port this far: home
    table('PortHook', 'Vector3', [g['port_hook'] for g in guns], v3)     # layer 2122: the shell at the port
    table('ShellInHand', 'Vector3', [g['shell_in_hand'] for g in guns], v3)  # off-hand frame
    table('AxisInHand', 'Vector3', [g['axis_in_hand'] for g in guns], v3)    # its crimp end, off-hand frame
    table('HandHook', 'Vector3', [g['hand_hook'] for g in guns], v3)     # layer 2210
    table('HandRot', 'Vector3', [g['hand_rot'] for g in guns], v3)
    table('Scale', 'Vector3', [g['scale'] for g in guns], v3)
    table('Offset', 'Vector3', [g['off'] for g in guns], v3)
    table('SprGun', 'Name', [g['spr_gun'] for g in guns], lambda s: "'%s'" % s)
    table('SprPart', 'Name', [g['spr_part'] for g in guns], lambda s: "'%s'" % s)
    table('SprWorld', 'Name', [g['spr_world'] for g in guns], lambda s: "'%s'" % s)
    table('ReadySprite', 'String', [g['ready_sprite'] for g in guns], st)
    table('WaitLabels', 'String', [g['waits'] for g in guns], st)       # the weapon's own wait loops (rsr_pump_patch.py)
    table('SndShell', 'String', [g['snd']['shell'][0] for g in guns], st)
    table('ChanShell', 'int', [g['snd']['shell'][1] for g in guns], lambda x: '%d' % x)
    table('SndBack', 'String', [g['snd']['back'][0] for g in guns], st)
    table('ChanBack', 'int', [g['snd']['back'][1] for g in guns], lambda x: '%d' % x)
    table('SndFwd', 'String', [g['snd']['fwd'][0] for g in guns], st)
    table('ChanFwd', 'int', [g['snd']['fwd'][1] for g in guns], lambda x: '%d' % x)
    table('SndLand', 'String', [g['snd']['land'] for g in guns], st)
    table('Reserve', 'String', [g['reserve'] for g in guns], st)
    # THE NAMES THE MODULE ACTUALLY CALLS. rsr_pump.zs (1.96b) asks for RSP_Guns.Loaded(i)
    # and RSP_Guns.Cap(i) -- it calls MagAmmo zero times. This generator was written against
    # an older rsr_pump.zs that used MagAmmo and had no tube capacity, so the pack it built
    # could never compile against the runtime it ships beside:
    #     rsr_pump.zs:369  Unknown function loaded
    #     rsr_pump.zs:370  Unknown function cap
    # and both results are assigned to locals, so two missing functions cascaded into
    # twelve errors. Loaded is the same string MagAmmo carried; Cap is the tube's capacity,
    # which the gun's own card already states.
    table('Loaded', 'String', [g['magammo'] for g in guns], st)
    table('Cap', 'int', [int(g.get('cap', 0)) for g in guns], lambda x: '%d' % x)
    table('OwnShell', 'bool', [g.get('own_shell', True) for g in guns], lambda x: 'true' if x else 'false')   # MS 1.5: false = no shell in the mesh (Ermac's shown)
    table('EjectFrames', 'int', [len(g['eject_frames']) for g in guns], lambda x: '%d' % x)
    L.append('\t// the set\'s own ejected shell, frame k (V+): its place on the gun in the ready pose')
    L.append('\tclearscope static Vector3 EjectHook(int i, int k)')
    L.append('\t{')
    for i, g in enumerate(guns, 1):
        for k, h in enumerate(g['eject_hooks']):
            L.append('\t\tif (i == %d && k == %d)\treturn %s;' % (i, k, v3(h)))
    L.append('\t\treturn (0, 0, 0);')
    L.append('\t}')
    L.append('}')
    return L


def main(out):
    sv = survey()
    guns = [compute(g, sv) for g in PUMPS]
    os.makedirs(out + '/zscript/rsr', exist_ok=True)
    open(out + '/zscript/rsr/rsr_pump_guns.zs', 'w').write('\n'.join(zs(guns)) + '\n')
    for st in ('bd', 'vp'):
        lines = []
        for g in guns:
            if g['set'] == st:
                lines += modeldef(g)
        open(out + '/MODELDEF.rsrpump.' + st, 'w').write('\n'.join(lines) + '\n')
    open(out + '/MODELDEF.rsrpump.hands', 'w').write(HANDS_MODELDEF)
    keys = ('grab', 'pull', 'travel', 'pump_hook', 'bolt_ratio', 'support_hook', 'port', 'push', 'depth', 'shell_ref', 'lead_v',
            'shell_len', 'port_hook', 'push_hook', 'shell_in_hand', 'axis_in_hand', 'ermac_mid', 'hand_hook', 'hand_rot',
            'world_scale', 'world_off', 'eject_hooks')
    conv = lambda v: [x.tolist() if isinstance(x, np.ndarray) else x for x in v] if isinstance(v, list) else (v.tolist() if isinstance(v, np.ndarray) else v)
    rep = {g['key']: {k: conv(g[k]) for k in keys} for g in guns}
    json.dump(rep, open(out + '/rsr_pump_geometry.json', 'w'), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
