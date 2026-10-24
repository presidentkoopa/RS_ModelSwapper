# RSQ Weapon Depot

**VR weapon sets for Doom, on the stock QuestZDoom engine.**

Hands on the gun. Reloading you do by pulling the magazine out and pushing a fresh one home.
Melee that reads your arm. Brass that leaves the port it is supposed to leave. On a standalone
headset, with no patched engine and no fork required.

The flagship is **bd22q 1.99** — Brutal Doom v22 in VR, as an addon. Brutal Doom stays Brutal
Doom: this loads after it, replaces none of its guns, and with its options off behaves exactly
as it shipped.

---

## Where this came from

**TeamBeef** brought Doom to VR and built the community that made the rest of it possible.
Everyone here found it through them.

**Emawind's QuestZDoom** is the engine these sets target — the one that put GZDoom on a
standalone headset. **Ermac's DoomXR** is the other half of the lineage, and the hands you wear
are his.

**REMA**, our own GZDoom fork, is named for the two of them — e**R**mac and **EMA**wind. REMA is
where VR reloading was worked out: real magazines, measured wells, a hand that takes hold of a
part and moves it.

**This repo is that work coming back.** Everything REMA taught us, carried to the stock engine
and made to run there, a little more of it each release. Where stock cannot do what REMA does,
the pack says so plainly instead of faking it.

---

## The rule that shapes everything

> **Every number is measured off a mesh, or parsed out of the parent mod. Nothing is retyped,
> and nothing is guessed.**

Where that was inconvenient it was still followed, and where a source turned out to be a guess it
was thrown away rather than shipped:

- Every gun's **ejection port** comes off its own mesh — the surface the model-maker named, or
  the hole itself, found by welding the ready frame and walking the edges that belong to one
  triangle. REMA's cards carry an `ejectport` for all 25 guns and every one of them is annotated
  *"the point and the direction are estimates"*, so none of them were used.
- Every gun's **recoil** comes from free-recoil arithmetic on its own cartridge — bullet weight,
  muzzle velocity, powder charge, the loaded gun's weight. An MG42 and a Kar98k fire the same
  round out of a 25 lb gun and a 9 lb gun, and the numbers say so.
- Every gun's **impact weight** is the authored per-pellet value. A weight derived from kinetic
  energy looked principled and was wrong on every shotgun by a factor of fifteen, because the
  engine raises its hitscan event once per *pellet* and a shotgun fires nine.
- Every **ready frame** is found by rigid fit against a reference mesh, and the answer is
  accepted at residual 0.0000 or not at all.

---

## What is in here

| set | state |
|---|---|
| `sets/bd22q_1.97` | **bd22q 1.99**, the flagship. Brutal Doom v22. |
| `sets/vanilla_0.9` | Doom's own arsenal |
| `sets/plus_0.7` | Vanilla+ |
| `sets/modern_0.9` | modern firearms |
| `sets/aliens` | Aliens |

Each set is a readable `src/` tree with a `PROVENANCE.txt` saying what came from where. Nothing
in a set is hand-written: `tools/bd22_plus.py` generates it in sixteen stages and a pre-commit
hook refuses a commit where `src/` does not match what the generators produce.

---

## bd22q 1.99, in short

- **Hand reloading** on 17 guns — magazine, pump and break-open. Including the MG42's belt drum,
  the Flamethrower's canister and the Unmaker's skull, which Brutal Doom never reloads at all.
- **Melee**: gun bash, pistol whip, butt strikes on all eight stocked guns, fists either hand,
  axe and Dragonslayer. It reads your arm, not your body — walking and turning are subtracted.
- **Per-gun ballistics** behind a Stock / Low / Max switch: recoil on 22 guns, muzzle flash on 18,
  flash tails on 14 with separate indoor and outdoor recordings, the round in flight on 11,
  impact sound by material, per-gun ricochet, and brass out of the right port three different ways.
- **Two guns brought forward from Brutal Doom 21**: the Machinegun and the slug revolver.

The pack's own README, shipped inside the pk3, has the detail — including a section on what the
stock engine **cannot** do and why.

---

## Building

```
python tools/bd22_plus.py geometry apply ...      # 16 stages, see HANDOFF.md
python tools/bd22_plus.py sync                    # copy to the set, stamp it
python tools/bd22_plus.py pk3 dist/BD22Q_199.pk3
sh gate/bd22_gate.sh dist/BD22Q_199.pk3           # headless load test
```

`HANDOFF.md` has the full stage order and why it matters. `PLAN.md` is the only plan.

The gate is a **load** test: it proves the pack parses, starts a map, fires every gun and quits
clean. It proves nothing about how anything feels, and it cannot run the VR code at all — melee
and the hands return early outside a headset. That part is the owner's.

---

## Credits

Brutal Doom v22 is **Sergeant_Mark_IV's**. It is the mod that reinvented Doom and brought a
generation back to it; everything here is an addon to it and ships none of its guns.

**TeamBeef** — Doom in VR, and the community.
**Emawind** — QuestZDoom, the engine.
**Ermac** — DoomXR, and the hands (Rusted Legacy, MIT).

The BD21 Machinegun and slug revolver are Brutal Doom 21's, brought forward. Reload foley, impact
and tail sounds the mod itself has none of come from RS_Ballistics and RS_VR_Weapons.
