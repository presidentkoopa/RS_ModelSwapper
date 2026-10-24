"""check.py -- static checks on a built pack directory (no engine here to compile it).

  braces balance per file; every state line ends in ';'
  every Goto / jump label exists in its class
  every item / actor class named in a string exists (pack, or Doom's own)
  every sprite a state shows has a MODELDEF block (or is TNT1 / ####); every MODELDEF sprite is declared
  every MODELDEF Path/Model/Skin file is in the pack
  every sound name is in the pack's SNDINFO or is an IWAD name
  every MAPINFO event handler is a class; every cvar the code reads is declared
usage: python3 check.py <build dir>
"""
import os, re, sys, glob

DOOM_CLASSES = {'Clip', 'Shell', 'Cell', 'RocketAmmo', 'BulletPuff', 'PlasmaBall', 'Rocket', 'BFGBall', 'FatShot', 'Grenade',
                'Inventory', 'Weapon', 'Ammo', 'Actor', 'Thinker', 'EventHandler', 'PlayerPawn', 'PowerStrength'}
ENGINE_CVARS = re.compile(r'^(vr_|r_|g_|sv_|cl_|snd_|gl_|m_|hud_)')
IWAD_SND = re.compile(r'^(weapons|misc|world|monsters|player|intermission|menu|switches|plats|doors)/|^ds[a-z0-9]{1,6}$')


