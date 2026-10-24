// RS VR hands for BD22 and Vanilla VR Plus on QuestZDoom 17.x. rsq_hands 0 hides them.
//
// The hands and their poses are Ermac's (Force Unleashed / Rusted Legacy, MIT):
// a gun hand posed on each gun's grip, a support hand posed on its front, and
// an off hand that is open, or holds the right magazine / shell / cell while
// reloading. rsq_hands_gen.py fitted his poses onto each set's guns
// (handtable.zs, one per set).
//
//   gun hand      always on the gun (none for melee weapons, two-gun weapons and the flame
//                 cannon your arm goes into). Fists and punches: Ermac's fist, in both
//                 hands; the VR grenade: his ammo hand round it (OwnHand)
//   off hand      free on the off controller. When the engine steadies the gun
//                 with both hands (the off hand brought to the gun and grip
//                 pressed: vr_two_handed_weapons), it takes hold of the front
//                 of the gun (the support hand), the way Ermac's two-hand
//                 models swap in, and lets go when the engine does. It never
//                 holds on while a reload needs it.
//
// The gun and support hands stay on the gun when it moves under them: when its
// layer is offset (raised, lowered, kicked by Offset) and when its model frames
// kick (BD22's and Vanilla VR Plus's recoil is in the meshes: gunmoves.zs, one
// per set, made by rsq_gunmoves_gen.py).
//
// How they reach the controllers (no engine changes): models.cpp puts a layer
// on the OFF controller only when its caller is the off-hand weapon, so the
// free hand belongs to RSQ_Hands (an off-hand weapon that never fires) and the
// gun and support hands to RSQ_GunSide (a plain item: main controller).
// hw_weapon.cpp asks the off-hand weapon's ModifyBobLayer3D where to put every
// layer that is not the ready weapon's; that places them per gun.

class RSQ_Layers abstract
{
	const GUNHAND = 2100;	// RSQ_GunSide, main controller
	const SUPPORT = 2101;	// RSQ_GunSide, main controller
	const FREEHAND = 2200;	// RSQ_Hands, off controller

	// 2026-10-23: ONE PSPRITE ID HOLDS ONE CALLER. Several lanes hand out layer ids in this
	// range -- the hands here, the real reload (rsr/vreload.zs), break-open (rsr_break.zs),
	// the pump (rsr_pump.zs), the M203 (rsr_m203.zs) -- and a clash between them is silent:
	// both owners SetPsprite the same id every tic and whichever ran last wins, so one of the
	// two features simply stops working with nothing in the log. Anything claiming a NEW id
	// asks here first. Free as of today: 2112-2119, 2124-2129, and 2132 upward.
	clearscope static bool Taken(int id)
	{
		return id == GUNHAND || id == SUPPORT || id == FREEHAND
			|| id >= RSR.LAYER_FIRST && id <= RSR.LAYER_LAST || id == RSR.HANDMAG
			|| id >= RSB.LAYER_FIRST && id <= RSB.LAYER_LAST
			|| id == RSB.HANDROUND || id == RSB.HANDROUND2
			|| id >= RSP.LAYER_FIRST && id <= RSP.LAYER_LAST || id == RSP.HANDSHELL
			|| id >= RSM.LAYER_FIRST && id <= RSM.LAYER_LAST;
	}
}

class RSQ_GunSide : Inventory
{
	Default
	{
		Inventory.MaxAmount 1;
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		+INVENTORY.QUIET
	}

	States
	{
	GunA: RQGS A -1; Stop;
	GunB: RQGS B -1; Stop;
	GunC: RQGS C -1; Stop;
	GunD: RQGS D -1; Stop;
	GunE: RQGS E -1; Stop;
	GunF: RQGS F -1; Stop;
	GunG: RQGS G -1; Stop;
	GunH: RQGS H -1; Stop;	// BD22 v9: axe, chainsaw. V+: BFG
	// the gun hand with its index finger on the trigger, and squeezing it (fire held)
	TrgA: RQGT A -1; Stop;
	SqzA: RQGU A -1; Stop;
	TrgB: RQGT B -1; Stop;
	SqzB: RQGU B -1; Stop;
	TrgC: RQGT C -1; Stop;
	SqzC: RQGU C -1; Stop;
	TrgD: RQGT D -1; Stop;
	SqzD: RQGU D -1; Stop;
	TrgE: RQGT E -1; Stop;
	SqzE: RQGU E -1; Stop;
	TrgF: RQGT F -1; Stop;
	SqzF: RQGU F -1; Stop;
	TrgG: RQGT G -1; Stop;
	SqzG: RQGU G -1; Stop;
	TrgH: RQGT H -1; Stop;
	SqzH: RQGU H -1; Stop;
	TrgI: RQGT I -1; Stop;
	SqzI: RQGU I -1; Stop;
	TrgJ: RQGT J -1; Stop;
	SqzJ: RQGU J -1; Stop;
	TrgK: RQGT K -1; Stop;
	SqzK: RQGU K -1; Stop;
	TrgL: RQGT L -1; Stop;
	SqzL: RQGU L -1; Stop;
	TrgM: RQGT M -1; Stop;
	SqzM: RQGU M -1; Stop;
	TrgN: RQGT N -1; Stop;
	SqzN: RQGU N -1; Stop;
	TrgO: RQGT O -1; Stop;
	SqzO: RQGU O -1; Stop;
	TrgP: RQGT P -1; Stop;
	SqzP: RQGU P -1; Stop;
	TrgQ: RQGT Q -1; Stop;
	SqzQ: RQGU Q -1; Stop;
	TrgR: RQGT R -1; Stop;
	SqzR: RQGU R -1; Stop;
	SupA: RQSP A -1; Stop;
	SupM1: RQ2S A -1; Stop;	// 1.31 RSR-M203: the off hand on the launcher, finger on its trigger
	SupM2: RQ2S B -1; Stop;	// ...squeezed
	SupB: RQSP B -1; Stop;
	SupC: RQSP C -1; Stop;
	SupD: RQSP D -1; Stop;
	SupE: RQSP E -1; Stop;
	SupF: RQSP F -1; Stop;
	Fist: RQGF A -1; Stop;	// Ermac's fist (the free hand's fist): fists, punches
	Nade: RQGN A -1; Stop;	// Ermac's ammo hand round the VR grenade
	// 2026-10-23: the VR scope's collimated reticle (rsq/scope.zs, layer RSQ_ScopeLayers.RETICLE).
	// Its own sprite, so it carries its own flat quad in MODELDEF and nothing about it is tied
	// to the hand meshes; ModifyBobLayer3D puts it on the glass every rendered frame. Bright,
	// because a reflex dot is light on glass and not paint on it.
	ScopeDot: RQRT A -1 Bright; Stop;
	ScopeRing: RQRT B -1 Bright; Stop;	// the same dot inside a ring; no option selects it yet
	Hidden: TNT1 A -1; Stop;
	}
}

