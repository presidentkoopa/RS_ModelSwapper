// RSQ_HandTable: no hands fitted yet in this set (hand fitting is its own pass). Every
// function the runtime calls, with Index 0 for every weapon.
class RSQ_HandTable abstract
{
	clearscope static int Index(Weapon w) { return 0; }
	clearscope static String GunOne(int i) { return ""; }
	clearscope static String GunTwo(int i) { return ""; }
	clearscope static String Support(int i) { return ""; }
	clearscope static Vector3 GunHook(int i) { return (0, 0, 0); }
	clearscope static Vector3 GunRot(int i) { return (0, 0, 0); }
	clearscope static Vector3 SupportHook(int i) { return (0, 0, 0); }
	clearscope static Vector3 SupportRot(int i) { return (0, 0, 0); }
	clearscope static Vector3 SupportPoint(int i) { return (0, 0, 0); }
	clearscope static String Trigger(int i) { return ""; }
	clearscope static Vector3 GunHookTwo(int i) { return (0, 0, 0); }
	clearscope static Vector3 GunRotTwo(int i) { return (0, 0, 0); }
}
