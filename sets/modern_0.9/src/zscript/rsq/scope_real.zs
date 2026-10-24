// RS VR scopes, REAL mode: the view down the bore, rendered into the scope's own glass.
//
// The companion to rsq/scope.zs. That file owns the per-gun table and the collimated DOT;
// this one owns the magnified see-through picture, and nothing here runs unless the gun's
// mode cvar (RSQ_ScopeTable.ModeCVar) says 1.
//
// HOW IT WORKS
//   An invisible actor (RSQ_ScopeCam) is parked each tic at the lens, pointing down the bore,
//   and TexMan.SetCameraToTexture binds it to a camera texture declared in ANIMDEFS.rsq. The
//   glass surface's skin is then swapped to that texture with A_ChangeModel /
//   CMDL_USESURFACESKIN, which is why the glass has to be its OWN MD3 surface: the RailGun's
//   mesh already carried one, the Ruger's ocular disc was carved into one by the kit
//   (kit/tool/md3_carve_surface.py).
//
// WHY THE GATE IS THE WHOLE DESIGN
//   A camera texture is a SECOND FULL SCENE RENDER of the level, every frame it is on screen
//   (hw_entrypoint.cpp, "prepare all camera textures that have been used in the last frame").
//   This ships on a standalone Quest, where that is not affordable as a background cost. The
//   engine's own trigger is the texture being DRAWN -- binding it for a draw calls
//   FCanvasTexture::NeedUpdate (gl_renderstate.cpp / gles_renderstate.cpp), and the entrypoint
//   only re-renders textures whose bNeedsUpdate is set. So the skin swap IS the switch: while
//   the glass wears its ordinary skin, the scope costs exactly nothing. The swap only happens
//   when the player's eye is actually behind the eyepiece.
//
// ONE EYE, ON PURPOSE
//   RenderViewpoint is called from the camera-texture loop with mainview and toscreen both
//   false, so GetVRMode(mainview && toscreen) hands back the MONO mode and the texture is
//   rendered ONCE, not once per eye. Both eyes therefore see the same flat image with no
//   stereo disparity. That is the right answer for a scope and not a limitation worked around:
//   a real telescopic sight is monocular and its image is at infinity. It also means the cost
//   is one extra render, not two.
//
//   The image is also one frame stale, because camera textures are rendered before the main
//   view. At 72 Hz that is 14 ms of lag on the picture inside the tube while the tube itself
//   is current. Nothing can be done about that from script.
//
// LOCAL PLAYER, SINGLE PLAYER
//   Everything here is driven by where the headset is, which only the local machine knows, and
//   it spawns an actor and writes modelData. Doing that for one player on one machine is fine
//   on its own but is not something to start in a netgame, so -- like the VR hand poses
//   (rsq/hands.zs) -- the whole feature is off when multiplayer is set. The mode cvar is still
//   read per player with CVar.GetCVar so that rule never depends on a local FindCVar.

class RSQ_ScopeReal : EventHandler
{
	// WHICH SURFACE THE GLASS IS. This belongs in RSQ_ScopeTable beside Lens/Axis/Radius/Mag
	// and should move there the next time that file is opened -- it is kept here only because
	// scope.zs is owned elsewhere and this lane may not edit it. Indices match the table's:
	//   1 RailGun  surface 1 "ScopeGlass", authored that way in RailGun.md3
	//   2 Sniper   surface 10 "ScopeGlass", carved out of surface 3 (leupold_scope) by
	//              kit/tool/md3_carve_surface.py; MODELDEF.rsr must list SurfaceSkin 0 10
	static int GlassSurface(int i)
	{
		static const int v[] = { -1, 1, 10 };
		return i > 0 && i < v.Size() ? v[i] : -1;
	}

	// The camera texture, declared in ANIMDEFS.rsq. Eight characters, because
	// ParseCameraTexture looks the name up with TEXMAN_ShortNameOnly and a longer one would
	// never be found again.
	//
	// ONE constant, and a String. A second one as a Name is "Bad type for constant
	// definiton": a ZScript const takes int, float, double, string or bool and nothing
	// else, so a name literal is refused outright. A_ChangeModel wants a Name and takes
	// this String by the implicit conversion -- which also means the two spellings can
	// never drift apart.
	const TEXNAME = "RSQSCOPE";

