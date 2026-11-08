# 6. Traps and fixes

Every one of these happened on BD22 and cost at least a session. Most of them end in a run that looks
green. Assume you have one until you have shown you do not.

## Saved settings and defaults

| trap | what it looks like | fix |
|---|---|---|
| **A saved cvar hides a new default.** Cvars are archived in the ini. Changing a default in CVARINFO does nothing for anyone who ran an older build (the owner's `rsq_hands=false` hid the hands; an old `rsq_scope_sniper 0` kept "Dot"; an old `rsa_rev_magnum=false` kept the slug off). | The feature "does not work" for the owner and works for you. | **Rename the cvar** when you change its default (`rsq_scope2_*`, `rsa_rev_slug`). `rig.py` prints `FEATURES SAVED OFF` before and after every run; `rig.py --cvars <pk3> <ini>` checks the owner's ini. Test defaults on the fresh ini (`tools/int20_rig/ini.f20`). |
| A cvar changed in the menu reaches only `user` cvars per player; a `clearscope static` table cannot read a user cvar | an option that does nothing | make it `server` when a static has to read it (`rsb_revolver_feed`) |
| The engine rewrites `tools/rig/bin/config/qzdoom.ini` on exit | a dirty tree, a stray commit | `git checkout tools/rig/bin/config/qzdoom.ini`, or run on a private copy (`tools/int20_rig/run.sh`) |
| `playerclass` not set in the ini | a random class each run; Purist (no reloading) turns the Brutal guns into Purist ones | `playerclass=$TAGBD_CLASS_RIFLE` |

## MODELDEF and models

| trap | what it looks like | fix |
|---|---|---|
| **`ZOffset` overwrites `Offset`'s z** (whichever line is last, `models.cpp:853-866`) | a tool's numbers 5 cm off; "the gun jumps 5 cm when the reload starts" (reload blocks with ZOffset 0, ready blocks -5) | always read both; every block that draws the same gun must carry the same placement |
| **A block is sized by its LAST `Model` line** (min 4) | `Too many models in RSQ_Hands`, a script error on the owner's load order | put the highest slot last; `tools/int20_rig/mdslots.py <pk3>` |
| **A whole-model `Skin` beats every `SurfaceSkin` and `A_ChangeModel`'s surface swap** (`models_md3.cpp:357-369`) | the scope glass shows the whole texture atlas; the camera picture never lands | per-surface skins on any gun with a part that changes skin |
| A fire frame with no `FrameIndex` | the gun draws as a 2D sprite for a few tics a shot (BD22's Ruger) | key every sprite frame the gun can show |
| A sprite name is known to the engine only if some actor's states use it | `Unknown sprite RQXM in model definition` | list new sprite names in a states block (`RSR_GunSprites`) |
| Measuring at mesh frame 0 | points in a stowed pose (the pistol's read U -28..-10) | measure at the frame the Ready sprite binds |
| An order-based (Kabsch) fit of two meshes that hold the same points in a different order | a plausible residual (11.26, 24.26) and the wrong answer, no error | compare per-surface vertex counts first; fit by position (ICP), or only the surfaces that match one for one |
| REMA's `*_wm.md3` meshes are single-frame stills | the gun goes stiff in the hand | never ship a `_wm`; the hook refuses an added one-frame set mesh unless `single_frame_ok.txt` lists it |
| Looking for an ejection port only on the side walls | "no port" on belt-fed guns (MG42 and M249 eject DOWN) | search all directions; a port is a boundary loop of the welded ready frame |

## Hands

| trap | what it looks like | fix |
|---|---|---|
| **The off hand is mirrored** (`hw_vrmodes.cpp:468`, scale -1 on the left hand) | a "left" hand frame draws as a right hand on the left controller; a magazine 2 x 3.9 cm off its axis | bake every off-hand frame as the RIGHT rig; flip L for off-hand targets; a side-loading well also needs a 180 degree yaw (`mags.py at()`) |
| **The open palm passes every number** | a support hand floating flat under the gun, contact and penetration within tolerance; the owner rejects it on sight | look at the frame from the eye (rule 4); start the support from 1.92's hold (support192), so the hand wraps (Rifle: 255 degrees) |
| The engine re-aims a steadied gun at the off hand | a hand on the charging handle is suddenly 16 cm away the tic the grip goes down | in grip mode the off TRIGGER takes the handle; never assume the gun stays put when steadied |
| Steadying a sword | the blade swings onto the off hand | draw a second sprite whose block is turned so the handle runs toward the off hand (`DSL2`) |
| Moving the gun but not what hangs off it | butt strikes landing behind the stock; the Purist rifle without its tube; a support sitting 0.7 cm off a re-fitted gun | `port_gun.py` moves everything it knows; then check melee points (`butt_move.py`), variants (`variants_all.py`) and the support rows by eye |
| A shortcut: baking the hand on the UNMOVED gun | a whole batch had to be reverted | the gun moves first, the hand is baked against the moved gun |
| A key-0 row in `gunmoves.zs` on 17.3's VM | every hand off its fit on 21 of 26 guns, 360-4328 px from 1.92 | key unused rows to a gun that does not exist (99), never 0 |
| More than 255 constants of one type in one function | the VM reads the wrong row | one table per type, split long tables |
| Fists left as Ermac's while everything else is FBX | mixed gloves and skin in one frame | the owner decides per hand family; check every frame for a stray glove |

## Code

| trap | what it looks like | fix |
|---|---|---|
| **An `EventHandler` not in MAPINFO `AddEventHandlers`** | it compiles, ships, and never runs | register it; prove it ran with a `Console.Printf` |
| ZScript names are case-insensitive | `const TRAVEL` beside `Travel(int)`: "Attempt to redefine"; `int m = min(d, M)` re-declared `M` and a counter never went down | distinct names |
| A static called on the wrong class (`RSR.WantsHands` lives on `RSR_ReloadHandler`) | the first pk3 ever handed over died at script parse | grep the class a static lives in; boot before anything leaves |
| Numeric jumps (`A_Jump*(.., n)`, `Goto Ready+6`) after you insert a state | the Flamethrower returned to the wrong frame; the Shotvolver copy re-fired forever and stopped the main gun | named jumps; or check every counted jump against the parent's file after patching |
| DECORATE takes the LATER of two labels | the M32's reload key did nothing (BD22's stub `Reload:` after ours) | remove or rename the parent's label |
| `extend class Weapon` | "Class Weapon cannot be found in the current translation unit" | no roll on the gun layer; use `psp.x/y` or a layer you own |
| ZSCRIPT compiles before DECORATE | a ZScript class cannot inherit a DECORATE class | put the subclass in DECORATE; DECORATE can name ZScript classes |
| `version "4.10"` in the root ZSCRIPT lump | `WorldHitscanPreFired` is hidden | declare `version "4.14"`; a `version` line in an included file is refused |
| A pose field read before the first rendered frame | a crash on loading a save (`AttackDir` before the engine set its pointer) | guard with `OverrideAttackPosDir` (`vrhand.zs`) |
| Two features on one psprite id | one of them silently stops | `RSQ_Layers.Taken(id)` before claiming an id |
| Our sound file with the same 8-letter lump name as the parent's | the parent's ricochets, glass and mag drops played our files | rename ours (`rqsNNNNN`) and point our SNDINFO at them |
| `MENUDEF OptionValue` written `0 = "Text"` | menu init dies with nothing in the log | `0, "Text"` |
| A 2D canvas texture | the texture never changes, or renders black, on this 17.3 build | camera textures work; for discrete looks use pre-made textures and `A_ChangeModel` |

## The rig and the scripts that drive it

| trap | what it looks like | fix |
|---|---|---|
| **`+forward` does nothing in VR mode** | the player never walks to a pickup | `qz_lstick "0 1"` |
| **BD22 pickups ignore you for their first 10 tics** (THRUACTORS), and a pickup on a ledge is out of reach | "dual wield does not work" | wait, and walk onto the pickup; this was the script, not the pack |
| `wait` inside an alias does not fire | a script that ends early | write the waits in the run's own script; runs end by `quit` or the timeout |
| A press shorter than one rendered frame on the slow rig | an alt-fire toggle "missed" | hold buttons 40 tics in tests; real input does not have this problem |
| Giving a gun and using it at once | the gun never raised, no shot, a clean log | about 150 tics after `use` before testing it |
| A relative `-file` path and a `cd` | the pack was never loaded; every marker present; exit 0 | absolute paths; check `adding <pack>, N lumps` in the log |
| The wrong ammo name (`Shell` vs `AmmoShell`) | the gun is selected, fires nothing, nothing in the log | read each gun's `AmmoType1` from its DECORATE |
| A fatal script error does not reach redirected output | the log just stops, looking clean | `+logfile` (rig.py does it); read `<name>.log` |
| "No errors" is not "it ran" | a run that died early looks like a pass | count the markers or probe lines you expect; prove a path with `Console.Printf` |
| The engine's `screenshot` in VR mode | garbage | the frame dump |
| **Disk full from frame dumps** (an unthrottled dump of a fast run filled the shared disk) | other lanes' writes fail | `QZ_DUMP_EVERY` of a few frames, convert to PNG and delete the `.ppm` at once |
| **An orphaned Xvfb holding the lock** after its parent died | every exclusive run stalls for 20 minutes | `flock -o` (children never inherit the lock); kill stray Xvfb / qzdoom |
| Several engines at once on 2 cores / 8 GB | runs killed for memory, timeouts, false failures | one engine at a time (`flock -o -x`); load average under 2 for timing tests |
| Stale driver geometry (constants typed for an older placement) | a reload that never seats, after the gun moved | take geometry from the live tables (the probe's `B22 GUN` lines from a fresh boot of THIS pack) |
| A prebuilt engine from the wrong commit (4.15pre) | everything "works" and every result is void | the version guard (`qz: engine OK`); stop on anything else |
| Chaining pipeline stages with `;` | a failed stage followed by a sync emptied half a set | `&&` and `set -o pipefail` |

## Process

| trap | what it looks like | fix |
|---|---|---|
| **Interrupting the coordinator stops every background lane, silently** | status reported from assumption for hours | after any interrupt or restart, check each lane's files and processes before reporting |
| **A committed tool importing from an uncommitted run folder** | deleting the folders for disk space broke 18 tools | commit the modules (`fitter_lib`), point data at the repo (`tools/depot.py`) |
| Two lanes writing in one checkout | a build carries another lane's half-finished files | one worktree per lane |
| A pk3 handed over before it booted on the owner's load order | a script error in his headset | rule 8; the answer to "do you have a pk3?" is "not yet" |
| Reading a design note on a card as a law, or "no such surface" from surface names alone | a gun closed that could reload (a welded surface held 124 bodies) | look at the geometry; only the owner closes a gun |
| A proxy that refuses some pushes (tags) in the cloud session | `git push --tags` fails | push branches; the archive is a branch (`archive/depot-2026-10-28`), not a tag |
