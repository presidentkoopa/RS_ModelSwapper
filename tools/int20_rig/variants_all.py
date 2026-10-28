"""TEST ONLY: every Purist block (any model, not only hands) against the Brutal gun's block with the same frames.
variants_all.py <pk3>. Prints per Purist class: blocks equal / differing / with no Brutal block on the same frames."""
import re, sys, zipfile, collections
z = zipfile.ZipFile(sys.argv[1]); B = collections.defaultdict(list)
for n in z.namelist():
    if not n.split('/')[-1].upper().startswith('MODELDEF'): continue
    t = re.sub(r'//[^\n]*', '', z.read(n).decode('latin-1'))
    for m in re.finditer(r'Model\s+(\w+)\s*\{(.*?)\}', t, re.S | re.I):
        ls = [' '.join(l.split()) for l in m.group(2).splitlines() if l.strip()]
        fr = tuple(sorted(l for l in ls if l.lower().startswith('frameindex')))
        B[m.group(1).lower()].append((fr, tuple(sorted(ls))))
PN = {'puristpistol': 'brutalpistol', 'puristsmg': 'brutalsmg'}
for c in sorted(B):
    if not c.startswith('purist'): continue
    b = PN.get(c, c[len('purist'):]); eq = dif = none = 0; bad = []
    idx = collections.defaultdict(list)
    for fr, body in B.get(b, []): idx[fr].append(body)
    for fr, body in B[c]:
        if fr not in idx: none += 1; bad.append(fr[:1]); continue
        if body in idx[fr]: eq += 1
        else: dif += 1; bad.append(fr[:1])
    print('%-30s vs %-24s equal %3d differ %2d no-match %2d %s' % (c, b, eq, dif, none, bad[:3] if dif or none else ''))
