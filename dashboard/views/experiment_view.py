import json
import streamlit as st
from programs.templates import list_templates, get_template, PROGRAM_TEMPLATES
from programs.evaluator import ProgramEvaluator, ProgramaAcademico
from simulation.experiment import ExperimentConfig
from simulation.runner import SimulationRunner
from dashboard.components.metrics_panel import render_kpi_row, render_estado_pie, render_curva_difusion
from simulation.analyzer import ResultsAnalyzer
import config


def render_experiment_view():
    st.title("🧪 Experimento")

    tab_config, tab_programa, tab_personalizado = st.tabs([
        "⚙️ Configurar Simulación",
        "📚 Seleccionar Programa",
        "✏️ Programa Personalizado",
    ])

    with tab_programa:
        _render_selector_programa()

    with tab_config:
        _render_configuracion()

    with tab_personalizado:
        _render_programa_personalizado()


def _render_selector_programa():
    st.subheader("Programas predefinidos")
    templates = list_templates()
    evaluator = ProgramEvaluator()

    for tmpl in templates:
        prog = get_template(tmpl["id"])
        ev = evaluator.evaluar(prog)
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                st.markdown(f"**{prog['nombre']}**")
                st.caption(prog["descripcion"][:120] + "...")
            with c2:
                st.metric("Score", f"{int(ev.score_global * 100)}/100")
                st.caption(f"${prog['precio_clp']:,} · {prog['duracion_meses']}m · {prog['modalidad']}")
            with c3:
                if st.button("Usar", key=f"usar_{tmpl['id']}"):
                    st.session_state["programa_activo"] = prog
                    st.success(f"Programa seleccionado: {prog['nombre']}")

    prog_activo = st.session_state.get("programa_activo")
    if prog_activo:
        st.success(f"✅ Programa activo: **{prog_activo['nombre']}**")


def _render_configuracion():
    st.subheader("Parámetros de la simulación")

    prog_activo = st.session_state.get("programa_activo")
    if not prog_activo:
        st.warning("Primero selecciona un programa en la pestaña **Seleccionar Programa**.")

    col1, col2 = st.columns(2)
    with col1:
        n_agentes = st.slider("Número de agentes", min_value=10, max_value=200, value=50, step=10)
        n_pasos = st.slider("Pasos de simulación", min_value=5, max_value=50, value=20)
        topologia = st.selectbox(
            "Topología de red",
            options=["small_world", "scale_free", "random", "comunidades"],
            index=0,
            help="small_world = red realista; scale_free = pocos nodos muy influyentes; comunidades = grupos por ciudad/educación",
        )
    with col2:
        seed = st.number_input("Semilla aleatoria", min_value=1, max_value=9999, value=42)
        usar_ia = st.toggle(
            "Usar IA (Claude) para agentes",
            value=False,
            disabled=not bool(config.ANTHROPIC_API_KEY),
            help="Genera personalidades más realistas pero requiere API key y consume créditos.",
        )
        nombre_exp = st.text_input("Nombre del experimento", value="Experimento EL ARCA")

    arquetipos_disponibles = _cargar_arquetipos()
    usar_arquetipos = st.toggle("Usar arquetipos chilenos de estudiantes", value=True)

    st.divider()

    if st.button("🚀 Ejecutar Simulación", type="primary", disabled=not prog_activo):
        if not prog_activo:
            st.error("Selecciona un programa primero.")
            return

        exp_config = ExperimentConfig(
            nombre=nombre_exp,
            descripcion=f"Simulación de {n_agentes} agentes sobre {prog_activo.get('nombre', '?')}",
            n_agentes=n_agentes,
            n_pasos=n_pasos,
            topologia_red=topologia,
            programa=prog_activo,
            seed=int(seed),
            usar_ia=usar_ia,
            arquetipos=arquetipos_disponibles if usar_arquetipos else [],
        )

        errores = exp_config.validar()
        if errores:
            for e in errores:
                st.error(e)
            return

        _ejecutar_simulacion(exp_config)


