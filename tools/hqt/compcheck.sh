#!/bin/bash
# compcheck.sh <pk3>: load a pack on a PC build of the engine (UZDXREMA) and say OK / script errors / HANG.
# Paths come from the environment: REMA_BIN (doomxr), REMA_IWAD, REMA_INI, REMA_BASE (a pk3 loaded before the one under test).
export DISPLAY=:99 SDL_AUDIODRIVER=dummy ALSOFT_DRIVERS=null VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json
out=$(script -q -c "timeout -s KILL 45 ${REMA_BIN:?set REMA_BIN to the doomxr binary} -iwad ${REMA_IWAD:?set REMA_IWAD} -nosound -nomusic -nocrashdialog -norun -config ${REMA_INI:-/tmp/compcheck.ini} +vid_preferbackend 1 ${REMA_BASE:+-file $REMA_BASE} -file $1" /dev/null 2>&1 | sed 's/\x1b\[[0-9;]*[A-Za-z]//g' | tr -d '\r')
if echo "$out" | grep -aq 'Script error\|errors while'; then echo "$out" | grep -a 'Script error\|Unknown\|Expect\|errors while' | head -6; elif echo "$out" | grep -aq 'D_CheckNetGame\|Init Playloop\|P_Init'; then echo OK; else echo "HANG (last: $(echo "$out" | grep -av '^\s*$' | grep -av '^\[\.\.' | tail -1 | cut -c1-80))"; fi
