RS Quest VR Weapons -- PLUS set
========================================

Generated 2026-10-24 by c2q (genpack.py + assemble.py) from the RS_VR_Weapons cards and meshes.
Target: QuestZDoom 17.3 (GZDoom 4.14.3 base, tag qzd17.3), stock engine, no engine changes.
Load after the IWAD. No other mod needed. Options: Options -> RS VR Weapons.

WHAT RELOADS IN VR
----------------------------------------
WM_VP_BFG                stock reload (feed part cell names no surface (joint / baked part)); fire as bfg [card], slot 7; shotclass RSB_BFGBall -> BFGBall; chargetics 30 not carried; replaces BFG9000; scale x -1.000 (REMA sign); no eject port on card
WM_VP_BFGHeavy           stock reload (feed part cell names no surface (joint / baked part)); fire as bfg [card], slot 7; shotclass RSB_BFGBallHeavy -> BFGBall; chargetics 30 not carried; scale x -1.000 (REMA sign); no eject port on card
WM_VP_Chaingun           stock reload (no feed part); fire as chaingun [card], slot 4; spinuptics 10 not carried; replaces Chaingun; scale x -1.000 (REMA sign); eject port RIGHT (L -13.7)
WM_VP_MachineGun         stock reload (no feed part); fire as chaingun [card], slot 4; scale x -1.000 (REMA sign); eject port RIGHT (L -3.5)
WM_VP_Chainsaw           stock reload (no feed part); fire as chainsaw [card], slot 1; replaces Chainsaw; scale x +1.350 (REMA sign); no eject port on card
WM_VP_ChainsawHeavy      stock reload (no feed part); fire as chainsaw [card], slot 1; scale x -1.000 (REMA sign); no eject port on card
WM_VP_Unmaker            VR reload: magazine; fire as bfg [card], slot 7; shotclass WM_UnmakerBolt -> PlasmaBall; scale x -1.000 (REMA sign); no eject port on card
WM_VP_Bolter             VR reload: magazine; fire as plasma [card], slot 6; shotclass WM_BolterBolt -> PlasmaBall; scale x -1.100 (REMA sign); no eject port on card
WM_VP_AssaultShotgun     VR reload: magazine + handle, slide lock False [default rule (part charginghandle)]; fire as shotgun [card], slot 3; scale x -1.000 (REMA sign); eject port LEFT (L +2.0)
WM_VP_BFGRifle           stock reload (feed part cell names no surface (joint / baked part)); fire as bfg [card], slot 7; shotclass RSB_BFGBall -> BFGBall; scale x -1.100 (REMA sign); no eject port on card
WM_VP_PlasmaCarbine      VR reload: magazine; fire as plasma [card], slot 6; shotclass RSB_PlasmaBallCarbine -> PlasmaBall; scale x -1.000 (REMA sign); no eject port on card
WM_VP_LongbarChainsaw    stock reload (no feed part); fire as chainsaw [card], slot 1; scale x -1.100 (REMA sign); no eject port on card
WM_VP_RotaryGun          stock reload (no feed part); fire as chaingun [card], slot 4; scale x -1.100 (REMA sign); eject port RIGHT (L -11.2)
WM_VP_RotaryLauncher     stock reload (no feed part); fire as launcher [card], slot 5; shotclass RSB_Rocket -> Rocket; scale x -1.100 (REMA sign); no eject port on card
WM_Moonlight             stock reload (no feed part); fire as revolver [card], slot 2; altmode fan not carried; scale x +1.350 (REMA sign); eject port centre (L -0.0)
WM_Sunset                stock reload (no feed part); fire as revolver [card], slot 2; altmode fan not carried; scale x +1.350 (REMA sign); eject port centre (L -0.0)
WM_ColaRevolver          stock reload (no feed part); fire as revolver [card], slot 2; altmode fan not carried; scale x -0.700 (REMA sign); eject port centre (L +0.0)
WM_Rifle                 VR reload: magazine + handle, slide lock False [default rule (part charginghandle)]; fire as rifle [card], slot 4; altmode selectfire not carried; altburst 3 not carried; scale x -1.000 (REMA sign); eject port RIGHT (L -1.4)
WM_M16                   VR reload: magazine + handle, slide lock False [default rule (part charginghandle)]; fire as rifle [card], slot 4; altmode selectfire not carried; altburst 3 not carried; scale x +1.350 (REMA sign); eject port LEFT (L +2.0)
WM_PistoletBlue          VR reload: magazine + handle, slide lock True [default rule (part slide)]; fire as pistol [card], slot 2; altmode burst not carried; altburst 3 not carried; scale x +1.350 (REMA sign); eject port RIGHT (L -1.8)
WM_Flamer                VR reload: magazine; fire as flamethrower [card], slot 6; shotclass WM_FlameShot -> FatShot; scale x -1.100 (REMA sign); no eject port on card
WM_Flamethrower          VR reload: magazine; fire as flamethrower [card], slot 6; shotclass WM_NapalmShot -> FatShot; scale x -1.000 (REMA sign); no eject port on card
WM_SMG                   VR reload: magazine; action part charginghandle is a hinge: not driven (the Quest handle is a straight pull); fire as smg [card], slot 4; altmode shred not carried; scale x -1.000 (REMA sign); eject port RIGHT (L -2.7)
WM_Tec9                  VR reload: magazine + handle, slide lock True [default rule (part bolt)]; fire as smg [card], slot 4; altmode shred not carried; scale x -1.100 (REMA sign); eject port RIGHT (L -2.4)
WM_VP_RocketLauncher     VR reload: magazine; fire as launcher [card], slot 5; shotclass RSB_Rocket -> Rocket; replaces RocketLauncher; scale x -1.000 (REMA sign); no eject port on card
WM_VP_RPG                VR reload: magazine; fire as launcher [card], slot 5; shotclass RSB_RocketRPG -> Rocket; scale x -1.000 (REMA sign); no eject port on card
WM_VP_M4A3               VR reload: magazine + handle, slide lock True [default rule (part slide)]; fire as pistol [card], slot 2; altmode burst not carried; altburst 3 not carried; replaces Pistol; scale x -0.820 (REMA sign); eject port RIGHT (L -1.2)
WM_VP_Pistolet           VR reload: magazine + handle, slide lock True [default rule (part slide)]; fire as pistol [card], slot 2; altmode burst not carried; altburst 3 not carried; scale x +1.350 (REMA sign); eject port RIGHT (L -1.8)
WM_VP_PlasmaRifle        VR reload: magazine; fire as plasma [card], slot 6; shotclass RSB_PlasmaBall -> PlasmaBall; replaces PlasmaRifle; scale x -1.000 (REMA sign); no eject port on card
WM_VP_PlasmaRifleBlue    VR reload: magazine; fire as plasma [card], slot 6; shotclass RSB_PlasmaBallCarbine -> PlasmaBall; scale x -1.000 (REMA sign); no eject port on card
WM_VP_PumpM37            stock reload (no feed part); fire as shotgun [card], slot 3; altmode slamfire not carried; scale x -1.100 (REMA sign); eject port centre (L +0.0)
WM_VP_PumpDoom           stock reload (no feed part); fire as shotgun [card], slot 3; altmode slamfire not carried; replaces Shotgun; scale x +1.350 (REMA sign); eject port RIGHT (L -1.9)
WM_VP_SSG                stock reload (no feed part); fire as breakaction [card], slot 3; altmode onebarrel not carried; replaces SuperShotgun; scale x +1.350 (REMA sign); eject port centre (L +0.0)
WM_VP_BullpupPump        stock reload (no feed part); fire as shotgun [card], slot 3; altmode doubleshell not carried; scale x -1.100 (REMA sign); eject port LEFT (L +2.7)

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
  * Sounds: 50 resolved.

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
