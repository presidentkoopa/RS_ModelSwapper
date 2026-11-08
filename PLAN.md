# PLAN: RS_ModelSwapper (owner, 2026-11-08; this file is the only plan)

Current step: **M1**

`none` is also a legal current step; `tools/check_plan.py` accepts it only while every `- F<n>` / `- W<n>` / `- M<n>`
line here is marked DONE. To do new work, add an item in a `[plan]` commit and name it here.

## What this repo is for
Give any Doom mod 3D weapon meshes and VR hand reloads, by the one method, measured with the tools in `tools/`.
The finished hand-built sets (BD22, Aliens, Rusted Legacy) are their own repos; this is the coverage tier and the
workshop. The plan before the merge is `docs/depot/PLAN.md` (the Depot's) and `HANDOFF.md` (ModelSwapper's).

## Items
- M1  THE MERGE (owner, 2026-11-08: "Greenlight on work for ModelSwapper, WeaponDepot, RustedLegacy"). The Depot's
      toolset, rig and handbook in this repo with every commit; one version of each measuring tool with both fix
      sets; `recheck_cards.py` as the gate (baseline kept); ModelSwapper's `tools_kit` and `tools_*` under `tools/`
      with every path repo-relative; the Quest pk3 builds from the merged tree; Rusted Legacy split to its own repo;
      the Depot archived read-only with a pointer here. Done when the owner has the summary and the Depot README points here.
- F14 CRITICAL, NOT STARTED: THE NEW-GUN PIPELINE, COMPLETE (owner, 2026-10-27, restated 2026-11-08: "a god-tier
      toolset and pipeline to scan imported meshes from a variety of formats and export them as labeled and understood
      .md3 files"). Not to be started before the owner says go. Done = a fresh clone takes one mesh (obj / iqm / blend /
      md3; rifle archetype first) and, with tools in this repo only, produces: the parts carved and named; a measured
      card (ports, insert point, stroke, grip line, muzzle); the phases; FBX hands by the one method; reload tables;
      the gun as a choice in ModelSwapper; on tools/rig, zero script errors and frames as proof; one runbook.
      Known gaps (2026-11-08): surface naming is partly by eye (`namedcard` reads artist names, `md3label` reads
      motion; neither is complete alone); `batch.py` guesses archetypes from motion and was last run on the shelf,
      not on the card well; a new gun still needs registry entries by hand (port_gun.GUNS, scene.GUNS, gunlm);
      `blendcard.py` needs Blender; the import side (`obj2md3 --stable-verts`, `iqm2md3`, `blendanim`) was never run
      end to end on one gun with the card as the result.

## To consider, not scheduled (each needs the owner's yes)
- C1  Re-run the five cards whose magazine travels under a non-pistol archetype (BD assault shotgun, rifle, RPG, two
      Chex zorchers) so they carry the `mag_out` / `mag_in` phases the merged `md3label` now writes (RECHECK_BASELINE
      names them). Cards are data; they were left as they are.
- C2  `gen_from_cards.py` no longer reproduces `main` from the lock alone: the 2026-11-03 hand edits (MS_QD_Quad,
      MS_CW_Nailgun, the RC M32 swing-out) were not fed back into the generator, and it sorts its output differently.
      Decide: generator is the source (re-run and accept), or the hand edits are (teach the generator).
- C3  One build for Quest and PC VR with animated meshes on both. The owner reports the Quest animation method was
      found; it is not recorded in this repo (README still says Quest models stay in their rest pose).
