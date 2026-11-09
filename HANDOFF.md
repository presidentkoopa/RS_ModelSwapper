# THE MERGE (2026-11-08) -- read this block first

RSQ_WeaponDepot is in this repo now (`git log` has its 183 commits; `docs/depot/` has its README, PLAN, HANDOFF and
rules as they were). What the owner trusts (2026-11-08): **the toolset, the test rig with its tools, and the cards
that came out of the Oct-31 batch-carding.** Everything else in either repo is "compiled, not re-verified".

## Done (measured)
- `tools/hqt/`: one version of each measuring tool. Base = the Depot's copy (the one that carded all 19 sets on
  2026-10-31). Onto it, ModelSwapper's `tools_kit` fixes of 2026-10-24/25: `namedcard` (Blender primitive names are
  not roles; `clip` is a magazine; a `mag_cover` is not), `obj2md3 --stable-verts` (same vertex count every frame),
  `motion -b`, `render` (20 colours, wrapping legend; VIEW/BODY kept), `md3label --carve-frame`, `--split-body`
  (opt-in), body = biggest surface not --assign'd a MOVING role, and the magazine labeller for any gun whose magazine
  travels > 5 units (not only `--archetype pistol_mag`).
- `tools/hqt/recheck_cards.py`: rebuilds each card's md3label command from the card and re-measures. The Depot's
  md3label on the 148 cards: 127 MATCH, 21 DIFF, every DIFF explained (owner hand-edits to muzzle / phases, carves made
  with tools/carve, static meshes carded by another writer) -- `tools/hqt/RECHECK_BASELINE.md`. The merged md3label
  against that baseline: 6 cards change, all one named fix (BD assault shotgun, rifle, RPG and the two Chex zorchers
  gain `mag_out` / `mag_in`; the CW nailgun, carded with ModelSwapper's copy, now matches). The cards themselves were
  not rewritten (PLAN C1).
- `tools/kit/` (was `tools_kit/`) and `tools/ms/` (was `tools_*.py`): moved, every path repo-relative; the 14 measuring
  tools `tools_kit` duplicated are forwarders to the one copy. `tools/ms/zs_lint.py`: 11 files, 0 problems.
  `tools/ms/build_pk3.py`: ModelSwapper-QUEST.pk3 built from the merged tree, 850 entries, every gate passed (0
  backslash entries, 0 static world models, 2834 asset refs resolved, 145 donors, 0 duplicate, 0 unstubbed). Rig not
  run this session (no engine here).
- `tools/depot.py`: `RSQ_SET` defaults to `../rs_brutal22weaponsq` (the set is its own repo), `RSQ_RL` to
  `../rsq_rustedlegacy`, `RSQ_CARDS` = `cards/`. `tools/check_plan.py` knows the merged layout; hooks via
  `sh tools/install_hooks.sh`; `PLAN.md` is the plan (current step M1).

## Done (measured), continued
- RSQ_WeaponDepot `main`: README points here (commit e3266f6). The owner archives the repo in GitHub settings.
- Rusted Legacy is its own repo: https://github.com/presidentkoopa/RSQ_RustedLegacy (9 commits: the eight S4
  commits by `git subtree split` + one that repoints its two tools at `../rs_modelswapper/tools`, or `RSQ_TOOLS`).

