# Samsara -- surveyed, not imported

Samsara-ViewModels-main is a view-model dev build: meshes and nothing else.
There is no MODELDEF anywhere in it, its zscript.zs is nine lines declaring
one class, and build_pk3.bat only zips the folder. Every other package in
the tree arrived with its authors' MODELDEF carrying Path, Skin, Scale,
Offset, ZOffset and a FrameIndex table. Samsara has none of that.

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
