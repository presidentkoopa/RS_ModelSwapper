// RS VR melee for Brutal Doom v22 on QuestZDoom 17.3 (stock engine).
//
// Axe (BrutalAxe) and Dragonslayer (DSweap): swing the controller and the blade
// hits whatever it passes through. The hit is BD22's own attack actor (AxeAttack,
// AxeAttackNoDecal, DSAttack, DSAttack2) started at the point and height where
// the blade met the body, so BD22's gore rules decide the result: its blood
// actors mark a head or leg hit from the impact height, and the Saw / Cut deaths
// take heads, legs, arms or cut the body in half from there.
//
// Axe throw (VR throwing on): hold the TRIGGER, swing, let go -- like the grenade. Alt-fire
// does the same. Either way: BD22's thrown axe (ThrowedAxe, or
// ThrowedAxeStrong with berserk) leaves the hand with the hand's speed.
//
// Two hands on the haft (the engine's own steadying) and the edge leading the swing
// add a half-strength bite, about 1.5x; a two-handed axe cannot be thrown.
//
// The trigger keeps BD22's own chop. Outside VR nothing here does anything and
// the axe's alt-fire is BD22's sideways swing.

class RSVR_MeleeHandler : EventHandler
{
	RSVR_Hand hands[MAXPLAYERS];

	// rsvr_axe_keys: the weapon hand's grip arrives as a KEY, not a usercmd button, so its codes
	// become a synchronised event the same way rsr_grip_keys does in vreload.zs. Every machine
	// sees the same down and up, so readying a throw is never a local-only decision.
	bool keyDown[MAXPLAYERS];
	ui Array<int> axeKeys;
	ui String axeKeysFrom;
	ui bool keyIsDown;

	static bool KeyHeld(PlayerPawn mo)
	{
		let h = RSVR_MeleeHandler(EventHandler.Find('RSVR_MeleeHandler'));
		if (!h || !mo || !mo.player)
			return false;
		int n = mo.PlayerNumber();
		return n >= 0 && n < MAXPLAYERS && h.keyDown[n];
	}

	bool offGrip[MAXPLAYERS];	// F11: the off grip (rsr_grip events, sent by vreload.zs InputProcess)
	override void NetworkProcess(ConsoleEvent e)
	{
		if (e.Name == "rsr_grip" && e.Player >= 0 && e.Player < MAXPLAYERS)
			offGrip[e.Player] = e.Args[0] != 0;
		if (e.Name != "rsvr_axe_grip")
			return;
		int n = e.Player;
		if (n >= 0 && n < MAXPLAYERS && playeringame[n])
			keyDown[n] = e.Args[0] != 0;
	}

	override bool InputProcess(InputEvent e)
	{
		if (e.Type != InputEvent.Type_KeyDown && e.Type != InputEvent.Type_KeyUp)
			return false;
		let me = players[consoleplayer];
		let cv = CVar.GetCVar('rsvr_axe_keys', me);
		String keys = cv ? cv.GetString() : "";
		if (keys != axeKeysFrom)
		{
			axeKeysFrom = keys;
			axeKeys.Clear();
			Array<String> w;
			keys.Split(w, " ", TOK_SKIPEMPTY);
			for (int j = 0; j < w.Size(); j++)
				axeKeys.Push(w[j].ToInt());
		}
		if (axeKeys.Size() == 0 || axeKeys.Find(e.KeyScan) == axeKeys.Size())
			return false;
		bool down = e.Type == InputEvent.Type_KeyDown;
		if (down == keyIsDown)
			return false;			// key repeat: only the edges are worth a net event
		keyIsDown = down;
		EventHandler.SendNetworkEvent("rsvr_axe_grip", down ? 1 : 0, e.KeyScan);
		return false;				// never eaten: the grip keeps whatever else it does
	}

	// 2026-10-23 (owner): a new map starts clean, as the reload handlers now do. The hand
	// keeps the blade's last position in the BODY's frame, and the first tic of a new map
	// would otherwise difference it against where the blade was in the old one -- a large
	// bogus velocity, which is a phantom swing on spawn. The teleport guard in Tick catches
	// most of that (a jump over 64 units, or a yaw change over 12 degrees) but neither is
	// guaranteed across an exit. The lock-on goes too: its target and ring were actors of
	// the old level.
	override void WorldLoaded(WorldEvent e)
	{
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			keyDown[n] = false;	// a grip held through the exit is not a throw readied here
			if (!hands[n])
				continue;
			hands[n].Reset();
			hands[n].Unlock();
			hands[n].kind = 0;	// so the next Tick re-reads the weapon rather than trusting it
		}
	}

	override void WorldTick()
	{
		for (int i = 0; i < MAXPLAYERS; i++)
		{
			if (!playeringame[i] || !players[i].mo)
				continue;
			if (!hands[i])
				hands[i] = new('RSVR_Hand');
			let mo = players[i].mo;
			hands[i].Tick(mo);
			// RSVR_AxeHold lets the axe's Ready state enter its hold loop from the grip. The
			// hold used to be reachable only from alt-fire, so no other button could ever ready
			// a throw however the cvars were set (owner, 2026-10-13: throwing should be hold and
			// release the grip). Only in VR: out of VR the axe keeps BD22's own sideways swing.
			bool want = RSVR_VRHand.InVR(mo) && RSVR_Hand.HoldDown(mo)
				&& mo.player.ReadyWeapon && RSVR_Hand.KindOf(mo) == RSVR_Hand.AXE;
			mo.SetInventory('RSVR_AxeHold', want ? 1 : 0);
			// VR throwing on (rsg_vr): the axe's trigger throws it the grenade's way (Axe.dec Fire)
			bool trigThrow = RSVR_VRHand.InVR(mo) && RSR.PlayerInt(mo.player, 'rsg_vr', 1) != 0
				&& mo.player.ReadyWeapon && RSVR_Hand.KindOf(mo) == RSVR_Hand.AXE;
			mo.SetInventory('RSVR_AxeVRThrow', trigThrow ? 1 : 0);
			// both hands on the haft: Axe.dec swaps to the shifted placement
			// F11: the axe and the sword go two-handed on the off grip held near them (the engine's
			// own steadying is off for them, RSVR_TwoHandSwitch), never by the engine re-aiming them
			int mk = mo.player.ReadyWeapon ? RSVR_Hand.KindOf(mo) : 0;
			bool meleeTwo = RSVR_VRHand.InVR(mo) && (mk == RSVR_Hand.AXE || mk == RSVR_Hand.SWORD)
				&& offGrip[i] && RSVR_VRHand.SteadyGap(mo) < 50.0;
			mo.SetInventory('RSVR_MeleeTwo', meleeTwo ? 1 : 0);
			bool twoUp = RSVR_VRHand.InVR(mo) && mo.player.ReadyWeapon
				&& RSVR_Hand.KindOf(mo) == RSVR_Hand.AXE && RSVR_VRHand.TwoHands(mo);
			mo.SetInventory('RSVR_AxeTwo', twoUp ? 1 : 0);
		}
	}

	static RSVR_Hand HandOf(PlayerPawn mo)
	{
		let h = RSVR_MeleeHandler(EventHandler.Find('RSVR_MeleeHandler'));
		if (!h || !mo || !mo.player)
			return null;
		int n = mo.PlayerNumber();
		if (n < 0 || n >= MAXPLAYERS)
			return null;
		if (!h.hands[n])
			h.hands[n] = new('RSVR_Hand');
		return h.hands[n];
	}
}

