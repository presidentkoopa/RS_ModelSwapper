"""realplay.py -- the owner's real play, on the Quest rig (triage 2026-10-27, made a gate).

    python3 -B gate/realplay.py <pack.pk3> [Class,Class,...]      (Class=MS_Donor: that model picked on it)

doom2 -> brutal22test6 -> BD_VoxelPack -> the pack, the rig's own ini (shipped cvars), the AUTO picker
(no rs_fm_picks), the pack's own vrhand.zs with the rig's scripted off hand (gate/rtest) so reloads
finish. One engine per BD22 class: select, three single shots, a burst, fire it empty, the reload
button, the hands' reload, then three more shots. SSG / GrenadeLauncher (break-open after EVERY shot,
owner 2026-10-27): three cycles of one shot and the hands' break / load / close.

Asserts, from the engine's log:
  1 no take while selecting / ready / singles / burst with the magazine above 0
  2 one take and one magazine-out per real reload (a take that the mod refused never starts the hands)
  3 the gun fires again afterwards (its magazine count goes down after the hands gave it back)
  4 each reload sound once: no ModelSwapper reload sound (ms_reload_sounds 0, the default) and no
    sound name twice in one tic
  5 a class whose lifted MS_BD22_ model has a reload row wears a model with a row
"""
import os, re, sys, subprocess, time, signal, shutil
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import run_gate
RIG = run_gate.RIG
GD = run_gate.GD
CLASSES = ['BrutalPistol', 'Rifle', 'BrutalSMG', 'MP40', 'AssaultShotgun', 'Shot_Gun', 'SSG', 'Revolver',
           'GrenadeLauncher', 'Rocket_Launcher', 'RailGun', 'Plasma_Gun', 'Sniper', 'MG42', 'MiniGun',
           'FlameCannon', 'Flamethrower2', 'IncendiaryLauncher']
BREAK = {'SSG', 'GrenadeLauncher'}
PUMP = {'Shot_Gun'}
# a gun whose hands' reload is the break-open driver (rsb) but which fires a full cylinder first
CHAMBERS = {'Revolver'}
# the lifted model of each class (tools_kit/lift_bd22.py) -- assert 5 checks these wear a row
LIFTED = {'BrutalPistol': 'MS_BD22_Pistol', 'Rifle': 'MS_BD22_Rifle', 'BrutalSMG': 'MS_BD22_SMG', 'MP40': 'MS_BD22_MP40',
          'AssaultShotgun': 'MS_BD22_AssaultShotgun', 'Shot_Gun': 'MS_BD22_Shotgun', 'SSG': 'MS_BD22_SSG',
          'Revolver': 'MS_BD22_Revolver', 'GrenadeLauncher': 'MS_BD22_M79', 'Rocket_Launcher': 'MS_BD22_RocketLauncher',
          'RailGun': 'MS_BD22_RailGun', 'Plasma_Gun': 'MS_BD22_PlasmaGun'}


def has_row(donor):
    return donor and (run_gate.slot_of(donor) > 0 or run_gate.pump_slot(donor) > 0 or run_gate.break_slot(donor) > 0)


def script(g):
    if g in PUMP:
        return 'rsrtest_script 0; rsptest_script 1; rsptest_every 0'
    if g in BREAK or g in CHAMBERS:
        return 'rsrtest_script 0; rsbtest_script 1'
    return 'rsrtest_script 7'   # shipped rsr_grab_with 0: the off TRIGGER takes the magazine (and works a handle)


