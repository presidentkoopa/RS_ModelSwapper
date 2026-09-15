# ModelSwapper lane: next agenda

Written 2026-09-15 at close of day. In order.

1. **Desktop Selaco patch** (`ModelSwapper-Selaco-Desktop-Patch.pk3`). **Parked, not started.** It waits for the owner's go in the ModelSwapper session.
   - The Selaco lane (selacovr-4b) asked for it for Selaco on UZDXREMA, and the owner wants both hands there.
   - **Plan:** add a desktop mode to `tools_make_selaco_patch.py`, built from `ModelSwapper.pk3`.
     - **Keep:** the Doom sprite-name actor, the `MS_SEL_*` stubs, `modeldef.selaco` with the Selaco shelf and name rows, the Mod Options + MenuLink MENUDEF, and the 8 Heretic/Hexen/Strife class-literal neutralisations.
     - **Drop:** the Weapon→WeaponBase rename, the VR-hand stripping and the lump renames. The Selaco engine has the VR fields, the class alias and both lump APIs.
   - **Load order:** `ModelSwapper.pk3`, then the patch. No autoload.
   - **Check:** selacovr-4b runs the `-norun` and Fresh checks on the Selaco exe.
2. **GitHub release refresh.** An owner decision: put the current builds (with addon support) up as v1.9.4 or v1.9.5, and decide whether the WW2 addon ships as an asset.
   - The old v1.9 release still carries the ballistics pk3s.
3. **RS_PSReload.** Parked until the owner talks to emawind; see `E:\DOOMWork\RS_PSReload\PLAN.md`.
   - Direction: start the weapon's own reload, hold it at the first and last timed frames, with gesture rules per reload type, on QZDoom 17 with minimal engine changes.
   - First step when resumed: a reload recorder.
4. **2.0 skins / tint.** An owner decision. Recommended: park.
5. **Small items:**
   - Unused WW2 frame tails.
   - Flammenwerfer draw/fire frames are guessed.
   - An Assign All "Selaco" set, if the Selaco lane wants one.
