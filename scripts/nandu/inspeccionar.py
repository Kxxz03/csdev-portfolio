"""Inventario del .blend: objetos, tamanos, materiales y texturas."""
import bpy

print("\n" + "=" * 60)
print("OBJETOS")
for o in bpy.data.objects:
    d = o.dimensions
    print(f"  {o.name:20} {o.type:10} {d.x:6.2f} x {d.y:6.2f} x {d.z:6.2f}  "
          f"verts={len(o.data.vertices) if o.type=='MESH' else '-'}")

print("\nMATERIALES")
for m in bpy.data.materials:
    print(f"  {m.name}")

print("\nIMAGENES / TEXTURAS")
for i in bpy.data.images:
    print(f"  {i.name:34} {i.size[0]}x{i.size[1]}  {i.filepath}")

print("\nCAMARAS Y LUCES")
for o in bpy.data.objects:
    if o.type in ("CAMERA", "LIGHT"):
        print(f"  {o.type:8} {o.name}")

print("\nRENDER")
s = bpy.context.scene
print(f"  motor: {s.render.engine}")
print(f"  resolucion: {s.render.resolution_x}x{s.render.resolution_y}")
print(f"  frames: {s.frame_start}-{s.frame_end}")
print("=" * 60)
