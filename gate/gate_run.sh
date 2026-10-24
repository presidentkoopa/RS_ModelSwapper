#!/bin/bash
# one launch per set: parse, start a map, give every gun, cycle them, quit
set=$1; pk3=/home/claude/c2q/dist/RSQ_$set.pk3; log=/home/claude/gate/$set.log
guns=$(python3 -c "import json;print(' '.join('give '+c+';' for c in [r[0] for r in json.load(open('/home/claude/c2q/build/RSQ_$set/genpack_report.json'))['report'] if not r[0].startswith('(')]))")
cmd="wait 35; $guns wait 10; weapnext; wait 8; weapnext; wait 8; weapnext; wait 8; weapnext; wait 8; weapnext; wait 8; weapnext; wait 8; weapnext; wait 8; weapnext; wait 8; echo GATE_FIRE; +attack; wait 20; -attack; wait 5; echo GATE_RELOAD; +reload; wait 3; -reload; wait 45; echo GATE_DONE; quit"
cd /home/claude/qgz/build
HOME=/home/claude/gate LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe timeout 150 xvfb-run -a -s "-screen 0 1024x768x24 +extension GLX" stdbuf -oL -eL ./qzdoom -iwad /usr/share/games/doom/freedoom2.wad -file $pk3 \
  -nosound -nomusic +vr_mode 0 +vid_preferbackend 0 -width 640 -height 480 -warp 1 +"$cmd" -stdout > $log 2>&1
echo "== $set exit $?"; grep -n -i "script parsing took\|error\|abort\|fatal\|unknown\|not found\|could not\|warning" $log | grep -v "Warning: freedoom\|Could not find.*in\b" | head -40