	// THE SIGHT PICTURE, in centimetres in the weapon controller's frame.
	//   RELIEF   how far behind the glass the eye may be and still be looking through it. A
	//            Leupold VX-1's real eye relief is about 10.7 cm; 12 gives a little slack for
	//            tracking jitter and for the fact that the eye point below is the pawn's XY
	//            with the player's view height rather than a true head position.
	//   RELIEF_OFF / SIDE_OFF  the same two limits, loosened, for staying on once on. Without
	//            hysteresis a head sitting on the threshold turns a whole extra scene render on
	//            and off on alternate frames, which is both the worst case for cost and a
	//            visible strobe. The gap is deliberate and wide.
	//   HOLD     tics the picture stays up after the gate fails, so a flinch or one bad
	//            tracking sample does not blank the scope.
	const RELIEF = 12.0;
	const RELIEF_OFF = 15.0;
	const SIDE_ON = 1.00;		// of the glass radius
	const SIDE_OFF = 1.35;
	const HOLD = 6;

	RSQ_ScopeCam cam;
	int lastIndex;			// the gun the swap is currently applied to, 0 = none
	int lastSurface;
	Weapon lastWeapon;
	bool skinOn;
	int holdTics;

	// ---------------------------------------------------------------- the hand this tic
	// Identical chain to rsvr/melee.zs Frame(): the gun is a psprite and has no world
	// position, so the only way to land on a point of the drawn model is to redo the
	// transform the renderer used (models.cpp RenderHUDModel).
	private Vector3 fH;
	private Vector3 fF;
	private Vector3 fR;
	private Vector3 fU;
	private double ps;
	private double vu;
	private double ox;
	private double oy;
	private double oz;

	private static double CVarF(Name n, double def)
	{
		let cv = CVar.FindCVar(n);
		return cv ? cv.GetFloat() : def;
	}

	private bool Frame(PlayerPawn mo)
	{
		if (!RSVR_VRHand.InVR(mo))
			return false;
		ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		fH = RSVR_VRHand.HandPos(mo);
		fF = RSVR_VRHand.HandDir(mo, 0, 0, ps);
		fR = -RSVR_VRHand.HandDir(mo, 90, 0, ps);
		fU = RSVR_VRHand.HandDir(mo, 0, 90, ps);
		vu = CVarF('vr_vunits_per_meter', 34);
		if (vu <= 0)
			vu = 34;
		ox = CVarF('vr_3dweaponOffsetX', 0);
		oy = CVarF('vr_3dweaponOffsetY', 0);
		oz = CVarF('vr_3dweaponOffsetZ', 0);
		return true;
	}

	// A point given in the table's own units -- centimetres in the controller frame, F forward,
	// L left, U up -- placed in the world.
	//
	// melee.zs Place() takes MODEL units and does the Scale / Offset / ZOffset / (0,5,30) /
	// vr_weaponScale arithmetic itself. RSQ_ScopeTable's numbers were measured AFTER all of
	// that (rgeo.py walks the same chain), so the only part left to redo here is the tail: the
	// 0.01 scale, the player's own weapon-offset cvars, the squash and the hand basis. Written
	// out against melee.zs Place(), with F = ws*m.x - 30 - Offset.y and so on already folded
	// into the table:
	//     f = 0.01 * (ws*m.x - 30 - oz - Offset.y)  ->  0.01 * (F - oz)
	//     r = 0.01 * (-ws*m.y + ox)                 ->  0.01 * (ox - L)
	//     u = 0.01 * (ws*m.z + oy + ZOffset + 5)    ->  0.01 * (U + oy)
	// so the two agree exactly at the vr_3dweaponOffset defaults, and still track the player's
	// offsets when they are not default. A vr_weaponScale other than the 1.02 the table was
	// measured at is the one thing it cannot follow; that is the table's limit, not this code's.
	private Vector3 Place(Vector3 flu)
	{
		Vector3 w = fF * (0.01 * (flu.x - oz))
			+ fR * (0.01 * (ox - flu.y))
			+ fU * (0.01 * (flu.z + oy));
		w.z /= ps;
		return fH + w * vu;
	}

