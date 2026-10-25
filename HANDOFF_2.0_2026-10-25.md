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

### Aliens set (second lift, `tools_kit/lift_aliens.py`)

| reload | models | source |
|---|---|---|
| magazine | MS_alien_ pistol, rifle, smartgun, flamer; MS_AE_ Pistol, Flamer (re-centred copies) | Aliens Quest set rows, layers (MODELDEF.aliens), hands |
| pump | MS_alien_shotgun, MS_AE_Shotgun | same; 8 pushes, 8 shells by the mod's loop |

* The meshes were already the Aliens set's, byte for byte. The Aliens rows ModelSwapper had came
  from the _wm pipeline (other numbers, and no MODELDEF for their layers at all); they are
  REPLACED IN PLACE (slots 1, 2, 17 keep their numbers). Smartgun is new rsr slot 40, the shotgun
  pump slot 3. Shelf rows untouched.
* Placement: MS_alien_rifle / smartgun / shotgun now draw at the Aliens set's placement (their
  rows and hands are fitted to it). The MS_AE_ copies already did (checked by mesh shift).
* Hands: models/rsq/hand.md3 gained the Aliens set's 10 trigger/squeeze frames, appended
  (`tools_kit/md3_frames.py`: the 46 BD22 frames keep their indices, byte-exact rebuild checked).
  Aliens hand rows re-keyed BY FRAME onto ModelSwapper's letters (RQGS I/J, RQGT/RQGU S..W new).
* Foley: aliases onto the BD22 foley already shipped + the set's own bolt sounds. The TC's own
  sound names are lumps of the TC and are not in any repo.

### The older reload guns (`main`'s), re-made where they are drawn

`tools_kit/placement_audit.py` measured the older rows (slots 3-30) against what is DRAWN: rows
made by genpack/card2quest at the card's placement, several donors per row, each donor drawn at its
own block -- up to 1.4 m apart -- and no MODELDEF for any of their layers (the gun vanished
mid-reload). The hand rows were checked first: their hooks land on the card palm at the DONOR's
placement (brt_RPG 4 cm vs 26 cm at the row's), so the drawing and the hands are right and the
rows are the odd ones out. (A trial that moved the donors instead was measured, found wrong, and
reverted; `rebase_donors.py` stays only as the record of that check -- do not run it.)

`tools_kit/regen_rows.py` runs the kit's own chain (card2quest.geometry -> genpack.build_gun ->
gen_rsr) at each donor's own placement and rest frame. Validated: at the card's placement it gives
back the shipped MS_Pistol row to 0.001 cm. 31 donors whose own card is on their real mesh now have
their OWN row (slots 41-72) and layers (MODELDEF.cards, from their own folder and skin); foley by
gun type. All 31 gated PASS, gun drawn through the reload.

Left on the old rows: donors whose card is a `_wm` rebuild (BD_AssaultShotgun, BD_Flamethrower2,
BD_RailGun, BD_Rifle, BD_Unmaker, MG_Bolter, MG_Tec9, PlasmaRifle, Rifle, RocketLauncher), donors
with no card (brt_ AssaultShotgun / Flamethrower2 / Unmaker / HitlersBuzzsaw, meat_ Bolter / TEC9,
wolf_KAR98). brt_Rifle was refused at first ("evidence disagrees"): ModelSwapper drew it on frame 0,
mid-raise; measured, its rest is frame 3 (card magcenter on the magazine surface, the hand row's fit,
the raise test, BD22Q's own) -- `tools_kit/rest_frames.py` sets it, and it has its own row now (slot 72).
Those need real-mesh cards -- the card standard's job.

## Fixed along the way (each also wrong on `main`)

8. **RSQ_GunMoves was BD22Q's table read by ModelSwapper's slot number.** Pivot (where the hands
   turn with the gun when its layer moves) came from whichever BD22 gun had the same index; slots
   past 26 got nothing. In the gate the hand floated off the gun on EVERY older donor checked
   (MS_Pistol, PlasmaRifle, Rifle, BD_AssaultShotgun, BD_RailGun, AE_Flamer) and on the BD22 pistol.
   `tools_kit/gunmoves_ms.py` computes every slot's Pivot / Mirrored / Blends from its donor's own
   MODELDEF block -- the kit's formula, which reproduces BD22Q's and the Aliens set's own tables
   exactly for every lifted gun (`--check`). After: the hand on the gun in all of them.
9. **89 skins the shipped break/pump MODELDEFs named were not in the pk3** (rsr_clear.png beside
   the MS_Shotgun / SuperShotgun / Revolver / brt_M79 meshes, and `rev.png` where MS_Revolver uses
   WPN-REV.png). The asset check only read modeldef/.bd22/.rsq. Both builds now ship and check
   EVERY root `MODELDEF.*` (a hand-kept list also dropped MODELDEF.aliens once: no gun mid-reload).
   `tools_kit/fix_layer_skins.py` -- re-run after gen_rsb.py / gen_pump.py on the PC.
10. The gate counted pump shells twice (engine log echoed to stdout).

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
* `tools_kit/lift_aliens.py` is a second hand-written lift beside `lift_bd22.py`. The next set
  (Vanilla / V+ / Modern) should make the shared part one tool -- read row, set row, re-key layers,
  hand letters by frame, gunmoves -- with a small per-set config, rather than a third copy.
* The other ~200 shelf models are not reloadable yet. Their route: CARD_STANDARD (one WMCARD per
  shipped mesh, with meshid / restframe / surfindex) and `handfit_cards.py` for the hand poses.
* Every gate log shows `RSQ_Scope.EyeInHandFrame: Unexpected JIT error` (x86 JIT on this Linux
  build; the engine falls back to the interpreter and the run continues). Present on the branch
  before the Aliens work; Quest is arm64 and has no JIT. Not chased.
* The smartgun's hands follow the Aliens set's refit (rear handlebar / brake grip); the flat
  camera cannot show whether that reads right -- headset.
* Desktop (UZDXREMA) build: no reload — parked by the owner; RS_VR_Reload is its counterpart.
