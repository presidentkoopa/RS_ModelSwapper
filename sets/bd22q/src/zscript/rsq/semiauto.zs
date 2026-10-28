// semiauto.zs (F11) -- a semi-automatic gun fires once per pull of the trigger.
// +WEAPON.NOAUTOFIRE cannot do it on QZD 17.3: PlayerPawn.TickPSprites stores CheckWeaponFire's
// return in player.attackdown, and that is false whenever NOAUTOFIRE just held the shot back, so
// the very next ready tic fires again (wadsrc/static/zscript/actors/player/player.zs:583, against
// upstream, which keeps attackdown set while the button is held). BD22's own Ready loop also
// jumps to Fire on FiredPrimary every tic it is held. The gun gives this lock when it fires; its
// Fire state goes back to waiting while the lock is there; the lock goes when the trigger is let go.
// THE SAME FAULT, FOR EVERY GUN (owner 2026-10-26: "our bd guns should have normal bd22 fire rates").
// Measured in the rig, trigger held 140 tics: Pistol 21 shots vs 13 with desktop's rule, pump
// Shotgun 6 vs 1, Incendiary Launcher 4 vs 1, Dual Pistols 32 vs 28; every other gun identical.
// Before the player thinks, attackdown is set the way upstream keeps it: down while the trigger has
// stayed down since the last tic. DoEffect runs in the pawn's own Tick, ahead of TickPSprites.
class RSQ_TriggerHeld : Inventory
{
	Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET }
	override void DoEffect()
	{
		Super.DoEffect();
		if (Owner && Owner.player)
			Owner.player.attackdown = (Owner.player.oldbuttons & BT_ATTACK) && (Owner.player.cmd.buttons & BT_ATTACK);
	}
}

class RSQ_SemiLock : Inventory
{
	Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET }
	override void DoEffect()
	{
		Super.DoEffect();
		if (!Owner || !Owner.player)
			return;
		if (!(Owner.player.cmd.buttons & BT_ATTACK) && Owner.CountInv("FiredPrimary") <= 0)
			Owner.TakeInventory("RSQ_SemiLock", 1);
	}
}
