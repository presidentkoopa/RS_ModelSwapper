"""assemble.py -- put the Quest reload runtime into a genpack build directory.

Nothing here is written from memory: every runtime file is COPIED from the owner's BD22 Quest pack 1.96b
and changed only by exact-match edits listed below (an edit whose text is not found aborts).
The per-set tables (RSR_Guns, weapons, MODELDEF) come from genpack.py; the hand/pump/break
tables that this pass does not generate are stubs built from the SOURCE signatures, so the
interface cannot drift.

usage: python3 assemble.py <build dir> <set name>
"""
import os, re, sys, shutil, json

# OUR COPY. The Depot's assemble.py is read-only and its SRC is the Linux path the
# original ran from. The same 1.96b tree is on this machine, and our zscript_depot/
# copies of hands.zs, vreload.zs, rsr_assist.zs and fists.zs are BYTE-IDENTICAL to it,
# so every exact-match edit below was written against exactly this text and applies.
SRC = 'E:/DOOMWork/_buildtemp/rs_brutal22weaponsq/src'           # RS_Brutal22WeaponsQ 1.96b
ZS = SRC + '/zscript'
TOOLDIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------------------------
# exact-match edits. (file, [(old, new, why), ...])

HANDS_EDITS = [
    # Upkeep: the dual-wield "stale copy" check needs rsq/dual.zs, which this edition does not carry
    ("""		let off = p.OffhandWeapon;
		bool stale = off && !(off is 'RSQ_Hands')
			&& RSQ_Dual.CopyIndex(off) != RSQ_Dual.GunIndex(p.ReadyWeapon);
		if (h && (!off || stale) && p.PendingWeapon == WP_NOCHANGE)
			p.PendingWeapon = h;""",
     """		let off = p.OffhandWeapon;
		if (h && !off && p.PendingWeapon == WP_NOCHANGE)
			p.PendingWeapon = h;""", "no dual wield module"),
    # the VR grenade's ring hand (rsg/grenade.zs) is not carried
    ("""		if (rsr == "" && mo.CountInv('RSG_RingHand') > 0)
			rsr = "RsgRing";				// the VR grenade's ring, pinched (rsg/grenade.zs)
""", "", "no grenade module"),
    # BD22's purist rifle (index 18): a class this edition never sees
    ("""		if (i == 18 && p.ReadyWeapon is 'PuristRifle')
			sp = "B";		// 1.30: purist's rifle has no launcher: its handguard grip as before
		else if (i == 18 && RSK_M203Handler.TriggerGrip(mo))""",
     """		if (i == 18 && RSK_M203Handler.TriggerGrip(mo))""", "no BD22 purist rifle"),
    ("""		if (!gunHand && i == 18 && !(o.ReadyWeapon is 'PuristRifle') && RSK_M203Handler.TriggerGrip(Owner))""",
     """		if (!gunHand && i == 18 && RSK_M203Handler.TriggerGrip(Owner))""", "no BD22 purist rifle"),
    ("""		if (!gunHand && i == 18 && o.ReadyWeapon is 'PuristRifle')
		{
			hook = (-0.090, -1.390, 11.380);	// 1.30: purist's rifle (no launcher): the handguard grip as before
			hookTurn = (0, 0, 0);
		}
""", "", "no BD22 purist rifle"),
    # the off-hand punch lands OUR strike (BD22's MeleeStrikeNormal is not here)
    ("""			Name sn = mo.CountInv('PowerStrength') > 0 ? 'MeleeStrike1Berserked' : 'MeleeStrikeNormal';
			class<Actor> sc = RSQ_Fists.Cls(sn);
			let a = sc ? Actor.Spawn(sc, RSVR_VRHand.OffPos(mo), ALLOW_REPLACE) : null;""",
     """			Name sn = mo.CountInv('PowerStrength') > 0 ? 'WMQ_PunchBerserk' : 'WMQ_Punch';
			class<Actor> sc = RSQ_Fists.Cls(sn);
			let a = sc ? Actor.Spawn(sc, RSVR_VRHand.OffPos(mo), ALLOW_REPLACE) : null;""", "punch strike: this pack's own"),
]

