// WMQ_Gun: the base of every weapon in this pack. Stock QuestZDoom 17.x, no engine changes.
// Fire comes from the set's own numbers (WMSHEET / the WM_Gun Default blocks); the VR reload is
// zscript/rsr (the tables rsr_guns.zs are generated from the REMA cards by genpack.py).
class WMQ_Gun : Weapon
{
	int capacity;
	String fireSound, drySound, magOutSound, magInSound, rackSound;
	property Capacity: capacity;
	property FireSound: fireSound;
	property DrySound: drySound;
	property MagOutSound: magOutSound;
	property MagInSound: magInSound;
	property RackSound: rackSound;

	Default
	{
		Weapon.Kickback 50;
		Weapon.BobStyle "Normal";
		+WEAPON.NOALERT
	}
}

// The punch (zscript/rsq/fists.zs lands one from the hand, the way the blow went): Doom's own
// fist numbers, 2 x 1d10, berserk x10. A short-lived projectile so it reaches about 32 units.
class WMQ_Punch : Actor
{
	Default
	{
		Projectile;
		+NOGRAVITY
		+FORCEXYBILLBOARD
		Radius 8;
		Height 8;
		Speed 16;
		DamageFunction (2 * random(1, 10));
		RenderStyle "None";
	}
	States
	{
	Spawn:
		TNT1 A 2;
		Stop;
	Death:
	XDeath:
		TNT1 A 1 A_StartSound("*fist", CHAN_WEAPON);
		Stop;
	}
}

class WMQ_PunchBerserk : WMQ_Punch
{
	Default
	{
		DamageFunction (20 * random(1, 10));
	}
}

class WMQ_Sprites : Actor
{
	States
	{
	Spawn:
		Q01S A 0;
		Q02S A 0;
		Q03S A 0;
		Q04S A 0;
		Q05S A 0;
		Q06S A 0;
		Q07S A 0;
		Q08S A 0;
		Q09S A 0;
		Q0AS A 0;
		Q01R A 0;
		Q01S A 0;
		Q02R A 0;
		Q02S A 0;
		Q03R A 0;
		Q03S A 0;
		Q04R A 0;
		Q04S A 0;
		Q05R A 0;
		Q05S A 0;
		Q06R A 0;
		Q06S A 0;
		Q07R A 0;
		Q07S A 0;
		Q08R A 0;
		Q08S A 0;
		Q09R A 0;
		Q09S A 0;
		Q0AR A 0;
		Q0AS A 0;
		Stop;
	}
}

class WMQ_Mag_WM_BreachGlock : Ammo { Default { Inventory.MaxAmount 17; Ammo.BackpackMaxAmount 17; +INVENTORY.IGNORESKILL } }

class WM_BreachGlock : WMQ_Gun replaces Pistol
{
	Default
	{
		Tag "Glock";
		Weapon.SlotNumber 2;
		Weapon.SelectionOrder 1900;
		Inventory.PickupMessage "Picked up the Glock";
		Weapon.AmmoType1 "WMQ_Mag_WM_BreachGlock";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 17;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 34;
		WMQ_Gun.Capacity 17;
		WMQ_Gun.FireSound "rsm/breachglock/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "rsm/breachglock/magout";
		WMQ_Gun.MagInSound "rsm/breachglock/magin";
		WMQ_Gun.RackSound "rsm/breachglock/slideback";
	}

