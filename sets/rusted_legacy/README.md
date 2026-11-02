# sets/rusted_legacy: Ermac's Rusted Legacy, measured (plan step S4)

**Source:** Ermac's Rusted Legacy dev build (`doom-force-unleashed_devbuild`, last edited 2025-06-03), the owner's
copy at `E:\DOOMWork\_old\doom-force-unleashed_devbuild`, **committed whole in `src/`** (1195 files, meshes and code,
byte-identical to the owner's copy; owner 2026-11-02 04:40). Ermac to the owner: "go have fun with my fork, i've
kept the codes as clean as possible". His code is MIT (c) 2025 iAmErmac (`src/LICENSE`); his meshes come from Sketchfab
and other sources under their own licences (`src/README.md` credits). Single-frame meshes are listed in
`single_frame_ok.txt` for the Depot's mesh hook.

**State:** measured only. No rig run yet, nothing in a headset. Nothing here is "shown working".

## What is here
- `cards/<gun>/rl_<gun>.card`: the readable card. `rl_<gun>.json`: every number, plus his reload piece's whole path.
  `rl_<gun>.png`: side / top / front.
- `sheets/`: the four sheets shown to the owner (three guns a sheet).
- `tools/rl_measure.py`: the measuring script. Depot tools only (`tools/hqt/md3label.py`, `tools/hqt/gripmeasure.py`,
  the fitter core's `gunview` / `hudrender`).

    RSQ_RL=sets/rusted_legacy/src python3 sets/rusted_legacy/tools/rl_measure.py pistol shotgun ssg chaingun plasma \
        rocket hellshotgun incinerator bfg heatwave chainsaw

  Re-run from the Depot on 2026-11-02: all 11 cards byte-identical to the first run.

The ShieldSaw is not measured: the owner's own ShieldSaw comes from UBQS at the end (owner, 2026-11-02).

## How it measures (every number from his files; say which)
- **Where:** the gun's first non-PBR "with both hands" MODELDEF group (else "with hand"), its `//Ready` row,
  Scale -1 1 1 / Offset 0 -24 -10, in the controller frame in cm (F forward, L left, U up) by the kit's chain
  (`hudrender.to_local` -> `gunview.to_fl`, vr_weaponScale 1.02). Parsed from his MODELDEF.
- **Parts:** his own surface names (`slide`, `shotgun_pump`, `ssg_barrel` ...) map to roles; each part's travel and
  rotation against the body, body motion removed (Kabsch), over every mesh frame his block plays. Mesh-measured.
- **Grip / support:** `gripmeasure` on the `hand.md3` / `hand2.md3` frames his Ready row uses. Mesh-measured.
- **Reload piece** (model slot 1): its seat, and the last straight run into the seat, in the frame order of his
  reload states. Parsed from his zscript + MODELDEF, positions mesh-measured.
- **HUD:** his gun ammo display (`holohud2.txt`, its own per-gun Offset) and his wrist watch (`holohud.txt`, one
  `w_dial` frame per gun = that gun hand's one-hand pose).

Rules his files needed (all in the script):
- His states draw the base sprite (`PISG`) and `A_SetAltModel` swaps the two-hand one (`PS2H`): states are read
  with the base sprite, frames looked up under the 2nd `A_SetAltModel` argument.
- GZDoom copies a block's current model set at each `FrameIndex` line, so slot 1 can change mid-block (rocket clips).
- A gun's reload rows can sit in an un-headed block after the headed one (hell shotgun): the group is merged.
- Break-open (SSG): the shells ride the barrel while it opens; the chamber seat is the last frame they still do.
- BFG: the pod is set into the open tray (frame 11) and the lid carries it home; the seat is the tray.
- BFG muzzle: a circle fitted to the ring mouth. Its body leans, so its bore is set to controller forward.

## The guns

| Gun | Reload piece | Into the seat | Notes |
|---|---|---|---|
| pistol | `berreta_mag` | 4.57 cm up into the grip | slide 6.14 cm; mesh frames 8-21 never played (a slide-lock fire cycle) |
| shotgun | `shell` | 2.72 cm into the port | pump and bolt 6.28 cm |
| ssg | `ssg_shell` (2) | 5.96 cm into the open chambers | barrels break 37 deg |
| chaingun | `cg_mag` | 3.09 cm straight up | support hand on the top carry handle; frames 5-10 a static hold |
| plasma | `plasma_mag` | 5.40 cm up | two stacked bores: muzzle = front-face centre, to refine |
| rocket | `rockets` (3-rocket clip) | 7.61 cm sideways | his clip slides through the receiver; one rocket in the window, two out the side |
| hellshotgun | `hellshell` | 2.49 cm into the side port | the lever loop swings 84.5 deg |
| incinerator | `gascan` | 4.96 cm up-forward under the barrel | no two-hand block (no support hand); the valve never moves; `ImmersiveReloadWait3` never reached |
| bfg | `bfg9000_pod` | 2.48 cm down into the open tray | the lid opens 69 deg; closing slides the pod ~10 cm home |
| heatwave | `heat_mag` | 2.64 cm up | the blades swing 25 deg out on fire |
| chainsaw | none | - | 1 frame; `saw_handle` is the wrap-around front handle the support hand holds (no pull cord in the mesh) |

**HUD:** the ammo display is a flat 9 x 3.7 cm panel facing the player, left of each gun at its own Offset (the
chainsaw has none). The watch sits within ~1.3 cm of the gun hand's wrist in every Ready pose.

## Found in his build (code and asset audit, 2026-11-02)
Rig: his build boots on QuestZDoom 17.3 (tools/rig/bin/qz) with freedoom2.wad (his README supports Freedoom; the
owner's doom2.wad was not reachable this session), MAP01, 0 script errors; all 11 guns drawn in hand
(`sheets/rig_baseline_all_guns.png`). Rig only, not headset-confirmed.

**Fixed (step S4, 2026-11-02), each against his own definitions; boots clean after:**
- `modeldefs/weapons/pistol.txt:45` `FrameIndex PISG J 1 99` -> `PISG S 1 99` (the S row had set J's magazine slot
  to hidden, and left S's unset). Data fix; the frame difference is not isolated on the rig yet
  (`sheets/rig_pistol_reload_base_vs_fix1.png`).
- `sndinfo.txt`: `$random rocket/explode` listed `weapons/explode1-6`, which do not exist; his file defines
  `grenade/explode1-6` (rexplod1-6). Rocket explosions were silent; now they use his sounds.
- `sndinfo.txt:265` `rolloff gascan/whoosh` -> `$rolloff gascan/whoosh` (the line was a sound named "rolloff").
- `zscript/weapons/incinerator.txt` 637 / 647: `weapons/IncineratorFlame/death|fizzle` (undefined) ->
  `weapons/flame/death|fizzle`, the names his SNDINFO defines for those files (dsincht1-3).

**Corrected:** `weapons/sawup`, `weapons/sawidle`, `weapons/plasmax`, `weapons/incinerator/burn` are defined by the
engine's own Doom SNDINFO (qzdoom.pk3 filter/game-doomchex): not bugs.

**Still open (no file of his fits; owner's call):** `flak/frag` (casing bounce, BD leftover), `props/redfire`
(flame death, BD leftover), `blackhole/cancel` (his SNDINFO names `bhcancel`, the file is not in his build),
`FighterHammerExplode` (ShieldSaw: out of scope). `weapons/pistol/reload` -> `breload` has no file but nothing
plays it.

Unused in his build: `berreta_pickup.md3`, `rl_laser.md3`, `tracer2.md3`; states `Laser0`, the heatwave's
`FlashCharge1`, `Disappear`, `Explosion`, `ImmersiveReloadWait3` (incinerator); 17 Brutal Doom effect classes never
spawned; pistol mesh frames 8-21 (a slide-lock fire cycle) never played.

His reload: an off-hand proximity trigger (3 units) at a point from `LineAttack(angle, 5, pitch-100)` off the
player, then a canned animation. Nothing follows the hand.

## Hand reloads (RSRL, 2026-11-02; rig only, not headset-confirmed)
His immersive reload walks each gun through steps; each step waits in a gate (`A_CheckImmersiveReloadActionN`) that
only tests whether the off hand is within 2-3 units of a point. Now, in VR with `rsrl_handreload 1` (default), each gate
asks `src/zscript/rsrl/rsrl_reload.zs` instead, and calls HIS `setReloadStep(...)` with HIS arguments only when the hand
has really done the job. His animations, sounds, shoulder ammo grab, markers and ammo code all still run. Outside VR or
with `rsrl_handreload 0` his touch test runs unchanged.
- **Insert** (a piece drawn in his off hand): the piece is captured in a cylinder about the measured seat axis (side
  3.5 cm, square to the mouth within 40 deg, up to stroke + 6 cm out), and must be pushed home along it (to 1 cm) without
  leaving (side 5.5, 55 deg). BD22 RSR tolerances.
- **Stroke** (empty hand on a part): palm within 7 cm of the part, then moved along its measured axis 0.85 of travel
  (rotating parts 0.6 of the chord). The pump goes back, then forward again.
- Gates: pistol mag, slide; shotgun shell, pump; SSG barrel down, shells, barrel up; chaingun / plasma / heatwave mag;
  rocket clip from the side; hell shotgun shell, chamber lever; incinerator lever, pull the can, new can, lever back;
  BFG lid open, pod, lid closed.
- Every number: `tools/gen_rsrl.py` reads the cards (seat, approach, stroke, parts), and measures the piece in his off
  hand (fist.txt ammo_hand frame + piece model), the piece's axis at the mouth, and his empty-hand palm (hand.md3
  frame 1, front 10 cm: -1.05, 2.62, -5.49). It writes `src/zscript/rsrl/rsrl_table.zs` and patches his 10 gun files
  (2 lines per gate, idempotent, CRLF kept). Re-run it after re-measuring.
- `rl_imreload` now defaults to **true** (his default was false), so the hand reloads are what a new player gets.
  New cvars: `rsrl_handreload` (1), `rsrl_debug` (0; 1 logs captures/grabs/done, 2 every 7 tics).

Shown on the rig (`tools/rl_drive.py`, freedoom2, tools/rig/bin/qz 17.3): all 10 guns, 20 of 20 gates passed by
hand motion alone, 0 script errors; sheets in `sheets/reloads/rig_reload_<gun>.png` (side view, looked at: piece
comes in from the mouth side, his in-gun animation then plays, the gun ends in Ready). Wrong-way run (`RL_NEG=1`):
pistol mag and shotgun shell turned 60 deg off their mouth axis were never captured; the incinerator lever pushed
against its travel was let go.

Not yet: headset. Some pieces need a real wrist turn to seat (the rig pitched the off hand by): pistol +13, chaingun
+17, plasma +15, shotgun -39, rocket 0, hell shell +69, heatwave -69, BFG pod -69, gas can -66, SSG shells -83 deg.
That is his in-hand pose against his gun's mouth; if it feels wrong in the headset the fix is the in-hand pose
(fist.txt), not the tolerance. The SSG approach axis is his animation's (it swings in from the right, L -0.47).

## HUD polish (2026-11-02; rig only, not headset-confirmed)
His watch and gun display are kept as he made them (meshes, colours, scales, numbers, menu). Measured first:
- `tools/rl_hud_audit.py`: every frame his HUD states can reach (all menu choices) has a MODELDEF frame in every
  class, and every file exists. One bug: the gun display's background set its translucency on the WATCH layer
  (`PSP_WHUD_Dial`, weaponhud2.txt), so the full background was always opaque. Fixed to `PSP_HHUD_BG`.
- The cards measured every watch on `w_dial.md3`; the shotgun, SSG, hell shotgun and BFG wear `w_dial2.md3`
  (inner wrist). `rl_measure.py` now reads the dial from the block; those 4 cards' watch rows changed, nothing else.
- `tools/rl_watch_drift.py`: his watch and panel are drawn at ONE pose per gun, but the gun and hand animate. Off the
  wrist / off the gun (worst): fist punch 55.7 cm, SSG 19.3 / 19.7, shotgun 13.3 / 13.1, hell shotgun 13.3 / 13.5,
  pistol 3.7 / 4.4. The other guns: under 1 cm in every frame.
- The fix (`tools/gen_hudfollow.py`, the method's rule that everything on the gun moves with it): each pose more than
  1 cm off gets its own copy of his HUD blocks. The watch uses the dial frame made for that hand frame (his meshes
  have one per hand frame), and the panel uses copies of his panel meshes with the gun body's measured motion baked
  in (`models/common/rsrl_<gun>_*.md3`). `zscript/rsrl/rsrl_hudfollow*.zs` swaps the layers' sprites from his
  Tick. Checked: 945 baked panel frames within 0.012 cm of the body's motion; the watch on its wrist within 0.3 cm in
  every pose. 70 poses (pistol 7, shotgun 8, SSG 18, hell 33, fist 4). Ready frames are his blocks, untouched.
  `rsrl_hudfollow 0` turns it off.
- Rig: `sheets/hud/rig_shotgun_recoil_follow_off_vs_on.png`. Off: in the recoil the watch stays in the air. On: the
  watch goes with the wrist and the panel with the gun. 0 script errors; the 4 guns' hand reloads re-run, all gates pass.

Measured but not changed (owner's call): from an eye behind the sights the rocket and BFG panels are hidden by the gun
body and plasma's is half hidden (`tools/rl_hud_view.py`). From the rig's default eye every panel is in full view.
The BFG's watch is hidden from both eyes by the gun: it is not inside the mesh (2 of 41 dial points touch it), it
sits under the BFG's body, which covers the gun hand from every angle tried on the rig.

## HUD performance (2026-11-02; rig)
His Tick, every tic: turns ammo/health/armor into strings, destroys and re-makes 17 HUD layers + the laser (18 new
PSprite objects per tic, garbage for the collector), runs ~150 A_JumpIf calls through their state chains, resolves 10
state labels by name. Now (`rsrl_hudfast 1`, default; `zscript/rsrl/rsrl_hudfast.zs`):
- his state chains are compiled to functions by `tools/gen_hudfast.py` (377 labels), so the frame each layer shows is
  the one his chain picks; layers are made once and only get sprite and frame set, and only when his values, his
  settings or the pose changed; his calculateHUDValues runs only when its inputs changed; labels resolved once;
  the laser is re-made only when his laser settings change. No per-tic allocations.
- measured on the rig (`rsrl_hudprof 1`, shotgun held, 350-tic averages): his ~100 us per tic, fast ~14 us (7x).
- same picture: `rsrl_hudcheck 1` runs his code and the compiled chains together, all 12 classes and a sweep of every
  menu setting kind, god mode, firing: 17,255 layer-tics, 0 differ. `rsrl_hudcheck 2` checks the fast path's drawn
  layers (with skipped redraws and the follow poses) every tic: 17,255 layer-tics, 0 wrong. `rsrl_hudfast 0` = his code.
- kept as he renders it: his hud_bracer sets the bracer's render flags but the DIAL's style and alpha (Add 0.8), so the
  dial is additive, not the Translucent 0.7 his hud_bg asks for. Probably a copy slip like the panel one; not changed
  because it is the look you see now.

## Next (S4)
1. DONE: rig boot (freedoom2, 0 script errors) and the four certain audit fixes. Re-run on doom2.wad when it is staged.
3. DONE on the rig (2026-11-02), see "Hand reloads" below: all 10 reloadable guns, 20 gates, by hand.
4. His gun ammo display and wrist watch kept and polished (owner, 2026-11-02 04:30): first pass DONE, see "HUD polish".
