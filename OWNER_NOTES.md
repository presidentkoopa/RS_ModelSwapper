# Owner notes: logged for later, not worked yet

- 2026-10-27 07:22 (headset, round 2 build): **Brutal Wolfenstein's Mauser PISTOL (not the Kar98; owner: "the mauser is a pistol"): the magazine sits wrong in the off hand.** The owner says just note it for now; hand poses take too long. Fix it when hand placement is next worked, with the FBX hands.

- 2026-10-27 07:29: **The 9 rows still on old `_wm` data: where the animated originals are** (owner). All are in **E:\DOOMWork\VR_WeaponSetRebuild**. There is only ONE real model behind each pair, so the doubled shelf entries are duplicates:
  - **Flamethrowers:** two, one from BD21 and one from Aliens.
  - **Unmaker:** only one, from BD21.
  - **Buzzsaw:** from BD21 or Brutal Wolf.
  - **Bolter:** only one, from MeatGrinder.
  - **Tec9:** from MeatGrinder. The other SMG is BrutalSMG, a different gun.
  - The owner looks at VR_WeaponSetRebuild himself; take only what he points to (his rule: "lots of noise ... need my eyes").
- 2026-10-27 08:15: **A skin-tone slider for the hands, a 2.0 requirement** (also in BD22 Weapons Q 2.0). It comes with the switch to the FBX hands. Discrete steps (pre-recoloured skins swapped by the option) are safe on 17.3; a smooth slider needs a shader proven on the rig first.
- 2026-10-27 09:15 (owner, angry at repeating himself): **guns whose animation moves no magazine STILL get reloads.** Carve the part (magazine, canister, skull, box) out of the mesh BY POSITION and build the reload on it. BD22 did exactly this on the same meshes (the Unmaker skull, the Flamethrower canister, the over-under box). "No reload to measure from the animation, rows stay" is the WRONG conclusion; never report it again.
  - **Next round:** carved reloads for Flamethrower2, Unmaker, HitlersBuzzsaw, Bolter and Tec9, reusing BD22's carves where the mesh is identical.
  - **Unmaker rest frame:** frame 0 (the gun's own rest). BD_Unmaker resting on frame 4, 10.3 units into lowering, is a bug; fix it to match.