	States
	{
	Spawn:
		Q01S A -1;
		Stop;
	Ready:
		Q01R A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q01R A 1 A_Lower(12);
		Loop;
	Select:
		Q01R A 1 A_Raise(12);
		Loop;
	Fire:
		Q01R A 0 A_JumpIfNoAmmo("Dry");
		Q01R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q01R A 6 A_FireBullets(3.0, 3.0, 1, 20, "BulletPuff", FBF_USEAMMO);
		Q01R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q01R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q01R A 8;
		Goto Ready;
	Reload:
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachGlock", 17, "Ready");
		Q01R A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q01R A 0 A_TakeInventory("RSR_Go", 1);
		Q01R A 0 A_GiveInventory("RSR_Start", 1);
		Q01R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q01R A 0 A_TakeInventory("RSR_Go", 1);
		Q01R A 0 A_JumpIfInventory("RSR_NoMag_WM_BreachGlock", 1, "RSR_Wait");	// no magazine in the gun
		Q01R A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q01R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachGlock", 1, "RSR_Unload1");
		Q01R A 0 A_GiveInventory("RSR_NoMag_WM_BreachGlock", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q01R A 0 A_TakeInventory("WMQ_Mag_WM_BreachGlock", 1);
		Q01R A 0 A_GiveInventory("RSR_Held_WM_BreachGlock", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q01R A 0 A_TakeInventory("RSR_Seated", 1);
		Q01R A 0 A_TakeInventory("RSR_NoMag_WM_BreachGlock", 1);
	RSR_Return:		// the held rounds first
		Q01R A 0 A_JumpIfInventory("RSR_Held_WM_BreachGlock", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q01R A 0 A_TakeInventory("RSR_Held_WM_BreachGlock", 1);
		Q01R A 0 A_GiveInventory("WMQ_Mag_WM_BreachGlock", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachGlock", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q01R A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachGlock", 17, "RSR_Filled");
		Q01R A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q01R A 0 A_GiveInventory("WMQ_Mag_WM_BreachGlock", 1);
		Q01R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q01R A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q01R A 0 A_TakeInventory("RSR_Done", 1);
		Q01R A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q01R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q01R A 10;
		Q01R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachGlock", 17, "RSR_StockDone");
		Q01R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q01R A 0 A_GiveInventory("WMQ_Mag_WM_BreachGlock", 1);
		Q01R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q01R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_BreachGlockS : Ammo { Default { Inventory.MaxAmount 17; Ammo.BackpackMaxAmount 17; +INVENTORY.IGNORESKILL } }

class WM_BreachGlockS : WMQ_Gun
{
	Default
	{
		Tag "Glock (suppressed)";
		Weapon.SlotNumber 2;
		Weapon.SelectionOrder 1900;
		Inventory.PickupMessage "Picked up the Glock (suppressed)";
		Weapon.AmmoType1 "WMQ_Mag_WM_BreachGlockS";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 17;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 34;
		WMQ_Gun.Capacity 17;
		WMQ_Gun.FireSound "rsm/breachglocks/fire";
		WMQ_Gun.DrySound "rsm/breach/click";
		WMQ_Gun.MagOutSound "rsm/breachglock/magout";
		WMQ_Gun.MagInSound "rsm/breachglock/magin";
		WMQ_Gun.RackSound "rsm/breachglock/slideback";
	}

	States
	{
	Spawn:
		Q02S A -1;
		Stop;
	Ready:
		Q02R A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q02R A 1 A_Lower(12);
		Loop;
	Select:
		Q02R A 1 A_Raise(12);
		Loop;
	Fire:
		Q02R A 0 A_JumpIfNoAmmo("Dry");
		Q02R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q02R A 6 A_FireBullets(3.0, 3.0, 1, 20, "BulletPuff", FBF_USEAMMO);
		Q02R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q02R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q02R A 8;
		Goto Ready;
	Reload:
		Q02R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachGlockS", 17, "Ready");
		Q02R A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q02R A 0 A_TakeInventory("RSR_Go", 1);
		Q02R A 0 A_GiveInventory("RSR_Start", 1);
		Q02R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q02R A 0 A_TakeInventory("RSR_Go", 1);
		Q02R A 0 A_JumpIfInventory("RSR_NoMag_WM_BreachGlockS", 1, "RSR_Wait");	// no magazine in the gun
		Q02R A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q02R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q02R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachGlockS", 1, "RSR_Unload1");
		Q02R A 0 A_GiveInventory("RSR_NoMag_WM_BreachGlockS", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q02R A 0 A_TakeInventory("WMQ_Mag_WM_BreachGlockS", 1);
		Q02R A 0 A_GiveInventory("RSR_Held_WM_BreachGlockS", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q02R A 0 A_TakeInventory("RSR_Seated", 1);
		Q02R A 0 A_TakeInventory("RSR_NoMag_WM_BreachGlockS", 1);
	RSR_Return:		// the held rounds first
		Q02R A 0 A_JumpIfInventory("RSR_Held_WM_BreachGlockS", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q02R A 0 A_TakeInventory("RSR_Held_WM_BreachGlockS", 1);
		Q02R A 0 A_GiveInventory("WMQ_Mag_WM_BreachGlockS", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q02R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachGlockS", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q02R A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q02R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachGlockS", 17, "RSR_Filled");
		Q02R A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q02R A 0 A_GiveInventory("WMQ_Mag_WM_BreachGlockS", 1);
		Q02R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q02R A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q02R A 0 A_TakeInventory("RSR_Done", 1);
		Q02R A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q02R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q02R A 10;
		Q02R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q02R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachGlockS", 17, "RSR_StockDone");
		Q02R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q02R A 0 A_GiveInventory("WMQ_Mag_WM_BreachGlockS", 1);
		Q02R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q02R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_BreachKimber : Ammo { Default { Inventory.MaxAmount 8; Ammo.BackpackMaxAmount 8; +INVENTORY.IGNORESKILL } }

class WM_BreachKimber : WMQ_Gun
{
	Default
	{
		Tag "BreachKimber";
		Weapon.SlotNumber 2;
		Weapon.SelectionOrder 1900;
		Inventory.PickupMessage "Picked up the BreachKimber";
		Weapon.AmmoType1 "WMQ_Mag_WM_BreachKimber";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 8;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 16;
		WMQ_Gun.Capacity 8;
		WMQ_Gun.FireSound "rsm/breachkimber/fire";
		WMQ_Gun.DrySound "rsm/breach/click";
		WMQ_Gun.MagOutSound "rsm/breach/clipout";
		WMQ_Gun.MagInSound "rsm/breach/clipin";
		WMQ_Gun.RackSound "rsm/breachglock/slideback";
	}

	States
	{
	Spawn:
		Q03S A -1;
		Stop;
	Ready:
		Q03R A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q03R A 1 A_Lower(12);
		Loop;
	Select:
		Q03R A 1 A_Raise(12);
		Loop;
	Fire:
		Q03R A 0 A_JumpIfNoAmmo("Dry");
		Q03R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q03R A 10 A_FireBullets(4.0, 2.0, 1, 5, "BulletPuff", FBF_USEAMMO);
		Q03R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q03R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q03R A 8;
		Goto Ready;
	Reload:
		Q03R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachKimber", 8, "Ready");
		Q03R A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q03R A 0 A_TakeInventory("RSR_Go", 1);
		Q03R A 0 A_GiveInventory("RSR_Start", 1);
		Q03R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q03R A 0 A_TakeInventory("RSR_Go", 1);
		Q03R A 0 A_JumpIfInventory("RSR_NoMag_WM_BreachKimber", 1, "RSR_Wait");	// no magazine in the gun
		Q03R A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q03R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q03R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachKimber", 1, "RSR_Unload1");
		Q03R A 0 A_GiveInventory("RSR_NoMag_WM_BreachKimber", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q03R A 0 A_TakeInventory("WMQ_Mag_WM_BreachKimber", 1);
		Q03R A 0 A_GiveInventory("RSR_Held_WM_BreachKimber", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q03R A 0 A_TakeInventory("RSR_Seated", 1);
		Q03R A 0 A_TakeInventory("RSR_NoMag_WM_BreachKimber", 1);
	RSR_Return:		// the held rounds first
		Q03R A 0 A_JumpIfInventory("RSR_Held_WM_BreachKimber", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q03R A 0 A_TakeInventory("RSR_Held_WM_BreachKimber", 1);
		Q03R A 0 A_GiveInventory("WMQ_Mag_WM_BreachKimber", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q03R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachKimber", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q03R A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q03R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachKimber", 8, "RSR_Filled");
		Q03R A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q03R A 0 A_GiveInventory("WMQ_Mag_WM_BreachKimber", 1);
		Q03R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q03R A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q03R A 0 A_TakeInventory("RSR_Done", 1);
		Q03R A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q03R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q03R A 10;
		Q03R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q03R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachKimber", 8, "RSR_StockDone");
		Q03R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q03R A 0 A_GiveInventory("WMQ_Mag_WM_BreachKimber", 1);
		Q03R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q03R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_BreachMK18 : Ammo { Default { Inventory.MaxAmount 30; Ammo.BackpackMaxAmount 30; +INVENTORY.IGNORESKILL } }

class WM_BreachMK18 : WMQ_Gun replaces Chaingun
{
	Default
	{
		Tag "BreachMK18";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 750;
		Inventory.PickupMessage "Picked up the BreachMK18";
		Weapon.AmmoType1 "WMQ_Mag_WM_BreachMK18";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 30;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 60;
		WMQ_Gun.Capacity 30;
		WMQ_Gun.FireSound "rsm/breachmk18/fire";
		WMQ_Gun.DrySound "rsm/breach/click";
		WMQ_Gun.MagOutSound "rsm/breach/clipout";
		WMQ_Gun.MagInSound "rsm/breach/clipin";
		WMQ_Gun.RackSound "rsm/breach/boltback";
	}

	States
	{
	Spawn:
		Q04S A -1;
		Stop;
	Ready:
		Q04R A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q04R A 1 A_Lower(12);
		Loop;
	Select:
		Q04R A 1 A_Raise(12);
		Loop;
	Fire:
		Q04R A 0 A_JumpIfNoAmmo("Dry");
		Q04R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q04R A 5 A_FireBullets(3.0, 1.5, 1, 8, "BulletPuff", FBF_USEAMMO);
		Q04R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q04R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q04R A 8;
		Goto Ready;
	Reload:
		Q04R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMK18", 30, "Ready");
		Q04R A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q04R A 0 A_TakeInventory("RSR_Go", 1);
		Q04R A 0 A_GiveInventory("RSR_Start", 1);
		Q04R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q04R A 0 A_TakeInventory("RSR_Go", 1);
		Q04R A 0 A_JumpIfInventory("RSR_NoMag_WM_BreachMK18", 1, "RSR_Wait");	// no magazine in the gun
		Q04R A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q04R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q04R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMK18", 1, "RSR_Unload1");
		Q04R A 0 A_GiveInventory("RSR_NoMag_WM_BreachMK18", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q04R A 0 A_TakeInventory("WMQ_Mag_WM_BreachMK18", 1);
		Q04R A 0 A_GiveInventory("RSR_Held_WM_BreachMK18", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q04R A 0 A_TakeInventory("RSR_Seated", 1);
		Q04R A 0 A_TakeInventory("RSR_NoMag_WM_BreachMK18", 1);
	RSR_Return:		// the held rounds first
		Q04R A 0 A_JumpIfInventory("RSR_Held_WM_BreachMK18", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q04R A 0 A_TakeInventory("RSR_Held_WM_BreachMK18", 1);
		Q04R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMK18", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q04R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMK18", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q04R A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q04R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMK18", 30, "RSR_Filled");
		Q04R A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q04R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMK18", 1);
		Q04R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q04R A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q04R A 0 A_TakeInventory("RSR_Done", 1);
		Q04R A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q04R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q04R A 10;
		Q04R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q04R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMK18", 30, "RSR_StockDone");
		Q04R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q04R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMK18", 1);
		Q04R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q04R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_BreachMK18S : Ammo { Default { Inventory.MaxAmount 30; Ammo.BackpackMaxAmount 30; +INVENTORY.IGNORESKILL } }

class WM_BreachMK18S : WMQ_Gun
{
	Default
	{
		Tag "BreachMK18S";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 750;
		Inventory.PickupMessage "Picked up the BreachMK18S";
		Weapon.AmmoType1 "WMQ_Mag_WM_BreachMK18S";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 30;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 60;
		WMQ_Gun.Capacity 30;
		WMQ_Gun.FireSound "rsm/breachmk18s/fire";
		WMQ_Gun.DrySound "rsm/breach/click";
		WMQ_Gun.MagOutSound "rsm/breach/clipout";
		WMQ_Gun.MagInSound "rsm/breach/clipin";
		WMQ_Gun.RackSound "rsm/breach/boltback";
	}

	States
	{
	Spawn:
		Q05S A -1;
		Stop;
	Ready:
		Q05R A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q05R A 1 A_Lower(12);
		Loop;
	Select:
		Q05R A 1 A_Raise(12);
		Loop;
	Fire:
		Q05R A 0 A_JumpIfNoAmmo("Dry");
		Q05R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q05R A 5 A_FireBullets(3.0, 1.5, 1, 8, "BulletPuff", FBF_USEAMMO);
		Q05R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q05R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q05R A 8;
		Goto Ready;
	Reload:
		Q05R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMK18S", 30, "Ready");
		Q05R A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q05R A 0 A_TakeInventory("RSR_Go", 1);
		Q05R A 0 A_GiveInventory("RSR_Start", 1);
		Q05R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q05R A 0 A_TakeInventory("RSR_Go", 1);
		Q05R A 0 A_JumpIfInventory("RSR_NoMag_WM_BreachMK18S", 1, "RSR_Wait");	// no magazine in the gun
		Q05R A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q05R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q05R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMK18S", 1, "RSR_Unload1");
		Q05R A 0 A_GiveInventory("RSR_NoMag_WM_BreachMK18S", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q05R A 0 A_TakeInventory("WMQ_Mag_WM_BreachMK18S", 1);
		Q05R A 0 A_GiveInventory("RSR_Held_WM_BreachMK18S", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q05R A 0 A_TakeInventory("RSR_Seated", 1);
		Q05R A 0 A_TakeInventory("RSR_NoMag_WM_BreachMK18S", 1);
	RSR_Return:		// the held rounds first
		Q05R A 0 A_JumpIfInventory("RSR_Held_WM_BreachMK18S", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q05R A 0 A_TakeInventory("RSR_Held_WM_BreachMK18S", 1);
		Q05R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMK18S", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q05R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMK18S", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q05R A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q05R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMK18S", 30, "RSR_Filled");
		Q05R A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q05R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMK18S", 1);
		Q05R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q05R A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q05R A 0 A_TakeInventory("RSR_Done", 1);
		Q05R A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q05R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q05R A 10;
		Q05R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q05R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMK18S", 30, "RSR_StockDone");
		Q05R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q05R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMK18S", 1);
		Q05R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q05R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_BreachHK416S : Ammo { Default { Inventory.MaxAmount 30; Ammo.BackpackMaxAmount 30; +INVENTORY.IGNORESKILL } }

class WM_BreachHK416S : WMQ_Gun
{
	Default
	{
		Tag "BreachHK416S";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 750;
		Inventory.PickupMessage "Picked up the BreachHK416S";
		Weapon.AmmoType1 "WMQ_Mag_WM_BreachHK416S";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 30;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 60;
		WMQ_Gun.Capacity 30;
		WMQ_Gun.FireSound "rsm/breachhk416s/fire";
		WMQ_Gun.DrySound "rsm/breach/click";
		WMQ_Gun.MagOutSound "rsm/breach/cmagout";
		WMQ_Gun.MagInSound "rsm/breach/cmagin";
		WMQ_Gun.RackSound "rsm/breach/boltback";
	}

	States
	{
	Spawn:
		Q06S A -1;
		Stop;
	Ready:
		Q06R A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q06R A 1 A_Lower(12);
		Loop;
	Select:
		Q06R A 1 A_Raise(12);
		Loop;
	Fire:
		Q06R A 0 A_JumpIfNoAmmo("Dry");
		Q06R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q06R A 5 A_FireBullets(3.0, 1.5, 1, 8, "BulletPuff", FBF_USEAMMO);
		Q06R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q06R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q06R A 8;
		Goto Ready;
	Reload:
		Q06R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachHK416S", 30, "Ready");
		Q06R A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q06R A 0 A_TakeInventory("RSR_Go", 1);
		Q06R A 0 A_GiveInventory("RSR_Start", 1);
		Q06R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q06R A 0 A_TakeInventory("RSR_Go", 1);
		Q06R A 0 A_JumpIfInventory("RSR_NoMag_WM_BreachHK416S", 1, "RSR_Wait");	// no magazine in the gun
		Q06R A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q06R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q06R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachHK416S", 1, "RSR_Unload1");
		Q06R A 0 A_GiveInventory("RSR_NoMag_WM_BreachHK416S", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q06R A 0 A_TakeInventory("WMQ_Mag_WM_BreachHK416S", 1);
		Q06R A 0 A_GiveInventory("RSR_Held_WM_BreachHK416S", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q06R A 0 A_TakeInventory("RSR_Seated", 1);
		Q06R A 0 A_TakeInventory("RSR_NoMag_WM_BreachHK416S", 1);
	RSR_Return:		// the held rounds first
		Q06R A 0 A_JumpIfInventory("RSR_Held_WM_BreachHK416S", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q06R A 0 A_TakeInventory("RSR_Held_WM_BreachHK416S", 1);
		Q06R A 0 A_GiveInventory("WMQ_Mag_WM_BreachHK416S", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q06R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachHK416S", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q06R A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q06R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachHK416S", 30, "RSR_Filled");
		Q06R A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q06R A 0 A_GiveInventory("WMQ_Mag_WM_BreachHK416S", 1);
		Q06R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q06R A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q06R A 0 A_TakeInventory("RSR_Done", 1);
		Q06R A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q06R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q06R A 10;
		Q06R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q06R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachHK416S", 30, "RSR_StockDone");
		Q06R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q06R A 0 A_GiveInventory("WMQ_Mag_WM_BreachHK416S", 1);
		Q06R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q06R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_BreachMCX : Ammo { Default { Inventory.MaxAmount 30; Ammo.BackpackMaxAmount 30; +INVENTORY.IGNORESKILL } }

class WM_BreachMCX : WMQ_Gun
{
	Default
	{
		Tag "BreachMCX";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 750;
		Inventory.PickupMessage "Picked up the BreachMCX";
		Weapon.AmmoType1 "WMQ_Mag_WM_BreachMCX";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 30;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 60;
		WMQ_Gun.Capacity 30;
		WMQ_Gun.FireSound "rsm/breachmcx/fire";
		WMQ_Gun.DrySound "rsm/breach/click";
		WMQ_Gun.MagOutSound "rsm/breach/cmagout";
		WMQ_Gun.MagInSound "rsm/breach/cmagin";
		WMQ_Gun.RackSound "rsm/breach/boltback";
	}

	States
	{
	Spawn:
		Q07S A -1;
		Stop;
	Ready:
		Q07R A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q07R A 1 A_Lower(12);
		Loop;
	Select:
		Q07R A 1 A_Raise(12);
		Loop;
	Fire:
		Q07R A 0 A_JumpIfNoAmmo("Dry");
		Q07R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q07R A 5 A_FireBullets(3.0, 1.5, 1, 8, "BulletPuff", FBF_USEAMMO);
		Q07R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q07R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q07R A 8;
		Goto Ready;
	Reload:
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMCX", 30, "Ready");
		Q07R A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q07R A 0 A_TakeInventory("RSR_Go", 1);
		Q07R A 0 A_GiveInventory("RSR_Start", 1);
		Q07R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q07R A 0 A_TakeInventory("RSR_Go", 1);
		Q07R A 0 A_JumpIfInventory("RSR_NoMag_WM_BreachMCX", 1, "RSR_Wait");	// no magazine in the gun
		Q07R A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q07R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMCX", 1, "RSR_Unload1");
		Q07R A 0 A_GiveInventory("RSR_NoMag_WM_BreachMCX", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q07R A 0 A_TakeInventory("WMQ_Mag_WM_BreachMCX", 1);
		Q07R A 0 A_GiveInventory("RSR_Held_WM_BreachMCX", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q07R A 0 A_TakeInventory("RSR_Seated", 1);
		Q07R A 0 A_TakeInventory("RSR_NoMag_WM_BreachMCX", 1);
	RSR_Return:		// the held rounds first
		Q07R A 0 A_JumpIfInventory("RSR_Held_WM_BreachMCX", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q07R A 0 A_TakeInventory("RSR_Held_WM_BreachMCX", 1);
		Q07R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMCX", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMCX", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q07R A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMCX", 30, "RSR_Filled");
		Q07R A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q07R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMCX", 1);
		Q07R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q07R A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q07R A 0 A_TakeInventory("RSR_Done", 1);
		Q07R A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q07R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q07R A 10;
		Q07R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMCX", 30, "RSR_StockDone");
		Q07R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q07R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMCX", 1);
		Q07R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q07R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_BreachG36C : Ammo { Default { Inventory.MaxAmount 30; Ammo.BackpackMaxAmount 30; +INVENTORY.IGNORESKILL } }

class WM_BreachG36C : WMQ_Gun
{
	Default
	{
		Tag "BreachG36C";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 750;
		Inventory.PickupMessage "Picked up the BreachG36C";
		Weapon.AmmoType1 "WMQ_Mag_WM_BreachG36C";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 30;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 60;
		WMQ_Gun.Capacity 30;
		WMQ_Gun.FireSound "rsm/breachg36c/fire";
		WMQ_Gun.DrySound "rsm/breach/click";
		WMQ_Gun.MagOutSound "rsm/breach/cmagout";
		WMQ_Gun.MagInSound "rsm/breach/cmagin";
		WMQ_Gun.RackSound "rsm/breach/boltback";
	}

	States
	{
	Spawn:
		Q08S A -1;
		Stop;
	Ready:
		Q08R A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q08R A 1 A_Lower(12);
		Loop;
	Select:
		Q08R A 1 A_Raise(12);
		Loop;
	Fire:
		Q08R A 0 A_JumpIfNoAmmo("Dry");
		Q08R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q08R A 5 A_FireBullets(3.0, 1.5, 1, 8, "BulletPuff", FBF_USEAMMO);
		Q08R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q08R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q08R A 8;
		Goto Ready;
	Reload:
		Q08R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachG36C", 30, "Ready");
		Q08R A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q08R A 0 A_TakeInventory("RSR_Go", 1);
		Q08R A 0 A_GiveInventory("RSR_Start", 1);
		Q08R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q08R A 0 A_TakeInventory("RSR_Go", 1);
		Q08R A 0 A_JumpIfInventory("RSR_NoMag_WM_BreachG36C", 1, "RSR_Wait");	// no magazine in the gun
		Q08R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q08R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachG36C", 1, "RSR_Unload1");
		Q08R A 0 A_GiveInventory("RSR_NoMag_WM_BreachG36C", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q08R A 0 A_TakeInventory("WMQ_Mag_WM_BreachG36C", 1);
		Q08R A 0 A_GiveInventory("RSR_Held_WM_BreachG36C", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q08R A 0 A_TakeInventory("RSR_Seated", 1);
		Q08R A 0 A_TakeInventory("RSR_NoMag_WM_BreachG36C", 1);
	RSR_Return:		// the held rounds first
		Q08R A 0 A_JumpIfInventory("RSR_Held_WM_BreachG36C", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q08R A 0 A_TakeInventory("RSR_Held_WM_BreachG36C", 1);
		Q08R A 0 A_GiveInventory("WMQ_Mag_WM_BreachG36C", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q08R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachG36C", 30, "RSR_Filled");
		Q08R A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q08R A 0 A_GiveInventory("WMQ_Mag_WM_BreachG36C", 1);
		Q08R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q08R A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q08R A 0 A_TakeInventory("RSR_Done", 1);
		Q08R A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q08R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q08R A 10;
		Q08R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q08R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachG36C", 30, "RSR_StockDone");
		Q08R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q08R A 0 A_GiveInventory("WMQ_Mag_WM_BreachG36C", 1);
		Q08R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q08R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_BreachMP5 : Ammo { Default { Inventory.MaxAmount 30; Ammo.BackpackMaxAmount 30; +INVENTORY.IGNORESKILL } }

class WM_BreachMP5 : WMQ_Gun
{
	Default
	{
		Tag "BreachMP5";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 800;
		Inventory.PickupMessage "Picked up the BreachMP5";
		Weapon.AmmoType1 "WMQ_Mag_WM_BreachMP5";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 30;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 60;
		WMQ_Gun.Capacity 30;
		WMQ_Gun.FireSound "rsm/breachmp5/fire";
		WMQ_Gun.DrySound "rsm/breach/click";
		WMQ_Gun.MagOutSound "rsm/breach/cmagout";
		WMQ_Gun.MagInSound "rsm/breach/cmagin";
		WMQ_Gun.RackSound "rsm/breach/boltback";
	}

	States
	{
	Spawn:
		Q09S A -1;
		Stop;
	Ready:
		Q09R A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q09R A 1 A_Lower(12);
		Loop;
	Select:
		Q09R A 1 A_Raise(12);
		Loop;
	Fire:
		Q09R A 0 A_JumpIfNoAmmo("Dry");
		Q09R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q09R A 4 A_FireBullets(5.6, 2.0, 1, 5, "BulletPuff", FBF_USEAMMO);
		Q09R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q09R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q09R A 8;
		Goto Ready;
	Reload:
		Q09R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMP5", 30, "Ready");
		Q09R A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q09R A 0 A_TakeInventory("RSR_Go", 1);
		Q09R A 0 A_GiveInventory("RSR_Start", 1);
		Q09R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q09R A 0 A_TakeInventory("RSR_Go", 1);
		Q09R A 0 A_JumpIfInventory("RSR_NoMag_WM_BreachMP5", 1, "RSR_Wait");	// no magazine in the gun
		Q09R A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q09R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q09R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMP5", 1, "RSR_Unload1");
		Q09R A 0 A_GiveInventory("RSR_NoMag_WM_BreachMP5", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q09R A 0 A_TakeInventory("WMQ_Mag_WM_BreachMP5", 1);
		Q09R A 0 A_GiveInventory("RSR_Held_WM_BreachMP5", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q09R A 0 A_TakeInventory("RSR_Seated", 1);
		Q09R A 0 A_TakeInventory("RSR_NoMag_WM_BreachMP5", 1);
	RSR_Return:		// the held rounds first
		Q09R A 0 A_JumpIfInventory("RSR_Held_WM_BreachMP5", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q09R A 0 A_TakeInventory("RSR_Held_WM_BreachMP5", 1);
		Q09R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMP5", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q09R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMP5", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q09R A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q09R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMP5", 30, "RSR_Filled");
		Q09R A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q09R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMP5", 1);
		Q09R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q09R A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q09R A 0 A_TakeInventory("RSR_Done", 1);
		Q09R A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q09R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q09R A 10;
		Q09R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q09R A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachMP5", 30, "RSR_StockDone");
		Q09R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q09R A 0 A_GiveInventory("WMQ_Mag_WM_BreachMP5", 1);
		Q09R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q09R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_BreachBenelli : Ammo { Default { Inventory.MaxAmount 7; Ammo.BackpackMaxAmount 7; +INVENTORY.IGNORESKILL } }

class WM_BreachBenelli : WMQ_Gun replaces Shotgun
{
	Default
	{
		Tag "BreachBenelli";
		Weapon.SlotNumber 3;
		Weapon.SelectionOrder 1300;
		Inventory.PickupMessage "Picked up the BreachBenelli";
		Weapon.AmmoType1 "WMQ_Mag_WM_BreachBenelli";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 7;
		Weapon.AmmoType2 "Shell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 14;
		WMQ_Gun.Capacity 7;
		WMQ_Gun.FireSound "rsm/breachbenelli/fire";
		WMQ_Gun.DrySound "rsm/breach/click";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0AS A -1;
		Stop;
	Ready:
		Q0AR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0AR A 1 A_Lower(12);
		Loop;
	Select:
		Q0AR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0AR A 0 A_JumpIfNoAmmo("Dry");
		Q0AR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0AR A 20 A_FireBullets(5.6, 0.0, 7, 5, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q0AR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0AR A 8;
		Goto Ready;
	Reload:
		Q0AR A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachBenelli", 7, "Ready");
		Q0AR A 0 A_JumpIfInventory("Shell", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0AR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0AR A 10;
		Q0AR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0AR A 0 A_JumpIfInventory("WMQ_Mag_WM_BreachBenelli", 7, "RSR_StockDone");
		Q0AR A 0 A_JumpIfInventory("Shell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0AR A 0 A_GiveInventory("WMQ_Mag_WM_BreachBenelli", 1);
		Q0AR A 0 A_TakeInventory("Shell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0AR A 8;
		Goto Ready;
	}
}
