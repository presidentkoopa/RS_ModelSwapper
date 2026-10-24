# REVIEW: not melee, and still no reload or rack

Everything here was taken through render + md3label --assign. What
remains is not a labelling gap: these meshes animate FIRING and their
frames contain no reload to measure. Listed so the next pass knows not
to re-derive them -- they need either a reload animation that exists
elsewhere, or a hand-measured card like RS_VR_Weapons' WMCARD.*

| model                  | frames   | what its frames do contain |
|------------------------|----------|----------------------------|
| bd/Unmaker             | 16f      | body only; three salvo-cannon surfaces, none move |
| hacx/Nuker             | 11f      | trigger only |
| hacx/Reznator          | 6f       | nothing moves relative to the body |
| meat/Bolter            | 5f       | trigger only |
| meat/RPG               | 7f       | trigger, hinging 45 degrees |
| meat/Shotgun           | 4f       | trigger and slide; its Mag surface never moves |
| blend/tazer            | 11f      | trigger only -- a stun weapon |
| bd/minigun             | 16f      | barrel spins 106 degrees, trigger; belt-fed, no magazine |
| bd/BFG                 | 16f      | one small mover (trigger class) |
| bd/BFG_10k             | 21f      | one small mover (trigger class) |
| bd/FlameCannon         | 8f       | a single surface; nothing separable |
| bd/Flamethrower2       | 6f       | two small movers (trigger class) |
| meat/BFG               | 11f      | one small mover (trigger class) |
| meat/tec9              | 6f       | bolt strokes 7 along the bore; magazine fused into the body |
| blend/tec9             | 6f       | bolt strokes 7 along the bore; magazine fused into the body |

Newly carded this pass: AssaultShotgun (mag drops 28), M79 (break action,
shell ejects 20 with a 30 degree hinge), Plasma and Dualplasma (battery drops
41), RailGun (Mag-Bat drops 30), bd Shotgun (pump strokes 6.3 with a shell),
Zooka (crossbow bolt travels 87, rotating 152 degrees), RPG (nine rockets).

Melee, effects and single-surface props are excluded: nothing to reload.
