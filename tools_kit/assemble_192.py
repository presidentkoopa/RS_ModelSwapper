"""assemble.py -- put the Quest reload runtime into a genpack build directory.

Nothing here is written from memory: every runtime file is COPIED from the pack 1.92 source
and changed only by exact-match edits listed below (an edit whose text is not found aborts).
The per-set tables (RSR_Guns, weapons, MODELDEF) come from genpack.py; the hand/pump/break
tables that this pass does not generate are stubs built from the SOURCE signatures, so the
interface cannot drift.

usage: python3 assemble.py <build dir> <set name>
"""
import os, re, sys, shutil, json

SRC = '/mnt/user-data/uploads/Quest_Weapons_Kit/pack_1.92_source/pack_1.92_source/src'
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
    # fists / grenade in the gun hand (OwnHand needs BD22 sprites and rsq/fists.zs)
    ("""		String own = on ? invoker.OwnHand(p) : "";
		invoker.showOwn = own != "";
		if (own != "")
			i = 0;
		// 1.5: the main fist follows BD22's punch frames (jab, cross, uppercut)
		invoker.fistMeshPrev = invoker.fistMesh;
		invoker.fistMesh = own == "Fist" ? invoker.FistFrame(p) : 0;
""", """		String own = "";
		invoker.showOwn = false;
""", "no fists module"),
    # the free hand: no punching here, so it is open, not a fist
    ("""		bool nade = p.ReadyWeapon && p.ReadyWeapon.GetClassName() == 'HandGrenades';
		String fh = !on || hold ? "Hidden" : rsr != "" ? rsr : carry == 0 && !nade ? "AmmoH" : ammo[clamp(carry, 0, 7)];
		invoker.freeFist = fh == "AmmoH";
		invoker.OffPunch(mo);
""", """		String fh = !on || hold ? "Hidden" : rsr != "" ? rsr : ammo[clamp(carry, 0, 7)];
		invoker.freeFist = false;
""", "no fists module: open free hand"),
    # BD22 rifle (index 18) special cases: purist rifle, M203 trigger grip
    ("""		if (i == 18 && p.ReadyWeapon is 'PuristRifle')
			sp = "B";		// 1.30: purist's rifle has no launcher: its handguard grip as before
		else if (i == 18 && RSK_M203Handler.TriggerGrip(mo))
			sp = (p.cmd.buttons & BT_OFFHANDATTACK) ? "M2" : "M1";	// 1.31: finger on the M203's trigger (squeezed)
""", "", "BD22 rifle special cases"),
    ("""		if (!gunHand && i == 18 && !(o.ReadyWeapon is 'PuristRifle') && RSK_M203Handler.TriggerGrip(Owner))
		{
			hook = (0, 0, 0);		// 1.31: the trigger grip is baked in place (MODELDEF.rsm RQ2S)
			hookTurn = (0, 0, 0);
		}
		if (!gunHand && i == 18 && o.ReadyWeapon is 'PuristRifle')
		{
			hook = (-0.090, -1.390, 11.380);	// 1.30: purist's rifle (no launcher): the handguard grip as before
			hookTurn = (0, 0, 0);
		}
""", "", "BD22 rifle special cases"),
    # the axe's two-hand regrip token lives in melee.zs
    ("""		bool two = Owner && Owner.CountInv('RSVR_AxeTwo') > 0;""",
     """		bool two = false;""", "no melee module"),
    # the off-hand trigger punch and the fist's punch motion
    ("""			if (offMesh > 0 || offMeshPrev > 0)	// 1.5: the off-hand trigger punch
			{
				Vector3 ft, fm;
				[ft, fm] = FistMove(offMeshPrev, offMesh, ticfrac);
				return translation + fm, rotation + ft;
			}
""", "", "no fists module"),
    ("""		if (layer == RSQ_Layers.GUNHAND && showOwn && (fistMesh > 0 || fistMeshPrev > 0))
		{
			Vector3 ft, fm;
			[ft, fm] = FistMove(fistMeshPrev, fistMesh, ticfrac);
			return translation + fm, rotation + ft;
		}
""", "", "no fists module"),
    # the off-hand slot: no fist weapon to swap back to
    ("""		Weapon.UseRange 48;
		Tag "Fist";
		Weapon.SlotNumber 1;	// 1.5: selectable in the OFF hand (slot 1), so a gun moved there can be swapped back for the fist
""", """		Tag "Free hand";
""", "no fists"),
]

# whole methods cut out of hands.zs (they only serve the fists / grenade / punch)
HANDS_CUT_METHODS = ['String OwnHand(PlayerInfo p)', 'int FistFrame(PlayerInfo p)',
                     'void OffPunch(PlayerPawn mo)', 'ui static Vector3, Vector3 FistMove(int prev, int cur, double ticfrac)']

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
"""

ZSCRIPT_LUMP = """version "4.10"

