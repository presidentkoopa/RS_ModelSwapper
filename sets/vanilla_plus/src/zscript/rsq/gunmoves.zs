// RSQ_GunMoves: no recoil-in-mesh tables yet for this set (rsq_gunmoves_gen.py is a later pass).
// The hands ride the gun layer's offset only.
class RSQ_GunMoves abstract play
{
	clearscope static Vector3 Pivot(int i) { return (0, 0, 0); }
	clearscope static bool Mirrored(int i) { return false; }
	clearscope static bool Blends(int i) { return false; }
	static Vector3, Vector3 Frame(int i, int sprite, int frame) { return (0, 0, 0), (0, 0, 0); }
}
