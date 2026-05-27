PROGRAM_TEMPLATES: dict[str, dict] = {
    "diplomado_gestion_proyectos": {
        "id": "diplomado_gestion_proyectos",
        "nombre": "Diplomado en Gestión de Proyectos y Liderazgo",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "diplomado",
        "duracion_meses": 6,
        "horas_totales": 120,
        "modalidad": "online_sincronica",
        "precio_clp": 1_200_000,
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
        # Factores para el motor de persuasión
        "reputacion_institucion": 0.72,
        "relevancia_mercado": 0.85,
        "modalidad_adecuada": 0.80,
        "factor_novedad": 0.55,
        "incertidumbre_percibida": 0.25,
        "retorno_profesional": 0.80,
        "roi_percibido": 0.75,
        "horas_semanales_requeridas": 8,
    },
    "diplomado_data_analytics": {
        "id": "diplomado_data_analytics",
        "nombre": "Diplomado en Data Analytics e Inteligencia de Negocios",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "diplomado",
        "duracion_meses": 8,
        "horas_totales": 160,
        "modalidad": "online_asincronica",
        "precio_clp": 1_500_000,
        "precio_cuotas": 8,
        "tiene_financiamiento": True,
        "requisitos": ["título universitario", "conocimientos básicos de Excel"],
        "certificacion": "Diploma + certificado en Power BI",
        "descripcion": (
            "Formación práctica en análisis de datos con Python, SQL, Power BI y machine learning "
            "aplicado a negocios. Transforma datos en decisiones estratégicas."
        ),
        "competencias": [
            "Python para análisis de datos",
            "SQL y bases de datos",
            "Power BI y Tableau",
            "Estadística aplicada",
            "Machine Learning básico",
        ],
        "mercado_laboral": "Uno de los perfiles más demandados. Salarios 30-50% superiores al promedio.",
        "reputacion_institucion": 0.72,
        "relevancia_mercado": 0.92,
        "modalidad_adecuada": 0.85,
        "factor_novedad": 0.80,
        "incertidumbre_percibida": 0.35,
        "retorno_profesional": 0.88,
        "roi_percibido": 0.82,
        "horas_semanales_requeridas": 12,
    },
    "diplomado_marketing_digital": {
        "id": "diplomado_marketing_digital",
        "nombre": "Diplomado en Marketing Digital y E-Commerce",
        "institucion": "Universidad Autónoma de Chile",
        "tipo": "diplomado",
        "duracion_meses": 5,
        "horas_totales": 100,
        "modalidad": "hibrida",
        "precio_clp": 980_000,
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
        "precio_clp": 1_100_000,
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
        }
        for k, v in PROGRAM_TEMPLATES.items()
    ]
