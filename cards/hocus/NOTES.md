# Hocus Pocus Doom VR (Hocus-Doom-VR) -- Ermac's mod; carded from the well's copy (upstream iAmErmac/Hocus-Doom-VR)

THE WEIRD THING (owner: "right away you'll see something weird there"): the fists weapon IS a pair of hands.
`hocus.md3` / `hocuspocus.md3` / `throw.md3` / `toss.md3` are full left+right HAND MESHES (veirdo's XARP Hexen
hand, 899 v per hand, ring on each middle finger as its own surface + a reflection surface), animated as the
spell-cast: hands open, fingers spread, the toss over 17 frames. `hocus_fire.md3` is the flame rig on the hand.
MODELDEF masks hand_left with no_hand.png for the one-hand option. Nothing to reload, nothing to grip: the
"weapon" is the player's own hands. Kept in `_hands/` next to Voidwalker's `_hands/`: a THIRD hand source, and
the only one with an articulated open-hand/throw animation. CREDITS.txt header still says "Robocop Weapons mod"
(copy-paste from Ermac's Robocop VR).

The four real guns, all magic, NOTHING RELOADS:
| gun | mesh | parts |
|---|---|---|
| blaster (Tribes Vengeance blaster remix) | blaster.md3 6f | `plasma` (324 v) = the glowing cell, still; body recoils 6 |
| cannon (fairy shooter) | cannon.md3 6f, 28 polySurfaces that all move as one (recoil 22) | no parts |
| rifle (Ark rifle mechanicus = Electro Gun) | rifle.md3 4f, 4 planes, recoil 7 | no parts |
| wand (arcane staff) | wand.md3 13f (`staff` 243 v) + wand_crystal.md3 (crystal + orb, 18f) + wand_crystal_big.md3 (25f) + phoenix.md3 (body + wing, 43 units of flap) as SEPARATE meshes | no parts; the crystal/orbs/phoenix are the mod's own effect meshes, copied into the wand folder |

HoloSight: SKIPPED (owner, 2026-10-31).
