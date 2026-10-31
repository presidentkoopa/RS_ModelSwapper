"""blend2anim.py -- every gun's .blend to one ANIMATED .md3, ready for batch.py.

Why this exists
---------------
The owner said at the outset: the models are animated, and the source .blend for
each one is on disk. The first pass exported a single frame per gun anyway, which
threw the reloads away and -- worse -- silently took whatever frame each blend
happened to be saved on as the gun's rest pose. Parts came out parked inside
buttstocks and drums came out already swung off the gun, and every card measured
from those frames was wrong.

This is the front half of the real pipeline:

    blend2anim.py  <blend-root> <out-dir>      # .blend  -> <GUN>.md3, animated
    batch.py       <out-dir> <label-dir>       # -> cards, carves, TABLE.md, sheet.png

batch.py already does everything after this point: it guesses the archetype from
what moves, runs md3label, writes the card and the carved parts, and renders a
contact sheet so the whole set is checked by eye at once. It only ever needed
animated input.

Per gun: one Blender launch exports the whole frame range (blendobj4 --frames),
then each frame becomes a single-frame MD3, then md3_stack joins them.

    --axes xzy      obj2md3's default puts the bore on +Y; the muzzle lands at
                    x 2.77 on a rifle 121 units long. xzy puts it on +X.
    --stable-verts  obj2md3 keys a vertex on (position, uv, NORMAL) by default, and
                    a rotating part gets different normal indices per frame, so the
                    surface changes vertex COUNT between frames and the stack is
                    refused. MD3 stores a normal per vertex per frame anyway.

usage:
  python -B blend2anim.py <blend-root> <out-dir> [--only NAME,NAME] [--jobs N]
"""
import os
import subprocess
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"

