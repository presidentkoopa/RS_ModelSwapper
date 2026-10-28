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
- `rebake.py check` in this checkout: 30 poses rebaked from data; every shipped hand MD3 reproduced to at most
  0.0156 md3 units (one quantum), every MODELDEF / pivot / fire row regenerated equal. VERIFIED.md has the run on
  a fresh clone.

## Not done
- See `docs/handbook/VERIFIED.md` for what the fresh-clone run proved and what it did not.
- The mesh tools (carve, label, card: the old `tools/kit`, `tools/hqt`) are on the archive branch only; F14 needs
  them back, proven, before it starts.

## Open
- Nothing in BD22 2.0.1 has been confirmed in the owner's headset yet (its own README says so).
- Outside the repo by design: the game data (`RSQ_GAMEDATA`), the FBX hand (`RSQ_FBX`), Ermac's models
  (`RSQ_ERMAC`, measuring scripts only).
