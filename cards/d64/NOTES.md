# D64Retribution -- 15 meshes, 12 of them ARE BD21 meshes (owner: "BE CAREFUL and doublecheck")

Every mesh was matched against every BD21 mesh, ALL surfaces and ALL frames vertex-exact (not sizes, not names):

| D64 mesh | result | card |
|---|---|---|
| BFG/BFG.md3 | = BD21 BFG.md3, 16/16 frames identical | cards/bd21/bfg |
| BFG/BFG_10k.md3 | = BD21 BFG_10k.md3, 21/21 identical | cards/bd21/bfg10k |
| BrutalPistol | = BD21, 38/38 | cards/bd21/pistol |
| Minigun | = BD21, 16/16 | cards/bd21/minigun |
| Plasma_Gun | = BD21, 30/30 | cards/bd21/plasma |
| RPG | = BD21, 39/39 | cards/bd21/rpg |
| RailGun | = BD21, 37/37 | cards/bd21/railgun |
| Rifle | = BD21, 32/32 | cards/bd21/rifle |
| SSG | = BD21, 52/52 | cards/bd21/ssg |
| Shotgun | = BD21, 36/36 | cards/bd21/shotgun |
| Unmaker | = BD21, 16/16 | cards/bd21/unmaker |
| Fist/fistclosed.md3 | SAME MESH as BD21 fistclosed, frames 36..74 identical, frames 0..35 RE-ANIMATED (D64 punch) | cards/bd21/fist rows copy; melee, no reload, so the new frames change nothing |
| BFG/BFG_Flame.md3 | effect (a 160-v cylinder + a quad), not a weapon | not carded |
| Boot/Boot.md3 | NEW: one surface 19068 v, 21 frames (BD21's Boot is a different mesh) | d64/boot (melee) |
| Chain_saw/Chain_saw.md3 | NEW: 7 surfaces (two 15k halves, bar, chain pieces), 8 frames; NOT HDVR's 2-surface 3DHaupt saw | d64/chainsaw (melee) |

Credits.txt lists sketchfab sources for all of them; the vertices say BD21 for twelve. The MODELDEFs bind the D64
sprite names (64* classes), so these are the BD21 cards with a D64 state map.

Correction found while double-checking (applied to cards/hdvr): HDVR's BFG.md3 is ALSO the BD21 BFG mesh (same
surfaces; 9 of 16 frames re-animated), not a new mesh.
