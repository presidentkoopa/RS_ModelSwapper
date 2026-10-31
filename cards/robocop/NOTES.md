# Robocop Retribution VR (Robocop-Retribution) -- Ermac's mod, carded from the well's copy

GOLD: artist-named surfaces on every gun.

| gun | mesh | reload | parts |
|---|---|---|---|
| m32 (grenade launcher) | m32.md3 37f | YES: the revolver cylinder `magazine` + `magazine_back` (surfs 2+5) swings out sideways (+Y, 39 units) frames ~18..27; carved as ONE mag; trigger_plate, trigger_guard, two brackets, trigger named | archetype revolver; sheet_top.png shows the swing |
| auto9 | auto9.md3 12f, ONE surface | YES by carve: magazine base plate (the nub under the grip) carved as mag (25 tris); auto9.txt has a Reload state; no separable slide | |
| ksg (bullpup pump) | ksg.md3 5f | pump: `front` (2949 v) is the slide forend; `barrel`, `trigger` named; `back` = body | no shell geometry; shells would come from the runtime |
| shotgun | shotgun.md3 9f | `pump` named (256 v), 15.8 travel in the fire frames | |
| cobra (Cobra assault cannon) | cobra.md3 4f + cobra_scope.md3 | no; `cobra_barrel` recoils 28.8, two bipod `leg`s, trigger; scope is its own mesh (5 surfaces incl. glass + view) -- a live-scope candidate | |
| chaingun (Tribes Vengeance) | chaingun.md3 6f | no; barrels (left+right) spin 9.3 | |
| m27 (Skynet plasma rifle) | m27_rifle.md3 2f, 9 named surfaces | no | trigger only |
| chainsaw (Quake Champions gauntlet = grinder) | chainsaw.md3 45f | melee; `chainsaw_blade` runs 73 | |
| fist (Robocop hand) | robohand.md3 15f | melee; `robospike` (the data spike, 7 v) extends 84 | |

`_hands/`: auto9_hand.md3 + shotgun_hand.md3 = Robocop's hand (444 v) animated with each gun -- a FIFTH hand source.
