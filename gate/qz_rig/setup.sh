#!/bin/bash
# TEST ONLY. Rebuild the rig's engine from source at the commits in PINS, into build/ (gitignored),
# then install it into bin/. Only needed if bin/ is missing or must be rebuilt; bin/ is prebuilt.
#   sh gate/qz_rig/setup.sh
# Needs: git, cmake, make, clang or gcc, python3, SDL2/EGL/GLES/OpenAL/libvpx headers (Mesa).
# ~20-40 min the first time. Refuses to install anything that is not the pinned 17.3 engine.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; B="$HERE/build"
. "$HERE/PINS"
mkdir -p "$B/src"
fetch() {	# dir url rev
  [ -d "$1/.git" ] || { git init -q "$1"; git -C "$1" remote add origin "$2"; }
  [ "$(git -C "$1" rev-parse HEAD 2>/dev/null)" = "$3" ] || { git -C "$1" fetch -q --depth 1 origin "$3"; git -C "$1" checkout -q -f FETCH_HEAD; }
  [ "$(git -C "$1" rev-parse HEAD)" = "$3" ] || { echo "setup: $1 is not at $3" >&2; exit 3; }
}
fetch "$B/src/qzd" "$QZD_REPO" "$QZD_REV"
git -C "$B/src/qzd" submodule update -q --init --depth 1 2>/dev/null || true
( cd "$B/src/qzd" && { git apply --check "$HERE/engine/s_sound_log.patch" 2>/dev/null && git apply "$HERE/engine/s_sound_log.patch"; } || true )
fetch "$B/src/qzw" "$QZW_REPO" "$QZW_REV"
mkdir -p "$B/rig"; cp -a "$HERE/engine/." "$B/rig/"
QGZ="$B/src/qzd" JNI="$B/src/qzw/Projects/Android/jni" bash "$B/rig/build.sh"
zs=$(unzip -p "$B/rig/res/qzdoom.pk3" zscript.txt | head -1 | sed -n 's/^version "\(.*\)"/\1/p')
grep -aq "$ENGINE_VERSION" "$B/rig/qzdoom" && [ "$zs" = "$ZSCRIPT_VERSION" ] || { echo "setup: built engine does not match PINS (ZScript '$zs')" >&2; exit 3; }
cp "$B/rig/qzdoom" "$HERE/bin/"; cp -L "$B/rig/deps/zmusic-install/lib/libzmusic.so.1" "$HERE/bin/"
cp "$B/rig/res/qzdoom.pk3" "$B/rig/res/game_support.pk3" "$HERE/bin/res/"
cp "$B/rig/brightmaps.pk3" "$B/rig/lights.pk3" "$B/rig/game_widescreen_gfx.pk3" "$HERE/bin/"
echo "rig rebuilt and installed: $HERE/bin/qz  (QuestZDoom $QZD_TAG, engine $ENGINE_VERSION, ZScript $zs)"
