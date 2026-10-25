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
