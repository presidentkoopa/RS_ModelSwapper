# RSQ Weapon Depot

### Reach down. Pull the magazine out. Slap a fresh one home. In Doom. On a headset with no wires and no PC.

Not a menu. Not a button that plays a reload animation. Your actual hand, closing on the actual
magazine in the actual mesh, and dragging it out of the well.

And then the brass comes out of the port the gun really has — because somebody went and found
the hole in the model.

The flagship is **bd22q 1.99**: **Brutal Doom v22 in VR**, as an addon. Brutal Doom stays Brutal
Doom. This loads after it, replaces none of its guns, and with its switches off behaves exactly
as it shipped. Turn them on and you are holding it.

<!-- CLIP GOES HERE -->

---

## The part nobody does

Anyone can bolt a hand onto a gun. Here is the stuff that took the month.

**The MP40's ejection port does not exist, so we built one — and the geometry agreed with a
human being.** Every slot in that receiver tube is mirrored: they are cooling slots, not a port.
The one unmirrored opening is on the *left*, which on an MP40 is the cocking handle. So the port
was constructed from two surfaces that *are* modelled — `zamek`, the bolt, trimmed to its core
so its charging handle wouldn't drag the axis, and `korpus`, the receiver — intersected on the
bore line, where a blowback gun ejects. It landed at **68% of the gun's length**. The BrutalSMG's
port, which a human had placed by eye in a headset months earlier, sits at **68% of that gun**.
Two guns, two completely different methods, same answer.

**An M249 ejects downward, and that fact hid two guns for a week.** The port finder filtered for
side-facing holes, which is most guns — and is also exactly how you make every belt-fed weapon in
the set invisible. The MG42 and the Machinegun were both written off as "no port in the mesh".
Both have one. They throw at your feet. Drop the filter and the Machinegun's chute is right
there: 7.1 × 10.2, centred, below the bore, by the breech. Eleven guns now throw from the real
hole, up from nine.

**The Minigun throws from the body, and it always will.** Every down-facing loop on it is
structural — the rotating body's own open ends, the grip, the six bores. There is no bolt, no
breech, nothing to construct from. So nothing was invented, and the file says so. That is the
whole ethic in one gun.

**A shotgun was hitting fifteen times too hard and looked completely fine.** Impact weight had
been derived from kinetic energy — principled, defensible, wrong. The engine raises its hitscan
event **once per pellet**, and a shotgun fires nine. The number that works is the authored
per-pellet value, and it took reading the caller to see it.

**The MG42 fires 7.92×57 Mauser and we do not have a 7.92 mesh.** The nearest thing on the shelf
is a 9mm case scaled up 1.35× — a 25.9 mm round, which is not a Mauser. So the MG42 wears the
7.62: the closest *real* measured mesh there is. And the table says that is what happened,
instead of quietly scaling something and calling it correct.

---

## Where this came from

**TeamBeef** brought Doom to VR and built the community that made the rest of it possible.
Everyone here found it through them.

**Emawind's QuestZDoom** is the engine these sets target — the one that put GZDoom on a
standalone headset.

**Ermac is the genesis of this whole line of work.** His **Force Unleashed** pack is what made
hands in Doom VR possible at all — before it, there was no proof the thing could be done, and
everything since is downstream of that pack. **DoomXR** is his. And the hands you are wearing are
his twice over: he **modelled** them and he **posed** them, every pose, by hand. That is not a
weekend's work, and nobody should read this page and think it came for free. It did not. It came
from him.

**REMA**, our own GZDoom fork, is named for the two of them — e**R**mac and **EMA**wind. REMA is
where VR reloading was worked out: real magazines, measured wells, a hand that takes hold of a
part and moves it.

**This repo is that work coming back.** Everything REMA taught us, carried to the *stock* engine
and made to run there, a little more of it each release. No patched binary. No fork required.
Where stock genuinely cannot do what REMA does, the pack says so plainly instead of faking it.

---

## The rule that shapes everything

> **Every number is measured off a mesh, or parsed out of the parent mod.
> Nothing is retyped, and nothing is guessed.**

It sounds like paperwork. It is the reason the thing feels right.

- **Ejection ports** come off the gun's own mesh — the surface the modeller named, or the hole
  itself, found by welding the ready frame and walking the edges that belong to exactly one
  triangle. REMA's cards carry an `ejectport` for all 25 guns, and every one is annotated *"the
  point and the direction are estimates"* — so not one of them was used.
