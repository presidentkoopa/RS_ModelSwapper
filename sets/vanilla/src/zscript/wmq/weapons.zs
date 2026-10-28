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
		Stop;
	}
}

class WMQ_Mag_DoomPistol : Ammo { Default { Inventory.MaxAmount 15; Ammo.BackpackMaxAmount 15; +INVENTORY.IGNORESKILL } }

class DoomPistol : WMQ_Gun replaces Pistol
{
	Default
	{
		Tag "Pistol";
		Weapon.SlotNumber 2;
		Weapon.SelectionOrder 1900;
		Inventory.PickupMessage "Picked up the Pistol";
		Weapon.AmmoType1 "WMQ_Mag_DoomPistol";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 15;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 30;
		WMQ_Gun.Capacity 15;
		WMQ_Gun.FireSound "wm/m4a3/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/m4a3/magout";
		WMQ_Gun.MagInSound "wm/m4a3/magin";
		WMQ_Gun.RackSound "wm/m4a3/slideback";
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
		Q01R A 10 A_FireBullets(5.6, 0.0, 1, 5, "BulletPuff", FBF_USEAMMO);
		Q01R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q01R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q01R A 8;
		Goto Ready;
	Reload:
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_DoomPistol", 15, "Ready");
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
		Q01R A 0 A_JumpIfInventory("RSR_NoMag_DoomPistol", 1, "RSR_Wait");	// no magazine in the gun
		Q01R A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q01R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_DoomPistol", 1, "RSR_Unload1");
		Q01R A 0 A_GiveInventory("RSR_NoMag_DoomPistol", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q01R A 0 A_TakeInventory("WMQ_Mag_DoomPistol", 1);
		Q01R A 0 A_GiveInventory("RSR_Held_DoomPistol", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q01R A 0 A_TakeInventory("RSR_Seated", 1);
		Q01R A 0 A_TakeInventory("RSR_NoMag_DoomPistol", 1);
	RSR_Return:		// the held rounds first
		Q01R A 0 A_JumpIfInventory("RSR_Held_DoomPistol", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q01R A 0 A_TakeInventory("RSR_Held_DoomPistol", 1);
		Q01R A 0 A_GiveInventory("WMQ_Mag_DoomPistol", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_DoomPistol", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q01R A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_DoomPistol", 15, "RSR_Filled");
		Q01R A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q01R A 0 A_GiveInventory("WMQ_Mag_DoomPistol", 1);
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
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_DoomPistol", 15, "RSR_StockDone");
		Q01R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q01R A 0 A_GiveInventory("WMQ_Mag_DoomPistol", 1);
		Q01R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q01R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_DoomShotgun : Ammo { Default { Inventory.MaxAmount 8; Ammo.BackpackMaxAmount 8; +INVENTORY.IGNORESKILL } }

class DoomShotgun : WMQ_Gun replaces Shotgun
{
	Default
	{
		Tag "Shotgun";
		Weapon.SlotNumber 3;
		Weapon.SelectionOrder 1300;
		Inventory.PickupMessage "Picked up the Shotgun";
		Weapon.AmmoType1 "WMQ_Mag_DoomShotgun";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 8;
		Weapon.AmmoType2 "Shell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 16;
		WMQ_Gun.Capacity 8;
		WMQ_Gun.FireSound "weapons/shotgf";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
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
		Q02R A 37 A_FireBullets(5.6, 0.0, 7, 5, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q02R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q02R A 8;
		Goto Ready;
	Reload:
		Q02R A 0 A_JumpIfInventory("WMQ_Mag_DoomShotgun", 8, "Ready");
		Q02R A 0 A_JumpIfInventory("Shell", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q02R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q02R A 10;
		Q02R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q02R A 0 A_JumpIfInventory("WMQ_Mag_DoomShotgun", 8, "RSR_StockDone");
		Q02R A 0 A_JumpIfInventory("Shell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q02R A 0 A_GiveInventory("WMQ_Mag_DoomShotgun", 1);
		Q02R A 0 A_TakeInventory("Shell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q02R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_DoomSuperShotgun : Ammo { Default { Inventory.MaxAmount 2; Ammo.BackpackMaxAmount 2; +INVENTORY.IGNORESKILL } }

class DoomSuperShotgun : WMQ_Gun replaces SuperShotgun
{
	Default
	{
		Tag "Super Shotgun";
		Weapon.SlotNumber 3;
		Weapon.SelectionOrder 400;
		Inventory.PickupMessage "Picked up the Super Shotgun";
		Weapon.AmmoType1 "WMQ_Mag_DoomSuperShotgun";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 2;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 4;
		WMQ_Gun.Capacity 2;
		WMQ_Gun.FireSound "weapons/sshotf";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
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
		Q03R A 53 A_FireBullets(11.2, 7.1, 20, 5, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q03R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q03R A 8;
		Goto Ready;
	Reload:
		Q03R A 0 A_JumpIfInventory("WMQ_Mag_DoomSuperShotgun", 2, "Ready");
		Q03R A 0 A_JumpIfInventory("Clip", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q03R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q03R A 10;
		Q03R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q03R A 0 A_JumpIfInventory("WMQ_Mag_DoomSuperShotgun", 2, "RSR_StockDone");
		Q03R A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q03R A 0 A_GiveInventory("WMQ_Mag_DoomSuperShotgun", 1);
		Q03R A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q03R A 8;
		Goto Ready;
	}
}

class DoomChaingun : WMQ_Gun replaces Chaingun
{
	Default
	{
		Tag "Chaingun";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 700;
		Inventory.PickupMessage "Picked up the Chaingun";
		Weapon.AmmoType1 "Clip";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 20;
		WMQ_Gun.FireSound "wm/chaingun/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
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
		Q04R A 4 A_FireBullets(5.6, 0.0, 1, 5, "BulletPuff", FBF_USEAMMO);
		Q04R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q04R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q04R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_DoomRocketLauncher : Ammo { Default { Inventory.MaxAmount 7; Ammo.BackpackMaxAmount 7; +INVENTORY.IGNORESKILL } }

class DoomRocketLauncher : WMQ_Gun replaces RocketLauncher
{
	Default
	{
		Tag "Rocket Launcher";
		Weapon.SlotNumber 5;
		Weapon.SelectionOrder 2500;
		Inventory.PickupMessage "Picked up the Rocket Launcher";
		Weapon.AmmoType1 "WMQ_Mag_DoomRocketLauncher";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 7;
		Weapon.AmmoType2 "RocketAmmo";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 14;
		WMQ_Gun.Capacity 7;
		WMQ_Gun.FireSound "weapons/rocklf";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/rocket/rpg_magout";
		WMQ_Gun.MagInSound "wm/rocket/rpg_magin";
		WMQ_Gun.RackSound "";
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
		Q05R A 20 A_FireProjectile("Rocket");
		Q05R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q05R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q05R A 8;
		Goto Ready;
	Reload:
		Q05R A 0 A_JumpIfInventory("WMQ_Mag_DoomRocketLauncher", 7, "Ready");
		Q05R A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q05R A 0 A_TakeInventory("RSR_Go", 1);
		Q05R A 0 A_GiveInventory("RSR_Start", 1);
		Q05R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q05R A 0 A_TakeInventory("RSR_Go", 1);
		Q05R A 0 A_JumpIfInventory("RSR_NoMag_DoomRocketLauncher", 1, "RSR_Wait");	// no magazine in the gun
		Q05R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q05R A 0 A_JumpIfInventory("WMQ_Mag_DoomRocketLauncher", 1, "RSR_Unload1");
		Q05R A 0 A_GiveInventory("RSR_NoMag_DoomRocketLauncher", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q05R A 0 A_TakeInventory("WMQ_Mag_DoomRocketLauncher", 1);
		Q05R A 0 A_GiveInventory("RSR_Held_DoomRocketLauncher", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q05R A 0 A_TakeInventory("RSR_Seated", 1);
		Q05R A 0 A_TakeInventory("RSR_NoMag_DoomRocketLauncher", 1);
	RSR_Return:		// the held rounds first
		Q05R A 0 A_JumpIfInventory("RSR_Held_DoomRocketLauncher", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q05R A 0 A_TakeInventory("RSR_Held_DoomRocketLauncher", 1);
		Q05R A 0 A_GiveInventory("WMQ_Mag_DoomRocketLauncher", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q05R A 0 A_JumpIfInventory("WMQ_Mag_DoomRocketLauncher", 7, "RSR_Filled");
		Q05R A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q05R A 0 A_GiveInventory("WMQ_Mag_DoomRocketLauncher", 1);
		Q05R A 0 A_TakeInventory("RocketAmmo", 1, TIF_NOTAKEINFINITE);
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
		Q05R A 0 A_JumpIfInventory("WMQ_Mag_DoomRocketLauncher", 7, "RSR_StockDone");
		Q05R A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q05R A 0 A_GiveInventory("WMQ_Mag_DoomRocketLauncher", 1);
		Q05R A 0 A_TakeInventory("RocketAmmo", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q05R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_DoomPlasmaRifle : Ammo { Default { Inventory.MaxAmount 50; Ammo.BackpackMaxAmount 50; +INVENTORY.IGNORESKILL } }

class DoomPlasmaRifle : WMQ_Gun replaces PlasmaRifle
{
	Default
	{
		Tag "Plasma Rifle";
		Weapon.SlotNumber 6;
		Weapon.SelectionOrder 100;
		Inventory.PickupMessage "Picked up the Plasma Rifle";
		Weapon.AmmoType1 "WMQ_Mag_DoomPlasmaRifle";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 50;
		Weapon.AmmoType2 "Cell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 100;
		WMQ_Gun.Capacity 50;
		WMQ_Gun.FireSound "weapons/plasmaf";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/plasma/magout";
		WMQ_Gun.MagInSound "wm/plasma/magin";
		WMQ_Gun.RackSound "";
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
		Q06R A 3 A_FireProjectile("PlasmaBall");
		Q06R A 20;
		Q06R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q06R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q06R A 8;
		Goto Ready;
	Reload:
		Q06R A 0 A_JumpIfInventory("WMQ_Mag_DoomPlasmaRifle", 50, "Ready");
		Q06R A 0 A_JumpIfInventory("Cell", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q06R A 0 A_TakeInventory("RSR_Go", 1);
		Q06R A 0 A_GiveInventory("RSR_Start", 1);
		Q06R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q06R A 0 A_TakeInventory("RSR_Go", 1);
		Q06R A 0 A_JumpIfInventory("RSR_NoMag_DoomPlasmaRifle", 1, "RSR_Wait");	// no magazine in the gun
		Q06R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q06R A 0 A_JumpIfInventory("WMQ_Mag_DoomPlasmaRifle", 1, "RSR_Unload1");
		Q06R A 0 A_GiveInventory("RSR_NoMag_DoomPlasmaRifle", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q06R A 0 A_TakeInventory("WMQ_Mag_DoomPlasmaRifle", 1);
		Q06R A 0 A_GiveInventory("RSR_Held_DoomPlasmaRifle", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q06R A 0 A_TakeInventory("RSR_Seated", 1);
		Q06R A 0 A_TakeInventory("RSR_NoMag_DoomPlasmaRifle", 1);
	RSR_Return:		// the held rounds first
		Q06R A 0 A_JumpIfInventory("RSR_Held_DoomPlasmaRifle", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q06R A 0 A_TakeInventory("RSR_Held_DoomPlasmaRifle", 1);
		Q06R A 0 A_GiveInventory("WMQ_Mag_DoomPlasmaRifle", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q06R A 0 A_JumpIfInventory("WMQ_Mag_DoomPlasmaRifle", 50, "RSR_Filled");
		Q06R A 0 A_JumpIfInventory("Cell", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q06R A 0 A_GiveInventory("WMQ_Mag_DoomPlasmaRifle", 1);
		Q06R A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
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
		Q06R A 0 A_JumpIfInventory("WMQ_Mag_DoomPlasmaRifle", 50, "RSR_StockDone");
		Q06R A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q06R A 0 A_GiveInventory("WMQ_Mag_DoomPlasmaRifle", 1);
		Q06R A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q06R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_DoomBFG9000 : Ammo { Default { Inventory.MaxAmount 160; Ammo.BackpackMaxAmount 160; +INVENTORY.IGNORESKILL } }

class DoomBFG9000 : WMQ_Gun replaces BFG9000
{
	Default
	{
		Tag "BFG 9000";
		Weapon.SlotNumber 7;
		Weapon.SelectionOrder 2800;
		Inventory.PickupMessage "Picked up the BFG 9000";
		Weapon.AmmoType1 "WMQ_Mag_DoomBFG9000";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 160;
		Weapon.AmmoType2 "Cell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 320;
		WMQ_Gun.Capacity 160;
		WMQ_Gun.FireSound "";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
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
		Q07R A 30;
		Q07R A 20 A_FireProjectile("BFGBall");
		Q07R A 20;
		Goto Ready;
	Dry:
		Q07R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q07R A 8;
		Goto Ready;
	Reload:
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_DoomBFG9000", 160, "Ready");
		Q07R A 0 A_JumpIfInventory("Cell", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q07R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q07R A 10;
		Q07R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_DoomBFG9000", 160, "RSR_StockDone");
		Q07R A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q07R A 0 A_GiveInventory("WMQ_Mag_DoomBFG9000", 1);
		Q07R A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q07R A 8;
		Goto Ready;
	}
}

class DoomChainsaw : WMQ_Gun replaces Chainsaw
{
	Default
	{
		Tag "Chainsaw";
		Weapon.SlotNumber 1;
		Weapon.SelectionOrder 2200;
		Inventory.PickupMessage "Picked up the Chainsaw";
		Weapon.Kickback 0;
		+WEAPON.MELEEWEAPON
		WMQ_Gun.FireSound "";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q08S A -1;
		Stop;
	Ready:
		Q08R A 1 A_WeaponReady(0);
		Loop;
	Deselect:
		Q08R A 1 A_Lower(12);
		Loop;
	Select:
		Q08R A 1 A_Raise(12);
		Loop;
	Fire:
		Q08R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q08R A 4 A_Saw;
		Q08R A 0 A_ReFire;
		Goto Ready;
	}
}


class RSQ_Player : DoomPlayer
{
	Default
	{
		Player.DisplayName "Doomguy";
		Player.StartItem "DoomPistol";
		Player.StartItem "Fist";
		Player.StartItem "Clip", 50;
		Player.WeaponSlot 1, "DoomChainsaw", "Fist";
		Player.WeaponSlot 2, "DoomPistol";
		Player.WeaponSlot 3, "DoomShotgun", "DoomSuperShotgun";
		Player.WeaponSlot 4, "DoomChaingun";
		Player.WeaponSlot 5, "DoomRocketLauncher";
		Player.WeaponSlot 6, "DoomPlasmaRifle";
		Player.WeaponSlot 7, "DoomBFG9000";
	}
}
