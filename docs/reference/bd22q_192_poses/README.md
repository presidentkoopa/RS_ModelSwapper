# BD22 VR Weapons 1.92 hand-pose reference gallery

Run: `cd docs/reference/bd22q_192_poses && python3 make_gallery.py [Class,Class...]` (one engine run per gun under `flock -o -s $RIG_LOCK`, default /tmp/rig.lock: set RIG_LOCK to the shared lock when other runs share the rig; ~30 s each, ~15 min for all; `--index` rebuilds index.json only). Needs the QuestZDoom 17.3 rig at
`tools/rig/build/rig` (or B22_RIG, e.g. RS_ModelSwapper's gate/qz_rig/bin), `probe192.pk3` (source in `probe192/`), `rig_qzdoom.ini`, and env B22_IWAD / B22_BD22 / B22_VOX / B22_PK3, defaults in the script).
Per gun: `<Class>_{side,eye,top,bottom,front34,grip[,support]}.jpg` and `<Class>.json` (1.92 handtable row, MODELDEF lines, exact poses and console). `index.json` lists them in BD22 slot order.
The Sniper set (`Sniper_*.jpg`, `Sniper.json`, incl. `scope_rest` / `scope_eye`) is rendered from current RS_Brutal22WeaponsQ main (70b0574), not 1.92, because 1.92 had no Sniper (nosniper.zs swapped it out).