FISTS_EDITS = [
    ("""		Name sn = mo.CountInv('PowerStrength') > 0 ? 'MeleeStrike1Berserked' : 'MeleeStrikeNormal';
		class<Actor> sc = RSQ_Fists.Cls(sn);
		if (!sc)
			return;""",
     """		Name sn = mo.CountInv('PowerStrength') > 0 ? 'WMQ_PunchBerserk' : 'WMQ_Punch';
		class<Actor> sc = RSQ_Fists.Cls(sn);
		if (!sc)
			return;""", "punch strike: this pack's own"),
]

HANDS_CUT_METHODS = []

VRELOAD_EDITS = [
    # the slide / bolt lock was tied to BD22's table indexes; the generated table says which guns lock
    ("""		if ((i == 1 || i == 2 || i == 3 || i == 5) && psp)""",
     """		if (RSR_Guns.SlideLock(i) && psp)""", "slide lock from the table, not BD22 indexes"),
    # BD22's purist mode
    ("""		// 1.10 (owner): BD22's purist mode has no reloading by design; ours stays out of it too.
		// One gate for all three (magazine, pump, break-open: they all ask here).
		if (mo.CountInv('IsPlayingAsPurist') > 0)
			return false;
""", "", "no BD22 purist mode"),
]

ASSIST_EDITS = [
    # BD22 Rocket_Launcher was Mag index 9; a long part's wider capture is now asked of the table
    ("""		double b = CAPTURE;
		switch (i)
		{
		// BD22 Rocket_Launcher: a 22 cm rocket held near its tail, its nose 18.9 cm from
		// the hand (RSR_Guns.TopInHand 9). The lever arm turns a radius into a wrist angle,
		// so this one needs more of it than a magazine held in the middle of the fist.
		case 9:	b = 12.0; break;
		}
		return R(p, b);""",
     """		double b = CAPTURE;
		// a long part held near its tail (a rocket: its top 12+ cm from the hand): the lever arm
		// turns a radius into a wrist angle, so it needs more of it than a magazine in the fist
		if (RSR_Guns.TopInHand(i).Length() > 12.0)
			b = 12.0;
		return R(p, b);""", "rocket capture by part length, not BD22 index"),
    ("""		double b = TILT;
		switch (i)
		{
		case 9:	b = 70.0; break;		// BD22 Rocket_Launcher: it goes in across the gun, an awkward wrist
		}
		return A(p, b);""",
     """		double b = TILT;
		if (RSR_Guns.TopInHand(i).Length() > 12.0)
			b = 70.0;		// a long part goes in across the gun: an awkward wrist
		return A(p, b);""", "rocket tilt by part length, not BD22 index"),
]


def apply_edits(text, edits, fname):
    for old, new, why in edits:
        n = text.count(old)
        if n != 1:
            raise SystemExit('assemble: %s: edit "%s" matched %d times, expected 1' % (fname, why, n))
        text = text.replace(old, new)
    return text


def cut_method(text, sig, fname):
    """remove a method (and the comment lines directly above it) from a class body"""
    i = text.find('\t' + sig)
    if i < 0:
        raise SystemExit('assemble: %s: method not found: %s' % (fname, sig))
    # back up over the comment block above it
    start = i
    while True:
        prev = text.rfind('\n', 0, start - 1)
        line = text[prev + 1:start]
        if line.strip().startswith('//'):
            start = prev + 1
        else:
            break
    # forward to the matching closing brace at one tab
    j = text.find('\n\t}\n', i)
    if j < 0:
        raise SystemExit('assemble: %s: no end for %s' % (fname, sig))
    end = j + len('\n\t}\n')
    # swallow one blank line after
    if text[end:end + 1] == '\n':
        end += 1
    return text[:start] + text[end:]


# ---------------------------------------------------------------------------------------------
# stubs from source signatures

