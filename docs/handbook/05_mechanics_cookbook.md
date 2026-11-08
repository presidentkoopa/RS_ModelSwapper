# 5. Mechanics cookbook

How each VR mechanic in BD22 VR Weapons Q is built, and where its code is. Paths are under
`sets/bd22q/src/`. Every mechanic follows three habits:
- **The parent mod's code stays the judge.** The VR part moves pieces and asks the gun's own states to do the
  ammo, damage, sounds and checks. Out of VR, or with the option off, the gun runs exactly as the parent mod
  shipped it.
- **Hook after the gun's own checks.** A reload hook goes where the gun's own `Reload:` state has already
  checked ammo and conditions, so the parent's rules still decide whether a reload may start.
- **Every position is cm in the weapon controller's frame (F, L, U), measured off the mesh as drawn**, and it
  moves with the gun when the gun moves (`port_gun.py`).

## Magazine reload (18 BD22 guns)
`zscript/rsr/vreload.zs` (the shared plumbing, names no gun), `zscript/rsr/rsr_guns.bd.zs` (the per-gun table),
`MODELDEF.rsr` (the parts), a few states in each gun's `.dec`.
- Phases: `IDLE > DROP > EMPTY > CARRY > INSERT > SEATED > (CHARGE > PULL > RELEASED) > DONE`.
- The gun's own `Reload:` jumps to `RSR_Start` after its checks. `RSR_Wait` holds the gun ("####" "#") while
  the hand works; `RSR_Seated` runs the gun's own fill loop; `RSR_Done` ends at the gun's own end of a reload.
- The magazine is the gun's own mesh surface, drawn in three places: in the well (`RSR_GunParts`, layer 2102),
  in the off hand (`RSQ_Hands`, layer 2201, the FBX hold round it), and dropped on the floor.
- Taking a new one: the off trigger (`rsr_grab_with 0`; 1 = off grip; 2 = Use) at least `POUCH_MIN` 20 cm from
  the well, anywhere or low at the belt (`rsr_pouch`). It goes in when it is on the well's axis and pushed
  past the mouth (`Well`, `Axis`, `Mouth`). `rsr_assist` scales every capture radius.
- The charging handle / slide: `Grab`, `Pull`, `Travel`; the off trigger takes it. In grip mode the off
  TRIGGER takes it, because pressing the grip steadies the gun and the engine moves the gun under the hand.
- Rounds held aside are not lost: a part-full magazine pulled out keeps its rounds (`RSR_Held_<gun>`), and they
  count when the reserve is empty.

## Guns the parent never reloads: real magazines (9 BD22 guns)
`zscript/rsq/counters.zs`. MG42 drum, Flamethrower canister, Machinegun box, Unmaker skull, Minigun box,
Devastator bay, Nuker block, Hellish drum, Incendiary cylinder. Capacities (`CAP[]`) are the owner's numbers
(the parent has none). The part was cut out of the gun's own mesh by position (a welded mesh can hold many
separate bodies) and checked rigid in every frame.
- A separate magazine item (`RSQ_Mag_<gun>`), the pouch = the parent's own reserve item, and up to `LEND` 10
  rounds lent from the magazine into the reserve item so the parent's fire code (`A_JumpIfNoAmmo`,
  `DepleteAmmo`) finds ammo. Every round it takes is charged to the magazine.
- Empty magazine: a guard before every shot jumps Fire to Reload. Seated: `min(cap - mag, pouch)` moves in.
- Option off (`rsq_reload_nonstd 0`) or out of VR: the rounds go back and the gun is the parent's again.

## Break-open: SSG, M79, the revolvers
`zscript/rsr/rsr_break.zs`, `rsb_guns.zs` (`RSB_Guns`), `MODELDEF.rsb`.
- The gun's own reload opens the action: the hinged part swings about a hinge **fitted from the gun's own
  open frame**, the gun's own open sound, the spent rounds out as the parent does it (its own casing actors).
- The off hand takes a round, brings it to an empty chamber from behind along the bore (`Bore`, `Base`,
  `Tip`) and pushes it home: the gun's own per-round step moves the ammo.
