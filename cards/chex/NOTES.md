# Chex Quest VR Weapons (Chex-Quest-VR-Weapons) -- 9 meshes

Source: the well's `Chex-Quest-VR-Weapons` (MD3 + modeldef.<slot>.txt + actors/weapons/<slot>.txt). No .blend
rigs in the well for this set. Cards: md3label + statephase (`states` block). No BD22 twin.

| gun | mesh | reload | parts (measured) |
|---|---|---|---|
| largezorcher (shotgun slot) | LargeZorcher.md3 78f | YES: a CELL CLIP (surf 9 box + six cells surfs 10..15, one surface per cell = the ammo meter) drops out 43 units at frame 43..46, back in by 61 | carved as ONE mag (cx_largezorcher_mag.md3) |
| superlargezorcher (ssg) | same body + extra barrels (surf 2) | YES, same clip (surfs 10..16) | mag carved; barrel = surf 2 |
| minizorcher (pistol) | 18f | no: nothing clip-shaped; surf 1 = barrel sleeve (1.2 on fire) | -- |
| rapidzorcher (chaingun) | 22f | no | surf 1 = the three-ball barrel cluster, it spins |
| phasingzorcher (plasma) | 45f, 4 surfaces, nothing moves relative to the body | no | -- |
| zorchpropulsor (rocket) | 32f, ONE surface | no | -- |
| lazdevice (bfg) | 11f | CREATIVE: the rack of seven cells on top (surfs 1+2, 3600 v) is the magazine, carved; surf 4 (186 v) moves 1.9 | mag carved |
| spoon (fist), spork (chainsaw) | melee | no | -- |

Open questions are in the owner's queue (2026-10-31).
