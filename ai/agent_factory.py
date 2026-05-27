import json
import random
import dataclasses
from datetime import datetime
import numpy as np
from rich.console import Console
from core.agent import PerfilEconomico, PerfilPsicologico, PerfilContextual
from ai.claude_client import ClaudeClient
import config

console = Console()

SAVED_DIR = config.PROFILES_DIR / "saved"


def _serializar_perfil(perfil: dict) -> dict:
    result = {}
    for k, v in perfil.items():
        result[k] = dataclasses.asdict(v) if dataclasses.is_dataclass(v) else v
    return result


def _deserializar_perfil(d: dict) -> dict:
    result = dict(d)
    if isinstance(result.get("perfil_economico"), dict):
        eco = result["perfil_economico"]
        result["perfil_economico"] = PerfilEconomico(
            ingreso_mensual=eco["ingreso_mensual"],
            disposicion_pago=eco["disposicion_pago"],
            sensibilidad_precio=eco["sensibilidad_precio"],
            deuda_actual=eco.get("deuda_actual", 0.3),
            ahorro_disponible_meses=eco.get("ahorro_disponible_meses", 2.0),
            beneficios_empresa=eco.get("beneficios_empresa", False),
        )
    if isinstance(result.get("perfil_psicologico"), dict):
        psi = result["perfil_psicologico"]
        result["perfil_psicologico"] = PerfilPsicologico(
            apertura_cambio=psi["apertura_cambio"],
            aversion_riesgo=psi["aversion_riesgo"],
            influenciabilidad=psi["influenciabilidad"],
            orientacion_logro=psi["orientacion_logro"],
            pragmatismo=psi["pragmatismo"],
            autoeficacia_academica=psi.get("autoeficacia_academica", 0.60),
            necesidad_reconocimiento=psi.get("necesidad_reconocimiento", 0.50),
            satisfaccion_laboral=psi.get("satisfaccion_laboral", 0.55),
            ansiedad_academica=psi.get("ansiedad_academica", 0.30),
        )
    if isinstance(result.get("perfil_contextual"), dict):
        ctx = result["perfil_contextual"]
        result["perfil_contextual"] = PerfilContextual(
            modalidad_preferida=ctx.get("modalidad_preferida", "indiferente"),
            horas_disponibles_semana=ctx.get("horas_disponibles_semana", 10),
            anios_desde_ultimo_estudio=ctx.get("anios_desde_ultimo_estudio", 7),
            red_apoyo_social=ctx.get("red_apoyo_social", 0.60),
            pares_con_estudios_extra=ctx.get("pares_con_estudios_extra", 0.40),
            exposicion_campo=ctx.get("exposicion_campo", 0.50),
        )
    elif "perfil_contextual" not in result:
        result["perfil_contextual"] = PerfilContextual()
    return result

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
CIUDADES = [
    "Santiago", "Valparaíso", "Concepción", "La Serena", "Antofagasta",
    "Temuco", "Iquique", "Rancagua", "Talca", "Puerto Montt",
]

