import uuid
import json
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

import config
from core.society import ArcaSociety
from core.agent import EstadoAgente
from ai.agent_factory import AgentFactory
from simulation.experiment import Experiment, ExperimentConfig

console = Console()


class SimulationRunner:
    def __init__(self):
        self.experimentos: dict[str, Experiment] = {}

    def ejecutar(
        self,
        exp_config: ExperimentConfig,
        callback_step=None,
    ) -> Experiment:
        errores = exp_config.validar()
        if errores:
            raise ValueError(f"Configuración inválida: {errores}")

        exp_id = str(uuid.uuid4())[:8]
        experimento = Experiment(config=exp_config, id=exp_id, estado="corriendo")
        self.experimentos[exp_id] = experimento

        console.print(f"\n[bold cyan]Iniciando experimento '{exp_config.nombre}' [{exp_id}][/bold cyan]")
        inicio = time.time()

        try:
            factory = AgentFactory(use_ai=exp_config.usar_ia)
            perfiles = factory.crear_sociedad(
                n=exp_config.n_agentes,
                model=None,
                arquetipos=exp_config.arquetipos or None,
                load_from=exp_config.cargar_agentes,
                save_as=exp_config.guardar_agentes_como,
            )

            # ArcaSociety crea los agentes Mesa internamente
            sociedad = ArcaSociety(
                perfiles=perfiles,
                programa=exp_config.programa,
                topologia_red=exp_config.topologia_red,
                seed=exp_config.seed,
            )

            snapshots = []
            metricas_red = sociedad.network.get_metricas()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("{task.completed}/{task.total} pasos"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Simulando...", total=exp_config.n_pasos)

                for step in range(exp_config.n_pasos):
                    sociedad.step()
                    snap = sociedad.get_snapshot()
                    snapshots.append(snap)

                    if callback_step:
                        callback_step(step, snap, sociedad)

                    progress.advance(task)

            duracion = time.time() - inicio
            df_modelo = sociedad.get_resultados_df()

            resultados = {
                "snapshots": snapshots,
                "metricas_red": metricas_red,
                "tasa_adopcion_final": snapshots[-1]["tasa_adopcion"] if snapshots else 0,
                "interes_medio_final": snapshots[-1]["interes_medio"] if snapshots else 0,
                "conteos_finales": snapshots[-1]["conteos"] if snapshots else {},
                "duracion_segundos": round(duracion, 2),
                "agentes": [a.to_dict() for a in sociedad.agentes],
                "serie_tiempo": df_modelo.to_dict(orient="list") if not df_modelo.empty else {},
            }

            experimento.resultados = resultados
            experimento.estado = "completado"
            experimento.metadata = {
                "inicio": datetime.now().isoformat(),
                "duracion_s": round(duracion, 2),
            }

            self._guardar_resultados(experimento)
            console.print(f"[green]Experimento completado en {duracion:.1f}s[/green]")
            console.print(f"  Tasa de adopción: {resultados['tasa_adopcion_final']:.1%}")

        except Exception as e:
            experimento.estado = "error"
            experimento.error_msg = str(e)
            console.print(f"[red]Error en simulación: {e}[/red]")
            raise

        return experimento

    def _guardar_resultados(self, experimento: Experiment):
        # Reemplaza espacios solo en el nombre del archivo, no en el path del directorio
        nombre_archivo = f"{experimento.id}_{experimento.config.nombre[:20]}.json".replace(" ", "_")
        path = config.SIMULATIONS_DIR / nombre_archivo
        with open(path, "w", encoding="utf-8") as f:
            json.dump(experimento.to_dict(), f, ensure_ascii=False, indent=2, default=str)
        console.print(f"  Resultados guardados en: {path.name}")

    def listar_experimentos(self) -> list[dict]:
        resultados = []
        for p in config.SIMULATIONS_DIR.glob("*.json"):
            try:
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
                resultados.append({
                    "id": data.get("id", ""),
                    "nombre": data.get("nombre", ""),
                    "estado": data.get("estado", ""),
                    "n_agentes": data.get("n_agentes", 0),
                    "tasa_adopcion": data.get("resultados", {}).get("tasa_adopcion_final", 0),
                    "archivo": p.name,
                })
            except Exception:
                continue
        return resultados

    def cargar_experimento(self, archivo: str) -> dict:
        path = config.SIMULATIONS_DIR / archivo
        with open(path, encoding="utf-8") as f:
            return json.load(f)
