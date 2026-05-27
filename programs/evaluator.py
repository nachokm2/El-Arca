import json
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ProgramaAcademico(BaseModel):
    id: str = ""
    nombre: str
    institucion: str
    tipo: str = "diplomado"
    duracion_meses: int = Field(ge=1, le=36)
    horas_totales: int = Field(ge=10, le=2000)
    modalidad: str
    precio_clp: int = Field(ge=50_000, le=50_000_000)
    precio_cuotas: int = Field(ge=1, le=60, default=1)
    tiene_financiamiento: bool = False
    requisitos: list[str] = []
    certificacion: str = ""
    descripcion: str = ""
    competencias: list[str] = []
    mercado_laboral: str = ""
    reputacion_institucion: float = Field(ge=0.0, le=1.0, default=0.7)
    relevancia_mercado: float = Field(ge=0.0, le=1.0, default=0.6)
    modalidad_adecuada: float = Field(ge=0.0, le=1.0, default=0.7)
    factor_novedad: float = Field(ge=0.0, le=1.0, default=0.5)
    incertidumbre_percibida: float = Field(ge=0.0, le=1.0, default=0.3)
    retorno_profesional: float = Field(ge=0.0, le=1.0, default=0.6)
    roi_percibido: float = Field(ge=0.0, le=1.0, default=0.5)

    @field_validator("modalidad")
    @classmethod
    def validar_modalidad(cls, v: str) -> str:
        opciones = ["presencial", "online_sincronica", "online_asincronica", "hibrida"]
        if v not in opciones:
            raise ValueError(f"Modalidad debe ser una de: {opciones}")
        return v

    def to_dict(self) -> dict:
        return self.model_dump()


@dataclass
class EvaluacionPrograma:
    programa: dict
    score_global: float
    score_precio: float
    score_mercado: float
    score_propuesta_valor: float
    fortalezas: list[str]
    debilidades: list[str]
    oportunidades: list[str]
    amenazas: list[str]
    recomendaciones: list[str]


class ProgramEvaluator:
    """Evalúa la competitividad y atractivo de un programa académico."""

    PESOS_SCORE = {
        "precio": 0.30,
        "mercado": 0.35,
        "propuesta_valor": 0.35,
    }

    def evaluar(self, programa: dict) -> EvaluacionPrograma:
        s_precio = self._score_precio(programa)
        s_mercado = self._score_mercado(programa)
        s_propuesta = self._score_propuesta_valor(programa)

        score_global = (
            self.PESOS_SCORE["precio"] * s_precio
            + self.PESOS_SCORE["mercado"] * s_mercado
            + self.PESOS_SCORE["propuesta_valor"] * s_propuesta
        )

        return EvaluacionPrograma(
            programa=programa,
            score_global=round(score_global, 3),
            score_precio=round(s_precio, 3),
            score_mercado=round(s_mercado, 3),
            score_propuesta_valor=round(s_propuesta, 3),
            fortalezas=self._fortalezas(programa),
            debilidades=self._debilidades(programa),
            oportunidades=self._oportunidades(programa),
            amenazas=self._amenazas(programa),
            recomendaciones=self._recomendaciones(programa, score_global),
        )

    def _score_precio(self, p: dict) -> float:
        precio = p.get("precio_clp", 1_500_000)
        cuotas = p.get("precio_cuotas", 1)
        financiamiento = p.get("tiene_financiamiento", False)

        cuota_mensual = precio / max(cuotas, 1)
        # Accesible si la cuota mensual equivale a menos de 1 sueldo mínimo (~500k CLP 2024)
        if cuota_mensual <= 200_000:
            score = 0.9
        elif cuota_mensual <= 300_000:
            score = 0.7
        elif cuota_mensual <= 500_000:
            score = 0.5
        else:
            score = 0.3

        if financiamiento:
            score = min(score + 0.1, 1.0)
        return score

    def _score_mercado(self, p: dict) -> float:
        return float(
            0.5 * p.get("relevancia_mercado", 0.6)
            + 0.3 * p.get("retorno_profesional", 0.6)
            + 0.2 * p.get("roi_percibido", 0.5)
        )

    def _score_propuesta_valor(self, p: dict) -> float:
        return float(
            0.4 * p.get("reputacion_institucion", 0.7)
            + 0.3 * p.get("modalidad_adecuada", 0.7)
            + 0.2 * (1 - p.get("incertidumbre_percibida", 0.3))
            + 0.1 * p.get("factor_novedad", 0.5)
        )

    def _fortalezas(self, p: dict) -> list[str]:
        items = []
        if p.get("reputacion_institucion", 0) >= 0.7:
            items.append(f"Institución reconocida: {p.get('institucion', '')}")
        if p.get("relevancia_mercado", 0) >= 0.8:
            items.append("Alta relevancia en el mercado laboral actual")
        if p.get("tiene_financiamiento"):
            items.append("Opciones de financiamiento disponibles")
        if p.get("precio_cuotas", 1) >= 6:
            items.append(f"Pago en {p['precio_cuotas']} cuotas facilita el acceso")
        if p.get("roi_percibido", 0) >= 0.75:
            items.append("Retorno de inversión percibido alto")
        return items or ["Sin fortalezas destacadas detectadas"]

    def _debilidades(self, p: dict) -> list[str]:
        items = []
        precio = p.get("precio_clp", 0)
        if precio > 1_500_000:
            items.append(f"Precio alto (${precio:,} CLP) puede limitar acceso")
        if p.get("incertidumbre_percibida", 0) >= 0.5:
            items.append("Alta incertidumbre percibida respecto al retorno")
        if p.get("reputacion_institucion", 0) < 0.6:
            items.append("Reputación institucional que aún se está consolidando")
        modalidades_preferidas = ["online_sincronica", "hibrida"]
        if p.get("modalidad") not in modalidades_preferidas:
            items.append(f"Modalidad '{p.get('modalidad')}' puede no adaptarse a todos")
        return items or ["Sin debilidades significativas detectadas"]

    def _oportunidades(self, p: dict) -> list[str]:
        items = []
        if p.get("factor_novedad", 0) >= 0.7:
            items.append("Área temática emergente con creciente demanda")
        if p.get("relevancia_mercado", 0) >= 0.85:
            items.append("Mercado laboral con déficit de profesionales en esta área")
        items.append("Posibilidad de alianzas con empresas para prácticas o bolsa laboral")
        return items

    def _amenazas(self, p: dict) -> list[str]:
        items = [
            "Competencia de programas similares en otras instituciones",
            "Cambios rápidos en el mercado laboral pueden deprecar habilidades",
        ]
        if p.get("modalidad") in ["presencial", "hibrida"]:
            items.append("Barreras geográficas pueden limitar la matrícula en regiones")
        return items

    def _recomendaciones(self, p: dict, score: float) -> list[str]:
        rec = []
        if score < 0.5:
            rec.append("Revisar propuesta de valor integral — el score global está por debajo de lo competitivo")
        if p.get("precio_clp", 0) > 1_200_000 and not p.get("tiene_financiamiento"):
            rec.append("Implementar opciones de financiamiento SENCE o crédito educativo")
        if not p.get("certificacion"):
            rec.append("Agregar certificación reconocida mejora la percepción de valor")
        if len(p.get("competencias", [])) < 4:
            rec.append("Detallar más las competencias adquiridas en la malla curricular")
        return rec or ["El programa está bien posicionado. Monitorear métricas de inscripción."]
