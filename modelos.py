from pydantic import BaseModel, Field, field_validator, model_validator


class Concepto(BaseModel):
    termino: str = Field(description="Término o concepto importante identificado en los apuntes.")
    explicacion: str = Field(description="Explicación clara y breve del término según el contenido de los apuntes.")


class Tarjeta(BaseModel):
    pregunta: str = Field(description="Pregunta breve para ayudar a repasar un dato o concepto de los apuntes.")
    respuesta: str = Field(description="Respuesta correcta y concisa a la pregunta de repaso.")


class Pregunta(BaseModel):
    enunciado: str = Field(description="Enunciado claro de una pregunta de opción múltiple sobre los apuntes.")
    opciones: list[str] = Field(description="Lista de opciones de respuesta para la pregunta.")
    correcta: int = Field(description="Índice, empezando en cero, de la opción correcta dentro de la lista de opciones.")

    @field_validator("opciones")
    @classmethod
    def validar_opciones(cls, opciones: list[str]) -> list[str]:
        if len(opciones) != 4:
            raise ValueError("La pregunta debe tener exactamente cuatro opciones.")

        if len({opcion.casefold() for opcion in opciones}) != 4:
            raise ValueError("Las cuatro opciones deben ser distintas, incluso si solo cambia el uso de mayúsculas.")

        return opciones

    @model_validator(mode="after")
    def validar_indice_correcto(self) -> "Pregunta":
        if not 0 <= self.correcta < len(self.opciones):
            raise ValueError(
                "El índice de la opción correcta debe estar entre 0 y 3 y señalar una opción existente."
            )
        return self


class Apunte(BaseModel):
    titulo: str = Field(description="Título breve que describa el tema principal de la página.")
    materia: str = Field(description="Nombre de la materia o asignatura a la que corresponde el contenido.")
    resumen: str = Field(description="Resumen claro y conciso de las ideas principales de la página.")
    conceptos: list[Concepto] = Field(description="Lista de conceptos importantes de la página con sus explicaciones.")
    tarjetas: list[Tarjeta] = Field(description="Lista de tarjetas de pregunta y respuesta para repasar el contenido.")
    examen: list[Pregunta] = Field(description="Lista de preguntas de opción múltiple basadas en el contenido.")
    dificultad: int = Field(description="Nivel de dificultad del contenido de la página expresado como un número entero.")

    @field_validator("dificultad")
    @classmethod
    def validar_dificultad(cls, dificultad: int) -> int:
        if not 1 <= dificultad <= 5:
            raise ValueError("La dificultad debe ser un número entero entre 1 y 5.")
        return dificultad

    @field_validator("conceptos")
    @classmethod
    def validar_cantidad_conceptos(cls, conceptos: list[Concepto]) -> list[Concepto]:
        if len(conceptos) < 3:
            raise ValueError("El apunte debe incluir al menos 3 conceptos.")
        return conceptos

    @field_validator("tarjetas")
    @classmethod
    def validar_cantidad_tarjetas(cls, tarjetas: list[Tarjeta]) -> list[Tarjeta]:
        if len(tarjetas) < 5:
            raise ValueError("El apunte debe incluir al menos 5 tarjetas.")
        return tarjetas

    @field_validator("examen")
    @classmethod
    def validar_cantidad_preguntas(cls, examen: list[Pregunta]) -> list[Pregunta]:
        if len(examen) < 3:
            raise ValueError("El apunte debe incluir al menos 3 preguntas de examen.")
        return examen
