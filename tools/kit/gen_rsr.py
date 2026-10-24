"""Generates the real-VR-reload data for each gun from its own mesh and the survey:
  zscript/rsr/rsr_guns.<set>.zs   per-gun geometry, hooks, sprites, sounds, items (one per set;
                            the pack ships it as zscript/rsr/rsr_guns.zs)
  MODELDEF.rsr.<set>        the gun's own model, re-keyed: gun without mag / handle parts,
                            mag only, handle only (main controller), mag in the off hand,
                            the dropped mag (world)
  rsr_geometry.json         the numbers, for the record
  rsr_files.json            the extra pack entries each set needs (clear skins, split meshes)
Every position: cm in the weapon controller's frame, F forward, L left, U up (rgeo.py).

To add a gun: one GUNS entry (its survey record gives the geometry), and its weapon-file
block in rsr_patch.py. vreload.zs does not change.

usage: gen_rsr.py <out dir>
"""
import sys, os, json
import numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rgeo import load_md3, shift_hook, to_flu

S = 'C:/Users/Command/Desktop/Quest_Weapons_Kit/kit/kit'
R = S + '/team/reload'
SURVEY = S + '/team/reload_survey/survey.json'
V8X = S + '/team/reload_survey/_v8x/models/bd/'      # the meshes RS_BD22_Models_v8.pk3 ships
VPM = '/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/models/weapons/hud/guns/'

# Ermac's off hand holding a magazine (ammo_hand frame 3 + mag_chaingun): his magazine's
# centre in the off-hand layer frame (tools/ermac_hold.py). Our magazine's grip point goes here.
PALM_MAG = np.array([-0.7, 3.9, -2.3])
# the middle of the closed hand (Ermac's ammo_hand / fist frames): what takes a handle
PALM_GRAB = np.array([-1.5, 2.0, -4.5])
VU = 34.0                      # vr_vunits_per_meter (world model scale)
CLEAR = 'rsr_clear.png'

BD_SCALE, BD_OFF = (-1.0, 1.0, 1.0), (0.0, 0.0, -5.0)

