// RSRL: Rusted Legacy hand reloads (RSQ Weapon Depot, step S4)
//
// Ermac's immersive reload walks each gun through steps; every step waits in a gate
// (A_CheckImmersiveReloadActionN) that tests whether the off hand is within 2-3 units of a point.
// In VR, with rsrl_handreload on, each gate asks Gate() here instead, and only when the hand has
// really done the job calls his own setReloadStep(...) with his own arguments:
//   insert row: the piece drawn in the off hand (his ammo_hand pieces) is captured in a cylinder
//               about the measured seat axis, square to it, and pushed home along it
//   stroke row: the empty off hand grabs the measured part (slide, pump, barrel, lever, lid) and
//               moves it along the measured axis far enough (and back again, for the pump)
// Every number is in rsrl_table.zs, generated from the measured cards by tools/gen_rsrl.py.
// The frame maths is BD22's (sets/bd22q/src/zscript/rsvr/vrhand.zs HandDir / OffDir, rsq/muzzle.zs).

class RSRL_Row play
{
	int id, kind;		// kind 0 insert, 1 stroke
	string name;
	Vector3 seat, axis, inHand, inAxis, seatAxis;
	double len;
	Vector3 grab, dir;
	double need;
	int ret;
}

class RSRL_Track : Inventory
{
	int rowId;
	int phase;
	int lastTic;
	Vector3 start;
	RSRL_Row row;

	Default
	{
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		Inventory.MaxAmount 1;
	}
}

class RSRL_Reload play
{
	// BD22 RSR tolerances (rsr/vreload.zs), cm and degrees
	const ENTER_SIDE = 3.5;
	const LEAVE_SIDE = 5.5;
	const ENTER_ANGLE = 40.0;
	const LEAVE_ANGLE = 55.0;
	const MOUTH_REACH = 6.0;	// how far out along the axis a piece can be captured, beyond the stroke
	const SEAT = 1.0;			// home: within this of the seat along the axis
	const GRAB = 7.0;
	const OFF_LINE = 6.0;		// a stroke hand may leave the part's line by this much

	static bool On(Weapon w)
	{
		if (!w || !w.owner || !w.owner.player)
			return false;
		let mo = w.owner.player.mo;
		if (!mo || !mo.OverrideAttackPosDir)
			return false;
		let cv = CVar.GetCVar('rsrl_handreload', w.owner.player);
		return cv && cv.GetInt() != 0;
	}

	static int Debug(PlayerInfo p)
	{
		let cv = CVar.GetCVar('rsrl_debug', p);
		return cv ? cv.GetInt() : 0;
	}

	// a unit direction in a controller's frame (yaw 0 pitch 0 forward, yaw 90 left, pitch 90 up),
	// with the vertical squash taken out: BD22 RSVR_VRHand.HandDir / OffDir
	static Vector3 Dir(PlayerPawn mo, bool off, double yaw, double pitch, double ps)
	{
		Vector3 ap = off ? mo.OffhandDir(mo, mo.angle + yaw, mo.pitch + pitch)
			: mo.AttackDir(mo, mo.angle + yaw, mo.pitch + pitch);
		double cp = cos(ap.y);
		Vector3 v = (cp * cos(ap.x), cp * sin(ap.x), -sin(ap.y) * ps);
		double l = v.Length();
		return l > 0 ? v / l : (1, 0, 0);
	}

	// the gun's controller and the other one; his left-handed mode swaps them
	static Vector3 Ctl(PlayerPawn mo, bool off)
	{
		return off ? mo.OffhandPos : mo.AttackPos;
	}

	static double Ps(PlayerPawn mo)
	{
		double ps = mo.Level.pixelstretch;
		return ps > 0 ? ps : 1.2;
	}

	static double Vu()
	{
		let cv = CVar.FindCVar('vr_vunits_per_meter');
		double vu = cv ? cv.GetFloat() : 34;
		return vu > 0 ? vu : 34;
	}