SIG = re.compile(r'^\t(?:clearscope )?static ([^\n(]+?) (\w+)\(([^)]*)\)\s*(\{[^\n]*\}\s*)?$', re.M)
ZERO = {'int': '0', 'double': '0', 'bool': 'false', 'Vector3': '(0, 0, 0)', 'Vector2': '(0, 0)',
        'String': '""', 'Name': "'None'"}


def zero(t):
    t = t.strip()
    if t.startswith('class<'):
        return 'null'
    if t not in ZERO:
        raise SystemExit('assemble: no zero for type ' + t)
    return ZERO[t]


def stub_table(src_path, cls, note, index_zero=True):
    """an abstract table class with every static function of the source's, returning zeros"""
    text = open(src_path).read()
    m = re.search(r'^class %s abstract\b.*?\n\{\n(.*?)\n\}\n' % cls, text, re.S | re.M)
    if not m:
        raise SystemExit('assemble: class %s not found in %s' % (cls, src_path))
    body = m.group(1)
    out = ['// %s: %s' % (cls, note), '// Every function the runtime calls, from the pack 1.92 source signatures; Index is 0 for',
           '// every weapon, so the module is present and idle.', 'class %s abstract' % cls, '{']
    seen = set()
    for mm in SIG.finditer(body):
        rtype, name, args = mm.group(1), mm.group(2), mm.group(3)
        if name in seen:
            continue
        seen.add(name)
        rets = [zero(t) for t in rtype.split(',')]
        out.append('\tclearscope static %s %s(%s) { return %s; }' % (rtype.strip(), name, args, ', '.join(rets)))
    out.append('}')
    return '\n'.join(out) + '\n', sorted(seen)


HANDTABLE_STUB = """// RSQ_HandTable: no hands fitted yet in this set (hand fitting is its own pass). Every
// function the runtime calls, with Index 0 for every weapon.
class RSQ_HandTable abstract
{
	clearscope static int Index(Weapon w) { return 0; }
	clearscope static String GunOne(int i) { return ""; }
	clearscope static String GunTwo(int i) { return ""; }
	clearscope static String Support(int i) { return ""; }
	clearscope static Vector3 GunHook(int i) { return (0, 0, 0); }
	clearscope static Vector3 GunRot(int i) { return (0, 0, 0); }
	clearscope static Vector3 SupportHook(int i) { return (0, 0, 0); }
	clearscope static Vector3 SupportRot(int i) { return (0, 0, 0); }
	clearscope static Vector3 SupportPoint(int i) { return (0, 0, 0); }
	clearscope static String Trigger(int i) { return ""; }
	clearscope static Vector3 GunHookTwo(int i) { return (0, 0, 0); }
	clearscope static Vector3 GunRotTwo(int i) { return (0, 0, 0); }
}
"""

GUNMOVES_STUB = """// RSQ_GunMoves: no recoil-in-mesh tables yet for this set (rsq_gunmoves_gen.py is a later pass).
// The hands ride the gun layer's offset only.
class RSQ_GunMoves abstract play
{
	clearscope static Vector3 Pivot(int i) { return (0, 0, 0); }
	clearscope static bool Mirrored(int i) { return false; }
	clearscope static bool Blends(int i) { return false; }
	static Vector3, Vector3 Frame(int i, int sprite, int frame) { return (0, 0, 0), (0, 0, 0); }
}
"""

# the host-mod modules the reload asks about (rsr_m203.zs, rsg/grenade.zs): present and idle.
# Signatures copied from the source call sites listed in assemble's check below.
HOST_STUBS = """// Modules of the BD22 pack this edition does not carry. The reload modules and hands.zs ask
// these; each answers "not busy, nothing to place".
class RSK_M203Handler abstract
{
	clearscope static bool Busy(int n) { return false; }
	clearscope static String FreeHand(PlayerPawn mo) { return ""; }
	clearscope static bool TriggerGrip(Actor mo) { return false; }
	clearscope static Vector3 SupportShift(Actor owner, double ticfrac) { return (0, 0, 0); }
	clearscope static bool Places(Actor owner, int layer) { return false; }
	clearscope static Vector3, Vector3 Place(Actor owner, Vector3 translation, Vector3 rotation, int layer, double ticfrac) { return translation, rotation; }
}

class RSG_Handler abstract
{
	clearscope static bool WantsGrab(int n) { return false; }
}

// rsr_m203.zs's layer range (hands.zs RSQ_Layers.Taken reads it): values from that file, 1.96b
class RSM abstract
{
	const LAYER_FIRST = 2130;
	const LAYER_LAST = 2131;
}
"""

