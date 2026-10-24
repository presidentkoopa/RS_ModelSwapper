"""md3_stack.py -- stack single-frame MD3s into one multi-frame MD3.

Why this exists
---------------
The blend-file guns were exported one frame at a time, at the rest pose, and a
rest pose is exactly where an author parks the parts a reload moves: the Kar98's
stripper clip and its five cartridges sit inside the buttstock at frame 0, and
the card measured from that put the magazine well at the back of the rifle.

md3label classifies parts by MOTION -- which surface travels down and clear
(the magazine), which rides the bore (the slide or bolt), which flicks and
returns (the trigger). On one frame it can do none of that and everything falls
back to 'body'. Exporting every frame of the source animation and stacking them
here is what gives it something to read, and it is also how you find the frame
where a part is clear of the gun so it can be carved by itself.

Every input must share topology -- same surfaces in the same order, same vertex
and triangle counts. blendobj4.py --frame N produces exactly that, because only
the positions change between frames. The check below is not a formality: a
mismatch means the exporter reordered something, and stacking it anyway would
silently scramble the animation.

usage:
  python -B md3_stack.py out.md3 frame_00.md3 frame_01.md3 ...
  python -B md3_stack.py out.md3 --dir frames/        (sorted by filename)
"""
import glob
import os
import struct
import sys


def pad(s, n):
    b = s.encode('latin-1')[:n - 1]
    return b + b'\0' * (n - len(b))


def read(path):
    d = open(path, 'rb').read()
    nframes, ntags, nsurf, nskins = struct.unpack_from('<4i', d, 76)
    ofs_frames, ofs_tags, ofs_surf, ofs_eof = struct.unpack_from('<4i', d, 92)
    if nframes != 1:
        raise SystemExit(f"{path}: expected a single-frame export, got {nframes} frames")
    frame = d[ofs_frames:ofs_frames + 56]
    surfs = []
    o = ofs_surf
    for _ in range(nsurf):
        name = d[o + 4:o + 68].split(b'\0')[0].decode('latin-1')
        (sflags, snf, nsh, nverts, ntris, ofs_tris, ofs_sh,
         ofs_st, ofs_xyz, ofs_end) = struct.unpack_from('<10i', d, o + 68)
        surfs.append(dict(
            name=name, nverts=nverts, ntris=ntris, nsh=nsh,
            tris=d[o + ofs_tris:o + ofs_tris + ntris * 12],
            shaders=d[o + ofs_sh:o + ofs_sh + nsh * 68],
            st=d[o + ofs_st:o + ofs_st + nverts * 8],
            xyz=d[o + ofs_xyz:o + ofs_xyz + nverts * 8],   # 1 frame: nverts * (3h + H)
        ))
        o += ofs_end
    return frame, surfs


def main():
    out = sys.argv[1]
    if '--dir' in sys.argv:
        files = sorted(glob.glob(os.path.join(sys.argv[sys.argv.index('--dir') + 1], '*.md3')))
    else:
        files = sys.argv[2:]
    if not files:
        raise SystemExit("no input frames")

    frames, per = [], []
    for f in files:
        fr, su = read(f)
        frames.append(fr)
        per.append(su)

    base = per[0]
    for i, su in enumerate(per[1:], 1):
        if len(su) != len(base):
            raise SystemExit(f"{files[i]}: {len(su)} surfaces, frame 0 has {len(base)}")
        for a, b in zip(base, su):
            if (a['name'], a['nverts'], a['ntris']) != (b['name'], b['nverts'], b['ntris']):
                raise SystemExit(
                    f"{files[i]}: surface {b['name']!r} is {b['nverts']}v/{b['ntris']}t, "
                    f"frame 0 has {a['name']!r} {a['nverts']}v/{a['ntris']}t -- topology changed")

    nf = len(files)
    body = bytearray()
    for si, s in enumerate(base):
        xyz = b''.join(per[f][si]['xyz'] for f in range(nf))
        ofs_tris = 108
        ofs_sh = ofs_tris + len(s['tris'])
        ofs_st = ofs_sh + len(s['shaders'])
        ofs_xyz = ofs_st + len(s['st'])
        ofs_end = ofs_xyz + len(xyz)
        body += (struct.pack('<4s', b'IDP3') + pad(s['name'], 64)
                 + struct.pack('<10i', 0, nf, s['nsh'], s['nverts'], s['ntris'],
                               ofs_tris, ofs_sh, ofs_st, ofs_xyz, ofs_end)
                 + s['tris'] + s['shaders'] + s['st'] + xyz)

    allframes = b''.join(frames)
    ofs_frames = 108
    ofs_tags = ofs_frames + len(allframes)
    ofs_surf = ofs_tags                      # no tags; md3label adds them later
    ofs_eof = ofs_surf + len(body)
    head = (struct.pack('<4si', b'IDP3', 15)
            + pad(os.path.basename(out), 64)
            + struct.pack('<9i', 0, nf, 0, len(base), 0,
                          ofs_frames, ofs_tags, ofs_surf, ofs_eof))
    open(out, 'wb').write(head + allframes + body)

    # verify by re-reading what was written, not by trusting the writer
    d = open(out, 'rb').read()
    gnf, gnt, gns, _ = struct.unpack_from('<4i', d, 76)
    print(f"{out}: {gns} surfaces x {gnf} frames  ({len(d)} bytes)")
    assert (gnf, gns) == (nf, len(base)), "written file does not match the inputs"
    for s in base:
        print(f"   {s['name']:<22} {s['nverts']:5d}v {s['ntris']:5d}t")


main()
