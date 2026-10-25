# The VR gate's rig: the owner's Quest_Weapons_Kit `quest_test_rig`, built here

`run_gate.py --vr` runs on the owner's Quest-faithful Linux rig (Desktop\Quest_Weapons_Kit\quest_test_rig):
the engine compiled from QuestZDoom's Android source set with the Android defines, the real OpenXR
device mode (vr_mode 15) and the real VrInputDefault.cpp; only the OpenXR runtime / JNI layer is the
rig's glue. The gate's off hand there is a CONTROLLER (pose, grip, trigger), read by the pack's own
zscript_depot/rsvr/vrhand.zs -- not the fakehands.zs stand-in the desktop gate uses.

Built 2026-10-25 against emawind84/gzdoom tag qzd17.3 (9afc750) and emawind84/questzdoom a85c819:

    cp -r <kit>/quest_test_rig ~/qzlinux17 && cp -r gate/qz_rig/* ~/qzlinux17/
    cp /usr/lib/jvm/java-21-openjdk-amd64/include/jni.h /usr/lib/jvm/java-21-openjdk-amd64/include/linux/jni_md.h ~/qzlinux17/shim/
    cd ~/qzlinux17 && mv Makefile.txt Makefile && QGZ=<gzdoom qzd17.3> JNI=<questzdoom>/Projects/Android/jni ./build.sh

What this folder adds to the kit's rig:
- `glue/qz_linux_glue.cpp`: `__android_log_write`, and the TEST DRIVER HOOK -- ZScript may not set an
  engine cvar, so a test pack defining `qzt_lhand` / `qzt_lgrip` / `qzt_ltrigger` (and r-) in CVARINFO
  drives the controllers instead of `qz_*`. Without such a pack nothing changes.
- `shim/android/*.h`: Linux stand-ins for the NDK headers; `tools/pad_csv.py`: the language-CSV fix
  build.sh calls (both as the 2026-10-24 session's notes record).

Measured on the rig: stage -> world is 34 map units per metre, (F, L, U) = (-z, -x, y / pixelstretch) * 34
from the player's floor point; controller pitch 30 is level. The grip arrives as key 443, the off
trigger as key 42 -- the keys the reload already listens for. Screenshots are the eye buffer
(1024 x 1024); `--shots` tilts the head 40 degrees down to look at the hands (QZ_SHOT_HMD).
