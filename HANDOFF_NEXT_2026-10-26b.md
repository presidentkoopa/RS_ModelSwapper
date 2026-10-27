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

---

# Round 3 (2026-10-27, Lane A), time box cut to 30 min by the owner

Branch `modelswapper-2.0-bd22-lift`, on origin 6c26bdf. Build `/home/claude/lane_a_out/ms_r3_final.pk3`.

## 1. Done (measured)

### Shelf RPG rows: the drum's real seat travel, 18.41 units (was 4.81)
* Round 1's 4.81 was wrong as well. The shelf RPG (`models/bd/RPG/RPG.md3`, and the one mesh shared by
  d64/hdvr/vplus) reloads a **drum**: eight surfaces, round2..round9, that move as one rigid body
  (one transform per frame, checked to 0.05 units). Tracking one round (surf 7) follows it around the drum's
  twist-lock (rotation up to 75.7 deg), so its distance to the seat wobbles (9.12 -> 10.35 -> 5.94). The walk
  back then stopped at frame 32. The card's `mag_in 19..33` also ends one frame early: the drum is still
  0.31 out at 33 and seats at 34.
* Measured on the drum's joint centroid: the old drum is thrown out (50.37 units at f24), the new one appears
  at f25 as a pure translation of the seated pose (rotation 0.0), and it closes monotonically 18.41 -> 15.13
  -> 10.95 -> 8.21 -> 6.10 -> 4.31 -> 2.71 -> 1.26 -> 0.31 -> 0 (f25..f34). **Stroke 18.41**, axis
  (0.745, -0.660, -0.101) from the seat. Ceiling (well 5.17 + drum 25.06) holds. All four meshes give the same numbers.
* `tools_kit/mag_insertion.py`: `rigid_group` / `track_group` (surfaces that ride with the magazine as one
  body), a window extended to the frame the part rests at, and a cut at a one-frame swap jump (more than 3x
  every other step). **Only for multi-surface magazines**; a one-surface magazine measures exactly as before.
  Re-run over all 157 shelf cards: only the 4 RPGs changed in what was written. If WMCARD.shelf is ever
  regenerated whole, the tool would also move MS_Pistol2 (3.858 -> 3.855), both chex zorchers (38.32 -> 36.77)
  and zblood_shotgun (2.30 -> 2.74). They are multi-surface magazines too. Not reviewed; don't regen whole
  without looking at them.
* WMCARD.shelf: only the four blocks re-made (`run_shelf_cards.py`, spliced). `regen_rows.py --only` the
  four: rsr rows 58-61 only. MODELDEF.cards / SNDINFO.ms came out only reordered (same 186 blocks, same lines)
  and were restored.
* **Open on the RPGs:** the carved hand part `MS_*_RPG_mag.md3` is ONE round (surf 7, 230 verts), but the
  stroke is the drum's. The hand pushes a single rocket the drum's travel. Carving the whole drum group is the
  next step (carve_by_ref / md3_carve_surface over surfaces 5-12).

## 2. Not done (time box)
* **KAR98 / brt_AssaultShotgun hand rows:** nothing new needed. Round 1 already gave them rows. Re-measured
  today with `hand_gap.py` on the shipped tables: MS_wolf_KAR98 slot 74 (handfit_cards.py), gun 0.04 / support
  0.07 cm; MS_brt_AssaultShotgun slot 63 (twin of MS_BD22_AssaultShotgun), 0.07 / 0.03 cm.
* **The 9 `_wm` rows -> animated originals: BLOCKER, no original found.** None of the 9 blocks DRAWS a
  `_wm` mesh. Each already draws a multi-frame mesh, but its reload ROW still comes from the old `_wm` card,
  and none of the drawn meshes moves a magazine (round 1, md3label). Drawn now (frames / surfaces):
  BD_Flamethrower2 `models/hud/Flamethrower/Flamethrower2.md3` 6/3; brt_Flamethrower2 `models/bd/Flamethrower2` 6/3;
  BD_Unmaker `models/hud/Unmaker` 16/3; brt_Unmaker `models/bd/Unmaker` 16/3; brt_HitlersBuzzsaw `models/bd/HitlersBuzzsaw` 3/2;
  MG_Bolter `models/hud/Bolter` 5/2; meat_Bolter `models/meat/Bolter` 5/2; MG_Tec9 `models/hud/Tec9/tec9.md3` 6/4;
  meat_Tec9: **no Model block named MS_meat_Tec9 in `modeldef`** (`models/meat/TEC9/tec9.md3` 6/4 is on disk).
  Searched by name (flame*, unmaker*, buzzsaw*, bolter*, tec9*, mg42*; md3/iqm/fbx/blend/md2) in `models/` and
  `/mnt/user-data/uploads/DOOMWork` (plus the one archive there, the VR hands handover zip): 86 files. The
  most frames any copy has is 16 (Unmaker, also in blend/, depot_bd/, carved/); everything else is 1-8. Nothing
  has the owner's "dozens and dozens of frames", and nothing has a magazine that moves. **Needed from the
  owner:** where the animated originals of these 9 are (file names or folder). Until then the old rows stay,
  and they are flagged here, not kept silently.
