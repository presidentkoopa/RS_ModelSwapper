// RSP_Guns: no pump guns generated in this pass
// Every function the runtime calls, from the pack 1.92 source signatures; Index is 0 for
// every weapon, so the module is present and idle.
class RSP_Guns abstract
{
	clearscope static int Index(Weapon w) { return 0; }
	clearscope static Vector3 Grab(int i) { return (0, 0, 0); }
	clearscope static Vector3 Pull(int i) { return (0, 0, 0); }
	clearscope static double Travel(int i) { return 0; }
	clearscope static Vector3 PumpHook(int i) { return (0, 0, 0); }
	clearscope static double BoltRatio(int i) { return 0; }
	clearscope static Vector3 SupportHook(int i) { return (0, 0, 0); }
	clearscope static Vector3 Port(int i) { return (0, 0, 0); }
	clearscope static Vector3 Push(int i) { return (0, 0, 0); }
	clearscope static double Depth(int i) { return 0; }
	clearscope static Vector3 PortHook(int i) { return (0, 0, 0); }
	clearscope static Vector3 ShellInHand(int i) { return (0, 0, 0); }
	clearscope static Vector3 AxisInHand(int i) { return (0, 0, 0); }
	clearscope static Vector3 HandHook(int i) { return (0, 0, 0); }
	clearscope static Vector3 HandRot(int i) { return (0, 0, 0); }
	clearscope static Vector3 Scale(int i) { return (0, 0, 0); }
	clearscope static Vector3 Offset(int i) { return (0, 0, 0); }
	clearscope static Name SprGun(int i) { return 'None'; }
	clearscope static Name SprPart(int i) { return 'None'; }
	clearscope static Name SprWorld(int i) { return 'None'; }
	clearscope static String ReadySprite(int i) { return ""; }
	clearscope static String WaitLabels(int i) { return ""; }
	clearscope static String SndShell(int i) { return ""; }
	clearscope static int ChanShell(int i) { return 0; }
	clearscope static String SndBack(int i) { return ""; }
	clearscope static int ChanBack(int i) { return 0; }
	clearscope static String SndFwd(int i) { return ""; }
	clearscope static int ChanFwd(int i) { return 0; }
	clearscope static String SndLand(int i) { return ""; }
	clearscope static String Loaded(int i) { return ""; }
	clearscope static int Cap(int i) { return 0; }
	clearscope static String Reserve(int i) { return ""; }
	clearscope static String MagAmmo(int i) { return ""; }
	clearscope static int EjectFrames(int i) { return 0; }
	clearscope static Vector3 EjectHook(int i, int k) { return (0, 0, 0); }
}
