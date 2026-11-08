# The VR weapon handbook (QuestZDoom 17.3)

How to give a Doom weapon set real VR mechanics on **QuestZDoom 17.3** (Emawind's TeamBeef fork, the version
players run on Quest): hands on the guns with the finger on the trigger, reloading with your hands, live
scopes, melee, throwing, dual wield. Nothing here changes the engine. Everything ships as ZScript, DECORATE,
MODELDEF and models.

It is written from the work that produced **BD22 VR Weapons Q 2.0.1** (`sets/bd22q`), the first full set
built this way, and every command and path in it was checked against this repository (see
[VERIFIED.md](VERIFIED.md)).

**Who it is for:** a modder who knows Doom modding (DECORATE, ZScript, MODELDEF) and has never seen this
project, and any Claude session picking the work up. If you are new, read the chapters in order once. After
that, chapter 4 (one gun end to end) and chapter 6 (traps) are the ones you come back to.

## The map

| chapter | what it answers |
|---|---|
| [01 How VR weapons work on QZD 17.3](01_how_vr_weapons_work.md) | Controllers and head, how a weapon model is drawn in VR, MODELDEF in detail, how hands are drawn, the mirrored off hand, `A_ChangeModel`, camera textures. |
| [02 The test rig](02_test_rig.md) | The real engine on Linux with posed controllers. Setup from a fresh clone, running a pack on the owner's load order, posing hands, frame dumps, logs, the lock, resources. |
| [03 The toolset](03_toolset.md) | Every tool in `tools/`: what it does, its inputs, the command, what good output looks like. Paths and environment variables. Known gaps. |
| [04 One gun, end to end](04_one_gun_end_to_end.md) | The Rifle, from mesh to headset, with the real files and numbers. |
| [05 Mechanics cookbook](05_mechanics_cookbook.md) | How each mechanic is built (magazine, break-open, pump, cylinder, under-barrel launcher, steadying, melee, throwing, scope, dual wield, ballistics, skin tone, HUD, ammo on top) and where its code is. |
| [06 Traps and fixes](06_traps_and_fixes.md) | Every trap that cost a day, and its fix. |
| [07 Working with Claude](07_working_with_claude.md) | Running this with Claude agents: lanes, briefs, liveness, the fit farm, reviewing frames. |
| [SKILL.md](SKILL.md) | The same process in one page, for a Claude session to load. |
| [REMA_BLOCKERS.md](REMA_BLOCKERS.md) | Addendum for REMA: what it takes to put these hands on REMA's avatars, and what blocks it. |
| [VERIFIED.md](VERIFIED.md) | This handbook followed on a fresh clone: what was run, and the result of each step. |

## Words used everywhere
- **Gun hand / main hand**: the controller that holds the weapon. **Off hand**: the other one.
- **Support hand**: the off hand holding the front of the gun (fore-end, pump, handguard).
- **Steadied**: the engine's two-hand mode. Press the off grip within 50 cm of the gun and the engine aims
  the gun from the main hand towards the off hand (chapter 1).
- **F / L / U**: centimetres in the weapon controller's frame: Forward, Left, Up. Almost every number in
  the code and in this handbook is in this frame.
- **The rig**: the real QuestZDoom 17.3 engine built for Linux, with the headset and controllers posed by
  console variables, rendering the left eye to image files (chapter 2).
- **The FBX hand**: the rigged hand model (`hand_final.fbx`, 22 joints) the 2.0 hands are posed from. Only
  baked MD3 frames of it ship. **Ermac's hands**: the older posed hands (Force Unleashed / Rusted Legacy,
  MIT) that BD22Q 1.92 used; their holds are the starting point for every 2.0 grip.
- **1.92**: BD22Q 1.92, the release whose hand holds the owner judged good. It is the reference.

## The ten rules

1. **One method.** The drawn wrist is pinned to the controller. The **gun moves to the hand**, and
   everything on the gun moves with it: every MODELDEF block that draws it, the muzzle, the ejection port,
   the reload rows, the scope lens, the recoil rows, the melee hit points. Never tilt the gun away from where
   the controller points to improve a grip (owner: "I would sooner accept a less than perfect grip than I
   will accept a tilted mesh").
2. **Start from existing poses.** Every grip starts from a named pose that already works (pistol grip /
   trigger / squeeze; foregrip / vgrip; pump / wrap; under / cup) or from that gun's 1.92 hold. Solve from
   scratch only when nothing fits. (The Flamethrower's "gas-pump grip" was the pump grip all along; ignoring
   that cost hours.)
3. **Measure, don't guess.** Every number comes from a mesh (measured by a tool) or from the parent mod's
   code (parsed). Write down which. Never type a number from memory.
4. **Look at every frame from the eye. Numbers lie.** An open palm under a gun passed every numeric check
   (no penetration, contact within tolerance) and was obviously wrong to anyone who looked. A sheet of
   frames is part of every result.
5. **Variants copy rows, never re-fit.** A Purist (or any variant) gun copies its base gun's rows and
   blocks exactly. `tools/int20_rig/variants_all.py` proves it.
6. **Nothing is "working" until it is shown working on the rig**: in-engine frames or a log of the
   behaviour itself, never "the code exists" or "it compiles". Anything VR is **"rig only, not
   headset-confirmed"** until the owner has played it.
7. **No engine changes to QuestZDoom 17.3.** If it seems to need the engine, find the script route
   (chapter 1 lists the hooks that exist). Compiling the engine for the rig is fine; changing it is not.
8. **Load order and zero script errors before any headset**: doom2 -> brutal22test6 -> BD_VoxelPack -> the
   pack, with no script error from the pack. BD_VoxelPack prints four of its own (`voxeldef.txt` lines 66,
   72, 77, 892); those are not yours.
9. **Commit every tool and every pose.** A committed tool must never import from, or default to, a folder
   that is not committed. (Deleting uncommitted run folders for disk space once broke 18 tools.)
10. **Check every lane after any interrupt.** An interrupt or a restart silently stops background work.
    Look at the files and processes before you report anything as running.