// RS Quest VR weapons -- %(set)s set. Generated by c2q/genpack.py + assemble.py from the
// RS_VR_Weapons cards. Runtime: the pack 1.92 reload modules, host-mod pieces cut.
#include "zscript/rsvr/vrhand.zs"
#include "zscript/rsvr/common.zs"
#include "zscript/rsq/handler.zs"
#include "zscript/rsq/handtable.zs"
#include "zscript/rsq/gunmoves.zs"
#include "zscript/rsq/hands.zs"
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
	AddEventHandlers = "RSQ_Handler", "RSR_ReloadHandler", "RSB_Handler", "RSP_Handler"
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
"""

MENUDEF_LUMP = """// RS Quest VR weapons: options
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

OptionMenu "RSQ_Options"
{
	Title "RS VR WEAPONS"
	Option "VR Hands", "rsq_hands", "OnOff"
	Option "Reloading", "rsr_reload", "RSR_ReloadMode"
	Option "Grab ammo with", "rsr_grab_with", "RSR_GrabWith"
	Option "Check the Chamber by Hand", "rsr_freecharge", "OnOff"
	Option "Shotgun Shells Per Insert", "rsr_shell_credit", "RSR_ShellCredit"
	Option "New magazine from", "rsr_pouch", "RSR_Pouch"
	Slider "Reload assist", "rsr_assist", 0.5, 3.0, 0.25, 2
	StaticText " "
	Submenu "Reload: tuning and debug", "RSR_Debug"
}

OptionMenu "RSR_Debug"
{
	Title "RELOAD: TUNING AND DEBUG"
	Option "Show the capture zones", "rsr_assist_debug", "OnOff"
	Option "Print each reload step", "rsr_debug", "OnOff"
}
"""


def hands_modeldef():
    """the hand blocks of the pack's MODELDEF.rsq / .rsr / .rsb / .rsrpump, copied: every Model block
    whose Path is models/rsq and whose model is one of the three hand meshes (no ring, no debris)"""
    out = ['// RS VR hands (zscript/rsq/hands.zs). Hands and poses: Ermac, Force Unleashed / Rusted Legacy',
           '// (models/rsq/LICENSE_RustedLegacy_MIT.txt). Blocks copied from the pack 1.92 MODELDEFs by assemble.py.']
    want = ('"hand.md3"', '"hand2.md3"', '"ammo_hand.md3"')
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
    for rel in ('rsvr/vrhand.zs', 'rsq/handler.zs', 'rsr/rsr_break.zs', 'rsr/rsr_pump.zs'):
        shutil.copy(ZS + '/' + rel, build + '/zscript/' + rel)
        report['edits'].append((rel, 'verbatim'))

    # edited copies
    t = open(ZS + '/rsq/hands.zs').read()
    t = apply_edits(t, HANDS_EDITS, 'hands.zs')
    for sig in HANDS_CUT_METHODS:
        t = cut_method(t, sig, 'hands.zs')
    t = t.replace('// RS VR hands for BD22 and Vanilla VR Plus on QuestZDoom 17.x.',
                  '// RS VR hands on QuestZDoom 17.x (pack 1.92 hands.zs, fists / grenade / dual / M203 cut by assemble.py).')
    open(build + '/zscript/rsq/hands.zs', 'w').write(t)
    report['edits'].append(('rsq/hands.zs', [e[2] for e in HANDS_EDITS] + ['cut ' + s for s in HANDS_CUT_METHODS]))

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
    open(build + '/zscript/rsvr/common.zs', 'w').write(common_zs())

    # Ermac's hands: the shipped meshes and the hand MODELDEF blocks (gun poses + trigger frames,
    # support poses, the free hand, and the reload holds the rsr / rsb / pump MODELDEFs add)
    hands_src = '/mnt/user-data/uploads/Quest_Weapons_Kit/hands/shipped_current'
    os.makedirs(build + '/models/rsq', exist_ok=True)
    for f in ('hand.md3', 'hand2.md3', 'ammo_hand.md3', 'hand.png', 'LICENSE_RustedLegacy_MIT.txt'):
        shutil.copy(os.path.join(hands_src, f), build + '/models/rsq/' + f)
    open(build + '/MODELDEF.rsq', 'w').write(hands_modeldef())
    report['edits'].append(('MODELDEF.rsq', 'pack 1.92 hand blocks: RSQ_GunSide (hand.md3, hand2.md3, fist, ammo hand), RSQ_Hands free hand; '
                            'reload holds RQHN I (rsr), J L (rsb), RQUN A (pump); grenade ring and debris blocks left out'))
    # lumps
    open(build + '/ZSCRIPT.txt', 'w').write(ZSCRIPT_LUMP % dict(set=setname))
    open(build + '/MAPINFO.txt', 'w').write(MAPINFO_LUMP)
    open(build + '/CVARINFO.txt', 'w').write(CVARINFO_LUMP)
    open(build + '/MENUDEF.txt', 'w').write(MENUDEF_LUMP)

    report['sprites_without_models'] = {
        'hand states of modules not carried (grenade ring, M203)': ['RQHR', 'RQ2H', 'RQ2S'],
        'pump module internals (no pump guns generated yet)': ['RQUG', 'RQUH', 'RQUP', 'RQUQ', 'RQUW', 'RQUX'],
        'break module internals (no break-open guns generated yet)': ['RBSP']}
    json.dump(report, open(build + '/assemble_report.json', 'w'), indent=1)
    print('assembled', build)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
