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
