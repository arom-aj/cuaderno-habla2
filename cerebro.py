import json

from google import genai
from google.genai import types

from modelos import Apunte


MODELO = "gemini-3.8-flash"
INSTRUCCION_SISTEMA = (
    "Actúa como un profesor paciente de bachillerato de El Salvador. "
    "Escribe siempre en español salvadoreño claro. Basa tu respuesta únicamente "
    "en lo que se ve en la imagen y no inventes temas. Si la foto está borrosa, "
    "dilo en el resumen en vez de inventar. Haz que las opciones incorrectas "
    "del examen sean creíbles y no absurdas, y varía la posición de la respuesta "
    "correcta entre preguntas."
)


class ImagenIlegible(Exception):
    """La imagen no se pudo convertir en un apunte útil."""


def crear_cliente(api_key: str) -> genai.Client:
    if not api_key or not api_key.strip():
        raise ValueError("La llave de API no puede estar vacía.")
    return genai.Client(api_key=api_key)


def analizar_pagina(datos_imagen: bytes, tipo_mime: str, cliente: genai.Client) -> Apunte:
    if not datos_imagen:
        raise ValueError("No se recibió ninguna imagen para analizar.")

    respuesta = cliente.models.generate_content(
        model=MODELO,
        contents=[
            types.Part.from_bytes(data=datos_imagen, mime_type=tipo_mime),
            "Analiza esta página y prepara el apunte solicitado.",
        ],
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCCION_SISTEMA,
            response_mime_type="application/json",
            response_schema=Apunte,
            temperature=0.4,
        ),
    )

    if isinstance(respuesta.parsed, Apunte):
        return respuesta.parsed

    if respuesta.text:
        try:
            return Apunte.model_validate(json.loads(respuesta.text))
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    raise ImagenIlegible(
        "No pudimos leer bien esta página. Probá con una foto más clara, enfocada "
        "y con buena iluminación."
    )


def calificar(apunte: Apunte, respuestas: dict) -> tuple[int, int]:
    total = len(apunte.examen)
    aciertos = sum(
        respuestas.get(indice) == pregunta.correcta
        for indice, pregunta in enumerate(apunte.examen)
    )
    return aciertos, total
