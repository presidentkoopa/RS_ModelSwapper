# hacx (E:\DOOMWork\VR_WeaponSetRebuild\HacX; blends in br_vr\Brutaldoom_blend_files\_Hacx), 2026-10-31

Three sources on every card: the MD3 (md3label), the MODELDEF + Weapons.txt states (statephase), the blend
(blendcard). Authored raked 20 deg in the hand (Handle rot -160) like MeatGrinder. In HacX most of the
reload frames live under ALTFIRE (frames 6..10 there-and-back on pistol, cryogun, nuker, tazer).

| mesh | parts (artist-named) | reload / action | eject | note |
|---|---|---|---|---|
| pistol.md3 | base, mag, slide, trigger | RELOADABLE (owner): the magazine is its own surface, 562 verts, base nub visible below the grip; the animation never drops it, the runtime does. Slide 6.0 on fire | none | hx_pistol_mag.md3 |
| UZI.md3 | bolt, button, clip, clipRelease, fireSelect, handle, slide, stock0/1, trigger: 16 surfaces | the orange part is the MAGAZINE (owner): drops 20.0 straight down, DoReload frames 5..10; bolt 6.0; charging handle 8.0 | none | hx_uzi_mag.md3; clipRelease is the mag button |
| cryogun.md3 | body, chick, mag | the orange block on top is the MAGAZINE / cell (owner): its own surface, never animated; drop axis +Z, up out of a top well; slide (surf 4) 10.0 on altfire | n/a | hx_cryogun_mag.md3 |
| Zooka.md3 | Bolt, crossbow, Str_long, Str_shrt, Trigger, Bolt(loaded) | CROSSBOW: THE BOLT IS THE AMMO (owner): the runtime slaps a bolt.md3 (Bolt / Detohead / Grenade heads) into the rig at the loaded position; firing launches it (87 on fire), the string snaps 19.7 | the bolt is the projectile | hx_zooka_round.md3 = the loaded bolt in place |
| Nuker.md3 | 6 unnamed | three parts move 3..8 on fire (the nuke's arming mechanism); can.md3 is the loaded canister | n/a | |
| Stick.md3 (Antigun) | 11 unnamed | nothing moves against the body before the altfire frames | n/a | |
| tazer.md3 | 2 unnamed | trigger only | n/a | |
| Reznator.md3 | Plane, Cube, Cylinder, warning | nothing moves; four skin frames (ReznatorF1..4) animate the display | n/a | |
| melee.md3 | 1 | kick | n/a | |

Tool fix: md3label's grip guesser found no body below the trigger on the crossbow (flat stock); it now
falls back to the whole body (the recorded hold supersedes it anyway).

parts.png: the four runtime parts in colour (owner's corrections, 2026-10-31). Energy weapons with no
reload: tazer, Reznator, Stick; the Nuker loads a canister (can.md3).
