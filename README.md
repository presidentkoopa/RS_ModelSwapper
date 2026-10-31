<img width="1248" height="1011" alt="Untitled" src="https://github.com/user-attachments/assets/b21b0fef-8a9f-41d2-a60f-d264206f1716" />
# ModelSwapper

3D weapons for any Doom mod, made for playing in VR.

The usual way to get one is for someone to hand-author a model set for a specific mod: every weapon modelled, fitted to the hand and animated to that mod's timing. That is a lot of work for a single mod, and the Doom VR community is small. Most weapon mods will never get a set of their own, including ones people love.

ModelSwapper doesn't wait for that. It carries one shelf of models and fits it to whatever you load.

![The model picker, with Project Brutality loaded](media/pb-choose-models.png)

Every weapon the loaded mod gives you, the family it was sorted into, and the model it is wearing. Any model can go on any weapon.

**Coming in 2.0: VR hands and hand reloading on any mod. Our models, their code.** Load any weapon mod, even one written long before VR, and its guns reload by hand the way each model is built: pull the magazine and seat a new one, break the shotgun and load the shells, work the pump, swing out the cylinder. The mod's own reload decides the ammo, rules and sounds. 2.0 is in progress on the `modelswapper-2.0-bd22-lift` branch, and its README says honestly what works today and what does not. Also coming: renamed models and selectable skins.

## Project goal and status (MS 1.5, 2026-10-31)

**Goal.** Load any Doom weapon mod in VR, pick any of our 3D models for any of its weapons, and reload by hand the
ones whose model can be reloaded (magazine out and in, shells into a pump or break-action, cylinder swung out) --
the mod's own code deciding ammo, rules and sounds. Quest (QuestZDoom 17.3) and PCVR.

**Where it stands (measured, 2026-10-31).**
- The model well was rebuilt from scratch into one unified system: `cards/<set>/<gun>/` holds, for every mesh, its
  card (measured parts, roles, states), the labelled mesh, the carved reload parts, its textures and a render sheet.
  143 donors; every card mesh has all of its source frames (checked against the source mesh, frame count and space).
  The measuring tools live in RSQ_WeaponDepot (`tools/hqt`, `tools/carve`); the cards and meshes live here.
- The donor systems are GENERATED from the cards (`tools_gen_from_cards.py` -> `modeldef`, donor stubs, shelf, names).
  **There is no placement math.** Every donor copies its own set's calibrated MODELDEF block (Skin, Scale, Offset,
  ZOffset, angles) and rests on the frame that block shows at the weapon's Ready state:
  - 142 of 143 donors on their own set's block. The exception is the Robocop KSG: the mod dropped it, no MODELDEF
    names the held mesh, so it sits at Scale 1.
  - Held frame read from the original code (Ready state through the block's model-0 FrameIndex, A_ReplaceSprite and
    renamed/pasted blocks followed) for the large majority; the rest are overlay parts or owner answers, each noted
    in `ready_frames.report.md`.
  - `sources.lock.json` records what every donor resolved to, so the output reproduces from this repo alone.
    The parent mods and add-on sources used to resolve it are listed in the generator's `--actors` / `--set-extra` help.
- `tools_rig_check.py` builds the Quest pk3, runs a donor on the Linux QuestZDoom rig on doom2 (+ a mod), pins the
  off hand, selects the gun the Depot-rig way, reads back the donor actually applied and makes a contact sheet.
- Rig, doom2 + Doomablo 0.9.1a, zero script errors from the pack: Doomablo's pistol, shotgun, rifle, SSG, rocket
  launcher and chaingun wear BD21's pistol, shotgun, rifle, SSG, RPG and minigun; alek's pistol on the pistol.
  Rig only, not headset-confirmed.
- Repository = three things: systems, cards (meshes + textures), the generators. Everything older is on branch
  `archive/pre-cards-2026-10-31` (see `ARCHIVE.md`).

**Next.** 1) Reload: re-point `MODELDEF.rsb` / `MODELDEF.rsrpump` and the WMCARD props at the cards, then drive one
hand reload on the rig (BD21 rifle on Doomablo's assault rifle). 2) Picks across all 143 donors on the rig.
3) Zion and Samsara: large sets, tabled, to be done together later. The other well folders are duplicates and are
ignored.