def run(pk3, g, pick=None):
    out = os.path.join(H, 'out', 'rp_' + g + ('_' + pick if pick else ''))
    shutil.rmtree(out, ignore_errors=True)
    ov, _tm = run_gate.build_aux(out, vr=True)
    ini = open(os.path.join(RIG, 'config', 'qzdoom.ini'), encoding='latin-1').read()
    open(os.path.join(out, 'gate.ini'), 'w', encoding='latin-1').write(ini)
    t = [(20, 'god; ms_join_trace 1; rsr_debug 1'), (40, 'take Rifle; take BrutalPistol; take Pistol'),
         (60, 'echo RP_GUN %s; give ammo; rsqt_gun %s; rsqt_empty 0' % (g, g)), (110, 'echo RP_SELECTED %s; ms_donor_main; %s' % (g, script(g)))]
    s = 130
    if g in BREAK:
        s += 70     # the SSG's first select animation is still playing at t130 (rig: cycle 0's shot did nothing)
        for k in range(3):
            # decision D: one shot, then the gun is held until the hands have broken / loaded / closed it.
            # A fire press while held must do nothing (RP_HOLDFIRE), and the next cycle's shot must fire.
            t += [(s, 'echo RP_BREAKSHOT %s %d; +attack' % (g, k)), (s + 6, '-attack'),
                  (s + 60, 'echo RP_HOLDFIRE %s %d; +attack' % (g, k)), (s + 66, '-attack'),
                  (s + 500, 'echo RP_CYCLEEND %s %d' % (g, k))]; s += 520
        s += 40
    else:
        for k in range(3):
            t += [(s, 'echo RP_SHOT %s %d; +attack' % (g, k)), (s + 3, '-attack')]; s += 35
        t += [(s, 'echo RP_BURST %s; +attack' % g), (s + 30, '-attack')]; s += 70
        t += [(s, 'echo RP_EMPTY %s; +attack' % g), (s + 200, '-attack')]; s += 230
        t += [(s, 'echo RP_RELOAD %s; +reload' % g), (s + 15, '-reload')]; s += 700
        for k in range(3):
            t += [(s, 'echo RP_AGAIN %s %d; +attack' % (g, k)), (s + 3, '-attack')]; s += 35
    t += [(s, 'echo GATE_END')]
    cmds, now = [], 0
    for w, c in sorted(t, key=lambda x: x[0]):
        if w > now:
            cmds.append('wait %d' % (w - now)); now = w
        cmds.append(c)
    cmds += ['wait 5', 'quit']
    log = os.path.join(out, 'engine.log')
    home = os.path.join(out, 'home'); os.makedirs(home, exist_ok=True)
    argv = [os.path.join(RIG, 'qz'), '-iwad', os.path.join(GD, 'doom2.wad'), '-file', os.path.join(GD, 'brutal22test6.pk3'),
            os.path.join(GD, 'BD_VoxelPack.pk3'), os.path.abspath(pk3), ov] + (
            # Class=Donor: the player's own pick from the menu (rs_fm_picks), as run_gate.py sets it
            ['+set', 'rs_fm_picks', '%s:%s:%d:%d' % ((g,) + run_gate.shelf_pick(pick) + (run_gate.shelf_pick(pick)[1],))] if pick else []) + [
            '-config', os.path.join(out, 'gate.ini'), '-nosound', '-nomusic', '+logfile', log, '-warp', '1', '+' + '; '.join(cmds)]
    env = dict(os.environ, HOME=home, QZ_SNDLOG='1')
    so = open(os.path.join(out, 'stdout.txt'), 'w')
    p = subprocess.Popen(['flock', '-o', '-x', '/home/claude/rig.lock'] + argv, cwd=RIG, env=env, stdout=so, stderr=subprocess.STDOUT, start_new_session=True)
    t0 = time.time()
    while p.poll() is None:
        time.sleep(2)
        lg = open(log, encoding='latin-1').read() if os.path.exists(log) else ''
        if re.search(r'Script error(?!, "BD_VoxelPack\.pk3:)|VM execution aborted', lg) or time.time() - t0 > 900:
            os.killpg(p.pid, signal.SIGKILL); break
    so.close()
    return judge(g, open(log, encoding='latin-1').read() if os.path.exists(log) else '')


