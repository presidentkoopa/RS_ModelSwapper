# cards/ -- the unified card well (moved here from RSQ_WeaponDepot/cards, 2026-10-31)

One folder per MESH, one card per mesh, in the card format ModelSwapper 2.0 reads (md3label output
+ `states` from the mod's MODELDEF/weapon code + the .blend rig + BD22 Weapons Q's hold where one exists).
The measuring tools stay in RSQ_WeaponDepot/tools (hqt, carve); the cards and renders live HERE, where
ModelSwapper pulls from. `<set>/<gun>/sheet.png` is the render of every moving part.

# cards/: one folder per mesh, the unified card

Started 2026-10-31 (owner: "we are starting over to unify everything and allow for posed hands").
Every mesh in the well (E:\DOOMWork\VR_WeaponSetRebuild) gets one folder here, named <set>/<gun>, holding:

- `<gun>.card`      the measured card: parts (from motion), ports (chamber, eject, mag well, load),
                    muzzle, grip line, support feature, phases. Written by tools/hqt/md3label.py; the
                    parts named by the owner (`--assign`), nothing typed twice.
- `<gun>.md3`       the same mesh, lossless, surfaces renamed to the vocabulary, frames named by phase,
                    tags added (tag_grip, tag_support, tag_mag_well, tag_chamber, tag_eject, tag_muzzle, tag_load).
- `<gun>_stable.md3`  the mesh with baked psprite sway removed, when there was any.
- `<gun>_<part>.md3`  carved parts (mag, shell) at their seated origin.
- `sheet.png`       the labelled mesh at its key frames, one colour per part. LOOK AT IT.

The grip line and support point on a card are tool estimates from the mesh ("owner's hand fit
supersedes"). The hand's real hold (wrist on the gun + finger pose) is recorded by the owner in the
headset and added to the card as its `grip` block; nothing here is re-measured when that lands.

Tools: tools/hqt/ (HighQualityTools, restored from archive/depot-2026-10-28 on 2026-10-31).

## When a part is welded into the body (2026-10-31, TEC9)
The labeller only sees surfaces. A magazine the artist left inside the body surface is carved out first
with `tools/carve/md3_carve_surface.py` (a slab crossed with a cylinder, or `--half HA HB` for a box), then
the carved mesh is labelled. The carve moves whole triangles and changes nothing else. A triangle moves only when ALL its vertices
are inside the selector, and a magazine's side triangles run from the base plate up INTO the receiver:
so the slab must reach the receiver line, or you get the collar and the base plate and no magazine
(TEC9, first try). Render the carved piece ALONE and look at it before trusting the triangle count.

## Carving: the cut must be the part's own triangles (2026-10-31, the TEC9)
A spatial box or cylinder selects triangles by where their vertices sit, and a magazine welded into a
body shares vertices with the receiver around its well. Two box cuts of the TEC9 were wrong: the first
took the collar and base plate only, the second took the whole box plus 216 receiver-wall triangles.
The good cut (792 tris, the magazine and nothing else) follows the mesh's own seams. Render the carved
piece ALONE and count what came with it before it goes on a card. A parted mesh that already exists and
is proven to drop in game beats a new carve.

## Three sources, always (2026-10-31, BrutalWolf)
1. The MESH: what moves, how far, along what axis (tools/hqt/md3label.py).
2. The MODELDEF + the weapon's states: which frames play under which state, in what order, forwards and
   backwards (tools/hqt/statephase.py). A pump that only goes back in the mesh comes home in the code.
3. The .BLEND, when there is one: the artist's part names, authored paths and grip (tools/hqt/blendcard.py).
A card that used only the mesh is lying by omission.
