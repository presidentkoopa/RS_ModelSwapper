# Weapons of Saturn set (PLAN M2, 2026-11-08)

Mod: "Weapons of Saturn" (`weapons_of_saturn.pk3`, pure DECORATE, `ACTORS/*.txt`). A modern-arms set (Beretta, 1911,
MP40, machine rifle, riot gun, coach gun, rotary cannon), so the look rule is the brief's: modern meshes, BD first for
their BD22 holds; the pairings seen working on the rig (README "Seen working") stay.

Set pk3: `pk3/WeaponsOfSaturn_MS.pk3` (`python3 tools/ms/build_pk3.py --set weapons_of_saturn`), menu
`MENUDEF.saturn` (Options > "Weapons of Saturn VR"). Load order: doom2 -> Weapons of Saturn -> WeaponsOfSaturn_MS.pk3.
**Not rig-run** (no engine in the session that made it).

## Inventory (parsed from the mod's DECORATE; `python3 -I` on the unpacked pk3)

In this mod ammo 1 is the RESERVE (stock Clip / Shell / Cell / RocketAmmo or the mod's own) and ammo 2 the gun's loaded
rounds, the reverse of Generic Weapons. Every reload is a `ReloadLoop` that moves reserve into the gun one unit per
tic, so the KIND is read from the reload frames and sounds, quoted in the last column.

| Class | Parent | Slot | Ammo 1 (reserve) / Ammo 2 (loaded) | Reload state | Kind | Sprites | Evidence (ACTORS/) |
|---|---|---|---|---|---|---|---|
| Knuckles | Fist | 1 | - / - | no | melee (punch, kick) | - (Fist's) | KNUCKLES.txt: Fire / AltFire |
| Motorsaw | Weapon | 1 | SawFuel (fuel, no reload) | no | melee (saw) | CSAW SAWF SAWN SLCE | CHAINSAW.txt |
| Beretta | Weapon | 2 | Clip / 9mm | yes | magazine, slide after empty | BOOT BRLD BRTF BRTT CHLD GKCK KICK PIST | PISTOL.txt: ReloadChamberCheck, ReloadLoop |
| MP40 | Weapon | 2 | Clip / MP40Ammo | yes | magazine (also a dual-wield reload, BReload*) | DFSH DHLD DRLD MP4C MP4F MP4R MPGN MPIC PSMP PWHP | MP40.txt:187 `weapons/MP40/reload` |
| Riotgun | Weapon | 3 | Shell / LoadedShell | yes | pump, shells one at a time | BOOF CSHT RGLS RGSW RIOT SHAT SHZM ZMCK ZMFI ZMFL | RIOTGUN.txt: FirstLoad, ReloadWork, ReloadPump |
| Coachgun | Weapon | 3 | Shell / LoadedShells | yes | break-open, one or two shells | CCHG DBBL DBLS LFTF PKS2 RHTF SH2R SHT2 | COACHGUN.txt: ReloadDouble / ReloadSingle |
| MachineRifle | Weapon | 4 | RifleAmmo / Magazine | yes | magazine, charging handle after empty | ASLR ASLT IRFI IRON IRSW MRFL RFLF RIFL | MACHINERIFLE.txt: ReloadChamberCheck, ReloadLoop |
| Minigun | Weapon | 4 | Nato / NatoBelt | yes | magazine (belt box) | CHAF CHAG CHPF MNIG NGLD RCLD VLCN VLCS | MINIGUN.txt:263 `weapons/chaingun/feed`, NGLD/RCLD frames |
| SaturnV | RocketLauncher | 5 | RocketAmmo / RocketRounds (6) | yes | magazine (one load sound, six rounds) | BRKK HELX LAWN MACX MSLE ROKK SATF SATG SATR SATV | SATURNV.txt:223 Reload, `weapons/launcher/load` once |
| NovaRifle | weapon | 6 | Cell / Cellpak | yes | magazine (cell) | NOVF PLAS PLCH PLZF PLZG PLZR RALE | NOVARIFLE.txt:115 `weapons/plasmagun/reload` |
| TITAN | Weapon | 7 | Cell / BFGCell | yes | magazine (cell) | BFFL DBFC DBFF DBFG DEBF | TITAN.txt:129 `weapons/bfg/reload` |
| 1911 | Weapon | 8 | Bullets / ACP | yes | magazine, slide after empty | 1911 BOOT COLP GNFL HGLL HGRL KICK PKCK | 1911.txt:111 `weapons/1911/slide` |

Every reload is behind a cvar the mod's ACS reads (`VulcanReload`, `SaturnReload`, `NovaReload`, `TitanReload`, ...):
with the mod's reload off, the weapon never enters Reload and the hand reload has nothing to join.

## Donors (the profile rows in `RS_ForeignScanner.ProfileDonor`, `zscript/RS_ForeignModels.zs`)

Reload rows: magazine = `zscript_depot/rsr/rsr_guns.ms.zs SlotForDonor`, pump = `card_pump.report.md`,
break = `card_break.report.md`. Hand row = `zscript_depot/rsq/handtable.zs RSQ_HandTable.SlotForDonor` keyed on the
donor name the weapon wears; "same mesh as 1.x X (row N)" = `reload_names.json` says the card mesh is byte-identical
(`exact`) to a 1.x donor that has a hand row, but the row is keyed on the 1.x name, so it does NOT fire today (open
item in HANDOFF.md).

| Class | Donor | Reload row | Hand row | Why |
|---|---|---|---|---|
| Knuckles | MS_BD_Fist | n/a | no (the fist is the hand) | the only fist on the shelf; PB's pick |
| Motorsaw | MS_BD_Chainsaw | n/a | no | modern look, BD22 hold; PB's pick |
| Beretta | MS_BD_Pistol | magazine 55 | no (same mesh as 1.x MS_d64_BrutalPistol, row 38) | SEEN WORKING on the rig (README) |
| MP40 | MS_BD_Mp40 | magazine 45 | no (same mesh as 1.x MS_BD22_MP40 row 62 / MS_brt_MP40 row 31) | SEEN WORKING |
| 1911 | MS_BW_1911 | magazine 94 | no | SEEN WORKING (BrutalWolf 1911: the same gun) |
| MachineRifle | MS_BD_Rifle | magazine 75 | **yes** (row 10) | SEEN WORKING |
| Riotgun | MS_BD_Shotgun | pump slot 2 | no | SEEN WORKING |
| Coachgun | MS_BD_Ssg | break slot 3 | no | SEEN WORKING |
| Minigun | MS_VP_Minigun | magazine 103 (owner-confirmed carved ammo box) | no | the only chaingun with a measured row; BD_Minigun has none (PB's minigun never reloads) |
| SaturnV | MS_BD_Rpg | magazine 58 | no (same mesh as 1.x MS_brt_RPG / MS_d64_RPG, row 66) | the only rocket donor with a row; PB's pick |
| NovaRifle | MS_BD_Plasma | magazine 48 | no (same mesh as 1.x MS_brt_PlasmaGun / MS_d64_PlasmaGun, row 65) | BD plasma, cell magazine measured; PB's pick |
| TITAN | MS_HX_Nuker | magazine 98 (owner-confirmed cell carve) | no | the ONLY bfg-shelf donor with a reload row (BD_Bfg has none); PB's Demon-Tech pick |

Totals: 12 weapons, 12 donors, 10 reloading weapons all on measured rows (8 magazine, 1 pump, 1 break); hand rows
under the worn name: 1 of 12 (MachineRifle), 5 more have the row for the identical mesh under a 1.x name.

Classes shared with Generic Weapons (`Beretta`, `Riotgun`, `Minigun`) have one profile row each; the picks agree.
