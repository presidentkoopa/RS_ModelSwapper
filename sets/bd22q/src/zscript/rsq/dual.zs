// RS dual wield (1.20, owner). Two of the same gun, one in each hand, each its own gun.
//   - Each dual-able gun has an off-hand COPY (DECORATE.rsqdual, generated): the gun itself,
//     with its own magazine, that lives in the off hand only (it never changes hands).
//   - You get a copy by picking up a second one of the gun (BD22's own rule for dual),
//     or the pistol's from the start ("Pistol Start: Start with Dual Pistols").
//   - BD22's Dual key (+user3) toggles the off hand: the copy of the gun in your main hand,
//     or back to the fist (so VR reloading of the main gun is always one press away).
//     A gun whose Dual Options entry is off does not go dual.
// Reserve ammo is shared with the gun; each copy keeps its own magazine. Firing is per hand
// (1.16) and so is reloading (1.17 flick).
class RSQ_Dual : EventHandler
{
	const MAXGUNS = 11;		// RSQ_DualTable.COUNT
	bool had[MAXPLAYERS][MAXGUNS];	// owned the gun last tic (a pickup now is a second one)
	bool forcedNoAuto[MAXPLAYERS];	// 1.21: NoAutoReload is ours while two guns are out

	static int GunIndex(Weapon w)
	{
		if (!w)
			return -1;
		for (int i = 0; i < RSQ_DualTable.COUNT; i++)
		{
			class<Actor> c = RSQ_DualTable.Gun(i);
			class<Actor> cc = RSQ_DualTable.Copy(i);
			if (c && w is c && !(cc && w is cc))
				return i;
		}
		return -1;
	}

	static bool Owns(PlayerPawn mo, int i)
	{
		class<Actor> c = RSQ_DualTable.Gun(i);
		class<Actor> cc = RSQ_DualTable.Copy(i);
		for (let it = mo.Inv; it; it = it.Inv)
			if (c && it is c && !(cc && it is cc))
				return true;
		return false;
	}

	// which gun this is the off-hand copy OF, or -1. IsCopy only says "some copy";
	// rsq/hands.zs has to know WHICH, to tell a real dual wield from one left behind.
	static int CopyIndex(Weapon w)
	{
		for (int i = 0; w && i < RSQ_DualTable.COUNT; i++)
		{
			class<Actor> cc = RSQ_DualTable.Copy(i);
			if (cc && w is cc)
				return i;
		}
		return -1;
	}

	static bool IsCopy(Weapon w)
	{
		for (int i = 0; w && i < RSQ_DualTable.COUNT; i++)
		{
			class<Actor> cc = RSQ_DualTable.Copy(i);
			if (cc && w is cc)
				return true;
		}
		return false;
	}

	static void GiveCopy(PlayerPawn mo, int i)
	{
		class<Inventory> cc = (class<Inventory>)(RSQ_DualTable.Copy(i));
		if (!cc || mo.FindInventory(cc))
			return;
		let p = mo.player;
		let pend = p.PendingWeapon;
		mo.GiveInventory(cc, 1);
		if (p.PendingWeapon != pend)
			p.PendingWeapon = pend;		// getting it never switches to it; the Dual key does
		class<Inventory> mc = (class<Inventory>)(RSQ_DualTable.Mag(i));
		if (mc)
			mo.SetInventory(mc, RSQ_DualTable.MagMax(i));
	}

	override void WorldTick()
	{
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo)
				continue;
			let mo = players[n].mo;
			let p = mo.player;
			if (p.playerstate != PST_LIVE)
				continue;

			// Pistol Start
			if (RSQ.PlayerInt(mo, 'rsq_dual_start', 1) != 0 && Owns(mo, 0))
				GiveCopy(mo, 0);
			// BD22's own "second one picked up" tokens count too
			static const Name hasDual[] = { 'HasDualPistol', 'None', 'HasDualSMG', 'HasDualMP40', 'HasDualRifle', 'HasDualPlasma' };
			for (int i = 0; i < hasDual.Size() && i < RSQ_DualTable.COUNT; i++)
			{
				if (hasDual[i] == 'None')
					continue;
				class<Inventory> tc = hasDual[i];
				if (tc && mo.CountInv(tc) > 0 && Owns(mo, i))
					GiveCopy(mo, i);
			}

			// 1.21 (owner): with a gun in each hand only the flick reloads. BD22's own "no auto
			// reload" token is forced on while both hands hold guns, and set back to the player's
			// BD22 option (bd_noautoreload) when they don't.
			bool two = RSQ_Flick.IsGun(p.OffhandWeapon);	// a gun in the off hand: it reloads only by flick
			if (two)
			{
				if (mo.CountInv('NoAutoReload') < 1)
					mo.SetInventory('NoAutoReload', 1);
				forcedNoAuto[n] = true;
			}
			else if (forcedNoAuto[n])
			{
				forcedNoAuto[n] = false;
				mo.SetInventory('NoAutoReload', RSQ.PlayerInt(mo, 'bd_noautoreload', 0) != 0 ? 1 : 0);
			}

			// the Dual key (BD22: +user3 gives StartDualWield; the guns no longer take it)
			if (mo.CountInv('StartDualWield') > 0)
			{
				mo.TakeInventory('StartDualWield', 0x7fffffff);
				Toggle(mo);
			}

			for (int i = 0; i < RSQ_DualTable.COUNT; i++)
				had[n][i] = Owns(mo, i);
		}
	}

	static void Toggle(PlayerPawn mo)
	{
		let p = mo.player;
		if (IsCopy(p.OffhandWeapon))
		{
			let fist = Weapon(mo.FindInventory('RSQ_Hands'));
			if (!fist)
			{
				mo.GiveInventory('RSQ_Hands', 1);
				fist = Weapon(mo.FindInventory('RSQ_Hands'));
			}
			if (fist)
				p.PendingWeapon = fist;
			return;
		}
		int i = GunIndex(p.ReadyWeapon);
		if (i < 0)
			return;
		if (RSQ.PlayerInt(mo, RSQ_DualTable.CVarName(i), 0) == 0)
		{
			mo.A_Print(String.Format("Dual %s is off in Dual Options", RSQ_DualTable.Nice(i)));
			return;
		}
		class<Inventory> cc = (class<Inventory>)(RSQ_DualTable.Copy(i));
		let w = cc ? Weapon(mo.FindInventory(cc)) : null;
		if (!w)
		{
			mo.A_Print(String.Format("Find a second %s to dual wield it", RSQ_DualTable.Nice(i)));
			return;
		}
		p.PendingWeapon = w;
	}

	// a BD22 weapon pickup taken by a player who already had that gun: a second one
	override void WorldThingDestroyed(WorldEvent e)
	{
		let a = e.Thing;
		if (!a || !(a is 'Inventory') || Inventory(a).Owner)
			return;
		int i = RSQ_DualTable.PickupGun(a.GetClassName());
		if (i < 0)
			return;
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo || !had[n][i])
				continue;
			let mo = players[n].mo;
			if (mo.Distance3D(a) <= mo.radius + a.radius + 16)
				GiveCopy(mo, i);
		}
	}
}
