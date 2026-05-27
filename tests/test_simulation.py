import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from ai.agent_factory import AgentFactory
from core.society import ArcaSociety
from core.agent import EstadoAgente
from simulation.runner import SimulationRunner
from simulation.experiment import ExperimentConfig
from simulation.analyzer import ResultsAnalyzer


PROGRAMA_TEST = {
    "nombre": "Diplomado Test",
    "precio_clp": 1_200_000,
    "tiene_financiamiento": True,
    "reputacion_institucion": 0.72,
    "relevancia_mercado": 0.85,
    "modalidad_adecuada": 0.80,
    "factor_novedad": 0.6,
    "incertidumbre_percibida": 0.25,
    "retorno_profesional": 0.80,
    "roi_percibido": 0.75,
}


def test_factory_genera_perfiles():
    factory = AgentFactory(use_ai=False)
    perfiles = factory.crear_sociedad(n=10)
    assert len(perfiles) == 10
    for p in perfiles:
        assert isinstance(p, dict)
        assert "nombre" in p
        assert 25 <= p["edad"] <= 55
        assert p["nivel_educativo"] in ["tecnico", "universitario", "postgrado"]


def test_society_crea_agentes_desde_perfiles():
    factory = AgentFactory(use_ai=False)
    perfiles = factory.crear_sociedad(n=15)
    sociedad = ArcaSociety(perfiles, PROGRAMA_TEST, topologia_red="small_world", seed=42)
    assert len(sociedad.agentes) == 15
    assert sociedad.network.grafo.number_of_nodes() == 15


def test_agentes_tienen_ids_unicos():
    factory = AgentFactory(use_ai=False)
    perfiles = factory.crear_sociedad(n=20)
    sociedad = ArcaSociety(perfiles, PROGRAMA_TEST, seed=42)
    ids = [a.unique_id for a in sociedad.agentes]
    assert len(ids) == len(set(ids))


def test_society_step():
    factory = AgentFactory(use_ai=False)
    perfiles = factory.crear_sociedad(n=20)
    sociedad = ArcaSociety(perfiles, PROGRAMA_TEST, seed=42)

    snap_antes = sociedad.get_snapshot()
    sociedad.step()
    snap_despues = sociedad.get_snapshot()

    assert snap_despues["step"] > snap_antes["step"]


def test_simulation_runner():
    cfg = ExperimentConfig(
        nombre="Test Run",
        descripcion="Test básico",
        n_agentes=15,
        n_pasos=5,
        programa=PROGRAMA_TEST,
        seed=42,
        usar_ia=False,
    )
    runner = SimulationRunner()
    experimento = runner.ejecutar(cfg)

    assert experimento.estado == "completado"
    assert len(experimento.resultados["snapshots"]) == 5
    assert 0 <= experimento.resultados["tasa_adopcion_final"] <= 1


def test_analyzer_resumen():
    cfg = ExperimentConfig(
        nombre="Test Analyzer",
        descripcion="Test análisis",
        n_agentes=20,
        n_pasos=8,
        programa=PROGRAMA_TEST,
        seed=99,
        usar_ia=False,
    )
    runner = SimulationRunner()
    exp = runner.ejecutar(cfg)

    analyzer = ResultsAnalyzer(exp.to_dict())
    resumen = analyzer.resumen_ejecutivo()

    assert "tasa_adopcion_final" in resumen
    assert 0 <= resumen["tasa_adopcion_final"] <= 1


def test_curva_difusion():
    cfg = ExperimentConfig(
        nombre="Test Curva",
        descripcion="Test curva difusión",
        n_agentes=15,
        n_pasos=6,
        programa=PROGRAMA_TEST,
        seed=7,
        usar_ia=False,
    )
    runner = SimulationRunner()
    exp = runner.ejecutar(cfg)
    analyzer = ResultsAnalyzer(exp.to_dict())
    curva = analyzer.curva_difusion()

    assert len(curva["pasos"]) == 6
    assert len(curva["adoptados"]) == 6


def test_topologias():
    factory = AgentFactory(use_ai=False)
    for topo in ["small_world", "scale_free", "random", "comunidades"]:
        perfiles = factory.crear_sociedad(n=20)
        sociedad = ArcaSociety(perfiles, PROGRAMA_TEST, topologia_red=topo, seed=1)
        assert sociedad.network.grafo.number_of_nodes() == 20
