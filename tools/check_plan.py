#!/usr/bin/env python3
"""check_plan.py -- the no-drift check (HANDOFF.md "No drift"). Run as the pre-commit hook.
Refuses the commit when:
  * anything under runtime/ is staged (the 1.96b snapshot is frozen);
  * PLAN.md's "Current step:" is not an item PLAN.md lists;
  * the commit adds a top-level directory PLAN.md / HANDOFF.md do not name;
  * sets/bd22q_1.97/src is staged but tools/bd22_plus.py or tools/bd22_mg.py are not what produced it
    (a .generated stamp written by the tools; hand edits have no stamp).
The commit message check ([step N] / [plan]) is in tools/commit-msg.
"""
import os, re, subprocess, sys
R = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
staged = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'], cwd=R, capture_output=True, text=True).stdout.split()
errs = []
first = subprocess.run(['git', 'rev-parse', '--verify', '-q', 'HEAD'], cwd=R, capture_output=True).returncode != 0
if not first and any(p.startswith('runtime/') for p in staged):
    errs.append('runtime/ is frozen (the 1.96b snapshot). Build changes into sets/, never here.')
plan = open(os.path.join(R, 'PLAN.md')).read()
cur = re.search(r'Current step: \*\*(\w+)\*\*', plan)
items = set(re.findall(r'^- (\w+) ', plan, re.M))
if not cur or cur.group(1) not in items:
    errs.append('PLAN.md "Current step" must be one of: %s' % ' '.join(sorted(items)))
known = {'runtime', 'sets', 'tools', 'gate', 'dist', 'docs', '.github'}
for p in staged:
    top = p.split('/')[0]
    if '/' in p and top not in known:
        errs.append('new top-level directory %r is not in the plan (HANDOFF.md table). Add it to PLAN.md in a [plan] commit first.' % top)
        break
if any(p.startswith('sets/bd22q_1.97/src/') for p in staged):
    stamp = os.path.join(R, 'sets/bd22q_1.97/.generated')
    if not os.path.exists(stamp):
        errs.append('sets/bd22q_1.97/src changed without the generators (no .generated stamp): run tools/bd22_plus.py apply && tools/bd22_mg.py, do not hand-edit.')
if errs:
    print('check_plan: REFUSED\n  - ' + '\n  - '.join(errs)); sys.exit(1)
print('check_plan: ok (step %s)' % cur.group(1))
