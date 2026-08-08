"""
Recorta los cuadros del giro y los exporta a WebP en dos tamaños.

    python scripts/nandu/optimizar.py

El recorte es un recuadro FIJO, igual para los 36. Recortar cada cuadro a
su propio contenido haría que la zapatilla saltara entre cuadros: a 90
grados la silueta es mucho más angosta que de perfil, y el centro se
correría.

El recuadro sale de la unión de las 36 siluetas más un margen. Del lienzo
original de 1400x1400, el 68% es transparente.
"""

from pathlib import Path

from PIL import Image

ORIGEN = Path("public/nandu/giro")
DESTINO = Path("public/nandu/giro")

# Unión de las 36 siluetas (176,431 a 1224,1030) más 24px de margen
RECORTE = (152, 407, 152 + 1096, 407 + 648)

# Ancho de salida y su carpeta. El alto sale de la proporción del recorte.
TAMANOS = (1096, 548)

CALIDAD = 82


def main() -> None:
    fuentes = sorted(ORIGEN.glob("[0-9][0-9].png"))
    if not fuentes:
        raise SystemExit(f"No hay PNG numerados en {ORIGEN}")

    ancho_recorte = RECORTE[2] - RECORTE[0]
    alto_recorte = RECORTE[3] - RECORTE[1]
    proporcion = alto_recorte / ancho_recorte

    print(f"{len(fuentes)} cuadros")
    print(f"recorte fijo: {ancho_recorte} x {alto_recorte} desde ({RECORTE[0]}, {RECORTE[1]})\n")

    for ancho in TAMANOS:
        alto = round(ancho * proporcion)
        carpeta = DESTINO / str(ancho)
        carpeta.mkdir(parents=True, exist_ok=True)
        total = 0

        for f in fuentes:
            im = Image.open(f).convert("RGBA").crop(RECORTE)
            if ancho != ancho_recorte:
                im = im.resize((ancho, alto), Image.LANCZOS)

            salida = carpeta / f"{f.stem}.webp"
            im.save(salida, "WEBP", quality=CALIDAD, method=6)
            total += salida.stat().st_size

        print(
            f"  {ancho} x {alto}:  {total // 1024} KB en total, "
            f"{total // len(fuentes) // 1024} KB por cuadro"
        )

    pesado = sum(f.stat().st_size for f in fuentes)
    print(f"\noriginales PNG: {pesado // 1024 // 1024} MB")


if __name__ == "__main__":
    main()
