# REMA blockers: putting the Depot's hands on REMA's avatars

An addendum to this handbook, for the REMA side. Written 2026-10-28 against Depot `main` at `483f767`
and UZDXREMA `avatar-ik-work` at `5d1188dcfa`.

**The goal (owner, 2026-10-28):** the REMA avatar's hands posed on the guns as well as they are in
BD22 VR Weapons Q, for every RS set, now and later.

Nothing in this file changes the Depot's method or its rules. Everything here is work on the REMA side,
or a question for the owner. Each claim says whether it was **read** (from a file named beside it) or
**inferred** (needs checking before anything is built on it).

## What the Depot already gives REMA

These were checked in the repo:

- **The same hand.** Both projects pose the same FBX hand, `hand_final.fbx` with 22 joints. REMA's
  `wadsrc/static/vrhandpose.txt` is generated from it by `mkfbxposes.py`. The Depot's fitter poses it with
  `tools/handfit/core/hands_tool/handmodel.py`. **(read)**
- **Per-gun poses, stored as data.** `sets/bd22q/handfit/poses/<Class>.json` exists for 30 BD22 classes.
  Each one holds:
  - the trigger and squeeze pose vectors (`q_trigger`, `q_squeeze`);
  - the solved fingers;
  - **the wrist on the gun** (`wrist_on_gun`: `R`, `t`);
  - the gun move;
  - the support hand;
  - the fit measurements (penetration, pad and palm gaps).

  `rebake.py check` rebuilds every one of them from that data. **(read)**
- **One method that matches REMA's.** The Depot pins the wrist to the controller and moves the gun to the
  hand (handbook rule 1). REMA places a held gun as `handTarget · WeaponFit`: the gun hangs off the hand
  too (`vr_rig.cpp`, `VRRig_ObjectToWorld`, role 2). So a Depot pose's `wrist_on_gun` is, in principle,
  REMA's per-gun fit. **(read; that the two are equivalent is inferred)**
- **The fitter itself.** It handles penetration both ways, contact rules G/S/U/N with cited tolerances,
  the fit farm, and sheets from the eye. It is the tool REMA would otherwise have to build. **(read)**

## The blockers

### B1. Nothing turns a Depot pose into REMA's pose format
**Read:** REMA reads finger rotations as `rot <pose> <R|L> <finger> <joint> <quaternion>` lines, in the
canonical bone frame, against the FBX open hand (`vrhandpose.txt`, header). The engine already picks a
per-gun pose by the held prop's class, `grip_<PropClass>` and `grip_<PropClass>_fire` (`vr_rig.h`,
`VRRig_HandPropClass`). The Depot stores a gun pose as `handmodel.py` parameter vectors.

**Missing:** an exporter. It would run each pose's `q_trigger` and `q_squeeze` through `handmodel.py` to
get joint rotations, express those the way `mkfbxposes.py` does, and write them as
`grip_<PropClass>` / `grip_<PropClass>_fire`. Support poses would be written the same way as
`hold_support_<PropClass>`.

**Closes when:** a pose round-trips. The REMA hand drawn from the exported lines matches the Depot's baked
MD3 frame for the same gun, joint for joint.

### B2. The hand-on-gun rotation in REMA is a guess (identity)
**Read:** REMA's `[GUNANCHOR]` rotation, from the avatar's hand frame to a gun's grip frame, is "the last
quantity in this chain that is not measured". It stays identity until `vr_gun_anchor_diag` measures it, and
`vr_gun_anchor_hand` is off by default (`vr_avatar_pose.cpp`, around line 1085). The owner's headset pass
on 2026-10-27 found every gun hand pose wrong. **(read)** That this rotation is the cause is **inferred**.

**What the Depot offers:** `wrist_on_gun` is that relation, measured per gun on the FBX hand.

**Missing:** two measurements.
- The fixed transform between the FBX wrist joint and REMA's canonical hand frame. It is the same for
  every gun.
- For each body, the transform between the FBX wrist and that body's own hand bone. REMA measures each
  body's hand rest already (`HandRest`, `O_hand`), but never against the FBX wrist.

**Closes when:** the Depot Rifle's wrist, carried through those two transforms, puts a REMA body's hand
where the Depot sheet shows it.

### B3. REMA's card can't carry the full hand placement
**Read:** REMA places the hand from the card's `palm`, `rake` and `triggerat` by one rule
(`VRRig_GripFrame`). There is no roll (`GUN_POSE_STANDARD.md` §2, §7). The Depot's hands are turned on
the wrist per gun. The Rifle's is 8.9° against the pistol hand (handbook chapter 4, step 3).

