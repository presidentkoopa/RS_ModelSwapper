# tools/questhands: the RS_QuestHands hand-fitting kit (TEST/MEASURE tooling, never ships)

Moved in for PLAN.md F12 (2026-10-26) from RS_QuestHands `tools/posefix/hands/` -- the tools behind
the 1.92 hand poses. The method, the transform chain and the fitting modes are in `HAND_FITTING.md`
(moved as is; it still names the kit's own layout, e.g. `hands/ermac.py`, `../rsq_hands_gen.py`,
`../vplus/fit/`, `rtest/`, which were NOT moved). Code unchanged except the paths (each change is
marked `F12` in the file). Needs python3 with numpy, scipy (align only) and Pillow.

## Paths (environment)
| variable | what | default |
|---|---|---|
| `RSQ_GUNPACK` | an extracted pack folder with `MODELDEF.bd.txt` and its `models/` (was `<scratchpad>/v7x`) | `tools/rig/build/src/bd22q_192/src` -- tag 1.92 of RS_Brutal22WeaponsQ, checked out by `sh tools/rig/setup.sh` |
| `RSQ_ERMAC` | Ermac's Force Unleashed `doom-force-unleashed_devbuild/models/` (`hand/hand.md3`, `hand/hand2.md3`, his gun meshes in `ermac.SETS`). Not vendored. | none: a clear error if unset or a file is missing |
| `RSQ_HAND_MD3` | the cut `hand.md3` (RS_QuestHands `tools/posefix/vrmelee/models/rsq/hand.md3`); only `support.hand_item()` reads it | none: a clear error |
| `RSQ_QH_OUT` | check sheets and temp images | `tools/questhands/out/` (gitignored) |
| `RSQ_FITS` | the fits file `fitall.py` / `minigun_fit.py` read and write | `tools/questhands/fits.json` |

## The files (what each does, read from the code)
| file | what |
|---|---|
| `hudrender.py` | the QZD HUD-model chain (`to_local`: MODELDEF scale/offset, hook translation + yaw/pitch/roll, jDoom Ry(90), vr_weaponScale 1.02) and a shaded perspective render from any eye; MD3 loader |
| `gunview.py` | orthographic side/bottom/front/top views of HUD models (md3 or skinned IQM) on a 5 cm grid, controller frame F/L/U cm, with markers; `to_fl()` local -> F/L/U |
| `pk3model.py` | parses a pack's MODELDEF into blocks; `lookup(class, sprite, frame)` -> mesh path, mesh frame, scale, offset |
| `guns.py` | BD22 classes' ready sprite/frame (`READY`) and `item(cls)`: the gun as the pack places it (Sniper takes the v8 placement override) |
| `ermac.py` | Ermac's sets: gun mesh, gun frame, hand.md3 / hand2.md3 frames (`SETS`), his placement `PL`, `path()` |
| `handtable.py` | BD22 gun -> Ermac set for the gun hand, for the support hand, and where the support goes (`wrap` F, `vgrip` box, `same`, `handle`) |
| `support.py` | cross-sections of a gun at F (`section`), the support point on the front (`front_point`), the mirrored-fist hook/rotation solver (`solve`, `euler_yxz`, `rot`) |
| `align.py` | the fit: samples Ermac's gun surface, keeps the patch his hand holds (3 cm), fits it onto the BD22 gun by translation-only trimmed ICP in a box; `hook_from_shift()` |
| `handfit.py` | `hand_items()` (Ermac's hands placed by shifts) and `sheet()`: side + bottom + player-eye check sheet |
| `fitall.py` | runs every gun in `handtable.TABLE` (or those named): gun-hand ICP, support by mode, writes check sheets and merges into `fits.json` |
| `minigun_fit.py` | `rot_hook()`: turns a pose about its centre and moves it to a target; fits the Minigun's side handle and writes its `fits.json` entry |
| `fits.json` | the fit results the 1.92 hand tables were generated from (RS_QuestHands copy, unchanged) |
| `HAND_FITTING.md` | how the hands were fitted, the transform chain, modes, checking |

`fitall.py` and `minigun_fit.py` WRITE `fits.json`: they refit. Do not run them to "check" anything;
F12 moved them, it did not refit. The measuring side needs only the pack, e.g. the support point
and a side view of a 1.92 gun:

```
cd tools/questhands
python3 -c "import support, gunview, guns; print(support.front_point('Rifle', 28)); \
  gunview.view([guns.item('Rifle')], 'out/Rifle_side.png', 'side', title='Rifle 1.92')"
#  ([28, 0.0, 1.38], (-1.12, 6.29))  = fits.json's Rifle target
```

Measured 2026-10-26 (F12) on the 1.92 pack: `front_point` at each `wrap` gun's F reproduces
`fits.json`'s target exactly for 16 of the 17 wrap guns; Rocket_Launcher measures [25, 0, 5.1] at
its table F 25, while `fits.json` has [22, 0, 4.6] (the entry was set at F 22; not changed).
Ermac's GUN meshes (pistol/berreta.md3 ... incinerator/flamethrower.md3) are not on this machine
(only `hand/`, `ammo_hand/`, `heatwave/`), so `align.fit` / `fitall.py` cannot run here.

Note: `tools/kit/` holds older copies of align, ermac, fitall, gunview, hudrender, support (same code,
Windows paths); they are not changed by F12.
