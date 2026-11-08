# 1. How VR weapons work on QuestZDoom 17.3

QuestZDoom 17.3 is GZDoom 4.14.3 with an OpenXR layer (tag `qzd17.3`, commit 9afc750 of
`emawind84/gzdoom`; the Android wrapper with the VR input code is `emawind84/questzdoom` a85c819). The rig
checks out both (`sh tools/rig/setup.sh build` puts them in `tools/rig/build/src/qzd` and `.../qzw`). The
line numbers below are from those checkouts. Read the source when in doubt: the ZScript version ceiling and
the VR hooks differ from current GZDoom and UZDoom.

## 1.1 Head and hands

Every rendered frame the engine reads the headset and both controllers and writes them onto the **console
player's** pawn (`hw_vrmodes.cpp`; the fallback at line 442 sets both to the view point when there is no VR):

| field (on the PlayerPawn) | what |
|---|---|
| `AttackPos` | the weapon controller, world position |
| `OffhandPos` | the other controller, world position |
| `AttackDir(mo, yaw, pitch)` / `OffhandDir(...)` | a direction in that controller's frame, as world angles |
| `OverrideAttackPosDir` | true while playing in VR |
| `HmdPosition` | the head |
| `player.WeaponState & WF_TWOHANDSTABILIZED` | the gun is steadied (below) |

`sets/bd22q/src/zscript/rsvr/vrhand.zs` (`RSVR_VRHand`) is the only file in BD22 that reads these; use it
or copy it. Two things to know:
- **They exist for the console player only**, and only after the first rendered frame. A pawn restored from a
  save thinks before that frame; calling `AttackDir` there crashed the game (vrhand.zs guards it with
  `OverrideAttackPosDir`). For anything other players must agree on (melee), BD22 sends the pose as a
  netevent once a tic and everyone reads that history (`zscript/rsq/pose.zs`).
- **Every player hitscan and rail starts at `AttackPos`**, the controller, not at the muzzle you see
  (`p_map.cpp` P_LineAttack / P_RailAttack). On a long rifle that is 60 cm behind the muzzle.
  `zscript/rsq/muzzle.zs` moves it (chapter 5).

**Steadying.** With `vr_two_handed_weapons` on, pressing the off grip with the off controller within
**50 cm** of the gun controller steadies the gun (`VrInputDefault.cpp:131-140`, `distance < 0.50f`). The
engine then **re-aims the gun from the main hand towards the off hand** and stops drawing the off-hand
weapon's layers (`hw_weapon.cpp:832`). Two consequences you will meet: a hand that was on a charging handle
is suddenly somewhere else the tic the grip goes down, and a sword steadied with the off hand below the main
hand swings its blade onto the off hand. A mod cannot change `vr_two_handed_weapons` (only a menu can).

## 1.2 How a weapon model is drawn

A weapon's psprite layer is drawn as a 3D model when MODELDEF has a block for its sprite and frame. In VR the
model hangs off the controller. The chain, from `RenderHUDModel` (`src/r_data/models.cpp:211-268`), applied
to a mesh vertex:

```
controller transform (GetWeaponTransform: the hand; the LEFT hand is mirrored, below)
  * scale 0.01, translate (0, 5, 30)                   [VR only]
  * scale (Scale.x, Scale.z, Scale.y)                  MODELDEF Scale
  * translate (Offset.x, ZOffset, Offset.y) / scale    MODELDEF Offset / ZOffset
  * translate (-vr_3dweaponOffsetX, Y, Z)              player cvars
  * rotate about the pivot by the layer's rotation     ModifyBobLayer3D (below)
  * translate by the layer's translation               ModifyBobLayer3D
  * rotate 90 about y                                  "jDoom models need to be rotated"
  * rotate -AngleOffset (y), PitchOffset (z), -RollOffset (x)
  * vertex
```

Plus `vr_weaponScale` (default 1.02) and `vr_weaponRotate` (default -30) from `hw_vrmodes.cpp:106-107`. You
never do this by hand: `tools/handfit/core/hands_tool/hudrender.py` (`to_local`) is this chain, and
`gunview.to_fl()` turns it into F / L / U cm. Every measured number in BD22 went through it.

**The layer's own offset tilts it.** `hw_weapon.cpp:108` adds `(mx / 4, (my - WEAPONTOP) / -4, 0)` degrees
to every layer's rotation. A layer drawn at y = 0 is tilted 8 degrees. New layers are drawn at y = WEAPONTOP
(32); `vreload.zs` says so as a constant.