class RSVR_Hand play
{
	const HIST = 6;
	const AXE = 1;
	const SWORD = 2;
	const PISTOL = 3;		// 1.97: the pistol whip
	const REVOLVER = 4;
	const RIFLEBUTT = 5;
	const SGBUTT = 6;
	const SSGBUTT = 7;
	const ASGBUTT = 8;
	const MP40BUTT = 9;
	const SMGBUTT = 10;
	const MGBUTT = 11;
	const MG42BUTT = 12;

	// swing speed (m/s at the blade's outer point, relative to the player's own
	// movement) that counts as a blow, and the slowest release that throws
	const AXE_SWING = 3.0;
	const SWORD_SWING = 3.5;
	const WHIP_SWING = 3.2;		// 1.97: a pistol is lighter than the axe
	const BUTT_SWING = 3.6;		// 1.97: a long gun is heavy and swung short
	const THROW_MIN = 2.5;
	const RISE = 0.15;			// of the blade's speed that may be upward before it is a backswing (about 9 degrees)

	// rsvr_melee_swing scales how hard you have to swing; rsvr_melee_up is how much of the
	// motion may point UP before it counts as raising the axe rather than striking with it.
	// Both are user cvars (CVARINFO.rsvr), read per player so a netgame cannot disagree.
	clearscope static double Cv(PlayerPawn mo, Name n, double def)
	{
		let cv = mo && mo.player ? CVar.GetCVar(n, mo.player) : CVar.FindCVar(n);
		return cv ? cv.GetFloat() : def;
	}

	clearscope static int CvI(PlayerPawn mo, Name n, int def)
	{
		let cv = mo && mo.player ? CVar.GetCVar(n, mo.player) : CVar.FindCVar(n);
		return cv ? cv.GetInt() : def;
	}

	// Is the throw's hold input down? QuestZDoom has no usercmd bit for the WEAPON hand's grip,
	// so this takes either a button mask (rsvr_axe_hold, default BT_ALTATTACK, how it has always
	// worked) or raw key codes (rsvr_axe_keys), read the way vreload.zs reads rsr_grip_keys.
	static bool HoldDown(PlayerPawn mo)
	{
		if (!mo || !mo.player)
			return false;
		int mask = CvI(mo, 'rsvr_axe_hold', BT_ALTATTACK);
		if (mask == BT_TURN180)	// F11: the old default, still archived in players' inis -- it meant alt fire
			mask = BT_ALTATTACK;
		if (mask != 0 && (mo.player.cmd.buttons & mask) != 0)
			return true;
		return RSVR_MeleeHandler.KeyHeld(mo);
	}

	// recent samples: blade outer point and player position, newest at [head]
	double tx[HIST];
	double ty[HIST];
	double tz[HIST];
	double px[HIST];
	double py[HIST];
	double pz[HIST];
	int count;
	int head;

	int kind;
	bool havePrev;
	Vector3 prevIn;
	Vector3 prevOut;
	Vector3 prevPos;
	Vector3 prevRel;		// 1.11: the blade tip in the BODY's frame last tic (forward, left, up)
	Vector3 prevRelIn;		// 1.97: and the inner end, so a butt strike can be asked to lead
	int prevStamp;		// 1.97 F7: the stamp of the sample prevRel was taken from
	Actor lockTarget;	// the monster painted while a throw is readied
	Actor lockRing;
	int lockKeep;		// F11: a release that was not a throw keeps the paint until this tic
	int poseFrame;		// 0 = one hand, 1 = the two-handed placement
	int swingTics;
	int calmTics;
	int whooshWait;
	int scrapeWait;
	bool inWall;
	Array<Actor> struck;

	// this tic's hand frame and view settings
	transient Vector3 fH;
	transient Vector3 pBod;		// 1.97 F7: the body pose recorded WITH this hand sample
	transient double pByaw;
	transient int pStamp;
	transient Vector3 fF;
	transient Vector3 fR;
	transient Vector3 fU;
	transient double vu;
	transient double ws;
	transient double ox;
	transient double oy;
	transient double oz;
	transient double ps;

	transient bool spritesSet;
	transient SpriteID sAXEG;
	transient SpriteID sRIFG;
	transient SpriteID s2IFG;
	transient SpriteID sRI2G;
	transient SpriteID sSHTN;
	transient SpriteID s2HTN;
	transient SpriteID sSHTA;
	transient SpriteID sVSSG;
	transient SpriteID sSHT2;
	transient SpriteID sVSHZ;
	transient SpriteID sUSAS;
	transient SpriteID s2SAS;
	transient SpriteID sA12P;
	transient SpriteID sMP40;
	transient SpriteID sMP42;
	transient SpriteID sPP40;
	transient SpriteID sSMGF;
	transient SpriteID sSMGR;
	transient SpriteID sVSMG;
	transient SpriteID sMGN1;
	transient SpriteID sHBUS;
	transient SpriteID sPBUS;
	transient SpriteID sPIST;
	transient SpriteID s2IST;
	transient SpriteID sREVO;
	transient SpriteID s2EVO;
	transient SpriteID sAXE2;
	transient SpriteID s1XEG;
	transient SpriteID s2XEG;
	transient SpriteID s3XEG;
	transient SpriteID s4XEG;
	transient SpriteID s5XEG;
	transient SpriteID sDSLA;

