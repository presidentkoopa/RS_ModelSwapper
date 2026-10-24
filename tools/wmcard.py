"""wmcard.py -- read RS_VR_Weapons WMCARD lumps into Python dicts.

Grammar (as the cards are written):
    weapon "Class"            ... key = value lines ... end
    grip   ... end                      (follows its weapon)
    part <name> ... key = value ... dof ... end ... end
    verb / mechanism lines are kept as raw key/value too
Values: numbers, comma vectors, quoted strings (one or two), bare words.
Comments: # to end of line.
"""
import re, sys, glob, os

NUM = re.compile(r'^-?\d+(\.\d+)?$')


def _val(s):
    s = s.strip()
    q = re.findall(r'"([^"]*)"', s)
    if q:
        return q if len(q) > 1 else q[0]
    if ',' in s:
        parts = [p.strip() for p in s.split(',')]
        if all(NUM.match(p) for p in parts):
            return [float(p) for p in parts]
        return parts
    if NUM.match(s):
        return float(s) if '.' in s else int(s)
    return s


def parse_text(text, src=''):
    """returns list of weapons: dict(cls, keys{}, grip{}, parts{name: dict(keys, dof{})}, src)"""
    weapons = []
    cur = None          # current weapon
    stack = []          # block names: 'weapon' | 'grip' | 'part' | 'dof' | other
    part = None
    for ln, raw in enumerate(text.splitlines(), 1):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        w = line.split()
        head = w[0].lower()
        if head == 'weapon' and len(w) >= 2 and '=' not in line:
            cur = dict(cls=_val(' '.join(w[1:])), keys={}, grip={}, parts={}, order=[], src=src, line=ln)
            weapons.append(cur)
            stack = ['weapon']
            continue
        if head == 'end':
            if stack:
                stack.pop()
            if not stack:
                part = None
            continue
        if cur is None:
            continue
        if head == 'grip' and len(w) == 1:
            stack.append('grip'); continue
        if head == 'part' and len(w) >= 2 and '=' not in line:
            part = dict(name=w[1], keys={}, dof={}, surfaces=[])
            cur['parts'][w[1]] = part
            cur['order'].append(w[1])
            stack.append('part'); continue
        if head == 'dof' and len(w) == 1:
            stack.append('dof'); continue
        if '=' not in line:
            # some other block (verb, store, load, ...): keep nesting right, key by name
            stack.append(head + (':' + w[1] if len(w) > 1 else ''))
            continue
        k, v = line.split('=', 1)
        k = k.strip().lower(); v = _val(v)
        top = stack[-1] if stack else 'weapon'
        if top == 'dof' and part is not None:
            part['dof'][k] = v
        elif top == 'part' and part is not None:
            if k == 'surface':
                part['surfaces'].append(v)
            else:
                part['keys'][k] = v
        elif top == 'grip':
            cur['grip'][k] = v
        elif top == 'weapon':
            cur['keys'][k] = v
        else:
            cur['keys'].setdefault('_' + top, {})[k] = v
    return weapons


def load(paths):
    out = []
    for p in paths:
        out += parse_text(open(p, encoding='utf-8', errors='replace').read(), os.path.basename(p))
    return out


if __name__ == '__main__':
    files = sys.argv[1:]
    ws = load(files)
    print(len(ws), 'weapons')
    for g in ws:
        k = g['keys']
        parts = ', '.join('%s[%s%s]' % (n, g['parts'][n]['keys'].get('role', '?'),
                                         ':' + g['parts'][n]['dof']['kind'] if 'kind' in g['parts'][n]['dof'] else '')
                          for n in g['order'])
        model = k.get('model'); model = model[1] if isinstance(model, list) else model
        print('%-22s %-10s %-8s %-28s grip=%s  %s' % (g['cls'], g['src'][:10], k.get('type', '?'), model,
              'palm' in g['grip'], parts))