- Closing: a quick turn of the gun hand the way the action closes, faster than `rsb_flick_speed` (450 deg/s
  over 3 tics): pitch for barrels, **roll** for a swing-out cylinder. Or push it shut with the off hand.
- When the gun moves, `RSB.Hook` passes `Offset(i)` both to the hinged parts and to the round in the off hand,
  so the off-hand block moves too and the hold rows are re-expressed: `Hand0-2 = g R^T`,
  `HandT = HandT - g R^T t` (the hand's hold is unchanged). `port_gun.py` does this.

## Cylinder: speedloader or a round at a time
Same file. Revolver rows carry `Chambers`, `Loader` and a seat per chamber. "Shot/Revolver Reload:
Speedloader / Per Round" (`rsb_revolver_feed`, server) picks the row. The Moonlight takes the Brutal Pistol's
ammo: `RSB_Guns.ReservePer(i)` = 3 pistol rounds per chamber (2.0.1).

## Pump shotgun
`zscript/rsr/rsr_pump.zs`, `rsr_pump_guns.zs` (`RSP_Guns`), `MODELDEF.rsrpump`.
- Shells: the off hand takes one, it goes in only at the loading port (its middle on the port's line, crimp
  first) and is pushed home; the gun's own per-shell step runs. Let go early and it drops.
- The pump: after each shot, the off hand on the pump (steadied) works it through a full stroke, both of the
  gun's own sounds. The pump's numbers (`Grab`, `Port`, `Pull`, `Push`, `PumpHook`, `SupportHook`, `PortHook`)
  move with the gun (`shotguns/port_sg.py`).

## Under-barrel launcher (M203 on the Rifle, the Machinegun's launcher)
`zscript/rsr/rsr_m203.zs`, `rsr_m203_geo.zs` (`RSM_Geo`, per gun: 1 rifle, 2 machinegun), `MODELDEF.rsm`.
Secondary fire launches; empty, a dry click. Steadied, the off TRIGGER is the latch: push forward and the
tube follows the hand and opens; take a 40 mm round, tilt its nose into the breech, push it home; steady and
pull back to lock it. While open, the gun is drawn from its no-tube twin blocks (`QT08 / QT09 / QT0A`). After
a gun move, `RSM_Geo.ToGun / DirToGun / FromGun` carry points between the launcher's tables (still in the
original frame) and the moved gun.

## Two-handed steadying and the support hand
The engine does the steadying (chapter 1.1); the pack only draws it. `zscript/rsq/hands.zs`: when
`RSVR_VRHand.Steadied`, the free hand hides and the support hand (layer 2101) shows on the gun at the gun's
row (`handtable.zs` `SupportHook / SupportRot / SupportPoint`); a pistol switches to its two-hand gun-hand pose.
The support never holds on while a reload needs the hand. One-hand guns (pistol, revolvers) cup the gun hand
when the off hand comes within 13 cm.

## Melee: swings, hit points
`zscript/rsvr/melee.zs`, `zscript/rsq/pose.zs`, `zscript/rsq/bash.zs`, `zscript/rsq/fists.zs`.
- **The pose spine** (`pose.zs`): 8 samples per hand per player of {point, body position, body yaw, time}, fed
  by one netevent a tic from the console player and read only from that history by everyone. Velocities are
  taken in the body frame, so a snap turn or a teleport is not a swing, and a second player works.
- **A hit** is a swept segment (the blade's `BladeIn` to `BladeOut`, measured off the mesh **at the ready
  frame**) crossing a body, and it fires the parent's own attack actor at the impact point and height
  (`AxeAttack`, `DSAttack`, `SawDamageHorizontal`, `KickAttack`, `MeleeStrikeNormal`), so the parent's gore and
  damage rules decide the result.
- **Axe**: only a cut where the edge leads the motion: cos(edge, motion) >= `rsvr_axe_edge` (0.5); an upswing is
  never a hit. **Sword**: two hands draw a second sprite (`DSL2`) whose block is turned 110 degrees about the grip,
  so the blade points away from the off hand; two hands land the attack twice. **Chainsaw**: cuts whatever the bar
  touches while the trigger is held, every 2 tics. **Pistol whip**: a gesture with the pistol or revolver.
  **Butt strike** (off by default): both hands on, the butt leading the muzzle (`rsvr_butt_fwd` 0.5,
  `rsvr_butt_lead` 1.3), because "two hands + motion" is how you hold a rifle. **Gun bash**: a button (the
  kick key), BD22's own kick.
