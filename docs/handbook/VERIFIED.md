# VERIFIED: the handbook followed on a fresh clone

**Date:** 2026-10-28. **Commit cloned:** `dc3bb6f` (main, pushed; the handbook as written, chapters 02 and 04).
**Where:** a fresh `git clone https://github.com/presidentkoopa/RSQ_WeaponDepot.git` into an empty scratch
folder, no other checkout of the Depot used. Game data from `/home/claude/gamedata` (`RSQ_GAMEDATA`), the FBX
hand from `/home/claude/dxr/models/hands/hand_final.fbx` (`RSQ_FBX`), every engine run under
`flock -o -x /home/claude/rig.lock` (`RSQ_RIGLOCK`), one engine at a time, load average under 0.4 at the start.
Machine: the 2-core / 8 GB cloud box. The whole sequence took 5 min 40 s. Everything here is
**rig only, not headset-confirmed.**

| # | step (handbook) | command | result |
|---|---|---|---|
| 1 | clone (02 §2.2) | `git clone https://github.com/presidentkoopa/RSQ_WeaponDepot.git rsq_weapondepot` | **PASS** head dc3bb6f |
| 2 | hooks (02 §2.2) | `sh tools/install_hooks.sh` | **PASS** "hooks installed" |
| 3 | rig setup (02 §2.2) | `sh tools/rig/setup.sh` | **PASS** rc 0, 56 s: `rig ready: ... QuestZDoom qzd17.3 (9afc750917bf54870f2d16b7ba0d00f2b77e6fb5), engine 4.14.3, ZScript 4.14.2`. Built `sets/bd22q` with its own `build.py` into `build/BD22Q_now.pk3` (786 lumps); fetched tag 1.92. |
| 4 | boot BD22 2.0.1 on the owner's load order (02 §2.4) | `cd tools/rig; flock -o -x /home/claude/rig.lock python3 rig.py boot 'wait 100; quit' 150` | **PASS** rc 0, 10 s. `qz: engine OK`; `adding .../BD22Q_now.pk3, 786 lumps`; `script parsing took 1354.58 ms`; `MAP01 - Entryway`. **Script errors: only BD_VoxelPack's four** (`voxeldef.txt` lines 66, 72, 77, 892), **0 from the pack**, 0 VM aborts. Probe: 18 `B22 GUN` lines (the 18 magazine guns' live tables). `FEATURES SAVED OFF: none`. |
| 5 | frames, A vs B (02 §2.6) | `flock -o -x /home/claude/rig.lock python3 cmp2.py build/BD22Q_192.pk3 build/BD22Q_now.pk3 BrutalPistol,Rifle hb` | **PASS** rc 0, 55 s, `build/shots/cmp2_hb.png`; 0 `.ppm` left. Looked at: 1.92's Ermac glove on the left, the 2.0.1 FBX hand on the grip with the index on the trigger on the right, both guns. [verified/cmp2_pistol_rifle.jpg](verified/cmp2_pistol_rifle.jpg) |
| 6 | restore the ini (02 §2.10) | `git checkout tools/rig/bin/config/qzdoom.ini` | **PASS** the engine had modified it (as documented); clean after the checkout |
| 7 | poses rebuilt from data (03 §3.3, 04 step 8) | `RSQ_FBX=... python3 tools/handfit/port/rebake.py check` | **PASS** rc 0, 18 s. `poses/sources: SHA256SUMS ok`; 30 poses; every hand MD3 reproduced: 31 comparisons byte-identical, 6 differ by at most 0.0156 md3 units (0.0159 cm, one MD3 quantum: Chain_saw, Devastator 0.0000; IncendiaryLauncher, Rocket_Launcher 0.0156), as recorded when they shipped; `"modeldef_mismatch": 0` on all 30; fire rows max diff 0.0 on 26 guns and 0.01 on BrutalPistol. Rifle: `bytes identical` vs the committed bake and the shipped md3. |
| 8 | one gun's frames (04 step 9) | `python3 tools/handfit/port/gate_gun.py sheet tools/rig/build/BD22Q_now.pk3 Rifle`, then `... compose work/gate/rifle_sheet.png Rifle` | **PASS** rc 0, 95 s; 6 runs (rest / steadied / firing x eye / side), 84-108 frames each, `errors: []` in all six; sheet made; 0 `.ppm` left. Looked at: side views show the FBX gun hand round the grip with the index on the trigger, the support hand wrapped round the M203 tube when steadied, brass and flash on fire. The eye camera sees mostly the stock (noted in 04 step 9). [verified/rifle_sheet.jpg](verified/rifle_sheet.jpg) |
| 9 | the Rifle's hand reload (04 step 8) | `python3 tools/handfit/port/gate_gun.py hands tools/rig/build/BD22Q_now.pk3 1` | **PASS** rc 0, 25 s: `1 Rifle IDLE>EMPTY>DROP>EMPTY>CARRY>INSERT>SEATED>DONE>IDLE`. The one error line the driver lists is BD22's own `Unknown class name 'DeathSphereHealth'` warning. |
| 10 | a sweep (03 §3.7) | `python3 tools/int20_rig/sweep_f20.py <pk3> hb 0 Rifle,Shot_Gun,BrutalPistol` | **PASS (as designed)** rc 0, 66 s, through `run.sh` (private rig copy, fresh default ini). All three selected and fired (ammo down, projectiles and tracer dots counted). BrutalPistol PASS; Rifle and Shot_Gun rows read FAIL on "alt: nothing seen" only, the sweep's documented limit: it counts only ammo, projectiles and tokens, and these two alt fires produce none of those here (the Rifle's is the M203 with an empty tube, a dry click). The 2.0 final lists the same two rows the same way. Frames: hands on all three. [verified/sweep_3guns.jpg](verified/sweep_3guns.jpg) |
| 11 | MODELDEF slots (01 §1.3) | `python3 tools/int20_rig/mdslots.py tools/rig/build/BD22Q_now.pk3` | **PASS** `blocks with a slot past their size: 0` |
| 12 | variants copy rows (rule 5) | `python3 tools/int20_rig/variants_all.py tools/rig/build/BD22Q_now.pk3` | **PASS** 25 Purist classes, 193 blocks equal, 0 differ |
| 13 | still meshes (`tools/check_plan.py --audit`) | | 40 meshes would be refused if added today, **all in `sets/vanilla`, `sets/vanilla_plus`, `sets/modern`** (REMA `_wm` stills, documented: those sets are rebuilt, never patched). 0 in `sets/bd22q`. |
| 14 | the clone afterwards | `git status --short`; `find . -name '*.ppm'` | **PASS** clean tree, 0 `.ppm`; run output 30 MB in `work/`, the rig build 202 MB in `tools/rig/build/` (both gitignored) |

