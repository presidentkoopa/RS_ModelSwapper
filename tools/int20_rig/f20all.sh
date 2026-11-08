#!/bin/bash
# TEST ONLY: every rig check of the 2.0 final on one pk3, one engine at a time (exclusive rig lock), the fresh default
# ini (ini.f20: written by the engine itself on a boot with no ini; playerclass set to Rifle Start, as New Game does).
# usage: f20all.sh <pk3> [out dir]      STEPS="boot sweep held rsweep dual holds scope" (default: all)
HERE="$(cd "$(dirname "$0")" && pwd)"; DEPOT="$(cd "$HERE/../.." && pwd)"; T="$DEPOT/tools"
W="${RSQ_WORK:-$DEPOT/work}"; R="$W/int20_rig"; P="$(realpath "$1")"; O="${2:-$W/out/final20}"
export INT20_INI="$HERE/ini.f20"; mkdir -p "$O" "$W/f20gate" "$W/f20scope" "$R/logs"
for step in ${STEPS:-boot sweep held rsweep dual holds scope}; do case $step in
boot) echo "== boot"; "$HERE/run.sh" f20_boot $P 120 'wait 200; quit' >/dev/null 2>&1
      grep -E "Script error|VM execution aborted|exception|Too many|cls " "$R/logs/f20_boot.log" | sort | uniq -c | head;;
sweep) echo "== sweep"; python3 "$HERE/sweep_f20.py" "$P" f20 0;;
held) echo "== held"; python3 "$HERE/f20held.py" "$P" "$O/held" Melee_Attacks BrutalAxe Chain_saw DSweap BrutalPistol BrutalRevolver Revolver BrutalSMG MP40 Shot_Gun SSG AssaultShotgun Sniper Rifle Minigun MG42 Machinegun GrenadeLauncher IncendiaryLauncher Rocket_Launcher Devastator HellishMissileLauncher Plasma_Gun Railgun BFG10k BIG_FUCKING_GUN NukeLauncher Unmaker Flamethrower2 FlameCannon HandGrenades;;
rsweep) echo "== hand reloads"; python3 "$HERE/rsweep.py" "$P" all;;
dual) echo "== dual"; python3 "$HERE/dualsweep.py" "$P" f20d;;
holds) echo "== FBX reload holds"; RSQ_GATE="$W/f20gate" python3 "$HERE/f20wrap.py" "$HERE/ini.f20" "$T/handfit/offhand/rig_holds.py" "$P" f20 mag18 mag13 brkSSG:AmmoShell:0 brkGrenadeLauncher:AmmoRocket:0 brkRevolver:AmmoShell:0 brkBrutalRevolver:Clip1:0 brkBrutalRevolver:Clip1:1 pump m203 2>&1 | grep -vE '^\s*$' | cut -c1-220;;
scope) echo "== scope 3x + alt toggle"; for g in Sniper RailGun; do
      SCOPE_OUT="$W/f20scope" EVERY=6 SECS=70 ALTSEQ='wait 30; +altattack; wait 40; -altattack; wait 70; +altattack; wait 40; -altattack; wait 70; ' python3 "$HERE/f20wrap.py" "$HERE/ini.f20" "$T/scope3x/drive.py" s3_$g "$P" $g 30 0 0 1 '' 960 2>&1 | grep -E 'rc|RSQT|scope' | head -8
      python3 "$T/scope3x/conv.py" "$W/f20scope/dump_s3_$g" | tail -1; python3 "$T/scope3x/blobs.py" "$W/f20scope/dump_s3_$g"; done;;
esac; done
echo "== all done"
