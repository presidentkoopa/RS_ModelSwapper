---
name: qzd-vr-weapon-mechanics
description: Build and check VR weapon mechanics (FBX hands on the guns, reloading by hand, live scopes, melee, throwing, dual wield) for Doom weapon sets on stock QuestZDoom 17.3 with the RSQ Weapon Depot's rig and tools.
---

# VR weapon mechanics on QuestZDoom 17.3

The full handbook is `docs/handbook/` in the RSQ Weapon Depot (github presidentkoopa/RSQ_WeaponDepot). Read
`README.md` there first (the ten rules), then the chapter for the task. BD22 VR Weapons Q 2.0.1
(`sets/bd22q`) is the worked example of every mechanic.

## Before you touch anything
1. Read the Depot's `CLAUDE.md`, `PLAN.md` ("Current step" is your job), `HANDOFF.md`. Run
   `sh tools/install_hooks.sh`. Commits start with `[step <id>]` or `[plan]`.
2. No engine changes to QuestZDoom 17.3. Everything is ZScript / DECORATE / MODELDEF / models.
3. Nothing is "working" until shown on the rig (frames or a log of the behaviour). VR behaviour is "rig only,
   not headset-confirmed" until the owner has played it.
4. Nothing goes to the owner until it boots on doom2 -> brutal22test6 -> BD_VoxelPack -> the pack with no script
   error from the pack (BD_VoxelPack's own four `voxeldef.txt` errors are not yours).

## The method, one gun (chapter 4)
mesh (measure at the Ready frame) -> the 1.92 hold or a named pose -> gun hand (re-seat the approved FBX pistol
hand, curl the fingers, solve the squeeze) -> **port: the gun moves to the hand, the wrist stays pinned; move
every MODELDEF block that draws it and everything on it** (`tools/handfit/port/port_gun.py`) -> support hand from
the 1.92 hold (`tools/handfit/support192/`) -> reload rows (moved by the port) -> the FBX reload hold
(`tools/handfit/offhand/`) -> pose as data (`$RSQ_POSES/<Class>.json`, `rebake.py check`) -> rig proof
(boot, hand reload, sheet) -> **look at every frame** -> the owner's headset. Variants copy the base gun's rows.

## The rig (chapter 2)
```sh
sh tools/rig/setup.sh                       # QZD 17.3 rig check + builds sets/bd22q (RSQ_SET) into tools/rig/build/BD22Q_now.pk3
cd tools/rig && RSQ_GAMEDATA=<dir> flock -o -x /home/claude/rig.lock python3 rig.py boot 'wait 100; quit' 150
grep -hE "Script error|VM execution aborted" build/logs/boot.log | sort | uniq -c
```
Pose with `qz_hmd` / `qz_rhand` / `qz_lhand "x y z pitch yaw roll"`, triggers `qz_ltrigger 1`, walk with
`qz_lstick` (never `+forward`). Frames: `QZ_RES=480 QZ_DUMP_EVERY=2 QZ_DUMP_DIR=<dir>`; convert to PNG and delete
the `.ppm` at once. One engine at a time. Restore `tools/rig/bin/config/qzdoom.ini` with `git checkout`.

## Checks that catch most mistakes
- `RSQ_FBX=<hand_final.fbx> python3 tools/handfit/port/rebake.py check` (poses rebuild from data; placements regenerate).
- `python3 tools/handfit/port/gate_gun.py sheet|hands|compose ...` (one gun's frames and hand reload).
- `tools/int20_rig/f20all.sh <pk3>` (whole pack on the fresh default ini); `mdslots.py <pk3>`; `variants_all.py <pk3>`.

## The traps that cost the most (chapter 6)
Saved cvars hide new defaults (rename the cvar). `ZOffset` overwrites `Offset`'s z. A MODELDEF block is sized by
its last `Model` line. A whole-model `Skin` beats `SurfaceSkin` and `A_ChangeModel`. The off hand is mirrored:
bake off-hand frames as the right rig. An open palm can pass every numeric check: look. An unregistered
EventHandler never runs. Interrupts silently stop lanes: check before reporting.

## Paths
All in `tools/depot.py`: `RSQ_SET`, `RSQ_SRC`, `RSQ_POSES`, `RSQ_FITS_DIR`, `RSQ_GAMEDATA`, `RSQ_RIGLOCK`,
`RSQ_WORK`, `RSQ_GUNPACK`; outside inputs never committed: `RSQ_FBX` (unknown licence), `RSQ_ERMAC`.
