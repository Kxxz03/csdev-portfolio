"""Un solo cuadro de perfil, en alta, para la primera pantalla."""
import importlib.util
from pathlib import Path
import bpy

BASE = Path("C:/Users/leona/Proyects/mk/csdev-astro")
spec = importlib.util.spec_from_file_location("render", BASE / "scripts/nandu/render.py")
render = importlib.util.module_from_spec(spec); spec.loader.exec_module(render)

z = render.limpiar_escena()
render.borrar_logo(z)
render.centrar(z)
render.armar_camara(z)
render.armar_luces(z)
render.configurar_render()

s = bpy.context.scene
# Encuadre apaisado y mas resolucion: es la unica imagen fija de la pagina
s.render.resolution_x = 2600
s.render.resolution_y = 1540
try:
    s.eevee.taa_render_samples = 128
except AttributeError:
    pass

s.render.filepath = str(BASE / "public/nandu/heroe.png")
bpy.ops.render.render(write_still=True)
print("listo")
