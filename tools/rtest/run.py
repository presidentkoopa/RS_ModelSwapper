"""rtest/run.py -- the behaviour harness, Linux: run a set's pk3 in the real playsim on the stock
qzd17.3 build with fake VR hands (fakehands.zs replaces zscript/rsvr/vrhand.zs through an overlay
pk3 loaded last) and the kit's scripted off hand (RSR_TestDriver), so a reload is EXERCISED.

    python3 run.py <pk3> <name> <timeout s> "T:console cmds" ...      [--pre file.pk3 ...]

Ported from RS_Aliens_Q tools/rtest (the Windows port of the kit's kit/team/integ/rtest).
Every run gets a fresh config copied from template.ini (the engine writes cvars back on quit).
"""
import os, sys, shutil, subprocess, zipfile, time

H = os.path.dirname(os.path.abspath(__file__))
ENG = '/home/claude/qgz/build'
IWAD = '/usr/share/games/doom/freedoom2.wad'
SCRATCH = '/home/claude/rtest/scratch'

CVARS = '''user int rsrtest_script = 0;
user bool rsr_test_offdraw = true;
user float rsr_test_yaw = 0;
user int rsbtest_script = 0;
user int rsbtest_chambers = 0;
user bool rsp_test_steady = false;
user bool rsp_test_trigger = false;
user int rsptest_script = 0;
user float rsptest_speed = 1.0;
user int rsptest_holds = 0;
user int rsptest_every = 0;
user int rsptest_casings = 1;
user string rsqt_gun = "";
user int rsqt_empty = 0;
user int rsqt_dbg = 0;
user int aet_buttons = 0;
'''


def overlay(path):
    body = '\n'.join(open(os.path.join(H, f)).read() for f in ('fakehands.zs', 'rsr_testdriver.zs', 'driver.zs'))
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('zscript/rsvr/vrhand.zs', body)       # the one lump the pack's ZSCRIPT includes
        z.writestr('CVARINFO.rtest', CVARS)
        z.writestr('MAPINFO.rtest', 'gameinfo { AddEventHandlers = "RSR_TestDriver", "RSQT_Driver" }\n')
    return path


def template_ini():
    """a config the engine itself wrote on a startup-only run: every cvar at its default"""
    p = os.path.join(H, 'template.ini')
    if os.path.exists(p):
        return p
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ, HOME=SCRATCH, LIBGL_ALWAYS_SOFTWARE='1')
    subprocess.run(['xvfb-run', '-a', '-s', '-screen 0 640x480x24 +extension GLX', os.path.join(ENG, 'qzdoom'),
                    '-iwad', IWAD, '-nosound', '-nomusic', '-config', p, '+vr_mode', '0', '+quit'],
                   cwd=ENG, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    return p


def run(pk3, name, tmo, specs, pre=()):
    os.makedirs(SCRATCH, exist_ok=True)
    ini = os.path.join(SCRATCH, name + '.ini')
    shutil.copy(template_ini(), ini)
    ov = overlay(os.path.join(SCRATCH, name + '_overlay.pk3'))
    log = os.path.join(SCRATCH, name + '.log')
    items = sorted((int(a.split(':', 1)[0]), a.split(':', 1)[1]) for a in specs)
    cmds, now = [], 0
    for t, c in items:
        if t > now:
            cmds.append('wait %d' % (t - now)); now = t
        cmds.append(c)
    cmds += ['wait 5', 'quit']
    files = []
    for f in list(pre) + [pk3, ov]:
        files += ['-file', f]
    argv = [os.path.join(ENG, 'qzdoom'), '-iwad', IWAD] + files + [
        '-config', ini, '-nosound', '-nomusic', '-width', '640', '-height', '480', '+vr_mode', '0', '+vid_preferbackend', '0', '+vid_fullscreen', '0', '+vid_rendermode', '4',
        '+rsr_debug', '1', '-warp', '1', '+' + '; '.join(cmds), '-stdout']
    env = dict(os.environ, HOME=SCRATCH, LIBGL_ALWAYS_SOFTWARE='1', GALLIUM_DRIVER='llvmpipe')
    with open(log, 'w') as out:
        try:
            subprocess.run(['xvfb-run', '-a', '-s', '-screen 0 640x480x24 +extension GLX', 'stdbuf', '-oL', '-eL'] + argv,
                           cwd=ENG, env=env, stdout=out, stderr=subprocess.STDOUT, timeout=tmo)
        except subprocess.TimeoutExpired:
            out.write('\n*** TIMEOUT %ds ***\n' % tmo)
    return log


if __name__ == '__main__':
    pk3, name, tmo = sys.argv[1], sys.argv[2], int(sys.argv[3])
    specs = [a for a in sys.argv[4:] if ':' in a and not a.startswith('--')]
    pre = [a for a in sys.argv[4:] if a.endswith('.pk3') and ':' not in a]
    print(run(pk3, name, tmo, specs, pre))