	// returns done, and where the marker goes (world)
	static bool, Vector3 Gate(Weapon w, int id, bool hasPiece)
	{
		let mo = w.owner.player.mo;
		let t = RSRL_Track(mo.FindInventory('RSRL_Track'));
		if (!t)
		{
			mo.GiveInventory('RSRL_Track', 1);
			t = RSRL_Track(mo.FindInventory('RSRL_Track'));
		}
		int dbg = Debug(mo.player);
		if (!t.row || t.rowId != id || Level.maptime - t.lastTic > 5)
		{
			t.row = Row(id);
			t.rowId = id;
			t.phase = 0;
			if (dbg && t.row)
				Console.Printf("RSRL %s: waiting", t.row.name);
		}
		t.lastTic = Level.maptime;
		let r = t.row;
		Vector3 here = mo.pos + (0, 0, mo.height / 2);
		if (!r)
			return false, here;

		bool goff = w.bOffhandWeapon;
		double ps = Ps(mo);
		double vu = Vu();
		Vector3 gp = Ctl(mo, goff);
		Vector3 gF = Dir(mo, goff, 0, 0, ps), gL = Dir(mo, goff, 90, 0, ps), gU = Dir(mo, goff, 0, 90, ps);
		Vector3 hp = Ctl(mo, !goff);
		Vector3 hF = Dir(mo, !goff, 0, 0, ps), hL = Dir(mo, !goff, 90, 0, ps), hU = Dir(mo, !goff, 0, 90, ps);

		// a point in the off hand's frame (cm), in the gun's frame (cm)
		Vector3 pt = r.kind == 0 ? r.inHand : Palm();
		Vector3 wm = (hF * pt.x + hL * pt.y + hU * pt.z);	// metric offset from the off controller, cm
		Vector3 d = (hp - gp);
		d.z *= ps;
		d *= 100.0 / vu;
		d += wm;
		Vector3 p = (d dot gF, d dot gL, d dot gU);

		// the marker: the mouth of the seat, or the part to grab
		Vector3 tgt = r.kind == 0 ? r.seat - r.axis * r.len : r.grab;
		Vector3 mw = (gF * tgt.x + gL * tgt.y + gU * tgt.z) * (vu / 100.0);
		mw.z /= ps;
		Vector3 marker = gp + mw;

		if (r.kind == 0)
		{
			Vector3 ia = hF * r.inAxis.x + hL * r.inAxis.y + hU * r.inAxis.z;
			Vector3 pa = (ia dot gF, ia dot gL, ia dot gU);
			double tilt = acos(clamp(abs(pa dot r.seatAxis), 0, 1));
			Vector3 dv = p - r.seat;
			double along = dv dot r.axis;
			double a = -along;							// still to go
			double side = (dv - r.axis * along).Length();
			if (dbg > 1 && !(Level.maptime % 7))
				Console.Printf("RSRL %s: piece %.1f %.1f %.1f  to go %.2f side %.2f tilt %.1f phase %d", r.name, p.x, p.y, p.z, a, side, tilt, t.phase);
			if (t.phase == 0)
			{
				if (hasPiece && side <= ENTER_SIDE && a >= -1 && a <= r.len + MOUTH_REACH && tilt <= ENTER_ANGLE)
				{
					t.phase = 1;
					if (dbg)
						Console.Printf("RSRL %s: captured (to go %.2f side %.2f tilt %.1f)", r.name, a, side, tilt);
				}
			}
			else
			{
				if (side > LEAVE_SIDE || a > r.len + MOUTH_REACH + 2 || tilt > LEAVE_ANGLE)
				{
					t.phase = 0;
					if (dbg)
						Console.Printf("RSRL %s: lost (to go %.2f side %.2f tilt %.1f)", r.name, a, side, tilt);
				}
				else if (a <= SEAT)
				{
					if (dbg)
						Console.Printf("RSRL %s: SEATED (side %.2f tilt %.1f)", r.name, side, tilt);
					t.row = null;
					return true, marker;
				}
			}
			return false, marker;
		}

		// stroke
		if (t.phase == 0)
		{
			double g = (p - r.grab).Length();
			if (dbg > 1 && !(Level.maptime % 7))
				Console.Printf("RSRL %s: palm %.1f %.1f %.1f  grab dist %.2f", r.name, p.x, p.y, p.z, g);
			if (g <= GRAB)
			{
				t.phase = 1;
				t.start = p;
				if (dbg)
					Console.Printf("RSRL %s: grabbed (%.2f from the part)", r.name, g);
			}
			return false, marker;
		}
		Vector3 m = p - t.start;
		double prog = m dot r.dir;
		double offl = (m - r.dir * prog).Length();
		if (dbg > 1 && !(Level.maptime % 7))
			Console.Printf("RSRL %s: moved %.2f of %.2f, off line %.2f phase %d", r.name, prog, r.need, offl, t.phase);
		if (offl > OFF_LINE || prog < -3)
		{
			t.phase = 0;
			if (dbg)
				Console.Printf("RSRL %s: let go (moved %.2f off line %.2f)", r.name, prog, offl);
			return false, marker;
		}
		if (t.phase == 1 && prog >= r.need)
		{
			if (!r.ret)
			{
				if (dbg)
					Console.Printf("RSRL %s: DONE (moved %.2f of %.2f)", r.name, prog, r.need);
				t.row = null;
				return true, marker;
			}
			t.phase = 2;
			if (dbg)
				Console.Printf("RSRL %s: back (moved %.2f), now return", r.name, prog);
		}
		else if (t.phase == 2 && prog <= r.need * 0.3)
		{
			if (dbg)
				Console.Printf("RSRL %s: DONE (returned to %.2f)", r.name, prog);
			t.row = null;
			return true, marker;
		}
		return false, marker;
	}
}
