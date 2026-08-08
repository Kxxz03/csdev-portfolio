"""
Pinta cada material de un color plano distinto, para ver qué parte de la
zapatilla es cada uno. Sirve para ubicar dónde está el logo de la marca
original antes de borrarlo.

    blender --background 1.blend --python diagnostico.py
"""

import importlib.util
from pathlib import Path

import bpy

BASE = Path("C:/Users/leona/Proyects/mk/csdev-astro")

# render.py define su bloque principal bajo __name__ == "__main__", así que
# importarlo no dispara ningún render.
spec = importlib.util.spec_from_file_location("render", BASE / "scripts/nandu/render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)

COLORES = {
    "Material0-material": (0.10, 0.10, 0.10, 1),  # gris oscuro
    "Material1-material": (1.00, 0.00, 0.00, 1),  # ROJO: sospechoso del logo
    "Material2-material": (0.90, 0.88, 0.82, 1),  # hueso
    "Material3-material": (0.00, 0.35, 1.00, 1),  # azul
    "Material4-material": (1.00, 0.75, 0.00, 1),  # amarillo
}

zapa = render.limpiar_escena()

for m in bpy.data.materials:
    # Nada de use_nodes: en Blender 5 está en desuso y devuelve falso
    # aunque el material tenga árbol de nodos, así que saltea todo.
    if m.name not in COLORES or not m.node_tree:
        continue
    for n in m.node_tree.nodes:
        if n.type != "BSDF_PRINCIPLED":
            continue
        entrada = n.inputs["Base Color"]
        # Desconectar la textura: si no, el color plano no se ve
        for enlace in list(entrada.links):
            m.node_tree.links.remove(enlace)
        entrada.default_value = COLORES[m.name]
        print(f"  {m.name} -> {COLORES[m.name][:3]}")

render.centrar(zapa)
render.armar_camara(zapa)
render.armar_luces(zapa)
render.configurar_render()

bpy.context.scene.render.filepath = str(BASE / "diagnostico.png")
bpy.ops.render.render(write_still=True)
print("listo")
