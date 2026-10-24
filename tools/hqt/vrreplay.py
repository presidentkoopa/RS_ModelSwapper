#!/usr/bin/env python3
"""
vrreplay.py -- author a UZDXREMA hand-input replay in human units.

The engine's replay file (p_vrreplay.cpp, cvar vr_replay_play) is raw wire integers, one row
per tic. Nobody should write that by hand. This script takes a small script in map units and
degrees, with holds and linear moves, and writes the engine file.

    python3 vrreplay.py reload_pistol.txt reload_pistol.vrr

Source script, one command per line, '#' comments. State persists between lines.

    main pos F L U            main hand position: forward, left, up from the player's floor point (map units)
    main ang Y P R            main hand yaw (relative to player yaw), pitch, roll (degrees)
    off  pos F L U  /  off ang Y P R
    head Z P R                eye height above floor (map units), head pitch, roll
    grip main|off V           analog 0-255
    trigger main|off V
    thumb main|off X Y        -127..127
    bits main|off NAME...     VALID GRIP TRIGGER THUMBTOUCH INDEXTOUCH, or 'none'
    buttons NAME...           BT_ names without the prefix (RELOAD OFFHANDATTACK USE ...), or 'none'
    hold N                    emit the current state for N tics
    move main|off pos F L U over N      linearly move to the target over N tics, emitting each tic
    move main|off ang Y P R over N
    press NAME... for N       set those buttons for N tics, then clear them

Units match VKOpenXRDeviceMode::WriteHandCommand: positions x16 into int16, angles BAM16.
"""
import sys

BT = {
    "ATTACK": 1 << 0, "USE": 1 << 1, "JUMP": 1 << 2, "CROUCH": 1 << 3, "TURN180": 1 << 4,
    "ALTATTACK": 1 << 5, "RELOAD": 1 << 6, "ZOOM": 1 << 7, "SPEED": 1 << 8, "STRAFE": 1 << 9,
    "MOVERIGHT": 1 << 10, "MOVELEFT": 1 << 11, "BACK": 1 << 12, "FORWARD": 1 << 13,
    "RIGHT": 1 << 14, "LEFT": 1 << 15, "LOOKUP": 1 << 16, "LOOKDOWN": 1 << 17,
    "MOVEUP": 1 << 18, "MOVEDOWN": 1 << 19, "MAINHANDRELOAD": 1 << 20,
    "USER1": 1 << 21, "USER2": 1 << 22, "USER3": 1 << 23, "USER4": 1 << 24, "RUN": 1 << 25,
    "OFFHANDATTACK": 1 << 26, "OFFHANDALTATTACK": 1 << 27, "OFFHANDRELOAD": 1 << 28,
}
HB = {"VALID": 0x01, "GRIP": 0x02, "TRIGGER": 0x04, "THUMBTOUCH": 0x08, "INDEXTOUCH": 0x10}


def q16(v):
    return max(-32768, min(32767, int(round(v * 16.0))))


def bam16(deg):
    v = int(round(deg * 65536.0 / 360.0))
    v = ((v + 32768) % 65536) - 32768
    return v


class State:
    def __init__(self):
        self.pos = {"main": [0.0, 0.0, 0.0], "off": [0.0, 0.0, 0.0]}
        self.ang = {"main": [0.0, 0.0, 0.0], "off": [0.0, 0.0, 0.0]}
        self.head = [0.0, 0.0, 0.0]
        self.grip = {"main": 0, "off": 0}
        self.trigger = {"main": 0, "off": 0}
        self.bits = {"main": 0, "off": 0}
        self.thumb = {"main": [0, 0], "off": [0, 0]}
        self.buttons = 0

    def row(self):
        v = []
        for h in ("main", "off"):
            v += [q16(x) for x in self.pos[h]]
            v += [bam16(a) for a in self.ang[h]]
        v += [q16(self.head[0]), bam16(self.head[1]), bam16(self.head[2])]
        v += [self.grip["main"], self.grip["off"], self.trigger["main"], self.trigger["off"],
              self.bits["main"], self.bits["off"],
              self.thumb["main"][0], self.thumb["main"][1], self.thumb["off"][0], self.thumb["off"][1]]
        v += [self.buttons]
        return tuple(v)


