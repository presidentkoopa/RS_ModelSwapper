<img width="1248" height="1011" alt="ModelSwapper" src="https://github.com/user-attachments/assets/b21b0fef-8a9f-41d2-a60f-d264206f1716" />

# ModelSwapper

**3D weapons for any Doom weapon mod, made for VR, with hand reloads on the guns that can reload.**

Load a weapon mod, then load ModelSwapper. Every weapon the mod gives you wears a 3D model, held in your hand, and
you can put any model on any weapon. Where the model can be reloaded, you reload it by hand: pull the magazine and
seat a new one, work the pump, break the shotgun and load the shells, swing out the cylinder. The mod's own code still
decides the ammo, the rules and the sounds. Nothing is written for any one mod, so a mod released tomorrow works the
same way as one from 2016.

![The model picker, with Project Brutality loaded](media/pb-choose-models.png)

## Status: version 1.5 (2026-10-31)

All results below were run on the QuestZDoom 17.3 test rig. **None are headset-confirmed yet.**

| | |
|---|---|
| Models | 143 meshes from 17 VR weapon sets, every one selectable on any weapon |
| Placement | each model sits where its own set's hand-authored MODELDEF puts it, on the frame that set shows at Ready |
| Magazine reloads | 37 models, generated from their cards |
| Pump reloads | 6 shotguns (the Meatgrinder SSG uses Ermac's shell in the loading hand) |
| Break-open / revolver | 5 models (BD M79, BD revolver, BD SSG, V+ revolver with speedloader, V+ SSG) |
| Charging handle | asked for after an empty reload; racked by the off hand |

Shown working on two mods that reload properly, with 0 script errors from the pack:

| Mod | Weapon | Model | Reload |
|---|---|---|---|
| Generic weapons | ARifle | BD rifle | magazine, and charging handle when shot dry |
| Generic weapons | Beretta | BD pistol | magazine + slide |
| Generic weapons | Riotgun | BD shotgun | shells into the port, pump after the shot |
| Generic weapons | DoubleSG | BD SSG | break open, two shells, flick shut |
| Weapons of Saturn | MachineRifle | BD rifle | magazine |
| Weapons of Saturn | Beretta / 1911 / MP40 | BD pistol / BW 1911 / BD MP40, BD SMG | magazine + slide or handle |
| Weapons of Saturn | Riotgun | BD shotgun | shells + pump |
| Weapons of Saturn | Coachgun | BD SSG | break open, shell, flick shut |

What is still open is listed in [HANDOFF.md](HANDOFF.md), most important first.

## Using it

- **Desktop VR:** `ModelSwapper.pk3`, for [UZDXREMA](https://github.com/presidentkoopa/UZDXREMA). Models animate with
  the weapon.
- **Quest:** `ModelSwapper-QUEST.pk3`, for [QuestZDoom](https://github.com/emawind84/QuestZDoom) 17.3. Same models,
  picker and reloads. The models hold their rest pose, because animating them needs engine features Quest does not
  have.

Load it **after** your weapon mod. The model picker lists every weapon the mod defines and which family it was sorted
into (pistol, shotgun, rifle, launcher and so on), with the model it is wearing. Pick any model for any weapon.

Reload options are in the menu. **Reload Order** decides whether the mod's own reload runs first (the default) or the
hands go first. **Charging Handle After Empty** decides whether an empty gun asks for its handle. The menu also has
pump-by-hand-after-a-shot and shells per grab.

## How it works

1. **Sorting.** ModelSwapper reads every weapon the loaded mods define and sorts each into a family. It looks at the
   name, the ammo, the parent class, and last the weapon slot, so no weapon is ever left without a model. A weapon
   that takes ammo or shows a muzzle flash always counts as a gun. Handlebars, lanterns and other helpers a mod builds
   out of weapon code don't get a model.
2. **Wearing a model.** The weapon's model data is pointed at the chosen model, so the engine draws our model in its
   place, with that model's own skin, scale and offsets. On desktop the weapon's own states drive the model's frames
   every tic.
3. **Hand reloads.** When a weapon wearing one of our models reloads, the join (`zscript/RS_ForeignReload.zs`) takes
   over:
   - It lets the mod's own reload run, so its ammo and rules stand.
   - It holds the weapon while the hands do the reload.
   - It gives the weapon back when the hands finish.

   Which reload a model gets comes from its slot in the reload tables: magazine (`RSR_Guns`), pump (`RSP_Guns`) or
   break-open (`RSB_Guns`). The slot is looked up from the model in the hand, not from the mod's weapon class. That's
   why it works on mods nobody has looked at.

## The cards

Everything starts from `cards/<set>/<gun>/`. Each folder holds:
- **The card** (`.card`): measured parts, roles, states, muzzle, grip and magazine well.
- **The labelled mesh** with all of its source frames.
- **The carved reload parts:** magazine, pump, hinge, rounds.
- **Its textures and a render sheet.**

The cards are measured with the RSQ_WeaponDepot tools (`tools/hqt`, `tools/carve`). The donor system and every
reload table are **generated** from them. Nothing is placed or wired by hand.

| Generator | Writes |
|---|---|
| `tools_gen_from_cards.py` | `modeldef`, donor stubs, shelf + names (each model on its own set's MODELDEF block; `sources.lock.json` makes it reproducible from this repo alone) |
| `tools_kit/card_mag.py` | magazine rows `zscript_depot/rsr/rsr_guns.ms.zs` + layers `MODELDEF.cards` |
| `tools_kit/card_pump.py` | pump rows `rsr_pump_guns.zs`, `rsp_rack.ms.zs` + layers `MODELDEF.rsrpump` |
| `tools_kit/card_break.py` | break-open rows `rsb_guns.zs` + layers `MODELDEF.rsb` |
| `tools_reload_modeldefs.py` | `MODELDEF.cards2x`: the 2.0-measured layers for the few models card_mag does not build |

Regenerate in that order. Each generator writes a report (`*.report.md`) saying what it built and why it left
anything out.

## Building

`./build.ps1` builds the desktop pk3; `./build.ps1 -Static` builds the Quest pk3. `tools_zs_lint.py` checks the
ZScript before anything is packed.

## Testing on the rig

The rig is QuestZDoom 17.3 on Linux, run on the real `doom2.wad`, with simulated head and hand poses.

- `tools_rig_check.py --donors MS_BD_Pistol,... --weapon <class> --extra <mod.pk3>` builds the Quest pk3. It puts
  each model on a weapon, reads back the model actually applied, and makes a contact sheet.
- `tools_rig_reload.py --kind mag|pump|break --donor <model> --weapon <class> --extra <mod.pk3>` drives one full
  hand reload and prints every phase. For magazine guns:
  - `--clicks N` or `--fire-tics N` shoots the gun dry first.
  - `--rack` works the charging handle.

**Test reloads on a mod whose weapons really have a Reload state.** The generic weapons pack and Weapons of Saturn
both do. Doomablo's shotgun and super shotgun reload inside Fire, so they never hand over a reload.

## Repository

- `zscript/`: the model swapper, the reload join, the picker.
- `zscript_depot/`: the reload system and the VR hands, plus the generated reload tables.
- `cards/`: the meshes, textures and cards.
- `tools_kit/`: the generators and the measuring kit.
- `tools_*.py`: placement, rig and mesh tools.
- `models/rsq`, `sounds/`, `SNDINFO.ms`: the VR hands and the reload foley.
- `reload_1x/`: the 1.x / 2.0 reload layers kept as reference for `tools_reload_modeldefs.py`.

Earlier work, including the 1.x model shelf and the 2.0 branch (`modelswapper-2.0-bd22-lift`), is described in
[ARCHIVE.md](ARCHIVE.md). The old tree is on branch `archive/pre-cards-2026-10-31`.

## Credits

The models are the work of the VR weapon set authors: Ermac, alek, and the Brutal Doom, Brutal Wolfenstein, Aliens,
MeatGrinder, HacX, Chex, Cola, Doom 64, Robocop, Universal Voxel, ZBlood and other set makers. See each set's
`cards/<set>/NOTES.md`. The VR hands are Ermac's.

ModelSwapper builds on teambeef QuestZDoom, ported to PC by Emawind84, moved into UZDoom by Ermac, and brought up
to UZDoom 5.0 with its VR features by presidentkoopa.