# gun name -> blend, relative to the blend root. Several folders hold a file of the
# same name (AssaultShotgun, knife), so the mapping is explicit rather than a glob.
GUNS = {
    '1911': '_ZMCwolf/1911.blend',          'Axe': '_ZMCwolf/Axe.blend',
    'Chaingun': '_ZMCwolf/Chaingun.blend',  'Flame': '_ZMCwolf/Flame.blend',
    'Grenade': '_ZMCwolf/Grenade.blend',    'Kar98': '_ZMCwolf/Kar98.blend',
    'Knife': '_ZMCwolf/Knife.blend',        'MG42': '_ZMCwolf/MG42.blend',
    'MP40': '_ZMCwolf/MP40.blend',          'STG44': '_ZMCwolf/STG44.blend',
    'Shotgun': '_ZMCwolf/Shotgun.blend',    'Tommy': '_ZMCwolf/Tommy.blend',
    'bar': '_ZMCwolf/bar.blend',            'garand': '_ZMCwolf/garand.blend',
    'luger': '_ZMCwolf/luger.blend',        'ppsh41': '_ZMCwolf/ppsh41.blend',
    'CANISTER': '_Hacx/CANISTER.blend',     'Nuker': '_Hacx/Nuker.blend',
    'Stick': '_Hacx/Stick.blend',           'UZI': '_Hacx/UZI.blend',
    'Zooka': '_Hacx/Zooka.blend',           'cryogun': '_Hacx/cryogun.blend',
    'melee': '_Hacx/melee.blend',           'pistol': '_Hacx/pistol.blend',
    'tazer': '_Hacx/tazer.blend',           'xplosebolt': '_Hacx/xplosebolt.blend',
    'AssaultShotgun': '_Meatgrinder/AssaultShotgun.blend',
    'CHAING': '_Meatgrinder/CHAING.blend',  'CHAINGRPG': '_Meatgrinder/CHAINGRPG.blend',
    'SSG': '_Meatgrinder/SSG.blend',        'Saw': '_Meatgrinder/Saw.blend',
    'bfg': '_Meatgrinder/bfg.blend',        'bolter': '_Meatgrinder/bolter.blend',
    'tec9': '_Meatgrinder/tec9.blend',

    # BrutalDoom's own folder and the two HacX weapons that were skipped as if they
    # were templates. Prefixed bd_/hx_ because several share a name with a gun
    # already here -- BrutalDoom/MP40 and _ZMCwolf/MP40, mg42 and MG42, nade and
    # Grenade -- and this filesystem is case-insensitive, so an unprefixed map would
    # have quietly overwritten the Wolfenstein versions with the BrutalDoom ones.
    'bd_AssaultShotgun': 'BrutalDoom/AssaultShotgun/AssaultShotgun.blend',
    'bd_AssaultShotgun2': 'BrutalDoom/AssaultShotgun/AssaultShotgun2.blend',
    'bd_BFG': 'BrutalDoom/BFG/BFG.blend',
    'bd_BFG10K': 'BrutalDoom/BFG/BFG10K.blend',
    'bd_BFG_Flame': 'BrutalDoom/BFG/BFG_Flame.blend',
    'bd_Boot': 'BrutalDoom/Boot/Boot.blend',
    'bd_Boot_DooM64': 'BrutalDoom/Boot/Boot_DooM64.blend',
    'bd_Bootlow': 'BrutalDoom/Boot/Bootlow.blend',
    'bd_BrutalAxe': 'BrutalDoom/BrutalAxe/BrutalAxe.blend',
    'bd_BrutalAxe_pbr': 'BrutalDoom/BrutalAxe/BrutalAxe_pbr.blend',
    'bd_br_pistol_f': 'BrutalDoom/BrutalPistol/br_pistol_f.blend',
    'bd_br_pistol_f_dual': 'BrutalDoom/BrutalPistol/br_pistol_f_dual.blend',
    'bd_br_pistol_holo': 'BrutalDoom/BrutalPistol/br_pistol_holo.blend',
    'bd_br_SMG_dual': 'BrutalDoom/BrutalSMG/br_SMG_dual.blend',
    'bd_br_SMG_f': 'BrutalDoom/BrutalSMG/br_SMG_f.blend',
    'bd_br_SMG_holo': 'BrutalDoom/BrutalSMG/br_SMG_holo.blend',
    'bd_Chain_saw': 'BrutalDoom/Chain_saw/Chain_saw.blend',
    'bd_Chain_saw_Better': 'BrutalDoom/Chain_saw/Chain_saw_Better.blend',
    'bd_Chain_saw_DooM64': 'BrutalDoom/Chain_saw/Chain_saw_DooM64.blend',
    'bd_Chain_saw_Low': 'BrutalDoom/Chain_saw/Chain_saw_Low.blend',
    'bd_Chain_saw_blood': 'BrutalDoom/Chain_saw/Chain_saw_blood.blend',
    'bd_Dslayer': 'BrutalDoom/DragonSlayer/Dslayer.blend',
    'bd_fist': 'BrutalDoom/Fist/fist.blend',
    'bd_FlameCannon': 'BrutalDoom/FlameCannon/FlameCannon.blend',
    'bd_Flamethrower2': 'BrutalDoom/Flamethrower2/Flamethrower2.blend',
    'bd_nade': 'BrutalDoom/Grenade/nade.blend',
    'bd_HellishMissile': 'BrutalDoom/HellishMissile/HellishMissile.blend',
    'bd_M79': 'BrutalDoom/M79/M79.blend',
    'bd_mg42': 'BrutalDoom/MG-42/mg42.blend',
    'bd_Dual_MP40': 'BrutalDoom/MP40/Dual_MP40.blend',
    'bd_MP40': 'BrutalDoom/MP40/MP40.blend',
    'bd__br_machinegun_f': 'BrutalDoom/Machinegun/_br_machinegun_f.blend',
    'bd_br_minigun_f': 'BrutalDoom/Minigun/br_minigun_f.blend',
    'bd_br_minigun_snub_f': 'BrutalDoom/Minigun/br_minigun_snub_f.blend',
    'bd_br_plasma_dual': 'BrutalDoom/Plasma/br_plasma_dual.blend',
    'bd_br_plasma_f': 'BrutalDoom/Plasma/br_plasma_f.blend',
    'bd_br_plasma_flame': 'BrutalDoom/Plasma/br_plasma_flame.blend',
    'bd_RPG': 'BrutalDoom/RPG/RPG.blend',
    'bd_RPGret': 'BrutalDoom/RPG/RPGret.blend',
    'bd_RailGun': 'BrutalDoom/RailGun/RailGun.blend',
    'bd_SnipaRailGun': 'BrutalDoom/RailGun/SnipaRailGun.blend',
    'bd_taurusload': 'BrutalDoom/Revolver/taurusload.blend',
    'bd_br_rifle_f': 'BrutalDoom/Rifle/br_rifle_f.blend',
    'bd_br_rifle_f_dual': 'BrutalDoom/Rifle/br_rifle_f_dual.blend',
    'bd_br_rifle_holo': 'BrutalDoom/Rifle/br_rifle_holo.blend',
    'bd_br_ssg_2f': 'BrutalDoom/SSG/br_ssg_2f.blend',
    'bd_br_ssg_f': 'BrutalDoom/SSG/br_ssg_f.blend',
    'bd_br_shotgun_aim_f': 'BrutalDoom/Shotgun/br_shotgun_aim_f.blend',
    'bd_br_shotgun_f': 'BrutalDoom/Shotgun/br_shotgun_f.blend',
    'bd_SnipaRailGun_2': 'BrutalDoom/Snipa/SnipaRailGun.blend',
    'bd_snipa': 'BrutalDoom/Snipa/snipa.blend',
    'bd_snipaRPG': 'BrutalDoom/Snipa/snipaRPG.blend',
    'bd_Unmaker': 'BrutalDoom/Unmaker/Unmaker.blend',
    'hx_Reznator': '_Hacx/REZnator/Reznator.blend',
    'hx_ElectroFX': '_Hacx/REZnator/ElectroFX.blend',
    'hx_arc': '_Hacx/REZnator/arc.blend',
    'hx_boot': '_Hacx/boot.blend',
}

