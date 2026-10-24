# REVIEW: not melee, and no reload or rack found

From batch.py's own motion survey, minus everything already carded.
Each of these is a gun whose magazine is hidden inside the body, whose
reload lives in frames the survey did not recognise, or that still needs
render + md3label --assign. A render of every one is in renders_packs/.

Note: RS_VR_Weapons already holds a hand-measured WMCARD for several of
these (Unmaker, RailGun, RPG, AssaultShotgun, Flamethrower, Bolter,
PlasmaRifle, MachineGun). Those cards were measured against the STATIC
_wm world models, whose vertex counts match the animated meshes exactly
but whose bounding boxes do not -- same mesh, re-origined. The numbers
transfer only with that transform applied; they cannot be repointed blind.

| model                | frames           | archetype              | what moves |
|----------------------|------------------|------------------------|------------|
| AssaultShotgun       |  32f/7s/5002v    |  mag_only (MED)        | part drops 28 with no slide: mag change, no ra |
| BFG                  |  16f/2s/7173v    |  arcade (MED)          | 1 small movers only (trigger/hammer class)  |
| BFG_10k              |  21f/2s/7173v    |  arcade (MED)          | 1 small movers only (trigger/hammer class)  |
| FlameCannon          |  8f/1s/5085v     |  arcade (HIGH)         | one surface: nothing separable; tier 0 only  |
| Flamethrower2        |  6f/3s/6155v     |  arcade (MED)          | 2 small movers only (trigger/hammer class)  |
| M79                  |  33f/5s/6858v    |  mag_only (MED)        | part drops 6 with no slide: mag change, no rac |
| minigun              |  16f/6s/5817v    |  mag_only (MED)        | part drops 40 with no slide: mag change, no ra |
| Dualplasma           |  44f/8s/15186v   |  mag_only (MED)        | part drops 41 with no slide: mag change, no ra |
| Plasma               |  30f/4s/7593v    |  mag_only (MED)        | part drops 41 with no slide: mag change, no ra |
| RPG                  |  39f/13s/8482v   |  mag_only (MED)        | part drops 50 with no slide: mag change, no ra |
| RailGun              |  37f/5s/7552v    |  arcade (MED)          | 4 small movers only (trigger/hammer class)  |
| Unmaker              |  16f/3s/11541v   |  arcade (MED)          | 1 small movers only (trigger/hammer class)  |
| Nuker                |  11f/6s/7101v    |  mag_only (MED)        | part drops 8 with no slide: mag change, no rac |
| Reznator             |  6f/4s/7698v     |  arcade (HIGH)         | nothing moves relative to the body  |
| Zooka                |  11f/7s/11996v   |  mag_only (MED)        | part drops 87 with no slide: mag change, no ra |
| tazer                |  11f/2s/15509v   |  arcade (HIGH)         | nothing moves relative to the body  |
| BFG                  |  11f/2s/7173v    |  arcade (MED)          | 1 small movers only (trigger/hammer class)  |
| Bolter               |  5f/2s/4565v     |  arcade (HIGH)         | nothing moves relative to the body  |
| RPG                  |  7f/18s/9707v    |  mag_only (MED)        | part drops 6 with no slide: mag change, no rac |
| tec9                 |  6f/4s/5469v     |  bolt_or_slide (MED)   | rear part strokes 7 along bore, no mag drop  |

Melee, effects and single-surface props are excluded: nothing to reload.