	// Where the eye is, in the same frame, in centimetres: the play-scope twin of
	// RSQ_Scope.EyeInHandFrame. That one rebuilds the hand basis from the Euler angles because
	// ui may not call AttackDir; here the real basis is already in hand.
	//
	// The view point is the pawn's XY with the player's view height, which in VR tracks the
	// headset vertically. Stock QuestZDoom exposes no head POSITION to script, so a sideways
	// head lean does not move this point -- the lateral test below is really "is the GUN in
	// front of your face", which for a shouldered rifle is the same question.
	private Vector3 EyeFLU(PlayerPawn mo)
	{
		let p = mo.player;
		if (!p)
			return (0, 0, 0);
		Vector3 eye = (mo.pos.x, mo.pos.y, p.viewz);
		Vector3 d = eye - mo.AttackPos;
		d.z *= ps;					// undo the squash Place applies
		double k = 100.0 / vu;		// map units -> cm
		return ((d dot fF) * k, -(d dot fR) * k, (d dot fU) * k);
	}

	// Is the player looking THROUGH the sight? Same geometry the collimated dot uses
	// (RSQ_Scope.DotAt): drop the eye onto the bore axis, and ask how far back it is and how
	// far off to the side. `wide` loosens both limits for a picture that is already up.
	private bool Through(PlayerPawn mo, int i, bool wide)
	{
		Vector3 P = RSQ_ScopeTable.Lens(i);
		Vector3 A = RSQ_ScopeTable.Axis(i);
		double al = A.Length();
		if (al <= 0)
			return false;
		A = A / al;
		Vector3 E = EyeFLU(mo);
		Vector3 toLens = P - E;
		double along = toLens dot A;		// > 0: the glass is in front of the eye
		if (along <= 0)
			return false;
		if (along > (wide ? RELIEF_OFF : RELIEF))
			return false;
		double side = (toLens - A * along).Length();
		double rr = RSQ_ScopeTable.Radius(i);
		if (rr <= 0)
			return false;
		return side <= rr * (wide ? SIDE_OFF : SIDE_ON);
	}

	// ---------------------------------------------------------------- the skin
	// A_ChangeModel is an Actor action function, so it is called on the weapon the way the
	// engine's own script calls A_Explode on a puff. From outside a psprite state and without
	// CMDL_WEAPONTOPLAYER it writes the INVOKER's modelData (p_actionfunctions.cpp), which is
	// the weapon -- and RenderHUDModel reads psp->Caller's modelData, so that is exactly the
	// one the drawn gun uses. Passing no skin name stores a null texture id, which
	// CalcModelOverrides treats as "fall through to the MODELDEF SurfaceSkin": that is the way
	// back to the ordinary glass.
	private void SetSkin(Weapon w, int surface, bool on)
	{
		if (!w || surface < 0)
			return;
		// Every argument but the surface skin is deliberately 'None' / "":
		//   modeldef 'None'  leaves modelData->modelDef null, so FindModelFrame keeps looking
		//                    the gun up by its own class exactly as it does untouched;
		//   model    'None'  leaves the override modelID at -1, which CalcModelOverrides reads
		//                    as "no override" and falls through to the MODELDEF mesh -- NOT as
		//                    hide, which is -2 and only comes from CMDL_HIDEMODEL;
		//   skin     'None'  stores a null texture id, which the same function treats as "fall
		//                    through to the MODELDEF SurfaceSkin". That is the way back.
		w.A_ChangeModel('None', 0, "", 'None', surface, "",
			on ? Name(TEXNAME) : Name("None"), CMDL_USESURFACESKIN);
	}

	private void ClearSkin()
	{
		if (skinOn && lastWeapon)
			SetSkin(lastWeapon, lastSurface, false);
		skinOn = false;
	}

	private void Shutdown()
	{
		ClearSkin();
		if (cam)
			cam.Destroy();
		cam = null;
		lastWeapon = null;
		lastIndex = 0;
		lastSurface = -1;
		holdTics = 0;
	}