class RSQ_Hands : Weapon
{
	// 2026-10-23: where the scope reticle's quad is parked when there is no sight picture.
	// Centimetres back along the model's own z (see ModifyBobLayer3D), so it clips away.
	const DOT_FARAWAY = 1000000.0;

	// How the ready weapon's model frame has moved the gun (RSQ_GunMoves), for
	// ModifyBobLayer3D: looked up in play by A_RSQ_Layers when the gun layer
	// changes frame, read by the renderer.
	State gunState;				// the gun layer's state, sprite and frame they are for
	int gunSprite, gunFrame;
	Vector3 gunTurn, gunMove;	// that frame
	Vector3 nextTurn, nextMove;	// the next state's frame, which the engine blends toward
	bool showOwn;				// the gun hand shows its own fist or grenade hold (OwnHand), at Ermac's placement
	bool freeFist;				// the free hand is a fist this tic (rsq/fists.zs punches with it)
	Array<int> fistSprites;		// BD22's punch / fist sprites (MODELDEF.bd.txt hides its glove on them)
	int nadeSprite;
	Array<int> bdHandSprites;
	Array<int> ongSprites, ungSprites;	// 1.5: the jab / cross and uppercut families (RSQ_FistMoves)
	int unsSprite;
	int fistMesh, fistMeshPrev;			// the main fist's BD punch frame, this tic and the last
	int offMesh, offMeshPrev;			// the off fist's punch frame
	int offPunchTic;					// -1 idle; the off-hand trigger punch's tic
	bool offTrigPrev;	// sprites where BD22's own hand model shows (taunts, grabs, carries)
	bool dotClash;		// the scope reticle's layer id clashes with another lane's: said once

	override void BeginPlay()
	{
		Super.BeginPlay();
		offPunchTic = -1;
	}

	Default
	{
		+WEAPON.OFFHANDWEAPON
		+WEAPON.NOHANDSWITCH
		+WEAPON.NO_AUTO_SWITCH
		+WEAPON.NOAUTOSWITCHTO
		+WEAPON.NOALERT
		+WEAPON.CHEATNOTWEAPON
		+WEAPON.NODEATHINPUT
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		+INVENTORY.QUIET
		Weapon.SelectionOrder 32000;
		Weapon.Kickback 0;
		Weapon.UpSound "";
		Weapon.ReadySound "";
		Weapon.UseRange 48;
		Tag "Fist";
		Weapon.SlotNumber 1;	// 1.5: selectable in the OFF hand (slot 1), so a gun moved there can be swapped back for the fist
	}

	static bool OffFist(PlayerPawn mo)
	{
		let h = RSQ_Hands(mo.FindInventory('RSQ_Hands'));
		return h && h.freeFist && mo.player && mo.player.OffhandWeapon == h;
	}

	static bool Shown(PlayerPawn mo)
	{
		return mo && RSQ.PlayerInt(mo, 'rsq_hands', 1) != 0 && RSVR_VRHand.InVR(mo);
	}

	// every tic, from RSQ_Handler.WorldTick: hand the player the off-hand
	// weapon when hands are on and they are playing in VR
	static void Upkeep(PlayerPawn mo)
	{
		let p = mo.player;
		if (!p || p.playerstate != PST_LIVE || mo.health <= 0 || !Shown(mo) && !RSR_ReloadHandler.WantsHands(mo))
			return;
		let h = Weapon(mo.FindInventory('RSQ_Hands'));
		if (!h)
		{
			mo.GiveInventory('RSQ_Hands', 1);
			h = Weapon(mo.FindInventory('RSQ_Hands'));
		}
		// 2026-10-23 (owner: empty gun -> dual -> back to one gun -> no reload ever again).
		// The real reload only runs while the off hand IS these hands (vreload.zs Wanted),
		// and this used to re-arm them only when the slot was EMPTY. A stale dual copy --
		// one whose gun is not the gun in the main hand -- sits in the slot forever, so the
		// slot is neither empty nor RSQ_Hands and reloading dies silently for EVERY gun.
		// A copy that matches the ready weapon is a real dual wield and is left alone.
		let off = p.OffhandWeapon;
		bool stale = off && !(off is 'RSQ_Hands')
			&& RSQ_Dual.CopyIndex(off) != RSQ_Dual.GunIndex(p.ReadyWeapon);
		if (h && (!off || stale) && p.PendingWeapon == WP_NOCHANGE)
			p.PendingWeapon = h;
	}

