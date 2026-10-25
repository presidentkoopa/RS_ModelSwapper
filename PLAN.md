**NO DRIFT. FOCUS ON WEAPON SET PRODUCTION.**
**USE TOOLS IN REPO. NOWHERE ELSE.**
(owner, 2026-10-24 04:39 -- these two instructions stand above everything else in this repo)

# PLAN — RS Quest weapon sets (owner approved 2026-10-24 02:35; this file is the only plan)

Current step: **F10** -- F1-F9 are DONE and committed (2026-10-25). F10 finishes the roster: the two
remaining non-melee guns that can reload. The owner's headset pass on F1-F9 is still outstanding and
is what gates the 1.99 release; nothing in this pack has ever been seen in VR.
The S items are TABLED; do not start one.

(`none` is also a legal current step, and `tools/check_plan.py` accepts it ONLY while every `- F<n>`
line here is marked DONE. It is not a way to commit off-plan: start a new F item in a `[plan]` commit
and name it here instead, which is what F10 is.)

## Principle
Every shipped gun is built from two sources only: its MESH (tool-measured) and its PARENT MOD (behaviour
parsed from the mod's own code). Nothing retyped from old folders. Quality over speed. "Done" = the
per-gun checklist below, in a headset, signed by the owner.

## Flagship: bd22q (sets/bd22q_1.97, base runtime/ = 1.96b) -- the COMPLETE BD22 VR experience; nothing of it is deferred
- F1  DONE 2026-10-24. Gate 1.97 on the owner's load order (doom2 → brutal22test6 → BD_VoxelPack →
      pack); fix; deliver pk3. Runs clean; pk3 handed over. The headset pass is the owner's.
- F2  DONE 2026-10-24. Slug revolver (BD21 Revolver2): roster + RSB break entry (Clip2) + "replaces
      Shotvolver" row.
      Plus a menu row **"Shot/Revolver Reload: Speedloader / PerRound"** covering BOTH revolvers
      (owner, 2026-10-24): the 2026-10-13 hand patch put BD22's Revolver on a speedloader and left its
      per-chamber rows unused; this makes that a choice instead of a fixed decision, for both guns.
- F3  DONE 2026-10-24. Options page onto the shared RSQ_Options standard. Four rows it was missing;
      the layout itself is still the owner's headset turn.
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
- F6  DONE 2026-10-24 (code) / 2026-10-25 (docs). Reload sounds for the drum / canister / skull
      (they had shipped silent since F1); pack README; HANDOFF update; release numbered 1.99.
      **The owner's headset pass is the one part still open, and it is the only thing that can test
      any of this.** It is his to do, not a tool's.

- F7  DONE 2026-10-25 (`65ad27e`). The real casing meshes. The brass leaves the right port at the
      right size, but it was still Brutal Doom's sprite. RS_Ballistics has measured 3D casings --
      9mm, .357, .45, 5.56, 7.62, 12ga -- and the pack already lends a model to a foreign actor
      twice over (voxels.zs, RSQ_Debris). Lent the same way, per instance, so one EmptyBrass is now
      four cartridges: `zscript/rsq/casemodels.zs`, 4 mesh holders, `CASE_FOR` over 12 guns.
      The lend sat behind the VR gate at first and printed zero; it is above it now.
