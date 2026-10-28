"""TEST ONLY: do Purist variants carry the Brutal gun's FBX hand rows? (built pk3, all MODELDEF lumps)"""
import re, sys, zipfile, collections
z = zipfile.ZipFile(sys.argv[1])
blocks = collections.defaultdict(list)	# class -> [normalized body of each fbx_hand block]
for n in z.namelist():
    if not n.split('/')[-1].upper().startswith('MODELDEF'): continue
    t = re.sub(r'//[^\n]*', '', z.read(n).decode('latin-1'))
    for m in re.finditer(r'Model\s+(\w+)\s*\{(.*?)\}', t, re.S | re.I):
        if 'fbx_hand' in m.group(2).lower():
            body = '\n'.join(sorted(l.strip() for l in m.group(2).strip().splitlines() if l.strip()))
            blocks[m.group(1).lower()].append(body)
PN = {'BrutalPistol': 'PuristPistol', 'BrutalSMG': 'PuristSMG'}
classes = sys.argv[2].split(',')
for c in classes:
    b, p = blocks.get(c.lower(), []), blocks.get(PN.get(c, 'purist' + c).lower(), [])
    if not b:
        print('%-24s Brutal: no FBX hand blocks' % c); continue
    same = sorted(b) == sorted(p)
    missing = len(set(b) - set(p))
    print('%-24s Brutal %3d blocks | %-28s %3d blocks | %s' % (c, len(b), PN.get(c, 'Purist' + c), len(p), 'SAME ROWS' if same else ('MISSING ALL' if not p else '%d Brutal blocks not in Purist' % missing)))
