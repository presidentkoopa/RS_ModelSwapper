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
	// NO ACTION FUNCTION, deliberately. A state's action is compiled against the
	// class that owns the state, so running it with the mod's weapon as the caller
	// fails the type check at runtime:
	//     Invalid class RwPistol in function call to MS_ReloadStates.StateFunction.0
	// RSR_PartStates gets away with an arbitrary caller for exactly this reason --
	// its state is `TNT1 A -1;` and calls nothing.
	//
	// And nothing is lost. A_WeaponReady is what lets a weapon fire, bob and be
	// switched away from; a psprite parked on a plain ticking state does none of
	// those, which IS the hold. The gun sits still in your hands while they work.
	MS_Hold:
		"####" "#" 1;
		Loop;
	}
}

class MS_ReloadJoin : EventHandler
{
	// Where each player's weapon was when we took the psprite, so it can be
	// put back exactly there. 0 = not driving.
	private State mReturn[MAXPLAYERS];
	private Weapon mHeld[MAXPLAYERS];
	private State mLastSeen[MAXPLAYERS];   // trace: only speak when the state changes
	// ARMED. Handing the gun back puts it at the HEAD of the mod's own reload --
	// which is exactly the thing this watches for, so it took the gun straight back
	// and the reload looped forever. After a release we stay disarmed until the
	// weapon has left its reload entirely, which is the mod's reload finishing.
	private bool mDisarmed[MAXPLAYERS];
	// FIX 4 (owner, 2026-10-27): the hands start only once the mod's reload has COMMITTED. Took at
	// the reload entry, the mod's own refusal checks (mag full, no reserve, purist, zoomed) have not
	// run yet; RSR_Start / RSR_MagOut / RSR_Charge wait in mPending until the mod's ammo moves or
	// its psprite rests on a ticking state of its reload (not an inspect, fidget or aim branch).
	private bool mPending[MAXPLAYERS];
	private int mAmmo1At[MAXPLAYERS];
	private int mAmmo2At[MAXPLAYERS];

	// THE PUMP (a tube-fed shotgun, RSP_Guns). A pack that owns its shotguns writes a loading
	// loop that waits for the hand and, per shell the hand pushes home, runs its own one-shell
	// step. A foreign shotgun has no such loop -- but its own reload almost always IS one: a
	// loop that puts one shell in per pass. So the hand PACES the mod's own loop: the gun is
	// held while the hand fetches a shell; a shell pushed home lets the mod's reload run until
	// its tube count rises by one; then it is held again, right where it stopped. The mod
	// decides every shell -- whether there is room, what it costs, what it sounds like.
	const FEED_LIMIT = 140;					// tics a shell may take in the mod's own loop
	private bool mFeeding[MAXPLAYERS];		// the mod's loop is running for one shell
	private int mTube[MAXPLAYERS];			// the tube count when that shell was let through
	private int mFeedTics[MAXPLAYERS];
	private Weapon mFeedW[MAXPLAYERS];

	// HOW THE MOD LOADS ITS TUBE (owner, 2026-10-26, item 2). Read from the mod's own states as they
	// run, the first time each weapon class reloads, and remembered for the session:
	//   PACED  its reload is a loop that puts ONE shell in per pass (TMShotgun, BD22's InsertingShells)
	//          -- interruptible, so the hand paces it shell by shell as before;
	//   WHOLE  its reload fills the tube in one go (DoomAblo's A_MagazineReload) -- the mod's reload
	//          runs first, then the gun is held, no fire, until the hand has pushed that many shells.
	// QuestZDoom 17.3's static build has no label table to walk (RS_Fork.CountLabels is a stub there)
	// and a DECORATE loop's jumps live in action arguments, so the evidence is the run itself: the
	// tube count (or, for a mod whose tube is a field, its reserve) the first time it moves, and
	// whether the psprite then goes back to an earlier state of the same reload.
	const KIND_PACED = 1;
	const KIND_WHOLE = 2;
	private Array<Name> mKindCls;
	private Array<int> mKind;
	private bool mProbe[MAXPLAYERS];		// the mod's reload runs while we learn which kind it is
	private int mProbeTics[MAXPLAYERS];
	private int mRise[MAXPLAYERS];			// tube rise / reserve drop since the press
	private int mRes0[MAXPLAYERS];
	private int mFurthest[MAXPLAYERS];		// the deepest state offset into its reload seen this pass
	private bool mWhole[MAXPLAYERS];		// WHOLE: the mod's reload runs / ran; the hand owes mOwe shells
	private int mOwe[MAXPLAYERS];
	private int mPaidFirst[MAXPLAYERS];		// PACED, learnt on this reload: shells the mod's loop put in while we watched

	// THE PUMP AFTER A SHOT (owner, 2026-10-25: "Hold at the mod's pump"). A pack that owns its
	// shotgun calls RSP_PumpStart from its fire states at its pump. A foreign shotgun's pump is in
	// ITS fire states, which we cannot edit -- so the join finds the point from outside: the mod's
	// fire chain walked from its Fire label, and the tic at which the donor model's pump starts in
	// its own fire animation (RSP_Rack.Frac, measured from the mesh by tools_kit/rack_frac.py --
	// the same by-tic laying of a donor's clip over a mod's states the model animation uses).
	// At that point, with the off hand on the pump, the gun is held and the hand works the pump
	// (RSP's own stroke: track, back and forward sounds, the spent shell). Then the mod's own fire
	// states carry on from exactly there -- its pump, its sounds, its refire. Hand off the pump:
	// no hold, the mod pumps by itself, unchanged.
	private Weapon mShotW[MAXPLAYERS];		// the weapon the hold point was found for
	private State mShotPre[MAXPLAYERS];		// hold at the END of this state ...
	private State mShotAt[MAXPLAYERS];		// ... and the mod's fire goes on from this one
	private bool mShot[MAXPLAYERS];			// held for the hand's pump stroke

	// MOD FIRST (owner, 2026-10-26: "when we press the reload button, we want the code to advance
	// to the end of its reload state, but not complete / allow the player to fire, until the player
	// finishes the physical VR reload sequence"). Options: Reload Order (ms_mod_first, on). The
	// hands' reload starts at the press as before, but the gun is NOT parked: the mod's own reload
	// runs at once, to its end (its ammo, its rules, its sounds). Where it leaves its reload the
	// gun is parked -- no A_WeaponReady, no fire -- until the hands say done; then it goes on from
	// exactly that state. Off: the old order (held at the press, the mod's reload after the hands).
	private bool mDriving[MAXPLAYERS];		// the hands' reload is running beside the mod's
	private Weapon mDrivW[MAXPLAYERS];
	private int mDrivTic[MAXPLAYERS];

