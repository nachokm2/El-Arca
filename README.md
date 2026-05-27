# 🏛️ EL ARCA — Simulador de Sociedades Artificiales

> Testea cómo distintos perfiles de personas perciben y adoptan programas académicos, campañas y productos.

## Caso de uso actual
Evaluación de **diplomados universitarios chilenos** con agentes que representan profesionales reales del mercado chileno.

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Simulación | Mesa 2.3 + NetworkX 3.3 |
| IA de agentes | Anthropic Claude (claude-opus-4-7) |
| Cálculo persuasivo | NumPy 1.26 |
| Dashboard | Streamlit 1.36 + Plotly 5.22 |
| Persistencia | SQLAlchemy + SQLite |
| Validación | Pydantic 2.8 |

---

## Instalación

```bash
# 1. Clonar / acceder al directorio
cd el-arca

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key (opcional pero recomendado)
cp .env.example .env
# Editar .env y poner tu ANTHROPIC_API_KEY
```

## Ejecutar el dashboard

```bash
streamlit run dashboard/app.py
```

## Ejecutar tests

```bash
pytest tests/ -v
```

---

## Estructura del proyecto

```
el-arca/
├── core/               # Motor de simulación
│   ├── agent.py        # ArcaAgent (Mesa)
│   ├── society.py      # ArcaSociety (modelo)
│   ├── persuasion.py   # Motor matemático de persuasión
│   └── network.py      # Red social (NetworkX)
│
├── ai/                 # Inteligencia artificial
│   ├── claude_client.py   # Wrapper API Anthropic
│   ├── agent_factory.py   # Generador de agentes
│   └── debate_engine.py   # Debates en lenguaje natural
│
├── simulation/         # Orquestación
│   ├── runner.py       # Ejecuta experimentos
│   ├── experiment.py   # Configuración
│   └── analyzer.py     # Análisis estadístico
│
├── programs/           # Programas académicos
│   ├── evaluator.py    # Evaluador de competitividad
│   └── templates.py    # 4 diplomados UAC precargados
│
├── dashboard/          # Interfaz Streamlit
│   ├── app.py          # App principal
│   ├── views/          # Pantallas
│   └── components/     # Componentes reutilizables
│
├── data/
│   └── agent_profiles/
│       └── chilean_students.json   # 6 arquetipos chilenos
│
└── tests/              # Tests unitarios
```

---

## Arquetipos de agentes incluidos

| Arquetipo | Descripción | Peso poblacional |
|-----------|-------------|-----------------|
| Profesional en Ascenso | Universitario 28-38 años buscando jefatura | 25% |
| Técnico con Experiencia | Técnico 30-45 años con experiencia práctica | 20% |
| Independiente/Emprendedor | Freelancer que valora ROI inmediato | 15% |
| Profesional de Región | Fuera de Santiago, valora modalidad online | 20% |
| Gerente de Nivel Medio | Alta posición, menor sensibilidad al precio | 10% |
| En Reorientación Profesional | Buscando cambio de área | 10% |

---

## Motor de persuasión

El impacto sobre cada agente se calcula como:

```
Δinterés = 0.35·score_económico + 0.30·score_psicológico + 0.20·score_social + 0.15·score_programa
```

Cada factor considera atributos individuales del agente y características del programa.

---

## Programas precargados (UAC)

1. **Diplomado en Gestión de Proyectos y Liderazgo** — $1.200.000 · 6 meses
2. **Diplomado en Data Analytics e Inteligencia de Negocios** — $1.500.000 · 8 meses
3. **Diplomado en Marketing Digital y E-Commerce** — $980.000 · 5 meses
4. **Diplomado en Salud Mental Organizacional** — $1.100.000 · 6 meses

---

## Sin API Key

El sistema funciona completamente sin API key de Anthropic, usando generación
estocástica de agentes con distribuciones realistas calibradas para el mercado chileno.
Con API key, los agentes generan narrativas y opiniones en lenguaje natural mediante Claude.

---

*Desarrollado para la Universidad Autónoma de Chile · EL ARCA v1.0*
