# gmod_cw/nailgun (MS_CW_Nailgun)

Owner upload 2026-11-03: a Garry's Mod workshop replacement for the HL2 SMG viewmodel (c_smg1), carrying a Cold War
"t9 nailgun" mesh, Source MDL v48 + VVD + VTX, VTF textures. No hands in the mesh.

- Read with srcmdl.py / srcanim.py (session tools): 110 bones; the parts the reload needs each have their own bone
  (j_mag1/j_mag2 + j_bullet_00..13, j_trigger, j_mag_release, j_slide, j_charging_handle).
- Frames are the model's OWN `reload` sequence (157 frames at 60 fps, every 4th = 40 frames), skinned in the
  receiver's frame (tag_sling), so only what moves on the gun moves. The bind pose has the magazine 5.5 units too
  high: the animation's seated pose is the real one and frame 0 uses it.
- The 14 nails share the magazine's material and ride it: merged into the mag surface.
- Textures: the *_rgb VTFs (DXT5 2048) decoded and scaled to 1024. Normal/emissive maps not used.
- Placement: mesh shifted +9.4 x so the grip palm lands on the shelf donors' palm; Scale 2.4 (about real size at
  the 0.34 controller ratio). Hand fit is the owner's.
