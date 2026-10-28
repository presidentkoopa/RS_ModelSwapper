**NO DRIFT. FOCUS ON WEAPON SET PRODUCTION.**
**USE TOOLS IN REPO. NOWHERE ELSE.**

# RSQ Weapon Depot: HANDOFF (2026-10-28, owner: presidentkoopa)

**State in one line:** the Depot is now the workshop. It holds the sets, BD22 VR Weapons Q 2.0.1 as the finished
example, the toolset proven on BD22, and the handbook. Everything older is on `archive/depot-2026-10-28`.

## Done (measured)
- W1, the layout (2026-10-28). See README.md "The layout". The archive branch `archive/depot-2026-10-28` = old
  `main` db001eb (confirmed with `git ls-remote`).
- `sets/bd22q` = RS_Brutal22WeaponsQ `main` b360875 (2.0.1): `src/`, `build.py`, `VERSION`, `README.md`,
  `CLAUDE.md`, set-only tools, `handfit/poses` and `handfit/fits` (the fit records the port tools read).
- `tools/handfit/core` = the hand-fitter core that every BD 2.0 hand was solved with (the cloud folder
  `lane_c/hands_tool` and the measured data it reads), now in the repo. The 1.92 pack it measures against is
  the tag-1.92 checkout `sh tools/rig/setup.sh` makes (`RSQ_GUNPACK`).
- Every tool path is Depot-relative or an environment variable (`tools/depot.py`).
- The handbook (`docs/handbook/`, README + 01-07 + SKILL.md) followed on a fresh clone of `dc3bb6f`
  (`docs/handbook/VERIFIED.md`): rig setup, BD22 2.0.1 booted on doom2 -> brutal22test6 -> BD_VoxelPack -> pack
  with 0 pack script errors, `rebake.py check` (30 poses, every MD3 within one quantum, 0 MODELDEF mismatches),
  the Rifle's frames and hand reload, a 3-gun sweep, `mdslots.py` 0 bad, `variants_all.py` 0 differ. Rig only.
- `sets/bd22q/reference/192_poses` = the 1.92 hold renders (from the old `docs/reference/bd22q_192_poses`):
  kept because the method starts from them and `gate_gun.py compose` reads them.

## Not done
- Not re-run after the move (compiled, paths moved): the fitters (`fit_hv.py`, `fit192.py`, `hold_fit.py`, the farm),
  the scope driver, `rsweep.py`, `dualsweep.py`, `f20all.sh`. `VERIFIED.md` "Not verified here".
- `tools/handfit/farm/pack_farm.py` still packs the old cloud layout; point it at `tools/handfit/core` and `$RSQ_SET`
  before the next farm run.
- `fitter_lib` reads old batch 1-4 stage files from `RS_FITTER_HOME` (default `work/fitter_home`); the ones the BD22
  port needs are in `sets/bd22q/handfit/fits/`, the rest only on the farm's mirror.
- The mesh tools (carve, label, card: the old `tools/kit`, `tools/hqt`) are on the archive branch only; F14 needs
  them back, proven, before it starts.

## Open
- Nothing in BD22 2.0.1 has been confirmed in the owner's headset yet (its own README says so).
- Outside the repo by design: the game data (`RSQ_GAMEDATA`), the FBX hand (`RSQ_FBX`), Ermac's models
  (`RSQ_ERMAC`, measuring scripts only).
