import importlib.util, math
from pathlib import Path
import bpy

BASE = Path("C:/Users/leona/Proyects/mk/csdev-astro")
spec = importlib.util.spec_from_file_location("render", BASE / "scripts/nandu/render.py")
render = importlib.util.module_from_spec(spec); spec.loader.exec_module(render)

z = render.limpiar_escena()
render.borrar_logo(z)
render.centrar(z)

print(f"\nparent: {z.parent}   constraints: {len(z.constraints)}   modifiers: {len(z.modifiers)}")
print(f"delta_rotation: {tuple(round(v,3) for v in z.delta_rotation_euler)}")
print(f"rotation_mode: {z.rotation_mode}")

for grados in (0, 90, 180):
    z.rotation_euler = (0, 0, math.radians(grados))
    bpy.context.view_layer.update()
    ev = bpy.context.evaluated_depsgraph_get().objects.get(z.name)
    print(f"\n{grados} grados")
    print(f"  rotation_euler = {tuple(round(math.degrees(v)) for v in z.rotation_euler)}")
    print(f"  matrix_world fila 0 = {tuple(round(v,3) for v in z.matrix_world[0])}")
    if ev:
        vs = [ev.matrix_world @ v.co for v in ev.data.vertices[:400]]
        print(f"  X evaluado: {min(v.x for v in vs):.3f} a {max(v.x for v in vs):.3f}")
        print(f"  Y evaluado: {min(v.y for v in vs):.3f} a {max(v.y for v in vs):.3f}")