	// Is the join running the hands' reload beside the mod's own for this gun (mod first, before the
	// park)? The reloads draw the gun without its moving parts while it is parked (RSR.InHold); with
	// the mod's reload running first the psprite is on the MOD's states, so they ask this too, or the
	// gun would show its magazine / its shut barrels while the hand holds the same part.
	clearscope static bool Drives(PlayerInfo p, Weapon w)
	{
		let h = MS_ReloadJoin(EventHandler.Find('MS_ReloadJoin'));
		if (!h || !p || !w || !p.mo)
			return false;
		int n = p.mo.PlayerNumber();
		return n >= 0 && n < MAXPLAYERS && h.mDriving[n] && !h.mPending[n] && h.mDrivW[n] == w;
	}

	// The model handler's own answer for the main hand (it runs first: a StaticEventHandler) against
	// the published cvar the reload tables read. Equal once the cvar has caught up.
	private bool DonorSettled()
	{
		let h = RS_ForeignModelHandler(StaticEventHandler.Find("RS_ForeignModelHandler"));
		if (!h)
			return true;
		String want = h.mBridgeHasMain ? h.mBridgeDonorMain : "";
		return RSR_Guns.DonorInHand(0) == want;
	}

	// A trace for the one failure mode that looks like nothing happening.
	private bool ms_join_trace;
	override void OnRegister() { let c = CVar.FindCVar('ms_join_trace'); ms_join_trace = c && c.GetInt() != 0; }

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
	// TWO ROUTES, because the remap only exists on one of the two builds.
	//
	// The thorough one is RS_ForeignRemap: it attributes every state, including a
	// DECORATE mod's custom reload labels, to the group it was written under. That
	// is the right answer and it catches a mod that jumps straight into Work1 or
	// ReloadChamber without passing through Reload:.
	//
	// But the STATIC build -- the Quest one -- draws models without animating them,
	// so it builds no remaps at all ("[RSRM] scan ... STATIC BUILD -- no animation"),
	// and the whole detection came back `remap NONE`. There the entry itself is
	// enough: we take over AT the handover, not part way through, and a weapon
	// entering its own Reload label is exactly that moment.
	// A RELOAD LABEL THAT IS REALLY THE GUN'S READY LOOP IS NOT A RELOAD (owner, 2026-10-27, fix 2).
	// BD22 names its idle loop Reload on guns with no reload of their own: FlameCannon.dec
	// `Ready: Ready3: Reload:` on one state, Flamethrower.dec `ReadyDry: Reload:` (its out-of-fuel idle
	// loop, which ends in Loop). Taken as a reload entry, the magazine dropped on select, the gun was
	// held with no fire, and once the hands finished it re-armed and dropped again after every shot
	// (triage, 2026-10-27). The test, per class, cached: the Reload state IS the Ready state or lies in
	// its run (State.InStateSequence), or the Reload label's own chain (fall-through and gotos, no
	// action jumps) comes back to the Reload state itself within 64 states -- an idle loop. A real
	// reload runs on to Ready and stays there. Such a gun reloads only through a real reload path,
	// or not at all by hand.
	private Array<Name> mRdyCls;
	private Array<bool> mRdyIs;
	private bool ReloadIsReady(Weapon w)
	{
		if (!w)
			return false;
		Name cn = w.GetClassName();
		int k = mRdyCls.Find(cn);
		if (k < mRdyCls.Size())
			return mRdyIs[k];
		bool rdy = false;
		let rs = w.FindState("Reload");
		State r = w.GetReadyState();
		if (rs && r)
		{
			if (rs == r || rs.InStateSequence(r))
				rdy = true;
			else
			{
				State s = rs;
				for (int n = 0; n < 64 && s; n++)
				{
					s = s.NextState;
					if (s == rs) { rdy = true; break; }
					if (s && s.InStateSequence(r)) break;		// reached its Ready: a real reload
				}
			}
		}
		mRdyCls.Push(cn);
		mRdyIs.Push(rdy);
		if (rdy && RS_ForeignRemap.DebugOn())
			Console.Printf("[MSJOIN] %s: its Reload label rdy its Ready loop -- not a reload entry; no hand reload on it", cn);
		return rdy;
	}

	private bool InReload(RS_ForeignRemap m, Weapon w, State s)
	{
		if (ReloadIsReady(w))
			return false;
		return InReloadGroup(m, s) || AtReloadEntry(w, s);
	}

	private bool AtReloadEntry(Weapon w, State s)
	{
		if (!w || !s)
			return false;
		if (ReloadIsReady(w))
			return false;
		let rs = w.FindState("Reload");
		if (!rs)
			return false;
		// NOT just `s == rs`. A reload label's first state is very often 0 tics --
		// a check, a jump, a sound -- so by the time WorldTick looks the psprite has
		// already walked past it and the entry is missed every time. Walk the chain
		// forward instead and ask whether the psprite is anywhere in the opening run
		// of the mod's own reload. 64 is well past any opening sequence and stops
		// dead on a loop, so a mod with a long reload costs nothing.
		// NOT a NextState walk: that runs clean past the end of the reload block into
		// whatever was declared after it, so the gun's own Ready loop measured as "in
		// the reload" on every tic. DistanceTo gives the state's offset inside the
		// class's own state array, which is bounded and does not wander.
		int d = rs.DistanceTo(s);
		return d >= 0 && d < ReloadEnd(w, rs);
	}

	// WHERE THE MOD'S RELOAD BLOCK ENDS, as a state offset from its Reload label. Its own reload
	// labels (BD22's ReloadNormally / InsertingShells / InsertShellAnimation / TurboReload) follow it
	// in source order; the block ends at the first STANDARD label declared after it. The static build
	// cannot enumerate a class's labels (RS_Fork.CountLabels is a stub there), but it can look these
	// names up, and DistanceTo gives where each sits. 32 was the old fixed window: BD22's Shot_Gun
	// reaches its first tic ~45 states in (rig: the join never took it). Never below 32; at most 256.
	private Array<Name> mEndCls;
	private Array<int> mEndAt;
	private int ReloadEnd(Weapon w, State rs)
	{
		Name cn = w.GetClassName();
		int k = mEndCls.Find(cn);
		if (k < mEndCls.Size())
			return mEndAt[k];
		static const String after[] = { "Ready", "Fire", "AltFire", "Hold", "AltHold", "Select", "Deselect", "Flash",
			"AltFlash", "Spawn", "Death", "Zoom", "User1", "User2", "User3", "User4", "Unload", "Steady" };
		int end = 256;
		for (int n = 0; n < after.Size(); n++)
		{
			let st = w.FindStateByString(after[n], true);
			int d = st ? rs.DistanceTo(st) : -1;
			if (d > 0 && d < end)
				end = d;
		}
		end = max(end, 32);
		mEndCls.Push(cn);
		mEndAt.Push(end);
		if (RS_ForeignRemap.DebugOn())
			Console.Printf("[MSJOIN] %s: its reload block is %d states from its Reload label", cn, end);
		return end;
	}

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
			if (mDriving[i] && (!w || w != mDrivW[i] || mo.health <= 0))
			{
				mDriving[i] = false;
				mHeld[i] = null;
				mReturn[i] = null;
				mDrivW[i] = null;
				mo.TakeInventory('RSR_Charge', 999);
			}
			if (mHeld[i] && (!w || w != mHeld[i] || mo.health <= 0))
			{
				Release(p, i, false);
				continue;
			}
			if (!w)
				continue;

