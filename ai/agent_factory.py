import json
import random
import numpy as np
from rich.console import Console
from core.agent import PerfilEconomico, PerfilPsicologico
from ai.claude_client import ClaudeClient

console = Console()

NOMBRES_MASCULINOS = [
    "Matías", "Sebastián", "Nicolás", "Diego", "Felipe", "Rodrigo", "Andrés", "Carlos",
    "José", "Manuel", "Tomás", "Pablo", "Ignacio", "Cristóbal", "Gonzalo", "Alejandro",
]
NOMBRES_FEMENINOS = [
    "Valentina", "Sofía", "Camila", "Isabella", "Catalina", "Javiera", "Francisca", "Daniela",
    "Constanza", "Fernanda", "Carla", "Claudia", "Paula", "Andrea", "Lorena", "Patricia",
]
APELLIDOS = [
    "González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", "Contreras", "Silva",
    "Martínez", "Sepúlveda", "Morales", "Torres", "Flores", "Miranda", "Castillo", "Fuentes",
]
CIUDADES = ["Santiago", "Valparaíso", "Concepción", "La Serena", "Antofagasta", "Temuco", "Iquique", "Rancagua"]
OCUPACIONES = {
    "universitario": ["Ingeniero Civil", "Administrador de Empresas", "Contador", "Periodista",
                      "Psicólogo", "Médico", "Abogado", "Profesor"],
    "tecnico": ["Técnico en Informática", "Técnico Contable", "Técnico en Administración", "Técnico en Enfermería"],
    "postgrado": ["Director de Proyectos", "Gerente de Área", "Jefe de Unidad", "Consultor", "Investigador"],
}
AREAS = ["Tecnología", "Salud", "Educación", "Finanzas", "Marketing", "Recursos Humanos", "Operaciones", "Legal"]