ZSCRIPT_LUMP = """version "4.10"

// RS Quest VR weapons -- %(set)s set. Generated by c2q/genpack.py + assemble.py from the
// RS_VR_Weapons cards. Runtime: RS_Brutal22WeaponsQ 1.96b, in its own include order, minus the
// BD22-only modules (ballistics, dual, flick, alts, casings, voxels, M203, grenade, nosniper).
#include "zscript/rsvr/vrhand.zs"
#include "zscript/rsvr/melee.zs"
#include "zscript/rsq/handler.zs"
#include "zscript/rsq/handtable.zs"
#include "zscript/rsq/gunmoves.zs"
#include "zscript/rsq/hands.zs"
#include "zscript/rsq/fists.zs"
#include "zscript/rsq/fistmoves.zs"
#include "zscript/rsq/scope.zs"
#include "zscript/rsq/scope_real.zs"
#include "zscript/rsq/stubs.zs"
#include "zscript/rsr/rsr_assist.zs"
#include "zscript/rsr/vreload.zs"
#include "zscript/rsr/rsb_guns.zs"
#include "zscript/rsr/rsr_break.zs"
#include "zscript/rsr/rsr_guns.zs"
#include "zscript/rsr/rsr_pump.zs"
#include "zscript/rsr/rsr_pump_guns.zs"
#include "zscript/wmq/weapons.zs"
"""

MAPINFO_LUMP = """// RS Quest VR weapons: hands and the real VR reload
gameinfo
{
	AddEventHandlers = "RSVR_MeleeHandler", "RSQ_Handler", "RSR_ReloadHandler", "RSB_Handler", "RSP_Handler", "RSQ_Fists", "RSQ_ScopeReal"
}
"""

CVARINFO_LUMP = """// RS Quest VR weapons. Options: RSQ_Options (MENUDEF).
user bool rsq_hands = true;			// VR hands on the controllers (Ermac's hands and poses, models/rsq)
user int rsr_reload = 1;			// Reloading: 1 VR (on the guns that have it; the rest stock), 0 stock
user int rsr_grab_with = 0;			// Grab ammo with: 0 off trigger, 1 off grip, 2 Use key (only while a reload has the hand)

// real VR reload (zscript/rsr/vreload.zs)
user string rsr_grip_keys = "443 436";	// key codes that are the off-hand grip: 443 KEY_PAD_RTHUMB, 436 KEY_PAD_DPAD_UP
user int rsr_grab_buttons = 67108864;	// usercmd buttons that grab anywhere: BT_OFFHANDATTACK (off-hand trigger); 0 = none
user int rsr_magrelease = 268435456;	// usercmd buttons that drop the magazine: BT_OFFHANDRELOAD; the gun's own reload always does
user int rsr_pouch = 0;				// where a new magazine is taken: 0 anywhere 20 cm from the gun, 1 low (40 cm below the eyes)
user bool rsr_eat_grip = true;		// while a reload has the off hand, its grip key does nothing else
user bool rsr_debug = false;		// print every key code pressed, and each reload step
user bool rsr_freecharge = false;	// take the charging handle / slide with no reload running (a press check)
user float rsr_assist = 1.0;		// reload assist: one number scales every capture radius and tolerance
user bool rsr_assist_debug = false;	// draw the capture zones as rings
user int rsr_shell_credit = 1;		// pump shotguns: how many shells one pushed home counts as, 1 to 4

// break-open guns (zscript/rsr/rsr_break.zs) and pumps (rsr_pump.zs)
user float rsb_flick_speed = 450;	// deg/s: a turn of the gun hand the way the action closes, this fast, snaps it shut
user int rsr_ssg_pair = 1;			// a double-barrel takes two shells at once when both barrels are empty
user int rsr_sideport = 1;			// a pump gun takes a shell at its ejection port too
user bool rsr_test_offdraw = false;	// pump test aid

// punching (zscript/rsq/fists.zs): a real punch with either fist lands; punches work switches
user int rsq_punch = 1;
user bool rsq_punch_use = true;

// VR scopes (zscript/rsq/scope.zs): per gun, 0 dot / 1 real; a gun joins through RSQ_ScopeTable
user int rsq_scope_sniper = 0;
user int rsq_scope_railgun = 0;
"""
CVARINFO_LUMP += open(SRC + '/CVARINFO.rsvr', encoding='latin-1').read()      # melee: verbatim 1.96b


