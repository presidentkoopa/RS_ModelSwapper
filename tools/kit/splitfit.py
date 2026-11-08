"""Split any MD3 surface over the per-surface vertex cap into slabs along the bore,
using the kit's own md3_carve_surface.py. Lossless: it moves triangles between
surfaces and never changes geometry.

DO NOT REACH FOR THIS TO GET UNDER 4096 VERTS. That cap is Quake 3's and does not
apply here: src/common/models/models_md3.cpp has no vertex limit, it just Resize()s
to whatever the header declares, and 112 surfaces already shipping in this mod are
over 4096 -- the largest 18929, four and a half times the supposed ceiling. The only
real MD3 constraint is the int16 position format, +/- 512 model units.

Splitting on that mistaken premise did active damage, all of it traced in
HANDOFF_2026-10-24.md section 11: the MG42's belt drum became the largest surface on
the gun and was claimed for the body, the Kar98's grip search found nothing because
the biggest slab did not contain the trigger, and the tec9's magazine was swallowed
whole into a slab and stopped being addressable.

What this IS still for: making a piece the game must treat on its own -- a lens, a
bulb, a panel needing its own SurfaceSkin -- into its own surface. That is a real
need and md3_carve_surface.py is the right tool for it. Bulk is not a reason."""
import sys, os, subprocess, shutil
sys.path.insert(0, "E:/DOOMWork/RS_ModelSwapper/tools_kit")
import numpy as np
from md3read import read_md3
T = "E:/DOOMWork/RS_ModelSwapper/tools_kit"
CAP = 4000

def over(path):
    m = read_md3(path)
    out = []
    for i, s in enumerate(m['surfs']):
        if s['nverts'] > CAP:
            x = s['xyz'][0][:, 0]
            out.append((i, s['name'], s['nverts'], float(x.min()), float(x.max())))
    return out

def fix(path):
    cuts = 0
    for _ in range(16):
        o = over(path)
        if not o: return cuts, None
        i, name, nv, xlo, xhi = max(o, key=lambda t: t[2])
        taken = {s['name'] for s in read_md3(path)['surfs']}
        k = int(np.ceil(nv / float(CAP)))
        ok = False
        # A thin slab can catch loose vertices without containing one whole triangle,
        # which the carve refuses. Widen the slab until a triangle fits.
        for widen in (1.0, 1.4, 2.0, 2.8, 4.0):
            frac = min(0.9, widen / k)
            lo = xhi - (xhi - xlo) * frac
            n = 2
            while "body_p%d" % n in taken: n += 1
            tmp = path + ".tmp.md3"
            r = subprocess.run([sys.executable, "-B", os.path.join(T, "md3_carve_surface.py"),
                                path, tmp, "--surface", str(i), "--name", "body_p%d" % n,
                                "--slab-axis", "x", "--slab", "%.3f" % lo, "%.3f" % (xhi + 1),
                                "--centre", "0", "0", "--radius", "1000"],
                               capture_output=True, text=True)
            if r.returncode == 0 and os.path.exists(tmp):
                shutil.move(tmp, path); cuts += 1; ok = True; break
            if os.path.exists(tmp): os.remove(tmp)
        if not ok:
            return cuts, "carve failed on %s: %s" % (name, (r.stderr or r.stdout)[-160:])
    return cuts, "still over after 16 cuts"

if __name__ == '__main__':
    c, err = fix(sys.argv[1])
    m = read_md3(sys.argv[1])
    big = max(s['nverts'] for s in m['surfs'])
    print("%-12s %d cuts, %d surfaces, largest %d verts %s" % (
        os.path.basename(sys.argv[1]), c, len(m['surfs']), big, ("| " + err) if err else "| OK"))
