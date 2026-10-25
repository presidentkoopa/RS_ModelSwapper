"""build_quest.py -- build.ps1 -Static, for a machine without PowerShell.

    python -B tools_kit/build_quest.py [out.pk3]      (default ModelSwapper-QUEST.pk3)

Same rules as build.ps1 -Static, in the same order: the include list, zscript/ +
models/ + zscript_depot/ + sounds/, the static fork shim swapped in, quest/ overrides,
no working copies, no models/blend, model folders only where modeldef names them (plus
the exact files the cards' magmodel/roundmodel/linkmodel name). Then the same checks:
no static *_wm world model, every modeldef asset resolves, no duplicate donor block.
If build.ps1 changes, change this with it -- a second build that drifts is how a gate
ends up testing a pack nobody ships."""
import os, re, sys, zipfile, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def SHIPPED_MODELDEFS():
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, 'MODELDEF.*')) if os.path.isfile(p))


def main(out):
    out = out or os.path.join(ROOT, 'ModelSwapper-QUEST.pk3')
    include = ['zscript.txt', 'modeldef', 'MENUDEF', 'CVARINFO', 'MAPINFO', 'KEYCONF']
    dirs = ['zscript', 'models', 'zscript_depot']
    include += sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, 'WMCARD.*')) if os.path.isfile(p))
    # every MODELDEF.<x> lump at the root ships (the reload layers of each lifted set, the hands):
    # a hand-kept list here dropped MODELDEF.aliens once and drew no gun mid-reload
    include += SHIPPED_MODELDEFS()
    include.append('SNDINFO.ms'); dirs.append('sounds')

    files = []
    for f in include:
        p = os.path.join(ROOT, f)
        if os.path.exists(p): files.append(p)
        else: print('warning: missing', f)
    for d in dirs:
        for r, _, fs in os.walk(os.path.join(ROOT, d)):
            files += [os.path.join(r, f) for f in fs]
    rel = lambda p: os.path.relpath(p, ROOT).replace('\\', '/')
    files = [p for p in files if not rel(p).startswith('zscript/static/') and not rel(p).startswith('quest/')]
    files = [p for p in files if not p.lower().endswith('.pdn')]
    files = [p for p in files if not re.search(r'(?i)\.(before_\w+|bak|orig|tmp)$', p)]
    files = [p for p in files if '/models/blend/' not in p.replace('\\', '/')]
    md = open(os.path.join(ROOT, 'modeldef'), encoding='latin-1').read()
    md_all = '\n'.join(open(os.path.join(ROOT, f), encoding='latin-1').read() for f in include if f.lower().startswith('modeldef'))
    md_refs = {m.lower() for m in re.findall(r'(?i)Path\s+"models/([^/"]+)', md_all)}
    card_refs = set()
    for c in glob.glob(os.path.join(ROOT, 'WMCARD.*')):
        t = open(c, encoding='latin-1').read()
        for a, b in re.findall(r'(?i)\b(?:mag|round|link)(?:model|skin)\s*=\s*"([^"]+)"\s+"([^"]+)"', t):
            card_refs.add((a.rstrip('/') + '/' + b).replace('\\', '/').lower())

    def keep(p):
        r = rel(p).lower()
        if r in card_refs: return True
        m = re.match(r'models/([^/]+)/', r)
        return not m or m.group(1) in md_refs
    files = [p for p in files if keep(p)]

    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(set(files)):
            r = rel(p); src = p
            if r == 'zscript/RS_ForeignFork.zs':
                src = os.path.join(ROOT, 'zscript/static/RS_ForeignFork.zs')
            q = os.path.join(ROOT, 'quest', r)
            if os.path.exists(q): src = q
            z.write(src, r)

    z = zipfile.ZipFile(out); names = {n.lower() for n in z.namelist()}
    bad = 0
    for n in z.namelist():
        if re.search(r'(?i)_wm\.md3$', n): print('STATIC WORLD MODEL packed:', n); bad += 1
    txt = z.read('modeldef').decode('latin-1'); path = ''; refs = miss = 0
    for line in txt.split('\n'):
        m = re.match(r'^\s*Path\s+"([^"]+)"', line)
        if m: path = m.group(1).replace('\\', '/').rstrip('/'); continue
        m = re.match(r'^\s*(?:Model|Skin)\s+\d+\s+"([^"]+)"', line)
        if m:
            refs += 1
            if (path + '/' + m.group(1)).lower() not in names: print('unresolved asset:', path + '/' + m.group(1)); miss += 1
    for lump in SHIPPED_MODELDEFS():
        if lump.lower() in names:
            t = z.read(lump).decode('latin-1'); path = ''
            for line in t.split('\n'):
                m = re.match(r'^\s*Path\s+"([^"]+)"', line)
                if m: path = m.group(1).rstrip('/'); continue
                m = re.match(r'^\s*(?:Model\s+\d+|Skin\s+\d+|SurfaceSkin\s+\d+\s+\d+)\s+"([^"]+)"', line)
                full = m.group(1) if m and '/' in m.group(1) else (path + '/' + m.group(1) if m else '')
                if m and full.lower() not in names:
                    print('unresolved asset (%s): %s/%s' % (lump, path, m.group(1))); miss += 1
    donors = re.findall(r'(?m)^Model\s+(\S+)', txt)
    dupes = sorted({d for d in donors if donors.count(d) > 1})
    if dupes: print('duplicate donor blocks:', dupes); bad += 1
    print('%s: %d entries, %.1f MB, %d modeldef refs, %d unresolved' % (out, len(names), os.path.getsize(out) / 1e6, refs, miss))
    return 1 if (bad or miss) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
