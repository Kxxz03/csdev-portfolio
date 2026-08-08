"""
Render de las dos zapatillas juntas, para la primera pantalla.

    blender --background 1.blend --python par.py

A diferencia de render.py, este NO borra la segunda zapatilla: la escena
original ya las trae apoyadas una sobre otra, con una mostrando la suela.
Esa composición dice más de un producto que un perfil suelto, porque deja
ver el dibujo de la suela y el volumen al mismo tiempo.

La cámara mira desde arriba en tres cuartos, que es como se fotografía un
par de calzados. Va en perspectiva y no ortográfica: acá no hay que
mantener coherencia entre cuadros, y la perspectiva da profundidad.
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

SALIDA = BASE / "public/nandu/par.png"


def limpiar() -> list[bpy.types.Object]:
    """Deja las dos zapatillas y saca el plano de fondo."""
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    zapas = [
        o for o in bpy.data.objects
        if o.type == "MESH" and o.name.startswith("Object_")
    ]
    for o in list(bpy.data.objects):
        if o not in zapas:
            bpy.data.objects.remove(o, do_unlink=True)

    print(f"  zapatillas: {len(zapas)}")
    return zapas


def centro_y_radio(objs: list[bpy.types.Object]) -> tuple[Vector, float]:
    """Centro del conjunto y radio que lo envuelve, en coordenadas de mundo."""
    puntos = [obj.matrix_world @ Vector(v) for obj in objs for v in obj.bound_box]
    minimo = Vector((min(p[i] for p in puntos) for i in range(3)))
    maximo = Vector((max(p[i] for p in puntos) for i in range(3)))
    centro = (minimo + maximo) / 2
    return centro, (maximo - minimo).length / 2


def main() -> None:
    zapas = limpiar()
    for z in zapas:
        render.borrar_logo(z)

    centro, radio = centro_y_radio(zapas)
    print(f"  centro {tuple(round(v, 3) for v in centro)}  radio {radio:.3f}")

    # Cámara en tres cuartos desde arriba: azimut 38°, elevación 34°.
    # Es el ángulo estándar de foto de par y deja ver la suela de la de
    # atrás sin perder el perfil de la de adelante.
    azimut = math.radians(38)
    elevacion = math.radians(34)

    LENTE = 85  # mm. Lente largo: menos deformación en los bordes
    SENSOR = 36  # mm, el ancho por defecto de Blender
    MARGEN = 1.5  # aire alrededor del conjunto

    # La distancia sale del ángulo real del lente, no de un multiplicador
    # al ojo: con radio * 3.4 la cámara quedaba DENTRO de la composición y
    # el par salía cortado por los cuatro lados.
    medio_angulo = math.atan(SENSOR / 2 / LENTE)
    distancia = radio / math.tan(medio_angulo) * MARGEN

    cam_data = bpy.data.cameras.new("Camara")
    cam_data.lens = LENTE
    cam = bpy.data.objects.new("Camara", cam_data)
    cam.location = centro + Vector((
        math.cos(elevacion) * math.cos(azimut) * distancia,
        math.cos(elevacion) * math.sin(azimut) * -distancia,
        math.sin(elevacion) * distancia,
    ))
    cam.rotation_euler = render.mirar_hacia(cam.location, centro)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    # Luces alrededor del conjunto, no de una sola zapatilla
    escala = radio * 2
    for nombre, (x, y, z), energia, tam in [
        ("Principal", (0.8, -0.9, 1.1), 90, 2.2),
        ("Relleno", (-0.9, -0.4, 0.4), 30, 2.6),
        ("Contra", (-0.5, 1.0, 0.8), 65, 1.6),
    ]:
        luz_data = bpy.data.lights.new(nombre, type="AREA")
        luz_data.energy = energia * (escala / 0.27) ** 2
        luz_data.size = tam * escala
        luz = bpy.data.objects.new(nombre, luz_data)
        luz.location = centro + Vector((x, y, z)) * escala * 3
        luz.rotation_euler = render.mirar_hacia(luz.location, centro)
        bpy.context.collection.objects.link(luz)

    render.configurar_render()
    s = bpy.context.scene
    s.render.resolution_x = 2600
    s.render.resolution_y = 1740
    try:
        s.eevee.taa_render_samples = 128
    except AttributeError:
        pass

    s.render.filepath = str(SALIDA)
    bpy.ops.render.render(write_still=True)
    print("listo")


if __name__ == "__main__":
    main()