	//------------------------------------------------------------------
	// the blade, in the held model's own units (BrutalAxe.md3 frame 5 = AXEG A,
	// DSweap.md3 frame 0 = DSLA A; posefix/melee measurements)
	static Vector3 BladeIn(int k)
	{
		if (k == AXE)
			return (44, 0, 26);		// top of the axe head
		if (k == RIFLEBUTT)
			return (25.1, 0.1, 6.3);	// 1.97: Rifle.md3 frame 3, toward the muzzle
		if (k == SGBUTT)
			return (23.7, 0.0, -5.4);	// 1.97: ShotGun.md3 frame 4, toward the muzzle
		if (k == SSGBUTT)
			return (27.9, 0.1, -2.8);	// 1.97: SSG.md3 frame 1, toward the muzzle
		if (k == ASGBUTT)
			return (20.0, 0.0, -2.6);	// 1.97: AssaultShotgun.md3 frame 4, toward the muzzle
		if (k == MP40BUTT)
			return (24.8, 0.2, -3.1);	// 1.97: MP40.md3 frame 2, toward the muzzle
		if (k == SMGBUTT)
			return (18.6, -0.3, -1.2);	// 1.97: BrutalSMG.md3 frame 3, toward the muzzle
		if (k == MGBUTT)
			return (20.1, 0.0, 4.3);	// 1.97: Machinegun.md3 frame 4, surface M249_lowpoly, toward the muzzle
		if (k == MG42BUTT)
			return (21.6, -1.0, 1.2);	// 1.97: HitlersBuzzsaw.md3 frame 0, toward the muzzle
		if (k == PISTOL)
			return (26.2, 0.0, -7.0);	// 1.97: BrutalPistol.md3 frame 3, just forward of the hand
		if (k == REVOLVER)
			return (29.4, 0.1, -1.5);	// 1.97: Revolver.md3 frame 0, just forward of the hand
		return (38, 0, 16);			// Dragonslayer: guard
	}

	static Vector3 BladeOut(int k)
	{
		if (k == AXE)
			return (55, 0, 16);		// the axe's cutting edge
		if (k == RIFLEBUTT)
			return (2.5, 0.5, -1.0);	// 1.97: Rifle.md3 frame 3, the butt
		if (k == SGBUTT)
			return (0.9, 0.0, -10.7);	// 1.97: ShotGun.md3 frame 4, the butt
		if (k == SSGBUTT)
			return (15.3, 0.1, -7.0);	// 1.97: SSG.md3 frame 1, the butt
		if (k == ASGBUTT)
			return (-1.7, 0.0, -6.0);	// 1.97: AssaultShotgun.md3 frame 4, the butt
		if (k == MP40BUTT)
			return (-1.2, 0.0, -3.5);	// 1.97: MP40.md3 frame 2, the butt
		if (k == SMGBUTT)
			return (0.6, 0.0, -10.4);	// 1.97: BrutalSMG.md3 frame 3, the butt
		if (k == MGBUTT)
			return (-1.4, 0.0, 2.0);	// 1.97: Machinegun.md3 frame 4, surface M249_lowpoly, the butt
		if (k == MG42BUTT)
			return (-10.8, -0.1, 1.6);	// 1.97: HitlersBuzzsaw.md3 frame 0, the butt
		if (k == PISTOL)
			return (44.2, 0.0, -0.2);	// 1.97: BrutalPistol.md3 frame 3, the muzzle
		if (k == REVOLVER)
			return (50.2, 0.0, 2.4);	// 1.97: Revolver.md3 frame 0, the muzzle
		return (90, 0, 159);		// Dragonslayer: point
	}

	static Vector3 AxeHead()
	{
		return (50, 0, 20);
	}

	//------------------------------------------------------------------
	void InitSprites()
	{
		sAXEG = Actor.GetSpriteIndex('AXEG');
		sRIFG = Actor.GetSpriteIndex('RIFG');
		s2IFG = Actor.GetSpriteIndex('2IFG');
		sRI2G = Actor.GetSpriteIndex('RI2G');
		sSHTN = Actor.GetSpriteIndex('SHTN');
		s2HTN = Actor.GetSpriteIndex('2HTN');
		sSHTA = Actor.GetSpriteIndex('SHTA');
		sVSSG = Actor.GetSpriteIndex('VSSG');
		sSHT2 = Actor.GetSpriteIndex('SHT2');
		sVSHZ = Actor.GetSpriteIndex('VSHZ');
		sUSAS = Actor.GetSpriteIndex('USAS');
		s2SAS = Actor.GetSpriteIndex('2SAS');
		sA12P = Actor.GetSpriteIndex('A12P');
		sMP40 = Actor.GetSpriteIndex('MP40');
		sMP42 = Actor.GetSpriteIndex('MP42');
		sPP40 = Actor.GetSpriteIndex('PP40');
		sSMGF = Actor.GetSpriteIndex('SMGF');
		sSMGR = Actor.GetSpriteIndex('SMGR');
		sVSMG = Actor.GetSpriteIndex('VSMG');
		sMGN1 = Actor.GetSpriteIndex('MGN1');
		sHBUS = Actor.GetSpriteIndex('HBUS');
		sPBUS = Actor.GetSpriteIndex('PBUS');
		sPIST = Actor.GetSpriteIndex('PIST');
		s2IST = Actor.GetSpriteIndex('2IST');
		sREVO = Actor.GetSpriteIndex('REVO');
		s2EVO = Actor.GetSpriteIndex('2EVO');
		sAXE2 = Actor.GetSpriteIndex('AXE2');	// the two-handed placement
		s1XEG = Actor.GetSpriteIndex('1XEG');
		s2XEG = Actor.GetSpriteIndex('2XEG');
		s3XEG = Actor.GetSpriteIndex('3XEG');
		s4XEG = Actor.GetSpriteIndex('4XEG');
		s5XEG = Actor.GetSpriteIndex('5XEG');
		sDSLA = Actor.GetSpriteIndex('DSLA');
		spritesSet = true;
	}

	static int KindOf(PlayerPawn mo)
	{
		let p = mo.player;
		if (!p || !p.ReadyWeapon || p.PendingWeapon != WP_NOCHANGE || mo.health <= 0)
			return 0;
		Name n = p.ReadyWeapon.GetClassName();
		if (n == 'BrutalAxe')
			return AXE;
		if (n == 'DSweap')
			return SWORD;
		if (RSQ.PlayerInt(mo, 'rsq_butt', 0) != 0)
		{
			if (n == 'Rifle')
				return RIFLEBUTT;
			if (n == 'Shot_Gun')
				return SGBUTT;
			if (n == 'SSG')
				return SSGBUTT;
			if (n == 'AssaultShotgun')
				return ASGBUTT;
			if (n == 'MP40')
				return MP40BUTT;
			if (n == 'BrutalSMG')
				return SMGBUTT;
			if (n == 'Machinegun')
				return MGBUTT;
			if (n == 'MG42')
				return MG42BUTT;
		}
		if (n == 'BrutalPistol')
			return PISTOL;
		if (n == 'Revolver' || n == 'Revolver2')
			return REVOLVER;
		return 0;
	}

