// roster.zs (1.97) -- guns added to the BD22 roster with an option to stand in for a BD22 gun
// (c2q/bd22_mg.py). Off (default): both exist. On: every spawn of the BD22 gun is the added gun
// (map pickups, spawners, drops). Server cvars: the playsim must agree.
class RSQ_Roster : EventHandler
{
	// 1.97: the slug revolver (BD21 Revolver2) in place of BD22's Shotvolver, when the option is on
	override void CheckReplacement(ReplaceEvent e)
	{
		if (!e.Replacee) return;
		let mg = CVar.FindCVar('rsq_mg_replaces_mg42');
		if (mg && mg.GetInt() != 0 && e.Replacee.GetClassName() == 'MG42')
			e.Replacement = 'Machinegun';
		let sv = CVar.FindCVar('rsq_slug_replaces_shotvolver');
		if (sv && sv.GetInt() != 0 && e.Replacee.GetClassName() == 'Revolver')
			e.Replacement = 'Revolver2';
	}
}
