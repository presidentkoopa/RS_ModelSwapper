# Heretic: VoidWalker (heretic-voidwalker) -- Ermac's mod, 8 weapons

Carded from the WELL's copy (owner, 2026-10-31: "make a choice"): the well is what ModelSwapper pulls from, so the
card describes the mesh that ships. Upstream is https://github.com/iAmErmac/heretic-voidwalker ; if the well is
refreshed from it, re-run the cards. GOLD set: every surface named by the artist.

Heretic weapons are magic: NOTHING RELOADS. What the meshes do move:

| weapon | mesh | moving parts (measured) |
|---|---|---|
| crossbow (Ethereal Crossbow) | xbow.md3 12f | `bow` limbs flex 6.7 / 16 deg on fire (frames 1..11); `bolts` (surf 0, 140 v) are the three loaded bolts: carved as `round` -- the only Heretic ammo a hand could seat, if we ever want it (arrow.md3 is the fired bolt, 4 frames) |
| staff (Combat Staff) | staff.md3 8f | bolt/cap/baton/cap2: the whole staff swings 52 units (melee); nothing moves relative to the shaft |
| gauntlet (Gauntlets of the Necromancer) | gauntlet.md3 3f | `glove` turns 21 deg on `arm` (the attack) |
| mace (Firemace) | mace.md3 1f + mace_cap.md3 + mace_spike.md3 (4f each) | cap and spike are SEPARATE meshes that extend 8..12 on fire |
| dragonclaw (Dragon Claw) | dragonclaw.md3 1f | bracer, two spikes, handle; animation is all flash meshes |
| phoenixrod | phoenixrod.md3 1f + crystal.md3 | still |
| skullrod (Hellstaff) | skullrod.md3 1f + horns.md3 | still |
| wand (Elven Wand) | wand.md3 1f + wand_crystal.md3 | still |

`_hands/`: Ermac's VERTEX HANDS as shipped with this set (claw_hand, mace_hand: 249 v, 1 frame = the grip pose;
xbow_hand 12f and staff_hand 9f = the hand animated WITH the weapon). These are the hands the owner first asked
for on the Aliens set; they are a measured grip reference for the capture tool later.

Holo bracer (holo_bracer_*.md3) is the off-hand HUD, not a weapon: not carded.
