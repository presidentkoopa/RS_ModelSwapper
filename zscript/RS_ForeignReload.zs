// =====================================================================
// RS_ForeignReload -- THE JOIN.
//
// ModelSwapper puts one of our meshes on a foreign mod's weapon. The RSR
// runtime can reload one of our meshes with your hands. Nothing connected
// the two, and this is that connection.
//
// The owner, 2026-10-25: "If VR reloading works on one mesh / weapon code,
// it can work on all of them." That is not optimism -- RSR_Guns.SlotForDonor
// keys the reload on the DONOR MODEL, not on the weapon class, so one
// measured mesh is measured for every mod's gun in that slot, forever.
// What was missing was the moment of handover.
//
// WHY A JOIN IS NEEDED AT ALL
//
// A standalone Quest pack owns its weapons, so the kit's generator writes
// the reload's own states straight into each weapon file (genpack.rsr_states,
// rsr_patch): its Reload goes to RSR_Start after the gun's own checks. We own
// no weapon here. The gun belongs to Brutal Doom or Ashes or something
// released next year, and ZScript cannot add a state to a class it does not
// declare. So the handover has to happen from outside, at runtime.
//
// WHAT WE ALREADY KNOW, EVERY TIC
//
//   * which labelled group the weapon's current state belongs to, including
//     `reload` -- RS_ForeignRemap walks the class's ENTIRE label table and
//     attributes every custom label (Work1, ReloadChamber, ReloadDone) to the
//     standard label it was written under. That machinery exists because
//     DECORATE-era mods hide their real animations behind runtime jumps, and
//     it is the hard half of this problem, already solved.
//   * which of our models is in that hand -- the donor cvar.
//   * whether that model has reload data -- RSR_Guns.Index().
//
// WHAT THIS ADDS
//
// When a weapon wearing one of our reloadable meshes enters its own reload
// group, take the psprite and park it on a hold of ours while the hands do
// the physical work. When they finish, put the psprite back at the head of
// the mod's reload group and let the mod's own reload run.
//
// THE MOD'S AMMO STAYS THE MOD'S. We never give, take or count a round.
// vreload.zs already ends this way on a gun it does drive (line ~1176: find
// the weapon's own "Reload" state and SetPsprite into it), and it is the only
// honest option here -- a mod's magazine, reserve, chamber rules and reload
// sounds are its own business. We take the ANIMATION and hand it to your
// hands; the mod still decides what that means for its ammo.
//
// THE STATE CARRIER. A psprite can run states belonging to an actor that is
// not the weapon: SetPsprite(id, state, pending, caller) takes the caller, and
// the runtime already does this -- vreload.zs runs RSR_PartStates' states on
// the part layers. MS_ReloadStates is the same device: a Weapon subclass that
// is never selectable, never auto-switched to and never dropped, existing only
// to own a state table we can point a psprite at.
// =====================================================================

// The hold the gun sits in while your hands work. A Weapon subclass for the
// same reason RSR_PartStates is one: psprite states resolve weapon actions,
// and A_WeaponReady is one of them.
class MS_ReloadStates : Weapon
{
	Default
	{
		+WEAPON.CHEATNOTWEAPON
		+WEAPON.NO_AUTO_SWITCH
		+WEAPON.NOAUTOSWITCHTO
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		+INVENTORY.QUIET
		Weapon.SelectionOrder 32002;	// never chosen; RSR_PartStates uses 32001
	}

	States
	{
	// "####" "#" keeps whatever the weapon layer was already showing, so the
	// gun does not flicker to another sprite at the handover. WRF_NOBOB stops
	// the idle sway fighting the hands; WRF_NOFIRE stops a trigger pull
	// cancelling a reload halfway through, which is what the gun's own reload
	// would do too.
	MS_Hold:
		"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE|WRF_NOSWITCH);
		Loop;
	}
}

class MS_ReloadJoin : EventHandler
{
	// Where each player's weapon was when we took the psprite, so it can be
	// put back exactly there. 0 = not driving.
	private State mReturn[MAXPLAYERS];
	private Weapon mHeld[MAXPLAYERS];

	// The remap for (weapon class, donor) -- the same object the model layer
	// uses, found the way the handler finds it.
	private RS_ForeignRemap RemapFor(PlayerPawn mo, Weapon w)
	{
		let h = RS_ForeignModelHandler(StaticEventHandler.Find("RS_ForeignModelHandler"));
		if (!h || !w)
			return null;
		// LOOK UP ONLY. MapFor() builds one when it finds none, and building needs the
		// frame count and rest frame that only the model layer knows; a map built here
		// with the wrong numbers would be worse than none. If the model layer has not
		// built one yet, there is no model drawn yet and nothing to join.
		string cn = w.GetClassName();
		string donor = RSR_Guns.DonorInHand(0);
		for (int k = 0; k < h.mMaps.Size(); ++k)
			if (h.mMaps[k].clsName == cn && h.mMaps[k].donor == donor)
				return h.mMaps[k];
		return null;
	}

