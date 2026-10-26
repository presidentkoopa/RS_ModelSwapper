"""run_gate.py -- put one of our models on a foreign gun and reload it with scripted hands.

    python3 -B gate/run_gate.py <ModelSwapper-QUEST.pk3> <donor> [--engine DIR] [--shots]

Runs stock QuestZDoom 17.3 headless (xvfb, software GL, +vr_mode 0) with:
  * the pack under test;
  * gate/testmod -- TMPistol, a pistol written like any mod's: its own Reload state and its
    own ammo (TMMag in the gun, Clip in reserve). It is "their code";
  * an overlay of gate/rtest: fake VR hands (fakehands.zs stands in for vrhand.zs, so the
    hand code runs with vr_mode 0) and the kit's scripted off hand (rsr_testdriver.zs).

The model is picked on TMPistol through rs_fm_picks, the magazine is emptied, the trigger
pulled (the mod's own Fire jumps to its own Reload), and the hands do the rest.

PASS needs ALL of, read from the engine's own log:
  script parsing finished, no "Script error", the join took TMPistol at its reload,
  the reload walked EMPTY -> CARRY -> INSERT -> SEATED/DONE, the join handed it back,
  and the MOD'S OWN reload then ran and refilled ITS magazine ("TM reload: mag 12").
With --shots it also writes screenshots at each phase into gate/out/<donor>/, so what
was DRAWN can be looked at -- a log can say a magazine left the gun while nothing moved.
"""
import os, re, sys, shutil, subprocess, zipfile, glob

H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(H)
IWAD = '/usr/share/games/doom/freedoom2.wad'
# TEST VIEW ONLY. Models placed for a VR controller sit at the eye on a flat screen and are
# not drawn at all (BD22's guns: Offset 0). vr_3dweaponOffset is applied to EVERY HUD model,
# every layer alike (r_data/models.cpp, RenderHUDModel), so it moves the camera back without
# moving any layer relative to another -- which is the thing under test.
VIEW = 'vr_3dweaponOffsetX 10; vr_3dweaponOffsetY -4; vr_3dweaponOffsetZ -45'
EXTRA = ''
VR_CVARS = '''
user int rsrtest_vr = 1;
user string qzt_lhand = "";
user string qzt_rhand = "";
user float qzt_lgrip = -1;
user float qzt_ltrigger = -1;
'''
RIG = os.environ.get('QZ_RIG', '/home/claude/qzlinux17')   # Desktop/Quest_Weapons_Kit quest_test_rig, built

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


def shelf_pick(donor):
    """(archetype, index of the donor within its archetype's rows) from RS_ForeignModels.zs"""
    t = open(os.path.join(ROOT, 'zscript/RS_ForeignModels.zs'), encoding='utf-8').read()
    s = t[t.index('static const string SHELF[] = {'):]
    rows = re.findall(r'"([^"|]+)\|(MS_\w+)\|', s[:s.index('};')])
    arch = next(a for a, d in rows if d == donor)
    return arch, [d for a, d in rows if a == arch].index(donor)


def pump_slot(donor):
    t = open(os.path.join(ROOT, 'zscript_depot/rsr/rsr_pump_guns.zs'), encoding='utf-8').read()
    m = re.search(r'donor == "%s"\)\s*return (\d+);' % re.escape(donor), t)
    return int(m.group(1)) if m else 0


def has_handle(donor):
    t = open(os.path.join(ROOT, 'zscript_depot/rsr/rsr_guns.ms.zs'), encoding='utf-8').read()
    s = slot_of(donor)
    seg = t[t.find('static bool HasHandle(int i)'):]
    m = re.search(r'case %d:\s*return (\w+);' % s, seg[:seg.find('\n\t}')])
    return bool(m and m.group(1) == 'true')


