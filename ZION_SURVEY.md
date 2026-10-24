# ZionVR weapon package — survey

Read-only investigation of the ZionVR Doom 2016 arsenal, done 2026-10-24.
Nothing in `VR_WeaponSetRebuild` was written to; nothing in this repo was changed
except this file and the ten renders in `renders_packs/`.

Source surveyed:

- `E:\DOOMWork\VR_WeaponSetRebuild\ZionVR-essential1\skins\03_ZionVR_WEAPONS\` — 32 `ModelDef.*` files, 62 MD3s under `MD3\Weapons\`
- `E:\DOOMWork\VR_WeaponSetRebuild\ZionVR-optional\` — three sub-packs, see "The optional set" below

**101 `Model <class>` blocks** were found and every one is classified. None is
left unexplained.

---

## 1. The ten classes

| Class | Base-gun block | Base-gun mesh(es) (MODEL index) | Frames | Surfaces | Hands in the mesh? |
|---|---|---|---|---|---|
| `D4Pistol` (EMG) | `ModelDef.EMG` | `0` Pistol.md3 | 149 | 1 | no |
| `D4SHOTGUN` (CSG) | `ModelDef.CSG` | `0` CombatShotGunBase.md3, `1` CombatShotGunBase2.md3 | 113 | 4 + 1 = 5 | **YES — surf 0** |
| `D4SUPERSHOTGUN` (SSG) | `ModelDef.SSG` | `1` SuperShotgun.md3, `2` SuperShotgunShells.md3 | 151 | 1 + 1 = 2 | no |
| `D4CHAINGUN` (CG) | `ModelDef.CG` | `1` CGBase.md3, `2` CGBarell.md3 | 63 / 65 | 1 + 1 = 2 | no |
| `D4MACHINEGUN` (HAR) | `ModelDef.HAR` | `0` HARBase.md3 | 64 | 1 | no |
| `D4PLASMARIFLE` (PLRF) | `ModelDef.PLRF` | `1` PLRFBase.md3, `2` PLRFBase1.md3, `3` PLRFBase2.md3 | 109 | 1 + 3 + 1 = 5 | no |
| `D4ROCKETLAUNCHER` (RL) | `ModelDef.RL` | `0` RLBase.md3 | 92 | 1 | no |
| `D4BFGGUN` (BFG9000) | `ModelDef.BFG9000` | `1` BFGBaseBurn.md3, `2` BFGElOrbSin.md3 | 201 | 2 + 3 = 5 | no |
| `Dumb4gausscannon` (GC) | `ModelDef.GC` | `1` GCBase.md3, `2` GCBarrel.md3 | 85 | 1 + 1 = 2 | no |
| `D4CHAINSAW` (CSAW) | `ModelDef.CSAW` | `1` CSAW.md3 | 22 | 1 | no |

Block totals per class: CSG 15, RL 12, PLRF 12, CG 12, GC 9, HAR 9, SSG 8,
EMG 8, CSAW 8, BFG 7, plus one orphan block under the separate class
`BFG9000Pickup`. 101 in all.

### The ready pose

Zion's modeldefs are pure animation tables — there is no neutral-pose lump and
no single "this is the gun" frame. The ready pose is reliably **the last frame
of the `…H` ("Unhide" / raise) run**, which in every class is also the first
frame of the fire run. These are the frames I rendered and the frames an import
should stand the gun on:

| Class | Ready frame | Confirmed by |
|---|---|---|
| D4Pistol | 58 | `PISH` 50–58, `PISF` starts 59 |
| D4SHOTGUN | 61 | `CSGH` 50–61, `CSGF` starts 63 |
| D4SUPERSHOTGUN | 62 | `SSGH` 50–62, `SSGF` starts 63 |
| D4CHAINGUN | 57 | `CGNH` ends 57, `CGNF A` = 57 — exact match |
| D4MACHINEGUN | 26 | `HARH` 15–26, `HARF` starts 27 |
| D4PLASMARIFLE | 21 | `PRNH` ends 21, `PRNR A` = 21 — exact match |
| D4ROCKETLAUNCHER | 27 | `RL1H` 15–27, `RL1F` spans 27–89 |
| D4BFGGUN | 22 | `BFGH` 13–22, `BFG1` starts 23 |
| Dumb4gausscannon | 21 | `GCNH` 15–21, `GCNF` starts 22 |
| D4CHAINSAW | 21 | `SAWH` 16–21 (last frame of a 22-frame mesh) |

### Transform block (all ten, as authored)

Every class uses `Scale -3.0 3.0 3.0` — a uniform ×3 with X mirrored. The rest:

| Class | offset | ZOffset | Pitch | Roll | Angle |
|---|---|---|---|---|---|
| D4Pistol | −12.0 25.0 0.0 | 3 | −2 | 0 | −1.5 |
| D4SHOTGUN | −15.0 0.0 0.0 | 2 | −4.0 | 0 | −1 |
| D4SUPERSHOTGUN | −9.0 0.0 0.0 | 1 | −2 | 0 | 0 |
| D4CHAINGUN | −11.0 0.0 0.0 | 10 | 0 | 10 | 1.5 |
| D4MACHINEGUN | −20.0 0.0 0.0 | 3 | −2 | 0 | −2 |
| D4PLASMARIFLE | −14.0 0.0 0.0 | 7 | 0 | 0 | 1 |
| D4ROCKETLAUNCHER | −19.5 0.0 0.0 | 5 | 0 | 0 | −1.5 |
| D4BFGGUN | −13.0 10.0 0.0 | 20 | 0 | 0 | −1 |
| Dumb4gausscannon | −26.0 −10.0 0.0 | 5 | 0 | 9 | −1.5 |
| D4CHAINSAW | −16.0 0.0 0.0 | 10 | −2 | 0 | −15.5 |

These are HUD-model numbers tuned against Zion's own ZScript offsets. They are
not world-space seating and do not carry over to a swap.

---

## 2. Every block, per class

Each class shares the same five glory-kill blocks and the same ledge-grab block,
so those are described once here and listed only by name below.

**The shared six (identical in every class, only the class name differs):**

| Block | File | Mesh | Sprite | Rows | What it is |
|---|---|---|---|---|---|
| Melee Left | `ModelDef.<X>_GK` | GK_MeleeLeft.md3 | `MELF` | 16 | left-hand punch, bare arms |
| Melee Right | `ModelDef.<X>_GK` | GK_MeleeRight.md3 | `MERG` | 16 | right-hand punch, bare arms |
| Kick Right | `ModelDef.<X>_GK` | GK_Kick.md3 | `KICK` | 5 | boot kick |
| Kick Left | `ModelDef.<X>_GK` | GK_Kick.md3 | `KICL` | 5 | same mesh, mirrored state |
| GK 1 | `ModelDef.<X>_GK` | GK_1.md3 | `GKZ0` | 19 | glory-kill grab animation |
| Ledge grab | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | 16 | climb/mantle, bare arms |

All six carry `Skin 0 "MD3/Weapons/Hand.jpg"` (except the kick, which uses
`GK_Kick.png`) and all six are **arms-only meshes with no gun in them**
(surface name `praetor.003`). They are weapon-independent — the same five files
are referenced ten times over. **None of them is a candidate for a model swap.**

Note `GK_2.md3` (39 frames) exists in the folder but is referenced by no block
in the essential set.

---

### D4Pistol (EMG) — 8 blocks

| # | File | Meshes | Sprites | What it is |
|---|---|---|---|---|
| 1 | `ModelDef.EMG` | `0` Pistol.md3 | `PISH` 50–58, `PISF` 59–70, `PISM` 36–49, `PISC` 71–80, `PIC1` 81–104, `PIC2` 105–121, `PISG` 133–148 | **BASE GUN.** Raise, fire, melee, charge, charged shot (two stages), grenade |
| 2–6 | `ModelDef.EMG_GK` | — | `MELF` `MERG` `KICK` `KICL` `GKZ0` | the shared five |
| 7 | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | ledge grab |
| 8 | `ModelDef.Weapon.pickups.def` | `0` Pistol.md3 | `WPPK` frame 0 | world pickup, one frame |

No weapon mods — correct to Doom 2016, the EMG's mods are software, not geometry.
Frames 0–35 of Pistol.md3 are referenced by nothing in this block.

### D4SHOTGUN (CSG) — 15 blocks

| # | File:line | Meshes | Sprites | What it is |
|---|---|---|---|---|
| 1 | `ModelDef.CSG:1` | `0` CombatShotGunBase.md3, `1` CombatShotGunBase2.md3 | `CSGH` 50–61, `CSGF` 63–82, `CSGM` 36–49, `CSGG` 83–112 | **BASE GUN** |
| 2 | `ModelDef.CSGMod1:1` | `0` CombatShotGunBase.md3, `1` CombatShotGunBomb.md3 | `CSBH` `CSBF` `CSBM` `CSBG` | Explosive Shot mod, **held** |
| 3 | `ModelDef.CSGMod1:96` | `0` CombatShotGunBombSwitchBase.md3, `1` CombatShotGunBombSwitchMod.md3 | `CSB1` `CSB2` `CSB3` | Explosive Shot mod, **equip/switch animation** (78-frame dedicated meshes) |
| 4 | `ModelDef.CSGMod2:1` | `0` Base, `1` Base2, `2` CombatShotGunTriple.md3 | `CSTH` `CSTF` `CSTM` `CSTG` | Triple Burst mod, **held** |
| 5 | `ModelDef.CSGMod2:101` | same three meshes, `Skin 2` = CombatShotgunTriple1.png | `CSC1 L` frame 61 only | one-pose variant, skin only |
| 6 | `ModelDef.CSGMod2:127` | same three meshes, `Skin 2` = CombatShotgunTriple2.png | `CSC2 L` frame 61 only | one-pose variant, skin only |
| 7 | `ModelDef.CSGMod2:153` | same three meshes, `Skin 2` = CombatShotgunTriple3.png | `CSC3 L` frame 61 only | one-pose variant, skin only |
| 8 | `ModelDef.CSGMod2:181` | `0` CombatShotGunTripleSwitchBase.md3, `1` CombatShotGunTripleSwitchMod.md3 | `CST1` `CST2` `CST3` | Triple Burst mod, **equip/switch animation** (71 frames) |
| 9–13 | `ModelDef.CSG_GK` | — | — | the shared five |
| 14 | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | ledge grab |
| 15 | `ModelDef.Weapon.pickups.def` | `0` shotgun.md3 | `WPPK` | world pickup — **a separate 1-frame mesh**, not CombatShotGunBase |

Blocks 5–7 are mechanically identical to block 4 frozen at frame 61, with only
the Triple mod's texture swapping between `CombatShotgunTriple1/2/3.png`. The
obvious reading is a burst-charge indicator (1, 2, 3 rounds staged), but I have
not opened the three PNGs to confirm what they actually show. **That is the
evidence that would settle it** — if the three textures differ only in which
indicator segments are lit, the reading is right.

### D4SUPERSHOTGUN (SSG) — 8 blocks

| # | File | Meshes | Sprites | What it is |
|---|---|---|---|---|
| 1 | `ModelDef.SSG` | `1` SuperShotgun.md3, `2` SuperShotgunShells.md3 | `SSGH` 50–62, `SSGM` 36–49, `SSGF` 63–75, `SGR1` 76–101, `SGR2` 102–121, `SSGG` 122–150 | **BASE GUN.** `SGR1`/`SGR2` are the two halves of the break-open reload |
| 2–6 | `ModelDef.SSG_GK` | — | — | the shared five |
| 7 | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | ledge grab |
| 8 | `ModelDef.Weapon.pickups.def` | `0` SuperShotgun.md3 | `WPPK` | world pickup |

No mods — correct to Doom 2016.

### D4CHAINGUN (CG) — 12 blocks

| # | File:line | Meshes | Sprites | What it is |
|---|---|---|---|---|
| 1 | `ModelDef.CG:1` | `1` CGBase.md3, `2` CGBarell.md3 | `CGNH` 14–57, `CGNM` 0–13, `CGNF` 57–64, `CGNG` 22–56 | **BASE GUN.** The spinning barrel is a separate mesh at MODEL 2 |
| 2 | `ModelDef.CGMod1:1` | `1` CGBase, `2` CGBarell, `3` CGGatling.md3 | `CGGH` `CGGM` `CGGF` `CGGG` | Gatling Rotator mod, **held** — base kept, attachment added |
| 3 | `ModelDef.CGMod1:82` | `1` CGGatlingSwitchBase.md3, `2` CGGatlingSwitch.md3 | `CGG1` `CGG2` `CGG3` | Gatling mod **switch animation** (64 frames) |
| 4 | `ModelDef.CGMod2:1` | `1` CGBase, `2` CGTurret.md3 | `CGTH` `CGTM` `CGTF` `CGTG` | Mobile Turret mod, **held** — note CGBarell is **dropped**, the turret mesh carries its own barrels |
| 5 | `ModelDef.CGMod2:80` | `1` CGTurretSwitchBase.md3, `2` CGTurretSwitch.md3 | `CGT1` `CGT2` `CGT3` `CGTX` 71–90, `CGTZ` 2 frames | Turret mod **switch animation** (92 frames). The longest switch in the pack |
| 6–10 | `ModelDef.CG_GK` | — | — | the shared five |
| 11 | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | ledge grab |
| 12 | `ModelDef.Weapon.pickups.def` | `0` CGBase.md3, `1` CGTurret.md3 | `WPPK` | world pickup — ships with the turret attached |

`CGTZ` (2 frames) is the only sprite in the pack I cannot name with confidence.
It sits at the tail of the turret switch block. It is almost certainly a
two-frame hold or abort state; a ZScript read of the `Dumb4chaingun` state
machine would settle it. I did not read Zion's ZScript (it is outside the
package folder I was pointed at).

### D4MACHINEGUN (HAR) — 9 blocks

| # | File:line | Meshes | Sprites | What it is |
|---|---|---|---|---|
| 1 | `ModelDef.HAR:1` | `0` HARBase.md3 | `HARH` 15–26, `HARM` 0–14, `HARF` 27–34, `HARG` 35–63 | **BASE GUN** |
| 2 | `ModelDef.HARMod2:1` | `0` HARBase.md3, `2` HARMicro.md3 | `HRMH` `HRMD` (deploy) `HRMM` `HRMF` `HRMG` | Micro Missiles mod, **held**. `HRMD` is the pod-deploy animation |
| 3–7 | `ModelDef.HAR_GK` | — | — | the shared five |
| 8 | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | ledge grab |
| 9 | `ModelDef.Weapon.pickups.def` | `0` HARBase.md3 | `WPPK` | world pickup |

**HAR is incomplete.** There is no `ModelDef.HARMod1` — the Tactical Scope mod
exists only as a **fully commented-out block** at `ModelDef.HARMod2:90`,
referencing `HARScopeSwitchBase.md3`, `HARScopeSwitch.md3` and `HARScope.png`,
**none of which are in the package**. The Micro Missiles mod also has **no
switch block** of its own, live or commented, even though the switch meshes
`HARMicroSwitch*.md3` are present in the folder.

### D4PLASMARIFLE (PLRF) — 12 blocks

| # | File:line | Meshes | Sprites | What it is |
|---|---|---|---|---|
| 1 | `ModelDef.PLRF:1` | `1` PLRFBase.md3, `2` PLRFBase1.md3, `3` PLRFBase2.md3 | `PRNH` 14–21, `PRNM` 0–13, `PRNR` 21–26, `PRNF` 26–74, `PRNG` 75–108 | **BASE GUN.** `PRNR` is fire-ready, `PRNF` is fire-hold |
| 2 | `ModelDef.PLRFMod1:1` | `1` PLRFBase, `2` PLRFStuntBase.md3, `3` PLRFBase2 | `PRSH` `PRSM` `PRSR` `PRSF` `PRSG` | Stun Bomb mod, **held** — PLRFBase1 swapped for PLRFStuntBase |
| 3 | `ModelDef.PLRFMod1:80` | `1` PLRFSwitchStuntBase.md3, `2` PLRFSwitchStunt.md3, `3` PLRFSwitchStuntPlate.md3 | `PRS1` `PRS2` `PRS3` | Stun Bomb **switch animation** (66 frames) |
| 4 | `ModelDef.PLRFMod2:1` | `1` PLRFBase, `2` PLRFHeatBase.md3 | `PRHH` `PRHM` `PRHR` `PRHF` `PRHG` | Heat Blast mod, **held** — PLRFBase1 swapped **and** PLRFBase2 dropped |
| 5 | `ModelDef.PLRFMod2:77` | `1` PLRFSwitchHeatBase.md3, `2` PLRFSwitchHeat.md3 | `PRH1` `PRH2` `PRH3` | Heat Blast **switch animation** (80 frames) |
| 6–10 | `ModelDef.PLRF_GK` | — | — | the shared five |
| 11 | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | ledge grab |
| 12 | `ModelDef.Weapon.pickups.def:106` | `0` **PLRF_hands.md3**, `1` PLRFBase, `2` PLRFBase1, `3` PLRFBase2 | `WPPK` | world pickup — **broken, see below** |

The plasma rifle pickup block is the **only live reference to a hands mesh in a
gun block anywhere in the essential set**, and `PLRF_hands.md3` **does not exist
in `MD3\Weapons\`**. (It exists in the optional hands pack, as `PLRF_Hands.md3`.)
That block will fail to resolve MODEL 0.

### D4ROCKETLAUNCHER (RL) — 12 blocks

| # | File:line | Meshes | Sprites | What it is |
|---|---|---|---|---|
| 1 | `ModelDef.RL:1` | `0` RLBase.md3 | `RL1H` 15–27, `RL1M` 0–14, `RL1F` 27–89, `RL1G` 28–61 | **BASE GUN** |
| 2 | `ModelDef.RLMod1:1` | `0` RLBase, `2` RLDet.md3 | `RL2H` `RL2M` `RL2F` `RL2G` | Remote Detonation mod, **held** |
| 3 | `ModelDef.RLMod1:105` | `0` RLSwitchBase.md3, `2` RLDetSwitch.md3 | `RLD1` `RLD2` `RLD3` | Remote Det **switch animation** (72 frames) |
| 4 | `ModelDef.RLMod2:1` | `0` RLBase, `2` RLLock.md3 | `RL3H` `RL3M` `RL3F` `RL3G` | Lock-On Burst mod, **held** |
| 5 | `ModelDef.RLMod2:106` | `0` RLSwitchBase.md3, `2` RLLockSwitch.md3 | `RLL1` `RLL2` `RLL3` | Lock-On **switch animation** (72 frames) |
| 6–10 | `ModelDef.RL_GK` | — | — | the shared five |
| 11 | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | ledge grab |
| 12 | `ModelDef.Weapon.pickups.def` | `0` RLBase.md3 | `WPPK` | world pickup |

RL is the cleanest class in the pack: one single-surface base mesh, both mods
additive at MODEL 2, both switch animations present.

### D4BFGGUN (BFG9000) — 7 blocks

| # | File | Meshes | Sprites | What it is |
|---|---|---|---|---|
| 1 | `ModelDef.BFG9000` | `1` BFGBaseBurn.md3, `2` BFGElOrbSin.md3 | `BFGH` 13–22, `BFGM` 0–13, `BFG1` 23–48, `BFG2` 49–74, `BFG3` 75–100, `BFG4` 101–122, `BFF1` 123–148, `BFF2` 149–165, `BFD1` 166–191, `BFD2` 192–200 | **BASE GUN.** 606 FrameIndex rows — the largest block in the pack. Four charge stages, two fire stages, two grenade stages |
| 2–6 | `ModelDef.BFG_GK` | — | — | the shared five |
| 7 | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | ledge grab |

No mods — correct to Doom 2016. **The BFG has no pickup block under its own
class.** The pickup lives under a separate class, `BFG9000Pickup`, in
`ModelDef.Weapon.pickups.def:145`, using the same two meshes at frame 0. That is
the 101st block and the only block whose class is not one of the ten.

### Dumb4gausscannon (GC) — 9 blocks

| # | File | Meshes | Sprites | What it is |
|---|---|---|---|---|
| 1 | `ModelDef.GC` | `1` GCBase.md3, `2` GCBarrel.md3 | `GCNH` 15–21, `GCNM` 0–14, `GCNR` 82–84, `GCNF` 22–47, `GCNG` 48–81 | **BASE GUN.** `GCNR` (ready) sits oddly at the far end of the frame range |
| 2 | `ModelDef.GCMod1` | `1` GCBase, `2` GCSigge.md3 | `GCSH` `GCSM` `GCSR` `GCSF` `GCSG` | Siege Mode mod, **held** — GCBarrel swapped for GCSigge |
| 3–7 | `ModelDef.GC_GK` | — | — | the shared five |
| 8 | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | ledge grab |
| 9 | `ModelDef.Weapon.pickups.def` | `0` GCBase.md3 | `WPPK` | world pickup |

**GC is incomplete in the same way HAR is.** There is no `ModelDef.GCMod2`
(the Precision Bolt mod is absent entirely), and the Siege mod has **no switch
block**, even though `GCSiggeSwitch.md3`, `GCSiggeSwitchBase.md3` and
`GCSiggeSwitch_hands.md3` (all 165 frames) sit unreferenced in the folder.

### D4CHAINSAW (CSAW) — 8 blocks

| # | File | Meshes | Sprites | What it is |
|---|---|---|---|---|
| 1 | `ModelDef.CSAW` | `1` CSAW.md3 | `SAWH` 16–21, `SAWM` 0–15 | **BASE GUN.** 22 frames: raise and swing, nothing else |
| 2–6 | `ModelDef.CSAW_GK` | — | — | the shared five |
| 7 | `ModelDef.LageGrab` | LageGrab.md3 | `CLIM` | ledge grab |
| 8 | `ModelDef.Weapon.pickups.def` | `0` chainsaw.md3 | `WPPK` | world pickup — **a separate 1-frame mesh**, not CSAW.md3 |

---

## 3. Are the mod blocks a different mesh, or the same mesh with different frames?

**Neither, exactly. They are the same base mesh plus a swapped or added
attachment mesh at a different MODEL index.** No mod block anywhere in the pack
substitutes a different *base* mesh for the held gun.

| Class | Mod | Base mesh | What changes |
|---|---|---|---|
| CG | Mod1 Gatling | CGBase.md3 **kept** at MODEL 1 | CGGatling.md3 **added** at MODEL 3 |
| CG | Mod2 Turret | CGBase.md3 **kept** at MODEL 1 | CGBarell.md3 **removed**, CGTurret.md3 at MODEL 2 |
| CSG | Mod1 Bomb | CombatShotGunBase.md3 **kept** at MODEL 0 | Base2 **replaced** by CombatShotGunBomb.md3 |
| CSG | Mod2 Triple | Base + Base2 **both kept** | CombatShotGunTriple.md3 **added** at MODEL 2 |
| PLRF | Mod1 Stun | PLRFBase.md3 **kept** at MODEL 1 | PLRFBase1 **replaced** by PLRFStuntBase.md3 |
| PLRF | Mod2 Heat | PLRFBase.md3 **kept** at MODEL 1 | PLRFBase1 **replaced** by PLRFHeatBase.md3, PLRFBase2 **dropped** |
| RL | Mod1 Det | RLBase.md3 **kept** at MODEL 0 | RLDet.md3 **added** at MODEL 2 |
| RL | Mod2 Lock | RLBase.md3 **kept** at MODEL 0 | RLLock.md3 **added** at MODEL 2 |
| GC | Mod1 Siege | GCBase.md3 **kept** at MODEL 1 | GCBarrel **replaced** by GCSigge.md3 |
| HAR | Mod2 Micro | HARBase.md3 **kept** at MODEL 0 | HARMicro.md3 **added** at MODEL 2 |

The attachment meshes share the base mesh's frame count and are driven by the
same frame index — they are co-animated, not independently timed:

| Attachment | Frames | Base frames |
|---|---|---|
| CGGatling.md3 | 63 | CGBase 63 |
| CGTurret.md3 | 65 | CGBase 63 (block indexes MODEL 2 up to 64) |
| CombatShotGunBomb.md3 | 113 | 113 |
| CombatShotGunTriple.md3 | 113 | 113 |
| PLRFStuntBase.md3 | 109 | 109 |
| PLRFHeatBase.md3 | 109 | 109 |
| RLDet.md3 | 92 | 92 |
| RLLock.md3 | 92 | 92 |
| GCSigge.md3 | 85 | 85 |
| HARMicro.md3 | 67 | HARBase 64 (block indexes MODEL 2 up to 66) |

**The "switch" blocks are different meshes.** Every switch block uses dedicated
`*Switch*.md3` files with their own, shorter frame counts (64–92), and they are
not usable as a held pose.

**Can the mods ship as separately selectable models?** Yes, on these terms:

- Each mod variant is a **2- or 3-mesh composite**, not a single file. Shipping
  one means either emitting multiple `MODEL n` lines in one block, or merging
  the meshes offline.
- All six classes with mods have both held variants fully present. The switch
  animations can be dropped without loss — a static swap never plays them.
- Two mods are missing from the package entirely: **HAR Mod1 (Tactical Scope)**
  and **GC Mod2 (Precision Bolt)**. So the arsenal is 10 base guns + 9 mod
  variants, not 10 + 20.

---

## 4. Per-surface structure, and what actually moves

**The hypothesis in the brief is half right, and the half that is wrong matters.**

Correct: **12 of the 17 base-gun meshes are a single surface.** Correct: there
is **no magazine anywhere in the pack** — no surface and no vertex group
anywhere travels down and clear of a gun, which is the magazine signature.

Wrong: they are not all "animated by vertex animation" in the sense of a
deforming mesh. **Most of them are rigid.** The frame data moves the whole gun
through space and never changes its shape at all. And three of them do contain a
localised internal moving part that *is* separable by motion.

### Method

For each surface, every frame was Kabsch-aligned back onto the ready frame and
the per-vertex residual measured. A surface that the animation only translates
and rotates leaves a residual at the MD3 quantisation floor (~0.016 units,
since MD3 stores vertices as int16/64). A surface that genuinely deforms leaves
a large residual spread across most of its vertices. A surface with one moving
part leaves a large residual confined to a small fraction of them.

Same method `tools_kit/batch.py::survey()` uses. No new tool was written; the
measurement was run as a throwaway script against `tools_kit/md3read.py`.

### Results — base-gun meshes

| Mesh | Surfaces | Max residual | % of size | Verts that moved | Verdict |
|---|---|---|---|---|---|
| Pistol.md3 | 1 `pistol` | 2.48 | 11.9% | 99.1% | **DEFORMS** — the whole gun, skeletal animation baked to vertices |
| CombatShotGunBase.md3 surf0 `praetor.003` | — | 19.85 | 39.2% | 100% | **DEFORMS** — these are the player's arms |
| CombatShotGunBase.md3 surf1 `shotgun.002` | — | 0.02 | 0.9% | — | RIGID (shell) |
| CombatShotGunBase.md3 surf2 `shotgun.001` | — | 0.03 | 0.3% | — | RIGID (standard mod / muzzle piece) |
| CombatShotGunBase.md3 surf3 `shotgun` | — | 0.04 | 0.2% | — | RIGID (the gun body) |
| CombatShotGunBase2.md3 | 1 `shotgun.003` | 0.03 | 0.2% | — | RIGID |
| SuperShotgun.md3 | 1 `double_barrel` | 6.89 | 20.5% | 94.1% | **DEFORMS** — the break-open action, one surface |
| SuperShotgunShells.md3 | 1 `shells` | 15.66 | 52.2% | 86.6% | **DEFORMS** — shells ejecting |
| CGBase.md3 | 1 `chaingun` | 0.04 | 0.1% | — | **RIGID** |
| CGBarell.md3 | 1 `chaingun_rotatior` | 0.03 | 0.1% | — | **RIGID** — it spins as a rigid body |
| HARBase.md3 | 1 `har` | 0.54 | 1.4% | 5.8% | near-rigid — one tiny part, see below |
| PLRFBase.md3 | 1 `plasmarifle` | 0.03 | 0.1% | — | **RIGID** |
| PLRFBase1.md3 | 3 | 0.03 | 0.2% | — | **RIGID** (all three surfaces) |
| PLRFBase2.md3 | 1 `plasmarifle.011` | 0.03 | 0.3% | — | **RIGID** |
| RLBase.md3 | 1 `rocketlauncher_base` | 9.50 | 20.0% | **5.2%** | **INTERNAL PART** |
| BFGBaseBurn.md3 | 2 | 0.04 | 0.1% | — | **RIGID** (both surfaces) |
| BFGElOrbSin.md3 surf0 `bfg_singie` | — | 2.70 | 15.5% | 55.0% | DEFORMS (FX geometry) |
| BFGElOrbSin.md3 surf1 `bfg_orb` | — | 2.96 | 13.1% | 100% | DEFORMS (FX geometry) |
| BFGElOrbSin.md3 surf2 `bfg_electric` | — | 0.81 | 2.7% | 37.7% | DEFORMS (FX geometry) |
| GCBase.md3 | 1 `gauss_rifle_base` | 4.62 | 7.4% | **15.9%** | **INTERNAL PART** |
| GCBarrel.md3 | 1 `gauss_rifle_barrel` | 0.03 | 0.1% | — | **RIGID** |
| CSAW.md3 | 1 `chainsaw` | 0.04 | 0.1% | — | **RIGID** |

### The three internal parts, located

| Mesh | Part bbox (mesh space) | Travel | Active frames | What it is |
|---|---|---|---|---|
| RLBase.md3 | x 0.9…13.6, y −6.3…−4.7, z −2.1…−0.4 (348 of 9358 verts) | 9.50 | 67–91 | mid-body, inside the `RL1F` fire run (27–89) — a breech or loader, not a magazine |
| GCBase.md3 | x 30.6…46.0, y −16.6…−1.7, z −9.4…−4.9 (1105 of 6933 verts) | 4.62 | 22–45 | the muzzle end, exactly the `GCNF` fire run (22–47) — the rail recoiling |
| HARBase.md3 | x 13.6…16.7 (528 of 9113 verts) | **0.54** | 30–31 only | a half-unit flinch over two frames; **too small to be a usable part** |

So RLBase and GCBase could each be carved into body + one moving part with
`tools_kit/md3_carve_surface.py` or `carve_by_ref.py`. Neither part is a
magazine, and neither is driven by a reload — both live inside the fire
animation. **Nothing in the pack gives a reload system anything to drive.**

### The arms problem

`CombatShotGunBase.md3` surface 0 is named `praetor.003` and its embedded shader
is `models_characters_doommarine_playerhands_doommarine_playerhands`. At 5652
verts it is the **largest surface in the mesh** — larger than the shotgun itself
(4086). A full-folder sweep confirms this is the **only gun mesh in the pack
with hands baked in**; all the others keep hands in separate `*_hands.md3`
files.

Every other class turns its hands off by commenting the whole `MODEL` line:

```
//	Skin 0 "MD3/Weapons/Hand.jpg"
//	MODEL 0 "MD3/Weapons/CG_hands.md3"
```

`ModelDef.CSG` cannot do that, because the hands are not a separate model. It
comments out only the skin assignment:

```
//	SurfaceSkin 0 0 "MD3/Weapons/Hand.jpg"
	SurfaceSkin 0 3 "MD3/Weapons/CombatShotgunBase.png"
