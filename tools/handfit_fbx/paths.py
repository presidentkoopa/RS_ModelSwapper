"""Where tools/handfit_fbx reads and writes. Depot-relative defaults; every outside input is an env var.

  HANDFIT_FBX      the FBX hand, hand_final.fbx (DXR models/hands/hand_final.fbx). REQUIRED, never committed.
  HANDFIT_FBX_TEX  its textures folder (lambert1_Base_Color.png ...). Default: <folder of HANDFIT_FBX>/textures.
  RSQ_GUNPACK      an extracted pack folder with MODELDEF.bd.txt and models/ (the guns and the 1.92 hands).
                   Default: tools/rig/build/src/bd22q_192/src, tag 1.92 of RS_Brutal22WeaponsQ, made by
                   `sh tools/rig/setup.sh` (same variable and default as tools/questhands).
  RSQ_ERMAC        Ermac's doom-force-unleashed_devbuild/models/ (hand/hand.md3, hand/hand2.md3): the calibration
                   reference. Same variable as tools/questhands. Not vendored.
  HANDFIT_WORK     results/, cache/ (distance fields), out/ (MD3, pk3), sheets/, rigout/ (engine runs).
                   Default: tools/handfit_fbx/work (gitignored).
  B22_RIG, B22_IWAD, B22_BD22, B22_VOX   the engine rig and the owner's load order, as tools/rig reads them.
                   B22_RIG default: tools/rig/bin (the prebuilt QuestZDoom 17.3).
data/ (committed) holds the measured inputs the fit reads: FBX calibration and landmarks, gun landmarks, 1.92's
measured tolerances. The scripts that measured them write them back there (calib.py, landmarks.py, ...)."""
import os
TOOL = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(os.path.dirname(TOOL))
DATA = os.path.join(TOOL, 'data')
WORK = os.path.abspath(os.environ.get('HANDFIT_WORK', os.path.join(TOOL, 'work')))
RESULTS = os.path.join(WORK, 'results'); OUT = os.path.join(WORK, 'out'); CACHE = os.path.join(WORK, 'cache')
SHEETS = os.path.join(WORK, 'sheets'); RIGOUT = os.path.join(WORK, 'rigout')
for _d in (RESULTS, OUT, CACHE, SHEETS):
    os.makedirs(_d, exist_ok=True)
def data(n): return os.path.join(DATA, n)

def _need(var, what, path=None):
    v = os.environ.get(var) if path is None else path
    if not v:
        raise SystemExit('handfit_fbx: %s is not set. %s' % (var, what))
    if not os.path.exists(v):
        raise SystemExit('handfit_fbx: %s=%s does not exist. %s' % (var, v, what))
    return v

FBX_WHAT = ('Point it at hand_final.fbx (DXR models/hands/hand_final.fbx; provenance in tools/handfit_fbx/README.md). '
            'The .fbx is never committed.')
FBX = _need('HANDFIT_FBX', FBX_WHAT)
FBX_TEX = os.environ.get('HANDFIT_FBX_TEX', os.path.join(os.path.dirname(FBX), 'textures'))
def fbx_tex(n='lambert1_Base_Color.png'):
    return _need('HANDFIT_FBX_TEX', 'The FBX textures folder (lambert1_Base_Color.png ...).', os.path.join(FBX_TEX, n))

GUNPACK = os.path.abspath(os.environ.get('RSQ_GUNPACK', os.path.join(DEPOT, 'tools', 'rig', 'build', 'src', 'bd22q_192', 'src')))
if not os.path.exists(os.path.join(GUNPACK, 'MODELDEF.bd.txt')):
    raise SystemExit('handfit_fbx: no MODELDEF.bd.txt in RSQ_GUNPACK=%s. Run sh tools/rig/setup.sh (it checks out tag 1.92 '
                     'of RS_Brutal22WeaponsQ there) or set RSQ_GUNPACK to an extracted pack folder.' % GUNPACK)

def ermac(rel):
    e = os.environ.get('RSQ_ERMAC')
    if not e:
        raise SystemExit("handfit_fbx: RSQ_ERMAC is not set. Point it at Ermac's doom-force-unleashed_devbuild/models/ "
                         "(hand/hand.md3, hand/hand2.md3: the calibration reference).")
    return _need('RSQ_ERMAC', "Ermac's models/ folder.", os.path.join(e, rel))

RIG = os.environ.get('B22_RIG', os.path.join(DEPOT, 'tools', 'rig', 'bin'))
RIGDIR = os.path.join(DEPOT, 'tools', 'rig')
def gamedata():
    return {k: _need(k, 'The owner\'s load order: B22_IWAD=doom2.wad, B22_BD22=brutal22test6.pk3, B22_VOX=BD_VoxelPack.pk3.')
            for k in ('B22_IWAD', 'B22_BD22', 'B22_VOX')}

def probe_pk3():
    """RIGOUT/probe.pk3 from probe192/ (the minimal 1.92 probe: logs LANEC T / LANEC FRAME and the B22 GUN tables);
    tools/rig/rig.py loads B22_BUILD/probe.pk3 after the pack. The Depot's own tools/rig/probe does not compile on 1.92."""
    import zipfile
    os.makedirs(RIGOUT, exist_ok=True); p = os.path.join(RIGOUT, 'probe.pk3'); src = os.path.join(TOOL, 'probe192')
    with zipfile.ZipFile(p, 'w', zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(src)):
            z.write(os.path.join(src, n), n)
    return p
