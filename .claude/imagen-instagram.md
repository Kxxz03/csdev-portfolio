# +CSdev — Instrucciones de imagen para Instagram

Usa este archivo cuando generes imágenes de mockups/demos de sitios web para publicar como @its_csdev en Instagram.

---

## Identidad de marca

**Nombre:** +CSdev  
**Handle:** @its_csdev  
**Tagline:** "Los sitios aburridos no me interesan y probablemente tampoco a tus clientes."  
**Tono:** Editorial, bold, con personalidad. Nunca genérico, nunca template.

---

## Paleta

| Token         | Hex       | Uso                                     |
|---------------|-----------|-----------------------------------------|
| `--yellow`    | `#FFD000` | Acento primario, fondos de énfasis      |
| `--black`     | `#0D0D0D` | Base oscura, texto sobre claro          |
| `--white`     | `#F7F6F1` | Off-white cálido, fondos primarios      |
| `--ember`     | `#E85D04` | Acento fuego (demos industriales/gym)   |
| `--steel`     | `#4A7DA7` | Azul acero, apoyo secundario            |

La imagen de marca principal es **amarillo + negro**. Los acentos de proyecto (ember, etc.) son del demo, no de CSdev.

---

## Tipografía

- **Display / headlines:** Space Grotesk Bold 700–900, tracking negativo, mayúsculas
- **Body / labels:** Space Grotesk Regular/Medium 400–500
- **Regla:** Tamaños masivos, alto contraste. Nunca tipografía decorativa genérica.

---

## Estilo visual de las imágenes

### Composición
- Ratio **1:1** (1080×1080) o **4:5** (1080×1350) para feed
- Ratio **9:16** (1080×1920) para Stories/Reels
- Mockup del sitio ocupa 60–75% del encuadre
- Fondo: negro sólido `#0D0D0D`, gradiente oscuro, o amarillo `#FFD000`
- El dispositivo/pantalla va ligeramente inclinado (3–8°) para dinamismo — nunca perfectamente plano
- Sombra profunda bajo el device: `0 32px 80px rgba(0,0,0,0.6)`

### Device mockup
- Usar **MacBook** para demos de landing/e-commerce full desktop
- Usar **iPhone Pro** (island visible) para mobile-first o sitios responsive
- Usar **ambos juntos** cuando el punto sea mostrar el responsive
- Los mockups deben ser oscuros/premium — no blancos plastificados

### Overlays y detalles de marca
- Logo `+CSdev` en esquina inferior derecha — pequeño, amarillo sobre negro
- Etiqueta del proyecto en esquina superior izquierda: nombre del cliente en caps pequeñas con `/` delante (ej. `/MJÖLNIR`)
- Número de work opcional: `01`, `02`, etc. — monoespacio, muy pequeño, con baja opacidad
- Línea separadora: 1px amarillo cuando aplique

### Texto en imagen (máximo 2 líneas)
- Una frase corta del proyecto o del outcome — nunca el nombre del servicio
- Ejemplos válidos: `"Gym que intimida antes de la primera clase"` / `"E-commerce que cierra solo"` / `"Landing que no parece landing"`
- Nunca: "Diseño web", "Landing page profesional", "Proyecto #1"

---

## Reglas de generación de imagen

### SÍ hacer
- Composición asimétrica con peso visual en diagonal
- Un solo punto focal claro (el mockup del sitio)
- Ruido/grano sutil sobre el fondo para textura
- Tipografía masiva si hay texto decorativo en el fondo
- Paleta reducida: máximo 2–3 colores por imagen

### NO hacer
- Fondos blancos o grises neutros
- Múltiples elementos compitiendo por atención
- Efectos de degradado pastel o colores "tech" clichés (morado, azul neón)
- Texto descriptivo genérico ("Desarrollo web · Diseño UI")
- Marcas de agua con logos grandes centrados

---

## Templates por tipo de post

### Post de nuevo work (Feed 1:1)
```
Fondo: negro (#0D0D0D) con ruido 3%
Mockup: MacBook inclinado 5° antihorario, centrado-izquierdo
Área derecha: label del proyecto + frase corta
Footer: "@its_csdev" en amarillo, muy pequeño
```

### Comparación before/after (Feed 4:5)
```
Mitad izquierda: screenshot "antes" con overlay rojo semitransparente + "X"
Mitad derecha: screenshot "después" limpio + checkmark amarillo
Línea divisoria: 2px amarillo vertical al centro
```

### Story de proceso (9:16)
```
Fondo: amarillo (#FFD000)
Texto negro masivo: verbo de acción ("CONSTRUYENDO", "LANZANDO")
Nombre del proyecto debajo, más pequeño
Mockup parcial visible desde abajo del frame
```

### Reel thumbnail (1:1)
```
Fondo: oscuro con gradiente de izquierda
Texto en mayúsculas bold izquierda: pregunta o dato del proyecto
Mockup del sitio a la derecha, cortado en el borde
Flecha o ícono play en amarillo
```

---

## Proyectos actuales para referencias visuales

| Work | Estética del demo | Color clave |
|------|-------------------|-------------|
| 01 Mjölnir Gym | Industrial, negro carbón, hierro | Ember `#E85D04` |
| 02 BARRO Motocross | Neo-brutalismo, naranja ignición | `#FF4D00` |
| 03–04 | Por definir | — |

---

## Prompt base para generación

Cuando generes imágenes para @its_csdev, usa este prompt como base y ajusta por proyecto:

```
Premium dark mockup, [MacBook/iPhone Pro] displaying [NOMBRE DEL SITIO], 
tilted 5 degrees, black background with subtle film grain, 
deep shadow 0 32px 80px rgba(0,0,0,0.6), 
brand accent color [HEX], 
editorial composition asymmetric layout, 
small +CSdev yellow label bottom right, 
project name /[NOMBRE] top left in small caps, 
no generic tech gradients, no white backgrounds, 
high contrast, cinematic, portfolio-grade
```
