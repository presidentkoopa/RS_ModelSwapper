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
- **Magazine** `tools_kit/card_mag.py` -> 2.0's `regen_rows` (unchanged chain: card2quest -> genpack -> gen_rsr).
  37 donors built. Held (keep the mod's reload): `MS_CX_Lazdevice` (its Chex placement puts the cell 52 cm ahead of
  the controller), `MS_RC_Ksg` (no MODELDEF anywhere: struck from the Robocop set, so its placement is a default, not
  measured; needs a real placement first). Writes `MODELDEF.cards` and `zscript_depot/rsr/rsr_guns.ms.zs`.
- **Break / revolver** `tools_kit/card_break.py` -> 2.0's `gen_rsb` (patched: per-surface skins, card-hidden parts,
  any set name). 5 donors: BD M79, BD revolver, BD SSG, V+ (alek) revolver with speedloader (home frame 26 measured =
  2.0's hand value), V+ SSG; hinge fits 0.03 cm. Left out: Cola revolver (rounds are one surface), Robocop M32 (no
  hinge on its card), UV SSG D4 and zblood sawed-off (no round on the card). Writes `MODELDEF.rsb`, `rsb_guns.zs`.
- **Pump** `tools_kit/card_pump.py` -> `gen_pump`. 6 slots: AE M37A2, BD shotgun, BW trench gun, Cola KS-23, MG SSG
  (Ermac shell), VP shotgun. Writes `MODELDEF.rsrpump`, `rsr_pump_guns.zs`, `rsp_rack.ms.zs`.
- `tools_reload_modeldefs.py` now only writes `MODELDEF.cards2x`: 2.0-measured layers for the 5 donors card_mag
  does not build (BW MG42 / Garand / Kar98 / trench gun, zblood sawed-off).
- Order to regenerate: `card_mag.py`, `card_pump.py`, `card_break.py`, `tools_reload_modeldefs.py`.

### Engine-side fixes today (ZScript)
- `CannotFire`: a weapon with ammo or a muzzle flash is a gun. The NextState-only walk had ruled the generic DoubleSG
  (all frames behind A_Jump branches) "not a gun", so it never got a model and the engine drew its 2D sprite.
- `vreload.zs CanTakeMag`: with "mod's reload first" the mod has already emptied its reserve into the gun; the hand
  no longer refuses the magazine for an empty reserve (WoS MachineRifle stalled at EMPTY).
- `regen_rows` keeps sprite registrations of rows it does not rebuild (87 were being dropped).
- See-through skin `rsr_clear.png` placed in every layer folder by the generators; reload foley (`SNDINFO.ms` +
  `sounds/`, from 2.0) packed by build.ps1 and tools_rig_check.

### Rig tools
- `tools_rig_reload.py --kind mag|pump|break --donor X --weapon Y --extra <mod.pk3>`; mag adds `--fire-tics N`
  (hold), `--clicks N` (semi-auto presses), `--rack` (work the charging handle by hand). Break uses the test probe.
- `tools_rig_check.py --donors ... --weapon ... --extra ...` (draw check; give ammo first for guns that need it).

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
