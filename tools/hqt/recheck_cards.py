#!/usr/bin/env python3
"""recheck_cards.py <cards-root> [--only set/gun] [--label PATH] [--out REPORT.md]

The regression gate for md3label. For every <set>/<gun>/<name>.card that has its <name>.md3 beside it,
rebuild the md3label command the card records (archetype, idle frame, bore/down, the surf -> role list
under `parts`, the `carve` line, the body = the one surface the parts list leaves out), run it into a
scratch folder, and compare what md3label writes against what the card holds:

  parts rows (role, surf, rest, axis, travel, frames, rot), the port rows (mag_well, chamber, eject,
  muzzle), grip, support, phases, baked_cant, authoring (verts only), the carved md3s byte for byte.

Everything else on a card is someone else's (owner comments, statephase's `states`, blendcard's blocks,
the bd22 hold) and is not compared. A card is MATCH when every compared line is identical. Any DIFF is
either a fix we can name or a break; there is no third kind.

Exit code 0 when every card matches, 1 otherwise. Writes a markdown report.
"""
import sys, os, re, glob, subprocess, tempfile, argparse, filecmp

HERE = os.path.dirname(os.path.abspath(__file__))
COMPARED = ('parts', 'grip', 'support', 'phases', 'baked_cant', 'authoring', 'carve')
PORT_ROWS = ('mag_well', 'chamber', 'eject', 'muzzle', 'load')


def parse(path):
    """-> dict: archetype, idle, bore, down, assign {surf: role}, carve [roles], body, lines {section: [str]}"""
    c = dict(assign={}, carve=[], lines={k: [] for k in COMPARED}, surfs=set())
    sec = None
    for raw in open(path, encoding='utf-8', errors='replace'):
        line = raw.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        body = line.split('#', 1)[0].rstrip()
        ind = len(line) - len(line.lstrip())
        if ind == 2:
            key = body.split()[0]
            sec = key
            rest = body.split(None, 1)[1] if len(body.split(None, 1)) > 1 else ''
            if key == 'archetype': c['archetype'] = rest.split()[0]
            elif key == 'model':
                m = re.search(r'idle_frame\s+(\d+)', rest); c['idle'] = int(m.group(1)) if m else None
                c['model'] = rest.split()[0]
            elif key == 'bore':
                v = re.findall(r'\[([^\]]*)\]', rest); c['bore'] = v[0].replace(' ', ''); c['down'] = v[1].replace(' ', '')
            elif key == 'carve': c['carve'] = rest.split(); c['lines']['carve'].append(body.strip())
            elif key in ('grip', 'support', 'baked_cant'): c['lines'][key].append(body.strip())
            elif key == 'authoring':
                m = re.search(r'verts\s+(\d+)', rest); c['lines']['authoring'].append('verts %s' % (m.group(1) if m else '?'))
            elif key == 'carved':
                role = rest.split()[0]; c.setdefault('carved', []).append(role)
                m = re.search(r'surfs\s+\[([^\]]*)\]', rest)
                if m:
                    for i in m.group(1).split(','):
                        if i.strip(): c.setdefault('carved_assign', {})[int(i)] = role
        elif ind == 4 and sec == 'parts':
            toks = body.split()
            if len(toks) > 2 and toks[1] == 'surf':
                c['assign'][int(toks[2])] = toks[0]; c['surfs'].add(int(toks[2]))
            c['lines']['parts'].append(body.strip())
        elif ind == 4 and sec == 'phases':
            c['lines']['phases'].append(body.strip())
    for i, role in c.get('carved_assign', {}).items():
        if i in c['assign'] and c['assign'][i] != role and re.fullmatch(role + r'\d+', c['assign'][i]):
            c['assign'][i] = role
    return c


def command(card, md3, out, name, label):
    a = card
    cmd = [sys.executable, label, md3, out, name, '--archetype', a.get('archetype', 'pistol_mag'),
           '--bore', a.get('bore', '1,0,0'), '--down', a.get('down', '0,0,-1'), '--no-stabilize-check']
    if a.get('idle') is not None: cmd += ['--idle', str(a['idle'])]
    cmd += ['--carve', ','.join(a['carve'])]
    if a['assign']: cmd += ['--assign', ','.join('%d=%s' % (k, v) for k, v in sorted(a['assign'].items()))]
    if a['surfs']:
        nsurf = nsurfs(md3)
        gaps = [i for i in range(nsurf) if i not in a['surfs']]
        if len(gaps) == 1 and gaps[0] != biggest(md3): cmd += ['--body', str(gaps[0])]
    return cmd


def nsurfs(md3):
    import struct
    d = open(md3, 'rb').read(); return struct.unpack_from('<i', d, 4 + 4 + 64 + 4 + 4 + 4)[0]