* Full rig halves, desktop set and extras: **not run** on r3 (30-min box). Run on r3: the four RPGs only.
  Round 2's counts (rig 74/74, desktop 74/74, extras 13/13) are on r2_final and are **not re-proven** on r3.
  r3 differs from r2 only in rsr rows 58-61 and WMCARD.shelf's four RPG dofs.

## Gate on r3 (`/home/claude/lane_a_out/ms_r3_final.pk3`, sha256 ae562270cddbdaf47d26d0bf1a6f2d8d9ac4cbb72d34ecaac840e3f25b579ef1)
* Rig (QZD 17.3, under the lock, load 1.2-1.7): MS_brt_RPG, MS_d64_RPG, MS_hdvr_RPG, MS_vplus_RPG **4/4 PASS**.
  Log: row 58, CARRY -> INSERT (14.7 out) -> SEATED -> DONE.
* Desktop: the same four, **4/4 PASS**. Log: `/home/claude/lane_a_out/r3_rpg.txt` (the first desktop pass
  tracebacked because MS_DESKTOP_ENGINE wasn't set; re-run with it set).
* Owner's load order (doom2 -> brutal22test6 -> BD_VoxelPack -> r3), rig, `--mod bd22:Rifle` MS_BD22_Rifle:
  **no script error from the pack** (only BD_VoxelPack's own 3: sphere.txt:50, voxeldef.txt:66/72). First run
  FAIL at load 1.57 / 1.81; which check failed was not captured (the log was overwritten). Re-run at load 1.5:
  **PASS**, all 16 checks ok. Count it as unproven until a calm-load batch confirms it.
* Not run: the full rig halves, the desktop 74, the rest of the extras.

## 3. Owner answers (2026-10-27) and where they stand
* **(a) Grip may grab a charging handle: YES. Not implemented, next item.** It isn't small. A handle sits on
  the gun, inside `RSR.STEADY_RANGE`, and there the engine itself starts two-hand steadying on the grip press
  (`vreload.zs:99-113`, `GripCanGrab`; the `rsr_grip` event at ~1263 refuses the grab when steadied or
  within range). Plan: under rsr_grab_with 1, a grip press within grabradius of a gun's handle (the CHARGE
  phase, or a handle part) takes the handle, even inside STEADY_RANGE. While held, steadying is ignored for
  the handle part (we can't stop the engine steadying; check on the rig that the steadied pose doesn't fight
  the pull). Gate: a grip-mode handle case on MS_BD22_Rifle and MS_AE_Pistol with vr_two_handed_weapons 1.
* **(b) Off-hand fist:** dropped. FBX hands come later. Nothing changed.
* **(c) A mesh is just a mesh: reload rows belong to the mesh.** Audit, nothing changed:
  * All three tables are keyed by **donor name** (the MODELDEF block), not by mesh:
    `RSR_Guns.SlotForDonor` (rsr_guns.ms.zs:3067, 78 donors), `RSB_Guns.SlotForDonor` (rsb_guns.zs:37, 6),
    the pump table (rsr_pump_guns.zs:37, 4). The mod's class doesn't pick a row: the join uses the donor in hand.
  * Result: the same mesh under two donor names reloads differently. MS_BD_M79 and MS_BD22_M79 draw the
    same M79.md3, but only MS_BD22_M79 has the break-open row. The 14 twins (twin_hands.py) share hands
    but keep their own reload rows. brt_RPG / d64_RPG are twins of MS_BD22_RocketLauncher, yet they have card
    rows 58/59 while BD22_RocketLauncher has the lifted BD22Q row. hdvr_ / vplus_RPG are the same mesh FILE
    as d64_RPG at a different placement (+5 Z), so they aren't "drawn identically" and get separate rows.
  * **Class-keyed:** `rsr_m203.zs:47-55` `IsRifle` / `IsAnyRifle` test `GetClassName() == 'Rifle'` (BD22's
    class). The M203 underbarrel reload exists only on BD22's Rifle, not on the same rifle mesh under another
    mod's class.
  * The fix is not small: rows are generated at each donor's placement, so a mesh-keyed table needs rows in mesh
    space plus a per-donor placement transform (or a mesh -> canonical donor alias wherever placement is
    identical, which covers the 14 twins). Not done; owner's go needed for the shape.

---

# Round 4 finish (2026-10-27, ModelSwapper lane), 75-min box

Branch `modelswapper-2.0-bd22-lift`. Build `/home/claude/lane_a_out/ms_r4.pk3`
(sha256 `f43ceca12565747a02e66badef85c4ffc36337785cbcf318aeeb3e6cb58eb3a5`, = 3f38eec's code).
Everything here is **rig only, not headset-confirmed**. The rig was shared with Lane B the whole time
(load 2.0-4.7), so held gestures were slow.

## 1. Done (measured)
* **The 9 `_wm` rows -> the owner's originals.** Read-only from `E:\DOOMWork\VR_WeaponSetRebuild`, staged to
  `/mnt/user-data/uploads/DOOMWork/VR_WeaponSetRebuild/`:
  `br_vr/PK3_pbr/Models/Weapons/Hud/{Flamethrower2,Unmaker,HitlersBuzzsaw}/*.md3` + `Modeldef.{Flamethrower2,Unmaker,HitlersBuzzsaw}.def`;
  `BR_VR_MeatGrinder/Models/{Bolter/Bolter.md3,TEC9/tec9.md3}` + `Modeldef.{Bolter,TEC9}.def`;
  `Aliens-Eradication-VR-addon/models/weapons/flamer/m260b.md3` + `modeldef[.quest].flamethrower.txt`.
  BrutalWolf has no buzzsaw (no folder or MODELDEF), so the buzzsaw is br_vr's.
  * **Each original IS the mesh the shelf already draws**: byte-identical (`models/bd/Flamethrower2`,
    `models/bd/HitlersBuzzsaw`, `models/meat/TEC9`, `models/alien/flamer/m260b.md3`) or the same vertices moved
    by one rigid translation (spread 0.000; the `models/hud/` copies after tools_reorigin_all.py).
  * **md3label on each original: no magazine moves in any of them.** Frames are fire / idle / lower only.
    Flamethrower2 6 frames (trigger 1.24, part 0.98); Unmaker 16 (idle 0-4, lower 5-7, idle 8-15; parts 1.2);
    HitlersBuzzsaw 3 (trigger 1.05); Bolter 5 (trigger 0.90); Tec9 6 (bolt/slide 7.09 along -X in the fire
    frames 3-4, a recoil cycle, not a reload). So no reload row can come from their animation: the old rows stay.
    The Aliens M260B is the second flamethrower; it already has its own canister row (slot 1, canister moves 186 units).
  * **Duplicates collapse (hands):** brt_Flamethrower2, meat_Bolter and meat_TEC9 draw their pair's vertices
    within 0.01 mm (twin_hands.drawn) and now use its hand slot (6 / 15 / 16). hand_gap: 0.09/0.03, 0.03/0.06,
    0.02/0.01 cm. They already shared the reload slot (5 / 10 / 11).
  * **Not collapsed: the Unmaker pair.** MS_BD_Unmaker rests on frame 4, MS_brt_Unmaker on frame 0. Frame 4 is
    10.3 units into the "lower" motion (frames 0-3 are identical). Which rest is right is the owner's call.
  * HitlersBuzzsaw (only brt_) still has no hand row.
* **Pump: a parked gun can always be fired out (09bc6d0).** Real play, BD22 Shot_Gun dry-fired with the
  trigger held: BD22 loads ONE shell and leaves through Pump2. The probe reads that as a whole-tube reload
  and parks the gun until the hand pushes 1 shell. The scripted hand gripped at the pouch and never got a
  shell, so the gun was parked for good. A new trigger press now ends that hold (the mod already loaded the
  shell). Final build: Shot_Gun real play PASS. **But** the hand still pushes nothing there. The AGAIN press
  freed the gun, which went back into BD22's reload (5 shells by the mod); the next press fired.
  **Open: why the hand takes no shell in that hold.**
* **Gate (realplay.py):** decision D is checked per cycle (one shot fired, one take, one give-back, no shot
  from a fire press while held, given back by the cycle's end). Revolver is a break slot and gets the rsb
  driver. The pump's give-back is recognised. The first break shot waits 70 more tics.
* Disk: deleted ms_a1..a6, ms_4227925, ms_r4_wip, ms_r4_final (+ its sha). Kept ms_r2_final, ms_r3_final, ms_r4.

## 2. Decision D (SSG / M79: break, load, close after EVERY shot): NOT clean on the rig
* Final build, real play (logs `/home/claude/lane_a_out/r4/logs/rp_SSG_r4final.log`, `rp_GL_r4final.log`):
  * SSG cycle 1: shot -> took -> mod loaded -> held -> hands open/load/close -> gave back. Clean.
  * **SSG cycle 2: a leak, the same as on the pre-fix build (`rp_SSG_r4.log`).** The mod's reload left through
    a different exit (parked "at -298 of its reload", not -413), a fire press at that tic fired (SHOT 4 t1301,
    SSGAmmo 2 -> 0), and the now-empty gun was taken a SECOND time (a double break cycle). The way-out
    park (a36c744) only sees the direct next state.
  * M79: cycle 1 clean. Cycle 2's hands did not finish inside 500 tics (carry from t1346, no insert by t1740).
    That is load 2.6-3.2, the rig's known held-gesture miss. It was not re-run at low load.
  * Cycle 0 on both: the 6-tic press at t200 did not fire (the gun was not ready). The hold press fired
    instead, so the checker counts it as "fired while held". That is a timing artefact, not a leak.
* **Tried and reverted (0ef7b2c -> 3f38eec):** park a break-open gun the moment the mod's reload fills it.
  Real play got worse: the SSG was taken twice per cycle (the rest of the mod's reload re-entered the join
  after the give-back) and the M79 was stuck after cycle 1. Logs: `rp_SSG_midpark.log`, `rp_GL_midpark.log`.
* Next step: map the SSG's -298 exit (SSG.dec) and make LeavesReload / the re-arm see it. Or keep the gun
  disarmed after a give-back until its psprite has been in Ready once.

## 3. Gates on ms_r4: NOT complete
* Real play, final build: **Shot_Gun PASS; SSG FAIL (the D leak); GrenadeLauncher FAIL (D cycle 2 under load).**
  Revolver and the other 14 BD22 classes were not reached in the box.
* rig halves / desktop / extras: started on the pre-fix build, then stopped (1 result in 10 min: MS_AE_Flamer
  PASS). **Counts vs r2 (74/74, 74/74, 13/13) are NOT re-proven on r4.** Run `lane_a_out/r4/final_gates.sh
  /home/claude/lane_a_out/ms_r4.pk3` when the rig is calm.
* The owner's load order ran with no script error from the pack on every engine run above (doom2 ->
  brutal22test6 -> BD_VoxelPack -> ms_r4).

# Round 5 (2026-10-27, ModelSwapper lane): the five guns reload by hand (75-min box)

Build `/home/claude/lane_a_out/ms_r5.pk3` (sha256 `599212cb8a2bc028964bd8ce4f1ac0583194789b9dca861bf65ab7fb2e274346`, = 517f816 data). Sheet
`/home/claude/lane_a_out/r5_five_reloads.png`. Logs `/home/claude/lane_a_out/r5/logs/`.
Everything here is **rig only, not headset-confirmed**.

## 1. Done (measured)
* **Why they did not reload.** Unmaker / Flamethrower2 / Bolter / TEC-9 / Buzzsaw sat on the old slots
  5 / 8 / 9 / 10 / 11. No MODELDEF in the pack names their layer sprites (Q04M..Q0AM): mid-reload the
  gun's sprite pointed at nothing (the gun vanished) and the hand's part drew nothing. regen_rows.py
  skipped them ("card mesh is a _wm rebuild"). Slots 3-30 except 17 have the same hole; the other
  donors on them were re-pointed to slots 41-80 earlier, these five were the last.
* **Port, not re-measure** (`tools_kit/port_plus_rows.py`, data `WMCARD.plusport`, `plusport_transforms.json`):
  * Sources: the RS_VR_Weapons model cards that Vanilla+ borrows (`WMSHEET.plus_exotics/extras`:
    `model = WM_Unmaker / WM_Bolter / WM_Tec9 / WM_Flamethrower`), measured on the `*_wm.md3` the Plus
    pk3 ships (byte-identical to ours in `models/vanilla/`). Buzzsaw: BD22 Weapons Q's MG42 belt drum
    (Depot `tools/bd22_plus.py` 'MG42': card BD_Buzzsaw, ref `buzzsaw_wm.md3`, part magazine) = our
    `WMCARD.bd22` "MS_Buzzsaw" on `models/bd22/bd22/buzzsaw_wm.md3`.
  * Transform per donor, by nearest-POSITION correspondence (never vertex order), scale free:
    all 9 donors **scale 1.00000, rotation 0.000, every vertex within 0.0000** both ways
    (11541 / 6155 / 4565 / 5469 / 18972 vertices). The hud/ copies: t = 0; the bd/ and meat/ copies:
    Unmaker (56.52, -0.02, 2.55), Flamethrower2 (57.03, 0.47, -8.36), Bolter (37.67, 0.20, -4.47),
    TEC-9 (39.31, 0.08, -1.66), Buzzsaw (47.59, 0.95, 3.36). The four RS_VR ones equal
    `card_transforms.json`'s earlier, independent fit to 0.0001. The scale between the sets lives in
    MODELDEF (1.1 vs the card's 0.374 world scale); regen_rows builds each row at the donor's own
    MODELDEF placement.
  * MS_BD_Unmaker rests on frame 4 (the owner's open call from round 4). Frame 0 matches exactly; frame
    0 -> 4 is the body's rigid move in the same file (6.247 deg, max 0.028). At frame 4 the flap is
    0.29 and the lever 2.21 units off that move (they animate). The card is carried to frame 4.
  * The drawn meshes are carved by that correspondence (carve_by_ref, all frames kept, 0 unlabelled):
    surfaces now named body/flap/lever, body/canister/pilotflame/trigger, body/mag/trigger,
    body/bolt/bolt_2/magazine/trigger, body/magazine/trigger. Same vertices, same skins.
  * `regen_rows.py` then gave each donor its own row with layers: slots 81 BD_Flamethrower2,
    82 brt_Flamethrower2, 83 BD_Unmaker, 84 brt_Unmaker, 85 brt_HitlersBuzzsaw, 86 MG_Bolter,
    87 meat_Bolter, 88 MG_Tec9, 89 meat_TEC9 (TEC-9 with its bolt handle on layers). All 186 old
    MODELDEF.cards blocks are unchanged. The Buzzsaw's row equals BD22Q's MG42 row (Well, Axis, Mouth,
    MagLen, MagCentre identical; hand hooks differ by the grip fits).
* **Rig, testmod gun, model picked (`run_gate.py --vr --shots`): 5/5 PASS.** Each: empty -> reload button ->
  part out -> off hand takes one (HELD 2201 Q..P@rsq_hands) -> carried -> inserted -> seated -> given back
  -> the mod's reload refilled. Frames on the sheet (the part is clearly visible for the canister,
  Bolter mag and the drum at its seat; the Unmaker skull and the black TEC-9 mag are small in the crop,
  the HELD log lines show them in the hand).
* **BD22 load order, real play (doom2 -> brutal22test6 -> BD_VoxelPack -> ms_r5, realplay.py, now with
  `Class=MS_Donor` picks): fire, burst, fire empty, reload button, the hands, fire again.**
  PASS with 2 takes / 2 magazine-outs / 2 give-backs and firing after: Plasma_Gun=MS_MG_Bolter,
  BrutalSMG=MS_MG_Tec9, Plasma_Gun=MS_BD_Unmaker, Rifle=MS_BD_Flamethrower2,
  BrutalSMG=MS_brt_HitlersBuzzsaw. No script error from the pack (only BD_VoxelPack's own 5).
* Gate driver: a part held back to front (the drum goes in from the side; the off hand's frame is
  mirrored: 118-180 deg) is now turned in quarter turns first (`rsr_testdriver.zs`, TurnWrist). Before
  it the Buzzsaw stalled in CARRY at 118-148 deg. `run_gate.py`: `MS_SHOT_TICS` sets the shot tics.

## 2. Not done / open
* **BD22's own Unmaker, Flamethrower2 and MG42 never reload, with any model.** Measured in real play
  (picked models, logs `rp_Unmaker_*`, `rp_Flamethrower2_*`, `rp_MG42_*`): Unmaker and Flamethrower2
  fire from a 999 pool with no reload ("its Reload label is its Ready loop -- no hand reload on it");
  MG42 fires straight from its Clip2 pool (200 -> 30 over 170 shots in the run) and never entered a reload. ModelSwapper joins the mod's own reload, so there is nothing to join.
  Giving those three BD22 guns a magazine is a new VR mechanic on BD22's balance: the owner's call
  (BD22 Weapons Q does it with its own Plus toggles).
* MS_wolf_MG42 still shares the old slot 9 (no layers drawn). Not in this job.
* The Unmaker rest frame (BD_ frame 4 vs brt_ frame 0) is still the owner's call.
* run_all on the rig: see section 3.