def names(tokens, table, what):
    if len(tokens) == 1 and tokens[0].lower() == "none":
        return 0
    m = 0
    for t in tokens:
        key = t.upper().removeprefix("BT_").removeprefix("VRHB_")
        if key not in table:
            raise ValueError(f"unknown {what} '{t}'")
        m |= table[key]
    return m


def hand(tok):
    t = tok.lower()
    if t in ("main", "mainhand", "m"):
        return "main"
    if t in ("off", "offhand", "o"):
        return "off"
    raise ValueError(f"hand must be main or off, not '{tok}'")


def compile_script(lines):
    st = State()
    rows = []  # list of (rep, rowtuple), merged when identical

    def emit(n=1):
        r = st.row()
        if rows and rows[-1][1] == r:
            rows[-1] = (rows[-1][0] + n, r)
        else:
            rows.append((n, r))

    for ln, raw in enumerate(lines, 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        t = line.split()
        c = t[0].lower()
        try:
            if c in ("main", "off"):
                h = hand(c)
                if t[1] == "pos":
                    st.pos[h] = [float(x) for x in t[2:5]]
                elif t[1] == "ang":
                    st.ang[h] = [float(x) for x in t[2:5]]
                else:
                    raise ValueError("expected 'pos' or 'ang'")
            elif c == "head":
                st.head = [float(x) for x in t[1:4]]
            elif c == "grip":
                st.grip[hand(t[1])] = max(0, min(255, int(t[2])))
            elif c == "trigger":
                st.trigger[hand(t[1])] = max(0, min(255, int(t[2])))
            elif c == "thumb":
                st.thumb[hand(t[1])] = [max(-127, min(127, int(t[2]))), max(-127, min(127, int(t[3])))]
            elif c == "bits":
                st.bits[hand(t[1])] = names(t[2:], HB, "hand bit")
            elif c == "buttons":
                st.buttons = names(t[1:], BT, "button")
            elif c == "hold":
                emit(int(t[1]))
            elif c == "press":
                i = [x.lower() for x in t].index("for")
                saved = st.buttons
                st.buttons |= names(t[1:i], BT, "button")
                emit(int(t[i + 1]))
                st.buttons = saved
            elif c == "move":
                h = hand(t[1])
                kind = t[2]
                target = [float(x) for x in t[3:6]]
                if t[6].lower() != "over":
                    raise ValueError("expected 'over N'")
                n = int(t[7])
                src = list(st.pos[h] if kind == "pos" else st.ang[h])
                for k in range(1, n + 1):
                    cur = [a + (b - a) * k / n for a, b in zip(src, target)]
                    if kind == "pos":
                        st.pos[h] = cur
                    else:
                        st.ang[h] = cur
                    emit(1)
            else:
                raise ValueError(f"unknown command '{c}'")
        except (ValueError, IndexError) as e:
            sys.exit(f"{ln}: {e}\n    {raw.rstrip()}")
    return rows


def write(rows, out, src_name):
    total = sum(r for r, _ in rows)
    with open(out, "w") as f:
        f.write("# vrreplay 1\n")
        f.write(f"# authored by vrreplay.py from {src_name}: {len(rows)} rows, {total} tics\n")
        f.write("# rep  mh.fwd mh.left mh.up mh.yaw mh.pitch mh.roll  oh.fwd oh.left oh.up oh.yaw oh.pitch oh.roll"
                "  head.z head.pitch head.roll  grip0 grip1 trig0 trig1 bits0 bits1 thumb0 thumb1 thumb2 thumb3  buttons\n")
        for rep, r in rows:
            f.write(f"{rep}  " + " ".join(str(x) for x in r) + "\n")
    return len(rows), total


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    with open(sys.argv[1]) as f:
        rows = compile_script(f.readlines())
    n, total = write(rows, sys.argv[2], sys.argv[1])
    print(f"{sys.argv[2]}: {n} rows, {total} tics ({total / 35.0:.1f} s)")
