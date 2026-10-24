// 1.38 (owner): in VR the spent brass of the pistol, rifle, SMG and assault shotgun comes out of
// the gun's own ejection port (just above the firing hand), flicked out to the gun's right and up.
// BD22's own casings (PistolCasing, EmptyBrass, ShotgunCasing) are kept; only where they start and
// how they fly changes. Ports: cm in the weapon controller's frame (F L U), measured on each gun's
// ready frame (kitbash/ports.png).
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
		return (0, 0, 0);
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
		// out to the right and up, a little back, as each gun's own casing speed
		Vector3 d = -L * 0.75 + U * frandom(0.45, 0.7) - F * frandom(0.05, 0.25);
		d.z /= ps;
		d = d.Unit();
		double spd = c.vel.Length();
		if (spd < 1)
			spd = 4;
		c.SetOrigin(pos, false);
		c.vel = d * spd + mo.vel;
		c.angle = atan2(d.y, d.x);
	}
}
