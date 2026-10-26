# The VR gate's rig: QuestZDoom 17.3 for Linux, in this repo, ready to run

`gate/run_gate.py --vr` runs here. The engine is Emawind's **QuestZDoom 17.3** (tag `qzd17.3`,
`emawind84/gzdoom` 9afc750, wrapper `emawind84/questzdoom` a85c819): the release the owner and his
players run, compiled for Linux from the Android source set with the Android defines, the real
OpenXR device mode (vr_mode 15) and the real `VrInputDefault.cpp`. Only the OpenXR runtime / JNI
layer is replaced, by `engine/glue/qz_linux_glue.cpp`. TEST ONLY, never ships.

## Use it
    QZ_RIG=$PWD/gate/qz_rig/bin python3 -B gate/run_gate.py <pk3> <model> --vr [--shots]
`bin/` is prebuilt (Linux x86_64; needs Mesa GLES/EGL and OpenAL at run time). `bin/qz` launches it.

## The version guard
`bin/qz` reads `PINS` and **refuses to run** unless the engine binary reports `ENGINE_VERSION` and
`res/qzdoom.pk3` declares `ZSCRIPT_VERSION`. It prints `qz: engine OK: QuestZDoom qzd17.3 ...` on
every launch, so every log shows which engine ran. Why: on 2026-10-26 a rig built from a later,
unreleased engine commit (4.15pre, ZScript 4.12) was in use; ModelSwapper could not compile on it
and every result from it was void, with nothing saying so. Change `PINS` only when the owner moves
to a new QuestZDoom release, and rebuild.

## Rebuild from source (only if bin/ must be rebuilt)
    sh gate/qz_rig/setup.sh
Fetches exactly the `PINS` commits, applies `engine/s_sound_log.patch`, builds into `build/`
(gitignored) with `engine/build.sh` + `engine/Makefile`, checks the result against `PINS`, and
installs it into `bin/`. ~20-40 min. A fresh cloud container cannot apt-install: SDL2, EGL, GLES3
(incl. an empty `GLES3/gl3ext.h`, as Mesa ships), OpenAL and libvpx headers may have to come from
their GitHub sources, with dev symlinks to the runtime `.so` files already present.

## What the glue adds (engine/glue/qz_linux_glue.cpp)
- OpenXR stand-in: head and both controllers posed from cvars (`qz_hmd`, `qz_lhand`, `qz_rhand`,
  triggers, grips, buttons, sticks).
- **Test driver hook**: ZScript may not set an engine cvar, so a test pack defining `qzt_lhand` /
  `qzt_rhand` / `qzt_lgrip` / `qzt_ltrigger` / `qzt_rgrip` / `qzt_rtrigger` in CVARINFO drives the
  controllers instead of `qz_*`. Without such a pack nothing changes.
- `__android_log_write`, and a frame dump: `QZ_DUMP_EVERY=n QZ_DUMP_DIR=<dir>` writes the left eye
  every n-th frame as PPM (the engine's `screenshot` command returns garbage in VR mode).
- Test-only sound log (`s_sound_log.patch`): `QZ_SNDLOG=1` prints every sound start.

## Measured on the rig
Stage -> world is 34 map units per metre, (F, L, U) = (-z, -x, y / pixelstretch) * 34 from the
player's floor point; controller pitch 30 is level. The grip arrives as key 443, the off trigger as
key 42 -- the keys the reload already listens for. Screenshots are the eye buffer (1024 x 1024);
`--shots` tilts the head 40 degrees down to look at the hands (QZ_SHOT_HMD).

## Traps
- `-warp 1` is required with BD22 (its title map swallows `+map`, and its AimingCamera stops VR attaching).
- Load order is always doom2 -> the parent mod (e.g. brutal22test6 -> BD_VoxelPack) -> the pack.
- Running the engine creates `bin/libGLESv3.so` and may write `bin/config/qzdoom.ini`; the first is
  gitignored, and the gate runs with its own `-config` copy so the committed ini stays as it is.