	// the weapon is in its held pose (AXEG A or a blood-colour copy, DSLA A):
	// the blade is where the model shows it
	bool ReadyPose(PlayerPawn mo, int k)
	{
		if (!spritesSet)
			InitSprites();
		let psp = mo.player.FindPSprite(PSP_WEAPON);
		if (!psp || psp.Frame != 0)
			return false;
		SpriteID s = psp.Sprite;
		if (k == SWORD)
			return s == sDSLA;
		if (k == RIFLEBUTT)
			return s == sRIFG || s == s2IFG || s == sRI2G;
		if (k == SGBUTT)
			return s == sSHTN || s == s2HTN || s == sSHTA;
		if (k == SSGBUTT)
			return s == sVSSG || s == sSHT2 || s == sVSHZ;
		if (k == ASGBUTT)
			return s == sUSAS || s == s2SAS || s == sA12P;
		if (k == MP40BUTT)
			return s == sMP40 || s == sMP42 || s == sPP40;
		if (k == SMGBUTT)
			return s == sSMGF || s == sSMGR || s == sVSMG;
		if (k == MGBUTT)
			return s == sMGN1;
		if (k == MG42BUTT)
			return s == sHBUS || s == sPBUS;
		if (k == PISTOL)
			return s == sPIST || s == s2IST;
		if (k == REVOLVER)
			return s == sREVO || s == s2EVO;
		// AXE2 is the same axe drawn at the TWO-HANDED placement (MODELDEF, Axe.dec
		// TwoHand). poseFrame tells Place which transform the blade sits in.
		poseFrame = s == sAXE2 ? 1 : 0;
		return s == sAXEG || s == sAXE2 || s == s1XEG || s == s2XEG || s == s3XEG || s == s4XEG || s == s5XEG;
	}

	static double CVarF(Name n, double def)
	{
		let cv = CVar.FindCVar(n);
		return cv ? cv.GetFloat() : def;
	}

	// 1.97 F7: THE HAND COMES OUT OF THE POSE HISTORY, not out of the engine fields.
	// RSVR_VRHand.HandPos reads AttackPos, which stock QuestZDoom writes on the CONSOLE
	// PLAYER'S PAWN ONLY and never sends: for every other player it is zero, so a second
	// player's melee resolved from nothing. RSQ_PoseHandler fills a stamped history on every
	// machine from one netevent a tic, and this reads that -- on the sender's machine too, so
	// there is one code path and no special case for the player holding the controller.
	//
	// `bod` and `byaw` are the body pose recorded WITH this hand sample. That is the whole
	// reason the snap-turn patch could be deleted: the controller pose is written by the
	// renderer at the end of a frame and the pawn's angle changes in the tic after, so
	// converting an old hand reading with a new body angle invented a swing out of a turn.
	// Matching each sample to its own body pose removes that at the source.
	bool Frame(PlayerPawn mo)
	{
		let ph = RSQ_PoseHandler.Of(mo, RSQ_Pose.MAIN);
		if (!ph || !ph.Fresh(mo.Level.maptime))
			return false;
		ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		fH = ph.pos[0];
		fF = ph.F;
		fR = -ph.L;
		fU = ph.U;
		pBod = ph.bod[0];
		pByaw = ph.byaw[0];
		pStamp = ph.stamp[0];
		vu = CVarF('vr_vunits_per_meter', 34);
		ws = CVarF('vr_weaponScale', 1.02);
		ox = CVarF('vr_3dweaponOffsetX', 0);
		oy = CVarF('vr_3dweaponOffsetY', 0);
		oz = CVarF('vr_3dweaponOffsetZ', 0);
		return true;
	}

	// a point of the held model -> world. Same chain as RenderHUDModel: hand,
	// scale .01, translate (0, 5, 30), model Scale -1 1 1 with ZOffset -5,
	// the jDoom 90 degree turn, vr_weaponScale; local x right, y up, -z forward.
	Vector3 Place(Vector3 m)
	{
		// The two-handed block moves the model, so the blade must move with it or the
		// hits stay where the one-handed axe was. Offset.y comes off forward, and
		// ZOffset off up measured against the shipped block's -5.
		double sf = poseFrame == 1 ? 8.9584 : 0.0;
		double su = poseFrame == 1 ? -17.2631 : 0.0;
		double f = 0.01 * (ws * m.x - 30 - oz - sf);
		double r = 0.01 * (-ws * m.y + ox);
		double u = 0.01 * (ws * m.z + oy + su);
		Vector3 w = fF * f + fR * r + fU * u;
		w.z /= ps;
		return fH + w * vu;
	}

	void Push(Vector3 tip, Vector3 pos)
	{
		head = (head + 1) % HIST;
		tx[head] = tip.x;
		ty[head] = tip.y;
		tz[head] = tip.z;
		px[head] = pos.x;
		py[head] = pos.y;
		pz[head] = pos.z;
		if (count < HIST)
			count++;
	}

	void Reset()
	{
		count = 0;
		havePrev = false;
		prevStamp = 0;
		swingTics = 0;
		calmTics = 0;
		inWall = false;
		struck.Clear();
	}

