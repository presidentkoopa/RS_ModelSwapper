// Modules of the BD22 pack this edition does not carry. The reload modules and hands.zs ask
// these; each answers "not busy, nothing to place".
class RSK_M203Handler abstract
{
	clearscope static bool Busy(int n) { return false; }
	clearscope static String FreeHand(PlayerPawn mo) { return ""; }
	clearscope static bool TriggerGrip(Actor mo) { return false; }
	clearscope static Vector3 SupportShift(Actor owner, double ticfrac) { return (0, 0, 0); }
	clearscope static bool Places(Actor owner, int layer) { return false; }
	clearscope static Vector3, Vector3 Place(Actor owner, Vector3 translation, Vector3 rotation, int layer, double ticfrac) { return translation, rotation; }
}

class RSG_Handler abstract
{
	clearscope static bool WantsGrab(int n) { return false; }
}

// rsr_m203.zs's layer range (hands.zs RSQ_Layers.Taken reads it): values from that file, 1.96b
class RSM abstract
{
	const LAYER_FIRST = 2130;
	const LAYER_LAST = 2131;
}
