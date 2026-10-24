**NO DRIFT. FOCUS ON WEAPON SET PRODUCTION.**
**USE TOOLS IN REPO. NOWHERE ELSE.**
(owner, 2026-10-24 04:39 -- these two instructions stand above everything else in this repo)

# RSQ Weapon Depot — HANDOFF (2026-10-24 04:40, owner: presidentkoopa)

**Addressed to: the next Claude session, any coding agent, and the local coding team.** `CLAUDE.md` at the
root is the ten rules; this file is the state. Both are binding.

**Read this whole file before touching anything. Then read `PLAN.md`. Do not drift from the plan.
`tools/check_plan.py` is run before every commit (pre-commit hook, see "No drift") and refuses work
that is not on the plan.**

## What this repo is
Everything for QuestZDoom 17.3 VR reloadable weapon sets: the owner's BD22 Quest pack as the runtime
base, the card→Quest pipeline, every set built so far, the engine gate, the source docs. One repo.
Nothing lives anywhere else.

| path | what |
|---|---|
| `runtime/` | RS_Brutal22WeaponsQ **1.96b** `src/` snapshot (commit 27bef2b). The base of everything. Never edited in place. |
| `sets/bd22q_1.97/src/` | **The flagship.** 1.96b + tonight's additions (below). Built by `tools/bd22_plus.py apply` then `tools/bd22_mg.py`, from `runtime/` — never by hand. |
| `sets/bd22q_1.97/carved_models/` | HitlersBuzzsaw / Flamethrower2 `_carved.md3` (drum, canister as own surfaces; all frames), `*_rsr.md3` shipped copies. |
| `sets/bd22q_1.97/_hands/Machinegun.png` | hand-fit sheet for the Machinegun (palm, support, latch, breech marked). Owner signs or rejects. |
| `sets/vanilla_0.9` `plus_0.7` `modern_0.9` | the c2q-built sets (genpack → assemble → check → mkpk3). Vanilla = Doom's eight, Doom's names/numbers, RSQ_Player start pistol. Renamed from `vanilla` / `plus` / `modern` with their versions on 2026-10-24 (owner); the tools take the set as an argument and build into `<out>/RSQ_<set>`, so nothing in `tools/` reads these folder names. |
| `sets/aliens/` | presidentkoopa/RS_Aliens_VR-WeaponsQ @ 1ee0cd2 verbatim (588 files, 34 MB), 2026-10-24, PLAN.md's S4. Parent mod: Aliens Eradication TC 2.0; this pack replaces its `_A03` VR addon rather than loading beside it (`README.txt`). |
| `dist/` | `RSQ_vanilla.pk3` (gate 5/5), `RSQ_plus.pk3`, `RSQ_modern.pk3` (older builds, no player class yet). The 43 MB BD22Q pk3 is NOT committed: build it (`tools/bd22_plus.py pk3 <out>`). |
| `tools/` | the pipeline (`README.md` there). `kit/` = keeper tools from the Quest_Weapons_Kit (gen_rsr.py, rgeo.py …), `rtest/` = behaviour harness port (shelved: times out after S_Init). |
| `gate/run.sh` | the engine gate (see below). |
| `docs/` | BD21 `Machinegun.txt`, `Revolver2.txt` (owner-supplied parent files), `VR_MELEE_ON_QUESTZDOOM_2026-10-24.md`, `HANDS_IN_THE_MESH.md`, `KIT_INVENTORY.md`. |

## State of the flagship (bd22q 1.97-pre) — measured, not remembered
Base 1.96b: 26 BD22 weapons, hands on all 26, 17 reload entries (9 magazine, 2 pump, 6 break = every
reload Brutal Doom itself has), dual on 10 guns, melee (axe swing/throw, punch, punch-switches, VR
throw), options page, ballistics switch (global, off = stock BD22).

Added tonight (all generated, all exact-match edits, logs in `sets/bd22q_1.97/*.json`):
1. **MG42 belt drum, Flamethrower canister, Unmaker skull — real VR reloads** (`bd22_plus.py`).
   Brutal Doom never reloads these; REMA's bd22 set does. Meshes carved by reference against REMA's
   `*_wm.md3` (same vertices, residual 0.0000). Well/axis/mouth from the card axis + the kit's own
   `mouth_depth`. Entries 10–12 appended to `rsr_guns.bd.zs` (merge, no regeneration of 1–9),
   `MODELDEF.rsr` blocks from gen_rsr. DECORATE: `Reload:` + RSR states added to `MG42.dec`,
   `Flamethrower.dec` (its `Reload:` alias of ReadyDry removed), `Unmaker.dec`; a guard
   `RSQ_Empty_<gun>` before every shot. **Counter model** (`zscript/rsq/counters.zs`): the drum is a
   count over BD22's own ammo; BD22's firing/reserve untouched; idle unless VR reloading is on.
   Capacities 200/200/60 are the owner's REMA sheet numbers (BD22 has none). **Not yet played in a
   headset.** Known gap: a dropped partial drum costs the reserve nothing (flagged in the .dec).
2. **BD21 Machinegun** (`bd22_mg.py`): BD21's `Machinegun.txt` verbatim except sound renames
   (GRLLO1/2→Rifle/Grenade1/2, insertshell→GrenadeLauncher/Load, weapons/empty→Weapon/Empty) and the
   `1.97 rsm` lines. Mesh BD21's own (br_vr), frame 4 = REMA's `machinegun_wm.md3` exactly (t = 52.88 F).
   Launcher on the pack's own M203 module, made per-gun (`RSM.GunOf`: 1 rifle, 2 machinegun;
   `RSM_Geo.*(gun)`; `RSM_NoTube.NamesMG`; layers `RQ3P`). Tube F 29.27→63.86, travel 9.69 (card 9.50),
   bore L −0.07 U −1.52. Ammo follows "Rifle Underbarrel Ammo". Hands: MG42's letters (F/F/B/I), ICP
   on the card's palm/supportat (1.29 / 1.16 cm). Slot 4 (`KEYCONF.rsq addslotdefault`). Dummy sprite lumps
   for MGN1/MGN2/MGS1 (HUD is the MD3); floor pickup = gun mesh block (no MGN1 Z sprite in BD22).
   Menu row **"Machinegun replaces MG42"** (`rsq_mg_replaces_mg42`, server, off) via `zscript/rsq/roster.zs`
   CheckReplacement. **Runs in the engine as of 2026-10-24** (see "F1 IS DONE"); not yet in a headset.