	//------------------------------------------------------------------
	void Tick(PlayerPawn mo)
	{
		if (whooshWait > 0)
			whooshWait--;
		if (scrapeWait > 0)
			scrapeWait--;
		// F11: a paint kept after a release that was not a throw -- gone after its second, or with its monster
		if (lockKeep > 0 && (mo.Level.maptime > lockKeep || !lockTarget || lockTarget.health <= 0))
			Unlock();
		if (lockKeep > 0 && lockRing && lockTarget)
			lockRing.SetOrigin(lockTarget.pos + (0, 0, lockTarget.height * 0.5), true);

		int k = KindOf(mo);
		if (k != kind)
		{
			Reset();
			Unlock();	// the axe went away: so does the paint
			kind = k;
		}
		if (k == 0 || !ReadyPose(mo, k) || !Frame(mo))
		{
			Reset();
			return;
		}

		// 1.97 F7: THE SNAP-TURN AND TELEPORT PATCH IS GONE, not retuned. It threw away two
		// tics whenever the pawn turned more than 12 degrees or moved more than 64 units, which
		// is the shape of fix the melee document records failing in the saber: above about
		// 280 deg/s a smooth-turn player trips it EVERY tic and loses every swing, and below the
		// threshold the turn is not subtracted at all. BodyFrame now converts each sample with
		// the body pose recorded beside it, so a turn cancels arithmetically and there is
		// nothing left to throw away.

		Vector3 bin = Place(BladeIn(k));
		Vector3 bout = Place(BladeOut(k));
		Push(bout, mo.pos);
		if (!havePrev)
		{
			prevIn = bin;
			prevOut = bout;
			prevPos = mo.pos;
			prevRel = BodyFrame(mo, bout);
			prevRelIn = BodyFrame(mo, bin);
			prevStamp = pStamp;
			havePrev = true;
			return;
		}

		bool isButt = k == RIFLEBUTT || k == SGBUTT || k == SSGBUTT || k == ASGBUTT || k == MP40BUTT || k == SMGBUTT || k == MGBUTT || k == MG42BUTT;
		double thr = (k == AXE ? AXE_SWING : k == SWORD ? SWORD_SWING
			: isButt ? BUTT_SWING : WHIP_SWING) * vu / 35.
			* max(0.2, Cv(mo, 'rsvr_melee_swing', 1.0))
			* ((k == AXE || k == SWORD) ? 1.5 : 1.0);	// F11 (owner): "swing sensitivity seems too high"
		// 1.11 (owner: "goes insane with attacks just when I move around"). The blade is measured
		// in the BODY's own frame (from the pawn, turned by the pawn's angle), so walking,
		// strafing and turning move nothing; only the arm swinging the blade counts. (World
		// motion minus the pawn's motion was fooled by turns and by the controller and the pawn
		// landing a tic apart.)
		// 1.97 F7: per TIC, over the gap the stamps actually record. This used to be a bare
		// difference, which is a velocity only while no tic is ever missed; a dropped tic read as
		// a swing twice as fast as it was. A gap of 0 would divide by zero, so it is floored at 1.
		int gap = max(1, pStamp - prevStamp);
		Vector3 rel = BodyFrame(mo, bout);
		Vector3 vel = (rel - prevRel) / gap;
		prevRel = rel;
		Vector3 relIn = BodyFrame(mo, bin);
		Vector3 velIn = (relIn - prevRelIn) / gap;
		prevRelIn = relIn;
		prevStamp = pStamp;
		double speed = vel.Length();
		double power = speed / thr;

		// THE BACKSWING IS NOT A STRIKE. The test used to be speed alone, so raising the axe to
		// strike was itself a hit -- it landed before the player had swung, and read as the axe
		// being wildly oversensitive (owner, 2026-10-13). Motion that is mostly upward is the
		// player winding up, so it does not cut, and it falls through to the calm branch below
		// so the downswing that follows is a fresh swing with a cleared strike list.
		double rise = speed > 0 ? vel.z / speed : 0;
		// 2026-10-16 (owner): NO hits on the upswing. Only a level or downward blade cuts
		// (rsvr_melee_up, default 0.15: about 9 degrees up at most; it was 0.55, about 33).
		// 1.11 (owner): "swinging an axe DOWNWARD meaningfully". A blow must now point down by at
		// least rsvr_melee_down of its speed (default 0.25, about 15 degrees below level); a
		// level or rising blade never cuts.
		bool backswing = rise > -clamp(Cv(mo, 'rsvr_melee_down', 0.25), 0.0, 0.9);
		// F11 (owner): the axe and the sword cut on a DOWN or a SIDE swing, never an upswing --
		// anything that rises more than about 9 degrees is a wind-up
		if (k == AXE || k == SWORD)
			backswing = rise > 0.15;
		if (isButt)
		{
			// 1.97 the butt strike. Not the axe's must-point-DOWN test: this blow drives
			// forward and up. And two hands is NOT the gate -- two hands on a rifle is how
			// you hold a rifle. What separates it is the butt LEADING: the gun pivots about
			// the front hand, so the stock outruns the muzzle. Walking moves both ends alike
			// (and the body frame has already cancelled it) and raising the gun moves both;
			// only the pivot does this.
			double fwd = speed > 0 ? vel.x / speed : 0;
			backswing = !RSVR_VRHand.Steadied(mo)
				|| fwd < clamp(Cv(mo, 'rsvr_butt_fwd', 0.5), 0.0, 1.0)
				|| velIn.Length() * clamp(Cv(mo, 'rsvr_butt_lead', 1.3), 1.0, 4.0) > speed;
		}

		if (power >= 1 && !backswing)
		{
			calmTics = 0;
			swingTics++;
			if (swingTics == 1 && whooshWait == 0)
			{
				if (k == AXE)
					mo.A_StartSound("Axe/Swing", CHAN_WEAPON, CHANF_OVERLAP);
				else
					mo.A_StartSound("Melee/SwingStrong", CHAN_WEAPON, CHANF_OVERLAP);
				whooshWait = 12;
			}
			Sweep(mo, k, prevIn, prevOut, bin, bout, power);
		}
		else if (++calmTics > 2)
		{
			swingTics = 0;
			struck.Clear();
		}
		WallCheck(mo, bout, power);

		prevIn = bin;
		prevOut = bout;
		prevPos = mo.pos;
	}

