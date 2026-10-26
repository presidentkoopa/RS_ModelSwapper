# bd22q 1.99, the owner's first headset pass (2026-10-26): every problem, and where each one stands

**Read this first if you pick up bd22q.** The owner played 1.99 (RS_Brutal22WeaponsQ `main`) on his
Quest. It was worse than **1.92**, which he calls the reference: "ALL HANDS WERE GREAT BEFORE". He
expected 1.99 = 1.92 + a few new weapons + bug fixes and polish. Instead, systems added after 1.92
changed how every gun looks and behaves. **The rule from here on: 1.92 is the behavioural baseline.
Anything that makes a 1.92 gun look or act differently is a regression unless the owner asked for it.**

State of the repos when this was written:
- RSQ_WeaponDepot: `4126d5b` (pushed) has everything below, including the recoil removal.
- RS_Brutal22WeaponsQ `main` = `76c9a2d`. It does NOT have the recoil removal. The owner has the
  pk3 from `76c9a2d` (no spin, no phantom shots, BD22's own sounds back, recoil still in).
- No GitHub release or tag exists for 1.99. This session cannot create releases or push tags.

## A. Fixed and confirmed in the rig

1. **Guns spun round the shoulder (all guns, worst while reloading).** F5 recoil ADDED its kick to
   `psp.x`/`psp.y` every tic. The engine turns the gun model by `psp.x / 4` degrees of yaw and
   `(32 - psp.y) / 4` of pitch. Reload waits and most fire frames don't rewrite the channel, so
   the kick piled up. Rig: `psp.y` reached -1439 = 368 degrees of pitch. Fixed in `76c9a2d`, then
   recoil **removed entirely**: see A3.
2. **Muzzle flash and gunshot sounds while walking or reloading.** Recoil and the flash
   (`rsq/flash.zs`) counted every player missile as a shot. That included BD22's **footsteps**
   (damaging `Trample` missiles), kicks, fists, the haptic buzz (`RSVR_Buzz`, fired on every reload
   step and melee contact) and BD22's own helper missiles (4 flashes per shot). Now one test,
   `RSQ_Ballistics.IsShot`, and one shot per tic. In `76c9a2d`.
3. **Recoil removed (owner: "this recoil needs to go").** It turns the gun model, but parts drawn on
   their own reload layers (the pistol's locked slide, the SSG's open barrels, a magazine at the
   well) are placed in the controller frame and don't turn with it, so the gun came apart.
   `RSQ_Recoil` is out of MAPINFO and the "Gun Recoil" menu row is gone. Committed in `4126d5b`;
   pk3 `/home/claude/gate_out/BD22Q_norec.pk3` (cloud session). NOT yet run in the rig, NOT on
   RS_Brutal22WeaponsQ, NOT sent to the owner.
4. **BD22's own sounds were replaced by ours.** 19 of our sound files had the same 8-letter lump
   name as BD22's (ricoche1-7, and ricoche10-16 truncate to ricoche1, plus winbrea, sparks1,
   DSAOUNC1-3). BD22's SNDINFO names those by lump, so its ricochets, glass break, sparks and big
   magazine drops played our files. `fixes` now renames them (`rqsNNNNN`). In `76c9a2d`.
5. Fire rates match PC BD22 (pistol, pump shotgun, M32, dual pistols). The Ruger is semi-auto.
   Rounds left in a pulled magazine aren't stranded when the reserve is empty. The axe alt-hold no
   longer freezes the game. Done earlier in 1.99.

## B. Reported by the owner, NOT fixed. Each needs work.

