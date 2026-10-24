# Samsara -- surveyed, not imported

Samsara-ViewModels-main holds 271 MD3s, 194 PNGs, 39 JPGs, the 7-zip binaries,
build_pk3.bat and a nine-line zscript.zs declaring one empty actor. That is the
whole folder -- verified by listing every file type in it, not by grep.

**FOUND IT.** The owner was right that a MODELDEF has to exist, and it does --
in a different repository.

`Samsara-Reincarnation/Samsara-ViewModels` ships the MESHES. The MODELDEFs live
in `Samsara-Reincarnation/Samsara-Reincarnation`, the mod itself, one per set:
MODELDEF.rtcw, .ge, .gf, .q3, .sof, .pk, ModelDef.dx, ModelDef.U1, plus d64, de,
df, dn64, hex2, hl, ol, q1, q2, str and a filter/doom.ce.doom64/MODELDEF.txt.

Checked rather than assumed -- every viewmodel mesh name resolves in the mod:

    bj_colt.md3        -> MODELDEF.rtcw
    bj_bar.md3         -> MODELDEF.rtcw
    sarge_bfg10k.md3   -> MODELDEF.q3
    daniel_asg.md3     -> MODELDEF.pk
    w_autoshotgun.md3  -> MODELDEF.sof and zscript/Core/sof.zs
    asmd.md3           -> ModelDef.U1
    AssaultGun3rd.md3  -> ModelDef.dx
    ar33_left.md3      -> zscript/Core/goldeneye.zs

The ViewModels copy on disk is NOT partial: the GitHub repo holds 530 entries
against 511 files here, and the difference is directories. That repo genuinely
carries no MODELDEF, because it was never meant to.

Cloned to VR_WeaponSetRebuild/Samsara-Reincarnation -- 47,346 files, 1.2 GB.
MODELDEF.rtcw alone is 276 Model blocks, and its frame tables run past 500,
with blocks compositing several MODEL indices over one shared animation.

It is also eight weapon sets in one folder, not one:

| set          |  guns | flashes | median size | scale to reach ~120 units |
|--------------|-------|-------|---------|---------------------------|
| DeusEx       |    15 |     0 |    24.2 | x5.0 |
| Goldeneye    |    44 |    36 |    30.1 | x4.0 |
| Goldfinger   |    47 |    38 |    36.7 | x3.3 |
| Painkiller   |     8 |     0 |     9.8 | x12.2 |
| Quake3       |    15 |     0 |    26.8 | x4.5 |
| RTCW         |    25 |    17 |    36.3 | x3.3 |
| SoF          |    11 |     0 |    29.6 | x4.1 |
| Unreal       |    15 |     0 |    65.1 | x1.8 |

180 gun meshes and 91 muzzle flashes. Every one of them is animated.

## The scale problem is real but it is not in the mesh

These were authored as flatscreen view models and never given a VR MODELDEF, so
they sit at 10 to 65 model units where a gun already working here is 90 to 120
(Kar98 121, bd Machinegun 89). That is a Scale line, not a mesh defect, and the
figure is derivable from the measurement above.

## What is NOT derivable

Offset and ZOffset place the gun in the hand, and nothing in the mesh says where
that is. On every other package those numbers are the author's and we copy them.
Here they would have to be fitted per gun, 180 times, by eye.

Goldeneye and Goldfinger are also dual-wield sets -- their meshes come in
_left/_right pairs -- so their 44 and 47 are closer to 22 and 23 distinct guns
seen twice.

## Before any of it lands

The Offset and ZOffset are no longer ours to invent -- the mod's MODELDEFs carry
the authors' numbers, the same as every other package. What does still need
deciding is the scale. Samsara's own Scale lines are flatscreen values (0.8, 1.0,
1.5, 2.0 and a lot of -1.0), which is why the meshes measure 10 to 65 units
against 90 to 120 for a gun already working here. Those are the numbers that
would have to be adjusted for VR -- not guessed from the mesh.
