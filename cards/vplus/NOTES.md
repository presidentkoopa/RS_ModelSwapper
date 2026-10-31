# sets/vplus (E:\DOOMWork\VR_WeaponSetRebuild\_01_DOOM_VanillaVRPlus_ErmacPack), 2026-10-31

| mesh | card | eject | note |
|---|---|---|---|
| shotgun.md3 | yes | shell path measured (frames 12..21, 60 cm); pump 7.39 cm, frames 12..23 | roles assigned: 1=pump 2=shell |
| ssg.md3 | yes | two cases out of the open breech, frame 9 | 4=barrel (hinge 59 deg), 2/3=case, 0/1=shell; 4 deg baked sway removed |
| minigun.md3 | yes | NONE: the mesh has no casing, belt or magazine; barrels never spin | a still; only muzzle, trigger, grip, side handle |
| m16.md3 | yes | case right+down 45 cm from (29.2, 0.8, -0.9), frames 1..8 | 1=case; mag well axis (-0.117, 0, -0.993), 23.4 cm clear |
| rev.md3 | yes | six cases out of the tipped cylinder from (36.8, 0, -7.2), frame 20 | TOP-BREAK, not swing-out: cyl+barrel hinge 86 deg together; speedloader seats frame 32; 10 deg baked sway removed |
| chainsaw.md3 | yes (grip only) | n/a | one surface, chain does not run; rear grip + top bar handle, both headset holds |
| Pistol.md3 (Ermac) | already carded in ModelSwapper WMCARD.shelf (MS_vplus_Pistol), full | yes | |
| PlasmaRifle.md3 | already carded (MS_vplus_PlasmaRifle) | n/a | |

Tool gap found: md3label writes `ports/eject` only for magazine guns (chamber + half width). For the pump
and the SSG the eject is the shell/case's own measured path and sits in `parts`, not `ports`.

Folder complete 2026-10-31: 8 meshes, 6 measured here, 2 already carded in ModelSwapper. The grip/support lines on every card are placeholders for the recorded hold.

## questvanillavrplusforclaude (checked 2026-10-31)
The Quest build of the same set. Vertex-checked against `_01_DOOM_VanillaVRPlus_ErmacPack`: rev, chainsaw, m16,
minigun, shotgun, ssg are IDENTICAL (all frames) -> the cards above stand. One mesh the other folder lacked:
`plasma.md3` (32 f, 3 surfaces) -> carded here as `plasma/`. Its Modeldef.Revolver/Rifle/shotty and Decorate are the
Quest-side state maps for the same guns.
