"""Build the Quest (stock QuestZDoom 17.3) package -- build.ps1 -Static, in Python -- and the Project Brutality set.

    python tools_build_pk3.py                 pk3/ModelSwapper-QUEST.pk3
    python tools_build_pk3.py --pb            pk3/ProjBrut_MS.pk3: the Quest build cut to the PB set + the PB menu

WHY A PORT. build.ps1 needs Windows PowerShell; the rig and the cloud sessions are Linux. This packs exactly what
build.ps1 -Static packs and runs the same gates, so either one makes the same pk3:
  - contents: zscript.txt, modeldef, MENUDEF, CVARINFO, MAPINFO, KEYCONF, MODELDEF.{rsb,rsrpump,cards,cards2x,rsq},
    SNDINFO.ms, the WMCARD.* root lumps, and zscript/, cards/, zscript_depot/, models/rsq/, sounds/
  - substitutions: zscript/static/RS_ForeignFork.zs for zscript/RS_ForeignFork.zs; quest/<lump> for a root lump
  - left out: cards' .card/.json/.md/.log/.txt and sheet*.png, .pdn, *.before_*/.bak/.orig/.tmp, models/blend/,
    and any models/<folder>/ that neither modeldef nor a WMCARD prop (mag/round/link model|skin) names
  - gates (any failure = no pk3): tools_zs_lint clean; no backslash entries; no static world models (*_wm.md3);
    every modeldef Model/Skin reference resolves inside the pk3; no duplicate Model block, no duplicate class stub,
    no donor without a class stub.

THE PB SET (--pb). Load order: Project Brutality, the PB VR offhand patch (its own pk3, from the releases or
tools_make_pb_offhand_patch.py -- owner, 2026-11-03: never baked into this pk3), then ProjBrut_MS.pk3. Adds
  - MENUDEF.pb: Options > "Project Brutality VR", the settings that matter with PB in one page.
  - textures over 1024 px scaled to 1024 in the packed copy (Quest).
The PB weapon -> model profile itself is in the shared code (RS_ForeignScanner.ProfileDonor), so it also applies when
the plain Quest build is loaded with PB.

THE PB SET SHIPS ONLY PB'S MODELS. The full shelf is 145 donors and 182 MB; the set carries the donors the PB profile
names (RS_ForeignModels.zs ProfileDonor), their card folders, and only their Model blocks in every MODELDEF lump.
The other donors' class stubs are left out of zscript.txt, so their shelf rows drop at load (RS_ForeignShelf.Build
keeps a row only when its donor class exists) and the picker offers exactly the PB set.
"""
import io, os, re, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(ROOT, 'pk3')
INCLUDE = ['zscript.txt', 'modeldef', 'MENUDEF', 'CVARINFO', 'MAPINFO', 'KEYCONF', 'MODELDEF.rsb', 'MODELDEF.rsrpump',
           'MODELDEF.cards', 'MODELDEF.cards2x', 'MODELDEF.rsq', 'SNDINFO.ms']
DIRS = ['zscript', 'cards', 'zscript_depot', 'models/rsq', 'sounds']
PB_MENU = 'MENUDEF.pb'


