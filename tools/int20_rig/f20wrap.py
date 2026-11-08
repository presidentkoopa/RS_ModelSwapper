"""TEST ONLY (2.0 final): run a rig tool with the lane's fresh default ini copied in before EVERY engine run (inside the
tool's own rig.lock hold), on the lane's rig binary copy, with the shared lock $RSQ_RIGLOCK.
f20wrap.py <ini> <script.py> [args...]"""
import os as _dpo, sys as _dps; _dps.path.append(_dpo.path.normpath(_dpo.path.join(_dpo.path.dirname(_dpo.path.abspath(__file__)), '..'))); import depot as _DP	# Depot paths (tools/depot.py)
import os, sys, shutil, runpy
S = _DP.WORK; GD = _DP.GAMEDATA
INI = os.path.abspath(sys.argv[1])
os.environ.update(B22_RIG=S + '/int20_rig/bin', B22_IWAD=GD + '/doom2.wad', B22_BD22=GD + '/brutal22test6.pk3', B22_VOX=GD + '/BD_VoxelPack.pk3',
                  RSQ_RIGLOCK=_DP.LOCK, RSQ_GAMEDATA=GD, RSQ_DEPOT=_DP.DEPOT)
if os.environ.get('SCOPE_OUT'): os.environ['B22_BUILD'] = os.environ['SCOPE_OUT']
if not os.path.exists(S + '/int20_rig/bin/qzdoom'):	# a private copy of the rig, so the ini copied in never touches tools/rig/bin
    os.makedirs(S + '/int20_rig', exist_ok=True); shutil.copytree(_DP.RIG + '/bin', S + '/int20_rig/bin'); shutil.copy(_DP.RIG + '/PINS', S + '/int20_rig/PINS')
sys.path.insert(0, _DP.RIG); import rig
_run = rig.run
def run(*a, **k):
    rig.PK3 = os.environ.get('B22_PK3', rig.PK3)	# drive.py sets the env after rig is imported
    shutil.copy(INI, rig.RIG + '/config/qzdoom.ini'); return _run(*a, **k)
rig.run = run
sys.argv = sys.argv[2:]; sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
runpy.run_path(sys.argv[0], run_name='__main__')
