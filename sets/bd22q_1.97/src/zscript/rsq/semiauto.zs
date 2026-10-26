// semiauto.zs (F11) -- a semi-automatic gun fires once per pull of the trigger.
// +WEAPON.NOAUTOFIRE cannot do it on QZD 17.3: PlayerPawn.TickPSprites stores CheckWeaponFire's
// return in player.attackdown, and that is false whenever NOAUTOFIRE just held the shot back, so
// the very next ready tic fires again (wadsrc/static/zscript/actors/player/player.zs:583, against
// upstream, which keeps attackdown set while the button is held). BD22's own Ready loop also
// jumps to Fire on FiredPrimary every tic it is held. The gun gives this lock when it fires; its
// Fire state goes back to waiting while the lock is there; the lock goes when the trigger is let go.
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