	action void A_RSQ_Layers()
	{
		let p = player;
		let mo = PlayerPawn(self);
		if (!p || !mo)
			return;
		bool on = Shown(mo);
		let s = RSQ_Handler.StateOf(mo);
		int carry = s ? s.carry : 0;
		// a real reload (rsr/vreload.zs) has the off hand: it says what the free hand shows
		String rsr = RSR_ReloadHandler.FreeHand(mo);
		if (rsr == "")
			rsr = RSP_Handler.FreeHand(mo);	// RSR-PUMP: the pump shotguns' loading and pump (rsr/rsr_pump.zs)
		if (rsr == "")
			rsr = RSB_Handler.FreeHand(mo);	// RSR-BREAK
		if (rsr == "")
			rsr = RSK_M203Handler.FreeHand(mo);	// 1.30 RSR-M203: the rifle's launcher (rsr/rsr_m203.zs)
		if (rsr == "" && mo.CountInv('RSG_RingHand') > 0)
			rsr = "RsgRing";				// the VR grenade's ring, pinched (rsg/grenade.zs)
		int i = on ? RSQ_HandTable.Index(p.ReadyWeapon) : 0;
		// 2026-10-16 (owner): fists are Ermac's, both hands, and the VR grenade sits in his hand
		String own = on ? invoker.OwnHand(p) : "";
		invoker.showOwn = own != "";
		if (own != "")
			i = 0;
		// 1.5: the main fist follows BD22's punch frames (jab, cross, uppercut)
		invoker.fistMeshPrev = invoker.fistMesh;
		invoker.fistMesh = own == "Fist" ? invoker.FistFrame(p) : 0;

		// The off hand holds the front of the gun exactly while the engine
		// steadies the gun with both hands (WF_TWOHANDSTABILIZED: the player
		// brought the off hand to the gun and pressed grip), unless a reload
		// needs it. Going by the engine's own grab keeps the hands and the
		// steadying together: a distance snap of our own fought it, and lost
		// the minigun's handlebar grip.
		// 1.12: never while a reload or the shell feed has the hand (rsr): grabbing a shell with grip
		// near the gun also two-hands it, and that hid the hand and the shell it was holding
		bool hold = i > 0 && (p.WeaponState & WF_TWOHANDSTABILIZED) != 0 && s && s.kind == 0 && carry == 0 && rsr == "";
		// 2026-10-16 (owner): pistols and revolvers. The engine's steadying aims the gun along
		// the line from the gun hand to the off hand, which is right for a forend and wrong for
		// a two-hand pistol grip, where the hands are together. So on a cup-support gun the
		// support hand shows by CLOSENESS instead: bring the off hand to the grip, no grip press,
		// and both hands are on the gun while it aims from the gun hand alone. Pressing grip
		// still steadies as stock. (Support "A" = Ermac's pistol cup.)
		if (!hold && i > 0 && s && s.kind == 0 && carry == 0 && RSQ_HandTable.Support(i) == "A" && rsr == "")
		{
			double gap = RSVR_VRHand.SteadyGap(mo);
			hold = gap < (s.holding ? 18.0 : 13.0);		// in at 13 cm, out at 18 (no flicker)
		}
		if (s)
			s.holding = hold;
		invoker.FollowGun(p, i);

		static const String ammo[] = { "FreeHand", "AmmoB", "AmmoC", "AmmoD", "AmmoE", "AmmoF", "AmmoG", "AmmoH" };
		// 2026-10-16 (owner): the free off hand is a FIST (it punches: rsq/fists.zs), open only
		// while the grenade is out, to take its ring
		bool nade = p.ReadyWeapon && p.ReadyWeapon.GetClassName() == 'HandGrenades';
		String fh = !on || hold ? "Hidden" : rsr != "" ? rsr : carry == 0 && !nade ? "AmmoH" : ammo[clamp(carry, 0, 7)];
		invoker.freeFist = fh == "AmmoH";
		invoker.OffPunch(mo);
		invoker.SetLayer(p, RSQ_Layers.FREEHAND, invoker, fh);

		let gs = RSQ_GunSide(FindInventory('RSQ_GunSide'));
		if (!gs)
		{
			A_GiveInventory('RSQ_GunSide', 1);
			gs = RSQ_GunSide(FindInventory('RSQ_GunSide'));
		}
		if (!gs)
			return;
		String g = hold ? RSQ_HandTable.GunTwo(i) : RSQ_HandTable.GunOne(i);
		// the index finger rests on the trigger, and squeezes it while fire is held
		String tf = RSQ_HandTable.Trigger(i);
		String gl = tf != "" ? ((p.cmd.buttons & BT_ATTACK) ? "Sqz" .. tf : "Trg" .. tf) : "Gun" .. g;
		invoker.SetLayer(p, RSQ_Layers.GUNHAND, gs, own != "" ? own : i > 0 && g != "" ? gl : "Hidden");
		String sp = RSQ_HandTable.Support(i);
		if (i == 18 && p.ReadyWeapon is 'PuristRifle')
			sp = "B";		// 1.30: purist's rifle has no launcher: its handguard grip as before
		else if (i == 18 && RSK_M203Handler.TriggerGrip(mo))
			sp = (p.cmd.buttons & BT_OFFHANDATTACK) ? "M2" : "M1";	// 1.31: finger on the M203's trigger (squeezed)
		invoker.SetLayer(p, RSQ_Layers.SUPPORT, gs, hold && sp != "" ? "Sup" .. sp : "Hidden");

		// 2026-10-23: the VR scope's reticle (rsq/scope.zs). WHETHER the layer is there is this
		// tic's business; WHERE it sits is ModifyBobLayer3D's, per rendered frame. It exists
		// only while the ready weapon has a row in RSQ_ScopeTable, that gun's own mode cvar says
		// DOT, and we are in VR -- out of VR there is nothing to collimate against and no layer.
		// A gun with a scope needs a table row and a cvar and nothing here.
		int sci = RSVR_VRHand.InVR(mo) ? RSQ_ScopeTable.Index(p.ReadyWeapon) : 0;
		if (sci > 0 && RSQ.PlayerInt(mo, RSQ_ScopeTable.ModeCVar(sci), 0) != 0)
			sci = 0;		// REAL mode: the glass is rendered into (rsq/scope_real.zs), no reticle
		// The reticle originally took 2102, which is RSR.WELLMAG (rsr/vreload.zs) -- the
		// magazine at the well, on exactly the two guns that have scopes (RSR_Guns.Index:
		// RailGun 6, Sniper 8). One psprite id holds one caller, so that would have killed
		// reloading on both guns with nothing in the log. DOT is 2112 now and this guard is
		// quiet; it stays as the general safeguard for the next lane that claims an id.
		if (RSQ_Layers.Taken(RSQ_ScopeLayers.RETICLE))
		{
			if (!invoker.dotClash)
			{
				invoker.dotClash = true;
				Console.Printf("RSQ scope: reticle layer %d is already a reload layer; the dot is off until RSQ_ScopeLayers.RETICLE (rsq/scope.zs) moves to a free id (2112-2119, 2124-2129).", RSQ_ScopeLayers.RETICLE);
			}
		}
		else
			invoker.SetLayer(p, RSQ_ScopeLayers.RETICLE, gs, sci > 0 ? "ScopeDot" : "Hidden");
	}

