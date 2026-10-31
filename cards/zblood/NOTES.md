# ZBlood VR (ZBlood-VR/ZBlood-VR-Weapons) -- Ermac; carded from the well's copy

Two parallel model sets in the mod: `models/3d/` (smooth, carded here) and `models/voxel/` (voxel-converted MD3 of
the same guns, not carded: same roles, blockier). GOLD: artist-named surfaces. The difficult part of this folder is
the OFF-HAND system (zscript/offhand_weapons.txt: dynamite, remote, proxy, zippo, doll, fist are off-hand weapons
with their own lighter/arm meshes) -- that is code, not mesh, and belongs to ModelSwapper's off-hand lane.

| weapon | mesh | reload | parts |
|---|---|---|---|
| sawedoff | shotgun.md3 33f + shotgun_shell.md3 (two shells, 33f) | YES: `sg_barrel` hinges (break open, 42 units at the muzzle), `sg_bolt1/2` move, the SHELLS are the mod's own second mesh (copied as zb_sawedoff_shells.md3); SawedOff.txt has ReloadGun | body = `sg_body` (the stock, 117 v) |
| tommygun | tommygun.md3 19f | no magazine surface (stick/drum not separable); `tommy_handle` = foregrip, trigger guard, trigger | no reload without a carve; owner to say |
| flaregun | flaregun.md3 23f | no break modelled; trigger guard + trigger | no |
| napalm | napalm.md3 13f | `napalm_bottom` (tank underside), handle, trigger | no |
| teslagun | teslagun.md3 47f | `teslarifl_barrel` | no |
| lifeleech | lifeleech.md3 20f + leechbuddy.md3 | grip, hand grip, eye glow | no |
| spraycan | spraycan.md3 43f | `lighter` + `spraycan` (two hands' worth) | no |
| pitchfork, voodoo doll, zippo (lid flips 15), tnt family (tnt/proxy/remote/lighter) | melee / thrown | -- | tnt/ holds the five throwable meshes |

`_hands/`: caleb_hand.md3 (232 v, 7 frames) + voodoo_hand/voodoo_fist -- Caleb's hand, a SIXTH hand source.
