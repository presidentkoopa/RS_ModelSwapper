// muzzle.zs (r4, owner 2026-10-27: "Ruger 14 / sniper: the bullets leave from below the barrel,
// as if from the magazine").
//
// WHERE A VR SHOT STARTS. On QuestZDoom 17.3 every player hitscan and rail starts at AttackPos,
// the weapon CONTROLLER (hw_openxrdevice.cpp writes it each frame; p_map.cpp P_LineAttack and
// P_RailAttack read it). The controller is the grip. On the Ruger that is 62 cm behind the muzzle
// and 5 cm under the bore, so BD22's gray trail -- the one thing you see of the shot -- came out
// of the magazine. AttackPos is `native readonly`, and A_RailAttack has no forward offset (its
// side/up offsets are zeroed in VR unless use_action_spawn_yzoffset is set), so the shot is
// moved here, without touching the engine, by two stock routes:
//
//   HITSCANS  WorldHitscanPreFired cancels the engine's trace and fires the SAME one again with
//             LineAttack(LAF_ABSPOSITION): the start is an absolute point, the muzzle; the
//             direction is still the engine's own AttackDir (p_map.cpp: the VR branch sets it
//             whatever the position flags). Same angle, pitch, damage, puff, range, flags.
//   THE TRAIL BD22's "Trail effect only" rail (damage 0) is cancelled and drawn again by
//             Actor.RailAttack from a mount at the muzzle, aimed down the same AttackDir, with
//             the same FRailParams: colour, duration, sparsity, puff, everything.
//
// What is NOT moved: the Ruger's damaging rail (30, "Heavy penetration", colour None, so it draws
// nothing). Fired from a mount, its damage would be credited to the mount, not to you. It starts
// at the controller, parallel to the bore and 5 cm under it, as it always has.
//
// THE WALL GUARD. A muzzle can be through a wall the hand is not. Before anything moves, the
// line from the controller to the muzzle is traced; if it hits a wall, floor or ceiling the shot
// is left exactly as the engine fired it. You never shoot from the far side of a wall.
//
// Per gun: the muzzle, cm in the weapon controller's frame (F forward, L left, U up), measured
// off the held mesh through its MODELDEF chain (Depot tools/kit/rgeo.py to_flu).

class RSQ_MuzzleRail : Actor
{
	Default
	{
		+NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; +DONTSPLASH;
		Height 0; Radius 0; FloatSpeed 0;
		RenderStyle "None";
	}
	States { Spawn: TNT1 A 1; Stop; }
}

class RSQ_Muzzle : EventHandler
{
	bool busy;