# One entry per gun. mesh: the file the pack ships (BD22: the v8 pack's frame-stripped
# meshes; their frame numbers are the pack's MODELDEF FrameIndex numbers).
#   mag_surfs / handle_surfs / bolt_surfs: surfaces (IQM: meshes) that are the magazine,
#     the handle or slide the hand pulls, the part that moves with it
#   handle_mode: 'layers' (handle surfaces on their own layers) | 'frames' (the gun's own
#     mesh frames by travel) | None (no handle: cells, drums)
#   charge: 'never' | 'token' (when the weapon file gives charge_token: the set's own rule)
#     | 'always' (as the set's canned reload)
#   grip: where the off hand holds the magazine: 'base' (halfway from the well mouth to the
#     survey's base point) | 'mesh' (halfway along the part below the mouth, the hand at
#     least 3 cm below the mouth: from the magazine's own vertices)
GUNS = [
    dict(key='BD22/Rifle', cls='Rifle', set='bd', mesh=V8X + 'Rifle/Rifle.md3',
         path='models/bd/Rifle', model='Rifle.md3', skin='Rifle.png', scale=BD_SCALE, off=BD_OFF,
         extra='\tNoInterpolation\n', ready_frame=3, mag_surfs=[3], handle_surfs=[0], bolt_surfs=[1],
         ready_sprites=['RIFG A', '2IFG A', 'RI2G A'],
         spr_gun='RQRM', spr_part='RQRP', spr_world='RQRW',
         handle_mode='layers', handle_part='charging_handle', bolt_part='bolt', grip='base',
         snd=dict(out='Rifle/Reload1', inn='Rifle/Reload2', back='Rifle/Bolt1', fwd='Rifle/Bolt2', land='weapons/largemagdrop'),
         back_at=0.5,             # BD plays Bolt1 as the handle starts back (2IFR I); Bolt2 on the way forward
         reserve='Clip2', magammo='RifleAmmo', nomag='HasUnloadedRifle', charge='token', charge_token='RifleReloadToken',
         reload_token='Reloading', chan=5),
    dict(key='V+/VR_Rifle', cls='VR_Rifle', set='vp', mesh=VPM + 'm16.md3',
         path='Models/Weapons/hud/guns', model='m16.md3', skin='WPN-M16.png', scale=(1.35, 1.35, 1.35), off=(0.0, 0.0, 0.0),
         extra='', ready_frame=0, mag_surfs=[3], handle_surfs=[], bolt_surfs=[], casing_surf=1,
         ready_sprites=['RIFL A'],
         spr_gun='RQVM', spr_part='RQVP', spr_world='RQVW',
         handle_mode='frames', handle_part='bolt', grip='base',
         # the gun's own frames with the bolt piece back (survey track): (travel cm, mesh frame)
         handle_frames=[(2.0, 35), (5.7, 36), (7.7, 37)],
         snd=dict(out='weapons/9mmclip1', inn='weapons/9mmclip2', back='weapons/9mmslide', fwd='', land=''),
         back_at=0.85,            # the set plays 9mmslide with the bolt at the back (RIFK L)
         reserve='Clip', magammo='VR_RifleLoaded', nomag='RSR_NoMag_VR_Rifle', charge='always', charge_token='',
         reload_token='', chan=0),
    # --- BD22, the rest of its magazine guns (rsr_patch.py BD_GUNS has their weapon blocks)
    dict(key='BD22/BrutalPistol', cls='BrutalPistol', set='bd', mesh=V8X + 'BrutalPistol/BrutalPistol.md3',
         path='models/bd/BrutalPistol', model='BrutalPistol.md3', skin='BrutalPistol.png', scale=BD_SCALE, off=BD_OFF,
         extra='\tNoInterpolation\n', ready_frame=3, mag_surfs=[3, 2], handle_surfs=[1], bolt_surfs=[],
         ready_sprites=['PIST E', 'PIST I'],
         spr_gun='RQPM', spr_part='RQPP', spr_world='RQPW',
         handle_mode='layers', handle_part='slide', grip='mesh',
         # the slide goes forward with pistol/slide2 (2ISR T, empty reload only); no sound going back
         snd=dict(out='Pistol/Reload1', inn='Pistol/Reload2', back='', fwd='pistol/slide2', land='weapons/smallmagdrop'),
         back_at=1.0, reserve='Clip1', magammo='BDPistolAmmo', nomag='HasUnloadedPistol', charge='token',
         charge_token='RSR_Charge', reload_token='Reloading', chan=5),
    dict(key='BD22/BrutalSMG', cls='BrutalSMG', set='bd', mesh=V8X + 'BrutalSMG/BrutalSMG.md3',
         path='models/bd/BrutalSMG', model='BrutalSMG.md3', skin='BrutalSMG.png', scale=BD_SCALE, off=BD_OFF,
         extra='\tNoInterpolation\n', ready_frame=3, mag_surfs=[3], handle_surfs=[0], bolt_surfs=[],
         ready_sprites=['SMGR A', 'SMGZ A'],
         spr_gun='RQBM', spr_part='RQBP', spr_world='RQBW',
         handle_mode='layers', handle_part='charging_handle', grip='mesh',
         # BD22 cocks the lever after every magazine (SMGR Y-]), silently: it has no sound for it
         snd=dict(out='SMG/Reload1', inn='SMG/Reload2', back='', fwd='', land='weapons/smallmagdrop'),
         back_at=1.0, reserve='Clip1', magammo='BDSMGAmmo', nomag='HasUnloadedSMG', charge='token',
         charge_token='RSR_Charge', reload_token='Reloading', chan=5),
    dict(key='BD22/MP40', cls='MP40', set='bd', mesh=V8X + 'MP40/MP40.md3',
         path='models/bd/MP40', model='MP40.md3', skin='MP40.png', scale=BD_SCALE, off=BD_OFF,
         extra='\tNoInterpolation\n', ready_frame=2, mag_surfs=[10], handle_surfs=[0], bolt_surfs=[],
         ready_sprites=['MP40 A'],
         spr_gun='RQMM', spr_part='RQMP', spr_world='RQMW',
         handle_mode='layers', handle_part='bolt_handle', grip='mesh',
         snd=dict(out='MP40/Reload1', inn='MP40/Reload2', back='MP40/Bolt1', fwd='MP40/Bolt2', land='weapons/smallmagdrop'),
         back_at=0.5,             # BD plays Bolt1 with the bolt half back (MP4R H, -8.6 of 17.1 cm)
         reserve='Mauser9mm', magammo='MP40Ammo', nomag='HasUnloadedMP40', charge='token',
         charge_token='MP40ReloadToken', reload_token='Reloading', chan=5),
    dict(key='BD22/AssaultShotgun', cls='AssaultShotgun', set='bd', mesh=V8X + 'AssaultShotgun/AssaultShotgun.md3',
         path='models/bd/AssaultShotgun', model='AssaultShotgun.md3', skin='AssaultShotgun.png', scale=BD_SCALE, off=BD_OFF,
         extra='\tNoInterpolation\n', ready_frame=4, mag_surfs=[6, 1], handle_surfs=[2], bolt_surfs=[],
         ready_sprites=['USAS A', '3SAR I'],
         spr_gun='RQAM', spr_part='RQAP', spr_world='RQAW',
         handle_mode='layers', handle_part='charging_handle', grip='mesh',
         # asg/bolt1 with the handle at the back (2SAR Q), asg/bolt2 as it runs home (2SAR O)
         snd=dict(out='ASG/Reload1', inn='ASG/Reload2', back='asg/bolt1', fwd='asg/bolt2', land='weapons/largemagdrop'),
         back_at=0.85, reserve='AmmoShell', magammo='AssaultShotgunAmmo', nomag='HasUnloadedASG', charge='token',
         charge_token='ASGReloadToken', reload_token='Reloading', chan=5),
    dict(key='BD22/RailGun', cls='RailGun', set='bd', mesh=V8X + 'RailGun/RailGun.md3',
         path='models/bd/RailGun', model='RailGun.md3', skin='RailGun.png', scale=BD_SCALE, off=BD_OFF,
         extra='\tNoInterpolation\n', ready_frame=3, mag_surfs=[4], handle_surfs=[], bolt_surfs=[],
         ready_sprites=['RAIL A', 'RAIL B', 'RAIL C', 'RAIL D'],
         spr_gun='RQLM', spr_part='RQLP', spr_world='RQLW',
         handle_mode=None, grip='mesh',
         snd=dict(out='Railgun/Reload1', inn='Railgun/Reload2', back='', fwd='', land='weapons/largemagdrop'),
         back_at=1.0, reserve='AmmoCell', magammo='RailgunAmmo', nomag='HasUnloadedRailgun', charge='never',
         charge_token='', reload_token='Reloading', chan=5),
    dict(key='BD22/Plasma_Gun', cls='Plasma_Gun', set='bd', mesh=V8X + 'Plasma_Gun/Plasma.md3',
         path='models/bd/Plasma_Gun', model='Plasma.md3', skin='Plasma.png', scale=BD_SCALE, off=BD_OFF,
         extra='\tNoInterpolation\n', ready_frame=4, mag_surfs=[1], handle_surfs=[], bolt_surfs=[],
         ready_sprites=['PRSG F', 'PRSG A', 'PRSG G', 'PRSG H', 'PRSG I'],
         spr_gun='RQZM', spr_part='RQZP', spr_world='RQZW',
         handle_mode=None, grip='mesh',
         snd=dict(out='Plasma/Reload1', inn='Plasma/Reload2', back='', fwd='', land='weapons/largemagdrop'),
         back_at=1.0, reserve='AmmoCell', magammo='PlasmaAmmo', nomag='HasUnloadedPlasma', charge='never',
         charge_token='', reload_token='Reloading', chan=5),
    dict(key='BD22/Sniper', cls='Sniper', set='bd', mesh=R + '/src/models/bd/HK416/hk416.iqm', ship_mesh='models/bd/HK416/hk416.iqm',
         path='models/bd/HK416', model='hk416.iqm',
         # the v8 pack's skins, mesh by mesh (mesh 0 is the hands it hides); 13-15 are the split parts
         skins=['nohands.png', 'SUP.bmp', 'Grip2.bmp', '1.bmp', '9.bmp', 'cock.bmp', 'marg-ris.bmp', 'f1.bmp', 'mag.bmp',
                'Magpul_Diffuse.bmp', 'eotech553.bmp', 'glass.png', 'anpaq.bmp', 'mag.bmp', 'Magpul_Diffuse.bmp', '1.bmp'],
         hidden_surfs=[0], scale=(-1.35, 1.35, 1.35), off=(6.499, -3.835, 10.913),
         extra='', ready_frame=25, mag_surfs=[13, 14], handle_surfs=[15], bolt_surfs=[],
         ready_sprites=['X21G A', 'P21G A'],
         spr_gun='RQKM', spr_part='RQKP', spr_world='RQKW',
         handle_mode='layers', handle_part='charging_handle', grip='mesh',
         snd=dict(out='Sniper/MagOut', inn='Sniper/MagIn', back='Sniper/BoltBack', fwd='Sniper/BoltForward', land='weapons/largemagdrop'),
         back_at=0.85,            # BoltBack with the handle at the back (X22R L)
         reserve='SniperAmmo', magammo='xm21Ammo', nomag='HasUnloadedSniper', charge='token',
         charge_token='SniperReloadToken', reload_token='Reloading', chan=5),
    dict(key='BD22/Rocket_Launcher', cls='Rocket_Launcher', set='bd', mesh=V8X + 'RPG/RPG.md3',
         path='models/bd/RPG', model='RPG.md3', skin='RPG.png', scale=BD_SCALE, off=BD_OFF,
         extra='\tNoInterpolation\n', ready_frame=5, mag_surfs=[5, 6, 7, 8, 9, 10, 11, 12], handle_surfs=[], bolt_surfs=[],
         ready_sprites=['MISG A', 'MISG J'],
         spr_gun='RQDM', spr_part='RQDP', spr_world='RQDW',
         handle_mode=None, mag_part='drum', grip='mesh',
         snd=dict(out='rocket/reload1', inn='rocket/reload2', back='', fwd='', land='weapons/barrelpain'),
         back_at=1.0, reserve='AmmoRocket', magammo='RocketRounds', nomag='HasUnloadedRL', charge='never',
         charge_token='', reload_token='Reloading', chan=5),
]

