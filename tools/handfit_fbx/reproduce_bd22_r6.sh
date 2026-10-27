#!/bin/sh
# Re-run the BD22 round-6 fit (BrutalPistol + Flamethrower2) and bake the MD3 frames, then compare them with
# reference/bd22_r6/expected_md3.json (= the frames in BD22Q_192_fbx_headset_r6.pk3).
# Needs HANDFIT_FBX (hand_final.fbx) and the 1.92 checkout (sh tools/rig/setup.sh, or RSQ_GUNPACK). See README.md.
#   (default)   assemble from the recorded final poses (reference/bd22_r6/fits): contact projection, squeeze solve,
#               support, gun move, bake.
#   --resolve   also RE-SOLVE the final link of each pose from its recorded seeds first (pistol gun hand K5, pistol
#               support R3c, flamer support D, flamer gas-pump Z3; about an hour), then the same assembly and bake.
set -e
T=$(cd "$(dirname "$0")" && pwd); cd "$T"
W=${HANDFIT_WORK:-$T/work}; mkdir -p "$W/results" "$W/logs"
cp reference/bd22_r6/fits/*.json "$W/results/"
R=no; [ "$1" = "--resolve" ] && R=yes
if [ $R = yes ]; then
  LANEC_W='{"anchor":0.1,"pen":20,"web":5.0}' LANEC_ANCHOR=K2 LANEC_SEED=K4,K \
    python3 run_wrist.py BrutalPistol 8 K5 none 0.03 > "$W/logs/resolve_pistol_K5.log"
  LANEC_CONTACT=-0.12 LANEC_SSEED=BrutalPistol_support_R3b.json \
    python3 run_support3.py BrutalPistol cup K5 R3c 0.1 '{"pads":2.5}' > "$W/logs/resolve_pistol_support_R3c.log"
fi
python3 final3.py BrutalPistol BrutalPistol_support_R3c.json > "$W/logs/final3_pistol.log"
python3 final3.py Flamethrower2 Flamethrower2_nozzle_support_R3g.json > "$W/logs/final3_flamer.log"
if [ $R = yes ]; then
  python3 run_under.py D '{"w":{"fore_u":4.0},"s6":6.0,"T":{"fore_deg":30.0},"seeds":["Flamethrower2_under_C.json"]}' > "$W/logs/resolve_under_D.log"
fi
python3 final4.py > "$W/logs/final4.log"
python3 squeeze.py BrutalPistol Flamethrower2 > "$W/logs/squeeze_r5.log"
python3 modeldef3.py > "$W/logs/modeldef3.log"
if [ $R = yes ]; then
  python3 run_pump.py Z3 '{"pen":0.05,"cant":8.0,"wrist_deg":6.0,"wrist_cm":6.0,"dev_max":20,"bore_deg":3.0,"seeds":["Flamethrower2_pump_Z2.json"],"lats":[],"P":{"palm_mode":"side","normal_deg":30,"palm_f":[-9.0,0.5],"under_tol":0.3},"w":{"side":3.0,"pads":3.0,"index_keep":1.5,"thumb_top":1.0,"boreC":3.0,"pen":10.0}}' > "$W/logs/resolve_pump_Z3.log"
  python3 resolve_cmp.py
fi
python3 final6.py > "$W/logs/final6.log"
python3 spout_tip.py > "$W/logs/spout_tip.log"
LANEC_SQUEEZE=1 LANEC_SQFILE=squeeze_r6.json LANEC_FINAL=round6_final.json LANEC_MD3=fbx_r6 python3 bake3.py > "$W/logs/bake.log"
python3 check_ref.py
