#!/bin/bash
# F1: run the bd22q pack on the owner's load order, headless, one launch. Edit the four paths.
# Pass = exit 0, no "Script error", no "Execution could not continue", GATE_DONE in the log.
QZD=/path/to/qzdoom-17.3/build          # stock qzd17.3 built -DNO_GTK=ON -DHAVE_VULKAN=OFF -DHAVE_GLES2=ON
IWAD=/path/to/doom2.wad                 # NOT Freedoom: BD_VoxelPack's voxeldef names Doom 2 sprites
BD22=/path/to/brutal22test6.pk3
VOX=/path/to/BD_VoxelPack.pk3
PK3=${1:-dist/BD22Q_197pre.pk3}         # python3 tools/bd22_plus.py pk3 dist/BD22Q_197pre.pk3
LOG=gate/bd22_197.log
cmd="wait 40; echo GATE_START; give MG42; give Flamethrower2; give Unmaker; give Machinegun; give Clip2 200; give Gas 200; give SoulAmmo 60; give AmmoRocket 5; wait 5; use Machinegun; wait 10; echo GATE_FIRE; +attack; wait 15; -attack; wait 5; +altattack; wait 3; -altattack; wait 10; +reload; wait 3; -reload; wait 40; use MG42; wait 10; +attack; wait 15; -attack; wait 5; +reload; wait 3; -reload; wait 20; use Flamethrower2; wait 10; +attack; wait 15; -attack; wait 5; +reload; wait 3; -reload; wait 20; use Unmaker; wait 10; +attack; wait 15; -attack; wait 5; +reload; wait 3; -reload; wait 20; echo GATE_DONE; quit"
cd "$QZD" && HOME=$(dirname "$LOG") LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe timeout 420 xvfb-run -a -s "-screen 0 1024x768x24 +extension GLX" stdbuf -oL -eL ./qzdoom -iwad "$IWAD" -file "$BD22" "$VOX" "$PK3" -nosound -nomusic +vr_mode 0 +vid_preferbackend 0 -width 640 -height 480 -warp 1 +"$cmd" -stdout > "$LOG" 2>&1
echo "exit $?"
grep -n -i "script error\|GATE_\|execution could not\|abort\|crash\|errors,\|VM execution\|Tried to\|Unknown\|not found\|invalid" "$LOG" | grep -v "FindModel\|Deh_Actor\|REGT\|BrutalWeapon\|limbs.dec\|aaliens\|eeevilll\|BDMummy\|Crush from actor Actor\|BBled1\|BrutalNightmareDemon"
# On Windows (the owner's PC): same -file order in ZDL; read the log for the same strings.
