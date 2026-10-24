# Carrying the RS_VR_Weapons cards onto the animated meshes

RS_VR_Weapons holds 37 hand-measured WMCARDs. 25 of them measure a STATIC
_wm world model. The mesh ModelSwapper ships is the ANIMATED copy of the
same gun -- the sharing runs right through the set -- so every measured
point in those cards (palm, grip, trigger, muzzle, magcenter, part grab
points) is in the wrong frame until it is moved.

`card_transform.py` solves that move. It cannot fit vertex-to-vertex,
because the two copies were exported separately and their vertex ORDER
differs even where the count matches; and it cannot fit surface-to-surface,
because the _wm copies were merged differently. So it works correspondence
free: the sorted distances from the centroid are invariant to any rotation
or translation, which proves whether it is the same mesh at all, and the
rotation then comes from the principal axes plus the 24 axis-aligned
candidates, scored on the sorted per-axis coordinates.

Apply to a card point p:  p' = R @ p + t

| card                 | animated mesh                            |   rot | translation |
|----------------------|------------------------------------------|-------|--------------|
| WM_Bolter            | models/meat\Bolter\Bolter.md3            | 0.0deg | [ 37.67 0.20 |
| WM_RotaryGun         | models/meat\ChainGun\Chaingun.md3        | 0.0deg | [ 60.83 0.47 |
| WM_RotaryLauncher    | models/meat\RPG\RPG.md3                  | 0.0deg | [ 54.94 0.12 |
| WM_BullpupPump       | models/meat\SSG\SSG.md3                  | 0.0deg | [ 41.27 0.00 |
| WM_Tec9              | models/meat\TEC9\tec9.md3                | 0.0deg | [ 39.31 0.08 |
| WM_AssaultShotgun    | models/bd\AssaultShotgun\AssaultShotgun.md3 | 45.0deg | [ 38.00 -0.05 |
| WM_BFGHeavy          | models/bd\BFG\BFG.md3                    | 45.0deg | [ 39.26 -0.08 |
| WM_SMG               | models/bd\BrutalSMG\BrutalSMG.md3        | 45.0deg | [ 22.94 0.16 |
| WM_Flamethrower      | models/bd\Flamethrower2\Flamethrower2.md3 | 0.0deg | [ 57.03 0.47 |
| WM_MachineGun        | models/bd\Machinegun\Machinegun.md3      | 35.1deg | [ 42.22 0.20 |
| WM_Chaingun          | models/bd\Minigun\minigun.md3            | 30.0deg | [ 55.80 0.48 |
| WM_RPG               | models/bd\RPG\RPG.md3                    | 52.0deg | [ 12.76 10.15 |
| WM_Railgun           | models/bd\RailGun\RailGun.md3            | 45.0deg | [ 39.08 0.14 |
| WM_Rifle             | models/bd\Rifle\Rifle.md3                | 0.0deg | [ 39.52 0.34 |
| WM_Unmaker           | models/bd\Unmaker\Unmaker.md3            | 0.0deg | [ 56.52 -0.02 |
|                      |                                          |   deg |    |

Unsolved: WM_PlasmaRifle -> models/bd/PlasmaGun/Plasma.md3. Proven the same
mesh (shape 0.02) but its principal axes are degenerate -- the gun is
symmetric about the axis it was turned on -- so the 90 degree rotation is
ambiguous and needs a hand check.

Not the same mesh, despite sharing a vertex count: meat/BFG, meat/Saw,
bd/BFG_10k. Coincidence, correctly rejected -- their shape signatures differ
by 6.4, 11.2 and 7.9 units.

Exact matches worth naming: WM_Tec9 onto meat/TEC9 and WM_BullpupPump onto
meat/SSG both solve as a pure translation with zero residual.
