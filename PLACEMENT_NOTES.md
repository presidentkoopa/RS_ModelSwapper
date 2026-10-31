# PLACEMENT_NOTES (tools_placement_from_1x.py, 2026-10-31)

Formula (tools_md3_compensate.py, the engine-matrix replica): `world = S*R*P + Off`, `Off_new = Off_old + S*R*c'` for a mesh shifted by -c.
tools_md3_reorigin centred each 1.x mesh on its rest centroid c, so 1.x mesh = card mesh - c. The card mesh keeps the original origin,
so its Offset is the 1.x Offset with that compensation UNDONE: `Off_card = compensate(-t, Scale, Off_1x, Angle, Pitch, Roll)`, t = card_f0 - old_f0.
ZOffset in a 1.x block overrides Offset.z when it comes after it (engine: last one wins), as tools_reorigin_all.py did.

## Counts: 1x-compensated 28, family-ref 114

## Verification (grip point under old mesh+old numbers vs card mesh+new numbers; must coincide)
- MS_AE_M260b (ref MS_AE_Flamer): old [-4.0039, -51.67, -2.2362]  new [-4.0039, -51.67, -2.2362]  max|d| = 0.00005
- MS_AE_M37a2 (ref MS_AE_Shotgun): old [0.4298, -24.4013, -9.409]  new [0.4298, -24.4013, -9.409]  max|d| = 0.00001
- MS_AE_M4a3 (ref MS_AE_Pistol): old [1.6238, -25.1951, -8.3684]  new [1.6238, -25.1951, -8.3684]  max|d| = 0.00002
- MS_BD_Assaultshotgun (ref MS_BD_AssaultShotgun): old [-0.4199, -31.7998, -9.5498]  new [-0.4199, -31.7997, -9.5498]  max|d| = 0.00005

## Family references

- axe -> MS_BD_Axe (1x-compensated)
- bfg -> MS_BD_Bfg (1x-compensated)
- chaingun -> MS_BD_Minigun (1x-compensated)
- flamethrower -> MS_AE_M260b (1x-compensated)
- grenade -> MS_BD_Grenade (1x-compensated)
- kick -> MS_BD_Boot (1x-compensated)
- launcher -> MS_BD_M79 (1x-compensated)
- machinegun -> MS_BD_Machinegun (1x-compensated)
- pistol -> MS_AE_M4a3 (1x-compensated)
- plasma -> MS_BD_Plasma (1x-compensated)
- railgun -> MS_BD_Railgun (1x-compensated)
- revolver -> MS_Cola_Revolver (1x-compensated)
- rifle -> MS_BD_Rifle (1x-compensated)
- rocket -> MS_BD_Rpg (1x-compensated)
- saw -> MS_RC_Chainsaw (1x-compensated)
- shotgun -> MS_AE_M37a2 (1x-compensated)
- smg -> MS_BD_Smg (1x-compensated)
- supershotgun -> MS_VP_Ssg (1x-compensated)
- sword -> MS_BD_Dragonslayer (1x-compensated)
- unmaker -> MS_BD_Unmaker (1x-compensated)

## Not placed

## Cross-check (grip and muzzle world positions, MODELDEF xyz)
- MS_AE_M37a2 (1x-compensated): grip [0.43 -24.40 -9.41]  muzzle [-0.49 -86.80 -0.58]
- MS_RC_Shotgun (family-ref:MS_AE_M37a2): grip [0.43 -24.40 -9.41]  muzzle [-3.04 -87.28 -6.73]
- MS_AE_M4a3 (1x-compensated): grip [1.62 -25.20 -8.37]  muzzle [0.45 -44.24 -4.91]
- MS_BD_Pistol (family-ref:MS_AE_M4a3): grip [1.62 -25.20 -8.37]  muzzle [0.51 -44.31 -5.32]
Grip points coincide; muzzles agree in distance (the length match) and differ only by each mesh's own bore direction.
Caveat: the 1.x placements were tuned for the flat-screen/first VR builds, in a hand pose the owner has not confirmed;
this table reproduces THAT placement, it does not claim the headset fit.
