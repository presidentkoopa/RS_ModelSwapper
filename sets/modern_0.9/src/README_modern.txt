RS Quest VR Weapons -- MODERN set
========================================

Generated 2026-10-24 by c2q (genpack.py + assemble.py) from the RS_VR_Weapons cards and meshes.
Target: QuestZDoom 17.3 (GZDoom 4.14.3 base, tag qzd17.3), stock engine, no engine changes.
Load after the IWAD. No other mod needed. Options: Options -> RS VR Weapons.

WHAT RELOADS IN VR
----------------------------------------
WM_BreachGlock           VR reload: magazine + handle, slide lock True [default rule (part slide)]; baked glockrerig.iqm frame 0 -> glockrerig_q.md3: body 5524 verts, magazine 897 verts, slide 1508 verts, trigger 97 verts; fire as pistol [card], slot 2; replaces Pistol; scale x +1.145 (REMA sign); eject port RIGHT (L -1.4)
WM_BreachGlockS          VR reload: magazine + handle, slide lock True [default rule (part slide)]; baked glocksil.iqm frame 0 -> glocksil_q.md3: body 5609 verts, magazine 897 verts, slide 2489 verts, trigger 97 verts; fire as pistol [card], slot 2; scale x +1.145 (REMA sign); eject port RIGHT (L -1.5)
WM_BreachKimber          VR reload: magazine + handle, slide lock True [default rule (part slide)]; baked kimber.iqm frame 0 -> kimber_q.md3: body 2563 verts, magazine 256 verts, slide 2701 verts; fire as pistol [card], slot 2; scale x +1.145 (REMA sign); eject port RIGHT (L -1.3)
WM_BreachMK18            VR reload: magazine + handle, slide lock False [card]; baked mk18nosil.iqm frame 25 -> mk18nosil_25_q.md3: body 29494 verts, charginghandle 3359 verts, magazine 3430 verts; dropped 2986 tris of ['j_mag2']; fire as rifle [card], slot 4; replaces Chaingun; scale x +1.145 (REMA sign); eject port RIGHT (L -2.0)
WM_BreachMK18S           VR reload: magazine + handle, slide lock False [card]; baked mk18nosil.iqm frame 25 + mk18newsilencer.iqm, mk18laser.iqm -> mk18nosil_25_x2_q.md3: body 33418 verts, charginghandle 3359 verts, magazine 3430 verts; dropped 2986 tris of ['j_mag2']; fire as rifle [card], slot 4; scale x +1.145 (REMA sign); eject port RIGHT (L -2.0)
WM_BreachHK416S          VR reload: magazine + handle, slide lock False [card]; baked hk416.iqm frame 25 -> hk416_25_q.md3: body 13968 verts, charginghandle 366 verts, magazine 1011 verts; dropped 812 tris of ['j_mag2']; fire as rifle [card], slot 4; scale x +1.145 (REMA sign); eject port RIGHT (L -1.7)
WM_BreachMCX             VR reload: magazine + handle, slide lock False [card]; baked mcxrig.iqm frame 25 -> mcxrig_25_q.md3: body 9872 verts, charginghandle 411 verts, magazine 1129 verts; dropped 1952 tris of ['j_mag2']; fire as rifle [card], slot 4; scale x +1.145 (REMA sign); eject port RIGHT (L -1.8)
WM_BreachG36C            VR reload: magazine; baked g36rerig.iqm frame 25 -> g36rerig_25_q.md3: body 8316 verts, magazine 880 verts; dropped 1014 tris of ['j_mag2']; part charginghandle: joint j_charginghandle owns no vertices (empty); fire as rifle [card], slot 4; scale x +1.145 (REMA sign); eject port RIGHT (L -2.8)
WM_BreachMP5             VR reload: magazine + handle, slide lock False [card]; baked mp5.iqm frame 109 -> mp5_109_q.md3: body 5857 verts, charginghandle 118 verts, magazine 301 verts; dropped 284 tris of ['j_mag2']; fire as smg [card], slot 4; scale x +2.290 (REMA sign); eject port RIGHT (L -1.7)
WM_BreachBenelli         stock reload (no feed part); fire as shotgun [card], slot 3; replaces Shotgun; scale x +2.620 (REMA sign); eject port RIGHT (L -1.9)

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
  * Sounds: 15 resolved.

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