# Factor de ingreso por ciudad respecto a Santiago (=1.0)
# Fuente: Censo 2024 escolaridad promedio por región como proxy de nivel salarial
# RM: 12.7 años | Antofagasta: 12.5 | Valparaíso: 12.2 | Biobío: 12.0
# Araucanía: 11.5 | Maule: 11.3 | Los Lagos: 11.4 | Ñuble: 11.0
FACTOR_INGRESO_CIUDAD: dict[str, float] = {
    "Santiago":    1.00,
    "Antofagasta": 0.97,
    "Iquique":     0.93,
    "Valparaíso":  0.88,
    "Concepción":  0.85,
    "La Serena":   0.83,
    "Rancagua":    0.81,
    "Puerto Montt":0.80,
    "Temuco":      0.78,
    "Talca":       0.76,
}
OCUPACIONES = {
    "universitario": ["Ingeniero Civil", "Administrador de Empresas", "Contador", "Periodista",
                      "Psicólogo", "Médico", "Abogado", "Profesor"],
    "tecnico": ["Técnico en Informática", "Técnico Contable", "Técnico en Administración", "Técnico en Enfermería"],
    "postgrado": ["Director de Proyectos", "Gerente de Área", "Jefe de Unidad", "Consultor", "Investigador"],
    "media": ["Vendedor/a", "Operario/a", "Auxiliar de Servicios", "Conductor/a", "Cajero/a",
              "Empleado/a de Hogar", "Guardia de Seguridad", "Comerciante Informal"],
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

    # ── guardado / carga ─────────────────────────────────────────────────────

    @classmethod
    def listar_guardados(cls) -> list[dict]:
        SAVED_DIR.mkdir(exist_ok=True)
        result = []
        for p in SAVED_DIR.glob("*.json"):
            try:
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
                result.append({
                    "nombre": p.stem,
                    "n_agentes": data.get("n_agentes", 0),
                    "fecha": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                })
            except Exception:
                continue
        return sorted(result, key=lambda x: x["fecha"], reverse=True)

    def guardar_perfiles(self, perfiles: list[dict], nombre: str):
        SAVED_DIR.mkdir(exist_ok=True)
        path = SAVED_DIR / f"{nombre}.json"
        payload = {
            "nombre": nombre,
            "n_agentes": len(perfiles),
            "perfiles": [_serializar_perfil(p) for p in perfiles],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        console.print(f"[green]Agentes guardados como '{nombre}' ({len(perfiles)} perfiles)[/green]")

    def cargar_perfiles(self, nombre: str) -> list[dict] | None:
        path = SAVED_DIR / f"{nombre}.json"
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return [_deserializar_perfil(p) for p in data.get("perfiles", [])]

    # ── generación ───────────────────────────────────────────────────────────

    def crear_sociedad(self, n: int, model=None, arquetipos: list[dict] | None = None,
                       load_from: str | None = None, save_as: str | None = None) -> list[dict]:
        """
        Retorna lista de dicts (perfiles) que ArcaSociety usará para crear agentes Mesa.
        Si load_from está definido, carga perfiles guardados en lugar de generar.
        Si save_as está definido, guarda los perfiles generados con ese nombre.
        """
        if load_from:
            loaded = self.cargar_perfiles(load_from)
            if loaded:
                console.print(f"[blue]Cargados {len(loaded)} agentes de '{load_from}'[/blue]")
                return loaded[:n]
            console.print(f"[yellow]Set '{load_from}' no encontrado. Generando nuevos.[/yellow]")

        rng = np.random.default_rng(42)
        perfiles = []
        for _ in range(n):
            if arquetipos:
                pesos = [a.get("peso_poblacional", 1.0) for a in arquetipos]
                perfil_base = random.choices(arquetipos, weights=pesos, k=1)[0]
            else:
                perfil_base = None
            if self.use_ai and self.claude and perfil_base:
                try:
                    perfiles.append(self._crear_perfil_con_ia(perfil_base))
                    continue
                except Exception as e:
                    console.print(f"[yellow]Fallo IA: {e}. Usando generación local.[/yellow]")
            perfiles.append(self._crear_perfil_aleatorio(perfil_base, rng))

        console.print(f"[green]Perfiles generados: {n} agentes[/green]")

        if save_as:
            self.guardar_perfiles(perfiles, save_as)

        return perfiles

    def _crear_perfil_aleatorio(self, perfil_base: dict | None, rng) -> dict:
        prob_femenino = perfil_base.get("genero_prob_femenino", 0.50) if perfil_base else 0.50
        genero = "femenino" if rng.random() < prob_femenino else "masculino"
        nombre = (str(rng.choice(NOMBRES_MASCULINOS)) if genero == "masculino"
                  else str(rng.choice(NOMBRES_FEMENINOS))) + " " + str(rng.choice(APELLIDOS))

        def _n(key, default, sd=0.15):
            return float(np.clip(rng.normal(perfil_base.get(key, default), sd), 0, 1))

        if perfil_base:
            nivel_edu   = perfil_base.get("nivel_educativo", str(rng.choice(["tecnico", "universitario", "postgrado"])))
            sit_laboral = perfil_base.get("situacion_laboral", "empleado")
            # Distribución geográfica por arquetipo
            dist_ciudades = perfil_base.get("ciudades_distribucion")
            if dist_ciudades:
                ciudades_list = list(dist_ciudades.keys())
                pesos_ciudad  = list(dist_ciudades.values())
                ciudad = random.choices(ciudades_list, weights=pesos_ciudad, k=1)[0]
            else:
                ciudad = perfil_base.get("ciudad", str(rng.choice(CIUDADES)))
            # Ajustar ingreso según ciudad (factor regional real)
            factor_ciudad = FACTOR_INGRESO_CIUDAD.get(ciudad, 0.85)
            ingreso_base  = perfil_base.get("ingreso_mensual_promedio", 1_000_000) * factor_ciudad
            ingreso       = int(np.clip(rng.normal(ingreso_base, ingreso_base * 0.20), 400_000, 3_500_000))
            apertura = _n("apertura_cambio_media", 0.55)
            aversion = _n("aversion_riesgo_media", 0.40)
            logro    = _n("orientacion_logro_media", 0.60)
            influenc = _n("influenciabilidad_media", 0.50)
            pragmat  = _n("pragmatismo_media", 0.60)
            # nuevos psicológicos
            autoef   = _n("autoeficacia_academica_media", 0.60)
            reconoc  = _n("necesidad_reconocimiento_media", 0.55)
            satisfac = _n("satisfaccion_laboral_media", 0.55)
            ansiedad = _n("ansiedad_academica_media", 0.30)
            # nuevos económicos
            ahorro   = float(np.clip(rng.normal(
                perfil_base.get("ahorro_disponible_meses_media", 2.5), 1.0), 0, 12))
            benef    = bool(rng.random() < perfil_base.get("beneficios_empresa_prob", 0.20))
            # contextual
            modalidad_pref = perfil_base.get("modalidad_preferida", "online")
            horas_disp = int(np.clip(rng.normal(
                perfil_base.get("horas_disponibles_semana_media", 10), 3), 3, 30))
            anios_est  = int(np.clip(rng.normal(
                perfil_base.get("anios_desde_ultimo_estudio_media", 8), 3), 0, 25))
            red_apoyo  = _n("red_apoyo_social_media", 0.60)
            pares_est  = _n("pares_con_estudios_extra_media", 0.40)
            exposicion = _n("exposicion_campo_media", 0.50)
        else:
            nivel_edu   = str(rng.choice(["tecnico", "universitario", "postgrado"], p=[0.3, 0.5, 0.2]))
            ciudad      = str(rng.choice(CIUDADES, p=[0.45, 0.15, 0.12, 0.07, 0.07, 0.07, 0.04, 0.03]))
            sit_laboral = str(rng.choice(["empleado", "independiente", "desempleado"], p=[0.65, 0.25, 0.10]))
            rangos = {"tecnico": (400_000, 900_000), "universitario": (700_000, 1_800_000), "postgrado": (1_200_000, 3_000_000)}
            ingreso  = int(rng.uniform(*rangos[nivel_edu]))
            apertura = float(rng.beta(5, 3))
            aversion = float(rng.beta(3, 4))
            logro    = float(rng.beta(4, 3))
            influenc = float(rng.beta(3, 4))
            pragmat  = float(rng.beta(4, 3))
            autoef   = float(rng.beta(4, 3))
            reconoc  = float(rng.beta(3, 3))
            satisfac = float(rng.beta(4, 3))
            ansiedad = float(rng.beta(2, 4))
            ahorro   = float(np.clip(rng.exponential(2.5), 0, 12))
            benef    = bool(rng.random() < 0.20)
            modalidad_pref = str(rng.choice(["online", "presencial", "hibrida", "indiferente"],
                                            p=[0.45, 0.20, 0.25, 0.10]))
            horas_disp = int(np.clip(rng.normal(10, 4), 3, 30))
            anios_est  = int(np.clip(rng.normal(8, 5), 0, 25))
            red_apoyo  = float(rng.beta(4, 3))
            pares_est  = float(rng.beta(3, 4))
            exposicion = float(rng.beta(3, 3))

        if perfil_base and perfil_base.get("ocupaciones_tipicas"):
            ocupacion = str(rng.choice(perfil_base["ocupaciones_tipicas"]))
        else:
            ocupacion = str(rng.choice(OCUPACIONES.get(nivel_edu, OCUPACIONES["universitario"])))
        if perfil_base and perfil_base.get("areas_tipicas"):
            area = str(rng.choice(perfil_base["areas_tipicas"]))
        else:
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
                ahorro_disponible_meses=ahorro,
                beneficios_empresa=benef,
            ),
            "perfil_psicologico": PerfilPsicologico(
                apertura_cambio=apertura,
                aversion_riesgo=aversion,
                influenciabilidad=influenc,
                orientacion_logro=logro,
                pragmatismo=pragmat,
                autoeficacia_academica=autoef,
                necesidad_reconocimiento=reconoc,
                satisfaccion_laboral=satisfac,
                ansiedad_academica=ansiedad,
            ),
            "perfil_contextual": PerfilContextual(
                modalidad_preferida=modalidad_pref,
                horas_disponibles_semana=horas_disp,
                anios_desde_ultimo_estudio=anios_est,
                red_apoyo_social=red_apoyo,
                pares_con_estudios_extra=pares_est,
                exposicion_campo=exposicion,
            ),
        }

    def _crear_perfil_con_ia(self, perfil_base: dict) -> dict:
        system = (
            "Eres un generador de perfiles de personas chilenas realistas para una simulación "
            "de adopción de programas académicos. Genera datos coherentes con el contexto "
            "socioeconómico, laboral y psicológico chileno. Sé preciso con los números."
        )
        # Sortear ciudad con distribución real antes de enviar a la IA
        dist_ciudades = perfil_base.get("ciudades_distribucion")
        if dist_ciudades:
            ciudad_ia = random.choices(list(dist_ciudades.keys()),
                                       weights=list(dist_ciudades.values()), k=1)[0]
        else:
            ciudad_ia = perfil_base.get("ciudad", "Santiago")
        factor_ciudad_ia = FACTOR_INGRESO_CIUDAD.get(ciudad_ia, 0.85)
        ingreso_base_ia  = int(perfil_base.get("ingreso_mensual_promedio", 1_000_000) * factor_ciudad_ia)

        prompt = f"""Genera un perfil para una persona chilena con estas características base:
{json.dumps(perfil_base, ensure_ascii=False, indent=2)}

Ciudad asignada: {ciudad_ia} (no cambiar)
Ingreso de referencia para esta ciudad: ${ingreso_base_ia:,} CLP (ajustado por nivel salarial regional)

Responde con JSON con exactamente estos campos (sin texto extra):
{{
  "nombre": "nombre apellido chileno realista",
  "edad": número entre 25 y 55,
  "genero": "masculino" o "femenino",
  "ciudad": "{ciudad_ia}",
  "nivel_educativo": "tecnico" | "universitario" | "postgrado",
  "situacion_laboral": "empleado" | "independiente" | "desempleado",
  "ocupacion": "cargo específico y realista",
  "area_profesional": "área de trabajo",
  "activo_en_redes": true o false,
  "ingreso_mensual": entero CLP entre 400000 y 3000000,
  "disposicion_pago": float 0.05-0.40 (fracción del ingreso anual que pagaría),
  "sensibilidad_precio": float 0.0-1.0,
  "deuda_actual": float 0.0-1.0 (nivel de endeudamiento),
  "ahorro_disponible_meses": float 0.0-12.0 (meses de ingreso ahorrados),
  "beneficios_empresa": true o false (empresa paga capacitación),
  "apertura_cambio": float 0.0-1.0,
  "aversion_riesgo": float 0.0-1.0,
  "influenciabilidad": float 0.0-1.0,
  "orientacion_logro": float 0.0-1.0,
  "pragmatismo": float 0.0-1.0,
  "autoeficacia_academica": float 0.0-1.0 (cree que puede estudiar con éxito),
  "necesidad_reconocimiento": float 0.0-1.0 (valora títulos y credenciales),
  "satisfaccion_laboral": float 0.0-1.0 (qué tan satisfecho está con su trabajo actual),
  "ansiedad_academica": float 0.0-1.0 (miedo a retomar estudios),
  "modalidad_preferida": "online" | "presencial" | "hibrida" | "indiferente",
  "horas_disponibles_semana": entero entre 3 y 30,
  "anios_desde_ultimo_estudio": entero entre 0 y 25,
  "red_apoyo_social": float 0.0-1.0 (apoyo de familia/pareja para estudiar),
  "pares_con_estudios_extra": float 0.0-1.0 (proporción de pares que hicieron postgrados),
  "exposicion_campo": float 0.0-1.0 (familiaridad con el área del programa)
}}"""
        raw = self.claude.completar_json(system, prompt)
        data = json.loads(raw)

        return {
            "nombre":           data["nombre"],
            "edad":             int(data["edad"]),
            "genero":           data["genero"],
            "ciudad":           data["ciudad"],
            "nivel_educativo":  data["nivel_educativo"],
            "situacion_laboral":data["situacion_laboral"],
            "ocupacion":        data.get("ocupacion", ""),
            "area_profesional": data.get("area_profesional", ""),
            "activo_en_redes":  bool(data.get("activo_en_redes", True)),
            "perfil_economico": PerfilEconomico(
                ingreso_mensual=int(data["ingreso_mensual"]),
                disposicion_pago=float(data["disposicion_pago"]),
                sensibilidad_precio=float(data["sensibilidad_precio"]),
                deuda_actual=float(data.get("deuda_actual", 0.3)),
                ahorro_disponible_meses=float(data.get("ahorro_disponible_meses", 2.0)),
                beneficios_empresa=bool(data.get("beneficios_empresa", False)),
            ),
            "perfil_psicologico": PerfilPsicologico(
                apertura_cambio=float(data["apertura_cambio"]),
                aversion_riesgo=float(data["aversion_riesgo"]),
                influenciabilidad=float(data["influenciabilidad"]),
                orientacion_logro=float(data["orientacion_logro"]),
                pragmatismo=float(data["pragmatismo"]),
                autoeficacia_academica=float(data.get("autoeficacia_academica", 0.6)),
                necesidad_reconocimiento=float(data.get("necesidad_reconocimiento", 0.5)),
                satisfaccion_laboral=float(data.get("satisfaccion_laboral", 0.55)),
                ansiedad_academica=float(data.get("ansiedad_academica", 0.3)),
            ),
            "perfil_contextual": PerfilContextual(
                modalidad_preferida=data.get("modalidad_preferida", "indiferente"),
                horas_disponibles_semana=int(data.get("horas_disponibles_semana", 10)),
                anios_desde_ultimo_estudio=int(data.get("anios_desde_ultimo_estudio", 7)),
                red_apoyo_social=float(data.get("red_apoyo_social", 0.6)),
                pares_con_estudios_extra=float(data.get("pares_con_estudios_extra", 0.4)),
                exposicion_campo=float(data.get("exposicion_campo", 0.5)),
            ),
        }
