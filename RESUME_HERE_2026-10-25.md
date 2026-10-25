# RESUME HERE — ModelSwapper 2.0, 2026-10-25

A full VR reload ran on a mod we do not own. This file is the handover.

## What happened

    rsr t201  gun 15: IDLE -> EMPTY                     magazine leaves the gun
    [MSJOIN]  took RwPistol (slot 15) at its reload
    rsr t293  grip down (key 443), grabs (56 cm apart)  fresh one off the belt
    rsr t293  gun 15: EMPTY -> CARRY
    rsr t304  gun 15: CARRY -> INSERT
    rsr t352  sound wm/pistolet/magin (slot 5)          seats, with sound
    rsr t352  gun 15: INSERT -> SEATED -> DONE
    [MSJOIN]  gave RwPistol back (the mod's own reload runs)
    rsr t353  gun 15: DONE -> IDLE

`RwPistol` is Doomablo's. This pack knows nothing about Doomablo. It scanned the
mod cold, decided RwPistol was a pistol, put `MS_Pistol` on it, resolved that mesh
to reload slot 15, caught the weapon entering its own reload, took it, let the
hands work against a well measured off our own mesh, and handed it back.

## Commits, in order

    63d8669  it compiles at all (68 script errors -> 0)
    b7d5c27  the donor bridge carries live data
    4003281  the join written
    693ea18  the handover fires
    4cf7623  the reload runs
    a96d624  a full reload, end to end

Read those messages before changing anything — each names the fault it fixed and
why the fix is shaped the way it is.

## The pieces, and where they live

    zscript/RS_ForeignReload.zs      THE JOIN. Takes a mod's weapon at its reload,
                                     holds it while the hands work, hands it back.
    zscript/RS_ForeignModels.zs      PublishHandFacts now publishes the worn donor
                                     to ms_donor_main / ms_donor_off.
    zscript_depot/                   the reload runtime, decontaminated of BD22.
    MAPINFO                          registers RSQ_Handler, RSR_ReloadHandler,
                                     RSB_Handler, RSP_Handler. Without these the
                                     whole reload is inert.
    tools_kit/run_assemble.py        runs the Depot's assemble.py over our tree.
                                     ONE-WAY. Re-running aborts, which is correct.
    tools_kit/gen_pump.py/.gen_rsb.py  now emit the donor Index behind MODELSWAPPER
                                     (default off) plus Loaded/Cap/LoaderEmptyInHand.

## To test it

    pk3:  ModelSwapper-QUEST.pk3  (built by .\build.ps1 -Static)
    load: doom2.wad -> any mod (Brutal Doom is FINE) -> that pk3

In game:

    Options -> RS VR Weapons -> Reloading = VR
    Options -> RS VR Weapons -> Grab ammo with = OFF-HAND GRIP    <- CRITICAL
    Options -> Weapon Model Swap Program -> Choose Models -> MS_Pistol on a pistol

**That "Grab ammo with" row cost an hour.** vreload discards every grip press
unless `rsr_grab_with == 1`; the default is the off-hand trigger. Symptom: the
magazine drops out and nothing ever happens again.

Reloadable today (pistol family, measured): MS_Pistol, MS_AE_Pistol,
MS_alien_pistol, MS_MG_Bolter, MS_qvplus_guns, MS_vplus_guns.

## Headless harness

    E:\DOOMWork\tools\main_boottest\main_boottest.ps1
      -Zdl <an empty .zdl>  -NetEvent rs-fm-rescan
      -ExtraArgs '+set rs_fm_picks "RwPistol:pistol:0:0" +rsrtest_script 1
                  +rsr_debug 1 +rsr_grab_with 1'
      -ExtraFiles @(mod.pk3, ModelSwapper-QUEST.pk3, ms_rtest_overlay.pk3)

The overlay is built from the Depot's `tools/rtest` (fakehands.zs +
rsr_testdriver.zs + driver.zs, with `RSR_Handler` -> `RSR_ReloadHandler`), shipped
as `zscript_depot/rsvr/vrhand.zs`. Its `InVR` returns true for any player, which
is how hand code runs under `vr_mode 0`.

A peer lane's `run_set.sh` (C:\Users\Command\.claude\skills\gate-a-doom-mod\) is a
better rig: it resolves paths before cd, reads each gun's real AmmoType1, and
counts a marker PER GUN. Use it before claiming "N guns reload".

Two switches when something does nothing:

    ms_join_trace 1    why the handover declined, one line per state change
    rsr_debug 1        the reload's own phase transitions

## Next, in the order they are worth doing

1. **The owner tests it in the headset.** Nothing here substitutes for that. Every
   result above is a scripted hand in a log: the geometry is measured and real,
   how it FEELS to reach for is not knowable from here.
2. **The 24 carded guns with no reload code.** Six working pistols -> thirty guns,
   same generator run that is already proven.
3. **Fit the hands.** RSQ_HandTable is a stub (index 0 for every weapon) because
   BD22's table matched BD22's classes. `handfit_cards.py` + `gripregions.json`.
4. The 8 held magazine strokes (REVIEW_MAG_STROKE.md).
5. The 84 single-surface carve candidates. 9 are carved and rendered, but their
   parts are NOT magazines — barrel groups and breech blocks — and are unwired.

## Do not

- Load it with our own BD22Q pack. Two products, same job: BD22Q is Our Code/Our
  Models, ModelSwapper 2.0 is Their Code/Our Models. They share meshes on purpose
  and never co-load. Brutal Doom ITSELF is fine.
- Re-run `run_assemble.py` on an already-stripped tree. It aborts, and that abort
  is the signal the divorce from the 1.96b source is done.
- Trust a clean log. `script parsing took` is the only pass.