	//------------------------------------------------------------------
	// the blade's path this tic (a0-b0 -> a1-b1) against every body near it;
	// each body is hit once per swing, at the first point the blade reaches it
	void Sweep(PlayerPawn mo, int k, Vector3 a0, Vector3 b0, Vector3 a1, Vector3 b1, double power)
	{
		double pad = (k == AXE) ? 3 : 5;
		Vector3 c = (a0 + b0 + a1 + b1) / 4;
		double r = max(max((a0 - c).Length(), (b0 - c).Length()), max((a1 - c).Length(), (b1 - c).Length())) + pad;
		double travel = max((b1 - b0).Length(), (a1 - a0).Length());
		int steps = clamp(int(travel / 4) + 1, 1, 16);
		int segs = (k == AXE) ? 2 : 8;

		Array<Actor> victims;
		Array<double> hx;
		Array<double> hy;
		Array<double> hz;
		Array<double> dx;
		Array<double> dy;
		Array<double> dz;
		let it = BlockThingsIterator.CreateFromPos(c.x, c.y, c.z - r, 2 * r, r, false);
		while (it.Next())
		{
			Actor t = it.thing;
			if (!t || t == mo || t.player || !t.bSHOOTABLE || t.bFRIENDLY || t.bDORMANT || t.health <= 0)
				continue;
			if (struck.Find(t) != struck.Size() || victims.Find(t) != victims.Size())
				continue;
			bool hit = false;
			Vector3 at = (0, 0, 0);
			Vector3 dir = (0, 0, 0);
			for (int i = 1; i <= steps && !hit; i++)
			{
				double f = double(i) / steps;
				for (int j = segs; j >= 0 && !hit; j--)
				{
					double s = double(j) / segs;
					Vector3 p0 = a0 + (b0 - a0) * s;
					Vector3 p1 = a1 + (b1 - a1) * s;
					Vector3 q = p0 + (p1 - p0) * f;
					if (Touches(t, q, pad))
					{
						hit = true;
						at = q;
						dir = p1 - p0;
					}
				}
			}
			if (!hit || !Clear(mo, fH, at))
				continue;
			victims.Push(t);
			hx.Push(at.x);
			hy.Push(at.y);
			hz.Push(at.z);
			dx.Push(dir.x);
			dy.Push(dir.y);
			dz.Push(dir.z);
		}

		// The axe is bladed on ONE side. BladeIn is the top of the head and BladeOut the
		// cutting edge, so this is where the edge points this tic -- what the two-handed
		// bite is scored against.
		Vector3 edge = b1 - a1;

		// strike after the search: the hits spawn gore and kill things
		for (int i = 0; i < victims.Size(); i++)
		{
			Actor t = victims[i];
			if (!t || t.health <= 0)
				continue;
			struck.Push(t);
			Strike(mo, k, t, (hx[i], hy[i], hz[i]), (dx[i], dy[i], dz[i]), power, edge);
		}
	}

	static bool Touches(Actor t, Vector3 q, double pad)
	{
		if (q.z < t.pos.z - pad || q.z > t.pos.z + t.height + pad)
			return false;
		double ddx = q.x - t.pos.x;
		double ddy = q.y - t.pos.y;
		double rr = t.radius + pad;
		return ddx * ddx + ddy * ddy <= rr * rr;
	}

	// nothing solid between the hand and that point
	static bool Clear(Actor mo, Vector3 from, Vector3 to)
	{
		Vector3 d = to - from;
		double len = d.Length();
		if (len < 1)
			return true;
		FLineTraceData tr;
		mo.LineTrace(VectorAngle(d.x, d.y), len, -asin(clamp(d.z / len, -1, 1)),
			TRF_ABSPOSITION | TRF_THRUACTORS, from.z, from.x, from.y, tr);
		return tr.HitType == TRACE_HitNone || tr.HitType == TRACE_HitActor;
	}

	// Both hands on the haft AND the cutting edge leading the blow. Two hands alone is
	// not the reward: the axe has an edge on one side, so what is paid for is landing
	// it (owner, 2026-10-23, in place of a flat 2x for holding it). Two hands is the
	// engine's own WF_TWOHANDSTABILIZED, the same flag hands.zs draws the support hand
	// from, so the damage and the hands the player sees can never disagree.
	static bool TwoHandedBite(PlayerPawn mo, Vector3 dir, Vector3 edge)
	{
		if (!RSVR_VRHand.TwoHands(mo))
			return false;
		double el = edge.Length(), dl = dir.Length();
		if (el <= 0 || dl <= 0)
			return false;
		return ((dir / dl) dot (edge / el)) >= clamp(Cv(mo, 'rsvr_axe_edge', 0.5), -1.0, 1.0);
	}

	void Strike(PlayerPawn mo, int k, Actor t, Vector3 at, Vector3 dir, double power, Vector3 edge)
	{
		// start BD22's attack just inside the body, at the height the blade met it
		double rx = at.x - t.pos.x;
		double ry = at.y - t.pos.y;
		double rl = sqrt(rx * rx + ry * ry);
		double lim = max(t.radius - 2, 1);
		if (rl > lim)
		{
			rx *= lim / rl;
			ry *= lim / rl;
		}
		Vector3 p = (t.pos.x + rx, t.pos.y + ry, clamp(at.z, t.pos.z + 1, t.pos.z + max(t.height - 1, 1)));
		double dl = dir.Length();
		if (dl > 0)
			dir = dir / dl;
		else
			dir = (cos(mo.angle), sin(mo.angle), 0);

		if (k == AXE)
		{
			Launch(mo, 'AxeAttack', p, dir);
			if (power >= 1.6)
				Launch(mo, 'AxeAttackNoDecal', p, dir);
			if (power >= 2.4)
				Launch(mo, 'AxeAttack', p, dir);
			// half an AxeAttack on top when the edge bites with both hands behind it
			if (TwoHandedBite(mo, dir, edge))
				Launch(mo, 'RSVR_AxeHalf', p, dir);
		}
		else if (k == SWORD)
		{
			Launch(mo, 'DSAttack', p, dir);
			Launch(mo, 'DSAttack2', p, dir);
		}
		else
		{
			// 1.97 the pistol whip: BD22's own punch, which is what this pack's fists
			// already land (zscript/rsq/fists.zs), so its gore decides the result.
			if (k == PISTOL || k == REVOLVER)
			{
				Launch(mo, mo.CountInv('PowerStrength') > 0 ? 'MeleeStrike1Berserked' : 'MeleeStrikeNormal', p, dir);
				if (power >= 2.0)
					Launch(mo, 'MeleeStrikeNormal', p, dir);
			}
			else
			{
				// 1.97 the butt strike: BD22's own kick, which is what a stock to the face is
				// and what the gun bash already lands.
				Launch(mo, mo.CountInv('PowerStrength') > 0 ? 'SuperKickAttack' : 'KickAttack', p, dir);
			}
		}
		Buzz(mo);
	}

	// BD22's attack actor, fired by the player from that point
	static void Launch(PlayerPawn mo, Name cname, Vector3 p, Vector3 dir)
	{
		class<Actor> cls = cname;
		if (!cls)
			return;
		let a = Actor.Spawn(cls, p, ALLOW_REPLACE);
		if (!a)
			return;
		a.target = mo;
		a.angle = VectorAngle(dir.x, dir.y);
		a.pitch = -asin(clamp(dir.z, -1, 1));
		a.vel = dir * a.speed;
		a.CheckMissileSpawn(0);
	}

