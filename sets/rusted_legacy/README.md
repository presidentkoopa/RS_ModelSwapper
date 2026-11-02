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
- Pistol MODELDEF: `FrameIndex PISG S 0 22  FrameIndex PISG J 1 99` (`J` should be `S`): probably hides the
  magazine on frame J, the first frame of the immersive reload.
- Sounds with no file: `weapons/pistol/reload` (`breload`), `blackhole/cancel` (`bhcancel`). Played but never
  defined: incinerator burn / flame death / fizzle, `weapons/sawidle`, `weapons/sawup`, `weapons/plasmax`,
  `props/redfire`, `flak/frag`, `fighterhammerexplode`. SNDINFO line 265 `rolloff gascan/whoosh` lacks its `$`.
- Unused: `berreta_pickup.md3`, `rl_laser.md3`, `tracer2.md3`; states `Laser0`, the heatwave's `FlashCharge1`,
  `Disappear`, `Explosion`; 17 Brutal Doom effect classes never spawned (his README: BD material is temporary).
- His reload: an off-hand proximity trigger (3 units) at a point from `LineAttack(angle, 5, pitch-100)` off the
  player, then a canned animation. Nothing follows the hand.

## Next (S4)
1. The rig: doom2 -> his build (`src/`), zero script errors, before any change counts.
2. The audit bugs fixed in `src/`.
3. Reloads by hand: magazine (pistol, chaingun, plasma, heatwave), pump (shotgun), break (ssg), sideways clip
   (rocket); new kinds: lever (hell shotgun), canister + valve (incinerator), tray + lid (BFG).
4. His gun ammo display and wrist watch kept and polished (owner, 2026-11-02 04:30).