	// (0, 0, 0): not moved.
	//   Sniper  XM21.md3 frame 0 (the only frame; X21G/X21F/P21F all show it), surface 9
	//           (trigger_safety_low.001_Cylinder.013, the body and barrel), MODELDEF.rsr Scale
	//           -10.485 10.485 10.485, Offset -0.2816 -44.5467, ZOffset -6.3157: the barrel's tip
	//           F 62.34, and the bore's centre L 0.28 U 5.03, the same from F 45 to the tip.
	static Vector3 Muzzle(Weapon w)
	{
		if (!w)
			return (0, 0, 0);
		Name n = w.GetClassName();
		if (n == 'Sniper')	return (68.38, 6.31, 9.77);	// r9 port: moved with the gun to the FBX hand (was 62.3, 0.3, 5.0)
		if (w is 'BrutalPistol')	return (23.3, 2.2, 6.3);	// BD 2.0 b1: BrutalPistol.md3 frame 3 slide face (F 15.18, bore U 0.10 at the 1.99 placement), moved with the gun to the FBX hand
		// hands b3: BrutalSMG.md3 frame 3, the front-most face (surface 1, F 35.07, L -1.02..1.02, U -5.74..-3.71 at the
		// 1.99 placement: the barrel end under the rail), its centre moved with the gun by batch 2's move (shift + pistol r5 move)
		if (w is 'BrutalSMG')	return (39.6, 4.4, 0.8);
		// moon-reload: rev.md3 frame 0, surface 3 (barrel and top strap), MODELDEF.rsqmoon placement. CONSTRUCTED:
		// no bore is modelled; the barrel is a box at the muzzle (face F 27.02-27.38, L -1.40..1.35, U 4.04..5.18):
		// its face's centre (reference/moonlight/bake_reload.txt "muzzle")
		if (n == 'BrutalRevolver')	return (35.03, 3.24, 8.51);	// batch 4: moved with the gun to the FBX hand (was 27.2, -0.03, 4.61)
		// batch 4: Rifle's drawn muzzle (front-most face centre of the ready frame, 65.80 0.49 2.57 before the move), moved with the gun
		if (w is 'Rifle')	return (71.18, 6.06, 11.42);
		// shotguns: AssaultShotgun's drawn muzzle (front-most face centre of the ready frame, 62.87 -0.13 -1.08 before the move), moved with the gun
		if (w is 'AssaultShotgun')	return (67.36, 11.02, -2.66);
		// batch 4: Revolver's drawn muzzle (front-most face centre of the ready frame, 21.54 -0.02 1.86 before the move), moved with the gun
		if (w is 'Revolver')	return (26.67, 2.61, 7.04);
		// shotguns: Shot_Gun's drawn muzzle (front-most face centre of the ready frame, 65.34 0.02 0.22 before the move), moved with the gun
		if (w is 'Shot_Gun')	return (69.20, 9.87, 1.83);
		// r9 port: GrenadeLauncher's drawn muzzle (front-most face centre of the ready frame, 46.39 0.00 1.16 before the move), moved with the gun
		if (w is 'GrenadeLauncher')	return (50.66, 9.86, -3.40);
		// r9 port: Rocket_Launcher's drawn muzzle (front-most face centre of the ready frame, 51.65 0.00 7.65 before the move), moved with the gun
		if (w is 'Rocket_Launcher')	return (55.59, 3.74, 17.94);
		// r9 port: RailGun's drawn muzzle (front-most face centre of the ready frame, 111.51 0.03 0.59 before the move), moved with the gun
		if (w is 'RailGun')	return (116.02, 10.31, 12.14);
		// r9 port: Plasma_Gun's drawn muzzle (front-most face centre of the ready frame, 72.10 0.07 -1.15 before the move), moved with the gun
		if (w is 'Plasma_Gun')	return (76.10, 8.12, 9.61);
		// r9 port: Minigun's drawn muzzle (front-most face centre of the ready frame, 95.92 0.35 -7.94 before the move), moved with the gun
		if (w is 'Minigun')	return (100.86, 11.49, 2.74);
		// r10 port: MG42's drawn muzzle (front-most face centre of the ready frame, 100.51 -0.15 1.86 before the move), moved with the gun
		if (w is 'MG42')	return (102.78, 8.98, 14.00);
		// r10 port: Machinegun's drawn muzzle (front-most face centre of the ready frame, 68.76 -0.04 4.77 before the move), moved with the gun
		if (w is 'Machinegun')	return (72.13, 6.28, 13.43);
		// r10 port: NukeLauncher's drawn muzzle (front-most face centre of the ready frame, 53.57 0.00 -2.87 before the move), moved with the gun
		if (w is 'NukeLauncher')	return (55.76, 6.04, 11.54);	// r12 port: moved with the re-fitted gun (was 55.74, 5.70, 11.67)
		// r10 port: BFG10k's drawn muzzle (front-most face centre of the ready frame, 88.00 0.01 -4.00 before the move), moved with the gun
		if (w is 'BFG10k')	return (90.36, 9.53, 7.73);	// r12 port: moved with the re-fitted gun (was 90.20, 9.05, 7.27)
		// r11 port: BIG_FUCKING_GUN's drawn muzzle (front-most face centre of the ready frame, 84.70 0.00 11.24 before the move), moved with the gun
		if (w is 'BIG_FUCKING_GUN')	return (86.71, 5.85, 21.97);
		// r11 port: IncendiaryLauncher's drawn muzzle (front-most face centre of the ready frame, 55.69 0.03 3.09 before the move), moved with the gun
		if (w is 'IncendiaryLauncher')	return (61.12, 11.16, 1.79);
		// r11 port: Devastator's drawn muzzle (front-most face centre of the ready frame, 64.79 0.02 13.59 before the move), moved with the gun
		if (w is 'Devastator')	return (66.55, 4.36, 21.68);
		// r11 port: SSG's drawn muzzle (front-most face centre of the ready frame, 36.84 0.04 1.12 before the move), moved with the gun
		if (w is 'SSG')	return (40.48, 8.12, -2.75);
		// r12 port: Unmaker's drawn muzzle (front-most face centre of the ready frame, 66.71 0.00 6.40 before the move), moved with the gun
		if (w is 'Unmaker')	return (72.53, 3.94, 17.03);
		// r12 port: HellishMissileLauncher's drawn muzzle (front-most face centre of the ready frame, 70.39 0.24 8.67 before the move), moved with the gun
		if (w is 'HellishMissileLauncher')	return (77.12, 1.68, 22.32);
		// r12 port: FlameCannon's drawn NOZZLE TIP (bore axis at the nozzle ring's front lip, 49.90 -0.31 -2.67 before the move; bore-face centre +8.06 cm along the housing axis), moved with the gun (fc_place)
		if (w is 'FlameCannon')	return (61.92, -5.02, -14.53);
		return (0, 0, 0);
	}