			// THE DONOR MUST BE THIS GUN'S. Every reload table keys on ms_donor_main, a `server`
			// cvar, and a server cvar set from script reaches its value through the net queue
			// (D_SendServerInfoChange: DEM_SINFCHANGED), a tic or more after the model handler
			// published it. A gun switched to and reloaded at once (BD22's GrenadeLauncher, fired
			// empty the tic it came up) was taken under the PREVIOUS gun's model: the rig showed
			// "took GrenadeLauncher (slot 17)" -- MS_alien_rifle, the BD22 Rifle's model -- and a
			// magazine reload on a break-open gun. Not driving yet: wait until the cvar says what
			// the handler says. Its reload entry is a 32-state window, so a tic or two is not missed.
			if (!mHeld[i] && !mDriving[i] && !mFeeding[i] && !DonorSettled())
				continue;

			// Only a weapon wearing one of OUR meshes, and only a mesh whose
			// reload we have actually measured. Everything else is untouched,
			// which is the whole of the mod's arsenal on day one.
			int slot = RSR_Guns.Index(w);
			int pslot = slot > 0 ? 0 : RSP_Guns.Index(w);
			int bslot = slot > 0 || pslot > 0 ? 0 : RSB_Guns.Index(w);
			if (mFeeding[i] && mFeedW[i] != w)
				mFeeding[i] = false;			// switched away mid-shell: the mod's own business now
			if ((mProbe[i] || mWhole[i]) && mFeedW[i] != w)
			{
				if (mHeld[i] && players[i].mo)
					Release(p, i, false);
				mProbe[i] = mWhole[i] = false;
				mOwe[i] = 0;
			}
			if (slot <= 0 && pslot <= 0 && bslot <= 0)
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

			if (pslot > 0)
			{
				PumpTick(mo, p, i, w, psp);
				continue;
			}
			if (bslot > 0)
			{
				BreakTick(mo, p, i, w, psp);
				continue;
			}

			if (mDriving[i])
			{
				ModFirstTick(mo, p, i, w, psp);
				continue;
			}

			if (mHeld[i])
			{
				// THE HEARTBEAT. vreload gives a reload three tics of silence before
				// it decides the gun has left and tears everything down:
				//     gone = ... || now - s.lastTick > 2
				// A generated weapon's RSR_Wait keeps it alive with
				// `A_GiveInventory("RSR_Tick", 1)` every tic. Our hold state cannot
				// call an action at all -- its caller is the mod's weapon, and a
				// state's action is compiled against the class that owns the state.
				// So the handler gives the tick instead. Same token, same effect, from
				// the one place here that is allowed to.
				//
				// Without this the reload ran for exactly three tics and aborted:
				//     rsr t201 gun 15: IDLE -> EMPTY
				//     rsr t204: the gun left the reload (EMPTY)
				mo.GiveInventory('RSR_Tick', 1);

				// SEATED is the magazine home -- the hands are finished. On a generated
				// weapon, RSR_Wait jumps to RSR_Fill here, which moves rounds from the
				// reserve into the magazine and answers RSR_Filled. We do neither: the
				// ammo is the MOD's, and the mod is about to run its own reload and do
				// exactly that in its own terms. So take the token, tell the reload the
				// magazine is filled so it closes out its own bookkeeping, and hand the
				// gun back.
				if (mo.CountInv('RSR_Seated') > 0)
				{
					mo.TakeInventory('RSR_Seated', 1);
					mo.GiveInventory('RSR_Filled', 1);
					// a gun that ran dry goes on to its charging handle (RSR_Charge, given at
					// Take): the hold stays until the hand has racked it and the reload says
					// RSR_Done. Handed back here, the reload saw its gun leave and dropped the
					// handle (CHARGE -> IDLE: every handle on a foreign gun, the gate showed).
					let rs = RSR_ReloadHandler.StateOf(mo);
					if (rs && rs.phase == RSR.CHARGE)
						continue;
					Release(p, i, true);
					continue;
				}

				// Or the reload says it is done by itself (it was cancelled, or a gun
				// whose sequence ends elsewhere).
				if (mo.CountInv('RSR_Done') > 0)
				{
					mo.TakeInventory('RSR_Done', 1);
					Release(p, i, true);
				}
				continue;
			}

			// Not driving yet. Has the mod's weapon just entered its reload?
			let m = RemapFor(mo, w);
			bool inReload = InReload(m, w, psp.CurState);
			if (mDisarmed[i])
			{
				// Re-arm only once the mod's own reload has run its course and the gun
				// is back to whatever it does normally.
				if (!inReload)
					mDisarmed[i] = false;
				continue;
			}
			if (!inReload)
			{
				// WHY NOT. A join that silently does nothing is the hardest kind of
				// bug to see -- it looks exactly like a gun that is not reloading.
				// One line per state change, only for a weapon that HAS a slot, so
				// it is quiet on an arsenal we do not drive.
				if (ms_join_trace && psp.CurState != mLastSeen[i])
				{
					mLastSeen[i] = psp.CurState;
					int row = m ? m.LookupIndex(psp.CurState) : -2;
					string clip = "-";
					if (m && row >= 0 && row < m.mGroupId.Size())
					{
						int gid = m.mGroupId[row];
						if (gid >= 0 && gid < m.mGroups.Size()) clip = m.mGroups[gid].clipName;
					}
					Console.Printf("[MSJOIN] %s slot %d: remap %s row %d clip '%s'",
						w.GetClassName(), slot, m ? "found" : "NONE", row, clip);
				}
				continue;
			}

