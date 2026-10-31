# brutalwolf (E:\DOOMWork\VR_WeaponSetRebuild\BrutalWolf; .blend sources in br_vr\Brutaldoom_blend_files\_ZMCwolf), 2026-10-31

THE BLENDS ARE THE SOURCE. Every gun was built on one TEMPLATE rig: Main Hand (the controller, with a real
Index controller mesh in the template) -> Handle (the gun) -> Magazine / Trigger / Extra (the parts), each
part on its own one-bone armature with its own authored action. tools/hqt/blendcard.py reads that straight
into a card: roles from the armature names, drop/eject/bolt paths from the animation, and Handle's transform
under Main Hand = the artist's own grip relation. Checked against the exported MD3 on the MP40: identical.
Each folder here has <gun>.blend.card (from the blend) and bw_<gun>.card (md3label on the MD3, roles taken
from the blend) and sheet.png.

Real reload animations on most guns. Baked hand sway only on the melee (axe 112, knife 126, grenade 144 deg).

| mesh | reload / action, authored | eject | note |
|---|---|---|---|
| 1911 | mag drops 13.5 along the grip axis (-0.32, 0, -0.95), frames 7..9; slide 4.0; hammer cocks | none modelled | |
| luger | mag drops 17.2 along (-0.58, 0, -0.81); the P08 TOGGLE: three linked parts, 80/50/5 deg knee on fire | none modelled | |
| MP40 | mag drops 12.0 straight down (0,0,-1) frames 5..9; well mouth (53.5, -0.5, -0.2) | CASING (surf 6) flies +X 12.0 from (36.2, 2.6, 3.2) on fire | blend's Magazine.001/.002 are the stock and receiver recoiling, misnamed |
| PP41 (PPSh) | drum mag drops 11.0 along (0.09, 0, -1.0) frames 5..9 | CASING (surf 0) 7.6 from (35.9, -2.8, 2.6) | |
| STG44 | mag drops 14.0 straight down frames 5..9; bolt (surf 17) 9.0 on fire; 23 named surfaces | none modelled | |
| BAR | mag drops 17.0 straight down; charging handle (surf 3) 13.0; bolt 4.0 | none modelled | |
| Tommy | stick mag drops 14.0 straight down frames 2..10; bolt 9.2 | none modelled | artist-named Bolt / Magazine / Trigga |
| MG42 | top COVER (surf 2) opens 40 deg about X for the belt, frames 10..14; charging handle (surf 3) 15.9 and rotates 90; bolt 10.0 | none modelled | belt-fed: the "mag" is the cover |
| Garand | EN-BLOC CLIP (surf 0, artist "Bullet_pack") goes down 11.4 into the receiver frames 5..13; op-rod 10.0 | none modelled | |
| Kar98 | BOLT ACTION: bolt (surf 4) rotates 89 deg and runs 12.1; STRIPPER CLIP (surf 1) + five rounds (6..10) come in from behind 43 cm frames 17..25 | none modelled | 26 frames |
| Shotgun (trench) | pump (surf 2+3) 6.9 frames 9..17; shells loaded one at a time twice (10..17, 19..28) | shell (surf 6) | 29 frames; blend rig unnamed |
| Chaingun | side AMMO BOX at y -34 (35 cm out), its cover swings 45 deg about X frames 6..15 | none modelled | 17 frames |
| Flame, Axe, Knife, Grenade | no parts | n/a | holds only |

Tool: tools/hqt/blendcard.py (new this pass: the Depot had obj2md3 for blends, nothing that read a rig).

## The frame map (2026-10-31, after the owner: "that shotgun doesn't seem like it pumps")
It pumps. The mesh only has the back-stroke; the code plays `ZSGP ABCDEFGHI`, holds `JKL`, then
`KJIHGFEDCBA`: a full stroke every shot and again after the reload. The MODELDEF (sprite frame -> mesh
frame) and the weapon's states (which sprite frames, in what order) are the frame map; vertex motion
alone cannot show a cycle. `tools/hqt/statephase.py` reads both and every card here now carries a
`states` block. Corrections it made: all reloads here are there-and-back (mag out, same frames reversed
as the fresh one seats); the chaingun's barrels DO spin (0,1,2 cycling) and its reload is the side box
opening 6..15 and back; the Kar98 has two reloads, single rounds (7..11) and the stripper clip (17..25).
