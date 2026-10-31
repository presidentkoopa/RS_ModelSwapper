#!/usr/bin/env bash
# run_replay.sh -- headless replay run for the weapon audit (Linux, Xvfb + llvmpipe).
#
#   run_replay.sh <engine-binary> <iwad> <replay.vrr> <out-dir> [tics] [extra engine args...]
#
# Writes <out-dir>/stdout.log and <out-dir>/telemetry.log. A run is only verified when
# stdout.log shows the replay loaded, telemetry.log has T rows, and the engine exited by
# itself on the 'quit' we scheduled (exit 0). Anything else is a failed run, whatever the
# log says in the middle.
set -u
ENGINE=$1; IWAD=$2; REPLAY=$3; OUT=$4; TICS=${5:-300}; shift 5 2>/dev/null || shift $#
mkdir -p "$OUT"
export DISPLAY=:99
if ! xdpyinfo -display :99 >/dev/null 2>&1; then
  Xvfb :99 -screen 0 1280x720x24 >/dev/null 2>&1 &
  sleep 2
fi
# Vulkan through Mesa's lavapipe. NOT OpenGL: REMA's GL backend cannot compile main.fp since
# 0c3f2f30c (the '#include "shaders/glsl/beamglow.glsl"' line; only the Vulkan loader
# expands includes). Vulkan is also the only backend whose VR mode writes hand poses into
# the tic command, so it is the one the audit must run on anyway.
export SDL_AUDIODRIVER=dummy ALSOFT_DRIVERS=null
export VK_ICD_FILENAMES=${VK_ICD_FILENAMES:-/usr/share/vulkan/icd.d/lvp_icd.x86_64.json}
HOME_DIR=$(mktemp -d)
timeout -s KILL 120 "$ENGINE" -iwad "$IWAD" -nosound -nomusic -nocrashdialog \
  -config "$OUT/audit.ini" -savedir "$HOME_DIR" \
  +vid_preferbackend 1 +vid_fullscreen 0 \
  +"vr_telemetry $OUT/telemetry.log" +"vr_replay_play $REPLAY" \
  +map map01 +"wait $TICS; quit" "$@" > "$OUT/stdout.log" 2>&1
RC=$?
echo "exit=$RC" >> "$OUT/stdout.log"
if [ $RC -eq 255 ]; then echo "FATAL (engine exited on error):"; grep -aE "error|Error|redefine|Unknown|Expect" "$OUT/stdout.log" | head -8; fi
if [ $RC -eq 124 ] || [ $RC -eq 137 ]; then
  # Hung past the cap: almost always an error dialog. Grab the screen so it can be shown at once.
  import -window root "$OUT/screen_on_timeout.png" 2>/dev/null
  echo "TIMED OUT after 120s -- screen saved to $OUT/screen_on_timeout.png"
fi
echo "--- $OUT: exit $RC"
grep -E 'vr_replay|vr_telemetry|Script error|VM execution|Segmentation|Abort' "$OUT/stdout.log" | head -20
if [ -f "$OUT/telemetry.log" ]; then
  echo "T rows: $(grep -c '^T ' "$OUT/telemetry.log")  S rows: $(grep -c '^S ' "$OUT/telemetry.log")  W rows: $(grep -c '^W ' "$OUT/telemetry.log")"
else
  echo "NO telemetry.log"
fi
exit $RC
