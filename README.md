# RSQ Weapon Depot

The workshop where Doom weapon sets become VR weapon sets for **QuestZDoom 17.3**: hands on every gun, the
finger on the trigger, reloads done with your hands, live scopes, melee. No engine changes: everything ships
as ZScript, DECORATE, MODELDEF and models that run on a stock QuestZDoom 17.3.

The finished example is **BD22 VR Weapons Q 2.0.1** (`sets/bd22q`). The other sets are waiting to be taken
through the same process.

**Start with the handbook: [`docs/handbook/README.md`](docs/handbook/README.md).**

## The layout

| path | what |
|---|---|
| `sets/bd22q/` | BD22 VR Weapons Q 2.0.1, copied from [presidentkoopa/RS_Brutal22WeaponsQ](https://github.com/presidentkoopa/RS_Brutal22WeaponsQ) `main` at b360875: `src/` (the pack), `build.py`, `VERSION`, its own `README.md` and `CLAUDE.md`, its set-only tools (`tools/`: hand tones, HUD, Moonlight ammo), its hand-fit data (`handfit/poses`, `handfit/fits`) and the 1.92 holds rendered (`reference/192_poses`, where every 2.0 grip started). Its history, handoffs and renders stay in that repo. |
| `sets/vanilla/` `sets/vanilla_plus/` `sets/modern/` | the c2q-built sets (were `vanilla_0.9`, `plus_0.7`, `modern_0.9`). Built from REMA's single-frame `_wm` meshes, so every gun is a still: they are rebuilt from the animated originals, never patched. |
| `sets/aliens/` | RS_Aliens_VR-WeaponsQ @ 1ee0cd2, verbatim. |
| `sets/rusted_legacy/` | Ermac's Rusted Legacy dev build, measured (S4): cards, sheets and `tools/rl_measure.py`. His files stay outside the repo (`RSQ_RL`). |
| `tools/rig/` | the QuestZDoom 17.3 test rig for Linux (prebuilt `bin/`, version-guarded by `PINS`), its drivers and probe. |
| `tools/handfit/` | hand fitting: the fitter core (`core/`), the gun port (`port/`), support hands (`support192/`), off-hand holds and fists (`offhand/`), grenade, melee, the PC fit farm (`farm/`), and the shared modules (`fitter_lib/`, `heavies/`, `shotguns/`). |
| `tools/scope3x/` | the live 3x scope rig driver and its measurement. |
| `tools/int20_rig/` | the whole-pack checks: sweep, held frames, hand reloads, dual wield, MODELDEF slot check (`mdslots.py`), variants. |
| `tools/depot.py` | every path the tools use: Depot-relative, or set by an environment variable. |
| `tools/check_plan.py`, `tools/commit-msg`, `tools/install_hooks.sh` | the no-drift hooks. |
| `sources/pbvp_v2/` | Project Brutality Voxel Patch v2, verbatim (credit required; `PROVENANCE.md`). |
| `docs/handbook/` | how VR weapon mechanics are built on QuestZDoom 17.3, and `VERIFIED.md` (the handbook followed on a fresh clone). |

Everything removed on 2026-10-28 (the old c2q pipeline, the 1.97 build, the gate, the old docs, the
earlier hand-fitting kits) is kept on the branch **`archive/depot-2026-10-28`**.

## Outside the repo, on purpose
- The owner's game data: `doom2.wad`, `brutal22test6.pk3`, `BD_VoxelPack.pk3` (`RSQ_GAMEDATA`).
- The FBX hand, `hand_final.fbx`, is in the repo at `tools/handfit/core/fbx_hand/` (`RSQ_FBX` overrides it).
  Only baked MD3 frames ship in a pack.
- Ermac's Force Unleashed models (`RSQ_ERMAC`): only the measuring scripts read them.
