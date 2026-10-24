# c2q — REMA weapon cards → QuestZDoom VR reloadable weapon packs

One pipeline, no hand edits, no engine changes. Input: the RS_VR_Weapons repo (cards, sheets,
meshes, sounds) and the Quest_Weapons_Kit (pack 1.92 runtime source + gen_rsr.py). Output: a pk3
per set that loads on QuestZDoom 17.3 (qzd17.3 = GZDoom 4.14.3 base) after the IWAD.

    python3 genpack.py  <rs_vr_weapons> <Quest_Weapons_Kit> build <vanilla|plus|modern>
    python3 assemble.py build/RSQ_<set> <set>
    python3 check.py    build/RSQ_<set>
    python3 mkpk3.py    build/RSQ_<set> <set> dist/RSQ_<set>.pk3

## Stages

| file | does |
|---|---|
| `wmcard.py` | reads WMCARD lumps (weapon / grip / part / dof / cycle / store blocks) |
| `card2quest.py` | REMA card + REMA MODELDEF scale → Quest HUD placement: HUD scale = world / 0.34, x sign kept from REMA; `Offset` puts the card's `palm` at the kit's grip reference (F −5.5, L 0, U −8.5); rest frame = first frame where the body stops turning; every card point/axis through the kit's controller-frame chain (`rgeo`); render sheet per gun |
| `iqm2md3.py` | Modern: skinned IQM at frame 0 → one-frame MD3 split by joint subtree (card `joint =`), `hidesurface` meshes and `hidejoint` subtrees dropped, one surface per (part, material) |
| `genpack.py` | set membership from WMSHEET files; per gun: feed part surfaces → magazine, action part (slide kind) → handle, well-mouth depth from the mesh (kit rule); the kit's **unmodified** `gen_rsr.py` writes `rsr_guns.zs` + `MODELDEF.rsr`; weapon classes (fire from WMSHEET, Doom numbers by type where the sheet is silent, sounds from the card), pickup models, `replaces` for Doom's weapons, sounds resolved to SNDINFO + files (`sndpack.py`), reports |
| `assemble.py` | copies the 1.96b runtime from source; the only changes are listed exact-match edits (fails if the text is not there); stubs built from the source signatures for the modules this pass does not fill (pump, break, hand tables, M203, grenade) |
| `check.py` | static gate: braces, `;` on every state line, labels, item classes, sprites vs MODELDEF, model files, sounds, handlers, cvars, includes |
| `handfit_cards.py` | the per-gun hand table: Ermac's poses moved onto each gun by the kit's own ICP (align_free / fitall_free logic), anchored on the card's `palm` (gun hand, contact face) and `supportat` (support hand, cylinder) in a tight window; letters from the shipped hand.md3; a gun+hands sheet per gun in `_hands/`; scores in `handfit_report.json` |
| `mkpk3.py` | zip + README with every per-gun flag |

## Runtime base
`assemble.py` copies the runtime from **RS_Brutal22WeaponsQ 1.96b** (`src/`), the owner's current BD22 Quest pack:
reload (vreload, assist, break, pump), hands, melee (`rsvr/melee.zs`: axe swing / two-hand / lock-on throw), punching
(`fists.zs`, landing this pack's own `WMQ_Punch`), scopes (`scope.zs`, `scope_real.zs`). Not carried: ballistics, dual,
flick, alts, casings, voxels, M203, grenade, nosniper. Every change to a copied file is an exact-match edit listed in
`assemble.py` (the build aborts if the text is not found); modules not carried are stubs built from the 1.96b signatures.

## The options menu standard
One page, **Options → RS VR Weapons** (`RSQ_Options`), the same rows in every pack, owned by the runtime. A set adds its
own rows to that page with `AddOptionMenu "RSQ_Options"` — one block per set, never a page of its own — so several packs
loaded together share one page. Cvar prefixes: `rsq_` common/hands, `rsr_` reload, `rsb_`/`rsp_` break/pump, `rsvr_`
melee, `rsa_` alt fires, `rsq_scope_<gun>`. No StaticText help lines. Debug rows stay in the menu (a console is no use in
a headset). Shared rows: VR Hands · Reloading VR/Stock · Grab ammo with · New magazine from · Check the chamber by hand ·
Shells per insert · Reload assist · VR Punching · Punch switches · Melee swing strength · Reload: tuning and debug.

## Rules that are rules, not card data (flagged per gun in each README)
- Slide / bolt lock-open: card `cycle rack / holdopen` where declared; else slide/bolt locks, charging handle does not.
- Damage, pellets, rate: WMSHEET keys where present; else Doom's own by type (`FIRE` table). Alt-fire modes dropped.
- Slots: Doom's by type (the set's own SlotNumbers are REMA's dev lane).
- Doom weapon replaced by: the set's stand-in of that type (M4A3, PumpDoom, SSG, Chaingun, RocketLauncher, PlasmaRifle, BFG, Chainsaw); Modern: Glock, MK18, Benelli.

## Not in this pass
Pump and break-open tables (RSP_Guns / RSB_Guns are present, Index 0 → canned reload); gunmoves (recoil-in-mesh); cell feeds with no mesh surface (BFG); REMA's ballistics / combat FX layer.

## Known flags from the first run
- Eject port on the LEFT with REMA's own x sign: WM_BullpupPump, WM_VP_AssaultShotgun, WM_M16 — mesh or card mirrored; check in the headset.
- WM_BreachG36C: card joint `j_charginghandle` owns no vertices in the IQM → magazine only.
- WM_SMG: charging handle is a hinge on the card; the Quest handle is a straight pull → magazine only.
- The kit's `quest_test_rig/` holds only its README; `build.sh`, `Makefile.txt`, `glue/`, `probe/` it describes are not in the kit.
- Modern rest frames come from REMA's MODELDEF per prop (Breach's own Ready frame: pistols 0, rifles 25, MP5 109, Benelli 59); MK18S = three IQMs merged. Baking at frame 0 drew the rifles mid-idle, pitched and yawed.
- Hand poses: measured gripping faces exist for Ermac frames 19/6 (pistol), 30 (shotgun), 106 (plasma) and hand2 4/15/91; ssg 47, chaingun 84, rocket 95, bfg 113, chainsaw 29 are unmeasured, so those gun types take 30 / 106 (said per gun in handfit_report.json).
- 1.96b `melee.zs` draws the axe lock-on ring with sprite `RQLK`, but no `RQLK*` lump exists in the RS_Brutal22WeaponsQ repo.
- 1.96b `scope.zs` `RSQ_Scope.EyeInHandFrame` trips the x86-64 JIT ("Unknown REGT value passed to EmitPARAM"): interpreted
  fallback on PC, no JIT on Quest.

## The engine gate
`gate_run.sh <set>`: stock qzd17.3 (`emawind84/gzdoom` tag `qzd17.3` = 9afc750, built with ZMusic from git,
`cmake -DNO_GTK=ON -DHAVE_VULKAN=OFF -DHAVE_GLES2=ON`), headless under `xvfb-run … +extension GLX` with
`LIBGL_ALWAYS_SOFTWARE=1`, Freedoom, `+vr_mode 0`; one launch per set: parse, map, give every gun, cycle, fire, reload,
quit. Pass = `script parsing took` + the three `GATE_` markers + exit 0 and no `Script error` line.