	// "Fist" while the gun layer shows one of BD22's punch / fist sprites (the fists, and a quick
	// punch on any gun); "Nade" while it shows the VR grenade (RQNP: Grenades.dec RSG_ states)
	String OwnHand(PlayerInfo p)
	{
		let g = p.FindPSprite(PSP_WEAPON);
		if (!g || !g.CurState)
			return "";
		if (fistSprites.Size() == 0)
		{
			static const Name fs[] = { '1ONG', '2ONG', '3ONG', '4ONG', '5ONG', 'PONG', '1UNG', '2UNG', '3UNG', '4UNG', '5UNG', 'PUNG',
				'1IST', '3IST', '5IST', 'FIST', '22ST', 'PUNS' };
			for (int k = 0; k < fs.Size(); k++)
				fistSprites.Push(GetSpriteIndex(fs[k]));
			nadeSprite = GetSpriteIndex('RQNP');
			static const Name hs[] = { '1HRG', '2HRG', '3HRG', 'THRG', '1HRW', '2HRW', '3HRW', '5HRW', 'THRW', '1KUP', '2KUP', '3KUP', 'PKUP',
				'1UCK', '2UCK', '3UCK', '4UCK', 'FUCK', 'VUCK', 'SALU', 'GRZ1', 'GRZ2', 'GRZ3', 'GRZ4', 'GRZ5', 'GRZ6', 'GRZ7',
				'PTG1', 'PTG2', 'PTG3', 'THEA', 'IEHW' };
			for (int k = 0; k < hs.Size(); k++)
				bdHandSprites.Push(GetSpriteIndex(hs[k]));
			static const Name on[] = { '1ONG', '2ONG', '3ONG', '4ONG', '5ONG', 'PONG' };
			for (int k = 0; k < on.Size(); k++)
				ongSprites.Push(GetSpriteIndex(on[k]));
			static const Name un[] = { '1UNG', '2UNG', '3UNG', '4UNG', '5UNG', 'PUNG' };
			for (int k = 0; k < un.Size(); k++)
				ungSprites.Push(GetSpriteIndex(un[k]));
			unsSprite = GetSpriteIndex('PUNS');
		}
		int s = g.Sprite;
		if (s == nadeSprite)
			return "Nade";
		if (fistSprites.Find(s) < fistSprites.Size())
			return "Fist";
		// the fists themselves: fists whenever BD22's own hand isn't showing something else
		// (a taunt, a grab, a carried barrel, a pickup, a throw, a fatality)
		let w = p.ReadyWeapon;
		if (w && w.GetClassName() == 'Melee_Attacks' && bdHandSprites.Find(s) >= bdHandSprites.Size())
			return "Fist";
		return "";
	}

	// the BD22 punch frame the main gun layer shows, as a fistclosed.md3 frame (RSQ_FistMoves)
	int FistFrame(PlayerInfo p)
	{
		let g = p.FindPSprite(PSP_WEAPON);
		if (!g || !g.CurState)
			return 0;
		int s = g.Sprite;
		int fam = ongSprites.Find(s) < ongSprites.Size() ? 1 : ungSprites.Find(s) < ungSprites.Size() ? 2 : s == unsSprite ? 3 : 0;
		return RSQ_FistMoves.MeshFrame(fam, g.Frame);
	}

