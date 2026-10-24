#!/usr/bin/env python3
"""batch.py <folder-of-md3s> <outdir>
Label EVERY MD3 under the folder in one pass. For each model: guess the archetype from what moves
(no names needed), run md3label.py, write Name.card / Name_stable.md3 / carves, and one row in
<outdir>/TABLE.md with a confidence flag. Models flagged LOW need one word from the owner
(the archetype); the rest need nothing. Also <outdir>/sheet.png: one row per model, idle +
busiest frames, so the whole set is checked by eye in one picture."""
import os
import sys, os, glob, subprocess, traceback; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from md3read import read_md3

def kabsch(P, Q):
    pc, qc = P.mean(0), Q.mean(0); H = (P - pc).T @ (Q - qc); U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T)); R = Vt.T @ np.diag([1, 1, d]) @ U.T; return R, qc - R @ pc
def rot_deg(R): return np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
def rot_axis(R):
    w = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]); n = np.linalg.norm(w); return w / n if n > 1e-9 else w

def survey(path):
    """What moves, relative to the body, with sway removed. Returns a dict the guesser reads."""
    m = read_md3(path); S = m['surfs']; nf = m['nframes']
    if len(S) == 0: return dict(error="no surfaces")
    body = max(range(len(S)), key=lambda i: S[i]['nverts']); B = S[body]['xyz']
    idle = 0
    for f in range(1, nf):
        if rot_deg(kabsch(B[f - 1], B[f])[0]) < 2.0: idle = f - 1; break
    Rs = [kabsch(B[f], B[idle]) for f in range(nf)]
    to_wpn = lambda i, f: S[i]['xyz'][f] @ Rs[f][0].T + Rs[f][1]
    ext = B[idle].max(0) - B[idle].min(0); bodyc = B[idle].mean(0)
    # bore guess: body's longest extent axis, sign toward the thin end
    bore_i = int(np.argmax(ext)); bore = np.zeros(3); bore[bore_i] = 1.0
    parts = []
    for i, s in enumerate(S):
        if i == body: continue
        X = [to_wpn(i, f) for f in range(nf)]
        diag = [np.linalg.norm(X[f].max(0) - X[f].min(0)) for f in range(nf)]
        vis = [f for f in range(nf) if diag[f] > 0.5]
        hidden_idle = diag[idle] < 0.5
        if not vis: continue
        ref = vis[0] if hidden_idle else idle
        c0 = X[ref].mean(0); size = X[ref].max(0) - X[ref].min(0)
        tr = 0; rt = 0; raxis = np.zeros(3); tdir = np.zeros(3)
        for f in vis:
            d = X[f].mean(0) - c0; dn = np.linalg.norm(d)
            if dn > tr: tr, tdir = dn, d / dn
            R, _ = kabsch(X[ref], X[f]); a = rot_deg(R)
            if a > rt: rt, raxis = a, rot_axis(R)
        parts.append(dict(i=i, nv=s['nverts'], size=size, maxsize=float(max(size)), rest=c0 - bodyc, travel=float(tr), tdir=tdir,
                          rot=float(rt), raxis=raxis, hidden=hidden_idle, busiest=int(max(vis, key=lambda f: np.linalg.norm(X[f].mean(0) - c0)))))
    sway = [rot_deg(Rs[f][0]) for f in range(nf)]
    return dict(nf=nf, nsurf=len(S), body=body, bodyv=S[body]['nverts'], idle=idle, ext=ext, bore=bore, parts=parts, sway=sway, verts=sum(s['nverts'] for s in S))

def guess(sv):
    """Archetype from motion alone. Returns (archetype, confidence, reason)."""
    if 'error' in sv: return 'unknown', 'LOW', sv['error']
    P = sv['parts']; bore = sv['bore']; L = float(max(sv['ext']))
    if sv['nsurf'] == 1: return 'arcade', 'HIGH', 'one surface: nothing separable; tier 0 only'
    movers = [p for p in P if p['travel'] > 1.0 or p['rot'] > 10]
    big = lambda p: p['maxsize'] > 0.12 * L
    slides = [p for p in movers if big(p) and p['travel'] > 0.04 * L and abs(p['tdir'] @ bore) > 0.8]
    drops = [p for p in movers if big(p) and p['travel'] > 0.08 * L and abs(p['tdir'] @ bore) < 0.6]
    hinges = [p for p in movers if big(p) and p['rot'] > 15 and p['travel'] < 0.4 * p['rot'] and abs(p['raxis'] @ bore) < 0.7]
    spinners = [p for p in movers if big(p) and p['rot'] > 15 and abs(p['raxis'] @ bore) > 0.8]
    smalls = [p for p in P if p['hidden'] and p['maxsize'] < 0.15 * L]
    if drops and slides: return 'pistol_mag', 'HIGH', f'mag drops {drops[0]["travel"]:.0f} + slide runs {slides[0]["travel"]:.0f} along bore'
    if hinges and not drops: return 'break_action', 'HIGH' if smalls else 'MED', f'part hinges {hinges[0]["rot"]:.0f}deg off-bore' + (' with hidden cases/shells' if smalls else '')
    if slides and not drops:
        # a pump is forward of the body centre and under the bore; a slide is over the grip
        fwd = [p for p in slides if p['rest'] @ bore > 0.1 * L]
        if fwd: return 'shotgun_pump', 'HIGH' if smalls else 'MED', f'forward part strokes {fwd[0]["travel"]:.0f} along bore' + (' with hidden shells' if smalls else '')
        return 'bolt_or_slide', 'MED', f'rear part strokes {slides[0]["travel"]:.0f} along bore, no mag drop'
    if drops: return 'mag_only', 'MED', f'part drops {drops[0]["travel"]:.0f} with no slide: mag change, no rack'
    if spinners: return 'revolver', 'MED', f'part spins {spinners[0]["rot"]:.0f}deg about the bore'
    if movers: return 'arcade', 'MED', f'{len(movers)} small movers only (trigger/hammer class)'
    return 'arcade', 'HIGH', 'nothing moves relative to the body'