def break_slot(donor):
    t = open(os.path.join(ROOT, 'zscript_depot/rsr/rsb_guns.zs'), encoding='utf-8').read()
    m = re.search(r'donor == "%s"\)\s*return (\d+);' % re.escape(donor), t)
    return int(m.group(1)) if m else 0


def slot_of(donor):
    """the reload slot RSR_Guns.SlotForDonor gives this donor -- the join prints it, so a
    matching number proves the WORN model is the one under test"""
    t = open(os.path.join(ROOT, 'zscript_depot/rsr/rsr_guns.ms.zs'), encoding='utf-8').read()
    m = re.search(r'donor == "%s"\)\s*return (\d+);' % re.escape(donor), t)
    return int(m.group(1)) if m else -1


def build_aux(out, vr=False):
    os.makedirs(out, exist_ok=True)
    ov = os.path.join(out, 'rtest_overlay.pk3')
    # --vr: the pack's OWN vrhand.zs (the engine's AttackPos / OffhandPos, real buttons), driven by
    # the rig's controllers; without it, the fake hands stand in for a headset
    hand = open(os.path.join(ROOT, 'zscript_depot/rsvr/vrhand.zs')).read() if vr else open(os.path.join(H, 'rtest', 'fakehands.zs')).read()
    body = '\n'.join([hand] + [open(os.path.join(H, 'rtest', f)).read() for f in ('rsr_testdriver.zs', 'driver.zs', 'pump_test.zs', 'break_test.zs')])
    with zipfile.ZipFile(ov, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('zscript_depot/rsvr/vrhand.zs', body)
        z.writestr('CVARINFO.rtest', CVARS + (VR_CVARS if vr else ''))
        z.writestr('MAPINFO.rtest', 'gameinfo { AddEventHandlers = "RSR_TestDriver", "RSQT_Driver", "RSP_TestDriver", "RSB_TestDriver" }\n')
    tm = os.path.join(out, 'testmod.pk3')
    with zipfile.ZipFile(tm, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(H, 'testmod', 'ZSCRIPT.txt'), 'ZSCRIPT.txt')
    return ov, tm


def run(pk3, donor, engine, shots, yaw=90, vr=False, shot=False):
    out = os.path.join(H, 'out', donor)
    if os.path.isdir(out):
        shutil.rmtree(out)
    ov, tm = build_aux(out, vr)
    arch, idx = shelf_pick(donor)
    home = os.path.join(out, 'home'); os.makedirs(home)
    exe = os.path.join(engine, 'qzdoom') if os.path.exists(os.path.join(engine, 'qzdoom')) else os.path.join(engine, 'gzdoom')
    pump = pump_slot(donor) > 0
    brk = not pump and break_slot(donor) > 0
    gun = 'TMShotgun' if pump else 'TMSSG' if brk else 'TMPistol'
    view = '' if vr else VIEW         # the flat-camera offset: off on the rig, which draws the real VR placement
    t = [(20, 'god; rsr_reload 1; rsr_grab_with 1; ms_join_trace 1; rsr_debug 1; rsr_test_yaw %d; %s%s' % (0 if vr else yaw, view, ('; ' + EXTRA) if EXTRA else '')),
         (25, 'netevent rs-fm-rescan'),
         (40, 'rsqt_gun %s; rsqt_empty 1' % gun)]
    # the rig renders slower than the game tics: a 3-tic tap can fall between its frames (kit README:
    # "a gesture must be held"), so on --vr the reload button is held for 15
    up = 130 if vr else 118
    if brk:
        t += [(110, 'rsrtest_script 0; rsbtest_script 1'), (115, '+reload'), (up, '-reload')]
    elif pump and shot:
        # --shot: the pump AFTER A SHOT. Loaded gun, the off hand steadied on the pump (script 2:
        # every pump a full stroke), one shot: the join must hold the mod's fire where the model's
        # pump starts, the hand works it, and the mod's own fire goes on from there.
        t[-1] = (40, 'rsqt_gun %s; rsqt_empty 0' % gun)
        t += [(110, 'rsrtest_script 0; rsptest_script 2; rsptest_every 0'), (130, '+attack'), (133 if not vr else 140, '-attack')]
    elif pump:
        t += [(110, 'rsrtest_script 0; rsptest_script 1; rsptest_every 0'), (115, '+reload'), (up, '-reload')]
    else:
        # a gun with a charging handle: the off TRIGGER grabs (rsr_grab_with 0, script 7). With
        # "grab with the grip" the grip on a handle is within the engine's steadying range, which
        # the reload's input rule says is steadying, never a grab -- the handle cannot be taken
        # that way at all (BD22Q's rule, unchanged; see the handoff)
        sc = 'rsr_grab_with 0; rsrtest_script 7' if has_handle(donor) else 'rsrtest_script 1'
        t += [(110, sc), (115, '+attack'), (125, '-attack')]
    end = 900 if pump else 520
    if shots:
        t += [(x, 'screenshot') for x in (100, 140, 170, 200, 230, 260, 300, 340, 400)]
    t += [(end, 'echo GATE_END')]
    cmds, now = [], 0
    for when, c in sorted(t):
        if when > now:
            cmds.append('wait %d' % (when - now)); now = when
        cmds.append(c)
    cmds += ['wait 5', 'quit']
    log = os.path.join(out, 'engine.log')
    # a build split across files (e.g. a 1of2 / 2of2-models pair) is given comma-separated, loaded in order
    argv = [exe, '-iwad', IWAD, '-file'] + [os.path.abspath(x) for x in pk3.split(',')] + [tm, ov,
            '-config', os.path.join(out, 'gate.ini'), '-nosound', '-nomusic', '-width', '640', '-height', '480',
            '+vid_fullscreen', '0', '+vr_mode', '0', '+vid_preferbackend', '0',
            '+set', 'rs_fm_picks', '%s:%s:%d:%d' % (gun, arch, idx, idx),
            '+screenshot_dir', out, '+logfile', log, '-warp', '1', '+' + '; '.join(cmds)]
    env = dict(os.environ, HOME=home, LIBGL_ALWAYS_SOFTWARE='1', GALLIUM_DRIVER='llvmpipe')
    launch = ['xvfb-run', '-a', '-s', '-screen 0 640x480x24 +extension GLX'] + argv
    if vr:
        # the Quest-faithful rig: its own ini (vr_mode 15, OpenXR device), without the BD22-only player
        # class; no desktop vid / vr_mode overrides; EGL surfaceless, so no X server
        ini = open(os.path.join(RIG, 'config', 'qzdoom.ini'), encoding='latin-1').read()
        ini = re.sub(r'^playerclass=.*$', 'playerclass=', ini, flags=re.M)
        open(os.path.join(out, 'gate.ini'), 'w', encoding='latin-1').write(ini)
        drop = {'+vid_fullscreen', '+vr_mode', '+vid_preferbackend'}
        a2, skip = [], 0
        for x in argv[1:]:
            if skip:
                skip -= 1; continue
            if x in drop:
                skip = 1; continue
            a2.append(x)
        if shots:
            a2 = ['+qz_hmd', os.environ.get('QZ_SHOT_HMD', '0 1.6 0 -40 0 0')] + a2   # head down at the hands, as a player looks
        launch = [os.path.join(RIG, 'qz')] + a2
    # A script error leaves the engine on its error screen until the timeout. Watch the log
    # and stop at the first one -- a failed compile is a FAIL in seconds, not ten minutes.
    import time
    so = open(os.path.join(out, 'stdout.txt'), 'w')
    p = subprocess.Popen(launch, cwd=RIG if vr else engine, env=env,
                         stdout=so, stderr=subprocess.STDOUT, start_new_session=True)
    t0 = time.time(); rc = None
    while rc is None:
        time.sleep(2)
        rc = p.poll()
        lg = open(log, encoding='latin-1').read() if os.path.exists(log) else ''
        if rc is None and (re.search(r'Script error|Execution could not continue|^\S+, line \d+: (?!.*[Ww]arning)', lg, re.M) or time.time() - t0 > 600):
            import signal
            os.killpg(p.pid, signal.SIGKILL)
            rc = 'KILLED (script error)' if 'rror' in lg else 'TIMEOUT'
    so.close()
    stdout = open(os.path.join(out, 'stdout.txt'), encoding='latin-1').read()
    text = (open(log, encoding='latin-1').read() if os.path.exists(log) else '') + stdout
    if brk:
        checks = [
            ('pack loaded', os.path.basename(pk3.split(',')[0]) in text),
            ('scripts parsed', 'script parsing took' in text),
            ('no script error', not re.search(r'Script error|Execution could not continue|VM execution aborted|^\S+, line \d+: (?!.*[Ww]arning)', text, re.M)),
            ('join took it', 'took TMSSG (break slot %d)' % break_slot(donor) in text),
            ('it opened', re.search(r'RSBT t\d+ phase 2', text) is not None),
            # on the rig the hand does it: the reload's own lines, a round CAUGHT by a chamber and
            # seated, and the shut by the gun hand's flick (no function of the reload is called)
            ('chambers seated', (len(re.findall(r'rsb t\d+ chamber \d+ loaded', text)) >= 1 and 'round at chamber' in text) if vr
                                else len(re.findall(r'RSBT t\d+ seated chamber', text)) >= 1),
            ('it closed', re.search(r'shut \(flick\)', text) is not None if vr else 'all chambers loaded: closing' in text),
            ('handed back', 'gave TMSSG back' in text),
            ('their reload ran', 'TM ssg: barrels 2' in text),
            ('reached the end', 'GATE_END' in text),
        ]
        print('donor %s  (%s #%d, break slot %d)  exit %s' % (donor, arch, idx, break_slot(donor), rc))
        for name, c in checks:
            print('  %-18s %s' % (name, 'ok' if c else 'FAIL'))
        for l in text.splitlines():
            if re.search(r'Script error|MSJOIN|TM ssg|RSBT|rsb t\d+', l):
                print('   |', l[:150])
        ok = all(c for _, c in checks)
        print('PASS' if ok else 'FAIL', '-- log', log)
        return 0 if ok else 1
    if pump and shot:
        logtext = open(log, encoding='latin-1').read() if os.path.exists(log) else stdout
        held = logtext.find('held for its stroke')
        checks = [
            ('pack loaded', os.path.basename(pk3.split(',')[0]) in text),
            ('scripts parsed', 'script parsing took' in text),
            ('no script error', not re.search(r'Script error|Execution could not continue|VM execution aborted|^\S+, line \d+: (?!.*[Ww]arning)', text, re.M)),
            ('it fired', 'TM shotgun: fired' in logtext),
            ('pump point found', 'pump point: tic' in logtext),
            ('held for the hand', held >= 0),
            ('pumped by hand', 'pumped by hand -- the mod\'s fire goes on' in logtext),
            ('their fire went on', held >= 0 and logtext.find('TM shotgun: its own pump done', held) > held),
            ('reached the end', 'GATE_END' in text),
        ]
        print('donor %s  (%s #%d, pump slot %d)  exit %s  -- the pump after a shot' % (donor, arch, idx, pump_slot(donor), rc))
        for name, c in checks:
            print('  %-18s %s' % (name, 'ok' if c else 'FAIL'))
        for l in logtext.splitlines():
            if re.search(r'Script error|MSJOIN|TM shotgun|rsp t\d+', l):
                print('   |', l[:150])
        ok = all(c for _, c in checks)
        print('PASS' if ok else 'FAIL', '-- log', log)
        return 0 if ok else 1
    if pump:
        # the engine echoes its log to stdout too: count the log alone, or every shell counts twice
        logtext = open(log, encoding='latin-1').read() if os.path.exists(log) else stdout
        shells = len(re.findall(r'TM shotgun: a shell in', logtext))
        checks = [
            ('pack loaded', os.path.basename(pk3.split(',')[0]) in text),
            ('scripts parsed', 'script parsing took' in text),
            ('no script error', not re.search(r'Script error|Execution could not continue|VM execution aborted|^\S+, line \d+: (?!.*[Ww]arning)', text, re.M)),
            ('join took it', 'TMShotgun pump: took it at its reload' in text),
            ('hand fed shells', 'a shell pushed home' in text),
            ('their loop ran', shells >= 2),
            ('re-held per shell', 'a shell in -- held for the next' in text),
            ('tube filled', re.search(r'tube full or reserve empty|reload done, tube 8', text) is not None),
            ('reached the end', 'GATE_END' in text),
        ]
        print('donor %s  (%s #%d, pump slot %d)  exit %s  -- %d shells by the mod\'s own loop' % (donor, arch, idx, pump_slot(donor), rc, shells))
        for name, c in checks:
            print('  %-18s %s' % (name, 'ok' if c else 'FAIL'))
        for l in text.splitlines():
            if re.search(r'Script error|MSJOIN|TM shotgun|rsp t\d+', l):
                print('   |', l[:150])
        ok = all(c for _, c in checks)
        print('PASS' if ok else 'FAIL', '-- log', log)
        return 0 if ok else 1
    checks = [
        ('pack loaded', os.path.basename(pk3.split(',')[0]) in text),
        ('scripts parsed', 'script parsing took' in text),
        ('no script error', not re.search(r'Script error|Execution could not continue|VM execution aborted|^\S+, line \d+: (?!.*[Ww]arning)', text, re.M)),
        ('join took it', 'took TMPistol' in text),
        ('as this model', 'took TMPistol (slot %d)' % slot_of(donor) in text),
        ('magazine out', re.search(r'gun \d+: \w+ -> EMPTY', text) is not None),
        ('carried', re.search(r'-> CARRY', text) is not None),
        ('inserted', re.search(r'-> INSERT', text) is not None),
        ('seated', re.search(r'-> (SEATED|DONE)', text) is not None),
        # shot dry (rsqt_empty), a gun with a charging handle must ask the hand to work it
        ('handle racked', re.search(r'PULL -> RELEASED', text) is not None if has_handle(donor) else True),
        ('handed back', 'gave TMPistol back' in text or re.search(r'\[MSJOIN\].*back', text) is not None),
        ('their reload ran', 'TM reload: mag 12' in text),
        ('reached the end', 'GATE_END' in text),
    ]
    ok = all(c for _, c in checks)
    print('donor %s  (%s #%d)  exit %s' % (donor, arch, idx, rc))
    for name, c in checks:
        print('  %-18s %s' % (name, 'ok' if c else 'FAIL'))
    for l in text.splitlines():
        if re.search(r'Script error|error|rsr t\d+: gun|MSJOIN|TM reload|no magazine', l, re.I):
            print('   |', l[:160])
    print('PASS' if ok else 'FAIL', '-- log', log)
    return 0 if ok else 1


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    eng = next((sys.argv[i + 1] for i, x in enumerate(sys.argv) if x == '--engine'), '/home/claude/engine/qzd/build')
    a = [x for x in a if x != eng]
    opt = lambda k, d: next((sys.argv[i + 1] for i, x in enumerate(sys.argv) if x == k), d)
    VIEW = opt('--view', VIEW)
    EXTRA = opt('--extra', '')
    a = [x for x in a if x not in (opt('--view', None), opt('--yaw', None), opt('--extra', None))]
    sys.exit(run(a[0], a[1], eng, '--shots' in sys.argv, int(opt('--yaw', 60)), vr='--vr' in sys.argv, shot='--shot' in sys.argv))
