// RS VR scopes: a sight that can be put on any gun that has one in its mesh.
//
// Two modes per gun (MENUDEF.rsq -> rsq_scope_<gun>):
//   DOT   a collimated red dot. No magnification, no render cost, no mesh change.
//   REAL  the view down the bore, rendered into the scope's own glass surface.
//
// THE DOT IS COLLIMATED, and that is the whole point of it. A reticle painted on the glass
// has full parallax: move your head and the dot slides off what the gun is pointing at, which
// is backwards -- a real reflex sight shows the dot in the same place whatever your eye does.
// So the dot is not painted on the glass. Each rendered frame it is placed at the point D on
// the lens plane where the eye-to-dot ray runs parallel to the bore:
//
//     D = E + A * ((P - E) dot A)          E eye, A bore axis, P a point on the lens plane
//
// The dot therefore slides across the glass as the head moves and the sight picture stays
// true. It is two dot products and a scale, once per frame, in the hook the renderer already
// calls -- ModifyBobLayer3D, which is ui scope and per FRAME, not per tic. That matters: a
// dot placed from a tic-rate sample would visibly lag the head.
//
// Per gun this needs four measured numbers and nothing else (RSQ_ScopeTable), so a scope is a
// component and not a per-weapon special case. The railgun's mesh already carries its glass as
// its own surface ("ScopeGlass", 18 verts); the Ruger's ocular disc is carved out of the scope
// surface by the kit so it has one too.
//
// Everything here is inert until a gun is in the table, and out of VR nothing runs at all.

class RSQ_ScopeLayers abstract
{
	// 2112, NOT 2102: RSR.WELLMAG is 2102 (rsr/vreload.zs:24) -- the magazine at the well --
	// and RSR_Guns has RailGun at 6 and Sniper at 8, so both scoped guns already use that id
	// for their VR reload. One psprite id holds one caller; sharing it would have killed the
	// reload on exactly the two guns getting scopes. Taken in the pack: 2100-2111, 2120-2123,
	// 2130-2131, 2200-2203, 2210, 2300-2301. Free: 2112-2119, 2124-2129.
	const RETICLE = 2112;		// RSQ_GunSide, main controller: the collimated reticle
}

class RSQ_ScopeTable abstract
{
	// Measured at each gun's READY frame through the model chain (rgeo.py), centimetres in
	// the weapon controller's frame: F forward, L left, U up.
	//   lens    the centre of the glass
	//   axis    down the bore, unit
	//   radius  the glass, so the dot can be clipped to it instead of floating off the tube
	//   mag     magnification for REAL mode; the DOT never magnifies
	clearscope static int Index(Weapon w)
	{
		if (!w)
			return 0;
		Name n = w.GetClassName();
		if (n == 'RailGun')	return 1;
		if (n == 'Sniper')	return 2;
		return 0;
	}

	clearscope static Vector3 Lens(int i)
	{
		static const double f[] = { 0, -1.710, -0.300 };
		static const double l[] = { 0, -0.090,  0.250 };
		static const double u[] = { 0, 11.810,  9.240 };
		return i > 0 && i < f.Size() ? (f[i], l[i], u[i]) : (0, 0, 0);
	}

	clearscope static Vector3 Axis(int i)
	{
		static const double f[] = { 0, 0.9998, 1.0000 };
		static const double l[] = { 0, 0.0149, -0.0040 };
		static const double u[] = { 0, 0.0152, 0.0038 };
		return i > 0 && i < f.Size() ? (f[i], l[i], u[i]) : (1, 0, 0);
	}

	clearscope static double Radius(int i)
	{
		static const double v[] = { 0, 1.78, 1.35 };
		return i > 0 && i < v.Size() ? v[i] : 0;
	}

	clearscope static double Mag(int i)
	{
		static const double v[] = { 0, 5.0, 6.0 };
		return i > 0 && i < v.Size() ? v[i] : 1.0;
	}

	// the cvar that chooses this gun's mode: 0 dot, 1 real
	clearscope static Name ModeCVar(int i)
	{
		static const Name v[] = { 'none', 'rsq_scope_railgun', 'rsq_scope_sniper' };
		return i > 0 && i < v.Size() ? v[i] : 'none';
	}
}