3. Vanilla set rebuilt as Doom's eight with `RSQ_Player` (start pistol, pickups measured). Gate 5/5.

## F1 IS DONE (2026-10-24, the owner's PC) — the pack runs on his load order
`dist/BD22Q_197pre.pk3`, 45 MB, 459 lumps. One launch on doom2.wad → brutal22test6 → BD_VoxelPack →
the pk3: **exit 0, GATE_START / GATE_FIRE / GATE_DONE, `script parsing took 3669 ms`, and not one
Script error or warning from `BD22Q_197pre`.** The nine warnings and four `voxeldef.txt` errors left in
the log belong to the parent load order (BD_VoxelPack's voxeldef lines 66/72/77/892 are malformed
entries in that file; BD22's own `23Player.dec` still calls `SubMachineGunSelected`).

Four faults stood between the committed set and a load. None of them could ever have loaded, which
matches "the gate run was interrupted" above. Each was fixed in the generator, never in `sets/`:
1. `rsr_m203_geo.zs`: `const TRAVEL` beside the generated `Travel(int gun)` — ZScript identifiers are
   case-insensitive, so "Attempt to redefine 'travel'". The accessor is `TravelOf` now; the other
   seven constants have an underscore and do not collide.
2. `rsr_m203.zs`: `RSM_Geo.X(gun)` inside `RSK_M203Handler.Place` — "Unknown identifier 'Gun'". `gun`
   is a field of `RSM_State` alone; elsewhere the state is a local `s`. The rewrite was a line-local
   lookahead for `s.` on the same line and missed Place's three `return` lines. Class-span aware now,
   and it refuses to finish if a bare `(gun)` is left outside `RSM_State`.
3. `rsr_guns.bd.zs`: `merge_tables` merged the switches but not `RSR_GunSprites`. The pack ships no
   `RQ**` lumps — a sprite name is known to the engine only if some actor's states use it — so
   MODELDEF died on "Unknown sprite RQXM in model definition for MG42". gen_rsr already writes that
   list; the merge appends its nine lines.
4. `KEYCONF.rsq`: `addslot 4 Machinegun` — no such KEYCONF command. `addslotdefault`, which the pack's
   own slot-1 line already uses, appends to BD22's `setslot 4 … MG42` instead of replacing it.

Two more, while there: `SubMachineGunSelected` → `SMGSelected` (BD21's name; brutal22test6 defines the
short one and never the long — parsed from every `actor <name>` in the pk3), and `bd22_mg.py` now
writes the `.generated` stamp `check_plan.py` looks for, which no tool wrote before.

**`runtime/` is NOT the 1.96b snapshot it claims to be** — 34 files / 1.1 MB, 33 of them a strict
subset of `sets/bd22q_1.97/src` (459 files / 85 MB), missing every mesh and every file the generators
read. `SRC` therefore points at a clone of **presidentkoopa/RS_Brutal22WeaponsQ @ 27bef2b** in
`E:/DOOMWork/_buildtemp/rs_brutal22weaponsq/src/` (406 files). Either fill `runtime/` from that commit
or keep `SRC` where it is — but do not trust `runtime/` as the snapshot.

**One number to check in the headset.** The tools measure the Unmaker's skull well at
`11.788 0.614 12.329`, insert depth `4.61`, off the shipped mesh. The committed `plus_geometry.json`
recorded `11.814 1.253 12.280` / `4.66`, and nothing in the repo reproduces it: all three copies of
`Unmaker_rsr.md3` are byte-identical and all give the new numbers. 0.64 cm in where the skull seats.
The regenerated numbers are what ship. Everything else in the set regenerates identical, bar line
endings on three `.dec` files (the generators run on Windows now).

Still open, for the owner, not the tools: the gate is a desktop run, not a headset pass — the four
things to try are the MG42 drum, the Flamethrower canister and the Unmaker skull reloads, and the
Machinegun launcher (open, load, close, fire). Also: `RSQ_Scope.EyeInHandFrame: Unexpected JIT error:
Unknown REGT value passed to EmitPARAM` is in 1.96b's own scope code, untouched by this work.
Minor: the pre-commit hook's shebang is `#!/usr/bin/env python3` and this PC has `python` / `py` only,
so commits here need a `python3` on PATH.

## Paths, now set for this PC (committed, `[step F1]`)
`bd22_plus.py` / `bd22_mg.py`: `TOOLS`/`KIT` from `__file__` (`tools/`, `tools/kit`); `SRC` → `runtime/`;
`REMA` → `E:/DOOMWork/RS_VR_Weapons/bd22/`; `BR` → `E:/DOOMWork/VR_WeaponSetRebuild/br_vr/PK3_pbr/`;
`BD21` → `docs/BD21_Machinegun.txt`; `OUT` → `E:/DOOMWork/_buildtemp/rsq_bd22/` (outside the repo, so
the hook sees no new top-level directory); new `BD22SRC` → `E:/DOOMWork/_buildtemp/bd22src/`
(brutal22test6.pk3's `actors/Weapons/*.dec`, extracted) in place of the hardcoded `/home/claude/bd22src/`.
`genpack.py`, `handfit_cards.py`: the two kit paths that blocked `import bd22_mg` → `tools/kit`.
`gate/bd22_gate.sh`: `QZD17-engine/build/Release`, its `doom2.wad`, `E:/DOOMWork/brutal22test6.pk3`,
the owner's `BD_VoxelPack.pk3`. Both tools import clean and every path they hold resolves.

## F2, done (2026-10-24) — the slug revolver and the feed option
New stage `python tools/bd22_plus.py revolver`, run **after** `bd22_mg.py`. `rsb_guns.zs` says it is
generated by `tools/gen_rsb.py`, which is in no checkout here, and `assemble.py` only stubs the
table — so this stage appends to it the way `merge_tables` appends to `rsr_guns.bd.zs`: indices 1–6
are never touched and the 2026-10-13 speedloader patch survives. Against 1.96b's file the diff is
additions plus exactly one changed line, the `Revolver` line of `Index()`.

- **Shot/Revolver Reload: Speedloader / Per Round** (`rsb_revolver_feed`, server, 0 = speedloader as
  1.96b shipped) — covers BOTH revolvers. Index 7 is BD22's Revolver loaded a round at a time:
  index 3's rows with `Chambers 5`, `Loader false` and the five chamber seats.
  **Server, not user**, because `Index()` is `clearscope static` with no player to read a user cvar.
- **The fifth chamber seat.** The speedloader patch overwrote `Base/Tip` k=0 with the mean of the
  five rims, so it is recovered as `5*mean − the four rows the patch left`, then checked before use
  against the cylinder itself: the five sit at 71.6/72.0/72.2/72.4/71.8° on radius 1.671 cm, spread
  0.042 (Tip: 1.676, 0.064). **The stage refuses to write if that check fails.** `Bore` and
  `Rest0/1/2/RestT` are identical across all five chambers in the shipped table, so they are copied.
  `HandBase/HandTip` are carried from index 3 — the patch recentred them on the cylinder's axis and
  the pre-patch pair is not recoverable, but they describe a 9.6 cm round in the hand, which is the
  same round either way (chamber length `Tip − Base` = 9.596).
- **The slug revolver**: BD21's `Revolver2.txt` verbatim bar the renames, RSB indices 8 (speedloader)
  and 9 (per round) — index 3's rows with `Reserve "Clip2"` (its own `Weapon.AmmoType1`) and
  `Cls 'Revolver2'`. It shares BD22's Revolver sprites and mesh, so **no sprite lumps and no MODELDEF
  of its own**: br_vr's `Modeldef.Revolver.def` binds both names to the same `Revolver.md3`, and
  REMA's `revolver_wm.md3` is that mesh already labelled. Slot 2, and
  `rsq_slug_replaces_shotvolver` (server, off) in the roster handler beside the Machinegun's.
- Sounds, each right side found in brutal22test6's SNDINFO and each left side absent from it:
  REVOFIR→Revolver/Fire, REVOHAM→Revolver/Hammer, REVOFIRpump→Revolver/Hammer, insertshell→
  Revolver/Reload, weapons/empty→Weapon/Empty, KICK→Kick/Swing. RELO1/RELO2 are in BD22 and stay.
  `Tired` is not in BD22's SNDINFO either, but BD22's own AssaultShotgun/Axe/Grenades play it at
  StopSprintTired, so the parent's line stands. The dead `PuristGun` state is dropped (it gives
  `ClassicShotgun`, which BD22 never defines, and nothing jumps to the label).
- Also learned: MENUDEF `OptionValue` takes `0, "Text"` — `0 = "Text"` kills menu init with **nothing
  in the log**; the engine simply stops after `M_Init: Init menus.`

**What the headless gate cannot prove.** RSB only engages when `RSR_ReloadHandler.Wanted()` is true,
and that needs `RSVR_VRHand.InVR`. The gate runs `+vr_mode 0`, so `RSB_Start` falls through to
`RSB_Stock` every time and what runs is each gun's own stock reload. **Every VR reload in 1.97 — the
F1 drum, canister and skull, and both revolvers — is still only testable in the headset.** The gate
proves the pack loads, the guns compile and select, and nothing faults when they fire and reload.

## F3, done (2026-10-24) — four rows the options page was missing

> **The shared-page standard does not apply to this pack. Do not apply it again.** `tools/README.md`
> ("The options menu standard") says one runtime page called **RS VR Weapons** with each set's rows
> in an `AddOptionMenu` block, so several packs loaded together share one page, and PLAN.md's F3 line
> named it. It was applied on 2026-10-24 and reverted the same day: **the owner never loads two packs
> together**, so it bought nothing and cost him his own menu. The page keeps its name
> (`Submenu "BD22 VR Weapons"`), its `Title "BD22 VR WEAPONS"`, and its order. The README is wrong
> for this pack — it was never the owner's standard.

What `python tools/bd22_plus.py options` does, and all it does, is insert four rows the page was
missing. It runs **last**, after `bd22_mg.py` and `revolver`, which add their own rows by anchors.
Each insertion is after a named existing line; nothing is reordered or renamed.

Three were for cvars the pack already declared:
**New magazine from** (`rsr_pouch` — its `OptionValue RSR_Pouch` was defined and *no row used it*),
**Reload assist** (`rsr_assist`), **Melee swing strength** (`rsvr_melee_swing`). The stage refuses to
write a row for a cvar no CVARINFO declares. Slider ranges are the code's own, not chosen:
`rsr_assist` is `clamp(x, 0.5, 3.0)` in `rsr_assist.zs`; `rsvr_melee_swing` is `max(0.2, x)` in
`melee.zs`, which fixes the floor but no ceiling, so the 3.0 is a menu limit only and the console can
still go higher. **"Reload: tuning and debug" now has a row** — `OptionMenu "RSR_Debug"` existed in
1.96b and nothing opened it, so it was unreachable, and a console is no use in a headset.

Gated on the owner's load order: both pages opened in a run (`openmenu RSQ_Options`,
`openmenu RSR_Debug`) with nothing logged against either, and the restored page loads clean. **The
layout itself is the owner's headset pass**, as the plan says.

