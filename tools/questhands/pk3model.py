"""Look up what the pack draws for (class, sprite, frame): mesh file, mesh frame, placement."""
import re, os

def blocks(modeldef_text):
    out = []
    for m in re.finditer(r'^Model (\S+)\s*\{(.*?)^\}', modeldef_text, re.M | re.S):
        cls, b = m.group(1), m.group(2)
        path = re.search(r'Path\s+"([^"]+)"', b).group(1).rstrip('/')
        mesh = re.search(r'Model\s+0\s+"([^"]+)"', b).group(1)
        pl = {'scale': (1.0, 1.0, 1.0), 'off': [0.0, 0.0, 0.0]}
        for l in b.split('\n'):
            l = l.strip()
            mm = re.match(r'Scale\s+(\S+)\s+(\S+)\s+(\S+)', l, re.I)
            if mm: pl['scale'] = tuple(float(x) for x in mm.groups())
            mm = re.match(r'Offset\s+(\S+)\s+(\S+)\s+(\S+)', l, re.I)
            if mm: pl['off'] = [float(x) for x in mm.groups()]
            mm = re.match(r'ZOffset\s+(\S+)', l, re.I)
            if mm: pl['off'][2] = float(mm.group(1))
        keys = {}
        for fm in re.finditer(r'FrameIndex\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)', b):
            keys[(fm.group(1).upper(), fm.group(2).upper())] = int(fm.group(4))
        out.append(dict(cls=cls, path=path, mesh=mesh, keys=keys, **pl))
    return out

def lookup(bl, cls, spr, fr, root):
    for b in bl:
        if b['cls'] == cls and (spr, fr) in b['keys']:
            return dict(path=os.path.join(root, b['path'], b['mesh']), frame=b['keys'][(spr, fr)],
                        scale=list(b['scale']), off=list(b['off']))
    return None
