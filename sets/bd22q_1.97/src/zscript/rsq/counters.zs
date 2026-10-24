// counters.zs (1.97) -- magazine COUNTERS for guns Brutal Doom never reloads (MG42 belt drum,
// Flamethrower2 canister, Unmaker skull). BD22's firing and ammo are untouched: the counter
// mirrors the reserve going down shot by shot, and when it is empty the gun's Reload runs
// (actors/Weapons/*.dec, "posefix rsr"). The real VR reload (vreload.zs) swaps the part; on
// the seat the counter takes the reserve's count up to its capacity. Idle unless VR reloading
// is on (RSR.WantsHands), so with it off the guns are Brutal Doom's exactly.

class RSQ_Counters : EventHandler
{
	static const Name GUN[] = { 'MG42', 'Flamethrower2', 'Unmaker' };
	static const Name MAG[] = { 'RSQ_Mag_MG42', 'RSQ_Mag_Flamethrower2', 'RSQ_Mag_Unmaker' };
	static const Name RES[] = { 'Clip2', 'Gas', 'SoulAmmo' };
	static const int CAP[] = { 200, 200, 60 };
	int lastRes[MAXPLAYERS][3];
	bool inited[MAXPLAYERS][3];

	override void WorldTick()
	{
		for (int pn = 0; pn < MAXPLAYERS; pn++)
		{
			if (!playeringame[pn]) continue;
			PlayerPawn mo = players[pn].mo;
			if (!mo) continue;
			let w = players[pn].ReadyWeapon;
			for (int g = 0; g < GUN.Size(); g++)
			{
				class<Inventory> mag = MAG[g]; class<Inventory> res = RES[g];
				class<Inventory> empty = "RSQ_Empty_" .. GUN[g]; class<Inventory> fill = "RSQ_Fill_" .. GUN[g];
				class<Inventory> nomag = "RSQ_NoMag_" .. GUN[g];
				if (!mag || !res || !empty || !fill || !nomag) continue;
				bool held = w && w.GetClassName() == GUN[g];
				int r = mo.CountInv(res);
				if (!held || !RSR_ReloadHandler.WantsHands(mo))
				{
					mo.TakeInventory(empty, 1);
					lastRes[pn][g] = r;
					continue;
				}
				if (!inited[pn][g])
				{
					inited[pn][g] = true;
					SetCount(mo, mag, min(CAP[g], r));
					mo.TakeInventory(nomag, 1);
				}
				int d = lastRes[pn][g] - r;
				if (d > 0)
					SetCount(mo, mag, max(0, mo.CountInv(mag) - d));
				if (mo.CountInv(fill) > 0)
				{
					mo.TakeInventory(fill, 1);
					SetCount(mo, mag, min(CAP[g], r));
					mo.TakeInventory(nomag, 1);
				}
				bool e = mo.CountInv(mag) <= 0 && r > 0;
				if (e) mo.GiveInventory(empty, 1); else mo.TakeInventory(empty, 1);
				lastRes[pn][g] = r;
			}
		}
	}

	static void SetCount(PlayerPawn mo, class<Inventory> it, int n)
	{
		int c = mo.CountInv(it);
		if (n > c) mo.GiveInventory(it, n - c);
		else if (n < c) mo.TakeInventory(it, c - n);
	}
}

class RSQ_Mag_MG42 : Inventory { Default { Inventory.MaxAmount 200; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_MG42 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_MG42 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_MG42 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Mag_Flamethrower2 : Inventory { Default { Inventory.MaxAmount 200; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_Flamethrower2 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_Flamethrower2 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_Flamethrower2 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Mag_Unmaker : Inventory { Default { Inventory.MaxAmount 60; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_Unmaker : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_Unmaker : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_Unmaker : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
