import bpy, sys
print("@@@BEGIN")
for o in bpy.data.objects:
    if o.type == 'MESH':
        me = o.data
        print("@@@OBJ\t%s\t%d\t%d\t%s" % (o.name, len(me.vertices), len(me.polygons),
              o.parent.name if o.parent else "-"))
    else:
        print("@@@OTHER\t%s\t%s" % (o.name, o.type))
print("@@@ACTIONS\t%d" % len(bpy.data.actions))
for a in bpy.data.actions:
    print("@@@ACT\t%s\t%s" % (a.name, tuple(int(x) for x in a.frame_range)))
print("@@@END")
