# ModelSwapper 1.5

ModelSwapper puts VR weapon models on the guns of any Doom weapon mod, and lets you reload them with your hands.

You keep the mod. Its weapons, ammo, damage and reload rules all stay as the mod wrote them. ModelSwapper changes what
you hold: a 3D model from one of 19 VR weapon sets, placed in your hand where that set's author placed it. When a gun
reloads, your hands do the work the model was built for, while the mod keeps the books.

## What works today

Tested on the QuestZDoom 17.3 rig (the 2026-10-31 runs). Not yet confirmed in a headset. The tree as merged on
2026-11-08 compiles, lints and packs; it has not been on the rig since (HANDOFF.md).

**Models.** 145 donors from 19 sets (`cards/`). Any of them can be chosen for any weapon of any mod. Each uses its own set's MODELDEF for
skin, scale, offsets and the frame it rests on.

**Hand reloads, built from the cards:**
- Magazine: 56 donors have a measured row (`zscript_depot/rsr/rsr_guns.ms.zs`). Pull the empty, take a fresh one from
  the pouch, seat it, rack the handle or slide if the gun was shot dry.
- Pump: 6 shotguns (Aliens M37A2, BD, BrutalWolf, Cola KS-23, MeatGrinder SSG, alek's shotgun;
  `card_pump.report.md`). Push shells into the port one by one, work the pump after a shot.
- Break-open and revolver: 7 (BD M79, BD revolver, BD super shotgun, alek's revolver with its speedloader, alek's
  super shotgun, the quad-barrel, the RoboCop M32 swing-out; `card_break.report.md`). Open the action, load the
  rounds, flick it shut.

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

| Platform | File | Engine | Built by |
|---|---|---|---|
| Quest | `ModelSwapper-QUEST.pk3` | QuestZDoom 17.3 | `python3 tools/ms/build_pk3.py` (Linux) or `./build.ps1 -Static` (Windows) |
| Quest, Project Brutality only | `pk3/ProjBrut_MS.pk3` (in the repo) | QuestZDoom 17.3 | `python3 tools/ms/build_pk3.py --pb` |
| Quest, Generic Weapons only | `pk3/GenericWeapons_MS.pk3` (in the repo; picks: `docs/sets/generic_weapons.md`) | QuestZDoom 17.3 | `python3 tools/ms/build_pk3.py --set generic_weapons` |
| Quest, Weapons of Saturn only | `pk3/WeaponsOfSaturn_MS.pk3` (in the repo; picks: `docs/sets/weapons_of_saturn.md`) | QuestZDoom 17.3 | `python3 tools/ms/build_pk3.py --set weapons_of_saturn` |
| PC VR | `ModelSwapper.pk3` | UZDXREMA | `./build.ps1` |

Load your weapon mod first and ModelSwapper after it. The two builds differ in one file: the Quest build ships
`zscript/static/RS_ForeignFork.zs`, which draws the models without the PC build's animation table, so on Quest the
models hold their rest pose today. The owner reports a way to animate them on Quest was found; it is not in this
repo yet (PLAN.md C3). Everything else, reloads included, is the same on both.

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

The cards are measured with `tools/hqt` and `tools/carve` (`docs/handbook/`); `tools/hqt/recheck_cards.py cards` re-measures every card and must report nothing changed against `tools/hqt/RECHECK_BASELINE.md` before any tool change lands. Everything the game reads is generated
from the cards:

1. `tools/ms/gen_from_cards.py`: model definitions, donor classes, the shelf and names. `sources.lock.json` pins every
   resolution, so it runs from this repo alone.
2. `tools/kit/card_mag.py`: magazine reload rows and layers.
3. `tools/kit/card_pump.py`: pump reload rows and layers.
4. `tools/kit/card_break.py`: break-open and revolver rows and layers.
5. `tools/ms/reload_modeldefs.py`: the few layers still taken from the 2.0 measurements.

Each one writes a `*.report.md` listing what it built and why it skipped anything.

## Build and test

- `./build.ps1` builds the PC VR pk3. `./build.ps1 -Static` or `tools/ms/build_pk3.py` builds the Quest pk3 (same
  contents, same gates). `tools/ms/zs_lint.py` checks the ZScript before packing; both builds run it.
