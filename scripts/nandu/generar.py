"""
Generador de imágenes del micrositio ÑANDÚ.

Todas las vistas salen de UNA imagen base que se adjunta como referencia.
Es lo que evita que la zapatilla cambie entre cuadros: sin referencia, cada
llamada inventa un modelo distinto y el giro tiembla.

    python scripts/nandu/generar.py base       una sola, para aprobar
    python scripts/nandu/generar.py giro       las 11 rotaciones restantes
    python scripts/nandu/generar.py capas      las 5 piezas de la explosion
    python scripts/nandu/generar.py detalles   los 3 primeros planos

Requiere ADC configurado (gcloud auth application-default login).
"""

import os
import time
import sys
from pathlib import Path

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "project-1f9e5213-8aff-44a2-bf6")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

from google import genai
from google.genai import types

SALIDA = Path("public/nandu")
BASE = SALIDA / "giro" / "01.png"

# El de más calidad para la base, porque de ella dependen todas las demás.
MODELO_BASE = "gemini-3-pro-image"
# Más barato para las variaciones, que solo repiten la referencia.
MODELO_VARIANTE = "gemini-3.1-flash-image"

# ── Descripción del producto ──────────────────────────────────────────────
# Se repite en cada prompt para que el modelo no derive. Cambiar acá y no
# en cada prompt suelto.
ZAPATILLA = (
    "a modern performance running shoe: seamless monofilament knit upper in "
    "warm off-white, one plain STRAIGHT horizontal signal-orange band across "
    "the midfoot, thick sculpted PEBA midsole in matte white with a visible "
    "dark carbon plate edge, black rubber outsole. Straight vertical heel "
    "counter, blunt rounded toe box"
)

# El primer intento salió con la forma del swoosh de Nike y silueta de
# Vaporfly. El modelo asocia "línea de acento en zapatilla de running" con
# ese logo, así que hay que prohibirlo por nombre y por forma.
SIN_MARCAS = (
    "Absolutely no logos, no text, no branding of any kind. Critically: NO "
    "swoosh, no checkmark, no chevron, no wave, no curved or swooping shape "
    "on the upper. The orange element is a plain straight horizontal band and "
    "nothing else. The silhouette must not resemble any existing commercial "
    "running shoe model"
)

ESTUDIO = (
    "Studio product photography, soft key light from the upper left, subtle "
    "rim light along the sole edge, sharp focus across the whole shoe, "
    "photorealistic, commercial quality. The shoe floats against a completely "
    "flat pure black void: no floor, no surface, no shadow, no reflection "
    "beneath it"
)

ENCUADRE = (
    "Square composition, the shoe occupies 80% of the frame width, centered, "
    "generous even margins on all sides"
)

# Pedir un "vacío negro" no funciona: el modelo asocia foto de producto con
# fondo blanco de catálogo y lo devuelve blanco igual, dos intentos seguidos.
# Describir un set físico concreto, papel de fondo continuo, sí lo respeta.
#
# El fondo blanco no servía porque la mediasuela también es blanca: no hay
# borde para recortar y el relleno desde los bordes se filtra hacia adentro.
PROMPT_BASE = (
    f"A photograph taken in a photography studio, on a seamless charcoal "
    f"black paper backdrop that fills the entire frame behind the subject. "
    f"The backdrop is very dark, near black, evenly lit, with no texture and "
    f"no gradient.\n\n"
    f"On this dark backdrop sits {ZAPATILLA}. "
    f"Lateral right-side view, perfectly perpendicular to the camera.\n\n"
    f"{ESTUDIO}. {ENCUADRE}. {SIN_MARCAS}.\n\n"
    f"The dark backdrop is essential: the shoe is pale and must stand out "
    f"clearly against it."
)

# 12 vistas, una cada 30 grados. Con 36 la consistencia se cae; con 12 y un
# cruce suave entre cuadros el giro se lee parejo igual.
ANGULOS = [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]

CAPAS = {
    "suela": "the black rubber outsole",
    "mediasuela": "the white PEBA foam midsole",
    "placa": "the carbon fiber plate",
    "upper": "the knit upper",
    "plantilla": "the insole",
}

DETALLES = {
    "textura-upper": (
        "Extreme close-up macro photograph of the seamless knit upper texture "
        "of a performance running shoe, warm off-white monofilament mesh, "
        "visible weave structure, a single signal-orange thread. Shallow depth "
        "of field, studio lighting, dark background. Photorealistic."
    ),
    "textura-suela": (
        "Close-up of the outsole tread pattern of a performance running shoe, "
        "black carbon rubber, geometric lug pattern 3.5mm deep, angled view "
        "showing depth. Studio lighting, dark background. Photorealistic."
    ),
    "textura-placa": (
        "Close-up cross-section of an exposed carbon fiber plate sandwiched "
        "inside white PEBA foam, visible carbon weave. Studio lighting, dark "
        "background. Photorealistic."
    ),
}


def cliente() -> genai.Client:
    return genai.Client()