```

**The arm geometry is still in the draw.** The render at the ready frame (61)
shows them at full size wrapping the gun. Commenting the skin removes the
texture assignment, not the surface. The same is true of
`CombatShotGunBombSwitchBase.md3` and `CombatShotGunTripleSwitchBase.md3`,
which carry the same four surfaces.

### Tags

**No MD3 in the pack has a single tag.** `ntags = 0` on every file read. There
are no attachment points to hang anything off.

---

## 5. The renders

Ten PNGs in `E:\DOOMWork\RS_ModelSwapper\renders_packs\`, each drawn at its
ready frame (not frame 0 — frame 0 is the start of the melee swing in most
classes and shows the gun thrown out of view).

| File | Frame | What I see |
|---|---|---|
| `zion_D4Pistol.png` | 58 | The EMG sidearm in profile, clean and complete. Slab slide, angular frame, underbarrel block, pistol grip and trigger guard all present. One surface, no hands. Reads immediately as a Doom 2016 EMG. |
| `zion_D4SHOTGUN.png` | 61 | **The arms dominate the frame.** A large grey forearm/hand mass (surf0, 5652 v) runs the full width, with the green shotgun body (surf3) sitting on top of it and the orange muzzle piece (surf2) at the right end. The tiny blue shell (surf1) is buried inside. The gun is clearly readable but it is riding inside an arm. |
| `zion_D4SUPERSHOTGUN.png` | 62 | A clean side-by-side double-barrel in profile: long twin barrels, break hinge, grip and a single trigger. One surface. Nothing extraneous. |
| `zion_D4CHAINGUN.png` | 57 | The chaingun receiver and shroud with the carry handle on top and the grip below — but **the front is visibly missing**, because the rotating barrel assembly is a separate mesh (CGBarell.md3, MODEL 2) that this render does not include. Rendering CGBase alone is an incomplete gun. |
| `zion_D4MACHINEGUN.png` | 26 | The HAR in full profile: stock, receiver, box magazine housing, foregrip and a long barrel shroud. The most conventional-looking weapon in the pack. One surface, complete on its own. |
| `zion_D4PLASMARIFLE.png` | 21 | The plasma rifle's outer shell — a wide, open, skeletal frame with a big circular coil housing mid-body, a muzzle fork and two grip points. It reads as a **hollow casing**, because the inner mod hardware lives in PLRFBase1/PLRFBase2 at MODEL 2 and 3, which this render omits. |
| `zion_D4ROCKETLAUNCHER.png` | 27 | The rocket launcher, complete and clean: long tube, side magazine, stock, foregrip and pistol grip. One surface, nothing missing. |
| `zion_D4BFGGUN.png` | 22 | The BFG in grey, complete and self-contained, with the small red `bfg_burn` surface at the muzzle. The FX meshes (orb, electric, sign) are in BFGElOrbSin.md3 at MODEL 2 and are not in this render, so the muzzle looks bare. |
| `zion_Dumb4gausscannon.png` | 21 | The gauss cannon receiver and rail with a prominent carry handle over the top. Like the chaingun, **the front is short**, because GCBarrel.md3 at MODEL 2 is not in the render. |
| `zion_D4CHAINSAW.png` | 21 | The chainsaw, complete: engine block, pull handle, wrap-around brace and a long toothed bar. One surface, 22 frames, the simplest model in the pack. |

Four of the ten (CG, PLRF, BFG, GC) are visibly incomplete when the primary mesh
is rendered on its own. That is a direct consequence of the composite structure
and it is the clearest visual argument for whatever decision is made in §6.1.

---

## 6. What has to be decided before Zion can be imported

### 6.1 Composites: emit multi-MODEL blocks, or merge the meshes offline?

**Six of ten classes are 2–4 mesh composites.** Only EMG, HAR, RL and CSAW are
single-mesh.

The current `ModelSwapper/modeldef` is 239 blocks and **every one of them is a
single mesh with a `Path` line** (`MODEL-lines-per-block: {1: 239}`). So the
shipping donor format has never carried a composite.

The pipeline is not incapable of it, though — `modeldefs_import_ziono.txt`
already contains blocks with `Model 0/1/2` under one `Path`
(`MS_ziono_DeadMarine`). So the choice is real and open:

- **(a) Emit multi-MODEL donor blocks.** Keeps the author's geometry intact.
  Needs the donor emitter and `RS_ForeignModels.zs` to carry more than one mesh
  per donor, and needs one frame index per mesh.
- **(b) Merge each composite into one MD3 at the ready frame.** Fits the existing
  format with no code change. Loses nothing visually for a static swap, because
  at a single frame a composite and its merge are the same geometry. Would need
  a merge step, and **the toolkit has no direct MD3→MD3 merge**: `md3_stack.py`
  stacks *frames*, `md3_extract.py` and `md3_carve_surface.py` take surfaces
  *out*, and `obj2md3.py` writes one surface per OBJ object (so an
  export-to-OBJ-and-recombine route exists, but nothing does it in one step).
  That is the one gap where a new tool may genuinely be needed — flagging it
  rather than writing one.

**This is the first decision and everything else follows from it.**

### 6.2 The shotgun's arms

`CombatShotGunBase.md3` surface 0 is the player's forearms and it is the biggest
surface in the file. Options:

- **Carve surf0 out** with `tools_kit/md3_carve_surface.py`, leaving the three
  gun surfaces. Clean, and the pack is read-only so the carve would write a
  derived mesh into this repo.
- **Accept the arms.** Not viable for a swapped weapon in VR — the player
  already has hands.
- **Use the pickup mesh instead.** `shotgun.md3` (1 frame, 2 surfaces) is a
  separate, arms-free shotgun used by the pickup block. It is a different and
  much simpler mesh. Whether it is good enough to stand in for the HUD gun is a
  judgement call I cannot make from the modeldef — **rendering `shotgun.md3`
  side by side with the carved CombatShotGunBase would settle it** and I did not
  do it because the brief scoped the renders to the ten base-gun meshes.

### 6.3 Which frame to freeze

For the six **rigid** base meshes (CG, PLRF, GC barrel, CSAW, BFG base, and the
shotgun's gun surfaces) the frame makes **no difference at all** — the geometry
is identical at every frame. For **Pistol, SuperShotgun and the shotgun's arms**
the shape genuinely changes and the frame choice is real. The ready frames in
§1 are the right default.

### 6.4 Mods: ship them or not

Nine mod variants exist as held poses (CG ×2, CSG ×2, PLRF ×2, RL ×2, GC ×1,
HAR ×1). Each is "base mesh + attachment", so they cost one extra mesh each and
depend entirely on decision 6.1. Shipping them would take the arsenal from 10
models to 19. Two advertised mods (HAR Scope, GC Precision Bolt) are **not in
the package** and cannot be shipped.

### 6.5 Skins

Four base blocks assign textures **per surface** (`SurfaceSkin <model> <surf>`),
not per model: CSG, PLRF, BFG, and the CSG mod blocks. A flat `Skin 0` line will
not reproduce them. If the composites are merged (6.1b), the surface indices
change and the SurfaceSkin mapping has to be rewritten against the merged mesh.

### 6.6 Transforms

All ten blocks use `Scale -3.0 3.0 3.0` with per-class offsets (§1). The
negative X is a mirror. These are Zion's own HUD numbers and will not survive a
swap — seating has to be re-derived per weapon, the same as any other pack.

### 6.7 Known defects in the source

- `ModelDef.Weapon.pickups.def:109` references `MD3/Weapons/PLRF_hands.md3`,
  which is **absent** from the essential set.
- `ModelDef.HARMod2:90` holds a fully commented-out Scope block referencing
  three files that are **absent** from the package.
- Unreferenced meshes present in the folder: `GK_2.md3`, all the
  `*Switch_hands.md3` files, `GCSiggeSwitch*.md3`, `HARMicroSwitch*.md3`.

### The optional set

`ZionVR-optional` holds three sub-packs:

- **`03_ZionVR_weapons_hands`** — the **same 20 weapon modeldefs** with the hands
  lines **uncommented**, plus ten `*_hands.md3` meshes. Diffs against the
  essential set are one or two lines each and nothing else. This is the
  hands-on variant, and it is **not useful to us** — we want the gun without
  arms.
- **`03_ZionVR_weapons_Slayer_PBR_`** — `Materials/textures/` only. **No meshes
  and no modeldefs.** A PBR texture overlay. It changes nothing about geometry,
  surfaces or frames, so none of this survey changes if it is used.
- **`05_ZionVR_DECORATIONS_Visual_Edition`** — decorations, not weapons. Already
  imported into this repo as `modeldefs_import_ziono.txt`.

### Already in this repo

`modeldefs_import_zion.txt` (446 lines) and `modeldefs_import_ziono.txt` (688
lines) exist, but they cover **the ZionVR player model, projectiles, powerup
sprites and decorations only** — `MS_zion_Player`, `MS_zion_Projectiles`,
`MS_zion_Infrared`, `MS_zion_RadSuit`, `MS_zion_Models`, and ~40
`MS_ziono_*` decorations. **No Zion weapon donor exists.** The weapon side of
the package is genuinely unimported.

---

## Things I could not settle

1. **`CGTZ`** (2 frames, tail of the chaingun turret switch block). I can say
   where it sits but not what state it is. Reading Zion's `Dumb4chaingun`
   ZScript state machine would settle it. That ZScript is outside the package
   folder I was given.
2. **`CSC1`/`CSC2`/`CSC3`** — three one-pose shotgun blocks differing only in
   `CombatShotgunTriple1/2/3.png`. Mechanically certain; the *meaning* (a
   burst-charge indicator) is an inference. Opening the three PNGs would settle
   it.
3. **Whether the shotgun's arm surface actually draws** with no skin assigned.
   The geometry is unquestionably in the file and in the frame — I measured and
   rendered it. What GZDoom does with a surface that has no `SurfaceSkin` and no
   `Skin` is an engine question I did not test. Either way the surface is there
   and should be carved, so this does not change the recommendation.

## Reproducing this

- Block inventory: parse each `ModelDef.*`, take blocks opening with
  `Model <class>` at line start, collect uncommented `MODEL n "path"`,
  `Skin n`, `SurfaceSkin m n` and all `FrameIndex <sprite> <frame> <model> <idx>`
  rows. 101 blocks, totals in §1.
- Surface structure: `tools_kit/md3read.py <mesh>.md3`.
- Motion: Kabsch-stabilise every frame onto the ready frame and measure the
  per-vertex residual (the method in `tools_kit/batch.py::survey()`).
- Renders: `python render.py <mesh>.md3 <ready frame> renders_packs/zion_<class>.png 0`
  with `IDLE=<ready frame>` in the environment.
