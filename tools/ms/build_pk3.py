"""Build the Quest (stock QuestZDoom 17.3) package -- build.ps1 -Static, in Python -- and the Project Brutality set.

    python tools/ms/build_pk3.py                 pk3/ModelSwapper-QUEST.pk3
    python tools/ms/build_pk3.py --pb            pk3/ProjBrut_MS.pk3: the Quest build cut to the PB set + the PB menu
    python tools/ms/build_pk3.py --set <name>    pk3/<Name>_MS.pk3: the Quest build cut to that set's donors (SETS below)

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
tools/ms/make_pb_offhand_patch.py -- owner, 2026-11-03: never baked into this pk3), then ProjBrut_MS.pk3. Adds
  - MENUDEF.pb: Options > "Project Brutality VR", the settings that matter with PB in one page.
  - textures over 1024 px scaled to 1024 in the packed copy (Quest).
The PB weapon -> model profile itself is in the shared code (RS_ForeignScanner.ProfileDonor), so it also applies when
the plain Quest build is loaded with PB.

THE PB SET SHIPS ONLY PB'S MODELS. The full shelf is 145 donors and 182 MB; the set carries the donors the PB profile
names (RS_ForeignModels.zs ProfileDonor), their card folders, and only their Model blocks in every MODELDEF lump.
The other donors' class stubs are left out of zscript.txt, so their shelf rows drop at load (RS_ForeignShelf.Build
keeps a row only when its donor class exists) and the picker offers exactly the PB set.

THE OTHER SETS (--set <name>, PLAN M2) are the same cut for another mod's profile rows. SETS names each set: the pk3 it
writes, which ProfileDonor rows are its (a class-name regex for a prefixed mod like PB, or the explicit class list for a
mod whose class names carry no prefix), and the menu lump it adds, if any. `--pb` is `--set pb`. A listed class with no
profile row is a gate failure, so the script and the ZScript cannot drift apart silently.
"""
import io, os, re, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTDIR = os.path.join(ROOT, 'pk3')
INCLUDE = ['zscript.txt', 'modeldef', 'MENUDEF', 'CVARINFO', 'MAPINFO', 'KEYCONF', 'MODELDEF.rsb', 'MODELDEF.rsrpump',
           'MODELDEF.cards', 'MODELDEF.cards2x', 'MODELDEF.rsq', 'SNDINFO.ms']
DIRS = ['zscript', 'cards', 'zscript_depot', 'models/rsq', 'sounds']
PB_MENU = 'MENUDEF.pb'

# set name -> pk3 file, the profile rows that are its (regex on the class name, or an explicit list of class names,
# spelled as the mod spells them), and the set's MENUDEF lump (None = no page). Picks: docs/sets/<name>.md.
SETS = {
    'pb': dict(pk3='ProjBrut_MS.pk3', classes=r'PB_\w+', menu=PB_MENU),
    'generic_weapons': dict(pk3='GenericWeapons_MS.pk3', menu='MENUDEF.gnrc', classes=[
        'Knuckle', 'ModChainsaw', 'Beretta', 'ARifle', 'Riotgun', 'DoubleSG', 'Minigun', 'Rlauncher', 'PlasRifle',
        'BFG9K']),
    'weapons_of_saturn': dict(pk3='WeaponsOfSaturn_MS.pk3', menu='MENUDEF.saturn', classes=[
        'Knuckles', 'Motorsaw', 'Beretta', '1911', 'MP40', 'MachineRifle', 'Riotgun', 'Coachgun', 'Minigun', 'SaturnV',
        'NovaRifle', 'TITAN']),
}


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


