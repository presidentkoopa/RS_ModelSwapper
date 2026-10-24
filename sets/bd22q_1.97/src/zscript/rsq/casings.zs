// 1.38 (owner): in VR the spent brass of the pistol, rifle, SMG and assault shotgun comes out of
// the gun's own ejection port (just above the firing hand), flicked out to the gun's right and up.
// BD22's own casings (PistolCasing, EmptyBrass, ShotgunCasing) are kept; only where they start and
// how they fly changes. Ports: cm in the weapon controller's frame (F L U), measured on each gun's
// ready frame (kitbash/ports.png).
// 1.97: and of the pump gun, the SSG, the Revolver and the Shotvolver. Those four are
// measured off the held mesh -- the surface the model-maker named, or the hole itself --
// NOT from WMCARD.bd22, whose ejectport every one of the 25 cards annotates "the point
// and the direction are estimates", and which misses all four of the ports above by
// between 0.8 and 10.8 cm. See tools/bd22_plus.py casings for the measurement and the
// four guns whose mesh has no port in it at all.
class RSA_Casings : EventHandler
{
	Array<Actor> pend;

	// (0, 0, 0): not one of ours. (This engine's VM cannot pass a Vector3 out by reference.)
	static Vector3 Port(Weapon w)
	{
		if (w is 'BrutalPistol')		return (-1.0, -1.0, 1.3);
		if (w is 'Rifle')				return (10.0, -0.6, 2.6);
		if (w is 'BrutalSMG')			return (14.0, -3.1, -1.0);
		if (w is 'AssaultShotgun')		return (16.0, -1.4, -0.6);
		if (w is 'Shot_Gun')			return (12.8, -1.5, 0.0);	// 1.97: the port the model-maker named `eject`
		if (w is 'SSG')					return (4.4, 0.0, 1.9);	// 1.97: the break-open breech, surface `Open`
		if (w is 'Revolver')			return (7.9, 0.0, 0.2);	// 1.97: the cylinder: the mean of its five `shells`
		if (w is 'Revolver2')			return (7.9, 0.0, 0.2);	// 1.97: the Shotvolver, on the Revolver's own mesh
		return (0, 0, 0);
	}

	// 1.97: not every gun THROWS. RSBDEFS calls brass_357 "dumped from a cylinder,
	// not thrown by a port: slow, no glow" and hull_12ga_magnum "dumped from an open
	// breech", so these fall out of the gun instead of being flicked clear of it.
	static bool Dumped(Weapon w)
	{
		if (w is 'SSG')
			return true;
		if (w is 'Revolver')
			return true;
		if (w is 'Revolver2')
			return true;
		return false;
	}

	// the player who fired: the casing's target (BD22's spawner hands its own on), or the spawner's
	static PlayerPawn Shooter(Actor c)
	{
		let t = c.target;
		if (PlayerPawn(t))
			return PlayerPawn(t);
		return t ? PlayerPawn(t.target) : null;
	}

	override void WorldThingSpawned(WorldEvent e)
	{
		let c = e.Thing;
		if (!c)
			return;
		Name n = c.GetClassName();
		if (n != 'PistolCasing' && n != 'EmptyBrass' && n != 'ShotgunCasing')
			return;
		let mo = Shooter(c);
		if (!mo || !mo.player || !RSVR_VRHand.InVR(mo))
			return;
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
		let p = mo.player;
		Vector3 hp = RSVR_VRHand.HandPos(mo), op = RSVR_VRHand.OffPos(mo);
		bool off = (c.pos - op).Length() < (c.pos - hp).Length() && p.OffhandWeapon && !(p.OffhandWeapon is 'RSQ_Hands');
		Weapon w = off ? p.OffhandWeapon : p.ReadyWeapon;
		Vector3 port = Port(w);
		if (port == (0, 0, 0))
			return;
		double ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		let cv = CVar.FindCVar('vr_vunits_per_meter');
		double vu = cv ? cv.GetFloat() : 34;
		if (vu <= 0)
			vu = 34;
		Vector3 F = off ? RSVR_VRHand.OffDir(mo, 0, 0, ps) : RSVR_VRHand.HandDir(mo, 0, 0, ps);
		Vector3 L = off ? RSVR_VRHand.OffDir(mo, 90, 0, ps) : RSVR_VRHand.HandDir(mo, 90, 0, ps);
		Vector3 U = off ? RSVR_VRHand.OffDir(mo, 0, 90, ps) : RSVR_VRHand.HandDir(mo, 0, 90, ps);
		Vector3 w3 = (F * port.x + L * port.y + U * port.z) * (vu / 100.0);
		w3.z /= ps;
		Vector3 pos = (off ? op : hp) + w3;
		// out to the right and up, a little back, as each gun's own casing speed --
		// except where the gun does not throw at all, and the cases just fall out.
		Vector3 d;
		double slow = 1.0;
		if (Dumped(w))
		{
			d = -U * frandom(0.8, 1.0) - F * frandom(0.1, 0.3) + L * frandom(-0.25, 0.25);
			slow = frandom(0.35, 0.5);
		}
		else
			d = -L * 0.75 + U * frandom(0.45, 0.7) - F * frandom(0.05, 0.25);
		d.z /= ps;
		d = d.Unit();
		double spd = c.vel.Length();
		if (spd < 1)
			spd = 4;
		c.SetOrigin(pos, false);
		c.vel = d * spd * slow + mo.vel;
		c.angle = atan2(d.y, d.x);
	}
}
