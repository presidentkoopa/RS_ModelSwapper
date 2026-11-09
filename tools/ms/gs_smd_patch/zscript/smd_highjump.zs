// The Super Mario Doom high jump for Golden Souls 1 and 2 (PLAN M4).
//
// WHY AN ITEM. Golden Souls 1 (GSPlayer : ZGSPlayer : DoomPlayer, Player.JumpZ 8.2, gplayer.dec line 28, with a
// PlayerThink that allows an instant re-jump) and Golden Souls 2 (GSPlayer : PlayerPawn, Player.JumpZ 15, DECORATE
// line 46, with a double-jump ACS and a MiniPlayer morph) each have their own player class, and MAPINFO's
// playerclasses names it. Replacing it would lose GS1's PlayerThink or break GS2's morph; a MAPINFO or KEYCONF
// cannot set a jump height. So an EventHandler hands every player one undroppable Inventory item, and the item sets
// the pawn's JumpZ each tic. Morphs carry inventory to the new pawn, so the MiniPlayer gets it too and the class
// default is restored by GetDefaultByType when the cvar is turned off.
//
// THE NUMBER. The SDMLITE pack holds no player code, so there is no SMD jump to measure. smd_jumpz defaults to 15,
// Golden Souls 2's own JumpZ: GS1 jumps like GS2, GS2 is unchanged until the cvar is raised. Server cvar: the same
// value on every machine. No consoleplayer anywhere in here.

class SMD_HighJump : Inventory
{
	Default
	{
		Inventory.MaxAmount 1;
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		+INVENTORY.UNCLEARABLE
		+INVENTORY.QUIET
	}

	override void DoEffect()
	{
		Super.DoEffect();
		let pp = PlayerPawn(Owner);
		if (!pp) return;
		double want = -1;
		CVar on = CVar.FindCVar('smd_highjump');
		CVar hz = CVar.FindCVar('smd_jumpz');
		if (on && hz && on.GetBool()) want = hz.GetFloat();
		if (want > 0)
		{
			pp.JumpZ = want;
		}
		else
		{
			let def = PlayerPawn(GetDefaultByType(pp.GetClass()));
			if (def) pp.JumpZ = def.JumpZ;
		}
	}
}

class SMD_HighJumpHandler : EventHandler
{
	private void Give(int pn)
	{
		if (pn < 0 || pn >= MAXPLAYERS || !playeringame[pn]) return;
		let mo = players[pn].mo;
		if (!mo || mo.FindInventory('SMD_HighJump')) return;
		mo.GiveInventoryType('SMD_HighJump');
	}

	override void PlayerEntered(PlayerEvent e) { Give(e.PlayerNumber); }
	override void PlayerRespawned(PlayerEvent e) { Give(e.PlayerNumber); }

	// a save made before the patch was loaded: every player in the game gets the item
	override void WorldLoaded(WorldEvent e)
	{
		for (int i = 0; i < MAXPLAYERS; i++) Give(i);
	}
}
