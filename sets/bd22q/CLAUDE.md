# RS_Brutal22WeaponsQ: standing rules (owner: presidentkoopa)

**This is BD22 rebuilt for VR. Its weapon code is ours to change.** (owner, 2026-10-27)
It started as fun 3D models and a few alt fires. Hand reloading and hands on the guns changed the
scope: the weapon code is now changed wherever that gives better VR mechanics. This is not an official
Brutal Doom release, so nothing in BD22's code is off limits. The limit is identity: the shotgun is
still a shotgun and the rifle still a rifle (same role, same feel, same balance). They just do more
for VR now.

- Where a gun's code and its 3D mesh disagree in VR (where the shot starts, the grip, the reload), we change
  the code to fit the mesh and the hands, not the other way around. Example (2026-10-27): the Flamethrower's
  flame starts at the drawn nozzle tip, and the nozzle is never tilted away from the stream.
- BD22's own features stay as they ship (e.g. the plasma gun's one alt fire: we don't touch it). New
  VR-only mechanics, such as a 6DoF homing attack, are allowed: we may build one, or decide not to. Each
  one is the owner's call, never added by default.
- QuestZDoom 17.3 is never changed (no engine changes); everything is done in ZScript/DECORATE.
- Work happens in this repo. When the set is finished, it is copied into RSQ_WeaponDepot (the workshop:
  meshes, rig, tools; never shipped to players).
- Before anything goes to the owner's headset, it must run on his load order with no script errors:
  doom2 -> brutal22test6 -> BD_VoxelPack -> this pack.

## Never call something working that has not been SHOWN working (owner, 2026-10-27)
The Ruger's "Real" scope was reported as working for a week. Nobody ever showed the magnified view in the lens, on the rig or in the headset, and in the owner's headset it was fake glass. That is not allowed again.
- **Working means shown working:** in-engine frames or a log of the behaviour itself, not "the code exists", "it compiles" or "the option is there".
- **VR-only behaviour is labelled "rig only, not headset-confirmed"** until the owner confirms it in his headset.
- **Option names promise only what has been proved.**
- **Scope:** the owner wants his scope (2026-10-27 07:30: "I want my scope"). It is being made to work and SHOWN working on the rig first.
