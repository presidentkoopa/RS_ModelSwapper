# hacx (E:\DOOMWork\VR_WeaponSetRebuild\HacX; blends in br_vr\Brutaldoom_blend_files\_Hacx), 2026-10-31

Three sources on every card: the MD3 (md3label), the MODELDEF + Weapons.txt states (statephase), the blend
(blendcard). Authored raked 20 deg in the hand (Handle rot -160) like MeatGrinder. In HacX most of the
reload frames live under ALTFIRE (frames 6..10 there-and-back on pistol, cryogun, nuker, tazer).

| mesh | parts (artist-named) | reload / action | eject | note |
|---|---|---|---|---|
| pistol.md3 | base, mag, slide, trigger | slide 6.0 on fire; the MAG IS A SEPARATE SURFACE but never moves in the animation (travel 0) | none | reloadable by the runtime: mag well axis from the part |
| UZI.md3 | bolt, button, clip, clipRelease, fireSelect, handle, slide, stock0/1, trigger: 16 surfaces | DoReload: mag drops 20.0 straight down frames 5..10 (there-and-back); bolt 6.0; charging handle 8.0 | none | the complete one; a mag release button is a separate part |
| cryogun.md3 | body, chick, mag(tank) | the "mag" is a fixed cryo tank (travel 0.01); slide (surf 4) 10.0 along the bore on altfire | n/a | |
| Zooka.md3 | Bolt, crossbow, Str_long, Str_shrt, Trigger, Bolt(loaded) | CROSSBOW: the bolt flies 87 on fire; the string snaps 19.7; a fresh bolt (surf 6) seats on altfire | the bolt IS the projectile | bolt.md3 is the loose bolt with Detohead + Grenade variants |
| Nuker.md3 | 6 unnamed | three parts move 3..8 on fire (the nuke's arming mechanism); can.md3 is the loaded canister | n/a | |
| Stick.md3 (Antigun) | 11 unnamed | nothing moves against the body before the altfire frames | n/a | |
| tazer.md3 | 2 unnamed | trigger only | n/a | |
| Reznator.md3 | Plane, Cube, Cylinder, warning | nothing moves; four skin frames (ReznatorF1..4) animate the display | n/a | |
| melee.md3 | 1 | kick | n/a | |

Tool fix: md3label's grip guesser found no body below the trigger on the crossbow (flat stock); it now
falls back to the whole body (the recorded hold supersedes it anyway).
