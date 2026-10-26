#!/bin/bash
# TEST ONLY, never ships. One command from a fresh clone to a working rig:
#   sh tools/rig/setup.sh          the test packs (seconds); the rig itself is prebuilt in bin/
#   sh tools/rig/setup.sh build    also rebuild the engine from source into build/rig/
# Builds everything under tools/rig/build/ (gitignored):
#   build/src/qzd   emawind84/gzdoom @ QZD_REV (4.14.3, the owner's QZD17 engine), + s_sound_log.patch
#   build/src/qzw   emawind84/questzdoom @ QZW_REV (the Android wrapper: VR input code, headers)
#   build/rig/      the Linux rig: real QZD engine, OpenXR replaced by glue/qz_linux_glue.cpp
#   build/probe.pk3, build/upstream.pk3   test-only zscript (log lines; upstream attackdown)
#   build/BD22Q_now.pk3   this depot's sets/bd22q_1.97/src
#   build/BD22Q_192.pk3   RS_Brutal22WeaponsQ tag 1.92 (the owner's behavioural baseline)
# Needs: git, cmake, make, a C++ compiler, zip, python3 + Pillow, libGLES/EGL (mesa), openal.
# The game data is the owner's: doom2.wad, brutal22test6.pk3, BD_VoxelPack.pk3. rig.py looks in
# /mnt/user-data/uploads (where the cloud session had them) or B22_IWAD / B22_BD22 / B22_VOX.
set -e
QZD_REV=9afc750917bf54870f2d16b7ba0d00f2b77e6fb5
QZW_REV=a85c81947219a5602df64694cb9e80c09380a3a4
HERE="$(cd "$(dirname "$0")" && pwd)"; DEPOT="$(cd "$HERE/../.." && pwd)"; B="$HERE/build"
mkdir -p "$B/src" "$B/logs" "$B/shots"

fetch() {	# dir url rev
  [ -d "$1/.git" ] || { git init -q "$1"; git -C "$1" remote add origin "$2"; }
  [ "$(git -C "$1" rev-parse HEAD 2>/dev/null)" = "$3" ] || { git -C "$1" fetch -q --depth 1 origin "$3"; git -C "$1" checkout -q -f FETCH_HEAD; }
}
if [ "$1" = build ]; then	# only to rebuild the engine from source; bin/ is the prebuilt rig
  fetch "$B/src/qzd" https://github.com/emawind84/gzdoom "$QZD_REV"
  git -C "$B/src/qzd" submodule update -q --init --depth 1 2>/dev/null || true
  ( cd "$B/src/qzd" && { git apply --check "$HERE/s_sound_log.patch" 2>/dev/null && git apply "$HERE/s_sound_log.patch"; } || true )
  fetch "$B/src/qzw" https://github.com/emawind84/questzdoom "$QZW_REV"
  # build.sh reads the ZMusic pin from the wrapper's submodule entry
  git -C "$B/src/qzw" fetch -q --depth 1 origin "$QZW_REV" 2>/dev/null || true
  mkdir -p "$B/rig"; cp -a "$HERE/engine/." "$B/rig/"
  QGZ="$B/src/qzd" JNI="$B/src/qzw/Projects/Android/jni" bash "$B/rig/build.sh"
fi
( cd "$HERE/probe" && rm -f "$B/probe.pk3" && zip -q -r "$B/probe.pk3" . )
T=$(mktemp -d); cp "$HERE/upstream_zscript.txt" "$T/zscript.txt"; cp "$HERE/upstream_MAPINFO.txt" "$T/MAPINFO.txt"
( cd "$T" && rm -f "$B/upstream.pk3" && zip -q -r "$B/upstream.pk3" . ); rm -rf "$T"
( cd "$DEPOT/sets/bd22q_1.97/src" && rm -f "$B/BD22Q_now.pk3" && zip -q -r "$B/BD22Q_now.pk3" . )
if [ ! -f "$B/BD22Q_192.pk3" ]; then
  fetch "$B/src/bd22q_192" https://github.com/presidentkoopa/RS_Brutal22WeaponsQ refs/tags/1.92 2>/dev/null || \
    { rm -rf "$B/src/bd22q_192"; git clone -q --depth 1 --branch 1.92 https://github.com/presidentkoopa/RS_Brutal22WeaponsQ "$B/src/bd22q_192"; }
  ( cd "$B/src/bd22q_192/src" && zip -q -r "$B/BD22Q_192.pk3" . )
fi
echo "rig ready: $HERE/bin/qz   try: cd $HERE && python3 cmp2.py build/BD22Q_192.pk3 build/BD22Q_now.pk3 Pistol t1"
