# 4. One gun, end to end: the Rifle

The Rifle (BD22's M4 with the kit-bashed M203 under it) went through every step of the method, and it is
the hardest of the ordinary guns: about 26 MODELDEF blocks, a magazine reload, a charging handle, an
under-barrel launcher with its own reload, a support hand that holds the launcher tube, and a Purist variant.
Every number below is in the repo; the file is named with each one. Paths are relative to `sets/bd22q/`
unless they start with `tools/`.

The order is always the same:

```
mesh -> measure -> gun hand -> port (the gun moves) -> support hand -> reload rows -> reload hold
     -> rig proof -> sheet -> the owner's headset
```

## Step 1. The mesh

`src/models/bd/Rifle/Rifle.md3` (the rifle, animated) and `M203.md3` (the launcher, model slot 1), skins
`Rifle.png` / `M203.png`. BD22's DECORATE (`src/actors/Weapons/Rifle.dec`) decides which sprite frame shows
when; `MODELDEF.bd.txt` binds each sprite frame to a mesh frame. The ready pose is the frame the Ready sprite
binds: `FrameIndex RIFG A 0 3`, so **mesh frame 3**, not 0. Measure everything at that frame.

Surfaces that matter, named by the modeller and found by listing them at frame 3
(`tools/handfit/heavies/surf_hv.py`; `tools/handfit/fitter_lib/fit3.py` records them): the trigger is
surface 2 `trigger`, the grip is inside surface 4 `Runko`. The magazine is its own surface, which is what
lets the reload draw it in the well, in the hand and on the floor.

Before the 2.0 hands the Rifle was drawn the 1.92 way: `Scale -1 1 1`, `Offset 0 0`, `ZOffset -5`.

## Step 2. Measure the 1.92 hold

The owner judged the 1.92 hands good, so the 2.0 hand starts from where 1.92's hand sat on this gun
(rule 2). `tools/handfit/core/rows192.json` records 1.92's row for the Rifle: gun hand = Ermac `hand.md3`
frame 38 (`TO`), hook (0.76, -4.96, 2.73); support = `hand2.md3` frame 2 under the M203 tube, hook
(0.954, -12.744, -17.4), turned 10 degrees. Rendered from six cameras in `reference/192_poses/Rifle_*.jpg`.

`tools/handfit/fitter_lib/m192.py` measures that hold on the mesh in F / L / U: web, palm, cuff (forearm stub),
the four knuckles, the index pad. Then the rigid fit T of 1.92's pistol hand onto 1.92's hand on this gun:
for the Rifle, 10.6 degrees off the pistol hand, residual 0.1-1.0 cm (batch 3's measurement, recorded in
the BD22 repo's handoff).

## Step 3. The gun hand

The approved FBX pistol hand (the owner passed it in his headset, 2026-10-27; `core/results/round4_final.json`,
`BrutalPistol`) is moved by T, then:
1. `rigid3.stage2` re-seats it rigidly on the Rifle's grip: no penetration past 0.25 cm, palm and web onto the
   grip, index pad to the trigger, the turn kept near 1.92's.
2. `curl3` closes middle, ring and pinky to 0.2 cm and solves the squeeze: the index pad moves 0.6 cm back
   along the bore.

Result (`handfit/poses/Rifle.json`, `fit`): before the curls palm 0.28, web 0.04, index pad 0.28 cm from the
trigger face, penetration 0.26; after, middle / ring / pinky 0.20, thumb 0.51; squeeze: index pad 0.76 cm from
the face. The hand is turned 8.9 degrees on the wrist against the pistol hand, the way 1.92's is. The fit is
a **shift of the gun** (-2.40, 0.57, -0.38) cm, not a move of the hand: the drawn wrist stays where the
approved pistol hand's wrist is (rule 1). The solve lives in `handfit/fits/curl3_Rifle.json` and
`st2_Rifle.npy`; the baked frames in `handfit/fits/bake/fbx_b4_Rifle_R.md3` and the shipped copy
`src/models/rsq/fbx/fbx_b4_Rifle_R.md3` (frame 0 trigger, 1 squeeze, 2 the pistol re-bake check).

In 2.0 this step ran as `tools/handfit/heavies/fit_hv.py` (one gun) or on the fit farm (`farm/fit_batch.py`)
for most guns; for the Rifle it ran as batch 3's scripts, now `tools/handfit/fitter_lib/` +
`tools/handfit/port/curl_gun.py` + `bake_gun.py`.

## Step 4. Port: the gun moves to the hand

```sh
python3 tools/handfit/port/port_gun.py Rifle sets/bd22q/handfit/fits/Rifle.json --tag "batch 4"
```

`fits/Rifle.json` holds the shift and the hand wiring: md3 `fbx_b4_Rifle_R.md3`, sprite `RQFJ` (A trigger,
B squeeze), the squeeze shown on the fire frames `RIFF / RI2F / 2IFF A-D` and their no-tube twins
`QT08 / QT09 / QT0A` (taken from the gunmoves fire rows). The six MODELDEF numbers come out of the QZD chain
with residual 0.0000 cm:

```
Offset 0.348 -5.912 0.0
ZOffset -1.812
AngleOffset 3.854
PitchOffset 3.363
RollOffset 10.974
```

The angles are the approved pistol's aim, the same on every pistol-gripped gun: the gun keeps that aim and
moves to the hand. `fits/ported_Rifle.json` lists what moved: MODELDEF.bd.txt Rifle x1, MODELDEF.rsr Rifle
x3 and RSR_GunParts x3, MODELDEF.rsm Rifle x5 and RSR_GunParts x2 (the M203 parts), MODELDEF.rsqoff
RSQ_Off_Rifle x9 (dual wield), MODELDEF.purist PuristRifle x3; gunmoves pivot row 18 and fire rows 93-95; the
casing port to (15.7, 1.2, 8.0) (`zscript/rsq/casings.zs`, was (10.0, -0.6, 2.6)); a muzzle row added at the
drawn tip (71.18, 6.06, 11.42) (`zscript/rsq/muzzle.zs`); and the reload rows (step 6). The M203's own tables
stay in the rifle's original frame: `RSM_Geo.ToGun / DirToGun / FromGun` carry points across, and its forward
hook is the moved axis.

Later, two more things had to move with the gun, found by looking, not by numbers: the butt-strike hit point
(`tools/int20_rig/butt_move.py`, from the pose's `gun_move`) and the Purist rifle's M203 block
(`tools/int20_rig/purist_m203.py`). Moving the gun means moving everything on it (rule 1); keep that list.

## Step 5. The support hand

The current Rifle support is the support192 fit (`handfit/poses/Rifle.json`, `support`):
`tools/handfit/support192/fit192.py Rifle` started from 1.92's Ermac support frame 2 under the tube (the FBX
left hand fitted to that frame: landmark rms 2.31 cm), carried onto the moved gun, then closed onto the
gun. Measured: penetration into the gun 0.18 cm, into the gun hand 0; palm 0.23 cm, index pad 0.13, the
other pads 0.0 to 0.11; the fingers wrap 255 degrees round the tube. `port192.py port Rifle` baked it as
frame 3 (letter D) of `src/models/rsq/fbx/fbx_s192_L.md3`, sprite `RQWS`, label `FbxWrapRifle` in `hands.zs`,
and the handtable row 18 support hook and rotation to 0 (baked in place). PuristRifle takes the same hand.

Before it, batch 5 had put the FBX open palm under the tube (`support_gun.py Rifle B`, palm 0.14 cm, pen 0.45):
the numbers were fine and the owner rejected it on sight. Chapter 6, "the open palm".

## Step 6. Reload rows

The Rifle is magazine gun 1 in `src/zscript/rsr/rsr_guns.bd.zs`. After the port (each line says "batch 4:
moved with the gun", with the old value):

| row | value | meaning |
|---|---|---|
| `Well(1)` | (17.669, 2.668, 6.708) | the magazine's top, seated |
| `Axis(1)` | (-0.023, -0.192, 0.981) | the way a magazine goes in |
| `Mouth(1)` | 8.80 | seated -> the well's mouth, cm along the axis |
| `MagLen(1)` | 20.59 | |
| `MagCentre(1)` | (17.654, 4.007, -0.088) | the magazine's centre, seated |
| `Grab(1)`, `Pull(1)`, `Travel(1)` | (-1.001, 1.551, 9.616), (-0.996, -0.068, -0.059), 7.30 | the charging handle, its pull direction and stroke |
| `Reserve(1)` | `"Clip2"` | where a new magazine's rounds come from |

All cm in the weapon controller's frame. Never edit them by hand after a move: `port_gun.py` moves them
with the gun, and `rebake.py place` regenerates them from the pose to prove it.

## Step 7. The reload hold

The magazine in the off hand is drawn by `RSQ_Hands` on layer 2201 (`RSR.HANDMAG`). Since 2.0 the hand round it
is FBX: `tools/handfit/offhand/hold_fit.py` fitted the FBX right hand (mirrored by the engine onto the left
controller) in place of Ermac's magazine hold and closed it round the Rifle's magazine as the pack draws it
(`objects.py` parses the MODELDEF and rows); `wire_holds.py` baked it as frame A of
`src/models/rsq/fbx/fbx_oh_hold_R.md3` (sprite `RQHF`; magazine guns 1-18 are A-R). The M203 round has its
own hold (frame Y).

## Step 8. Rig proof

All on a fresh clone (VERIFIED.md has the actual run). Build and boot first:

```sh
sh tools/rig/setup.sh                      # builds sets/bd22q into tools/rig/build/BD22Q_now.pk3
cd tools/rig
RSQ_GAMEDATA=/path/to/gamedata flock -o -x /home/claude/rig.lock python3 rig.py boot 'wait 100; quit' 150
grep -hE "Script error|VM execution aborted" build/logs/boot.log | sort | uniq -c   # only BD_VoxelPack's four
cd ../..
```

The poses rebuild from data, and every placement number regenerates:

```sh
RSQ_FBX=/path/to/hand_final.fbx python3 tools/handfit/port/rebake.py check
#  == Rifle ... vs shipped src/models/rsq/fbx/fbx_b4_Rifle_R.md3: bytes identical ...
#  placement: {"cls": "Rifle", ... "modeldef_match": 27, "modeldef_mismatch": 0, ... "fire_rows_max_diff": 0.0}
```

The magazine reload, driven by the off hand (`gate_gun.py` boots the pack so `mags.py` can read the live
table, then runs `mags.py 1`; it takes the rig lock itself):

```sh
export RSQ_GAMEDATA=/path/to/gamedata RSQ_RIGLOCK=/home/claude/rig.lock
python3 tools/handfit/port/gate_gun.py hands tools/rig/build/BD22Q_now.pk3 1
#  1 Rifle  IDLE>EMPTY>DROP>EMPTY>CARRY>INSERT>SEATED>DONE>IDLE ...
```

The M203 on the moved gun: `gate_gun.py hands <pk3> m203` (latch, open, round into the breech, round home,
"shut: loaded"; shown in batch 4 and in the 2.0 final). A whole-pack sweep: `tools/int20_rig/f20all.sh <pk3>`.

## Step 9. The sheet

```sh
python3 tools/handfit/port/gate_gun.py sheet tools/rig/build/BD22Q_now.pk3 Rifle
python3 tools/handfit/port/gate_gun.py compose work/gate/rifle_sheet.png Rifle
```

Six engine runs (rest, steadied, firing; from the eye and from the side), one frame kept from each as PNG
(the `.ppm` dumps are deleted), then the sheet with 1.92's renders in the first column. **Look at it**
(rule 4): the side views must show the gun hand round the grip with the index on the trigger, the support hand
round the M203 tube when steadied, and the gun not tilted off the aim. The eye camera of `gate_gun.py` sits
behind and above the gun hand and sees mostly the stock: judge the hold from the side view and from
`cmp2.py`'s view (chapter 2.6).

## Step 10. The owner's headset

Only now does anything go to the owner: a pk3 built by the set's own `build.py`, booted on his load order
with zero pack script errors, with the sheet and the list of what is rig-only. Everything above is "rig only,
not headset-confirmed" until he has played it.
