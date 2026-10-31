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

// BD22 SSG break-open (tools_kit/lift_bd22.py)
ms/bd22/ssg/open                     sounds/ms/DSDBOPN.ogg
ms/bd22/ssg/load                     sounds/ms/CLIPINSS.ogg
ms/bd22/ssg/close                    sounds/ms/DSDBCLS.ogg
$alias ms/bd22/ssg/rounddrop ms/magdrop

// BD22 Revolver break-open (tools_kit/lift_bd22.py)
ms/bd22/revolver/open                sounds/ms/DBOPN.ogg
ms/bd22/revolver/load                sounds/ms/DBLOD.ogg
ms/bd22/revolver/close               sounds/ms/DBCLS.ogg
$alias ms/bd22/revolver/rounddrop ms/magdrop

// BD22 GrenadeLauncher break-open (tools_kit/lift_bd22.py)
ms/bd22/m79/open                     sounds/ms/DSGROPEN.ogg
ms/bd22/m79/load                     sounds/ms/DSGRLOAD.ogg
ms/bd22/m79/close                    sounds/ms/DSGRCLOS.ogg
$alias ms/bd22/m79/rounddrop ms/magdrop

// ---- Aliens set (tools_kit/lift_aliens.py)
// Aliens M4A3Pistol_3D (tools_kit/lift_aliens.py)
$alias ms/aliens/pistol/magout ms/bd22/pistol/magout
$alias ms/aliens/pistol/magin ms/bd22/pistol/magin
$alias ms/aliens/pistol/slideback ms/bd22/pistol/slideback
$alias ms/aliens/pistol/slidefwd ms/bd22/pistol/slidefwd
$alias ms/aliens/pistol/magdrop ms/magdrop
// Aliens PulseRifle_3D (tools_kit/lift_aliens.py)
$alias ms/aliens/rifle/magout ms/bd22/rifle/magout
$alias ms/aliens/rifle/magin ms/bd22/rifle/magin
ms/aliens/rifle/slideback            sounds/ms/rsrboltbk.ogg
ms/aliens/rifle/slidefwd             sounds/ms/rsrboltfw.ogg
$alias ms/aliens/rifle/magdrop ms/magdrop
// Aliens Smartgun_3D (tools_kit/lift_aliens.py)
$alias ms/aliens/smartgun/magout ms/bd22/rifle/magout
$alias ms/aliens/smartgun/magin ms/bd22/rifle/magin
$alias ms/aliens/smartgun/magdrop ms/magdrop
// Aliens M240Flamethrower_3D (tools_kit/lift_aliens.py)
$alias ms/aliens/flamer/magout ms/bd22/rocketlauncher/magout
$alias ms/aliens/flamer/magin ms/bd22/rocketlauncher/magin
$alias ms/aliens/flamer/magdrop ms/magdrop
// Aliens NewShotgun_3D (tools_kit/lift_aliens.py)
$alias ms/aliens/shotgun/shellin ms/bd22/shotgun/shellin
$alias ms/aliens/shotgun/pumpback ms/bd22/shotgun/pumpback
$alias ms/aliens/shotgun/shelldrop ms/magdrop

