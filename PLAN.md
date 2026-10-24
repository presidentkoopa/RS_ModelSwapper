**NO DRIFT. FOCUS ON WEAPON SET PRODUCTION.**
**USE TOOLS IN REPO. NOWHERE ELSE.**
(owner, 2026-10-24 04:39 -- these two instructions stand above everything else in this repo)

# PLAN — RS Quest weapon sets (owner approved 2026-10-24 02:35; this file is the only plan)

Current step: **F4**

## Principle
Every shipped gun is built from two sources only: its MESH (tool-measured) and its PARENT MOD (behaviour
parsed from the mod's own code). Nothing retyped from old folders. Quality over speed. "Done" = the
per-gun checklist below, in a headset, signed by the owner.

## Flagship: bd22q (sets/bd22q_1.97, base runtime/ = 1.96b) -- the COMPLETE BD22 VR experience; nothing of it is deferred
- F1  Gate 1.97 on the owner's load order (doom2 → brutal22test6 → BD_VoxelPack → pack); fix; deliver pk3.
- F2  Slug revolver (BD21 Revolver2): roster + RSB break entry (Clip2) + "replaces Shotvolver" row.
      Plus a menu row **"Shot/Revolver Reload: Speedloader / PerRound"** covering BOTH revolvers
      (owner, 2026-10-24): the 2026-10-13 hand patch put BD22's Revolver on a speedloader and left its
      per-chamber rows unused; this makes that a choice instead of a fixed decision, for both guns.
- F3  Options page onto the shared RSQ_Options standard (owner's headset turn for layout).
- F4  Melee on bd22q from docs/VR_MELEE_ON_QUESTZDOOM_2026-10-24.md: pistol whip, rifle/shotgun butt strikes, the spike,
      switch-punching with either hand. Nothing of it exists yet.
- F5  Per-gun ballistics / CombatFX profiles (REMA WMSHEET round/flash/recoil) on bd22q, behind the existing
      Ballistics switch (off = stock BD22). PENDING the owner's yes (added 04:25).
- F6  Reload sounds for the drum / canister / skull (empty today); pack README; HANDOFF update; owner headset pass.

## Then, in this order
- S1  Vanilla / V+ roster + menu (V+ = toggles inside Vanilla per the owner's checklist).  (owner's order, 03:21)
- S2  Modern: player class, every Doom drop/pickup → a modern gun, start Glock.
- S3  BW_Quest (Brutal Wolfenstein; E:\DOOMWork\BW_Quest; parent mod from the owner).
- S4  Aliens, Meatgrinder, survivors of the discarded sets whose parent the owner keeps (re-measure or ditch).
      `sets/aliens/` = presidentkoopa/RS_Aliens_VR-WeaponsQ @ 1ee0cd2, verbatim (owner, 2026-10-24).
- P   Plus pass per set (menu-row extras), only after that set stands.

## Per set
1 inventory the parent mod · 2 measure every mesh fresh, carve/bake parts, sheets, owner signs placement ·
3 numbers parsed from the parent, diffed · 4 build, static check, engine gate (start item, pickups, every
gun fired + reloaded), hand-fit scores · 5 headset pass vs checklist; fixes through the pipe only ·
6 ship with README, menu rows, provenance.

## Definition of done, per gun
parts separate/hidden · reload works in headset · hands ≤1.5 cm on sheet, signed · eject side right ·
sounds · numbers = parent · reachable by start/pickup/toggle · in the menu.

## Changing this plan
Only in its own `[plan]` commit, one line of reason, owner's yes before building. `tools/check_plan.py`
enforces the rest.