	// 1.5 (owner): the OFF-hand trigger throws BD22's jab from the off fist, with BD's jab motion:
	// PONG B C D, E E E, F, G H (BD22 Melee.dec Jab + FinishJab), the blow landing on D. Only when
	// the off hand is a free fist and the main hand holds no gun (fists, axe, chainsaw, sword):
	// with a gun out, the off trigger is the reload grab and must not punch.
	void OffPunch(PlayerPawn mo)
	{
		static const int seq[] = { 1, 2, 3, 4, 4, 4, 5, 7, 8 };
		let p = mo.player;
		bool trig = (p.cmd.buttons & BT_OFFHANDATTACK) != 0;
		bool press = trig && !offTrigPrev;
		offTrigPrev = trig;
		offMeshPrev = offMesh;
		if (offPunchTic < 0 || offPunchTic >= seq.Size())
		{
			offPunchTic = -1;
			offMesh = 0;
			// 2026-10-23 (owner: "yes -- that way we can punch open switches n shit"): the off
			// trigger now punches with a GUN in the main hand too. It is also the reload's grab,
			// so POSITION decides instead of the weapon: a hand up at the gun is reaching for
			// ammo, a hand out away from it is a punch. freeFist already rules out the support
			// grip and any reload that has the hand.
			if (!press || !freeFist)
				return;
			if (RSVR_VRHand.SteadyGap(mo) < 30.0)	// cm: at the gun, so that press is the reload's
				return;
			offPunchTic = 0;
			mo.A_StartSound("Melee/Swing", CHAN_AUTO, CHANF_OVERLAP);
		}
		offMesh = seq[offPunchTic];
		if (offPunchTic == 2)
		{
			double ps = mo.Level.pixelstretch;
			if (ps <= 0)
				ps = 1.2;
			Vector3 dir = RSVR_VRHand.OffDir(mo, 0, 0, ps);
			Name sn = mo.CountInv('PowerStrength') > 0 ? 'MeleeStrike1Berserked' : 'MeleeStrikeNormal';
			class<Actor> sc = RSQ_Fists.Cls(sn);
			let a = sc ? Actor.Spawn(sc, RSVR_VRHand.OffPos(mo), ALLOW_REPLACE) : null;
			if (a)
			{
				a.target = mo;
				a.angle = VectorAngle(dir.x, dir.y);
				a.pitch = -asin(clamp(dir.z, -1, 1));
				a.vel = dir * 16;
			}
			RSQ_Fists.PunchUse(mo, RSVR_VRHand.OffPos(mo), dir);
		}
		offPunchTic++;
	}

	// a fist's punch move between last tic's frame and this one (BD22's meshes do not blend, but
	// our hands are drawn every display frame, so they glide between tics)
	ui static Vector3, Vector3 FistMove(int prev, int cur, double ticfrac)
	{
		Vector3 t0, m0, t1, m1;
		[t0, m0] = RSQ_FistMoves.Move(prev);
		[t1, m1] = RSQ_FistMoves.Move(cur);
		return t0 + (t1 - t0) * ticfrac, m0 + (m1 - m0) * ticfrac;
	}

	// put a layer on a state only when it changes, so a pose is not
	// restarted every tic
	void SetLayer(PlayerInfo p, int id, Actor caller, String label)
	{
		State want = caller.FindStateByString(label);
		let psp = p.FindPSprite(id);
		if (psp && psp.Caller == caller && psp.CurState == want)
			return;
		p.SetPsprite(id, want, false, caller);
		psp = p.FindPSprite(id);
		if (psp)
		{
			psp.bAddWeapon = false;
			psp.bAddBob = true;
			// a fresh layer has y 0, which tilts a HUD model 8 degrees (hw_weapon.cpp:
			// pitch (y - WEAPONTOP) / -4): every hand layer, the free hand too, sits at WEAPONTOP
			psp.y = WEAPONTOP;
			psp.oldy = WEAPONTOP;
		}
	}

	// Look up how the gun's model frame moves it when the gun layer shows
	// another frame. The gun layer has ticked by now (layers tick in ID order,
	// the off-hand weapon's last), so this is the frame drawn this tic.
	void FollowGun(PlayerInfo p, int i)
	{
		let g = i > 0 ? p.FindPSprite(PSP_WEAPON) : null;
		if (!g || !g.CurState)
		{
			gunState = null;
			gunTurn = gunMove = nextTurn = nextMove = (0, 0, 0);
			return;
		}
		int spr = g.Sprite;
		if (g.CurState == gunState && spr == gunSprite && g.Frame == gunFrame)
			return;
		gunState = g.CurState;
		gunSprite = spr;
		gunFrame = g.Frame;
		Vector3 t, m;
		[t, m] = RSQ_GunMoves.Frame(i, spr, g.Frame);
		gunTurn = nextTurn = t;
		gunMove = nextMove = m;
		// The engine blends a model toward the next state's frame, unless that
		// state keeps the layer's sprite ("####": sprite index 1 or 2), which it
		// cannot look up.
		let n = gunState.NextState;
		if (RSQ_GunMoves.Blends(i) && n && n != gunState && n.sprite > 2)
		{
			[t, m] = RSQ_GunMoves.Frame(i, n.sprite, n.Frame);
			nextTurn = t;
			nextMove = m;
		}
	}

	// a layer's offset as the renderer draws it this frame (hw_weapon.cpp BobWeapon3D)
	ui static Vector2 LayerOffset(PSprite s, double ticfrac)
	{
		if (s.firstTic)
			return (s.x, s.y);
		return (s.oldx + (s.x - s.oldx) * ticfrac, s.oldy + (s.y - s.oldy) * ticfrac);
	}