- F8  DONE 2026-10-25 (`0f9a5d2`). A port for the MP40, the Minigun and the Machinegun. Two of the
      three were a mistake of mine, not a missing feature: I had filtered for SIDE-facing holes,
      which hides every belt-fed gun in the set. **The Machinegun had a chute all along** --
      7.1 x 10.2, centred, below the bore by the breech, the same signature as the MG42 and found
      by the same rule, which is now a box in the table instead of a thing I remembered to check.
      Port (14.3, -0.3, -4.3), DOWN. **The MP40's is CONSTRUCTED, not measured**, and the generated
      file says so on the line: every slot in its receiver tube is mirrored (cooling slots) and the
      one unmirrored opening is the cocking-handle slot, so it is built from `zamek` (bolt, trimmed
      to its core) and `korpus` (receiver) on the bore line, where a blowback gun ejects. It is in
      only because it corroborates: it lands at 68% of the MP40's length, and the owner's own
      hand-tuned BrutalSMG port sits at 68% of THAT gun. Port (34.7, -2.2, 3.3), SIDE.
      **The Minigun keeps throwing from the body, permanently.** Every down-facing loop on it is
      structural -- the rotating body's own open ends, the grip, the six bores -- and there is no
      bolt or breech surface to construct one from. Nothing to measure, nothing to build on,
      nothing invented. This question is CLOSED; do not go hunting for that port again.
      11 ports, up from 9.

- F9  DONE 2026-10-25 (`bd8fa71`). A gate ANY LANE can point at its own set. gate/bd22_gate.sh had
      hardcoded bd22q's four paths, its parent mod and its weapon class names, so a lane building
      another set could not use it. Split into `gate/run_set.sh` (generic) plus `gate/bd22q.gate`
      (this set's paths, guns and ammo); bd22_gate.sh is now a one-line wrapper, keeping the name
      this file and HANDOFF have always used. A marker per gun, so the log says WHICH guns were
      actually reached. The method and the eight traps are written down in `gate/GATING_A_SET.md`.
      (owner, 2026-10-25: "another lane is doing another weaponset, they need to be able to do
      what you just did".) Also packaged as a standalone skill at
      `C:\Users\Command\.claude\skills\gate-a-doom-mod\`, and sent to the RS ModelSwapper lane on
      the owner's instruction, 2026-10-25.

- F10 The rest of the roster. 28 guns carry hands; 3 are melee (BrutalAxe, Chain_saw, DSweap) and
      17 of the other 25 reload by hand. The owner's objective is that every non-melee gun reloads,
      and no F item covered the remaining eight. He ruled on them 2026-10-25:
        * **IncendiaryLauncher = M32**, a Milkor MGL: a six-shot revolving cylinder. DO THIS ONE
          FIRST -- it is the easiest gun left, not the hardest. `models/bd/M32/m32.md3` ships the
          magazine ALREADY NAMED as its own surface (`magazine`, 484 v / 488 t) with
          `magazine_back`, `magazine_bracket` and `magazine_bracket_front` beside it, so there is
          nothing to carve. A revolving cylinder is the Revolver's reload shape, and the pack has
          that system twice over (speedloader and per-round, both on a menu row).
        * **GrenadeLauncher = M79**, break action -- the owner's call, and the mesh agrees: a
          surface named `Shell` (828 v) and 26 frames on a 5-surface model, which is an open/close
          animation already in there. Break-open is a system the pack runs six times.
        * **Minigun: NOT in this step.** `models/bd/Minigun/Minigun.md3` is Runko / Runko / Pipe /
          Runko / Trigger / Grip -- no belt, no drum, no magazine, no ammo surface. Nothing to
          grab. This is the SECOND time this gun has come back empty, after F8's ejection port, and
          for the same reason: the part is not modelled. Only an imported mesh could change that
          (Ermac's `mag_chaingun.md3` and `cg_ammo1..10` exist but are a different gun, so they
          would be a stand-in, not a measurement). Do not re-derive this; the answer is in the mesh.
        * **Devastator, BFG10k, BIG_FUCKING_GUN: not wanted.** "if the bfg never reloads i wont
          lose sleep" (owner). Note for later only: Ermac's Force Unleashed has `pod_bfg.md3` and a
          FOUR-step pod reload (unload, grab, insert), so a BFG reload is precedented if he asks.
        * **HellishMissileLauncher, NukeLauncher: ruled out.** "dont need a reload" (owner).
      Numbers come off these two meshes with the repo's own tools, as every other gun's did.

## Then, in this order
TABLED 2026-10-25 (owner): the four sets below wait. **Priority is bd22q.**
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
