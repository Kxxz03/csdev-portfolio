import bpy
if bpy.context.object and bpy.context.object.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    print(f"\n{o.name}  ({len(o.data.polygons)} caras)")
    conteo = {}
    for p in o.data.polygons:
        conteo[p.material_index] = conteo.get(p.material_index, 0) + 1
    for i, r in enumerate(o.material_slots):
        nombre = r.material.name if r.material else "(vacia)"
        print(f"   [{i}] {nombre:34} {conteo.get(i,0):6} caras")