	// Where the gun-side hands sit for the gun in hand (ui scope, inherited).
	// The incoming translation is the weapon bob every layer gets; the hook is
	// added to it. The free hand keeps Ermac's own placement on its controller.
	override Vector3, Vector3 ModifyBobLayer3D(Vector3 translation, Vector3 rotation, int layer, double ticfrac)
	{
		// 2026-10-23: THE VR SCOPE'S COLLIMATED DOT (rsq/scope.zs). It is placed here, per
		// rendered FRAME, and not from a tic hook, because holding still against the world while
		// the head moves is the entire point of it: a dot sampled at tic rate visibly lags.
		// This case is FIRST because the RSR reload branch below claims a range of layer ids.
		//
		// UNITS. DotAt() answers in the weapon controller's frame, centimetres, (forward, left,
		// up). A ModifyBobLayer3D translation is applied by r_data/models.cpp RenderHUDModel
		// AFTER objectToWorldMatrix.scale(xscale, zscale, yscale) and after the renderer's own
		// 0.01 shrink of the controller frame -- so one unit is one centimetre divided by that
		// layer's own MODELDEF scale, on the model axes (x left, y up, z back):
		//     (x, y, z) = (L / xscale, U / zscale, -F / yscale)
		// The reticle's quad is Scale -1.0 1.0 1.0, the same as the hand meshes, so every
		// divisor is 1 and the conversion is just (L, U, -F). Corroborated by the pack's own
		// rsr/vreload.zs DeskShift, which turns F,L,U cm into exactly
		// (-c.y / scale.x, c.z / scale.z, -c.x / scale.y) -- same mapping, same divisors, and
		// RSR_Guns.WellHook reproduces (L, U, -F) of each gun's magazine axis to three decimals.
		// (the Taken() test is the same stand-down as in A_RSQ_Layers: while the id belongs to
		// another lane this case must not shadow that lane's branch below)
		if (layer == RSQ_ScopeLayers.RETICLE && !RSQ_Layers.Taken(RSQ_ScopeLayers.RETICLE))
		{
			let mo = PlayerPawn(Owner);
			let so = mo ? mo.player : null;
			int si = so ? RSQ_ScopeTable.Index(so.ReadyWeapon) : 0;
			if (si <= 0)
				return translation, rotation;
			Vector3 d;
			bool ok;
			[d, ok] = RSQ_Scope.DotAt(mo, si);
			// No sight picture (the eye is off the glass, or behind the objective end). The
			// layer's STATE is the honest way to hide it, but a state is play data and this hook
			// is ui and returns a translation and nothing else, so the quad is thrown far enough
			// away to clip instead -- ten kilometres behind the controller, which in practice is
			// behind the near plane. A_RSQ_Layers above does the tic-rate hiding it can.
			if (!ok)
				return translation + (0, 0, DOT_FARAWAY), rotation;
			return translation + (d.y, d.z, -d.x), rotation;
		}
		// RSR-BREAK: the break-open / revolver reload's layers (rsr/rsr_break.zs)
		if (RSB_Handler.Owns(Owner, layer))
		{
			Vector3 bt, br;
			[bt, br] = RSB_Handler.Place(Owner, translation, rotation, layer, ticfrac);
			return bt, br;
		}
		// 1.30 RSR-M203: the rifle launcher's tube and round (rsr/rsr_m203.zs)
		if (RSK_M203Handler.Places(Owner, layer))
		{
			Vector3 mt, mr;
			[mt, mr] = RSK_M203Handler.Place(Owner, translation, rotation, layer, ticfrac);
			return mt, mr;
		}
		// RSR-PUMP: the pump shotguns' layers (rsr/rsr_pump.zs)
		if (RSP_Handler.Places(Owner, layer))
		{
			Vector3 pt, pr;
			[pt, pr] = RSP_Handler.Place(Owner, translation, rotation, layer, ticfrac);
			return pt, pr;
		}
		// the real reload's layers (rsr/vreload.zs)
		if (layer >= RSR.LAYER_FIRST && layer <= RSR.LAYER_LAST || layer == RSR.HANDMAG || layer == RSQ_Layers.FREEHAND)
		{
			Vector3 t, r;
			[t, r] = RSR_ReloadHandler.Place(Owner, translation, rotation, layer, ticfrac);
			if (layer != RSQ_Layers.FREEHAND)
				return t, r;
			translation = t;
			rotation = r;
			if (offMesh > 0 || offMeshPrev > 0)	// 1.5: the off-hand trigger punch
			{
				Vector3 ft, fm;
				[ft, fm] = FistMove(offMeshPrev, offMesh, ticfrac);
				return translation + fm, rotation + ft;
			}
		}
		if (layer == RSQ_Layers.GUNHAND && showOwn && (fistMesh > 0 || fistMeshPrev > 0))
		{
			Vector3 ft, fm;
			[ft, fm] = FistMove(fistMeshPrev, fistMesh, ticfrac);
			return translation + fm, rotation + ft;
		}
		if (layer != RSQ_Layers.GUNHAND && layer != RSQ_Layers.SUPPORT || showOwn)
			return translation, rotation;
		let o = Owner ? Owner.player : null;
		int i = o ? RSQ_HandTable.Index(o.ReadyWeapon) : 0;
		if (i <= 0)
			return translation, rotation;
		bool gunHand = layer == RSQ_Layers.GUNHAND;
		// 2026-10-23: a weapon may be gripped somewhere else in two hands. GunHookTwo
		// defaults to GunHook for every gun, so only the axe moves.
		bool two = Owner && Owner.CountInv('RSVR_AxeTwo') > 0;
		Vector3 hook = gunHand ? (two ? RSQ_HandTable.GunHookTwo(i) : RSQ_HandTable.GunHook(i))
			: RSQ_HandTable.SupportHook(i);
		Vector3 hookTurn = gunHand ? (two ? RSQ_HandTable.GunRotTwo(i) : RSQ_HandTable.GunRot(i))
			: RSQ_HandTable.SupportRot(i);
		if (!gunHand && i == 18 && !(o.ReadyWeapon is 'PuristRifle') && RSK_M203Handler.TriggerGrip(Owner))
		{
			hook = (0, 0, 0);		// 1.31: the trigger grip is baked in place (MODELDEF.rsm RQ2S)
			hookTurn = (0, 0, 0);
		}
		if (!gunHand && i == 18 && o.ReadyWeapon is 'PuristRifle')
		{
			hook = (-0.090, -1.390, 11.380);	// 1.30: purist's rifle (no launcher): the handguard grip as before
			hookTurn = (0, 0, 0);
		}

		// The renderer turns every HUD model by its own layer's offset: yaw x / 4,
		// pitch (y - WEAPONTOP) / -4 (hw_weapon.cpp, RenderHUDModel's call). The gun
		// layer is at y = 32 when ready and moves when it is raised, lowered or
		// kicked by Offset; ours stay at 0, which on its own tipped the hands 8
		// degrees up off the gun (the support hand into the shotguns' barrels). So
		// the hands take the gun layer's turn instead of their own, about the point
		// the gun model turns on. A gun model mirrored against the hands turns the
		// other way sideways.
		PSprite gp, hp;
		for (let s = o.psprites; s; s = s.Next)
		{
			if (s.ID == PSP_WEAPON)
				gp = s;
			else if (s.ID == layer)
				hp = s;
		}
		Vector2 g = gp ? LayerOffset(gp, ticfrac) : (0, WEAPONTOP);
		Vector2 h = hp ? LayerOffset(hp, ticfrac) : (0, 0);
		Vector3 gunTurnNow = (g.x / 4, (g.y - WEAPONTOP) / -4, 0);
		if (RSQ_GunMoves.Mirrored(i))
			gunTurnNow.x = -gunTurnNow.x;

		// The gun's model frame (the recoil is in the meshes), blended toward the
		// next state's frame the way the engine blends the model
		// (models.cpp CalcModelFrame).
		Vector3 frameTurn = gunTurn;
		Vector3 frameMove = gunMove;
		if (gp && gunState && gp.CurState == gunState && gunState.Tics > 0 && gp.Tics <= gunState.Tics)
		{
			double inter = (gunState.Tics - gp.Tics + ticfrac) / gunState.Tics;
			frameTurn += (nextTurn - gunTurn) * inter;
			frameMove += (nextMove - gunMove) * inter;
		}

		if (!gunHand)
		{
			frameMove += RSP_Handler.SupportShift(Owner, ticfrac);	// RSR-PUMP: the support hand rides the pump
			frameMove += RSK_M203Handler.SupportShift(Owner, ticfrac);	// 1.30 RSR-M203: ...and the launcher's tube
		}
		Vector3 t, r;
		[t, r] = RSQ_Turn.Place(hook, hookTurn, gunTurnNow, frameTurn, frameMove, RSQ_GunMoves.Pivot(i));
		// the renderer still adds this layer's own turn on top: take it back out
		return translation + t, rotation + r - (h.x / 4, (h.y - WEAPONTOP) / -4, 0);
	}

