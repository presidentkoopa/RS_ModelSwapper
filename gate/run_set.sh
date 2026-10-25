#!/bin/bash
# run_set.sh -- run ANY weapon set through the engine, headless, one launch.
#
#     sh gate/run_set.sh gate/<set>.gate [pk3]
#
# The engine plays itself. GZDoom's console takes commands chained with ';' and a `wait N` that
# pauses N tics, and `+attack` / `+reload` are the same commands your keybinds fire -- so a
# single `+"..."` argument gives every gun, switches to each, holds the trigger, reloads, and
# quits. No automation framework, no input faking.
#
# WHAT IT PROVES: the pack parses, the map starts, each gun can be selected and fired and
# reloaded, and the run reached the end. Every claim of that kind in this repo came from here.
# WHAT IT CANNOT PROVE: anything about VR, and anything about how something looks. It runs
# +vr_mode 0, so hands, melee and any pose code return early and never execute. It has no eyes.
#
# See gate/GATING_A_SET.md for the method, and for the traps -- several of which cost this
# project a day each and every one of which is a way to PASS while testing nothing.
set -u
CFG=${1:?usage: sh gate/run_set.sh gate/<set>.gate [pk3]}
[ -f "$CFG" ] || { echo "no config at $CFG"; exit 2; }
ROOT=$(cd "$(dirname "$0")/.." && pwd)

# defaults a config may override
QZD=""; IWAD=""; PK3=""; LOG=""; TIMEOUT=420; WARP=1; GOD=1
FILES=(); GUNS=(); AMMO=""; EXTRA=""
RAISE=40; FIRE=25; SETTLE=20; RELOAD=1
# shellcheck disable=SC1090
. "$CFG"

PK3=${2:-$PK3}
NAME=$(basename "$CFG" .gate)
LOG=${LOG:-$ROOT/gate/$NAME.log}

[ -n "$QZD" ]  || { echo "$CFG: QZD is not set"; exit 2; }
[ -n "$IWAD" ] || { echo "$CFG: IWAD is not set"; exit 2; }
[ -f "$IWAD" ] || { echo "no iwad at $IWAD"; exit 2; }
[ ${#GUNS[@]} -gt 0 ] || { echo "$CFG: GUNS is empty -- nothing would be fired"; exit 2; }

# ABSOLUTE PATHS, BEFORE THE cd. The run line cds to $QZD, so a relative -file is not found
# there -- and the engine then loads WITHOUT the pack, reaches the end and exits 0. The gate
# passes while testing nothing. This is the single easiest way to fool yourself with it.
[ -f "$PK3" ] || { echo "no pk3 at $PK3 (run from the repo root)"; exit 2; }
PK3=$(cd "$(dirname "$PK3")" && pwd)/$(basename "$PK3")
for i in "${!FILES[@]}"; do
	f=${FILES[$i]}
	[ -f "$f" ] || { echo "parent file missing: $f"; exit 2; }
	FILES[$i]=$(cd "$(dirname "$f")" && pwd)/$(basename "$f")
done
mkdir -p "$(dirname "$LOG")"
LOG=$(cd "$(dirname "$LOG")" && pwd)/$(basename "$LOG")

# WHICH BUILD DID THIS ACTUALLY RUN. A stale copy of a pk3 somewhere else cost this project a
# diagnosis: the log said 415 lumps and the build on disk had 519. The engine names the build in
# its own log too ("adding .../x.pk3, N lumps"); printing it here means a pasted log can be
# matched to a build at a glance.
echo "set  $NAME"
echo "pk3  $PK3"
echo "     $(stat -c '%s bytes, %y' "$PK3" 2>/dev/null | cut -d. -f1), $(unzip -l "$PK3" 2>/dev/null | tail -1 | awk '{print $2}') lumps"

# ---- build the console script ---------------------------------------------------------
# A MARKER PER GUN. Without one the log says the run finished and not which guns took part --
# and a gun that was never selected, or had no ammo, is silent and indistinguishable from one
# that worked. That is how a whole leg of this gate fired nothing for a day.
cmd="wait 40;"
[ "$GOD" = 1 ] && cmd="$cmd god;"
cmd="$cmd echo GATE_START;"
for g in "${GUNS[@]}"; do cmd="$cmd give $g;"; done
[ -n "$AMMO" ] && cmd="$cmd $AMMO"
cmd="$cmd wait 10;"
for g in "${GUNS[@]}"; do
	cmd="$cmd echo GATE_GUN_$g; use $g; wait $RAISE;"
	cmd="$cmd +attack; wait $FIRE; -attack; wait 10;"
	[ "$RELOAD" = 1 ] && cmd="$cmd +reload; wait 3; -reload; wait $SETTLE;"
done
[ -n "$EXTRA" ] && cmd="$cmd $EXTRA"
cmd="$cmd echo GATE_DONE; quit"

# xvfb only where there is one. This came off a Linux container; on Windows there is none, and
# `timeout` answered "failed to run command 'xvfb-run'" while the line still reported exit 0.
if command -v xvfb-run >/dev/null 2>&1; then
	WRAP="xvfb-run -a -s "-screen\ 0\ 1024x768x24\ +extension\ GLX" stdbuf -oL -eL"
	X11=1
else
	WRAP=""
	X11=0
fi
cd "$QZD" || { echo "no engine dir $QZD"; exit 2; }
[ -x ./qzdoom ] || [ -x ./qzdoom.exe ] || { echo "no qzdoom in $QZD"; exit 2; }

# +logfile, not just the redirect: a FATAL script error does NOT reach the redirected stream.
# The log simply stops looking clean. That cost three diagnoses in one session.
# NEVER FULLSCREEN -- the owner's standing rule, and it is why -width/-height are here.
HOME=$(dirname "$LOG") LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe \
	timeout "$TIMEOUT" $WRAP ./qzdoom -iwad "$IWAD" \
	${FILES[@]+-file "${FILES[@]}"} "$PK3" \
	-nosound -nomusic +logfile "$LOG.engine" +vid_fullscreen 0 +vr_mode 0 \
	+vid_preferbackend 0 -width 640 -height 480 -warp "$WARP" +"$cmd" -stdout > "$LOG" 2>&1
rc=$?

# rc FIRST. `echo "exit $?"` placed after a grep reports the GREP's status, so a crashed run
# printed "exit 0" as long as the grep found nothing.
echo "exit $rc  xvfb $X11"
hit () { grep -c "$1" "$LOG" "$LOG.engine" 2>/dev/null | awk -F: '{s+=$2} END {print s+0}'; }
echo "--- markers ---"
for m in GATE_START GATE_DONE; do printf '%-18s %s\n' "$m" "$(hit $m)"; done
echo "--- guns that were actually selected ---"
miss=0
for g in "${GUNS[@]}"; do
	n=$(hit "GATE_GUN_$g")
	printf '%-18s %s%s\n' "$g" "$n" "$( [ "$n" = 0 ] && echo '   <-- NEVER REACHED' )"
	[ "$n" = 0 ] && miss=1
done
[ "$miss" = 1 ] && echo "WARNING: a gun above was never reached. It tested nothing."
echo "--- faults ---"
grep -n -i "script error\|execution could not\|VM execution\|abort" "$LOG.engine" 2>/dev/null \
	| grep -viE "${IGNORE:-__none__}" | head
echo "--- pass needs: exit 0, 'script parsing took', GATE_DONE, and every gun above non-zero ---"
grep -i "script parsing took" "$LOG.engine" 2>/dev/null
