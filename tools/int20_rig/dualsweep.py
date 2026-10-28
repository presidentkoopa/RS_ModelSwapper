"""TEST ONLY (2.0 integration lane): real-play dual check for every dual gun. dualsweep.py <pk3> [tag] [extra cvars]"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import re, subprocess, sys
R = (_DP.WORK + '/int20_rig')
G = [('BrutalPistol','PistolSpawner','BDPistolAmmoOff','rsq_dual_pistol'), ('Revolver','RevolverSpawner','RevolverAmmoOff','rsq_dual_revolver'),
     ('BrutalSMG','SMGSpawner','BDSMGAmmoOff','rsq_dual_smg'), ('MP40','MP40Spawner','MP40AmmoOff','rsq_dual_mp40'),
     ('Rifle','RifleSpawner','RifleAmmoOff','rsq_dual_rifle'), ('Plasma_Gun','PLasmagunSpawner','PlasmaAmmoOff','rsq_dual_plasma'),
     ('Shot_Gun','ShotgunSpawner','ShotgunAmmoOff','rsq_dual_shotgun'), ('SSG','SSGSpawner','SSGAmmoOff','rsq_dual_ssg'),
     ('AssaultShotgun','ASGSpawner','AssaultShotgunAmmoOff','rsq_dual_asg'), ('RailGun','RailgunSpawner','RailgunAmmoOff','rsq_dual_railgun'),
     ('BrutalRevolver','BrutalRevolver','BrutalRevolverCylinderOff','rsq_dual_moonlight')]
pk3 = sys.argv[1]; tag = sys.argv[2] if len(sys.argv) > 2 else 'd'; extra = sys.argv[3] if len(sys.argv) > 3 else ''
only = sys.argv[4].split(',') if len(sys.argv) > 4 else None
for g, sp, om, cv in G:
    if only and g not in only: continue
    c = 'netevent int_cnt_%s; netevent int_mark' % om
    pre = 'give BrutalRevolverCylinder 6; wait 5; ' if g == 'BrutalRevolver' else ''
    getsecond = ('give HasDualMP40; wait 10; ' if g == 'MP40' else
                 'netevent int_drop_%s; wait 15; qz_lstick "0 0.6"; wait 4; qz_lstick "0 -0.6"; wait 4; qz_lstick "0 0"; wait 30; ' % sp)
    s = ('wait 100; god; notarget; rsq_extra_weapons 1; rsr_debug 1; rsq_dual_start 0; %s 1; %s give %s; use %s; wait 150; '
         '%s%s'
         '+user3; wait 3; -user3; wait 100; %s_a; qz_ltrigger 1; wait 4; qz_ltrigger 0; wait 40; %s_b; wait 40; %s_c; '
         'qz_rtrigger 1; wait 4; qz_rtrigger 0; wait 40; %s_d; qz_ltrigger 1; wait 4; qz_ltrigger 0; wait 40; %s_e; wait 3; quit'
         % (cv, extra, g, g, pre, getsecond, c, c, c, c, c))
    name = '%s_dual_%s' % (tag, g)
    subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh'), name, pk3, '420', s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
    off = [int(x) for x in re.findall(r'INT CNT t\d+ %s=(-?\d+)' % om, t)]
    main = [int(x) for x in re.findall(r'INT MARK int_mark_\w t\d+ .* ammo2 (-?\d+)', t)]
    wpn = re.findall(r'INT WPN t\d+ main (\S+) off (\S+)', t)
    gotcopy = any(o.startswith('RSQ_Off_') for m, o in wpn)
    errs = [l for l in t.splitlines() if re.search(r'VM abort|Script error|exception', l) and 'voxeldef' not in l]
    msgs = re.findall(r'(Find a second .*|Dual .* is off.*)', t)
    ok = gotcopy and len(off) == 5 and len(main) == 5 and off[1] < off[0] and off[2] == off[1] and off[1] >= 0 and main[3] < main[2] and off[4] < off[3] and not errs
    print('%-15s %s copy-in-off %s off %s main %s %s %s' % (g, 'PASS' if ok else 'FAIL', gotcopy, off, main, msgs[:1], errs[:2]), flush=True)
