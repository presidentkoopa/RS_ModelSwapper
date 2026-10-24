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
| `sets/vanilla` `plus` `modern` | the c2q-built sets (genpack → assemble → check → mkpk3). Vanilla = Doom's eight, Doom's names/numbers, RSQ_Player start pistol. |
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

## What is NOT done (the plan's remaining flagship items, in order)
1. ~~Gate `sets/bd22q_1.97` on the owner's exact load order.~~ **Done 2026-10-24** (see "F1 IS DONE"):
   runs clean, pk3 handed over. What is left of F1 is the owner's headset pass, which is his to do.
2. **Slug revolver** (BD21 `Revolver2`, `docs/BD21_Revolver2.txt`): add to roster, break reload entry
   (RSB) with Clip2 reserve, menu row "Slug revolver replaces Shotvolver". Same pattern as the Machinegun.
3. Options page: move 1.96b's page onto the shared `RSQ_Options` standard (`tools/README.md`). The
   owner does the headset pass on the layout.
4. **Melee** on bd22q from `docs/VR_MELEE_ON_QUESTZDOOM_2026-10-24.md`: pistol whip, rifle/shotgun butt
   strikes, the spike, switch-punching with either hand. **None of it is built.** It is flagship work,
   not a later pass (owner, 04:24).
5. Per-gun ballistics profiles from REMA's WMSHEET behind the Ballistics switch -- pending the owner's yes.
6. Reload SOUNDS for the drum / canister / skull (the gen_rsr snd fields are empty: assign BD22's own from
   SNDINFO.BD); README for the pack release; this handoff updated; owner headset pass.

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
Regenerating is: `python3 tools/bd22_plus.py geometry && python3 tools/bd22_plus.py apply && python3 tools/bd22_mg.py && python3 tools/bd22_plus.py pk3 dist/BD22Q_197pre.pk3`. The result must equal `sets/bd22q_1.97/src` (diff it; that is the drift check for the generators themselves).

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
