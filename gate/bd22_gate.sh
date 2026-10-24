#!/bin/bash
# F1: run the bd22q pack on the owner's load order, headless, one launch. Edit the four paths.
# Pass = exit 0, no "Script error", no "Execution could not continue", GATE_DONE in the log.
QZD=/e/DOOMWork/QZD17-engine/build/Release                          # owner's PC: the qzd17.3 build
IWAD=/e/DOOMWork/QZD17-engine/build/Release/doom2.wad               # NOT Freedoom: BD_VoxelPack's voxeldef names Doom 2 sprites
BD22=/e/DOOMWork/brutal22test6.pk3
VOX="/d/SteamLibrary/steamapps/Common/DooM VR/__Games/BrutalDoom/BD_VoxelPack.pk3"
PK3=${1:-dist/BD22Q_197pre.pk3}         # python3 tools/bd22_plus.py pk3 dist/BD22Q_197pre.pk3
LOG=gate/bd22_197.log
# BOTH OF THOSE ARE RELATIVE AND THE RUN LINE BELOW CDs TO $QZD FIRST (2026-10-24). A relative
# -file simply is not found there, and the engine loads WITHOUT the pack and still reaches
# GATE_DONE and still exits 0: the gate passes while testing nothing at all, which is the same
# failure god was added for. Resolve them here, against the directory the gate was called from,
# and fail now rather than silently.
[ -f "$PK3" ] || { echo "no pk3 at $PK3 (run from the repo root)"; exit 2; }
PK3=$(cd "$(dirname "$PK3")" && pwd)/$(basename "$PK3")
# WHICH BUILD DID THIS GATE ACTUALLY RUN (2026-10-24). The owner launched a copy of the pk3 he
# had dragged to his Desktop eight hours earlier, hit a fatal "Unknown function WantsHands", and
# the gate was passing all the while -- on a different file. The engine names the build in its
# own log ("adding .../BD22Q_197pre.pk3, 519 lumps"), so printing the same three facts here is
# all it takes to tell at a glance whether a pasted log is the build that was gated.
echo "pk3  $PK3"
echo "     $(stat -c '%s bytes, %y' "$PK3" 2>/dev/null | cut -d. -f1), $(unzip -l "$PK3" 2>/dev/null | tail -1 | awk '{print $2}') lumps"
mkdir -p "$(dirname "$LOG")"
LOG=$(cd "$(dirname "$LOG")" && pwd)/$(basename "$LOG")
# god first (owner, 2026-10-24): a gate that dies partway still prints GATE_DONE and still exits 0,
# because the quit at the end runs either way -- it just stops firing and reloading anything. The
# run passes while testing nothing, and nothing in the log says so.
# The casings leg (2026-10-24) fires the four guns whose ejection port 1.97 added, because the
# four 1.38 shipped were the only ones this gate ever ran: RSA_Casings.Place is reached from
# WorldThingSpawned on a PistolCasing/EmptyBrass/ShotgunCasing, so a gun that is never fired
# never reaches the new Port() rows and the gate passes without touching them. The Shotvolver
# (Revolver2) is NOT here: it only exists when rsq_slug_revolver replaces the Revolver at spawn.
cas="give Shot_Gun; give SSG; give Revolver; give Shell 80; give RevolverAmmo 24; wait 5; echo GATE_CASINGS; use Shot_Gun; wait 10; +attack; wait 25; -attack; wait 20; use SSG; wait 10; +attack; wait 25; -attack; wait 20; +reload; wait 3; -reload; wait 30; use Revolver; wait 10; +attack; wait 25; -attack; wait 20; +reload; wait 3; -reload; wait 40"
cmd="wait 40; god; echo GATE_START; give MG42; give Flamethrower2; give Unmaker; give Machinegun; give Clip2 200; give Gas 200; give SoulAmmo 60; give AmmoRocket 5; wait 5; use Machinegun; wait 10; echo GATE_FIRE; +attack; wait 15; -attack; wait 5; +altattack; wait 3; -altattack; wait 10; +reload; wait 3; -reload; wait 40; use MG42; wait 10; +attack; wait 15; -attack; wait 5; +reload; wait 3; -reload; wait 20; use Flamethrower2; wait 10; +attack; wait 15; -attack; wait 5; +reload; wait 3; -reload; wait 20; use Unmaker; wait 10; +attack; wait 15; -attack; wait 5; +reload; wait 3; -reload; wait 20; $cas; echo GATE_DONE; quit"
# +logfile, not just the redirect. A FATAL script error does NOT reach the redirected stream --
# it cost three diagnoses in one session: "Unknown sprite RQXM", "cvar already exists" and
# "Unexpected 'version'" all showed a clean-looking log that simply stopped, and the owner had to
# paste the real error each time. The engine's own logfile catches them.
# xvfb only where there is one. This script came off a Linux container and kept its xvfb-run; on
# the owner's PC there is none, and `timeout` answered "failed to run command 'xvfb-run'" while
# the line still reported exit 0. On Windows the engine just opens its own 640x480 window --
# +vid_fullscreen 0 is passed either way, and it is never to be run fullscreen.
if command -v xvfb-run >/dev/null 2>&1; then
	WRAP="xvfb-run -a -s "-screen\ 0\ 1024x768x24\ +extension\ GLX" stdbuf -oL -eL"
	X11=1
else
	WRAP=""
	X11=0
fi
cd "$QZD" || exit 2
[ -x ./qzdoom ] || [ -x ./qzdoom.exe ] || { echo "no qzdoom in $QZD"; exit 2; }
HOME=$(dirname "$LOG") LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe timeout 420 $WRAP ./qzdoom -iwad "$IWAD" -file "$BD22" "$VOX" "$PK3" -nosound -nomusic +logfile "$LOG.engine" +vid_fullscreen 0 +vr_mode 0 +vid_preferbackend 0 -width 640 -height 480 -warp 1 +"$cmd" -stdout > "$LOG" 2>&1
rc=$?
# `echo "exit $?"` AFTER the grep reported the GREP's status, not the engine's, so a crashed run
# printed "exit 0" as long as the grep found nothing (2026-10-24). Capture rc first, and say
# outright whether the run reached its own markers -- "no hits" is not the same as "it ran".
echo "exit $rc  xvfb $X11"
for m in GATE_START GATE_FIRE GATE_CASINGS GATE_DONE; do
	printf '%-14s %s\n' "$m" "$(grep -c "$m" "$LOG" "$LOG.engine" 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')"
done
grep -n -i "script error\|execution could not\|already exists\|unexpected" "$LOG.engine" 2>/dev/null | grep -vi "voxeldef" | head
grep -n -i "script error\|GATE_\|execution could not\|abort\|crash\|errors,\|VM execution\|Tried to\|Unknown\|not found\|invalid" "$LOG" | grep -v "FindModel\|Deh_Actor\|REGT\|BrutalWeapon\|limbs.dec\|aaliens\|eeevilll\|BDMummy\|Crush from actor Actor\|BBled1\|BrutalNightmareDemon"
# On Windows (the owner's PC): same -file order in ZDL; read the log for the same strings.