def pedir(c: genai.Client, modelo: str, contenido, intentos: int = 5):
    """
    El modelo pro devuelve 429 con facilidad: son peticiones por minuto, no
    presupuesto. Se espera y se reintenta duplicando la espera; recién si
    agota los intentos falla.
    """
    espera = 20
    for n in range(1, intentos + 1):
        try:
            return c.models.generate_content(
                model=modelo, contents=contenido, config=config()
            )
        except Exception as e:
            if "RESOURCE_EXHAUSTED" not in str(e) and "429" not in str(e):
                raise
            if n == intentos:
                raise
            print(f"    cuota agotada, reintento {n} en {espera}s")
            time.sleep(espera)
            espera *= 2


def config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="1:1"),
    )


def guardar(respuesta, destino: Path) -> bool:
    """
    Extrae la primera imagen de la respuesta. Devuelve si hubo imagen.

    Nada de esto se puede dar por sentado: el modelo devuelve respuestas sin
    candidatos, con candidato pero sin contenido, o con contenido sin partes,
    según si filtró el pedido o simplemente no generó nada. Cortar el lote
    entero por eso obliga a rehacer todo lo anterior.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)

    candidatos = getattr(respuesta, "candidates", None) or []
    for candidato in candidatos:
        contenido = getattr(candidato, "content", None)
        for parte in getattr(contenido, "parts", None) or []:
            datos = getattr(parte, "inline_data", None)
            if datos and datos.data:
                destino.write_bytes(datos.data)
                print(f"  {destino}  {len(datos.data) // 1024} KB")
                return True

    # Sin imagen: el motivo puede venir como texto, como razón de corte o
    # como bloqueo del prompt. Se muestran los tres para no quedar a ciegas.
    motivos = []
    for candidato in candidatos:
        razon = getattr(candidato, "finish_reason", None)
        if razon:
            motivos.append(f"finish_reason={razon}")
    bloqueo = getattr(getattr(respuesta, "prompt_feedback", None), "block_reason", None)
    if bloqueo:
        motivos.append(f"block_reason={bloqueo}")
    try:
        if respuesta.text:
            motivos.append(respuesta.text[:120])
    except Exception:
        pass

    print(f"  SIN IMAGEN {destino.name}: {'; '.join(motivos) or 'sin motivo declarado'}")
    return False


def generar_base(c: genai.Client) -> None:
    print(f"Base con {MODELO_BASE}")
    r = pedir(c, MODELO_BASE, PROMPT_BASE)
    guardar(r, BASE)
    print("\nMirala antes de seguir. Si no te convence, corré 'base' de nuevo.")


def leer_base() -> types.Part:
    if not BASE.exists():
        sys.exit(f"Falta {BASE}. Corré primero: python {sys.argv[0]} base")
    return types.Part.from_bytes(data=BASE.read_bytes(), mime_type="image/png")


def generar_giro(c: genai.Client) -> None:
    ref = leer_base()
    print(f"11 rotaciones con {MODELO_VARIANTE}")

    for i, grados in enumerate(ANGULOS, start=2):
        destino = SALIDA / "giro" / f"{i:02d}.png"
        if destino.exists():
            print(f"  {destino.name} ya existe, se saltea")
            continue

        prompt = (
            f"Using the attached image as the exact reference, generate the "
            f"same shoe rotated {grados} degrees clockwise on its vertical "
            f"axis, as if on a turntable.\n\n"
            f"Keep identical: shoe model, colors, materials, lighting setup, "
            f"camera height, camera distance, background and framing. Only the "
            f"rotation angle changes. {ENCUADRE}. {SIN_MARCAS}."
        )
        r = pedir(c, MODELO_VARIANTE, [ref, prompt])
        guardar(r, destino)


def generar_capas(c: genai.Client) -> None:
    ref = leer_base()
    print(f"5 capas con {MODELO_VARIANTE}")

    for nombre, pieza in CAPAS.items():
        destino = SALIDA / "capas" / f"{nombre}.png"
        if destino.exists():
            print(f"  {destino.name} ya existe, se saltea")
            continue

        prompt = (
            f"Using the attached image as reference, generate ONLY {pieza} of "
            f"this shoe, isolated on a pure black background.\n\n"
            f"Exact same lateral view, same lighting, and critically: the same "
            f"scale and the same position within the frame as in the reference "
            f"image, as if the rest of the shoe had been erased. No other part "
            f"of the shoe is visible. {ENCUADRE}. {SIN_MARCAS}."
        )
        r = pedir(c, MODELO_VARIANTE, [ref, prompt])
        guardar(r, destino)


def generar_detalles(c: genai.Client) -> None:
    print(f"3 detalles con {MODELO_VARIANTE}")
    for nombre, prompt in DETALLES.items():
        destino = SALIDA / "detalles" / f"{nombre}.png"
        if destino.exists():
            print(f"  {destino.name} ya existe, se saltea")
            continue
        r = pedir(c, MODELO_VARIANTE, prompt)
        guardar(r, destino)


TAREAS = {
    "base": generar_base,
    "giro": generar_giro,
    "capas": generar_capas,
    "detalles": generar_detalles,
}

if __name__ == "__main__":
    tarea = sys.argv[1] if len(sys.argv) > 1 else ""
    if tarea not in TAREAS:
        sys.exit(f"Uso: python {sys.argv[0]} [{' | '.join(TAREAS)}]")
    TAREAS[tarea](cliente())