ARCH_FOR_LABELLER = {'pistol_mag': 'pistol_mag', 'shotgun_pump': 'shotgun_pump', 'break_action': 'revolver_topbreak'}

def main():
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src, '**', '*.md3'), recursive=True))
    rows = []; sheet_rows = []
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        try:
            sv = survey(f); arch, conf, why = guess(sv)
        except Exception as e:
            rows.append((name, '-', 'ERROR', f'{type(e).__name__}: {e}', '', '')); continue
        if sv.get('nf', 0) == 1 and sv.get('nsurf', 0) > 1: why += '; single frame, parts named? -> namedcard.py'
        od = os.path.join(out, name); os.makedirs(od, exist_ok=True); log = ''
        la = ARCH_FOR_LABELLER.get(arch)
        if la and sv['nsurf'] > 1:
            carve = 'mag,round' if la == 'pistol_mag' else ('shell' if la == 'shotgun_pump' else 'loader,case')
            r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'md3label.py'), f, od, name, '--archetype', la, '--carve', carve, '--idle', str(sv['idle'])],
                               capture_output=True, text=True, timeout=600)
            open(os.path.join(od, 'label.log'), 'w').write(r.stdout + r.stderr)
            log = 'card' if r.returncode == 0 and os.path.exists(os.path.join(od, name + '.card')) else f'labeller rc={r.returncode}'
            if r.returncode != 0: conf = 'LOW'
        else:
            log = 'survey only'
        movers = sorted(sv.get('parts', []), key=lambda p: -(p['travel'] + p['rot'] / 10))[:3]
        parts = '; '.join(f"s{p['i']} {'HID ' if p['hidden'] else ''}{p['maxsize']:.0f}u tr{p['travel']:.0f} rot{p['rot']:.0f}" for p in movers)
        rows.append((name, f"{sv['nf']}f/{sv['nsurf']}s/{sv['verts']}v", f"{arch} ({conf})", why, parts, log))
        busiest = sorted({p['busiest'] for p in movers} | {sv['idle']})[:4]
        sheet_rows.append((f, name, sv['idle'], busiest, f"{arch} ({conf})"))
        print(f"{name:<18} {arch:<14} {conf:<5} {why}", flush=True)
    with open(os.path.join(out, 'TABLE.md'), 'w') as t:
        t.write("# Batch label table\n\nOne row per MD3. HIGH = archetype read from motion with no doubt; MED = plausible, glance at the sheet; LOW = owner names the archetype.\n"
                "`parts` = the three busiest surfaces: index, HID if hidden at idle, longest side in model units, travel, rotation.\n\n")
        t.write("| model | frames/surfs/verts | archetype | why | parts | output |\n|---|---|---|---|---|---|\n")
        for r in rows: t.write("| " + " | ".join(str(x) for x in r) + " |\n")
    # contact sheet
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        n = len(sheet_rows); fig, axs = plt.subplots(n, 4, figsize=(16, 3.2 * n)); axs = np.atleast_2d(axs)
        for r, (f, name, idle, frames, lab) in enumerate(sheet_rows):
            m = read_md3(f); S = m['surfs']; body = max(range(len(S)), key=lambda i: S[i]['nverts']); B = S[body]['xyz']
            pal = ['#d62728', '#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b', '#e377c2', '#17becf', '#bcbd22', '#aec7e8', '#ffbb78', '#98df8a']
            for c, fr in enumerate((frames + [idle] * 4)[:4]):
                ax = axs[r, c]; R, t = kabsch(B[fr], B[idle])
                for i, s in enumerate(S):
                    P = s['xyz'][fr] @ R.T + t
                    if np.linalg.norm(P.max(0) - P.min(0)) < 0.5: continue
                    tri = P[s['tris']]; ax.add_collection(matplotlib.collections.PolyCollection(tri[:, :, [0, 2]], facecolors='#999999' if i == body else pal[i % 12], edgecolors='none', alpha=0.9))
                allp = np.vstack([s['xyz'][idle] for s in S]); lo, hi = allp.min(0), allp.max(0); pad = 0.05 * (hi - lo).max()
                ax.set_xlim(lo[0] - pad, hi[0] + pad); ax.set_ylim(lo[2] - pad, hi[2] + pad); ax.set_aspect('equal'); ax.axis('off')
                ax.set_title(f"{name}  f{fr}" + (f"  {lab}" if c == 0 else ""), fontsize=9, loc='left')
        plt.tight_layout(); plt.savefig(os.path.join(out, 'sheet.png'), dpi=60); print("sheet.png written")
    except Exception: traceback.print_exc()

if __name__ == '__main__': main()