class AgentFactory:
    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai
        self.claude = None
        if use_ai:
            try:
                self.claude = ClaudeClient()
            except ValueError:
                console.print("[yellow]API key no disponible. Generando agentes sin IA.[/yellow]")
                self.use_ai = False

    def crear_sociedad(self, n: int, model=None, arquetipos: list[dict] | None = None) -> list[dict]:
        """
        Retorna lista de dicts (perfiles) que ArcaSociety usará para crear agentes Mesa.
        El parámetro `model` se ignora (compatibilidad hacia atrás).
        """
        rng = np.random.default_rng(42)
        perfiles = []
        for _ in range(n):
            perfil_base = random.choice(arquetipos) if arquetipos else None
            if self.use_ai and self.claude and perfil_base:
                try:
                    perfiles.append(self._crear_perfil_con_ia(perfil_base))
                    continue
                except Exception as e:
                    console.print(f"[yellow]Fallo IA: {e}. Usando generación local.[/yellow]")
            perfiles.append(self._crear_perfil_aleatorio(perfil_base, rng))

        console.print(f"[green]Perfiles generados: {n} agentes[/green]")
        return perfiles

    def _crear_perfil_aleatorio(self, perfil_base: dict | None, rng) -> dict:
        """Genera un dict con todos los kwargs para ArcaAgent (excepto model)."""
        genero = str(rng.choice(["masculino", "femenino"]))
        if genero == "masculino":
            nombre = str(rng.choice(NOMBRES_MASCULINOS)) + " " + str(rng.choice(APELLIDOS))
        else:
            nombre = str(rng.choice(NOMBRES_FEMENINOS)) + " " + str(rng.choice(APELLIDOS))

        if perfil_base:
            nivel_edu = perfil_base.get("nivel_educativo", str(rng.choice(["tecnico", "universitario", "postgrado"])))
            ciudad = perfil_base.get("ciudad", str(rng.choice(CIUDADES)))
            sit_laboral = perfil_base.get("situacion_laboral", str(rng.choice(["empleado", "independiente"])))
            ingreso_base = perfil_base.get("ingreso_mensual_promedio", 1_000_000)
            ingreso = int(np.clip(rng.normal(ingreso_base, ingreso_base * 0.2), 400_000, 3_000_000))
            apertura = float(np.clip(rng.normal(perfil_base.get("apertura_cambio_media", 0.5), 0.15), 0, 1))
            aversion = float(np.clip(rng.normal(perfil_base.get("aversion_riesgo_media", 0.4), 0.15), 0, 1))
            logro = float(np.clip(rng.normal(perfil_base.get("orientacion_logro_media", 0.6), 0.15), 0, 1))
        else:
            nivel_edu = str(rng.choice(["tecnico", "universitario", "postgrado"], p=[0.3, 0.5, 0.2]))
            ciudad = str(rng.choice(CIUDADES, p=[0.45, 0.15, 0.12, 0.07, 0.07, 0.07, 0.04, 0.03]))
            sit_laboral = str(rng.choice(["empleado", "independiente", "desempleado"], p=[0.65, 0.25, 0.10]))
            rangos = {"tecnico": (400_000, 900_000), "universitario": (700_000, 1_800_000), "postgrado": (1_200_000, 3_000_000)}
            lo, hi = rangos[nivel_edu]
            ingreso = int(rng.uniform(lo, hi))
            apertura = float(rng.beta(5, 3))
            aversion = float(rng.beta(3, 4))
            logro = float(rng.beta(4, 3))

        ocupaciones_nivel = OCUPACIONES.get(nivel_edu, OCUPACIONES["universitario"])
        ocupacion = str(rng.choice(ocupaciones_nivel))
        area = str(rng.choice(AREAS))

        return {
            "nombre": nombre,
            "edad": int(rng.integers(25, 56)),
            "genero": genero,
            "ciudad": ciudad,
            "nivel_educativo": nivel_edu,
            "situacion_laboral": sit_laboral,
            "ocupacion": ocupacion,
            "area_profesional": area,
            "activo_en_redes": bool(rng.random() > 0.3),
            "perfil_economico": PerfilEconomico(
                ingreso_mensual=ingreso,
                disposicion_pago=float(np.clip(rng.beta(2, 5), 0.05, 0.4)),
                sensibilidad_precio=float(1.0 - (ingreso - 400_000) / 2_600_000),
                deuda_actual=float(rng.beta(2, 5)),
            ),
            "perfil_psicologico": PerfilPsicologico(
                apertura_cambio=apertura,
                aversion_riesgo=aversion,
                influenciabilidad=float(rng.beta(3, 4)),
                orientacion_logro=logro,
                pragmatismo=float(rng.beta(4, 3)),
            ),
        }

    def _crear_perfil_con_ia(self, perfil_base: dict) -> dict:
        system = (
            "Eres un generador de perfiles de personas chilenas realistas para una simulación social. "
            "Genera datos coherentes con el contexto socioeconómico chileno."
        )
        prompt = f"""Genera un perfil para una persona chilena con estas características base:
{json.dumps(perfil_base, ensure_ascii=False, indent=2)}

Responde con JSON con exactamente estos campos:
{{
  "nombre": "nombre apellido (chileno)",
  "edad": número entre 25 y 55,
  "genero": "masculino" o "femenino",
  "ciudad": ciudad chilena,
  "nivel_educativo": "tecnico", "universitario" o "postgrado",
  "situacion_laboral": "empleado", "independiente" o "desempleado",
  "ocupacion": "cargo específico",
  "area_profesional": "área de trabajo",
  "ingreso_mensual": número CLP entre 400000 y 3000000,
  "disposicion_pago": float 0.05-0.4,
  "sensibilidad_precio": float 0.0-1.0,
  "apertura_cambio": float 0.0-1.0,
  "aversion_riesgo": float 0.0-1.0,
  "influenciabilidad": float 0.0-1.0,
  "orientacion_logro": float 0.0-1.0,
  "pragmatismo": float 0.0-1.0,
  "activo_en_redes": true o false
}}"""
        raw = self.claude.completar_json(system, prompt)
        data = json.loads(raw)

        return {
            "nombre": data["nombre"],
            "edad": int(data["edad"]),
            "genero": data["genero"],
            "ciudad": data["ciudad"],
            "nivel_educativo": data["nivel_educativo"],
            "situacion_laboral": data["situacion_laboral"],
            "ocupacion": data.get("ocupacion", ""),
            "area_profesional": data.get("area_profesional", ""),
            "activo_en_redes": bool(data.get("activo_en_redes", True)),
            "perfil_economico": PerfilEconomico(
                ingreso_mensual=int(data["ingreso_mensual"]),
                disposicion_pago=float(data["disposicion_pago"]),
                sensibilidad_precio=float(data["sensibilidad_precio"]),
                deuda_actual=0.3,
            ),
            "perfil_psicologico": PerfilPsicologico(
                apertura_cambio=float(data["apertura_cambio"]),
                aversion_riesgo=float(data["aversion_riesgo"]),
                influenciabilidad=float(data["influenciabilidad"]),
                orientacion_logro=float(data["orientacion_logro"]),
                pragmatismo=float(data["pragmatismo"]),
            ),
        }
