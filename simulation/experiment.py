from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExperimentConfig:
    nombre: str
    descripcion: str
    n_agentes: int = 50
    n_pasos: int = 20
    topologia_red: str = "small_world"
    programa: dict = field(default_factory=dict)
    seed: int = 42
    usar_ia: bool = False
    arquetipos: list[dict] = field(default_factory=list)
    variantes_programa: list[dict] = field(default_factory=list)

    def validar(self) -> list[str]:
        errores = []
        if self.n_agentes < 5:
            errores.append("Se necesitan al menos 5 agentes.")
        if self.n_agentes > 500:
            errores.append("Máximo 500 agentes por simulación.")
        if self.n_pasos < 1:
            errores.append("Se necesita al menos 1 paso de simulación.")
        if not self.programa:
            errores.append("Debes definir un programa a evaluar.")
        if self.topologia_red not in ["small_world", "scale_free", "random", "comunidades"]:
            errores.append(f"Topología '{self.topologia_red}' no válida.")
        return errores


@dataclass
class Experiment:
    config: ExperimentConfig
    id: str = ""
    estado: str = "pendiente"  # pendiente | corriendo | completado | error
    resultados: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    error_msg: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.config.nombre,
            "descripcion": self.config.descripcion,
            "n_agentes": self.config.n_agentes,
            "n_pasos": self.config.n_pasos,
            "topologia_red": self.config.topologia_red,
            "programa": self.config.programa,
            "seed": self.config.seed,
            "estado": self.estado,
            "resultados": self.resultados,
            "error_msg": self.error_msg,
        }
