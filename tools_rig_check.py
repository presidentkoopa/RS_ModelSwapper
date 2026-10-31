#!/usr/bin/env python3
"""tools_rig_check.py -- build the Quest (static) ModelSwapper pk3 and look at donors on the QuestZDoom rig.

    python3 tools_rig_check.py --donors MS_BD_Pistol,MS_BD_Shotgun --tag smoke [--extra doomablo.pk3 ...]

For each donor: finds its family and its 0-based index among that family's SHELF rows
(zscript/RS_ForeignModels.zs), writes the pick into rs_fm_picks as "<WeaponClass>:<family>:<i>:<i>;"
(the record format RS_ForeignPersist reads: class, archetype, mainhand pick, offhand pick), launches the rig
at /home/claude/rig with doom2 on MAP01, switches to the vanilla weapon the family maps to (give all + slot N),
and keeps the last dumped frame. One contact sheet per run: /home/claude/cards/rigcheck_<tag>.png, one tile per
donor, labelled. Prints PASS/FAIL per donor: FAIL = any pack script error / VM abort in the log, or no frame.
The engine's own statusbarcore / DI_ITEM_CENTER lines (QuestZDoom 17.3's, present in every run) are not counted.

The pk3 is built the way build.ps1 -Static does (MODELDEF.rsb / .rsrpump are now generated for the MS 1.5 donors by
tools_reload_modeldefs.py), minus everything in cards/ the engine does not read (.card, sheets, notes).
"""
import argparse, os, re, subprocess, sys, zipfile, glob, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
RIG = '/home/claude/rig'
IWAD = os.environ.get('MS_IWAD', '/home/claude/doom2.wad')
PK3 = '/tmp/claude-0/ModelSwapper-QUEST.pk3'
SHOTS = '/home/claude/shots'
SHEETS = '/home/claude/cards'

# family -> (vanilla weapon class the rig can hold, slot number for `slot N`)
FAMILY_WEAPON = {
    'pistol': ('Pistol', 2), 'revolver': ('Pistol', 2),
    'shotgun': ('Shotgun', 3), 'supershotgun': ('SuperShotgun', 3),
    'chaingun': ('Chaingun', 4), 'smg': ('Chaingun', 4), 'machinegun': ('Chaingun', 4), 'rifle': ('Chaingun', 4),
    'sniper': ('Chaingun', 4),
    'rocket': ('RocketLauncher', 5), 'launcher': ('RocketLauncher', 5), 'grenade': ('RocketLauncher', 5),
    'plasma': ('PlasmaRifle', 6), 'railgun': ('PlasmaRifle', 6), 'flamethrower': ('PlasmaRifle', 6),
    'bfg': ('BFG9000', 7), 'unmaker': ('BFG9000', 7),
    'saw': ('Chainsaw', 1),
    'melee': ('Fist', 1), 'axe': ('Fist', 1), 'kick': ('Fist', 1), 'sword': ('Fist', 1),
}
ENGINE_NOISE = re.compile(r'statusbarcore|DI_ITEM_CENTER', re.I)
ERR = re.compile(r'Script error|VM execution|abort|Unknown identifier', re.I)


