# PLAN — RS Quest weapon sets (owner approved 2026-10-24 02:35; this file is the only plan)

Current step: **F1**

## Principle
Every shipped gun is built from two sources only: its MESH (tool-measured) and its PARENT MOD (behaviour
parsed from the mod's own code). Nothing retyped from old folders. Quality over speed. "Done" = the
per-gun checklist below, in a headset, signed by the owner.

## Flagship: bd22q (sets/bd22q_1.97, base runtime/ = 1.96b)
- F1  Gate 1.97 on the owner's load order (doom2 → brutal22test6 → BD_VoxelPack → pack); fix; deliver pk3.
- F2  Slug revolver (BD21 Revolver2): roster + RSB break entry (Clip2) + "replaces Shotvolver" row.
- F3  Options page onto the shared RSQ_Options standard (owner's headset turn for layout).
- F4  Pack README + HANDOFF update. Owner headset pass on: drum / canister / skull reloads, Machinegun launcher.

## Then, in this order
- S1  BW_Quest (Brutal Wolfenstein; E:\DOOMWork\BW_Quest; parent mod from the owner).
- S2  Vanilla / V+ roster + menu (V+ = toggles inside Vanilla per the owner's checklist).
- S3  Modern: player class, every Doom drop/pickup → a modern gun, start Glock.
- S4  Aliens, Meatgrinder, survivors of the discarded sets whose parent the owner keeps (re-measure or ditch).
- P   Plus pass per set (menu-row extras), only after that set stands.
- M   Melee pass from docs/VR_MELEE_ON_QUESTZDOOM_2026-10-24.md (pistol whip, butt strikes, spike, off-hand switch punch).
- B   Ballistics / CombatFX per-gun profiles (REMA WMSHEET) as a shared layer, after two sets stand.

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
