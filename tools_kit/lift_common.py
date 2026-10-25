"""lift_common.py -- what every lift / regen tool shares: ModelSwapper's generated tables read and
written as data (both shapes: `case N: return X;` switches and static const arrays), MODELDEF blocks,
donor placement and rest frames, md3 frames. Moved here unchanged from lift_bd22.py, lift_aliens.py
and placement_audit.py on 2026-10-25 (one copy each; the tools import from here)."""
import os, re, sys, struct
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import rsr_table as T
import md3_frames as M3


def donor_blocks(text=None):
    """class -> the FIRST block of that class in `modeldef` (the donor block: placement + rest frame)"""
    if text is None:
        text = open(os.path.join(ROOT, 'modeldef'), encoding='utf-8', errors='replace').read()
    out = {}
    for m in re.finditer(r'^Model\s+(\w+)\s*\n\{(.*?)^\}', text, re.S | re.M):
        out.setdefault(m.group(1), m.group(2))
    return out


# from lift_bd22.py
def read(p):
    return open(p, encoding='utf-8', errors='replace').read()


# from lift_bd22.py
def write(p, t):
    open(p, 'w', encoding='utf-8', newline='\n').write(t)


# from lift_bd22.py
def bd22_blocks(text):
    """every Model block with the comment lines just above it"""
    out = []
    for m in re.finditer(r'((?:^[ \t]*//[^\n]*\n)*)^[ \t]*Model\s+(\S+)\s*\n?\s*\{(.*?)^[ \t]*\}', text, re.S | re.M):
        out.append(dict(comment=m.group(1), cls=m.group(2), body=m.group(3), text=m.group(0)))
    return out


# from lift_bd22.py
def frames_of(body):
    return re.findall(r'FrameIndex\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)', body)


