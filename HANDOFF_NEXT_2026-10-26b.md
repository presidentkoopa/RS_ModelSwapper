# ModelSwapper 2.0 — handoff, 2026-10-26 (b) (branch `modelswapper-2.0-bd22-lift`)

Lane A's pass on `HANDOFF_NEXT_2026-10-26.md`. Read that one first: it has the owner's four headset
findings. This one says what changed since. `main` is untouched.

Mantra: **their code, our models, collective reload.** All of it is ZScript/data on a stock QuestZDoom 17.3.

## 0. Read this before trusting any older rig result

The shared rig at `rsq_weapondepot/tools/rig/bin` **was not QuestZDoom 17.3**. Its engine said 4.15pre and
its ZScript said 4.12. The pack did not even compile there (`Wads.GetLumpContainer`, which 17.3 has).
The rig is now in this repo at `gate/qz_rig/`, built from emawind84/gzdoom `qzd17.3` (9afc750) and
questzdoom a85c819. Its launcher `gate/qz_rig/bin/qz` refuses any other engine. `run_gate.py --vr` FAILs
unless it sees the launcher's `qz: engine OK` line. Any result from the old bin/ is void.

Every engine launch takes `flock -o -x|-s /home/claude/rig.lock`. The rig is shared with Lane B.
Without `-o`, an orphaned Xvfb kept the lock and stalled everyone.

## 1. Done (measured, rig-proven)

### Finding 3: M79 support hand "detached" (FIXED)
* **Cause.** On BD22's own `GrenadeLauncher`, ModelSwapper binds **MS_BD_M79** by default, not
  MS_BD22_M79 (rig, `autopick`). MS_BD_M79 draws the same `M79.md3`, shifted by its Offset onto
  identical vertices (0.00000 m in the controller frame). Its hand row (slot 7) came from the older
  card fit. Measured against BD22Q 1.92's pose: gun hand 8.6 cm off, support hand 9.0 cm off. The
  gun hand sat above the stock and the support hand at the muzzle.
  MS_BD22_M79 itself always matched 1.92 number for number. The hand row, GunMoves, the RSB row and
  the mesh were all checked.
* **Fix.** `tools_kit/twin_hands.py`: a shelf donor that draws every vertex of a lifted MS_BD22_ gun
  (all Model N on their frames, within 0.5 mm, same Scale-x sign) takes that gun's hand slot.
  It found 14 twins: BD_ AssaultShotgun, BrutalSMG, M79, RailGun; brt_ AssaultShotgun, BrutalSMG,
  PlasmaGun, RPG, Revolver, SSG; d64_ PlasmaGun, RPG, ShotGun, SSG. Five of them had no hand row at
  all before (brt_AssaultShotgun, brt_Revolver, brt_SSG, d64_ShotGun, d64_SSG).
* **Stale lifted rows.** Three lifted rows matched no BD22Q release: AssaultShotgun, Revolver and
  Ruger. They were re-copied with `lift_bd22.py --hands <BD22Q src> [gun]`; AssaultShotgun and
  Revolver now come from 1.92. The Ruger comes from 1.97, because the XM21 is a 1.97 mesh and 1.92's
  Sniper draws the M16. All 13 lifted rows now equal 1.92 / 1.97 / current BD22Q field for field.
