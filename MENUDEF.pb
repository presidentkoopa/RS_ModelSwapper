// PROJECT BRUTALITY VR -- the options page of the PB set (pk3/ProjBrut_MS.pk3, tools_build_pk3.py --pb).
//
// One page with what matters when playing Project Brutality. Every row is an existing ModelSwapper cvar
// (quest/CVARINFO); nothing here is a second copy of a setting, so a change here IS the change in "VR Reload"
// and "Weapon Model Swap Program", and the other way round. Shipped only in the PB set.

AddOptionMenu "OptionsMenu"
{
	StaticText " "
	Submenu "Project Brutality VR", "MSPB_Options"
}

OptionValue "MSPB_ReloadMode"
{
	1, "By hand (VR)"
	0, "PB's own reload"
}

OptionMenu "MSPB_Options"
{
	Title "PROJECT BRUTALITY VR"
	StaticText " "
	StaticText "Every PB gun wears a 3D model that reloads by hand.", "DarkGray"
	StaticText "PB's damage, ammo, sounds and moves stay PB's.", "DarkGray"
	StaticText " "

	StaticText "Guns", "Gold"
	Option "3D Gun Models", "rs_foreignmodels", "OnOff"
	Submenu "Choose Models", "RSFM_Picker"
	Command "Back to the PB Set's Models", "netevent rs-fm-forget-picks"
	StaticText "Forgets the models you picked by hand; every PB gun goes back", "DarkGray"
	StaticText "to its PB-set model.", "DarkGray"
	StaticText " "

	StaticText "Reloading", "Gold"
	Option "Reloading", "rsr_reload", "MSPB_ReloadMode"
	StaticText "By hand: drop the magazine, grab a new one and seat it, pump,", "DarkGray"
	StaticText "break open and load shells. PB's own: PB's reload animation,", "DarkGray"
	StaticText "no hands. Guns PB never reloads (minigun, BFG, Unmaker) are", "DarkGray"
	StaticText "the same either way.", "DarkGray"
	Option "Reload Order", "ms_mod_first", "MS_ReloadOrder"
	StaticText "Mod's reload first: PB reloads at the press and the gun holds", "DarkGray"
	StaticText "its fire until your hands finish.", "DarkGray"
	Option "Reload Sounds", "ms_reload_sounds", "MS_ReloadSounds"
	Option "Grab Ammo With", "rsr_grab_with", "RSR_GrabWith"
	Option "Pump by Hand After a Shot", "ms_hand_pump", "OnOff"
	Option "Charging Handle After Empty", "ms_charge_dry", "OnOff"
	Option "Shells per Grab", "ms_shell_grab", "MS_ShellGrab"
	Option "Shells per Insert", "rsr_shell_credit", "RSR_ShellCredit"
	Slider "Reload Assist", "rsr_assist", 0.5, 3.0, 0.25, 2
	StaticText "How forgiving the grabs and pushes are. 1 is the shipped feel.", "DarkGray"
	StaticText " "

	StaticText "Hands", "Gold"
	Option "VR Hands", "rsq_hands", "OnOff"
	Option "Off Hand", "ms_off_fist", "MS_OffHand"
	Option "Flick to Reload (dual guns)", "rsq_flick", "OnOff"
	Option "VR Punching", "rsq_punch", "OnOff"
	Option "Punch Switches Open", "rsq_punch_use", "OnOff"
	StaticText " "

	StaticText "Effects", "Gold"
	Option "Casings and Smoke From the Gun", "rs_fm_effects", "OnOff"
	StaticText "PB builds brass, smoke and sparks at your eye; this moves them", "DarkGray"
	StaticText "to the gun in your hand.", "DarkGray"
	Slider "Extra Muzzle Distance", "rs_fm_muzzle", -20, 80, 1, 0
	StaticText " "

	StaticText "Everything", "Gold"
	Submenu "VR Reload (all settings)", "RSMS_Reload"
	Submenu "Weapon Model Swap Program", "RSFM_Main"
}