def build_pk3(out=PK3):
    os.chdir(HERE)
    z = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    quest = {'zscript.txt': 'quest/zscript.txt', 'MENUDEF': 'quest/MENUDEF', 'CVARINFO': 'quest/CVARINFO'}
    for f in ('zscript.txt', 'modeldef', 'MODELDEF.rsb', 'MODELDEF.rsrpump', 'MODELDEF.cards', 'MODELDEF.rsq', 'MENUDEF', 'CVARINFO', 'MAPINFO', 'KEYCONF'):
        src = quest.get(f, f) if os.path.exists(quest.get(f, f)) else f
        if os.path.exists(src): z.write(src, f)
    for f in sorted(os.listdir('.')):
        if f.startswith('WMCARD.'): z.write(f, f)
    for root, ds, fs in os.walk('zscript'):
        if 'static' in root.split(os.sep): continue
        for f in fs:
            if not f.endswith('.zs') or 'before' in f: continue
            p = os.path.join(root, f)
            z.write('zscript/static/RS_ForeignFork.zs' if f == 'RS_ForeignFork.zs' else p, p)
    for root, ds, fs in os.walk('zscript_depot'):
        for f in fs: z.write(os.path.join(root, f), os.path.join(root, f))
    for root, ds, fs in os.walk('models/rsq'):
        for f in fs:
            if f.lower().endswith(('.md3', '.png')): z.write(os.path.join(root, f), os.path.join(root, f))
    n = 0
    for root, ds, fs in os.walk('cards'):
        for f in fs:
            if re.match(r'^sheet.*\.png$', f) or os.path.splitext(f)[1].lower() in ('.card', '.json', '.md', '.log', '.txt'): continue
            z.write(os.path.join(root, f), os.path.join(root, f)); n += 1
    z.close()
    return out, os.path.getsize(out) // 1048576, n


def shelf():
    """donor -> (family, index within family) from SHELF[] in RS_ForeignModels.zs."""
    t = open(os.path.join(HERE, 'zscript/RS_ForeignModels.zs')).read()
    body = re.search(r'static const string SHELF\[\] = \{(.*?)\};', t, re.S).group(1)
    rows = re.findall(r'"([^"]+)"', body)
    out, count = {}, {}
    for r in rows:
        f = r.split('|')
        if len(f) < 2: continue
        fam, donor = f[0], f[1]
        if donor not in out:          # a donor listed under two families keeps its first (menu order)
            out[donor] = (fam, count.get(fam, 0))
        count[fam] = count.get(fam, 0) + 1
    return out


def run_one(donor, fam, idx, extra, tag, weapon=None, fist_idx=None):
    """One rig run. What every earlier run got wrong, fixed here (2026-10-31):
    * the pin string goes in with +set and embedded quotes ("\"...\""), and starts with ';' -- the engine
      splits the command line on ';' and keeps a literal quote on the first record, so the first record is a
      throwaway and every real record sits between separators;
    * the off hand (rsq_hands) and the fist are pinned too (rsq_hands otherwise wears a hash-picked melee donor
      in every frame);
    * the gun is selected the way the Depot rig's drivers do it: wait 120 for the player, give, use, then 170
      tics for the select animation (tools/rig/README.md traps);
    * the hand sits where the Depot rig shoots guns: in front of the eye, side-on (cmp2.py POSE);
    * the donor actually applied is read back from the rs_foreignmodels_dump table, not assumed."""
    cls = weapon or FAMILY_WEAPON.get(fam, ('Pistol', 2))[0]
    d = os.path.join(SHOTS, 'rigcheck_%s_%s' % (tag, donor)); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    recs = ['%s:%s:%d:%d' % (cls, fam, idx, idx)]
    if fist_idx is not None:
        recs += ['rsq_hands:melee:%d:%d' % (fist_idx, fist_idx), 'Fist:melee:%d:%d' % (fist_idx, fist_idx)]
    picks = ';' + ';'.join(recs) + ';'
    cmds = ['wait 120', 'god', 'qz_rhand "0.0 1.68 -0.40 20 -70 0"', 'give ammo', 'give %s' % cls, 'wait 2',
            'use %s' % cls, 'wait 170', 'quit']
    args = ['./qz', '-iwad', IWAD, '-file'] + list(extra) + [PK3, '-warp', '1', '-nomonsters', '-nosound',
            '+set', 'rs_foreignmodels_dump', 'true', '+set', 'rsq_hands', '1', '+set', 'rs_fm_picks', '"%s"' % picks, '+' + '; '.join(cmds)]
    env = dict(os.environ, QZ_RES='480', QZ_DUMP_EVERY='145', QZ_DUMP_DIR=d)
    log = open(os.path.join(d, 'log.txt'), 'w')
    try:
        subprocess.run(args, cwd=RIG, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=240)
    except subprocess.TimeoutExpired:
        pass
    log.close()
    text = open(os.path.join(d, 'log.txt'), errors='ignore').read()
    errs = sorted(set(l.strip() for l in text.splitlines() if ERR.search(l) and not ENGINE_NOISE.search(l)))
    m = re.search(r'^\s+%s\s+slot\s+-?\d+\s+->\s+\S+\s+(MS_\w+)' % re.escape(cls), text, re.M)
    applied = m.group(1) if m else None
    frames = sorted(glob.glob(os.path.join(d, '*.ppm')))
    return dict(donor=donor, fam=fam, idx=idx, cls=cls, dir=d, errs=errs, frames=frames, applied=applied)