			Take(mo, p, i, w, psp);
		}
	}

	// Take the psprite: remember where the weapon was, park it on our hold,
	// and start the reload the hands drive.
	private void Take(PlayerPawn mo, PlayerInfo p, int i, Weapon w, PSprite psp)
	{
		// The hold state off the CLASS DEFAULT -- nothing is given to the player.
		// GiveInventory of a Weapon subclass silently fails (Weapon.TryPickup has its
		// own rules), which is why this used to return here having done nothing at all.
		// The caller stays the mod's OWN weapon, so A_WeaponReady in the hold holds
		// that gun, and the psprite still belongs to the weapon it came from.
		State hold = GetDefaultByType('MS_ReloadStates').FindState("MS_Hold");
		if (!hold)
			return;
		mReturn[i] = psp.CurState;
		mHeld[i] = w;
		if (RSR.PlayerInt(p, 'ms_mod_first', 1) != 0)
		{
			// mod first: nothing is given to the hands until the mod's reload commits (CommitTick)
			mReturn[i] = null;
			mHeld[i] = null;
			mDriving[i] = true;
			mPending[i] = true;
			mDrivW[i] = w;
			mDrivTic[i] = mo.Level.maptime;
			mAmmo1At[i] = w.AmmoType1 ? mo.CountInv(w.AmmoType1) : 0;
			mAmmo2At[i] = w.AmmoType2 ? mo.CountInv(w.AmmoType2) : 0;
			if (RS_ForeignRemap.DebugOn())
				Console.Printf("[MSJOIN] %s at its reload entry -- waiting for the mod's reload to commit", w.GetClassName());
			return;
		}
		StartHands(mo, p, i, w);
		p.SetPsprite(PSP_WEAPON, hold, false, w);
		if (RS_ForeignRemap.DebugOn())
			Console.Printf("[MSJOIN] took %s (slot %d) at its reload", w.GetClassName(), RSR_Guns.Index(w));
	}

	// The hands' reload starts: what a pack's own weapon would send from its Reload.
	private void StartHands(PlayerPawn mo, PlayerInfo p, int i, Weapon w)
	{
		// RSR_Start is what vreload watches for; it answers with RSR_Go when it is
		// willing to take the reload, and the hands take over from there.
		mo.GiveInventory('RSR_Start', 1);
		// AND THE MAGAZINE COMES OUT. A pack that owns its guns sends RSR_MagOut from the
		// weapon's own reload, right after RSR_Start (BD22 Pistol.dec RSR_Out) -- unless its
		// gun already has no magazine in. That is what plays the magazine-out sound, drops the
		// old magazine and shows the empty well (the DROP phase). Nothing sent it here, so a
		// ModelSwapper reload went from IDLE straight to EMPTY: no drop, no sound. The join
		// plays the weapon's part. NoMag is the reload's own "no magazine in" flag.
		class<Inventory> nm = RSR_Guns.NoMag(RSR_Guns.Index(w));
		if (!nm || mo.CountInv(nm) <= 0)
			mo.GiveInventory('RSR_MagOut', 1);
		// AND THE HANDLE WHEN IT RAN DRY. A pack that owns its guns gives RSR_Charge from its
		// reload when the chamber is empty (BD22: the gun shot dry), and the reload then asks the
		// hand to work the charging handle after the magazine is in (ChargeRule 1). Nothing gave
		// it here, so no foreign gun's handle was ever asked for. The mod's own magazine count is
		// the evidence, read and never changed: empty, nothing is chambered.
		let mag = RSR.WeaponStore(mo, false);
		mo.TakeInventory('RSR_Charge', 999);
		if (mag && mag.Amount <= 0 && RSR_Guns.HasHandle(RSR_Guns.Index(w)) && RSR.PlayerInt(p, 'ms_charge_dry', 1) != 0)
			mo.GiveInventory('RSR_Charge', 1);
	}

	// Has the mod's reload committed? Its ammo moved, or its psprite rests (tics > 0) on a state of
	// its reload block that is not one of BD22's non-reload branches inside that block.
	private bool Committed(PlayerPawn mo, int i, Weapon w, PSprite psp)
	{
		int a1 = w.AmmoType1 ? mo.CountInv(w.AmmoType1) : 0;
		int a2 = w.AmmoType2 ? mo.CountInv(w.AmmoType2) : 0;
		if (a1 != mAmmo1At[i] || a2 != mAmmo2At[i])
			return true;
		State s = psp.CurState;
		if (!s || psp.Tics <= 0 || !AtReloadEntry(w, s))
			return false;
		static const String notReload[] = { "Inspect", "Inspect2", "InspectHold", "Fidget", "ContinueFidget",
			"PuristWarning", "NoAim", "IsHolding", "HoldAim", "HoldingAim", "NoAmmo", "Ready", "Ready3" };
		for (int n = 0; n < notReload.Size(); n++)
		{
			let ns = w.FindStateByString(notReload[n], true);
			if (ns && s.InStateSequence(ns))
				return false;
		}
		return true;
	}

	private void ModFirstTick(PlayerPawn mo, PlayerInfo p, int i, Weapon w, PSprite psp)
	{
		if (w != mDrivW[i] || mo.health <= 0)
		{
			// switched away or died: the hands' reload sees its gun leave and ends itself
			ModFirstEnd(mo, p, i, w, psp, "the gun left");
			return;
		}
		if (mPending[i])
		{
			let m0 = RemapFor(mo, w);
			if (Committed(mo, i, w, psp))
			{
				mPending[i] = false;
				mDrivTic[i] = mo.Level.maptime;
				StartHands(mo, p, i, w);
				if (RS_ForeignRemap.DebugOn())
					Console.Printf("[MSJOIN] took %s (slot %d) at its reload -- the mod's reload runs first", w.GetClassName(), RSR_Guns.Index(w));
			}
			else if (!InReload(m0, w, psp.CurState) || mo.Level.maptime - mDrivTic[i] > 70)
			{
				// the mod refused (full, no reserve, an inspect): the hands never start
				mPending[i] = false;
				mDriving[i] = false;
				mDrivW[i] = null;
				mDisarmed[i] = InReload(m0, w, psp.CurState);
				if (RS_ForeignRemap.DebugOn())
					Console.Printf("[MSJOIN] %s: the mod's reload did not commit -- no hand reload", w.GetClassName());
			}
			return;
		}
		mo.GiveInventory('RSR_Tick', 1);		// the heartbeat (see the hold path)
		let rs = RSR_ReloadHandler.StateOf(mo);
		if (rs && rs.phase == RSR.IDLE && mo.Level.maptime - mDrivTic[i] > 4)
		{
			// the reload declined (or is over without a word): nothing to wait for
			ModFirstEnd(mo, p, i, w, psp, "the hands' reload is not running");
			return;
		}
		let m = RemapFor(mo, w);
		bool inReload = InReload(m, w, psp.CurState);
		// PARK ON THE WAY OUT, not after. The mod's reload ends into its Ready, whose A_WeaponReady fires
		// at once with the trigger still held (real play: the gun shot dry, trigger down, its Fire went to
		// its Reload) -- parked a tic later, one shot had already gone (rig: "SHOT 32 t447" right at the
		// park). On the last tic of a reload state whose 0-tic chain leaves the reload, park now and go
		// on from its next state when the hands finish.
		State exitTo = null;
		if (!mHeld[i] && inReload && psp.Tics <= 1)
			exitTo = LeavesReload(m, w, psp.CurState.NextState);
		if (!mHeld[i] && (exitTo || !inReload) && psp.CurState != GetDefaultByType('MS_ReloadStates').FindState("MS_Hold"))
		{
			// the mod's reload has run to its end: park the gun there, no fire, until the hands finish
			State hold = GetDefaultByType('MS_ReloadStates').FindState("MS_Hold");
			if (hold)
			{
				mReturn[i] = exitTo ? psp.CurState.NextState : psp.CurState;
				mHeld[i] = w;
				p.SetPsprite(PSP_WEAPON, hold, false, w);
				if (RS_ForeignRemap.DebugOn())
					Console.Printf("[MSJOIN] %s: the mod's reload is done -- held, no fire, until the hands finish (at %d of its reload, tics %d)", w.GetClassName(), w.FindState("Reload") ? w.FindState("Reload").DistanceTo(mReturn[i]) : -1, psp.Tics);
			}
		}
		if (mo.CountInv('RSR_Seated') > 0)
		{
			mo.TakeInventory('RSR_Seated', 1);
			mo.GiveInventory('RSR_Filled', 1);
			rs = RSR_ReloadHandler.StateOf(mo);
			if (rs && rs.phase == RSR.CHARGE)
				return;			// the charging handle next
			ModFirstEnd(mo, p, i, w, psp, "hands finished");
			return;
		}
		if (mo.CountInv('RSR_Done') > 0)
		{
			mo.TakeInventory('RSR_Done', 1);
			ModFirstEnd(mo, p, i, w, psp, "hands finished");
		}
	}

	// `s` (the state after the one on its last tic) when it is already OUT of the mod's reload: the
	// reload's last ticking state goes straight to its Ready (BD22: `"####" AA 1 A_ReFire` / `Goto Ready`).
	// Only that direct step counts. A 0-tic chain cannot be walked: its states may jump by action
	// (A_JumpIfInventory) past a Goto that the walk would take for the exit (BD22 SSG RaiseReloading:
	// a false exit 27 states in parked it before it had loaded). Null otherwise.
	private State LeavesReload(RS_ForeignRemap m, Weapon w, State s)
	{
		if (s && !InReload(m, w, s))
			return s;
		return null;
	}

	private void ModFirstEnd(PlayerPawn mo, PlayerInfo p, int i, Weapon w, PSprite psp, String why)
	{
		mDriving[i] = false;
		mPending[i] = false;
		let bs = RSB_Handler.StateOf(mo);
		if (bs)
			bs.paid = false;
		mo.TakeInventory('RSR_Charge', 999);
		bool parked = mHeld[i] != null;
		State go = mReturn[i];
		mHeld[i] = null;
		mReturn[i] = null;
		if (parked && go && w == mDrivW[i])
			p.SetPsprite(PSP_WEAPON, go, false, w);		// on from where the mod's reload left it
		// the mod's reload still running (the hands were quicker): stay off until it ends
		mDisarmed[i] = !parked;
		mDrivW[i] = null;
		if (RS_ForeignRemap.DebugOn())
			Console.Printf("[MSJOIN] gave %s back (%s -- %s)", w ? w.GetClassName() : 'none', why,
				parked ? "fire allowed" : "the mod's reload was still running");
	}

	// Give it back. `finished` means the hands completed the reload, so the mod
	// runs its own reload from the top; otherwise put the psprite exactly where
	// it was, because nothing happened.
	// ---------------------------------------------------------------- break-open
	// A break-open gun or a revolver (RSB_Guns): the hands open it, the spent rounds come out,
	// they load each chamber and close it. The join plays the weapon's part the way it does for
	// a magazine: hold the gun through the hands' whole cycle, then give it to the mod's own
	// reload, which fills its own ammo its own way. The per-round tokens the break reload hands
	// a weapon that owns its reload (RSB_LoadT: run your one-round step; RSB_EjectT: your casing
	// spawns; RSB_TopUpT) have no taker on a foreign gun -- its own reload does all of that when
	// it runs -- so they are cleared here each tic rather than left to pile up.
	private void BreakTick(PlayerPawn mo, PlayerInfo p, int i, Weapon w, PSprite psp)
	{
		if (mHeld[i] || mDriving[i])
		{
			mo.GiveInventory('RSB_Tick', 1);		// the heartbeat a weapon's RSB_Wait would give
			mo.TakeInventory('RSB_EjectT', 999);
			mo.TakeInventory('RSB_LoadT', 999);
			mo.TakeInventory('RSB_TopUpT', 999);
		}
		if (mDriving[i])
		{
			BreakFirstTick(mo, p, i, w, psp);
			return;
		}
		if (mHeld[i])
		{
			if (mo.CountInv('RSB_Done') > 0)
			{
				mo.TakeInventory('RSB_Done', 999);
				Release(p, i, true);
			}
			return;
		}
		let m = RemapFor(mo, w);
		bool inReload = InReload(m, w, psp.CurState);
		if (mDisarmed[i])
		{
			if (!inReload)
				mDisarmed[i] = false;
			return;
		}
		if (!inReload)
			return;
		State hold = GetDefaultByType('MS_ReloadStates').FindState("MS_Hold");
		if (!hold)
			return;
		mo.TakeInventory('RSB_Go', 999);
		mo.TakeInventory('RSB_Done', 999);
		mo.GiveInventory('RSB_Start', 1);
		if (mo.CountInv('RSB_Go') <= 0)
			return;						// the break reload declined (VR off, Stock): the mod's own reload
		mo.TakeInventory('RSB_Go', 999);
		if (RSR.PlayerInt(p, 'ms_mod_first', 1) != 0)
		{
			// MOD FIRST (owner, 2026-10-26: "whenever we press reload, the code does its reload stuff,
			// but prevents us from firing until we do the mesh manipulation stuff"), as for a magazine:
			// the gun is NOT parked at its reload -- the mod's own reload runs now, to its end, with its
			// own ammo -- and BreakFirstTick parks it where that reload leaves off until the hands have
			// opened it, loaded it and shut it.
			let bs = RSB_Handler.StateOf(mo);
			if (bs)
				bs.paid = true;			// the mod pays for these rounds: its reserve is not the hand's limit
			mReturn[i] = null;
			mHeld[i] = null;
			mDriving[i] = true;
			mDrivW[i] = w;
			mDrivTic[i] = mo.Level.maptime;
			if (RS_ForeignRemap.DebugOn())
				Console.Printf("[MSJOIN] took %s (break slot %d) at its reload -- the mod's reload runs first", w.GetClassName(), RSB_Guns.Index(w));
			return;
		}
		mReturn[i] = psp.CurState;
		mHeld[i] = w;
		p.SetPsprite(PSP_WEAPON, hold, false, w);
		if (RS_ForeignRemap.DebugOn())
			Console.Printf("[MSJOIN] took %s (break slot %d) at its reload", w.GetClassName(), RSB_Guns.Index(w));
	}

	// Break-open, mod first: the mod's reload is running (or has run) while the hands open, load and
	// shut the gun. Where the mod's reload ends, the gun is parked -- no A_WeaponReady, so no fire --
	// until RSB_Done; then it goes on from that state. The same park and release as the magazine's
	// ModFirstTick; only the "hands finished" signal differs.
	private void BreakFirstTick(PlayerPawn mo, PlayerInfo p, int i, Weapon w, PSprite psp)
	{
		if (w != mDrivW[i] || mo.health <= 0)
		{
			ModFirstEnd(mo, p, i, w, psp, "the gun left");
			return;
		}
		let bs = RSB_Handler.StateOf(mo);
		if (mo.CountInv('RSB_Done') > 0 || bs && bs.phase == RSB.DONE)
		{
			mo.TakeInventory('RSB_Done', 999);
			ModFirstEnd(mo, p, i, w, psp, "hands finished");
			return;
		}
		if (!bs || bs.phase == RSB.IDLE && mo.Level.maptime - mDrivTic[i] > 4)
		{
			ModFirstEnd(mo, p, i, w, psp, "the hands' reload is not running");
			return;
		}
		State hold = GetDefaultByType('MS_ReloadStates').FindState("MS_Hold");
		if (mHeld[i] || !hold || psp.CurState == hold)
			return;
		let m = RemapFor(mo, w);
		State exitTo = null;
		if (InReload(m, w, psp.CurState))
		{
			// park on the way out (see ModFirstTick): no shot slips through with the trigger held
			if (psp.Tics <= 1)
				exitTo = LeavesReload(m, w, psp.CurState.NextState);
			if (!exitTo)
				return;
		}
		mReturn[i] = exitTo ? psp.CurState.NextState : psp.CurState;
		mHeld[i] = w;
		p.SetPsprite(PSP_WEAPON, hold, false, w);
		if (RS_ForeignRemap.DebugOn())
			Console.Printf("[MSJOIN] %s: the mod's reload is done -- held, no fire, until the hands finish (at %d of its reload, tics %d)", w.GetClassName(), w.FindState("Reload") ? w.FindState("Reload").DistanceTo(mReturn[i]) : -1, psp.Tics);
	}

	// ---------------------------------------------------------------- the pump
	private void PumpTick(PlayerPawn mo, PlayerInfo p, int i, Weapon w, PSprite psp)
	{
		let tube = RSR.WeaponStore(mo, false);
		int have = tube ? tube.Amount : 0;
		int pi = RSP_Guns.Index(w);
		let m = RemapFor(mo, w);
		bool inReload = InReload(m, w, psp.CurState);
		// Once the mod's reload is under way, it is running until its psprite is back in its Ready
		// loop. The entry window (AtReloadEntry, 32 states) is too short for a long DECORATE reload:
		// BD22's InsertShellAnimation is ~45 states past its Reload label, and the static build has
		// no remap to say so.
		bool running = inReload || InReloadBlock(w, psp.CurState) && !AtRest(w, psp.CurState);

		// 0. learning how this mod loads (the first reload of this class), or a whole-tube reload
		if (mProbe[i])
		{
			ProbeTick(mo, p, i, w, psp, have, running);
			return;
		}
		if (mWhole[i])
		{
			WholeTick(mo, p, i, w, psp, running);
			return;
		}

		// 1. the mod's own reload is running for one shell the hand pushed home
		if (mFeeding[i])
		{
			mo.GiveInventory('RSP_LTick', 1);	// the hand keeps loading meanwhile (Shells per grab)
			mFeedTics[i]++;
			if (have > mTube[i])
			{
				mFeeding[i] = false;
				bool more = tube && have < tube.MaxAmount && !RSP.NoReserve(mo, pi);
				if (more && running)
					PumpHold(p, i, w, psp, "a shell in -- held for the next");
				else
					PumpDone(i, w, "tube full or reserve empty -- the mod's own reload finishes");
				return;
			}
			if (!running || mFeedTics[i] > FEED_LIMIT)
			{
				mFeeding[i] = false;
				// the mod's own rule ended its reload (full by its count, out of reserve): the shells
				// still in the hand are not wanted -- the reload's own end puts them away
				let ps = RSP_Handler.StateOf(mo);
				if (ps && ps.mode == RSP.LOAD)
					ps.Abort(mo);
				PumpDone(i, w, !running ? "the mod's reload ended" : "no shell went in");
			}
			return;
		}

		// 2a. held after a shot: the hand works the pump (RSP's stroke), then the mod's fire goes on
		if (mHeld[i] && mShot[i])
		{
			ShotTick(mo, p, i, w);
			return;
		}

		// 2. held: the hands load, and this stands in for the weapon's loading loop
		if (mHeld[i])
		{
			mo.GiveInventory('RSP_LTick', 1);
			if (p.cmd.buttons & BT_ATTACK)
			{
				// fire ends a reload, as it does on BD22's own shotgun
				mHeld[i] = null;
				mDisarmed[i] = true;
				p.SetPsprite(PSP_WEAPON, w.GetReadyState(), false, w);
				Trace(w, "fire -- the gun goes back to ready");
				return;
			}
			if (mo.CountInv('RSP_ShellIn') > 0)
			{
				mo.TakeInventory('RSP_ShellIn', 1);
				if (mPaidFirst[i] > 0)
				{
					// learnt on this reload: a shell the mod put in while we watched is this push's
					mPaidFirst[i]--;
					Trace(w, String.Format("a shell pushed home -- one the mod's loop loaded while it was read (%d more)", mPaidFirst[i]));
					return;
				}
				PumpFeed(p, i, w, have);
			}
			return;
		}

		// 3. idle
		if (mDisarmed[i])
		{
			if (!inReload)
				mDisarmed[i] = false;
			return;
		}
		if (!inReload && ShotWatch(mo, p, i, w, psp))
			return;
		if (inReload)
		{
			mo.TakeInventory('RSP_Go', 999);
			mo.GiveInventory('RSP_LoadStart', 1);
			if (mo.CountInv('RSP_Go') <= 0)
				return;					// the pump runtime declined (VR off, Stock): the mod's own reload
			mo.TakeInventory('RSP_Go', 999);
			int kind = KindOf(w);
			Trace(w, String.Format("took it at its reload (%s)", kind == KIND_PACED ? "one shell per pass: paced by the hand"
				: kind == KIND_WHOLE ? "the whole tube at once: the mod's reload first" : "first reload: the mod's reload shows how it loads"));
			if (kind == KIND_PACED)
			{
				PumpHold(p, i, w, psp, "held for the hand's first shell");
				return;
			}
			// WHOLE, or not known yet: the mod's reload runs now; ProbeTick / WholeTick watch it
			let res = RSR.WeaponStore(mo, true);
			mRise[i] = 0;
			mRes0[i] = res ? res.Amount : 0;
			mTube[i] = have;
			mFurthest[i] = -1;
			mProbeTics[i] = 0;
			mOwe[i] = 0;
			mFeedW[i] = w;
			if (kind == KIND_WHOLE)
				mWhole[i] = true;
			else
				mProbe[i] = true;
			mHeld[i] = null;
			mReturn[i] = null;
			return;
		}
		// a shell pushed straight into the port with no reload under way (the pump runtime's
		// free feed): start the mod's own reload for that one shell
		if (mo.CountInv('RSP_ShellIn') > 0)
		{
			mo.TakeInventory('RSP_ShellIn', 1);
			let rs = w.FindState("Reload");
			if (rs && !(tube && have >= tube.MaxAmount))
			{
				mReturn[i] = rs;
				PumpFeed(p, i, w, have);
			}
		}
	}

	// The mod's fire chain from its Fire label, along the states as written (NextState), to its
	// Ready, a loop or a stop; the hold point is the state the tic RSP_Rack.Frac of the way
	// through falls in. Held at the end of the state before it, so no state's action runs twice
	// and none is skipped: the mod goes on by entering that state, as it would have.
	private void FindShotPoint(int i, Weapon w)
	{
		mShotW[i] = w;
		mShotPre[i] = mShotAt[i] = null;
		double fr = RSP_Rack.Frac(RSR_Guns.DonorInHand(0));
		State st = w.FindState("Fire");
		if (fr < 0 || !st)
			return;
		State ready = w.GetReadyState();
		Array<State> ch;
		int total = 0;
		while (st && ch.Size() < 64 && st != ready && ch.Find(st) == ch.Size() && st.tics >= 0)
		{
			ch.Push(st);
			total += st.tics;
			st = st.NextState;
		}
		if (total < 4 || ch.Size() < 2)
			return;
		double want = fr * total;
		int c = 0;
		for (int k = 1; k < ch.Size(); k++)
		{
			c += ch[k - 1].tics;
			if (c >= want && ch[k - 1].tics >= 1)
			{
				mShotPre[i] = ch[k - 1];
				mShotAt[i] = ch[k];
				Trace(w, String.Format("pump point: tic %d of its fire's %d (%.0f%%, measured on the model)", c, total, fr * 100));
				return;
			}
		}
	}

	private bool ShotWatch(PlayerPawn mo, PlayerInfo p, int i, Weapon w, PSprite psp)
	{
		if (RSR.PlayerInt(p, 'ms_hand_pump', 1) == 0)
			return false;			// Options, VR Reload: Pump by Hand After a Shot off -- the mod pumps by itself
		if (mShotW[i] != w)
			FindShotPoint(i, w);
		if (!mShotPre[i] || psp.CurState != mShotPre[i] || psp.Tics > 1)
			return false;
		// the pump runtime decides whether the hand is on the pump (steadied at it, or the grab
		// held on it); waiting for a hand that is not there is not what was asked for
		mo.GiveInventory('RSP_PumpStart', 1);
		let s = RSP_Handler.StateOf(mo);
		if (!s || s.mode != RSP.PUMPING)
			return false;
		if (s.waitHand)
		{
			s.End(mo);
			return false;			// the hand is off the pump: the mod pumps by itself
		}
		State hold = GetDefaultByType('MS_ReloadStates').FindState("MS_Hold");
		if (!hold)
		{
			s.End(mo);
			return false;
		}
		mReturn[i] = mShotAt[i];
		mHeld[i] = w;
		mShot[i] = true;
		p.SetPsprite(PSP_WEAPON, hold, false, w);
		Trace(w, "after the shot: the hand is on the pump -- held for its stroke");
		return true;
	}

	private void ShotTick(PlayerPawn mo, PlayerInfo p, int i, Weapon w)
	{
		mo.GiveInventory('RSP_PTick', 1);
		// what the stroke tells a weapon that owns it; the mod's own states do all of that
		mo.TakeInventory('RSP_Back', 999);
		mo.TakeInventory('RSP_Fwd', 999);
		mo.TakeInventory('RSP_CaseOut', 999);
		bool ready = mo.CountInv('RSP_Ready') > 0;
		bool byItself = mo.CountInv('RSP_Auto') > 0;
		if (!ready && !byItself)
			return;
		mo.TakeInventory('RSP_Ready', 999);
		mo.TakeInventory('RSP_Auto', 999);
		mShot[i] = false;
		mHeld[i] = null;
		State go = mReturn[i];
		mReturn[i] = null;
		if (go)
			p.SetPsprite(PSP_WEAPON, go, false, w);
		Trace(w, ready ? "pumped by hand -- the mod's fire goes on" : "the hand left the pump -- the mod's fire goes on");
	}

	private void PumpHold(PlayerInfo p, int i, Weapon w, PSprite psp, String why)
	{
		State hold = GetDefaultByType('MS_ReloadStates').FindState("MS_Hold");
		if (!hold)
			return;
		mReturn[i] = psp.CurState;		// the mod's loop resumes exactly here
		mHeld[i] = w;
		p.SetPsprite(PSP_WEAPON, hold, false, w);
		Trace(w, why);
	}

	private void PumpFeed(PlayerInfo p, int i, Weapon w, int have)
	{
		mHeld[i] = null;
		mFeeding[i] = true;
		mFeedW[i] = w;
		mTube[i] = have;
		mFeedTics[i] = 0;
		State go = mReturn[i] ? mReturn[i] : w.FindState("Reload");
		if (go)
			p.SetPsprite(PSP_WEAPON, go, false, w);
		Trace(w, String.Format("a shell pushed home -- the mod's own reload runs for it (tube %d)", have));
	}

	private void PumpDone(int i, Weapon w, String why)
	{
		mPaidFirst[i] = 0;
		mHeld[i] = null;
		mReturn[i] = null;
		mDisarmed[i] = true;
		Trace(w, why);
	}

	// Anywhere in the states declared from the mod's Reload label on (its own reload's labels follow
	// it in source order: BD22's InsertingShells / InsertShellAnimation / FinishedInsertingShells).
	// A state declared before Reload (its Ready, Fire, a pump label) is not its reload.
	private bool InReloadBlock(Weapon w, State s)
	{
		return AtReloadEntry(w, s);
	}

	// back in the weapon's Ready loop (its Ready label's run of states): the mod's reload is over
	private bool AtRest(Weapon w, State s)
	{
		State hold = GetDefaultByType('MS_ReloadStates').FindState("MS_Hold");
		if (!s || s == hold)
			return false;
		State r = w.GetReadyState();
		return r && s.InStateSequence(r);
	}

	private int KindOf(Weapon w)
	{
		Name cn = w.GetClassName();
		int k = mKindCls.Find(cn);
		return k < mKindCls.Size() ? mKind[k] : 0;
	}

	private void SetKind(Weapon w, int kind)
	{
		Name cn = w.GetClassName();
		if (mKindCls.Find(cn) < mKindCls.Size())
			return;
		mKindCls.Push(cn);
		mKind.Push(kind);
		Trace(w, kind == KIND_PACED ? "its reload loads ONE shell per pass (a loop): paced by the hand, shell by shell"
			: "its reload loads the WHOLE tube at once: the mod's reload first, fire held until the hand has pushed as many");
	}

	// how far the mod's reload has moved the ammo since the press: its tube up, or (a tube kept in a
	// field, DoomAblo's currentClipAmmo) its reserve down
	private int Moved(PlayerPawn mo, int i, int have)
	{
		let res = RSR.WeaponStore(mo, true);
		int drop = res ? mRes0[i] - res.Amount : 0;
		return max(have - mTube[i], drop);
	}

	// the first reload of this class: let the mod's own reload run and read how it loads
	private void ProbeTick(PlayerPawn mo, PlayerInfo p, int i, Weapon w, PSprite psp, int have, bool inReload)	// inReload: the mod's reload is still running
	{
		mo.GiveInventory('RSP_LTick', 1);
		mProbeTics[i]++;
		int moved = Moved(mo, i, have);
		let rs = w.FindState("Reload");
		int at = rs && psp.CurState ? rs.DistanceTo(psp.CurState) : -1;
		let tube = RSR.WeaponStore(mo, false);
		bool full = tube && have >= tube.MaxAmount;
		// A loop goes BACK to an earlier state of its reload for its next shell; a whole-tube reload
		// never does. Checked first: BD22's loop jumps back through 0-tic states and gives its next
		// shell in the same tic (rig: tube 1 at t129, 2 at t139), so the count alone reads as "2 at once".
		bool loopedBack = at >= 0 && mFurthest[i] >= 0 && at < mFurthest[i] && inReload;
		if (moved >= 1 && loopedBack)
		{
			mProbe[i] = false;
			SetKind(w, KIND_PACED);
			mPaidFirst[i] = moved;
			PumpHold(p, i, w, psp, String.Format("held for the next shell (the mod's loop loaded %d while it was read)", moved));
			return;
		}
		if (moved >= 2 || moved >= 1 && (full || !inReload))
		{
			// more than one shell in one pass, or one and out: a reload that loads what it can at once
			mProbe[i] = false;
			SetKind(w, KIND_WHOLE);
			mWhole[i] = true;
			WholeTick(mo, p, i, w, psp, inReload);
			return;
		}
		if (at > mFurthest[i])
			mFurthest[i] = at;
		if (moved <= 0 && (!inReload || mProbeTics[i] > FEED_LIMIT))
		{
			mProbe[i] = false;
			PumpDone(i, w, "the mod's reload loaded nothing");
			let s = RSP_Handler.StateOf(mo);
			if (s)
				s.Abort(mo);
		}
	}

	// WHOLE: the mod's reload runs to its end (its ammo), the gun is parked there -- no fire -- until
	// the hand has pushed as many shells as the mod loaded; then it goes on from that state.
	private void WholeTick(PlayerPawn mo, PlayerInfo p, int i, Weapon w, PSprite psp, bool inReload)
	{
		let s = RSP_Handler.StateOf(mo);
		let tube = RSR.WeaponStore(mo, false);
		int have = tube ? tube.Amount : 0;
		mo.GiveInventory('RSP_LTick', 1);
		State hold = GetDefaultByType('MS_ReloadStates').FindState("MS_Hold");
		if (!mHeld[i])
		{
			int moved = Moved(mo, i, have);
			if (moved > mRise[i])
			{
				mOwe[i] += moved - mRise[i];
				mRise[i] = moved;
			}
			if (s)
			{
				s.paid = true;
				s.owe = mOwe[i];
			}
			if (!inReload && psp.CurState != hold && hold)
			{
				if (mOwe[i] <= 0)
				{
					mWhole[i] = false;
					PumpDone(i, w, "the mod's reload loaded nothing");
					if (s)
						s.Abort(mo);
					return;
				}
				mReturn[i] = psp.CurState;
				mHeld[i] = w;
				p.SetPsprite(PSP_WEAPON, hold, false, w);
				Trace(w, String.Format("the mod's reload is done (%d shells) -- held, no fire, until the hand has pushed them", mOwe[i]));
			}
		}
		while (mo.CountInv('RSP_ShellIn') > 0 && mOwe[i] > 0)
		{
			mo.TakeInventory('RSP_ShellIn', 1);
			mOwe[i]--;
			Trace(w, String.Format("a shell pushed home -- %d to go", mOwe[i]));
		}
		if (s)
			s.owe = mOwe[i];
		// the pump stroke ends a loading reload (RSP's own rule): the hand is done with it
		bool stroke = s && s.mode == RSP.NONE;
		if (mHeld[i] && (mOwe[i] <= 0 || stroke))
		{
			mWhole[i] = false;
			mo.TakeInventory('RSP_ShellIn', 999);
			State go = mReturn[i];
			mHeld[i] = null;
			mReturn[i] = null;
			mDisarmed[i] = true;
			if (s)
			{
				s.paid = false;
				s.owe = 0;
				if (s.mode == RSP.LOAD)
					s.End(mo);
			}
			if (go)
				p.SetPsprite(PSP_WEAPON, go, false, w);
			Trace(w, stroke && mOwe[i] > 0 ? "the hand pumped -- fire allowed" : "the hand pushed every shell -- fire allowed");
		}
	}

	private void Trace(Weapon w, String what)
	{
		if (RS_ForeignRemap.DebugOn())
			Console.Printf("[MSJOIN] %s pump: %s", w ? w.GetClassName() : 'none', what);
	}

	private void Release(PlayerInfo p, int i, bool finished)
	{
		let w = mHeld[i];
		mHeld[i] = null;
		if (mShot[i])
		{
			// switched away or died while the hand was pumping: nothing to give back to
			mShot[i] = false;
			mReturn[i] = null;
			return;
		}
		if (p && p.mo)
			p.mo.TakeInventory('RSR_Charge', 999);	// ours, given at Take: the reload is over
		State back = mReturn[i];
		mReturn[i] = null;
		mDisarmed[i] = true;
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