def main(build):
    bad = []; info = []
    zs = sorted(glob.glob(build + '/zscript/**/*.zs', recursive=True))
    texts = {f: open(f, encoding='latin-1').read() for f in zs}
    allt = '\n'.join(texts.values())
    classes = set(re.findall(r'^class\s+(\w+)', allt, re.M))

    # braces, semicolons
    for f, t in texts.items():
        code = re.sub(r'//[^\n]*', '', t)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.S)
        code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
        if code.count('{') != code.count('}'):
            bad.append('%s: braces %d { vs %d }' % (f, code.count('{'), code.count('}')))
        in_states = False
        tl = t.splitlines()
        for ln, line in enumerate(tl, 1):
            s = line.split('//')[0].strip()
            nxt = tl[ln].strip() if ln < len(tl) else ''
            if nxt.startswith('{'):
                continue
            if not s:
                continue
            if re.match(r'^States\b', s):
                in_states = True; continue
            if in_states and s == '}':
                in_states = False; continue
            if in_states and (re.match(r'^("####"|[A-Z0-9_]{4})\s+("#"|[A-Z\[\]\\]+)\s+-?\d+', s) or re.match(r'^(Goto\b|Loop\b|Stop\b|Wait\b|Fail\b)', s)):
                if not (s.endswith(';') or s.endswith('{') or s.endswith('}')):
                    bad.append('%s:%d: state line without ;  %s' % (f, ln, s))

    # labels per class, items, sprites
    sprites_used = set()
    for f, t in texts.items():
        for m in re.finditer(r'^class\s+(\w+)[^\n]*\n\{(.*?)^\}', t, re.S | re.M):
            cls, body = m.group(1), m.group(2)
            labels = set(re.findall(r'^\s*([A-Za-z_][\w.]*):(?=\s)', body, re.M))
            gotos = re.findall(r'^\s*Goto\s+([A-Za-z_][\w.]*)', body, re.M)
            jumps = re.findall(r'A_Jump\w*\([^)]*?"([A-Za-z_][\w.]*)"\s*\)', body)
            for lab in gotos + jumps:
                base = lab.split('+')[0]
                if base not in labels and base not in ('Super.Ready',):
                    bad.append('%s: class %s: label %s not found' % (f, cls, lab))
            for spr in re.findall(r'^\s*(?:[A-Za-z_][\w.]*:\s*)?([A-Z0-9_]{4})\s+[A-Z\[\]\\]+\s+-?\d+', body, re.M):
                if spr != 'TNT1':
                    sprites_used.add(spr)
        for item in re.findall(r'A_(?:Give|Take|JumpIf|Check)\w*Inventory\s*\(\s*"(\w+)"', t) + \
                re.findall(r'(?:AmmoType\d|AmmoType|DropItem|FindInventory\s*\(\s*\'|CountInv\s*\(\s*\')\s*"?(\w+)"?', t) + \
                re.findall(r'(?:GiveInventory|TakeInventory|CountInv|FindInventory)\s*\(\s*\'(\w+)\'', t):
            if item not in classes and item not in DOOM_CLASSES:
                bad.append('%s: item class %s not defined' % (f, item))

    # MODELDEF
    md_sprites = set(); md_files = []
    md = ''
    for f in glob.glob(build + '/MODELDEF*'):
        md += open(f, encoding='latin-1').read() + '\n'
    for m in re.finditer(r'Model\s+\w+\s*\{(.*?)\}', md, re.S):
        b = m.group(1)
        path = re.search(r'Path\s+"([^"]+)"', b)
        p = path.group(1) if path else ''
        for mf in re.findall(r'(?:Model|Skin|SurfaceSkin)\s+\d+(?:\s+\d+)?\s+"([^"]+)"', b):
            md_files.append(os.path.join(p, mf))
        for spr in re.findall(r'FrameIndex\s+([A-Z0-9_]{4})', b):
            md_sprites.add(spr)
    for mf in sorted(set(md_files)):
        if not os.path.exists(os.path.join(build, mf)):
            bad.append('MODELDEF file missing: ' + mf)
    for spr in sorted(md_sprites - sprites_used):
        bad.append('MODELDEF sprite %s is not declared by any state (engine: "Sprite not found")' % spr)
    known = {}
    ar = build + '/assemble_report.json'
    if os.path.exists(ar):
        import json
        for why, lst in json.load(open(ar)).get('sprites_without_models', {}).items():
            for sp in lst:
                known[sp] = why
    for spr in sorted(sprites_used - md_sprites):
        if spr in known:
            info.append('sprite %s has no model: %s' % (spr, known[spr]))
        else:
            bad.append('state sprite %s has no MODELDEF block (would draw nothing / warn)' % spr)

    # sounds
    snd = open(build + '/SNDINFO.txt', encoding='latin-1').read() if os.path.exists(build + '/SNDINFO.txt') else ''
    defined = set(w.split()[0] for w in snd.splitlines() if w and not w.startswith('//') and not w.startswith('$')) | \
        set(re.findall(r'^\$random\s+(\S+)', snd, re.M)) | set(re.findall(r'^\$alias\s+(\S+)', snd, re.M))
    for name in sorted(set(re.findall(r'"((?:wm|rsr|rs|vp|bd|weapons|misc)/[A-Za-z0-9_/]+)"', allt))):
        if name not in defined and not IWAD_SND.match(name):
            bad.append('sound %s not in SNDINFO' % name)

    # MAPINFO handlers, cvars
    mi = open(build + '/MAPINFO.txt').read() if os.path.exists(build + '/MAPINFO.txt') else ''
    for h in re.findall(r'"(\w+)"', mi):
        if h not in classes:
            bad.append('MAPINFO handler %s is not a class' % h)
    cv = open(build + '/CVARINFO.txt').read() if os.path.exists(build + '/CVARINFO.txt') else ''
    declared = set(re.findall(r'^\s*(?:user|server|nosave|noarchive|cheat|latch|\s)*\s*(?:int|bool|float|string|color)\s+(\w+)', cv, re.M))
    for c in sorted(set(re.findall(r"(?:GetCVar|FindCVar|PlayerInt|PlayerFloat|Float|TestCvar\w*|Debug)\s*\(\s*(?:\w+\s*,\s*)?'(\w+)'", allt))):
        if c not in declared and not ENGINE_CVARS.match(c):
            (info if c.startswith('rsp_test_') else bad).append('cvar %s read but not declared%s' % (c, ' (null-guarded test aid)' if c.startswith('rsp_test_') else ''))
    # ZSCRIPT includes exist
    zl = open(build + '/ZSCRIPT.txt').read() if os.path.exists(build + '/ZSCRIPT.txt') else ''
    for inc in re.findall(r'#include\s+"([^"]+)"', zl):
        if not os.path.exists(os.path.join(build, inc)):
            bad.append('ZSCRIPT include missing: ' + inc)
    inc = set(re.findall(r'#include\s+"([^"]+)"', zl))
    for f in zs:
        if os.path.relpath(f, build) not in inc:
            bad.append('zscript file not included: ' + os.path.relpath(f, build))

    print('%s: %d classes, %d sprites, %d problems' % (build, len(classes), len(sprites_used), len(bad)))
    for b in bad:
        print('  ' + b)
    for b in info:
        print('  (info) ' + b)
    return bad


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1]) else 0)
