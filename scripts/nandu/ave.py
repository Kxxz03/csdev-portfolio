"""El ñandú para la sección de origen. Una sola imagen."""
import os
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "project-1f9e5213-8aff-44a2-bf6")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

from pathlib import Path
from google import genai
from google.genai import types

PROMPT = (
    "A photograph taken in a photography studio, on a seamless charcoal "
    "black paper backdrop that fills the entire frame. The backdrop is very "
    "dark, near black, evenly lit, no texture, no gradient.\n\n"
    "Subject: a greater rhea (ñandú), the large flightless South American "
    "bird, standing in full profile facing right, its long neck slightly "
    "forward, one leg lifted mid-stride. Shaggy grey-brown plumage with "
    "visible feather texture, powerful bare legs, three-toed feet.\n\n"
    "Dramatic low side lighting from the right rim-lights the edge of the "
    "bird and leaves the far side in deep shadow. The bird floats against "
    "the black: no ground, no horizon, no shadow beneath it.\n\n"
    "Muted, almost monochrome, with a faint warm amber cast in the "
    "highlights. Editorial, restrained, photorealistic. Vertical 3:4 "
    "composition, the bird occupies 70% of the frame height, generous "
    "margins. No text, no logos, no people."
)

c = genai.Client()
r = c.models.generate_content(
    model="gemini-3-pro-image",
    contents=PROMPT,
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="3:4"),
    ),
)
destino = Path("public/nandu/ave.png")
for parte in r.candidates[0].content.parts or []:
    d = getattr(parte, "inline_data", None)
    if d and d.data:
        destino.write_bytes(d.data)
        print(f"{destino}  {len(d.data)//1024} KB")
        break
else:
    print("sin imagen:", getattr(r, "text", "")[:160])
