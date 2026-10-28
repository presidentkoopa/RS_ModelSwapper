// RSB_Guns: no break-open guns generated in this pass
// Every function the runtime calls, from the pack 1.92 source signatures; Index is 0 for
// every weapon, so the module is present and idle.
class RSB_Guns abstract
{
	clearscope static int Index(Weapon w) { return 0; }
	clearscope static Vector3 Hinge(int i) { return (0, 0, 0); }
	clearscope static Vector3 Axis(int i) { return (0, 0, 0); }
	clearscope static double OpenDeg(int i) { return 0; }
	clearscope static int Chambers(int i) { return 0; }
	clearscope static bool Loader(int i) { return false; }
	clearscope static Vector3 Base(int i, int k) { return (0, 0, 0); }
	clearscope static Vector3 Tip(int i, int k) { return (0, 0, 0); }
	clearscope static Vector3 Bore(int i, int k) { return (0, 0, 0); }
	clearscope static Vector3 Rest0(int i, int k) { return (0, 0, 0); }
	clearscope static Vector3 Rest1(int i, int k) { return (0, 0, 0); }
	clearscope static Vector3 Rest2(int i, int k) { return (0, 0, 0); }
	clearscope static Vector3 RestT(int i, int k) { return (0, 0, 0); }
	clearscope static Vector3 Hand0(int i) { return (0, 0, 0); }
	clearscope static Vector3 Hand1(int i) { return (0, 0, 0); }
	clearscope static Vector3 Hand2(int i) { return (0, 0, 0); }
	clearscope static Vector3 HandT(int i) { return (0, 0, 0); }
	clearscope static Vector3 HandBase(int i) { return (0, 0, 0); }
	clearscope static Vector3 HandTip(int i) { return (0, 0, 0); }
	clearscope static String HoldState(int i) { return ""; }
	clearscope static Vector3 Scale(int i) { return (0, 0, 0); }
	clearscope static Vector3 Offset(int i) { return (0, 0, 0); }
	clearscope static Name SprGun(int i) { return 'None'; }
	clearscope static Name SprPart(int i) { return 'None'; }
	clearscope static Name SprWorld(int i) { return 'None'; }
	clearscope static String ReadySprite(int i) { return ""; }
	clearscope static String SndOpen(int i) { return ""; }
	clearscope static String SndOpen2(int i) { return ""; }
	clearscope static String SndLoad(int i) { return ""; }
	clearscope static String SndClose(int i) { return ""; }
	clearscope static String SndClose2(int i) { return ""; }
	clearscope static int Channel(int i) { return 0; }
	clearscope static String Reserve(int i) { return ""; }
	clearscope static String Loaded(int i) { return ""; }
	clearscope static int PerLoad(int i) { return 0; }
	clearscope static int Cap(int i) { return 0; }
	clearscope static bool WorldEject(int i) { return false; }
	clearscope static Vector3 Casing(int i) { return (0, 0, 0); }
	clearscope static Name Cls(int i) { return 'None'; }
	clearscope static String Unloaded(int i) { return ""; }
	clearscope static bool LoaderEmptyInHand(int i) { return false; }
	clearscope static bool ReserveHoldsLoaded(int i) { return false; }
	clearscope static String ReloadToken(int i) { return ""; }
	clearscope static double LoaderDepth(int i) { return 0; }
	clearscope static Vector3 PushRef(int i) { return (0, 0, 0); }
	clearscope static double PushZ0(int i) { return 0; }
	clearscope static double PushZ1(int i) { return 0; }
	clearscope static double PushR0(int i) { return 0; }
	clearscope static double PushR1(int i) { return 0; }
	clearscope static double PushEdge(int i, double rho) { return 0; }
}

class RSB_Sprites : Actor { States { Spawn: TNT1 A -1; Stop; } }
