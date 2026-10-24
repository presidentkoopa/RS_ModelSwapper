// rsr_guns.ms.zs -- the VR reload table for ModelSwapper's own models.
//
// Produced 2026-10-24 by the RSQ Weapon Depot's card pipeline:
//   tools/genpack.py <RS_VR_Weapons> <Quest_Weapons_Kit> <out> vanilla
// which reads the REMA cards (parts, axes, travel, grip, trigger, eject port,
// sounds, capacity), takes the surfaces from each mesh and the scale from the
// REMA MODELDEF, places the gun on the Quest controller, and feeds the kit's
// unmodified gen_rsr generator. Every position below is cm in the weapon
// controller's frame -- F forward, L left, U up.
//
// ONE function was changed by hand: Index(). See the comment on it.
// Regenerate the rest; never hand-edit it.
// Real VR reload: per gun. Positions cm in the weapon controller's frame (F, L, U);
// hooks are ModifyBobLayer3D translations for the gun's own MODELDEF placement.

class RSR_Guns abstract
{
	clearscope static int Count() { return 3; }

	// ===================================================================
	// RE-KEYED FOR MODELSWAPPER -- the ONE change to this generated file.
	//
	// Everything below this function is gen_rsr's own output, verbatim, from
	// the REMA cards and the meshes. Not one number was retyped.
	//
	// What was replaced: the generator emits its own weapon classes and keys
	// the table on their names (DoomPistol, DoomRocketLauncher, ...).
	// ModelSwapper has no classes of its own and never knows a foreign mod's
	// class names in advance, so that test can never match here.
	//
	// What it keys on instead: the MODEL the hand is wearing. ModelSwapper
	// already decides that and republishes it once per tic, and exposes it
	// through a Service -- the one lookup path with no compile-time link in
	// either direction, so nothing here names ModelSwapper and a miss is just
	// a null rather than a fatal load error. The card blocks carry the same
	// MS_ names as the models, so model -> card is the identity.
	//
	// Slots 1-3 are m4a3, rpg and plasmarifle: the three Doom-set guns whose
	// cards declare a feed part the generator can use. Pumps, break actions,
	// revolvers and melee fall through to slot 0 and get the mod's own reload,
	// which is correct until the pump and break tables are generated too.
	// ===================================================================
	clearscope static int Index(Weapon w)
	{
		if (!w) return 0;
		return SlotForDonor(DonorInHand(HandOf(w)));
	}

	// Which hand is holding this weapon: 0 main, 1 off.
	clearscope static int HandOf(Weapon w)
	{
		let pi = players[consolePlayer];
		if (pi && pi.OffhandWeapon == w) return 1;
		return 0;
	}

	// The model ModelSwapper has put in that hand, or "" if none / not loaded.
	clearscope static string DonorInHand(int hand)
	{
		let it = ServiceIterator.Find("RS_WeaponArchetypeService");
		if (!it) return "";
		let s = it.Next();
		if (!s) return "";
		return s.GetString("weapon.donor", "", hand);
	}

	// Model name -> slot. The card blocks are named after the models, so this
	// is a straight name match and nothing has to be kept in step by hand.
	clearscope static int SlotForDonor(string donor)
	{
		if (donor.Length() == 0) return 0;
		if (donor == "MS_AE_Pistol")     return 1;
		if (donor == "MS_RocketLauncher") return 2;
		if (donor == "MS_PlasmaRifle")   return 3;
		return 0;
	}

	// the magazine's top, seated
	clearscope static Vector3 Well(int i)
	{
		switch (i)
		{
		case 1:	return (-2.435, 0.015, -2.917);
		case 2:	return (-15.041, 3.112, 8.661);
		case 3:	return (9.030, 0.017, -9.693);
		}
		return (0, 0, 0);
	}

	// the way a magazine goes in
	clearscope static Vector3 Axis(int i)
	{
		switch (i)
		{
		case 1:	return (0.354, -0.000, 0.935);
		case 2:	return (-0.000, 0.944, -0.329);
		case 3:	return (-0.194, -0.000, 0.981);
		}
		return (0, 0, 0);
	}

	// seated -> the well's mouth, cm along the axis
	clearscope static double Mouth(int i)
	{
		switch (i)
		{
		case 1:	return 12.86;
		case 2:	return 22.07;
		case 3:	return 3.41;
		}
		return 0;
	}

	clearscope static double MagLen(int i)
	{
		switch (i)
		{
		case 1:	return 12.25;
		case 2:	return 22.64;
		case 3:	return 12.57;
		}
		return 0;
	}

