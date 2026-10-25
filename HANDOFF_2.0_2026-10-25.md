# ModelSwapper 2.0 — handoff, 2026-10-25 (branch `modelswapper-2.0-bd22-lift`)

**Their code, our models, collective reload.** ModelSwapper stays what it always was — universal 3D
meshes on whatever mod it detects. 2.0 adds, on the Quest build: hands on the meshes, more
reloadable meshes, and VR reloading on any weapon whose mod has a reload of its own. The mod's
code still fires the gun and decides every round; the hands do the physical part.

`main` is untouched. Everything below is on the branch, one commit per step, each gated.

## What works, measured

Gated on stock QuestZDoom 17.3 (emawind84/gzdoom `qzd17.3`, 9afc750), headless, fake VR hands,
with each of our models worn on a **foreign** weapon from `gate/testmod` (a pistol, a pump shotgun
and a double barrel written like any mod's: their own Reload states, their own ammo names).

| reload | models | proof |
|---|---|---|
| magazine | MS_BD22_ Pistol, Rifle, SMG, MP40, AssaultShotgun, RailGun, PlasmaGun, Ruger, RocketLauncher | mag out (sound, old mag drops) → hand carries one → into the well → seated → the mod's own reload refills ITS magazine. Screenshots: gun drawn without its magazine, the new one rising into the well. |
| pump | MS_BD22_Shotgun | the hand takes a shell, pushes it home; the mod's own loop puts exactly one in; 8 pushes → 8 shells → the mod ends its own reload. |
| break-open | MS_BD22_ SSG, Revolver, M79 | open, spent ejected, chambers loaded, closed, handed back, the mod's reload fills. (Hand aim/push driven by the reload's own functions, see Limits.) |

The Ruger is logic-verified only (the flat test camera does not frame it at its scale).

## How it fits together

* **Meshes and measurements: BD22Q's, lifted, not measured.** `models/depot_bd/bd` holds BD22Q's
  meshes byte for byte; ModelSwapper draws BD meshes at BD22's placement; so BD22's reload, hand,
  pump and break rows are copied by `tools_kit/lift_bd22.py`, keyed to a donor model instead of a
  BD22 class. Only fields that named BD22's own items change. Shelf rows are APPENDED (a saved pick
  is an index — inserting would move everyone's picks).
* **The join (`zscript/RS_ForeignReload.zs`)** plays the part a weapon that owns its reload plays:
  * magazine: RSR_Start, **RSR_MagOut** (the drop, its sound, the empty well), hold, RSR_Tick, then
    the mod's own Reload;
  * pump: RSP_LoadStart, hold, RSP_LTick; each RSP_ShellIn lets the mod's loop run until ITS tube
    rises by one, then holds again where it stopped;
  * break-open: RSB_Start, hold, RSB_Tick, per-round tokens cleared, RSB_Done → the mod's Reload.
* **The mod's ammo is the mod's.** Every ModelSwapper row names no ammo; the reloads use the
  weapon's own two stores (`RSR.WeaponStore`: the larger the reserve, the smaller what is loaded).
* **Hands: `MODELDEF.rsq` + `models/rsq`** (Ermac's, RustedLegacy MIT), incl. the reload holding
  poses RQHN I/J/L. **Reload layers: `MODELDEF.bd22`**, re-keyed to the donor (A_ChangeModel gives
  the foreign weapon the donor's MODELDEF, so its layers must be the donor's).
* **Sounds: `SNDINFO.ms` + `sounds/ms`**, from RS_VR_Weapons / RS_VR_Reload, under `ms/`. Option
  **Reload sounds: ModelSwapper / Mod only** (`ms_reload_sounds`).

## Faults found on `main`, each shown by the gate against an unmodified build

1. No reload layer had a model — mid-reload the gun kept its magazine, hand and floor empty.
2. vreload drew those layers only in the weapon's own RSR_Wait; the join parks it in MS_Hold.
3. Reserve was a fixed class name (Clip, Cell…) — any mod naming its ammo otherwise could never take
   a magazine (last session's 26 "carry 0" guns).
4. No SNDINFO: every reload silent.
5. No hand meshes / hand MODELDEF shipped at all — no hands were ever drawn.
6. The join never sent RSR_MagOut — no drop, no mag-out sound.
7. Pump and break-open never handed a foreign gun to their reloads.
"54 of 54 verified" read the phase log, never the screen.

## Build and gate

* Windows: `./build.ps1 -Static` (now ships MODELDEF.bd22, MODELDEF.rsq, SNDINFO.ms, sounds/, and
  packs every model folder ANY shipped MODELDEF names).
* Linux: `python3 -B tools_kit/build_quest.py out.pk3` — the same rules; on clean `main` it
  reproduces the 1540-entry pk3 exactly.
* Gate: `python3 -B gate/run_gate.py <pk3> <donor> [--shots] [--yaw N] [--view "cvars"] [--extra "cmds"]`.
  Chooses the magazine, pump or break flow from the donor's tables; prints PASS/FAIL per step and
  stops at the first script error. `--shots` writes screenshots into `gate/out/<donor>/`.
  Needs a qzd17.3 build (`--engine DIR`) and `freedoom2.wad`.

## Limits — say these before anyone says "done"

* **Nothing here has been in a headset.** Gates prove the logic ran and what was drawn on a flat
  screen; reach, feel and the hand fit are the owner's pass.
* Break-open's hand aim and push are driven by the reload's own functions in the gate, not by a
  scripted hand. That geometry is BD22Q's own, unchanged.
* The pump after a shot is still the mod's own animation (working the forend by hand between shots
  is the next layer).
* BD22's RSQ_Debris blocks are left out: with them the engine hangs after P_Init.
* The other ~200 shelf models are not reloadable yet. Their route: CARD_STANDARD (one WMCARD per
  shipped mesh, with meshid / restframe / surfindex) and `handfit_cards.py` for the hand poses.
* Desktop (UZDXREMA) build: no reload — parked by the owner; RS_VR_Reload is its counterpart.
