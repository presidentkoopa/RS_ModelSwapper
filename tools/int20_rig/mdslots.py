"""TEST ONLY: built-pk3 check that no MODELDEF block names a model slot at or above its LAST Model line + 1 (QZD 17.3
models.cpp sizes a block by the last Model line; min 4). mdslots.py <pk3>"""
import zipfile, re, sys
z = zipfile.ZipFile(sys.argv[1]); bad = 0
for n in z.namelist():
    if not n.split('/')[-1].upper().startswith('MODELDEF'): continue
    t = re.sub(r'//[^\n]*', '', z.read(n).decode('latin-1'))
    for m in re.finditer(r'Model\s+(\w+)\s*\{(.*?)\}', t, re.S | re.I):
        idx = [int(x) for x in re.findall(r'(?im)^\s*Model\s+(\d+)', m.group(2))]
        fi = [int(x) for x in re.findall(r'(?im)^\s*FrameIndex\s+\S+\s+\S+\s+(\d+)', m.group(2))]
        amt = max(idx[-1] + 1, 4) if idx else 4
        if any(i >= amt for i in idx + fi): bad += 1; print('BAD', n, m.group(1), idx, sorted(set(fi)))
print('blocks with a slot past their size:', bad)
