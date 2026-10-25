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

- F10 **EVERY NON-MELEE GUN RELOADS.** The owner's objective, stated plainly on 2026-10-25:
      "we want reloading for all weapons that are not melee / if bd22 does not allow it then we
      already ship our own weapon code anyway so why not". That settles it. 28 guns carry hands,
      3 are melee (BrutalAxe, Chain_saw, DSweap), and the other 25 all reload when this step ends.
      17 do today. These 8 do not.

      I TWICE TRIED TO CLOSE GUNS IN THIS STEP AND WAS WRONG BOTH TIMES. Once by reading a card's
      design note as if it were a law -- a card is REMA's decision, not the owner's, and he owns
      this pack. Once by declaring a part "absent" from SURFACE NAMES without looking at the
      geometry, when a welded surface can hold many separate bodies (M249_lowpoly holds 124).
      Neither is evidence that a gun cannot reload. Do not close a gun in this step without the
      owner saying so.

      SOURCE RULE (owner, 2026-10-25): **no `_wm` meshes. Cards only, against our own animating
      copies.** THE CARD MEASURES; OUR MESH ANIMATES. The reason is in the frame counts:
      REMA's `machinegun_wm.md3` has ONE frame -- it is a static reference pose with the surfaces
      already split -- while our `Machinegun.md3` has 36, our `SSG.md3` 46, `M79.md3` 26,
      `Minigun.md3` 12, `m32.md3` 2. Ship a `_wm` and the gun goes stiff. (The existing carves
      used a `_wm` for vertex CORRESPONDENCE only and kept all our frames, which is why MG42,
      Flamethrower and Unmaker still animate -- but the owner has ruled that route out, and the
      card does not need it.)
      A card's numbers are in the CONTROLLER's frame, which is mesh-independent: where the part
      is, which way it comes out, how far it travels. That transfers to our animated mesh without
      touching theirs. The join to make: the cards name REMA's surfaces (`canister`, `barrels`,
      `forend`) and ours are named differently (`Runko`, `Pipe`, `magazine`) -- so locate the part
      in OUR mesh by the card's position, not by its surface name.

      WHAT MAKES A GUN RELOADABLE, from the one that works (BD_Flamethrower):
          firesfrom = magazine       capacity = 200       magfamily = "bd_fuel"
          part canister -> role = feed, surface = canister, dof kind = slide
      A capacity and a `part` with `role = feed`. Capacity is NOT a blocker and never was: the
      owner's point is that we invent it. MG42 200, Flamethrower 200, Unmaker 60 are all numbers
      chosen off his REMA sheet because BD22 has none.

      FIVE OF THE EIGHT ALREADY CARRY A CAPACITY AND AN AMMO FAMILY. They are `firesfrom = reserve`
      with no feed part, and that is the ONLY thing missing:
          BD_Machinegun  100  bd_40mm       BD_Minigun  200  bd_762
          BD_BFG          40  bd_cell       BD_BFG10k    99  bd_cell
          BD_Hellish       6  bd_hell
      Someone already decided a Minigun holds 200 of 7.62 and a BFG holds 40 cells. Adding a feed
      part to a card is an edit to a card, not a new system.

      THREE HAVE NO CARD AT ALL -- IncendiaryLauncher (M32), NukeLauncher (Nuker), Devastator
      (Sidewinder). Those need one made, the way every other card in this pack was.

      Per gun:
        * **IncendiaryLauncher = M32**, a Milkor MGL: a six-shot revolving cylinder. DO THIS ONE
          FIRST -- it is the easiest gun left, not the hardest. `models/bd/M32/m32.md3` ships the
          magazine ALREADY NAMED as its own surface (`magazine`, 484 v / 488 t) with
          `magazine_back`, `magazine_bracket` and `magazine_bracket_front` beside it, so there is
          nothing to carve. A revolving cylinder is the Revolver's reload shape, and the pack has
          that system twice over (speedloader and per-round, both on a menu row).
        * **GrenadeLauncher = M79: ALREADY BUILT. NOT IN THIS STEP.** I put it in the gap on
          2026-10-25 and it was never in the gap -- it is break index 2 in `zscript/rsr/rsb_guns.zs`
          with hinge (18.3427, -0.1278, -3.7417), which matches its survey record's (18.3, 0.0,
          -3.7), and its own "GrenadeLauncher/Open" sound. I had counted the reload set from
          `rsr_guns.bd.zs` alone, which is the MAGAZINE table; the pump and break guns live in
          `rsr_pump_guns.zs` and `rsb_guns.zs`. Count all three or the answer is wrong.
        * **Machinegun** -- card BD_Machinegun, 100, bd_40mm, needs a feed part. Its `Reload:`
          jumps straight to `Ready` under `RSM_VR` (`Machinegun.dec:229`), so the hand reload is a
          no-op today; the underbarrel 40mm is hand-loaded and stays so (`rsr_m203.zs`). The card
          carries a note saying a magazine swap "should never have had" -- that was a REMA
          decision and the owner has overruled it. The box DOES separate: our `M249_lowpoly` is
          11996 verts, which is REMA's `body` 11581 + `magazine` 415 exactly. Find it in our own
          mesh, not by loading theirs.
        * **Minigun** -- card BD_Minigun, 200, bd_762, needs a feed part. The card already has
          `part barrels` (hinge) and `part forend`, so the gun is partly described. Its surface
          names in our mesh are Runko / Runko / Pipe / Runko / Trigger / Grip, which do not match
          the card's; that is the join to make, not a reason to stop. F8 closed its EJECTION PORT,
          which is a different question from its feed -- do not carry that conclusion across.
        * **BIG_FUCKING_GUN** -- card BD_BFG, 40, bd_cell, needs a feed part. Ermac's Force
          Unleashed has `pod_bfg.md3` and a FOUR-step pod reload (unload, grab, insert): the right
          SHAPE for a BFG reload, from the man who invented this. Shape only -- his numbers are a
          different gun.
        * **BFG10k** -- card BD_BFG10k, 99, bd_cell, needs a feed part.
        * **HellishMissileLauncher** -- card BD_Hellish, 6, bd_hell, needs a feed part.
        * **Devastator** (`Sidewinder/sidewinder.md3`) -- no card. Make one.
        * **NukeLauncher** (`Nuker/Nuker.md3`) -- no card. Make one.
        * **GrenadeLauncher = M79: ALREADY DONE, leave it alone.** (Kept in this list only so the
          next reader does not re-open it -- see the note below.)
      THE M32 IS MEASURED ALREADY and is the one to build first -- it needs no carve and no
      `_wm`, because its `magazine` is its own surface in the mesh we ship.
      (2026-10-25, `rgeo.py`, controller frame, cm F/L/U.) The `magazine` surface:
      centroid (14.60, -0.03, -4.04), principal axis (-1.000, 0.001, 0.003) -- along the bore --
      extent 17.38 cm, radius mean 7.57 / max 10.27. A drum 17.4 long and ~15 across, on the bore
      line, centred 14.6 forward and 4 below, dead centre laterally. An MGL cylinder.
      Frame 1 is a RECOIL pose, not a reload: every surface shifts back 7-8 cm with some muzzle
      rise. There is no open/eject animation in this mesh, so the motion is ours to drive -- which
      is how every other gun in the pack does it.

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
