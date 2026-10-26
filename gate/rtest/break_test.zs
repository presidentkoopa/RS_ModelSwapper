// TEST ONLY (ModelSwapper gate): the break-open reload's hand, by its own functions.
// rsbtest_script 1: while the gun is OPEN with an empty chamber and the hand free, seat that
// chamber (RSB_State.Seat, exactly what the hand's push home calls) one chamber per 20 tics;
// when none is empty, close it (RSB_State.StartClose, what the push shut or the flick calls).
// What this exercises: ModelSwapper taking a foreign gun into the break reload, the reload's
// cycle running on it (open, eject, load, close, its tokens and sounds), the hand-back, and the
// mod's own reload afterwards. What it does NOT: the hand's aim down a bore and its push --
// that geometry is BD22Q's own code and numbers, unchanged, and is a headset check.
class RSB_TestDriver : EventHandler
{
	int next;
	int lastPhase;
	int lastHand;
	int flickAt, flickDir, flickTries, flickAxis;
	int pressAt;

	// ON THE VR RIG (rsrtest_vr): a hand, not the reload's functions. Take a round at the belt
	// (grip, away from the chambers: the pouch rule), carry it to the first empty chamber's mouth
	// -- placed with the off hand's measured axes, the wrist turned until the reload's own angle
	// to the bore is in its limit -- push it home along the bore, let go; when all are loaded,
	// FLICK the gun hand (the right controller pitched ~60 degrees in 3 tics, the reload's closing
	// test: 450 deg/s about the hinge), the other way if the first does not close it.
	void Hand(PlayerPawn mo, RSB_State s, int now)
	{
		let d = RSR_TestDriver(EventHandler.Find('RSR_TestDriver'));
		if (!d)
			return;
		d.wristExternal = s.phase == RSB.OPEN || s.phase == RSB.OPENING;
		if (s.hand != lastHand)
		{
			Console.Printf("RSBT t%d hand %d -> %d", now, lastHand, s.hand);
			lastHand = s.hand;
			d.wy = d.wp = d.wr = 0; d.wStep = 0;
		}
		// the flick in progress: 20 degrees a tic for 3 tics, then back over 9
		if (flickAt > 0)
		{
			int f = now - flickAt;
			double a = f < 3 ? flickDir * 20.0 * (f + 1) : f < 12 ? flickDir * 60.0 * (1 - (f - 2) / 9.0) : 0;
			d.rPitch = flickAxis == 0 ? a : 0;
			d.rRoll = flickAxis == 1 ? a : 0;
			d.rYaw = flickAxis == 2 ? a : 0;
			if (f >= 30)
			{
				flickAt = 0;
				d.rPitch = d.rRoll = d.rYaw = 0;
			}
			return;
		}
		if (s.phase != RSB.OPEN)
		{
			d.grip = false;
			d.MoveTo((d.REST_F, d.REST_L, d.REST_U), 3);
			return;
		}
		int k = -1;
		for (int j = 0; j < s.nch; j++)
		{
			if (s.ch[j] == RSB.EMPTY)
			{
				k = j;
				break;
			}
		}
		if (k < 0)
		{
			// all loaded: let go, hand back to rest, flick to close
			d.grip = false;
			if (!d.MoveTo((d.REST_F, d.REST_L, d.REST_U), 3) || d.at < 10)
				return;
			// about the controller axis nearest the gun's hinge (pitch: across, roll: along the
			// bore -- a swing-out cylinder --, yaw: up), that axis first, both ways, then the others
			Vector3 ax = RSB_Guns.Axis(s.gun);
			int first = abs(ax.y) >= abs(ax.x) && abs(ax.y) >= abs(ax.z) ? 0 : abs(ax.x) >= abs(ax.z) ? 1 : 2;
			flickAxis = (first + flickTries / 2) % 3;
			flickDir = flickTries % 2 == 0 ? 1 : -1;
			flickTries++;
			flickAt = now;
			static const String nm[] = { "pitch", "roll", "yaw" };
			Console.Printf("RSBT t%d all chambers loaded: flick %s %s (try %d, hinge %.2f %.2f %.2f)", now, nm[flickAxis], flickDir > 0 ? "+" : "-", flickTries, ax.x, ax.y, ax.z);
			return;
		}
		// placed by FEEDBACK: the round's tip as the reload itself measures it (from the real
		// controller pose), and the hand moved by the error -- what an eye does
		Vector3 rb, rt;
		[rb, rt] = s.RoundInHand();
		Vector3 bore = s.BoreAt(k, s.theta);
		Vector3 home = s.TipAt(k, s.theta);
		double dep = s.Depth(k);
		switch (s.hand)
		{
		case RSB.FREE:
			d.grip = false;
			if (!d.MoveTo((-10, 28, -48), 3) || d.at < 4)		// the belt: away from the chambers
				return;
			pressAt = now;
			d.grip = true;		// the press takes a round
			break;
		case RSB.CARRY:
		{
			d.grip = true;
			double ss, side, ang;
			[ss, side, ang] = s.AtChamber(k);
			d.TurnWrist(ang);
			Vector3 mouth = home - bore * (dep + 2);		// the tip 2 cm out of the mouth, on the bore
			d.MoveTo(d.off + (mouth - rt), 2);
			break;
		}
		case RSB.INSERT:
			d.grip = true;
			d.MoveTo(d.off + (home + bore * 1.0 - rt), 1);			// pushed home along the bore
			break;
		}
	}

	override void WorldTick()
	{
		let mo = players[0].mo;
		if (!mo)
			return;
		let cv = CVar.FindCVar('rsbtest_script');
		if (!cv || cv.GetInt() <= 0)
			return;
		let s = RSB_Handler.StateOf(mo);
		if (!s)
			return;
		int now = Level.maptime;
		if (s.phase != lastPhase)
		{
			Console.Printf("RSBT t%d phase %d (gun %d, %d chambers)", now, s.phase, s.gun, s.nch);
			lastPhase = s.phase;
			next = now + 20;
		}
		if (RSR_TestDriver.VRT())
		{
			Hand(mo, s, now);
			return;
		}
		if (s.phase != RSB.OPEN || s.hand != RSB.FREE || now < next)
			return;
		next = now + 20;
		for (int k = 0; k < s.nch; k++)
		{
			if (s.ch[k] == RSB.EMPTY)
			{
				s.insCh = k;
				s.Seat(mo);
				Console.Printf("RSBT t%d seated chamber %d", now, k);
				return;
			}
		}
		Console.Printf("RSBT t%d all chambers loaded: closing", now);
		s.StartClose(mo);
	}
}