- **When the weapon moves to the hand, the hit points must move too**: `RSVR_MeleeMove.Apply(k, frame, p)`
  applies each weapon's gun move (written by `tools/int20_rig/butt_move.py` and the r12 melee port). Forgetting
  this left butt strikes landing behind the drawn stock.

## Throwing
- **Grenade** (`zscript/rsg/grenade.zs`): the off hand takes the ring and pulls the pin; the main trigger is the
  spoon. Let go while swinging: thrown with the hand's speed and direction, from the drawn grenade. Let go while
  still: the spoon flies and it cooks in the hand. BD22's own grenade, fuse and blast.
- **Axe throw** (`melee.zs`): hold the trigger (or alt fire), a lock-on ring marks what the hand points at, swing
  and let go; the throw blends the arm's motion with where the hand points (`rsvr_axe_throw_blend` 0.7).

## Live scope (and the alt-fire toggle)
`zscript/rsq/scope.zs` (`RSQ_ScopeTable`: all per-gun data), `zscript/rsq/scope_real.zs` (the handler and the
camera), `ANIMDEFS.rsq` (`cameratexture RSQSCOPE 256 256 fit 240 200`), the gun's MODELDEF with **per-surface
skins** and the glass as its own surface.
- Per gun: `Lens` (glass centre), `Axis` (bore), `Up` (glass up, after the port), `Radius` (from the glass's UV
  extent, not the disc's outer bound), `GlassSurface`, `Mag` (3), `AltToggle`.
- A camera actor is placed every tic on the bore and renders into `RSQSCOPE`; `A_ChangeModel` puts that texture
  on the glass surface. Field of view: `fov = 2 * atan((r / relief) / mag)` from the sighting eye's distance.
  The eye is `HmdPosition` (not the view height: with `vr_crouch_use_button` on, viewz does not follow the head),
  and each eye is tested, not the point between them. Camera roll = 180 + the glass's own roll, so a gun turned
  in the hand still shows an upright picture.
- **Alt fire toggles it** (the rising edge of `BT_ALTATTACK`, read by the handler; it keeps its own last-tic copy
  because `player.oldbuttons` already equals this tic's buttons in WorldTick). Off: the glass gets its own skin
  back and the camera texture is drawn nowhere, so the engine does not render it (zero cost).
- Measured on the rig: Sniper 3.07x across / 3.06x up, RailGun 3.2x / 3.0x; picture tilt under 1 degree.
- The cvar was renamed (`rsq_scope_sniper` -> `rsq_scope2_sniper`) so an old saved "Dot" could not hide the new
  default. The manifest for lifting it out as its own mod is at the top of `scope.zs` (PLAN C3).

## Where the shot starts, and the flame
- `zscript/rsq/muzzle.zs`: every VR hitscan starts at the controller. `WorldHitscanPreFired` cancels it and fires
  the same one again from the drawn muzzle with `LineAttack(LAF_ABSPOSITION)`: same direction (the engine's own
  `AttackDir`), damage, puff, range, flags. A wall guard traces controller -> muzzle and leaves the shot alone if
  the muzzle is through a wall. Per gun: `Muzzle(w)` (F, L, U).
- `zscript/rsq/flamespout.zs`: the flame projectiles start at the drawn nozzle tip and fly along the drawn
  barrel; the nozzle is never tilted to suit the stream (owner).

## Dual wield and the flick reload
`zscript/rsq/dual.zs`, `dualtable.zs`, `dualhands.zs`, `DECORATE.rsqdual`, `MODELDEF.rsqoff` / `.rsqdual`;
`zscript/rsq/flick.zs`.
- Each dual-able gun has an off-hand COPY (`RSQ_Off_<Gun>`, generated): the same gun with its own magazine that
  lives only in the off hand. You get it by picking up a second one (BD22's rule); the Dual key (+user3) toggles
  the off hand between the copy and the fist. Reserve shared, magazines separate, each hand fires on its own.
- Off-hand shots start at the off-hand gun's muzzle (`RSQ_PlayerRounds.OffWhere`, the muzzle table in the off
  controller's frame).
- **Flick reload**: with a gun in each hand, snap a barrel down (45 degrees within a few tics, ending below
  level) and that gun alone runs the parent's own reload. Re-arms once the barrel comes back up.

## Player ballistics: Hitscan / Bullet
`zscript/rsq/playerrounds.zs` (`sv_rsq_player_ballistics`, 0 = Hitscan = BD22 as shipped). Ported from the owner's
RS_Ballistics enemy fire. One `WorldHitscanPreFired` event per pellet (spread already rolled in), cancelled; a
round flies from the muzzle at 80 units a tic along the engine's own aim; when its per-tic trace finds something
it fires **the original hitscan** from 2 units short, so damage, damage type, puff, blood and kill credit are the
engine's own. Logged per gun: identical damage in both modes. The round's first trace runs as the shooter (the
muzzle can sit inside the player's own box). Tracers: `zscript/rsq/shotfx.zs` (Dakka, `rsq_shot_tracers`).

## Hand skin tone
`zscript/rsq/handtone.zs`, `tools/handtones.py`, `tools/handtone_build.py` (set tools).
Pre-tinted copies of the hand texture (Lab recolour keeping the shading), 18 steps (`rsq_hand_tone`). A skin
override is per actor and per model slot, and one actor often draws an FBX hand beside a gun or an Ermac hand in
slot 0, so the build moves every FBX hand block to **model slot 7** (in the built pk3 only) and the tone is
`A_ChangeModel`'s skin override on slot 7. Put slot 7's `Model` line LAST in a block (chapter 1.3). A 2D canvas
texture would have been smoother; it does not work on this build (chapter 1.7).

## HUD: magazine | reserve, and ammo on top
`zscript/rsq/counters.zs` (`RSQ_Counters.Hud`), `SBARINFO.rsq` (`rsq_hud_ammo`: 0 Magazine + Reserve, 1 Reserve
only). The status bar draws inventory counters the handler keeps (`RSQ_HudMag`, `RSQ_HudMagOff`, `RSQ_HudRes`).
**Ammo on top**: a loaded magazine never counts against what you can carry. A real-magazine gun lends up to 10
rounds into the reserve item, and that item's cap is raised by exactly the lent rounds, so a pickup still fills
the pouch to its cap.

## Fire rate on QZD 17.3 (semi-auto and held triggers)
`zscript/rsq/semiauto.zs`. `+WEAPON.NOAUTOFIRE` cannot work on 17.3: `PlayerPawn.TickPSprites` stores
`CheckWeaponFire`'s return in `player.attackdown` (`player.zs:583`), false whenever NOAUTOFIRE held the shot
back, so the next ready tic fires anyway. `RSQ_TriggerHeld` keeps `attackdown` set while the trigger stays down,
as desktop GZDoom does; a semi-auto gun takes a lock token on each shot (`RSQ_SemiLock`). Measured, trigger held
140 tics: Pistol 21 -> 13 shots, pump Shotgun 6 -> 1, the rest unchanged.

## Casings and ejection ports
`zscript/rsq/casings.zs` (`Port(w)`: where and which way: SIDE, DOWN or TIP), `casemodels.zs`. The port is found on
the mesh (a named surface, or a boundary loop of the welded ready frame), never from a card's estimate. Real 3D
casings are **lent** per instance to the parent's own casing actors with `A_ChangeModel` (one `EmptyBrass` is four
cartridges depending on the gun), not replacements.

## Recoil: why there is none
Built in 1.97, removed in 1.99 after the owner's headset pass: the only channel a pack has on the gun's layer is
`psp.x` / `psp.y` (yaw and pitch, no roll: chapter 1.4), additive kicks piled up during reloads and spun the gun
round the shoulder, and the gun pulled away from the hands. The parent mod's recoil that is in the mesh frames
stays, and the hands follow it through `gunmoves.zs`. `Weapon.BobPivot3D` (a writable field) could pivot a kick at
the grip; it was never shipped. The owner's rule on ModelSwapper: recoil does not belong there.
