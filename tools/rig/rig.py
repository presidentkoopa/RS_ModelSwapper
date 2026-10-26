"""TEST ONLY: drive bd22q in the owner's quest_test_rig (real QZD 17.3, OpenXR mode, poses from cvars).

Lives outside the depot and never ships. run(name, script) launches the load order the depot's
CLAUDE.md names -- doom2 -> brutal22test6 -> BD_VoxelPack -> the pack -- plus the test probe, with
one chained console script, and returns the log.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.environ.get('B22_BUILD', HERE + '/build')		# setup.sh builds everything here
RIG = os.environ.get('B22_RIG', B + '/rig' if os.path.exists(B + '/rig/qzdoom') else HERE + '/bin')	# bin/ = prebuilt
UP = '/mnt/user-data/uploads'				# where the cloud session had the owner's files
IWAD = os.environ.get('B22_IWAD', UP + '/DOOMWork/QZD17-engine/build/Release/doom2.wad')
BD22 = os.environ.get('B22_BD22', UP + '/DOOMWork/brutal22test6.pk3')
VOX = os.environ.get('B22_VOX', UP + '/Desktop/BD_VoxelPack.pk3')
PROBE = B + '/probe.pk3'
OUT = B + '/logs'
PK3 = os.environ.get('B22_PK3', B + '/BD22Q_now.pk3')

# gun frame (cm, F L U) -> stage pose for the OFF hand, oriented like the gun hand (pitch 30 = level
# after vr_weaponRotate -30), so the off hand's frame IS the gun's frame and OffDirInGun(axis) = axis.
RHAND = (0.25, 1.3, -0.3)

def lpose(F, L, U, pitch=30.0, yaw=0.0, roll=0.0):
    return '%.4f %.4f %.4f %.1f %.1f %.1f' % (RHAND[0] - L / 100.0, RHAND[1] + U / 100.0,
                                             RHAND[2] - F / 100.0, pitch, yaw, roll)

def run(name, script, secs=150, extra=()):
    os.makedirs(OUT, exist_ok=True)
    log = '%s/%s.log' % (OUT, name)
    for f in (log, log + '.out'):
        if os.path.exists(f):
            os.remove(f)
    files = [BD22, VOX, PK3] + ([] if os.environ.get('B22_NOPROBE') else [PROBE]) + list(extra)
    files = [os.path.abspath(f) for f in files]	# the engine runs from RIG, not from here
    for f in [IWAD] + files:
        if not os.path.exists(f):
            raise SystemExit('missing ' + f)
    cmd = ['timeout', str(secs), RIG + '/qz', '-iwad', IWAD, '-file'] + files + \
          ['-nosound', '-warp', '1', '-skill', '3', '+logfile', log, '+' + script]
    with open(log + '.out', 'w') as fo:
        rc = subprocess.run(cmd, stdout=fo, stderr=subprocess.STDOUT, cwd=RIG,
                            env=dict(os.environ, QZ_RES=os.environ.get('QZ_RES','200'), EGL_PLATFORM='surfaceless',
                                     LIBGL_ALWAYS_SOFTWARE='1')).returncode
    text = ''
    for f in (log, log + '.out'):
        if os.path.exists(f):
            text += open(f, errors='replace').read()
    return rc, text

if __name__ == '__main__':
    rc, t = run(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 150)
    print('rc', rc)
    print(t[-4000:])