	clearscope static Vector3 MagCentre(int i)
	{
		switch (i)
		{
		case 1:	return (-5.273, 0.015, -11.448);
		case 2:	return (-15.119, -8.038, 11.537);
		case 3:	return (15.423, 0.017, -14.510);
		}
		return (0, 0, 0);
	}

	// the magazine's top, in the off-hand frame
	clearscope static Vector3 TopInHand(int i)
	{
		switch (i)
		{
		case 1:	return (8.326, 3.900, 11.241);
		case 2:	return (-0.595, 28.056, -9.166);
		case 3:	return (-5.952, 4.103, 4.806);
		}
		return (0, 0, 0);
	}

	// layer 2201
	clearscope static Vector3 HandHook(int i)
	{
		switch (i)
		{
		case 1:	return (4.738, 17.266, -13.123);
		case 2:	return (24.944, -17.827, -14.446);
		case 3:	return (4.086, 14.499, 14.982);
		}
		return (0, 0, 0);
	}

	// layer 2102, per cm out
	clearscope static Vector3 WellHook(int i)
	{
		switch (i)
		{
		case 1:	return (0.000, -1.141, 0.432);
		case 2:	return (-0.944, 0.329, -0.000);
		case 3:	return (0.000, -0.981, -0.194);
		}
		return (0, 0, 0);
	}

	clearscope static bool HasHandle(int i)
	{
		switch (i)
		{
		case 1:	return true;
		case 2:	return false;
		case 3:	return false;
		}
		return false;
	}

	// the handle / slide / bolt the hand takes
	clearscope static Vector3 Grab(int i)
	{
		switch (i)
		{
		case 1:	return (-6.033, 0.072, 0.986);
		case 2:	return (0.000, 0.000, 0.000);
		case 3:	return (0.000, 0.000, 0.000);
		}
		return (0, 0, 0);
	}

	clearscope static Vector3 Pull(int i)
	{
		switch (i)
		{
		case 1:	return (-1.000, 0.000, 0.000);
		case 2:	return (-1.000, 0.000, 0.000);
		case 3:	return (-1.000, 0.000, 0.000);
		}
		return (0, 0, 0);
	}

	clearscope static double Travel(int i)
	{
		switch (i)
		{
		case 1:	return 5.67;
		case 2:	return 0.00;
		case 3:	return 0.00;
		}
		return 0;
	}

	// layer 2103, per cm back
	clearscope static Vector3 HandleHook(int i)
	{
		switch (i)
		{
		case 1:	return (0.000, 0.000, 1.220);
		case 2:	return (0.000, 0.000, 1.000);
		case 3:	return (0.000, 0.000, 1.000);
		}
		return (0, 0, 0);
	}

	clearscope static double BoltRatio(int i)
	{
		switch (i)
		{
		case 1:	return 0.000;
		case 2:	return 0.000;
		case 3:	return 0.000;
		}
		return 0;
	}

	clearscope static bool HandleLayers(int i)
	{
		switch (i)
		{
		case 1:	return true;
		case 2:	return false;
		case 3:	return false;
		}
		return false;
	}

	// the handle after a magazine: 0 never, 1 when the weapon gave ChargeToken (the set's own rule), 2 always
	clearscope static int ChargeRule(int i)
	{
		switch (i)
		{
		case 1:	return 1;
		case 2:	return 0;
		case 3:	return 0;
		}
		return 0;
	}

	clearscope static double BackAt(int i)
	{
		switch (i)
		{
		case 1:	return 0.85;
		case 2:	return 1.00;
		case 3:	return 1.00;
		}
		return 0;
	}

	// the set's own sound slot
	clearscope static int Channel(int i)
	{
		switch (i)
		{
		case 1:	return 5;
		case 2:	return 5;
		case 3:	return 5;
		}
		return 0;
	}

	clearscope static Vector3 Scale(int i)
	{
		switch (i)
		{
		case 1:	return (-0.820, 0.820, 0.820);
		case 2:	return (-1.000, 1.000, 1.000);
		case 3:	return (-1.000, 1.000, 1.000);
		}
		return (0, 0, 0);
	}

	// MODELDEF Offset x y, ZOffset
	clearscope static Vector3 Offset(int i)
	{
		switch (i)
		{
		case 1:	return (0.003, -29.061, -9.200);
		case 2:	return (3.289, -11.172, 4.149);
		case 3:	return (0.461, -58.378, -6.007);
		}
		return (0, 0, 0);
	}

	clearscope static Name SprGun(int i)
	{
		switch (i)
		{
		case 1:	return 'Q01M';
		case 2:	return 'Q05M';
		case 3:	return 'Q06M';
		}
		return 'None';
	}

	clearscope static Name SprPart(int i)
	{
		switch (i)
		{
		case 1:	return 'Q01P';
		case 2:	return 'Q05P';
		case 3:	return 'Q06P';
		}
		return 'None';
	}

