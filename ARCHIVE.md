# Housekeeping, 2026-10-31 (owner: "commence housekeeping")

ModelSwapper main is now three things:
1. **Systems** -- zscript/, modeldef/, MODELDEF.*, WMCARD.*, CVARINFO, MENUDEF, KEYCONF, MAPINFO, build.ps1, quest/, media/.
2. **Meshes + textures** -- inside cards/<set>/<gun>/ next to each card (self-contained folders).
3. **Cards** -- cards/<set>/<gun>/<label>.card, the unified card well (19 sets, 145 meshes, 2026-10-31).

Everything else was moved off main, untouched, to branch **archive/pre-cards-2026-10-31** (commit 2dedcf3):
the old models/ tree (1.5 GB: every imported set incl. Zion, Samsara, Breach, Strife, Universal 3D, classic-doom),
the seven earlier card attempts (cards_anim/_bd/_blend/_carried/_hud/_packs/_shelf), renders*, *_depot copies,
_handfit, _place, the *.before_* backups, the modeldefs_import_*.txt, the survey/handoff markdowns, tools_*.py.
`git checkout archive/pre-cards-2026-10-31 -- <path>` brings any of it back.

Size later (owner): "building it is first, making it pretty comes later."

## MS 1.5 status (2026-10-31, 04:00)
- `tools_gen_from_cards.py` regenerates the donor systems from cards/: `modeldef` (142 `Model MS_<SET>_<Gun>` blocks,
  Path cards/<set>/<gun>, Scale/Offset copied from the source mod's own MODELDEF block), the donor stubs in
  zscript.txt + quest/zscript.txt (GEN-DONORS block), SHELF[]/NAMES[] in zscript/RS_ForeignModels.zs.
  `gen_from_cards.report.md` lists every donor, its family, and the 10 with no source placement.
- build.ps1 ships cards/ (meshes + textures only) instead of models/.
- QuestZDoom 17.3 rig, doom2 + ModelSwapper-QUEST (static build, MODELDEF.rsb/.rsrpump left out): compiles, ZERO script
  errors from the pack, donors draw with their skins. PLACEMENT IS RAW: each donor sits where its own mod's MODELDEF put
  it for a flat HUD (BD21 pistol: huge, in the face). NEXT: the centring/offset pass the 1.x pipeline did
  (tools_reorigin_all.py's compensation) re-done from the cards' grip line + bore, as a generator step.
- MODELDEF.rsb / MODELDEF.rsrpump (the 2.0 break-open and pump reload lumps) still name old models/ paths: re-point
  later with the WMCARD lane.
- zscript_depot, tools_zs_lint.py and the tools_*.py were restored to main: they are systems (the Quest reload code and
  the build's lint), wrongly archived at 03:33.
