RS Quest VR Weapons -- VANILLA set
========================================

Generated 2026-10-24 by c2q (genpack.py + assemble.py) from the RS_VR_Weapons cards and meshes.
Target: QuestZDoom 17.3 (GZDoom 4.14.3 base, tag qzd17.3), stock engine, no engine changes.
Load after the IWAD. No other mod needed. Options: Options -> RS VR Weapons.

WHAT RELOADS IN VR
----------------------------------------
WM_BFG                   stock reload (feed part cell names no surface (joint / baked part)); fire as bfg [card], slot 7; shotclass RSB_BFGBall -> BFGBall; chargetics 30 not carried; replaces BFG9000; scale x -1.000 (REMA sign); no eject port on card
WM_BFGHeavy              stock reload (feed part cell names no surface (joint / baked part)); fire as bfg [card], slot 7; shotclass RSB_BFGBallHeavy -> BFGBall; chargetics 30 not carried; scale x -1.000 (REMA sign); no eject port on card
WM_Chaingun              stock reload (no feed part); fire as chaingun [card], slot 4; spinuptics 10 not carried; replaces Chaingun; scale x -1.000 (REMA sign); eject port RIGHT (L -13.7)
WM_MachineGun            stock reload (no feed part); fire as chaingun [card], slot 4; scale x -1.000 (REMA sign); eject port RIGHT (L -3.5)
WM_Chainsaw              stock reload (no feed part); fire as chainsaw [card], slot 1; replaces Chainsaw; scale x +1.350 (REMA sign); no eject port on card
WM_ChainsawHeavy         stock reload (no feed part); fire as chainsaw [card], slot 1; scale x -1.000 (REMA sign); no eject port on card
WM_RocketLauncher        VR reload: magazine; fire as launcher [card], slot 5; shotclass RSB_Rocket -> Rocket; replaces RocketLauncher; scale x -1.000 (REMA sign); no eject port on card
WM_RPG                   VR reload: magazine; fire as launcher [card], slot 5; shotclass RSB_RocketRPG -> Rocket; scale x -1.000 (REMA sign); no eject port on card
WM_M4A3                  VR reload: magazine + handle, slide lock True [default rule (part slide)]; fire as pistol [card], slot 2; replaces Pistol; scale x -0.820 (REMA sign); eject port RIGHT (L -1.2)
WM_Pistolet              VR reload: magazine + handle, slide lock True [default rule (part slide)]; fire as pistol [card], slot 2; scale x +1.350 (REMA sign); eject port RIGHT (L -1.8)
WM_PlasmaRifle           VR reload: magazine; fire as plasma [card], slot 6; shotclass RSB_PlasmaBall -> PlasmaBall; replaces PlasmaRifle; scale x -1.000 (REMA sign); no eject port on card
WM_PlasmaRifleBlue       VR reload: magazine; fire as plasma [card], slot 6; shotclass RSB_PlasmaBallCarbine -> PlasmaBall; scale x -1.000 (REMA sign); no eject port on card
WM_PumpM37               stock reload (no feed part); fire as shotgun [card], slot 3; scale x -1.100 (REMA sign); eject port centre (L +0.0)
WM_PumpDoom              stock reload (no feed part); fire as shotgun [card], slot 3; replaces Shotgun; scale x +1.350 (REMA sign); eject port RIGHT (L -1.9)
WM_SSG                   stock reload (no feed part); fire as breakaction [card], slot 3; replaces SuperShotgun; scale x +1.350 (REMA sign); eject port centre (L +0.0)
WM_BullpupPump           stock reload (no feed part); fire as shotgun [card], slot 3; scale x -1.100 (REMA sign); eject port LEFT (L +2.7)

HOW TO RELOAD (magazine guns, in VR, rsr_reload 1)
----------------------------------------
  Press the gun's reload (or the off-hand reload button) -> the magazine drops out.
  Reach the off hand to the gun's well, pull the off trigger (rsr_grab_with) -> a fresh magazine is in the hand.
  Bring it to the well: it snaps to the axis and follows your depth; push it home to seat it.
  Guns with a slide / charging handle: grab the handle with the off hand, pull it back and let go.
  Out of VR, or with reloading set to Stock, the same button does a canned reload.

FLAGS -- read before judging a gun
----------------------------------------
  * Gunplay numbers (damage, pellets, rate, auto) come from each set's WMSHEET where it has them; what the
    sheets do not carry (damage) is Doom's own by gun type (genpack FIRE table). Alt-fire modes are not carried.
  * Slide / bolt lock-open on empty: from the card where its rack cycle declares holdopen; otherwise a RULE
    (a part named slide/bolt locks, a charging handle does not). Each gun's line above says which.
  * Scale x sign follows REMA's MODELDEF for the mesh. Eject-port side per gun is in the line above:
    "LEFT" on a right-handed gun means the mesh or its card is mirrored -- check in the headset.
  * VR hands are OFF (rsq_hands 0): the hand meshes are Ermac's, art licensed for education only, so no
    public set ships them. Reloading works without hands. A private hand pack can switch them on.
  * Pump and break-open guns use the canned reload in this pass (the Quest pump / break modules are present
    but have no tables yet). BFG-type cells with no mesh surface: canned reload.
  * Modern (IQM) guns are baked at their rest pose into MD3s split by joint; the rig's view arms and the
    parked second magazine are dropped. Their animation frames are not used.
  * Sounds: 31 resolved.

RUNTIME
----------------------------------------
  Pack 1.92 reload modules (vreload, rsr_assist, rsr_break, rsr_pump, hands, handler, vrhand) copied from source
  with these exact-match edits only:
    rsvr/vrhand.zs       verbatim
    rsvr/melee.zs        verbatim
    rsq/handler.zs       verbatim
    rsq/fistmoves.zs     verbatim
    rsq/scope.zs         verbatim
    rsq/scope_real.zs    verbatim
    rsr/rsr_break.zs     verbatim
    rsr/rsr_pump.zs      verbatim
    rsq/hands.zs         no dual wield module; no grenade module; no BD22 purist rifle; no BD22 purist rifle; no BD22 purist rifle; punch strike: this pack's own
    rsq/fists.zs         punch strike: this pack's own
    rsr/vreload.zs       slide lock from the table, not BD22 indexes; no BD22 purist mode
    rsr/rsr_assist.zs    rocket capture by part length, not BD22 index; rocket tilt by part length, not BD22 index
    MODELDEF.rsq         pack 1.92 hand blocks: RSQ_GunSide (hand.md3, hand2.md3, fist, ammo hand), RSQ_Hands free hand; reload holds RQHN I (rsr), J L (rsb), RQUN A (pump); grenade ring and debris blocks left out
  Stubs (interface from the pack source, Index 0): RSB_Guns, RSP_Guns, RSQ_HandTable, RSQ_GunMoves, RSK_M203Handler, RSG_Handler.

Build reports: genpack_report.json, assemble_report.json in the pk3. Render sheets: _sheets/.
