# Golden Souls 1 + 2: Super Mario Doom enemies and high jump (PLAN M4, 2026-11-08)

Owner, 23:30: "have a separate agent make a patch for this for GoldenSouls 1 and 2. I want the enemies from this, and
the high jump. when i play GS, I want to see these enemies and load our MS to see foreign meshes on GS natural weapon
code." "This" = `00_SMD2_00_SuperMarioDoom_Assets_SDMLITE.pk3` (46,150,786 bytes, sha256 25f7994b…; read as data).

**Patch:** `pk3/GoldenSouls_SMD_Enemies.pk3` (1031 entries, 6.2 MB), one pk3 for both mods.
**Build:** `python3 tools/ms/make_gs_smd_patch.py` from `sources/smd_lite/` (the SMD lumps, PROVENANCE.md, CREDITS.txt)
and `tools/ms/gs_smd_patch/` (the patch's own lumps); `--from <SDMLITE.pk3>` re-cuts the sources from the pack.
**Load order:** Golden Souls 1 or 2 -> GoldenSouls_SMD_Enemies.pk3; `GoldenSouls1_MS.pk3` before or after it (checked
on the rig in both orders; the build's gate proves they share no lump).

## What the LITE pack is (inventoried, `python3 -I` on the unpacked copy)
1893 entries: `sprites/` (1249), `sounds/` (140), `music/` (36 MB), `graphics/`, `patches/`, `flats/`, `hires/`,
SNDINFO, LANGUAGE, SBARINFO, FONTDEFS, ANIMDEFS, TEXTURES.*, three intermission scripts. **No DECORATE, ZScript,
MAPINFO, ACS, KEYCONF or maps at all.** The "enemies" are the stock Doom monsters redrawn under the stock sprite names
and voiced by stock-named sound lumps plus a SNDINFO that re-points the rest; LANGUAGE's cast list names them. The LITE
cut therefore left out every piece of code -- including whatever gave Super Mario Doom its jump (there is a Mario
`DSJUMP` sound lump, nothing else about jumping).

Every stock monster frame is present (checked against the engine's own `zscript/actors/doom/*.zs` state tables with
`frames.py`: the only "missing" letters are SKUL L-Q, an engine-internal variant no IWAD ships, and VILE `\`, which the
pack spells `^` as GZDoom requires). Sheets: `smd_enemies/smd_monster_sheet.png`, `smd_effect_sheet.png`.

## What Golden Souls spawns (parsed from the map wads' THINGS / TEXTMAP, `things.py`)
| Doom class | GS1 things | GS2 things | GS's own subclass (gs1 doomenem.txt / gs2 DOOMENEM) |
|---|---|---|---|
| DoomImp | 230 | 597 | DoomImpNew (coin drops; stock TROO frames) |
| Demon | 82 | 293 | DemonNew |
| Cacodemon | 60 | 278 | CacodemonNew |
| HellKnight | 78 | 256 | HellKnightNew |
| BaronOfHell | 39 | 90 | BaronOfHellNew |
| Revenant | 53 | 118 | RevenantNew (+ RevenantTracerNew with GS's own Bullet Bill sprites) |
| Fatso | 29 | 136 | FatsoNew |
| Arachnotron | 7 | 0 | ArachnotronNew |
| PainElemental | 0 | 26 | PainElementalNew (GS2 only); spawns stock LostSoul |
| SpiderMastermind | 1 | 0 | SpiderMastermindNew |
| Cyberdemon | 1 | 0 | CyberdemonNew |
Zombieman, ShotgunGuy, ChaingunGuy, Archvile, Spectre, WolfensteinSS, Keen and the dog are placed by neither mod;
their sprites are in the patch anyway (except Keen and dog) so a spawner or a cheat shows the right thing.
Both mods keep every stock sprite name in those subclasses, so one sprite-level patch fits both.

## The mapping (the pack's own, LANGUAGE cast list; nothing was re-assigned)
| Doom monster (sprite) | Super Mario Doom enemy | Projectile / effect in the patch |
|---|---|---|
| Zombieman (POSS) | Koopa Troopa (green) | hitscan: `grunt/attack` = zapper |
| ShotgunGuy (SPOS) | Red Koopa Troopa | `shotguy/attack` = raygun |
| ChaingunGuy (CPOS) | Blue Koopa Troopa | `chainguy/attack` = scope |
| WolfensteinSS (SSWV) | Yellow Koopa Troopa | `wolfss/attack` = raygun |
| DoomImp (TROO) | Shy Guy | BAL1 (rock), `imp/attack` = shystone, `imp/shotx` = shyston2 |
| Demon / Spectre (SARG) | Goomba / "ghostly goomba" | melee |
| Cacodemon (HEAD) | Lakitu | BAL2 (spiny), `caco/attack` = throw |
| HellKnight (BOS2) | Blue Magikoopa | BAL7 (magic) |
| BaronOfHell (BOSS) | Red Magikoopa | BAL7 |
| LostSoul (SKUL) | Boo | `skull/death` = defeat |
| PainElemental (PAIN) | Big Boo | spawns Boos |
| Revenant (SKEL) | Evil Luigi | FATB (spiny shell; GS replaces the tracer with its own Bullet Bill, so unseen) |
| Fatso (FATT) | Wario | MANF (Chain Chomp), `fatso/attack` = chomp |
| Archvile (VILE) | Waluigi | **FIRE not taken** (see below): Doom's fire with SMD's `revive` / `shystone` sounds |
| Arachnotron (BSPI) | Evil Mario | APBX / APLS (fireballs), `baby/attack` = fireball |
| SpiderMastermind (SPID) | Donkey Kong | `spider/attack` = raygun, `spider/walk` silenced |
| Cyberdemon (CYBR) | Bowser | MISL A only (a Bullet Bill in flight); rocket explosion frames stay the game's |
No role needed a choice between two SMD enemies: the pack has exactly one redraw per Doom monster.

## What is in the patch (1031 entries)
- `sprites/` 939: the 17 monsters above + BAL1 BAL2 BAL7 MANF FATB APBX APLS + MISL A-rotations.
- `sounds/` 83: 54 stock-named monster lumps (override by name) + 29 the SNDINFO names (zapper, raygun, luigiow …).
- `SNDINFO`: the pack's monster section, verbatim (player, dog, menu, intermission lines left out).
- `LANGUAGE`: the pack's CC_* cast names and OB_* obituaries only.
- `zscript.txt` + `zscript/smd_highjump.zs`, `MAPINFO` (registers the handler), `CVARINFO`, `MENUDEF`, `README.txt`, `CREDITS.txt`.

**Left out on purpose:** PLAY/PLYC and the Mario player sounds (the owner asked for enemies; GS2 ships its own extra
PLAY frames), weapons, items, decorations, textures, flats, music, Keen and the helper dog; **FIRE** (GS1 uses the FIRE
sprite 48 times and GS2 69 times for its own monsters' flames -- CacoLich, Gargoyle, Archvile_Boss and more -- and
the SMD FIRE is a red target reticle, so Waluigi keeps Doom's fire); PUFF, BLUD, BEXP, FBXP, MISL B-D (effects GS's own
weapons and actors share; the SMD versions would restyle GS's explosions).

**Side effects to know (GS actors that borrow stock monster sprites or sound names):** GS1 GhostSoul uses SKUL frames
(becomes a Boo -- it is a ghost), Drybones two SKEL pain frames, IconOfSinFinalForm one VILE frame; GS2's "Comet"
variants (CometDemon, CometCacodemon, HellKnightComet, BaronOfHellComet, PainElementalComet) are recoloured Doom
monsters and become recoloured Mario enemies; GS2 Archvile_Boss draws VILE (Waluigi boss); GS2 Cyberdemon_Boss draws
CYBR A-P (Bowser) but its death uses GS2's own CYBR Q-U frames, so that death animation mixes. GS1 Bloodfiend and
GS2's swamp/snow zombies play `demon/*` and `fatso/*` sounds and will sound like Goombas / Wario. CathedralBell (GS2)
names VILE frames but is a MODELDEF model: unaffected.

## The high jump: method and why
- **Where SMD's number would come from:** nowhere -- the pack has no player code. Not measured, said plainly.
- **GS's own numbers (parsed):** GS1 `Player.JumpZ 8.2` (decorate/gplayer.dec line 28; GSPlayer : ZGSPlayer :
  DoomPlayer, whose PlayerThink in zscript/zplayer.zc allows an instant re-jump); GS2 `Player.JumpZ 15` (DECORATE
  line 46; GSPlayer : PlayerPawn, with a double-jump ACS `dbljump.acs` and a `MiniPlayer` morph). Both MAPINFOs name
  the class in `playerclasses`; GS2 has two `nojump` maps.
- **Method:** `SMD_HighJumpHandler : EventHandler` (registered in the patch's MAPINFO -- without that line it never
  runs; found on the rig) gives every player an undroppable `SMD_HighJump : Inventory` at PlayerEntered,
  PlayerRespawned and WorldLoaded (old saves). The item's DoEffect sets the pawn's JumpZ every tic from the server cvar
  `smd_jumpz` (default **15** = GS2's own) while `smd_highjump` is on, and restores the class default
  (GetDefaultByType) when off. GS's player classes are not replaced; morphs carry the item to the new pawn; `nojump`
  maps stay no-jump (JumpZ is a height, not permission). Netplay: server cvars and player-number loops only, no
  consoleplayer. Options > "Golden Souls: Mario enemies + jump" has the switch and a slider (8-40).
- **Not done:** MAPINFO / KEYCONF cannot set a jump height; replacing GSPlayer would lose GS1's PlayerThink or GS2's
  morph chain, so neither was used.

## Verified on the rig (QuestZDoom 17.3 Linux, `tools/rig/bin/qz`, doom2.wad from the owner's upload, 2026-11-08)
Logs in the session's work dir; the lines that matter, from the test-only probe (`tools/ms/gs_smd_probe/`,
`make_gs_smd_patch.py --probe`, loaded last, never shipped):
- Init, GS1 -> patch, GS1 -> patch -> GoldenSouls1_MS, GS1 -> GoldenSouls1_MS -> patch, GS2 -> patch: **no script
  error, no warning** from any archive (`-norun` and full map runs).
- Lumps resolve to the patch: `SMDPROBE sprite TROOA1 lump 10908 = sprites/trooa1.png`,
  `SMDPROBE sound DSBGSIT1 lump 10048 = sounds/dsbgsit1`, and `FIREA0 lump 6126 = FIREA0` (the IWAD's, as intended).
- GS1 MAP01 "Happy Gardens": `SMDPROBE monster DoomImpNew draws TROOA1`, `DemonNew draws SARGA1`, `CacodemonNew draws
  HEADA1`, `HellKnightNew draws BOS2A1`; GS's own Red_Plant / Golden_Caco keep their sprites. Frame:
  `smd_enemies/gs1_map01_shyguy_lakitu.png` (a Shy Guy on the path, a Lakitu behind). GS2 MAP01: same lines, frame
  `smd_enemies/gs2_map01_shyguy.png`.
- Jump, GS1: `SMDPROBE tic 1 p0 GSPlayer JumpZ 15.00 item yes` from the first tic; `smd_highjump 0` -> `JumpZ 8.20`
  (GS1's own default back); `smd_highjump 1; smd_jumpz 30` -> `JumpZ 30.00`. GS2: 15.00 (its own) -> `smd_jumpz 24` ->
  24.00 -> off -> 15.00. A real jump: apex **120.0 units above the floor at JumpZ 15, 37.8 at 8.2** (`SMDPROBE air`).
- Not verified: a headset; the Spider Mastermind / Cyberdemon / Arachnotron / Pain Elemental drawn in a GS map (only
  listed and sprite-checked); sounds heard (lump resolution only, `-nosound`).

## Open (the owner's call)
- The jump height. 15 is GS2's number, not Super Mario Doom's. If the full SMD pack turns up, its player class gives the
  real one; `smd_jumpz` takes it without a rebuild.
- The Mario jump sound: the pack's `DSJUMP` is not in the patch (GS1 and GS2 each define their own `*jump`; overriding
  it is a taste call). One line each in SNDINFO would do it: `$playersound Remasteredguy male *jump DSJUMP` (GS1),
  `$playersound gs2player male *jump DSJUMP` (GS2), plus the lump.
- The player as Mario (PLAY/PLYC) and the Mario player pain sounds: left out, two lines in the tool to add.
