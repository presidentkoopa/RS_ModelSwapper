// bash.zs (1.97) -- the gun bash: BD22's own kick, with a gun in your hands instead of a boot.
// The trigger is BD22's: +zoom gives Kicking and DEFAULTWEAPON's DoKick runs. Our branch is taken
// only in VR, only with the option on, and only when what you are holding is not already a melee
// weapon -- so the axe, the Dragonslayer, the chainsaw and the fists keep BD22's kick exactly.
//
// RSQ_BashAsk is the pack's own handshake idiom (rsr_break.zs RSB_Call): Inventory.TryPickup runs
// SYNCHRONOUSLY inside A_GiveInventory, so a 0-tic DECORATE state can ask ZScript a question and
// branch on the answer in the same tic. The token is never kept.

// play, not the default data context: PlayerInt and InVR are both play functions
// ("Can't call play function PlayerInt from data context").
class RSQ_Bash abstract play
{
	// not a gun = BD22's kick, untouched
	static bool IsMelee(Name n)
	{
		return n == 'BrutalAxe' || n == 'DSweap' || n == 'Chain_saw' || n == 'Melee_Attacks';
	}

	static bool Wanted(PlayerPawn mo)
	{
		if (!mo || !mo.player || mo.health <= 0)
			return false;
		if (RSQ.PlayerInt(mo, 'rsq_bash', 1) == 0)
			return false;
		if (!RSVR_VRHand.InVR(mo))
			return false;			// desktop keeps the boot
		let w = mo.player.ReadyWeapon;
		return w && !IsMelee(w.GetClassName());
	}
}

class RSQ_BashGo : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }

class RSQ_BashAsk : Inventory
{
	Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET }
	override bool TryPickup(in out Actor toucher)
	{
		let mo = PlayerPawn(toucher);
		if (mo && RSQ_Bash.Wanted(mo))
			mo.GiveInventory('RSQ_BashGo', 1);
		return false;			// never kept
	}
}

// the impact: the effect the owner picked, at the point the bash landed. DECORATE's
// RSQ_BashAttack spawns this; this picks which of the five to draw, and tints RSH0.
class RSQ_BashFX : Actor
{
	Default { +NOINTERACTION; +NOBLOCKMAP; +DONTSPLASH; RenderStyle "Add"; Alpha 1.0; }

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		int n = RSQ.PlayerInt(PlayerPawn(target), 'rsq_bash_fx', 0);
		static const Name FXC[] = { 'RSQ_FX_RSS3', 'RSQ_FX_RSU1', 'RSQ_FX_RSU4', 'RSQ_FX_RSU5', 'RSQ_FX_RSH0' };
		if (n < 0 || n >= 5)
			n = 0;
		let a = Spawn(FXC[n], pos, ALLOW_REPLACE);
		if (a)
		{
			a.target = target;
			int t = RSQ.PlayerInt(PlayerPawn(target), 'rsq_bash_tint', 0);
			if (FXC[n] == 'RSQ_FX_RSH0' && t > 0 && t < 5)
				a.A_SetTranslation(String.Format("RSQ_BashTint%d", t));
		}
		Destroy();
	}
}

class RSQ_FXBase : Actor
{
	Default { +NOINTERACTION; +NOBLOCKMAP; +DONTSPLASH;
		+FORCEXYBILLBOARD; RenderStyle "Add"; Alpha 1.0; }
}
class RSQ_FX_RSS3 : RSQ_FXBase
{
	Default { Scale 0.384; }	// 250 px art at the 96 px standard
	States
	{
	Spawn:
		RSS3 ABCDEFG 2 Bright;
		Stop;
	}
}
class RSQ_FX_RSU1 : RSQ_FXBase
{
	Default { Scale 1.600; }	// 60 px art at the 96 px standard
	States
	{
	Spawn:
		RSU1 ABCD 2 Bright;
		Stop;
	}
}
class RSQ_FX_RSU4 : RSQ_FXBase
{
	Default { Scale 6.400; }	// 15 px art at the 96 px standard
	States
	{
	Spawn:
		RSU4 ABCD 2 Bright;
		Stop;
	}
}
class RSQ_FX_RSU5 : RSQ_FXBase
{
	Default { Scale 0.857; }	// 112 px art at the 96 px standard
	States
	{
	Spawn:
		RSU5 ABCDEFGHIJ 2 Bright;
		Stop;
	}
}
class RSQ_FX_RSH0 : RSQ_FXBase
{
	Default { Scale 1.000; }	// 96 px art at the 96 px standard
	States
	{
	Spawn:
		RSH0 ABCDEFGHIJKLMNOPQRS 2 Bright;
		Stop;
	}
}
