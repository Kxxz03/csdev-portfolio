"""
Renderiza la secuencia de giro de la zapatilla desde Blender, sin interfaz.

    blender --background 1.blend --python render.py -- giro
    blender --background 1.blend --python render.py -- prueba

La escena original trae dos zapatillas, un plano de fondo de 18 metros, y
ni cámara ni luces. Este script arma todo de cero para que el resultado no
dependa de cómo quedó guardado el archivo.

Decisiones y por qué:

  Fondo transparente. La zapatilla va sobre el grafito del sitio; si se
  renderiza con fondo, después no hay forma de sacarlo bien.

  Cámara ortográfica. En perspectiva, al girar, las partes cercanas se
  agrandan y el objeto parece cambiar de tamaño entre cuadros.

  Rota el objeto, no la cámara. Así la iluminación se mantiene fija
  respecto al mundo y el giro se lee como un objeto sobre una tornamesa.

  El material del logo se vuelve invisible: el modelo es de una marca real
  y esto es una marca inventada.
"""

import math
import sys
from pathlib import Path

import bpy

# ── Parámetros ────────────────────────────────────────────────────────────
CUADROS = 36  # uno cada 10 grados
RESOLUCION = 1400
SALIDA = Path("C:/Users/leona/Proyects/mk/csdev-astro/public/nandu/giro")

# El logo de la marca original es una calcomania: 76 caras con un nodo
# transparente mezclado. Los materiales llamados "Logo.*" que aparecen en
# el archivo estan huerfanos, no los usa ningun objeto.
MATERIALES_OCULTOS = ("Material1-material",)

# Blanco hueso y naranja de ÑANDÚ
NARANJA = (1.0, 0.353, 0.122, 1.0)


def limpiar_escena() -> bpy.types.Object:
    """Deja una sola zapatilla, sin fondo. Devuelve la zapatilla."""
    # El .blend vino guardado en modo edición y casi ninguna operación de
    # objeto funciona ahí. Salir es lo primero.
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    zapatillas = [
        o for o in bpy.data.objects
        if o.type == "MESH" and o.name.startswith("Object_")
    ]
    if not zapatillas:
        sys.exit("No encontré la zapatilla en la escena")

    # La segunda es una copia; el plano es el fondo de 18 metros
    for o in list(bpy.data.objects):
        if o is not zapatillas[0]:
            bpy.data.objects.remove(o, do_unlink=True)

    return zapatillas[0]


def borrar_logo(obj: bpy.types.Object) -> int:
    """
    Borra la geometría del logo de la marca original.

    Ponerle alpha 0 al material no alcanza: le saca el color pero la
    geometría sigue ahí, en relieve, y el pespunte marca la silueta del
    logo igual. Hay que eliminar las caras.
    """
    indices = [
        i for i, ranura in enumerate(obj.material_slots)
        if ranura.material
        and any(c.lower() in ranura.material.name.lower() for c in MATERIALES_OCULTOS)
    ]
    if not indices:
        print("  sin material de logo")
        return 0

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_mode(type="FACE")

    for i in indices:
        obj.active_material_index = i
        bpy.ops.object.material_slot_select()
        print(f"  logo borrado: {obj.material_slots[i].material.name}")

    antes = len(obj.data.vertices)
    bpy.ops.mesh.delete(type="FACE")
    bpy.ops.object.mode_set(mode="OBJECT")
    print(f"  vertices: {antes} -> {len(obj.data.vertices)}")

    return len(indices)


