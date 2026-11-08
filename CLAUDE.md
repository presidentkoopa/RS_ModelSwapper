# RS_ModelSwapper: standing rules (owner: presidentkoopa)

**Only `main` matters.** (owner, 2026-11-01) Every other branch (`modelswapper-2.0-bd22-lift`,
`archive/pre-cards-2026-10-31`) is dead: do not work from it, merge it or take anything from it.
Before beginning any work in this repo, tell the owner what you are about to do and wait for his confirmation.

## Since 2026-11-08: the Depot lives here
RSQ_WeaponDepot (the toolset, the test rig, the handbook) was merged into this repo; its rules came with it and
stand (`docs/depot/CLAUDE.md` is the original text). The ones that matter every day:
- **NO DRIFT.** `PLAN.md` lists the work; the plan's "Current step" is the job. Run `sh tools/install_hooks.sh` once:
  every commit message starts with `[step <id>]` or `[plan]`, `tools/check_plan.py` refuses what the plan does not list.
- **USE TOOLS IN REPO. NOWHERE ELSE.** Every path through `tools/depot.py` or an environment variable.
- **The cards are trusted. The tools that made them are trusted.** `tools/hqt/recheck_cards.py cards --baseline
  tools/hqt/RECHECK_BASELINE.md` must report no change after any tool edit, or every change it reports is a fix with a
  name. Everything else in this repo (the ZScript systems, the generators, the reload tables) is "compiled, not
  re-verified" until it ran on the rig (owner, 2026-11-08).
- **Shown working only.** Working means in-engine frames or a log; never "the code exists". Rig only is not headset.
- **Measure, don't guess.** Every number comes from a mesh (tool-measured) or the parent mod's code (parsed).
- **Look at every frame.** Numbers lie.
- **Say a blocker the moment it appears.** Keep `HANDOFF.md` current: done (measured), not done, open, in that order.
- One build for Quest and PC VR is the goal; the Quest build is `build_pk3.py` / `build.ps1 -Static` today.
