# Welding the hands into the gun — what it is, and what to ask the designer for

**Date:** 2026-10-24
**For:** PresidentKoopa, to talk through with the modeller

---

## The problem it solves

A VR hand is not attached to the gun. It is a separate model on its own psprite layer, and the
engine has no way to parent one layer to another. So the hand has no position of its own — it
has an *answer*, which the renderer asks for by calling `ModifyBobLayer3D` once per layer per
rendered frame, about 72 times a second.

That has a cost we hit hard on 2026-10-23: because every hand's position is a computed answer
rather than a stored fact, **one fault anywhere in that function loses every hand on every gun
at once**. A single bad line took thirty grips down together. A stored position would have
survived it.

It is also the reason `gunmoves.zs` exists at all: when the gun's own mesh frame moves (recoil,
a reload), the hand has to be *told* to move with it, frame by frame, from a generated table.

## The idea

Merge the posed hand into the gun's own MD3, as extra surfaces.

Then the hand is at the grip because **that is where its vertices are**. No layer, no hook, no
per-frame question, nothing to compute and nothing to fail. The gun's MODELDEF places the gun,
and the hand comes with it.

### What falls out for free

| today | welded |
|---|---|
| hand placed every frame from a table | hand is part of the mesh |
| `gunmoves.zs` tells the hand how the gun's frame moved | hand moves with the gun because it *is* the gun |
| a script fault loses every hand | geometry cannot throw |
| trigger finger = a second layer with its own pose | a different frame of the same mesh |
| three layers per gun | one, and only for the free hand |

The one hand that still needs a layer is the **free hand on the off controller** — that one
genuinely moves on its own: it carries magazines, punches, grabs charging handles. Everything
on the gun side stops being dynamic.

### The real cost, stated plainly

Baking kills iteration. Today a grip is a number you edit and reload in seconds. Welded, a grip
is a mesh you rebuild. That is fine for a finished weapon and miserable while fitting one.

**So the shape is both: fit with layers, ship welded.** The fitting tools do not change at all.
When a gun is signed off, a merge step bakes the hand in and that gun stops depending on any
per-frame answer forever. The kit already has the mesh surgery for this — `md3_extract.py`
pulls surfaces out of a model; merge is the same machinery pointed the other way.

---

## What to actually ask the designer for

The merge itself is ours — the designer does **not** need to model hands, and should not. The
hand pose comes out of the fitting tools and gets baked in afterwards.

But there is one thing they can give us that would remove most of the guesswork, and it costs
them almost nothing:

### Three markers on the gun

Small named objects (or empties) placed on the model, which we read and then delete:

| name | where |
|---|---|
| `grip` | the centre of the firing hand's grip — where the web of the hand sits against the backstrap |
| `trigger` | the face of the trigger, where the fingertip touches it |
| `support` | where the off hand belongs — the forend, the pump, the foregrip, the magwell. Omit on a pistol |

Why it matters: right now we *infer* those from the mesh — find the grip by taking a slab of
geometry behind the trigger and below the slide, and hope. It works, and it is the single
biggest source of back-and-forth. Three markers turn a solve into a lookup, and the person who
modelled the gun knows exactly where they go.

If markers are awkward, the fallback is just as useful: **one screenshot of the gun with the
three points circled**, and real dimensions for them.

### And the thing already in the asset spec

Everything in `QuestWeapon_Asset_Spec_2026-10-23.md` still applies and matters more than any of
this — above all that **every part that moves is its own named object**. A welded hand does not
help a gun whose magazine cannot come out.

---

## Honest summary for the conversation

- We are not asking them to model hands.
- We are asking for three markers, which is maybe ten minutes per gun.
- In exchange, hand fitting stops being a guess, and once a gun is final its hands stop being
  something that can break.
