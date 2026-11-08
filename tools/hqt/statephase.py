#!/usr/bin/env python3
"""
statephase.py -- the frame map the MESH cannot give you: which mesh frame plays under which weapon state,
in what order, from the MODELDEF (sprite frame -> mesh frame) and the DECORATE/ZScript states (state ->
sprite frames, in sequence, forwards and backwards).

The owner's rule, 2026-10-31: "if a mesh says it doesn't move or reload, it is lying to you; if the
modeldef says it doesn't, it is lying to you; this is what the tools are for." A pump that only goes
back in the mesh comes home because the code plays its frames in reverse (BrutalWolf trench gun:
`ZSGP ABCDEFGHI`, hold `JKL`, `KJIHGFEDCBA`). Nothing in the vertex data shows that.

Usage:  statephase.py MODELDEF ACTORFILE [ModelName]   -> prints state -> mesh frame sequence
        import statephase; statephase.phases(modeldef_path, actor_path, model) -> {state: [frames]}
"""
import re, sys

def bindings(modeldef_path, model=None):
    """{(sprite, letter): mesh_frame} for the (first or named) Model block"""
    t = open(modeldef_path, errors='replace').read()
    t = re.sub(r'//[^\n]*', '', t)
    out = {}
    for m in re.finditer(r'Model\s+(\S+)\s*\{(.*?)\}', t, re.S):
        name, body = m.group(1), m.group(2)
        if model and name.lower() != model.lower(): continue
        for b in re.finditer(r'FrameIndex\s+(\w{4})\s+([A-Z\[\]\\])\s+(\d+)\s+(\d+)', body):
            out[(b.group(1).upper(), b.group(2))] = int(b.group(4))
        if out: break
    return out

def states(actor_path):
    """[(state_name, [(sprite, letters, tics)])] in file order, from the first actor with States"""
    t = open(actor_path, errors='replace').read()
    t = re.sub(r'//[^\n]*', '', t); t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    i = t.find('States'); t = t[i:] if i >= 0 else t
    out = []; cur = None
    for line in t.splitlines():
        s = line.strip()
        m = re.match(r'^([A-Za-z_][\w.]*)\s*:\s*$', s)
        if m: cur = m.group(1); out.append((cur, [])); continue
        m = re.match(r'^(\w{4})\s+([A-Z\[\]\\]+)\s+(-?\d+)', s)
        if m and cur: out[-1][1].append((m.group(1).upper(), m.group(2), int(m.group(3))))
    return out

def phases(modeldef_path, actor_path, model=None):
    B = bindings(modeldef_path, model); out = {}
    for st, rows in states(actor_path):
        seq = []
        for spr, letters, tics in rows:
            for L in letters:
                f = B.get((spr, L))
                if f is not None: seq += [f] * max(1, tics)
        if seq: out[st] = seq
    return out

def summarize(seq):
    """compress [0,0,1,1,2,3,3,2,1] -> '0,1,2,3 then 2,1' (forward runs and reverse runs)"""
    u = [seq[0]] + [f for a, f in zip(seq, seq[1:]) if f != a]
    return ','.join(map(str, u))

if __name__ == '__main__':
    P = phases(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    for st, seq in P.items():
        print('%-16s %3d tics  frames %s' % (st, len(seq), summarize(seq)))
