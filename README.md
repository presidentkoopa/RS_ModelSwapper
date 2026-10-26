# ModelSwapper

3D weapons for any Doom mod, made for playing in VR.

The usual way to get one is for someone to hand-author a model set for a specific mod: every weapon modelled, fitted to the hand and animated to that mod's timing. That is a lot of work for a single mod, and the Doom VR community is small. Most weapon mods will never get a set of their own, including ones people love.

ModelSwapper doesn't wait for that. It carries one shelf of models and fits it to whatever you load.

![The model picker, with Project Brutality loaded](media/pb-choose-models.png)

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

## 2.0: hands and VR reloading on Quest (branch `modelswapper-2.0-bd22-lift`)

Our models, their code, collective reloads.

Load Brutal Doom, or Ashes, or a weapon mod written in 2009 by someone who has never heard of VR. Hit reload, and the magazine drops out of the gun. You reach down and grab a fresh one, slap it into the well and rack the handle. The mod's own reload then fills the gun with the mod's own ammo, its own rules and its own sounds.

Nobody wrote a VR version of that mod. Nobody had to.

A pump shotgun waits for your hand on the forend between shots. A double barrel breaks open, throws its empties and takes shells one at a time, then shuts with a flick of the wrist. A revolver's cylinder swings out and snaps back in.

All of it sits on top of weapon code ModelSwapper has never seen. It reads the mod's states from outside and holds the gun at the right moment while your hands do the work. Then it hands the gun back exactly where the mod expects it. It never touches the mod's ammo or its code. Every number the hands use is measured from the meshes themselves: where the magazine sits, how far it travels, where the pump starts in the fire animation. None of it is typed in by hand.

One shelf of models is measured once and then reloads on every mod, forever. That's the whole idea. As far as we know, nobody has done it before.

ModelSwapper still puts its models on whatever weapon mod is loaded, and that mod's code still fires the gun and decides every round. What 2.0 adds on the Quest build:

- **Hands on the guns.** Ermac's VR hands hold each model: gun hand on the grip with a finger on the trigger, support hand on the gun.
- **VR reloading on any mod that reloads.** When the mod's weapon starts its own reload, ModelSwapper hands the physical part to you, then gives the gun back and the mod's reload fills it with the mod's own ammo:
  - **Magazine guns:** pull the magazine, take a new one, seat it. Reloaded from empty, guns with a charging handle or slide ask you to rack it too.
  - **Pump shotguns:** push shells into the port one by one; the mod's own loop counts them. Between shots, with your off hand on the forend, the gun waits at the mod's own pump for you to work it, then the mod's fire carries on.
  - **Break-open guns:** open the action, load the chambers, flick it shut.
- **74 reloadable models:**
  - 64 magazine guns, 24 of them with a charging handle or slide;
  - 4 pump shotguns;
  - 6 break-open guns and revolvers.

  Every model's reload data is measured from its own mesh and the place it is drawn, except 9 whose animation moves no magazine (flamethrowers, Unmakers, Bolters, TEC-9s, the Buzzsaw). Those keep the older numbers.
- **Options, VR Reload:**
  - *Reload sounds*: ModelSwapper's magazine and shell foley, or the mod's only.
  - *Pump by Hand After a Shot*: on or off.
  - *Charging Handle After Empty*: on or off.
  - *Grab ammo with*: trigger or grip. A charging handle can only be taken with the trigger.

Each model is tested headless by `gate/run_gate.py`, and `gate/run_all.py` runs them all:
- **Desktop build:** all 74 PASS (2026-10-25). This covers the logic, the models and the drawing.
- **The Quest's own engine build, with real VR input:** simulated controllers, the real grip and trigger keys, and the pack's own hand code. Every reload kind is driven by a simulated hand, with no shortcut through the reload's own functions. This is the owner's `Quest_Weapons_Kit` rig; see `gate/qz_rig/`.

Feel and reach are the headset's to judge. `HANDOFF_2.0_2026-10-25.md` lists what is measured, what is open, and every fault found on the way.

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

2.0's tools are in `tools_kit/`, and the gate is in `gate/`. Every number they write is copied from a measured source or regenerated by the kit's own generator, never typed in:
- lift_bd22.py and lift_aliens.py put a Quest set's guns on the shelf with that set's own reload rows, layers and hands.
- regen_rows.py remakes a card-measured gun's reload row at the place the gun is drawn, using card2quest → genpack → gen_rsr.
- card_leftovers.py measures, with md3label, each gun that only had a `_wm` card, on the mesh it is actually drawn with.
- rack_frac.py measures where each pump shotgun's pump starts in its fire animation, for the pump by hand.
- rest_frames.py moves a model drawn mid-raise to its measured rest frame.
- gunmoves_ms.py works out where each gun turns under the hands, from its own model definition.
- md3_frames.py adds one set's hand poses to the shared hand mesh without moving any existing pose.
- placement_audit.py reports, for every reloadable gun, how far its reload row is from where the gun is drawn.
- fix_layer_skins.py makes sure every skin a shipped model definition names is in the pk3.
- build_quest.py is the Linux equivalent of `./build.ps1 -Static`, and it checks every asset.
- gate/run_gate.py runs one gun through a full reload, headless, and prints PASS or FAIL per step. Add `--vr` to run it on the Quest-faithful rig, `--shot` to test the pump by hand after a shot, and `--shots` for screenshots, which on the rig are the real eye view. gate/run_all.py runs every reloadable model.

