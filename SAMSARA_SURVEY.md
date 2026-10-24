# Samsara -- surveyed, not imported

Samsara-ViewModels-main holds 271 MD3s, 194 PNGs, 39 JPGs, the 7-zip binaries,
build_pk3.bat and a nine-line zscript.zs declaring one empty actor. That is the
whole folder -- verified by listing every file type in it, not by grep.

**There is no MODELDEF in it, and the owner is right that there has to be one
somewhere**: GZDoom cannot load an MD3 without a Model block naming it. So the
MODELDEF exists, it is just not in this copy. Two readings, and the evidence
does not settle between them:

- This repo supplies REPLACEMENT view models and the MODELDEF that points at
  them ships in Samsara-Reincarnation itself, which is not on this disk --
  searched E:\DOOMWork, the Desktop, Downloads and D: and found no Samsara
  pk3, wad or folder.
- Or the copy is partial. There is no .git, so the files were copied rather
  than cloned. build_pk3.bat excludes `filter\` and `src\`, neither of which
  is present, and ZDoom's `filter/` tree is exactly where a per-game MODELDEF
  would live -- but that script says "Stolen from COG lol" at the top, so its
  exclusion list is inherited boilerplate and proves nothing on its own.

Either way nothing can be imported from this folder as it stands, and writing a
MODELDEF from scratch for 180 guns would be throwing away one that already
exists. The thing to find is Samsara-Reincarnation, or the rest of this repo.

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

Someone decides whether 180 guns are worth fitting by hand, and in what order.
A per-set Scale gets them to the right size; nothing gets them into the right
place in the hand except fitting.
