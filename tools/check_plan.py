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
staged = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'], cwd=R, capture_output=True, text=True).stdout.splitlines()  # one path per line: paths may hold spaces
errs = []
first = subprocess.run(['git', 'rev-parse', '--verify', '-q', 'HEAD'], cwd=R, capture_output=True).returncode != 0
if not first and any(p.startswith('runtime/') for p in staged):
    errs.append('runtime/ is frozen (the 1.96b snapshot). Build changes into sets/, never here.')
plan = open(os.path.join(R, 'PLAN.md')).read()
cur = re.search(r'Current step: \*\*(\w+)\*\*', plan)
items = set(re.findall(r'^- (\w+) ', plan, re.M))
# "none" is a real state this checker did not model: every flagship item built, the work waiting on
# the owner's headset pass. It is NOT a free pass -- it is accepted only while every `- F<n>` line is
# marked DONE, so the completion claim is verified here rather than taken on trust. To do new work,
# add an F item in a [plan] commit and name it as the current step; `none` will not cover it.
undone = [i for i, body in re.findall(r'^- (F\d+)  (.*)$', plan, re.M) if 'DONE' not in body]
if not cur:
    errs.append('PLAN.md has no "Current step: **X**" line.')
elif cur.group(1) == 'none':
    if undone:
        errs.append('PLAN.md "Current step" is **none**, but these are not marked DONE: %s'
                    % ' '.join(undone))
elif cur.group(1) not in items:
    errs.append('PLAN.md "Current step" must be **none** or one of: %s' % ' '.join(sorted(items)))
# NO STILL FRAMES IN PLACE OF ANIMATED GUNS (owner, 2026-10-27: "every single one of my md3s is animated
# with dozens and dozens of frames"). The Plus/Vanilla/Modern sets were built from REMA's *_wm.md3, which
# are single-frame reference meshes the owner ruled out on 2026-10-25, so every gun in them is a still. A
# staged set mesh is refused when it is a *_wm.md3 or has ONE frame, unless the set lists it in
# sets/<set>/single_frame_ok.txt with a reason (a carved part that truly never animates; one path + reason
# per line). `python3 tools/check_plan.py --audit` lists every set mesh this would refuse today.
import struct
def md3_frames(path):
    try:
        with open(path, 'rb') as f: h = f.read(80)
        return struct.unpack('<i', h[76:80])[0] if h[:4] == b'IDP3' else None
    except OSError:
        return None
def still_frame_errors(paths):
    out = []
    for p in paths:
        if not (p.startswith('sets/') and p.lower().endswith('.md3')): continue
        st = p.split('/')[1]
        okf = os.path.join(R, 'sets', st, 'single_frame_ok.txt')
        ok = set(l.split()[0] for l in open(okf) if l.strip() and not l.startswith('#')) if os.path.exists(okf) else set()
        n = md3_frames(os.path.join(R, p))
        if p.lower().endswith('_wm.md3'):
            out.append('%s is a REMA *_wm.md3 single-frame reference (ruled out 2026-10-25): use the animated original' % p)
        elif n == 1 and p not in ok:
            out.append('%s has 1 frame: use the animated original, or list it in sets/%s/single_frame_ok.txt with a reason' % (p, st))
    return out
if '--audit' in sys.argv:
    allm = subprocess.run(['git', 'ls-files', 'sets'], cwd=R, capture_output=True, text=True).stdout.split()
    bad = still_frame_errors(allm)
    print('\n'.join(bad)); print('%d set mesh(es) would be refused' % len(bad)); sys.exit(0)
errs += still_frame_errors(staged)
known = {'runtime', 'sets', 'tools', 'gate', 'dist', 'docs', '.github'}
for p in staged:
    top = p.split('/')[0]
    if '/' in p and top not in known:
        errs.append('new top-level directory %r is not in the plan (HANDOFF.md table). Add it to PLAN.md in a [plan] commit first.' % top)
        break
staged_src = [p for p in staged if p.startswith('sets/bd22q_1.97/src/')]
if staged_src:
    # THE STAMP MUST BE CURRENT, not merely present. Until 2026-10-24 this only asked whether
    # the file existed -- and the stages wrote their stamp to the BUILD dir, so the one in the
    # set was never touched by anything and the check passed unconditionally from the day it
    # was added. `bd22_plus.py sync` writes it now, as part of the copy, so it certifies the
    # copy. Anything staged that is newer than the stamp did not come out of that run.
    stamp = os.path.join(R, 'sets/bd22q_1.97/.generated')
    if not os.path.exists(stamp):
        errs.append('sets/bd22q_1.97/src changed without the generators (no .generated stamp): run tools/bd22_plus.py sync, do not hand-edit.')
    else:
        ts = os.path.getmtime(stamp)
        newer = [p for p in staged_src
                 if os.path.exists(os.path.join(R, p)) and os.path.getmtime(os.path.join(R, p)) > ts + 2]
        if newer:
            errs.append('%d staged file(s) under sets/bd22q_1.97/src are NEWER than the .generated stamp, so they did not come from the generators: %s%s. Run tools/bd22_plus.py sync.'
                        % (len(newer), ', '.join(newer[:3]), ' ...' if len(newer) > 3 else ''))
if errs:
    print('check_plan: REFUSED\n  - ' + '\n  - '.join(errs)); sys.exit(1)
print('check_plan: ok (step %s)' % cur.group(1))
