from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import mesa


class EstadoAgente(Enum):
    NEUTRAL = "neutral"
    INTERESADO = "interesado"
    ESCEPTICO = "esceptico"
    ADOPTADO = "adoptado"
    RECHAZADO = "rechazado"


@dataclass
class PerfilEconomico:
    ingreso_mensual: int
    disposicion_pago: float
    sensibilidad_precio: float
    deuda_actual: float
    ahorro_disponible_meses: float = 2.0    # meses de ingreso ahorrados
    beneficios_empresa: bool = False         # empresa financia educación


@dataclass
class PerfilPsicologico:
    apertura_cambio: float
    aversion_riesgo: float
    influenciabilidad: float
    orientacion_logro: float
    pragmatismo: float
    autoeficacia_academica: float = 0.60    # cree que puede estudiar con éxito
    necesidad_reconocimiento: float = 0.50  # valora títulos y credenciales
    satisfaccion_laboral: float = 0.55      # alta satisfacción → menos motivado a cambiar
    ansiedad_academica: float = 0.30        # miedo a retomar estudios


@dataclass
class PerfilContextual:
    modalidad_preferida: str = "indiferente"     # "online","presencial","hibrida","indiferente"
    horas_disponibles_semana: int = 10            # horas reales para estudiar
    anios_desde_ultimo_estudio: int = 7           # barrrera psicológica de retomar
    red_apoyo_social: float = 0.60                # apoyo de familia/pareja
    pares_con_estudios_extra: float = 0.40        # proporción de pares que hicieron algo similar
    exposicion_campo: float = 0.50                # familiaridad con el área del programa


class ArcaAgent(mesa.Agent):
    def __init__(
        self,
        model,
        nombre: str,
        edad: int,
        genero: str,
        ciudad: str,
        nivel_educativo: str,
        situacion_laboral: str,
        perfil_economico: PerfilEconomico,
        perfil_psicologico: PerfilPsicologico,
        perfil_contextual: Optional[PerfilContextual] = None,
        activo_en_redes: bool = True,
        ocupacion: str = "",
        area_profesional: str = "",
    ):
        super().__init__(model)
        self.nombre = nombre
        self.edad = edad
        self.genero = genero
        self.ciudad = ciudad
        self.nivel_educativo = nivel_educativo
        self.situacion_laboral = situacion_laboral
        self.ocupacion = ocupacion
        self.area_profesional = area_profesional
        self.activo_en_redes = activo_en_redes

        self.economico = perfil_economico
        self.psicologico = perfil_psicologico
        self.contextual = perfil_contextual or PerfilContextual()

        self.estado: EstadoAgente = EstadoAgente.NEUTRAL
        self.nivel_interes: float = 0.0
        self.nivel_resistencia: float = 0.0
        self.historial_interacciones: list[dict] = []
        self.razon_decision: str = ""
        self.step_adopcion: Optional[int] = None
        self.influencias_recibidas: list[float] = []

    @property
    def es_influyente(self) -> bool:
        return self.activo_en_redes and self.psicologico.orientacion_logro > 0.6

    @property
    def capacidad_pago_max(self) -> int:
        return int(self.economico.ingreso_mensual * self.economico.disposicion_pago * 12)

    def registrar_interaccion(self, tipo: str, delta_interes: float, fuente: str = ""):
        step = getattr(self.model, "steps", 0)
        self.historial_interacciones.append({
            "step": step,
            "tipo": tipo,
            "delta_interes": delta_interes,
            "fuente": fuente,
            "estado_post": self.estado.value,
        })

    def actualizar_estado(self):
        if self.estado in (EstadoAgente.ADOPTADO, EstadoAgente.RECHAZADO):
            return
        if self.nivel_interes >= 0.75:
            self.estado = EstadoAgente.ADOPTADO
            self.step_adopcion = getattr(self.model, "steps", 0)
        elif self.nivel_interes >= 0.45:
            self.estado = EstadoAgente.INTERESADO
        elif self.nivel_interes <= -0.4:
            self.estado = EstadoAgente.RECHAZADO
        elif self.nivel_interes <= -0.1:
            self.estado = EstadoAgente.ESCEPTICO
        else:
            self.estado = EstadoAgente.NEUTRAL

    def step(self):
        pass

    def to_dict(self) -> dict:
        ctx = self.contextual
        return {
            "id": self.unique_id,
            "nombre": self.nombre,
            "edad": self.edad,
            "genero": self.genero,
            "ciudad": self.ciudad,
            "nivel_educativo": self.nivel_educativo,
            "situacion_laboral": self.situacion_laboral,
            "ocupacion": self.ocupacion,
            "area_profesional": self.area_profesional,
            # económico
            "ingreso_mensual": self.economico.ingreso_mensual,
            "disposicion_pago": self.economico.disposicion_pago,
            "sensibilidad_precio": self.economico.sensibilidad_precio,
            "deuda_actual": self.economico.deuda_actual,
            "ahorro_disponible_meses": self.economico.ahorro_disponible_meses,
            "beneficios_empresa": self.economico.beneficios_empresa,
            # psicológico
            "apertura_cambio": self.psicologico.apertura_cambio,
            "aversion_riesgo": self.psicologico.aversion_riesgo,
            "influenciabilidad": self.psicologico.influenciabilidad,
            "orientacion_logro": self.psicologico.orientacion_logro,
            "pragmatismo": self.psicologico.pragmatismo,
            "autoeficacia_academica": self.psicologico.autoeficacia_academica,
            "necesidad_reconocimiento": self.psicologico.necesidad_reconocimiento,
            "satisfaccion_laboral": self.psicologico.satisfaccion_laboral,
            "ansiedad_academica": self.psicologico.ansiedad_academica,
            # contextual
            "modalidad_preferida": ctx.modalidad_preferida,
            "horas_disponibles_semana": ctx.horas_disponibles_semana,
            "anios_desde_ultimo_estudio": ctx.anios_desde_ultimo_estudio,
            "red_apoyo_social": ctx.red_apoyo_social,
            "pares_con_estudios_extra": ctx.pares_con_estudios_extra,
            "exposicion_campo": ctx.exposicion_campo,
            # estado simulación
            "estado": self.estado.value,
            "nivel_interes": round(self.nivel_interes, 3),
            "activo_en_redes": self.activo_en_redes,
        }

    def __repr__(self) -> str:
        return f"<ArcaAgent #{self.unique_id} {self.nombre} [{self.estado.value}]>"
