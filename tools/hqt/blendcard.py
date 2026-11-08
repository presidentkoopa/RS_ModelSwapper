#!/usr/bin/env python3
"""
blendcard.py -- the card straight from the artist's .blend, for sets built on the ZMC TEMPLATE rig
(BrutalWolf, MeatGrinder: E:\\DOOMWork\\VR_WeaponSetRebuild\\br_vr\\Brutaldoom_blend_files).

The template is an armature tree the artist parented every part to:
    Main Hand (the controller)  ->  Handle (the gun)  ->  Magazine / Trigger / Extra / ... (the parts)
Each part armature has one bone and one action. So the card needs no motion analysis: the role is the
armature's name, the drop/eject/bolt path is the bone's authored animation, and Handle's transform under
Main Hand is where the artist put the gun in the hand. Everything is read in WORLD space, which is the
MD3's own frame: the exporter wrote the MD3 from this scene with Main Hand at the origin (checked on the
MP40: the magazine drops 12.0 units along -Z in frames 5..9 in both the blend and the exported MD3).

Usage:  blendcard.py in.blend out.card [--md3 exported.md3]
Needs the bpy module (pip install bpy). Run with python3 -I from a clean directory.
"""
import sys, os, json, math, argparse
import bpy, mathutils

ROLE = {'magazine':'mag','trigger':'trigger','extra':'extra','handle':'body','bolt':'bolt','slide':'slide',
        'pump':'pump','shell':'shell','clip':'clip','round':'round','casing':'case','case':'case','hammer':'hammer',
        'cover':'cover','lever':'lever','cylinder':'cyl'}

def role_of(name):
    base=name.split('.')[0].strip().lower().replace(' ','')
    for k,v in ROLE.items():
        if base.startswith(k): return v
    return base

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('blend'); ap.add_argument('out'); ap.add_argument('--md3',default='')
    a=ap.parse_args()
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.blend))
    sc=bpy.context.scene; O=bpy.data.objects
    hand=O.get('Main Hand'); handle=O.get('Handle')
    arm=[o for o in O if o.type=='ARMATURE']
    if not handle:
        # the older files (MeatGrinder, the Wolf Shotgun) have the same tree with unnamed armatures:
        # the gun armature is the one whose child mesh has the most vertices; the hand is its parent (if any)
        def nv(o): return sum(len(m.data.vertices) for m in O if m.type=='MESH' and m.parent is o)
        cands=[o for o in arm if nv(o)>0]
        handle=max(cands,key=nv) if cands else None
        if not handle: sys.exit('no armature carries a mesh: not a ZMC-style rig')
        hand=handle.parent if handle.parent and handle.parent.type=='ARMATURE' else None
        # roles come from the mesh names when the armature is unnamed
    if hand is None:
        class _H: matrix_world=mathutils.Matrix.Identity(4)
        hand=_H()
    # WORLD space, not Main Hand's: the MD3 exporter wrote the scene in world units with Main Hand at the
    # origin and scaled 25, so world IS the MD3 frame (checked: the MP40 magazine drops 12.0 in both).
    def world_in_hand(m): return m
    name=os.path.splitext(os.path.basename(a.blend))[0]
    arms=[o for o in O if o.type=='ARMATURE' and o is not hand and (handle in (o.parent, o.parent.parent if o.parent else None) or o is handle)]
    meshes={o.name:o for o in O if o.type=='MESH' and o.parent}
    card=[f'weapon {name}', f'  source      {os.path.basename(a.blend)}   blender {".".join(map(str,bpy.data.version))}   frames {sc.frame_start}..{sc.frame_end}',
          '  space       world = the MD3 frame (Main Hand at the origin, scale %.0f); units = MD3 model units'%hand.matrix_world.to_scale()[0]]
    hm=world_in_hand(handle.matrix_world); t=hm.to_translation(); e=[math.degrees(x) for x in hm.to_euler()]
    card.append('  handle      loc [%.2f, %.2f, %.2f]  rot_deg [%.1f, %.1f, %.1f]   # the gun under the hand: the artist\'s grip relation'%(t.x,t.y,t.z,*e))
    card.append('  parts')
    paths={}
    for o in sorted(arms,key=lambda o:o.name):
        if o is handle: continue
        pb=o.pose.bones[0] if o.pose and o.pose.bones else None
        kids=[m.name for m in O if m.type=='MESH' and m.parent is o]
        r=role_of(o.name)
        if r.startswith('armature') and kids: r=role_of(kids[0])	# unnamed armature: the mesh's name
        if o.parent is None and o is not handle: continue		# a stray root armature with no mesh
        nv=sum(len(O[k].data.vertices) for k in kids)
        P=[]
        for f in range(sc.frame_start, sc.frame_end+1):
            sc.frame_set(f); m=world_in_hand(o.matrix_world @ (pb.matrix if pb else mathutils.Matrix()))
            P.append(m.to_translation())
        sc.frame_set(sc.frame_start)
        p0=P[0]; d=[(p-p0).length for p in P]; k=max(range(len(d)),key=lambda i:d[i]); trav=d[k]
        ax=(P[k]-p0).normalized() if trav>1e-4 else mathutils.Vector((0,0,0))
        moving=[f for f,x in zip(range(sc.frame_start,sc.frame_end+1),d) if x>1e-3]
        card.append('    %-9s armature "%s"  rest [%.2f, %.2f, %.2f]  axis [%.3f, %.3f, %.3f]  travel %.2f  frames %s  meshes %s (%d verts)'%(
            r,o.name,p0.x,p0.y,p0.z,ax.x,ax.y,ax.z,trav,('%d..%d'%(moving[0],moving[-1])) if moving else '-',kids,nv))
        paths[o.name]=[[round(v,4) for v in p] for p in P]
    body=[m.name for m in O if m.type=='MESH' and m.parent is handle]
    card.append('  body        meshes %s'%body)
    phases=[]
    card.append('  authoring   rig=ZMC TEMPLATE  roles_from_armature_names yes  paths_authored yes')
    open(a.out,'w').write('\n'.join(card)+'\n')
    json.dump(dict(weapon=name,paths=paths),open(os.path.splitext(a.out)[0]+'_paths.json','w'))
    print('\n'.join(card))
main()
