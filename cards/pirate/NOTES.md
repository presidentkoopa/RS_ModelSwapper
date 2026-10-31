# Pirate Doom VR (pirate-doom-vr) -- 13 meshes + glove

Carded from the well's copy. GOLD: the artist named the lock parts on every flintlock: `_cock` (the hammer),
`_frizzen` (the pan cover it strikes), `_trigger`; the flintlock pistol also has `pistol_barrel`.
These are MUZZLE-LOADERS: reloading is powder + ball down the muzzle and the cock pulled back. What the meshes
give a hand: the cock on every gun (a real hinge, 12..20 units of travel in the fire frames), the frizzen
(flips open), and nothing else separable yet -- see CARVING below.

| gun | mesh | lock parts | notes |
|---|---|---|---|
| flintlock (pistol) | flintlock.md3 12f | cock, frizzen, trigger, barrel (296 v, separate surface) | |
| superpistol | s_pistol.md3 8f | hammer, trigger | |
| musket | musket.md3 9f | cock, frizzen, trigger | |
| blunderbuss | blunderbuss.md3 9f | cock, frizzen, trigger | |
| nock (Nock volley gun) | nock.md3 9f | cock, frizzen, trigger; body is surf 1 | |
| mortar (hand mortar) | mortar.md3 9f | cock, frizzen, trigger | |
| repeater | repeater.md3 3f | cock (781 v top lever), frizzen | |
| cannon, swivelcannon | 1 surface each | -- | fuse-lit, no lock |
| bomb, grog, cutlass | thrown / melee | grog: trigger + bottle surfaces | |

`_hands/`: glove.md3 (62 frames, the fist/pipe animation) + pipe.md3 -- a FOURTH hand source (one glove).

CARVING: NONE (owner, 2026-10-31: "i doubt the pirate guns reload"). Flintlocks do not reload by hand here; the cock and frizzen stay as the only moving parts.
geometry (one tube under the barrel line); blunderbuss and flintlock have two thin 8-vertex rods under the
barrel (z ~7.9 and ~9.9 on the blunderbuss at x 64) that may be ramrod + rib. Waiting for the owner to name
the parts to carve.
