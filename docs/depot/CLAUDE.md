**NO DRIFT. FOCUS ON WEAPON SET PRODUCTION.**
**USE TOOLS IN REPO. NOWHERE ELSE.**
(owner, 2026-10-24 04:39: these two instructions stand above everything else in this repo)

# RSQ Weapon Depot: the workshop (owner: presidentkoopa)

This repo is where weapon sets are turned into VR sets as good as BD22 VR Weapons Q: hands on every gun,
reloads by hand, live scopes, melee, all on a stock QuestZDoom 17.3. Take a set from `sets/`, follow
`docs/handbook/`, and build it with the tools in `tools/`.

## Before anything
1. Read `docs/handbook/README.md`, then `PLAN.md` and `HANDOFF.md`. The plan's "Current step" is your job.
2. Run `sh tools/install_hooks.sh` once. Every commit message starts with `[step <id>]` (an id PLAN.md
   lists) or `[plan]`. `tools/check_plan.py` refuses drift.
3. If the plan does not list it, do not build it. To change the plan: a `[plan]` commit with one line of
   reason, and the owner's yes BEFORE building.

## The owner's standing rules
- **No engine changes to QuestZDoom 17.3.** Everything is ZScript, DECORATE, MODELDEF and data.
- **Load order and zero script errors before the headset.** Nothing goes to the owner until it ran on
  doom2 -> brutal22test6 -> BD_VoxelPack -> the pack with no script error from the pack. Asked "do you
  have a pk3?" before that, the answer is "not yet".
- **Shown working only.** Working means in-engine frames or a log of the behaviour, never "the code
  exists" or "it compiles". VR behaviour is "rig only, not headset-confirmed" until the owner says so.
- **One method.** The drawn wrist is pinned to the controller; the GUN moves to the hand, and everything
  on the gun moves with it (muzzle, ejection port, reload rows, scope, recoil rows, melee points).
- **Start from the existing poses.** Never solve a grip from scratch when a named pose fits.
- **Variants copy rows.** A Purist or other variant copies its base gun's rows; it is never re-fitted.
- **Measure, don't guess.** Every number comes from a mesh (tool-measured) or the parent mod's code
  (parsed). Say which. Don't ask the owner to check what a tool can check.
- **Look at every frame.** Numbers lie: an open palm floating under a gun passed every numeric check.
- **Commit every tool and pose.** A committed tool never imports from or defaults to an uncommitted
  folder. The FBX hand is in the repo at `tools/handfit/core/fbx_hand/` (owner, 2026-10-28); `RSQ_FBX` overrides it.
- **Say a blocker the moment it appears.** Never work round it silently. Don't narrate tests every turn.
- Never tell the owner when to sleep or work. Stop when told to stop. Discuss before new projects.
- Keep `HANDOFF.md` current: what is done (measured), what is not, what is open, in that order.