### Hands and poses
6. **"All of the hand poses are off."** BFG grips are off ("the white texture gun is the
   closest"), the plasma rifle hand is off, and the plasma magazine-in-hand pose is bad. **Checked:**
   `zscript/rsq/handtable.zs` and the reload MODELDEF are byte-identical to 1.92 for every 1.92
   gun. The reload tables (`rsr_guns.bd.zs`) are identical except the Ruger (new XM21 model). So the
   cause is NOT the hand tables.
   - Prime suspect: recoil (A3) moved the gun model while the hands are placed from the gun layer's
     offset. Retest with recoil removed before anything else.
   - Then compare 1.92 against current IN THE RIG, visually (see section D, tooling).
   - Other changes since 1.92 to check: `MODELDEF.bd.txt` (ready FrameIndex per sprite, the
     "pose restored" tables), `hands.zs` (scope dot, axe GunHookTwo, dual stale-offhand fix),
     `gunmoves.zs`, the casing / voxel lending (`casemodels.zs`, `voxels.zs`).
7. **"The Nuker is the same model as the BFG, which had good hands"**, yet the Nuker's hands are
   wrong. Compare their hand-table rows and MODELDEF placement.
8. **Chainsaw grip hand: move 2 cm left.** Edit the hand table row, in the generator.
9. **Incendiary Launcher (M32): bad grip, move it forward 2 cm.**
10. **The magazine-in-hand poses for the 9 F10 guns were never hand-fitted** (`grip='base'`:
    the palm is at the far end of the part). The Hellish drum is held 28 cm from where it meets
    the gun; the Nuker block is held 18 cm above the palm. Use the `vr-hand-fitting` skill on the
    actual meshes, with render checks.

### Weapons coming apart
11. **Weapons "literally come apart when I grab them"** (grabbing = the off hand on the gun,
    steadied / two-handed). The pistol came apart on its last shot as the slide locked back. The
    SSG broke when reloaded. Recoil (A3) explains the last-shot and reload cases. **Re-check after
    the recoil removal.** If grabbing alone still separates parts: the engine re-aims a steadied gun
    at the off hand (WF_TWOHANDSTABILIZED, `p_pspr.cpp`), and our separately placed layers (well
    magazine, handle, bolt, break barrels) may not follow that re-aim. Check
    `RSR_ReloadHandler.Place` / `RSB_Handler.Place` against the stabilised orientation.

### Reloads that don't work
12. **Chaingun (Minigun): "no optional reload code, 100 round per load, we cannot reload it".**
    F10 built a 200-round box counter (`rsq_plus_minigun` entry; the counters cap at 200). The
    owner reports 100 and no reload, so it is either not in the build he ran or not reachable. Also
    check the 1.92 class name (`MiniGun` vs `Minigun`): `RSQ_Counters` and the `Index()` tables use
    `Minigun`, while BD22's actor is `MiniGun`. ZScript Name comparison is case-insensitive, but
    verify. The rig run used `Minigun` and reloaded, but only with the off hand starting at a pouch
    20 cm or more from the box (`POUCH_MIN`). Ask the owner what he pressed. Rule 5: verify on his
    real input.
13. **Machinegun (M249 with the over-under 40 mm): the box doesn't detach.** Owner: "we need to clone
    and alter the weapon code to allow it". F10 built the box reload in the `late` stage (Reload's
    VR line jumps to `RSR_Box`). It works in the rig; in the headset it doesn't. Find out why
    (input path, `rsq_mg_replaces_mg42`, which class he is holding).
14. **Machinegun launcher: the 40 mm grenade sits too high when inserted**, "half in the barrel,
    half in the gun above". This is the M203 geometry for the Machinegun (`rsr_m203_geo.zs`,
    gun index for the Machinegun). Lower it to the tube's bore, measured off the mesh.
15. **Incendiary Launcher (M32) doesn't animate or reload in the headset.** It worked in the rig
    (cylinder reload). Same question as 12/13: what differs between the rig's input and the Quest's?

### Melee
16. **Sword (DSweap) and axe: no two-handed mode.** The engine's two-handed weapon handling is too
    much for them. The owner's alternative: on a button press, the model and hands change to the
    two-handed placement, but only ONE controller drives the weapon. Today `RSVR_AxeTwo` is set
    when `RSVR_VRHand.Steadied` (the engine's steadying): switch that to a button toggle, and stop
    steadying (two-handed aim) on these weapons.
17. **Swing sensitivity too high.** Attacks should come only from a DOWN or SIDE swing, never an
    UPswing. Gate `melee.zs`' swing detection on the direction of travel (body-frame up component
    of the edge velocity).

### Sounds
18. **"A bang sound when I load into a map."** Unknown. Candidates: a tail or flash fired by a
    missile spawned at map start (now filtered by IsShot), the voxel lender, the casing lender, or
    a counter / reload sound on the first tic. Reproduce with a sound-logging probe.
19. **"The BFG and many other sounds are incorrect."** A4 fixed BD22's own sounds being replaced.
    The pack does not touch BD22's BFG code. Ask the owner which sounds are still wrong after A4.

### Visuals
20. **Voxel shells are enormous.** F7 `casemodels.zs` lends 3D casing meshes to BD22's casings and
    sets scale 1.0. `casings.zs` sets a VR size (`Size()`) on top. BD_VoxelPack also replaces the
    casings with voxels: the lend or the scale is wrong when the voxel pack is loaded. Compare in
    the rig (section D) with `rsq_casing_models 0`.
21. **The Ruger's scope is not a real scope, just a texture.** 1.96b's scope has two modes: Dot
    (`rsq/scope.zs`, a collimated dot) and Real (`scope_real.zs`, a camera texture on the lens).
    The menu default is Dot (0), so by default the lens shows the plain glass tile
    (`scope_glass.png`). Decide with the owner whether Real is the default; check that Real works
    on the Quest (camera textures cost frame time).

## C. Owner calls already made (don't re-ask)
- Off-hand punch stays off by default (behind `rsq_punch`). "Check the chamber by hand" stays off
  by default.
- The axe locks one target only and does not come back (it has 10 rounds). The ring is the
  ShieldSaw's.
- Every gun at BD22's own fire rate and damage. The pistol semi-auto option stays.
- BFG and BFG10k: no reload.
- Minigun: carve the block under the gun; a bigger in-hand ammo box later (not built).

## D. Tooling that exists for this (cloud session `/home/claude`, NOT in any repo)
- `rigtest/` + `rig2/`: the owner's quest_test_rig (real QZD 17.3 OpenXR path, poses from cvars).
  `rig.py run()`. Set `B22_NOPROBE=1` to run old packs, whose class names the probe doesn't know.
