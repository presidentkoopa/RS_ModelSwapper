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
		Q0BS A 0;
		Q0CS A 0;
		Q0DS A 0;
		Q0ES A 0;
		Q0FS A 0;
		Q0GS A 0;
		Q0HS A 0;
		Q0IS A 0;
		Q0JS A 0;
		Q0KS A 0;
		Q0LS A 0;
		Q0MS A 0;
		Q0NS A 0;
		Q0OS A 0;
		Q0PS A 0;
		Q0QS A 0;
		Q0RS A 0;
		Q0SS A 0;
		Q0TS A 0;
		Q0US A 0;
		Q0VS A 0;
		Q0WS A 0;
		Q0XS A 0;
		Q0YS A 0;
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
		Q0BR A 0;
		Q0BS A 0;
		Q0CR A 0;
		Q0CS A 0;
		Q0DR A 0;
		Q0DS A 0;
		Q0ER A 0;
		Q0ES A 0;
		Q0FR A 0;
		Q0FS A 0;
		Q0GR A 0;
		Q0GS A 0;
		Q0HR A 0;
		Q0HS A 0;
		Q0IR A 0;
		Q0IS A 0;
		Q0JR A 0;
		Q0JS A 0;
		Q0KR A 0;
		Q0KS A 0;
		Q0LR A 0;
		Q0LS A 0;
		Q0MR A 0;
		Q0MS A 0;
		Q0NR A 0;
		Q0NS A 0;
		Q0OR A 0;
		Q0OS A 0;
		Q0PR A 0;
		Q0PS A 0;
		Q0QR A 0;
		Q0QS A 0;
		Q0RR A 0;
		Q0RS A 0;
		Q0SR A 0;
		Q0SS A 0;
		Q0TR A 0;
		Q0TS A 0;
		Q0UR A 0;
		Q0US A 0;
		Q0VR A 0;
		Q0VS A 0;
		Q0WR A 0;
		Q0WS A 0;
		Q0XR A 0;
		Q0XS A 0;
		Q0YR A 0;
		Q0YS A 0;
		Stop;
	}
}

class WMQ_Mag_WM_VP_BFG : Ammo { Default { Inventory.MaxAmount 160; Ammo.BackpackMaxAmount 160; +INVENTORY.IGNORESKILL } }