## Making a model reloadable: the pipeline

This is how one of the shelf's models becomes a gun you reload with your hands on any mod. Each step is a tool in this repo. Each reads what the step before it wrote. No number is typed in.

**You need:**
- Python 3 with numpy and Pillow (`pip install numpy pillow scipy`)
- the model already on the shelf: its MODELDEF block in `modeldef` and its row in `zscript/RS_ForeignModels.zs`
- for the test: a QuestZDoom 17.3 build and `freedoom2.wad`

**1. Check the model rests on the right frame.**
```
python3 -B tools_kit/md3label.py <mesh.md3> /tmp/look MS_YourGun --idle 0
```
Look at the `phases` list in `/tmp/look/MS_YourGun.card`. If the frame the model is drawn on is a `raise` frame, the gun sits mid-raise. Add the measured rest frame to `REST` in `tools_kit/rest_frames.py`, with a note on how you know, and run:
```
python3 -B tools_kit/rest_frames.py
```

**2. Measure the gun from its own animation.**
```
python3 -B tools_kit/card_leftovers.py --donor MS_YourGun
```
This runs md3label on the mesh the model actually draws, at its rest frame:
- It finds the parts by how they move: the magazine, the charging handle or slide, the trigger.
- It finds the reload's phases and carves the magazine into its own mesh.
- It writes the card to `cards_left/` and the carved magazine beside the mesh.
- `card_from_motion` turns that into the reload grammar in `WMCARD.left`.

If the animation never moves a magazine, it says so and stops. Nothing is guessed.

**3. Make its reload row, at the spot it is drawn.**
```
python3 -B tools_kit/regen_rows.py --add MS_YourGun
python3 -B tools_kit/fix_layer_skins.py
```
This runs the kit's own chain at the model's drawn placement and rest frame: card2quest → genpack → gen_rsr. The model gets:
- its own reload slot;
- its reload layers in `MODELDEF.cards`;
- its foley aliases in `SNDINFO.ms`;
- a charging handle, if a slide was measured.

**4. Hands.** Most shelf models already have a hand row in `zscript_depot/rsq/handtable.zs`. A new one needs a fit: `tools_kit/handfit_cards.py`, the kit's method on Ermac's hands. Then run `tools_kit/gunmoves_ms.py`, which works out where the hands turn with the gun. Without a hand row, the reload still works, but no hands are drawn on the gun.

**Pump shotguns** get their rows from `tools_kit/gen_pump.py`, then `python3 -B tools_kit/rack_frac.py`. That measures where the pump starts in the fire animation, for pumping by hand between shots. **Break-open guns** get theirs from `tools_kit/gen_rsb.py`.

**5. Build.**
```
python3 -B tools_kit/build_quest.py ModelSwapper-QUEST.pk3     # Linux
./build.ps1 -Static                                          # Windows
```
Both check every model, skin and sprite that any MODELDEF names.

**6. Test it.**
```
python3 -B gate/run_gate.py ModelSwapper-QUEST.pk3 MS_YourGun            # desktop, headless
python3 -B gate/run_gate.py ModelSwapper-QUEST.pk3 MS_YourGun --vr       # the Quest engine, simulated controllers
python3 -B gate/run_gate.py ModelSwapper-QUEST.pk3 MS_YourGun --shots    # plus screenshots
python3 -B gate/run_all.py  ModelSwapper-QUEST.pk3                       # every reloadable model
```
The test puts your model on a weapon written like any mod's, with its own Reload state and its own ammo. Then a scripted hand does the reload. Each step prints PASS or FAIL:
- the join took the gun;
- the magazine came out;
- the hand carried a new one;
- it seated, and the handle was racked;
- the gun went back to the mod, and the mod's own reload filled it.

`--vr` runs the same test on the Quest's own engine code with simulated controllers (`gate/qz_rig/README.md`).

**7. Then the headset.** The gate proves the logic and what is drawn. Reach and feel are yours to judge.

Worked through on MS_hacx_UZI (2026-10-26, dry run): step 2 measured a 20-unit magazine stroke and a 6-unit handle. Step 3 gave it slot 81, with the handle and the well 11 cm from the grip.

## Which build

ModelSwapper.pk3 is the desktop VR build, for [UZDXREMA](https://github.com/presidentkoopa/UZDXREMA). Models are animated, reloads included.

ModelSwapper-QUEST.pk3 is for standalone Quest, on [QuestZDoom](https://github.com/emawind84/QuestZDoom). It has the same models and the same picker. The models don't play their own animations, because that needs engine features Quest doesn't have. From 2.0 the Quest build has the hands and the VR reloading described above. Fit In Hand and the muzzle flash setting are engine features too, so they do nothing there. A full Quest build is about 450 MB.

Load either one after your weapon mod. To build them from source, run ./build.ps1, or ./build.ps1 -Static for the Quest build.

INTERNALS.md explains the binding, classification and animation in detail, along with what they can't do. ENGINE_CHANGES.md covers the engine changes the animation needs.
