#!/usr/bin/env python3
"""Build pk3/GoldenSouls_SMD_Enemies.pk3 (PLAN M4): the Super Mario Doom enemies and a high jump for Golden Souls 1 and 2.

    python3 tools/ms/make_gs_smd_patch.py                       build the pk3 from sources/smd_lite + tools/ms/gs_smd_patch
    python3 tools/ms/make_gs_smd_patch.py --from <SDMLITE.pk3>  (re)fill sources/smd_lite from the owner's asset pk3, then build
    python3 tools/ms/make_gs_smd_patch.py --probe               TEST ONLY: work/gs_smd_probe.pk3 (SMDPROBE log lines on the rig)

Load order: Golden Souls 1 or 2, then this patch; GoldenSouls1_MS.pk3 before or after it (they share no lump: checked
by `verify`). Docs: docs/sets/golden_souls_smd_enemies.md.

WHY SPRITES AND NOT ACTORS. The SDMLITE pack has no DECORATE, ZScript, MAPINFO or ACS at all: its enemies are the
stock Doom monsters re-drawn under the stock sprite names (POSS = Koopa Troopa, TROO = Shy Guy, SARG = Goomba ...;
LANGUAGE's cast list names them) with stock-named sound lumps (DSBGSIT1 ...) and a SNDINFO that re-points the rest.
Golden Souls 1 and 2 spawn the stock Doom monsters through `<Class>New : <Class> replaces <Class>` subclasses
(gs1 doomenem.txt, gs2 DOOMENEM) that keep the stock sprite names, so a lump-level patch re-skins both mods with no
actor code, cannot raise a script error, and leaves GS's own monsters (their own sprite names) alone. A class-level
patch would have to name GS classes that differ between the two mods (PainElementalNew is GS2 only) and would fail to
load on the other.

WHAT IS TAKEN FROM THE PACK (sources/smd_lite, CREDITS.txt): the sprites of the 17 monsters and of the projectiles only
those monsters fire, 68 monster sound lumps, and the monster section of its SNDINFO and the cast / obituary lines of
its LANGUAGE (verbatim copies of both whole lumps are kept beside the cut for audit). Left out on purpose: the player
(PLAY/PLYC, the Mario player sounds), weapons, items, decorations, textures, flats, music, menu / intermission sounds,
the Keen and the helper dog (GS places neither), FIRE (GS's own monsters draw their flames with the FIRE sprite: the
SMD FIRE is a target reticle), PUFF / BLUD / BEXP / MISL B-D (generic effects GS's own actors and weapons share).

THE JUMP (tools/ms/gs_smd_patch): the pack carries no player code, so there is no SMD jump number to measure. The patch
gives every player an Inventory item (SMD_HighJump) from an EventHandler at PlayerEntered / PlayerRespawned /
WorldLoaded; the item sets the pawn's JumpZ every tic from the server cvar smd_jumpz (default 15 = Golden Souls 2's own
Player.JumpZ, gs2 DECORATE line 46; GS1's is 8.2, gplayer.dec line 28) and puts the class default back when
smd_highjump is off. GS's player classes are not replaced (GS1's ZGSPlayer PlayerThink and GS2's double-jump ACS keep
working); MAPINFO `nojump` maps stay no-jump (JumpZ is not permission). Server cvars and player-number loops: the same
on every machine, no consoleplayer.
"""
import hashlib, io, os, re, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'sources', 'smd_lite')
PATCH = os.path.join(ROOT, 'tools', 'ms', 'gs_smd_patch')
OUT = os.path.join(ROOT, 'pk3', 'GoldenSouls_SMD_Enemies.pk3')
MS_SET = os.path.join(ROOT, 'pk3', 'GoldenSouls1_MS.pk3')

# the monsters (the cast list of the pack's LANGUAGE, in Doom's order) and the projectiles only they fire
MONSTER_SPRITES = ['POSS', 'SPOS', 'CPOS', 'SSWV', 'TROO', 'SARG', 'HEAD', 'SKUL', 'PAIN', 'SKEL', 'FATT', 'VILE',
                   'BSPI', 'SPID', 'CYBR', 'BOS2', 'BOSS']
