import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import ArcaAgent


class PersuasionEngine:
    """
    Motor de persuasión multi-dimensional.

    Dimensiones:
      eco  (0.35) — capacidad y situación financiera real
      psi  (0.30) — motivación, autoeficacia, satisfacción laboral, ansiedad
      soc  (0.20) — red de vecinos + soporte personal + prueba social
      fit  (0.15) — adecuación del programa al perfil (modalidad + tiempo)
    """

    def __init__(
        self,
        peso_economico: float = 0.35,
        peso_psicologico: float = 0.30,
        peso_social: float = 0.20,
        peso_programa: float = 0.15,
    ):
        total = peso_economico + peso_psicologico + peso_social + peso_programa
        self.w_eco  = peso_economico  / total
        self.w_psi  = peso_psicologico / total
        self.w_soc  = peso_social      / total
        self.w_prog = peso_programa    / total

    def calcular_impacto(
        self,
        agente: "ArcaAgent",
        programa: dict,
        presion_social: float = 0.0,
    ) -> float:
        eco  = self._score_economico(agente, programa)
        psi  = self._score_psicologico(agente, programa)
        soc  = self._score_social(agente, presion_social)
        prog = self._score_programa(agente, programa)

        raw = (self.w_eco * eco + self.w_psi * psi +
               self.w_soc * soc + self.w_prog * prog)
        ruido = np.random.normal(0, 0.03)
        return float(np.clip(raw + ruido, -1.0, 1.0))

    # ── dimensión económica ──────────────────────────────────────────────────

    def _score_economico(self, agente: "ArcaAgent", programa: dict) -> float:
        eco = agente.economico

        # Si la empresa cubre la educación, la barrera económica casi desaparece
        if eco.beneficios_empresa:
            return 0.75

        precio    = programa.get("precio_clp", 1_000_000)
        capacidad = agente.capacidad_pago_max

        if capacidad <= 0:
            return -0.8

        ratio = precio / capacidad
        if ratio <= 0.3:    score = 0.80
        elif ratio <= 0.6:  score = 0.40
        elif ratio <= 1.0:  score = 0.00
        elif ratio <= 1.5:  score = -0.40
        else:               score = -0.90

        # sensibilidad amplifica o atenúa el efecto del precio
        score *= (0.5 + eco.sensibilidad_precio)

        # financiamiento del programa mitiga si el precio es alto
        if programa.get("tiene_financiamiento") and ratio > 0.6:
            score += 0.20

        # ahorro disponible reduce la ansiedad financiera cuando el precio aprieta
        if ratio > 0.6:
            factor_ahorro = min(eco.ahorro_disponible_meses / 6.0, 1.0)
            score += factor_ahorro * 0.25

        return float(np.clip(score, -1.0, 1.0))

    # ── dimensión psicológica ────────────────────────────────────────────────

    def _score_psicologico(self, agente: "ArcaAgent", programa: dict) -> float:
        psi = agente.psicologico
        ctx = agente.contextual

        retorno     = programa.get("retorno_profesional", 0.60)
        novedad     = programa.get("factor_novedad", 0.50)
        incert      = programa.get("incertidumbre_percibida", 0.30)
        roi         = programa.get("roi_percibido", 0.50)
        reputacion  = programa.get("reputacion_institucion", 0.70)

        # insatisfacción laboral genera motivación de cambio
        score_motivacion = (1.0 - psi.satisfaccion_laboral) * 0.35

        # autoeficacia × retorno: "puedo hacerlo y valdrá la pena"
        score_autoeficacia = psi.autoeficacia_academica * retorno * 0.35

        # necesidad de reconocimiento × prestigio institucional
        score_reconocimiento = psi.necesidad_reconocimiento * reputacion * 0.25

        # apertura al cambio × novedad del programa
        score_apertura = psi.apertura_cambio * novedad * 0.25

        # aversión al riesgo × incertidumbre percibida
        score_riesgo = -psi.aversion_riesgo * incert * 0.30

        # orientación al logro × retorno profesional
        score_logro = psi.orientacion_logro * retorno * 0.25

        # ansiedad académica: se amplifica con los años sin estudiar
        factor_tiempo = min(ctx.anios_desde_ultimo_estudio / 15.0, 1.0)
        score_ansiedad = -psi.ansiedad_academica * (0.5 + factor_tiempo * 0.5) * 0.35

        # pragmatismo × ROI concreto
        score_pragmatismo = psi.pragmatismo * roi * 0.20

        total = (score_motivacion + score_autoeficacia + score_reconocimiento +
                 score_apertura + score_riesgo + score_logro +
                 score_ansiedad + score_pragmatismo)

        return float(np.clip(total, -1.0, 1.0))

    # ── dimensión social ─────────────────────────────────────────────────────

    def _score_social(self, agente: "ArcaAgent", presion_social: float) -> float:
        psi = agente.psicologico
        ctx = agente.contextual

        # presión de la red de vecinos (puede ser positiva o negativa)
        score_red = psi.influenciabilidad * presion_social

        # soporte contextual: apoyo personal + prueba social + familiaridad
        soporte = (
            ctx.red_apoyo_social         * 0.45 +
            ctx.pares_con_estudios_extra * 0.35 +
            ctx.exposicion_campo         * 0.20
        )  # promedio ponderado en [0, 1]
        # centrar en 0 (media esperada ≈ 0.5 → contribución ≈ 0)
        score_contexto = (soporte - 0.5) * 0.80

        return float(np.clip(score_red * 0.65 + score_contexto * 0.35, -1.0, 1.0))

    # ── dimensión fit programa ───────────────────────────────────────────────

    def _score_programa(self, agente: "ArcaAgent", programa: dict) -> float:
        ctx = agente.contextual

        reputacion = programa.get("reputacion_institucion", 0.70)
        relevancia = programa.get("relevancia_mercado", 0.60)

        # fit de modalidad preferida vs modalidad del programa
        modalidad_prog = programa.get("modalidad", "online_sincronica")
        pref = ctx.modalidad_preferida
        if pref == "indiferente":
            fit_modalidad = 0.70
        elif pref == "online" and "online" in modalidad_prog:
            fit_modalidad = 1.00
        elif pref == "presencial" and "presencial" in modalidad_prog:
            fit_modalidad = 1.00
        elif pref == "hibrida" and "hibrida" in modalidad_prog:
            fit_modalidad = 1.00
        elif pref == "hibrida":
            fit_modalidad = 0.55  # parcialmente compatible
        elif pref == "online" and modalidad_prog == "hibrida":
            fit_modalidad = 0.60
        else:
            fit_modalidad = 0.15  # mismatch fuerte

        # fit de disponibilidad horaria
        horas_req = programa.get("horas_semanales_requeridas", 10)
        ratio_h = ctx.horas_disponibles_semana / max(horas_req, 1)
        if ratio_h >= 1.5:    score_horas = 1.00
        elif ratio_h >= 1.0:  score_horas = 0.70
        elif ratio_h >= 0.7:  score_horas = 0.35
        elif ratio_h >= 0.5:  score_horas = 0.00
        else:                 score_horas = -0.50

        score = (reputacion    * 0.28 +
                 relevancia    * 0.24 +
                 fit_modalidad * 0.28 +
                 score_horas   * 0.20)

        return float(np.clip(score * 2 - 1, -1.0, 1.0))

    # ── presión social de vecinos ────────────────────────────────────────────

    def calcular_presion_social(self, vecinos: list["ArcaAgent"]) -> float:
        if not vecinos:
            return 0.0
        scores = []
        for v in vecinos:
            peso = 1.5 if v.es_influyente else 1.0
            scores.append(v.nivel_interes * peso)
        return float(np.clip(np.mean(scores), -1.0, 1.0))
