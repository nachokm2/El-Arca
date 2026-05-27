import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from core.agent import ArcaAgent, EstadoAgente, PerfilEconomico, PerfilPsicologico


class _StubModel:
    """Stub mínimo compatible con Mesa 3.x Agent.__init__."""

    def __init__(self):
        self.agent_id_counter = 1

    def register_agent(self, agent) -> None:
        # Mesa 3.x register_agent sets unique_id
        agent.unique_id = self.agent_id_counter
        self.agent_id_counter += 1

    @property
    def steps(self) -> int:
        return 0


def make_agent(ingreso=1_000_000, disposicion=0.2, sensibilidad=0.5):
    eco = PerfilEconomico(
        ingreso_mensual=ingreso,
        disposicion_pago=disposicion,
        sensibilidad_precio=sensibilidad,
        deuda_actual=0.2,
    )
    psi = PerfilPsicologico(
        apertura_cambio=0.6,
        aversion_riesgo=0.4,
        influenciabilidad=0.5,
        orientacion_logro=0.7,
        pragmatismo=0.6,
    )
    return ArcaAgent(
        model=_StubModel(),
        nombre="Test Agente",
        edad=35,
        genero="masculino",
        ciudad="Santiago",
        nivel_educativo="universitario",
        situacion_laboral="empleado",
        perfil_economico=eco,
        perfil_psicologico=psi,
    )


def test_agent_creation():
    agente = make_agent()
    assert agente.unique_id >= 0
    assert agente.estado == EstadoAgente.NEUTRAL
    assert agente.nivel_interes == 0.0
    assert agente.ciudad == "Santiago"


def test_capacidad_pago():
    # 1M CLP * 0.2 disposición * 12 meses = 2.4M
    agente = make_agent(ingreso=1_000_000, disposicion=0.2)
    assert agente.capacidad_pago_max == 2_400_000


def test_estado_adopcion():
    agente = make_agent()
    agente.nivel_interes = 0.8
    agente.actualizar_estado()
    assert agente.estado == EstadoAgente.ADOPTADO


def test_estado_rechazo():
    agente = make_agent()
    agente.nivel_interes = -0.5
    agente.actualizar_estado()
    assert agente.estado == EstadoAgente.RECHAZADO


def test_estado_interesado():
    agente = make_agent()
    agente.nivel_interes = 0.5
    agente.actualizar_estado()
    assert agente.estado == EstadoAgente.INTERESADO


def test_estado_esceptico():
    agente = make_agent()
    agente.nivel_interes = -0.2
    agente.actualizar_estado()
    assert agente.estado == EstadoAgente.ESCEPTICO


def test_adoptado_no_cambia():
    agente = make_agent()
    agente.nivel_interes = 0.9
    agente.actualizar_estado()
    assert agente.estado == EstadoAgente.ADOPTADO
    agente.nivel_interes = -0.9
    agente.actualizar_estado()
    assert agente.estado == EstadoAgente.ADOPTADO


def test_to_dict():
    agente = make_agent()
    d = agente.to_dict()
    assert "id" in d
    assert "nombre" in d
    assert "estado" in d
    assert d["estado"] == "neutral"


def test_registrar_interaccion():
    agente = make_agent()
    agente.registrar_interaccion("exposicion", 0.1, "test")
    assert len(agente.historial_interacciones) == 1
    assert agente.historial_interacciones[0]["tipo"] == "exposicion"
