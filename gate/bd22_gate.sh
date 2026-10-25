#!/bin/sh
# bd22q's gate. Kept as the name HANDOFF.md and PLAN.md have always used; the work moved into
# gate/run_set.sh (generic) and gate/bd22q.gate (this set's paths, guns and ammo) on 2026-10-25
# so another lane can gate ITS set with the same tool. Everything this file used to carry --
# the absolute-path fix, +logfile, the xvfb test, rc before the grep, the marker counting -- is
# in run_set.sh, and the reasons are in gate/GATING_A_SET.md.
#
#     sh gate/bd22_gate.sh [pk3]
exec sh "$(dirname "$0")/run_set.sh" "$(dirname "$0")/bd22q.gate" "$@"