## F4, done but for "the spike" (2026-10-24) — bash, whip, butt strike
All three melee moves built. Stages `bash`, `whip` and `butt`, all run after `options`. **Switch-punching with either hand was already built** — `zscript/rsq/fists.zs` runs an
`RSQ_FistHand` for `mainH` and `offH` and the same path ends in `PunchUse`, so F4's fourth item
needed nothing. **"The spike" is still undefined**: the word appears only in PLAN.md and in the
sentence HANDOFF copied from it — not in brutal22test6, not in the pack, not in the melee doc.

**The gun bash** is a BUTTON, not a gesture, and deliberately: a gun is a thing you hold still and
point, so gesture detection on one starts worse off than the axe did, and the melee doc's trap table
is largely BD22 learning that (speed alone made *raising* the axe a hit; `rsvr_melee_up` at 0.55
still cut on the upswing). BD22's own kick is the trigger — `+zoom` gives `Kicking`, DEFAULTWEAPON's
Ready jumps to `DoKick` — so a three-line branch at the top of `DoKick` asks ZScript, and BD22's
whole kick body is kept behind `RSQ_BashStock`. Out of VR, option off, or a melee weapon in hand and
the boot runs untouched. **BD22's own `KickAttack` still decides the result**; what changes is no
`KickFlash` (no boot over the gun), a lighter quake, and the impact effect. The mid-tic question
uses the pack's own idiom from `rsr_break.zs`: `Inventory.TryPickup` runs *synchronously* inside
`A_GiveInventory`. **Load order forces where classes live** — ZSCRIPT compiles before DECORATE, so
`RSQ_BashAttack` must be DECORATE to inherit `KickAttack`, while anything reading a cvar is ZScript;
DECORATE can name a ZScript class, not the reverse.

