# 3. The toolset

Every tool here was used to build BD22 VR Weapons Q 2.0 and 2.0.1. They were copied from the BD22 repo
(and the fitter core from the cloud folder it was developed in) on 2026-10-28, with every path made
Depot-relative or an environment variable. **Status** says what was re-run from a fresh clone of this repo
(see VERIFIED.md); "compiled" means the file compiles here but was not re-run after the move.

Most tools are written for BD22's classes and tables. They are the method in working form, and the place to
start for another set: the per-gun registries (`port_gun.GUNS`, `heavies/port_hv.GUNS_HV`, `scene.GUNS`,
`revlm.GUNS`) are where a new gun goes in.

## 3.1 Paths (`tools/depot.py`)

Every tool imports `tools/depot.py` and takes its paths from there. Nothing defaults to a folder outside the
repo except the three that cannot be committed.

| variable | what | default |
|---|---|---|
| `RSQ_SET` | the set being worked on | `sets/bd22q` |
| `RSQ_SRC` | the set's pack source | `$RSQ_SET/src` |
| `RSQ_POSES` | solved hand poses as data | `$RSQ_SET/handfit/poses` |
| `RSQ_FITS_DIR` | fit records, bakes, port records | `$RSQ_SET/handfit/fits` |
| `RSQ_HANDS_LANE` / `RSQ_HANDS_TOOL` | the fitter core: its data / its code | `tools/handfit/core` / `.../core/hands_tool` |
| `RSQ_GUNPACK` | BD22Q 1.92 extracted (the reference holds) | `tools/rig/build/src/bd22q_192/src` (made by `setup.sh`) |
| `RSQ_GAMEDATA` | `doom2.wad`, `brutal22test6.pk3`, `BD_VoxelPack.pk3` | `gamedata/` beside the Depot checkout |
| `RSQ_RIGLOCK` | the rig lock | `rig.lock` beside the Depot checkout |
| `RSQ_WORK` | run output: logs, frames, sheets, scratch packs | `work/` (gitignored) |
| `RSQ_FBX` | `hand_final.fbx`, the FBX hand | `tools/handfit/core/fbx_hand/hand_final.fbx` (in the repo) |
| `RSQ_FBX_TEX` | its textures folder | `<folder of RSQ_FBX>/textures` |
| `RSQ_ERMAC` | Ermac's `doom-force-unleashed_devbuild/models` | none: only measuring scripts read it |
| `RSQ_RL` | the whole Rusted Legacy dev build (`models/`, `modeldefs/`, `zscript/`), read by `sets/rusted_legacy/tools/rl_measure.py` | `sets/rusted_legacy/src` (his build, committed) |
| `RSQ_MODELSWAPPER` | an RS_ModelSwapper checkout (`core/hands_tool/scene.py` can read its meshes) | `rs_modelswapper/` beside the Depot |
| `B22_RIG`, `B22_PK3`, `B22_IWAD`, `B22_BD22`, `B22_VOX`, `B22_BUILD`, `B22_NOPROBE`, `QZ_RES`, `QZ_DUMP_EVERY`, `QZ_DUMP_DIR`, `QZ_SNDLOG` | the rig (chapter 2) | |

Python 3 with numpy, scipy and Pillow. Run tools from the Depot root unless the table says otherwise.

## 3.2 The rig (`tools/rig/`)
Chapter 2. **Status: setup, `rig.py`, `cmp2.py` and `mags.py` (through `gate_gun.py hands`) re-run on a fresh
clone.** `brk.py`, `pump.py`, `m203.py`, `grip.py` drive the other reload families; their constants were
written for the 1.99 placements and some are stale since the guns moved to the FBX hands (pump.py's port is
now at L 7.33 cm). The 2.0 tools take the live numbers instead: `tools/int20_rig/rsweep.py` and
`tools/handfit/shotguns/pump_sg.py` move them by the port record.

## 3.3 Hand fitting (`tools/handfit/`)