- `tools/ms/rig_check.py --donors <models> --weapon <class> --extra <mod.pk3>` puts models on a mod's weapons on the
  Linux QuestZDoom rig and makes a contact sheet.
- `tools/ms/rig_reload.py --kind mag|pump|break --donor <model> --weapon <class> --extra <mod.pk3>` runs one full hand
  reload and prints each phase. For magazine guns, `--clicks` / `--fire-tics` shoot the gun dry first and `--rack`
  works the handle.

Test reloads on weapons that have their own Reload state. Doomablo's shotguns reload inside Fire and are not a valid
reload test.

## Layout

One repo holds the method and the product it feeds (RSQ_WeaponDepot merged in on 2026-11-08, every commit kept):

| Path | Contents |
|---|---|
| `zscript/` | model swapping, filing, the reload join, the menu |
| `zscript_depot/` | the hand-reload system, VR hands, generated reload tables |
| `cards/` | the card well: one folder per mesh (labelled MD3, card, carved parts, textures, sheet) |
| `tools/hqt/` | **the measuring pipeline** (High Quality Tools): `md3label`, `namedcard`, `blendcard`, `statephase`, `batch`, `render`, `motion`, `obj2md3`, and `recheck_cards.py`, the regression gate that re-measures every card |
| `tools/carve/` | carving a part out of a welded mesh (`md3_carve_surface --half / --like`) |
| `tools/rig/` | the QuestZDoom 17.3 test rig for Linux (`PINS` pins the one engine), its drivers and probe |
| `tools/int20_rig/`, `tools/scope3x/` | whole-pack checks on the rig; the live 3x scope rig |
| `tools/handfit/` | the FBX hand fitter and the one method (gun to hand, everything on the gun moves with it) |
| `tools/kit/` | ModelSwapper's generators (`card_mag`, `card_pump`, `card_break`, `gen_rsb`, `gen_rsr`, ...) and format converters; the measuring tools in here are forwarders to `tools/hqt` |
| `tools/ms/` | ModelSwapper's own scripts: `gen_from_cards`, `build_pk3`, `zs_lint`, `rig_check`, `rig_reload`, the mod patches |
| `tools/depot.py` | every path a tool uses, repo-relative or an environment variable (`docs/handbook/03_toolset.md`) |
| `docs/handbook/` | how VR weapon mechanics are built on QuestZDoom 17.3, with the tools above |
| `docs/depot/` | the Depot's own README, PLAN, HANDOFF and rules as they were at the merge |
| `sources/pbvp_v2/` | Project Brutality Voxel Patch v2, verbatim (credit required) |
| `models/rsq/`, `sounds/`, `SNDINFO.ms` | VR hands and reload sounds |
| `reload_1x/` | earlier reload layers, reference for `tools/ms/reload_modeldefs.py` |

**Two tiers.** The finished, hand-built VR weapon sets are their own repos ([RS_Brutal22WeaponsQ](https://github.com/presidentkoopa/RS_Brutal22WeaponsQ),
[RS_Aliens_VR-WeaponsQ](https://github.com/presidentkoopa/RS_Aliens_VR-WeaponsQ),
[RSQ_RustedLegacy](https://github.com/presidentkoopa/RSQ_RustedLegacy), unfinished). ModelSwapper is the coverage tier: any of the hundreds of Doom mods gets real meshes and hand reloads by the
same method, measured with the same tools, without a set being built for it. The proven BD22 meshes feed it as the
`BD_*` donors.

History of earlier versions: [ARCHIVE.md](ARCHIVE.md), branch `archive/pre-cards-2026-10-31`. The Depot's history is in this repo's log (183 commits, merged 2026-11-08); its sets are on RSQ_WeaponDepot `main`, read-only.

## Credits

Models by the authors of the VR weapon sets, Ermac and alek among them; each set's `cards/<set>/NOTES.md` names its
makers. VR hands by Ermac. Engine lineage: teambeef QuestZDoom, PC port by Emawind84, UZDoom by Ermac, UZDoom 5.0 and
VR work by presidentkoopa.
