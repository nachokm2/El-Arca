import json
from dataclasses import dataclass
from rich.console import Console
from ai.claude_client import ClaudeClient
from core.agent import ArcaAgent

console = Console()


@dataclass
class TurnoDebate:
    agente_id: int
    agente_nombre: str
    posicion: str
    argumento: str
    impacto_estimado: float


@dataclass
class ResultadoDebate:
    tema: str
    turnos: list[TurnoDebate]
    consenso: str
    ganador_id: int | None
    delta_interes_promedio: float


class DebateEngine:
    """
    Orquesta debates en lenguaje natural entre agentes usando Claude.
    Los argumentos generados retroalimentan el nivel de interés de cada agente.
    """

    def __init__(self):
        try:
            self.claude = ClaudeClient()
            self.disponible = True
        except ValueError:
            self.disponible = False
            console.print("[yellow]DebateEngine sin API key. Los debates no estarán disponibles.[/yellow]")

    def debatir(
        self,
        agentes: list[ArcaAgent],
        programa: dict,
        rondas: int = 2,
    ) -> ResultadoDebate | None:
        if not self.disponible:
            return None
        if len(agentes) < 2:
            return None

        tema = f"Programa: {programa.get('nombre', 'Diplomado')}"
        turnos: list[TurnoDebate] = []

        for ronda in range(rondas):
            for agente in agentes[:4]:  # máximo 4 agentes por debate
                turno = self._generar_turno(agente, programa, turnos)
                if turno:
                    turnos.append(turno)

        consenso = self._sintetizar_consenso(turnos, programa)
        delta_promedio = sum(t.impacto_estimado for t in turnos) / max(len(turnos), 1)

        ganador_id = None
        if turnos:
            ganador_id = max(turnos, key=lambda t: abs(t.impacto_estimado)).agente_id

        return ResultadoDebate(
            tema=tema,
            turnos=turnos,
            consenso=consenso,
            ganador_id=ganador_id,
            delta_interes_promedio=delta_promedio,
        )

    def _generar_turno(
        self,
        agente: ArcaAgent,
        programa: dict,
        turnos_previos: list[TurnoDebate],
    ) -> TurnoDebate | None:
        contexto_previo = ""
        if turnos_previos:
            ultimos = turnos_previos[-3:]
            contexto_previo = "\n".join(
                f"- {t.agente_nombre} ({t.posicion}): {t.argumento}" for t in ultimos
            )

        system = f"""Eres {agente.nombre}, una persona chilena de {agente.edad} años.
Trabajo: {agente.ocupacion}, {agente.situacion_laboral}
Ciudad: {agente.ciudad}
Educación: {agente.nivel_educativo}
Ingreso mensual: ${agente.economico.ingreso_mensual:,} CLP
Tu posición actual sobre el programa: {agente.estado.value} (interés: {agente.nivel_interes:.2f})

Habla en primera persona, en español chileno natural. Sé conciso (2-3 oraciones)."""

        prompt = f"""Se está debatiendo sobre el siguiente programa:
{json.dumps(programa, ensure_ascii=False, indent=2)}

{"Argumentos previos en este debate:" + contexto_previo if contexto_previo else "Eres el primero en hablar."}

Da tu opinión honesta sobre este programa desde tu perspectiva personal.
Responde en JSON: {{"posicion": "a_favor/en_contra/neutro", "argumento": "tu argumento", "impacto_en_tu_interes": float -1.0 a 1.0}}"""

        try:
            raw = self.claude.completar_json(system, prompt)
            data = json.loads(raw)
            return TurnoDebate(
                agente_id=agente.unique_id,
                agente_nombre=agente.nombre,
                posicion=data.get("posicion", "neutro"),
                argumento=data.get("argumento", ""),
                impacto_estimado=float(data.get("impacto_en_tu_interes", 0.0)),
            )
        except Exception as e:
            console.print(f"[red]Error en turno de {agente.nombre}: {e}[/red]")
            return None

    def _sintetizar_consenso(self, turnos: list[TurnoDebate], programa: dict) -> str:
        if not turnos or not self.disponible:
            return "Sin consenso disponible."

        resumen = "\n".join(f"- {t.agente_nombre}: {t.argumento}" for t in turnos)
        system = "Eres un analista de comportamiento del consumidor chileno. Sé conciso."
        prompt = f"""Debate sobre: {programa.get('nombre', 'el programa')}

Argumentos:
{resumen}

Resume en 2 oraciones el consenso o la tensión principal del debate."""

        try:
            return self.claude.completar(system, prompt, temperatura=0.3)
        except Exception:
            return "No se pudo generar síntesis del debate."

    def generar_opinion_individual(self, agente: ArcaAgent, programa: dict) -> str:
        if not self.disponible:
            return f"{agente.nombre} no pudo expresar su opinión (sin conexión a IA)."

        system = f"""Eres {agente.nombre}, {agente.edad} años, {agente.ocupacion} en {agente.ciudad}.
Responde en primera persona, en español chileno, en 2-3 oraciones naturales."""

        prompt = f"""Te preguntan qué opinas del siguiente programa académico:
{json.dumps(programa, ensure_ascii=False, indent=2)}

Tu estado actual: {agente.estado.value}, interés: {agente.nivel_interes:.2f}
Da tu opinión honesta y personal."""

        try:
            return self.claude.completar(system, prompt, temperatura=0.9)
        except Exception as e:
            return f"[Error generando opinión: {e}]"