CHARGE_RULE = {'never': 0, 'token': 1, 'always': 2}


def survey():
    d = json.load(open(SURVEY))
    return {g['id']: g for g in d['guns']}


def v3(a):
    return '(%.3f, %.3f, %.3f)' % tuple(float(x) for x in a)


_iqm = {}


def raw_surfs(g):
    """per surface: (raw model-space vertices at the ready frame, triangles indexing them)"""
    if g['mesh'].lower().endswith('.iqm'):
        sys.path.insert(0, S + '/tool/hands')
        import gunview
        key = (g['mesh'], g['ready_frame'])
        if key not in _iqm:
            _iqm[key] = gunview.load_iqm(g['mesh'], g['ready_frame'], skip_meshes=())
        out = []
        for tris, pos in _iqm[key]:
            v = np.unique(tris)
            remap = {int(a): k for k, a in enumerate(v)}
            out.append((pos[v], np.vectorize(remap.get)(tris) if len(tris) else tris))
        return out
    m = load_md3(g['mesh'])
    return [(s['xyz'][g['ready_frame']], s['tris']) for s in m]


def compute(g, sv):
    s = sv[g['key']]
    mag = s['parts'][g.get('mag_part', 'magazine')]
    well = np.array(mag['well_point'], float)
    axis = np.array(mag['insert_dir'], float); axis /= np.linalg.norm(axis)
    mouth = float(mag['insert_depth_cm'])
    base = np.array(mag['base_point'], float)
    surfs = raw_surfs(g)
    g['nsurf'] = len(surfs)
    raw = np.concatenate([surfs[i][0] for i in g['mag_surfs']])
    mv = to_flu(raw, g['scale'], g['off'])               # the magazine, seated, gun frame cm
    mouth_pt = well - axis * mouth
    if g['grip'] == 'base':
        grip = (mouth_pt + base) / 2
    else:
        sa = (mv - well) @ axis
        below = mv[sa < -mouth]
        c = (below if len(below) > 8 else mv).mean(0)
        side = (c - well) - axis * np.dot(c - well, axis)
        sg = min((-mouth + sa.min()) / 2, -mouth - 3.0)
        grip = well + axis * sg + side
    shift = PALM_MAG - grip                         # into the off hand, orientation kept
    g['well'] = well; g['axis'] = axis; g['mouth'] = mouth; g['grip'] = grip; g['base'] = base
    g['mag_len'] = float(np.dot(well - base, axis))
    g['hand_hook'] = shift_hook(g['scale'], shift)
    g['top_in_hand'] = well + shift                 # the magazine's top in the off-hand frame
    g['well_hook'] = shift_hook(g['scale'], -axis)  # per cm out of the well
    if g.get('handle_part'):
        h = s['parts'][g['handle_part']]
        g['grab'] = np.array(h['grab_point'], float)
        pd = np.array(h['pull_dir'], float); g['pull'] = pd / np.linalg.norm(pd)
        g['travel'] = float(h['travel_cm'])
    else:
        g['grab'] = np.zeros(3); g['pull'] = np.array([-1.0, 0, 0]); g['travel'] = 0.0
    g['handle_hook'] = shift_hook(g['scale'], g['pull'])
    if g.get('bolt_part'):
        b = s['parts'][g['bolt_part']]
        g['bolt_ratio'] = float(b['travel_cm']) / g['travel']
    else:
        g['bolt_ratio'] = 0.0
    # world magazine: the mag's centre at the actor's origin
    c = raw.mean(0)
    sc = VU * 0.01 * 1.02 * abs(g['scale'][1])
    # world model axes are (forward, left, up) = md3 (x, y, z) * Scale; match the HUD's handedness
    hud = to_flu(np.eye(3), g['scale'], (0, 0, 0)) - to_flu(np.zeros((1, 3)), g['scale'], (0, 0, 0))
    sgn = np.sign(np.diag(hud))
    g['world_scale'] = (sc * sgn[0], sc * sgn[1], sc * sgn[2])
    g['world_off'] = (-sc * sgn[0] * c[0], -sc * sgn[1] * c[1], -sc * sgn[2] * c[2] / 1.2)
    g['mag_centre'] = mv.mean(0)
    return g


