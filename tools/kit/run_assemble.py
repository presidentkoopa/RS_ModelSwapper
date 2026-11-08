"""Run the Depot's assemble.py decontamination over ModelSwapper's own runtime.

WHY THIS EXISTS

ModelSwapper's zscript_depot/ is RS_Brutal22WeaponsQ 1.96b's runtime copied in
whole -- hands.zs, vreload.zs, rsr_assist.zs and fists.zs are byte-identical to
that tree, checked. So it names Brutal Doom's own weapons (BrutalPistol, MG42,
PuristRifle, Devastator ...) and Brutal Doom's own modules (RSK_M203Handler,
RSG_Handler, RSQ_Dual, RSM, IsPlayingAsPurist) as if they were always loaded.
They are not, and the pack fails to compile: 51 of its 65 remaining script errors
are exactly that.

The VR reload was discovered inside BD22, so the runtime that proves it still
wears BD22's clothes. The owner's words, 2026-10-25: "this is why bd22 was baked
into our shit for so long ... ModelSwapper 2.0 needs to be liberated."

assemble.py IS the decontaminator and it was written for this. Nothing is
retyped here: its edit lists, its stub text and its stub_table() generator are
imported and applied. An edit whose text is not found aborts, which is the whole
point of the exact-match design -- it cannot drift silently.

DIVORCE FROM 1.96b (the owner, same day: "eventually we need to divorce from the
Runtime BD 196 source, keep that in mind")

This is a ONE-WAY pass. After it runs, zscript_depot/ no longer refers to any
BD22 class and ModelSwapper owns those files outright; the only remaining tie to
1.96b is historical -- that is the text the edits were written against. The right
end state is that this script is run once, its output is committed, and nothing
re-derives from 1.96b again. Re-running it on an already-stripped tree will abort
on the first edit it cannot find, which is the correct behaviour and the signal
that the divorce is done.

WHAT IS NOT DONE HERE
  RSQ_HandTable is replaced by assemble.py's stub -- Index 0 for every weapon, so
  the hands are present and unfitted. BD22's own hand table is useless to us: it
  matches on BD22's weapon classes. Fitting hands to OUR guns is handfit_cards.py
  (the Depot's own tool, with gripregions.json) and is a later pass, not a loss.

usage: python -B tools_kit/run_assemble.py [--dry-run]
"""
import os, shutil, sys

sys.path.insert(0, 'tools_kit')
sys.dont_write_bytecode = True
import assemble

ROOT = 'zscript_depot'
DRY = '--dry-run' in sys.argv


def edit_file(rel, edits, what):
    """assemble.apply_edits on one of our files. Aborts if an edit's text is gone."""
    p = os.path.join(ROOT, rel)
    t = open(p, encoding='utf-8', errors='replace').read()
    nl = '\r\n' if '\r\n' in t else '\n'
    flat = t.replace('\r\n', '\n')
    out = assemble.apply_edits(flat, edits, rel)        # raises SystemExit on a miss
    if not DRY:
        open(p, 'w', encoding='utf-8', newline='').write(out.replace('\n', nl))
    print('  %-26s %d edit(s): %s' % (rel, len(edits), what))


def write_file(rel, text, what):
    p = os.path.join(ROOT, rel)
    if not DRY:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8', newline='').write(text)
    print('  %-26s %s' % (rel, what))


def drop_file(rel, what):
    p = os.path.join(ROOT, rel)
    if os.path.exists(p) and not DRY:
        os.remove(p)
    print('  %-26s REMOVED: %s' % (rel, what))


def main():
    print('decontaminating %s (%s)' % (ROOT, 'DRY RUN' if DRY else 'writing'))
    # 1. the edited copies -- BD22's dual wield, grenade ring, M203, purist rifle,
    #    purist mode, and its own melee strike, cut by exact match
    edit_file('rsq/hands.zs', assemble.HANDS_EDITS, 'dual / grenade / M203 / purist rifle / punch')
    edit_file('rsr/vreload.zs', assemble.VRELOAD_EDITS, 'slide lock from the table; purist mode')
    edit_file('rsq/fists.zs', assemble.FISTS_EDITS, "the punch lands this pack's own strike")
    edit_file('rsr/rsr_assist.zs', assemble.ASSIST_EDITS, 'rocket capture/tilt by part length')
    # 2. the modules BD22 has and we do not: present and idle, from the 1.96b signatures
    write_file('rsq/stubs.zs', assemble.HOST_STUBS,
               'RSK_M203Handler / RSG_Handler / RSM stubs')
    # 3. BD22's hand table out, the stub in (see the header: hand fitting is its own pass)
    write_file('rsq/handtable.zs', assemble.HANDTABLE_STUB,
               "RSQ_HandTable stub (BD22's table matched BD22's classes)")
    # 4. BD21's Machinegun roster option: it belongs to the BD22 pack, not here
    drop_file('rsq/roster.zs', 'names BD21 Machinegun / MG42, both BD22-only')
    print('done.' if not DRY else 'dry run: nothing written.')


if __name__ == '__main__':
    main()
