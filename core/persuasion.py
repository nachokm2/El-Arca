import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import ArcaAgent


class PersuasionEngine:
    """
    Motor matemático que calcula el impacto persuasivo de un programa
    sobre un agente individual, considerando su perfil económico,
    psicológico y el contexto social.
    """

    def __init__(
        self,
        peso_economico: float = 0.35,
        peso_psicologico: float = 0.30,
        peso_social: float = 0.20,
        peso_programa: float = 0.15,
    ):
        total = peso_economico + peso_psicologico + peso_social + peso_programa
        self.w_eco = peso_economico / total
        self.w_psi = peso_psicologico / total
        self.w_soc = peso_social / total
        self.w_prog = peso_programa / total

    def calcular_impacto(
        self,
        agente: "ArcaAgent",
        programa: dict,
        presion_social: float = 0.0,
    ) -> float:
        """
        Retorna un delta de interés en [-1, 1].
        Positivo = acerca al agente a adoptar el programa.
        Negativo = lo aleja.
        """
        eco = self._score_economico(agente, programa)
        psi = self._score_psicologico(agente, programa)
        soc = self._score_social(agente, presion_social)
        prog = self._score_programa(programa)

        raw = (
            self.w_eco * eco
            + self.w_psi * psi
            + self.w_soc * soc
            + self.w_prog * prog
        )
        ruido = np.random.normal(0, 0.03)
        return float(np.clip(raw + ruido, -1.0, 1.0))

    def _score_economico(self, agente: "ArcaAgent", programa: dict) -> float:
        precio = programa.get("precio_clp", 1_000_000)
        capacidad = agente.capacidad_pago_max

        if capacidad <= 0:
            return -0.8

        ratio_precio = precio / capacidad
        if ratio_precio <= 0.3:
            score_precio = 0.8
        elif ratio_precio <= 0.6:
            score_precio = 0.4
        elif ratio_precio <= 1.0:
            score_precio = 0.0
        elif ratio_precio <= 1.5:
            score_precio = -0.4
        else:
            score_precio = -0.9

        # sensibilidad amplifica/atenúa el efecto del precio
        sensibilidad = agente.economico.sensibilidad_precio
        score_precio *= (0.5 + sensibilidad)

        # financiamiento disponible mitiga
        tiene_financiamiento = programa.get("tiene_financiamiento", False)
        if tiene_financiamiento and ratio_precio > 0.6:
            score_precio += 0.2

        return float(np.clip(score_precio, -1.0, 1.0))

    def _score_psicologico(self, agente: "ArcaAgent", programa: dict) -> float:
        psi = agente.psicologico

        # apertura al cambio positiva para programas innovadores
        novedad = programa.get("factor_novedad", 0.5)
        score_apertura = psi.apertura_cambio * novedad * 0.5

        # aversión al riesgo negativa si el programa es percibido incierto
        incertidumbre = programa.get("incertidumbre_percibida", 0.3)
        score_riesgo = -psi.aversion_riesgo * incertidumbre * 0.4

        # orientación al logro positiva si hay retorno profesional claro
        retorno_profesional = programa.get("retorno_profesional", 0.6)
        score_logro = psi.orientacion_logro * retorno_profesional * 0.5

        # pragmatismo: valora ROI concreto
        roi_percibido = programa.get("roi_percibido", 0.5)
        score_pragmatismo = psi.pragmatismo * roi_percibido * 0.3

        total = score_apertura + score_riesgo + score_logro + score_pragmatismo
        return float(np.clip(total, -1.0, 1.0))

    def _score_social(self, agente: "ArcaAgent", presion_social: float) -> float:
        influencia = agente.psicologico.influenciabilidad
        return float(np.clip(influencia * presion_social, -1.0, 1.0))

    def _score_programa(self, programa: dict) -> float:
        reputacion = programa.get("reputacion_institucion", 0.7)
        relevancia = programa.get("relevancia_mercado", 0.6)
        modalidad_ok = programa.get("modalidad_adecuada", 0.7)
        score = (reputacion * 0.4 + relevancia * 0.35 + modalidad_ok * 0.25)
        return float(np.clip(score * 2 - 1, -1.0, 1.0))

    def calcular_presion_social(self, vecinos: list["ArcaAgent"]) -> float:
        if not vecinos:
            return 0.0
        scores = []
        for v in vecinos:
            peso = 1.5 if v.es_influyente else 1.0
            scores.append(v.nivel_interes * peso)
        return float(np.clip(np.mean(scores), -1.0, 1.0))
