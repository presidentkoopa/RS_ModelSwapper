# Batch label table

One row per MD3. HIGH = archetype read from motion with no doubt; MED = plausible, glance at the sheet; LOW = owner names the archetype.
`parts` = the three busiest surfaces: index, HID if hidden at idle, longest side in model units, travel, rotation.

| model | frames/surfs/verts | archetype | why | parts | output |
|---|---|---|---|---|---|
| m260b | 20f/3s/3436v | mag_only (MED) | part drops 186 with no slide: mag change, no rack | s1 28u tr186 rot20; s2 11u tr2 rot17 | survey only |
| m4a3 | 20f/5s/1934v | pistol_mag (HIGH) | mag drops 65 + slide runs 7 along bore | s4 15u tr65 rot23; s2 4u tr3 rot62; s3 27u tr7 rot0 | card |
| m37a2 | 29f/4s/1615v | shotgun_pump (MED) | forward part strokes 11 along bore | s3 5u tr13 rot33; s1 18u tr11 rot0; s2 3u tr1 rot31 | card |
| AssaultShotgun | 32f/7s/5002v | mag_only (MED) | part drops 28 with no slide: mag change, no rack | s1 6u tr31 rot10; s6 12u tr28 rot0; s2 11u tr10 rot0 | survey only |
| BrutalAxe | 15f/2s/1101v | arcade (HIGH) | nothing moves relative to the body | s0 14u tr0 rot0 | survey only |
| BFG | 16f/2s/7173v | arcade (MED) | 1 small movers only (trigger/hammer class) | s1 3u tr1 rot30 | survey only |
| Beretta | 24f/4s/3331v | break_action (MED) | part hinges 57deg off-bore | s0 4u tr3 rot57; s2 24u tr6 rot0; s1 3u tr1 rot41 | card |
| Bolter | 5f/2s/4565v | arcade (HIGH) | nothing moves relative to the body | s1 5u tr1 rot0 | survey only |
| Chaingun | 16f/6s/5817v | mag_only (MED) | part drops 40 with no slide: mag change, no rack | s0 18u tr40 rot106; s5 21u tr13 rot106; s3 17u tr12 rot106 | survey only |
| chainsaw | 16f/1s/1028v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| revolver | 55f/7s/3345v | pistol_mag (HIGH) | mag drops 4 + slide runs 20 along bore | s2 7u tr20 rot180; s4 10u tr6 rot180; s3 6u tr6 rot180 | card |
| DSweap | 10f/1s/11507v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| fist | 57f/2s/2310v | arcade (MED) | 1 small movers only (trigger/hammer class) | s1 HID 19u tr38 rot93 | survey only |
| Flamethrower2 | 6f/3s/6155v | arcade (MED) | 2 small movers only (trigger/hammer class) | s2 4u tr1 rot45; s1 10u tr1 rot15 | survey only |
| M79 | 33f/5s/6858v | mag_only (MED) | part drops 6 with no slide: mag change, no rack | s3 11u tr20 rot30; s4 38u tr6 rot30; s0 4u tr1 rot45 | survey only |
| nade | 27f/5s/2650v | mag_only (MED) | part drops 37 with no slide: mag change, no rack | s2 7u tr37 rot0; s3 11u tr17 rot87; s4 1u tr0 rot0 | survey only |
| jackhammer | 20f/2s/994v | arcade (HIGH) | nothing moves relative to the body | s1 10u tr0 rot0 | survey only |
| Boot | 58f/4s/11484v | arcade (HIGH) | nothing moves relative to the body | s1 24u tr0 rot0; s2 26u tr0 rot0; s3 26u tr0 rot0 | survey only |
| Machinegun | 36f/6s/16748v | shotgun_pump (MED) | forward part strokes 10 along bore | s3 34u tr10 rot0; s2 3u tr0 rot20; s0 2u tr0 rot19 | card |
| pistolet | 32f/6s/704v | pistol_mag (HIGH) | mag drops 14 + slide runs 2 along bore | s2 2u tr18 rot33; s1 9u tr14 rot18; s3 2u tr11 rot18 | card |
| PlasmaRifle | 30f/4s/7593v | mag_only (MED) | part drops 41 with no slide: mag change, no rack | s1 13u tr41 rot0; s2 3u tr1 rot20; s0 5u tr0 rot0 | survey only |
| auto9 | 3f/2s/2326v | arcade (MED) | 1 small movers only (trigger/hammer class) | s1 4u tr1 rot33 | survey only |
| chainsaw | 45f/2s/1600v | break_action (MED) | part hinges 180deg off-bore | s0 28u tr1 rot180 | card |
| m32 | 37f/9s/4895v | break_action (MED) | part hinges 21deg off-bore | s5 32u tr0 rot180; s8 10u tr3 rot21; s0 20u tr0 rot0 | card |
| RailGun | 37f/5s/7552v | arcade (MED) | 4 small movers only (trigger/hammer class) | s4 15u tr30 rot0; s1 3u tr6 rot1; s0 25u tr6 rot1 | survey only |
| rev | 41f/11s/859v | pistol_mag (HIGH) | mag drops 1 + slide runs 6 along bore | s7 HID 4u tr132 rot86; s4 HID 4u tr120 rot178; s9 HID 4u tr118 rot168 | card |
| Rifle | 32f/6s/9804v | pistol_mag (HIGH) | mag drops 36 + slide runs 10 along bore | s3 22u tr36 rot0; s1 15u tr10 rot0; s0 9u tr7 rot0 | card |
| m16 | 41f/4s/696v | mag_only (MED) | part drops 23 with no slide: mag change, no rack | s1 HID 4u tr45 rot171; s3 12u tr23 rot16; s2 3u tr1 rot0 | survey only |
| RPG | 39f/13s/8482v | mag_only (MED) | part drops 50 with no slide: mag change, no rack | s6 14u tr55 rot76; s7 14u tr54 rot76; s12 14u tr53 rot76 | survey only |
| BrutalSMG | 27f/4s/21072v | pistol_mag (HIGH) | mag drops 17 + slide runs 11 along bore | s0 8u tr11 rot90; s3 25u tr17 rot0; s2 3u tr1 rot0 | card |
| shotgun | 32f/3s/597v | shotgun_pump (HIGH) | forward part strokes 7 along bore with hidden shells | s2 HID 4u tr52 rot153; s1 13u tr7 rot0 | card |
| ssg | 26f/6s/675v | mag_only (MED) | part drops 51 with no slide: mag change, no rack | s3 4u tr77 rot72; s2 4u tr51 rot109; s1 HID 2u tr45 rot95 | survey only |
| tec9 | 6f/4s/5469v | bolt_or_slide (MED) | rear part strokes 7 along bore, no mag drop | s2 4u tr7 rot0; s3 10u tr7 rot0; s1 3u tr1 rot25 | survey only |
| Unmaker | 16f/3s/11541v | arcade (MED) | 1 small movers only (trigger/hammer class) | s2 7u tr1 rot20; s1 10u tr0 rot6 | survey only |
