"""depot.py: where everything is. Every tool in tools/ finds its inputs here.

Each path is relative to this repository, or comes from an environment variable. Nothing points at a
folder outside the repo unless you set the variable. The names, defaults and meanings are listed in
docs/handbook/03_toolset.md ("Paths").
"""
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(TOOLS)


def _env(name, default):
    v = os.environ.get(name)
    return os.path.abspath(v if v else default)


# the set being worked on (its src/, its hand-fit data). Default: BD22 VR Weapons Q.
SET = _env('RSQ_SET', os.path.join(DEPOT, 'sets', 'bd22q'))
SRC = _env('RSQ_SRC', os.path.join(SET, 'src'))
POSES = _env('RSQ_POSES', os.path.join(SET, 'handfit', 'poses'))		# solved hand poses as data
FITS = _env('RSQ_FITS_DIR', os.path.join(SET, 'handfit', 'fits'))		# fit records, bakes, port logs

# the test rig (QuestZDoom 17.3). The engine binary is chosen by rig.py (B22_RIG, else tools/rig/bin).
RIG = os.path.join(TOOLS, 'rig')

# the hand-fitter core: its code (hands_tool) and the measured data it reads (one folder up from the code)
CORE = _env('RSQ_HANDS_LANE', os.path.join(TOOLS, 'handfit', 'core'))
HANDS_TOOL = _env('RSQ_HANDS_TOOL', os.path.join(CORE, 'hands_tool'))
# BD22Q 1.92, the owner's reference holds: an extracted pack (MODELDEF.bd.txt + models/).
# sh tools/rig/setup.sh checks out tag 1.92 here.
GUNPACK192 = _env('RSQ_GUNPACK', os.path.join(RIG, 'build', 'src', 'bd22q_192', 'src'))

# game data and the rig lock: the owner's files, never committed
GAMEDATA = _env('RSQ_GAMEDATA', os.path.join(DEPOT, '..', 'gamedata'))	# doom2.wad, brutal22test6.pk3, BD_VoxelPack.pk3
LOCK = _env('RSQ_RIGLOCK', os.path.join(DEPOT, '..', 'rig.lock'))		# one engine at a time: flock -o -x

# run output (gitignored): logs, frame dumps, sheets, scratch packs
WORK = _env('RSQ_WORK', os.path.join(DEPOT, 'work'))

# outside inputs that are never committed (licence or size). Empty = not set: the tool that needs one says so.
FBX = os.environ.get('RSQ_FBX', '')				# hand_final.fbx (unknown licence: never commit it)
FBX_TEX = os.environ.get('RSQ_FBX_TEX', '') or (os.path.join(os.path.dirname(FBX), 'textures') if FBX else '')
ERMAC = os.environ.get('RSQ_ERMAC', '')			# Ermac's doom-force-unleashed_devbuild/models (hand/, ammo_hand/)
DOOMWORK = os.environ.get('RSQ_DOOMWORK', '')		# the owner's E:\DOOMWork (REMA, RS_VR_Reload): history tools only
MODELSWAPPER = _env('RSQ_MODELSWAPPER', os.path.join(DEPOT, '..', 'rs_modelswapper'))


def need(path, what):
    """Stop with a clear message when an outside input is not set or not there."""
    if not path or not os.path.exists(path):
        raise SystemExit('%s not found (%r). Set the environment variable named in docs/handbook/03_toolset.md, "Paths".'
                         % (what, path))
    return path


def gp192(path):
    """A mesh path recorded against the 1.92 pack ('bd22q_192/models/...') -> the file in GUNPACK192."""
    if 'bd22q_192/' in path:
        return os.path.join(GUNPACK192, path.split('bd22q_192/', 1)[1])
    return path