PROJECTILE_SPRITES = ['BAL1', 'BAL2', 'BAL7', 'MANF', 'FATB', 'APBX', 'APLS']
# the Cyberdemon's rocket in flight (a Bullet Bill); its B-D explosion frames stay the game's (GS weapons share them)
PARTIAL_SPRITES = {'MISL': 'A'}
# stock monster sound lumps the pack re-records (override by lump name, no SNDINFO line needed)
MONSTER_DS = '''DSPOSIT1 DSPOSIT2 DSPOSIT3 DSPOPAIN DSPODTH1 DSPODTH2 DSPODTH3 DSPOSACT
DSBGSIT1 DSBGSIT2 DSBGACT DSBGPAIN DSBGDTH1 DSBGDTH2 DSCLAW DSFIRSHT
DSSGTSIT DSSGTATK DSSGTDTH DSCACSIT DSCACDTH DSKNTSIT DSKNTDTH DSBRSSIT DSBRSDTH
DSSKLATK DSPESIT DSPEPAIN DSSKESIT DSSKEDTH DSSKEACT DSSKEATK DSSKEPCH DSSKEPC2 DSSKESWG DSSKESW2
DSMANSIT DSMANDTH DSMNPAIN DSMANATK DSVILSIT DSVILDTH DSVIPAIN DSVILACT DSVILATK DSFLAME
DSBSPSIT DSBSPDTH DSBSPACT DSBSPWLK DSSPISIT DSSPIDTH DSCYBSIT DSCYBDTH'''.split()
# the pack's SNDINFO: the monster section is everything from this header to the intermission lines
SND_START, SND_END = '// MONSTER SOUNDS', 'intermission/tick'
LANG_KEYS = re.compile(r'^(CC_|OB_)')


def fail(msg):
    print('make_gs_smd_patch: ' + msg); sys.exit(1)


def lumpname(path):
    return os.path.splitext(os.path.basename(path))[0].upper()


def monster_sndinfo(text):
    a, b = text.find(SND_START), text.find(SND_END)
    if a < 0 or b < 0:
        fail('SNDINFO: monster section markers not found')
    a = text.rfind('//====', 0, a)
    return text[a:b].rstrip() + '\n'


def sndinfo_lumps(section):
    names = set()
    for line in section.splitlines():
        line = line.split('//')[0].strip()
        if not line or line.startswith('$random'):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1].lower() != 'null':
            names.add(parts[1].upper())
    return names


def language_cut(text):
    out = ['[enu default]', '']
    for line in text.splitlines():
        if LANG_KEYS.match(line.strip()):
            out.append(line.rstrip())
    return '\n'.join(out) + '\n'


def fill_sources(pk3):
    """Copy the selected lumps of the asset pk3 into sources/smd_lite (read as data; nothing from it is executed)."""
    z = zipfile.ZipFile(pk3)
    names = z.namelist()
    byname = {}
    for n in names:
        byname.setdefault(lumpname(n), []).append(n)
    snd_orig = z.read('SNDINFO').decode('latin1')
    lang_orig = z.read('LANGUAGE').decode('latin1')
    section = monster_sndinfo(snd_orig)
    want_sounds = set(MONSTER_DS) | sndinfo_lumps(section)
    taken = []
    for n in names:
        if n.endswith('/'):
            continue
        d, base = n.rsplit('/', 1) if '/' in n else ('', n)
        ln = lumpname(base)
        keep = False
        if d == 'sprites':
            sp = ln[:4]
            keep = sp in MONSTER_SPRITES or sp in PROJECTILE_SPRITES or \
                   (sp in PARTIAL_SPRITES and len(ln) > 4 and ln[4] in PARTIAL_SPRITES[sp])
        elif d == 'sounds':
            keep = ln in want_sounds
        if keep:
            dst = os.path.join(SRC, d, base)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'wb') as f:
                f.write(z.read(n))
            taken.append(n)
    missing = sorted(s for s in want_sounds if s not in byname)
    if missing:
        fail('sound lumps named but not in the pack: ' + ' '.join(missing))
    with open(os.path.join(SRC, 'SNDINFO.orig'), 'w', encoding='latin1') as f:
        f.write(snd_orig)
    with open(os.path.join(SRC, 'LANGUAGE.orig'), 'w', encoding='latin1') as f:
        f.write(lang_orig)
    h = hashlib.sha256(open(pk3, 'rb').read()).hexdigest()
    with open(os.path.join(SRC, 'PROVENANCE.md'), 'w') as f:
        f.write('# smd_lite: the Super Mario Doom enemy lumps, verbatim\n\n'
                '- From the owner, 2026-11-08, as `%s` (%d bytes, sha256 %s), %d entries. Read as data.\n'
                '- Taken unchanged by `tools/ms/make_gs_smd_patch.py --from`: %d entries (%d sprites, %d sounds), plus the whole\n'
                '  SNDINFO and LANGUAGE as `*.orig` for audit; the patch packs only their monster lines.\n'
                '- Credit: CREDITS.txt. The pack names no author; the characters are Nintendo\'s.\n'
                % (os.path.basename(pk3), os.path.getsize(pk3), h, len(names), len(taken),
                   sum(1 for t in taken if t.startswith('sprites/')), sum(1 for t in taken if t.startswith('sounds/'))))
    print('sources/smd_lite: %d lumps taken from %s' % (len(taken), os.path.basename(pk3)))