def judge(g, text):
    phase, takes, magouts, gaveback = 'pre', [], [], []
    donor, pre_take, snd, ms_snd, fired_after = '', 0, {}, 0, False
    mag_back = None
    cyc, last_mag = [], None
    ready_loop_skip = 'its Reload label is its Ready loop' in text
    for l in text.splitlines():
        m = re.match(r'RP_(GUN|SELECTED|SHOT|BURST|EMPTY|RELOAD|AGAIN|BREAKSHOT|HOLDFIRE|CYCLEEND) ?(\S*) ?(\d*)', l)
        if m:
            phase = m.group(1)
            if phase == 'BREAKSHOT':
                cyc.append({'take': 0, 'back': 0, 'held_shot': False, 'shot': False, 'm0': last_mag})
            if phase in ('HOLDFIRE', 'CYCLEEND') and cyc:
                cyc[-1][phase] = cyc[-1]['back']     # gave back before the held press / by the cycle's end
            continue
        mm0 = re.match(r'AMMO t\d+ mag (\d+)', l)
        if mm0:
            prev_mag, last_mag = last_mag, int(mm0.group(1))
        if cyc and phase in ('BREAKSHOT', 'HOLDFIRE'):
            mm = re.match(r'AMMO t\d+ mag (\d+)', l)
            if mm:
                n, c0 = int(mm.group(1)), cyc[-1]
                if c0['m0'] is not None and n < c0['m0']:
                    if phase == 'HOLDFIRE' and c0['back'] == 0:
                        c0['held_shot'] = True   # fired while the hands still held it
                    elif phase == 'BREAKSHOT':
                        c0['shot'] = True
                c0['m0'] = n
        m = re.search(r'"ms_donor_main" is "(\w*)"', l)
        if m and phase == 'SELECTED':
            donor = m.group(1)
        m = re.match(r'AMMO t\d+ mag (\d+)', l)
        if m:
            n = int(m.group(1))
            if mag_back is not None and n < mag_back:
                fired_after = True
            if gaveback and mag_back is None:
                mag_back = n
            elif mag_back is not None:
                mag_back = min(mag_back, n) if n < mag_back else n
        if re.search(r'\[MSJOIN\] took %s\b|%s pump: took it' % (g, g), l):
            takes.append(phase)
            if cyc:
                cyc[-1]['take'] += 1
            if phase in ('GUN', 'SELECTED', 'SHOT', 'BURST'):
                pre_take += 1
        if re.search(r'rsr t\d+ gun \d+: IDLE -> EMPTY', l):
            magouts.append(phase)
        # the magazine / break join gives the gun back with "gave X back (hands finished"; the pump's
        # whole-tube hold with "pump: the hand pushed every shell" / "pump: the hand pumped"
        if re.search(r'\[MSJOIN\] gave %s back \(hands finished|\[MSJOIN\] %s pump: (the hand (pushed every shell|pumped) -- fire allowed|tube full or reserve empty)' % (g, g), l):
            gaveback.append(phase)
            if cyc:
                cyc[-1]['back'] += 1
            mag_back = None if not gaveback else mag_back
        if re.match(r'(rsr|rsb|rsp) t\d+ sound ', l):
            ms_snd += 1
        # the gun's sounds (started on the player) and ModelSwapper's reload actors; a world actor of
        # the mod's own (two BD22 casings landing in one tic) is not a reload sound played twice
        m = re.match(r'QZSND (\d+) (\S+) ch \d+ .* src (BDoomer|\w*Player\w*|RSR_\w+|RSB_\w+|RSP_\w+)\s*$', l)
        if m:
            k = (m.group(1), m.group(2)); snd[k] = snd.get(k, 0) + 1
    if g in BREAK:
        # D: every cycle = one shot that fired, exactly one take and one give-back, no shot while held,
        # and given back before the cycle ended (never stuck)
        fired_after = len(cyc) == 3 and all(c['take'] == 1 and c['back'] == 1 and not c['held_shot']
                                            and c.get('CYCLEEND') == 1 for c in cyc) \
            and all(c['shot'] for c in cyc[1:])
        for i, c in enumerate(cyc):
            print('  D %s cycle %d: shot fired %s, take %d, back %d, fired while held %s, given back by cycle end %s' % (
                g, i, c['shot'], c['take'], c['back'], c['held_shot'], c.get('CYCLEEND') == 1), flush=True)
    dup = [k for k, v in snd.items() if v > 1 and re.search(r'reload|clip|mag|shell|open|close|insert|load', k[1], re.I)]
    reloads = len(takes) - pre_take
    lifted = LIFTED.get(g)
    c = [
        ('no script error', not re.search(r'Script error(?!, "BD_VoxelPack\.pk3:)|VM execution aborted', text)),
        ('1 no early take', pre_take == 0),
        ('2 one take/magout', (reloads == len(magouts) and reloads == len(gaveback)) if g not in BREAK and g not in PUMP and g not in CHAMBERS else (reloads == len(gaveback))),
        ('3 fires again', fired_after or reloads == 0),
        ('4 sounds once', ms_snd == 0 and not dup),
        ('5 row model', (not lifted or not has_row(lifted)) or has_row(donor)),
        ('reached end', 'GATE_END' in text),
    ]
    return g, donor, has_row(donor), reloads, len(magouts), len(gaveback), ready_loop_skip, c, dup[:3]


if __name__ == '__main__':
    pk3 = sys.argv[1]
    guns = sys.argv[2].split(',') if len(sys.argv) > 2 else CLASSES
    bad = 0
    print('%-18s %-26s row takes magout back  %s' % ('class', 'model', '  '.join(n.split()[0] for n in ['err', '1', '2', '3', '4', '5', 'end'])))
    for g in guns:
        g, pick = (g.split('=') + [None])[:2]     # Class=Donor picks that model on the class
        g, d, r, n, mo, gb, rl, c, dup = run(pk3, g, pick)
        ok = all(x for _, x in c)
        bad += not ok
        # A run where the hands never took a part is not a hand reload, whatever the checks say
        # (round 5: Unmaker/Flamethrower2/MG42 printed PASS with 0 takes -- tests must match real play).
        verdict = ('PASS' if n > 0 else 'NOHAND') if ok else 'FAIL'
        print('%-18s %-26s %-3s %5d %6d %4d  %s  %s%s%s' % (g, d or '(none)', 'yes' if r else 'no', n, mo, gb,
              ' '.join('ok' if x else 'FAIL' for _, x in c), verdict,
              ' (Reload = Ready loop: no hand reload)' if rl else '', ' dup %s' % dup if dup else ''), flush=True)
    sys.exit(1 if bad else 0)
