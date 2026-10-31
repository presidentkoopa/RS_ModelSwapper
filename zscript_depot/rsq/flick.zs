// RS VR flick reload (1.17, owner). With a GUN IN EACH HAND, snapping a gun's barrel down
// reloads THAT gun with BD22's own reload, and only that one. With one gun (off hand free or
// a fist) nothing here runs: VR reloading (rsr) has the gun as before.
//
// The flick is read from the barrel's elevation, which turning and walking do not change:
//   fast    the barrel drops FLICK_DEG within FLICK_TICS;
//   down    it ends at least DOWN_DEG below level;
//   once    it re-arms only after coming back above REARM_DEG.
// The gun must be in its ready loop (the engine's ready flag for that hand), so a flick never
// cuts into firing or a reload already running. rsq_flick 0 turns it off. Purist: off (BD22
// purist has no reloading).
class RSQ_Flick : EventHandler
{
	const FLICK_DEG = 45.0;		// degrees of drop...
	const FLICK_TICS = 4;		// ...within this many tics (about 400 degrees a second)
	const DOWN_DEG = -40.0;
	const REARM_DEG = -15.0;
	const HIST = 8;

	double el[MAXPLAYERS][2][HIST];
	int head[MAXPLAYERS][2];
	int count[MAXPLAYERS][2];
	bool armed[MAXPLAYERS][2];

	// the hand-held things that are not guns: they have no magazine to reload
	static bool IsGun(Weapon w)
	{
		if (!w || w is 'RSQ_Hands')
			return false;
		static const Name notGuns[] = { 'Melee_Attacks', 'BrutalAxe', 'Chain_saw', 'DSweap', 'HandGrenades' };
		for (int i = 0; i < notGuns.Size(); i++)
		{
			class<Actor> c = notGuns[i];
			if (c && w is c)
				return false;
		}
		return w.FindState("Reload") != null;
	}

	override void WorldTick()
	{
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo)
				continue;
			let mo = players[n].mo;
			let p = mo.player;
			bool live = RSVR_VRHand.InVR(mo) && p.playerstate == PST_LIVE && mo.health > 0
				&& RSQ.PlayerInt(mo, 'rsq_flick', 1) != 0 && mo.CountInv('IsPlayingAsPurist') == 0;
			bool on = live && IsGun(p.OffhandWeapon);	// 1.21: a gun in the off hand flicks, whatever the main hand holds
			// 2026-10-23: with ONE rifle the whole flick was off, so "flick down to reload both
			// barrels" (1.30) only ever worked while dual wielding -- and a lone rifle is the
			// common case. A single rifle now flicks for its LAUNCHER ONLY: the magazine stays
			// the hand reload's, exactly as the header says, and the flick gets the M203.
			bool loneM203 = live && !on && RSM.IsAnyRifle(p.ReadyWeapon);
			double ps = mo.Level.pixelstretch;
			if (ps <= 0)
				ps = 1.2;
			for (int h = 0; h < 2; h++)
			{
				// the main gun flicks only when the off hand has a gun too (one gun alone: VR reload)
				bool run = on && (h != 0 || IsGun(p.ReadyWeapon));
				bool m203Only = !run && h == 0 && loneM203;	// a lone rifle: the launcher only
				if (!run && !m203Only)
				{
					count[n][h] = 0;
					armed[n][h] = false;
					continue;
				}
				Vector3 d = h == 0 ? RSVR_VRHand.HandDir(mo, 0, 0, ps) : RSVR_VRHand.OffDir(mo, 0, 0, ps);
				double e = asin(clamp(d.z, -1, 1));
				head[n][h] = (head[n][h] + 1) % HIST;
				el[n][h][head[n][h]] = e;
				if (count[n][h] < HIST)
					count[n][h]++;
				if (e > REARM_DEG)
					armed[n][h] = true;
				if (!armed[n][h] || count[n][h] <= FLICK_TICS || e > DOWN_DEG)
					continue;
				double before = el[n][h][(head[n][h] - FLICK_TICS + HIST) % HIST];
				if (before - e < FLICK_DEG)
					continue;
				armed[n][h] = false;
				if (m203Only)
					RSM.FlickLoad(mo, false);	// the magazine stays the hand reload's
				else
					Reload(p, h);
			}
		}
	}

	static void Reload(PlayerInfo p, int h)
	{
		Weapon w = h == 0 ? p.ReadyWeapon : p.OffhandWeapon;
		int ready = h == 0 ? WF_WEAPONREADY : WF_OFFHANDREADY;
		if (!w || !(p.WeaponState & ready))
			return;
		State st = w.FindState("Reload");
		if (!st)
			return;
		p.SetPsprite(h == 0 ? PSP_WEAPON : PSP_OFFHANDWEAPON, st, false, w);
		// 1.30 (owner: "flick down to reload both barrels"): a rifle's empty M203 loads with it
		if (RSM.IsAnyRifle(w) && p.mo)
			RSM.FlickLoad(p.mo, h != 0);
	}
}
