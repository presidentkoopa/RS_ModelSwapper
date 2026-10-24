# To every Claude, coding agent or human picking this repo up

1. Read `HANDOFF.md` in full, then `PLAN.md`. The plan's "Current step" is your job. Nothing else is.
2. Run `sh tools/install_hooks.sh` once. The pre-commit hook (`tools/check_plan.py`) refuses commits
   that drift; every commit message starts with `[step <id>]` from PLAN.md, or `[plan]`.
3. Do not invent steps, sets, toggles, names or tools. If the plan does not list it, you do not build
   it. If you believe the plan is wrong, change PLAN.md in a `[plan]` commit with one line of reason
   and get the owner's yes BEFORE building.
4. Never from memory: every number comes from a mesh (tool-measured) or the parent mod's code (parsed),
   and you say which. Don't guess, measure. Don't ask the owner to verify what a tool can check.
5. Nothing leaves this repo for the owner's headset until it has run on his load order
   (doom2 -> brutal22test6 -> BD_VoxelPack -> the pack) without a script error. Not even if asked
   "do you have a pk3" -- the answer is "not yet". The headless gate in `gate/` is optional tooling;
   the owner's headset pass is the test.
6. `runtime/` (1.96b) is frozen. Work goes in `sets/`, produced by the tools, never hand-edited.
7. No engine changes to QZD 17.3. Ermac's assets ship (REMA is 1/3 Ermac, 1/3 Emawind, 1/3 owner).
8. Say a blocker the moment it appears. Do not work around it silently. Do not narrate tests every turn.
9. Never tell the owner when to sleep or work. Stop when told to stop. Discuss before new projects.
10. Keep `HANDOFF.md` current: what is done (measured), what is not, what is open, in that order.