# THE MENU STANDARD (owner, 2026-10-24; from docs/RS_Quest_LOAD_ORDER.md "The options menu" and the
# 1.96b BD22 menu). One page, Options -> RS VR Weapons, the SAME rows in every pack, owned by the
# runtime; a set adds its own rows to that page with AddOptionMenu "RSQ_Options" (one block per
# set), never a page of its own. Cvar prefixes: rsq_ common/hands, rsr_ reload, rsb_/rsp_ break/pump,
# rsvr_ melee, rsa_ alt fires, rsq_scope_<gun>. No StaticText help. Debug rows stay in the menu
# because a console is no use with a headset on.
MENUDEF_LUMP = """// RS VR Weapons: the shared options page (menu standard: tools/README.md). Every pack defines
// the same page; a set adds its own rows below with AddOptionMenu "RSQ_Options".
AddOptionMenu "OptionsMenu"
{
	Submenu "RS VR Weapons", "RSQ_Options"
}

OptionValue "RSR_ReloadMode"
{
	1, "VR"
	0, "Stock"
}

OptionValue "RSR_GrabWith"
{
	0, "Off-hand trigger"
	1, "Off-hand grip"
	2, "Use key"
}

OptionValue "RSR_Pouch"
{
	0, "Anywhere, 20 cm from the gun"
	1, "Low, 40 cm below the eyes"
}

OptionValue "RSR_ShellCredit"
{
	1, "1"
	2, "2"
	3, "3"
	4, "4"
}

OptionValue "RSQ_ScopeMode"
{
	0, "Dot"
	1, "Real"
}

OptionMenu "RSQ_Options"
{
	Title "RS VR WEAPONS"
	Option "VR Hands", "rsq_hands", "OnOff"
	Option "Reloading", "rsr_reload", "RSR_ReloadMode"
	Option "Grab ammo with", "rsr_grab_with", "RSR_GrabWith"
	Option "New magazine from", "rsr_pouch", "RSR_Pouch"
	Option "Check the Chamber by Hand", "rsr_freecharge", "OnOff"
	Option "Shotgun Shells Per Insert", "rsr_shell_credit", "RSR_ShellCredit"
	Slider "Reload Assist", "rsr_assist", 0.5, 3.0, 0.25, 2
	StaticText " "
	Option "VR Punching", "rsq_punch", "OnOff"
	Option "Punch Switches Open", "rsq_punch_use", "OnOff"
	Slider "Melee Swing Strength", "rsvr_melee_swing", 0.5, 2.0, 0.1, 1
	StaticText " "
	Submenu "Reload: Tuning and Debug", "RSR_Debug"
}

OptionMenu "RSR_Debug"
{
	Title "RELOAD: TUNING AND DEBUG"
	Slider "Reload Assist", "rsr_assist", 0.5, 3.0, 0.25, 2
	Option "Show the Capture Zones", "rsr_assist_debug", "OnOff"
	Option "Print Each Reload Step", "rsr_debug", "OnOff"
}
"""

# a set's own rows, appended to the shared page (genpack writes MENUDEF.set with these when a set has any)
SET_MENU = """// %(title)s: this set's own rows on the shared RS VR Weapons page
AddOptionMenu "RSQ_Options"
{
	StaticText " "
	StaticText "%(title)s"
%(rows)s}
"""


