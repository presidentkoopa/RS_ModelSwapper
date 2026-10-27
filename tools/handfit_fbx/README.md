# tools/handfit_fbx -- the FBX hand fitter (PLAN F13, pipeline 2: hands on the gun, finger on the trigger)

Fits a skinned, rigged hand (hand_final.fbx, 22 joints, 1667 vertices per hand) onto a gun mesh for QuestZDoom 17.3 VR:
it solves the wrist, the gun's move and every finger joint against grip rules, and bakes the result as MD3 frames
(`trigger`, `squeeze`, support) plus the MODELDEF / gunmoves / hands rows that draw them. Prototyped outside this repo
(/home/claude/lane_c, rounds 1-6, 2026-10-26/27); the owner provisionally passed BrutalPistol and Flamethrower2 in his
headset (2026-10-27). **Sets are built in their own repos with this tool (BD22 in RS_Brutal22WeaponsQ); the Depot holds
only the tool** and, as its regression test, the round-6 fit records in `reference/bd22_r6/`.

It reads the FBX hand, NOT the DXR IQM hands (owner's rule). Ermac's hand.md3 is the calibration reference only.

## Inputs (paths.py) -- nothing outside the Depot is assumed

| variable | what | default |
|---|---|---|
| `HANDFIT_FBX` | `hand_final.fbx` (DXR `models/hands/hand_final.fbx`). **Required; never committed** (`.gitignore` has `*.fbx`). | none: a clear error |
| `HANDFIT_FBX_TEX` | its textures folder (`lambert1_Base_Color.png`, read by the pack builders) | `<folder of the fbx>/textures` |
| `RSQ_GUNPACK` | an extracted pack with `MODELDEF.bd.txt` + `models/` (the guns, the 1.92 hands) | `tools/rig/build/src/bd22q_192/src` = tag 1.92 of RS_Brutal22WeaponsQ, made by `sh tools/rig/setup.sh` (as tools/questhands) |
| `RSQ_ERMAC` | Ermac's `doom-force-unleashed_devbuild/models/` (`hand/hand.md3`, `hand2.md3`). Only the measuring scripts (calib, regions, ermaclm build, measure192, offwrist) read it. | none: a clear error when a script needs it |
| `HANDFIT_WORK` | where runs write: `results/`, `cache/` (distance fields, ~2 min each to build), `out/` (MD3, pk3), `sheets/`, `rigout/` | `tools/handfit_fbx/work` (gitignored) |
| `B22_RIG` `B22_IWAD` `B22_BD22` `B22_VOX` | engine checks only: the rig and the owner's load order doom2 -> brutal22test6 -> BD_VoxelPack -> pack | `B22_RIG` = `tools/rig/bin`; the game data have no default |

`data/` (committed) holds the measured inputs every fit reads; the script that measured each writes it back there:
`calib.json` (FBX hand -> controller, scale + open/fist fits against Ermac's hand), `landmarks_fbx.json` (web, palm,
pads, cuff on the FBX mesh), `regions.json`, `landmarks_ermac.json`, `landmarks_ermac_frames.json`, `gun_landmarks.json`
(per gun: grip axis, backstrap, trigger face, bore, handle bars ... from the meshes), `fbx_limits.json` (what the FBX's
own 1279-frame take reaches per joint = the pose bounds), `rows192.json`, `metrics192.json`, `ref192_pistol.json`,
`offwrist192.json`, `forearm192.json` (1.92's 22 guns measured: the rule tolerances), `poses_auto.json`.

Python 3 with numpy, scipy, Pillow. Run every script from this folder.

## Fitting a gun

1. Measure (once per hand / per gun; results land in `data/`):
   ```
   python3 calib.py data/calib.json            # FBX hand -> controller (Ermac's free hand), scale + grip pose
   python3 landmarks.py data/landmarks_fbx.json
   python3 regions.py && python3 ermaclm.py    # landmark regions, and the same regions on Ermac's topology
   python3 ermac_lm.py data/rows192.json data/landmarks_fbx.json data/calib.json data/landmarks_ermac_frames.json
   python3 gunlm.py data/gun_landmarks.json    # gun landmarks from the meshes
   python3 measure192.py data/rows192.json x data/metrics192.json   # 1.92's guns -> the tolerances
   ```
   A new gun needs its entry in `scene.GUNS` (mesh path, ready frame, scale, offset: parsed from the pack's
   MODELDEF.bd.txt) and in `gunlm.py`.
2. Solve the gun hand. Mode C = the displayed wrist cuff pinned to the controller grip, the gun moves (that move is
   later written as MODELDEF Offset / ZOffset / Angle / Pitch / RollOffset, exact): `run_gun.py <Gun>` (modes A/B, the
   seeds), then `run_wrist.py <Gun> <cant cap> <key> <rotmax> <pen>` with `LANEC_W` (weights), `LANEC_ANCHOR`,
   `LANEC_SEED` (earlier keys as starts). A gas-pump / nozzle grip: `run_pump.py <key> '<json overrides>'`.
3. Solve the support hand: `run_support3.py <Gun[@variant]> <cup|vgrip> <gunkey> <outkey> <pen> '<weights>'`
   (`LANEC_SSEED`, `LANEC_CONTACT`, `LANEC_PENOTHER`); an open palm under a tank: `run_under.py <key> '<json>'`.
4. Assemble: contact projection (depen / depen2: the skin pulled off the gun's surface and edges, both ways), the
   squeeze pose (fingers follow the trigger / lever between the ready and fire frames of the gun mesh), the rules,
   the gun's MODELDEF placement: `final3.py`, `final4.py`, `squeeze.py`, `modeldef3.py`, `final6.py` (round-6 form;
   `reproduce_bd22_r6.sh` is the worked order).
5. Bake: `LANEC_FINAL=<final json> LANEC_SQUEEZE=1 LANEC_SQFILE=<squeeze json> LANEC_MD3=<name> python3 bake3.py`
   -> `out/<name>_R.md3` (gun hand: trigger frames, then squeeze frames) and `<name>_L.md3` (support), each frame baked
   where it is drawn (hand-table hook / rot 0).
6. Test pack (TEST only, never ships): `headsetpack.py <out.pk3>` with `LANEC_MD3`, `LANEC_FINAL`, `LANEC_GM` (the gun
   MODELDEF json), `LANEC_SQUEEZE`, `LANEC_FLAMESPOUT`, `LANEC_MANI`: a copy of `RSQ_GUNPACK` with only the fitted guns
   changed; every edit is listed in `out/<manifest>.json` (file, what, before, after).
7. Engine check, one engine at a time:
   `flock -o -s /home/claude/rig.lock python3 gate3.py <pk3> <tag> <Gun> [row]` (give, rest, two-hand support, fire,
   alt-fire, VR reload; frame dumps; logs grepped for script errors) and `engine_sheet.py` for the side / eye /
   close-up sheet. The owner's headset pass is the test; this is only the parse-and-play check.

## The rules (traffic lights; every rule carries its source string)
Thresholds are learned from 1.92 (`metrics192.json`, 22 guns the owner judged good) where 1.92 can be measured, else
from 1.92's BrutalPistol (his reference hold), else a stated definition.
- **G (gun hand on a pistol grip):** G1 no penetration; G2 web on the backstrap top; G3 palm on the back of the grip;
  G4 grip axis diagonal across the palm vs 1.92's pistol; G5 middle/ring/little wrap the front strap; G6 thumb on the far
  side; G7 index pad on the trigger face; **G8 VR: the displayed wrist vs the real hand (controller grip), deg / cm**;
  G9 forearm in line behind the gun.
- **N (gas-pump grip, round 6):** N1 no penetration both ways (exact: hand into gun AND gun/lever into hand); N2 handle in
  the palm, palm sideways (handshake), as the owner holds the controller; N3 thumb over the top/side; N4 index on the
  lever; N5 middle/ring on the lever underside; plus G8. Owner's override (2026-10-27): the nozzle is never tilted to
  improve the grip ("I would sooner accept a less than perfect grip than i will accept a tilted mesh").
- **S (support, two-hand):** S1 no penetration (gun and gun hand); S2 pads touch; S3 palm touches; S4 the bar runs
  through the fist (vgrip) / thumb on the gun (cup); S5 knuckle line along the bar / fingers wrap; **S6 the support wrist
  vs the OFF controller** (the engine re-aims a steadied gun at the off hand: VrInputDefault.cpp).
- **U (open palm under a tank):** U1 no penetration; U2 palm on the underside; U3 palm normal into the tank; U4 fingers
  follow the curve; U5 wrap; U6 forearm under/behind the tank; plus S6.
- Penetration is checked exactly (winding number + point-to-triangle) in both directions, not on grid fields alone:
  hand-vertex-only checks miss thin gun parts (the pistol's trigger blade).

## Outputs
`out/*.md3` (the baked frames), `results/*_final.json` (per gun: pose vectors, vertices, every rule with its light and
source, penetration, projection report, wrist and gun-move numbers), `results/gun_modeldef_*.json`, `results/squeeze_*.json`,
`sheets/*.png`, the test pk3 and its edit manifest, `rigout/` (engine logs, frame dumps, gate json).

## Regression: the round-6 BD22 frames
`sh reproduce_bd22_r6.sh` copies the recorded fit records (`reference/bd22_r6/fits/`: the solved pose vectors and the
seeds the last solves started from) into `work/results`, assembles, bakes, and `check_ref.py` compares the MD3s with
`reference/bd22_r6/expected_md3.json` (the frames in `BD22Q_192_fbx_headset_r6.pk3`, sha256 per file and per frame).
`--resolve` first re-solves the last link of each pose (pistol gun hand K5, pistol support R3c, flamer support D,
flamer gas-pump Z3) from its recorded seeds, then the same.
Frames: `fbx_r6_R.md3` 0 pistol trigger, 1 flamer trigger, 2 pistol squeeze, 3 flamer squeeze; `fbx_r6_L.md3` 0 pistol
support, 1 flamer support. (In the pack they are `models/rsq/fbx/fbx_r3_R.md3` / `_L.md3`.)

## Provenance of hand_final.fbx (the owner, 2026-10-27)
- Downloaded months ago by the owner from a free model site (CGTrader or similar); the page cannot be found now.
- Maya 2019, saved 2020-06-24 (FBX 7.5). Artist's path inside the file:
  `D:\onedrive\working_on\projects\hand\animation\done\hand_final.fbx`, from `animation_4.mb`.
- Substance textures: `lambert1_Base_Color.png`, `lambert1_Normal_OpenGL.png`, `lambert1_Roughness.png`.
- No author or licence field in the file.
- The raw .fbx is never committed or shipped. Only baked MD3 frames ship, inside the owner's packs.
- **Open:** confirm the licence if the page is found.

## Open (recorded in PLAN F13)
- Licences for the FBX source (above).
- Per-set frame letters (the prototype's sprites RQFG / RQFS are its own picks).
- The pistol trigger through the finger on BD22's fire frames: 0.66 cm (owner: minor); BD22's trigger swings forward
  on fire, so there is no pull to follow.
- Script and env names keep the prototype's (`LANEC_*`, `final3/4/6`, `fbx_r3_*` in the pack) so the round-6 frames
  reproduce byte for byte.

## Rule: start from the existing poses (owner, 2026-10-27)
Every gun starts from an existing named pose:
- pistol grip / trigger / squeeze;
- foregrip / vgrip;
- pump / wrap;
- under / cup.

A new grip is solved from scratch only when none of these fits.
- **The Flamethrower lesson:** its gas-pump grip IS the pump-shotgun support grip, palm sideways round a bar along the bore. In VR a pistol-held controller under a drawn pump-wrap is normal, so the wrist pin is relaxed for that pose the same way support hands relax it. Ignoring this cost over an hour (rounds 6-7). The Flamethrower is parked at r5 (lane notes: FLAMETHROWER_PARKED.md).
- **Time box:** each batch has a fixed time box, and the owner gets the sheet when it ends.
