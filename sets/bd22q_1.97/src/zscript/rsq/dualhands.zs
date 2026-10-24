// RS VR hands for DUAL WIELD (2026-10-16, owner). A gun moved into the off hand takes the off
// hand from RSQ_Hands, and with it every hand RSQ_Hands draws. So while a gun is in the off hand:
//   - each gun (off hand, and main hand) is held by our posed hand, finger on the trigger,
//     squeezing while that hand fires (off: BT_OFFHANDATTACK, main: BT_ATTACK);
//   - the hand is a layer CALLED BY THE GUN, because only the off-hand weapon may draw on the
//     off controller (models.cpp); its model is a block of the gun's own class (MODELDEF.rsqdual,
//     the gun's hook baked into Offset), so no ModifyBobLayer3D is needed;
//   - RSQ_Hands' own layers are cleared (they would sit wrong without it). It puts them back
//     when it returns to the off hand.
// The hands do not follow the guns' recoil kick here. rsq_hands 0 hides them, as everywhere.
class RSQ_DualHands : EventHandler
{
	const OFFGUN = 2300;
	const MAINGUN = 2301;

	override void WorldTick()
	{
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo)
				continue;
			let mo = players[n].mo;
			let p = mo.player;
			let off = p.OffhandWeapon;
			bool dual = off && !(off is 'RSQ_Hands') && p.playerstate == PST_LIVE && RSQ_Hands.Shown(mo);
			let gs = RSQ_Hands(mo.FindInventory('RSQ_Hands'));	// it holds the hand states (DTrg..)
			if (dual)
			{
				Clear(p, RSQ_Layers.GUNHAND);
				Clear(p, RSQ_Layers.SUPPORT);
				Clear(p, RSQ_Layers.FREEHAND);
			}
			Hand(p, OFFGUN, dual ? off : null, gs, (p.cmd.buttons & BT_OFFHANDATTACK) != 0);
			Hand(p, MAINGUN, dual ? p.ReadyWeapon : null, gs, (p.cmd.buttons & BT_ATTACK) != 0);
		}
	}

	static void Clear(PlayerInfo p, int id)
	{
		if (p.FindPSprite(id))
			p.SetPsprite(id, null);
	}

	static void Hand(PlayerInfo p, int id, Weapon w, RSQ_Hands gs, bool firing)
	{
		// 1.4: not only guns -- the fists and the VR grenade keep their hand too (MODELDEF.rsqdual)
		String label = "";
		Name cn = w ? w.GetClassName() : 'None';
		if (gs && cn == 'Melee_Attacks')
			label = "DFist";
		else if (gs && cn == 'HandGrenades')
		{
			let g = p.FindPSprite(id == MAINGUN ? PSP_WEAPON : PSP_OFFHANDWEAPON);
			if (g && g.Sprite == Actor.GetSpriteIndex('RQNP'))
				label = "DNade";
		}
		else
		{
			int i = w && gs ? RSQ_HandTable.Index(w) : 0;
			if (i > 0 && RSQ_HandTable.GunRot(i) == (0, 0, 0))	// not the axe / chainsaw (turned hands)
			{
				String tf = RSQ_HandTable.Trigger(i);
				label = tf != "" ? (firing ? "DSqz" : "DTrg") .. tf : "DGun" .. RSQ_HandTable.GunOne(i);
			}
		}
		if (label == "")
		{
			Clear(p, id);
			return;
		}
		State st = gs.FindStateByString(label);
		if (!st)
		{
			Clear(p, id);
			return;
		}
		let psp = p.FindPSprite(id);
		if (psp && psp.Caller == w && psp.CurState == st)
			return;
		p.SetPsprite(id, st, false, w);
		psp = p.FindPSprite(id);
		if (psp)
		{
			psp.bAddWeapon = false;
			psp.bAddBob = true;
			psp.y = WEAPONTOP;		// as hands.zs SetLayer: y 0 would tilt the model 8 degrees
			psp.oldy = WEAPONTOP;
		}
	}
}