### The fitter core: `core/` (hands_tool + its measured data)
The FBX-skeleton hand fitter that every 2.0 hand was solved with. It reads the FBX in pure numpy
(`fbxbin.py`, `fbxhand.py`), poses it (`handmodel.py`: 18 pose parameters, limits from the FBX's own take),
places guns through the QZD chain (`hudrender.py`, `gunview.py`, `gunplace.py`, `scene.py`), checks the grip
rules (`rules.py`: G gun hand, S support, U open palm under, N gas-pump; every rule cites where its tolerance
came from), measures penetration exactly both ways (`exactpen.py`), solves (`solve.py`, `run_*.py`) and bakes
MD3 frames (`bake.py`, `bake3.py`). Its data, one folder up, are measurements, not settings: `calib.json`
(FBX hand to controller), `landmarks_fbx.json`, `landmarks_ermac*.json`, `regions.json`, `gun_landmarks.json`,
`rows192.json` (1.92's hand rows per gun), `metrics192.json` (22 guns the owner judged good: the
tolerances), `ref192_pistol.json`, `results/` (the round 1-7 fits, among them `round4_final.json`: the
approved pistol hand every other gun hand starts from). `core/README.md` and `core/REPORT.md` are the
fitter's own notes, including the rule list.
**Status: used by `rebake.py check` on a fresh clone (30 poses).**

### Shared modules: `fitter_lib/`, `heavies/`, `shotguns/`
`fitter_lib/` holds the batch 1-4 modules the others import: `m192.py` (where 1.92's hand sits on a gun),
`rigid3.py` (re-seat the approved hand rigidly onto a grip), `curl3.py` / `curl4.py` (close middle, ring,
pinky; solve the index onto the trigger and the squeeze), `revlm.py` / `fit3.py` (grip landmarks),
`gunmove.py`, `mdblocks.py` (parse every MODELDEF block). `heavies/` and `shotguns/` add their guns to the
port registry (`port_hv.py`, `port_sg.py`) and hold the per-family fitting (`fit_hv.py`, `fit_sg.py`),
pose export (`poses_hv.py`, `poses_sg.py`) and sheets. **Status: compiled; imported by the tools above.**
Gap: `fitter_lib` reads the old stage files of batches 1-4 (`st2_*.npy`, `curl3_*.json`) from
`RS_FITTER_HOME` (default `work/fitter_home`); the ones the BD22 port needs are in
`sets/bd22q/handfit/fits/`, the rest only on the fit farm's mirror.

### Measure and fit a gun hand
- `heavies/fit_hv.py`: one gun, the batch 3 method: 1.92's hold on that gun (`m192`) carried onto the
  approved FBX pistol hand, re-seated rigidly (`rigid3.stage2`: no penetration past 0.25 cm, palm and web on
  the grip, index pad to the trigger), fingers curled, squeeze solved, baked. A gun with no 1.92 hold starts
  from a similar gun's solved hold moved by the trigger-face difference.
- `heavies/surf_hv.py`: list a mesh's surfaces at its ready frame in F / L / U (to name grip, trigger, bore).
- `heavies/dense_hv.py`: re-fit a gun whose penetration is over 0.5 cm with every vertex tested.
- `farm/fit_batch.py`: the same fits, many at once, on a machine with more cores (3.4).
- `port/reseat_from.py`, `port/curl_gun.py`, `port/bake_gun.py`: the batch 4 steps one at a time.
- `port/sniper_pistol.py`, `sniper_wrist.py`, `sniper_fit.py`: the Ruger, which has a stock wrist, not a
  pistol grip (three tries; the owner chose pistol-style).
Good output: index pad 0 to 0.5 cm from the trigger face, middle / ring / pinky 0.2 cm, penetration at most
0.5 cm, palm and web on the grip; and a sheet that looks right from the eye.

### Port the gun to the hand: `port/port_gun.py`
```sh
python3 tools/handfit/port/port_gun.py <Class> <fit.json> [--src DIR] [--tag TEXT] [--dry]
```
The one method in one command. `fit.json` gives `shift` (cm, the gun's original frame) or `place` (the six
MODELDEF numbers). It writes the gun move to **every MODELDEF block that draws the gun on the gun controller**
(found by parsing all MODELDEF lumps; the count is asserted) and moves everything that hangs off the gun:
- `gunmoves.zs` Pivot and fire rows (found from `key[]`; the original placement must first reproduce the
  shipped rows, asserted);
- the reload rows: `rsr_guns.bd.zs` (magazine: Well, Axis, MagCentre, WellHook, Grab, Pull, HandleHook,
  Offset), `rsb_guns.zs` (break-open: Hinge, Axis, PushRef, Bores, Offset, and the off-hand round's block with
  its hold rows re-expressed so the hand's hold is unchanged), `rsr_pump_guns.zs` (via `port_sg.py`);
- the casing port, the muzzle row (`RSQ_Muzzle`, added at the drawn tip if missing), the scope rows
  (`RSQ_ScopeTable`), the Rifle's M203 tables (`RSM_Geo.ToGun/FromGun`, `FwdHook`);
- optionally the FBX gun hand (the md3, its MODELDEF hand blocks, `hands.zs` / `dualhands.zs` labels,
  `handtable.zs` rows; `support: "move"` moves the existing support pose with the gun).
It writes nothing unless every step passes, and records what it moved in `fits/ported_<Class>.json`.
`--dry` prints the plan. It was checked byte-for-byte against a hand-made move (`port/verify_mp40.sh`,
which needs the BD22 repo's history: `RSQ_BD22_REPO`).
Related: `port/reseat_gun.py` (move an already ported gun again, every table by the relative move),
`heavies/port_hv.py` and `shotguns/port_sg.py` (port_gun with their registries),
`port/flamecannon_r12.py` (a weapon worn on the arm: no gun hand), `port/melee_r12.py` (melee weapons, their
swing rows too), `int20_rig/butt_move.py` (butt-strike and pistol-whip points of guns already moved).
**Status: compiled. Its result is re-checked on a fresh clone by `rebake.py check` (`placement` lines).**

### The support hand
- `support192/fit192.py <Class>`: the FBX support hand fitted **from the 1.92 hold** (the seed is the FBX
  left hand fitted to 1.92's Ermac support frame on that gun, carried onto the moved gun), then closed onto
  the gun. `port192.py port <Class>` bakes it (`models/rsq/fbx/fbx_s192_L.md3`, one frame per gun, sprite
  `RQWS`) and writes the MODELDEF blocks, the `hands.zs` label and the `handtable.zs` row; `port192.py check`
  re-bakes every one from its pose data. `rigsheet.py` / `compose.py` / `view.py` make the sheets.
  `axe192.py`: the axe's second hand on the haft.
- `port/support_gun.py <Class> <A|B> <out.json>`: the earlier way: an existing FBX support pose (A pistol cup,
  B open palm under) placed at 1.92's SupportPoint and lowered in 1 mm steps until clear. `port/support_md3.py`
  wires a support hand that has its own baked md3.
Good output: palm and pads touching (0 to 0.5 cm), no penetration over 0.5 cm, the bar through the fist or
the fingers wrapping, **and the frame from the eye showing a hand that holds the gun** (chapter 6: the
open-palm trap).

### The off hand: fists, free hand, reload holds (`offhand/`)
`ohfit.py` fits the FBX hand in place of an Ermac frame and then round the object it holds;
`objects.py` parses what each reload hold holds, as the engine draws it; `hold_fit.py` fits every hold;
`wire_holds.py` writes the frames (`fbx_oh_hold_R.md3`, sprite `RQHF`) and the rows they need;
`free_oh.py` / `mk_free.py` make the free hand, the fist and the grenade-ring pinch; `ohbake.py check`
re-bakes them all from data. `rig_holds.py` and `rig_fists.py` show them on the rig. All off-hand frames are
the **right** rig baked in place: the engine mirrors them (chapter 1.5).

### Grenade and melee
`grenade/fit_nade.py`, `port_nade.py`: the FBX hand round BD22's grenade, the grenade moved to it, the throw
from the drawn grenade. `melee/fit_melee.py` (farm), `support_melee.py`, `poses_melee.py`, `sheet_melee.py`:
the axe, chainsaw and sword hands. `melee/melee.json` lists each weapon's mesh, frame and contact rules.

### Poses as data, and the rebake check: `port/rebake.py`
Every finished hand is stored as data in `$RSQ_POSES/<Class>.json`: the FBX joint vectors (trigger,
squeeze), the solved fingers, the wrist placement on the gun, the gun move, the support, the measurements.

```sh
python3 tools/handfit/port/rebake.py check
```

re-bakes every pose from its JSON and compares with the shipped MD3s, and regenerates every MODELDEF number,
pivot and fire row from the pose and compares with `src/`. Good output: `poses/sources: SHA256SUMS ok`, one
`== <Class>` block per pose (30 for BD22), `bytes identical` or `max 0.0156 md3 units` at most (one MD3
quantum), `"modeldef_mismatch": 0` everywhere. `rebake.py bake <pose.json> <out>` rebuilds one hand; with a new
hand mesh on the same skeleton, every gun re-bakes in one run. **Status: re-run on a fresh clone, PASS.**

## 3.4 The fit farm (`farm/`)
The cloud box has 2 cores; the owner's PC has 16. Fits run there: `pack_farm.py` packs the fitter and every
input into a zip (split into 28 MB parts), the parts go to the PC over the remote-device connection,
`unpack_farm.py` unpacks them (checking the sha256), `fit_batch.py --workers N --batch NAME [--detach] JOB...`
runs one process per gun (`Gun`, `=Gun` to reuse a saved seat, `Gun:from=<Src>:<seat.npy>`,
`Gun:idx`, `Gun:dense`, `Gun:wrap`), and results come back as `results/<Gun>/` (`st2_<Gun>.npy`,
`curl3_<Gun>.json`, `fbx_hv_<Gun>_R.md3`, `<Gun>_hv.json`). `farm.json` sets the mirror folder and worker
count; `farm_ps.py` lists the workers; `compare_fit.py` compares a farm fit with a cloud fit; `bench.py`
times the hot calls on both machines.
**Status: proven in the 2.0 work. Gap: `pack_farm.py` still packs the old cloud layout (the fitter folder,
the old run folders, a BD22 checkout at a git ref); it has to be pointed at `tools/handfit/core` and
`$RSQ_SET` before the next farm run.** The farm's own picks for BD22 are in
`sets/bd22q/handfit/fits/farm_*/PICKS_*.md`.

## 3.5 Reload tables (in the set's source)
Not tools but data the tools move: `src/zscript/rsr/rsr_guns.bd.zs` (`RSR_Guns`, magazine guns 1-18),
`rsb_guns.zs` (`RSB_Guns`, break-open and revolvers), `rsr_pump_guns.zs` (`RSP_Guns`), `rsr_m203_geo.zs`
(`RSM_Geo`, under-barrel launchers), `zscript/rsq/counters.zs` (real magazines on guns BD22 never reloads).
Every row is cm in the weapon controller's frame. Chapter 5 says what each row means.
**Gap:** the generators that first wrote these tables (`gen_rsr.py`, `gen_rsb.py`) are not in `tools/`
(`gen_rsr.py` is on the archive branch in `tools/kit/`, `gen_rsb.py` is in RS_ModelSwapper's `tools/kit/`).
For BD22 the rows are moved by `port_gun.py`; a new gun's first rows need the generator back, proven (PLAN F14).

## 3.6 The scope (`tools/scope3x/`)
`drive.py <name> <pk3> <Gun> <rhand pitch> <eye off L> <eye off U> <dump 0/1> [extra console] [res]` puts the
left eye 8 cm behind the eyepiece (from the set's `RSQ_ScopeTable`), with a test pack (`tpk/`) that draws two
identical magenta targets down range, and dumps frames. `conv.py` converts the dump to PNG and deletes the
`.ppm`; `blobs.py` measures the target in the lens against the one outside it (the magnification);
`tilt.py` the picture's tilt; `sheet.py`, `sheet_toggle.py` the sheets. Measured for 2.0: Sniper 3.07x across,
3.06x up; RailGun 3.2x / 3.0x. Run it through `int20_rig/f20wrap.py` to get the fresh default ini
(`f20all.sh` step `scope` shows how). **Status: compiled.** `port/scope_eye.py` re-checks a scope after its
gun moved.

## 3.7 Whole-pack checks (`tools/int20_rig/`)
Everything here runs through `run.sh`, which takes the rig lock and runs a **private copy** of the rig with
the fresh default ini (`ini.f20`), so saved cvars never hide a default and `tools/rig/bin` is never touched.
- `sweep_f20.py <pk3> <tag> <ballistics 0|1> [Gun,...]`: give, select, fire, alt fire per gun, one held frame
  each (PNG in `work/out/final20/`). A FAIL row with "alt: nothing seen" is the sweep's own limit on guns whose
  alt fire is not an attack (Rifle and Machinegun M203 with an empty tube, Shot_Gun, SSG, Sniper's scope
  toggle, GrenadeLauncher, NukeLauncher). **Status: re-run on a fresh clone for 3 guns.**
- `f20held.py`: one eye frame per weapon with the support hand on; `f20sheet.py` the contact sheet.
- `rsweep.py <pk3> [mag|pump|brk|all]`: every hand reload with the drivers, geometry from the live tables.
- `dualsweep.py`: dual wield the way a player gets it (own the gun, touch its pickup, Dual key).
- `rl3.py`, `mini20.py`: reloads with no backpack; the Minigun's own ammo pool.
- `butt.py`, `buttmark.py`: the butt strike, and where its hit point is against the drawn stock.
- `casecap.py`: casings in flight. `slugtest.py`: an option's default under an old and a fresh ini.
- `mdslots.py <pk3>`: no MODELDEF block names a slot past its size. **Status: re-run, 0 bad blocks.**
- `variants_all.py <pk3>`: every Purist block equals its Brutal block. **Status: re-run, 25 classes, 0 differ.**
- `purist_sync.py`, `purist_m203.py`: make the variant blocks equal (rule 5).
- `f20all.sh <pk3>`: all of the above in order (`STEPS="boot sweep held rsweep dual holds scope"`).

## 3.8 The set's own tools (`sets/bd22q/`)
`build.py [version]` builds the pk3 (LZMA for `.md3`; `tools/handtone_build.py` moves the FBX hand blocks to
slot 7). `tools/handtones.py` makes the skin-tone textures. `tools/hud/make_sbarinfo.py` the HUD.
`tools/moonammo/` the Moonlight's pickup. `reference/192_poses/` holds the 1.92 holds rendered from six
cameras per gun (`make_gallery.py` remakes them); `gate_gun.py compose` puts them beside new frames.

## 3.9 Not in this repo
- The mesh tools (name surfaces, carve a part out of a mesh, make a card of measured points: the old
  `tools/hqt`, `tools/kit/md3_carve_*.py`, `carve_by_ref.py`) and the reload table generators are on the
  branch `archive/depot-2026-10-28`. Bring a tool back only with a plan step and a proof run.
- The generators BD22 1.x used for `handtable.zs` and `gunmoves.zs` (`rsq_hands_gen.py`,
  `rsq_gunmoves_gen.py`) are not in any repo; the 2.0 tools edit those files row by row instead.
- The FBX hand, the game data and Ermac's models (3.1).
