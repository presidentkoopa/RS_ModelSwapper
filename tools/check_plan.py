#!/usr/bin/env python3
"""check_plan.py -- the no-drift check. Run as the pre-commit hook (tools/install_hooks.sh installs it).
Refuses the commit when:
  * PLAN.md's "Current step:" is not an item PLAN.md lists (or `none` while an F/W item is not DONE);
  * the commit adds a top-level directory the layout does not name (README.md, "The layout");
  * a set mesh is ADDED that is a REMA *_wm.md3 reference or has ONE frame and is not listed in
    sets/<set>/single_frame_ok.txt (owner, 2026-10-27: "every single one of my md3s is animated");
  * a file is committed that must never be: any .fbx other than the one FBX hand (tools/handfit/core/fbx_hand/), frame dumps (*.ppm),
    or anything under work/ (run output).
The commit message check ([step <id>] / [plan]) is in tools/commit-msg.
`python3 tools/check_plan.py --audit` lists every set mesh the mesh rule would refuse today.
"""
import os, re, struct, subprocess, sys

R = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True).stdout.strip()
# one path per line (paths may hold spaces). Added only for the mesh rule: a rename (R) of an existing set is not new work.
def staged(flt):
    return subprocess.run(['git', 'diff', '--cached', '-M', '-l20000', '--name-only', '--diff-filter=' + flt], cwd=R,
                          capture_output=True, text=True).stdout.splitlines()
errs = []

plan = open(os.path.join(R, 'PLAN.md')).read()
cur = re.search(r'Current step: \*\*(\w+)\*\*', plan)
items = set(re.findall(r'^- (\w+) ', plan, re.M))
undone = [i for i, body in re.findall(r'^- ([FW]\d+)  (.*)$', plan, re.M) if 'DONE' not in body]
if not cur:
    errs.append('PLAN.md has no "Current step: **X**" line.')
elif cur.group(1) == 'none':
    if undone:
        errs.append('PLAN.md "Current step" is **none**, but these are not marked DONE: %s' % ' '.join(undone))
elif cur.group(1) not in items:
    errs.append('PLAN.md "Current step" must be **none** or one of: %s' % ' '.join(sorted(items)))


def md3_frames(path):
    try:
        with open(path, 'rb') as f:
            h = f.read(80)
        return struct.unpack('<i', h[76:80])[0] if h[:4] == b'IDP3' else None
    except OSError:
        return None


def still_frame_errors(paths):
    out = []
    for p in paths:
        if not (p.startswith('sets/') and p.lower().endswith('.md3')):
            continue
        st = p.split('/')[1]
        okf = os.path.join(R, 'sets', st, 'single_frame_ok.txt')
        ok = set(l.split('\t')[0].split()[0] for l in open(okf) if l.strip() and not l.startswith('#')) if os.path.exists(okf) else set()
        n = md3_frames(os.path.join(R, p))
        if p.lower().endswith('_wm.md3'):
            out.append('%s is a REMA *_wm.md3 single-frame reference (ruled out 2026-10-25): use the animated original' % p)
        elif n == 1 and p not in ok:
            out.append('%s has 1 frame: use the animated original, or list it in sets/%s/single_frame_ok.txt with a reason' % (p, st))
    return out


if '--audit' in sys.argv:
    allm = subprocess.run(['git', 'ls-files', 'sets'], cwd=R, capture_output=True, text=True).stdout.splitlines()
    bad = still_frame_errors(allm)
    print('\n'.join(bad)); print('%d set mesh(es) would be refused' % len(bad)); sys.exit(0)

errs += still_frame_errors(staged('AM'))

# the layout (README.md "The layout"): nothing else at the top
KNOWN = {'tools', 'docs', 'sources', 'cards', 'zscript', 'zscript_depot', 'modeldef', 'models', 'sounds', 'quest', 'media', 'pk3', 'reload_1x', '.github'}   # RS_ModelSwapper since 2026-11-08
for p in staged('ACMR'):
    top = p.split('/')[0]
    if '/' in p and top not in KNOWN:
        errs.append('new top-level directory %r is not in the layout (README.md). Add it to PLAN.md in a [plan] commit first.' % top)
        break
for p in staged('ACMR'):
    low = p.lower()
    if low.endswith('.fbx') and p != 'tools/handfit/core/fbx_hand/hand_final.fbx':
        errs.append('%s: only tools/handfit/core/fbx_hand/hand_final.fbx is committed' % p)
    elif low.endswith('.ppm'):
        errs.append('%s: frame dumps are converted to PNG and deleted, never committed' % p)
    elif p.startswith('work/'):
        errs.append('%s: work/ is run output, never committed' % p)

if errs:
    print('check_plan: REFUSED\n  - ' + '\n  - '.join(errs)); sys.exit(1)
print('check_plan: ok (step %s)' % cur.group(1))
