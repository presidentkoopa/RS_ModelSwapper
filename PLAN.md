**NO DRIFT. FOCUS ON WEAPON SET PRODUCTION.**
**USE TOOLS IN REPO. NOWHERE ELSE.**
(owner, 2026-10-24 04:39: these two instructions stand above everything else in this repo)

# PLAN: the RSQ Weapon Depot workshop (owner, 2026-10-28; this file is the only plan)

Current step: **W1**

`none` is also a legal current step, and `tools/check_plan.py` accepts it only while every `- F<n>` and
`- W<n>` line here is marked DONE. To do new work, add an item in a `[plan]` commit and name it here.

## What the workshop is for
Take a set from `sets/`, follow `docs/handbook/`, and turn it into a reloadable, VR-centred set like BD22
VR Weapons Q: hands on every gun, reloads by hand, scopes, melee. The plan before 2026-10-28 (F1-F13: the
bd22q 1.97-1.99 work, the rig, the first fitter) is on the branch `archive/depot-2026-10-28`.

## Items
- W1  THE WORKSHOP AND THE HANDBOOK (owner, 2026-10-28 16:28: "I need this toolset, this test rig,
      instructions for others ... yes, this is how you design these kinds of reloading and weapon mechanics
      in VR on QuestZDoom 17.3"; 16:29-16:4x: "depot must be clean, holding only the sets + BD22 + the
      proven toolset"). The layout cleaned (everything removed stays on `archive/depot-2026-10-28`);
      BD22 VR Weapons Q 2.0.1 copied in as `sets/bd22q`; the toolset proven on BD22 in `tools/`, every path
      Depot-relative or an environment variable; `docs/handbook/` written and followed on a fresh clone
      (`docs/handbook/VERIFIED.md`).
- F14 CRITICAL, NOT STARTED: THE NEW-GUN PIPELINE, COMPLETE (owner, 2026-10-27 16:32: "I want the
      pipeline, complete. With the correct qzd rig and all tools needed. Mark this for a critical task.";
      "That can happen later just don't forget it"). Not to be started before the owner says go. Done = a
      fresh clone takes one md3 (rifle archetype first) and, with tools in this repo only, produces: the
      parts carved/named (mag, bolt/rack, trigger); a measured card (ejection port, insert point, stroke);
      FBX hands (gun hand + support) by the one method; reload tables; the gun as a choice in ModelSwapper;
      on tools/rig, the owner's load order, zero script errors, rig frames as proof, one runbook.
      Known gaps: surface naming partly by eye; the mesh tools (carve, label, card) are on the archive
      branch, not in tools/; a new gun needs registry entries by hand (port_gun.GUNS, scene.GUNS, gunlm).

## The sets, in no order until the owner picks (TABLED: do not start one without his yes)
- S1  sets/vanilla + sets/vanilla_plus: Doom's eight, Doom's names and numbers; V+ = toggles inside it.
      Rebuild from the animated originals (they are stills today), then the handbook.
- S2  sets/modern: player class, every Doom drop / pickup -> a modern gun, start Glock.
- S3  sets/aliens: RS_Aliens_VR-WeaponsQ, through the handbook.

## To consider, not scheduled (each needs the owner's yes)
- C1  RS_VR_Reload's own meshes for clips and magazines (its dropped magazine glows and shows its ammo).
- C2  Project Brutality, a complete brutal voxel set (`sources/pbvp_v2`). Probably REMA, probably standalone.
- C3  Universal real-time scope mod: BD22's live scope (RSQ_ScopeTable + scope zscript) as a standalone,
      data-driven ZScript mod. The handbook's scope recipe is the starting point.

## Definition of done, per gun
Parts separate/hidden; reload works in the headset; hands checked on the sheet and signed; eject side right;
sounds; numbers = parent; reachable by start / pickup / toggle; in the menu.

## Changing this plan
Only in its own `[plan]` commit, one line of reason, the owner's yes before building. `tools/check_plan.py`
enforces the rest.
