"""TEST ONLY (rig, never ships): the revolvers and the Revolver's rounds on the Depot's QZD 17.3 rig.

python3 rig_rev.py <pack.pk3> <outdir>
Load order doom2 -> brutal22test6 -> BD_VoxelPack -> pack (+ the rig's probe). Run it under
`flock -o -x $RSQ_RIGLOCK`. Jobs (each one engine run, logs in <outdir>/logs):
  roster : idkfa, then which revolvers the player holds (printinv); give / summon Revolver2 (gone)
  cap    : Revolver + 100 rounds (cap 36); a second Revolver picked up off the floor (dual.zs gives the off-hand
           copy: cap 72); 100 more; then a backpack (cap stays 72)
  spawn  : MAP01/03/07/11 with rsq_moonlight_pistol 0 and then 1: the map's Clip2 and the rounds put beside them
  combos : a new game (map map01) for each of Moonlight Replaces Pistol x Start With Two: the weapons, cylinders
           and the RevolverRounds cap (printinv), the counts
  drops  : with Moonlight Replaces Pistol 0 and 1: 10 PistolSpawner summoned (a map pistol), 5 PistolZombie summoned
           and killed (their PistolDrop flies and lands as a PistolSpawner), then what is in the world
  slug   : the Shotvolver (BD22 Revolver) with rsa_rev_slug 1: alt fire, then fire; the test-only slugprobe.pk3
           (tools/moonammo/slugprobe) counts the bullets' puffs per tic: the slug is one bullet, the shell 35
  menu   : the BD22 VR WEAPONS menu opened, frames dumped
  dual   : one Moonlight, a second picked up, the Dual key: both held; fire main, off, both; flick the off hand,
           then the main hand (reloads); printinv after each; frames dumped
  frame  : MAP07, the player warped onto open floor by one of its bullet pickups (-1090 -1138, where a run put
           rounds), facing west; a RevolverRounds summoned 56 units ahead; frames dumped
"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '../../../../tools'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, re, sys, glob, shutil, subprocess
PK3, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
JOBS = sys.argv[3].split(',') if len(sys.argv) > 3 else ['roster', 'cap', 'spawn', 'frame']
RIGD = os.environ.get('RIGD', _DP.RIG)
os.makedirs(OUT + '/build', exist_ok=True)
shutil.copy(RIGD + '/build/probe.pk3', OUT + '/build/probe.pk3')
os.environ.update(B22_IWAD=(_DP.GAMEDATA + '/doom2.wad'), B22_BD22=(_DP.GAMEDATA + '/brutal22test6.pk3'),
                  B22_VOX=(_DP.GAMEDATA + '/BD_VoxelPack.pk3'), B22_PK3=PK3, B22_BUILD=OUT + '/build')
sys.path.insert(0, RIGD)
import rig

PRE = 'wait 100; god; notarget; screenblocks 12; crosshair 0; rsq_extra_weapons 1; rsr_debug 1; '


def errs(t):
    return [l for l in t.splitlines() if re.search(r'Script error|VM abort|exception|Execution could not continue', l, re.I)
            and 'voxeldef' not in l.lower()]


def show(tag, t, pat):
    print('=== %s' % tag)
    for l in t.splitlines():
        if re.search(pat, l):
            print('   ', l.strip())
    e = errs(t)
    print('    script errors (not BD_VoxelPack voxeldef):', e[:8] or 'none')


def restore_ini():
    subprocess.run(['git', '-C', RIGD, 'checkout', '--', 'bin/config/qzdoom.ini'], check=False)


if 'roster' in JOBS:
    s = PRE + ('take BrutalRevolver; take Revolver; idkfa; wait 20; echo REV PRINTINV; printinv; wait 5; '
               'echo REV GIVE_REVOLVER2; give Revolver2; wait 5; echo REV SUMMON_REVOLVER2; summon Revolver2; wait 5; '
               'echo REV GIVE_SLUGCVAR; rsq_slug_replaces_shotvolver; wait 5; echo REV END; quit')
    rc, t = rig.run('rev_roster', s, 200); restore_ini()
    show('roster rc %d' % rc, t, r'REV |[Rr]evolver|Shotvolver|[Uu]nknown|rsq_slug')

if 'cap' in JOBS:
    # the second Revolver: summon puts it 56 units ahead of the player; the rig's player walks with the left
    # stick (qz_lstick; +forward does not move it), and a pickup needs the walk (a warp onto it touches nothing)
    s = PRE + ('take RevolverRounds 999; give BrutalRevolver; wait 5; give RevolverRounds 100; wait 3; echo REV ONE_GUN; printinv; '
               'summon BrutalRevolver; wait 3; qz_lstick "0 1"; wait 15; qz_lstick "0 0"; wait 5; echo REV AFTER_SECOND; '
               'give RevolverRounds 100; wait 3; echo REV TWO_GUNS; printinv; '
               'give Backpack; wait 3; give RevolverRounds 100; wait 3; echo REV BACKPACK; printinv; echo REV END; quit')
    rc, t = rig.run('rev_cap', s, 200); restore_ini()
    show('cap rc %d' % rc, t, r'REV |RSQ moon|RevolverRounds|BrutalRevolver|Backpack|AmmoSuply')

if 'spawn' in JOBS:
    s = PRE + ''.join('rsq_moonlight_pistol %d; echo REV MOONLIGHT_PISTOL %d; map map01; wait 40; map map03; wait 40; map map07; wait 40; map map11; wait 40; ' % (m, m)
                      for m in (0, 1)) + 'rsq_moonlight_pistol 0; echo REV END; quit'
    rc, t = rig.run('rev_spawn', s, 200); restore_ini()
    show('spawn rc %d' % rc, t, r'REV |RSQ moon')

if 'frame' in JOBS:
    fr = OUT + '/frames_pickup'
    shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
    os.environ.update(QZ_RES='480', QZ_DUMP_EVERY='10', QZ_DUMP_DIR=fr)
    s = PRE + ('map map07; wait 20; warp -1010 -1138; qz_hmd "0 1.6 0 -35 0 0"; qz_rhand "0.4 0.6 0.4 30 0 0"; qz_lhand "-0.4 0.6 0.4 30 0 0"; '
               'summon RevolverRounds; wait 60; echo REV SHOT; wait 30; echo REV END; quit')
    rc, t = rig.run('rev_frame', s, 200); restore_ini()
    for k in ('QZ_DUMP_EVERY', 'QZ_DUMP_DIR'):
        os.environ.pop(k)
    show('frame rc %d' % rc, t, r'REV ')
    print('    frames:', len(glob.glob(fr + '/*')), fr)

if 'combos' in JOBS:
    # the rig's ini plays the Rifle class (starts with the Rifle); the pistol start is BD22's Pistol class (Doomer2)
    s = PRE + 'playerclass "$TAGBD_CLASS_PISTOL"; ' + ''.join('rsq_moonlight_pistol %d; rsq_moonlight_two %d; map map01; wait 120; echo REV COMBO pistol %d two %d; printinv; '
                      'netevent rsq_moon_count; wait 5; ' % (a, b, a, b) for a, b in ((0, 0), (0, 1), (1, 0), (1, 1)))
    s += 'rsq_moonlight_pistol 0; rsq_moonlight_two 0; playerclass "$TAGBD_CLASS_RIFLE"; quit'
    rc, t = rig.run('rev_combos', s, 300); restore_ini()
    log = OUT + '/build/logs/rev_combos.log'
    show('combos rc %d (from %s)' % (rc, log), open(log, errors='replace').read(),
         r'REV COMBO|RSQ moon|BrutalPistol|RSQ_Off_BrutalPistol|BrutalRevolver|RSQ_Off_BrutalRevolver|Cylinder|RevolverRounds|Clip1 ')

if 'drops' in JOBS:
    s = PRE + ''.join('rsq_moonlight_pistol %d; map map01; wait 30; echo REV DROPS pistol %d; %s %s wait 5; kill monsters; wait 200; '
                      'netevent rsq_moon_count; wait 5; ' % (a, a, 'summon PistolSpawner; ' * 10, 'summon PistolZombie; ' * 5) for a in (0, 1))
    s += 'rsq_moonlight_pistol 0; quit'
    rc, t = rig.run('rev_drops', s, 300); restore_ini()
    log = OUT + '/build/logs/rev_drops.log'
    show('drops rc %d (from %s)' % (rc, log), open(log, errors='replace').read(), r'REV DROPS|RSQ moon: map|monsters')

if 'slug' in JOBS:
    probe = os.environ.get('SLUGPROBE', os.path.join(OUT, '..', 'slugprobe.pk3'))
    s = PRE + ('rsa_rev_slug 1; give Revolver; give AmmoShell 50; use Revolver; wait 150; echo REV ALTFIRE; +altattack; wait 40; '
               '-altattack; wait 60; echo REV FIRE; +attack; wait 4; -attack; wait 60; echo REV ALTFIRE2; +altattack; wait 40; -altattack; '
               'wait 60; echo REV END; quit')
    rc, t = rig.run('rev_slug', s, 240, [os.path.abspath(probe)]); restore_ini()
    log = OUT + '/build/logs/rev_slug.log'
    show('slug rc %d (from %s)' % (rc, log), open(log, errors='replace').read(), r'REV |SLUGPROBE|rsa_rev_slug')

if 'menu' in JOBS:
    fr = OUT + '/frames_menu'
    shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
    os.environ.update(QZ_RES='480', QZ_DUMP_EVERY='10', QZ_DUMP_DIR=fr)
    s = PRE + 'wait 20; openmenu RSQ_Options; wait 60; echo REV MENU; wait 20; quit'
    rc, t = rig.run('rev_menu', s, 200); restore_ini()
    for k in ('QZ_DUMP_EVERY', 'QZ_DUMP_DIR'):
        os.environ.pop(k)
    show('menu rc %d' % rc, t, r'REV |Unknown menu|openmenu')
    print('    frames:', len(glob.glob(fr + '/*')), fr)

if 'dual' in JOBS:
    fr = OUT + '/frames_dual'
    shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
    os.environ.update(QZ_RES='320', QZ_DUMP_EVERY='4', QZ_DUMP_DIR=fr)
    R, L = '0.22 1.3 -0.35 %d 0 0', '-0.22 1.3 -0.35 %d 0 0'
    s = PRE + ('rsr_reload 1; qz_hmd "0 1.6 0 -20 0 0"; qz_rhand "%s"; qz_lhand "%s"; take RevolverRounds 999; give BrutalRevolver; '
               'use BrutalRevolver; wait 120; echo REV ONE; printinv; summon BrutalRevolver; wait 3; qz_lstick "0 1"; wait 15; '
               'qz_lstick "0 0"; wait 5; echo REV PICKED; printinv; give StartDualWield; wait 80; echo REV DUAL_HELD; printinv; '
               'echo REV FIRE_MAIN; +attack; wait 3; -attack; wait 25; echo REV FIRE_OFF; qz_ltrigger 1; wait 3; qz_ltrigger 0; wait 25; '
               'echo REV FIRE_BOTH; +attack; qz_ltrigger 1; wait 3; -attack; qz_ltrigger 0; wait 25; echo REV AFTER_FIRE; printinv; '
               'echo REV FLICK_OFF; qz_lhand "%s"; wait 8; qz_lhand "%s"; wait 60; echo REV AFTER_FLICK_OFF; printinv; '
               'echo REV FLICK_MAIN; qz_rhand "%s"; wait 8; qz_rhand "%s"; wait 90; echo REV AFTER_FLICK_MAIN; printinv; echo REV END; quit'
               % (R % 30, L % 30, L % -70, L % 30, R % -70, R % 30))
    rc, t = rig.run('rev_dual', s, 300); restore_ini()
    for k in ('QZ_DUMP_EVERY', 'QZ_DUMP_DIR'):
        os.environ.pop(k)
    log = OUT + '/build/logs/rev_dual.log'
    show('dual rc %d (from %s)' % (rc, log), open(log, errors='replace').read(), r'REV |RSQ moon|Revolver|Cylinder|B22 SHOT')
    print('    frames:', len(glob.glob(fr + '/*')), fr)

# ---- round 5 (owner 20:47): ammo "on top" and the HUD's ammo
ONTOP = [('Rifle', 'Clip2', 'Clip2', 'RifleAmmo'), ('Minigun', 'Clip2', 'Clip2', 'RSQ_Mag_Minigun'),
         ('MG42', 'Clip2', 'Clip2', 'RSQ_Mag_MG42'), ('Shot_Gun', 'AmmoShell', 'AmmoShell', 'ShotgunAmmo')]
if 'ontop' in JOBS:
    # each gun: reserve filled to its cap with the magazine full (a REAL gun fills its magazine from the pouch the first
    # time it is held, so the reserve is filled again after), then a pickup of its reserve summoned and walked onto (it
    # must stay: refused at the cap; every walk starts from MAP07's yard, warped to); then, with the Rifle in hand (so a REAL gun's bookkeeping does not read it as
    # shots), 30 taken from the reserve, the gun back, and a second pickup summoned and walked onto the same way: taken
    # round 6: on MAP07's flat yard (-1010 -1138, facing west). MAP01's start is a ledge (z 56): the summoned pickup
    # dropped to the floor below it (z 8) and the player, still on the ledge, never touched it -- a test artifact that
    # made round 5's at-cap 'refused' and the Shot_Gun's 'not taken' meaningless (tools/moonammo/pickprobe shows it).
    s = PRE + 'rsr_reload 1; rsq_reload_nonstd 1; map map07; wait 20; '
    for g, res, pick, mag in ONTOP:
        s += ('warp -1010 -1138; give %s; give %s 999; use %s; wait 160; give %s 999; wait 5; echo REV ONTOP %s FULL; netevent rsq_ontop; wait 3; '
              'summon %s; wait 3; qz_lstick "0 1"; wait 12; qz_lstick "0 0"; wait 8; echo REV ONTOP %s AFTER_PICKUP; netevent rsq_ontop; '
              'warp -1010 -1138; use Rifle; wait 40; take %s 30; use %s; wait 90; echo REV ONTOP %s BELOW_CAP; netevent rsq_ontop; '
              'summon %s; wait 3; qz_lstick "0 1"; wait 12; qz_lstick "0 0"; wait 8; '
              'echo REV ONTOP %s AFTER_PICKUP_BELOW_CAP; netevent rsq_ontop; wait 3; ' % (g, res, g, res, g, pick, g, res, g, g, pick, g))
    s += 'quit'
    rc, t = rig.run('rev_ontop', s, 400); restore_ini()
    log = OUT + '/build/logs/rev_ontop.log'
    show('ontop rc %d (from %s)' % (rc, log), open(log, errors='replace').read(), r'REV ONTOP|RSQ ontop|[Pp]icked up|You got|GOT')

if 'hud' in JOBS:
    # one run per gun, the classic bar (screenblocks 10): HUD Ammo 0 (Magazine + Reserve) for 70 tics, then 1 (Reserve
    # Only) for 70; netevent rsq_ontop prints the HUD items too; frames dumped (the last of each half is used)
    for g, extra in (('Rifle', 'give Clip2 120;'), ('Minigun', 'give Clip2 300;'), ('MG42', 'give Clip2 300;'), ('Shot_Gun', 'give AmmoShell 30;'),
                     ('BrutalRevolver', 'give RevolverRounds 20;'), ('BrutalPistol', 'give Clip1 60; give StartDualWield;')):
        fr = OUT + '/frames_hud_' + g
        shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
        os.environ.update(QZ_RES='480', QZ_DUMP_EVERY='5', QZ_DUMP_DIR=fr)
        s = PRE.replace('screenblocks 12', 'screenblocks 10') + ('rsr_reload 1; rsq_reload_nonstd 1; give %s; %s use %s; wait 170; %s give Clip2 120; give RevolverRounds 20; wait 60; '
             'rsq_hud_ammo 0; wait 70; echo REV HUD %s MAG_RESERVE; netevent rsq_ontop; rsq_hud_ammo 1; wait 70; echo REV HUD %s RESERVE_ONLY; '
             'netevent rsq_ontop; wait 3; rsq_hud_ammo 0; quit' % (g, extra.replace('give StartDualWield;', ''), g, 'give StartDualWield;' if 'StartDualWield' in extra else '', g, g))
        rc, t = rig.run('rev_hud_' + g, s, 300); restore_ini()
        for k in ('QZ_DUMP_EVERY', 'QZ_DUMP_DIR'):
            os.environ.pop(k)
        log = OUT + '/build/logs/rev_hud_%s.log' % g
        show('hud %s rc %d' % (g, rc), open(log, errors='replace').read(), r'REV HUD|RSQ ontop')
        print('    frames:', len(glob.glob(fr + '/*')), fr)
