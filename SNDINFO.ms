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
