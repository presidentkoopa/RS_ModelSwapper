// BD 2.0 b1, from lane_c R6 (owner, 2026-10-27): in VR the Flamethrower2's flame starts at the DRAWN spout tip. BD22's fire states
// (brutal22test6 Flamethrower.dec, not ours to edit there) spawn FlamethrowerProjectileNew/New2/New3 at the
// controller (AttackPos, p_mobj.cpp OverrideAttackPosDir) plus BD22's own offsets; the drawn spout is ~95 cm ahead.
// This only MOVES where each flame projectile starts, once, the tic after it is spawned: timing, damage, speed and
// direction stay BD22's. If the spout position is blocked (inside a wall), the projectile is left where BD22 put it.
// Tip: the drawn spout tip in the weapon controller's frame, cm (F, L, U). BD 2.0 b1: recomputed for the r5 gun move
// (MODELDEF Offset -4.371 -8.313, ZOffset -5.669, Angle/Pitch/Roll -3.798 1.805 0.100): r6's own tip point on
// Flamethrower2.md3 (lane_c results/round6_final.json tip_gun) through the same chain reproduces r6's 88.39 -5.14 -1.42
// to 0.001 cm with r6's offsets, and gives 91.25 -2.94 -4.47 with r5's.
// r12 port (owner items 21 / 29, CLAUDE.md: "the flame starts at the drawn nozzle tip, and the nozzle is never tilted away from the
// stream"): the FlameCannon too. It is worn on the arm and moved to the hand (MODELDEF place from hands r4 fc_place.py), so its
// drawn nozzle is ~62 cm ahead of the controller and its barrel runs along the forearm, 6 deg below and 4 deg left of the
// controller's forward. Its flames (FlamethrowerProjectileNew: AltFire; BigFireBallWithGravity: Fire) and their sparks
// (Shotgunparticles2) start at the moved nozzle tip (tools/handfit/port/flamecannon_r12.py: the bore axis at the nozzle ring's front
// lip, moved with the gun; the same point as its RSQ_Muzzle row), and the flames fly along the drawn barrel (FCAX: the housing axis
// after the move, fc_place.json) at BD22's own speed. Sparks keep BD22's random spread.
class RSA_FlameSpout : EventHandler
{
	Array<Actor> pend;
	const TIPF = 91.25;
	const TIPL = -2.94;
	const TIPU = -4.47;
	const FCF = 61.92;	// r12: FlameCannon nozzle tip (F, L, U cm in the weapon controller's frame)
	const FCL = -5.02;
	const FCU = -14.53;
	const FCAXF = 0.99189;	// r12: FlameCannon barrel axis after the move (F, L, U)
	const FCAXL = -0.07220;
	const FCAXU = -0.10456;

	static PlayerPawn Shooter(Actor c)
	{
		return c ? PlayerPawn(c.target) : null;
	}

	override void WorldThingSpawned(WorldEvent e)
	{
		let c = e.Thing;
		if (!c)
			return;
		Name n = c.GetClassName();
		bool flame = n == 'FlamethrowerProjectileNew' || n == 'FlamethrowerProjectileNew2' || n == 'FlamethrowerProjectileNew3';
		if (!flame && n != 'BigFireBallWithGravity' && n != 'Shotgunparticles2')
			return;
		let mo = Shooter(c);
		if (!mo || !mo.player || !RSVR_VRHand.InVR(mo))
			return;
		let w = mo.player.ReadyWeapon;
		if ((w is 'Flamethrower2' && flame) || w is 'FlameCannon')
			pend.Push(c);
	}

	override void WorldTick()
	{
		for (int i = 0; i < pend.Size(); i++)
		{
			let c = pend[i];
			if (c)
				Place(c);
		}
		pend.Clear();
	}

	void Place(Actor c)
	{
		let mo = Shooter(c);
		if (!mo || !mo.player)
			return;
		double ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		let cv = CVar.FindCVar('vr_vunits_per_meter');
		double vu = cv ? cv.GetFloat() : 34;
		if (vu <= 0)
			vu = 34;
		Vector3 F = RSVR_VRHand.HandDir(mo, 0, 0, ps);
		Vector3 L = RSVR_VRHand.HandDir(mo, 90, 0, ps);
		Vector3 U = RSVR_VRHand.HandDir(mo, 0, 90, ps);
		bool fc = mo.player.ReadyWeapon is 'FlameCannon';
		Vector3 w3 = fc ? (F * FCF + L * FCL + U * FCU) * (vu / 100.0) : (F * TIPF + L * TIPL + U * TIPU) * (vu / 100.0);
		w3.z /= ps;
		Vector3 tip = RSVR_VRHand.HandPos(mo) + w3;
		Vector3 was = c.pos;
		Vector3 wasVel = c.vel;
		if (fc && c.GetClassName() != 'Shotgunparticles2')
		{
			// r12: along the drawn barrel, at BD22's speed (the nozzle is never tilted away from the stream)
			Vector3 ax = F * FCAXF + L * FCAXL + U * FCAXU;
			ax.z /= ps;
			if (ax.Length() > 0)
				c.vel = ax.Unit() * c.vel.Length();
		}
		Vector3 to = tip + c.vel * c.GetAge();
		c.SetOrigin(to, false);
		if (!c.TestMobjLocation())
		{
			c.SetOrigin(was, false);
			c.vel = wasVel;
		}
		let lg = CVar.FindCVar('lanec_flamelog');
		if (lg && lg.GetInt() != 0)
		{
			Vector3 back = c.pos - c.vel * c.GetAge();
			Vector3 bdstart = was - wasVel * c.GetAge();
			if (fc)
			{
				Vector3 d = c.vel.Length() > 0 ? c.vel.Unit() : (0, 0, 0);
				Vector3 b = F * FCAXF + L * FCAXL + U * FCAXU;
				b.z /= ps;
				Console.Printf("RSQ FC FLAME t %d %s age %d start-to-nozzle %.2f cm (BD22 start was %.1f cm from it) stream-to-barrel %.2f deg blocked %d", Level.maptime, c.GetClassName(), c.GetAge(), (back - tip).Length() * 100.0 / vu, (bdstart - tip).Length() * 100.0 / vu, b.Length() > 0 ? acos(clamp(d dot b.Unit(), -1, 1)) : -1, c.pos == was ? 1 : 0);
			}
			else
			Console.Printf("LANEC FLAME t %d %s age %d start-to-tip %.2f cm (BD22 start was %.1f cm from the tip) blocked %d", Level.maptime, c.GetClassName(), c.GetAge(), (back - tip).Length() * 100.0 / vu, (bdstart - tip).Length() * 100.0 / vu, c.pos == was ? 1 : 0);
		}
	}
}
