"""
Matriz de renders: cada ángulo de giro en varios estados de desarme.

    blender --background 1.blend --python matriz.py

Un giro solo, o un desarme solo, se resuelven con una secuencia. Poder
hacer las dos cosas a la vez necesita una malla: para cada ángulo hay que
tener la zapatilla armada, media abierta y abierta del todo.

El costo crece multiplicando, así que los números están elegidos para que
el resultado pese algo razonable:

    24 ángulos x 5 estados = 120 cuadros

Con 36 ángulos y 8 estados serían 288, y a esa altura la descarga pesa
más que todo el resto del sitio junto.

Salida: public/nandu/matriz/e{estado}/{angulo}.png
"""

import importlib.util
import math
from pathlib import Path

import bpy

BASE = Path("C:/Users/leona/Proyects/mk/csdev-astro")

spec = importlib.util.spec_from_file_location("render", BASE / "scripts/nandu/render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)

spec2 = importlib.util.spec_from_file_location("explosion", BASE / "scripts/nandu/explosion.py")
explosion = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(explosion)

ANGULOS = 24
ESTADOS = 5
SEPARACION = 1.35
SALIDA = BASE / "public/nandu/matriz"


def main() -> None:
    zapa = render.limpiar_escena()
    render.borrar_logo(zapa)
    render.centrar(zapa)
    alto = zapa.dimensions.z

    piezas = explosion.separar_por_material(zapa)
    plan = explosion.preparar(piezas, alto)
    base_z = {p.name: p.location.z for p, _ in plan}

    # Todas las piezas cuelgan de un vacío en el origen: rotar ese vacío
    # gira el conjunto. Rotar cada pieza la haría girar sobre su propio
    # centro y la composición se desarmaría de la manera equivocada.
    eje = bpy.data.objects.new("Eje", None)
    bpy.context.collection.objects.link(eje)
    eje.location = (0, 0, 0)
    eje.rotation_mode = "XYZ"
    for p, _ in plan:
        p.parent = eje
        p.matrix_parent_inverse = eje.matrix_world.inverted()

    # El encuadre se calcula sobre el caso más grande, el de las capas
    # totalmente separadas, para que no se corte en ningún estado.
    cam = render.armar_camara(zapa)
    cam.data.ortho_scale *= 1.45
    render.armar_luces(zapa)
    render.configurar_render()

    s = bpy.context.scene
    s.render.resolution_x = 900
    s.render.resolution_y = 900

    paso_angulo = 360.0 / ANGULOS
    total = ANGULOS * ESTADOS
    hecho = 0

    for e in range(ESTADOS):
        # Suavizado en los extremos: la primera y la última porción del
        # recorrido avanzan menos, como una pieza que se posa.
        t = e / (ESTADOS - 1)
        apertura = t * t * (3.0 - 2.0 * t)

        carpeta = SALIDA / f"e{e}"
        carpeta.mkdir(parents=True, exist_ok=True)

        for p, destino in plan:
            p.location.z = base_z[p.name] + destino * apertura * SEPARACION / explosion.SEPARACION

        for a in range(ANGULOS):
            eje.rotation_euler = (0, 0, math.radians(a * paso_angulo))
            eje.update_tag()
            for p, _ in plan:
                p.update_tag()
            bpy.context.view_layer.update()

            s.render.filepath = str(carpeta / f"{a + 1:02d}.png")
            bpy.ops.render.render(write_still=True)
            hecho += 1
            print(f"  {hecho}/{total}  estado {e} angulo {a * paso_angulo:.0f}")

    print("listo")


if __name__ == "__main__":
    main()
