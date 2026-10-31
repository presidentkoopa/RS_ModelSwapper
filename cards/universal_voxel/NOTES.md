# Universal Doom Voxel Weapons VR (Universal_Doom_VoxelWeapons_VR) -- Ermac; three switchable sets

Owner: "prob nothing here". Mostly right. Measured:

1. **Voxel set (Chell)** -- `Pistol.md3`, `Shotgun.md3`, `DoubleSG.md3`, `Chaingun.md3`, `Launcher.md3`, `PlasmaRifle.md3`, `BFG.md3`:
   voxel models converted to MD3, ONE surface, 250 IDENTICAL frames each (static). Nothing moves, nothing to card.
   The real voxels are `VOXELS/Weapons/Hud/*.kvx` (16 files) -- not MD3, outside the tools.
2. **Alt set (Rogue_Steve)** -- `*_alt/doom*-NN.md3`: one static single-frame MD3 PER ANIMATION FRAME (doompistol-00..03,
   -slideback; doomssg-00/01/03/04/-maximum/-reloadend; doomsg-00/-pump1..3). MODELDEF swaps whole files per frame.
   No parts, no card.
3. **D4 set (Doom 2016 look)** -- low-poly, and the only one with PARTS:
   | gun | mesh | parts |
   |---|---|---|
   | ssg_d4 | sssg.md3 8f + sssg_shell.md3 (two shells, 8f) | `sssg_barrel` hinges 47.6 (break open); the SHELLS are the mod's own second mesh: copied as uv_ssg_d4_shells.md3. Reloadable |
   | shotgun_d4 | sshot.md3 4f | `sshot_pump` (58 v) travels 3.8 | pump |
   | chaingun_d4 | schaingun.md3 2f | `schaingun_barrel` spins | no reload |
   | pistol/plasma/rpg/bfg _d4 | one surface, 2..3 frames | no parts | no reload |

Universal_Doom_3DWeapons_VR (the other Universal folder) has not been compared yet; its big MD3s are probably these.
