# 7. Working with Claude

BD22 2.0 was built by several Claude agents at once ("lanes"), run by one coordinating session, with the owner
deciding. What worked and what did not:

## Lanes
- **One lane, one job, one worktree, one branch.** `git worktree add <dir> -b <branch>`. Two lanes in one
  checkout once shipped each other's half-finished files in a build.
- **A brief per lane**, written so a stranger could do it: the goal in the owner's words with the time he said
  it, the files to read first (this handbook, `PLAN.md`, the set's `CLAUDE.md`), what "done" means (the rig
  proof it must show), a time box, and what NOT to touch. End every brief with: "report what is done (shown on
  the rig), what is not, what is open; rig only, not headset-confirmed".
- **Time-box every batch** and give the owner the sheet when the box ends, finished or not.
- **Merge in the coordinator, file by file**, for generated tables (`handtable.zs` was merged row by row).

## The machine
- The cloud box has **2 cores and 8 GB**. Run at most two lanes that use the engine or the fitter, and one engine
  at a time (`flock -o -x`, chapter 2.8). Four or five lanes at once made fits take 8-25 minutes instead of 2
  and got them killed for memory.
- **The fit farm**: heavy hand fits run on the owner's PC (16 cores) through the remote-device connection
  (`tools/handfit/farm/`, chapter 3.4). The bridge runs one request at a time: start a batch with `--detach` and
  poll its status file.
- Disk is shared: delete frame dumps as soon as the PNGs exist; keep run output in `work/`.

## Liveness
An interrupt of the coordinator, or a container restart, **silently stops every background lane**. After either,
and before reporting any lane as running: look at its files (newest modification time), its processes, and its
last log line. Never report a status from memory. Lanes commit and push verified work often, so a restart loses
little.

## Reviewing
- The coordinator looks at **every sheet** before anything is called done (rule 4). Numbers that pass and a
  frame that looks wrong means it is wrong.
- Every claim is shown: a frame, or a log line of the behaviour. "It compiles" and "the code is there" are not
  results.
- A lane says a blocker the moment it hits it, and does not work round it silently.

## What to ask a Claude session for
- "Port <gun> by the one method, starting from its 1.92 hold; show rest / steadied / firing from the eye and the
  side beside 1.92; rig only." (Chapter 4 is the recipe.)
- "Boot the set on the owner's load order and list every script error that is ours."
- "Run `rebake.py check` and `variants_all.py` and tell me what differs."
- Ask for a decision list, not a decision: an agent proposes, the owner decides (a grip that needs the gun
  tilted, a default, a gun with no reload). Agent messages are never the owner's approval.

Load [SKILL.md](SKILL.md) at the start of a session to get the method in one page.
