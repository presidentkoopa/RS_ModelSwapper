"""sndpack.py -- resolve every sound name a built pack uses to SNDINFO lines and files.

Sources, in order: RS_VR_Weapons/SNDINFO.txt (+ RS_Modern), rs_vr_reload/SNDINFO.txt. IWAD names
(weapons/*, misc/*, dsxxx) are left to the IWAD. $random groups pull their members; $volume /
$limit / $pitchshift lines for a name come along. Returns the unresolved names.
"""
import os, re, shutil, glob

IWAD = re.compile(r'^(weapons|misc|world|monsters|player|intermission|menu|switches|plats|doors)/|^ds[a-z0-9]{1,6}$')


def parse_sndinfo(path):
    """name -> list of lines defining it; random groups -> members; file for plain lines"""
    defs = {}; files = {}; members = {}
    for raw in open(path, encoding='latin-1'):
        line = raw.split('//', 1)[0].strip()
        if not line:
            continue
        w = line.split()
        if w[0].startswith('$'):
            d = w[0].lower()
            if d == '$random' and len(w) >= 2:
                m = re.findall(r'\{(.*)\}', line)
                members[w[1]] = m[0].split() if m else []
                defs.setdefault(w[1], []).append(line)
            elif d in ('$volume', '$limit', '$pitchshift', '$rolloff', '$attenuation') and len(w) >= 2:
                defs.setdefault(w[1], []).append(line)
            elif d == '$alias' and len(w) >= 3:
                defs.setdefault(w[1], []).append(line); members[w[1]] = [w[2]]
            continue
        if len(w) >= 2:
            defs.setdefault(w[0], []).append(line)
            files[w[0]] = w[1]
    return defs, files, members


def resolve(names, sources, out_dir):
    """names: sound names used. sources: [(sndinfo path, sound root dir)]. Writes SNDINFO.txt and
    copies the files under out_dir. Returns (resolved, unresolved)."""
    parsed = [(parse_sndinfo(p), root) for p, root in sources if os.path.exists(p)]
    lines = ['// RS Quest VR weapons: the sounds this set names, pulled from RS_VR_Weapons / rs_vr_reload (sndpack.py)']
    done = set(); unresolved = []
    todo = [n for n in sorted(set(names)) if n and not IWAD.match(n)]
    while todo:
        n = todo.pop(0)
        if n in done:
            continue
        done.add(n)
        hit = False
        for (defs, files, members), root in parsed:
            if n in defs:
                hit = True
                lines += defs[n]
                for m in members.get(n, []):
                    if m not in done:
                        todo.append(m)
                if n in files:
                    src = os.path.join(root, files[n])
                    cands = [src] if os.path.exists(src) else glob.glob(src + '.*')
                    if not cands:
                        unresolved.append(n + ' (file missing: %s)' % files[n])
                    else:
                        dst = os.path.join(out_dir, os.path.relpath(cands[0], root))
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(cands[0], dst)
                break
        if not hit:
            unresolved.append(n)
    open(os.path.join(out_dir, 'SNDINFO.txt'), 'w').write('\n'.join(lines) + '\n')
    return sorted(done), unresolved