def sheet(results, tag):
    from PIL import Image, ImageDraw
    tiles = []
    for r in results:
        if r['frames']:
            im = Image.open(r['frames'][-1]).convert('RGB')
        else:
            im = Image.new('RGB', (640, 480), (40, 0, 0))
        dr = ImageDraw.Draw(im)
        label = '%s  [%s #%d on %s]  %s' % (r['donor'], r['fam'], r['idx'], r['cls'], 'PASS' if (r['frames'] and not r['errs']) else 'FAIL')
        dr.rectangle((0, 0, im.width, 18), fill=(0, 0, 0)); dr.text((4, 3), label, fill=(255, 255, 0))
        tiles.append(im)
    cols = min(3, len(tiles)); rows = (len(tiles) + cols - 1) // cols
    w, h = tiles[0].width, tiles[0].height
    out = Image.new('RGB', (cols * w, rows * h), 'black')
    for i, t in enumerate(tiles): out.paste(t, ((i % cols) * w, (i // cols) * h))
    os.makedirs(SHEETS, exist_ok=True)
    p = os.path.join(SHEETS, 'rigcheck_%s.png' % tag); out.save(p); return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--donors', required=True, help='comma list of donor classes, e.g. MS_BD_Pistol,MS_BD_Shotgun')
    ap.add_argument('--extra', nargs='*', default=[], help='extra pk3s loaded BEFORE ModelSwapper (a mod to swap on)')
    ap.add_argument('--tag', default='check')
    ap.add_argument('--no-build', action='store_true', help='reuse the pk3 already at %s' % PK3)
    ap.add_argument('--weapon', default=None, help='weapon class to hold instead of the vanilla one for the family (e.g. RwPistol on Doomablo)')
    a = ap.parse_args()
    if not a.no_build:
        p, mb, n = build_pk3(); print('pk3 %s (%d MB, %d card files)' % (p, mb, n))
    sh = shelf(); results = []
    for donor in [x.strip() for x in a.donors.split(',') if x.strip()]:
        if donor not in sh:
            print('%-28s FAIL  not on the shelf (SHELF[] in RS_ForeignModels.zs)' % donor); continue
        fam, idx = sh[donor]
        fist = sh.get('MS_BD_Fist', (None, None))[1]
        r = run_one(donor, fam, idx, [os.path.abspath(x) for x in a.extra], a.tag, a.weapon, fist); results.append(r)
        ok = bool(r['frames']) and not r['errs'] and r['applied'] == donor
        print('%-28s %s  family %s #%d on %s, applied %s, %d error line(s), %d frame(s)%s' % (donor, 'PASS' if ok else 'FAIL', fam, idx, r['cls'], r['applied'], len(r['errs']), len(r['frames']), ('  log: ' + r['dir'] + '/log.txt') if not ok else ''))
        for e in r['errs'][:5]: print('      ' + e[:160])
    if results:
        print('sheet:', sheet(results, a.tag))


if __name__ == '__main__': main()
