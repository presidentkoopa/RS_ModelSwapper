"""Run the pump / hand-loaded-shell generator over OUR guns.

gen_pump ships two entries whose meshes are not on this disk, so like gen_rsb it
cannot run as it stands. Its code is untouched; only the PUMPS table is replaced.

The Vanilla+ entry turned out to describe a mesh we already ship. Ours reads:
  s0 doomshot      494v  the body
  s1 doomshot.001   69v  the pump, strokes 7 units
  s2 shotshl        34v  collapsed at rest, first visible at FRAME 12
and the kit's entry is pump_surfs=[1], shell_surf=2, shell_frame=12. Same mesh,
same numbers, so they are carried over rather than re-derived -- only the mesh
path changes to ours.
"""
import sys, os
sys.path.insert(0, 'tools_kit')
sys.dont_write_bytecode = True
import gen_pump

CHAN_AUTO = getattr(gen_pump, 'CHAN_AUTO', 0)
CHAN_WEAPON = getattr(gen_pump, 'CHAN_WEAPON', 1)

OURS = [
    # key stays V+/VR_Shotgun because that is how the reload survey names this
    # gun, and this IS that gun -- same mesh, same surfaces, same shell frame.
    # Only the class and the mesh path are ours.
    dict(key='V+/VR_Shotgun', cls='MS_Shotgun', set='vp',
         mesh='models/hud/Shotgun/shotgun.md3',
         path='models/hud/Shotgun', model='shotgun.md3', skin='WPN-GUNS-k1.png',
         scale=(1.35, 1.35, 1.35), off=(0.0, 0.0, 0.0),
         extra='', ready_frame=0, pump_surfs=[1], bolt_surfs=[], shell_surf=2,
         shell_frame=12,
         lead=None,
         depth=1.5,
         ready_sprite='SHTG A', spr_gun='RQUH', spr_part='RQUQ', spr_world='RQUX',
         waits='RSP_LoadWait RSP_PWait',
         snd=dict(shell=('Shotgun/Reload', CHAN_AUTO), back=('shotpump', CHAN_WEAPON),
                  fwd=('', 0), land=''),
         reserve='Shell', magammo='MSShotLoaded', eject_frames=[],
         # the tube's capacity, which rsr_pump.zs reads as RSP_Guns.Cap(i) to know when
         # it is full. 8, from this gun's own card (WMCARD.02_pump, MS_Shotgun).
         cap=8),
]

if __name__ == '__main__':
    # the Ermac hand meshes live under models/ammo_hand in this pack
    for attr in ('RSQ', 'ERMAC_DIR', 'HANDS'):
        if isinstance(getattr(gen_pump, attr, None), str):
            setattr(gen_pump, attr, os.path.abspath('models/ammo_hand') + os.sep)
    # ModelSwapper's weapon belongs to whatever mod is loaded and only its MODEL is
    # ours, so the reload slot comes from the DONOR IN HAND, not the weapon's class.
    gen_pump.MODELSWAPPER = True
    gen_pump.PUMPS = OURS
    gen_pump.main(sys.argv[1])
