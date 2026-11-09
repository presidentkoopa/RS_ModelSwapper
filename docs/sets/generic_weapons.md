# Generic Weapons set (PLAN M2, 2026-11-08)

Mod: "Generic Weapons" (`li-gnrcwpn.zip`, DECORATE weapons over a ZScript `ModWeapon : Weapon` base,
`zscript/weapons/base.txt`). A vanilla-Doom weapon set with magazines, so the owner's rule for its look is
**closest to vanilla**: alek's Vanilla Plus (`cards/vplus`) first, then `universal_voxel` D4 / `d64`, BD only where no
vanilla-looking mesh exists; the four pairings seen working on the rig (README "Seen working") stay unless a
vanilla-look donor with a measured reload row of the same kind AND a hand row exists (none does, see below).

Set pk3: `pk3/GenericWeapons_MS.pk3` (`python3 tools/ms/build_pk3.py --set generic_weapons`), menu `MENUDEF.gnrc`
(Options > "Generic Weapons VR"). Load order: doom2 -> Generic Weapons -> GenericWeapons_MS.pk3.
**Not rig-run** (no engine in the session that made it).

## Inventory (parsed from the mod's DECORATE; `python3 -I` on the unpacked zip)

Every weapon is `ACTOR X : ModWeapon`; ammo 1 is the gun's own magazine counter, ammo 2 the reserve. "Reload kind"
is read from the Reload state's own actions, quoted in the last column.

