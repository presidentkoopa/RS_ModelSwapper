# Golden Souls 1 set (PLAN M3, 2026-11-08)

Source: `00_SMD2_A1_GoldenSouls1_Full_1_4.pk3` (Doom: The Golden Souls 1, v1.4), `decorate/dec_weps.dec`. Read as data.
Profile rows: `zscript/RS_ForeignModels.zs` ProfileDonor. Set: `tools/ms/build_pk3.py --set golden_souls_1` ->
`pk3/GoldenSouls1_MS.pk3` with `MENUDEF.gs1`. Hands: `zscript_depot/rsq/handtable.zs` rows, sheets in `hands/`
(`SET_golden_souls_1.png` is every weapon). Not rig-run.

## The mod's weapons
| Class | Slot | Ammo | Reload | Kind (from its states) |
|---|---|---|---|---|
| Fist2 | 1 | - | no | fists (replaces Fist) |
| Cannon | - | CannonballAmmo | no | a hand cannon that fires Bullet Bills |
| AutoShotgun | - | Shell | yes | one reload animation refilling an internal counter (`Ammoshotgun`): magazine-style |
| OverandUnder | - | Shell | yes | break-open, one or two shells (ReloadSingle / the pair) |
| Revolver | - | Rev_Ammo | yes | swing out, eject, insert, close (REV2/REV3/REV4) |
| AK47 | - | AK_Mag | yes | magazine, bolt pull after 30 (`BoltPull`) |
| SpikeGun | 5 | Spikeammo | no | spike / nail gun, two barrels |
| RailBow | - | RainbowAmmo | no | charged rail shot, iron sights (`IronSightSniper`) |

## The picks
| Class | Donor | Reload row | Hand row | Why |
|---|---|---|---|---|
| Fist2 | MS_BD_Fist | n/a | the fist is the hand | the only fist |
| Cannon | MS_PD_Cannon | none (no reload) | **no**: fitted and REFUSED, the pirate cannon is a metre-long carried barrel and the ICP put the hand inside it (hands/MS_PD_Cannon.png) | the look: a cannon. The alternative with a hand row is BD_Rpg (row 66), a rocket launcher |
| AutoShotgun | MS_BD_Assaultshotgun | magazine 79 | yes (row 63, BD22 fit) | magazine-style auto shotgun, same mechanism |
| OverandUnder | MS_BD_Ssg | break slot 3 | yes (row 76: gun + support under the barrels) | break-open double |
| Revolver | MS_BD_Revolver | break slot 2 (speedloader) | **yes** (row 80: gun B + cup A; fitted 2026-11-08, hands/MS_BD_Revolver.png) | swing-out revolver; the alek VP_Rev (break 7) has no hand |
| AK47 | MS_BD_Rifle | magazine 75 | yes (row 10) | the only rifle with a measured magazine row AND a hand row; BW_Stg44 is the closer look but has neither |
| SpikeGun | MS_CW_Nailgun | magazine 40 (unused: the mod has no reload) | **yes** (row 81: gun F + support B on the magazine, the card's measured `magwell` feature; hands/MS_CW_Nailgun.png) | nail gun for a spike gun |
| RailBow | MS_BD_Railgun | magazine 43 (unused) | **yes** (row 83: gun F on the grip + support B under the forend, fitted on the LEVEL gun; the donor's rest frame is 3 now, the OG Ready frame 2 was the last raise frame, 12 units low and pitched -9 deg; hands/MS_BD_Railgun.png) | the rail gun; HV_Crossbow is the bow look but has no rows |

Totals: 8 weapons, 8 donors; the 4 reloading weapons on measured rows of their kind (2 magazine, 2 break). Hands:
7 of 8 (the fist is the hand), the Cannon without. Rig only: nothing in a headset.