	// Is this state part of the weapon's RELOAD group, as RS_ForeignRemap
	// attributed it? This is the question the whole join turns on, and it is
	// already answered for every mod, including the ones that hide their real
	// reload behind a custom label.
	private bool InReloadGroup(RS_ForeignRemap m, State s)
	{
		if (!m || !s)
			return false;
		int row = m.LookupIndex(s);
		if (row < 0 || row >= m.mGroupId.Size())
			return false;
		int gid = m.mGroupId[row];
		return gid >= 0 && gid < m.mGroups.Size() && m.mGroups[gid].clipName == "reload";
	}

	// The head of that group: where the mod's own reload starts. We put the
	// psprite back here when the hands are done, so the mod's reload runs in
	// full -- its animation, its sounds, its ammo.
	private State ReloadHead(RS_ForeignRemap m, Weapon w)
	{
		// The weapon's own Reload label when it has one; it is the head of the
		// group by construction (RS_ForeignRemap opens the reload group on it).
		let rs = w.FindState("Reload");
		return rs;
	}

	override void WorldTick()
	{
		for (int i = 0; i < MAXPLAYERS; i++)
		{
			if (!playeringame[i] || !players[i].mo)
				continue;
			let mo = PlayerPawn(players[i].mo);
			if (!mo || !mo.player)
				continue;
			let p = mo.player;
			let w = p.ReadyWeapon;

			// Dropped the weapon, died, or switched mid-reload: let go cleanly
			// rather than hold a psprite for a gun that is no longer in hand.
			if (mHeld[i] && (!w || w != mHeld[i] || mo.health <= 0))
			{
				Release(p, i, false);
				continue;
			}
			if (!w)
				continue;

			// Only a weapon wearing one of OUR meshes, and only a mesh whose
			// reload we have actually measured. Everything else is untouched,
			// which is the whole of the mod's arsenal on day one.
			int slot = RSR_Guns.Index(w);
			if (slot <= 0)
			{
				if (mHeld[i]) Release(p, i, false);
				continue;
			}
			if (!RSR_ReloadHandler.WantsHands(mo))	// VR off, or reloading set to Stock
			{
				if (mHeld[i]) Release(p, i, false);
				continue;
			}

			let psp = p.FindPSprite(PSP_WEAPON);
			if (!psp)
				continue;

			if (mHeld[i])
			{
				// Driving. The hands are working; wait for the reload to say it
				// is finished, then give the gun back to the mod at the head of
				// its own reload so IT does the ammo.
				if (mo.CountInv('RSR_Done') > 0)
				{
					mo.TakeInventory('RSR_Done', 1);
					Release(p, i, true);
				}
				continue;
			}

			// Not driving yet. Has the mod's weapon just entered its reload?
			let m = RemapFor(mo, w);
			if (!InReloadGroup(m, psp.CurState))
				continue;

			Take(mo, p, i, w, psp);
		}
	}

	// Take the psprite: remember where the weapon was, park it on our hold,
	// and start the reload the hands drive.
	private void Take(PlayerPawn mo, PlayerInfo p, int i, Weapon w, PSprite psp)
	{
		let shim = MS_ReloadStates(mo.FindInventory('MS_ReloadStates'));
		if (!shim)
		{
			mo.GiveInventory('MS_ReloadStates', 1);
			shim = MS_ReloadStates(mo.FindInventory('MS_ReloadStates'));
		}
		if (!shim)
			return;
		mReturn[i] = psp.CurState;
		mHeld[i] = w;
		// RSR_Start is what vreload watches for; it answers with RSR_Go when it
		// is willing to take the reload, and the hands take over from there.
		mo.GiveInventory('RSR_Start', 1);
		p.SetPsprite(PSP_WEAPON, shim.FindState("MS_Hold"), false, shim);
		if (RS_ForeignRemap.DebugOn())
			Console.Printf("[MSJOIN] took %s (slot %d) at its reload", w.GetClassName(), RSR_Guns.Index(w));
	}

	// Give it back. `finished` means the hands completed the reload, so the mod
	// runs its own reload from the top; otherwise put the psprite exactly where
	// it was, because nothing happened.
	private void Release(PlayerInfo p, int i, bool finished)
	{
		let w = mHeld[i];
		mHeld[i] = null;
		State back = mReturn[i];
		mReturn[i] = null;
		if (!w || !p)
			return;
		State go = null;
		if (finished)
			go = w.FindState("Reload");
		if (!go)
			go = back;
		if (!go)
			go = w.GetReadyState();
		if (go)
			p.SetPsprite(PSP_WEAPON, go, false, w);
		if (RS_ForeignRemap.DebugOn())
			Console.Printf("[MSJOIN] gave %s back (%s)", w.GetClassName(),
				finished ? "hands finished -- the mod's own reload runs" : "let go");
	}
}