	// the muzzle in the world, or the controller itself when the guard says no
	static Vector3, bool Where(PlayerPawn mo)
	{
		Vector3 hp = RSVR_VRHand.HandPos(mo);
		if (!mo || !mo.player || !RSVR_VRHand.InVR(mo))
			return hp, false;
		Vector3 m = Muzzle(mo.player.ReadyWeapon);
		if (m == (0, 0, 0))
			return hp, false;
		double ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		let cv = CVar.FindCVar('vr_vunits_per_meter');
		double vu = cv ? cv.GetFloat() : 34;
		if (vu <= 0)
			vu = 34;
		// the same frame casings.zs places brass in
		Vector3 F = RSVR_VRHand.HandDir(mo, 0, 0, ps);
		Vector3 L = RSVR_VRHand.HandDir(mo, 90, 0, ps);
		Vector3 U = RSVR_VRHand.HandDir(mo, 0, 90, ps);
		Vector3 w3 = (F * m.x + L * m.y + U * m.z) * (vu / 100.0);
		w3.z /= ps;
		Vector3 at = hp + w3;
		// the wall guard
		double len = w3.Length();
		if (len > 0)
		{
			FLineTraceData tr;
			mo.LineTrace(VectorAngle(w3.x, w3.y), len, -asin(clamp(w3.z / len, -1, 1)),
				TRF_ABSPOSITION | TRF_THRUACTORS, hp.z, hp.x, hp.y, tr);
			if (tr.HitType != TRACE_HitNone)
				return hp, false;
		}
		return at, true;
	}

	override bool WorldHitscanPreFired(WorldEvent e)
	{
		let mo = PlayerPawn(e.Thing);
		if (busy || !mo || (e.AttackLineFlags & LAF_ISOFFHAND) || (e.AttackLineFlags & LAF_ABSPOSITION))
			return false;
		Vector3 at; bool ok;
		[at, ok] = Where(mo);
		if (!ok)
			return false;
		busy = true;
		mo.LineAttack(e.AttackAngle, e.AttackDistance, e.AttackPitch, e.Damage, e.DamageType, e.AttackPuffType,
			e.AttackLineFlags | LAF_ABSPOSITION, null, at.z, at.x, at.y);
		busy = false;
		return true;	// the engine's own trace, from the controller, is not run
	}

	override bool WorldRailgunPreFired(WorldEvent e)
	{
		let mo = PlayerPawn(e.Thing);
		if (busy || !mo || e.RailParams.damage != 0 || (e.RailParams.flags & RGF_ISOFFHAND))
			return false;	// only the trail-only rail: a damaging one stays the player's own
		Vector3 at; bool ok;
		[at, ok] = Where(mo);
		if (!ok)
			return false;
		let r = Actor.Spawn('RSQ_MuzzleRail', at);
		if (!r)
			return false;
		// the engine's own direction for this rail (p_map.cpp P_RailAttack, VR branch)
		// 2026-10-27: AttackDir only while live (see rsvr/vrhand.zs); else the event's own angles
		Vector3 ap = mo.OverrideAttackPosDir ? mo.AttackDir(mo, e.AttackAngle, e.AttackPitch)
			: (e.AttackAngle, e.AttackPitch, 0);
		r.angle = ap.x;
		r.pitch = ap.y;
		r.target = mo;
		FRailParams p;
		p.damage = e.RailParams.damage;
		p.offset_xy = 0;
		p.offset_z = 0;
		p.color1 = e.RailParams.color1;
		p.color2 = e.RailParams.color2;
		p.maxdiff = e.RailParams.maxdiff;
		p.flags = (e.RailParams.flags | RGF_CENTERZ) & ~RGF_ISOFFHAND;	// CENTERZ: start at the mount, not at an attack height
		p.puff = e.RailParams.puff;
		p.angleoffset = 0;
		p.pitchoffset = 0;
		p.distance = e.RailParams.distance;
		p.duration = e.RailParams.duration;
		p.sparsity = e.RailParams.sparsity;
		p.drift = e.RailParams.drift;
		p.spawnclass = e.RailParams.spawnclass;
		p.SpiralOffset = e.RailParams.SpiralOffset;
		p.limit = e.RailParams.limit;
		busy = true;
		r.RailAttack(p);
		busy = false;
		r.Destroy();
		return true;	// the engine's trail, from the controller, is not drawn
	}
}
