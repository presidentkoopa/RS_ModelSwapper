# tools/rig: testing bd22q in the real engine (TEST ONLY, never ships)

The real QuestZDoom engine -- Emawind's **QuestZDoom 17.3** (tag `qzd17.3`, gzdoom 9afc750, the
release the owner and his players run) -- built for Linux, on the OpenXR code path, with the
headset and both controllers posed from cvars. It renders the left eye to image files, so you can
SEE a held gun and its hands.

**The engine is always QuestZDoom 17.3, the commits in `PINS`.** The launcher (`engine/qz`, copied
to `bin/qz` and `build/rig/qz`) refuses to start any other engine and prints `qz: engine OK: ...` on
every launch.

**History of `bin/`.** The first prebuilt `bin/` (pushed c896330) was NOT 17.3: it was built from a
later, unreleased commit (4.15pre, ZScript 4.12), ran silently, and was removed on 2026-10-26
(32cc8df); results measured on it are void. The `bin/` here now (F12, 2026-10-26) is the correct
QuestZDoom 17.3 build, moved in from RS_ModelSwapper `gate/qz_rig/bin` (98ae205; the `qzdoom` binary
is byte-identical to a `setup.sh build` from `PINS` on this machine), with the Depot's own `engine/qz`
as its launcher. It reports `qz: engine OK: QuestZDoom qzd17.3 (9afc750...), engine 4.14.3, ZScript 4.14.2`.

## Start here (one command)
```
sh tools/rig/setup.sh                 # seconds: test packs + check that tools/rig/bin is 17.3
#   or: sh tools/rig/setup.sh build   # ~20-40 min: engine from PINS into build/rig/ (then B22_RIG=tools/rig/build/rig)
cd tools/rig
RSQ_GAMEDATA=<folder with doom2.wad, brutal22test6.pk3, BD_VoxelPack.pk3> \
  flock -o -x /home/claude/rig.lock python3 cmp2.py build/BD22Q_192.pk3 build/BD22Q_now.pk3 BrutalPistol,Plasma_Gun t1
#  -> build/shots/cmp2_t1.png : each gun held, 1.92 on the left, the depot's current set on the right
```
Gun names are BD22's classes (`BrutalPistol`, `Plasma_Gun`, ...). The example used to say
`Pistol,PlasmaGun`: that runs and writes the PNG, but no pistol is drawn and the PlasmaGun row shows
the start rifle (measured on a fresh clone, F12).
`setup.sh` zips `build/probe.pk3`, `build/upstream.pk3`,
`build/BD22Q_now.pk3` (the set under work, `$RSQ_SET` or `sets/bd22q`, built by its own `build.py`) and `build/BD22Q_192.pk3` (tag 1.92 of
RS_Brutal22WeaponsQ, the owner's baseline), then checks the rig is 17.3. Re-run it after changing
the set (it re-zips BD22Q_now). `rig.py` uses `B22_RIG` if set, else `bin/`, and stops with
a message if it has no engine. On a shared machine run one engine at a time: `flock -o -x` as above (`-o`: a child such as a stray Xvfb never inherits the lock).

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
| `PINS` | the one engine allowed: QuestZDoom 17.3 commits and the versions a correct build reports |
| `bin/` | the prebuilt QuestZDoom 17.3 rig (engine, its pk3s, libzmusic, test ini, `qz` launcher with the guard). `bin/saves/` and `bin/libGLESv3.so` are made at run time (gitignored) |
| `setup.sh` | the one command above; checks the rig is 17.3, or builds from `PINS` (`build`) |
| `engine/` | the rig build: `build.sh` + `Makefile`, `glue/qz_linux_glue.cpp` (OpenXR stand-in, poses from cvars, the qzt_* test-driver hook, frame dump), `shim/` (NDK/JNI header stand-ins), `config/qzdoom.ini` (test ini), `pose.py`, `qz` (launcher with the version guard) |
| `s_sound_log.patch` | test-only `QZ_SNDLOG` in the engine's StartSound |
| `rig.py` | `run(name, script, secs, extra)`: one engine run on the load order + probe; logs to `build/logs/`. Env: `B22_PK3`, `B22_RIG`, `B22_NOPROBE`, `QZ_RES` |
| `shots.py`, `cmp.py`, `cmp2.py` | frame dumps; `cmp2.py <pkA> <pkB> <Gun,...> <tag> [pose]` = A left, B right |
| `mags.py` | magazine reloads driven by the off hand (`with_pouch` for wells near the rest pose) |
| `pump.py`, `brk.py`, `m203.py`, `grip.py` | pump, break-open, M203 and grip-mode drivers |
| `spintest.py` | walk / fire / reload, logs psp.x/psp.y and flash count |
| `holdtest3.py` | trigger held 140 tics per gun, QZD as is vs upstream attackdown (`build/upstream.pk3`) |
| `probe/` | the `B22 ...` log lines (reload tables, state, shots, psp, casings, axe lock) |

Load order is always doom2 -> brutal22test6 -> BD_VoxelPack -> pack (CLAUDE.md). The full how-to is docs/handbook/02_test_rig.md.
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
- The engine rewrites `bin/config/qzdoom.ini` (tracked) on exit -- on the F12 runs only its first,
  timestamp line. `git checkout tools/rig/bin/config/qzdoom.ini` before committing.
- Never chain pipeline stages with `;` after a failing stage. Use `set -o pipefail` and `&&`.
