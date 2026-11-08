"""Run md3label over every ranged donor that has no card yet.

Nothing new is measured here by hand. md3label is the tool that produced the 32
cards that already drive a reload; this only feeds it the rest of the shelf,
taking each gun's mesh from modeldef and its archetype from the shelf row.
"""
import json, os, re, subprocess, sys

ROOT = r'E:\DOOMWork\RS_ModelSwapper'
os.chdir(ROOT)
missing = set(json.load(open('NEVER_CARDED.json')))
md = open('modeldef', encoding='utf-8', errors='replace').read()
zs = open('zscript/RS_ForeignModels.zs', encoding='utf-8', errors='replace').read()
arch = {n: a for a, n in re.findall(r'"([a-z]+)\|(MS_\w+)\|', zs)}

mesh = {}
for name, b in re.findall(r'(?ms)^Model\s+(\S+)\s*\r?\n\{(.*?)^\}', md):
    p = re.search(r'Path\s+"([^"]+)"', b)
    f = re.search(r'Model\s+0\s+"([^"]+)"', b)
    if p and f:
        mesh[name] = os.path.join(p.group(1).rstrip('/'), f.group(1))

SCRATCH = r'C:/Users/Command/AppData/Local/Temp/claude/E--DOOMWork-UZDXREMA/41c253b2-0e7e-44c4-807f-185f9dc7e0d1/scratchpad/shelfcards'
os.makedirs(SCRATCH, exist_ok=True)
os.makedirs('cards_shelf', exist_ok=True)
ok, fail = [], []
for n in sorted(missing):
    m = mesh.get(n)
    if not m or not os.path.exists(m):
        fail.append((n, 'mesh not found')); continue
    d = os.path.join(SCRATCH, n)
    out = os.path.join(d, n + '.card')
    r = subprocess.run([sys.executable, '-I', 'tools_kit/md3label.py', m, d, n,
                        '--archetype', arch.get(n, 'pistol')],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not os.path.exists(out):
        fail.append((n, (r.stderr.strip().splitlines() or ['?'])[-1][:90])); continue
    t = open(out, encoding='utf-8', errors='replace').read()
    open(os.path.join('cards_shelf', n + '.card'), 'w', encoding='utf-8').write(t)
    has = bool(re.search(r'^\s+mag\s+surf', t, re.M))
    ph = re.findall(r'^\s+(mag_in|mag_out|pump|bolt_\w+)\s+(\d+)\.\.(\d+)', t, re.M)
    ok.append((n, has, [p[0] for p in ph]))

print(f'cards written .......... {len(ok)}')
print(f'  with a `mag` surface . {sum(1 for _,h,_ in ok if h)}')
print(f'  with a mag_in phase .. {sum(1 for _,_,p in ok if "mag_in" in p)}')
print(f'failed ................. {len(fail)}')
print()
for n, why in fail[:25]:
    print(f'  {n:<30} {why}')
json.dump({'ok': ok, 'fail': fail}, open('CARD_PASS.json', 'w'), indent=1)