## How it works

ModelSwapper reads every weapon the loaded mods define and sorts each one into a family, such as pistol, shotgun, rifle or launcher. It goes by the weapon's name, its ammo and its parent class, and finally by the weapon slot it sits in, so nothing is left without a model. Each weapon then wears a model from its family.

The animation is driven by the weapon's own code. Every Doom weapon already reports what it is doing each tic through its states: ready, fire, reload, raise, lower. When a model is attached, ModelSwapper maps those states onto the model's frames, and from then on the model plays whatever the weapon is doing. A reload lasts exactly as long on the model as it does in the mod, a partial reload plays short, and the very first shot is already in time, with nothing to learn or calibrate.

Nothing in it is written for a particular mod, so a pack released tomorrow works the same way as one from 2016. It has been calibrated against the following mods:

- vanilla Doom
- Brutal Doom v21 and v22
- Brutal Doom 64, Doom 64 Unseen Evil and Doom 64 Retribution
- Project Brutality 0.4.1
- Golden Souls 1 and 2
- Ashes 2063 and Ashes Afterglow
- DoomRL Arsenal
- Guncaster
- MetaDoom
- Trailblazer
- Combined Arms
- Final Doomer
- LegenDoom Lite
- Complex Doom
- Lithium
- Dakka
- Pandemonia
- MeatGrinder
- VanillaVR Plus
- the DOOM Infinite demo
- SELACO - Uses its own models.
- Wolfenstein: Blade of Agony - Recommend to use WW2 Addon.


Each one's weapon code was checked against the model menu, so the menu lists the guns you can actually hold and leaves out the vehicles, meat shields, ledge grabs and other helpers a mod builds out of weapon code.


36 models across 22 weapon families, built from 34 meshes (the rest are alternate finishes), about 30 MB in all. 


All 35 are in renders/, and renders/sheets/ lays the before and after views side by side.

## Tools

Everything used on the models is in this repo. The scripts need Python 3, and the renderer also needs Pillow.

- tools_md3_pitch.py reads an MD3 mesh and measures the angle of every frame.
- tools_md3_reorigin.py centres a mesh on its origin and verifies the result byte by byte.
- tools_md3_compensate.py works out the position setting that keeps a centred gun exactly where it was, using a copy of the engine's own transform.
- tools_reorigin_all.py runs both over every model and stamps each model definition so a block can never be adjusted twice.
- tools_md3_render.py draws the wireframe renders shown above.
- tools_clip_audit.py shows which frames each animation uses and which frames nothing plays.
- tools_pitch_audit.py finds raise and sprint frames that swing the gun away from its resting angle.
- tools_model_inventory.py writes a full inventory of every model: frames, poses, angles and animations.
- tools_gen_pickups.ps1 generates the pickup model definitions from the meshes.
- tools_gen_bd21.ps1 generates the Brutal Doom v21 shelf from Brutal Doom's own model definitions.
- tools_zs_lint.py checks the ZScript for syntax errors before build.ps1 packs anything.
- tools_make_pb_offhand_patch.py builds a VR patch from your own copy of Project Brutality 0.4.1: its guns move between hands without crashing, and casings, smoke and muzzle sparks come off the gun instead of your face. Load it after PB.

## Which build

ModelSwapper.pk3 is the desktop VR build, for [UZDXREMA](https://github.com/presidentkoopa/UZDXREMA). Models are animated, reloads included.

ModelSwapper-QUEST.pk3 is for standalone Quest, on [QuestZDoom](https://github.com/emawind84/QuestZDoom). Same models and the same picker, but the models hold still, because animation needs engine features Quest doesn't have. Fit In Hand and the muzzle flash setting are engine features too, so they do nothing there.

Load either one after your weapon mod. To build them from source, run ./build.ps1, or ./build.ps1 -Static for the Quest build.

INTERNALS.md explains the binding, classification and animation in detail, along with what they can't do. ENGINE_CHANGES.md covers the engine changes the animation needs.
