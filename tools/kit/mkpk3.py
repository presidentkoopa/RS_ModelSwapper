"""mkpk3.py -- zip a built set into a pk3 with a README built from the genpack / assemble reports.
usage: python3 mkpk3.py <build dir> <set name> <out pk3>
"""
import os, sys, json, zipfile, time


def readme(build, setname):
    g = json.load(open(os.path.join(build, 'genpack_report.json')))
    a = json.load(open(os.path.join(build, 'assemble_report.json')))
    L = ['RS Quest VR Weapons -- %s set' % setname.upper(),
         '=' * 40, '',
         'Generated %s by c2q (genpack.py + assemble.py) from the RS_VR_Weapons cards and meshes.' % time.strftime('%Y-%m-%d'),
         'Target: QuestZDoom 17.3 (GZDoom 4.14.3 base, tag qzd17.3), stock engine, no engine changes.',
         'Load after the IWAD. No other mod needed. Options: Options -> RS VR Weapons.', '',
         'WHAT RELOADS IN VR', '-' * 40]
    for cls, what in g['report']:
        if cls.startswith('('):
            continue
        L.append('%-24s %s' % (cls, what))
    L += ['', 'HOW TO RELOAD (magazine guns, in VR, rsr_reload 1)', '-' * 40,
          '  Press the gun\'s reload (or the off-hand reload button) -> the magazine drops out.',
          '  Reach the off hand to the gun\'s well, pull the off trigger (rsr_grab_with) -> a fresh magazine is in the hand.',
          '  Bring it to the well: it snaps to the axis and follows your depth; push it home to seat it.',
          '  Guns with a slide / charging handle: grab the handle with the off hand, pull it back and let go.',
          '  Out of VR, or with reloading set to Stock, the same button does a canned reload.', '',
          'FLAGS -- read before judging a gun', '-' * 40,
          '  * Gunplay numbers (damage, pellets, rate, auto) come from each set\'s WMSHEET where it has them; what the',
          '    sheets do not carry (damage) is Doom\'s own by gun type (genpack FIRE table). Alt-fire modes are not carried.',
          '  * Slide / bolt lock-open on empty: from the card where its rack cycle declares holdopen; otherwise a RULE',
          '    (a part named slide/bolt locks, a charging handle does not). Each gun\'s line above says which.',
          '  * Scale x sign follows REMA\'s MODELDEF for the mesh. Eject-port side per gun is in the line above:',
          '    "LEFT" on a right-handed gun means the mesh or its card is mirrored -- check in the headset.',
          '  * VR hands are OFF (rsq_hands 0): the hand meshes are Ermac\'s, art licensed for education only, so no',
          '    public set ships them. Reloading works without hands. A private hand pack can switch them on.',
          '  * Pump and break-open guns use the canned reload in this pass (the Quest pump / break modules are present',
          '    but have no tables yet). BFG-type cells with no mesh surface: canned reload.',
          '  * Modern (IQM) guns are baked at their rest pose into MD3s split by joint; the rig\'s view arms and the',
          '    parked second magazine are dropped. Their animation frames are not used.',
          '  * Sounds: %s.' % g['report'][-1][1],
          '', 'RUNTIME', '-' * 40,
          '  Pack 1.92 reload modules (vreload, rsr_assist, rsr_break, rsr_pump, hands, handler, vrhand) copied from source',
          '  with these exact-match edits only:']
    for f, e in a['edits']:
        L.append('    %-20s %s' % (f, e if isinstance(e, str) else '; '.join(e)))
    L += ['  Stubs (interface from the pack source, Index 0): RSB_Guns, RSP_Guns, RSQ_HandTable, RSQ_GunMoves, RSK_M203Handler, RSG_Handler.',
          '', 'Build reports: genpack_report.json, assemble_report.json in the pk3. Render sheets: _sheets/.']
    return '\n'.join(L) + '\n'


def main(build, setname, out):
    open(os.path.join(build, 'README_%s.txt' % setname), 'w').write(readme(build, setname))
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for dp, dn, fn in os.walk(build):
            for f in sorted(fn):
                p = os.path.join(dp, f)
                z.write(p, os.path.relpath(p, build).replace(os.sep, '/'))
    print(out, '%.1f MB' % (os.path.getsize(out) / 1e6))


if __name__ == '__main__':
    main(*sys.argv[1:4])