def profile_rows():
    """{class name: donor} for every row of RS_ForeignScanner.ProfileDonor's table."""
    zs = open(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs'), encoding='utf-8').read()
    a = zs.index('static string ProfileDonor'); b = zs.index('};', a)
    return dict(re.findall(r'"([^"|]+)\|(MS_\w+)"', zs[a:b]))


def set_donors(name):
    """the donors a set's profile rows name, sorted; exits when a listed class has no row."""
    rows = profile_rows()
    want = SETS[name]['classes']
    if isinstance(want, str):
        pat = re.compile(want + r'\Z')
        return sorted({d for c, d in rows.items() if pat.match(c)})
    missing = [c for c in want if c not in rows]
    if missing: sys.exit('set %s lists classes with no ProfileDonor row: %s' % (name, missing))
    return sorted({rows[c] for c in want})


def model_blocks(text):
    """(start, end, name, path) of every Model block."""
    out = []
    for m in re.finditer(r'(?m)^Model\s+(\S+)\s*\n\{.*?\n\}[ \t]*\n?', text, re.S):
        pm = re.search(r'Path\s+"([^"]+)"', m.group(0))
        out.append((m.start(), m.end(), m.group(1), pm.group(1).replace('\\', '/').rstrip('/') if pm else ''))
    return out


def pb_filter(files, name='pb'):
    """keep only the set's profile donors: returns (files, {rel: new bytes} for rewritten lumps, donors, dirs)."""
    donors = set_donors(name)
    md = open(os.path.join(ROOT, 'modeldef'), encoding='utf-8-sig').read()
    dirs = {p for s, e, n, p in model_blocks(md) if n in donors}
    missing = [d for d in donors if not any(n == d for s, e, n, p in model_blocks(md))]
    if missing: sys.exit('%s profile names donors with no modeldef block: %s' % (name, missing))
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
    # the menus (zs_lint does not read MENUDEF): every OptionValue an Option row names and every Submenu target is
    # defined in a packed MENUDEF lump (or is an engine built-in), and no OptionMenu / OptionValue is defined twice
    menus = ''.join(z.read(n).decode('utf-8-sig', 'replace') for n in z.namelist() if n == 'MENUDEF' or n.startswith('MENUDEF.'))
    menus = re.sub(r'//[^\n]*', '', menus)
    om = re.findall(r'(?m)^OptionMenu\s+"([^"]+)"', menus)
    ov = re.findall(r'(?m)^OptionValue\s+"([^"]+)"', menus)
    builtin = {'onoff', 'yesno', 'noyes'}
    badov = sorted({v for v in re.findall(r'(?m)^\s*Option\s+"[^"]*",\s*"[^"]*",\s*"([^"]+)"', menus)
                    if v.lower() not in builtin and v not in ov})
    badsm = sorted({m for m in re.findall(r'(?m)^\s*Submenu\s+"[^"]*",\s*"([^"]+)"', menus) if m not in om})
    dupmenu = sorted({m for m in om if om.count(m) > 1} | {v for v in ov if ov.count(v) > 1})
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
    print(f'  menus              : {len(om)} OptionMenu, {len(ov)} OptionValue; {len(badov)} undefined OptionValue, '
          f'{len(badsm)} undefined Submenu, {len(dupmenu)} defined twice')
    for v in badov: print('    Option names an OptionValue no lump defines:', v)
    for m in badsm: print('    Submenu names an OptionMenu no lump defines:', m)
    for m in dupmenu: print('    defined twice:', m)
    return not (bad or wm or miss or dup or sdup or nostub or badov or badsm or dupmenu)


def main():
    name = 'pb' if '--pb' in sys.argv else (sys.argv[sys.argv.index('--set') + 1] if '--set' in sys.argv else None)
    if name is not None and name not in SETS:
        sys.exit('unknown set %r: one of %s' % (name, ' '.join(sorted(SETS))))
    pb = name is not None
    lint = subprocess.run([sys.executable, '-B', os.path.join(ROOT, 'tools', 'ms', 'zs_lint.py')] +
                          [os.path.join('zscript', f) for f in sorted(os.listdir(os.path.join(ROOT, 'zscript'))) if f.endswith('.zs')],
                          cwd=ROOT, capture_output=True, text=True)
    print(lint.stdout.strip().splitlines()[-1] if lint.stdout.strip() else lint.stderr)
    if lint.returncode != 0:
        sys.exit('tools/ms/zs_lint.py found problems -- not packing')
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, SETS[name]['pk3'] if pb else 'ModelSwapper-QUEST.pk3')
    files = gather()
    extra = {}
    rewrite = {}
    if pb:
        files, rewrite, donors, dirs = pb_filter(files, name)
        print('%s set: %d donors, %d card folders' % (name, len(donors), len(dirs)))
        if SETS[name]['menu']:
            extra[SETS[name]['menu']] = open(os.path.join(ROOT, SETS[name]['menu']), 'rb').read()
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