	// controller rumble: the engine buzzes the weapon hand when the player
	// fires a projectile (p_mobj.cpp P_SpawnPlayerMissile)
	static void Buzz(PlayerPawn mo)
	{
		mo.SpawnPlayerMissile('RSVR_Buzz', mo.angle, noautoaim: true);
	}

	// the blade going into a wall, floor or ceiling at speed: BD22's axe impact
	// (sparks and clang, or the floor's splash / dirt)
	void WallCheck(PlayerPawn mo, Vector3 bout, double power)
	{
		Vector3 d = bout - fH;
		double len = d.Length();
		bool blocked = false;
		Vector3 hitAt = (0, 0, 0);
		if (len > 1)
		{
			FLineTraceData tr;
			mo.LineTrace(VectorAngle(d.x, d.y), len, -asin(clamp(d.z / len, -1, 1)),
				TRF_ABSPOSITION | TRF_THRUACTORS, fH.z, fH.x, fH.y, tr);
			if (tr.HitType == TRACE_HitWall || tr.HitType == TRACE_HitFloor || tr.HitType == TRACE_HitCeiling)
			{
				blocked = true;
				hitAt = tr.HitLocation;
			}
		}
		if (blocked && !inWall && power >= 1 && scrapeWait == 0)
		{
			Vector3 dir = d / len;
			Launch(mo, 'AxeAttack', hitAt - dir * 6, dir);
			Buzz(mo);
			scrapeWait = 8;
		}
		inWall = blocked;
	}

	//------------------------------------------------------------------
	// axe alt-fire, called every tic of the hold by RSVR_AxeGrip
	static void Grip(PlayerPawn mo)
	{
		// rsg_vr 0 (menu: VR throwing off) -> BD22's own canned axe throw
		bool vr = RSVR_VRHand.InVR(mo) && RSR.PlayerInt(mo.player, 'rsg_vr', 1) != 0;
		mo.SetInventory('RSVR_NotVR', vr ? 0 : 1);
		mo.SetInventory('RSVR_AxeThrown', 0);
		if (!vr)
			return;
		// the trigger path (Axe.dec TrigGrip, VR throwing on) holds with the trigger, like the grenade
		bool held = mo.CountInv('RSVR_AxeTrig') > 0 ? (mo.player.cmd.buttons & BT_ATTACK) != 0 : HoldDown(mo);
		mo.SetInventory('RSVR_AxeHolding', held ? 1 : 0);
		if (!held)	// F11: WorldTick sets this AFTER the weapon ticks, so it is still 1 on the release tic,
			mo.SetInventory('RSVR_AxeHold', 0);	// and Ready would send the axe straight back here: a zero-tic loop
		let h = RSVR_MeleeHandler.HandOf(mo);
		if (held)
		{
			// winding up: paint what the hand is pointing at
			if (h)
			{
				h.lockKeep = 0;	// F11: a kept paint is picked back up
				h.LockTick(mo);
			}
			return;
		}
		if (h && h.Throw(mo))
		{
			mo.SetInventory('RSVR_AxeThrown', 1);
			h.Unlock();
		}
		// F11 (owner): let go without a throw and the paint stays a second, as on the ShieldSaw and the
		// saber -- pick the hold back up and it is still there; otherwise Tick takes it down
		else if (h && h.lockTarget && h.lockKeep == 0)
			h.lockKeep = mo.Level.maptime + 35;
	}

	// a world point in the body's own frame: forward, left, up (map units)
	// 1.97 F7: against the body pose that came WITH the sample (pBod / pByaw), not against
	// the pawn's live position and angle. Those two are a tic apart -- the hand is written by
	// the renderer at the end of a frame, the pawn turns in the tic after -- and that gap is
	// what used to turn a snap turn into a swing.
	Vector3 BodyFrame(PlayerPawn mo, Vector3 p)
	{
		Vector3 d = p - pBod;
		double c = cos(pByaw), s = sin(pByaw);
		return (d.x * c + d.y * s, -d.x * s + d.y * c, d.z);
	}

	// Drop the paint and take the ring down.
	void Unlock()
	{
		if (lockRing)
			lockRing.Destroy();
		lockRing = null;
		lockTarget = null;
		lockKeep = 0;
	}

	// While the throw is held: paint the monster the hand points at. A lock STAYS locked
	// until it dies, is lost from sight, or leaves a much wider cone than the one that
	// took it -- otherwise it flickers off every time the arm moves to wind up. Same
	// shape as the Quest ShieldSaw's disc locks (ssq/disc.zs).
	void LockTick(PlayerPawn mo)
	{
		if (!Frame(mo) || KindOf(mo) != AXE)
		{
			Unlock();
			return;
		}
		double cone = clamp(Cv(mo, 'rsvr_axe_lock_cone', 16.0), 1.0, 90.0);
		double range = clamp(Cv(mo, 'rsvr_axe_lock_range', 1200.0), 64.0, 8192.0);
		Vector3 from = fH;
		Vector3 aim = fF;
		if (lockTarget)
		{
			Vector3 to = lockTarget.pos + (0, 0, lockTarget.height * 0.5) - from;
			double dist = to.Length();
			bool keep = lockTarget.health > 0 && dist > 1 && dist <= range * 1.5
				&& acos(clamp((to / dist) dot aim, -1, 1)) <= cone * 2.2
				&& mo.CheckSight(lockTarget);
			if (!keep)
				Unlock();
		}
		if (!lockTarget)
		{
			Actor best = null;
			double bestAng = cone;
			let it = BlockThingsIterator.CreateFromPos(from.x, from.y, from.z - range, range * 2.0, range, false);
			while (it.Next())
			{
				Actor t = it.thing;
				if (!t || t == mo || t.player || !t.bISMONSTER || !t.bSHOOTABLE
					|| t.bFRIENDLY || t.bDORMANT || t.health <= 0)
					continue;
				Vector3 to = t.pos + (0, 0, t.height * 0.5) - from;
				double dist = to.Length();
				if (dist < 1 || dist > range)
					continue;
				double ang = acos(clamp((to / dist) dot aim, -1, 1));
				if (ang >= bestAng || !mo.CheckSight(t))
					continue;
				bestAng = ang;
				best = t;
			}
			if (best)
			{
				lockTarget = best;
				lockRing = Actor.Spawn('RSVR_AxeLock', best.pos + (0, 0, best.height * 0.5), ALLOW_REPLACE);
				Buzz(mo);	// the hand says the paint landed
			}
		}
		if (lockRing && lockTarget)
			lockRing.SetOrigin(lockTarget.pos + (0, 0, lockTarget.height * 0.5), true);
	}

