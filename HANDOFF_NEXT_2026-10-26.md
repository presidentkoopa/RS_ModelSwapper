# ModelSwapper 2.0 — handoff to the next agent, 2026-10-26 (branch `modelswapper-2.0-bd22-lift`)

Read first: `README.md` (the 2.0 section and "Making a model reloadable: the pipeline"), then
`HANDOFF_2.0_2026-10-25.md` (what is measured, every fault found, the gate). This file adds the owner's
FIRST HEADSET PASS (2026-10-26, 03:20) and what to do about it. Branch head at writing: `49222b9`,
pushed. `main` untouched by design — do not merge without the owner's yes.

Mantra: **their code, our models, collective reload.** The mod's code fires the gun and decides every
round; ModelSwapper puts its models on it and the hands do the physical part. Never change the mod's
ammo; never guess a number (measure from the mesh / parse the code, and say which). No engine changes
(QuestZDoom 17.3). Test load order: doom2 -> brutal22test6 -> BD_VoxelPack -> the pack.

## The owner's headset findings, in his words, with leads

### 1. "Magazines and shells do not appear in the offhand, all I see is a knife." — TOP PRIORITY
Weapon meshes reload, but the held part (magazine, shell, round) is never drawn in the off hand.
**Lead (read, not yet tested):** every held part is drawn on the OFF-HAND WEAPON's layers, and only
when that weapon is `RSQ_Hands`:
- `zscript_depot/rsr/vreload.zs:898-899` `RSR.SetPart(p, RSR.HANDMAG, hands is 'RSQ_Hands' ? hands : null, ...)`
- the same in `rsr_pump.zs:990` (shell) and `rsr_break.zs:1121` (round).
On the owner's load order the off-hand weapon is Brutal Doom's (the knife), not RSQ_Hands, so the
caller is null and nothing is drawn. Also `vreload.zs:1095` `RSR_ReloadHandler.Wanted()` requires
`OffhandWeapon is 'RSQ_Hands'`; check which path the join actually uses (`RSR_ReloadHandler.WantsHands`
is what RS_ForeignReload checks) and why reloads ran at all.
The gate never caught this: it gives the player RSQ_Hands as the off hand. **Add a gate case with a
foreign off-hand weapon** (a test-mod knife in the off hand) before fixing, and make it fail first.
Fix direction: draw the held part on a layer whose caller is whatever is in the off hand (as the gun's
layers use the foreign main weapon via A_ChangeModel / the donor's MODELDEF), or on RSQ_Hands' layer
while the knife is hidden for the reload. Owner decides the look; see 2.

### 2. Off hand = Brutal Doom's Offhand Fist, always, unless a weapon is moved to the off hand
"BD22 has a Fist and an Offhand Fist; we only want these." The off hand should show BD22's off-hand
fist all the time; only when the player moves a weapon to the off hand does it show that weapon.
Not the knife. Start: `zscript_depot/rsq/fists.zs` (`offFist`), `hands.zs:199` (`freeFist`),
`dual.zs` / `dualhands.zs` (weapons moved between hands), and how BD22Q itself picks its off-hand
fist (Depot, read only). Likely ties into 1: the off hand being OUR hands object with BD's fist
model is what lets the reload draw a magazine in it.

### 3. BD22 grenade launcher (MS_BD22_M79): the support hand is detached, far from the model
"The bd22 192 set was perfect, so I would expect those models to cooperate." Some other support
poses are wrong too (owner did not list which — ask, or render all with `--shots`).
Leads: hand slot 71 (`handtable.zs:104`), its `RSQ_GunMoves` row (`gunmoves.zs`, written by
`tools_kit/gunmoves_ms.py` from the donor block), the donor's placement in `modeldef`
(MS_BD22_M79, lifted by `tools_kit/lift_bd22.py`). Compare, number for number, with BD22Q's own row
for its M79 in the Depot (192 set) — the lift copies rows, so a difference is the lift's fault
(slot keyed wrong, a placement field not copied, a break-open gun's support pose living in a
different table — e.g. `rsb_guns.zs` has its own hand points). `gunmoves_ms.py --check <bd22 dir>
<aliens dir>` validates pivots against the sets. Prove it on the rig with
`gate/run_gate.py <pk3> MS_BD22_M79 --vr --shots` (the rig's shots are the real eye view) BEFORE and
AFTER the fix.

### 4. New reload timing (ModelSwapper): run the mod's reload first, hold the FIRE until the hands finish
"When we press the reload button, we want the code to advance to the end of its reload state, but
not complete / allow the player to fire, until the player finishes the physical VR reload sequence."
Today (`zscript/RS_ForeignReload.zs`): at the mod's Reload entry the gun is PARKED (MS_Hold) while
the hands work, then handed to the head of the mod's reload, which runs after.
Wanted: the mod's reload runs at once, to its end (its ammo, its rules), and the gun is then held —
no fire — until the hands are done (RSR_Done / RSB_Done / the pump's end). Design notes:
- detect "the mod's reload reached its end": the psprite leaves the reload group back to Ready
  (`InReloadGroup` / `AtReloadEntry` already exist); park THERE in MS_Hold (no A_WeaponReady = no
  fire), release to the Ready state when the hands finish;
- the hands' reload must still start at the press (RSR_Start / RSR_MagOut at entry, as now) but must
  no longer gate the mod's reload; the SEATED -> RSR_Filled -> CHARGE -> RSR_Done chain stays;
- the PUMP join paces the mod's loop shell by shell today (one push = one pass of its loop). Under
  the new rule decide with the owner: the mod loads its whole tube at once and the hands then push
  the same count, or keep pacing. Break-open: same as magazine.
- add a switch (Options, VR Reload) for old vs new timing, per the owner's "everything can be
  switched off" rule; update the gate's checks ("their reload ran" comes BEFORE "seated" now).

## Gate status at close-down
- Desktop: **74 of 74** reloadable models PASS (`gate/run_all.py`).
- Rig (`--vr`): full re-run on the final build stopped at 29: 27 PASS, AE_Pistol and BD22_Rifle were
  timing misses (whole reload ran; the run ended before the mod's refill) — handle guns now run 900
  tics. Re-run: `python3 -B gate/run_all.py <pk3> --vr --only <half>` (each run under 2 h).
- The gate's blind spots, now known from the headset: it uses RSQ_Hands as the off hand (finding 1),
  and it checks phases and the hand on the gun, not the support pose's distance (finding 3). Close
  both.

## Still open from before (see the 2.0 handoff's Limits)
- Grip-mode cannot grab a charging handle (BD22Q's steadying rule) — owner's call.
- Four shelf RPG rows (brt_/d64_/hdvr_/vplus_RPG) push the rocket only 1.64 units (WMCARD.shelf).
- KAR98 and brt_AssaultShotgun have no hand row.
- 9 models whose animation moves no magazine keep their old `_wm` rows.
- ~200 shelf models not reloadable yet: the pipeline in the README (`card_leftovers.py --donor`,
  `regen_rows.py --add`) — dry-run worked on MS_hacx_UZI (slot 81).

## Where things are
- Build: `python3 -B tools_kit/build_quest.py out.pk3` (Linux) / `./build.ps1 -Static` (Windows): one pk3, ~450 MB.
- Rig: `/home/claude/qzlinux17` in the last session's container (rebuild from the owner's
  `Desktop/Quest_Weapons_Kit/quest_test_rig`, see `gate/qz_rig/README.md`).
- Delivered to the owner: `ModelSwapper-QUEST-2.0-4227925-1of2.pk3` + `-2of2-models.pk3`.