def hands_modeldef():
    """the hand blocks of the pack's MODELDEF.rsq / .rsr / .rsb / .rsrpump, copied: every Model block
    whose Path is models/rsq and whose model is one of the three hand meshes (no ring, no debris)"""
    out = ['// RS VR hands (zscript/rsq/hands.zs). Hands and poses: Ermac, Force Unleashed / Rusted Legacy',
           '// (models/rsq/LICENSE_RustedLegacy_MIT.txt). Blocks copied from the pack 1.92 MODELDEFs by assemble.py.']
    want = ('"hand.md3"', '"hand2.md3"', '"ammo_hand.md3"', '"rsq_dot.md3"')
    for lump in ('MODELDEF.rsq', 'MODELDEF.rsr', 'MODELDEF.rsb', 'MODELDEF.rsrpump'):
        text = open(os.path.join(SRC, lump), encoding='latin-1').read()
        for m in re.finditer(r'((?://[^\n]*\n)*)Model\s+(\w+)\s*\n\{(.*?)\n\}', text, re.S):
            body = m.group(3)
            if 'Path "models/rsq"' not in body or not any(w in body for w in want) or 'Model 1' in body:
                continue
            out += ['', (m.group(1) or '').rstrip('\n'), 'Model %s' % m.group(2), '{' + body, '}']
    return '\n'.join(l for l in out if l is not None) + '\n'


def common_zs():
    """RSVR_Token and RSVR_Buzz, copied out of melee.zs"""
    text = open(ZS + '/rsvr/melee.zs').read()
    out = ['// RSVR_Token and RSVR_Buzz, copied from pack 1.92 zscript/rsvr/melee.zs (the melee module itself',
           '// is not carried). The reload modules give tokens of these and spawn the buzz for haptics.', '']
    for cls in ('class RSVR_Token : Inventory', 'class RSVR_Buzz : Actor'):
        i = text.find(cls)
        if i < 0:
            raise SystemExit('assemble: melee.zs: ' + cls + ' not found')
        # include the comment line above RSVR_Buzz
        start = i
        prev = text.rfind('\n', 0, start - 1)
        if text[prev + 1:start].strip().startswith('//'):
            start = prev + 1
        j = text.find('\n}\n', i)
        out.append(text[start:j + 3])
    return '\n'.join(out)


