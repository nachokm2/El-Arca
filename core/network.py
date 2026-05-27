import networkx as nx
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import ArcaAgent


class NetworkManager:
    """
    Gestiona la red social entre agentes usando NetworkX.
    Soporta topologías small-world, scale-free y aleatorias.
    """

    TOPOLOGIAS = ["small_world", "scale_free", "random", "comunidades"]

    def __init__(self, topologia: str = "small_world"):
        if topologia not in self.TOPOLOGIAS:
            raise ValueError(f"Topología '{topologia}' no soportada. Usa: {self.TOPOLOGIAS}")
        self.topologia = topologia
        self.grafo: nx.Graph = nx.Graph()

    def construir_red(self, agentes: list["ArcaAgent"], seed: int = 42) -> nx.Graph:
        n = len(agentes)
        if n < 2:
            return self.grafo

        ids = [a.unique_id for a in agentes]

        if self.topologia == "small_world":
            k = min(6, n - 1)
            base = nx.watts_strogatz_graph(n, k, p=0.15, seed=seed)
        elif self.topologia == "scale_free":
            base = nx.barabasi_albert_graph(n, m=3, seed=seed)
        elif self.topologia == "random":
            base = nx.erdos_renyi_graph(n, p=0.08, seed=seed)
        elif self.topologia == "comunidades":
            base = self._grafo_comunidades(n, agentes, seed)
        else:
            base = nx.watts_strogatz_graph(n, 4, 0.1, seed=seed)

        mapping = {i: ids[i] for i in range(n)}
        self.grafo = nx.relabel_nodes(base, mapping)

        for agente in agentes:
            self.grafo.nodes[agente.unique_id]["estado"] = agente.estado.value
            self.grafo.nodes[agente.unique_id]["nombre"] = agente.nombre
            self.grafo.nodes[agente.unique_id]["nivel_interes"] = agente.nivel_interes

        return self.grafo

    def _grafo_comunidades(self, n: int, agentes: list["ArcaAgent"], seed: int) -> nx.Graph:
        rng = np.random.default_rng(seed)
        # Agrupar por ciudad/nivel educativo como comunidades
        comunidades: dict[str, list[int]] = {}
        for i, a in enumerate(agentes):
            key = f"{a.ciudad}_{a.nivel_educativo}"
            comunidades.setdefault(key, []).append(i)

        G = nx.Graph()
        G.add_nodes_from(range(n))

        for miembros in comunidades.values():
            for i in range(len(miembros)):
                for j in range(i + 1, len(miembros)):
                    if rng.random() < 0.4:
                        G.add_edge(miembros[i], miembros[j])

        # Conexiones entre comunidades
        com_list = list(comunidades.values())
        for c1 in com_list:
            for c2 in com_list:
                if c1 is c2:
                    continue
                if rng.random() < 0.05 and c1 and c2:
                    G.add_edge(rng.choice(c1), rng.choice(c2))

        return G

    def get_vecinos(self, agent_id: int) -> list[int]:
        if agent_id not in self.grafo:
            return []
        return list(self.grafo.neighbors(agent_id))

    def actualizar_estado(self, agent_id: int, estado: str, nivel_interes: float):
        if agent_id in self.grafo:
            self.grafo.nodes[agent_id]["estado"] = estado
            self.grafo.nodes[agent_id]["nivel_interes"] = nivel_interes

    def get_metricas(self) -> dict:
        if self.grafo.number_of_nodes() == 0:
            return {}
        return {
            "nodos": self.grafo.number_of_nodes(),
            "aristas": self.grafo.number_of_edges(),
            "densidad": round(nx.density(self.grafo), 4),
            "grado_promedio": round(
                sum(d for _, d in self.grafo.degree()) / self.grafo.number_of_nodes(), 2
            ),
            "componentes_conexas": nx.number_connected_components(self.grafo),
            "coeficiente_clustering": round(nx.average_clustering(self.grafo), 4),
        }

    def to_agraph_data(self, agentes_dict: dict) -> tuple[list, list]:
        """Retorna (nodes, edges) para streamlit-agraph."""
        nodes = []
        edges = []

        COLOR_MAP = {
            "neutral": "#94a3b8",
            "interesado": "#3b82f6",
            "esceptico": "#f97316",
            "adoptado": "#22c55e",
            "rechazado": "#ef4444",
        }

        for node_id in self.grafo.nodes():
            agente = agentes_dict.get(node_id)
            estado = self.grafo.nodes[node_id].get("estado", "neutral")
            color = COLOR_MAP.get(estado, "#94a3b8")
            label = self.grafo.nodes[node_id].get("nombre", str(node_id))
            nodes.append({
                "id": str(node_id),
                "label": label,
                "color": color,
                "size": 15,
                "title": f"{label} | {estado}",
            })

        for u, v in self.grafo.edges():
            edges.append({"from": str(u), "to": str(v)})

        return nodes, edges
