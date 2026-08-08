"""
Renderiza el despiece: las capas de la zapatilla separándose.

    blender --background 1.blend --python explosion.py

La malla viene entera, con las piezas distinguidas solo por material. El
script la separa por material y aleja cada trozo en Z **según su propia
altura**: lo que está abajo baja, lo que está arriba sube. Así no hace
falta identificar a mano cuál es la suela y cuál el upper, y si el modelo
cambia sigue funcionando.

Se renderiza de perfil y con la misma cámara que el giro, para que la
transición entre las dos secciones no salte.
"""

import importlib.util
import math
from pathlib import Path

import bpy

BASE = Path("C:/Users/leona/Proyects/mk/csdev-astro")

spec = importlib.util.spec_from_file_location("render", BASE / "scripts/nandu/render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)

CUADROS = 40
SALIDA = BASE / "public/nandu/explosion"

# Cuánto se separan, en múltiplos del alto de la zapatilla. Con 0.95 el
# despiece se leía tímido: las piezas quedaban casi tocándose.
SEPARACION = 1.35


def separar_por_material(obj: bpy.types.Object) -> list[bpy.types.Object]:
    """Parte la malla en un objeto por material."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="MATERIAL")
    bpy.ops.object.mode_set(mode="OBJECT")

    piezas = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    print(f"  piezas: {len(piezas)}")
    return piezas


def preparar(piezas: list[bpy.types.Object], alto_total: float) -> list[tuple]:
    """
    Devuelve (pieza, desplazamiento) ordenado de abajo hacia arriba.

    El desplazamiento es proporcional a qué tan lejos está el centro de la
    pieza respecto del centro del conjunto: la suela, que está abajo, se va
    para abajo; el upper, arriba, para arriba. Las del medio casi no se
    mueven, que es como se lee un despiece técnico.
    """
    centros = []
    for p in piezas:
        z = sum((p.matrix_world @ v.co).z for v in p.data.vertices) / len(p.data.vertices)
        centros.append((p, z))

    zs = [z for _, z in centros]
    medio = (min(zs) + max(zs)) / 2
    rango = max(max(zs) - min(zs), 1e-6)

    plan = []
    for p, z in sorted(centros, key=lambda x: x[1]):
        # -1 la más baja, +1 la más alta
        relativo = (z - medio) / (rango / 2)
        plan.append((p, relativo * alto_total * SEPARACION))
        # El modo cuaternión ignora rotation_euler y también location_euler
        # no existe; location sí funciona, pero se normaliza igual por si
        # alguna pieza heredó otro modo.
        p.rotation_mode = "XYZ"

    return plan


def main() -> None:
    zapa = render.limpiar_escena()
    render.borrar_logo(zapa)
    render.centrar(zapa)

    alto = zapa.dimensions.z
    base_z = {}

    piezas = separar_por_material(zapa)
    plan = preparar(piezas, alto)
    for p, _ in plan:
        base_z[p.name] = p.location.z

    # La cámara se arma sobre el conjunto todavía unido, y se le da más
    # aire porque las piezas separadas ocupan bastante más alto.
    cam = render.armar_camara(zapa)
    # 1.85 dejaba la zapatilla diminuta en el cuadro. 1.45 da aire
    # para la separación sin desperdiciar la mitad del lienzo.
    cam.data.ortho_scale *= 1.45
    render.armar_luces(zapa)
    render.configurar_render()

    s = bpy.context.scene
    s.render.resolution_x = 1100
    s.render.resolution_y = 1100

    SALIDA.mkdir(parents=True, exist_ok=True)

    for i in range(CUADROS):
        t = i / (CUADROS - 1)
        # Suavizado: arranca y termina lento, como una pieza que se posa
        suave = t * t * (3.0 - 2.0 * t)

        for p, destino in plan:
            p.location.z = base_z[p.name] + destino * suave
            p.update_tag()

        bpy.context.view_layer.update()
        s.render.filepath = str(SALIDA / f"{i + 1:02d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"  {i + 1:02d}/{CUADROS}")

    print("listo")


if __name__ == "__main__":
    main()