**Missing:** a card field for the full per-gun transform, or for roll and offset, filled from
`wrist_on_gun`. REMA's open question about how a hand holds a straight stock (`GUN_POSE_STANDARD.md` §7)
is answered by the Depot's fits where they exist (the Ruger: pistol-style, owner's choice, chapter 3).

**Closes when:** a card can hold a Depot placement exactly. This needs an engine change in REMA, which is
allowed there and is not the Depot's concern.

### B4. Hand size
**Inferred:** the Depot's fingers close on a gun at the FBX hand's own size, but each REMA body's hand is
scaled to that body (`vr_avatar_handscale`, `HandScaleFor`). On a body whose hand is not FBX-sized, the
same joint rotations stand off the grip or sink into it.

**Missing:** one of these.
- Measure each body's hand against the FBX hand and correct the placement for the difference.
- Re-curl the fingers per body against the gun. The Depot's `curl3` / `curl4` close fingers to 0.2 cm,
  and could run per body.

**Closes when:** REMA's `gun_fit_preview` shows each body's hand closing on the grip within the Depot's
tolerances: penetration at most 0.5 cm, and pads 0.2 to 0.5 cm.

### B5. The guns are different meshes in different spaces
**Read:**
- The Depot fits BD22's own animated HUD meshes (for example `models/bd/Rifle/Rifle.md3`, ready frame 3),
  through the QZD HUD chain (chapter 1.2).
- REMA's world guns are RS_VR_Weapons cards with `*_wm.md3` stills at 34 map units per metre.
- The Depot ruled the `_wm` stills out for its own sets (chapter 6, `check_plan.py`).

**Missing:** for each gun, the rigid transform from the Depot mesh at its ready frame to REMA's mesh. The
1.97 work found these by rigid fit at residual 0.0000 (archive branch `HANDOFF.md`). Also missing: a class
map from Depot class (`Rifle`) to REMA card and prop (`WM_*`, the prop class the engine keys poses on).

**Question for the owner:** should REMA move off the `_wm` stills too? Recoil and reload frames need the
animated originals.

### B6. The support hand
**Read:** the Depot fits a support hand per gun (`support192`, stored in the pose JSON). REMA's brace
(RS_VR_Reload `AnchorBrace`) places the support hand with the main grip's frame, so a hand on a forend is
oriented like a hand on a pistol grip (`GUN_POSE_STANDARD.md` §4, `supportaxis`). REMA's two-hand mode is
also its own, not QZD's 50 cm steady (chapter 1.1).

**Missing:** REMA placing the support hand from a per-gun transform (B3's field, for the off hand), plus
B1's export of the support pose.

### B7. Only BD22 has FBX poses
**Read:** `sets/bd22q` has 30 FBX poses. `sets/vanilla`, `vanilla_plus`, `modern` and `aliens` still carry
the old letter-based hand tables (`handfit_report.json`) or nothing. Those sets are tabled until the owner
picks (PLAN S1-S3). For "every RS set, now and later", each set goes through the Depot's fitter first.
REMA would then take it through B1-B5, and gets nothing a set doesn't have.

### B8. Reload holds and other hand states
**Read:** the Depot has FBX off-hand holds per gun (magazine and round in the hand, `offhand/`), fists, the
grenade pinch, and melee hands. REMA's reload hands are `hold_<subject>[_<class>]` poses on real parts
(`GUN_POSE_STANDARD.md` §5, §9). They come after B1-B3, through the same exporter.

### B9. Licence of the FBX hand
**Read:** the Depot never commits `hand_final.fbx` ("unknown licence", `check_plan.py`). REMA's pose
generator reads it from `models/hands/hand_final.fbx`. **To check:** whether REMA has committed it
anywhere, so both projects follow the same rule.

## The order

1. **B2's measurement**, on one body (c_doom_marine) and one gun (the Rifle or the pistol). Until a hand sits
   right through the identity-free chain, nothing else can be judged.
2. **B1**, the exporter, on the same gun, round-tripped against its baked MD3.
3. **B5**, the mesh transform and class map for BD22, then **B3**, the card field.
4. **B4** across the bodies.
5. **B6**, then **B8**.
6. **B7**, one set at a time, when the owner picks the Depot set.

## Questions for the owner
- B5: should REMA's world guns move from the `_wm` stills to the animated originals, as the Depot did?
- B3: a full transform on the card, or roll plus offset?
- B9: where `hand_final.fbx` lives for REMA, and whether it is committed.
