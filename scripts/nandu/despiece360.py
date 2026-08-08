"""
Giro de 360 grados con la zapatilla ya desarmada.

    blender --background 1.blend --python despiece360.py

Combina las dos ideas anteriores: las capas se separan hasta su posición
final y desde ahí el conjunto entero rota sobre el eje vertical. Deja ver
la suela por abajo y el interior del upper por arriba, que es lo que un
despiece fijo de perfil no muestra.

Para rotar el conjunto sin mover cada pieza por separado, todas se
emparentan a un objeto vacío en el origen y se rota ese vacío. Rotar cada
pieza por su cuenta las haría girar sobre su propio centro y se
desarmaría la composición.
"""

import importlib.util
import math
from pathlib import Path

import bpy
from mathutils import Vector

BASE = Path("C:/Users/leona/Proyects/mk/csdev-astro")

spec = importlib.util.spec_from_file_location("render", BASE / "scripts/nandu/render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)

spec2 = importlib.util.spec_from_file_location("explosion", BASE / "scripts/nandu/explosion.py")
explosion = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(explosion)

CUADROS = 36
SALIDA = BASE / "public/nandu/despiece360"
SEPARACION = 1.35


def main() -> None:
    zapa = render.limpiar_escena()
    render.borrar_logo(zapa)
    render.centrar(zapa)
    alto = zapa.dimensions.z

    piezas = explosion.separar_por_material(zapa)
    plan = explosion.preparar(piezas, alto)

    # Las capas quedan directamente en su posición final: acá el
    # movimiento es el giro, no la separación.
    for p, destino in plan:
        p.location.z += destino * SEPARACION / explosion.SEPARACION

    # Un vacío en el origen como padre de todo. Rotarlo mueve el conjunto
    # como una sola pieza; rotar cada capa las haría girar sobre sí mismas.
    eje = bpy.data.objects.new("Eje", None)
    bpy.context.collection.objects.link(eje)
    eje.location = (0, 0, 0)
    eje.rotation_mode = "XYZ"

    for p, _ in plan:
        p.parent = eje
        p.matrix_parent_inverse = eje.matrix_world.inverted()

    # Cámara y luces sobre el conjunto ya separado, que es mucho más alto
    # que la zapatilla armada.
    cam = render.armar_camara(zapa)
    cam.data.ortho_scale *= 1.45
    render.armar_luces(zapa)
    render.configurar_render()

    s = bpy.context.scene
    s.render.resolution_x = 1100
    s.render.resolution_y = 1100

    SALIDA.mkdir(parents=True, exist_ok=True)
    paso = 360.0 / CUADROS

    for i in range(CUADROS):
        eje.rotation_euler = (0, 0, math.radians(i * paso))
        eje.update_tag()
        bpy.context.view_layer.update()

        s.render.filepath = str(SALIDA / f"{i + 1:02d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"  {i + 1:02d}/{CUADROS}  {i * paso:.0f} grados")

    print("listo")


if __name__ == "__main__":
    main()
