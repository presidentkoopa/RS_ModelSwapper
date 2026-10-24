RS_Brutal22WeaponsQ -- bd22q 1.97-pre
=====================================

VR hands, hand-driven reloading and VR melee for Brutal Doom v22, on stock QuestZDoom 17.3.
An ADDON: it needs Brutal Doom loaded, it replaces none of its guns, and with its options off it
behaves as Brutal Doom shipped.


LOAD ORDER
----------
    doom2.wad  ->  brutal22test6.pk3  ->  BD_VoxelPack.pk3  ->  BD22Q_197pre.pk3

Doom 2, not Freedoom: BD_VoxelPack's voxeldef names Doom 2's own sprites and Freedoom fails on it.
No engine changes. Stock QuestZDoom 17.3.


WHAT IT ADDS
------------
Hands on every Brutal Doom gun, and reloading you do WITH YOUR HANDS instead of a keypress:

  magazine    12 guns -- Rifle, Pistol, SMG, MP40, Assault Shotgun, Railgun, Plasma,
              Sniper, Rocket Launcher, and (new in 1.97) the MG42's belt drum, the
              Flamethrower's canister and the Unmaker's skull
  pump        the Shotgun
  break-open  the SSG, the Grenade Launcher, the Shotvolver, and the slug revolver

Take the magazine out with your off hand, bring a fresh one up, push it home. Break guns swing
open, take a round at a time or a speedloader, and a flick of the wrist shuts them.

NEW IN 1.97
  * The MG42 belt drum, the Flamethrower canister and the Unmaker skull now reload. Brutal Doom
    never reloads those three; the parts were carved out of their own meshes to do it.
  * The BD21 MACHINEGUN (M249 with an over-under launcher), on slot 4. Its launcher is loaded by
    hand. Menu row: "Machinegun replaces MG42".
  * The BD21 SLUG REVOLVER, on slot 2 beside the Shotvolver. Menu row: "Slug revolver replaces
    Shotvolver".
  * Both revolvers take a SPEEDLOADER or a ROUND AT A TIME, your choice: "Shot/Revolver Reload".
  * VR MELEE with a gun in your hands -- see below.


MELEE
-----
  GUN BASH          your kick key, with a gun in your hands, bashes with the gun instead of
                    kicking. Brutal Doom's own kick damage; the boot is simply not drawn.
                    Pick its impact effect and its colour in the menu.
  PISTOL WHIP       swing a pistol or a revolver and it hits what it passes through.
  BUTT STRIKE       drive the stock of a rifle or shotgun forward with both hands on it.
                    OFF by default -- two hands on a rifle is also how you aim one, so this is
                    the one most likely to go off when you did not mean it. Turn it on and judge.
  FISTS             a real punch with either hand, and punching a switch works it.
  AXE / DRAGONSLAYER  swing them; two hands and the edge leading bite harder.

Out of VR, or with these turned off, Brutal Doom's own melee is untouched.


OPTIONS
-------
Options -> BD22 VR Weapons. 30 rows, including Reloading (VR or Stock), what grabs the
ammo, where a new magazine comes from, reload assist, the per-gun scopes, the dual-wield and
voxel pages, and "Reload: tuning and debug" for the capture zones and a step-by-step print.

Every option defaults to how Brutal Doom behaves, or to the gentler setting, except the VR hands
and reloading themselves. Turn Reloading to "Stock (BD22)" and the guns reload as they always did.


CREDITS
-------
Brutal Doom v22 is Sergeant_Mark_IV's; this pack is an addon to it and ships none of its guns.
The hands and much of the art are Ermac's (Rusted Legacy, MIT -- see
models/rsq/LICENSE_RustedLegacy_MIT.txt). The engine this targets is Emawind's QuestZDoom.
Reload foley the mod itself has none of comes from RS_VR_Weapons.
The BD21 Machinegun and slug revolver are Brutal Doom 21's, brought forward.


KNOWN GAPS
----------
  * A dropped partial drum costs the reserve nothing.
  * The Shotvolver's cylinder has five chambers and a capacity of six; that is how Brutal Doom
    counts it, and loading a round at a time inherits it.
  * The Machinegun's HUD is its model: its sprite lumps are placeholders.

Built from the RSQ Weapon Depot. Every number in it is measured off a mesh or parsed out of the
parent mod -- sets/bd22q_1.97/PROVENANCE.txt says what came from where and how to rebuild it.