| Class | Slot | Ammo 1 (mag) / Ammo 2 (reserve) | Reload state | Kind | Sprites | Evidence (actors/weapons/) |
|---|---|---|---|---|---|---|
| Knuckle | 1 | - / - | no | melee | GRAB PKFS PUNP | knuckle.txt: Fire only |
| ModChainsaw | MS_BD_Chainsaw | n/a | no (owner 2026-11-08: chainsaws go without hands until Handfit) | BD's chainsaw (was VP_Chainsaw; its Ermac fit was refused by the owner) |
| Beretta | 2 | PistolMag / PistolAmmo | yes | magazine, slide after empty | BRLD BRTF BRTT CHLD PIST | pistol.txt:164 `A_FireProjectile("SpentClip1")`, ChamberCheck |
| ARifle | 2 | RifleMag / RifleAmmo | yes | magazine, charging handle after empty | ASLR ASLT ASRL IRFI IRON IRSW RFLF RIFG RIFL | rifle.txt:167 `RifleMagDrop`, ChamberCheck |
| Riotgun | 3 | ShotgunMag / Shell | yes | pump, shells one at a time | BOOF RGLS RGSW RIOB RIOT SHZM ZMCK ZMFI ZMFL | shotgun.txt: ReloadLoop one shell, ReloadPump |
| DoubleSG | MS_BD_Ssg | break slot 3 | **yes** (row 76: gun hand C + support B UNDER THE BARRELS, midway; owner 2026-11-08; hands/MS_BD_Ssg.png) | SEEN WORKING |
| Minigun | MS_BD_Minigun | none (the mod's own ammo-box reload runs) | **yes** (row 80: gun hand F on the rear grip + support E, the fist on the side handlebar the card names; hands/MS_BD_Minigun.png) | owner 2026-11-08: BD's minigun; the VP one's card grip sits on the ammo box (its fit refused, hands/MS_VP_Minigun.png) |
| Rlauncher | 5 | RocketMag / RocketAmmo | yes | magazine (rocket pack) | LAWN LNCH LNFI LODE | rlaunch.txt:155 `RocketPackDrop` |
| PlasRifle | 6 | PlasmaMag / Cell | yes | magazine (cell) | PLAS PLCH PLZA PLZG PLZR | plasrifle.txt:208 `PulseCellDrop` |
| BFG9K | 7 | BFGMag / Cell | yes | magazine (cell) | BFGE BFGN BFGO BFGR BFGX BFGY BFUG LBFG | bfg.txt:170-172 `weapons/bfg/clipout`, `PulseCellDrop` |

`ModWeapon` itself (base.txt) has no slot, ammo or sprites of its own: not a weapon the player holds, no row.

## Donors (the profile rows in `RS_ForeignScanner.ProfileDonor`, `zscript/RS_ForeignModels.zs`)

Reload rows: magazine = `zscript_depot/rsr/rsr_guns.ms.zs SlotForDonor`, pump = `card_pump.report.md`,
break = `card_break.report.md`. Hand row = `zscript_depot/rsq/handtable.zs RSQ_HandTable.SlotForDonor` keyed on the
donor name the weapon wears (`ms_donor_main`); "same mesh as 1.x X (row N)" = `reload_names.json` says the card
mesh is byte-identical (`exact`) to a 1.x donor that has a hand row; `tools/ms/hand_names.py` (2026-11-08) writes those
rows under the card name too, so they fire.

| Class | Donor | Reload row | Hand row | Why |
|---|---|---|---|---|
| Knuckle | MS_BD_Fist | n/a | no (the fist is the hand) | the only fist on the shelf (melee family); PB's pick |
| ModChainsaw | MS_VP_Chainsaw | n/a | **yes** (row 79: gun hand only, Ermac F; fitted 2026-11-08, see hands/MS_VP_Chainsaw.png) | vanilla look (alek's Vanilla Plus saw, card: rear grip + top bar, both headset holds); BD_Chainsaw was the modern alternative |
| Beretta | MS_BD_Pistol | magazine 55 | **yes** (row 38, via its exact twin MS_d64_BrutalPistol; hand_names.py) | SEEN WORKING on the rig (README); VP_Pistol has a magazine row (104) but no hand row, so the rule to switch is not met |
| ARifle | MS_BD_Rifle | magazine 75 | **yes** (row 10) | SEEN WORKING; VP_M16 has a row (52) but no hand row under its card name |
| Riotgun | MS_BD_Shotgun | pump slot 2 | **yes** (row 75: gun hand C + support B on the pump; fitted 2026-11-08, hands/MS_BD_Shotgun.png) | SEEN WORKING; VP_Shotgun has a pump row (slot 6) but no hand row |
| DoubleSG | MS_BD_Ssg | break slot 3 | **yes** (row 76: gun hand C; support off, the card has no measured support point; hands/MS_BD_Ssg.png) | SEEN WORKING; VP_Ssg has a break row (slot 7) but no hand row |
| Minigun | MS_VP_Minigun | magazine 103 (owner-confirmed carved ammo box) | no: fitted and REFUSED, the card's grip line sits on the ammo box, the hand landed there (hands/MS_VP_Minigun.png) | vanilla look AND the only chaingun with a measured row; BD_Minigun has no row (PB's minigun never reloads) |
| Rlauncher | MS_BD_Rpg | magazine 58 | **yes** (row 66, via its exact twin MS_brt_RPG / MS_d64_RPG; hand_names.py) | the Vanilla Plus RPG IS this mesh (`reload_names`: MS_vplus_RPG = MS_BD_Rpg exact); only rocket donor with a row |
| PlasRifle | MS_BD_Plasma | magazine 48 | **yes** (row 65, via its exact twin MS_brt_PlasmaGun / MS_d64_PlasmaGun; hand_names.py) | the Vanilla Plus plasma rifle IS this mesh (MS_vplus_PlasmaRifle = MS_BD_Plasma exact); carded VP_Plasma has no magazine |
| BFG9K | MS_HX_Nuker | magazine 98 (owner-confirmed cell carve) | **yes** (row 78: gun hand F; support off, no measured support point; hands/MS_HX_Nuker.png) | the ONLY bfg-shelf donor with a reload row; the vanilla-look MG_Bfg / BD_Bfg have none (the mod's own reload would run). Owner's call if the look matters more |

Totals: 10 weapons, 10 donors, 7 reloading weapons on measured rows (5 magazine, 1 pump, 1 break; the Minigun runs the
mod's own reload: BD's minigun has no row). Hands: 9 of 10 (the fist is the hand; Beretta, ARifle, Rlauncher, PlasRifle by
`hand_names.py`; Riotgun, DoubleSG, Minigun, BFG9K fitted 2026-11-08 by `tools/ms/handfit_donors.py`, sheets in `hands/`;
ModChainsaw without, by the owner). Rig only: nothing in a headset.

Classes shared with Weapons of Saturn (`Beretta`, `Riotgun`, `Minigun`) have one profile row each; the picks agree.
