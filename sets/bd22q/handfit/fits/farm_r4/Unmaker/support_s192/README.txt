Unmaker support (support192, STAGED, NOT PORTED: its gun hand is on lane-hands-r4, not in lane-b-1.99x).
Fitted by tools/handfit/support192/fit192.py Unmaker --staged <lane-hands-r4 poses/Unmaker.json>,<fitfarm_results/Unmaker/fbx_hv_Unmaker_R.md3>
(seed = 1.92's own hold, Ermac hand2 frame 3, carried onto the r4-placed gun; the FBX left hand re-fitted to it, then closed onto the gun).
Gun placement read from lane-hands-r4 tools/handfit/poses/Unmaker.json gun_move.modeldef_place; gun hand assumed baked in place (hook 0).
fbx_s192_Unmaker_L.md3: the frame baked in place (hook [-0.0, -0.0, 0.0], rot [-0.0, 0.0, -0.0]; bake check 0.0080 cm).
Measured (exact): pen into gun 0.11 cm, into gun hand 0.00 cm, 3 of 9 finger contacts touching, wrap 119 deg, palm gap 0.81 cm.
To port when the gun hand lands: add it to support192/port192.py ORDER (its frame then joins fbx_s192_L.md3, RQWS) and run port192.py port.
Rig only after port; nothing here has been on the rig.