def skin_of(g, si):
    return g['skins'][si] if 'skins' in g else g['skin']


def modeldef(g):
    out = ['// RS real VR reload (zscript/rsr/vreload.zs, team/reload/tools/gen_rsr.py): %s.' % g['key'],
           '// The gun\'s own model and frames; pieces shown or hidden by a clear skin (HUD models',
           '// are alpha-tested at gl_mask_threshold, so a clear surface is not drawn).']
    always = set(g.get('hidden_surfs', []))

    def block(cls, keys, hide, comment, scale=None, off=None, flags=''):
        sc = scale or g['scale']
        of = off or g['off']
        # every surface gets its own skin: the md3 / IQM RenderFrame only reads SurfaceSkin
        # when the block has no Skin (models_md3.cpp, models_iqm.cpp)
        b = ['', '// ' + comment, 'Model %s' % cls, '{', '\tPath "%s"' % g['path'], '\tModel 0 "%s"' % g['model']]
        for si in range(g['nsurf']):
            # hidden_surfs keep the pack's own hiding skin (the HK416's hands: nohands.png)
            sk = skin_of(g, si) if si in always or si not in hide else CLEAR
            b.append('\tSurfaceSkin 0 %d "%s"' % (si, sk))
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
    cas = [g['casing_surf']] if 'casing_surf' in g else []
    rf = g['ready_frame']
    mags = g['mag_surfs']
    out += block(g['cls'], [(g['spr_gun'], 'A', rf)], mags + cas, 'the gun without its magazine (ready frame)')
    if g['handle_mode'] == 'layers':
        out += block(g['cls'], [(g['spr_gun'], 'B', rf)], g['handle_surfs'] + g['bolt_surfs'],
                     'the gun without its handle / slide (and what moves with it): they are on their own layers while pulled')
        out += block('RSR_GunParts', [(g['spr_part'], 'B', rf)], allbut(g['handle_surfs']), 'the handle / slide alone')
        if g['bolt_surfs']:
            out += block('RSR_GunParts', [(g['spr_part'], 'C', rf)], allbut(g['bolt_surfs']), 'the bolt carrier alone')
    elif g['handle_mode'] == 'frames':
        keys = [(g['spr_gun'], 'BCDEFG'[i], mf) for i, (t, mf) in enumerate(g['handle_frames'])]
        out += block(g['cls'], keys, cas, 'the gun\'s own frames with the bolt back (2.0 / 5.7 / 7.7 cm)')
    out += block('RSR_GunParts', [(g['spr_part'], 'A', rf)], allbut(mags), 'the magazine alone, at the gun (main controller)')
    out += block('RSQ_Hands', [(g['spr_part'], 'A', rf)], allbut(mags), 'the magazine alone, in the off hand (off controller)')
    out += block('RSR_DroppedMag', [(g['spr_world'], 'A', rf)], allbut(mags), 'the dropped magazine (world)',
                 scale=g['world_scale'], off=g['world_off'], flags='USEACTORPITCH\n\tUSEACTORROLL')
    return out


