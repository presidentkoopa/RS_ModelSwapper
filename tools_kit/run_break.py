"""Run the break-open / revolver generator over OUR guns.

gen_rsb ships with six entries pointing at BD22 and Vanilla+ meshes that are not
on this disk, so it cannot run as it stands. Its code is untouched; only the GUNS
table is replaced, with entries describing the meshes ModelSwapper actually
ships. Every index below was measured, not guessed:

  MS_SuperShotgun  6 surfaces -- ssgbase is the body, ssgbarrel breaks open
                   58.6 deg, the two shotshells sit visible in the chambers and
                   eject at frame 9, and the two newshells are collapsed to a
                   point at idle, so they are rounds in the off hand rather than
                   in the gun.
  MS_brt_M79       body, a latch that pivots in place, a 2667-vertex barrel that
                   hinges 30 deg, and one shell.
  MS_Revolver      python.004 is the body, python.005 and .007 swing out together
                   85.8 deg, and six 18-vertex surfaces are the rounds.

The generator fits the hinge itself from the open frame and prints a residual;
that number is the check on whether the open frame is right.
"""
import sys, os
sys.path.insert(0, 'tools_kit')
sys.dont_write_bytecode = True
import gen_rsb

OURS = [
    dict(key='MS/SuperShotgun', cls='MS_SuperShotgun', set='vp',
         mesh='models/hud/SuperShotgun/ssg.md3', path='models/hud/SuperShotgun',
         model='ssg.md3', skin='WPN-GUNS-k1.png', scale=(-1.35, 1.35, 1.35),
         off=(0.0, 0.0, -5.0), extra='\tNoInterpolation',
         ready=0, body=[5], hinged=[4], open_frame=16,
         chambers=[(2, 0), (3, 0)], hold='shell',
         spr='M', ready_sprite='SHT2 A',
         snd=dict(open=['weapons/sshoto'], load='weapons/sshotl',
                  close=['weapons/sshotc'], chan=5),
         eject='bd', reserve='Shell', loaded='MSSSGAmmo', per_load=1, cap=2,
         casing=None, unloaded='MSHasUnloadedSSG', reload_token='Reloading'),

    dict(key='MS/M79', cls='MS_brt_M79', set='vp',
         mesh='models/bd/M79/M79.md3', path='models/bd/M79',
         model='M79.md3', skin='M79.png', scale=(-1.0, 1.0, 1.0),
         off=(0.0, 0.0, -5.0), extra='\tNoInterpolation',
         ready=0, body=[1], hinged=[4], open_frame=22,
         chambers=[(3, 0)], hold='big',
         spr='N', ready_sprite='MISG A',
         snd=dict(open=['GrenadeLauncher/Open'], load='GrenadeLauncher/Load',
                  close=['GrenadeLauncher/Close'], chan=5),
         eject='bd', reserve='RocketAmmo', loaded='MSM79Ammo', per_load=1, cap=1,
         casing=None, unloaded='MSM79Reload', reload_token='Reloading'),

    # This revolver does not take loose rounds: its six 18-vertex round surfaces
    # are collapsed to a point until frame 20, and surface 10 (257 verts) is a
    # SPEEDLOADER. The kit had already worked that out -- its V+ revolver entry
    # is chambers=[] with loader=(10, 26) against the same surface layout -- so
    # those are its numbers, not a fresh guess.
    dict(key='MS/Revolver', cls='MS_Revolver', set='vp',
         mesh='models/hud/Revolver/rev.md3', path='models/hud/Revolver',
         model='rev.md3', skin='rev.png', scale=(-1.35, 1.35, 1.35),
         off=(0.0, 0.0, -5.0), extra='	NoInterpolation',
         ready=0, body=[0], hinged=[1, 3], open_frame=25,
         chambers=[], loader=(10, 26), hold='cell',
         spr='O', ready_sprite='PISG A',
         snd=dict(open=['weapons/revopen'], load='weapons/revload',
                  close=['weapons/revclose'], chan=5),
         eject='bd', reserve='Clip', loaded='MSRevAmmo', per_load=6, cap=6,
         casing=None, unloaded='MSRevUnloaded', reload_token='Reloading'),
]

if __name__ == '__main__':
    # the Ermac hand meshes the generator wants under _x/rsq/ are already in
    # the pack under models/ammo_hand/, so point it there rather than extract
    # a second copy of the same files
    gen_rsb.RSQ = os.path.abspath('models/ammo_hand') + os.sep
    gen_rsb.GUNS = OURS
    gen_rsb.main(sys.argv[1])
