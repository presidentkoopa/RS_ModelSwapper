# aliens (E:\DOOMWork\VR_WeaponSetRebuild\Aliens-Eradication-VR-addon, the original A03), 2026-10-31

Every mesh here carries heavy baked hand sway (42 to 131 degrees). All numbers below are from the
stabilised copies; any tool reading the raw frames on this set reads nonsense.

| mesh | card | reload / action | eject | note |
|---|---|---|---|---|
| m4a3.md3 pistol | yes | mag out/in (well axis measured, 65 cm drop), slide 6.8 cm, hammer 62 deg, rack after reload | chamber+port written | the one gun whose numbers were already in a ModelSwapper card; they agree |
| m37a2.md3 shotgun | yes | pump 11.2 cm along the bore on FIRE frames (racks itself); one shell into the port at (7.05, 0, -0.1) frame 23 | shell path only | roles: 1=pump 3=shell |
| m41a.md3 pulse rifle | yes | mag out/in (77 cm drop); pump 14.2 cm frames 9..12 = THE GRENADE LAUNCHER'S ACTION, support hand pumps it (owner); bolt 7.7 cm on fire | chamber+port written | roles: 0=trigger 1=pump 3=bolt |
| m56.md3 smartgun | yes | mag drum slides back 33 cm after its latch swings 94 deg | none in mesh | OWNER (corrected): rear pistol grip UNUSED. Main hand = vertical bar under the receiver behind the drum (x -4..4, y -6..-10, z to -9.6). Support = horizontal handlebar on top forward of the drum (x 24..36, z 8..12, across y -6..+20) |
| m260b.md3 flamer | yes | fuel canister drops out and a fresh one rises, frames 5..12; nozzle tilts 17 deg on fire | n/a | |
| knife.md3 | grip only | one surface, no parts | n/a | 131 deg sway |
| satchel_charge.md3 | grip only | four surfaces, none move | n/a | throw/place is a gesture, not a part |
| mechloader.md3 | parts only | claws open frame 7 (in the body surface); cage and lamp mast separate | n/a | NO HANDS: the arms are the weapon (owner). Both arms one surface. |

Agrees with the earlier `_parts/SUMMARY.md` pass in the source folder (state-based) on every verdict.