	clearscope static Name SprWorld(int i)
	{
		switch (i)
		{
		case 1:	return 'Q01W';
		case 2:	return 'Q05W';
		case 3:	return 'Q06W';
		}
		return 'None';
	}

	clearscope static String ReadySprites(int i)
	{
		switch (i)
		{
		case 1:	return "Q01R A";
		case 2:	return "Q05R A";
		case 3:	return "Q06R A";
		}
		return "";
	}

	clearscope static String SndOut(int i)
	{
		switch (i)
		{
		case 1:	return "wm/m4a3/magout";
		case 2:	return "wm/rocket/rpg_magout";
		case 3:	return "wm/plasma/magout";
		}
		return "";
	}

	clearscope static String SndIn(int i)
	{
		switch (i)
		{
		case 1:	return "wm/m4a3/magin";
		case 2:	return "wm/rocket/rpg_magin";
		case 3:	return "wm/plasma/magin";
		}
		return "";
	}

	clearscope static String SndBack(int i)
	{
		switch (i)
		{
		case 1:	return "wm/m4a3/slideback";
		case 2:	return "";
		case 3:	return "";
		}
		return "";
	}

	clearscope static String SndFwd(int i)
	{
		switch (i)
		{
		case 1:	return "wm/m4a3/slidefwd";
		case 2:	return "";
		case 3:	return "";
		}
		return "";
	}

	clearscope static String SndLand(int i)
	{
		switch (i)
		{
		case 1:	return "wm/magdrop";
		case 2:	return "wm/magdrop/large";
		case 3:	return "wm/magdrop";
		}
		return "";
	}

	clearscope static String Reserve(int i)
	{
		switch (i)
		{
		case 1:	return "Clip";
		case 2:	return "RocketAmmo";
		case 3:	return "Cell";
		}
		return "";
	}

	clearscope static String MagAmmo(int i)
	{
		switch (i)
		{
		case 1:	return "WMQ_Mag_DoomPistol";
		case 2:	return "WMQ_Mag_DoomRocketLauncher";
		case 3:	return "WMQ_Mag_DoomPlasmaRifle";
		}
		return "";
	}

	clearscope static String NoMag(int i)
	{
		switch (i)
		{
		case 1:	return "RSR_NoMag_DoomPistol";
		case 2:	return "RSR_NoMag_DoomRocketLauncher";
		case 3:	return "RSR_NoMag_DoomPlasmaRifle";
		}
		return "";
	}

	clearscope static String ChargeToken(int i)
	{
		switch (i)
		{
		case 1:	return "RSR_Charge";
		case 2:	return "";
		case 3:	return "";
		}
		return "";
	}

	// '' = the engine's reload state
	clearscope static String ReloadToken(int i)
	{
		switch (i)
		{
		case 1:	return "";
		case 2:	return "";
		case 3:	return "";
		}
		return "";
	}

	// the gun's own frame (letter of SprGun) for a handle travel; 0 = its ready frame
	clearscope static int HandleFrame(int i, double t)
	{
		return 0;
	}

	// the action locks open on an empty gun (card holdopen, or genpack's default rule)
	clearscope static bool SlideLock(int i)
	{
		static const bool v[] = { false, true, false, false };
		return i > 0 && i < v.Size() && v[i];
	}
}

// every sprite the reload shows (MODELDEF.rsr), so the engine knows the names; never spawned
class RSR_GunSprites : Actor
{
	States
	{
	Spawn:
		Q01M AB 0;	// DoomPistol
		Q01P AB 0;
		Q01W A 0;
		Q05M A 0;	// DoomRocketLauncher
		Q05P A 0;
		Q05W A 0;
		Q06M A 0;	// DoomPlasmaRifle
		Q06P A 0;
		Q06W A 0;
		Stop;
	}
}

// the rounds of a magazine that was dropped, held until a magazine is home (the sets top up,
// so nothing is lost and the reserve's cap cannot eat them)
class RSR_Held_DoomPistol : Inventory { Default { Inventory.MaxAmount 999; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSR_Held_DoomRocketLauncher : Inventory { Default { Inventory.MaxAmount 999; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSR_Held_DoomPlasmaRifle : Inventory { Default { Inventory.MaxAmount 999; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
// "no magazine in the gun" for a set that has no such item of its own
class RSR_NoMag_DoomPistol : RSVR_Token {}
// "no magazine in the gun" for a set that has no such item of its own
class RSR_NoMag_DoomRocketLauncher : RSVR_Token {}
// "no magazine in the gun" for a set that has no such item of its own
class RSR_NoMag_DoomPlasmaRifle : RSVR_Token {}