def _ejecutar_simulacion(exp_config: ExperimentConfig):
    runner = SimulationRunner()
    placeholder = st.empty()
    snapshots_live = []

    def on_step(step, snap, sociedad):
        snapshots_live.append(snap)
        with placeholder.container():
            st.markdown(f"**Paso {step + 1}/{exp_config.n_pasos}**")
            conteos = snap["conteos"]
            total = snap["total_agentes"]
            cols = st.columns(5)
            labels = ["neutral", "interesado", "esceptico", "adoptado", "rechazado"]
            emojis = ["⚪", "🔵", "🟠", "🟢", "🔴"]
            for col, label, emoji in zip(cols, labels, emojis):
                with col:
                    n = conteos.get(label, 0)
                    st.metric(f"{emoji} {label.capitalize()}", n, delta=None)
            st.progress((step + 1) / exp_config.n_pasos)

    with st.spinner("Ejecutando simulación..."):
        try:
            experimento = runner.ejecutar(exp_config, callback_step=on_step)
            placeholder.empty()
            st.session_state["experimento_activo"] = experimento.to_dict()
            st.session_state["vista"] = "resultados"
            st.success("✅ Simulación completada. Ve a **Resultados** para el análisis completo.")
            st.balloons()

            # Vista rápida
            resultados = experimento.resultados
            analyzer = ResultsAnalyzer(experimento.to_dict())
            resumen = analyzer.resumen_ejecutivo()
            st.divider()
            st.subheader("Vista rápida de resultados")
            render_kpi_row(resumen)
            render_estado_pie(resultados.get("conteos_finales", {}))

        except Exception as e:
            st.error(f"Error en la simulación: {e}")


def _render_programa_personalizado():
    st.subheader("Define tu propio programa")
    st.caption("Todos los campos con * son obligatorios")

    with st.form("form_programa_custom"):
        nombre = st.text_input("Nombre del programa *", placeholder="Diplomado en ...")
        institucion = st.text_input("Institución *", placeholder="Universidad ...")
        tipo = st.selectbox("Tipo", ["diplomado", "curso", "magister", "certificado"])
        col1, col2 = st.columns(2)
        with col1:
            duracion = st.number_input("Duración (meses) *", min_value=1, max_value=36, value=6)
            horas = st.number_input("Horas totales *", min_value=10, max_value=2000, value=120)
            precio = st.number_input("Precio CLP *", min_value=50000, max_value=50000000, value=1200000, step=50000)
        with col2:
            cuotas = st.number_input("Número de cuotas", min_value=1, max_value=60, value=6)
            modalidad = st.selectbox("Modalidad *", ["online_sincronica", "online_asincronica", "hibrida", "presencial"])
            tiene_fin = st.checkbox("¿Tiene financiamiento?", value=False)

        st.markdown("**Factores de percepción** (ajusta según tu conocimiento del mercado)")
        cf1, cf2 = st.columns(2)
        with cf1:
            reputacion = st.slider("Reputación institución", 0.0, 1.0, 0.7, 0.05)
            relevancia = st.slider("Relevancia de mercado", 0.0, 1.0, 0.7, 0.05)
            modalidad_ok = st.slider("Adecuación de la modalidad", 0.0, 1.0, 0.7, 0.05)
        with cf2:
            novedad = st.slider("Factor novedad", 0.0, 1.0, 0.5, 0.05)
            incertidumbre = st.slider("Incertidumbre percibida", 0.0, 1.0, 0.3, 0.05)
            roi = st.slider("ROI percibido", 0.0, 1.0, 0.6, 0.05)

        descripcion = st.text_area("Descripción", placeholder="Describe el programa...")
        submit = st.form_submit_button("💾 Guardar como programa activo", type="primary")

    if submit and nombre and institucion:
        programa = {
            "nombre": nombre,
            "institucion": institucion,
            "tipo": tipo,
            "duracion_meses": int(duracion),
            "horas_totales": int(horas),
            "modalidad": modalidad,
            "precio_clp": int(precio),
            "precio_cuotas": int(cuotas),
            "tiene_financiamiento": tiene_fin,
            "descripcion": descripcion,
            "reputacion_institucion": reputacion,
            "relevancia_mercado": relevancia,
            "modalidad_adecuada": modalidad_ok,
            "factor_novedad": novedad,
            "incertidumbre_percibida": incertidumbre,
            "retorno_profesional": roi,
            "roi_percibido": roi,
        }
        st.session_state["programa_activo"] = programa
        st.success(f"✅ Programa '{nombre}' guardado. Ve a **Configurar Simulación** para ejecutar.")


def _cargar_arquetipos() -> list[dict]:
    try:
        import json
        path = config.PROFILES_DIR / "chilean_students.json"
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