// ---- card-regenerated guns (tools_kit/regen_rows.py)
$alias ms/card/ae_m260b/magout ms/bd22/pistol/magout
$alias ms/card/ae_m260b/magin ms/bd22/pistol/magin
$alias ms/card/ae_m260b/slideback ms/bd22/pistol/slideback
$alias ms/card/ae_m260b/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/ae_m260b/magdrop ms/magdrop
$alias ms/card/ae_m41a/magout ms/bd22/pistol/magout
$alias ms/card/ae_m41a/magin ms/bd22/pistol/magin
$alias ms/card/ae_m41a/slideback ms/bd22/pistol/slideback
$alias ms/card/ae_m41a/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/ae_m41a/magdrop ms/magdrop
$alias ms/card/ae_m4a3/magout ms/bd22/pistol/magout
$alias ms/card/ae_m4a3/magin ms/bd22/pistol/magin
$alias ms/card/ae_m4a3/slideback ms/bd22/pistol/slideback
$alias ms/card/ae_m4a3/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/ae_m4a3/magdrop ms/magdrop
$alias ms/card/ae_m56/magout ms/bd22/pistol/magout
$alias ms/card/ae_m56/magin ms/bd22/pistol/magin
$alias ms/card/ae_m56/slideback ms/bd22/pistol/slideback
$alias ms/card/ae_m56/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/ae_m56/magdrop ms/magdrop
$alias ms/card/bd_assaultshotgun/magout ms/bd22/rifle/magout
$alias ms/card/bd_assaultshotgun/magin ms/bd22/rifle/magin
$alias ms/card/bd_assaultshotgun/slideback ms/bd22/rifle/slideback
$alias ms/card/bd_assaultshotgun/slidefwd ms/bd22/rifle/slidefwd
$alias ms/card/bd_assaultshotgun/magdrop ms/magdrop
$alias ms/card/bd_buzzsaw/magout ms/bd22/rifle/magout
$alias ms/card/bd_buzzsaw/magin ms/bd22/rifle/magin
$alias ms/card/bd_buzzsaw/slideback ms/bd22/rifle/slideback
$alias ms/card/bd_buzzsaw/slidefwd ms/bd22/rifle/slidefwd
$alias ms/card/bd_buzzsaw/magdrop ms/magdrop
$alias ms/card/bd_flamethrower/magout ms/bd22/rocketlauncher/magout
$alias ms/card/bd_flamethrower/magin ms/bd22/rocketlauncher/magin
$alias ms/card/bd_flamethrower/slideback ms/bd22/rifle/slideback
$alias ms/card/bd_flamethrower/slidefwd ms/bd22/rifle/slidefwd
$alias ms/card/bd_flamethrower/magdrop ms/magdrop
$alias ms/card/bd_mp40/magout ms/bd22/pistol/magout
$alias ms/card/bd_mp40/magin ms/bd22/pistol/magin
$alias ms/card/bd_mp40/slideback ms/bd22/pistol/slideback
$alias ms/card/bd_mp40/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bd_mp40/magdrop ms/magdrop
$alias ms/card/bd_pistol/magout ms/bd22/pistol/magout
$alias ms/card/bd_pistol/magin ms/bd22/pistol/magin
$alias ms/card/bd_pistol/slideback ms/bd22/pistol/slideback
$alias ms/card/bd_pistol/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bd_pistol/magdrop ms/magdrop
$alias ms/card/bd_plasma/magout ms/bd22/pistol/magout
$alias ms/card/bd_plasma/magin ms/bd22/pistol/magin
$alias ms/card/bd_plasma/slideback ms/bd22/pistol/slideback
$alias ms/card/bd_plasma/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bd_plasma/magdrop ms/magdrop
$alias ms/card/bd_railgun/magout ms/bd22/pistol/magout
$alias ms/card/bd_railgun/magin ms/bd22/pistol/magin
$alias ms/card/bd_railgun/slideback ms/bd22/pistol/slideback
$alias ms/card/bd_railgun/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bd_railgun/magdrop ms/magdrop
$alias ms/card/bd_rifle/magout ms/bd22/rifle/magout
$alias ms/card/bd_rifle/magin ms/bd22/rifle/magin
$alias ms/card/bd_rifle/slideback ms/bd22/rifle/slideback
$alias ms/card/bd_rifle/slidefwd ms/bd22/rifle/slidefwd
$alias ms/card/bd_rifle/magdrop ms/magdrop
$alias ms/card/bd_rpg/magout ms/bd22/rocketlauncher/magout
$alias ms/card/bd_rpg/magin ms/bd22/rocketlauncher/magin
$alias ms/card/bd_rpg/slideback ms/bd22/rifle/slideback
$alias ms/card/bd_rpg/slidefwd ms/bd22/rifle/slidefwd
$alias ms/card/bd_rpg/magdrop ms/magdrop
$alias ms/card/bd_smg/magout ms/bd22/pistol/magout
$alias ms/card/bd_smg/magin ms/bd22/pistol/magin
$alias ms/card/bd_smg/slideback ms/bd22/pistol/slideback
$alias ms/card/bd_smg/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bd_smg/magdrop ms/magdrop
$alias ms/card/bd_unmaker/magout ms/bd22/plasmagun/magout
$alias ms/card/bd_unmaker/magin ms/bd22/plasmagun/magin
$alias ms/card/bd_unmaker/slideback ms/bd22/rifle/slideback
$alias ms/card/bd_unmaker/slidefwd ms/bd22/rifle/slidefwd
$alias ms/card/bd_unmaker/magdrop ms/magdrop
$alias ms/card/bw_1911/magout ms/bd22/pistol/magout
$alias ms/card/bw_1911/magin ms/bd22/pistol/magin
$alias ms/card/bw_1911/slideback ms/bd22/pistol/slideback
$alias ms/card/bw_1911/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bw_1911/magdrop ms/magdrop
$alias ms/card/bw_bar/magout ms/bd22/pistol/magout
$alias ms/card/bw_bar/magin ms/bd22/pistol/magin
$alias ms/card/bw_bar/slideback ms/bd22/pistol/slideback
$alias ms/card/bw_bar/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bw_bar/magdrop ms/magdrop
$alias ms/card/bw_luger/magout ms/bd22/pistol/magout
$alias ms/card/bw_luger/magin ms/bd22/pistol/magin
$alias ms/card/bw_luger/slideback ms/bd22/pistol/slideback
$alias ms/card/bw_luger/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bw_luger/magdrop ms/magdrop
$alias ms/card/bw_mp40/magout ms/bd22/pistol/magout
$alias ms/card/bw_mp40/magin ms/bd22/pistol/magin
$alias ms/card/bw_mp40/slideback ms/bd22/pistol/slideback
$alias ms/card/bw_mp40/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bw_mp40/magdrop ms/magdrop
$alias ms/card/bw_pp41/magout ms/bd22/pistol/magout
$alias ms/card/bw_pp41/magin ms/bd22/pistol/magin
$alias ms/card/bw_pp41/slideback ms/bd22/pistol/slideback
$alias ms/card/bw_pp41/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bw_pp41/magdrop ms/magdrop
$alias ms/card/bw_stg44/magout ms/bd22/pistol/magout
$alias ms/card/bw_stg44/magin ms/bd22/pistol/magin
$alias ms/card/bw_stg44/slideback ms/bd22/pistol/slideback
$alias ms/card/bw_stg44/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bw_stg44/magdrop ms/magdrop
$alias ms/card/bw_tommy/magout ms/bd22/pistol/magout
$alias ms/card/bw_tommy/magin ms/bd22/pistol/magin
$alias ms/card/bw_tommy/slideback ms/bd22/pistol/slideback
$alias ms/card/bw_tommy/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/bw_tommy/magdrop ms/magdrop
$alias ms/card/cx_largezorcher/magout ms/bd22/assaultshotgun/magout
$alias ms/card/cx_largezorcher/magin ms/bd22/assaultshotgun/magin
$alias ms/card/cx_largezorcher/slideback ms/bd22/assaultshotgun/slideback
$alias ms/card/cx_largezorcher/slidefwd ms/bd22/assaultshotgun/slidefwd
$alias ms/card/cx_largezorcher/magdrop ms/magdrop
$alias ms/card/cx_superlargezorcher/magout ms/bd22/assaultshotgun/magout
$alias ms/card/cx_superlargezorcher/magin ms/bd22/assaultshotgun/magin
$alias ms/card/cx_superlargezorcher/slideback ms/bd22/assaultshotgun/slideback
$alias ms/card/cx_superlargezorcher/slidefwd ms/bd22/assaultshotgun/slidefwd
$alias ms/card/cx_superlargezorcher/magdrop ms/magdrop
$alias ms/card/cola_particlegun/magout ms/bd22/plasmagun/magout
$alias ms/card/cola_particlegun/magin ms/bd22/plasmagun/magin
$alias ms/card/cola_particlegun/slideback ms/bd22/rifle/slideback
$alias ms/card/cola_particlegun/slidefwd ms/bd22/rifle/slidefwd
$alias ms/card/cola_particlegun/magdrop ms/magdrop
$alias ms/card/hx_cryogun/magout ms/bd22/pistol/magout
$alias ms/card/hx_cryogun/magin ms/bd22/pistol/magin
$alias ms/card/hx_cryogun/slideback ms/bd22/pistol/slideback
$alias ms/card/hx_cryogun/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/hx_cryogun/magdrop ms/magdrop
$alias ms/card/hx_nuker/magout ms/bd22/plasmagun/magout
$alias ms/card/hx_nuker/magin ms/bd22/plasmagun/magin
$alias ms/card/hx_nuker/slideback ms/bd22/rifle/slideback
$alias ms/card/hx_nuker/slidefwd ms/bd22/rifle/slidefwd
$alias ms/card/hx_nuker/magdrop ms/magdrop
$alias ms/card/hx_pistol/magout ms/bd22/pistol/magout
$alias ms/card/hx_pistol/magin ms/bd22/pistol/magin
$alias ms/card/hx_pistol/slideback ms/bd22/pistol/slideback
$alias ms/card/hx_pistol/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/hx_pistol/magdrop ms/magdrop
$alias ms/card/hx_uzi/magout ms/bd22/pistol/magout
$alias ms/card/hx_uzi/magin ms/bd22/pistol/magin
$alias ms/card/hx_uzi/slideback ms/bd22/pistol/slideback
$alias ms/card/hx_uzi/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/hx_uzi/magdrop ms/magdrop
$alias ms/card/mg_shotgun/magout ms/bd22/pistol/magout
$alias ms/card/mg_shotgun/magin ms/bd22/pistol/magin
$alias ms/card/mg_shotgun/slideback ms/bd22/pistol/slideback
$alias ms/card/mg_shotgun/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/mg_shotgun/magdrop ms/magdrop
$alias ms/card/mg_tec9/magout ms/bd22/pistol/magout
$alias ms/card/mg_tec9/magin ms/bd22/pistol/magin
$alias ms/card/mg_tec9/slideback ms/bd22/pistol/slideback
$alias ms/card/mg_tec9/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/mg_tec9/magdrop ms/magdrop
$alias ms/card/rc_m32/magout ms/bd22/pistol/magout
$alias ms/card/rc_m32/magin ms/bd22/pistol/magin
$alias ms/card/rc_m32/slideback ms/bd22/pistol/slideback
$alias ms/card/rc_m32/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/rc_m32/magdrop ms/magdrop
$alias ms/card/vp_m16/magout ms/bd22/pistol/magout
$alias ms/card/vp_m16/magin ms/bd22/pistol/magin
$alias ms/card/vp_m16/slideback ms/bd22/pistol/slideback
$alias ms/card/vp_m16/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/vp_m16/magdrop ms/magdrop
$alias ms/card/vp_minigun/magout ms/bd22/pistol/magout
$alias ms/card/vp_minigun/magin ms/bd22/pistol/magin
$alias ms/card/vp_minigun/slideback ms/bd22/pistol/slideback
$alias ms/card/vp_minigun/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/vp_minigun/magdrop ms/magdrop
$alias ms/card/vp_pistol/magout ms/bd22/pistol/magout
$alias ms/card/vp_pistol/magin ms/bd22/pistol/magin
$alias ms/card/vp_pistol/slideback ms/bd22/pistol/slideback
$alias ms/card/vp_pistol/slidefwd ms/bd22/pistol/slidefwd
$alias ms/card/vp_pistol/magdrop ms/magdrop
$alias ms/card/zb_tommygun/magout ms/bd22/smg/magout
$alias ms/card/zb_tommygun/magin ms/bd22/smg/magin
$alias ms/card/zb_tommygun/slideback ms/bd22/smg/slideback
$alias ms/card/zb_tommygun/slidefwd ms/bd22/smg/slidefwd
$alias ms/card/zb_tommygun/magdrop ms/magdrop
