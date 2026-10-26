# tools/rig: testing bd22q in the real engine (TEST ONLY, never ships)

The real QuestZDoom engine (emawind84/gzdoom 4.14.3, the owner's QZD17 version), built for Linux,
on the OpenXR code path, with the headset and both controllers posed from cvars. It renders the
left eye to image files, so you can SEE a held gun and its hands. Every check in the 1.99 work
ran here: hand fits, reloads, fire rates, spin, casings, the axe lock-on.

## Start here (one command)
The rig is PREBUILT in `bin/` (`bin/qz` launches it; Linux x86_64, needs Mesa GLES/EGL + OpenAL).
```
sh tools/rig/setup.sh          # seconds: zips the probe and the test packs into tools/rig/build/
cd tools/rig
python3 cmp2.py build/BD22Q_192.pk3 build/BD22Q_now.pk3 Pistol,PlasmaGun t1
#  -> build/shots/cmp2_t1.png : each gun held, 1.92 on the left, the depot's current set on the right
```
`setup.sh` zips `build/probe.pk3`, `build/upstream.pk3`,
`build/BD22Q_now.pk3` (this depot's `sets/bd22q_1.97/src`) and `build/BD22Q_192.pk3` (tag 1.92 of
RS_Brutal22WeaponsQ, the owner's baseline). Re-run it after changing the set (it re-zips BD22Q_now).
`sh tools/rig/setup.sh build` rebuilds the engine from source (pinned commits, ~20-40 min) into
`build/rig/`, which `rig.py` then prefers over `bin/`.

**Game data is the owner's and is not in git:** doom2.wad, brutal22test6.pk3, BD_VoxelPack.pk3.
`rig.py` looks in `/mnt/user-data/uploads` (where the cloud session had them) or in
`B22_IWAD` / `B22_BD22` / `B22_VOX`. Ask the owner to attach them if they are missing.
Needs: git, cmake, make, clang or gcc, zip, python3 + Pillow, Mesa GLES/EGL, OpenAL.

## Posing the hands
- `qz_hmd "x y z pitch yaw roll"` places the head; `qz_rhand` / `qz_lhand` place the controllers
  (metres, degrees, stage space). `qz_rhand "0.0 1.68 -0.40 20 -70 0"` shows the held gun side-on
  in front of the eye; `"0.0 1.50 -0.30 30 0 0"` from behind.
- `rig.lpose(F, L, U)` / `engine/pose.py F L U`: an off-hand point given in the gun's frame (cm)
  -> the `qz_lhand` value. `handrot.py` has the rotation maths for the off hand.
- Frame dumps: `QZ_DUMP_EVERY=N QZ_DUMP_DIR=<dir>` with `QZ_RES=480`; `shots.shoot()` wraps it.
- Sound log: `QZ_SNDLOG=1` prints `QZSND <tic> <sound> ch vol src <class>` for every sound start.

## What is here
| file | what |
|---|---|
| `bin/` | the prebuilt rig: `qzdoom` (with the sound log), `libzmusic.so.1`, engine pk3s, `config/qzdoom.ini`, `qz` launcher |
| `setup.sh` | the one command above. Source pins for `build`: engine `9afc750`, wrapper `a85c819` |
| `engine/` | the rig build: `build.sh` + `Makefile`, `glue/qz_linux_glue.cpp` (OpenXR stand-in, poses from cvars, frame dump), `shim/` (NDK/JNI header stand-ins), `config/qzdoom.ini` (test ini), `pose.py`, `qz` (launcher) |
| `s_sound_log.patch` | test-only `QZ_SNDLOG` in the engine's StartSound |
| `rig.py` | `run(name, script, secs, extra)`: one engine run on the load order + probe; logs to `build/logs/`. Env: `B22_PK3`, `B22_RIG`, `B22_NOPROBE`, `QZ_RES` |
| `shots.py`, `cmp.py`, `cmp2.py` | frame dumps; `cmp2.py <pkA> <pkB> <Gun,...> <tag> [pose]` = A left, B right |
| `mags.py` | magazine reloads driven by the off hand (`with_pouch` for wells near the rest pose) |
| `pump.py`, `brk.py`, `m203.py`, `grip.py` | pump, break-open, M203 and grip-mode drivers |
| `spintest.py` | walk / fire / reload, logs psp.x/psp.y and flash count |
| `holdtest3.py` | trigger held 140 tics per gun, QZD as is vs upstream attackdown (`build/upstream.pk3`) |
| `probe/` | the `B22 ...` log lines (reload tables, state, shots, psp, casings, axe lock) |

Load order is always doom2 -> brutal22test6 -> BD_VoxelPack -> pack (CLAUDE.md rule 5).
BD_VoxelPack prints four `voxeldef.txt` script errors on its own; they are not ours.

## Traps (each cost a run)
- `-warp 1` is required: BD22's title map swallows `+map` and its AimingCamera stops VR attaching.
  `QZ_RES=200` for speed, 480 for pictures.
- `playerclass=$TAGBD_CLASS_RIFLE` (in the ini), or you get a random class (Purist has no reload).
- `rsq_extra_weapons 1` for the hidden guns. `give <class>` explicitly; `give all` gives Purist guns.
- The off hand is the gun hand mirrored in L; side wells need a 180 degree yaw (`mags.at`).
- `CanTakeMag` refuses a hand within 20 cm of the magazine (`POUCH_MIN`): reach to a pouch first.
- Give a gun ~150 tics to finish its select animation before testing it.
- `wait` inside an alias does not fire; runs end by `timeout`.
- The engine's `screenshot` command returns garbage in VR mode; use the frame dump.
- `B22_NOPROBE=1` for old packs whose class names the probe does not know.
- Never chain pipeline stages with `;` after a failing stage. Use `set -o pipefail` and `&&`.
