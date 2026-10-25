// ModelSwapper's own reload foley. Every name is under ms/, so it cannot collide with a
// name the loaded mod defines (a bare Pistol/Reload1 would, and the last definition wins
// silently, on load order). The files are the owner's: RS_VR_Weapons (sounds/pistols) and
// RS_VR_Reload (the magazine landing). Rows for BD22Q guns are named by tools_kit/lift_bd22.py.

$random ms/magdrop { ms/magdrop1 ms/magdrop2 ms/magdrop3 }
ms/magdrop1         sounds/ms/DSBOUNC1.ogg
ms/magdrop2         sounds/ms/DSBOUNC2.ogg
ms/magdrop3         sounds/ms/DSBOUNC3.ogg

// BD22 pistol (RS_VR_Weapons wm/pistolet)
ms/bd22/pistol/magout     sounds/ms/9mmclip1.wav
ms/bd22/pistol/magin      sounds/ms/9mmclip2.wav
ms/bd22/pistol/slideback  sounds/ms/9mmslide.wav
ms/bd22/pistol/slidefwd   sounds/ms/PSNAP.ogg
$volume ms/bd22/pistol/slidefwd 0.8
$alias ms/bd22/pistol/magdrop ms/magdrop

// BD22 Rifle (tools_kit/lift_bd22.py)
ms/bd22/rifle/magout                 sounds/ms/RCOUT.ogg
ms/bd22/rifle/magin                  sounds/ms/RCIN.ogg
ms/bd22/rifle/slideback              sounds/ms/RCKBCK.ogg
ms/bd22/rifle/slidefwd               sounds/ms/RCKFWD.ogg
$alias ms/bd22/rifle/magdrop ms/magdrop

// BD22 BrutalSMG (tools_kit/lift_bd22.py)
ms/bd22/smg/magout                   sounds/ms/RCOUT.ogg
ms/bd22/smg/magin                    sounds/ms/RCIN.ogg
ms/bd22/smg/slideback                sounds/ms/rsrslide.wav
ms/bd22/smg/slidefwd                 sounds/ms/rsrsmgfw.wav
$alias ms/bd22/smg/magdrop ms/magdrop

// BD22 MP40 (tools_kit/lift_bd22.py)
ms/bd22/mp40/magout                  sounds/ms/RCOUT.ogg
ms/bd22/mp40/magin                   sounds/ms/RCIN.ogg
ms/bd22/mp40/slideback               sounds/ms/rsrslide.wav
ms/bd22/mp40/slidefwd                sounds/ms/rsrsmgfw.wav
$alias ms/bd22/mp40/magdrop ms/magdrop

// BD22 AssaultShotgun (tools_kit/lift_bd22.py)
ms/bd22/assaultshotgun/magout        sounds/ms/RCOUT.ogg
ms/bd22/assaultshotgun/magin         sounds/ms/RCIN.ogg
ms/bd22/assaultshotgun/slideback     sounds/ms/RCKBCK.ogg
ms/bd22/assaultshotgun/slidefwd      sounds/ms/RCKFWD.ogg
$alias ms/bd22/assaultshotgun/magdrop ms/magdrop

// BD22 RailGun (tools_kit/lift_bd22.py)
ms/bd22/railgun/magout               sounds/ms/PLCOUT.ogg
ms/bd22/railgun/magin                sounds/ms/PLCIN.ogg
$alias ms/bd22/railgun/magdrop ms/magdrop

// BD22 Plasma_Gun (tools_kit/lift_bd22.py)
ms/bd22/plasmagun/magout             sounds/ms/PLCOUT.ogg
ms/bd22/plasmagun/magin              sounds/ms/PLCIN.ogg
$alias ms/bd22/plasmagun/magdrop ms/magdrop

// BD22 Sniper (tools_kit/lift_bd22.py)
ms/bd22/ruger/magout                 sounds/ms/RCOUT.ogg
ms/bd22/ruger/magin                  sounds/ms/RCIN.ogg
ms/bd22/ruger/slideback              sounds/ms/RCKBCK.ogg
ms/bd22/ruger/slidefwd               sounds/ms/RCKFWD.ogg
$alias ms/bd22/ruger/magdrop ms/magdrop

// BD22 Rocket_Launcher (tools_kit/lift_bd22.py)
ms/bd22/rocketlauncher/magout        sounds/ms/RLCOUT.ogg
ms/bd22/rocketlauncher/magin         sounds/ms/RLCIN.ogg
$alias ms/bd22/rocketlauncher/magdrop ms/magdrop

// BD22 Shot_Gun pump (tools_kit/lift_bd22.py)
ms/bd22/shotgun/shellin              sounds/ms/SHOTLOAD1.ogg
ms/bd22/shotgun/pumpback             sounds/ms/shotcycle.wav
$alias ms/bd22/shotgun/shelldrop ms/magdrop