* **BD22 Rifle drew no M203.** Its donor block had a FrameIndex row for Model 0 only, so the support
  hand (BD22Q's, which holds the tube) held air: 5.85 cm from the gun. `lift_bd22.py` now writes a
  row per model (`rest_rows`, `--rest-rows`); the gap is now 0.79 cm. 16 zion_ multi-part blocks have
  the same pattern (see Open).
* Shots (rig eye, side view, BD22's own guns, steadied):
  `/home/claude/lane_a_out/report/m79_BEFORE_default_MS_BD_M79_vs_192.png`,
  `/home/claude/lane_a_out/report/m79_AFTER_default_MS_BD_M79_vs_192.png` (left is 1.92, right is
  ModelSwapper). The other twins are in `twins_BEFORE_*.png` / `twins_AFTER_*.png`. The stale rows are
  in `stale_rows_BEFORE.png` / `stale_rows_AFTER.png`. The rifle is in `rifle_no_M203_BEFORE.png`.

### Finding 1: held parts in a foreign off hand (VERIFIED, gate closed)
* The gate's rtest driver prints `HELD` lines: layers 2201 / 2202 / 2203 / 2210 with their caller,
  plus the off-hand weapon. **Every** reload kind now needs its part (magazine, round or shell) drawn
  by the off-hand weapon, not just the `--offknife` case.
* `--offknife` (a mod's +OFFHANDWEAPON knife in the off hand) on **4227925, the owner's build:
  FAIL** for magazine, pump and break-open. On this branch: **PASS** for all three.
* On BD22 itself: MS_BD22_M79 on BD22's GrenadeLauncher shows the grenade round in the off hand
  (`2202 …@rsq_hands`); MS_BD22_Rifle on BD22's Rifle shows the magazine (`2201 RQRP/A@rsq_hands`).

### Finding 2: off hand = the fist, unless the player moves a weapon there (DONE, look unchanged)
* `KEYCONF`: `addslotdefault 1 RSQ_Hands`, as BD22Q 1.5+ does. After `switchhand 1`, weapnext 1 /
  weapprev 1 brings the fist back. Slot 1 in the main hand is still the mod's melee, since RSQ_Hands
  can't enter the main hand. Rig: BD22 and doom2.
* `hands.zs`: the take-back rule used to read "no Reload state" as "the mod's own off-hand item". A
  vanilla Pistol has no Reload state either, so on doom2 a pistol moved to the off hand was taken
  back 2 tics later. Now only a weapon that is off-hand **by its defaults** (+WEAPON.OFFHANDWEAPON) is
  replaced. A weapon the player moved there stays.
* Look: the idle off hand is Ermac's fist, identical to 1.92's (`offhand_idle_192_vs_MS.png`).

### Gate blind spot, finding 3: "hands on the gun"
`tools_kit/hand_gap.py` works from the tables the engine reads (MODELDEF, RSQ_HandTable,
MODELDEF.rsq, RenderHUDModel's chain). It checks two things:
* Each hand's closest approach to the gun must be ≤ 1.5 cm.
* For a twin of a lifted gun, each hand centre must be within 2 cm of BD22Q's.

`run_gate.py` checks it for every kind. MS_BD_M79 on 4227925 FAILS (8.6 / 9.0 cm) and passes now.
Over all 77 hand slots, these are over: MS_BD_Flamethrower2 (gun 4.6), MS_Chainsaw (4.1 / 2.6),
MS_RocketLauncher (support 2.2), chex large / superlarge zorcher (5.3 / 3.8). They are all card fits,
all on the rig (`outliers_card_fits.png`), and still open.

### Engine crash (FIXED)
`RSQ_Scope.Basis` took three `out Vector3` parameters. QZD 17.3's VM interpreter I_Errors on that
("REGT_ADDROF not implemented for vectors"). Quest has no JIT, so the first frame with BD22's RailGun
or Sniper in hand closed the game. Basis now returns the vectors. Rig: all 13 BD22 guns selected in
turn, with no crash. The "Unexpected JIT error" in every older gate log was this.

### Gate: real input only
* A magazine reload starts with `+reload` (R grip + R stick down on Quest; the mod's own
  A_WeaponReady(WRF_ALLOWRELOAD)). `--by-fire` keeps the trigger-on-empty path.
* An audit of the drivers on `--vr`: they write controllers (qzt_*), buttons, view pitch and the test
  gun's ammo. No reload state is written; break_test's Seat/StartClose shortcut only runs off the rig.
* `--noallow`: a gun whose Ready never allows reload. The button does nothing (that is the mod's rule;
  a player can't either), and firing it empty reloads.
* `--mod bd22:<Class>` and `--mod doomablo:<Class>` gate a real mod's own weapon.

### Still-open items from before
* **KAR98** has a hand row now, fitted by `handfit_cards.py`'s own fit (its paths can now be set with
  MS_GRIPREGIONS / MS_ERMAC_HANDS). The same script reproduces the shipped wolf_MP40 and wolf_Garand
  rows to the last digit. Gap: 0.04 / 0.07 cm.
* **brt_AssaultShotgun** has hands (a twin of MS_BD22_AssaultShotgun).
* **Four shelf RPGs** pushed the rocket 1.64 units. WMCARD.shelf had taken the first mag_in window
  (the recoil twitch). Those four blocks were re-made by `run_shelf_cards.py` (longest window: 4.81,
  the same as MS_RocketLauncher's own row) and spliced in. `regen_rows.py` changed rsr rows 58-61 only.
  WMCARD.shelf was not regenerated whole, because that would also move wolf_Shotgun, voxel_SSGD4 and
  the BrutalPistols. That needs its own pass.
* **The 9 old `_wm` rows** were checked by measurement and left as they are: no magazine moves
  anywhere in their meshes. Their hands: BD_Unmaker, MG_Bolter and MG_Tec9 touch the gun.
  BD_Flamethrower2's gun hand is 4.6 cm off (open). The brt_/meat_ copies have no hand row.

### DoomAblo 0.9.1a smoke (doom2 -> doomablo -> pack; no BD_VoxelPack, the mod's README names none)
* Loads with no script error from the pack. The scan lists 29 weapons, and all 14 DoomAblo guns
  bind a model (rig).
* VR reload on its own 7 magazine guns (whose default models have reload rows): rwPistol, rwShotgun,
  RwAssaultRifle, RwGrenadeLauncher, RwPlasmaRifle and RwRailgun PASS. **RwRocketLauncher FAILS on "hands on the gun" only**: its default donor
  MS_RocketLauncher has a card-fit support hand 2.2 cm off the tube. Its reload itself ran.
  RwRailgun PASS (6 of 7). Its magazine is a field (`currentClipAmmo`), so the gate fires it
  dry as a player would.

## 2. Gate on the final build (`/home/claude/lane_a_out/ms_final.pk3`, = branch head)

QuestZDoom 17.3 rig (`gate/qz_rig`), `run_all.py --vr` in halves, run under the lock:
* Half 1: **36 of 37 PASS**. The one FAIL is MS_BD_Flamethrower2, on the new hand check (gun hand 4.6 cm).
* Half 2: **33 of 37**, then **34 of 37** after MS_Revolver was re-run. MS_Revolver had been a timing
  miss: the round took three pushes and the gun shut at t522, past the 520 end, so break-open now runs
  900 tics, and it PASSes with that. The remaining FAILs are MS_RocketLauncher and the two chex
  zorchers, all on the hand check.
* **Total: 70 of 74.** All 4 FAILs are the card-fit pose outliers, caught by the new
  "hands on the gun" check. Every reload passes.

Desktop: QZD 17.3 built here, `run_all.py`.
* **64 of 74**, then **70 of 74** after the round-in-the-off-hand check was made rig-only and the 6
  break-open donors were re-run. That check is rig-only because the desktop's break driver seats
  chambers itself, so no hand carries a round. All 6 PASS. The same 4 hand outliers FAIL.

Extra cases (`/home/claude/lane_a_out/extra_gates.txt`):
* BD22's own guns: MS_BD22_M79 on GrenadeLauncher, MS_BD22_Rifle on Rifle: PASS.
* `--offknife` magazine / pump / break-open: PASS.
* `--noallow` by button: FAIL, by design; by fire: PASS.
* brt_ / d64_ / hdvr_ / vplus_RPG, wolf_KAR98, brt_AssaultShotgun: PASS.
* DoomAblo: rwPistol, rwShotgun, RwAssaultRifle, RwGrenadeLauncher, RwPlasmaRifle and RwRailgun PASS.
  RwRocketLauncher FAILs on the hand check only: MS_RocketLauncher's support hand is 2.2 cm off.

Before the fixes, on 4227925 (the owner's build): `--offknife` FAIL for all three kinds; MS_BD_M79's
hands 8.6 / 9.0 cm off BD22Q's pose.

## 3. Not done
* The 5 card-fit pose outliers above (Flamethrower2, Chainsaw, RocketLauncher, the two chex zorchers).
  They need a re-fit with the owner's toolkit (`RS_QuestHands/tools/posefix/hands`; `minigun_fit.py`'s
  `rot_hook` for the chainsaw handle), then a rig shot each.
* Owner correction: no new models were converted (item 6 dropped).
* DoomAblo's rwRevolver (MS_Revolver, break-open) and the pump / no-row guns were selected and bind,
  but were not gated through a reload on DoomAblo.
* The desktop gate needs `gl_portals 0`. This container's desktop QZD 17.3 (Mesa llvmpipe) segfaults
  in `HWSkyPortal::DrawContents` at MAG_OUT; the owner's 4227925 does the same. Not seen on the rig.

## 4. Open
* 16 zion_ multi-part donor blocks have FrameIndex rows for Model 0 only, so their extra parts (CG
  barrel, BFG orb, ...) are never drawn. They are not BD22 lifts; the fix belongs to whatever wrote
  those blocks.
* WMCARD.shelf as a whole (see the RPGs above).
* `ms_off_fist` (Options) is still there. Finding 2 removes the need for a mod-knife exception, but
  removing the option is the owner's call.

* **MS_BD_M79 (the default on BD22's GrenadeLauncher) has its hands now but no break-open reload row**
  (only MS_BD22_M79 does), so by default that gun reloads the mod's stock way with the hands on it.
  MS_BD22_M79 picked in the menu gets the VR break-open. Making the twin reload too (pointing
  RSB_Guns.SlotForDonor at slot 6, plus MODELDEF.bd22's layer blocks re-keyed to MS_BD_M79) is the same
  move as the hands; the same is true for the twins' magazine rows (they keep their own card rows).
  Not done without the owner's yes (see question 6).

## 5. Owner questions (not decided here)
1. **Pump timing:** the whole tube at once (the mod's reload first, then the hands push the same
   count), or one push per pass of the mod's loop, as now?
2. **Break-open order:** the mod's reload first and the gun held, as for magazines, or hands first,
   as now?
3. **Grip-mode charging handle:** should "Grab ammo with: grip" be allowed to take a charging handle?
   BD22Q's rule makes a grip near the gun steadying, never a grab.
4. **Finding 2's look:** the off hand is Ermac's fist (BD22Q's), identical to 1.92. Is that the
   "Offhand Fist" you meant, or BD22's own 2D off-hand fist sprite?
5. **5 pose outliers:** re-fit them with your toolkit here, or do you want them yourself?
6. **Twins' reloads:** should a shelf model drawn exactly like a lifted BD22Q gun also take that gun's
   reload rows (e.g. MS_BD_M79 -> BD22Q's break-open), or should the default model on BD22's own guns
   simply be the MS_BD22_ one?

---

# Round 2 (2026-10-26, Lane A)

The owner's four decisions of 2026-10-26, in order. Branch `modelswapper-2.0-bd22-lift`, `main` untouched.
Final build: `/home/claude/lane_a_out/ms_r2_final.pk3` (= branch head before this handoff). The rig is
QuestZDoom 17.3 (`gate/qz_rig`, "qz: engine OK" in every log).

## 1. Done (measured, rig-proven)

### Item 1: break-open reload order, the mod's reload first (057a2f4)
* *Reload Order* (`ms_mod_first`, default *Mod's reload first*) now covers break-open guns (SSG, M79,
  revolvers) as well as magazines. At the press, the hands' break reload starts and the mod's own reload
  runs straight away, moving its own ammo. The gun is parked where that reload ends (no A_WeaponReady,
  so no fire) until the hands have opened the gun, loaded it and shut it. *Hands first* is unchanged.
  `RSB_State.paid`: once the mod has paid for the rounds, its emptied reserve doesn't stop the hand's grab.
* **Bug found and fixed:** `ms_donor_main` is a `server` cvar, so a value set from script arrives through
  the net queue a tic later (`D_SendServerInfoChange`, DEM_SINFCHANGED, read in the 17.3 source). If BD22's
  GrenadeLauncher was fired dry the same tic it came up, the join took it under the *previous* gun's model.
  The log showed "took GrenadeLauncher (slot 17)", which is MS_alien_rifle: a magazine reload on the M79.
  The join now waits until the cvar matches the model handler.
* Gate: break-open checks *fire held for hands*. The gate fires BD22's SSG dry, because its `SSGLoaded`
  flag makes an emptied count read as loaded (SSG.dec:383).
* Rig PASS: MS_SuperShotgun in both orders, MS_Revolver, MS_BD22_SSG, MS_BD22_SSG on `bd22:SSG`,
  MS_BD22_M79 on `bd22:GrenadeLauncher`. Log: `/home/claude/lane_a_out/r2/item1.txt`.

### Item 2: pump, *Shells per grab* 1-4 (f3372ad)
* *Shells per grab* (`ms_shell_grab`, default 1, the same as before). One grab takes that many shells,
  capped by the reserve and by the room left in the tube, and each push counts. Shells 2-4 are drawn on
  layers 2211-2213 beside the held one, parallel and touching. Their direction was measured on Ermac's
  one-shell hold (`tools_kit/shell_stack.py` -> `rsp_stack.ms.zs`): each added shell touches the hand and
  none sits deeper in it than the held shell. The spacing is each gun's own shell diameter (2.395 / 2.191 /
  2.021 cm). If the hand lets go, every shell falls.
  Render: `/home/claude/lane_a_out/report/shells_per_grab.png`.
* **How a mod loads its tube** is read from the mod's own reload the first time each class reloads, then
  kept for the session. QZD 17.3's static build has no label table, so the run itself is the evidence:
  * if the psprite goes back to an earlier state of its reload for the next shell, the mod loads **one
    shell per pass** and the hand paces it shell by shell;
  * if more than one shell goes in during one pass, or one goes in and the reload ends, it loads the
    **whole tube**: the mod's reload runs first, and the gun can't fire until the hand has pushed that
    many shells.
  * **Per donor (rig):** BD22 `Shot_Gun` (its InsertingShells loop) is one per pass. DoomAblo `rwShotgun`
    (A_MagazineReload) is whole tube. Test mod: `TMShotgun` one per pass, `TMShotgunW` (new) whole tube.
* The join's reload window now ends at the next standard label after `Reload:`. It used to be a fixed 32
  states, but BD22's Shot_Gun reaches its first tic about 45 states in, so the join never took it on the rig.
* Rig PASS: BD22 Shot_Gun one per pass with grab 1 and grab 4; DoomAblo rwShotgun whole tube with grab 1
  and grab 4. Desktop PASS: TMShotgun grab 1 and 4; TMShotgunW grab 1 and 4.
  Logs: `/home/claude/lane_a_out/r2/item2.txt` and `*.log` beside it.

### Item 3: the hand-pose outliers, minimal re-fit (791eaf2)
`tools_kit/refit_outliers.py` uses handfit_cards.py's own method: Ermac's pose is kept, and his measured
gripping face is translated onto the gun by trimmed ICP, starting from where the hand is drawn now. Only a
hand that fails is touched. hand_gap in cm (gun hand / support):
| model | before | after |
|---|---|---|
| MS_BD_Flamethrower2 | 4.64 / 0.03 | 0.09 / 0.03 |
| MS_RocketLauncher (DoomAblo RwRocketLauncher) | 0.02 / 2.17 | 0.02 / 0.16 |
| MS_Chainsaw | 4.10 / 2.58 | 0.06 / 0.04 |
| MS_chex_largezorcher | 5.29 / 3.81 | 0.04 / 0.05 |
| MS_chex_superlargezorcher | 5.30 / 3.57 | 0.04 / 0.05 |
Renders: `/home/claude/lane_a_out/report/refit_<model>.png`. The renders show that the zorchers' gun hand
now touches the top of the body rather than the arc grip below it. It is on the gun but not yet a real
grip; that is left for the FBX fitter, as asked.

### Item 4: the 16 zion_ blocks with the missing frame row (1af94d9)
`tools_kit/part_rows.py` adds a FrameIndex row for each extra model on the same sprite and frame, but only
where it measures that the part belongs there: every triangle island of the part must chain back to the
gun through gaps of 3.5 mesh units or less. 15 blocks now draw every part. Renders, before and after, plus
a contact sheet: `/home/claude/lane_a_out/report/zion_parts/`.
**Not written, measured:** MS_zion_D4SUPERSHOTGUN's shells (SuperShotgunShells.md3). At the rest frame 62,
6 pieces sit 20.4-23.4 units below the gun; they only reach it from frame 95, during its reload. That block
stays as it was. None of the zion_ models has a hand row, so they draw no hands either way.

## 2. Gate on the final build
Pack `/home/claude/lane_a_out/ms_r2_final.pk3`, sha256 `15fd55781d276abac6ceed95bff13c048cbf8840adae88ee464e79a5d9fadea6`. It is built from f3372ad; the
commit after it changes only the gate and docs.
* **Rig, half 1: 37 of 37 PASS.** MS_BD_Flamethrower2 (round 1's FAIL) now passes.
* **Rig, half 2: 36 of 37**, then **37 of 37** after a re-run. MS_RocketLauncher and both chex zorchers
  (round 1's FAILs) pass. MS_BD22_M79's round was never seated during the batch.
* **Desktop: 74 of 74 PASS.**
* **Extras: 11 of 13**, then **13 of 13** after the re-gate. Covered: hands-first SSG, bd22:SSG,
  bd22:GrenadeLauncher, bd22:Shot_Gun one per pass with grab 1 and 4, DoomAblo rwShotgun whole tube with
  grab 1 and 4, test-mod whole tube with grab 4, DoomAblo RwRocketLauncher (round 1's FAIL), bd22:Rifle, and
  `--offknife` for magazine, pump and break-open.
* **Triage of the 3 FAILs.** Neither was a code regression.
  * *MS_BD22_M79 not seated* is rig load. On the M79 the item-1 commit seated, HEAD with the item-1 join
    seated, and so did the final pk3 at load 1.35. The final pk3 failed 3 of 3 at load ~2.5, while other
    lanes were running engines. The rig's scripted wrist search misses frames under load (round 1 saw the
    same with MS_Revolver).
  * *"their reload ran" on bd22:SSG and bd22:GrenadeLauncher* was a **gate bug**. With the mod's reload
    first, the mod refills before the hands give the gun back, but the check only looked for the refill
    after the give-back. It now looks after the join took the gun.
  * Re-gate on the same pk3, at load 1.2-1.9: bd22:SSG (both orders), bd22:GrenadeLauncher, MS_BD22_M79,
    MS_brt_M79, MS_BD22_SSG, MS_SuperShotgun, MS_BD22_Revolver and MS_Revolver all PASS (9 of 9).
* Logs: `/home/claude/lane_a_out/r2/` (`final_*.txt`, `regate.txt`, `item1.txt`, `item2.txt`).
* **Blocker to know about:** the shared rig gives false FAILs on held gestures when other lanes load the
  machine (load average above ~2). Gate under lower load, or run `-x` batches back to back.

## 3. Not done
* The SSG shells above (a reload-only part; drawing them at rest would hang them in the air).
* Shells per grab on break-open guns: not asked for (the SSG already takes a pair).

## 4. Open (owner calls, unchanged)
* Grip mode taking a charging handle (BD22Q's rule makes a grip near the gun steady it, never grab).
* Is Ermac's fist the "Offhand Fist" you meant, or BD22's own 2D off-hand fist sprite?
* (Round 1's question 6, the twins' reloads, still stands.)