def centrar(obj: bpy.types.Object) -> None:
    """Lleva el objeto al origen, para que gire sobre sí mismo y no orbite."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    obj.location = (0, 0, 0)

    # El modelo vino en modo cuaternión y ahí Blender IGNORA rotation_euler:
    # se puede escribir cualquier ángulo, la matriz del mundo no cambia y
    # salen los 36 cuadros idénticos sin ningún error que lo delate.
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0, 0, 0)


def armar_camara(obj: bpy.types.Object) -> bpy.types.Object:
    """
    Cámara ortográfica de perfil, encuadrada al objeto con margen.

    La zapatilla es larga en Y (27 cm) y angosta en X (10 cm), así que el
    perfil se ve desde X. Poner la cámara en Y da la vista frontal.

    El margen no es capricho: al girar, la diagonal en planta es más larga
    que cualquiera de los lados, así que sin aire los cuadros de tres
    cuartos se salen del cuadro.
    """
    cam_data = bpy.data.cameras.new("Camara")
    cam_data.type = "ORTHO"

    d = obj.dimensions
    diagonal = math.sqrt(d.x**2 + d.y**2)
    cam_data.ortho_scale = max(diagonal, d.z) * 1.25

    cam = bpy.data.objects.new("Camara", cam_data)
    bpy.context.collection.objects.link(cam)

    # De perfil, apenas por encima para que se lea el volumen de la suela
    # Apunta al origen, que despues de centrar() es el centro del
    # recuadro del objeto. Apuntar mas arriba lo corre hacia abajo.
    distancia = max(d) * 4
    cam.location = (distancia, 0, distancia * 0.22)
    cam.rotation_euler = mirar_hacia(cam.location, (0, 0, 0))

    bpy.context.scene.camera = cam
    return cam


def mirar_hacia(desde, hacia) -> "bpy.types.Object.rotation_euler":
    """Rotación que apunta el -Z de un objeto hacia un punto."""
    from mathutils import Vector

    direccion = Vector(hacia) - Vector(desde)
    return direccion.to_track_quat("-Z", "Y").to_euler()


def armar_luces(obj: bpy.types.Object) -> None:
    """
    Tres luces: principal, relleno y contra.

    Las energías van bajas a propósito: el primer intento con 240 W quemó
    todo a blanco plano y se perdió el relieve de la suela, que es lo que
    hace que la zapatilla se lea como un objeto y no como una silueta.
    """
    escala = max(obj.dimensions)

    esquema = [
        # nombre, posición relativa, energía, tamaño relativo
        ("Principal", (0.9, -0.7, 1.0), 55, 2.0),
        ("Relleno", (-0.4, -0.9, 0.3), 18, 2.5),
        ("Contra", (-0.7, 0.8, 0.7), 40, 1.5),
    ]

    for nombre, (x, y, z), energia, tam in esquema:
        luz_data = bpy.data.lights.new(nombre, type="AREA")
        luz_data.energy = energia
        luz_data.size = tam * escala
        luz = bpy.data.objects.new(nombre, luz_data)
        luz.location = (x * escala * 3, y * escala * 3, z * escala * 3)
        luz.rotation_euler = mirar_hacia(luz.location, (0, 0, 0))
        bpy.context.collection.objects.link(luz)


def configurar_render() -> None:
    s = bpy.context.scene
    s.render.resolution_x = RESOLUCION
    s.render.resolution_y = RESOLUCION
    s.render.resolution_percentage = 100

    # Sin esto el fondo sale negro y no transparente
    s.render.film_transparent = True

    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGBA"
    s.render.image_settings.compression = 15

    # EEVEE alcanza y es unas 20 veces más rápido que Cycles para esto
    for motor in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            s.render.engine = motor
            break
        except TypeError:
            continue
    print(f"  motor: {s.render.engine}")


def renderizar(obj: bpy.types.Object, cuadros: int) -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    paso = 360.0 / cuadros

    for i in range(cuadros):
        obj.rotation_euler = (0, 0, math.radians(i * paso))

        # Sin esto Blender renderiza el estado anterior y salen los 36
        # cuadros idénticos. Cambiar rotation_euler marca el objeto como
        # sucio, pero en modo sin interfaz nada dispara la reevaluación
        # antes del render.
        obj.update_tag()
        bpy.context.view_layer.update()

        destino = SALIDA / f"{i + 1:02d}.png"
        bpy.context.scene.render.filepath = str(destino)
        bpy.ops.render.render(write_still=True)
        print(f"  {destino.name}  {i * paso:.0f} grados")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    tarea = args[0] if args else "prueba"

    print("\n--- preparando escena ---")
    zapa = limpiar_escena()
    print(f"  zapatilla: {zapa.name}, {len(zapa.data.vertices)} vertices")
    borrar_logo(zapa)
    centrar(zapa)
    armar_camara(zapa)
    armar_luces(zapa)
    configurar_render()

    cuadros = {"prueba": 1, "cuatro": 4}.get(tarea, CUADROS)
    print(f"\n--- renderizando {cuadros} cuadro(s) ---")
    renderizar(zapa, cuadros)
    print("\nlisto")