PROBE = r"""
import bpy, sys
sc = bpy.context.scene
movers = 0
for o in bpy.data.objects:
    for src in (o, o.parent):
        if src and src.animation_data and src.animation_data.action:
            movers += 1
            break
print("@@@RANGE %d %d %d" % (sc.frame_start, sc.frame_end, movers))
"""


def run(cmd, **kw):
    # Blender inherits the console's cp1252 on Windows, and a blend whose objects carry
    # a non-ASCII name (br_rifle_f has one with \x83 in it) kills the run with a
    # UnicodeEncodeError the moment anything prints that name. Force UTF-8 on the child
    # and never let a decode problem in captured output end an export.
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', env=env, **kw)


def frame_range(blend, probe_py):
    r = run([BLENDER, blend, '--background', '--python', probe_py])
    for line in r.stdout.splitlines():
        if line.startswith('@@@RANGE'):
            _, a, b, mv = line.split()
            return int(a), int(b), int(mv)
    return None


def build(name, blend, outdir, work, probe_py):
    rng = frame_range(blend, probe_py)
    if not rng:
        return name, 0, 'could not read frame range'
    f0, f1, movers = rng
    if f1 <= f0 or not movers:
        f0 = f1 = 0                       # genuinely static: one frame is honest
    d = os.path.join(work, name)
    os.makedirs(os.path.join(d, 'md3'), exist_ok=True)
    r = run([BLENDER, blend, '--background', '--python',
             os.path.join(HERE, 'blendobj4.py'), '--',
             '--out', d + os.sep, '--frames', str(f0), str(f1)])
    objs = sorted(glob.glob(os.path.join(d, 'f*.obj')))
    if not objs:
        return name, 0, 'no OBJ written (%s)' % (r.stderr or r.stdout)[-120:]
    for o in objs:
        m = os.path.join(d, 'md3', os.path.basename(o)[:-4] + '.md3')
        run([sys.executable, '-B', os.path.join(HERE, 'obj2md3.py'), o, m,
             name + '.png', '--stable-verts', '--axes', 'xzy'])
    mds = sorted(glob.glob(os.path.join(d, 'md3', '*.md3')))
    if not mds:
        return name, 0, 'no MD3 written'
    out = os.path.join(outdir, name + '.md3')
    r = run([sys.executable, '-B', os.path.join(HERE, 'md3_stack.py'), out, '--dir',
             os.path.join(d, 'md3')])
    if r.returncode != 0 or not os.path.exists(out):
        return name, 0, (r.stdout + r.stderr).strip().splitlines()[-1][:140]
    return name, len(mds), ''


def main():
    root, outdir = sys.argv[1], sys.argv[2]
    only = None
    if '--only' in sys.argv:
        only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    os.makedirs(outdir, exist_ok=True)
    work = os.path.join(outdir, '_work')
    os.makedirs(work, exist_ok=True)
    probe_py = os.path.join(work, '_probe.py')
    open(probe_py, 'w').write(PROBE)

    names = [n for n in sorted(GUNS) if not only or n in only]
    print(f"{len(names)} guns -> {outdir}\n")
    ok = bad = 0
    for n in names:
        blend = os.path.join(root, GUNS[n])
        if not os.path.exists(blend):
            print(f"  {n:<16} MISSING {GUNS[n]}")
            bad += 1
            continue
        nm, frames, err = build(n, blend, outdir, work, probe_py)
        if err:
            print(f"  {nm:<16} FAILED  {err}")
            bad += 1
        else:
            print(f"  {nm:<16} {frames:3d} frames")
            ok += 1
    print(f"\n{ok} built, {bad} failed")


if __name__ == '__main__':
    main()
