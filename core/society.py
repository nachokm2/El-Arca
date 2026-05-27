import mesa
import numpy as np
from mesa.datacollection import DataCollector
from .agent import ArcaAgent, EstadoAgente
from .persuasion import PersuasionEngine
from .network import NetworkManager


def _count_estado(estado: EstadoAgente):
    def counter(model: "ArcaSociety") -> int:
        return sum(1 for a in model.agents if a.estado == estado)
    counter.__name__ = f"count_{estado.value}"
    return counter


class ArcaSociety(mesa.Model):
    def __init__(
        self,
        perfiles: list[dict],   # lista de dicts con kwargs para ArcaAgent (sin 'model')
        programa: dict,
        topologia_red: str = "small_world",
        seed: int = 42,
    ):
        super().__init__(seed=seed)  # Mesa 3.x: seed configura self.random
        self.programa = programa
        np.random.seed(seed)

        self.persuasion = PersuasionEngine()
        self.network = NetworkManager(topologia=topologia_red)

        # Mesa 3.x: al crear ArcaAgent(model=self, ...) se auto-registra en self.agents
        for perfil in perfiles:
            ArcaAgent(model=self, **perfil)

        self._agentes_dict: dict[int, ArcaAgent] = {a.unique_id: a for a in self.agents}
        self.network.construir_red(list(self.agents), seed=seed)

        self.datacollector = DataCollector(
            model_reporters={
                "Neutral": _count_estado(EstadoAgente.NEUTRAL),
                "Interesado": _count_estado(EstadoAgente.INTERESADO),
                "Esceptico": _count_estado(EstadoAgente.ESCEPTICO),
                "Adoptado": _count_estado(EstadoAgente.ADOPTADO),
                "Rechazado": _count_estado(EstadoAgente.RECHAZADO),
                "InteresMedio": lambda m: float(
                    np.mean([a.nivel_interes for a in m.agents])
                ),
                "TasaAdopcion": lambda m: sum(
                    1 for a in m.agents if a.estado == EstadoAgente.ADOPTADO
                ) / max(len(list(m.agents)), 1),
            },
            agent_reporters={
                "estado": lambda a: a.estado.value,
                "nivel_interes": "nivel_interes",
                "ciudad": "ciudad",
                "nivel_educativo": "nivel_educativo",
            },
        )

    @property
    def agentes(self) -> list[ArcaAgent]:
        return list(self.agents)

    def step(self):
        self.datacollector.collect(self)
        self._procesar_exposicion_inicial()
        self._procesar_difusion_social()
        self.steps += 1  # Mesa 3.x: incremento manual al llamar step() directamente

    def _procesar_exposicion_inicial(self):
        for agente in self.agents:
            if agente.estado in (EstadoAgente.ADOPTADO, EstadoAgente.RECHAZADO):
                continue
            delta = self.persuasion.calcular_impacto(agente, self.programa, presion_social=0.0)
            tasa = 0.15
            agente.nivel_interes = float(
                np.clip(agente.nivel_interes + delta * tasa, -1.0, 1.0)
            )
            agente.registrar_interaccion("exposicion_programa", delta * tasa)

    def _procesar_difusion_social(self):
        for agente in self.agents:
            if agente.estado in (EstadoAgente.ADOPTADO, EstadoAgente.RECHAZADO):
                continue
            vecino_ids = self.network.get_vecinos(agente.unique_id)
            vecinos = [self._agentes_dict[vid] for vid in vecino_ids if vid in self._agentes_dict]
            if not vecinos:
                continue

            presion = self.persuasion.calcular_presion_social(vecinos)
            delta = self.persuasion.calcular_impacto(agente, self.programa, presion_social=presion)
            tasa = 0.10
            agente.nivel_interes = float(
                np.clip(agente.nivel_interes + delta * tasa, -1.0, 1.0)
            )
            agente.influencias_recibidas.append(presion)
            agente.registrar_interaccion("influencia_social", delta * tasa, "red")
            self.network.actualizar_estado(agente.unique_id, agente.estado.value, agente.nivel_interes)

        for agente in self.agents:
            agente.actualizar_estado()

    def get_snapshot(self) -> dict:
        conteos = {e.value: 0 for e in EstadoAgente}
        for a in self.agents:
            conteos[a.estado.value] += 1
        total = len(list(self.agents))
        return {
            "step": self.steps,
            "total_agentes": total,
            "conteos": conteos,
            "tasa_adopcion": conteos["adoptado"] / max(total, 1),
            "interes_medio": float(np.mean([a.nivel_interes for a in self.agents])),
        }

    def get_resultados_df(self):
        return self.datacollector.get_model_vars_dataframe()

    def get_agentes_df(self):
        return self.datacollector.get_agent_vars_dataframe()