**Sprite or model.** A weapon with no MODELDEF block for its current sprite frame draws as a flat sprite. In
VR that is a 2D picture glued to your hand. A fire frame that nobody keyed in MODELDEF draws as a sprite for
those tics (BD22's Ruger did it for three tics a shot). Every sprite frame a gun can show needs a
`FrameIndex` line.

## 1.3 MODELDEF, the parts that matter

```
Model Rifle                       // the class whose psprites this block draws
{
   Path "models/bd/Rifle"
   Model 0 "Rifle.md3"            // slot 0: the gun
   Skin 0 "Rifle.png"
   Model 1 "M203.md3"             // slot 1: the launcher under it
   Skin 1 "M203.png"
   Scale -1.0 1.0 1.0
   Offset 0.348 -5.912 0.0
   ZOffset -1.812                 // overwrites Offset's z
   AngleOffset 3.854
   PitchOffset 3.363
   RollOffset 10.974              // the gun moved to the FBX hand (sets/bd22q/src/MODELDEF.bd.txt)
   NoInterpolation
   FrameIndex RIFG A 0 3          // sprite RIFG frame A -> slot 0, mesh frame 3
   ...
}
```

- **`ZOffset` and `Offset` write the same field.** `Offset x y z` sets all three; `ZOffset z` sets the third.
  Whichever line comes **last** wins (`models.cpp:853-866`). BD22 writes `Offset ... 0.0` and then `ZOffset`,
  so ZOffset is the real height. A tool that reads only `Offset` gets the gun 5 cm off (this happened).
- **A block is sized by its LAST `Model` line**, not the largest: `modelsAmount = index + 1` for each `Model`
  line in order, minimum 4 (`models.cpp:769-775`). A block that lists `Model 7` then `Model 1` has 2 slots, and
  slot 7 gives "Too many models". Put the highest slot last. `tools/int20_rig/mdslots.py <pk3>` checks a pack.
- **`FrameIndex SPRITE FRAME slot meshframe`** binds a sprite frame to a mesh frame per slot. The gun's ready
  pose is whatever frame its Ready sprite binds, which is not frame 0 (BD22's pistol: frame 3).
- **`AngleOffset / PitchOffset / RollOffset`** turn the model. With Offset and ZOffset they are the six numbers
  the hand fitter writes when it moves a gun to the hand ("the gun move").
- **A whole-model `Skin` beats every `SurfaceSkin`**, and beats `A_ChangeModel`'s surface-skin swap too
  (`src/common/models/models_md3.cpp:357-369`: the surface skins are read only when no model skin is set).
  The RailGun's scope glass showed the whole texture atlas for this reason. A gun with a part that changes
  skin (a scope glass) must use `SurfaceSkin` for every surface.
- One class can have several `Model <Class>` blocks for different sprites (BD22's Rifle has blocks for its
  kick boot and grenade too). When you move a gun, move every block that draws it on the gun controller,
  and only those: `port_gun.py` finds them and asserts the count (chapter 3).

## 1.4 How hands are drawn

A hand is a model on its own psprite layer. The engine cannot parent one layer to another, so each hand is
placed every rendered frame by an answer:

- **Which controller.** A layer is drawn on the **off** controller only when its caller is the player's
  off-hand weapon (`models.cpp:221`, `hand = psp->GetCaller() == player->OffhandWeapon`). So BD22 has
  `RSQ_Hands`, an off-hand weapon that never fires, which owns the free hand (layer 2200), and `RSQ_GunSide`,
  a plain inventory item, which owns the gun hand (2100) and the support hand (2101) on the main controller
  (`zscript/rsq/hands.zs`, `RSQ_Layers`).
- **Where on it.** `hw_weapon.cpp` asks the off-hand weapon's `ModifyBobLayer3D` (ZScript virtual,
  `weapons.zs:46`) for every layer that is not the ready weapon's own; it returns a translation and a
  rotation (the "hook"). `RSQ_Hands` returns the row for the gun in hand from `zscript/rsq/handtable.zs`
  (`GunHook`, `GunRot`, `SupportHook`, `SupportRot`, `SupportPoint`).
- **Following the gun's own animation.** BD22's recoil is in the mesh frames, so when a fire frame moves
  the gun, the hands are told by `zscript/rsq/gunmoves.zs` (generated: a pivot and per-frame turn and move
  rows) so they stay on it.
- **Since 2.0 the FBX hands are baked "in place"**: each hand frame is baked where it is drawn, so its hook
  is 0 and the MODELDEF block that draws it carries the same placement as the gun. The only computed part is
  which frame to show (trigger or squeeze, support or not).
- **Layer ids are shared.** One psprite id holds one caller. Two features using the same id both
  `SetPsprite` it every tic and one silently stops working. `RSQ_Layers.Taken(id)` in `hands.zs` lists the
  ids in use; ask it before claiming a new one.
- **What the gun layer cannot do.** `ModifyBobLayer3D` is dispatched on the class that owns the layer. The
  gun's own layer belongs to the parent mod's weapon class, and **ZScript cannot inherit or extend a DECORATE
  class or `Weapon` itself** (`extend class Weapon` gives "Class Weapon cannot be found in the current
  translation unit"). So a pack cannot roll the gun model; `psp.x` / `psp.y` (yaw and pitch) is the whole
  channel. This is why recoil roll is impossible on 17.3 and why recoil was finally taken out of BD22.

## 1.5 The off hand is mirrored

`GetWeaponTransform` scales the LEFT hand's transform by (-1, 1, 1) unless the weapon has
`WIF_NO_AUTO_REVERSE` (`hw_vrmodes.cpp:455-470`). So:
- **A right-hand mesh drawn on the left controller is a left hand.** Every off-hand FBX frame is baked as the
  RIGHT rig; the engine mirrors it. A frame baked as a left hand draws as a right hand on the left
  controller (the first FBX free hand did exactly this).
- **The off hand's L axis is flipped.** A point in the gun's frame at L = +3 is at L = -3 in the off hand's
  frame. The rig's off-hand drivers flip L, and for a magazine that goes in from the side (|axis L| > 0.5)
  also turn the hand 180 degrees (`tools/rig/mags.py`, `at()`).
- `OffhandDir` already includes the mirror, so axes from `RSVR_VRHand.OffDir` are the ones the off-hand
  layers are drawn in.

## 1.6 `A_ChangeModel`: lending a model per actor

`A_ChangeModel(modeldef, modelindex, modelpath, model, skinindex, skinpath, skin, flags, ...)`
(`actor.zs:1232`) points ONE actor instance's model data at another MODELDEF block, or swaps one slot's mesh
or skin. The HUD render reads the psprite caller's per-instance model data before its class's, so it works on
weapons and hand layers. BD22 uses it to:
- put real 3D casings on Brutal Doom's own casing actors, per instance, because one `EmptyBrass` is four
  different cartridges depending on the gun (`zscript/rsq/casemodels.zs`);
- swap the scope glass skin to the camera texture (`zscript/rsq/scope_real.zs`);
- skin every FBX hand with the chosen skin tone through model slot 7 (`zscript/rsq/handtone.zs`);
- ModelSwapper uses it to put any model on any mod's weapon (`rs_modelswapper/INTERNALS.md`).

Remember 1.3: it cannot beat a whole-model `Skin`.

## 1.7 Camera textures

`ANIMDEFS`: `cameratexture RSQSCOPE 256 256 fit 240 200` declares a texture a camera actor renders into
(`SetCameraToTexture`). A surface whose skin is that texture shows the camera's view: that is the live scope.
The engine renders a camera texture only if it was drawn last frame, so taking the skin off costs nothing.
It renders at `aspectRatio / pixelstretch` (`hw_entrypoint.cpp:400`): a square 256 x 256 texture came out
squashed to 0.83 until it was declared 240 x 200 (ratio 1.2 = BD22's pixelstretch). The picture is mono: both
eyes see the same texture. The 2D canvas texture (drawing into a texture from ZScript) does **not** work on
this 17.3 build (it renders unchanged or black); camera textures do.

## 1.8 Where a mod hooks in (no engine changes)

| need | hook |
|---|---|
| where a hand or extra layer is drawn, per frame | `ModifyBobLayer3D` on an off-hand weapon you own |
| move a hitscan's start | `WorldHitscanPreFired` (cancel, re-fire with `LineAttack(LAF_ABSPOSITION)`); needs `version "4.14"` or later in the root ZSCRIPT lump |
| per-tic logic per player | an `EventHandler` (it must be listed in MAPINFO `AddEventHandlers`, or it compiles and never runs) |
| per-instance model / skin | `A_ChangeModel` |
| the controllers, buttons, steadying | `RSVR_VRHand` (1.1), `player.cmd.buttons` (`BT_OFFHANDATTACK` is the off trigger) |
| something DECORATE must inherit | write it in DECORATE: ZSCRIPT compiles first, so DECORATE can name a ZScript class but not the reverse |
| haptics | already there: the engine buzzes the firing hand on P_LineAttack / P_RailAttack / P_SpawnPlayerMissile |