def build():
    for p in (SRC, PATCH):
        if not os.path.isdir(p):
            fail('missing ' + p)
    snd_orig = open(os.path.join(SRC, 'SNDINFO.orig'), encoding='latin1').read()
    lang_orig = open(os.path.join(SRC, 'LANGUAGE.orig'), encoding='latin1').read()
    section = monster_sndinfo(snd_orig)
    entries = {}  # arcname -> bytes
    for dp, dn, fn in os.walk(PATCH):
        dn.sort()
        for f in sorted(fn):
            rel = os.path.relpath(os.path.join(dp, f), PATCH).replace(os.sep, '/')
            entries[rel] = open(os.path.join(dp, f), 'rb').read()
    for d in ('sprites', 'sounds'):
        for f in sorted(os.listdir(os.path.join(SRC, d))):
            entries[d + '/' + f] = open(os.path.join(SRC, d, f), 'rb').read()
    entries['SNDINFO'] = ('// Super Mario Doom monster sounds: the monster section of the SDMLITE pack\'s SNDINFO, verbatim\n'
                          '// (sources/smd_lite/SNDINFO.orig). Player, dog, menu and intermission lines left out.\n'
                          + section).encode('latin1')
    entries['LANGUAGE'] = ('// cast list and obituaries of the SDMLITE pack\'s LANGUAGE (sources/smd_lite/LANGUAGE.orig)\n'
                           + language_cut(lang_orig)).encode('latin1')
    entries['CREDITS.txt'] = open(os.path.join(SRC, 'CREDITS.txt'), 'rb').read()
    verify(entries, section)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as o:
        for name in sorted(entries):
            o.writestr(name, entries[name])
    print('%s: %d entries, %.1f MB' % (os.path.relpath(OUT, ROOT), len(entries), os.path.getsize(OUT) / 1e6))


def verify(entries, section):
    """Gates: every sound the SNDINFO names is packed; every monster sprite prefix has its frames; the patch's own
    lumps are there; no entry name collides with GoldenSouls1_MS.pk3 (so either load order works)."""
    errs = []
    have_snd = {lumpname(n) for n in entries if n.startswith('sounds/')}
    for s in sorted(sndinfo_lumps(section) | set(MONSTER_DS)):
        if s not in have_snd:
            errs.append('SNDINFO names sound %s, not packed' % s)
    have_spr = {}
    for n in entries:
        if n.startswith('sprites/'):
            ln = lumpname(n)
            have_spr.setdefault(ln[:4], set()).add(ln[4])
            if len(ln) >= 8:
                have_spr[ln[:4]].add(ln[6])
    for sp in MONSTER_SPRITES + PROJECTILE_SPRITES:
        if sp not in have_spr:
            errs.append('no sprites for ' + sp)
    for sp, letters in PARTIAL_SPRITES.items():
        extra = have_spr.get(sp, set()) - set(letters)
        if extra:
            errs.append('%s: frames %s packed, only %s wanted' % (sp, ''.join(sorted(extra)), letters))
    for must in ('zscript.txt', 'CVARINFO', 'MENUDEF', 'MAPINFO', 'CREDITS.txt', 'SNDINFO', 'LANGUAGE'):
        if must not in entries:
            errs.append('patch lump missing: ' + must)
    for n in entries:
        if '\\' in n:
            errs.append('backslash in entry name: ' + n)
    if os.path.exists(MS_SET):
        # root lumps the engine reads from EVERY archive are not a clash (cumulative by design)
        cumulative = {'zscript.txt', 'CVARINFO', 'MENUDEF', 'SNDINFO', 'LANGUAGE', 'MAPINFO', 'KEYCONF'}
        ms = set(zipfile.ZipFile(MS_SET).namelist())
        clash = sorted((set(entries) & ms) - cumulative)
        if clash:
            errs.append('entries shared with GoldenSouls1_MS.pk3 (load order would matter): ' + ' '.join(clash[:10]))
    if errs:
        fail('\n  '.join(['gates failed:'] + errs))
    print('gates: %d sounds, %d sprite names, no clash with %s' % (len(have_snd), len(have_spr), os.path.basename(MS_SET)))


def probe():
    """TEST ONLY: zip tools/ms/gs_smd_probe to work/gs_smd_probe.pk3 (run output, not committed)."""
    d = os.path.join(ROOT, 'tools', 'ms', 'gs_smd_probe')
    out = os.path.join(ROOT, 'work', 'gs_smd_probe.pk3')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as o:
        for f in sorted(os.listdir(d)):
            o.write(os.path.join(d, f), f)
    print(os.path.relpath(out, ROOT))


if __name__ == '__main__':
    if '--probe' in sys.argv:
        probe(); sys.exit(0)
    if '--from' in sys.argv:
        fill_sources(sys.argv[sys.argv.index('--from') + 1])
    build()