- H1 step 1 (2026-11-08): `tools/handfit/blender/` -- `pose_library.json` (29 BD22 holds via the kit's own FK + the
  FBX take's 5 poses x 2 hands), `handfit_addon.py`, `test_brutalpistol.py`, README. The non-Blender math is checked
  against the kit to 0.000000 (gun chain, flu_to_md3, six-number round trip, md3 I/O); the library's BrutalPistol pose
  lands on the shipped `fbx_b1_R.md3` frame at mean 0.0085 / max 0.240 md3 units. The Blender calls are NOT run
  (no Blender here): written, not verified.

## Not done
- H1: `blender -b --python tools/handfit/blender/test_brutalpistol.py -- --bd22 <RS_Brutal22WeaponsQ>` on the owner's
  machine. Until it passes, Handfit is not working.
- Anything on the rig: this session had no engine. First rig run of the merged tree is the next thing to do.

## Open
- `gen_from_cards.py` lock-only run no longer reproduces `main` (PLAN C2): it drops the hand-added
  `smg|MS_CW_Nailgun` shelf row, re-sorts, and dies at its report on a donor with a block but no source file. Its
  output was reverted; only `PREFIX` (quad=QD, gmod_cw=CW) and `WELL_DIR.get()` were added so it runs past the two
  2026-11-03 sets.
- Quest animated meshes: the owner says the method was found; not in this repo (PLAN C3).
- `tools/hqt/compcheck.sh` takes REMA_BIN / REMA_IWAD / REMA_INI / REMA_BASE from the environment now (was hardcoded).

# M4 -- Golden Souls: Super Mario Doom enemies + high jump patch (2026-11-08, RIG-RUN)

Owner 23:30: "have a separate agent make a patch for this for GoldenSouls 1 and 2. I want the enemies from this, and
the high jump." Full account: `docs/sets/golden_souls_smd_enemies.md`.
## Done (measured)
- The SDMLITE pack inventoried: 1893 entries, NO code of any kind (no DECORATE / ZScript / MAPINFO / ACS); its enemies
  are the stock Doom monsters redrawn under stock sprite names + stock-named sound lumps + a SNDINFO. Every stock monster
  frame present (checked against the engine's own state tables). GS1 / GS2 map THINGS parsed: both place Imp, Demon,
  Caco, Knight, Baron, Revenant, Fatso (GS1 also Arachnotron, Spider, Cyber; GS2 Pain Elemental) through `<Class>New`
  subclasses that keep stock sprite names -> one sprite-level patch serves both mods, no actor code.
- `pk3/GoldenSouls_SMD_Enemies.pk3`: 1031 entries, 6.2 MB (939 sprites, 83 sounds, monster SNDINFO + cast/obituary
  LANGUAGE verbatim from the pack, the jump code). `tools/ms/make_gs_smd_patch.py` builds it from `sources/smd_lite/`
  (+ PROVENANCE.md, CREDITS.txt) and `tools/ms/gs_smd_patch/`; gates: every named sound packed, every monster sprite,
  no backslash, no lump shared with GoldenSouls1_MS.pk3 (so either load order works). zs_lint 0 problems.
- The jump: `SMD_HighJump` Inventory given by an EventHandler (PlayerEntered / Respawned / WorldLoaded), JumpZ from
  server cvar `smd_jumpz` (default 15 = GS2's own, parsed; GS1's is 8.2), class default back when `smd_highjump` off.
  GS's player classes untouched. The pack has NO jump number to measure: 15 is GS2's, said so in the doc and the menu.
- RIG (doom2.wad from the owner's upload, QuestZDoom 17.3): zero script errors on GS1 -> patch, GS1 -> patch -> MS,
  GS1 -> MS -> patch, GS2 -> patch (init and in-map). Probe lines: TROOA1 and DSBGSIT1 resolve to the patch, FIREA0 to
  the IWAD; GS1 MAP01 DoomImpNew draws TROO, DemonNew SARG, CacodemonNew HEAD, HellKnightNew BOS2; frames in
  `docs/sets/smd_enemies/`. JumpZ 15.00 from tic 1 in both mods; off -> 8.20 (GS1) / 15.00 (GS2); `smd_jumpz 30` ->
  30.00. A jump measured: apex 120.0 units at JumpZ 15, 37.8 at 8.2.
- Found on the rig, fixed: the EventHandler needed `MAPINFO GameInfo AddEventHandlers` or it never ran.
## Not done
- Headset. Sounds heard (`-nosound`; lump resolution only). Spider / Cyber / Arachnotron / Pain Elemental seen drawn in
  a GS map (sprite-checked only).
## Open
- Jump height is GS2's 15, not SMD's (no code in LITE). The Mario `DSJUMP` sound and the Mario player sprite were left
  out as taste calls; one-liners listed in the doc.

# M3 -- Golden Souls 1 set (2026-11-08, NOT rig-run)

Owner 19:41: "theorize on sets for these, but only start with the first GS". GS1 built the M2 way, GS2 theorised in
docs/sets/golden_souls_2.md.
## Done (measured)
- docs/sets/golden_souls_1.md: 8 weapons from dec_weps.dec, a donor each, the reason, the hand row. Profile rows in
  RS_ForeignModels.zs (Fist2 shared with GS2), MENUDEF.gs1 (no pump row: no pump gun), build_pk3 SETS entry.
  pk3/GoldenSouls1_MS.pk3: 161 entries, 19.7 MB, every gate passed; lint 0.
- Hands: BD_Revolver (gun B + cup A) and CW_Nailgun (gun F + support B on its measured magwell) fitted by
  handfit_donors.py as slots 80-81, sheets looked at (docs/sets/hands). PD_Cannon fit REFUSED (hand inside the
  barrel): the Cannon goes without. Coverage 7/8. SET_golden_souls_1.png has every weapon.
- handfit_donors.py --write keeps the earlier fits' SlotForDonor lines (it rewrote the block before: the M2 lines
  75-79 were lost for one run and put back; the arrays were never wrong).
## Open
- BD_Railgun rest frame: the owner saw the gun tilted on the sheet. Measured: the OG Ready frame the generator took (2)
  is the last RAISE frame (body 12 units low, pitched -9 deg); the card's idle (3) is level. modeldef + the SHELF row
  say 3 now, gen_from_cards has REST_OVERRIDE for it, the hands re-fitted on frame 3 (slot 83; a re-fit replaces its
  ledger line, the old slot stays unused). Every other donor of the three sets checked: rest frame == card idle, or
  the same pose.
- RailBow: BD_Railgun re-fitted on the owner's ask (19:55 "support hand on rifle"): slot 82, gun hand on the grip + support
  under the forend at the card's support x; the handfit_donors block now sits FIRST in SlotForDonor so a fit beats an
  alias or an old row (the renderer reads it the same way).
- GS2 is theory only; three fits would be new (blunderbuss, crossbow or nailgun for Cupid, the whip or none).

# M2 -- Generic Weapons + Weapons of Saturn sets (2026-11-08, branch `set-profiles`, NOT rig-run)

Owner: "spin up mesh sets for these two weapon sets ... hands on guns". No engine in this session: everything below
is parsed, measured against the tables, and gate-checked; nothing ran. Picks and the mod inventories:
`docs/sets/generic_weapons.md`, `docs/sets/weapons_of_saturn.md`.

## Done (measured)
- Inventories from the mods' own DECORATE (`python3 -I` on the unpacked zips): Generic Weapons 10 weapons (8 reload:
  6 magazine incl. the minigun's box, 1 pump, 1 break), Weapons of Saturn 12 weapons (10 reload: 8 magazine incl.
  belt box and the six-round Saturn V, 1 pump, 1 break). Every reload kind cites the mod's line.
- Donors: 19 new `ProfileDonor` rows (`zscript/RS_ForeignModels.zs`), no PB row touched. The 8 pairings seen working
  on the rig stay. Every reloading weapon wears a donor with a measured row of its kind: Generic 10 donors (BD fist,
  VP chainsaw, BD pistol / rifle / shotgun / SSG, VP minigun, BD RPG / plasma, HX Nuker); Saturn 12 (the same minus
  VP chainsaw, plus BD chainsaw, BD MP40, BW 1911). Generic follows the owner's vanilla-look rule: VP first; the
  VP RPG and plasma rifle ARE the BD meshes (`reload_names.json`: exact), the VP minigun is the only chaingun with a
  row. Not switched: Beretta / ARifle / Riotgun / DoubleSG to VP pistol / M16 / shotgun / SSG -- those have reload
  rows but no hand row, so the owner's switch condition is not met.
- `tools/ms/build_pk3.py --set <name>`: a SETS table (pk3 name, the profile rows that are the set's -- `PB_\w+` for
  PB, explicit class lists for the two unprefixed mods -- and the menu lump). `--pb` = `--set pb`: 260 entries,
  every entry's size and CRC unchanged except `zscript/RS_ForeignModels.zs` (the new rows). A listed class with no
  profile row fails the build. New gate in `verify`: every Option's OptionValue and every Submenu target is defined
  in a packed MENUDEF lump, none defined twice (checked negative on a fake lump).
- `MENUDEF.gnrc` / `MENUDEF.saturn` (Options > "Generic Weapons VR" / "Weapons of Saturn VR"): modelled on
  MENUDEF.pb, shorter; every row an existing cvar in quest/CVARINFO (rs_foreignmodels, rsr_reload, ms_mod_first,
  rsr_grab_with, ms_hand_pump, ms_charge_dry, rsq_hands, ms_off_fist), RSFM_Picker, `netevent rs-fm-forget-picks`,
  one per-set OptionValue (MSGNRC_ReloadMode / MSSATURN_ReloadMode). Shipped only by their own `--set`.
- `pk3/GenericWeapons_MS.pk3` 172 entries 17.8 MB; `pk3/WeaponsOfSaturn_MS.pk3` 186 entries 27.9 MB; both every
  gate (0 backslash, 0 world models, 360 / 472 asset refs resolved, 0 duplicate, 0 unstubbed, menus clean).
  `zs_lint`: 11 files, 0 problems. Plain Quest build still 850 entries, 182.4 MB, clean. `check_plan`: ok.

## Not done
- Rig: not run (no engine). First thing: doom2 -> mod -> set pk3, zero script errors, then each reload kind on the
  rig (`tools/ms/rig_reload.py --extra <mod.pk3>`), the Saturn V six-round load and both miniguns' box reload have
  never been seen on a model.
- Hands on guns: the per-gun FBX gun-hand poses are PLAN H1 / Handfit (Blender), not this item.

## Open
- Hands (2026-11-08, the owner's corrections at 19:26 folded in): `tools/ms/handfit_donors.py` (handfit_cards.py's
  ICP, inputs from `modeldef` + the card; Ermac's full hands from RSQ_RustedLegacy `src/models/hand`, the cut frames
  ModelSwapper ships match them 0.0000; gripping faces `tools/kit/gripregions.json` from `tools/hqt/gripmeasure.py`).
  Slots 75-79, every sheet looked at (`docs/sets/hands/`): BD_Shotgun (gun C + support B on the pump), BD_Ssg (gun C +
  support B UNDER THE BARRELS midway, from the barrel surface), BW_1911 (gun B + cup A), HX_Nuker (gun F, support off:
  placeholder point), BD_Minigun (gun F on the rear grip + support E, the fist on the card's handlebar). Refused: the
  VP minigun (card grip on the ammo box) and the VP chainsaw (owner: a mess); both sets now wear BD's minigun (no
  reload row: the mod's own reload runs) and BD's chainsaw with no hand. Coverage: Generic 9/10, Saturn 10/12.
  Rig only. Mesh identity vs `archive/pre-cards-2026-10-31` measured (read only): bd_ssg / shotgun / chainsaw == the
  1.x BD meshes 0.0000; the vplus hud meshes are shifted copies drawn differently (rows not transferable).
- Still without a hand: the two chainsaws (owner's call: none until Handfit in Blender, PLAN H1).
- BFG9K / TITAN wear MS_HX_Nuker because it is the only bfg-shelf donor with a reload row; the vanilla-look MG_Bfg
  and BD_Bfg have none. Owner's call if the look matters more (the mod's own reload would then run).
- The profile keys carry no mod prefix (`Beretta`, `Minigun`, `1911`...): another mod spelling a class the same way
  wears the same donor. Harmless as far as seen (the picks fit the names), noted.

# TABLED (owner, 2026-11-03 09:04) -- PB set: reload feel

Owner tested ProjBrut_MS.pk3 himself. Wanted: a magazine / clip IN THE HAND during the reload, and the meshes
animating (slide locked back when empty, etc.). NEXT STEP IS THE OWNER'S: he reviews all 29 meshes; if they look good,
a PB VR weaponset becomes its own project (not before). His queue first: UBQS, BD22 hotfix, PunchOut and AliensWeapons
releases, then Zelda and Castlevania, maybe Excitebike.
Also open from the rig runs (rig only, not headset): PB_Pistol's reload joined magazine slot 104 (MS_VP_Pistol's row)
where the profile says MS_BD_Pistol (slot 55) -- check which donor is actually worn. The rig frames never clearly
showed a mesh in hand (mostly PB's sprite): unproven. PB plays an opening sequence; rig scripts need ~420 tics of
settle (tools/ms/rig_reload.py --settle was tried, not committed).

# ModelSwapper 2.0 scoping + M32 swing-out (2026-11-03) -- read this block first

**Not rig-run.** This session had no rig (/home/claude/rig absent, no engine): everything below is mesh- and
generator-checked only, and tools_zs_lint is clean on the touched files. Uncommitted until the owner says.

### 2.0 = a curated ~30-mesh set, Project Brutality as the coverage test (owner)
Rule (owner): PB decides what reloads; every mesh on a PB weapon that reloads must have a MEASURED reload row.
PB profile picks (class -> donor), all with rows: Pistol BD_Pistol, Revolver BD_Revolver, Deagle VP_Pistol (alek),
SMG BD_Smg, MP40 BD_Mp40, Shotgun BD_Shotgun, SSG BD_Ssg, AutoShotgun BD_Assaultshotgun, QuadSG VP_Ssg (until the
quad lands), DMR BD_Rifle (DMR fires every 5 tics: not the Ruger), Carbine VP_M16, LMG BW_Bar, MG42 BW_Mg42,
SuperGL **RC_M32** (below), RL BD_Rpg, M1 BD_Plasma, M2 MG_Bolter, PulseCannon Cola_Particlegun, DemonTech HX_Nuker
(eyeball), Cryo HX_Cryogun, Flamer BD_Flamethrower, Railgun BD_Railgun. No PB reload: Minigun BD_Minigun, BFG BD_Bfg,
Unmaker BD_Unmaker; melee BD_Fist / BD_Axe / BD_Chainsaw. **Nailgun: open** (owner is sourcing a mesh).
DONE (2026-11-03, later): the table is the PB profile in RS_ForeignScanner.ProfileDonor / ProfileFamily
(RS_ForeignModels.zs): a profile donor sets the weapon's family AND pick (Demon-Tech wears the bfg-shelf HX_Nuker), the
player's menu pick still wins. QuadSG -> MS_QD_Quad, Nailgun -> MS_CW_Nailgun (both below, now in the repo). The five
TokenArchetype misses are fixed (sawn-off / double-barrel / quad-barrel -> supershotgun; nailgun -> smg; cryo,
pulsecannon, dark matter, demon-tech -> plasma; bare "pulse" deliberately NOT, the Aliens M41A is ballistic).
NEXT: the PB weaponset spin-out (where it lives is the owner's call: WeaponDepot vs ModelSwapper, to discuss), then
a rig pass on PB: draw check + every reload kind, two reloads in a row.

### RC M32: authored swing-out reload (this session)
The mesh never reloaded (sheet_top frames 0/18/27 identical; its "reload" clip 7-36 was fire cycles 2-6). Its
magazine row 102 came from the rear plate being labelled `mag`: the hand would have pulled the whole cylinder off.
- cards/robocop/m32/rc_m32.md3: frames 0-36 untouched, 37-59 appended (swing 38-43, rounds out 44-47, in 49-52,
  close 53-58). Crane axis x-parallel through yz (12, -17), 100 deg: the smallest arm that clears all six chambers
  from behind. Six chambers MEASURED on the rear face (R 9.2 at 30+60k deg, bore r 3.72). Six rounds added as
  surfaces 9-14 = BD M79 round x1.9, skin rc_m32_round_m79.png (copy of M79.png). Built by m32_frames.py (session
  tools, not in the repo; the card's `source` block records every number).
- card: surf 2 renamed mag -> plate, surf 5 -> cyl, rounds round..round6. card_break: break slot 4 (VP_Rev and
  VP_Ssg renumber to 5, 6), hinge fit 0.01 cm, open 100 deg at frame 52, 6 chambers.
- card_mag rerun: no longer builds the M32 (MODELDEF.cards QWP* layers, foley aliases, NoMag token gone). Its
  SlotForDonor line removed by hand from rsr_guns.ms.zs (regen keeps unrebuilt rows; RS_ForeignReload.zs:415 only
  reaches the break system when the mag slot is 0). The case-102 arms are now unreachable data.
- modeldef: SurfaceSkin 9-14; shelf frameCount 37 -> 60; clip `reload` 7-36 -> 38-58.
- To check on the rig: `tools/ms/rig_reload.py --kind break --donor MS_RC_M32` against PB's SuperGL (Reload state),
  two reloads in a row (see open item 1).

### Added to the repo this session (2026-11-03), not rig-run
- MS_QD_Quad (cards/quad/quad): owner's quad FBX; hinge measured from the lug pin hole, 45 deg open authored, 2x2
  shell carve; break slot 4, fit res 0.01 cm. Lock riding the barrel is an assumption: owner to confirm.
- MS_CW_Nailgun (cards/gmod_cw/nailgun): owner's Garry's Mod upload (Source MDL); its own reload animation decoded
  and skinned in the receiver frame (40 frames); magazine row 106. NOTES.md in the folder.
- Session tools that read these sources (fbxread/fbx2obj/quad_frames, srcmdl/srcanim/src_frames/vtf2png,
  m32_frames, shade) are NOT in the repo yet: where they go is part of the WeaponDepot/ModelSwapper talk.

# ModelSwapper 1.5 handoff (2026-10-31, 10:00)

RS_ModelSwapper `main` (GitHub moved it to `presidentkoopa/RS_ModelSwapper`; the old URL still redirects).
Everything below is committed and pushed. Nothing in flight. The owner's E: copy has not pulled any of today's commits.
All results are **rig only, not headset-confirmed** (QuestZDoom 17.3 Linux rig, /home/claude/rig, real doom2.wad).

## Goal (owner)
Every carded mesh selectable as a donor on any mod's weapons, placed by its set's own hand-authored MODELDEF, and
reloading by hand where it can reload. The cards are the single source: placement, reload rows and layers are all
generated from them; nothing is hand-wired.

## Test mods (owner, 2026-10-31)
- **Use mods that really reload.** Generic weapons (`li-gnrcwpn.zip`, unpacked and zipped to `/tmp/claude-0/gnrc.pk3`)
  and Weapons of Saturn (`weapons_of_saturn.pk3`, `/tmp/claude-0/wos.pk3`). Both have Reload states on every gun.
- **Do not reload-test on Doomablo.** Its SSG and shotgun reload inside Fire (no Reload label), so the join never gets
  a reload. Doomablo is fine for the draw / switching checks only.
- Reload guns with Reload states: generic `Beretta` `Riotgun` (pump) `DoubleSG` (break) `ARifle` `Minigun` `Rlauncher`
  `PlasRifle`; WoS `Beretta` `1911` `MP40` `MachineRifle` `Riotgun` (pump) `Coachgun` (break) `Minigun` `NovaRifle`.

## Done (measured on the rig)
| Reload | Mod / weapon | Donor | Result | Commit |
|---|---|---|---|---|
| Magazine | generic ARifle | MS_BD_Rifle | IDLE>EMPTY>DROP>EMPTY>CARRY>INSERT>SEATED>DONE>IDLE | 039769c |
| Magazine | WoS MachineRifle | MS_BD_Rifle | same full cycle (after the reserve fix) | e24fe2e |
| Magazine + handle (shot dry) | generic ARifle; generic + WoS Beretta; WoS 1911; WoS MP40 | BD rifle, BD pistol, BW 1911, BD MP40, BD SMG | ...SEATED>CHARGE>PULL>RELEASED>DONE>IDLE | 7a62b5f |
| Pump | generic Riotgun | MS_BD_Shotgun | 2 shells into the port, pump stroke after the shot | e24fe2e |
| Pump | WoS Riotgun | MS_BD_Shotgun | 2 shells home, stroke done | e24fe2e |
| Pump (Ermac shell) | Doomablo RwShotgun | MS_MG_Ssg | 2 shells, 2 strokes | 4ffcb67 |
| Break | generic DoubleSG | MS_BD_Ssg | open, 2 shells, flick shut, gun drawn in the hand | 2edc09c |
| Break | WoS Coachgun | MS_BD_Ssg | open, 1 shell (one barrel fired), flick shut | 2edc09c |
All with 0 pack errors. Frames: `/home/claude/shots/rigreload_<tag>_<donor>/`.

### Reload rows generated from the cards (today)
- **Magazine** `tools/kit/card_mag.py` -> 2.0's `regen_rows` (unchanged chain: card2quest -> genpack -> gen_rsr).
  37 donors built. Held (keep the mod's reload): `MS_CX_Lazdevice` (its Chex placement puts the cell 52 cm ahead of
  the controller), `MS_RC_Ksg` (no MODELDEF anywhere: struck from the Robocop set, so its placement is a default, not
  measured; needs a real placement first). Writes `MODELDEF.cards` and `zscript_depot/rsr/rsr_guns.ms.zs`.
- **Break / revolver** `tools/kit/card_break.py` -> 2.0's `gen_rsb` (patched: per-surface skins, card-hidden parts,
  any set name). 5 donors: BD M79, BD revolver, BD SSG, V+ (alek) revolver with speedloader (home frame 26 measured =
  2.0's hand value), V+ SSG; hinge fits 0.03 cm. Left out: Cola revolver (rounds are one surface), Robocop M32 (no
  hinge on its card), UV SSG D4 and zblood sawed-off (no round on the card). Writes `MODELDEF.rsb`, `rsb_guns.zs`.
- **Pump** `tools/kit/card_pump.py` -> `gen_pump`. 6 slots: AE M37A2, BD shotgun, BW trench gun, Cola KS-23, MG SSG
  (Ermac shell), VP shotgun. Writes `MODELDEF.rsrpump`, `rsr_pump_guns.zs`, `rsp_rack.ms.zs`.
- `tools/ms/reload_modeldefs.py` now only writes `MODELDEF.cards2x`: 2.0-measured layers for the 5 donors card_mag
  does not build (BW MG42 / Garand / Kar98 / trench gun, zblood sawed-off).
- Order to regenerate: `card_mag.py`, `card_pump.py`, `card_break.py`, `tools/ms/reload_modeldefs.py`.

### Engine-side fixes today (ZScript)
- `CannotFire`: a weapon with ammo or a muzzle flash is a gun. The NextState-only walk had ruled the generic DoubleSG
  (all frames behind A_Jump branches) "not a gun", so it never got a model and the engine drew its 2D sprite.
- `vreload.zs CanTakeMag`: with "mod's reload first" the mod has already emptied its reserve into the gun; the hand
  no longer refuses the magazine for an empty reserve (WoS MachineRifle stalled at EMPTY).
- `regen_rows` keeps sprite registrations of rows it does not rebuild (87 were being dropped).
- See-through skin `rsr_clear.png` placed in every layer folder by the generators; reload foley (`SNDINFO.ms` +
  `sounds/`, from 2.0) packed by build.ps1 and tools_rig_check.

### Rig tools
- `tools/ms/rig_reload.py --kind mag|pump|break --donor X --weapon Y --extra <mod.pk3>`; mag adds `--fire-tics N`
  (hold), `--clicks N` (semi-auto presses), `--rack` (work the charging handle by hand). Break uses the test probe.
- `tools/ms/rig_check.py --donors ... --weapon ... --extra ...` (draw check; give ammo first for guns that need it).

## Not done / open, in order
0. **Next test mod (owner, 2026-10-31): Project Brutality, the big one** -- https://github.com/pa1nki113r/Project_Brutality
   (build its pk3 from the repo; run the draw check and every reload kind against its weapons' own Reload states).
1. **2.0 bug: SSG and M79 glitch on the second reload.** Not yet reproduced or worked on. Next task.
2. **Charging handle "stick" (2.0 note):** did not reproduce on 6 runs (above). Possible cause the owner may mean:
   after an empty reload the gun waits for the handle and will not fire until racked, with no cue. Owner to say if a
   timeout or trigger-press fallback is wanted.
3. **Break-action on mods that reload inside Fire** (Doomablo SSG): the join has no fire-path for break guns.
4. More reload guns on the two test mods with family-matched donors (pistols done; revolver, M79/launcher, minigun,
   plasma where a donor fits).
5. KSG placement (no OG MODELDEF), Lazdevice reach; Cola revolver / UV SSG D4 / sawed-off / M32 have no measured round
   or hinge on their cards.
6. Pump leftovers: RC / UV D4 ports untrusted, BW trench gun pump unchecked, Cola KS-23 pump point not measured (-1).
7. Gun-hand poses for the 1.5 donors (the gun hand barely shows on grips) -- owner: not now ("no hand stuff").
8. A full rig pass on all donors, then a pk3 to the owner for the headset.
9. Zion and Samsara: tabled, do not touch.

## Rules that bit today
- Keep the owner informed: one line when something blocks, before digging. Answer questions directly.
- Test reloads only on weapons that really reload; never substitute a different weapon class to "test the rows".
- Unverified changes are not commits; rig-shown changes are.

## 2026-11-09 00:25 Generic Weapons set: the VR HAND RELOAD on the rig (owner: "meshes survive firing and manual reloading")
Real QuestZDoom 17.3 (tools/rig/bin/qz), OpenXR path, doom2 -> li-gnrcwpn -> pk3/GenericWeapons_MS.pk3 -> tools/rig/probe_ms,
god, `rsr_reload 1`, off hand driven through the kit's drivers re-pointed at the set: `tools/rig/msmags.py` (magazines,
mags.py's method), `tools/rig/msload.py` (pump and break, pump.py/brk.py's). Logs: tools/rig/runs/gnrc_*.log (gitignored).
- MAGAZINES Beretta, ARifle, Rlauncher, PlasRifle, BFG9K: `IDLE>EMPTY>DROP>CARRY>INSERT>SEATED>DONE>IDLE` on every one;
  the weapon layer stayed on the MS anchor sprite for every tic of the reload (144-174 tics each) EXCEPT one tic at
  DONE->IDLE where it reads the mod's own 2D sprite before the pin returns (all five, same tic): a one-frame flash if the
  renderer catches it. The only defect found.
- PUMP Riotgun: two shells taken from the hand and pushed home (`LOAD/CARRY -> INSERT -> shell 1 home`, `shell 2 home`);
  then, with the off hand ON the pump before the shot (RS_ForeignReload.ShotWatch's rule: the gun is held at the mod's
  pump point only if the hand is already there), the stroke by hand: `the hand is on the pump (grab): it pumps` ->
  `pump at the back` -> `pump forward: stroke done` -> `ready`. Anchor sprite held throughout (spr 6).
- BREAK DoubleSG: `IDLE>OPENING` (ejected 2) `>OPEN`, hand `FREE>CARRY>INSERT`, `chamber 0 loaded`, gun hand flick
  `467 deg/s about the hinge` -> `CLOSING>DONE>IDLE`, `loaded 2 this reload`. Anchor sprite held (spr 950, 79 tics).
- Also measured (not asked for, recorded once): meshes held through FIRING on every gun of Generic (10), Saturn (12) and
  GS1 (8); Generic's chainsaw fell to its 2D sprite for 3 tics at the start of its fire animation. Saturn's seven
  magazine guns did the full hand cycle too before the owner said stop. GS1 hand reloads NOT run (owner: "if it works in
  GNRC it works everywhere else").
- Rig facts: the engine reads/writes bin/config/qzdoom.ini relative to its cwd and ignores -config (the drivers restore
  it from git around every run); a `+reload` from a ZScript WorldTick is too late for P_CheckWeaponButtons (console
  `+reload`/`-reload` works); tools/rig/probe is BD22-only (FiredPrimary, RSQ_Flash, the axe): probe_ms is the MS cut.