## Fixed in the handbook and the tools while following it
Found by following the steps on earlier fresh clones the same day (`4c7339f`, `c01efd3`), fixed, pushed, then the
whole run above repeated on `dc3bb6f`:
- `setup.sh` zipped `sets/bd22q_1.97/src`, which the new layout removed: it now builds `$RSQ_SET` (default
  `sets/bd22q`) with the set's own `build.py` (a plain zip of `src/` is not BD22's pack: no LZMA, no slot-7 hands).
- `gate_gun.py` defaulted the game data, the rig lock and the Depot to `<BD22 repo>/..`: now `tools/depot.py`.
  Its `compose` read the 1.92 renders from the removed `docs/reference`: they are back as
  `sets/bd22q/reference/192_poses` (they are the method's starting point, rule 2). A path edit there had commented
  out a variable on the same line (NameError on the first compose); fixed.
- `rebake.py` looked for the committed bakes beside the tool: they live with the set's fit records now.
- `cmp2.py` left its `.ppm` dumps behind: it deletes them once the frame is used.
- The rig README said `flock -o -s` (shared, which does not serialise engines): now `-x` everywhere.

## Not verified here
- **Nothing in a headset.** The owner's headset pass is the test.
- The fit itself (solving a new hand: `fit_hv.py`, the farm, `fit192.py`, `hold_fit.py`): compiled, imports
  resolved, not re-run (each fit takes minutes to an hour; the PC farm is not reachable from this run).
  `pack_farm.py` still packs the old cloud layout (03 §3.4).
- `port_gun.py` was not re-run as a write (it would move a gun that is already moved); its output is re-derived
  and compared by `rebake.py check` (step 7, `placement` lines).
- The scope driver (`tools/scope3x/drive.py`), `rsweep.py`, `dualsweep.py`, `f20all.sh`: compiled, paths moved,
  not re-run on this clone. Their last results are in the BD22 repo's handoff (2.0 final).
- `setup.sh build` (building the engine from source): not re-run; the prebuilt `bin/` passed the version guard.
