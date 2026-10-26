"""run_all.py -- every reloadable donor through run_gate.py, one at a time, and a summary.

    python3 -B gate/run_all.py <pk3> [--vr] [--only A,B] [--handles] [run_gate options]

The donors are read from the reload tables (RSR_Guns / RSP_Guns / RSB_Guns SlotForDonor) and kept
when the shelf has them. One at a time: the rig renders slower than the tics, and two engines at
once have made a held gesture fall between frames (false failures). --handles: only the magazine
guns with a charging handle. Writes gate/out/SUMMARY[_vr].txt; exit 1 if any failed.
"""
import os, re, sys, subprocess
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import run_gate as G


def donors():
    out = []
    for f in ('rsr_guns.ms.zs', 'rsr_pump_guns.zs', 'rsb_guns.zs'):
        t = open(os.path.join(G.ROOT, 'zscript_depot/rsr', f), encoding='utf-8').read()
        for d in re.findall(r'donor == "(\w+)"\)\s*return \d+;', t):
            if d not in out:
                out.append(d)
    keep = []
    for d in out:
        try:
            G.shelf_pick(d)
            keep.append(d)
        except StopIteration:
            pass
    return keep


def main():
    pk3 = sys.argv[1]
    vr = '--vr' in sys.argv
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
    pas = [x for x in sys.argv[2:] if x not in ('--handles',) and not (only and x in (','.join(only), '--only'))]
    ds = [d for d in donors() if not only or d in only]
    if '--handles' in sys.argv:
        ds = [d for d in ds if G.pump_slot(d) == 0 and G.break_slot(d) == 0 and G.has_handle(d)]
    res = []
    for d in ds:
        r = subprocess.run([sys.executable, '-B', os.path.join(H, 'run_gate.py'), pk3, d] + pas,
                           capture_output=True, text=True, timeout=4000)
        fails = [l.split()[0] for l in r.stdout.splitlines() if l.rstrip().endswith('FAIL') and not l.startswith(('PASS', 'FAIL'))]
        ok = re.search(r'^PASS', r.stdout, re.M) is not None
        line = '%-26s %s%s' % (d, 'PASS' if ok else 'FAIL', '' if ok else '  ' + ' '.join(fails))
        print(line, flush=True)
        res.append((d, ok, line))
    n = sum(1 for _, ok, _ in res if ok)
    tail = '%d of %d PASS%s' % (n, len(res), ' (VR rig)' if vr else ' (desktop)')
    print(tail)
    open(os.path.join(H, 'out', 'SUMMARY%s.txt' % ('_vr' if vr else '')), 'w').write('\n'.join(l for _, _, l in res) + '\n' + tail + '\n')
    return 0 if n == len(res) else 1


if __name__ == '__main__':
    sys.exit(main())