def main(build, setname):
    report = {'set': setname, 'edits': [], 'stubs': {}}
    os.makedirs(build + '/zscript/rsvr', exist_ok=True)
    os.makedirs(build + '/zscript/rsq', exist_ok=True)
    os.makedirs(build + '/zscript/rsr', exist_ok=True)

    # verbatim copies
    for rel in ('rsvr/vrhand.zs', 'rsvr/melee.zs', 'rsq/handler.zs', 'rsq/fistmoves.zs', 'rsq/scope.zs', 'rsq/scope_real.zs',
                'rsr/rsr_break.zs', 'rsr/rsr_pump.zs'):
        shutil.copy(ZS + '/' + rel, build + '/zscript/' + rel)
        report['edits'].append((rel, 'verbatim'))

    # edited copies
    t = open(ZS + '/rsq/hands.zs').read()
    t = apply_edits(t, HANDS_EDITS, 'hands.zs')
    open(build + '/zscript/rsq/hands.zs', 'w').write(t)
    report['edits'].append(('rsq/hands.zs', [e[2] for e in HANDS_EDITS]))
    t = apply_edits(open(ZS + '/rsq/fists.zs').read(), FISTS_EDITS, 'fists.zs')
    open(build + '/zscript/rsq/fists.zs', 'w').write(t)
    report['edits'].append(('rsq/fists.zs', [e[2] for e in FISTS_EDITS]))

    t = open(ZS + '/rsr/vreload.zs').read()
    t = apply_edits(t, VRELOAD_EDITS, 'vreload.zs')
    open(build + '/zscript/rsr/vreload.zs', 'w').write(t)
    report['edits'].append(('rsr/vreload.zs', [e[2] for e in VRELOAD_EDITS]))

    t = open(ZS + '/rsr/rsr_assist.zs').read()
    t = apply_edits(t, ASSIST_EDITS, 'rsr_assist.zs')
    open(build + '/zscript/rsr/rsr_assist.zs', 'w').write(t)
    report['edits'].append(('rsr/rsr_assist.zs', [e[2] for e in ASSIST_EDITS]))

    # stubs from source signatures
    rsb, names = stub_table(ZS + '/rsr/rsb_guns.zs', 'RSB_Guns', 'no break-open guns generated in this pass')
    # rsb_guns.zs also declares the sprites actor and Held items the module names
    rsb += '\nclass RSB_Sprites : Actor { States { Spawn: TNT1 A -1; Stop; } }\n'
    open(build + '/zscript/rsr/rsb_guns.zs', 'w').write(rsb)
    report['stubs']['RSB_Guns'] = names
    rsp, names = stub_table(ZS + '/rsr/rsr_pump_guns.zs', 'RSP_Guns', 'no pump guns generated in this pass')
    open(build + '/zscript/rsr/rsr_pump_guns.zs', 'w').write(rsp)
    report['stubs']['RSP_Guns'] = names
    open(build + '/zscript/rsq/handtable.zs', 'w').write(HANDTABLE_STUB)
    open(build + '/zscript/rsq/gunmoves.zs', 'w').write(GUNMOVES_STUB)
    open(build + '/zscript/rsq/stubs.zs', 'w').write(HOST_STUBS)
    if os.path.exists(build + '/zscript/rsvr/common.zs'):
        os.remove(build + '/zscript/rsvr/common.zs')

    # Ermac's hands: the shipped meshes and the hand MODELDEF blocks (gun poses + trigger frames,
    # support poses, the free hand, and the reload holds the rsr / rsb / pump MODELDEFs add)
    hands_src = SRC + '/models/rsq'
    os.makedirs(build + '/models/rsq', exist_ok=True)
    os.makedirs(build + '/sprites', exist_ok=True)
    for f in ('hand.md3', 'hand2.md3', 'ammo_hand.md3', 'hand.png', 'LICENSE_RustedLegacy_MIT.txt', 'rsq_dot.md3', 'RQRTA0.png', 'RQRTB0.png'):
        shutil.copy(os.path.join(hands_src, f), build + '/models/rsq/' + f)
    for f in ('RQRTA0.png', 'RQRTB0.png'):
        shutil.copy(os.path.join(SRC, 'sprites', f), build + '/sprites/' + f)
    shutil.copy(SRC + '/ANIMDEFS.rsq', build + '/ANIMDEFS.txt')     # the scope's camera texture
    open(build + '/MODELDEF.rsq', 'w').write(hands_modeldef())
    report['edits'].append(('MODELDEF.rsq', 'pack 1.92 hand blocks: RSQ_GunSide (hand.md3, hand2.md3, fist, ammo hand), RSQ_Hands free hand; '
                            'reload holds RQHN I (rsr), J L (rsb), RQUN A (pump); grenade ring and debris blocks left out'))
    # lumps
    open(build + '/ZSCRIPT.txt', 'w').write(ZSCRIPT_LUMP % dict(set=setname))
    open(build + '/MAPINFO.txt', 'w').write(MAPINFO_LUMP)
    open(build + '/CVARINFO.txt', 'w').write(CVARINFO_LUMP)
    open(build + '/MENUDEF.txt', 'w').write(MENUDEF_LUMP)

    report['sprites_without_models'] = {
        'hand states of modules not carried (grenade ring, M203, BD22 fist / grenade holds)': ['RQHR', 'RQ2H', 'RQ2S'],
        'pump module internals (no pump guns generated yet)': ['RQUG', 'RQUH', 'RQUP', 'RQUQ', 'RQUW', 'RQUX'],
        'break module internals (no break-open guns generated yet)': ['RBSP'],
        'axe lock-on ring: 1.96b itself ships no RQLK lump (flagged to the owner 2026-10-24)': ['RQLK']}
    json.dump(report, open(build + '/assemble_report.json', 'w'), indent=1)
    print('assembled', build)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
