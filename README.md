# ModelSwapper 1.5

ModelSwapper puts VR weapon models on the guns of any Doom weapon mod, and lets you reload them with your hands.

You keep the mod. Its weapons, ammo, damage and reload rules all stay as the mod wrote them. ModelSwapper changes what
you hold: a 3D model from one of 17 VR weapon sets, placed in your hand where that set's author placed it. When a gun
reloads, your hands do the work the model was built for, while the mod keeps the books.

## What works today

Tested on the QuestZDoom 17.3 rig. Not yet confirmed in a headset.

**Models.** 143 meshes. Any of them can be chosen for any weapon of any mod. Each uses its own set's MODELDEF for
skin, scale, offsets and the frame it rests on.

**Hand reloads, built from the cards:**
- Magazine: 37 models. Pull the empty, take a fresh one from the pouch, seat it, rack the handle or slide if the gun
  was shot dry.
- Pump: 6 shotguns. Push shells into the port one by one, work the pump after a shot.
- Break-open and revolver: 5 models (BD M79, BD revolver, BD super shotgun, the alek revolver with its speedloader,
  the alek super shotgun). Open the action, load the rounds, flick it shut.

**Seen working on mods with real reloads (0 pack script errors):**

| Mod | Weapon | Model | Reload |
|---|---|---|---|
| Generic weapons | ARifle | BD rifle | magazine, charging handle after empty |
| Generic weapons | Beretta | BD pistol | magazine, slide after empty |
| Generic weapons | Riotgun | BD shotgun | shells by hand, pump |
| Generic weapons | DoubleSG | BD super shotgun | break open, two shells, flick shut |
| Weapons of Saturn | MachineRifle | BD rifle | magazine |
| Weapons of Saturn | Beretta, 1911, MP40 | BD pistol, BW 1911, BD MP40 / SMG | magazine, slide or handle after empty |
| Weapons of Saturn | Riotgun | BD shotgun | shells by hand, pump |
| Weapons of Saturn | Coachgun | BD super shotgun | break open, shell, flick shut |

The open list, in order of priority, is in [HANDOFF.md](HANDOFF.md).

## Install

| Platform | File | Engine |
|---|---|---|
| Quest | `ModelSwapper-QUEST.pk3` | QuestZDoom 17.3 |
| PC VR | `ModelSwapper.pk3` | UZDXREMA |

Load your weapon mod first and ModelSwapper after it. On Quest the models stay in their rest pose (no animation on that
engine); everything else, reloads included, is the same.

## In game

- **Model menu:** every weapon of the loaded mod, the family ModelSwapper filed it under, and the model on it. Change
  any of them.
- **Reload Order:** the mod's own reload runs first and the hands follow (default), or the hands go first.
- **Charging Handle After Empty:** a gun reloaded from empty waits for you to rack it.
- **Pump by Hand After a Shot**, **Shells per grab**, **Shotgun Shells Per Insert**: pump-gun behaviour.

## Under the hood

**Filing.** Each weapon of the loaded mod is filed into a family (pistol, shotgun, super shotgun, rifle, chaingun,
launcher, plasma, BFG, melee, ...) by name, ammo, parent class and finally slot. Anything that takes ammo or flashes is
a gun. Helpers that never fire get no model.

**Wearing.** The weapon's model data is redirected to the chosen model's MODELDEF entry, so the engine draws that model
with its own skin, scale and offsets.

**Reloading.** `zscript/RS_ForeignReload.zs` watches every weapon that wears one of our models. When the mod enters its
Reload state, the join lets the mod's reload finish so its ammo is right, then holds the weapon while the hands do the
reload. It hands the weapon back when the hands are done. The reload type comes from the model in the hand (magazine,
pump or break-open table), not from the mod. That is how it works on mods it has never seen.

## Cards and generators

Each model lives in `cards/<set>/<gun>/` with:
- its card: measured parts, roles, states, grip, muzzle and magazine well
- the labelled mesh with every source frame
- the carved reload parts
- textures and a render sheet

The cards are measured with RSQ_WeaponDepot's `tools/hqt` and `tools/carve`. Everything the game reads is generated
from the cards:

1. `tools_gen_from_cards.py`: model definitions, donor classes, the shelf and names. `sources.lock.json` pins every
   resolution, so it runs from this repo alone.
2. `tools_kit/card_mag.py`: magazine reload rows and layers.
3. `tools_kit/card_pump.py`: pump reload rows and layers.
4. `tools_kit/card_break.py`: break-open and revolver rows and layers.
5. `tools_reload_modeldefs.py`: the few layers still taken from the 2.0 measurements.

Each one writes a `*.report.md` listing what it built and why it skipped anything.

## Build and test

- `./build.ps1` builds the PC VR pk3. `./build.ps1 -Static` builds the Quest pk3. `tools_zs_lint.py` checks the
  ZScript before packing.
- `tools_rig_check.py --donors <models> --weapon <class> --extra <mod.pk3>` puts models on a mod's weapons on the
  Linux QuestZDoom rig and makes a contact sheet.
- `tools_rig_reload.py --kind mag|pump|break --donor <model> --weapon <class> --extra <mod.pk3>` runs one full hand
  reload and prints each phase. For magazine guns, `--clicks` / `--fire-tics` shoot the gun dry first and `--rack`
  works the handle.

Test reloads on weapons that have their own Reload state. Doomablo's shotguns reload inside Fire and are not a valid
reload test.

## Layout

| Path | Contents |
|---|---|
| `zscript/` | model swapping, filing, the reload join, the menu |
| `zscript_depot/` | the hand-reload system, VR hands, generated reload tables |
| `cards/` | models, textures, cards |
| `tools_kit/` | generators and measuring kit |
| `tools_*.py` | rig, placement and mesh tools |
| `models/rsq/`, `sounds/`, `SNDINFO.ms` | VR hands and reload sounds |
| `reload_1x/` | earlier reload layers, reference for `tools_reload_modeldefs.py` |

History of earlier versions: [ARCHIVE.md](ARCHIVE.md), branch `archive/pre-cards-2026-10-31`.

## Credits

Models by the authors of the VR weapon sets, Ermac and alek among them; each set's `cards/<set>/NOTES.md` names its
makers. VR hands by Ermac. Engine lineage: teambeef QuestZDoom, PC port by Emawind84, UZDoom by Ermac, UZDoom 5.0 and
VR work by presidentkoopa.
