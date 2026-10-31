# meatgrinder (E:\DOOMWork\VR_WeaponSetRebuild\BR_VR_MeatGrinder), 2026-10-31

Nine meshes, fire-only animations. The MODELDEFs bind reload sprite frames on the SSG only. BUT the meshes
are built in PARTS -- magazines, bolts, charging handles, pumps, grips are separate surfaces -- and the
animations simply never use them. That is the ModelSwapper case exactly: the part is there, the card says
where it goes, the hands do the reload. "The mesh says it doesn't reload" was a lie on every gun here.

| mesh | what it is (from the parts, not the name) | reload / action parts | eject | note |
|---|---|---|---|---|
| SSG.md3 | a bullpup PUMP shotgun (KSG style), not a break-action | pump = forend+front grip (surf 5) and barrel sleeve (surf 1) slide back 10.8 cm together, frames 6..11 | none modelled | surfaces named by role: 0 trigger, 6 rear grip, 10 stock |
| Shotgun.md3 | a MAGAZINE shotgun | box mag (surf 6, artist-named "Mag", never animated: 8.5 x 12.4 x 13.2 under the receiver); bolt (surf 2) 10.8 cm and charging handle (surf 1) 7.3 cm on fire | none modelled | artist surfaces are named: Sights, Trigger, Receiver, Frame, Mag |
| tec9.md3 | open-bolt SMG, RELOADABLE: detachable 32-round box magazine | magazine is its own surface (792 tris, proven to drop in game); bolt 7.1 cm on fire frames 3..4; the mod's own animation never reloads, the runtime does | -y side | parted mesh used; my own box carve was wrong twice (collar+base, then with receiver wall) |
| Chaingun.md3 | six-barrel rotary | the six barrels (surf 5..10) ARE separate and spin 45 deg per fire frame | none modelled | side grip surf 14 for the support hand |
| RPG.md3 | six-tube rocket pod on the chaingun body | tubes (surf 9,13..17) are still; whole gun recoils 45 deg on fire (removed in _stable) | n/a | |
| Saw.md3 | chainsaw | blade (surf 3) is its own surface, static; surf 5 is a spark effect on fire | n/a | the chain can be made to run: the blade is separable |
| BFG.md3 | one body + trigger | nothing moves | n/a | |
| Bolter.md3 | one body + trigger | nothing moves | n/a | |
| knife.md3 | one surface | nothing moves | n/a | |

Tool fix this folder: md3label.py crashed on an --assign'd part that never moves (the RPG tubes); now written
with travel 0.

## Blend sources (2026-10-31): br_vr\Brutaldoom_blend_files\_Meatgrinder
Same rig tree as BrutalWolf but the armatures are unnamed (older files); blendcard.py walks it by shape and
takes roles from the mesh names. The important find: these guns were AUTHORED TILTED 20 deg in the hand
(Handle rot -160 vs the Wolf set's -180): that is the grip rake, captured in the artist's own file. Each
folder has <gun>.blend.card beside the MD3 card. CHAING.blend has no part armatures (the barrels spin only
in the exported MD3).