	States
	{
	Ready:
		TNT1 A 1
		{
			A_RSQ_Layers();
			A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
		}
		Loop;
	Deselect:
		TNT1 A 1 A_Lower(64);
		Loop;
	Select:
		TNT1 A 1 A_Raise(64);
		Loop;
	Fire:
		TNT1 A 1;
		Goto Ready;

	// the free hand (MODELDEF.rsq): open, or a fist
	FreeHand: RQHN A -1; Stop;
	AmmoH: RQHN H -1; Stop;		// a closed hand
	RspShell: RQUN A -1; Stop;	// RSR-PUMP: Ermac's one-shell hold (ammo_hand frame 1), round the gun's own shell
	RsrHold: RQHN I -1; Stop;	// real reload: Ermac's hold, round the gun's own magazine (rsr)
	RsbShell: RQHN J -1; Stop;	// RSR-BREAK: Ermac's hold of one shell (ammo_hand 1), round the gun's own round
	RsbCell: RQHN L -1; Stop;	// RSR-BREAK: Ermac's hold of a cell (ammo_hand 5), round the gun's own speedloader
	RsgRing: RQHR A -1; Stop;
	RsmRound: RQ2H A -1; Stop;	// 1.30 RSR-M203: Ermac's open grip (ammo_hand 3) round a 40 mm round
	RsmGrip: RQ2H B -1; Stop;	// ...the same grip, the round on the gun
	// dual wield (rsq/dualhands.zs): the gun hand as a layer CALLED BY A GUN must use weapon
	// states (an inventory item's states are refused for a weapon caller), so they live here
	DTrgA: RQGT A -1; Stop;
	DSqzA: RQGU A -1; Stop;
	DTrgB: RQGT B -1; Stop;
	DSqzB: RQGU B -1; Stop;
	DTrgC: RQGT C -1; Stop;
	DSqzC: RQGU C -1; Stop;
	DTrgD: RQGT D -1; Stop;
	DSqzD: RQGU D -1; Stop;
	DTrgE: RQGT E -1; Stop;
	DSqzE: RQGU E -1; Stop;
	DTrgF: RQGT F -1; Stop;
	DSqzF: RQGU F -1; Stop;
	DTrgG: RQGT G -1; Stop;
	DSqzG: RQGU G -1; Stop;
	DTrgH: RQGT H -1; Stop;
	DSqzH: RQGU H -1; Stop;
	DTrgI: RQGT I -1; Stop;
	DSqzI: RQGU I -1; Stop;
	DTrgJ: RQGT J -1; Stop;
	DSqzJ: RQGU J -1; Stop;
	DTrgK: RQGT K -1; Stop;
	DSqzK: RQGU K -1; Stop;
	DTrgL: RQGT L -1; Stop;
	DSqzL: RQGU L -1; Stop;
	DTrgM: RQGT M -1; Stop;
	DSqzM: RQGU M -1; Stop;
	DTrgN: RQGT N -1; Stop;
	DSqzN: RQGU N -1; Stop;
	DTrgO: RQGT O -1; Stop;
	DSqzO: RQGU O -1; Stop;
	DTrgP: RQGT P -1; Stop;
	DSqzP: RQGU P -1; Stop;
	DTrgQ: RQGT Q -1; Stop;
	DSqzQ: RQGU Q -1; Stop;
	DFist: RQGF A -1; Stop;	// dual wield: the fists in the main hand
	DNade: RQGN A -1; Stop;	// dual wield: the VR grenade in the main hand
	DGunA: RQGS A -1; Stop;
	DGunB: RQGS B -1; Stop;
	DGunC: RQGS C -1; Stop;
	DGunD: RQGS D -1; Stop;
	DGunE: RQGS E -1; Stop;
	DGunF: RQGS F -1; Stop;
	DGunG: RQGS G -1; Stop;
	DGunH: RQGS H -1; Stop;	// VR grenade: Ermac's one-shell pinch (ammo_hand 1) holding the ring
	Hidden: TNT1 A -1; Stop;
	}
}

