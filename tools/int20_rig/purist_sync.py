"""BUILD helper (2.0 int r2, owner rule r3 item 23: variants copy the Brutal gun's rows): replace each Purist<Gun> block in
src/MODELDEF.purist whose FrameIndex set matches exactly one <Gun> block elsewhere in src/MODELDEF* with that block's body.
purist_sync.py <Gun> [<Gun> ...]"""
import re, glob, sys
pat = re.compile(r'^Model\s+(\S+)[ \t]*\n\{(.*?)^\}', re.M | re.S)
fr = lambda body: tuple(sorted(' '.join(l.split('//')[0].split()) for l in body.splitlines() if l.strip().lower().startswith('frameindex')))
for gun in sys.argv[1:]:
    src = []
    for f in sorted(glob.glob('src/MODELDEF*')):
        if f.endswith('.purist'): continue
        t = open(f, encoding='latin-1').read()
        src += [(f, m.group(2)) for m in pat.finditer(t) if m.group(1) == gun]
    p = 'src/MODELDEF.purist'; t = open(p, encoding='latin-1').read(); out, last = [], 0
    for m in pat.finditer(t):
        if m.group(1) != 'Purist' + gun: continue
        hits = [b for f, b in src if fr(b) == fr(m.group(2))]
        if len(hits) != 1 or hits[0] == m.group(2):
            print('Purist%s %s: %s' % (gun, fr(m.group(2))[:1], 'already the same' if hits and hits[0] == m.group(2) else '%d matches, left' % len(hits))); continue
        out += [t[last:m.start(2)], hits[0]]; last = m.end(2)
        print('Purist%s %s: copied from %s' % (gun, fr(m.group(2))[:1], [f for f, b in src if b == hits[0]][0]))
    out.append(t[last:]); open(p, 'w', encoding='latin-1').write(''.join(out))