	// ---------------------------------------------------------------- the tic
	override void WorldLoaded(WorldEvent e)
	{
		// the camera was an actor of the old level and the swap was on the old level's weapon
		cam = null;
		skinOn = false;
		lastWeapon = null;
		lastIndex = 0;
		lastSurface = -1;
		holdTics = 0;
	}

	override void WorldTick()
	{
		// Driven by the headset, writes render state on one machine, and spawns an actor:
		// none of that is a thing to switch on in a netgame. Same gate the hand poses use.
		if (multiplayer)
		{
			Shutdown();
			return;
		}
		if (consoleplayer < 0 || !playeringame[consoleplayer] || !players[consoleplayer].mo)
		{
			Shutdown();
			return;
		}
		let mo = players[consoleplayer].mo;

		let w = mo.player.ReadyWeapon;
		int i = RSQ_ScopeTable.Index(w);
		int surface = GlassSurface(i);

		// out of VR nothing here does anything at all
		if (i <= 0 || surface < 0 || !Frame(mo))
		{
			Shutdown();
			return;
		}

		// 0 = dot, 1 = real. Read per player, never FindCVar, so a netgame cannot disagree
		// about which mode a gun is in. A cvar that does not exist yet reads as dot, which is
		// why this file is inert until MENUDEF/CVARINFO carry the option.
		let cv = CVar.GetCVar(RSQ_ScopeTable.ModeCVar(i), mo.player);
		if (!cv || cv.GetInt() != 1)
		{
			Shutdown();
			return;
		}

		// the gun changed under us: take the swap off the one that had it
		if (w != lastWeapon || i != lastIndex)
		{
			ClearSkin();
			lastWeapon = w;
			lastIndex = i;
			lastSurface = surface;
			holdTics = 0;
		}

		bool through = Through(mo, i, skinOn);
		if (through)
			holdTics = HOLD;
		else if (holdTics > 0)
			holdTics--;
		bool want = through || holdTics > 0;

		if (!want)
		{
			// Off: the glass gets its own skin back and the camera texture is drawn nowhere,
			// so the engine stops rendering it. The camera actor is left parked rather than
			// destroyed -- it costs one thinker and saves spawning on every shoulder.
			ClearSkin();
			return;
		}

		Vector3 lens = Place(RSQ_ScopeTable.Lens(i));
		// Down the bore, as the difference of two placed points rather than a rotated vector:
		// the squash in Place is not a rotation, so a direction has to be transformed the same
		// way a displacement is or it drifts off axis with pitch.
		Vector3 A = RSQ_ScopeTable.Axis(i);
		double al = A.Length();
		if (al <= 0)
			return;
		Vector3 ahead = Place(RSQ_ScopeTable.Lens(i) + A * (10.0 / al));
		Vector3 d = ahead - lens;
		double dl = d.Length();
		if (dl <= 0)
			return;
		d = d / dl;

		if (!cam)
		{
			cam = RSQ_ScopeCam(Actor.Spawn('RSQ_ScopeCam', lens, NO_REPLACE));
			if (!cam)
				return;
		}
		cam.SetOrigin(lens, true);
		cam.angle = VectorAngle(d.x, d.y);
		cam.pitch = -asin(clamp(d.z, -1, 1));
		cam.roll = 0;

		// Horizontal fov for the magnification. 90 degrees is the picture a 1x sight would
		// show, so 90/mag is what a mag-times sight shows of it.
		double mag = RSQ_ScopeTable.Mag(i);
		if (mag < 1.0)
			mag = 1.0;
		TexMan.SetCameraToTexture(cam, TEXNAME, 90.0 / mag);

		if (!skinOn)
		{
			SetSkin(w, surface, true);
			skinOn = true;
		}
	}
}

// The viewpoint the scope renders from. Invisible, inert, and never in anything's way --
// but it keeps its sector links, because the renderer needs a subsector for a viewpoint.
class RSQ_ScopeCam : Actor
{
	Default
	{
		+NOINTERACTION
		+NOBLOCKMAP
		+NOGRAVITY
		+NOCLIP
		+NOTONAUTOMAP
		+DONTSPLASH
		RenderStyle "None";
		Radius 1;
		Height 1;
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}
}