**The impact**: the owner's five from RS_CombatFX (RSS3, RSU1, RSU4, RSU5, RSH0), 44 frames. Each
actor's `Scale` is computed from its own art so all draw at **RSH0's 96 px frame, the owner's
standard** (2026-10-24): RSS3 0.384 from 250 px, RSU1 1.6 from 60, RSU4 6.4 from 15, RSU5 0.857 from
112, RSH0 1.0. RSH0's red is what his headshot mod uses, so it is tintable (Original/Blue/Green/
Amber/White) by a luminance ramp in `TRNSLATE.rsq`. Drawing every candidate at one size is what
ruled the others out — RSU0/RSU4 are 5×5 and RSU3 13×12 natively, and they turn to mush at 96.

**The pistol whip** IS a gesture: a pistol is the one gun you genuinely swing. Two more kinds in
1.96b's own `melee.zs` (nine exact-match edits), reusing its body-frame sample history, its gates
and its swept segment. `BladeIn`/`BladeOut` are raw md3 coordinates **at the gun's ready frame**,
which is not frame 0 — it is whatever MODELDEF binds the Ready sprite to:

| gun | ready sprites | frame | in | out |
|---|---|---|---|---|
| BrutalPistol | PIST / 2IST | 3 | 26.2, 0.0, −7.0 | 44.2, 0.0, −0.2 |
| Revolver, Revolver2 | REVO / 2EVO | 0 | 29.4, 0.1, −1.5 | 50.2, 0.0, 2.4 |

Measuring the pistol at frame 0 would have put the segment in a stowed pose (it reads U −28..−10
there). Revolver2 has no Model block of its own and rides the Revolver's by sprite, so the slug
revolver whips too. `WHIP_SWING` 3.2 m/s against the axe's 3.0; the result is BD22's own
`MeleeStrikeNormal` / `MeleeStrike1Berserked`, which is what `fists.zs` already lands.

**The two-handed butt strike ships OFF** (`rsq_butt`, default 0) — of the three it is the one most
likely to misfire, so it is the player's choice. Four more kinds in `melee.zs`. **Two hands cannot
be the gate**: two hands on a rifle is how you *hold* a rifle, so "two hands + motion" is precisely
the false-positive case, and the axe's must-point-**down** test is exactly wrong because this blow
drives forward and up. What separates it is the **butt leading** — the gun pivots about the front
hand, so the stock outruns the muzzle; walking moves both ends alike (already cancelled by the body
frame) and raising the gun moves both. So: `RSVR_VRHand.Steadied` (the engine's own
`WF_TWOHANDSTABILIZED`, the same flag `hands.zs` draws the support hand from), the butt moving
forward by `rsvr_butt_fwd` (0.5), and the butt outrunning the muzzle by `rsvr_butt_lead` (1.3). That
needed a second tracked end, `prevRelIn`. The result is BD22's own `KickAttack` /
`SuperKickAttack` — what a stock to the face is, and what the bash already lands.

Ready frames came the way `bd22_mg.py` found the Machinegun's: REMA's `<gun>_wm.md3` is the gun at
its ready pose **in its own coordinate frame**, so the frame is the one with the lowest residual
*after a rigid fit* — all four at 0.0000. A raw vertex compare gave 22–52 and picked wrong. Several
frames tie at 0.0000 because the idle pose repeats, so the frame is not unique but the geometry is.
These guns' Ready states say `"####"` and name no sprite, so the pose check gates on each gun's own
idle sprite, read off the MODELDEF lines pointing at that frame — never the shared `PLAY` / `RIFF`.

