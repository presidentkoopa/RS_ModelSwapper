# Quest_Weapons_Kit inventory (generated 2026-10-24 from the folder listing)

USED = the pipeline imports or copies it · KEEP = a tool we will run · REFERENCE = read-only source of truth · doc/asset/sheet as named.

## The short version
- The pipeline needs **8 files** from the kit (USED). They are copied into `vault/tools/kit/` and are byte-identical to the kit's.
- **37 KEEP** tools are worth running again: Ermac's gun meshes (unlock the original ICP hand fit), the carve/extract/quad mesh surgery, gripmeasure, the original align/fitall.
- Everything else is reference or evidence: three lanes' duplicates of the same hand tools (`kit/melee/`, `kit/tool/hands/`, `kit/tool/melee/` are the same scripts copied three times), v8 backups, sheets, lane packs.
- Nothing is lost: the kit only ever grew (681 entries; 43 added since 2026-10-23 22:00, none removed).

| file | bytes | status |
|---|---|---|
| kit/cur/bd/MODELDEF.rsq | 7137 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/cur/bd/models/rsq/hand.md3 | 390624 | asset |
| kit/cur/bd/models/rsq/hand2.md3 | 69888 | asset |
| kit/cur/bd/zscript/rsq/handtable.zs | 6885 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/ermac/ammo_hand/LICENSE_RustedLegacy_MIT.txt | 1086 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/ammo_hand/ammo_hand.md3 | 102784 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/ammo_hand/berettam9.jpg | 21632 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/ammo_hand/hand.png | 48471 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/ammo_hand/mag_chaingun.md3 | 22908 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/ammo_hand/mag_pistol.md3 | 43604 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/ammo_hand/mag_plasma.md3 | 7628 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/ammo_hand/pod_rocket.md3 | 20776 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/ammo_hand/shot_shell.md3 | 1828 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/ammo_hand/shot_shell2.md3 | 3548 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/hand/hand.md3 | 1764032 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/hand/hand.png | 48471 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/hand/hand2.md3 | 1640672 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/pistol/berreta.md3 | 707392 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/pistol/berreta_mag.md3 | 202620 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/pistol/berreta_mag2.md3 | 13556 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/pistol/berreta_mf.md3 | 8424 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/pistol/berreta_pickup.md3 | 46480 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/plasmarifle/plasma_d1.md3 | 428 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/plasmarifle/plasma_d2.md3 | 428 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/plasmarifle/plasma_d3.md3 | 428 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/plasmarifle/plasma_mag.md3 | 19708 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/plasmarifle/plasma_mag2.md3 | 7628 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/plasmarifle/plasma_mf2.md3 | 1368 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/plasmarifle/plasma_rifle.md3 | 162276 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/plasmarifle/plasmarifle_pickup.md3 | 54968 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/shotgun/shell.md3 | 3684 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/shotgun/shotgun.md3 | 216604 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/shotgun/shotgun_mf.md3 | 1248 | KEEP — Ermac source mesh (original ICP fit) |
| kit/ermac/shotgun/shotgun_pickup.md3 | 23448 | KEEP — Ermac source mesh (original ICP fit) |
| kit/hands/fit_NewShotgun_3D.png | 62533 | sheet (evidence) |
| kit/hands/fit_PulseRifle_3D.png | 77459 | sheet (evidence) |
| kit/hands/fitfree_NewShotgun_3D.png | 63375 | sheet (evidence) |
| kit/hands/fitfree_PulseRifle_3D.png | 78401 | sheet (evidence) |
| kit/hands/fitfree_Rifle.png | 72266 | sheet (evidence) |
| kit/hands/fitfree_Shot_Gun.png | 72032 | sheet (evidence) |
| kit/hands/fits.json | 7444 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/hands/fits_free.json | 761 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/hands/gripregions.png | 143456 | sheet (evidence) |
| kit/hands/tmp_a.png | 22753 | sheet (evidence) |
| kit/hands/tmp_b.png | 9727 | sheet (evidence) |
| kit/hands/tmp_c.png | 11539 | sheet (evidence) |
| kit/melee/align.py | 3188 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/bladeinfo.py | 1427 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/ermac.py | 1521 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/fitall.py | 2304 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/gripcheck.py | 1021 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/guns.py | 2536 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/gunview.py | 7683 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/handfit.py | 1519 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/handframe.py | 2014 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/handtable.py | 1464 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/hudrender.py | 4519 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/hudview.py | 2027 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/minigun_fit.py | 2249 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/pk3model.py | 1469 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/regen_displayed.py | 1388 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/melee/support.py | 4231 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/setpath.py | 1637 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/team/build_bd22_v9.py | 14615 | REFERENCE — lane work |
| kit/team/build_vplus_v9.py | 11328 | REFERENCE — lane work |
| kit/team/gunmoves_bd22.zs | 13092 | REFERENCE — lane work |
| kit/team/gunmoves_vplus.zs | 6158 | REFERENCE — lane work |
| kit/team/hands.zs | 12677 | REFERENCE — lane work |
| kit/team/hands_work/fire_bd22.json | 6460 | REFERENCE — lane work |
| kit/team/hands_work/fire_frames.py | 5407 | REFERENCE — lane work |
| kit/team/hands_work/fire_vplus.json | 930 | REFERENCE — lane work |
| kit/team/hands_work/kick_bd22.json | 279654 | REFERENCE — lane work |
| kit/team/hands_work/kick_measure.py | 7396 | REFERENCE — lane work |
| kit/team/hands_work/kick_vplus.json | 6888 | REFERENCE — lane work |
| kit/team/hands_work/rsq_gunmoves_gen.py | 12565 | REFERENCE — lane work |
| kit/team/integ/rtest/compare.py | 1234 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/driver.zs | 8965 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/final.sh | 3036 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/fire_bd.sh | 572 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/layers.py | 757 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/logdiff.py | 1742 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/pertable.py | 2626 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/recoil.py | 2017 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/run.py | 6159 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/sheet.py | 822 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/suite.sh | 3205 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/template.ini | 23348 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/v8stub.zs | 128 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/v9extra.zs | 1991 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/vrcompare.py | 1507 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/integ/rtest/vrshots.sh | 857 | REFERENCE — the Linux rtest harness (ported to /home/claude/rtest) |
| kit/team/melee_hands/check_gen.py | 3378 | REFERENCE — melee hand fits |
| kit/team/melee_hands/fit_melee.py | 9137 | REFERENCE — melee hand fits |
| kit/team/melee_hands/fits_bd22_v9.json | 9178 | REFERENCE — melee hand fits |
| kit/team/melee_hands/gen/MODELDEF.rsq | 4720 | REFERENCE — melee hand fits |
| kit/team/melee_hands/rsq_hands_gen_melee.py | 10697 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_c.png | 13272 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_cmp_135f.png | 17287 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_cmp_195f.png | 15796 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_cmp_270.png | 15218 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_e0.png | 18063 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_e1.png | 21790 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_f.png | 18516 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_s.png | 26910 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_slot_+0.00_-0.50.png | 14170 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_slot_+0.60_+0.30.png | 13804 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_slot_+0.60_-0.60.png | 13451 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_slot_-0.90_+1.20.png | 14812 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_000.png | 10206 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_000f.png | 10575 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_045.png | 11049 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_045f.png | 12240 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_090.png | 10053 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_090f.png | 10229 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_135.png | 11166 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_135f.png | 11317 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_180.png | 10172 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_180f.png | 10527 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_225.png | 11262 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_225f.png | 11455 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_270.png | 10333 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_270f.png | 10585 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_315.png | 12017 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_sw_315f.png | 11572 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/_t.png | 18030 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/ax1.py | 757 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/ax2.py | 1817 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/ax3.py | 1487 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/ax_sheet.py | 504 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_measure.py | 2683 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_shift.py | 3338 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_sup.py | 4456 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_sup2.py | 7348 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_sup_best.json | 124 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_sup_cmp.py | 1408 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_sup_score.py | 3455 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_sup_slot.json | 287 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_sup_slot.py | 5207 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_sup_sweep.py | 3892 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/axe_two.py | 5975 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/cmp_axe_wrap.png | 48206 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/common.py | 242 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/contact.py | 3744 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/contact_bd22_hands.png | 375139 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/ds_bat.py | 5112 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/ds_fit.py | 6096 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/ds_profile.py | 2386 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/e1.py | 855 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/f91.py | 714 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/fitlib.py | 9630 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/fits_axe_spread.json | 548 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/fits_axe_sup.json | 485 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/fits_axe_two.json | 565 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/fits_dsweap.json | 560 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/fits_dsweap_bat.json | 558 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/fits_saw_fix.json | 482 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/grip29_const.json | 161 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/grip29_recover.py | 3823 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/h29f.py | 555 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/h29x.py | 575 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/handpos.py | 840 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/hollow.py | 2049 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/look.py | 742 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/look2.py | 708 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/look3.py | 228 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/look4.py | 235 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/m1.py | 928 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/review_BrutalAxe_spread.png | 118558 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/review_BrutalAxe_twohand.png | 145354 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/review_Chain_saw_fix.png | 184117 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/review_Chain_saw_now.png | 177972 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/review_DSweap.png | 132600 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/review_DSweap_bat.png | 137140 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/review_axe_one.png | 65459 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/review_axe_two.png | 105253 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/saw_blade.py | 3294 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/saw_blade_components.png | 23388 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/saw_blade_draw.py | 3415 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/saw_fix.py | 4413 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/saw_now.py | 3117 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/saw_trigger.py | 2586 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/saw_trigger_box.json | 83 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/saw_trigger_side.png | 33999 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/slot_axe_sections.png | 55929 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/sw1.py | 858 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/sw2.py | 1522 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/sw3.py | 1158 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/sw4.py | 797 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/sw5.py | 2094 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/sw_sheet.py | 744 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/sweep_axe_roll.png | 173428 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/xs.py | 2466 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/xsec_BrutalAxe_sup.png | 14063 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/xsec_Chain_saw_fix.png | 14256 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/xsec_Chain_saw_now.png | 14728 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/xsec_DSweap_bat.png | 14963 | REFERENCE — melee hand fits |
| kit/team/melee_hands/work/xsec_DSweap_sup.png | 15800 | REFERENCE — melee hand fits |
| kit/team/offscan.py | 1374 | REFERENCE — lane work |
| kit/team/reload_merged/DESIGN.md | 14213 | REFERENCE — lane work |
| kit/team/reload_merged/PROGRESS.md | 9103 | REFERENCE — lane work |
| kit/team/reload_merged/_hands_in.zs | 12677 | REFERENCE — lane work |
| kit/team/reload_merged/_hands_test.zs | 13362 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/gun.py | 8410 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/pump_test.zs | 16182 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/rsb_testdriver.zs | 16926 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/run.sh | 449 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/scenario.py | 1798 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/sheet.py | 3198 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/suite_all.sh | 1774 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/suite_empty.sh | 780 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/suite_shots.sh | 1362 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/suite_t1.sh | 1612 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/table.py | 3618 | REFERENCE — lane work |
| kit/team/reload_merged/rtest/vrhand_rsr.zs | 18260 | REFERENCE — lane work |
| kit/team/reload_merged/rtest_break/par.sh | 374 | REFERENCE — lane work |
| kit/team/reload_merged/rtest_break/rsb_run.py | 3595 | REFERENCE — lane work |
| kit/team/reload_merged/rtest_break/run.sh | 715 | REFERENCE — lane work |
| kit/team/reload_merged/rtest_break/scenario.py | 1972 | REFERENCE — lane work |
| kit/team/reload_merged/rtest_pump/pump_scen.py | 5265 | REFERENCE — lane work |
| kit/team/reload_merged/rtest_pump/pump_suite.py | 7477 | REFERENCE — lane work |
| kit/team/reload_merged/rtest_pump/pump_summary.py | 4877 | REFERENCE — lane work |
| kit/team/reload_merged/rtest_pump/run.sh | 715 | REFERENCE — lane work |
| kit/team/reload_merged/src/CVARINFO.rsb | 333 | REFERENCE — lane work |
| kit/team/reload_merged/src/CVARINFO.rsr | 930 | REFERENCE — lane work |
| kit/team/reload_merged/src/Decorate/revolver.txt | 8559 | REFERENCE — lane work |
| kit/team/reload_merged/src/Decorate/rifle.txt | 5133 | REFERENCE — lane work |
| kit/team/reload_merged/src/Decorate/shotty.txt | 10365 | REFERENCE — lane work |
| kit/team/reload_merged/src/MODELDEF.rsb.bd | 10086 | REFERENCE — lane work |
| kit/team/reload_merged/src/MODELDEF.rsb.hands | 370 | REFERENCE — lane work |
| kit/team/reload_merged/src/MODELDEF.rsb.vp | 10727 | REFERENCE — lane work |
| kit/team/reload_merged/src/MODELDEF.rsr.bd | 26585 | REFERENCE — lane work |
| kit/team/reload_merged/src/MODELDEF.rsr.hands | 329 | REFERENCE — lane work |
| kit/team/reload_merged/src/MODELDEF.rsr.vp | 2058 | REFERENCE — lane work |
| kit/team/reload_merged/src/MODELDEF.rsrpump.bd | 3032 | REFERENCE — lane work |
| kit/team/reload_merged/src/MODELDEF.rsrpump.hands | 349 | REFERENCE — lane work |
| kit/team/reload_merged/src/MODELDEF.rsrpump.vp | 2066 | REFERENCE — lane work |
| kit/team/reload_merged/src/rsb_geometry.json | 5167 | REFERENCE — lane work |
| kit/team/reload_merged/src/rsb_vrev_loader.md3 | 7652 | REFERENCE — lane work |
| kit/team/reload_merged/src/rsr_files.json | 2568 | REFERENCE — lane work |
| kit/team/reload_merged/src/rsr_geometry.json | 10025 | REFERENCE — lane work |
| kit/team/reload_merged/src/rsr_pump_geometry.json | 3475 | REFERENCE — lane work |
| kit/team/reload_merged/src/rsr_weapons.json | 2506 | REFERENCE — lane work |
| kit/team/reload_merged/tools/bd_rifle_geo.py | 626 | REFERENCE — lane work |
| kit/team/reload_merged/tools/bd_rifle_view.py | 892 | REFERENCE — lane work |
| kit/team/reload_merged/tools/build_proto.py | 8241 | REFERENCE — lane work |
| kit/team/reload_merged/tools/ermac_hold.py | 1494 | REFERENCE — lane work |
| kit/team/reload_merged/tools/gen_pump.py | 17497 | REFERENCE — lane work |
| kit/team/reload_merged/tools/gen_rsb.py | 36454 | REFERENCE — lane work |
| kit/team/reload_merged/tools/gen_rsr.py | 26859 | USED — genpack: reload tables + MODELDEF.rsr (unmodified) |
| kit/team/reload_merged/tools/hands_hook.py | 4880 | REFERENCE — lane work |
| kit/team/reload_merged/tools/iqm_split.py | 4906 | REFERENCE — lane work |
| kit/team/reload_merged/tools/m16_geo.py | 1718 | REFERENCE — lane work |
| kit/team/reload_merged/tools/md3parts.py | 1236 | REFERENCE — lane work |
| kit/team/reload_merged/tools/md3rel.py | 1869 | REFERENCE — lane work |
| kit/team/reload_merged/tools/publish.sh | 963 | REFERENCE — lane work |
| kit/team/reload_merged/tools/pump_build.py | 3564 | REFERENCE — lane work |
| kit/team/reload_merged/tools/pump_hands_hook.py | 3041 | REFERENCE — lane work |
| kit/team/reload_merged/tools/rgeo.py | 4827 | USED — controller-frame chain (to_flu) |
| kit/team/reload_merged/tools/rsb_patch.py | 18027 | REFERENCE — lane work |
| kit/team/reload_merged/tools/rsr_patch.py | 23164 | REFERENCE — BD22 DECORATE patcher (the 1.96b architecture) |
| kit/team/reload_merged/tools/rsr_pump_patch.py | 23101 | REFERENCE — lane work |
| kit/team/reload_merged/tools/rview.py | 2538 | REFERENCE — lane work |
| kit/team/reload_survey/SURVEY.md | 83860 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_AssaultShotgun_geometry_front.png | 7752 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_AssaultShotgun_geometry_side.png | 15341 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_AssaultShotgun_storyboard.png | 74553 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_BrutalPistol_geometry_front.png | 6308 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_BrutalPistol_geometry_side.png | 12377 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_BrutalPistol_storyboard.png | 65832 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_BrutalSMG_geometry_front.png | 8548 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_BrutalSMG_geometry_side.png | 20728 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_BrutalSMG_storyboard.png | 119492 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_GrenadeLauncher_geometry_front.png | 7662 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_GrenadeLauncher_geometry_side.png | 16942 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_GrenadeLauncher_open_front.png | 11341 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_GrenadeLauncher_open_side.png | 26448 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_GrenadeLauncher_storyboard.png | 109673 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_MP40_geometry_front.png | 8095 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_MP40_geometry_side.png | 18385 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_MP40_storyboard.png | 44807 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Plasma_Gun_geometry_front.png | 10055 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Plasma_Gun_geometry_side.png | 28876 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Plasma_Gun_storyboard.png | 108431 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_RailGun_geometry_front.png | 8696 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_RailGun_geometry_side.png | 26257 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_RailGun_storyboard.png | 116380 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Revolver_geometry_front.png | 8715 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Revolver_geometry_side.png | 18724 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Revolver_open_front.png | 14634 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Revolver_open_side.png | 18957 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Revolver_storyboard.png | 66669 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Rifle_geometry_front.png | 7853 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Rifle_geometry_side.png | 22768 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Rifle_storyboard.png | 142122 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Rocket_Launcher_geometry_front.png | 12964 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Rocket_Launcher_geometry_side.png | 28301 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Rocket_Launcher_storyboard.png | 98352 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_SSG_geometry_front.png | 8485 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_SSG_geometry_side.png | 18539 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_SSG_open_front.png | 9383 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_SSG_open_side.png | 23126 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_SSG_storyboard.png | 70760 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Shot_Gun_geometry_front.png | 8078 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Shot_Gun_geometry_side.png | 25888 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Shot_Gun_storyboard.png | 130181 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Sniper_geometry_front.png | 19702 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Sniper_geometry_side.png | 24318 | REFERENCE — lane work |
| kit/team/reload_survey/img/BD22_Sniper_storyboard.png | 80288 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Revolver2_geometry_front.png | 14785 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Revolver2_geometry_side.png | 14136 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Revolver2_open_front.png | 20081 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Revolver2_open_side.png | 16755 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Revolver2_storyboard.png | 62480 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Revolver_geometry_front.png | 14648 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Revolver_geometry_side.png | 14003 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Revolver_open_front.png | 20051 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Revolver_open_side.png | 16723 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Revolver_storyboard.png | 62480 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Rifle_geometry_front.png | 5726 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Rifle_geometry_side.png | 13570 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Rifle_storyboard.png | 83692 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Shotgun_geometry_front.png | 4818 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Shotgun_geometry_side.png | 11791 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_Shotgun_storyboard.png | 37617 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_SuperShotgun_geometry_front.png | 5805 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_SuperShotgun_geometry_side.png | 12693 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_SuperShotgun_open_front.png | 10547 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_SuperShotgun_open_side.png | 16237 | REFERENCE — lane work |
| kit/team/reload_survey/img/V+_VR_SuperShotgun_storyboard.png | 64678 | REFERENCE — lane work |
| kit/team/reload_survey/scripts/decflow.py | 9876 | REFERENCE — lane work |
| kit/team/reload_survey/scripts/geo.py | 12889 | REFERENCE — lane work |
| kit/team/reload_survey/scripts/guns_cfg.py | 27341 | REFERENCE — lane work |
| kit/team/reload_survey/scripts/report.py | 11373 | REFERENCE — lane work |
| kit/team/reload_survey/scripts/sounds.py | 4351 | REFERENCE — lane work |
| kit/team/reload_survey/scripts/survey.py | 34955 | REFERENCE — lane work |
| kit/team/reload_survey/survey.json | 893402 | REFERENCE — BD22/V+ reload survey |
| kit/team/v9common.py | 40684 | REFERENCE — lane work |
| kit/team/v9src/CVARINFO.rsq | 363 | REFERENCE — lane work |
| kit/team/v9src/MENUDEF.bd22.rsq | 1018 | REFERENCE — lane work |
| kit/team/v9src/MENUDEF.vplus.rsq | 1009 | REFERENCE — lane work |
| kit/team/v9src/gen_gunmoves_bd22.py | 1032 | REFERENCE — lane work |
| kit/team/v9src/gunmoves_bd22.zs | 19329 | REFERENCE — lane work |
| kit/team/v9src/handler.zs | 2110 | REFERENCE — lane work |
| kit/tool/README.md | 8694 | doc |
| kit/tool/bd22_displayed.json | 286920 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/decsim.py | 13439 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/fill_tables.py | 18590 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/BrutalAxe.py | 4579 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/BrutalPistol.py | 2146 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/BrutalSMG.py | 6369 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/Chain_saw.py | 8379 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/DSweap.py | 2631 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/Flamethrower2.py | 2776 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/HellishMissileLauncher.py | 3084 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/MP40.py | 8135 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/Minigun.py | 6548 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/RailGun.py | 5959 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/Revolver.py | 2238 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/Rifle.py | 7178 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/Rocket_Launcher.py | 6526 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/SSG.py | 9161 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/Shot_Gun.py | 8007 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/Unmaker.py | 2867 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/gun_tables/__init__.py | 0 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/GRIP_REGIONS.md | 8606 | doc |
| kit/tool/hands/HAND_FITTING.md | 10029 | doc |
| kit/tool/hands/align.py | 3188 | KEEP — the original ICP fit, now runnable (Ermac guns staged) |
| kit/tool/hands/align_free.py | 5652 | USED (logic copied) — gun-free fit |
| kit/tool/hands/bladeinfo.py | 1427 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/ermac.py | 1521 | KEEP — Ermac pose table |
| kit/tool/hands/fit_pack_free.py | 2982 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/fitall.py | 2304 | KEEP — original fit driver |
| kit/tool/hands/fitall_free.py | 3254 | USED (logic copied) — wrap branch |
| kit/tool/hands/fits.json | 7444 | REFERENCE — BD22 shipped fits (ground truth) |
| kit/tool/hands/gripcheck.py | 1021 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/gripmeasure.py | 11858 | KEEP — measures a new hand pose's grip region |
| kit/tool/hands/gripregions.json | 136264 | USED — hand gripping faces (handfit_cards) |
| kit/tool/hands/gripsheet.py | 4895 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/guns.py | 2625 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/gunview.py | 7683 | USED — sheets, surface points |
| kit/tool/hands/handfit.py | 1519 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/handframe.py | 2014 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/handtable.py | 1464 | REFERENCE — BD22 pose assignments |
| kit/tool/hands/hudrender.py | 4519 | USED — model chain for sheets/fits |
| kit/tool/hands/hudview.py | 2027 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/minigun_fit.py | 2249 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/pk3model.py | 1469 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/regen_displayed.py | 1388 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/rtest/CVARINFO.txt | 27 | doc |
| kit/tool/hands/rtest/mk.sh | 671 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/rtest/vrhand_fake.zs | 2700 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/hands/support.py | 4231 | USED (logic copied) — front_point/section |
| kit/tool/hands_blocks.py | 3046 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/md3_carve_surface.py | 17994 | KEEP — carve by slab/cylinder (weld + lens work) |
| kit/tool/md3_extract.py | 5999 | KEEP — pull surfaces out |
| kit/tool/md3_quad.py | 4526 | KEEP |
| kit/tool/md3strip.py | 3479 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/melee/bladeinfo.py | 1676 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/melee/handframe.py | 2014 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/melee/regen_displayed.py | 1380 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/pose_axis.py | 617 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/pose_tables.py | 6127 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/quickpack.sh | 657 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/restore_and_strip.py | 21793 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/restore_and_strip_v3.py | 10376 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/rsq_hands_gen.py | 9496 | REFERENCE — BD22 hand table generator (ours: handfit_cards) |
| kit/tool/verify_pk3.py | 14062 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/build_vplus.py | 5836 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/fit/board.py | 839 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/fit/gripcmp.py | 1052 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/fit/meshsig.py | 775 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/fit/sawfit.py | 2666 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/fit/vfit.py | 2365 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/fit/vfits.json | 3377 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/fit/vplus.py | 2171 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/fit/vsheets.py | 2507 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/fit/xsec.py | 2043 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/rtest/mk.py | 882 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/rtest/run.sh | 442 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/rtest/testlog.zs | 2196 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/rtest/vrhand_fake.zs | 1421 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/vfits.json | 3377 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vplus/vplus_patch.py | 7114 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee/CVARINFO.rsq | 543 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/MAPINFO.rsvr | 185 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/MENUDEF.rsq | 1276 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/MODELDEF.rsq | 4662 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/SURFACES.rsq | 2342 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/ZSCRIPT.rsvr | 452 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/LICENSE_RustedLegacy_MIT.txt | 1086 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/ammo_hand.md3 | 102784 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/berettam9.jpg | 21632 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/hand.md3 | 102784 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/hand2.md3 | 69888 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/mag_chaingun.md3 | 22908 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/mag_pistol.md3 | 43604 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/mag_plasma.md3 | 7628 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/pod_rocket.md3 | 20776 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/shot_shell.md3 | 1828 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/models/rsq/shot_shell2.md3 | 3548 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/zscript/rsq/ballistics.zs | 10621 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/zscript/rsq/guns.zs | 2960 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/zscript/rsq/hands.zs | 6336 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/zscript/rsq/handtable.zs | 5701 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/zscript/rsq/reload.zs | 9737 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/zscript/rsvr/common.zs | 511 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/zscript/rsvr/melee.zs | 15511 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee/zscript/rsvr/vrhand.zs | 1757 | REFERENCE — melee lane pack source |
| kit/tool/vrmelee_v8_backup/CVARINFO.rsq | 543 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/MAPINFO.rsvr | 185 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/MENUDEF.rsq | 1276 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/MODELDEF.rsq | 4662 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/SURFACES.rsq | 2342 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/ZSCRIPT.rsvr | 387 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/models/rsq/LICENSE_RustedLegacy_MIT.txt | 1086 | doc |
| kit/tool/vrmelee_v8_backup/models/rsq/ammo_hand.md3 | 102784 | asset |
| kit/tool/vrmelee_v8_backup/models/rsq/berettam9.jpg | 21632 | asset |
| kit/tool/vrmelee_v8_backup/models/rsq/hand.md3 | 102784 | asset |
| kit/tool/vrmelee_v8_backup/models/rsq/hand2.md3 | 69888 | asset |
| kit/tool/vrmelee_v8_backup/models/rsq/mag_chaingun.md3 | 22908 | asset |
| kit/tool/vrmelee_v8_backup/models/rsq/mag_pistol.md3 | 43604 | asset |
| kit/tool/vrmelee_v8_backup/models/rsq/mag_plasma.md3 | 7628 | asset |
| kit/tool/vrmelee_v8_backup/models/rsq/pod_rocket.md3 | 20776 | asset |
| kit/tool/vrmelee_v8_backup/models/rsq/shot_shell.md3 | 1828 | asset |
| kit/tool/vrmelee_v8_backup/models/rsq/shot_shell2.md3 | 3548 | asset |
| kit/tool/vrmelee_v8_backup/zscript/rsq/ballistics.zs | 10621 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/zscript/rsq/hands.zs | 6273 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/zscript/rsq/handtable.zs | 4971 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/zscript/rsq/reload.zs | 11654 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/zscript/rsvr/melee.zs | 15908 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/vrmelee_v8_backup/zscript/rsvr/vrhand.zs | 1757 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/tool/weapon_patch.py | 20414 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/v7x/MODELDEF.bd.txt | 350088 | doc |
| kit/v7x/models/bd/AssaultShotgun/AssaultShotgun.md3 | 1361872 | asset |
| kit/v7x/models/bd/AssaultShotgun/AssaultShotgun.png | 376937 | asset |
| kit/v7x/models/bd/AssaultShotgun/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/BFG/BFG.md3 | 950264 | asset |
| kit/v7x/models/bd/BFG/BFG.png | 239547 | asset |
| kit/v7x/models/bd/BFG/BFG_10k.md3 | 950264 | asset |
| kit/v7x/models/bd/BFG/BFG_10k.png | 249483 | asset |
| kit/v7x/models/bd/BFG/BFG_10k2.png | 251117 | asset |
| kit/v7x/models/bd/Boot/Boot.md3 | 3447756 | asset |
| kit/v7x/models/bd/Boot/Boot.png | 292551 | asset |
| kit/v7x/models/bd/BrutalAxe/BrutalAxe.md3 | 160332 | asset |
| kit/v7x/models/bd/BrutalAxe/BrutalAxe.png | 408784 | asset |
| kit/v7x/models/bd/BrutalPistol/BrutalPistol.md3 | 1454988 | asset |
| kit/v7x/models/bd/BrutalPistol/BrutalPistol.png | 261594 | asset |
| kit/v7x/models/bd/BrutalPistol/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/BrutalSMG/BrutalSMG.md3 | 3926372 | asset |
| kit/v7x/models/bd/BrutalSMG/BrutalSMG.png | 111989 | asset |
| kit/v7x/models/bd/BrutalSMG/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/Chain_saw/Chain_saw.md3 | 14382624 | asset |
| kit/v7x/models/bd/Chain_saw/Chain_saw.png | 350217 | asset |
| kit/v7x/models/bd/DSweap/DSweap.md3 | 1015456 | asset |
| kit/v7x/models/bd/DSweap/DSweap.png | 240469 | asset |
| kit/v7x/models/bd/FIST/fist.png | 246015 | asset |
| kit/v7x/models/bd/FIST/fistclosed.md3 | 2125548 | asset |
| kit/v7x/models/bd/FIST/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/FlameCannon/FlameCannon.md3 | 397136 | asset |
| kit/v7x/models/bd/FlameCannon/FlameCannon.png | 232215 | asset |
| kit/v7x/models/bd/Flamethrower2/Flamethrower2.md3 | 377984 | asset |
| kit/v7x/models/bd/Flamethrower2/Flamethrower2.png | 367633 | asset |
| kit/v7x/models/bd/Grenade/nade.md3 | 643356 | asset |
| kit/v7x/models/bd/Grenade/nade.png | 111147 | asset |
| kit/v7x/models/bd/Grenade/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/HellishMissile/HellishMissile.md3 | 149956 | asset |
| kit/v7x/models/bd/HellishMissile/HellishMissile.png | 492978 | asset |
| kit/v7x/models/bd/HitlersBuzzsaw/HitlersBuzzsaw.md3 | 748332 | asset |
| kit/v7x/models/bd/HitlersBuzzsaw/HitlersBuzzsaw.png | 354693 | asset |
| kit/v7x/models/bd/M32/m32.md3 | 159772 | asset |
| kit/v7x/models/bd/M32/m32_tex1.png | 71282 | asset |
| kit/v7x/models/bd/M32/m32_tex2.png | 134810 | asset |
| kit/v7x/models/bd/M79/M79.md3 | 1561388 | asset |
| kit/v7x/models/bd/M79/M79.png | 318658 | asset |
| kit/v7x/models/bd/M79/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/MP40/MP40.md3 | 655876 | asset |
| kit/v7x/models/bd/MP40/MP40.png | 234734 | asset |
| kit/v7x/models/bd/MP40/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/Minigun/Minigun.md3 | 683736 | asset |
| kit/v7x/models/bd/Minigun/Minigun.png | 423626 | asset |
| kit/v7x/models/bd/Nuker/Nuker.md3 | 486444 | asset |
| kit/v7x/models/bd/Nuker/Nuker.png | 452970 | asset |
| kit/v7x/models/bd/Plasma_Gun/Plasma.md3 | 1746220 | asset |
| kit/v7x/models/bd/Plasma_Gun/Plasma.png | 380855 | asset |
| kit/v7x/models/bd/Plasma_Gun/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/RPG/RPG.md3 | 2197328 | asset |
| kit/v7x/models/bd/RPG/RPG.png | 215452 | asset |
| kit/v7x/models/bd/RPG/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/RailGun/RailGun.md3 | 2064964 | asset |
| kit/v7x/models/bd/RailGun/RailGun.png | 589709 | asset |
| kit/v7x/models/bd/RailGun/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/Revolver/Revolver.md3 | 3271648 | asset |
| kit/v7x/models/bd/Revolver/Revolver.png | 360269 | asset |
| kit/v7x/models/bd/Revolver/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/Rifle/M203.md3 | 1172124 | asset |
| kit/v7x/models/bd/Rifle/M203.png | 284447 | asset |
| kit/v7x/models/bd/Rifle/Rifle.md3 | 2463220 | asset |
| kit/v7x/models/bd/Rifle/Rifle.png | 243614 | asset |
| kit/v7x/models/bd/Rifle/m203_round.md3 | 9620 | asset |
| kit/v7x/models/bd/Rifle/m203_round.png | 78 | asset |
| kit/v7x/models/bd/Rifle/m203_spent.md3 | 9620 | asset |
| kit/v7x/models/bd/Rifle/m203_spent.png | 78 | asset |
| kit/v7x/models/bd/Rifle/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/SSG/SSG.md3 | 7115380 | asset |
| kit/v7x/models/bd/SSG/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/SSG/ssg.png | 365851 | asset |
| kit/v7x/models/bd/ShotGun/Shotgun.md3 | 5655952 | asset |
| kit/v7x/models/bd/ShotGun/Shotgun.png | 285797 | asset |
| kit/v7x/models/bd/ShotGun/rsr_clear.png | 72 | asset |
| kit/v7x/models/bd/Sidewinder/sidewinder.md3 | 570580 | asset |
| kit/v7x/models/bd/Sidewinder/smr.png | 585360 | asset |
| kit/v7x/models/bd/Sidewinder/smr_ext1.png | 30768 | asset |
| kit/v7x/models/bd/Sidewinder/smr_plate.png | 65336 | asset |
| kit/v7x/models/bd/Unmaker/Unmaker.md3 | 1811888 | asset |
| kit/v7x/models/bd/Unmaker/Unmaker.png | 475065 | asset |
| kit/vplus/board.py | 839 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/gripcmp.py | 1052 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/meshsig.py | 775 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/pk3/zscript/rsq/handtable.zs | 3641 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/rtest/mk.py | 882 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/rtest/run.sh | 442 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/rtest/testlog.zs | 2196 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/rtest/vrhand_fake.zs | 1421 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/sawfit.py | 2666 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/vfit.py | 2365 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/vfits.json | 3377 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/vplus.py | 2171 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/vsheets.py | 2507 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
| kit/vplus/xsec.py | 2043 | REFERENCE — lane tooling (hands/gun_tables/vplus/melee duplicates of tool/hands; vrmelee_v8_backup = backup) |