- **Frame dumps (new, this session):** `rig2/glue/qz_linux_glue.cpp` writes the left eye every N
  frames when `QZ_DUMP_EVERY=N QZ_DUMP_DIR=<dir>` are set (PPM). Use `QZ_RES=480`.
  `rigtest/shots.py shoot()` wraps it. The gun hand pose `qz_rhand "0.0 1.68 -0.40 20 -70 0"`
  shows the held gun and hand side-on, in front of the eye. **Use this to compare 1.92
  (`gate_out/BD22Q_192.pk3`, built from tag 1.92) against current, gun by gun, before changing
  anything.** It was about to be run when the session ended.
- `rigtest/holdtest3.py` (fire rates), `spintest.py` (gun offset, flashes), `mags.py` (reloads;
  use `with_pouch`), `probe/` (`B22 W/SHOT/PSP/LOCK/AXE` lines).
- Load order is always doom2 -> brutal22test6 -> BD_VoxelPack -> pack (CLAUDE.md rule 5).

## E. Suggested order
1. Run the rig smoke and spin test, then visually compare 1.92 against
   now for every 1.92 gun (D). Most of items 6, 7 and 11 may already be gone with the recoil.
2. Anything still different from 1.92 on a 1.92 gun: find the change and revert it toward 1.92.
3. The headset-only reload failures (12, 13, 15): get the owner's exact input, reproduce, fix.
4. Grips (8, 9, 14), then the F10 in-hand poses (10) with the hand-fitting skill.
5. Melee (16, 17), sounds (18, 19), casings (20), scope (21).
6. Publish to RS_Brutal22WeaponsQ only after the owner's headset pass on a test build.

## PROGRESS after this doc was written (2026-10-26, same session) -- newest last
- `e752cef` tools/rig: the rig scripts, probe, frame-dump glue, ini and build notes are IN THE REPO
  now (tools/rig/README.md). `cmp2.py <pkA> <pkB> <Gun,...> <tag> [pose]` = one run per gun, side by side.
- Rig renders, 1.92 vs now, recoil removed: Pistol, Plasma, BFG and SSG hold poses are the SAME at
  rest. The "hands off" was the gun moving (recoil), not the hand data. Items 6/7/11: retest in the
  headset on the next build before changing hand data.
- `3360579` item 8/9: chainsaw hand 2 cm left (x -2: +x moved it right on screen), M32 hand 2 cm
  forward (z -2). `GRIP_NUDGES` in bd22_plus.py, applied in `fixes`.
- `e1c9a57` items 16/17: the axe and sword cut on a DOWN or SIDE swing only (no cut if the blade rises
  more than ~9 degrees) and need 1.5x the swing speed. Two-handed: the engine REFUSES scripts
  changing `vr_two_handed_weapons` ("outside of menu code"), so per-weapon disabling is impossible on
  stock 17.3. It is a menu row now, "Two-Handed Steadying"; with it OFF, holding the off grip
  within 50 cm of the axe or sword gives the two-handed pose and support hand (`RSVR_MeleeTwo`,
  `RSVR_VRHand.TwoHands`) while one controller drives it (rig: meleeTwo/axeTwo 1 on grip). Guns lose
  steadying too while it is off -- the owner's trade-off to judge.
- `f16df01` item 12: the Minigun box is 100 (owner). At 200 it equalled BD22's Clip2 cap, so it was
  always as full as the reserve and reload never started. **The same flaw remains, NOT changed, for
  the owner to decide:** MG42 drum 200 vs Clip2 200, and the M32 cylinder 6 vs AmmoM202 max 4 (it
  can never be filled past the reserve, so a reload never adds anything). A counter is only a real
  magazine when its capacity is below the reserve's max.
- `41d1c3b` item 14: the Machinegun's launcher numbers and its hand fit were measured WITHOUT the
  gun's ZOffset -5, so the 40 mm round, latch, load point and hands were 5 cm high. Fixed in
  bd22_mg.py; the rig render shows the gun hand moving down onto the pistol grip.
- `f80df0f` (part of item 11): the MG42, Flamethrower and Unmaker reload model blocks were at ZOffset
  0 while the gun sits at -5, so the gun jumped 5 cm when their reload started. Now -5; their
  card-measured points are shifted, not re-measured. All three reload in the rig.
- Item 20 FIXED: with "Spent casings" voxels on (the rig's ini has it on, likely the owner's too), a
  casing the F7 lend had given a real-size 3D mesh at scale 1.0 was then handed the voxel AT 1.0 --
  rig: a pump-shotgun shell at scale 1.000 against BD22's 0.25. Now the lend steps aside when voxel
  casings are on, and the F6 sprite sizing no longer shrinks a lent 3D casing. Rig after: 0.25.
- STILL OPEN: 10 (F10 in-hand poses, never hand-fitted), 13/15 (Machinegun box and M32 in the headset
  -- 15 is likely the 6-vs-4 capacity above), 18 (bang on map load), 19 (BFG sounds after A4),
  20 (voxel shells), 21 (Ruger scope default), and NO new build has been published to
  RS_Brutal22WeaponsQ or sent to the owner since 76c9a2d.
