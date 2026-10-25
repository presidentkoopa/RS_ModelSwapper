"""rest_frames.py -- donors whose block rests on the wrong frame of their own mesh, set to the measured one.

    python -B tools_kit/rest_frames.py [--dry]

A donor block's anchor FrameIndex picks which frame of an animated mesh is drawn at rest (and the
shelf row's rest-frame field says the same). A mesh whose first frames are its raise animation drawn
on frame 0 shows the gun mid-raise: out of the hand, its magazine somewhere else, and the reload
generator then refuses it (genpack: "evidence disagrees"). Each entry says what was measured.
Only the frame changes -- never the placement (the hands were fitted at the donor's placement).
Run tools_kit/regen_rows.py after, so the donor's reload row is made at the new frame.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

REST = {
    # 2026-10-25. models/bd/Rifle/Rifle.md3, 32 frames; surface 3 is "Lipas" (Finnish: magazine).
    # Frame 3: the card's magcenter sits ON Lipas's centre (0.0 units); at frame 0 it is 23 units
    # off (the raise pose). card2quest.rest_frame (body stops turning after the raise) = 3, and
    # BD22Q rests the same rifle on 3. The shipped hand row lands 8.4 cm from the frame-3 palm and
    # 15.5 cm from the frame-0 one -- it was fitted at 3.
    'MS_brt_Rifle': 3,
}


def main(dry):
    md_p = os.path.join(ROOT, 'modeldef'); md = open(md_p, encoding='utf-8', errors='replace').read()
    sh_p = os.path.join(ROOT, 'zscript/RS_ForeignModels.zs'); sh = open(sh_p).read()
    an_p = os.path.join(ROOT, 'zscript/RS_ForeignAnim.zs'); an = open(an_p).read()
    for d, fr in REST.items():
        bm = re.search(r'^Model\s+%s\s*\n\{(.*?)^\}' % d, md, re.S | re.M)
        body = bm.group(1)
        fm = next(m for m in re.finditer(r'^([ \t]*FrameIndex\s+(\w{4})\s+(\S)\s+0\s+)(\d+)', body, re.M) if m.group(2) != 'MSBL')
        was = int(fm.group(4))
        nb = body[:fm.start(4)] + str(fr) + body[fm.end(4):]
        if 'rest_frames.py' not in nb:
            nb = '\n\t// rest frame %d, measured (tools_kit/rest_frames.py; was %d)\n' % (fr, was) + nb.lstrip('\n')
        md = md[:bm.start(1)] + nb + md[bm.end(1):]
        sh = re.sub(r'("\w+\|%s\|\w{4}\|\d+\|)\d+(\|\d+")' % d, r'\g<1>%d\2' % fr, sh)
        an = re.sub(r'("%s\|ready\|)\d+(@)' % d, r'\g<1>%d\2' % fr, an)
        print('%-24s rest frame %d -> %d' % (d, was, fr))
    if not dry:
        for p, t in ((md_p, md), (sh_p, sh), (an_p, an)):
            open(p, 'w', encoding='utf-8', newline='\n').write(t)


if __name__ == '__main__':
    main('--dry' in sys.argv)