| gun | sprites | frame | in (toward muzzle) | out (the butt) |
|---|---|---|---|---|
| Rifle | RIFG / 2IFG / RI2G | 3 | 25.1, 0.1, 6.3 | 2.5, 0.5, −1.0 |
| Shot_Gun | SHTN / 2HTN / SHTA | 4 | 23.7, 0.0, −5.4 | 0.9, 0.0, −10.7 |
| SSG | VSSG / SHT2 / VSHZ | 1 | 27.9, 0.1, −2.8 | 15.3, 0.1, −7.0 |
| AssaultShotgun | USAS / 2SAS / A12P | 4 | 20.0, 0.0, −2.6 | −1.7, 0.0, −6.0 |
| MP40 | MP40 / MP42 / PP40 | 2 | 24.8, 0.2, −3.1 | −1.2, 0.0, −3.5 |
| BrutalSMG | SMGF / SMGR / VSMG | 3 | 18.6, −0.3, −1.2 | 0.6, 0.0, −10.4 |
| Machinegun | MGN1 | 4 | 20.1, 0.0, 4.3 | −1.4, 0.0, 2.0 |

Seven. The Machinegun is one sprite, not three — it is BD21's and has no dual — and its butt is
measured off `M249_lowpoly` **alone**, because the model carries an `alt-` block of 4694 vertices
about 40 units below the gun and a span over everything measures the pair, not the gun. Its
segment is 21.6, inside the other six's 13.3–26.0.