def zs(guns):
    L = ['// generated by team/reload/tools/gen_rsr.py -- do not edit by hand',
         '// Real VR reload: per gun. Positions cm in the weapon controller\'s frame (F, L, U);',
         '// hooks are ModifyBobLayer3D translations for the gun\'s own MODELDEF placement.',
         '', 'class RSR_Guns abstract', '{']
    L += ['\tclearscope static int Count() { return %d; }' % len(guns), '']
    L += ['\tclearscope static int Index(Weapon w)', '\t{', '\t\tif (!w)', '\t\t\treturn 0;', '\t\tName n = w.GetClassName();']
    for i, g in enumerate(guns, 1):
        L.append("\t\tif (n == '%s')\treturn %d;" % (g['cls'], i))
    L += ['\t\treturn 0;', '\t}', '']

    def table(name, typ, vals, fmt, note=''):
        if note:
            L.append('\t// ' + note)
        L.append('\tclearscope static %s %s(int i)' % (typ, name))
        L.append('\t{')
        L.append('\t\tswitch (i)')
        L.append('\t\t{')
        for i, v in enumerate(vals, 1):
            L.append('\t\tcase %d:\treturn %s;' % (i, fmt(v)))
        L.append('\t\t}')
        dflt = {'Vector3': '(0, 0, 0)', 'double': '0', 'int': '0', 'String': '""', 'Name': "'None'", 'bool': 'false'}[typ]
        L.append('\t\treturn %s;' % dflt)
        L.append('\t}')
        L.append('')

    st = lambda s: '"%s"' % s
    f2 = lambda x: '%.2f' % x
    table('Well', 'Vector3', [g['well'] for g in guns], v3, 'the magazine\'s top, seated')
    table('Axis', 'Vector3', [g['axis'] for g in guns], v3, 'the way a magazine goes in')
    table('Mouth', 'double', [g['mouth'] for g in guns], f2, 'seated -> the well\'s mouth, cm along the axis')
    table('MagLen', 'double', [g['mag_len'] for g in guns], f2)
    table('MagCentre', 'Vector3', [g['mag_centre'] for g in guns], v3)
    table('TopInHand', 'Vector3', [g['top_in_hand'] for g in guns], v3, 'the magazine\'s top, in the off-hand frame')
    table('HandHook', 'Vector3', [g['hand_hook'] for g in guns], v3, 'layer 2201')
    table('WellHook', 'Vector3', [g['well_hook'] for g in guns], v3, 'layer 2102, per cm out')
    table('HasHandle', 'bool', [g['handle_mode'] is not None for g in guns], lambda x: 'true' if x else 'false')
    table('Grab', 'Vector3', [g['grab'] for g in guns], v3, 'the handle / slide / bolt the hand takes')
    table('Pull', 'Vector3', [g['pull'] for g in guns], v3)
    table('Travel', 'double', [g['travel'] for g in guns], f2)
    table('HandleHook', 'Vector3', [g['handle_hook'] for g in guns], v3, 'layer 2103, per cm back')
    table('BoltRatio', 'double', [g['bolt_ratio'] for g in guns], lambda x: '%.3f' % x)
    table('HandleLayers', 'bool', [g['handle_mode'] == 'layers' for g in guns], lambda x: 'true' if x else 'false')
    table('ChargeRule', 'int', [CHARGE_RULE[g['charge']] for g in guns], lambda x: '%d' % x,
          'the handle after a magazine: 0 never, 1 when the weapon gave ChargeToken (the set\'s own rule), 2 always')
    table('BackAt', 'double', [g['back_at'] for g in guns], f2)
    table('Channel', 'int', [g['chan'] for g in guns], lambda x: '%d' % x, 'the set\'s own sound slot')
    table('Scale', 'Vector3', [g['scale'] for g in guns], v3)
    table('Offset', 'Vector3', [g['off'] for g in guns], v3, 'MODELDEF Offset x y, ZOffset')
    table('SprGun', 'Name', [g['spr_gun'] for g in guns], lambda s: "'%s'" % s)
    table('SprPart', 'Name', [g['spr_part'] for g in guns], lambda s: "'%s'" % s)
    table('SprWorld', 'Name', [g['spr_world'] for g in guns], lambda s: "'%s'" % s)
    table('ReadySprites', 'String', [' '.join(g['ready_sprites']) for g in guns], st)
    table('SndOut', 'String', [g['snd']['out'] for g in guns], st)
    table('SndIn', 'String', [g['snd']['inn'] for g in guns], st)
    table('SndBack', 'String', [g['snd']['back'] for g in guns], st)
    table('SndFwd', 'String', [g['snd']['fwd'] for g in guns], st)
    table('SndLand', 'String', [g['snd']['land'] for g in guns], st)
    table('Reserve', 'String', [g['reserve'] for g in guns], st)
    table('MagAmmo', 'String', [g['magammo'] for g in guns], st)
    table('NoMag', 'String', [g['nomag'] for g in guns], st)
    table('ChargeToken', 'String', [g['charge_token'] for g in guns], st)
    table('ReloadToken', 'String', [g['reload_token'] for g in guns], st, '\'\' = the engine\'s reload state')

    # V+ style: the gun's own frames for the handle, by travel
    L.append('\t// the gun\'s own frame (letter of SprGun) for a handle travel; 0 = its ready frame')
    L.append('\tclearscope static int HandleFrame(int i, double t)')
    L.append('\t{')
    framed = any(g['handle_mode'] == 'frames' for g in guns)
    if framed:
        L.append('\t\tswitch (i)')
        L.append('\t\t{')
    for i, g in enumerate(guns, 1):
        if g['handle_mode'] != 'frames':
            continue
        fr = g['handle_frames']
        L.append('\t\tcase %d:' % i)
        prev = 0.0
        for k, (t, mf) in enumerate(fr):
            L.append('\t\t\tif (t < %.2f) return %d;' % ((prev + t) / 2, k))
            prev = t
        L.append('\t\t\treturn %d;' % len(fr))
    if framed:
        L.append('\t\t}')
    L.append('\t\treturn 0;')
    L.append('\t}')
    L.append('}')
    L.append('')
    # every sprite name the reload shows (MODELDEF.rsr), so the engine knows them
    L.append('// every sprite the reload shows (MODELDEF.rsr), so the engine knows the names; never spawned')
    L.append('class RSR_GunSprites : Actor')
    L.append('{')
    L.append('\tStates')
    L.append('\t{')
    L.append('\tSpawn:')
    for g in guns:
        nparts = 'A' + ('B' if g['handle_mode'] == 'layers' else '') + ('C' if g['bolt_surfs'] else '')
        ngun = 'A' + ('B' if g['handle_mode'] == 'layers' else 'BCDEFG'[:len(g.get('handle_frames', []))] if g['handle_mode'] == 'frames' else '')
        L.append('\t\t%s %s 0;\t// %s' % (g['spr_gun'], ngun, g['key']))
        L.append('\t\t%s %s 0;' % (g['spr_part'], nparts))
        L.append('\t\t%s A 0;' % g['spr_world'])
    L.append('\t\tStop;')
    L.append('\t}')
    L.append('}')
    L.append('')
    L.append('// the rounds of a magazine that was dropped, held until a magazine is home (the sets top up,')
    L.append('// so nothing is lost and the reserve\'s cap cannot eat them)')
    for g in guns:
        L.append('class RSR_Held_%s : Inventory { Default { Inventory.MaxAmount 999; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }' % g['cls'])
    for g in guns:
        if g['nomag'].startswith('RSR_'):
            L.append('// "no magazine in the gun" for a set that has no such item of its own')
            L.append('class %s : RSVR_Token {}' % g['nomag'])
    return L