// Turns the way ModifyBobLayer3D gives them: models.cpp RenderHUDModel turns
// yaw about y, then pitch about x, then roll about z (degrees), in the hand
// models' frame before the MODELDEF scale (x left, y up, z back). A turn is
// kept as the three rows of its matrix.
class RSQ_Turn abstract
{
	clearscope static Vector3, Vector3, Vector3 Rows(Vector3 a)
	{
		double cx = cos(a.x), sx = sin(a.x);
		double cy = cos(a.y), sy = sin(a.y);
		double cz = cos(a.z), sz = sin(a.z);
		return (cx * cz + sx * sy * sz, -cx * sz + sx * sy * cz, sx * cy),
			(cy * sz, cy * cz, -sy),
			(-sx * cz + cx * sy * sz, sx * sz + cx * sy * cz, cx * cy);
	}

	clearscope static Vector3 Angles(Vector3 r0, Vector3 r1, Vector3 r2)
	{
		return (atan2(r0.z, r2.z), asin(clamp(-r1.z, -1., 1.)), atan2(r1.x, r1.y));
	}

	// the rows of a * b
	clearscope static Vector3, Vector3, Vector3 Mul(Vector3 a0, Vector3 a1, Vector3 a2, Vector3 b0, Vector3 b1, Vector3 b2)
	{
		Vector3 c0 = (b0.x, b1.x, b2.x);
		Vector3 c1 = (b0.y, b1.y, b2.y);
		Vector3 c2 = (b0.z, b1.z, b2.z);
		return (a0 dot c0, a0 dot c1, a0 dot c2), (a1 dot c0, a1 dot c1, a1 dot c2), (a2 dot c0, a2 dot c1, a2 dot c2);
	}

	// v turned back (by the transpose)
	clearscope static Vector3 Back(Vector3 r0, Vector3 r1, Vector3 r2, Vector3 v)
	{
		return r0 * v.x + r1 * v.y + r2 * v.z;
	}

	// Where a gun-side hand goes, and how it turns, so that it stays where it
	// holds the gun. hook / hookTurn: its place on the gun at rest (the hand
	// table). gunTurn: the gun layer's turn, about pivot (the gun model's turning
	// point from the hands'). frameTurn / frameMove: how the gun's model frame
	// has moved it off its ready frame. rsq_gunmoves_gen.py checks this against
	// RenderHUDModel's chain.
	clearscope static Vector3, Vector3 Place(Vector3 hook, Vector3 hookTurn, Vector3 gunTurn, Vector3 frameTurn, Vector3 frameMove, Vector3 pivot)
	{
		Vector3 q0, q1, q2, k0, k1, k2, h0, h1, h2, a0, a1, a2, e0, e1, e2;
		[q0, q1, q2] = Rows(gunTurn);
		[k0, k1, k2] = Rows(frameTurn);
		[h0, h1, h2] = Rows(hookTurn);
		[a0, a1, a2] = Mul(q0, q1, q2, k0, k1, k2);
		[e0, e1, e2] = Mul(a0, a1, a2, h0, h1, h2);
		Vector3 v = frameMove + Back(k0, k1, k2, Back(q0, q1, q2, pivot) - pivot);
		return hook + Back(h0, h1, h2, v), Angles(e0, e1, e2);
	}
}