class RSQ_Scope abstract
{
	// The hand's own axes, built from the Euler angles the renderer wrote this frame.
	// CLEARSCOPE, deliberately: nothing here calls a native: AttackAngle / AttackPitch /
	// AttackRoll are plain readable fields and the rest is trig. So the renderer hook (ui, per
	// frame) and the layer-state chooser (play, per tic) share ONE implementation instead of
	// the play side needing a second copy to decide whether to show the reticle at all. AttackDir() cannot be called from ui (it is a play method on Actor), but the
	// ANGLES are plain fields and ui may read play data -- so the basis is rebuilt here with
	// trig instead. AttackAngle is the world yaw MINUS 90 and AttackPitch is negated, which
	// is the engine's own convention (p_map.cpp adds the 90 back everywhere it uses them).
	// F11: RETURNS the three axes. An `out Vector3` parameter aborts the VM the first time it is
	// called (qzd17.3 vmexec.h:828-830, "REGT_ADDROF not implemented for vectors").
	clearscope static Vector3, Vector3, Vector3 Basis(PlayerPawn mo)
	{
		Vector3 fwd, right, up;
		double yaw = mo.AttackAngle + 90.0;
		double pit = -mo.AttackPitch;
		double rol = mo.AttackRoll;
		double cy = cos(yaw), sy = sin(yaw), cp = cos(pit), sp = sin(pit);
		fwd = (cp * cy, cp * sy, sp);
		Vector3 r0 = (-sy, cy, 0);
		// roll the right/up pair about the forward axis
		double cr = cos(rol), sr = sin(rol);
		Vector3 u0 = (fwd cross r0);
		right = r0 * cr + u0 * sr;
		up = (right cross fwd);
		return fwd, right, up;
	}

	// Where the eye is, in the hand's own frame, in centimetres. The view point is the pawn's
	// XY with the player's own view height, which in VR already tracks the headset.
	clearscope static Vector3 EyeInHandFrame(PlayerPawn mo)
	{
		let p = mo.player;
		if (!p)
			return (0, 0, 0);
		Vector3 eye = (mo.pos.x, mo.pos.y, p.viewz);
		Vector3 d = eye - mo.AttackPos;
		double ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		d.z *= ps;				// undo the vertical squash the hand transform applies
		double vu = 34.0;
		let cv = CVar.FindCVar('vr_vunits_per_meter');
		if (cv && cv.GetFloat() > 0)
			vu = cv.GetFloat();
		Vector3 f, r, u;
		[f, r, u] = Basis(mo);
		// map units -> cm in the hand frame
		return ((d dot f) * 100.0 / vu, -(d dot r) * 100.0 / vu, (d dot u) * 100.0 / vu);
	}

	// The collimated dot's position on the lens plane, in the hand frame, cm.
	// D = E + A * ((P - E) dot A), then clipped to the glass so it never leaves the tube.
	clearscope static Vector3, bool DotAt(PlayerPawn mo, int i)
	{
		Vector3 P = RSQ_ScopeTable.Lens(i);
		Vector3 A = RSQ_ScopeTable.Axis(i);
		double al = A.Length();
		if (al <= 0)
			return P, false;
		A = A / al;
		Vector3 E = EyeInHandFrame(mo);
		Vector3 D = E + A * ((P - E) dot A);
		// off the glass: the eye is not behind the sight, so show nothing rather than a dot
		// stuck to the rim
		Vector3 off = D - P;
		double rr = RSQ_ScopeTable.Radius(i);
		double side = (off - A * (off dot A)).Length();
		if (rr > 0 && side > rr)
			return D, false;
		// behind the glass (looking at the objective end) is not a sight picture either
		if (((P - E) dot A) <= 0)
			return D, false;
		return D, true;
	}

	// Play-callable: is there a sight picture at all this frame? The layer chooser uses this to
	// pick the Hidden state, instead of flinging the quad off-screen to make it disappear.
	clearscope static bool DotOk(PlayerPawn mo, int i)
	{
		if (!mo || !mo.player || i <= 0)
			return false;
		Vector3 d;
		bool ok;
		[d, ok] = DotAt(mo, i);
		return ok;
	}
}