**Both of the two that would not fit are in now, and the reason I first gave was wrong.** I wrote
that their fit (residual 11.26 and 24.26 against everyone else's 0.0000) meant "the lookup is
finding the wrong model". It is the right model. The fit stacks every surface's vertices in order and calls the
correspondence identity, and **these two files split the mesh differently from REMA's**:

| | pack | REMA `*_wm.md3` |
|---|---|---|
| `Machinegun.md3` | 6 surfaces `[104, 1014, 106, 3470, 58, 11996]` | 7 surfaces `[104, 1014, 106, 3470, 58, 415, 11581]` |
| `HitlersBuzzsaw.md3` | 2 surfaces `[18912, 60]` | 3 surfaces `[3059, 15853, 60]` |

Same total either way — 16748 and 18972 — so the stack is the same length and nothing complained,
but the body's vertices are not in the same order and one rigid transform over the lot is
least-squares nonsense. Fit only the surfaces that correspond one for one and the Machinegun
answers: **ready frame 4, residual 0.0000** on its 4752 matching vertices (frame 3, the old answer,
was never right), and `MODELDEF.bd.txt` says the same thing independently — `FrameIndex MGN1 A 0 4`,
MGN1 A being the sprite the gun's Ready state holds. Its butt strike is in, above.

The MG42 has no surface that corresponds at all, so there is nothing to fit one-for-one on: it
needed **the correspondence found by position rather than assumed by order**, and the tool to do
that was already in `bd22_plus.py` and went unused for two sessions. `rigid()` is ICP with a
cKDTree, and the `geometry` stage has been reporting this very mesh at **mean 0.0 cm, max 0.0 cm,
rotation 1.7e-06°** the whole time. Per frame it gives frame 0 at 0.0000 and frames 1 and 2 at
0.0105, and `MODELDEF.bd.txt` agrees independently — `FrameIndex HBUS A 0 0`. Its butt strike is
in, above; `PBUS` is the same frames again (what BD22 draws in Purist mode), so both sprites count.

**The lesson worth keeping: an order-identity Kabsch silently returns a plausible number when the
two meshes hold the same points in a different order.** Nothing errors — the arrays are the same
length. Any future gun whose residual is not ~0.0000 should go to `rigid()` before it is written
off, and the surface vertex counts should be compared first.

**None of the eight can be gated.** `RSM_Melee.Tick` returns at `!RSVR_VRHand.InVR(mo)`, so a
headless run with `vr_mode 0` never reaches a line of it; the gate proves they compile and that
nothing faults, and the headset is what proves they swing.

**`god` is now the first thing `gate/bd22_gate.sh` does** (owner, 2026-10-24). A gate that dies
partway still prints GATE_DONE and still exits 0 — the quit at the end runs either way — it just
stops firing and reloading anything, so the run passes while testing nothing and the log never says
so. Full run with it on: `Degreelessness Mode ON`, all markers, exit 0, no fault, 9 warnings and
none ours.

**Three more ways that gate was passing without testing** (2026-10-24), all now fixed:
- `$PK3` and `$LOG` were relative and the run line `cd`s to `$QZD` first, so **the pack was not
  found and the engine loaded without it** — and still reached GATE_DONE, still exited 0. Both are
  resolved to absolute paths now, and a missing pk3 exits 2.
- `xvfb-run` came off the Linux container this script started on. There is none on the owner's PC,
  so `timeout` answered *"failed to run command 'xvfb-run'"* and the line still reported exit 0.
  It is used only where it exists; on Windows the engine opens its own 640×480 window
  (`+vid_fullscreen 0` either way — **it is never to be run fullscreen**).
- `echo "exit $?"` sat *after* the grep, so it printed the GREP's status, not the engine's: a
  crashed run said "exit 0" as long as the grep found nothing. The run's own code is captured
  first, and the gate now prints a hit count for each of its markers, because "no errors found" is
  not the same claim as "it ran".

The gate also **fires the casing guns** now (`GATE_CASINGS`: Shot_Gun, SSG, Revolver). `Place()` is
only reached from `WorldThingSpawned` on a casing, so until this leg existed a gun that was never
fired never touched the new `Port()` rows and the gate passed without exercising a line of it.

## F6, done bar the headset pass (2026-10-24) — reload foley and the pack README

**The three reloads had shipped silent since F1.** gen_rsr's snd fields were empty, so entries 10,
11 and 12 of `SndOut` / `SndIn` / `SndLand` all returned `""`. Brutal Doom has no foley for them
because it never reloads them, and REMA's bd22 SNDINFO covers only the nine it does — so these come
from the wider RS_VR_Weapons library, which the owner allowed for exactly this case.

| | out | in | landing |
|---|---|---|---|
| MG42 belt drum | `rsr/drumout` (MGCHAIN, the V+ minigun box) | `rsr/drumin` (MGLOAD) | `rsr/bigdrop` |
| Flamethrower canister | `rsr/canout` (RLCOUT, the V+ rocket canister) | `rsr/canin` (RLCIN) | `rsr/bigdrop` |
| Unmaker skull | `Unmaker/Stop` — BD22's own | `Unmaker/Start` | `rsr/bigdrop` |

`rsr/bigdrop` is a `$random` of DSAOUNC1-3, which RS_VR_Weapons' own SNDINFO describes as "a big
magazine hitting the floor — a chaingun box, a rocket magazine, a canister": written for this case
before we got here. The Unmaker needed no file: BD22's `Unmaker/Start` / `Stop` are the same
UNMSTA / UNMSTO lumps RS_VR_Weapons ships.

Declared under our own `rsr/` names, never `wm/` or BD22's. That is what `SNDINFO.rsr` already does
for its racking sounds, and REMA's SNDINFO spells out why: a bare `Pistol/Reload1` collides the
moment both packs load and the last definition wins silently, on load order.

**A gate cannot see any of this.** It runs `-nosound`, so a missing lump never shows. Checked
statically instead: all 10 paths our SNDINFO names are in the pk3, all 7 new files are real `OggS`,
and all 40 names the reload table asks for resolve — to ours or to one brutal22test6 defines.

**README.txt** ships in the pk3, generated by `bd22_plus.py readme`, with its gun count and menu-row
count read out of the built files rather than retyped. It states the load order, what each reload
family is, the 1.97 additions, the melee, the credits (Brutal Doom is Sergeant_Mark_IV's; the hands
are Ermac's under Rusted Legacy MIT; the engine is Emawind's) and the known gaps.

## F5, PART DONE (2026-10-24) — recoil and the dial are in; flashes and casings are NOT

Stages `recoil`, `impacts` and `bullet`, all after `butt`. **The owner's yes was given 2026-10-24.**

**Done.**
- **Per-gun recoil, 22 guns.** REMA's own numbers: each gun's `recoilprofile` on WMSHEET.bd22
  against RS_Ballistics' recoil blocks, computed there from free-recoil arithmetic. SSG rises 22°
  over 18 tics, the minigun 1.5° over 4. Axe, Dragonslayer and grenades are `none` and get nothing.
  **In VR this is the gun moving in your hands, not your aim**: the controller decides where a shot
  goes, `psp.x`/`psp.y` rotate the model. So `bloom` and `brace` have nothing to act on and are not
  carried, and the channel has no roll, so each profile's roll and backward shove are dropped.
  Additive in WorldTick, never assigned — A_WeaponReady rewrites that channel every tic.
- **Ballistics is Stock / Low / Max.** Low is exactly 1.96b (24 tracers, 64 debris); Max doubles the
  caps and multiplies counts by 1.8. `rsq_recoil` is its OWN row, not on that dial: it costs one
  float a tic, the effects cost a frame budget.
- **Per-gun impact weight**, derived not typed: mass × speed² from the `ballistics` blocks, cube
  root of the ratio against the 9mm. 7.62 2.21, 5.56 1.91, buckshot 1.66, .357 1.26, 9mm 1.00.
  Ten guns; the rest have no cartridge and take 1.0.
- **The pack is raised to ZScript 4.14** (ZSCRIPT.rsvr). 1.96b declared 4.10, which HIDES
  `WorldHitscanPreFired` (added Nov 2024). A `version` line in an included file is refused, so it
  has to be the root lump. qzd17.3 is GZDoom 4.14.3 and the pack compiles clean at it.
- **`gate/bd22_gate.sh` now passes `+logfile`.** A fatal script error does NOT reach the redirected
  stream — the log just stops looking clean. That cost three diagnoses in one session and the owner
  had to paste the real error each time.

**NOT done, and this is the honest list.**
1. **Muzzle flashes — nothing.** The sheet names 20 distinct `flashprofile`s. Every shot still has
   Brutal Doom's own flash. This is the most visible thing on a gun and it is the real gap.
2. **Casings — eight guns now, not four.** `bd22_plus.py casings` added Shot_Gun, SSG, Revolver and
   Revolver2 to the four 1.38 hand-tuned, and gave the Revolver, the Shotvolver and the SSG a
   *dump* instead of a flick (RSBDEFS: `brass_357` is "dumped from a cylinder, not thrown by a
   port: slow, no glow"; `hull_12ga_magnum` "dumped from an open breech"). Still open: the casing
   MODELS and smoke behind the 11 `ejectaprofile`s, and the four guns below.

   **Do not use WMCARD.bd22's `ejectport` for this.** All 25 cards carry one and every one of them
   is annotated *"the point and the direction are estimates"* — what was measured is the SIDE, by
   counting vertices on each wall. Carried onto the held mesh by the exact rigid transform
   (residual 0.0000) it misses all four hand-tuned ports: BrutalPistol by 3.8 cm, BrutalSMG by
   10.8 cm, Rifle by 3.0, AssaultShotgun by 0.8. A guess transformed exactly is still a guess.

   **What is measured is the mesh.** The model-makers named the port — Rifle `ejectport`, Shot_Gun
   `eject`, SSG `Open`, Revolver five × `shells` — and where nobody named it, it is still a HOLE:
   weld the ready frame and every edge used by one triangle only is a boundary, and the boundaries
   close into loops. The check, on the two guns that have both a modelled port and a hand-tuned
   number: BrutalPistol lands **0.84** units away (a 3.9 × 0.2 × 0.3 slot, 10 verts, facing right
   and up) and AssaultShotgun **0.44** (7.8 × 0.7 × 2.0, same signature). On Shot_Gun the named
   surface and the boundary loop agree with each other to 0.06.

   **The MG42's port is DOWN, not sideways**, and looking only at the walls is what hid it. The
   regular loops down its flank at x 68–108 are the barrel jacket's cooling slots. A real MG42
   ejects through the floor of the receiver, and the chute is modelled: one flat opening 10.1 × 2.8,
   centred (y −0.04), below the bore (z −0.57), under the breech. So the case leaves three ways,
   not two — `Throw()` returns SIDE, DOWN or TIP — and a belt gun at 1200 rpm is not TIP. `MGLinks`
   are caught too: same chute, and an `EmptyBrass` subclass the exact-name filter was missing.

   **Three guns have no port in their mesh to find**, and guessing them would put brass somewhere
   arbitrary: **MP40** (every `korpus` slot is mirrored at ±1.44 — the tube's cooling slots; `zamek`
   is the bolt, y +1.2 being its left-side handle), **Minigun** (91 loops, all of them bores in
   `Pipe`), **Machinegun** (an M249 body with no port loop).
3. **The round in flight — written, inert.** `zscript/rsq/rounds.zs` DOES ship and IS included, but
   it is `class RSQ_Rounds abstract` with nothing calling it and `MODELDEF.rsbullet` left out of the
   pk3, so it is dead code, not a working bullet — do not read its presence as "done". Every gun with
   a cartridge is HITSCAN, and the only carrier is a PROJECTILE follower, so it can never fire as
   wired. It needs spawning and flying from the muzzle (each card has one) to the impact.
4. **Impact character.** Only a strength multiplier crossed. RS_Ballistics' 572 impact blocks decide
   what a 9mm does to metal versus wood versus glass; none of that came, and it cannot come as
   written — bursts resolve PARTICLEDEFS, a REMA renderer feature.
5. **Butt strikes — done.** All eight stocked guns: Rifle, Shot_Gun, SSG, AssaultShotgun, MP40,
   BrutalSMG, Machinegun, MG42. None of them can be gated (melee is VR-only), so the headset is
   what proves they swing.
6. **The slug revolver has no hand-fit sheet.** The Machinegun got one.
7. **The melee doc's §9 architecture** — the netevent pose-history spine it calls the single
   highest-leverage thing in the three codebases. `melee.zs` was extended instead, so its snap-turn
   and teleport patches remain.

**Two bugs that looked fine and did nothing** — both found only by reading the CALLER:
- `Impact(Actor tracer, …)` is misnamed; `RSQ_Tracer` passes the **shooter**. The per-gun impact
  weight looked the gun up through `tracer.target`, null on a player, so **every gun weighed 1.0**
  and the whole table did nothing. Fixed.
- A regex over RSBDEFS required a block name to end its line, but those headers carry trailing
  comments. It matched almost nothing and produced a plausible six-gun table instead of ten.

## What is NOT done (the plan's remaining flagship items, in order)
1. ~~Gate `sets/bd22q_1.97` on the owner's exact load order.~~ **Done 2026-10-24** (see "F1 IS DONE"):
   runs clean, pk3 handed over. What is left of F1 is the owner's headset pass, which is his to do.
2. ~~**Slug revolver** (BD21 `Revolver2`): roster, RSB break entry with Clip2, "replaces Shotvolver".~~
   **Done 2026-10-24** (see "F2, done" below). Headset pass outstanding, like everything else VR.
3. ~~Options page onto the shared `RSQ_Options` standard.~~ **Done 2026-10-24** (see "F3, done").
   The layout's headset pass is the owner's.
4. **Melee** on bd22q from `docs/VR_MELEE_ON_QUESTZDOOM_2026-10-24.md`: pistol whip, rifle/shotgun butt
   strikes, the spike, switch-punching with either hand. **None of it is built.** It is flagship work,
   not a later pass (owner, 04:24).
5. Per-gun ballistics profiles from REMA's WMSHEET behind the Ballistics switch -- pending the owner's yes.
6. ~~Reload SOUNDS for the drum / canister / skull; README for the pack release; this handoff.~~
   **Sounds and README done 2026-10-24** (see "F6, done" below). **The owner's headset pass is the
   only thing left on the flagship** — and it is the only thing that can test any of this.

Open questions for the owner: counter model vs REMA's fire-from-magazine for the three reloads; the
revolver primary/alt swap asked at 03:41 (parked when Revolver2-with-option was asked at 03:56).
Then the plan's next sets (PLAN.md): BW_Quest, Aliens, Meatgrinder, Modern wiring, Plus passes per set.

## Owner's rules (violating these ended the last session's trust)
- **Never from memory. Re-check source.** Every number comes from a mesh (tool-measured) or a parent
  mod's code (parsed). Say which.
- **Don't guess — measure.** If a tool can check it, the owner must not be asked to.
- **No engine changes** to QZD 17.3. Compiling it is fine.
- **Ermac's hands/assets ship.** REMA is 1/3 Ermac, 1/3 Emawind, 1/3 owner.
- **Don't test guns one at a time** in the engine. One launch per set.
- **Vanilla = Doom's arsenal**, Doom's names, Doom's numbers.
- **Plus = optional extras inside a set as menu rows**, not a separate pack, and a Plus pass comes
  AFTER the set stands. (Tonight's three reloads are NOT Plus: they close the gap to REMA's bd22 set,
  which the plan names as the flagship work.)
- **Don't hand over an unbuilt/untested pk3.** Not even when asked "do you have a pk3". Say "not yet".
- **Never tell the owner when to sleep or work.**
- **Say blockers the moment they appear** (e.g. "Freedoom lacks the voxel pack's sprites, I need doom2.wad")
  — do not work around them silently.
- **Don't narrate tests every turn.** Run the gate, report results, move on.
- Discuss before starting new projects. Stop when told to stop.

## The engine gate (`gate/run.sh`, and the bd22 variant inside `tools/bd22_plus.py` history)
Stock qzd17.3 (emawind84/gzdoom tag qzd17.3 = GZDoom 4.14.3) built headless: `cmake -DNO_GTK=ON
-DHAVE_VULKAN=OFF -DHAVE_GLES2=ON`, run under `xvfb-run … +extension GLX`, `LIBGL_ALWAYS_SOFTWARE=1`,
`+vr_mode 0`. One launch: parse, map, give guns, fire, reload, quit; pass = no `Script error`, the
`GATE_*` markers, exit 0. **BD22 needs doom2.wad** (BD_VoxelPack's voxeldef names Doom 2 sprites;
Freedoom fails). The owner supplies doom2.wad and brutal22test6.pk3; they are not in this repo.

## No drift
`tools/check_plan.py` is installed as `.git/hooks/pre-commit` by `tools/install_hooks.sh`. It refuses
a commit when: the commit touches `runtime/` (frozen); a file under `sets/bd22q_1.97/src` differs from
what `bd22_plus.py apply` + `bd22_mg.py` regenerate (hand edits); `PLAN.md`'s "Current step" is not
one of the numbered items; or a new top-level directory appears that PLAN.md does not name. Every
commit message starts with `[step N]` matching PLAN.md. If you need to do something the plan does not
list, add it to PLAN.md first in its own commit `[plan]` with one line of reason, and get the owner's
yes before building it.

## Paths you must change before running anything (they are the previous machine's)
Each tool has its paths at the top. Set them once:
- `tools/bd22_plus.py`: `SRC` → `runtime/` (1.96b src), `REMA` → your checkout of RS_VR_Weapons `bd22/`, `OUT` → a build dir; the kit path on the `sys.path.insert` line → `tools/kit` (gen_rsr.py, rgeo.py live there).
- `tools/bd22_mg.py`: `OUT`, `BR` (br_vr `PK3_pbr/` from E:\DOOMWork\VR_WeaponSetRebuild), `BD21` → `docs/BD21_Machinegun.txt`, `REMA`, the kit path.
- `tools/genpack.py`, `assemble.py`, `handfit_cards.py`: the `/mnt/user-data/uploads/Quest_Weapons_Kit/...` and `/home/claude/...` lines → `tools/kit` and your paths.
- `gate/bd22_gate.sh`: the four paths at the top. This is the F1 command.
Regenerating is every stage below, in this order, then the pk3 — the earlier short form in this
file was missing eight of them:

```
geometry  apply  [bd22_mg.py]  revolver  options  bash  whip  butt  recoil  impacts  flash
casings  readme        then:  pk3 dist/BD22Q_197pre.pk3
```

i.e. `python tools/bd22_plus.py geometry`, … , with `python tools/bd22_mg.py` (no argument) in
third place. The result must equal `sets/bd22q_1.97/src` (diff it; that is the drift check for the
generators themselves). **Order matters**: `revolver` must follow `bd22_mg.py` (it edits the roster
handler `bd22_mg.py` writes), `options` must come after both (it restructures the menu page they
add rows to), and `apply` must precede everything that edits a 1.96b file — `bash`, `whip`, `butt`,
`impacts` and `casings` all patch files `apply` copies in, so running one twice on an already-built
tree is what their "is not there exactly once" guards are for. `bullet` is deliberately NOT in the
pipeline. (`python`, not `python3`, on the owner's PC.)

## Known failure already fixed (so nobody re-learns it)
`counters.zs` called `RSR.WantsHands`; the function lives on `RSR_ReloadHandler`. The first pk3 handed to the owner had this and died at script parse. Lesson for every ZScript addition: grep the class a static lives in; then run the gate before anything leaves the repo.

## Model -> card: tools/hqt (the kit's HighQualityTools; I had wrongly said none existed -- owner, 04:34)
`tools/hqt/namedcard.py model.md3 Name archetype > Name.card`: an MD3 with NAMED surfaces -> a card
(roles from the surface names: mag, slide, pump, bolt, cyl, crane, latch, trigger, round, case...;
geometry from the mesh). `md3label.py` names surfaces, `obj2md3.py` converts with the right axes,
`motion.py` / `phase.py` read part travel from the frames, `render.py` draws, `batch.py` runs a folder,
`diff.py` compares cards. Its own paths (`sys.path.insert(0, '/home/claude/md3')`) need fixing like the rest.
This is the "HQT" of PLAN.md's foundation line. Wiring it as step 2 of "Per set" (measure every mesh
fresh) is not done. The REMA cards' comments mention `CardPipeline/` -- a desktop folder with the dead
Forges, not needed.

## The tools that matter (owner, 04:36) -- everything else in tools/ is clutter to be removed
A gun passes through these, in order:
1. `tools/hqt/md3label.py` -- name the surfaces of a new mesh (mag, slide, pump, bolt, cyl, latch, trigger...)
2. `tools/hqt/namedcard.py` -- mesh -> card (the numbers)
3. `tools/kit/gen_rsr.py` -- card numbers -> reload tables + MODELDEF.rsr (the kit's own, unmodified)
4. `tools/handfit_cards.py` -- hands onto the gun from the card's palm / supportat
5. `tools/genpack.py` + `tools/assemble.py` -- weapon classes, sounds, the 1.96b runtime -> a pack folder
6. `tools/check.py` -- static check of that folder
Then the OWNER tests in the headset on his load order. The headless engine gate (`gate/`) is optional
tooling for catching parse errors; the owner does not want it in the required chain.
`carve_by_ref.py` when a part must be cut out of a mesh; `bd22_plus.py` / `bd22_mg.py` are steps 3-5
applied to 1.96b for the flagship. Cleanup task (after F1): delete every other script in tools/.
