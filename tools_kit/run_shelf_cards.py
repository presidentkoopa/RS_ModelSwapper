"""Run the magazine card generator over the WHOLE shelf, not a hand-written table.

card_from_motion ships a MESH dict naming nine guns by hand. That was right while
nine guns were carded; it is the wrong shape for 189. Nothing in the generator
changes -- this only fills MESH from evidence already on disk:

  model dir / mesh / skin   from the donor's own Model block in modeldef
  type                      from the archetype on its shelf row in RS_ForeignModels.zs
  capacity                  a per-archetype default, listed below and easy to correct

Only guns whose card carries a measured `mag_in` insertion phase are converted,
which is the generator's own gate, unchanged.
"""
import os, re, sys
sys.path.insert(0, 'tools_kit')
sys.dont_write_bytecode = True
import card_from_motion as cfm

# Rounds per magazine. These are defaults by archetype, not measurements -- the
# mesh cannot tell us a capacity. They are here so a gun gets a sane number
# instead of none; correct any that matter.
CAP = {
    'pistol': 12, 'pistol_mag': 12, 'revolver': 6, 'smg': 32, 'rifle': 20,
    'shotgun': 8, 'chaingun': 50, 'plasma': 100, 'railgun': 10, 'launcher': 1,
    'rocket': 1, 'bfg': 40, 'flamethrower': 100, 'grenade': 1, 'cell': 40,
}


def shelf(cards_dir):
    md = open('modeldef', encoding='utf-8', errors='replace').read()
    zs = open('zscript/RS_ForeignModels.zs', encoding='utf-8', errors='replace').read()
    arch = {n: a for a, n in re.findall(r'"([a-z]+)\|(MS_\w+)\|', zs)}
    mesh = {}
    for name, b in re.findall(r'(?ms)^Model\s+(\S+)\s*\r?\n\{(.*?)^\}', md):
        p = re.search(r'Path\s+"([^"]+)"', b)
        f = re.search(r'Model\s+0\s+"([^"]+)"', b)
        sk = re.search(r'(?:Skin\s+0|SurfaceSkin\s+0\s+\d+)\s+"([^"]+)"', b)
        if not (p and f):
            continue
        d = p.group(1).rstrip('/')
        mesh[name] = (d, f.group(1), sk.group(1) if sk else '', arch.get(name, 'pistol'))
    out = {}
    for n, (d, f, sk, a) in mesh.items():
        if not os.path.exists(os.path.join(cards_dir, n + '.card')):
            continue
        out[n] = (d, f, sk, a, CAP.get(a, 12))
    return out


if __name__ == '__main__':
    cards_dir, outpath = sys.argv[1], sys.argv[2]
    cfm.SRC = cards_dir
    cfm.MESH = shelf(cards_dir)
    print(f'{len(cfm.MESH)} donors have a card in {cards_dir}/')
    cfm.main(outpath)
