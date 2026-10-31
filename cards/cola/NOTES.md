# Cola 3 VR Weapons (Cola-3-VR-Weapons) -- 8 meshes (+2 dual copies skipped)

GOLD set: every surface is NAMED in the source, so roles come from the artist's names (not guessed).
Sources: md3 + modeldef.<gun>.txt + actors/weapons/<gun>.txt (`states` block). The `modeldef.quest.*`
files are byte-identical copies for Quest. No .blend in the well.

| gun | mesh | reload | parts (authored names) |
|---|---|---|---|
| revolver (ColaHandgun) | revolver.md3 55f | YES, full animation: cylinder (Magazine.wheel + Bullet_holes) swings out +Y at 37, Magazine_rod (ejector) pushes the Bullet_set out, hammer, trigger | round carved = Bullet_set (one piece of six) |
| ks23 (shotgun) | shotgun.md3 21f | YES: pump 13 units, shell (surf 4) ejects at 14; prong = the shell lifter | shell carved. `shotgun_left/right.md3` are the DUAL copies (same 3473-v body, same parts): variants copy rows, not carded |
| piledriver = PANCOR JACKHAMMER (owner): bullpup auto shotgun | jackhammer.md3 + jackhammer_mag.md3 20f | YES: the 10-round rotating ammo CASSETTE is the magazine, shipped as the mod's own second mesh (Model 1); copied as cola_piledriver_mag.md3, its 20 frames are the reload (drops -Z 38, swings back in by frame 11). surf 1 = the drum face | archetype shotgun_drum |
| sidewinder (missile launcher) | sidewinder.md3 45f + sw_ammo_*.md3 | NO (owner: non-reloading). Belt of five rockets as SEPARATE meshes is the mod's own feed animation (sw_ammo_reload: rockets enter one by one 0..19; sw_ammo_fire: one leaves per shot; full_reload): copied here. bolt, loading_bay, display, plate are named parts | |
| plasmagun (plasma autorifle) | 3f | no (heat skins cycle) | wheel_thingy, heat |
| particlegun (toothpaste laser) | 2f | NO RELOAD (owner). AmmoClip surface named, not carved; display = separate md3 | |
| frypan, carddeck | melee / thrown | no | cards: Card_1, Card_2 fly off the deck |