def biggest(md3):
    sys.path.insert(0, HERE); from md3read import read_md3
    S = read_md3(md3)['surfs']; return max(range(len(S)), key=lambda i: S[i]['nverts'])


def run_once(card, md3, out, name, label, body):
    cmd = command(card, md3, out, name, label)
    if body is not None:
        if '--body' in cmd: cmd[cmd.index('--body') + 1] = str(body)
        else: cmd += ['--body', str(body)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return cmd, r


def recheck(card_path, label):
    folder = os.path.dirname(card_path); name = os.path.basename(card_path)[:-5]
    md3 = os.path.join(folder, name + '.md3')
    if not os.path.exists(md3): return 'SKIP', ['no %s.md3 beside the card' % name]
    card = parse(card_path)
    gaps = [i for i in range(nsurfs(md3)) if i not in card['surfs']] if card['surfs'] else []
    bodies = gaps if len(gaps) > 1 else [None]
    best = None
    for body in bodies:
        with tempfile.TemporaryDirectory() as out:
            res = recheck_body(card, md3, out, name, label, body, folder)
            if best is None or (res[0] == 'DIFF' and best[0] == 'DIFF' and len(res[1]) < len(best[1])) or (res[0] == 'MATCH'):
                best = res if body is None else (res[0], (['body surf %d (inferred: the parts list leaves %s out)' % (body, gaps)] if res[0] != 'MATCH' else []) + res[1])
            if best[0] == 'MATCH': break
    return best


def recheck_body(card, md3, out, name, label, body, folder):
    if True:
        cmd, r = run_once(card, md3, out, name, label, body)
        if r.returncode != 0: return 'ERROR', [' '.join(cmd[1:]), (r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else 'no output']
        new = os.path.join(out, name + '.card')
        if not os.path.exists(new): return 'ERROR', ['md3label wrote no card']
        n = parse(new); diffs = []
        for sec in COMPARED:
            a, b = card['lines'][sec], n['lines'][sec]
            if a != b:
                for x in a:
                    if x not in b: diffs.append('- %s' % x)
                for x in b:
                    if x not in a: diffs.append('+ %s' % x)
        for part in card.get('carved', []):
            f = '%s_%s.md3' % (name, part); old, newf = os.path.join(folder, f), os.path.join(out, f)
            if not os.path.exists(old): continue
            if not os.path.exists(newf): diffs.append('- carved %s (not re-made by md3label: another tool made it)' % f); continue
            if not filecmp.cmp(old, newf, shallow=False): diffs.append('! carved %s differs' % f)
        return ('MATCH' if not diffs else 'DIFF'), diffs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root'); ap.add_argument('--only', default=''); ap.add_argument('--label', default=os.path.join(HERE, 'md3label.py'))
    ap.add_argument('--out', default='')
    ap.add_argument('--baseline', default='', help='an earlier report: list only the cards whose result changed')
    a = ap.parse_args()
    cards = sorted(glob.glob(os.path.join(a.root, '*', '*', '*.card')))
    cards = [c for c in cards if '.blend.card' not in c and a.only in c]
    rows = []; tally = {}
    for c in cards:
        st, d = recheck(c, a.label); tally[st] = tally.get(st, 0) + 1
        rows.append((os.path.relpath(c, a.root), st, d))
        print('%-6s %s' % (st, os.path.relpath(c, a.root)), flush=True)
        for x in d: print('       ', x)
    rep = ['# recheck_cards: %s' % '  '.join('%s %d' % kv for kv in sorted(tally.items())), '',
           'md3label: `%s`' % os.path.relpath(a.label), '', '| card | result | detail |', '|---|---|---|']
    for rel, st, d in rows: rep.append('| %s | %s | %s |' % (rel, st, '<br>'.join(x.replace('|', '\\|') for x in d)))
    if a.out: open(a.out, 'w').write('\n'.join(rep) + '\n')
    print('\n' + rep[0])
    if a.baseline:
        base = {}
        for line in open(a.baseline):
            if line.startswith('| ') and not line.startswith('| card'):
                cells = [x.strip() for x in line.strip().strip('|').split('|')]
                if len(cells) == 3: base[cells[0]] = (cells[1], cells[2])
        changed = [(rel, st, d) for rel, st, d in rows if base.get(rel) != (st, '<br>'.join(x.replace('|', '\\|') for x in d))]
        print('\nagainst %s: %d card(s) changed' % (a.baseline, len(changed)))
        for rel, st, d in changed:
            print('  %-6s %s   (was %s)' % (st, rel, base.get(rel, ('absent',))[0]))
            for x in d: print('         ', x)
        sys.exit(0 if not changed else 1)
    sys.exit(0 if set(tally) <= {'MATCH', 'SKIP'} else 1)


if __name__ == '__main__':
    main()
