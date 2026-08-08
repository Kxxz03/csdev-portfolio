"""Que hay realmente dentro de los materiales de la zapatilla."""
import bpy
for m in bpy.data.materials:
    if not m.name.startswith("Material") or "material" not in m.name:
        continue
    print(f"\n{m.name}   node_tree={'si' if m.node_tree else 'NO'}")
    if not m.node_tree:
        continue
    for n in m.node_tree.nodes:
        entradas = ""
        if n.type == "BSDF_PRINCIPLED":
            bc = n.inputs["Base Color"]
            entradas = f"  BaseColor conectado={bool(bc.links)} valor={tuple(round(v,2) for v in bc.default_value)}"
        elif n.type == "TEX_IMAGE":
            entradas = f"  imagen={n.image.name if n.image else 'ninguna'}"
        print(f"   {n.type:22} {n.name:24}{entradas}")
