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
