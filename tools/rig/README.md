# tools/rig: testing bd22q in the owner's quest_test_rig (TEST ONLY, never ships)

The real QuestZDoom 17.3 engine, built for Linux, on the OpenXR path, with controller poses set
from cvars. It ran every check in the 1.99 work. These are the scripts and the rig changes, as
used in the cloud session of 2026-10-25/26.

- `rigtest/` + `rig2/`: the owner's quest_test_rig (real QZD 17.3 OpenXR path, poses from cvars).
  `rig.py run()`. Set `B22_NOPROBE=1` to run old packs, whose class names the probe doesn't know.
- **Frame dumps (new, this session):** `rig2/glue/qz_linux_glue.cpp` writes the left eye every N
  frames when `QZ_DUMP_EVERY=N QZ_DUMP_DIR=<dir>` are set (PPM). Use `QZ_RES=480`.
  `rigtest/shots.py shoot()` wraps it. The gun hand pose `qz_rhand "0.0 1.68 -0.40 20 -70 0"`
  shows the held gun and hand side-on, in front of the eye. **Use this to compare 1.92
  (`gate_out/BD22Q_192.pk3`, built from tag 1.92) against current, gun by gun, before changing
  anything.**
- `rigtest/holdtest3.py` (fire rates), `spintest.py` (gun offset, flashes), `mags.py` (reloads; use
  `with_pouch`), `probe/` (`B22 W/SHOT/PSP/LOCK/AXE` lines).
- Load order is always doom2 -> brutal22test6 -> BD_VoxelPack -> pack (CLAUDE.md rule 5).

## What is here, and where it lived in the session
| here | session path | what |
|---|---|---|
| `rig.py` | `rigtest/rig.py` | `run(name, script, secs, extra)`: one engine run, load order + probe, logs to `rigtest/logs/`. Env: `B22_PK3`, `B22_RIG`, `B22_NOPROBE`, `QZ_RES` |
| `shots.py`, `cmp.py` | `rigtest/` | frame dumps; `cmp.py <pk3> <Gun,Gun,...> <tag>` renders each gun held, 1.92 left, given pk3 right |
| `mags.py` | `rigtest/` | magazine reloads driven by the off hand (`with_pouch` for guns whose well is near the rest pose) |
| `spintest.py` | `rigtest/` | walk / fire / reload, logs the gun layer's psp.x/psp.y and flash count |
| `holdtest3.py` | `rigtest/` | trigger held 140 tics, one gun per run, QZD as is vs upstream attackdown |
| `upstream_zscript.txt` + `upstream_MAPINFO.txt` | `rigtest/upstream/` | zip as `upstream.pk3`: emulates upstream GZDoom's attackdown (for holdtest3) |
| `handrot.py`, `pump.py`, `brk.py`, `m203.py`, `grip.py` | `rigtest/` | off-hand pose maths and the pump / break / M203 / grip-mode drivers |
| `probe/` | `rigtest/probe/` | zip as `probe.pk3`: the B22 log lines (tables, state, shots, psp, axe lock) |
| `glue/qz_linux_glue.cpp` | `rig2/glue/` | the rig's OpenXR stand-in, WITH the frame-dump patch |
| `config/qzdoom.ini` | `rig2/config/` | the test ini (`playerclass=$TAGBD_CLASS_RIFLE`; NOTE it carries `rsvr_axe_hold=16`, the old default) |
| `s_sound_log.patch` | rig engine `src/common/audio/sound/s_sound.cpp` | TEST ONLY: `QZ_SNDLOG=1` prints `QZSND <tic> <sound> ch vol src <class>` for every sound start, even under -nosound (for item 18, the bang on map load). Apply to the rig's engine tree, relink |
| `Makefile.rig`, `build.sh.rig` | `rig2/` | the rig build. Relink after a glue change: `make QGZ=<gzdoom questzdoom> JNI=<questzdoom>/Projects/Android/jni DEPS=<rig2>/deps ZLIB=<rig2>/deps/zmusic-install/lib/` |

## Traps (each cost a run)
- `-warp 1`: BD22's title map swallows `+map` and its AimingCamera stops VR attaching. `QZ_RES=200`
  for speed, 480 for pictures.
- `playerclass=$TAGBD_CLASS_RIFLE`, or you get a random class (Purist has no reload).
- `rsq_extra_weapons 1` for the hidden guns. `give <class>` explicitly; `give all` gives Purist guns.
- The off hand is the gun hand mirrored in L; side wells need a 180 degree yaw (`mags.at`).
- `CanTakeMag` refuses a hand within 20 cm of the magazine (`POUCH_MIN`): reach to a pouch first.
- Give a gun ~150 tics to finish its select animation before testing it.
- Never chain pipeline stages with `;` after a failing stage (a failed apply + sync emptied the
  set once). Use `set -o pipefail` and `&&`.
- The engine's `screenshot` command returns garbage in VR mode; use the frame dump.
