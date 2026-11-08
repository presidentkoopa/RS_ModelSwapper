#!/bin/bash
# TEST ONLY. One engine run for the sweep tools in this folder: the exclusive rig lock, a PRIVATE copy of the rig
# (work/int20_rig/bin) with the fresh default ini (ini.f20) copied in before the run, so a saved cvar can never hide
# a new default and tools/rig/bin is never touched.
# usage: run.sh <name> <pk3> <secs> <console script> [extra pk3...]     log: $RSQ_WORK/int20_rig/logs/<name>.log
HERE="$(cd "$(dirname "$0")" && pwd)"; DEPOT="$(cd "$HERE/../.." && pwd)"
W="${RSQ_WORK:-$DEPOT/work}/int20_rig"; GD="${RSQ_GAMEDATA:-$DEPOT/../gamedata}"; LOCK="${RSQ_RIGLOCK:-$DEPOT/../rig.lock}"
N=$1; P=$2; T=$3; C=$4; shift 4
mkdir -p "$W/logs"
[ -x "$W/bin/qzdoom" ] || cp -a "$DEPOT/tools/rig/bin" "$W/bin"
[ -f "$W/PINS" ] || cp "$DEPOT/tools/rig/PINS" "$W/PINS"			# bin/qz reads ../PINS (the version guard)
[ -f "$W/ini.pristine" ] || cp "$HERE/ini.f20" "$W/ini.pristine"
[ -f "$W/ini.f20" ] || cp "$HERE/ini.f20" "$W/ini.f20"
[ -f "$W/probe.pk3" ] || (cd "$DEPOT/tools/rig/probe" && zip -q -r -D "$W/probe.pk3" .)	# rig.py loads B22_BUILD/probe.pk3
[ -f "$W/int20dump.pk3" ] || (cd "$HERE/logger" && zip -q -r -D "$W/int20dump.pk3" .)	# the INT ... log lines
[ -f "$W/buttprobe.pk3" ] || (cd "$HERE/buttprobe" && zip -q -r -D "$W/buttprobe.pk3" .)
export B22_IWAD="$GD/doom2.wad" B22_BD22="$GD/brutal22test6.pk3" B22_VOX="$GD/BD_VoxelPack.pk3"
export B22_BUILD="$W" B22_RIG="$W/bin" B22_PK3="$P"
cd "$DEPOT/tools/rig"
sleep 4		# yield: another tool already waiting on the lock goes first
flock -o -x "$LOCK" bash -c "cp \"\${INT20_INI:-$W/ini.pristine}\" \"$W/bin/config/qzdoom.ini\"; exec python3 -c 'import sys,rig; rc,t=rig.run(sys.argv[1],sys.argv[2],int(sys.argv[3]),tuple(sys.argv[4:])); print(\"rc\",rc)' \"\$@\"" _ "$N" "$C" "$T" "$@"
