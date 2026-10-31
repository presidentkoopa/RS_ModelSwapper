# BD21 (br_vr/PK3_pbr) cards

Source: `VR_WeaponSetRebuild/br_vr/PK3_pbr` (BD21 MODELDEFs + weapon code + Models/Weapons/Hud),
blend rigs from `br_vr/Brutaldoom_blend_files/BrutalDoom`. Dual skipped (owner). Classic MODELDEFs
bind the SAME meshes as Brutal: one card per mesh, `classic` line notes the second state map.

Every card carries the three sources: MD3 motion (md3label), MODELDEF + weapon states
(statephase, the `states` block), and the .blend rig (`<gun>.blend.card`, artist handle = 20° rake).
Plus a `bd22` block: BD22 Weapons Q was built from these meshes, so its approved hold
(`sets/bd22q/handfit/poses/<Class>.json` gun_move) and the bit-exact bd22->bd21 frame map are on the card.

## Second opinion: BD22 Weapons Q (read only, owner 2026-10-31)
`BD22_SECOND_OPINION.txt` = my first-pass roles vs the roles BD22Q ships (parsed from its MODELDEF
SurfaceSkin masks: which surfaces are drawn clear for "the pump alone", "the magazine alone"...).
Where they differed BD22Q won, because it is the working, headset-proven set:
- pistol: mag is surfs 2+3 (I had 2 as a case). smg: surf 0 is the charging handle (slide).
- shotgun: surf 2 is the SHELL (mesh names it "trigger"; BD22 drives it as the shell at the port),
  4 pump, 5 bolt (rides with the pump 1:1, BoltRatio 1.0). The pump stroke is 6.6 units back at
  frame 18; the shell leaves the port frames 23..28. Numbers from the mesh, both copies identical.
- ssg: surf 0 is the hinged barrel assembly, 2+3 rounds. m79: 4 hinge, 3 round.
- rifle: 0 charging handle, 1 bolt carrier, 3 mag. assaultshotgun: mag is 1+6, 2 slide.
- rpg: the whole pod surfs 5..12 is the magazine. revolver: 1+2 hinge, 5..9 rounds.
- machinegun: surf 3 is the "tube" (BD22's module moves it per cm). unmaker: both skulls 1+2 = mag.
Tool change for this: md3label now carves EVERY surface of a role into one part file
(`carved <role> surfs [...]`), as BD22 masks them together.

## Not yet matched
minigun, flamethrower, hellishmissile, buzzsaw: BD22Q uses RE-CARVED meshes (`*_rsr.md3`) with a
magazine surface the BD21 mesh does not have. These need a carve (tools/carve) before they reload;
cards mark them `carve` pending. Melee/misc (axe, boot, fist, chainsaw, grenade, bfg, bfg10k,
dragonslayer, flamecannon, mp40 ok, plasma ok, railgun ok) agree with BD22Q or have no reload.
