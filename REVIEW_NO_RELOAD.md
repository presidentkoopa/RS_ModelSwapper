# REVIEW: reload status by gun

## Already measured -- a card exists, do NOT re-derive

These 19 meshes are byte-for-byte the same geometry as a mesh
RS_VR_Weapons already carded by hand. The card was measured against the
STATIC _wm copy; the mesh wired here is the ANIMATED one. Same vertex
count, different origin, so the card's points transfer once the offset
between the two is applied. Never ship the _wm mesh -- the mesh sharing
runs through the whole set.

| animated mesh                              | verts | frames | card |
|--------------------------------------------|-------|------|----------------|
| models/meat\BFG\BFG.md3                    |  7173 |   11 | WM_BFGHeavy |
| models/meat\Bolter\Bolter.md3              |  4565 |    5 | WM_Bolter |
| models/meat\ChainGun\Chaingun.md3          |  5180 |    6 | WM_RotaryGun |
| models/meat\RPG\RPG.md3                    |  9707 |    7 | WM_RotaryLauncher |
| models/meat\SSG\SSG.md3                    |  7472 |   12 | WM_BullpupPump |
| models/meat\Saw\Saw.md3                    |  7399 |    6 | WM_LongbarChainsaw |
| models/meat\TEC9\tec9.md3                  |  5469 |    6 | WM_Tec9 |
| models/bd\AssaultShotgun\AssaultShotgun.md3 |  5002 |   32 | WM_AssaultShotgun |
| models/bd\BFG\BFG.md3                      |  7173 |   16 | WM_BFGHeavy |
| models/bd\BFG\BFG_10k.md3                  |  7173 |   21 | WM_BFGHeavy |
| models/bd\BrutalSMG\BrutalSMG.md3          | 21072 |   27 | WM_SMG |
| models/bd\Flamethrower2\Flamethrower2.md3  |  6155 |    6 | WM_Flamethrower |
| models/bd\Machinegun\Machinegun.md3        | 16748 |   36 | WM_MachineGun |
| models/bd\Minigun\minigun.md3              |  5817 |   16 | WM_Chaingun |
| models/bd\PlasmaGun\Plasma.md3             |  7593 |   30 | WM_PlasmaRifle |
| models/bd\RPG\RPG.md3                      |  8482 |   39 | WM_RPG |
| models/bd\RailGun\RailGun.md3              |  7552 |   37 | WM_Railgun |
| models/bd\Rifle\Rifle.md3                  |  9804 |   32 | WM_Rifle |
| models/bd\Unmaker\Unmaker.md3              | 11541 |   16 | WM_Unmaker |

## Carded from motion this session

wolf: MG42 (drum swings 40 deg), MP40 (mag drops 12), PP41 (11), BAR (17),
Kar98 (stripper clip seats frame 21), Garand (en-bloc frame 11), plus 1911,
luger, STG44, Shotgun and Tommy from batch.
bd: AssaultShotgun, M79 (break action), Plasma, Dualplasma, RailGun,
Shotgun, Zooka, RPG, minigun.

## Still genuinely unmeasured

| model | frames | why |
|---|---|---|
| meat/Shotgun | 4f | no card anywhere and its Mag surface never moves in four frames |
| hacx/Nuker | 11f | trigger only in its frames |
| hacx/Reznator | 6f | nothing moves relative to the body |
| bd/FlameCannon | 8f | a single surface; nothing separable |

Melee, effects and pickups are excluded: nothing to reload.
