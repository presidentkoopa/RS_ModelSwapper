**NO DRIFT. FOCUS ON WEAPON SET PRODUCTION.**
**USE TOOLS IN REPO. NOWHERE ELSE.**
(owner, 2026-10-24 04:39 -- these two instructions stand above everything else in this repo)

# PLAN — RS Quest weapon sets (owner approved 2026-10-24 02:35; this file is the only plan)

Current step: **F6** -- and the only thing left in it is the owner's headset pass.

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
- F4  DONE 2026-10-24. Melee on bd22q: the gun bash (BD22's kick, with the gun in your hands, and an
      RS_CombatFX impact), the pistol whip, the two-handed butt strike (off by default).
      Later the same day, on the owner's instruction: butt strikes extended to all EIGHT stocked
      guns, and melee moved onto the pose spine of the melee document's Part Two section 9 --
      a per-player, per-hand netevent history, which made the snap-turn and teleport patch
      deletable rather than tunable. Two commits were tagged `[step F7]`, which is not a step in
      this file; the work is melee and belongs here. Do not read F7 as a plan item.
      Switch-punching with either hand was ALREADY BUILT in zscript/rsq/fists.zs and needed nothing.
      "The spike" was struck from this line on the owner's instruction: the word entered in this
      repo's first commit, attributed to a melee doc that does not contain it, and exists nowhere
      else -- not in brutal22test6, not in the pack, not in any transcript on the machine.
- F5  DONE 2026-10-24. Per-gun ballistics / CombatFX profiles (REMA WMSHEET round/flash/recoil) on
      bd22q, behind the existing Ballistics switch (off = stock BD22). The owner's yes was given on
      2026-10-24 ("Yes - build F5, the per-gun ballistics and recoil"), so the PENDING note this
      line carried is spent.
      ROUND: the bullet in flight, 11 guns, flying the hitscan itself from muzzle to impact.
      FLASH: the light, 18 guns; the tail, 14 guns, with its interior / exterior pair chosen on
      whether the ceiling over the muzzle is sky.
      RECOIL: 22 guns. Its `roll` and backward shove are NOT carried and cannot be -- tested, not
      assumed: `extend class Weapon` does not compile ("Class Weapon cannot be found in the current
      translation unit"), so the only hook with roll is unreachable on a weapon class this pack does
      not own. `psp.x`/`psp.y`, yaw and pitch, is the whole channel.
      BEYOND THE LINE, from the owner's own list: per-gun impact weight (17 guns, read from
      RSBDEFS' authored `scale` after the derived one proved wrong on every shotgun), impact sound /
      ricochet / light, and the ejection ports and casing sizes.
- F6  Reload sounds for the drum / canister / skull (empty today); pack README; HANDOFF update; owner headset pass.

## Then, in this order
- S1  Vanilla / V+ roster + menu (V+ = toggles inside Vanilla per the owner's checklist).  (owner's order, 03:21)
- S2  Modern: player class, every Doom drop/pickup → a modern gun, start Glock.
- S3  BW_Quest (Brutal Wolfenstein; E:\DOOMWork\BW_Quest; parent mod from the owner).
- S4  Aliens, Meatgrinder, survivors of the discarded sets whose parent the owner keeps (re-measure or ditch).
      `sets/aliens/` = presidentkoopa/RS_Aliens_VR-WeaponsQ @ 1ee0cd2, verbatim (owner, 2026-10-24).
- P   Plus pass per set (menu-row extras), only after that set stands.

## To consider, not scheduled
- C1  RS_VR_Reload's own meshes for clips and magazines, instead of carving each one out of the
      gun's mesh. Port over its DROPPED MAGAZINE in particular: it glows, and it shows the ammo
      still in it. (owner, 2026-10-24.) Today every set carves its magazine from the gun's own mesh
      and the dropped one is that carved piece, unlit and empty-looking. Not scheduled, and not to
      be started without the owner's yes.

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