# from lift_bd22.py
def append_rows(target, source, src_idx, new_idx, overrides):
    """append source row src_idx to every accessor of target as row new_idx"""
    tf = T.functions(target)
    sf = {f['name']: f for f in T.functions(source)}
    edits = []
    for f in tf:
        name = f['name']
        if name in ('Index', 'HandOf', 'DonorInHand', 'SlotForDonor', 'Count'):
            continue
        if 'int k' in f['args'] and name in sf:
            # PER CHAMBER (rsb_guns.zs Base/Tip/Bore/Rest*): switch (i * 8 + k) -- copy the
            # source gun's eight keys, renumbered to the new gun's
            src = T.cases(sf[name]['body'])
            rows = ['\t\tcase %d:\treturn %s;' % (new_idx * 8 + k - src_idx * 8, src[k])
                    for k in sorted(src) if src_idx * 8 <= k < src_idx * 8 + 8]
            last = list(re.finditer(r'^[ \t]*case\s+\d+:[^\n]*\n', f['body'], re.M))
            if rows and last:
                edits.append((f['end'] - 1 - len(f['body']) + last[-1].end(), '\n'.join(rows) + '\n'))
            continue
        if name == 'PushEdge' and name in sf:
            # 25 values per gun, e[(i - 1) * 25 + b], and an i <= N guard
            body = f['body']
            m = re.search(r'static const double e\[\] = \{(.*?)\};', body, re.S)
            sm = re.search(r'static const double e\[\] = \{(.*?)\};', sf[name]['body'], re.S)
            cur = [x.strip() for x in m.group(1).split(',') if x.strip()]
            sv = [x.strip() for x in sm.group(1).split(',') if x.strip()]
            cur = cur[:(new_idx - 1) * 25] + ['-999.0'] * max(0, (new_idx - 1) * 25 - len(cur)) + sv[(src_idx - 1) * 25:src_idx * 25]
            rows = ['\t\t\t' + ', '.join(cur[r * 25:(r + 1) * 25]) for r in range(len(cur) // 25)]
            nb = body.replace(m.group(0), 'static const double e[] = {\n' + ',\n'.join(rows) + '};')
            nb = re.sub(r'return i >= 1 && i <= \d+ \?', 'return i >= 1 && i <= %d ?' % new_idx, nb)
            edits.append(('REPLACE', f['end'] - 1 - len(body), f['end'] - 1, nb))
            continue
        body = f['body']
        if 'switch' in body:
            if name in overrides:
                val = overrides[name]
            else:
                val = T.cases(sf[name]['body']).get(src_idx) if name in sf else None
            if val is None:
                continue
            last = list(re.finditer(r'^[ \t]*case\s+\d+:[^\n]*\n', body, re.M))
            if not last:
                continue
            at = f['start'] + (len(target[f['start']:f['end']]) - len(body) - 1) + last[-1].end()
            # recompute absolute: body begins at end-1-len(body)
            body_abs = f['end'] - 1 - len(body)
            at = body_abs + last[-1].end()
            edits.append((at, '\t\tcase %d:\treturn %s;\n' % (new_idx, val)))
        else:
            body_abs = f['end'] - 1 - len(body)
            for am in re.finditer(r'static const (\w+) (\w+)\[\] = \{(.*?)\};', body, re.S):
                typ, arr, items = am.group(1), am.group(2), [x.strip() for x in am.group(3).split(',')]
                if name in overrides:
                    val = overrides[name]
                else:
                    val = None
                    if name in sf:
                        sm = re.search(r'static const \w+ %s\[\] = \{(.*?)\};' % arr, sf[name]['body'], re.S)
                        if sm:
                            sitems = [x.strip() for x in sm.group(1).split(',')]
                            if src_idx < len(sitems):
                                val = sitems[src_idx]
                default = {'bool': 'false', 'String': '""', 'string': '""'}.get(typ, '0')
                pad = [default] * max(0, new_idx - len(items))
                add = pad + [val if val is not None else default]
                close = body_abs + am.start(3) + len(am.group(3))
                edits.append((close, ', ' + ', '.join(add)))
    for e in sorted(edits, key=lambda e: e[1] if e[0] == 'REPLACE' else e[0], reverse=True):
        if e[0] == 'REPLACE':
            target = target[:e[1]] + e[3] + target[e[2]:]
        else:
            target = target[:e[0]] + e[1] + target[e[0]:]
    return target


# from lift_bd22.py
def add_slot_for_donor(target, name, slot):
    f = next(f for f in T.functions(target) if f['name'] == 'SlotForDonor')
    body_abs = f['end'] - 1 - len(f['body'])
    m = list(re.finditer(r'^[ \t]*return 0;', f['body'], re.M))[-1]
    at = body_abs + m.start()
    return target[:at] + '\t\tif (donor == "%s")\treturn %d;\n' % (name, slot) + target[at:]


# from lift_bd22.py
def count_of(target):
    m = re.search(r'static int Count\(\) \{ return (\d+); \}', target)
    return int(m.group(1)) if m else None


# from lift_bd22.py
def array_len(target, fname):
    f = next(f for f in T.functions(target) if f['name'] == fname)
    m = re.search(r'static const \w+ \w+\[\] = \{(.*?)\};', f['body'], re.S)
    return len(m.group(1).split(','))


# from lift_bd22.py
def insert_after_array_head(t, head, rows):
    """APPEND at the array's end. A saved pick is an index into its archetype's rows, in
    array order, so a row inserted ahead of existing ones would move every player's pick."""
    start = t.index(head) + len(head)
    close = t.index('};', start)
    body = t[start:close].rstrip()
    if not body.endswith(','):
        body += ','
    return t[:start] + body + '\n\t\t\t// BD22Q guns (tools_kit/lift_bd22.py)\n' + '\n'.join('\t\t\t' + r for r in rows).rstrip(',') + '\n\t\t' + t[close:]


# from lift_bd22.py
def md3_frames(p):
    import struct
    return struct.unpack_from('<i', open(p, 'rb').read(), 76)[0]


# from lift_aliens.py
ARR = re.compile(r'static const (\w+) (\w+)\[\] = \{(.*?)\};', re.S)


# from lift_aliens.py
def read_row(text, idx):
    out = {}
    for f in T.functions(text):
        c = T.cases(f['body'])
        if c:
            if idx in c:
                out[f['name']] = ('case', c[idx])
            continue
        arrs = {}
        for m in ARR.finditer(f['body']):
            items = [x.strip() for x in m.group(3).split(',')]
            if idx < len(items):
                arrs[m.group(2)] = items[idx]
        if arrs:
            out[f['name']] = ('arr', arrs)
    return out


# from lift_aliens.py
def set_row(target, idx, values):
    """write row idx: replace a `case idx:` / array item that is there, else add it"""
    for name, (kind, val) in values.items():
        f = next((f for f in T.functions(target) if f['name'] == name), None)
        if f is None:
            continue
        body = f['body']; b0 = f['end'] - 1 - len(body)
        if kind == 'case':
            if 'switch' not in body:
                continue
            m = re.search(r'^([ \t]*case\s+%d:\s*return\s+)([^;]+)(;)' % idx, body, re.M)
            if m:
                nb = body[:m.start(2)] + val + body[m.end(2):]
            else:
                last = list(re.finditer(r'^[ \t]*case\s+(\d+):[^\n]*\n', body, re.M))
                after = [l for l in last if int(l.group(1)) > idx]
                at = after[0].start() if after else last[-1].end()
                nb = body[:at] + '\t\tcase %d:\treturn %s;\n' % (idx, val) + body[at:]
        else:
            nb = body
            for m in reversed(list(ARR.finditer(body))):
                typ, arr = m.group(1), m.group(2)
                if arr not in val:
                    continue
                items = [x.strip() for x in m.group(3).split(',')]
                default = {'bool': 'false', 'String': '""', 'string': '""'}.get(typ, '0')
                items += [default] * max(0, idx + 1 - len(items))
                items[idx] = val[arr]
                nb = nb[:m.start(3)] + ', '.join(items) + nb[m.end(3):]
        target = target[:b0] + nb + target[b0 + len(body):]
    return target


# from lift_aliens.py
def slot_of(text, donor):
    m = re.search(r'donor == "%s"\)\s*return (\d+);' % re.escape(donor), text)
    return int(m.group(1)) if m else None


# from lift_aliens.py
def max_slot(text):
    return max([0] + [int(x) for x in re.findall(r'donor == "\w+"\)\s*return (\d+);', text)])


# from lift_aliens.py
def tc_index(text):
    f = next(f for f in T.functions(text) if f['name'] == 'Index')
    return {c: int(n) for c, n in re.findall(r"w is '(\w+)'\)\s*return (\d+);", f['body'])}


# from lift_aliens.py
def block_of(text, cls):
    m = re.search(r'^Model\s+%s\s*\n\{(.*?)^\}' % re.escape(cls), text, re.S | re.M)
    return m


# from lift_aliens.py
def get_line(body, key):
    m = re.search(r'^[ \t]*%s\s+([^\n/]+)' % key, body, re.M | re.I)
    return [float(x) for x in m.group(1).split()] if m else None


# from lift_aliens.py
def frame_names(p):
    d = open(p, 'rb').read(); h = struct.unpack_from(M3.HDR, d, 0)
    return [d[h[8] + i * 56 + 40:h[8] + i * 56 + 56].split(b'\0')[0].decode() for i in range(h[4])]


# from lift_aliens.py
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


# from placement_audit.py
def placement(body):
    sc = [float(x) for x in re.search(r'^\s*Scale\s+([^\n/]+)', body, re.M).group(1).split()]
    om = re.search(r'^\s*Offset\s+([^\n/]+)', body, re.M)
    off = [float(x) for x in om.group(1).split()] if om else [0.0, 0.0, 0.0]
    off += [0.0] * (3 - len(off))
    z = re.search(r'^\s*ZOffset\s+([-\d.]+)', body, re.M)
    if z:
        off[2] = float(z.group(1))
    return sc, off


# from placement_audit.py
def vec(s):
    return [float(x) for x in s.strip('()').split(',')]


# from placement_audit.py
def resolve(p):
    """the file as the engine finds it: lump names are case-insensitive, Linux paths are not"""
    if os.path.exists(p):
        return p
    cur = '/'
    for part in os.path.abspath(p).strip('/').split('/'):
        hit = [x for x in os.listdir(cur) if x.lower() == part.lower()] if os.path.isdir(cur) else []
        if not hit:
            return p
        cur = os.path.join(cur, hit[0])
    return cur


# from placement_audit.py
def frame0(p, f=0):
    import genpack as gp
    p = resolve(p)
    s = gp.md3_surfaces(p)[1]
    f = min(f, s[0]['xyz'].shape[0] - 1)
    return np.concatenate([x['xyz'][f] for x in s])


# from placement_audit.py
def shelf_rest():
    t = open(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs')).read()
    return {m.group(1): int(m.group(2)) for m in re.finditer(r'"\w+\|(\w+)\|\w{4}\|\d+\|(\d+)\|\d+"', t)}


blocks = bd22_blocks