class WM_VP_BFG : WMQ_Gun replaces BFG9000
{
	Default
	{
		Tag "BFG 9000";
		Weapon.SlotNumber 7;
		Weapon.SelectionOrder 2800;
		Inventory.PickupMessage "Picked up the BFG 9000";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_BFG";
		Weapon.AmmoUse1 40;
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
		Q01R A 30;
		Q01R A 10 A_FireProjectile("BFGBall");
		Q01R A 20;
		Q01R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q01R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q01R A 8;
		Goto Ready;
	Reload:
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_BFG", 160, "Ready");
		Q01R A 0 A_JumpIfInventory("Cell", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q01R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q01R A 10;
		Q01R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q01R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_BFG", 160, "RSR_StockDone");
		Q01R A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q01R A 0 A_GiveInventory("WMQ_Mag_WM_VP_BFG", 1);
		Q01R A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q01R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_BFGHeavy : Ammo { Default { Inventory.MaxAmount 160; Ammo.BackpackMaxAmount 160; +INVENTORY.IGNORESKILL } }

class WM_VP_BFGHeavy : WMQ_Gun
{
	Default
	{
		Tag "BFG 10000";
		Weapon.SlotNumber 7;
		Weapon.SelectionOrder 9800;
		Inventory.PickupMessage "Picked up the BFG 10000";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_BFGHeavy";
		Weapon.AmmoUse1 40;
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
		Q02R A 30;
		Q02R A 10 A_FireProjectile("BFGBall");
		Q02R A 20;
		Q02R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q02R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q02R A 8;
		Goto Ready;
	Reload:
		Q02R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_BFGHeavy", 160, "Ready");
		Q02R A 0 A_JumpIfInventory("Cell", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q02R A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q02R A 10;
		Q02R A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q02R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_BFGHeavy", 160, "RSR_StockDone");
		Q02R A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q02R A 0 A_GiveInventory("WMQ_Mag_WM_VP_BFGHeavy", 1);
		Q02R A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q02R A 8;
		Goto Ready;
	}
}

class WM_VP_Chaingun : WMQ_Gun replaces Chaingun
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
		Q03R A 4 A_FireBullets(5.6, 0.0, 1, 5, "BulletPuff", FBF_USEAMMO);
		Q03R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q03R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q03R A 8;
		Goto Ready;
	}
}

class WM_VP_MachineGun : WMQ_Gun
{
	Default
	{
		Tag "Machine Gun";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 9600;
		Inventory.PickupMessage "Picked up the Machine Gun";
		Weapon.AmmoType1 "Clip";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 20;
		WMQ_Gun.FireSound "wm/machinegun/fire";
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

class WM_VP_Chainsaw : WMQ_Gun replaces Chainsaw
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
		Q05S A -1;
		Stop;
	Ready:
		Q05R A 1 A_WeaponReady(0);
		Loop;
	Deselect:
		Q05R A 1 A_Lower(12);
		Loop;
	Select:
		Q05R A 1 A_Raise(12);
		Loop;
	Fire:
		Q05R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q05R A 4 A_Saw;
		Q05R A 0 A_ReFire;
		Goto Ready;
	}
}

class WM_VP_ChainsawHeavy : WMQ_Gun
{
	Default
	{
		Tag "Heavy Chainsaw";
		Weapon.SlotNumber 1;
		Weapon.SelectionOrder 9900;
		Inventory.PickupMessage "Picked up the Heavy Chainsaw";
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
		Q06S A -1;
		Stop;
	Ready:
		Q06R A 1 A_WeaponReady(0);
		Loop;
	Deselect:
		Q06R A 1 A_Lower(12);
		Loop;
	Select:
		Q06R A 1 A_Raise(12);
		Loop;
	Fire:
		Q06R A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q06R A 4 A_Saw;
		Q06R A 0 A_ReFire;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_Unmaker : Ammo { Default { Inventory.MaxAmount 100; Ammo.BackpackMaxAmount 100; +INVENTORY.IGNORESKILL } }

class WM_VP_Unmaker : WMQ_Gun
{
	Default
	{
		Tag "Unmaker";
		Weapon.SlotNumber 7;
		Weapon.SelectionOrder 2850;
		Inventory.PickupMessage "Picked up the Unmaker";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_Unmaker";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 100;
		Weapon.AmmoType2 "Cell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 200;
		WMQ_Gun.Capacity 100;
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
		Q07R A 1 A_FireProjectile("PlasmaBall");
		Goto Ready;
	Dry:
		Q07R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q07R A 8;
		Goto Ready;
	Reload:
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Unmaker", 100, "Ready");
		Q07R A 0 A_JumpIfInventory("Cell", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q07R A 0 A_TakeInventory("RSR_Go", 1);
		Q07R A 0 A_GiveInventory("RSR_Start", 1);
		Q07R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q07R A 0 A_TakeInventory("RSR_Go", 1);
		Q07R A 0 A_JumpIfInventory("RSR_NoMag_WM_VP_Unmaker", 1, "RSR_Wait");	// no magazine in the gun
		Q07R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Unmaker", 1, "RSR_Unload1");
		Q07R A 0 A_GiveInventory("RSR_NoMag_WM_VP_Unmaker", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q07R A 0 A_TakeInventory("WMQ_Mag_WM_VP_Unmaker", 1);
		Q07R A 0 A_GiveInventory("RSR_Held_WM_VP_Unmaker", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q07R A 0 A_TakeInventory("RSR_Seated", 1);
		Q07R A 0 A_TakeInventory("RSR_NoMag_WM_VP_Unmaker", 1);
	RSR_Return:		// the held rounds first
		Q07R A 0 A_JumpIfInventory("RSR_Held_WM_VP_Unmaker", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q07R A 0 A_TakeInventory("RSR_Held_WM_VP_Unmaker", 1);
		Q07R A 0 A_GiveInventory("WMQ_Mag_WM_VP_Unmaker", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Unmaker", 100, "RSR_Filled");
		Q07R A 0 A_JumpIfInventory("Cell", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q07R A 0 A_GiveInventory("WMQ_Mag_WM_VP_Unmaker", 1);
		Q07R A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
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
		Q07R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Unmaker", 100, "RSR_StockDone");
		Q07R A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q07R A 0 A_GiveInventory("WMQ_Mag_WM_VP_Unmaker", 1);
		Q07R A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q07R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_Bolter : Ammo { Default { Inventory.MaxAmount 10; Ammo.BackpackMaxAmount 10; +INVENTORY.IGNORESKILL } }

class WM_VP_Bolter : WMQ_Gun
{
	Default
	{
		Tag "Bolter";
		Weapon.SlotNumber 6;
		Weapon.SelectionOrder 9510;
		Inventory.PickupMessage "Picked up the Bolter";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_Bolter";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 10;
		Weapon.AmmoType2 "Cell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 20;
		WMQ_Gun.Capacity 10;
		WMQ_Gun.FireSound "wm/plasma/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/plasma/magout";
		WMQ_Gun.MagInSound "wm/plasma/magin";
		WMQ_Gun.RackSound "";
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
		Q08R A 18 A_FireProjectile("PlasmaBall");
		Q08R A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q08R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q08R A 8;
		Goto Ready;
	Reload:
		Q08R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Bolter", 10, "Ready");
		Q08R A 0 A_JumpIfInventory("Cell", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q08R A 0 A_TakeInventory("RSR_Go", 1);
		Q08R A 0 A_GiveInventory("RSR_Start", 1);
		Q08R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q08R A 0 A_TakeInventory("RSR_Go", 1);
		Q08R A 0 A_JumpIfInventory("RSR_NoMag_WM_VP_Bolter", 1, "RSR_Wait");	// no magazine in the gun
		Q08R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q08R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Bolter", 1, "RSR_Unload1");
		Q08R A 0 A_GiveInventory("RSR_NoMag_WM_VP_Bolter", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q08R A 0 A_TakeInventory("WMQ_Mag_WM_VP_Bolter", 1);
		Q08R A 0 A_GiveInventory("RSR_Held_WM_VP_Bolter", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q08R A 0 A_TakeInventory("RSR_Seated", 1);
		Q08R A 0 A_TakeInventory("RSR_NoMag_WM_VP_Bolter", 1);
	RSR_Return:		// the held rounds first
		Q08R A 0 A_JumpIfInventory("RSR_Held_WM_VP_Bolter", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q08R A 0 A_TakeInventory("RSR_Held_WM_VP_Bolter", 1);
		Q08R A 0 A_GiveInventory("WMQ_Mag_WM_VP_Bolter", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q08R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Bolter", 10, "RSR_Filled");
		Q08R A 0 A_JumpIfInventory("Cell", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q08R A 0 A_GiveInventory("WMQ_Mag_WM_VP_Bolter", 1);
		Q08R A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
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
		Q08R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Bolter", 10, "RSR_StockDone");
		Q08R A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q08R A 0 A_GiveInventory("WMQ_Mag_WM_VP_Bolter", 1);
		Q08R A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q08R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_AssaultShotgun : Ammo { Default { Inventory.MaxAmount 14; Ammo.BackpackMaxAmount 14; +INVENTORY.IGNORESKILL } }

class WM_VP_AssaultShotgun : WMQ_Gun
{
	Default
	{
		Tag "Assault Shotgun";
		Weapon.SlotNumber 3;
		Weapon.SelectionOrder 1320;
		Inventory.PickupMessage "Picked up the Assault Shotgun";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_AssaultShotgun";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 14;
		Weapon.AmmoType2 "Shell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 28;
		WMQ_Gun.Capacity 14;
		WMQ_Gun.FireSound "weapons/shotgf";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/rifle/magout";
		WMQ_Gun.MagInSound "wm/rifle/magin";
		WMQ_Gun.RackSound "wm/rifle/rackback";
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
		Q09R A 28 A_FireBullets(5.6, 0.0, 7, 5, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q09R A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q09R A 8;
		Goto Ready;
	Reload:
		Q09R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_AssaultShotgun", 14, "Ready");
		Q09R A 0 A_JumpIfInventory("Shell", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q09R A 0 A_TakeInventory("RSR_Go", 1);
		Q09R A 0 A_GiveInventory("RSR_Start", 1);
		Q09R A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q09R A 0 A_TakeInventory("RSR_Go", 1);
		Q09R A 0 A_JumpIfInventory("RSR_NoMag_WM_VP_AssaultShotgun", 1, "RSR_Wait");	// no magazine in the gun
		Q09R A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q09R A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q09R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_AssaultShotgun", 1, "RSR_Unload1");
		Q09R A 0 A_GiveInventory("RSR_NoMag_WM_VP_AssaultShotgun", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q09R A 0 A_TakeInventory("WMQ_Mag_WM_VP_AssaultShotgun", 1);
		Q09R A 0 A_GiveInventory("RSR_Held_WM_VP_AssaultShotgun", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q09R A 0 A_TakeInventory("RSR_Seated", 1);
		Q09R A 0 A_TakeInventory("RSR_NoMag_WM_VP_AssaultShotgun", 1);
	RSR_Return:		// the held rounds first
		Q09R A 0 A_JumpIfInventory("RSR_Held_WM_VP_AssaultShotgun", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q09R A 0 A_TakeInventory("RSR_Held_WM_VP_AssaultShotgun", 1);
		Q09R A 0 A_GiveInventory("WMQ_Mag_WM_VP_AssaultShotgun", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q09R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_AssaultShotgun", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q09R A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q09R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_AssaultShotgun", 14, "RSR_Filled");
		Q09R A 0 A_JumpIfInventory("Shell", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q09R A 0 A_GiveInventory("WMQ_Mag_WM_VP_AssaultShotgun", 1);
		Q09R A 0 A_TakeInventory("Shell", 1, TIF_NOTAKEINFINITE);
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
		Q09R A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_AssaultShotgun", 14, "RSR_StockDone");
		Q09R A 0 A_JumpIfInventory("Shell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q09R A 0 A_GiveInventory("WMQ_Mag_WM_VP_AssaultShotgun", 1);
		Q09R A 0 A_TakeInventory("Shell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q09R A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_BFGRifle : Ammo { Default { Inventory.MaxAmount 160; Ammo.BackpackMaxAmount 160; +INVENTORY.IGNORESKILL } }

class WM_VP_BFGRifle : WMQ_Gun
{
	Default
	{
		Tag "BFG Rifle";
		Weapon.SlotNumber 7;
		Weapon.SelectionOrder 2810;
		Inventory.PickupMessage "Picked up the BFG Rifle";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_BFGRifle";
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
		Q0AR A 30 A_FireProjectile("BFGBall");
		Goto Ready;
	Dry:
		Q0AR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0AR A 8;
		Goto Ready;
	Reload:
		Q0AR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_BFGRifle", 160, "Ready");
		Q0AR A 0 A_JumpIfInventory("Cell", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0AR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0AR A 10;
		Q0AR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0AR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_BFGRifle", 160, "RSR_StockDone");
		Q0AR A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0AR A 0 A_GiveInventory("WMQ_Mag_WM_VP_BFGRifle", 1);
		Q0AR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0AR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_PlasmaCarbine : Ammo { Default { Inventory.MaxAmount 50; Ammo.BackpackMaxAmount 50; +INVENTORY.IGNORESKILL } }

class WM_VP_PlasmaCarbine : WMQ_Gun
{
	Default
	{
		Tag "Plasma Carbine";
		Weapon.SlotNumber 6;
		Weapon.SelectionOrder 9500;
		Inventory.PickupMessage "Picked up the Plasma Carbine";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_PlasmaCarbine";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 50;
		Weapon.AmmoType2 "Cell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 100;
		WMQ_Gun.Capacity 50;
		WMQ_Gun.FireSound "wm/plasma/carbine_fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/plasma/carbine_magout";
		WMQ_Gun.MagInSound "wm/plasma/carbine_magin";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0BS A -1;
		Stop;
	Ready:
		Q0BR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0BR A 1 A_Lower(12);
		Loop;
	Select:
		Q0BR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0BR A 0 A_JumpIfNoAmmo("Dry");
		Q0BR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0BR A 3 A_FireProjectile("PlasmaBall");
		Q0BR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0BR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0BR A 8;
		Goto Ready;
	Reload:
		Q0BR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaCarbine", 50, "Ready");
		Q0BR A 0 A_JumpIfInventory("Cell", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0BR A 0 A_TakeInventory("RSR_Go", 1);
		Q0BR A 0 A_GiveInventory("RSR_Start", 1);
		Q0BR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0BR A 0 A_TakeInventory("RSR_Go", 1);
		Q0BR A 0 A_JumpIfInventory("RSR_NoMag_WM_VP_PlasmaCarbine", 1, "RSR_Wait");	// no magazine in the gun
		Q0BR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0BR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaCarbine", 1, "RSR_Unload1");
		Q0BR A 0 A_GiveInventory("RSR_NoMag_WM_VP_PlasmaCarbine", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0BR A 0 A_TakeInventory("WMQ_Mag_WM_VP_PlasmaCarbine", 1);
		Q0BR A 0 A_GiveInventory("RSR_Held_WM_VP_PlasmaCarbine", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0BR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0BR A 0 A_TakeInventory("RSR_NoMag_WM_VP_PlasmaCarbine", 1);
	RSR_Return:		// the held rounds first
		Q0BR A 0 A_JumpIfInventory("RSR_Held_WM_VP_PlasmaCarbine", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0BR A 0 A_TakeInventory("RSR_Held_WM_VP_PlasmaCarbine", 1);
		Q0BR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PlasmaCarbine", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q0BR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaCarbine", 50, "RSR_Filled");
		Q0BR A 0 A_JumpIfInventory("Cell", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0BR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PlasmaCarbine", 1);
		Q0BR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0BR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0BR A 0 A_TakeInventory("RSR_Done", 1);
		Q0BR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0BR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0BR A 10;
		Q0BR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0BR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaCarbine", 50, "RSR_StockDone");
		Q0BR A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0BR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PlasmaCarbine", 1);
		Q0BR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0BR A 8;
		Goto Ready;
	}
}

class WM_VP_LongbarChainsaw : WMQ_Gun
{
	Default
	{
		Tag "Longbar Chainsaw";
		Weapon.SlotNumber 1;
		Weapon.SelectionOrder 2210;
		Inventory.PickupMessage "Picked up the Longbar Chainsaw";
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
		Q0CS A -1;
		Stop;
	Ready:
		Q0CR A 1 A_WeaponReady(0);
		Loop;
	Deselect:
		Q0CR A 1 A_Lower(12);
		Loop;
	Select:
		Q0CR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0CR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0CR A 4 A_Saw;
		Q0CR A 0 A_ReFire;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_RotaryGun : Ammo { Default { Inventory.MaxAmount 10; Ammo.BackpackMaxAmount 10; +INVENTORY.IGNORESKILL } }

class WM_VP_RotaryGun : WMQ_Gun
{
	Default
	{
		Tag "Rotary Gun";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 710;
		Inventory.PickupMessage "Picked up the Rotary Gun";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_RotaryGun";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 10;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 20;
		WMQ_Gun.Capacity 10;
		WMQ_Gun.FireSound "wm/chaingun/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0DS A -1;
		Stop;
	Ready:
		Q0DR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0DR A 1 A_Lower(12);
		Loop;
	Select:
		Q0DR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0DR A 0 A_JumpIfNoAmmo("Dry");
		Q0DR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0DR A 4 A_FireBullets(5.6, 0.0, 1, 5, "BulletPuff", FBF_USEAMMO);
		Q0DR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0DR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0DR A 8;
		Goto Ready;
	Reload:
		Q0DR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RotaryGun", 10, "Ready");
		Q0DR A 0 A_JumpIfInventory("Clip", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0DR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0DR A 10;
		Q0DR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0DR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RotaryGun", 10, "RSR_StockDone");
		Q0DR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0DR A 0 A_GiveInventory("WMQ_Mag_WM_VP_RotaryGun", 1);
		Q0DR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0DR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_RotaryLauncher : Ammo { Default { Inventory.MaxAmount 1; Ammo.BackpackMaxAmount 1; +INVENTORY.IGNORESKILL } }

class WM_VP_RotaryLauncher : WMQ_Gun
{
	Default
	{
		Tag "Rotary Launcher";
		Weapon.SlotNumber 5;
		Weapon.SelectionOrder 9710;
		Inventory.PickupMessage "Picked up the Rotary Launcher";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_RotaryLauncher";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 1;
		Weapon.AmmoType2 "RocketAmmo";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 2;
		WMQ_Gun.Capacity 1;
		WMQ_Gun.FireSound "wm/rocket/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0ES A -1;
		Stop;
	Ready:
		Q0ER A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0ER A 1 A_Lower(12);
		Loop;
	Select:
		Q0ER A 1 A_Raise(12);
		Loop;
	Fire:
		Q0ER A 0 A_JumpIfNoAmmo("Dry");
		Q0ER A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0ER A 20 A_FireProjectile("Rocket");
		Goto Ready;
	Dry:
		Q0ER A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0ER A 8;
		Goto Ready;
	Reload:
		Q0ER A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RotaryLauncher", 1, "Ready");
		Q0ER A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0ER A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0ER A 10;
		Q0ER A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0ER A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RotaryLauncher", 1, "RSR_StockDone");
		Q0ER A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0ER A 0 A_GiveInventory("WMQ_Mag_WM_VP_RotaryLauncher", 1);
		Q0ER A 0 A_TakeInventory("RocketAmmo", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0ER A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_Moonlight : Ammo { Default { Inventory.MaxAmount 6; Ammo.BackpackMaxAmount 6; +INVENTORY.IGNORESKILL } }

class WM_Moonlight : WMQ_Gun
{
	Default
	{
		Tag "Moonlight";
		Weapon.SlotNumber 2;
		Weapon.SelectionOrder 1800;
		Inventory.PickupMessage "Picked up the Moonlight";
		Weapon.AmmoType1 "WMQ_Mag_WM_Moonlight";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 6;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 12;
		WMQ_Gun.Capacity 6;
		WMQ_Gun.FireSound "wm/revolver/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0FS A -1;
		Stop;
	Ready:
		Q0FR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0FR A 1 A_Lower(12);
		Loop;
	Select:
		Q0FR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0FR A 0 A_JumpIfNoAmmo("Dry");
		Q0FR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0FR A 6 A_FireBullets(0.6, 0.2, 1, 13, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q0FR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0FR A 8;
		Goto Ready;
	Reload:
		Q0FR A 0 A_JumpIfInventory("WMQ_Mag_WM_Moonlight", 6, "Ready");
		Q0FR A 0 A_JumpIfInventory("Clip", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0FR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0FR A 10;
		Q0FR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0FR A 0 A_JumpIfInventory("WMQ_Mag_WM_Moonlight", 6, "RSR_StockDone");
		Q0FR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0FR A 0 A_GiveInventory("WMQ_Mag_WM_Moonlight", 1);
		Q0FR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0FR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_Sunset : Ammo { Default { Inventory.MaxAmount 6; Ammo.BackpackMaxAmount 6; +INVENTORY.IGNORESKILL } }

class WM_Sunset : WMQ_Gun
{
	Default
	{
		Tag "Sunset";
		Weapon.SlotNumber 2;
		Weapon.SelectionOrder 1800;
		Inventory.PickupMessage "Picked up the Sunset";
		Weapon.AmmoType1 "WMQ_Mag_WM_Sunset";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 6;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 12;
		WMQ_Gun.Capacity 6;
		WMQ_Gun.FireSound "wm/revolver/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0GS A -1;
		Stop;
	Ready:
		Q0GR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0GR A 1 A_Lower(12);
		Loop;
	Select:
		Q0GR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0GR A 0 A_JumpIfNoAmmo("Dry");
		Q0GR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0GR A 6 A_FireBullets(0.6, 0.2, 1, 13, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q0GR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0GR A 8;
		Goto Ready;
	Reload:
		Q0GR A 0 A_JumpIfInventory("WMQ_Mag_WM_Sunset", 6, "Ready");
		Q0GR A 0 A_JumpIfInventory("Clip", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0GR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0GR A 10;
		Q0GR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0GR A 0 A_JumpIfInventory("WMQ_Mag_WM_Sunset", 6, "RSR_StockDone");
		Q0GR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0GR A 0 A_GiveInventory("WMQ_Mag_WM_Sunset", 1);
		Q0GR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0GR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_ColaRevolver : Ammo { Default { Inventory.MaxAmount 12; Ammo.BackpackMaxAmount 12; +INVENTORY.IGNORESKILL } }

class WM_ColaRevolver : WMQ_Gun
{
	Default
	{
		Tag "Cola Revolver";
		Weapon.SlotNumber 2;
		Weapon.SelectionOrder 1800;
		Inventory.PickupMessage "Picked up the Cola Revolver";
		Weapon.AmmoType1 "WMQ_Mag_WM_ColaRevolver";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 12;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 24;
		WMQ_Gun.Capacity 12;
		WMQ_Gun.FireSound "wm/revolver/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0HS A -1;
		Stop;
	Ready:
		Q0HR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0HR A 1 A_Lower(12);
		Loop;
	Select:
		Q0HR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0HR A 0 A_JumpIfNoAmmo("Dry");
		Q0HR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0HR A 6 A_FireBullets(0.6, 0.2, 1, 13, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q0HR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0HR A 8;
		Goto Ready;
	Reload:
		Q0HR A 0 A_JumpIfInventory("WMQ_Mag_WM_ColaRevolver", 12, "Ready");
		Q0HR A 0 A_JumpIfInventory("Clip", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0HR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0HR A 10;
		Q0HR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0HR A 0 A_JumpIfInventory("WMQ_Mag_WM_ColaRevolver", 12, "RSR_StockDone");
		Q0HR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0HR A 0 A_GiveInventory("WMQ_Mag_WM_ColaRevolver", 1);
		Q0HR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0HR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_Rifle : Ammo { Default { Inventory.MaxAmount 20; Ammo.BackpackMaxAmount 20; +INVENTORY.IGNORESKILL } }

class WM_Rifle : WMQ_Gun
{
	Default
	{
		Tag "Rifle";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 750;
		Inventory.PickupMessage "Picked up the Rifle";
		Weapon.AmmoType1 "WMQ_Mag_WM_Rifle";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 20;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 40;
		WMQ_Gun.Capacity 20;
		WMQ_Gun.FireSound "wm/rifle/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/rifle/magout";
		WMQ_Gun.MagInSound "wm/rifle/magin";
		WMQ_Gun.RackSound "wm/rifle/rackback";
	}

	States
	{
	Spawn:
		Q0IS A -1;
		Stop;
	Ready:
		Q0IR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0IR A 1 A_Lower(12);
		Loop;
	Select:
		Q0IR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0IR A 0 A_JumpIfNoAmmo("Dry");
		Q0IR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0IR A 6 A_FireBullets(0.3, 0.1, 1, 14, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q0IR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0IR A 8;
		Goto Ready;
	Reload:
		Q0IR A 0 A_JumpIfInventory("WMQ_Mag_WM_Rifle", 20, "Ready");
		Q0IR A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0IR A 0 A_TakeInventory("RSR_Go", 1);
		Q0IR A 0 A_GiveInventory("RSR_Start", 1);
		Q0IR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0IR A 0 A_TakeInventory("RSR_Go", 1);
		Q0IR A 0 A_JumpIfInventory("RSR_NoMag_WM_Rifle", 1, "RSR_Wait");	// no magazine in the gun
		Q0IR A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q0IR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0IR A 0 A_JumpIfInventory("WMQ_Mag_WM_Rifle", 1, "RSR_Unload1");
		Q0IR A 0 A_GiveInventory("RSR_NoMag_WM_Rifle", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0IR A 0 A_TakeInventory("WMQ_Mag_WM_Rifle", 1);
		Q0IR A 0 A_GiveInventory("RSR_Held_WM_Rifle", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0IR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0IR A 0 A_TakeInventory("RSR_NoMag_WM_Rifle", 1);
	RSR_Return:		// the held rounds first
		Q0IR A 0 A_JumpIfInventory("RSR_Held_WM_Rifle", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0IR A 0 A_TakeInventory("RSR_Held_WM_Rifle", 1);
		Q0IR A 0 A_GiveInventory("WMQ_Mag_WM_Rifle", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q0IR A 0 A_JumpIfInventory("WMQ_Mag_WM_Rifle", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q0IR A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q0IR A 0 A_JumpIfInventory("WMQ_Mag_WM_Rifle", 20, "RSR_Filled");
		Q0IR A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0IR A 0 A_GiveInventory("WMQ_Mag_WM_Rifle", 1);
		Q0IR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0IR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0IR A 0 A_TakeInventory("RSR_Done", 1);
		Q0IR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0IR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0IR A 10;
		Q0IR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0IR A 0 A_JumpIfInventory("WMQ_Mag_WM_Rifle", 20, "RSR_StockDone");
		Q0IR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0IR A 0 A_GiveInventory("WMQ_Mag_WM_Rifle", 1);
		Q0IR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0IR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_M16 : Ammo { Default { Inventory.MaxAmount 20; Ammo.BackpackMaxAmount 20; +INVENTORY.IGNORESKILL } }

class WM_M16 : WMQ_Gun
{
	Default
	{
		Tag "M16";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 750;
		Inventory.PickupMessage "Picked up the M16";
		Weapon.AmmoType1 "WMQ_Mag_WM_M16";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 20;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 40;
		WMQ_Gun.Capacity 20;
		WMQ_Gun.FireSound "wm/rifle/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/rifle/magout";
		WMQ_Gun.MagInSound "wm/rifle/magin";
		WMQ_Gun.RackSound "wm/rifle/rackback";
	}

	States
	{
	Spawn:
		Q0JS A -1;
		Stop;
	Ready:
		Q0JR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0JR A 1 A_Lower(12);
		Loop;
	Select:
		Q0JR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0JR A 0 A_JumpIfNoAmmo("Dry");
		Q0JR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0JR A 6 A_FireBullets(3.0, 1.5, 1, 8, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q0JR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0JR A 8;
		Goto Ready;
	Reload:
		Q0JR A 0 A_JumpIfInventory("WMQ_Mag_WM_M16", 20, "Ready");
		Q0JR A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0JR A 0 A_TakeInventory("RSR_Go", 1);
		Q0JR A 0 A_GiveInventory("RSR_Start", 1);
		Q0JR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0JR A 0 A_TakeInventory("RSR_Go", 1);
		Q0JR A 0 A_JumpIfInventory("RSR_NoMag_WM_M16", 1, "RSR_Wait");	// no magazine in the gun
		Q0JR A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q0JR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0JR A 0 A_JumpIfInventory("WMQ_Mag_WM_M16", 1, "RSR_Unload1");
		Q0JR A 0 A_GiveInventory("RSR_NoMag_WM_M16", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0JR A 0 A_TakeInventory("WMQ_Mag_WM_M16", 1);
		Q0JR A 0 A_GiveInventory("RSR_Held_WM_M16", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0JR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0JR A 0 A_TakeInventory("RSR_NoMag_WM_M16", 1);
	RSR_Return:		// the held rounds first
		Q0JR A 0 A_JumpIfInventory("RSR_Held_WM_M16", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0JR A 0 A_TakeInventory("RSR_Held_WM_M16", 1);
		Q0JR A 0 A_GiveInventory("WMQ_Mag_WM_M16", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q0JR A 0 A_JumpIfInventory("WMQ_Mag_WM_M16", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q0JR A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q0JR A 0 A_JumpIfInventory("WMQ_Mag_WM_M16", 20, "RSR_Filled");
		Q0JR A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0JR A 0 A_GiveInventory("WMQ_Mag_WM_M16", 1);
		Q0JR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0JR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0JR A 0 A_TakeInventory("RSR_Done", 1);
		Q0JR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0JR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0JR A 10;
		Q0JR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0JR A 0 A_JumpIfInventory("WMQ_Mag_WM_M16", 20, "RSR_StockDone");
		Q0JR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0JR A 0 A_GiveInventory("WMQ_Mag_WM_M16", 1);
		Q0JR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0JR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_PistoletBlue : Ammo { Default { Inventory.MaxAmount 15; Ammo.BackpackMaxAmount 15; +INVENTORY.IGNORESKILL } }

class WM_PistoletBlue : WMQ_Gun
{
	Default
	{
		Tag "PistoletBlue";
		Weapon.SlotNumber 2;
		Weapon.SelectionOrder 1900;
		Inventory.PickupMessage "Picked up the PistoletBlue";
		Weapon.AmmoType1 "WMQ_Mag_WM_PistoletBlue";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 15;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 30;
		WMQ_Gun.Capacity 15;
		WMQ_Gun.FireSound "wm/pistolet/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/pistolet/magout";
		WMQ_Gun.MagInSound "wm/pistolet/magin";
		WMQ_Gun.RackSound "wm/pistolet/slideback";
	}

	States
	{
	Spawn:
		Q0KS A -1;
		Stop;
	Ready:
		Q0KR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0KR A 1 A_Lower(12);
		Loop;
	Select:
		Q0KR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0KR A 0 A_JumpIfNoAmmo("Dry");
		Q0KR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0KR A 6 A_FireBullets(4.0, 2.0, 1, 5, "BulletPuff", FBF_USEAMMO);
		Q0KR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0KR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0KR A 8;
		Goto Ready;
	Reload:
		Q0KR A 0 A_JumpIfInventory("WMQ_Mag_WM_PistoletBlue", 15, "Ready");
		Q0KR A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0KR A 0 A_TakeInventory("RSR_Go", 1);
		Q0KR A 0 A_GiveInventory("RSR_Start", 1);
		Q0KR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0KR A 0 A_TakeInventory("RSR_Go", 1);
		Q0KR A 0 A_JumpIfInventory("RSR_NoMag_WM_PistoletBlue", 1, "RSR_Wait");	// no magazine in the gun
		Q0KR A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q0KR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0KR A 0 A_JumpIfInventory("WMQ_Mag_WM_PistoletBlue", 1, "RSR_Unload1");
		Q0KR A 0 A_GiveInventory("RSR_NoMag_WM_PistoletBlue", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0KR A 0 A_TakeInventory("WMQ_Mag_WM_PistoletBlue", 1);
		Q0KR A 0 A_GiveInventory("RSR_Held_WM_PistoletBlue", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0KR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0KR A 0 A_TakeInventory("RSR_NoMag_WM_PistoletBlue", 1);
	RSR_Return:		// the held rounds first
		Q0KR A 0 A_JumpIfInventory("RSR_Held_WM_PistoletBlue", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0KR A 0 A_TakeInventory("RSR_Held_WM_PistoletBlue", 1);
		Q0KR A 0 A_GiveInventory("WMQ_Mag_WM_PistoletBlue", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q0KR A 0 A_JumpIfInventory("WMQ_Mag_WM_PistoletBlue", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q0KR A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q0KR A 0 A_JumpIfInventory("WMQ_Mag_WM_PistoletBlue", 15, "RSR_Filled");
		Q0KR A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0KR A 0 A_GiveInventory("WMQ_Mag_WM_PistoletBlue", 1);
		Q0KR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0KR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0KR A 0 A_TakeInventory("RSR_Done", 1);
		Q0KR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0KR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0KR A 10;
		Q0KR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0KR A 0 A_JumpIfInventory("WMQ_Mag_WM_PistoletBlue", 15, "RSR_StockDone");
		Q0KR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0KR A 0 A_GiveInventory("WMQ_Mag_WM_PistoletBlue", 1);
		Q0KR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0KR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_Flamer : Ammo { Default { Inventory.MaxAmount 100; Ammo.BackpackMaxAmount 100; +INVENTORY.IGNORESKILL } }

class WM_Flamer : WMQ_Gun
{
	Default
	{
		Tag "FlameCannon";
		Weapon.SlotNumber 6;
		Weapon.SelectionOrder 150;
		Inventory.PickupMessage "Picked up the FlameCannon";
		Weapon.AmmoType1 "WMQ_Mag_WM_Flamer";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 100;
		Weapon.AmmoType2 "Cell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 200;
		WMQ_Gun.Capacity 100;
		WMQ_Gun.FireSound "";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/plasma/magout";
		WMQ_Gun.MagInSound "wm/plasma/magin";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0LS A -1;
		Stop;
	Ready:
		Q0LR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0LR A 1 A_Lower(12);
		Loop;
	Select:
		Q0LR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0LR A 0 A_JumpIfNoAmmo("Dry");
		Q0LR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0LR A 2 A_FireProjectile("FatShot");
		Q0LR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0LR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0LR A 8;
		Goto Ready;
	Reload:
		Q0LR A 0 A_JumpIfInventory("WMQ_Mag_WM_Flamer", 100, "Ready");
		Q0LR A 0 A_JumpIfInventory("Cell", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0LR A 0 A_TakeInventory("RSR_Go", 1);
		Q0LR A 0 A_GiveInventory("RSR_Start", 1);
		Q0LR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0LR A 0 A_TakeInventory("RSR_Go", 1);
		Q0LR A 0 A_JumpIfInventory("RSR_NoMag_WM_Flamer", 1, "RSR_Wait");	// no magazine in the gun
		Q0LR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0LR A 0 A_JumpIfInventory("WMQ_Mag_WM_Flamer", 1, "RSR_Unload1");
		Q0LR A 0 A_GiveInventory("RSR_NoMag_WM_Flamer", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0LR A 0 A_TakeInventory("WMQ_Mag_WM_Flamer", 1);
		Q0LR A 0 A_GiveInventory("RSR_Held_WM_Flamer", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0LR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0LR A 0 A_TakeInventory("RSR_NoMag_WM_Flamer", 1);
	RSR_Return:		// the held rounds first
		Q0LR A 0 A_JumpIfInventory("RSR_Held_WM_Flamer", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0LR A 0 A_TakeInventory("RSR_Held_WM_Flamer", 1);
		Q0LR A 0 A_GiveInventory("WMQ_Mag_WM_Flamer", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q0LR A 0 A_JumpIfInventory("WMQ_Mag_WM_Flamer", 100, "RSR_Filled");
		Q0LR A 0 A_JumpIfInventory("Cell", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0LR A 0 A_GiveInventory("WMQ_Mag_WM_Flamer", 1);
		Q0LR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0LR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0LR A 0 A_TakeInventory("RSR_Done", 1);
		Q0LR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0LR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0LR A 10;
		Q0LR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0LR A 0 A_JumpIfInventory("WMQ_Mag_WM_Flamer", 100, "RSR_StockDone");
		Q0LR A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0LR A 0 A_GiveInventory("WMQ_Mag_WM_Flamer", 1);
		Q0LR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0LR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_Flamethrower : Ammo { Default { Inventory.MaxAmount 100; Ammo.BackpackMaxAmount 100; +INVENTORY.IGNORESKILL } }

class WM_Flamethrower : WMQ_Gun
{
	Default
	{
		Tag "Flamethrower";
		Weapon.SlotNumber 6;
		Weapon.SelectionOrder 150;
		Inventory.PickupMessage "Picked up the Flamethrower";
		Weapon.AmmoType1 "WMQ_Mag_WM_Flamethrower";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 100;
		Weapon.AmmoType2 "Cell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 200;
		WMQ_Gun.Capacity 100;
		WMQ_Gun.FireSound "";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/plasma/magout";
		WMQ_Gun.MagInSound "wm/plasma/magin";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0MS A -1;
		Stop;
	Ready:
		Q0MR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0MR A 1 A_Lower(12);
		Loop;
	Select:
		Q0MR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0MR A 0 A_JumpIfNoAmmo("Dry");
		Q0MR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0MR A 2 A_FireProjectile("FatShot");
		Q0MR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0MR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0MR A 8;
		Goto Ready;
	Reload:
		Q0MR A 0 A_JumpIfInventory("WMQ_Mag_WM_Flamethrower", 100, "Ready");
		Q0MR A 0 A_JumpIfInventory("Cell", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0MR A 0 A_TakeInventory("RSR_Go", 1);
		Q0MR A 0 A_GiveInventory("RSR_Start", 1);
		Q0MR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0MR A 0 A_TakeInventory("RSR_Go", 1);
		Q0MR A 0 A_JumpIfInventory("RSR_NoMag_WM_Flamethrower", 1, "RSR_Wait");	// no magazine in the gun
		Q0MR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0MR A 0 A_JumpIfInventory("WMQ_Mag_WM_Flamethrower", 1, "RSR_Unload1");
		Q0MR A 0 A_GiveInventory("RSR_NoMag_WM_Flamethrower", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0MR A 0 A_TakeInventory("WMQ_Mag_WM_Flamethrower", 1);
		Q0MR A 0 A_GiveInventory("RSR_Held_WM_Flamethrower", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0MR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0MR A 0 A_TakeInventory("RSR_NoMag_WM_Flamethrower", 1);
	RSR_Return:		// the held rounds first
		Q0MR A 0 A_JumpIfInventory("RSR_Held_WM_Flamethrower", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0MR A 0 A_TakeInventory("RSR_Held_WM_Flamethrower", 1);
		Q0MR A 0 A_GiveInventory("WMQ_Mag_WM_Flamethrower", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q0MR A 0 A_JumpIfInventory("WMQ_Mag_WM_Flamethrower", 100, "RSR_Filled");
		Q0MR A 0 A_JumpIfInventory("Cell", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0MR A 0 A_GiveInventory("WMQ_Mag_WM_Flamethrower", 1);
		Q0MR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0MR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0MR A 0 A_TakeInventory("RSR_Done", 1);
		Q0MR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0MR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0MR A 10;
		Q0MR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0MR A 0 A_JumpIfInventory("WMQ_Mag_WM_Flamethrower", 100, "RSR_StockDone");
		Q0MR A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0MR A 0 A_GiveInventory("WMQ_Mag_WM_Flamethrower", 1);
		Q0MR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0MR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_SMG : Ammo { Default { Inventory.MaxAmount 35; Ammo.BackpackMaxAmount 35; +INVENTORY.IGNORESKILL } }

class WM_SMG : WMQ_Gun
{
	Default
	{
		Tag "SMG";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 800;
		Inventory.PickupMessage "Picked up the SMG";
		Weapon.AmmoType1 "WMQ_Mag_WM_SMG";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 35;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 70;
		WMQ_Gun.Capacity 35;
		WMQ_Gun.FireSound "wm/m4a3/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/rifle/magout";
		WMQ_Gun.MagInSound "wm/rifle/magin";
		WMQ_Gun.RackSound "wm/rifle/rackback";
	}

	States
	{
	Spawn:
		Q0NS A -1;
		Stop;
	Ready:
		Q0NR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0NR A 1 A_Lower(12);
		Loop;
	Select:
		Q0NR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0NR A 0 A_JumpIfNoAmmo("Dry");
		Q0NR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0NR A 4 A_FireBullets(5.6, 2.0, 1, 5, "BulletPuff", FBF_USEAMMO);
		Q0NR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0NR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0NR A 8;
		Goto Ready;
	Reload:
		Q0NR A 0 A_JumpIfInventory("WMQ_Mag_WM_SMG", 35, "Ready");
		Q0NR A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0NR A 0 A_TakeInventory("RSR_Go", 1);
		Q0NR A 0 A_GiveInventory("RSR_Start", 1);
		Q0NR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0NR A 0 A_TakeInventory("RSR_Go", 1);
		Q0NR A 0 A_JumpIfInventory("RSR_NoMag_WM_SMG", 1, "RSR_Wait");	// no magazine in the gun
		Q0NR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0NR A 0 A_JumpIfInventory("WMQ_Mag_WM_SMG", 1, "RSR_Unload1");
		Q0NR A 0 A_GiveInventory("RSR_NoMag_WM_SMG", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0NR A 0 A_TakeInventory("WMQ_Mag_WM_SMG", 1);
		Q0NR A 0 A_GiveInventory("RSR_Held_WM_SMG", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0NR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0NR A 0 A_TakeInventory("RSR_NoMag_WM_SMG", 1);
	RSR_Return:		// the held rounds first
		Q0NR A 0 A_JumpIfInventory("RSR_Held_WM_SMG", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0NR A 0 A_TakeInventory("RSR_Held_WM_SMG", 1);
		Q0NR A 0 A_GiveInventory("WMQ_Mag_WM_SMG", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q0NR A 0 A_JumpIfInventory("WMQ_Mag_WM_SMG", 35, "RSR_Filled");
		Q0NR A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0NR A 0 A_GiveInventory("WMQ_Mag_WM_SMG", 1);
		Q0NR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0NR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0NR A 0 A_TakeInventory("RSR_Done", 1);
		Q0NR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0NR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0NR A 10;
		Q0NR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0NR A 0 A_JumpIfInventory("WMQ_Mag_WM_SMG", 35, "RSR_StockDone");
		Q0NR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0NR A 0 A_GiveInventory("WMQ_Mag_WM_SMG", 1);
		Q0NR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0NR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_Tec9 : Ammo { Default { Inventory.MaxAmount 32; Ammo.BackpackMaxAmount 32; +INVENTORY.IGNORESKILL } }

class WM_Tec9 : WMQ_Gun
{
	Default
	{
		Tag "Tec9";
		Weapon.SlotNumber 4;
		Weapon.SelectionOrder 800;
		Inventory.PickupMessage "Picked up the Tec9";
		Weapon.AmmoType1 "WMQ_Mag_WM_Tec9";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 32;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 64;
		WMQ_Gun.Capacity 32;
		WMQ_Gun.FireSound "wm/pistolet/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/pistolet/magout";
		WMQ_Gun.MagInSound "wm/pistolet/magin";
		WMQ_Gun.RackSound "wm/pistolet/slideback";
	}

	States
	{
	Spawn:
		Q0OS A -1;
		Stop;
	Ready:
		Q0OR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0OR A 1 A_Lower(12);
		Loop;
	Select:
		Q0OR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0OR A 0 A_JumpIfNoAmmo("Dry");
		Q0OR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0OR A 3 A_FireBullets(0.9, 0.3, 1, 7, "BulletPuff", FBF_USEAMMO);
		Q0OR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0OR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0OR A 8;
		Goto Ready;
	Reload:
		Q0OR A 0 A_JumpIfInventory("WMQ_Mag_WM_Tec9", 32, "Ready");
		Q0OR A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0OR A 0 A_TakeInventory("RSR_Go", 1);
		Q0OR A 0 A_GiveInventory("RSR_Start", 1);
		Q0OR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0OR A 0 A_TakeInventory("RSR_Go", 1);
		Q0OR A 0 A_JumpIfInventory("RSR_NoMag_WM_Tec9", 1, "RSR_Wait");	// no magazine in the gun
		Q0OR A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q0OR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0OR A 0 A_JumpIfInventory("WMQ_Mag_WM_Tec9", 1, "RSR_Unload1");
		Q0OR A 0 A_GiveInventory("RSR_NoMag_WM_Tec9", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0OR A 0 A_TakeInventory("WMQ_Mag_WM_Tec9", 1);
		Q0OR A 0 A_GiveInventory("RSR_Held_WM_Tec9", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0OR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0OR A 0 A_TakeInventory("RSR_NoMag_WM_Tec9", 1);
	RSR_Return:		// the held rounds first
		Q0OR A 0 A_JumpIfInventory("RSR_Held_WM_Tec9", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0OR A 0 A_TakeInventory("RSR_Held_WM_Tec9", 1);
		Q0OR A 0 A_GiveInventory("WMQ_Mag_WM_Tec9", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q0OR A 0 A_JumpIfInventory("WMQ_Mag_WM_Tec9", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q0OR A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q0OR A 0 A_JumpIfInventory("WMQ_Mag_WM_Tec9", 32, "RSR_Filled");
		Q0OR A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0OR A 0 A_GiveInventory("WMQ_Mag_WM_Tec9", 1);
		Q0OR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0OR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0OR A 0 A_TakeInventory("RSR_Done", 1);
		Q0OR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0OR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0OR A 10;
		Q0OR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0OR A 0 A_JumpIfInventory("WMQ_Mag_WM_Tec9", 32, "RSR_StockDone");
		Q0OR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0OR A 0 A_GiveInventory("WMQ_Mag_WM_Tec9", 1);
		Q0OR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0OR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_RocketLauncher : Ammo { Default { Inventory.MaxAmount 7; Ammo.BackpackMaxAmount 7; +INVENTORY.IGNORESKILL } }

class WM_VP_RocketLauncher : WMQ_Gun replaces RocketLauncher
{
	Default
	{
		Tag "Rocket Launcher";
		Weapon.SlotNumber 5;
		Weapon.SelectionOrder 2500;
		Inventory.PickupMessage "Picked up the Rocket Launcher";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_RocketLauncher";
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
		Q0PS A -1;
		Stop;
	Ready:
		Q0PR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0PR A 1 A_Lower(12);
		Loop;
	Select:
		Q0PR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0PR A 0 A_JumpIfNoAmmo("Dry");
		Q0PR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0PR A 20 A_FireProjectile("Rocket");
		Q0PR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0PR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0PR A 8;
		Goto Ready;
	Reload:
		Q0PR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RocketLauncher", 7, "Ready");
		Q0PR A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0PR A 0 A_TakeInventory("RSR_Go", 1);
		Q0PR A 0 A_GiveInventory("RSR_Start", 1);
		Q0PR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0PR A 0 A_TakeInventory("RSR_Go", 1);
		Q0PR A 0 A_JumpIfInventory("RSR_NoMag_WM_VP_RocketLauncher", 1, "RSR_Wait");	// no magazine in the gun
		Q0PR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0PR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RocketLauncher", 1, "RSR_Unload1");
		Q0PR A 0 A_GiveInventory("RSR_NoMag_WM_VP_RocketLauncher", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0PR A 0 A_TakeInventory("WMQ_Mag_WM_VP_RocketLauncher", 1);
		Q0PR A 0 A_GiveInventory("RSR_Held_WM_VP_RocketLauncher", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0PR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0PR A 0 A_TakeInventory("RSR_NoMag_WM_VP_RocketLauncher", 1);
	RSR_Return:		// the held rounds first
		Q0PR A 0 A_JumpIfInventory("RSR_Held_WM_VP_RocketLauncher", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0PR A 0 A_TakeInventory("RSR_Held_WM_VP_RocketLauncher", 1);
		Q0PR A 0 A_GiveInventory("WMQ_Mag_WM_VP_RocketLauncher", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q0PR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RocketLauncher", 7, "RSR_Filled");
		Q0PR A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0PR A 0 A_GiveInventory("WMQ_Mag_WM_VP_RocketLauncher", 1);
		Q0PR A 0 A_TakeInventory("RocketAmmo", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0PR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0PR A 0 A_TakeInventory("RSR_Done", 1);
		Q0PR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0PR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0PR A 10;
		Q0PR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0PR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RocketLauncher", 7, "RSR_StockDone");
		Q0PR A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0PR A 0 A_GiveInventory("WMQ_Mag_WM_VP_RocketLauncher", 1);
		Q0PR A 0 A_TakeInventory("RocketAmmo", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0PR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_RPG : Ammo { Default { Inventory.MaxAmount 6; Ammo.BackpackMaxAmount 6; +INVENTORY.IGNORESKILL } }

class WM_VP_RPG : WMQ_Gun
{
	Default
	{
		Tag "RPG";
		Weapon.SlotNumber 5;
		Weapon.SelectionOrder 9700;
		Inventory.PickupMessage "Picked up the RPG";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_RPG";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 6;
		Weapon.AmmoType2 "RocketAmmo";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 12;
		WMQ_Gun.Capacity 6;
		WMQ_Gun.FireSound "wm/rocket/rpg_fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/rocket/rpg_magout";
		WMQ_Gun.MagInSound "wm/rocket/rpg_magin";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0QS A -1;
		Stop;
	Ready:
		Q0QR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0QR A 1 A_Lower(12);
		Loop;
	Select:
		Q0QR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0QR A 0 A_JumpIfNoAmmo("Dry");
		Q0QR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0QR A 20 A_FireProjectile("Rocket");
		Q0QR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0QR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0QR A 8;
		Goto Ready;
	Reload:
		Q0QR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RPG", 6, "Ready");
		Q0QR A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0QR A 0 A_TakeInventory("RSR_Go", 1);
		Q0QR A 0 A_GiveInventory("RSR_Start", 1);
		Q0QR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0QR A 0 A_TakeInventory("RSR_Go", 1);
		Q0QR A 0 A_JumpIfInventory("RSR_NoMag_WM_VP_RPG", 1, "RSR_Wait");	// no magazine in the gun
		Q0QR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0QR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RPG", 1, "RSR_Unload1");
		Q0QR A 0 A_GiveInventory("RSR_NoMag_WM_VP_RPG", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0QR A 0 A_TakeInventory("WMQ_Mag_WM_VP_RPG", 1);
		Q0QR A 0 A_GiveInventory("RSR_Held_WM_VP_RPG", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0QR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0QR A 0 A_TakeInventory("RSR_NoMag_WM_VP_RPG", 1);
	RSR_Return:		// the held rounds first
		Q0QR A 0 A_JumpIfInventory("RSR_Held_WM_VP_RPG", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0QR A 0 A_TakeInventory("RSR_Held_WM_VP_RPG", 1);
		Q0QR A 0 A_GiveInventory("WMQ_Mag_WM_VP_RPG", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q0QR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RPG", 6, "RSR_Filled");
		Q0QR A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0QR A 0 A_GiveInventory("WMQ_Mag_WM_VP_RPG", 1);
		Q0QR A 0 A_TakeInventory("RocketAmmo", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0QR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0QR A 0 A_TakeInventory("RSR_Done", 1);
		Q0QR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0QR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0QR A 10;
		Q0QR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0QR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_RPG", 6, "RSR_StockDone");
		Q0QR A 0 A_JumpIfInventory("RocketAmmo", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0QR A 0 A_GiveInventory("WMQ_Mag_WM_VP_RPG", 1);
		Q0QR A 0 A_TakeInventory("RocketAmmo", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0QR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_M4A3 : Ammo { Default { Inventory.MaxAmount 15; Ammo.BackpackMaxAmount 15; +INVENTORY.IGNORESKILL } }

class WM_VP_M4A3 : WMQ_Gun replaces Pistol
{
	Default
	{
		Tag "Pistol";
		Weapon.SlotNumber 2;
		Weapon.SelectionOrder 100;
		Inventory.PickupMessage "Picked up the Pistol";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_M4A3";
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
		Q0RS A -1;
		Stop;
	Ready:
		Q0RR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0RR A 1 A_Lower(12);
		Loop;
	Select:
		Q0RR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0RR A 0 A_JumpIfNoAmmo("Dry");
		Q0RR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0RR A 6 A_FireBullets(4.0, 2.0, 1, 5, "BulletPuff", FBF_USEAMMO);
		Q0RR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0RR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0RR A 8;
		Goto Ready;
	Reload:
		Q0RR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_M4A3", 15, "Ready");
		Q0RR A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0RR A 0 A_TakeInventory("RSR_Go", 1);
		Q0RR A 0 A_GiveInventory("RSR_Start", 1);
		Q0RR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0RR A 0 A_TakeInventory("RSR_Go", 1);
		Q0RR A 0 A_JumpIfInventory("RSR_NoMag_WM_VP_M4A3", 1, "RSR_Wait");	// no magazine in the gun
		Q0RR A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q0RR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0RR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_M4A3", 1, "RSR_Unload1");
		Q0RR A 0 A_GiveInventory("RSR_NoMag_WM_VP_M4A3", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0RR A 0 A_TakeInventory("WMQ_Mag_WM_VP_M4A3", 1);
		Q0RR A 0 A_GiveInventory("RSR_Held_WM_VP_M4A3", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0RR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0RR A 0 A_TakeInventory("RSR_NoMag_WM_VP_M4A3", 1);
	RSR_Return:		// the held rounds first
		Q0RR A 0 A_JumpIfInventory("RSR_Held_WM_VP_M4A3", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0RR A 0 A_TakeInventory("RSR_Held_WM_VP_M4A3", 1);
		Q0RR A 0 A_GiveInventory("WMQ_Mag_WM_VP_M4A3", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q0RR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_M4A3", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q0RR A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q0RR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_M4A3", 15, "RSR_Filled");
		Q0RR A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0RR A 0 A_GiveInventory("WMQ_Mag_WM_VP_M4A3", 1);
		Q0RR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0RR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0RR A 0 A_TakeInventory("RSR_Done", 1);
		Q0RR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0RR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0RR A 10;
		Q0RR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0RR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_M4A3", 15, "RSR_StockDone");
		Q0RR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0RR A 0 A_GiveInventory("WMQ_Mag_WM_VP_M4A3", 1);
		Q0RR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0RR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_Pistolet : Ammo { Default { Inventory.MaxAmount 15; Ammo.BackpackMaxAmount 15; +INVENTORY.IGNORESKILL } }

class WM_VP_Pistolet : WMQ_Gun
{
	Default
	{
		Tag "Black Handgun";
		Weapon.SlotNumber 2;
		Weapon.SelectionOrder 9000;
		Inventory.PickupMessage "Picked up the Black Handgun";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_Pistolet";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 15;
		Weapon.AmmoType2 "Clip";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 30;
		WMQ_Gun.Capacity 15;
		WMQ_Gun.FireSound "wm/pistolet/fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "wm/pistolet/magout";
		WMQ_Gun.MagInSound "wm/pistolet/magin";
		WMQ_Gun.RackSound "wm/pistolet/slideback";
	}

	States
	{
	Spawn:
		Q0SS A -1;
		Stop;
	Ready:
		Q0SR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0SR A 1 A_Lower(12);
		Loop;
	Select:
		Q0SR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0SR A 0 A_JumpIfNoAmmo("Dry");
		Q0SR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0SR A 6 A_FireBullets(4.0, 2.0, 1, 5, "BulletPuff", FBF_USEAMMO);
		Q0SR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0SR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0SR A 8;
		Goto Ready;
	Reload:
		Q0SR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Pistolet", 15, "Ready");
		Q0SR A 0 A_JumpIfInventory("Clip", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0SR A 0 A_TakeInventory("RSR_Go", 1);
		Q0SR A 0 A_GiveInventory("RSR_Start", 1);
		Q0SR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0SR A 0 A_TakeInventory("RSR_Go", 1);
		Q0SR A 0 A_JumpIfInventory("RSR_NoMag_WM_VP_Pistolet", 1, "RSR_Wait");	// no magazine in the gun
		Q0SR A 0 A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled");	// a magazine in, the handle still to pull
		Q0SR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0SR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Pistolet", 1, "RSR_Unload1");
		Q0SR A 0 A_GiveInventory("RSR_NoMag_WM_VP_Pistolet", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0SR A 0 A_TakeInventory("WMQ_Mag_WM_VP_Pistolet", 1);
		Q0SR A 0 A_GiveInventory("RSR_Held_WM_VP_Pistolet", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0SR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0SR A 0 A_TakeInventory("RSR_NoMag_WM_VP_Pistolet", 1);
	RSR_Return:		// the held rounds first
		Q0SR A 0 A_JumpIfInventory("RSR_Held_WM_VP_Pistolet", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0SR A 0 A_TakeInventory("RSR_Held_WM_VP_Pistolet", 1);
		Q0SR A 0 A_GiveInventory("WMQ_Mag_WM_VP_Pistolet", 1);
		Goto RSR_Return;
	RSR_FillGo:
		Q0SR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Pistolet", 1, "RSR_FillA");	// the gun was not empty: no handle
		Q0SR A 0 A_GiveInventory("RSR_Charge", 1);	// it was empty: the handle is due (vreload.zs ChargeToken)
	RSR_FillA:
		Q0SR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Pistolet", 15, "RSR_Filled");
		Q0SR A 0 A_JumpIfInventory("Clip", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0SR A 0 A_GiveInventory("WMQ_Mag_WM_VP_Pistolet", 1);
		Q0SR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0SR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0SR A 0 A_TakeInventory("RSR_Done", 1);
		Q0SR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0SR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0SR A 10;
		Q0SR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0SR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_Pistolet", 15, "RSR_StockDone");
		Q0SR A 0 A_JumpIfInventory("Clip", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0SR A 0 A_GiveInventory("WMQ_Mag_WM_VP_Pistolet", 1);
		Q0SR A 0 A_TakeInventory("Clip", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0SR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_PlasmaRifle : Ammo { Default { Inventory.MaxAmount 50; Ammo.BackpackMaxAmount 50; +INVENTORY.IGNORESKILL } }

class WM_VP_PlasmaRifle : WMQ_Gun replaces PlasmaRifle
{
	Default
	{
		Tag "Plasma Rifle";
		Weapon.SlotNumber 6;
		Weapon.SelectionOrder 1700;
		Inventory.PickupMessage "Picked up the Plasma Rifle";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_PlasmaRifle";
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
		Q0TS A -1;
		Stop;
	Ready:
		Q0TR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0TR A 1 A_Lower(12);
		Loop;
	Select:
		Q0TR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0TR A 0 A_JumpIfNoAmmo("Dry");
		Q0TR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0TR A 3 A_FireProjectile("PlasmaBall");
		Q0TR A 20;
		Q0TR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0TR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0TR A 8;
		Goto Ready;
	Reload:
		Q0TR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaRifle", 50, "Ready");
		Q0TR A 0 A_JumpIfInventory("Cell", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0TR A 0 A_TakeInventory("RSR_Go", 1);
		Q0TR A 0 A_GiveInventory("RSR_Start", 1);
		Q0TR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0TR A 0 A_TakeInventory("RSR_Go", 1);
		Q0TR A 0 A_JumpIfInventory("RSR_NoMag_WM_VP_PlasmaRifle", 1, "RSR_Wait");	// no magazine in the gun
		Q0TR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0TR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaRifle", 1, "RSR_Unload1");
		Q0TR A 0 A_GiveInventory("RSR_NoMag_WM_VP_PlasmaRifle", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0TR A 0 A_TakeInventory("WMQ_Mag_WM_VP_PlasmaRifle", 1);
		Q0TR A 0 A_GiveInventory("RSR_Held_WM_VP_PlasmaRifle", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0TR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0TR A 0 A_TakeInventory("RSR_NoMag_WM_VP_PlasmaRifle", 1);
	RSR_Return:		// the held rounds first
		Q0TR A 0 A_JumpIfInventory("RSR_Held_WM_VP_PlasmaRifle", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0TR A 0 A_TakeInventory("RSR_Held_WM_VP_PlasmaRifle", 1);
		Q0TR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PlasmaRifle", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q0TR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaRifle", 50, "RSR_Filled");
		Q0TR A 0 A_JumpIfInventory("Cell", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0TR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PlasmaRifle", 1);
		Q0TR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0TR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0TR A 0 A_TakeInventory("RSR_Done", 1);
		Q0TR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0TR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0TR A 10;
		Q0TR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0TR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaRifle", 50, "RSR_StockDone");
		Q0TR A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0TR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PlasmaRifle", 1);
		Q0TR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0TR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_PlasmaRifleBlue : Ammo { Default { Inventory.MaxAmount 50; Ammo.BackpackMaxAmount 50; +INVENTORY.IGNORESKILL } }

class WM_VP_PlasmaRifleBlue : WMQ_Gun
{
	Default
	{
		Tag "Blue Plasma Rifle";
		Weapon.SlotNumber 6;
		Weapon.SelectionOrder 1750;
		Inventory.PickupMessage "Picked up the Blue Plasma Rifle";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_PlasmaRifleBlue";
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
		Q0US A -1;
		Stop;
	Ready:
		Q0UR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0UR A 1 A_Lower(12);
		Loop;
	Select:
		Q0UR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0UR A 0 A_JumpIfNoAmmo("Dry");
		Q0UR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0UR A 3 A_FireProjectile("PlasmaBall");
		Q0UR A 20;
		Q0UR A 0 A_ReFire;
		Goto Ready;
	Dry:
		Q0UR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0UR A 8;
		Goto Ready;
	Reload:
		Q0UR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaRifleBlue", 50, "Ready");
		Q0UR A 0 A_JumpIfInventory("Cell", 1, "RSR_Start");
		Goto Ready;
	// the real VR reload (zscript/rsr/vreload.zs). Not in VR, or with it off, RSR_Start goes on into RSR_Stock.
	RSR_Start:
		Q0UR A 0 A_TakeInventory("RSR_Go", 1);
		Q0UR A 0 A_GiveInventory("RSR_Start", 1);
		Q0UR A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out");
		Goto RSR_Stock;
	RSR_Out:
		Q0UR A 0 A_TakeInventory("RSR_Go", 1);
		Q0UR A 0 A_JumpIfInventory("RSR_NoMag_WM_VP_PlasmaRifleBlue", 1, "RSR_Wait");	// no magazine in the gun
		Q0UR A 0 A_GiveInventory("RSR_MagOut", 1);	// the magazine drops out
	RSR_Unload:		// its rounds are held aside; they come back when a magazine is home
		Q0UR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaRifleBlue", 1, "RSR_Unload1");
		Q0UR A 0 A_GiveInventory("RSR_NoMag_WM_VP_PlasmaRifleBlue", 1);
		Goto RSR_Wait;
	RSR_Unload1:
		Q0UR A 0 A_TakeInventory("WMQ_Mag_WM_VP_PlasmaRifleBlue", 1);
		Q0UR A 0 A_GiveInventory("RSR_Held_WM_VP_PlasmaRifleBlue", 1);
		Goto RSR_Unload;
	RSR_Wait:		// the gun as the script shows it; the script runs every tic
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE);
		"####" "#" 0 A_GiveInventory("RSR_Tick", 1);
		"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill");
		"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done");
		Goto RSR_Wait;
	RSR_Fill:		// the magazine is home
		Q0UR A 0 A_TakeInventory("RSR_Seated", 1);
		Q0UR A 0 A_TakeInventory("RSR_NoMag_WM_VP_PlasmaRifleBlue", 1);
	RSR_Return:		// the held rounds first
		Q0UR A 0 A_JumpIfInventory("RSR_Held_WM_VP_PlasmaRifleBlue", 1, "RSR_Return1");
		Goto RSR_FillGo;
	RSR_Return1:
		Q0UR A 0 A_TakeInventory("RSR_Held_WM_VP_PlasmaRifleBlue", 1);
		Q0UR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PlasmaRifleBlue", 1);
		Goto RSR_Return;
	RSR_FillGo:
	RSR_FillA:
		Q0UR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaRifleBlue", 50, "RSR_Filled");
		Q0UR A 0 A_JumpIfInventory("Cell", 1, "RSR_FillAa");
		Goto RSR_Filled;
	RSR_FillAa:
		Q0UR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PlasmaRifleBlue", 1);
		Q0UR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_FillA;
	RSR_Filled:
		Q0UR A 0 A_GiveInventory("RSR_Filled", 1);	// the script: the handle if it is due, else done
		Goto RSR_Wait;
	RSR_Done:
		Q0UR A 0 A_TakeInventory("RSR_Done", 1);
		Q0UR A 0 A_TakeInventory("RSR_Charge", 1);
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0UR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0UR A 10;
		Q0UR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0UR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PlasmaRifleBlue", 50, "RSR_StockDone");
		Q0UR A 0 A_JumpIfInventory("Cell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0UR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PlasmaRifleBlue", 1);
		Q0UR A 0 A_TakeInventory("Cell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0UR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_PumpM37 : Ammo { Default { Inventory.MaxAmount 8; Ammo.BackpackMaxAmount 8; +INVENTORY.IGNORESKILL } }

class WM_VP_PumpM37 : WMQ_Gun
{
	Default
	{
		Tag "Steelgun";
		Weapon.SlotNumber 3;
		Weapon.SelectionOrder 1300;
		Inventory.PickupMessage "Picked up the Steelgun";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_PumpM37";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 8;
		Weapon.AmmoType2 "Shell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 16;
		WMQ_Gun.Capacity 8;
		WMQ_Gun.FireSound "wm/shotgun/m37_fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0VS A -1;
		Stop;
	Ready:
		Q0VR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0VR A 1 A_Lower(12);
		Loop;
	Select:
		Q0VR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0VR A 0 A_JumpIfNoAmmo("Dry");
		Q0VR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0VR A 20 A_FireBullets(5.6, 0.0, 7, 5, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q0VR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0VR A 8;
		Goto Ready;
	Reload:
		Q0VR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PumpM37", 8, "Ready");
		Q0VR A 0 A_JumpIfInventory("Shell", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0VR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0VR A 10;
		Q0VR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0VR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PumpM37", 8, "RSR_StockDone");
		Q0VR A 0 A_JumpIfInventory("Shell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0VR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PumpM37", 1);
		Q0VR A 0 A_TakeInventory("Shell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0VR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_PumpDoom : Ammo { Default { Inventory.MaxAmount 8; Ammo.BackpackMaxAmount 8; +INVENTORY.IGNORESKILL } }

class WM_VP_PumpDoom : WMQ_Gun replaces Shotgun
{
	Default
	{
		Tag "Shotgun";
		Weapon.SlotNumber 3;
		Weapon.SelectionOrder 9100;
		Inventory.PickupMessage "Picked up the Shotgun";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_PumpDoom";
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
		Q0WS A -1;
		Stop;
	Ready:
		Q0WR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0WR A 1 A_Lower(12);
		Loop;
	Select:
		Q0WR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0WR A 0 A_JumpIfNoAmmo("Dry");
		Q0WR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0WR A 20 A_FireBullets(5.6, 0.0, 7, 5, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q0WR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0WR A 8;
		Goto Ready;
	Reload:
		Q0WR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PumpDoom", 8, "Ready");
		Q0WR A 0 A_JumpIfInventory("Shell", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0WR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0WR A 10;
		Q0WR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0WR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_PumpDoom", 8, "RSR_StockDone");
		Q0WR A 0 A_JumpIfInventory("Shell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0WR A 0 A_GiveInventory("WMQ_Mag_WM_VP_PumpDoom", 1);
		Q0WR A 0 A_TakeInventory("Shell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0WR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_SSG : Ammo { Default { Inventory.MaxAmount 2; Ammo.BackpackMaxAmount 2; +INVENTORY.IGNORESKILL } }

class WM_VP_SSG : WMQ_Gun replaces SuperShotgun
{
	Default
	{
		Tag "Super Shotgun";
		Weapon.SlotNumber 3;
		Weapon.SelectionOrder 1350;
		Inventory.PickupMessage "Picked up the Super Shotgun";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_SSG";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 2;
		Weapon.AmmoType2 "Shell";
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
		Q0XS A -1;
		Stop;
	Ready:
		Q0XR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0XR A 1 A_Lower(12);
		Loop;
	Select:
		Q0XR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0XR A 0 A_JumpIfNoAmmo("Dry");
		Q0XR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0XR A 20 A_FireBullets(11.2, 7.1, 10, 5, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q0XR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0XR A 8;
		Goto Ready;
	Reload:
		Q0XR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_SSG", 2, "Ready");
		Q0XR A 0 A_JumpIfInventory("Shell", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0XR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0XR A 10;
		Q0XR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0XR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_SSG", 2, "RSR_StockDone");
		Q0XR A 0 A_JumpIfInventory("Shell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0XR A 0 A_GiveInventory("WMQ_Mag_WM_VP_SSG", 1);
		Q0XR A 0 A_TakeInventory("Shell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0XR A 8;
		Goto Ready;
	}
}

class WMQ_Mag_WM_VP_BullpupPump : Ammo { Default { Inventory.MaxAmount 4; Ammo.BackpackMaxAmount 4; +INVENTORY.IGNORESKILL } }

class WM_VP_BullpupPump : WMQ_Gun
{
	Default
	{
		Tag "Quad Super";
		Weapon.SlotNumber 3;
		Weapon.SelectionOrder 9150;
		Inventory.PickupMessage "Picked up the Quad Super";
		Weapon.AmmoType1 "WMQ_Mag_WM_VP_BullpupPump";
		Weapon.AmmoUse1 1;
		Weapon.AmmoGive1 4;
		Weapon.AmmoType2 "Shell";
		Weapon.AmmoUse2 0;
		Weapon.AmmoGive2 8;
		WMQ_Gun.Capacity 4;
		WMQ_Gun.FireSound "wm/shotgun/bullpup_fire";
		WMQ_Gun.DrySound "wm/dry";
		WMQ_Gun.MagOutSound "";
		WMQ_Gun.MagInSound "";
		WMQ_Gun.RackSound "";
	}

	States
	{
	Spawn:
		Q0YS A -1;
		Stop;
	Ready:
		Q0YR A 1 A_WeaponReady(WRF_ALLOWRELOAD);
		Loop;
	Deselect:
		Q0YR A 1 A_Lower(12);
		Loop;
	Select:
		Q0YR A 1 A_Raise(12);
		Loop;
	Fire:
		Q0YR A 0 A_JumpIfNoAmmo("Dry");
		Q0YR A 0 A_StartSound(invoker.fireSound, CHAN_WEAPON);
		Q0YR A 20 A_FireBullets(11.2, 7.1, 20, 5, "BulletPuff", FBF_USEAMMO);
		Goto Ready;
	Dry:
		Q0YR A 0 A_StartSound(invoker.drySound, CHAN_WEAPON);
		Q0YR A 8;
		Goto Ready;
	Reload:
		Q0YR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_BullpupPump", 4, "Ready");
		Q0YR A 0 A_JumpIfInventory("Shell", 1, "RSR_Stock");
		Goto Ready;
	RSR_Stock:		// the canned reload: out of VR, with VR reloading off, or no VR reload on this gun
		Q0YR A 10 A_StartSound(invoker.magOutSound, CHAN_WEAPON);
		Q0YR A 10;
		Q0YR A 10 A_StartSound(invoker.magInSound, CHAN_WEAPON);
	RSR_StockFill:
		Q0YR A 0 A_JumpIfInventory("WMQ_Mag_WM_VP_BullpupPump", 4, "RSR_StockDone");
		Q0YR A 0 A_JumpIfInventory("Shell", 1, "RSR_StockFillA");
		Goto RSR_StockDone;
	RSR_StockFillA:
		Q0YR A 0 A_GiveInventory("WMQ_Mag_WM_VP_BullpupPump", 1);
		Q0YR A 0 A_TakeInventory("Shell", 1, TIF_NOTAKEINFINITE);
		Goto RSR_StockFill;
	RSR_StockDone:
		Q0YR A 8;
		Goto Ready;
	}
}


class RSQ_Player : DoomPlayer
{
	Default
	{
		Player.DisplayName "Doomguy";
		Player.StartItem "WM_VP_M4A3";
		Player.StartItem "Fist";
		Player.StartItem "Clip", 50;
		Player.WeaponSlot 1, "WM_VP_Chainsaw", "WM_VP_ChainsawHeavy", "WM_VP_LongbarChainsaw", "Fist";
		Player.WeaponSlot 2, "WM_Moonlight", "WM_Sunset", "WM_ColaRevolver", "WM_PistoletBlue", "WM_VP_M4A3", "WM_VP_Pistolet";
		Player.WeaponSlot 3, "WM_VP_AssaultShotgun", "WM_VP_PumpM37", "WM_VP_PumpDoom", "WM_VP_SSG", "WM_VP_BullpupPump";
		Player.WeaponSlot 4, "WM_VP_Chaingun", "WM_VP_MachineGun", "WM_VP_RotaryGun", "WM_Rifle", "WM_M16", "WM_SMG", "WM_Tec9";
		Player.WeaponSlot 5, "WM_VP_RotaryLauncher", "WM_VP_RocketLauncher", "WM_VP_RPG";
		Player.WeaponSlot 6, "WM_VP_Bolter", "WM_VP_PlasmaCarbine", "WM_Flamer", "WM_Flamethrower", "WM_VP_PlasmaRifle", "WM_VP_PlasmaRifleBlue";
		Player.WeaponSlot 7, "WM_VP_BFG", "WM_VP_BFGHeavy", "WM_VP_Unmaker", "WM_VP_BFGRifle";
	}
}