def gather():
    files = [f for f in INCLUDE if os.path.exists(os.path.join(ROOT, f))]
    files += sorted(f for f in os.listdir(ROOT) if f.startswith('WMCARD.') and os.path.isfile(os.path.join(ROOT, f)))
    for d in DIRS:
        for dp, dn, fn in os.walk(os.path.join(ROOT, d)):
            dn.sort()
            for f in sorted(fn):
                files.append(os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, '/'))
    keep = []
    for rel in files:
        name = rel.rsplit('/', 1)[-1]
        if rel.startswith('zscript/static/') or rel.startswith('quest/'): continue
        if rel.startswith('cards/') and (re.match(r'^sheet.*\.png$', name) or
                                         os.path.splitext(name)[1].lower() in ('.card', '.json', '.md', '.log', '.txt')): continue
        if name.lower().endswith('.pdn'): continue
        if re.search(r'(?i)\.(before_\w+|bak|orig|tmp)$', name): continue
        if '/models/blend/' in '/' + rel: continue
        keep.append(rel)
    # every MODELDEF lump names model folders, not just modeldef: MODELDEF.rsq's VR hands live in models/rsq, and
    # build.ps1's modeldef-only filter dropped them from every Quest pk3 (its verify only read modeldef, so it passed)
    md = ''.join(open(os.path.join(ROOT, f), encoding='utf-8-sig').read() for f in os.listdir(ROOT)
                 if f == 'modeldef' or f.startswith('MODELDEF.'))
    md_refs = {m.lower() for m in re.findall(r'(?i)Path\s+"models/([^/"]+)', md)}
    card_refs = set()
    for f in os.listdir(ROOT):
        if f.startswith('WMCARD.'):
            for a, b in re.findall(r'(?i)\b(?:mag|round|link)(?:model|skin)\s*=\s*"([^"]+)"\s+"([^"]+)"',
                                   open(os.path.join(ROOT, f), encoding='utf-8', errors='replace').read()):
                card_refs.add((a.rstrip('/') + '/' + b).replace('\\', '/').lower())
    out = []
    for rel in keep:
        if rel.lower() in card_refs: out.append(rel); continue
        m = re.match(r'models/([^/]+)/', rel)
        if not m or m.group(1).lower() in md_refs: out.append(rel)
    return out


