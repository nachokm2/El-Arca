import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
from core.agent import ArcaAgent, PerfilEconomico, PerfilPsicologico
from core.persuasion import PersuasionEngine


PROGRAMA_BASE = {
    "precio_clp": 1_200_000,
    "tiene_financiamiento": True,
    "factor_novedad": 0.6,
    "incertidumbre_percibida": 0.25,
    "retorno_profesional": 0.8,
    "roi_percibido": 0.75,
    "reputacion_institucion": 0.72,
    "relevancia_mercado": 0.85,
    "modalidad_adecuada": 0.80,
}


class _StubModel:
    def __init__(self):
        self.agent_id_counter = 1
    def register_agent(self, agent):
        agent.unique_id = self.agent_id_counter
        self.agent_id_counter += 1
    @property
    def steps(self): return 0


def make_agente(ingreso=1_500_000, disposicion=0.25, aversion=0.3, apertura=0.7, logro=0.8):
    eco = PerfilEconomico(
        ingreso_mensual=ingreso,
        disposicion_pago=disposicion,
        sensibilidad_precio=1 - (ingreso - 400_000) / 2_600_000,
        deuda_actual=0.2,
    )
    psi = PerfilPsicologico(
        apertura_cambio=apertura,
        aversion_riesgo=aversion,
        influenciabilidad=0.5,
        orientacion_logro=logro,
        pragmatismo=0.65,
    )
    return ArcaAgent(
        model=_StubModel(),
        nombre="Test",
        edad=35,
        genero="masculino",
        ciudad="Santiago",
        nivel_educativo="universitario",
        situacion_laboral="empleado",
        perfil_economico=eco,
        perfil_psicologico=psi,
    )


def test_impacto_en_rango():
    engine = PersuasionEngine()
    agente = make_agente()
    np.random.seed(42)
    delta = engine.calcular_impacto(agente, PROGRAMA_BASE)
    assert -1.0 <= delta <= 1.0


def test_agente_rico_menos_sensible():
    engine = PersuasionEngine()
    agente_rico = make_agente(ingreso=2_500_000, disposicion=0.3)
    agente_pobre = make_agente(ingreso=500_000, disposicion=0.15)
    np.random.seed(0)
    delta_rico = engine.calcular_impacto(agente_rico, PROGRAMA_BASE)
    np.random.seed(0)
    delta_pobre = engine.calcular_impacto(agente_pobre, PROGRAMA_BASE)
    assert delta_rico > delta_pobre


def test_presion_social_positiva_suma():
    engine = PersuasionEngine()
    agente = make_agente()
    np.random.seed(42)
    delta_sin_social = engine.calcular_impacto(agente, PROGRAMA_BASE, presion_social=0.0)
    np.random.seed(42)
    delta_con_social = engine.calcular_impacto(agente, PROGRAMA_BASE, presion_social=0.8)
    assert delta_con_social >= delta_sin_social - 0.1


def test_presion_social_vecinos():
    engine = PersuasionEngine()
    vecinos = [make_agente() for _ in range(3)]
    for v in vecinos:
        v.nivel_interes = 0.7
    presion = engine.calcular_presion_social(vecinos)
    assert presion > 0


def test_programa_caro_sin_financiamiento():
    engine = PersuasionEngine()
    programa_caro = PROGRAMA_BASE.copy()
    programa_caro["precio_clp"] = 5_000_000
    programa_caro["tiene_financiamiento"] = False
    agente = make_agente(ingreso=600_000)
    np.random.seed(1)
    delta = engine.calcular_impacto(agente, programa_caro)
    assert delta < 0


def test_pesos_suman_uno():
    engine = PersuasionEngine()
    total = engine.w_eco + engine.w_psi + engine.w_soc + engine.w_prog
    assert abs(total - 1.0) < 1e-6
