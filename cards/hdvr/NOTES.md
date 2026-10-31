# HDVRweapons -- 9 meshes, 6 of them ARE the BD21 meshes

**VERDICT (owner, 2026-10-31): SKIP THIS SET.** Six meshes are BD21 (already carded), the PBR maps alone are
pointless without the whole set having them, and the three new meshes (BFG, chainsaw, glove) reload nothing.
Cards kept here for the record only; ModelSwapper pulls nothing from HDVR.

Checked vertex-for-vertex against br_vr/PK3_pbr (same surfaces, same frame counts, frame-0 geometry equal):

| HDVR mesh | is | card |
|---|---|---|
| Pistol/Pistol.md3 | BD21 BrutalPistol.md3 | cards/bd21/pistol (copy rows) |
| Shotgun/Shotgun.md3 | BD21 Shotgun.md3 | cards/bd21/shotgun |
| SSG/ssg.md3 | BD21 SSG.md3 | cards/bd21/ssg |
| RPG/RPG.md3 | BD21 RPG.md3 | cards/bd21/rpg |
| PlasmaRifle/PlasmaRifle.md3 | BD21 Plasma.md3 | cards/bd21/plasma |
| Chaingun/chaingun.md3 | BD21 minigun.md3 | cards/bd21/minigun |

Those six are BD21 with PBR materials (materials/*_n/_r/_m/_ao) and a vanilla-Doom MODELDEF (Modeldef.Doom.Weapons.def
binds PISG/SHTG/SHT2/MISG/PLSG/CHGG). "Variants copy rows": no second fit, no second card. The credits.txt says
sketchfab sources; the bytes say BD21.

Carded here (new meshes):
| gun | mesh | reload | parts |
|---|---|---|---|
| bfg | BFG.md3 16f (RD-100 remix) | no | surf 1 (52 v) = trigger |
| chainsaw | Chainsaw.md3 8f (3DHaupt animated) | no | surf 0 = the chain (moves 8 along the bar), body = surf 1 (--body 1) |
| fist | fist.md3 57f | no | two glove surfaces (punch animation) |