def pb_donors():
    zs = open(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs'), encoding='utf-8').read()
    a = zs.index('static string ProfileDonor'); b = zs.index('};', a)
    return sorted(set(re.findall(r'"PB_\w+\|(MS_\w+)"', zs[a:b])))


def model_blocks(text):
    """(start, end, name, path) of every Model block."""
    out = []
    for m in re.finditer(r'(?m)^Model\s+(\S+)\s*\n\{.*?\n\}[ \t]*\n?', text, re.S):
        pm = re.search(r'Path\s+"([^"]+)"', m.group(0))
        out.append((m.start(), m.end(), m.group(1), pm.group(1).replace('\\', '/').rstrip('/') if pm else ''))
    return out


def pb_filter(files):
    """keep only the PB profile's donors: returns (files, {rel: new bytes} for rewritten lumps, donors, dirs)."""
    donors = pb_donors()
    md = open(os.path.join(ROOT, 'modeldef'), encoding='utf-8-sig').read()
    dirs = {p for s, e, n, p in model_blocks(md) if n in donors}
    missing = [d for d in donors if not any(n == d for s, e, n, p in model_blocks(md))]
    if missing: sys.exit('PB profile names donors with no modeldef block: %s' % missing)
    def card_dir(rel):
        m = re.match(r'(cards/[^/]+/[^/]+)/', rel)
        return m.group(1) if m else None
    keep = [r for r in files if card_dir(r) is None or card_dir(r) in dirs]
    rewrite = {}
    for rel in keep:
        if rel == 'modeldef' or rel.startswith('MODELDEF.'):
            txt = open(source_of(rel), encoding='utf-8-sig').read()
            out = []; last = 0
            for s, e, n, p in model_blocks(txt):
                if p.startswith('cards/') and p not in dirs:
                    out.append(txt[last:s]); last = e
            out.append(txt[last:])
            rewrite[rel] = ''.join(out).encode('utf-8')
        elif rel == 'zscript.txt':
            txt = open(source_of(rel), encoding='utf-8-sig').read()
            txt = re.sub(r'(?m)^class\s+(MS_\w+)\s*:\s*Actor\s*\{\}[ \t]*\n',
                         lambda m: m.group(0) if m.group(1) in donors else '', txt)
            rewrite[rel] = txt.encode('utf-8')
    return keep, rewrite, donors, dirs


TEX_MAX = 1024


def capped(path):
    """PNG bytes scaled so its longest side is TEX_MAX, or None when it already fits. The PB set is for Quest, where a
    4096 skin is memory and load time for nothing (cards/bd21/mp40/MP40.png was 18.5 MB of a 72.6 MB pk3). The
    repo's own textures are never touched; only the packed copy is."""
    from PIL import Image
    im = Image.open(path)
    if max(im.size) <= TEX_MAX: return None
    k = TEX_MAX / max(im.size)
    im = im.resize((max(1, round(im.size[0] * k)), max(1, round(im.size[1] * k))), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return b.getvalue()


def source_of(rel):
    if rel == 'zscript/RS_ForeignFork.zs': return os.path.join(ROOT, 'zscript/static/RS_ForeignFork.zs')
    q = os.path.join(ROOT, 'quest', rel)
    return q if os.path.exists(q) else os.path.join(ROOT, rel)


def verify(path):
    z = zipfile.ZipFile(path)
    names = {n.lower() for n in z.namelist()}
    bad = [n for n in z.namelist() if '\\' in n]
    wm = [n for n in z.namelist() if re.search(r'(?i)_wm\.md3$', n)]
    md = z.read('modeldef').decode('utf-8-sig', 'replace')
    refs = miss = 0; missing = []
    # every MODELDEF lump, and SurfaceSkin too (build.ps1 checked modeldef's Model/Skin only)
    for lump in [n for n in z.namelist() if n == 'modeldef' or n.startswith('MODELDEF.')]:
        cur = ''
        for line in z.read(lump).decode('utf-8-sig', 'replace').split('\n'):
            m = re.match(r'^\s*Path\s+"([^"]+)"', line)
            if m: cur = m.group(1).replace('\\', '/').rstrip('/'); continue
            m = re.match(r'^\s*(?:Model|Skin)\s+\d+\s+"([^"]+)"', line) or re.match(r'^\s*SurfaceSkin\s+\d+\s+\d+\s+"([^"]+)"', line)
            if m:
                refs += 1
                if (cur + '/' + m.group(1)).lower() not in names: miss += 1; missing.append('%s: %s/%s' % (lump, cur, m.group(1)))
    donors = re.findall(r'(?m)^Model\s+(\S+)', md)
    stubs = re.findall(r'(?m)^class\s+(\S+)\s*:', z.read('zscript.txt').decode('utf-8-sig', 'replace'))
    dup = sorted({d for d in donors if donors.count(d) > 1})
    sdup = sorted({s for s in stubs if stubs.count(s) > 1})
    nostub = sorted(set(donors) - set(stubs))
    mb = os.path.getsize(path) / 1048576
    print(f'{os.path.basename(path)}  --  {len(z.namelist())} entries, {mb:.1f} MB')
    print(f'  backslash entries  : {len(bad)}')
    print(f'  static world models: {len(wm)}   (must be 0)')
    print(f'  asset refs         : {refs} checked, {miss} unresolved')
    print(f'  donors             : {len(donors)}, {len(dup)} duplicate, {len(nostub)} unstubbed')
    for m in missing[:20]: print('    unresolved:', m)
    for d in dup: print('    duplicate Model block:', d)
    for d in sdup: print('    duplicate class stub:', d)
    for d in nostub: print('    donor with no class stub:', d)
    return not (bad or wm or miss or dup or sdup or nostub)


def main():
    pb = '--pb' in sys.argv
    lint = subprocess.run([sys.executable, '-B', os.path.join(ROOT, 'tools_zs_lint.py')] +
                          [os.path.join('zscript', f) for f in sorted(os.listdir(os.path.join(ROOT, 'zscript'))) if f.endswith('.zs')],
                          cwd=ROOT, capture_output=True, text=True)
    print(lint.stdout.strip().splitlines()[-1] if lint.stdout.strip() else lint.stderr)
    if lint.returncode != 0:
        sys.exit('tools_zs_lint.py found problems -- not packing')
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, 'ProjBrut_MS.pk3' if pb else 'ModelSwapper-QUEST.pk3')
    files = gather()
    extra = {}
    rewrite = {}
    if pb:
        files, rewrite, donors, dirs = pb_filter(files)
        print('PB set: %d donors, %d card folders' % (len(donors), len(dirs)))
    if pb:
        extra[PB_MENU] = open(os.path.join(ROOT, PB_MENU), 'rb').read()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in files:
            if rel in rewrite: z.writestr(rel, rewrite[rel])
            elif pb and rel.lower().endswith('.png') and capped(source_of(rel)) is not None:
                z.writestr(rel, capped(source_of(rel)))
            else: z.write(source_of(rel), rel)
        for n, b in extra.items():
            z.writestr(n, b)
    if not verify(out):
        os.remove(out)
        sys.exit('package verification failed -- pk3 removed')


if __name__ == '__main__':
    main()
