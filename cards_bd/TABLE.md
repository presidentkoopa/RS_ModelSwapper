# Batch label table

One row per MD3. HIGH = archetype read from motion with no doubt; MED = plausible, glance at the sheet; LOW = owner names the archetype.
`parts` = the three busiest surfaces: index, HID if hidden at idle, longest side in model units, travel, rotation.

| model | frames/surfs/verts | archetype | why | parts | output |
|---|---|---|---|---|---|
| bd_AssaultShotgun | 32f/6s/3680v | mag_only (MED) | part drops 28 with no slide: mag change, no rack | s4 13u tr28 rot0; s0 11u tr10 rot0; s3 2u tr1 rot20 | survey only |
| bd_BFG | 16f/2s/7173v | arcade (MED) | 1 small movers only (trigger/hammer class) | s1 3u tr1 rot30 | survey only |
| bd_BFG10K | 21f/2s/7173v | arcade (MED) | 1 small movers only (trigger/hammer class) | s1 3u tr1 rot30 | survey only |
| bd_BFG_Flame | 16f/2s/68v | revolver (MED) | part spins 175deg about the bore | s1 37u tr0 rot175 | survey only |
| bd_Boot | 58f/2s/16142v | mag_only (MED) | part drops 50 with no slide: mag change, no rack | s1 35u tr50 rot103 | survey only |
| bd_Boot_DooM64 | 21f/1s/8071v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| bd_Bootlow | 58f/5s/5503v | arcade (HIGH) | nothing moves relative to the body | s1 24u tr0 rot0; s4 24u tr0 rot0; s3 26u tr0 rot0 | survey only |
| bd_BrutalAxe | 15f/1s/976v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| bd_BrutalAxe_pbr | 15f/2s/873v | arcade (HIGH) | nothing moves relative to the body | s0 14u tr0 rot0 | survey only |
| bd_Chain_saw | 65f/3s/15088v | mag_only (MED) | part drops 9 with no slide: mag change, no rack | s2 12u tr9 rot4; s0 65u tr2 rot4 | survey only |
| bd_Chain_saw_Better | 65f/5s/25576v | mag_only (MED) | part drops 54 with no slide: mag change, no rack | s0 37u tr54 rot105; s1 12u tr46 rot105; s2 47u tr9 rot105 | survey only |
| bd_Chain_saw_DooM64 | 8f/7s/25161v | mag_only (MED) | part drops 12 with no slide: mag change, no rack | s4 50u tr24 rot0; s2 14u tr12 rot0; s6 14u tr12 rot0 | survey only |
| bd_Chain_saw_Low | 65f/6s/6833v | mag_only (MED) | part drops 9 with no slide: mag change, no rack | s1 11u tr9 rot0; s5 61u tr0 rot0; s2 61u tr0 rot0 | survey only |
| bd_Chain_saw_blood | 12f/1s/8v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| bd_Dslayer | 10f/1s/10135v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| bd_Dual_MP40 | 20f/22s/9758v | pistol_mag (HIGH) | mag drops 25 + slide runs 17 along bore | s21 26u tr25 rot18; s0 26u tr25 rot0; s11 12u tr18 rot59 | card |
| bd_FlameCannon | 8f/1s/4977v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| bd_Flamethrower2 | 6f/3s/6088v | arcade (MED) | 2 small movers only (trigger/hammer class) | s2 4u tr1 rot45; s1 10u tr1 rot15 | survey only |
| bd_HellishMissile | 10f/1s/1484v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| bd_M79 | 33f/5s/5771v | mag_only (MED) | part drops 6 with no slide: mag change, no rack | s3 11u tr20 rot30; s4 38u tr6 rot30; s0 4u tr1 rot45 | survey only |
| bd_MP40 | 14f/11s/4879v | pistol_mag (HIGH) | mag drops 25 + slide runs 17 along bore | s10 26u tr25 rot0; s0 12u tr17 rot44; s9 3u tr1 rot28 | card |
| bd_RPG | 39f/13s/5646v | mag_only (MED) | part drops 50 with no slide: mag change, no rack | s6 14u tr55 rot76; s7 14u tr53 rot76; s12 14u tr52 rot76 | survey only |
| bd_RPGret | 1f/2s/8v | arcade (HIGH) | nothing moves relative to the body; single frame, parts named? -> namedcard.py | s1 2u tr0 rot0 | survey only |
| bd_RailGun | 37f/5s/7503v | arcade (MED) | 4 small movers only (trigger/hammer class) | s4 15u tr30 rot0; s1 3u tr6 rot0; s0 25u tr6 rot1 | survey only |
| bd_SnipaRailGun | 36f/5s/7503v | arcade (MED) | 2 small movers only (trigger/hammer class) | s4 15u tr30 rot0; s3 3u tr1 rot23; s1 3u tr0 rot0 | survey only |
| bd_SnipaRailGun_2 | 36f/5s/7503v | arcade (MED) | 2 small movers only (trigger/hammer class) | s4 15u tr30 rot0; s3 3u tr1 rot23; s1 3u tr0 rot0 | survey only |
| bd_Unmaker | 16f/3s/11535v | arcade (MED) | 1 small movers only (trigger/hammer class) | s2 7u tr1 rot20; s1 10u tr0 rot6 | survey only |
| bd__br_machinegun_f | 36f/6s/15786v | shotgun_pump (MED) | forward part strokes 10 along bore | s3 34u tr10 rot0; s2 3u tr0 rot20; s0 2u tr0 rot19 | card |
| bd_br_SMG_dual | 48f/8s/41884v | pistol_mag (HIGH) | mag drops 17 + slide runs 11 along bore | s4 8u tr12 rot94; s3 8u tr11 rot90; s7 25u tr17 rot21 | card |
| bd_br_SMG_f | 27f/6s/20978v | pistol_mag (HIGH) | mag drops 17 + slide runs 11 along bore | s0 8u tr11 rot90; s4 3u tr18 rot0; s3 25u tr17 rot0 | card |
| bd_br_SMG_holo | 27f/8s/20241v | pistol_mag (HIGH) | mag drops 17 + slide runs 11 along bore | s0 8u tr11 rot90; s4 3u tr18 rot0; s3 25u tr17 rot0 | card |
| bd_br_minigun_f | 16f/6s/5737v | mag_only (MED) | part drops 40 with no slide: mag change, no rack | s0 18u tr40 rot106; s5 21u tr13 rot106; s3 24u tr12 rot106 | survey only |
| bd_br_minigun_snub_f | 16f/6s/5787v | mag_only (MED) | part drops 40 with no slide: mag change, no rack | s0 18u tr40 rot106; s5 21u tr13 rot106; s3 17u tr12 rot106 | survey only |
| bd_br_pistol_f | 38f/6s/6709v | pistol_mag (HIGH) | mag drops 13 + slide runs 1 along bore | s3 13u tr30 rot0; s2 3u tr13 rot24; s5 4u tr1 rot37 | card |
| bd_br_pistol_f_dual | 47f/12s/13418v | pistol_mag (HIGH) | mag drops 14 + slide runs 1 along bore | s8 3u tr14 rot22; s9 13u tr14 rot21; s3 3u tr14 rot10 | card |
| bd_br_pistol_holo | 38f/8s/7729v | pistol_mag (HIGH) | mag drops 13 + slide runs 1 along bore | s3 13u tr30 rot0; s2 3u tr13 rot24; s5 4u tr1 rot37 | card |
| bd_br_plasma_dual | 44f/8s/15158v | mag_only (MED) | part drops 41 with no slide: mag change, no rack | s5 13u tr41 rot21; s2 13u tr41 rot0; s7 87u tr10 rot21 | survey only |
| bd_br_plasma_f | 30f/4s/7579v | mag_only (MED) | part drops 41 with no slide: mag change, no rack | s1 13u tr41 rot0; s2 3u tr1 rot20; s0 5u tr0 rot0 | survey only |
| bd_br_plasma_flame | 4f/3s/72v | break_action (MED) | part hinges 131deg off-bore | s0 5u tr14 rot131; s2 40u tr0 rot52 | card |
| bd_br_rifle_f | 32f/6s/7341v | pistol_mag (HIGH) | mag drops 36 + slide runs 10 along bore | s3 22u tr36 rot0; s1 15u tr10 rot0; s0 9u tr7 rot0 | card |
| bd_br_rifle_f_dual | 40f/12s/14682v | pistol_mag (HIGH) | mag drops 42 + slide runs 10 along bore | s9 22u tr42 rot22; s2 22u tr42 rot0; s7 15u tr11 rot22 | card |
| bd_br_rifle_holo | 32f/7s/5381v | pistol_mag (HIGH) | mag drops 36 + slide runs 10 along bore | s3 22u tr36 rot0; s1 15u tr10 rot0; s0 9u tr7 rot0 | card |
| bd_br_shotgun_aim_f | 36f/7s/19428v | shotgun_pump (MED) | forward part strokes 6 along bore | s0 6u tr17 rot29; s3 7u tr6 rot0; s2 15u tr6 rot0 | card |
| bd_br_shotgun_f | 36f/5s/19198v | shotgun_pump (MED) | forward part strokes 6 along bore | s0 6u tr17 rot29; s3 7u tr6 rot0; s2 15u tr6 rot0 | card |
| bd_br_ssg_2f | 52f/7s/16616v | pistol_mag (HIGH) | mag drops 6 + slide runs 1 along bore | s1 6u tr10 rot30; s2 6u tr10 rot30; s6 29u tr6 rot30 | card |
| bd_br_ssg_f | 52f/6s/20427v | pistol_mag (HIGH) | mag drops 6 + slide runs 1 along bore | s1 6u tr10 rot30; s2 6u tr10 rot30; s3 29u tr6 rot30 | card |
| bd_fist | 75f/4s/4520v | mag_only (MED) | part drops 3 with no slide: mag change, no rack | s1 HID 19u tr49 rot99; s3 HID 23u tr20 rot147; s2 HID 23u tr3 rot8 | survey only |
| bd_mg42 | 3f/2s/14709v | arcade (MED) | 1 small movers only (trigger/hammer class) | s1 3u tr1 rot20 | survey only |
| bd_nade | 27f/5s/2650v | mag_only (MED) | part drops 37 with no slide: mag change, no rack | s2 7u tr37 rot0; s3 11u tr17 rot87; s4 1u tr0 rot0 | survey only |
| bd_snipa | 1f/2s/8v | arcade (HIGH) | nothing moves relative to the body; single frame, parts named? -> namedcard.py | s1 17u tr0 rot0 | survey only |
| bd_snipaRPG | 1f/2s/8v | arcade (HIGH) | nothing moves relative to the body; single frame, parts named? -> namedcard.py | s1 17u tr0 rot0 | survey only |
| bd_taurusload | 33f/10s/11849v | pistol_mag (HIGH) | mag drops 5 + slide runs 1 along bore | s9 9u tr17 rot90; s5 9u tr17 rot90; s8 9u tr17 rot90 | card |
| hx_ElectroFX | 1f/2s/114v | arcade (HIGH) | nothing moves relative to the body; single frame, parts named? -> namedcard.py |  | survey only |
| hx_Reznator | 1f/4s/1730v | arcade (HIGH) | nothing moves relative to the body; single frame, parts named? -> namedcard.py | s0 31u tr0 rot0; s3 5u tr0 rot0; s2 18u tr0 rot0 | survey only |
| hx_arc | 6f/1s/8v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