- **Recoil** is free-recoil arithmetic on the gun's own cartridge: bullet weight, muzzle
  velocity, powder charge, weight of the loaded gun. An MG42 and a Kar98k fire the same round out
  of a 25 lb gun and a 9 lb gun, and you feel which is which.
- **Ready frames** are found by rigid fit against a reference mesh, accepted at residual 0.0000
  or not at all. When two models split their surfaces differently, the fit is redone by position
  rather than by vertex order — because an order-identity fit will hand you plausible nonsense
  and never tell you.
- **Casings** are measured: 9mm at 19.2 mm, rifle at 44.7 and 51.0, 12ga at 70.06, each with
  brass, inner wall and primer skinned separately.

---

## bd22q 1.99

- **Hands on all 26 guns.** 17 of them reload by hand — nine magazine, two pump, six break-open.
  That is every reload type Brutal Doom has.
- **Three guns Brutal Doom never reloads at all now do**: the MG42's belt drum (200), the
  Flamethrower's canister (200), the Unmaker's skull (60). Meshes carved by reference against
  REMA's own, residual 0.0000.
- **Melee that reads your arm, not your body.** Gun bash, pistol whip, buttstroke on all eight
  stocked guns, fists with either hand, axe, Dragonslayer. Walking, turning and teleporting are
  subtracted out, so a snap-turn is not a swing.
- **Per-gun ballistics**, behind a Stock / Low / Max switch: recoil on 22 guns, muzzle flash on
  18, flash tails on 14 with separate indoor and outdoor recordings chosen by whether there is
  sky above the muzzle, the round visibly in flight on 11, impact sound by material, per-gun
  ricochet, impact lights.
- **Real 3D brass on 12 guns**, leaving the real port, at the real size, lent per instance — so
  one `EmptyBrass` is four different cartridges depending on which gun threw it.
- **Two guns brought forward from Brutal Doom 21**: the Machinegun and the slug revolver, each
  with its own menu row.
- **Dual wielding on 10.**

Every one of those switches defaults to something sane, and all of them turn off.

---

## What is in here

| set | what |
|---|---|
| `sets/bd22q_1.97` | **bd22q 1.99** — the flagship. Brutal Doom v22. |
| `sets/vanilla_0.9` | Doom's own arsenal, Doom's own numbers |
| `sets/plus_0.7` | Vanilla+ |
| `sets/modern_0.9` | modern firearms |
| `sets/aliens` | Aliens |

Nothing in a set is hand-written. `tools/bd22_plus.py` generates it in nineteen stages, each set
carries a `PROVENANCE.txt` saying what came from where, and a pre-commit hook refuses any commit
where `src/` does not match what the generators produce. You cannot sneak a number in here.

---

## Building

```sh
python tools/bd22_plus.py geometry apply ...      # 19 stages, order in HANDOFF.md
python tools/bd22_plus.py sync                    # copy into the set, stamp it
python tools/bd22_plus.py pk3 dist/BD22Q_199.pk3
sh gate/run_set.sh gate/bd22q.gate dist/BD22Q_199.pk3
```

That last line is worth a word. **The gate makes the engine play itself.** GZDoom's console
chains commands with `;` and has a `wait N` in tics, and `+attack` and `+reload` are the same
commands your keybinds fire — so one long argument gives the engine every gun, switches to each,
holds the trigger, reloads, and quits, writing the whole thing to a log. It is how every "18
guns, 157 times" claim in this repo's history was actually checked rather than asserted.

`gate/GATING_A_SET.md` is the method, including the eight separate ways it can pass while testing
absolutely nothing — all eight found here, each with the fix. Point it at your own set with a
twelve-line config.

`HANDOFF.md` is the state of everything. `PLAN.md` is the only plan.

---

## Credits

Brutal Doom v22 is **Sergeant_Mark_IV's**. It is the mod that reinvented Doom and brought a
generation back to it. Everything here is an addon to it and ships none of its guns.

**Ermac** — **he started this.** The Force Unleashed pack that made hands in Doom VR possible,
DoomXR, and the hands in this pack end to end: modelled by him, and posed by him, every pose
(Rusted Legacy, MIT). None of this exists without that work.
**TeamBeef** — Doom in VR, and the community that grew around it.
**Emawind** — QuestZDoom, the engine all of this runs on.

The BD21 Machinegun and slug revolver are Brutal Doom 21's, brought forward. Reload foley, impact
and tail sounds that the mod itself has none of come from RS_Ballistics and RS_VR_Weapons.