def main(out, only=None):
    sv = survey()
    guns = [compute(g, sv) for g in GUNS if not only or g['cls'] in only]
    names = [n for g in guns for n in (g['spr_gun'], g['spr_part'], g['spr_world'])]
    assert len(names) == len(set(names)), 'sprite names must be unique'
    os.makedirs(out + '/zscript/rsr', exist_ok=True)
    # one table per set: each pack gets only its own guns (build_proto.py ships it as zscript/rsr/rsr_guns.zs)
    for st in sorted({g['set'] for g in guns}):
        open(out + '/zscript/rsr/rsr_guns.%s.zs' % st, 'w').write('\n'.join(zs([g for g in guns if g['set'] == st])) + '\n')
    if os.path.exists(out + '/zscript/rsr/rsr_guns.zs'):
        os.remove(out + '/zscript/rsr/rsr_guns.zs')
    files = {}
    for st in sorted({g['set'] for g in guns}):
        lines = []
        extra = {}
        for g in guns:
            if g['set'] == st:
                lines += modeldef(g)
                extra[g['path'] + '/' + CLEAR] = out + '/' + CLEAR
                if g.get('ship_mesh'):
                    extra[g['ship_mesh']] = g['mesh']
        open(out + '/MODELDEF.rsr.' + st, 'w').write('\n'.join(lines) + '\n')
        files[st] = extra
    json.dump(files, open(out + '/rsr_files.json', 'w'), indent=1)
    rep = {g['key']: {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in g.items()
                      if k in ('well', 'axis', 'mouth', 'grip', 'mag_len', 'hand_hook', 'top_in_hand', 'well_hook', 'grab',
                               'pull', 'travel', 'handle_hook', 'bolt_ratio', 'world_scale', 'world_off', 'mag_centre')} for g in guns}
    json.dump(rep, open(out + '/rsr_geometry.json', 'w'), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == '__main__':
    # --only Cls,Cls: just those guns (the others' weapon files are then the set's own)
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
    main(sys.argv[1], only)
