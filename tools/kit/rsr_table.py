"""Read and write the RSR_Guns reload table (gen_rsr.py's ZScript output) as data.

    rows(text)          -> {accessor: {index: value-text}}, plus the switch/array shape
Every accessor in the generated file is either a `switch (i) { case N: return X; }` or a
static const array indexed by i. This reads both, so a row can be lifted from one table
(BD22's rsr_guns.bd.zs) into another (ModelSwapper's rsr_guns.ms.zs) without retyping."""
import re

FN = re.compile(r'clearscope static (\S+) (\w+)\(([^)]*)\)\s*\n?\s*\{', re.M)

def functions(text):
    out = []
    for m in FN.finditer(text):
        depth = 0; i = m.end() - 1
        while True:
            c = text[i]
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: break
            i += 1
        out.append(dict(ret=m.group(1), name=m.group(2), args=m.group(3), start=m.start(), end=i + 1, body=text[m.end():i]))
    return out

def cases(body):
    return {int(n): v.strip() for n, v in re.findall(r'case\s+(\d+):\s*return\s+([^;]+);', body)}

def array(body):
    m = re.search(r'static const \w+ v\[\] = \{(.*?)\};', body, re.S)
    if not m: return None
    return [x.strip() for x in m.group(1).split(',')]

def row(text, idx):
    """every accessor's value for one index"""
    out = {}
    for f in functions(text):
        c = cases(f['body'])
        if c:
            out[f['name']] = c.get(idx); continue
        a = array(f['body'])
        if a is not None:
            out[f['name']] = ('ARRAY', a[idx] if idx < len(a) else None)
    return out
