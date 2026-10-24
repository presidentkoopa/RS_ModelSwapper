# Batch label table

One row per MD3. HIGH = archetype read from motion with no doubt; MED = plausible, glance at the sheet; LOW = owner names the archetype.
`parts` = the three busiest surfaces: index, HID if hidden at idle, longest side in model units, travel, rotation.

| model | frames/surfs/verts | archetype | why | parts | output |
|---|---|---|---|---|---|
| 1911 | 10f/5s/2187v | pistol_mag (HIGH) | mag drops 13 + slide runs 4 along bore | s4 12u tr13 rot0; s3 22u tr4 rot0; s2 3u tr1 rot20 | card |
| AssaultShotgun | 4f/7s/3826v | arcade (MED) | 3 small movers only (trigger/hammer class) | s0 12u tr11 rot0; s6 6u tr7 rot5; s3 3u tr1 rot20 | survey only |
| Axe | 11f/4s/1691v | arcade (HIGH) | nothing moves relative to the body | s2 16u tr0 rot0; s1 41u tr0 rot0; s0 28u tr0 rot0 | survey only |
| CANISTER | 1f/4s/250v | arcade (HIGH) | nothing moves relative to the body; single frame, parts named? -> namedcard.py | s3 13u tr0 rot0; s0 15u tr0 rot0; s1 11u tr0 rot0 | survey only |
| CHAING | 6f/18s/1175v | pistol_mag (HIGH) | mag drops 5 + slide runs 5 along bore | s13 45u tr5 rot45; s15 45u tr5 rot45; s12 45u tr5 rot45 | card |
| CHAINGRPG | 7f/18s/2068v | mag_only (MED) | part drops 5 with no slide: mag change, no rack | s7 2u tr7 rot45; s6 3u tr6 rot45; s17 22u tr6 rot45 | survey only |
| Chaingun | 17f/4s/10133v | mag_only (MED) | part drops 44 with no slide: mag change, no rack | s2 45u tr44 rot45; s3 62u tr0 rot50; s1 6u tr0 rot10 | survey only |
| Flame | 10f/1s/1746v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| Grenade | 12f/1s/2947v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| Kar98 | 26f/11s/9415v | bolt_or_slide (MED) | rear part strokes 12 along bore, no mag drop | s1 9u tr43 rot10; s6 7u tr43 rot0; s9 9u tr43 rot0 | survey only |
| Knife | 11f/1s/2856v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| MG42 | 15f/5s/14709v | arcade (MED) | 4 small movers only (trigger/hammer class) | s3 10u tr16 rot90; s2 13u tr16 rot40; s4 6u tr10 rot0 | survey only |
| MP40 | 10f/7s/11943v | mag_only (MED) | part drops 12 with no slide: mag change, no rack | s6 2u tr12 rot0; s4 22u tr12 rot0; s5 4u tr1 rot25 | survey only |
| Nuker | 11f/6s/7101v | mag_only (MED) | part drops 8 with no slide: mag change, no rack | s3 27u tr8 rot0; s5 14u tr3 rot0; s2 27u tr3 rot0 | survey only |
| SSG | 12f/11s/6152v | shotgun_pump (HIGH) | forward part strokes 11 along bore with hidden shells | s1 17u tr11 rot0; s5 31u tr11 rot0; s0 3u tr0 rot10 | card |
| STG44 | 10f/23s/9056v | pistol_mag (HIGH) | mag drops 14 + slide runs 9 along bore | s2 26u tr14 rot0; s21 4u tr9 rot0; s17 15u tr9 rot0 | card |
| Saw | 6f/6s/6833v | arcade (HIGH) | nothing moves relative to the body | s2 17u tr0 rot0; s3 88u tr0 rot0; s0 87u tr0 rot0 | survey only |
| Shotgun | 29f/7s/19428v | shotgun_pump (MED) | forward part strokes 7 along bore | s6 6u tr19 rot29; s4 17u tr7 rot0; s3 8u tr7 rot0 | card |
| Stick | 11f/11s/820v | revolver (MED) | part spins 90deg about the bore | s3 11u tr0 rot90; s5 3u tr0 rot10; s4 3u tr0 rot3 | survey only |
| Tommy | 11f/4s/7029v | pistol_mag (HIGH) | mag drops 14 + slide runs 9 along bore | s3 22u tr14 rot0; s1 21u tr9 rot0; s2 4u tr1 rot20 | card |
| UZI | 16f/16s/2961v | pistol_mag (HIGH) | mag drops 20 + slide runs 6 along bore | s3 23u tr20 rot0; s6 16u tr8 rot0; s0 14u tr6 rot0 | card |
| Zooka | 11f/7s/11037v | mag_only (MED) | part drops 88 with no slide: mag change, no rack | s6 13u tr160 rot152; s0 62u tr88 rot152; s2 45u tr20 rot89 | survey only |
| bar | 10f/6s/5946v | bolt_or_slide (MED) | rear part strokes 13 along bore, no mag drop | s1 15u tr17 rot0; s3 18u tr13 rot0; s5 8u tr4 rot10 | survey only |
| bfg | 11f/2s/7173v | arcade (MED) | 1 small movers only (trigger/hammer class) | s1 2u tr0 rot15 | survey only |
| bolter | 5f/2s/4565v | arcade (HIGH) | nothing moves relative to the body | s1 5u tr1 rot0 | survey only |
| cryogun | 11f/5s/4788v | shotgun_pump (MED) | forward part strokes 10 along bore | s4 23u tr10 rot0; s3 2u tr0 rot10; s1 4u tr0 rot0 | card |
| garand | 14f/5s/16219v | bolt_or_slide (MED) | rear part strokes 10 along bore, no mag drop | s0 9u tr11 rot0; s3 10u tr10 rot10; s2 19u tr10 rot0 | survey only |
| luger | 13f/6s/5674v | pistol_mag (HIGH) | mag drops 17 + slide runs 4 along bore | s5 14u tr17 rot0; s1 6u tr3 rot80; s2 7u tr4 rot50 | card |
| melee | 6f/1s/460v | arcade (HIGH) | one surface: nothing separable; tier 0 only |  | survey only |
| pistol | 11f/6s/4151v | break_action (MED) | part hinges 25deg off-bore | s2 16u tr6 rot0; s3 5u tr1 rot25; s5 24u tr0 rot0 | card |
| ppsh41 | 10f/7s/11138v | mag_only (MED) | part drops 11 with no slide: mag change, no rack | s6 16u tr11 rot0; s0 6u tr8 rot0; s4 3u tr1 rot20 | survey only |
| tazer | 11f/2s/15467v | arcade (MED) | 1 small movers only (trigger/hammer class) | s1 3u tr0 rot10 | survey only |
| tec9 | 6f/4s/4433v | bolt_or_slide (MED) | rear part strokes 7 along bore, no mag drop | s2 4u tr7 rot0; s3 10u tr7 rot0; s1 3u tr1 rot25 | survey only |
| xplosebolt | 1f/3s/586v | arcade (HIGH) | nothing moves relative to the body; single frame, parts named? -> namedcard.py | s2 1u tr0 rot0; s1 12u tr0 rot0 | survey only |
