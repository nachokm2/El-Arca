PROGRAM_TEMPLATES: dict[str, dict] = {
    # ── Programas de Salud (segmento dominante UAU: 54% de matrículas) ──────
    "diplomado_neurorehabilitacion": {
        "id": "diplomado_neurorehabilitacion",
        "nombre": "Diplomado en Neurorrehabilitación Infantil e Integración Sensorial",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "diplomado",
        "duracion_meses": 6,
        "horas_totales": 120,
        "modalidad": "online_asincronica",
        "precio_clp": 645_000,
        "precio_cuotas": 6,
        "tiene_financiamiento": True,
        "requisitos": ["título universitario en área de salud", "experiencia clínica"],
        "certificacion": "Diploma",
        "descripcion": (
            "Especialización en evaluación e intervención neuromotora en población infantil. "
            "Integración sensorial, desarrollo psicomotor y técnicas de rehabilitación pediátrica. "
            "El programa más demandado de la UAU con 96% de tasa de matrícula."
        ),
        "competencias": [
            "Evaluación neuromotora infantil",
            "Integración sensorial",
            "Intervención en parálisis cerebral",
            "Estimulación temprana",
            "Trabajo interdisciplinario en salud",
        ],
        "mercado_laboral": "Alta demanda en centros de rehabilitación, colegios especiales y clínicas pediátricas.",
        "reputacion_institucion": 0.72,
        "relevancia_mercado": 0.90,
        "modalidad_adecuada": 0.92,
        "factor_novedad": 0.60,
        "incertidumbre_percibida": 0.15,
        "retorno_profesional": 0.88,
        "roi_percibido": 0.85,
        "horas_semanales_requeridas": 7,
    },
    "diplomado_salud_mental_psiquiatria": {
        "id": "diplomado_salud_mental_psiquiatria",
        "nombre": "Diplomado en Salud Mental y Psiquiatría",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "diplomado",
        "duracion_meses": 6,
        "horas_totales": 120,
        "modalidad": "online_asincronica",
        "precio_clp": 645_000,
        "precio_cuotas": 6,
        "tiene_financiamiento": True,
        "requisitos": ["título universitario en psicología, medicina, enfermería o área afín"],
        "certificacion": "Diploma",
        "descripcion": (
            "Formación en diagnóstico, intervención y gestión de patologías de salud mental. "
            "Trastornos del estado de ánimo, ansiedad, psicosis y adicciones desde un enfoque "
            "biopsicosocial. Segundo programa más matriculado de la UAU."
        ),
        "competencias": [
            "Diagnóstico psicopatológico",
            "Intervención en crisis",
            "Psicofarmacología básica",
            "Psicoterapia breve",
            "Gestión de redes de salud mental",
        ],
        "mercado_laboral": "Demanda creciente en COSAM, hospitales, clínicas y empresas (Ley de Salud Mental).",
        "reputacion_institucion": 0.72,
        "relevancia_mercado": 0.88,
        "modalidad_adecuada": 0.92,
        "factor_novedad": 0.55,
        "incertidumbre_percibida": 0.15,
        "retorno_profesional": 0.85,
        "roi_percibido": 0.82,
        "horas_semanales_requeridas": 7,
    },
    "magister_psicologia_clinica": {
        "id": "magister_psicologia_clinica",
        "nombre": "Magíster en Psicología Clínica",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "magister",
        "duracion_meses": 24,
        "horas_totales": 960,
        "modalidad": "online_sincronica",
        "precio_clp": 2_995_000,
        "precio_cuotas": 18,
        "tiene_financiamiento": True,
        "requisitos": ["título de psicólogo/a", "2 años de experiencia clínica"],
        "certificacion": "Grado de Magíster (CNED)",
        "descripcion": (
            "Programa de postgrado que forma psicólogos clínicos con enfoque en psicodiagnóstico, "
            "psicoterapia de adultos y niños, y gestión clínica. Grado reconocido por el CNED."
        ),
        "competencias": [
            "Psicodiagnóstico avanzado",
            "Psicoterapia cognitivo-conductual",
            "Psicoterapia sistémica",
            "Peritaje y psicología forense",
            "Supervisión clínica",
        ],
        "mercado_laboral": "Habilitante para cargos clínicos de mayor responsabilidad y docencia universitaria.",
        "reputacion_institucion": 0.72,
        "relevancia_mercado": 0.85,
        "modalidad_adecuada": 0.88,
        "factor_novedad": 0.45,
        "incertidumbre_percibida": 0.30,
        "retorno_profesional": 0.90,
        "roi_percibido": 0.80,
        "horas_semanales_requeridas": 14,
    },
    # ── Programas de Tecnología / Negocios ───────────────────────────────────
    "diplomado_data_analytics": {
        "id": "diplomado_data_analytics",
        "nombre": "Diplomado en Python y Data Science",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "diplomado",
        "duracion_meses": 6,
        "horas_totales": 120,
        "modalidad": "online_asincronica",
        "precio_clp": 695_000,
        "precio_cuotas": 6,
        "tiene_financiamiento": True,
        "requisitos": ["título universitario o técnico", "conocimientos básicos de Excel"],
        "certificacion": "Diploma",
        "descripcion": (
            "Formación práctica en análisis de datos con Python, SQL y visualización. "
            "Transforma datos en decisiones estratégicas. Programa real UAU con 98% tasa de matrícula."
        ),
        "competencias": [
            "Python para análisis de datos",
            "SQL y bases de datos",
            "Visualización con Matplotlib/Seaborn",
            "Estadística aplicada",
            "Machine Learning básico",
        ],
        "mercado_laboral": "Uno de los perfiles más demandados. Salarios 30-50% superiores al promedio.",
        "reputacion_institucion": 0.72,
        "relevancia_mercado": 0.92,
        "modalidad_adecuada": 0.88,
        "factor_novedad": 0.80,
        "incertidumbre_percibida": 0.35,
        "retorno_profesional": 0.88,
        "roi_percibido": 0.82,
        "horas_semanales_requeridas": 10,
    },
    "diplomado_inteligencia_artificial": {
        "id": "diplomado_inteligencia_artificial",
        "nombre": "Diplomado en Inteligencia Artificial",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "diplomado",
        "duracion_meses": 6,
        "horas_totales": 120,
        "modalidad": "online_asincronica",
        "precio_clp": 695_000,
        "precio_cuotas": 6,
        "tiene_financiamiento": True,
        "requisitos": ["título universitario o técnico", "conocimientos básicos de programación o Excel"],
        "certificacion": "Diploma",
        "descripcion": (
            "Fundamentos y aplicaciones de IA: machine learning, deep learning, LLMs y automatización "
            "de procesos. Enfoque práctico con herramientas actuales. Programa real UAU."
        ),
        "competencias": [
            "Machine Learning supervisado y no supervisado",
            "Redes neuronales y Deep Learning",
            "Procesamiento de lenguaje natural",
            "IA aplicada a negocios",
            "Prompt engineering y LLMs",
        ],
        "mercado_laboral": "Alta demanda transversal en todos los sectores. Perfil del futuro.",
        "reputacion_institucion": 0.72,
        "relevancia_mercado": 0.95,
        "modalidad_adecuada": 0.88,
        "factor_novedad": 0.90,
        "incertidumbre_percibida": 0.38,
        "retorno_profesional": 0.90,
        "roi_percibido": 0.85,
        "horas_semanales_requeridas": 10,
    },
    "diplomado_gestion_proyectos": {
        "id": "diplomado_gestion_proyectos",
        "nombre": "Diplomado en Gestión de Proyectos y Liderazgo",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "diplomado",
        "duracion_meses": 6,
        "horas_totales": 120,
        "modalidad": "online_sincronica",
        "precio_clp": 695_000,
        "precio_cuotas": 6,
        "tiene_financiamiento": True,
        "requisitos": ["título universitario o técnico", "2 años de experiencia laboral"],
        "certificacion": "Diploma con reconocimiento SENCE",
        "descripcion": (
            "Programa intensivo que desarrolla competencias para liderar equipos y gestionar "
            "proyectos complejos usando metodologías ágiles y tradicionales. "
            "Ideal para profesionales que buscan ascender a roles de jefatura."
        ),
        "competencias": [
            "Gestión de alcance, tiempo y costos",
            "Liderazgo y trabajo en equipo",
            "Metodologías Ágiles (Scrum, Kanban)",
            "Gestión de riesgos",
            "Comunicación efectiva con stakeholders",
        ],
        "mercado_laboral": "Alta demanda. Roles: PM, coordinador de proyectos, jefe de operaciones.",
        "reputacion_institucion": 0.72,
        "relevancia_mercado": 0.85,
        "modalidad_adecuada": 0.80,
        "factor_novedad": 0.55,
        "incertidumbre_percibida": 0.25,
        "retorno_profesional": 0.80,
        "roi_percibido": 0.75,
        "horas_semanales_requeridas": 8,
    },
    "diplomado_marketing_digital": {
        "id": "diplomado_marketing_digital",
        "nombre": "Diplomado en Marketing Digital y E-Commerce",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "diplomado",
        "duracion_meses": 5,
        "horas_totales": 100,
        "modalidad": "hibrida",
        "precio_clp": 645_000,
        "precio_cuotas": 5,
        "tiene_financiamiento": True,
        "requisitos": ["título técnico o universitario"],
        "certificacion": "Diploma + certificado Google Ads",
        "descripcion": (
            "Especialización en estrategias digitales: SEO, SEM, redes sociales, email marketing "
            "y e-commerce. Con herramientas reales y proyectos de marca personal."
        ),
        "competencias": [
            "SEO y posicionamiento web",
            "Google Ads y Meta Ads",
            "Estrategia de contenidos",
            "Analytics y métricas",
            "E-commerce y conversión",
        ],
        "mercado_laboral": "Alta demanda en PYMEs y agencias digitales.",
        "reputacion_institucion": 0.72,
        "relevancia_mercado": 0.78,
        "modalidad_adecuada": 0.75,
        "factor_novedad": 0.65,
        "incertidumbre_percibida": 0.20,
        "retorno_profesional": 0.70,
        "roi_percibido": 0.65,
        "horas_semanales_requeridas": 7,
    },
    "diplomado_salud_mental_laboral": {
        "id": "diplomado_salud_mental_laboral",
        "nombre": "Diplomado en Salud Mental Organizacional",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "diplomado",
        "duracion_meses": 6,
        "horas_totales": 120,
        "modalidad": "online_sincronica",
        "precio_clp": 645_000,
        "precio_cuotas": 6,
        "tiene_financiamiento": True,
        "requisitos": ["título universitario en área de salud, psicología o RRHH"],
        "certificacion": "Diploma",
        "descripcion": (
            "Formación para gestionar el bienestar psicológico en las organizaciones. "
            "Prevención del burnout, protocolos de salud mental y liderazgo empático."
        ),
        "competencias": [
            "Diagnóstico del clima organizacional",
            "Prevención del burnout",
            "Gestión del estrés laboral",
            "Protocolos de salud mental",
            "Liderazgo empático",
        ],
        "mercado_laboral": "Creciente demanda post-pandemia en grandes empresas.",
        "reputacion_institucion": 0.72,
        "relevancia_mercado": 0.75,
        "modalidad_adecuada": 0.78,
        "factor_novedad": 0.60,
        "incertidumbre_percibida": 0.22,
        "retorno_profesional": 0.72,
        "roi_percibido": 0.60,
        "horas_semanales_requeridas": 8,
    },
}


def get_template(template_id: str) -> dict:
    if template_id not in PROGRAM_TEMPLATES:
        raise KeyError(f"Template '{template_id}' no existe. Disponibles: {list(PROGRAM_TEMPLATES.keys())}")
    return PROGRAM_TEMPLATES[template_id].copy()


def list_templates() -> list[dict]:
    return [
        {
            "id": k,
            "nombre": v["nombre"],
            "precio_clp": v["precio_clp"],
            "modalidad": v["modalidad"],
            "duracion_meses": v["duracion_meses"],
            "tipo": v.get("tipo", "diplomado"),
        }
        for k, v in PROGRAM_TEMPLATES.items()
    ]