	bool Throw(PlayerPawn mo)
	{
		if (KindOf(mo) != AXE || !Frame(mo))
			return false;
		// A two-handed axe is not thrown (owner, 2026-10-23). Let go with the off hand and
		// it is one-handed again, so the throw is back -- the rule follows the grip, and
		// the same flag that pays the damage withholds the throw.
		if (RSVR_VRHand.TwoHands(mo))
			return false;

		// fastest step of the axe's edge over the last few tics: people slow
		// down as they let go
		Vector3 t1 = Place(BladeOut(AXE));
		Vector3 p1 = mo.pos;
		double best = 0;
		Vector3 vel = (0, 0, 0);
		int n = min(count, 4);
		for (int i = 0; i < n; i++)
		{
			int j = (head - i + HIST) % HIST;
			Vector3 t0 = (tx[j], ty[j], tz[j]);
			Vector3 p0 = (px[j], py[j], pz[j]);
			Vector3 v = t1 - t0;
			double rel = (v - (p1 - p0)).Length();
			if (rel > best)
			{
				best = rel;
				vel = v;
			}
			t1 = t0;
			p1 = p0;
		}
		if (best < THROW_MIN * vu / 35. || vel.Length() <= 0)
			return false;

		double spd = clamp(vel.Length() * 3, 14, 42);
		Vector3 dir = vel.Unit();
		// F11 (owner): the arm's own motion blended with where the hand points, as the ShieldSaw
		// (ssq_throw_blend 0.7) and the saber (0.6) do. 1 = all arm (as it was), 0 = all aim.
		double bl = clamp(Cv(mo, 'rsvr_axe_throw_blend', 0.7), 0.0, 1.0);
		if (fF.Length() > 0)
			dir = (dir * bl + fF.Unit() * (1.0 - bl)).Unit();
		Vector3 from = Place(AxeHead());
		if (!Clear(mo, fH, from))
			from = fH;
		// a painted target takes the throw; with nothing painted, the old 8-degree assist
		if (lockTarget && lockTarget.health > 0)
		{
			Vector3 to = lockTarget.pos + (0, 0, lockTarget.height * 0.5) - from;
			double tt = to.Length() / spd;
			to.z += 0.5 * mo.GetGravity() * tt * tt;
			if (to.Length() > 0)
				dir = to.Unit();
		}
		else
			dir = AimAssist(mo, from, dir, spd);

		Name cname = mo.CountInv('PowerStrength') > 0 ? 'ThrowedAxeStrong' : 'ThrowedAxe';
		class<Actor> cls = cname;
		if (!cls)
			return false;
		let axe = Actor.Spawn(cls, from, ALLOW_REPLACE);
		if (!axe)
			return false;
		axe.target = mo;
		axe.angle = VectorAngle(dir.x, dir.y);
		axe.pitch = -asin(clamp(dir.z, -1, 1));
		axe.vel = dir * spd;
		mo.A_StartSound("Axe/Throw", CHAN_WEAPON, CHANF_OVERLAP);
		Buzz(mo);
		axe.CheckMissileSpawn(mo.radius);
		Reset();
		return true;
	}

	// a throw within 8 degrees of a visible monster goes to it, arced for the drop
	static Vector3 AimAssist(PlayerPawn mo, Vector3 from, Vector3 dir, double spd)
	{
		Actor best = null;
		double bestCos = cos(8);
		let it = ThinkerIterator.Create('Actor');
		Actor t;
		while (t = Actor(it.Next()))
		{
			if (!t.bISMONSTER || !t.bSHOOTABLE || t.bFRIENDLY || t.bDORMANT || t.health <= 0)
				continue;
			Vector3 to = t.pos + (0, 0, t.height * 0.5) - from;
			double dist = to.Length();
			if (dist < 1 || dist > 1536)
				continue;
			double c = (to dot dir) / dist;
			if (c <= bestCos || !mo.CheckSight(t))
				continue;
			bestCos = c;
			best = t;
		}
		if (!best)
			return dir;
		Vector3 to = best.pos + (0, 0, best.height * 0.5) - from;
		double tics = to.Length() / spd;
		to.z += 0.5 * mo.GetGravity() * tics * tics;
		return to.Unit();
	}
}

// the axe's alt-fire state gives this every tic it holds; it never stays in
// the inventory, it only runs RSVR_Hand.Grip for the player
class RSVR_AxeGrip : Inventory
{
	override bool TryPickup(in out Actor toucher)
	{
		let mo = PlayerPawn(toucher);
		if (mo)
			RSVR_Hand.Grip(mo);
		return false;
	}
}

class RSVR_Token : Inventory
{
	Default
	{
		Inventory.MaxAmount 1;
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
	}
}

class RSVR_AxeHolding : RSVR_Token {}
class RSVR_AxeHold : RSVR_Token {}		// the hold input is down: Ready enters the hold loop
class RSVR_AxeThrown : RSVR_Token {}
class RSVR_AxeTrig : RSVR_Token {}
class RSVR_AxeVRThrow : RSVR_Token {}
class RSVR_MeleeTwo : RSVR_Token {}	// F11: the off grip held near the axe or the sword
class RSVR_AxeTwo : RSVR_Token {}		// both hands on the haft: the shifted placement
class RSVR_NotVR : RSVR_Token {}

// a projectile the engine counts as a shot: spawning it buzzes the weapon hand
class RSVR_Buzz : Actor
{
	Default
	{
		Projectile;
		+NOCLIP
		Radius 1;
		Height 1;
		Speed 1;
		DamageType "RSVRHaptic";
		RenderStyle "None";
	}
	States
	{
	Spawn:
		TNT1 A 1;
		Stop;
	}
}

// The ring painted on the monster the axe is aimed at while a throw is readied. The art is
// the Quest ShieldSaw's own lock mark (ssq/disc.zs SSQ_LockMark), carried here under our
// own sprite name so the two mods never share a lump -- which is what ShieldSaw did with
// the saber's UBLK frames. 48x48 drawn at 0.35, billboarded so it is never seen edge-on.
class RSVR_AxeLock : Actor
{
	Default
	{
		+NOINTERACTION
		+NOBLOCKMAP
		+NOGRAVITY
		+NOTONAUTOMAP
		+FORCEXYBILLBOARD
		RenderStyle "Add";
		Alpha 0.95;
		Scale 0.35;
	}
	States
	{
	Spawn:
		RQLK ABCD 3 Bright;
		Loop;
	}
}
